#!/usr/bin/python3

import argparse
import logging
import os
import sys
from contextlib import redirect_stdout
import requests

import koji
from koji_cli.lib import watch_tasks

LAST_SUCCESSFUL_BULD = "https://osci-jenkins-1.ci.fedoraproject.org/job/eln-periodic/lastSuccessfulBuild/artifact/buildable-eln-packages.txt"  # pylint: disable=C0301


# Connect to Fedora Koji instance
# If KOJI_KEYTAB is set, it will override default kerberos authentication settings

session = koji.ClientSession('https://koji.fedoraproject.org/kojihub')
session.gssapi_login(keytab=os.getenv('KOJI_KEYTAB'))


def configure_logging(verbose=False, output=None):
    """Configure logging

    If verbose is set, set debug level for the default console logger.  If
    output filename is given, configure FileHandler to additionally send all
    INFO-level messages to the file.

    Return logger object.
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if verbose:
        logger.setLevel(logging.DEBUG)

    if output:
        output_fh = logging.FileHandler(output)
        output_fh.setLevel(logging.INFO)
        output_fh.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(output_fh)


    # #To allow stdout redirect
    logger.write = lambda msg: logger.info(msg) if msg != '\n' else None
    logger.flush = lambda: None
    return logger


def is_eln(eln_package):
    """Checking if a package is in the last successful build

    Return boolean.
    """
    buildable_packagelist = requests.get(LAST_SUCCESSFUL_BULD, allow_redirects=True).text.splitlines()
    return bool(eln_package in buildable_packagelist)


def rebuild_source(build_source, scratch=False):
    """Rebuilding sources

    Return task_id.
    """
    logger.debug("Rebuilding sources {0}".format(build_source))

    opts = {}

    opts['fail_fast'] = True

    if scratch:
        opts['scratch'] = True

    return session.build(src=build_source, target="eln", opts=opts)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-b", "--build-id",
                        help="koji build id",
                        type=int,
    )
    parser.add_argument("-v", "--verbose",
                        help="Enable debug logging",
                        action='store_true',
    )
    parser.add_argument("-s", "--scratch",
                        help="Run scratch build",
                        action='store_true',
    )
    parser.add_argument("-w", "--wait",
                        help="Wait for the task to finish",
                        action='store_true',
    )
    parser.add_argument("-o", "--output",
                        help="Add output to the specified file",
                        default=None,
    )

    args = parser.parse_args()

    logger = configure_logging(verbose=args.verbose, output=args.output)
    build = session.getBuild(args.build_id)

    package = build["name"]
    source = build["source"]

    if not is_eln(package):
        logger.info("{0} is not in ELN".format(package))
        sys.exit(0)

    task_id = rebuild_source(source, scratch=args.scratch)

    info_fmt = (
        "{0}\n"
        "https://koji.fedoraproject.org/koji/taskinfo?taskID={1}\n\n"
        "{2}\n"
        )
    logger.info(info_fmt.format(package, task_id, source))

    if task_id and args.wait:
        with redirect_stdout(logger):
            rv = watch_tasks(session, [task_id], poll_interval=10)

        sys.exit(rv)
