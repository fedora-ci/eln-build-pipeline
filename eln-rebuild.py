#!/usr/bin/python3

import argparse
import os
import koji
from koji_cli.lib import watch_tasks
import logging


session = koji.ClientSession('https://koji.fedoraproject.org/kojihub')
session.gssapi_login(keytab=os.getenv('KOJI_KEYTAB'))


def rebuild_for_eln(build_id):
    build = session.getBuild(build_id)

    package = build["name"]
    scm = build["source"]

    builds_in_ELN = session.listTagged("eln", package=package)

    if not builds_in_ELN:
        logging.info("Package {0} is not in ELN".format(package))
        return None

    logging.info("Package {0} needs rebuilding".format(package))
    task_id = session.build(src=scm, target="eln", opts={'scratch': True})

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
    parser.add_argument("-w", "--wait",
                        help="Wait for the task to finish",
                        action='store_true',
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    task_id = rebuild_for_eln(args.build_id)

    if task_id and args.wait:
        watch_tasks(session, [task_id], poll_interval=10)
