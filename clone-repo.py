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

    parser.add_argument('-f', '--repofile', action='store_true', default=False,
                        help='enable if you want a <reponame>.repo file for\
                                use by yum clients')

    parser.add_argument('-n', '--dryrun', action="store_true",
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the filesystem')

    args = parser.parse_args()

    return args


def getpackagelist(src_repo):
    """ Build a dict of the files that are going to be linked or copied
        packagename = fq_Filename"""
    pkglisting = {}
    pkgs = os.listdir(src_repo)
    for rpm_pkg in pkgs:
        if rpm_pkg.endswith('.rpm'):
            ts = rpm.TransactionSet()
            package = src_repo + rpm_pkg
            fdno = os.open(package, os.O_RDONLY)
            hdr = ts.hdrFromFdno(fdno)
            os.close(fdno)
            if hdr[rpm.RPMTAG_SOURCERPM]:
               print "header is from a binary package"
            else:
               print "header is from a source package"
            pkg_name = hdr[rpm.RPMTAG_NAME]
            pkglisting[pkg_name]=package
    
    return pkglisting


def assemble_repo(pkglisting, destdir, link='symlink'):
    """ copy or link files to cloned location. """
    pass
    message, success = 'failed for some reason', 1
    return message, success


def createrepo(destdir):
    """ Run createrepo on destdir, assembling the bits yum needs"""
    pass  # Again, nothing happening yet
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

    if not args.dest_dir:
        print 'need a location to clone the repo into.'
        sys.exit(1)


    pkgs = getpackagelist(args.source_repo)
    print pkgs
