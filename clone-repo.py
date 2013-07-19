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
    import createrepo
except ImportError as error:
        print 'Python says %s, please ensure you have access to the\
 yum rpm, and createrepo python modules. ' % error
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
                        dest="destdir", help='Topdir of cloned repo')

    parser.add_argument("--linktype",
                        action="store", dest="linktype",
                        default='symlink', help='symlink, hardlink, or copy')

    parser.add_argument('-f', '--repofile', action='store_true', default=False,
                        help='enable if you want a <reponame>.repo file for\
                                use by yum clients')

    parser.add_argument('-n', '--dryrun', action="store_true",
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the filesystem')

    args = parser.parse_args()

    return args


def get_packagelist(src_repo):
    """ Build a dict of the files that are going to be linked or copied
        packagename = fq_Filename"""
    pkglisting = []
    pkgs = os.listdir(src_repo)
    for rpm_pkg in pkgs:
        if rpm_pkg.endswith('.rpm'):
            ts = rpm.TransactionSet()
            package = src_repo + '/' + rpm_pkg
            fdno = os.open(package, os.O_RDONLY)
            try:
                hdr = ts.hdrFromFdno(fdno)
            except rpm.error, e:
                # Eating errors from signed packages where
                # we don't have the key
                print package, e
            pkglisting.append(package)
            os.close(fdno)
    print pkglisting
    return pkglisting


def assemble_repo(pkglisting, destdir, link):
    """ copy or link files to cloned location. """
    message, success = 'failed for some reason', 1
    return message, success


def create_repo(destdir):
    """ Run createrepo on destdir, assembling the bits yum needs"""
    message, success = 'createrepo failed', 1

    return message, success


def create_repofile(reponame, dest_dir):
    """ Create a <name>.repo file to be used by yum on clients """
    repofile = "nothing yet"
    return repofile


if "__main__" in __name__:
    args = get_options()
    if args.dryrun:
        message = 'dry run only'
        print args
        print message
        sys.exit(0)

    if not args.source_repo:
        print 'need a source repo to clone from'
        sys.exit(1)
    else:
        source_repo = args.source_repo

    if not args.destdir:
        print 'need a location to clone the repo into.'
        sys.exit(1)
    else:
        destdir = args.destdir

    if not args.linktype:
        link = 'symlink'
    else:
        l_requested = args.linktype
        if l_requested == 'hardlink' or 'symlink' or 'copy':
            link = l_requested
        else:
            print 'Incorrect value for linktype, please use symlink, \
            hardlink,or copy, not %s' % l_requested
            sys.exit(1)

    # Assemble the package list, with locations
    pkgs = get_packagelist(args.source_repo)
    # Send package list, along with destdir and linktype
    # to assemble_repo to build the file structure.
    assemble_repo(pkgs, destdir, link)
