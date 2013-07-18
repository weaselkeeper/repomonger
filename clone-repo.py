#!/usr/bin/env  python
""" Simple script that takes a source and destination repo directory, and
clones the repo in the source directory, to the dest. Then reruns create repo
against it.  Every package in src_repo is linked or copied (default, symlink,
hardlink and copy are optional)

Author: Jim Richardson <weaselkeeper@gmail.com>
Date:   18 Jul 2013

"""


import os
import yum
import rpm
import logging

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
    OptionParser = optparse.OptionParser
    parser = OptionParser(usage)

    required = optparse.OptionGroup(parser, "Required")
    optional = optparse.OptionGroup(parser, "Optional")

    required.add_option('-s', '--src', action="store", type="string",
                        dest="source repo", help='Repo to clone.')

    required.add_option('-d', '--dst', action="store", type="string",
                        dest="dest_dir", help='Topdir of cloned repo')

    optional.add_option("--linktype",
                        action="store", type="string", dest="username",
                        default='symlink', help='symlink, hardlink, or copy')

    optional.add_option('-n', '--dryrun', action="store_true", type=boolean,
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the filesystem')

    parser.add_option_group(required)
    parser.add_option_group(optional)

    options, args = parser.parse_args()

    if not options.failures:
        parser.print_help()

    return options, args


if "__main__" in __name__:
    options, args = get_options()

    if options.dryrun:
        message = 'dry run only'
    elif options.failures or options.catalog_run_failures:
        get_failed(cursor)
