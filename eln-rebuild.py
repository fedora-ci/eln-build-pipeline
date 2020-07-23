#!/usr/bin/python3

import argparse
import logging
import os

import sys
from contextlib import redirect_stdout

import koji
from koji_cli.lib import watch_tasks


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

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


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


def is_eln(package):
    builds_in_ELN = session.listTagged("eln", package=package)
    return bool(builds_in_ELN)

def rebuild_source(source, scratch=False):
    logger.debug("Rebuilding sources {0}".format(source))

    opts = {}
    if scratch:
        opts['scratch'] = True

    task_id = session.build(src=source, target="eln", opts=opts)

    return task_id


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
        exit(0)

    task_id = rebuild_source(source, scratch=args.scratch)

    info_fmt = (
        "{0}: {1}\n\n"
        "https://koji.fedoraproject.org/koji/taskinfo?taskID={1}\n"
        "{2}\n"
        )
    logger.info(info_fmt.format(package, task_id, source))

    if task_id and args.wait:
        with redirect_stdout(logger):
            rv = watch_tasks(session, [task_id], poll_interval=10)

        exit(rv)
