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


def is_eln(package):
    builds_in_ELN = session.listTagged("eln", package=package)
    return bool(builds_in_ELN)

def rebuild_source(source, scratch=False):
    logging.info("Rebuilding sources {0}".format(source))

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
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    build = session.getBuild(args.build_id)

    package = build["name"]
    source = build["source"]

    if not is_eln(package):
        logging.info("Package {0} is not in ELN".format(package))
        print("{0}: skipped".format(package))
        exit(0)
        
    task_id = rebuild_source(source, scratch=args.scratch)
    if task_id and args.wait:
        with redirect_stdout(sys.stderr):
            watch_tasks(session, [task_id], poll_interval=10)
        print("{0}: {1}".format(package, task_id))

