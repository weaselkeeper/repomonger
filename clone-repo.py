#!/usr/bin/env  python
""" Simple script that takes a source and destination repo directory, and
clones the repo in the source directory, to the dest. Then reruns create repo
against it.  Every package in src_repo is linked or copied (default, symlink,
hardlink and copy are optional)

Author: Jim Richardson <weaselkeeper@gmail.com>
Date:   18 Jul 2013

"""


import os
import sys
import logging
import argparse

try:
    import rpm
    import yum
except ImportError as error:
        print 'Python says %s, please ensure you have access to the\
 yum and rpm python modules. ' % error
        sys.exit(1)

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                    )

console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("clone_repo").addHandler(console)
log = logging.getLogger("clone_repo")


def get_options():
    """ command-line options """
    usage = "usage: %prog [options]"
    parser = argparse.ArgumentParser(description='Pass cli options to \
        script')

    parser.add_argument('-s', '--src', action="store",
                        dest="source_repo", help='Repo to clone.')

    parser.add_argument('-d', '--dst', action="store",
                        dest="dest_dir", help='Topdir of cloned repo')

    parser.add_argument("--linktype",
                        action="store", dest="linktype",
                        default='symlink', help='symlink, hardlink, or copy')

    parser.add_argument('-n', '--dryrun', action="store_true",
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the filesystem')

    args = parser.parse_args()

    return args


if "__main__" in __name__:
    args = get_options()
    print args
    if not args.source_repo:
        print 'need a source repo to clone from'
        sys.exit()

    if args.dryrun:
        message = 'dry run only'
        print args
        print message
