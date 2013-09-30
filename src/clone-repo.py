#!/usr/bin/env  python
""" Simple script that takes a source and destination repo directory, and
clones the repo in the source directory, to the dest. Then reruns create repo
against it.  Every package in src_repo is linked or copied (default, symlink,
hardlink and copy are optional)

License: GPL V2 See LICENSE file
Author: Jim Richardson <weaselkeeper@gmail.com>
Date:   18 Jul 2013

"""


import os
import sys
import shutil
from ConfigParser import SafeConfigParser
import logging

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                    )
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("clone_repo").addHandler(console)
log = logging.getLogger("clone_repo")

# Some default settings
CONFIGFILE = '/etc/repomonger/repomonger.conf'


try:
    import rpm
    import yum
    import createrepo
except ImportError as error:
        logging.warn('Python says %s, please ensure you have access to the \
                 yum rpm, and createrepo python modules. ' % error)
        sys.exit(1)


def get_options():
    """ command-line options """
    log.debug('Entering get_options()')
    parser = argparse.ArgumentParser(description='Pass cli options to \
        script')

    parser.add_argument('-S', '--src', action="store",
                        dest="source_repo", help='Repo to clone.')

    parser.add_argument('-D', '--dst', action="store",
                        dest="destdir", help='Topdir of cloned repo')

    parser.add_argument("-l", "--linktype",
                        action="store", dest="linktype",
                        default='symlink', help='symlink, hardlink, or copy')

    parser.add_argument('-f', '--repofile', action='store_true', default=False,
                        help='enable if you want a <reponame>.repo file for\
                                use by yum clients')

    parser.add_argument('-n', '--dryrun', action="store_true",
                        default=False, help='Dry run will report what it \
                        would do, but makes no changes to the filesystem')

    parser.add_argument('-d', '--debug', action="store_true", default=False)

    args = parser.parse_args()
    args.usage = "clone_repo.py [options]"
    logging.debug('Exiting get_options with args %s' % args)
    return args


def get_packagelist(src_repo):
    """ Build a dict of the files that are going to be linked or copied
        packagename = fq_Filename"""
    log.debug('Entering get_packagelist()')
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
                log.warn(package + " " + str(e))
            pkglisting.append(package)
            os.close(fdno)
    log.debug('Exiting get_packagelist, with pkglisting %s' % pkglisting)
    return pkglisting


def assemble_repo(pkglisting, destdir, link):
    """ copy or link files to cloned location. """
    log.debug('Entering assemble_repo()')
    message, success = 'Beginning to assemble repo', 1
    try:
        if not os.path.exists(destdir):
            log.warn('destdir %s does not exist, creating it' % destdir)        
            os.makedirs(destdir)
            message = ('%s created' % destdir)

    except:
        message = ('Can not create dir %s' % destdir)

    log.debug('in assemble_repo(), message is %s' % message)
 
    if link == 'copy':
        for pkg in pkglisting:
            shutil.copy(pkg, destdir)
        message, success = 'pkgs copied', 0

    elif link == 'hardlink':
        for pkg in pkglisting:
            _path, _file = os.path.split(pkg)
            linkedfile = destdir + '/' + _file
            os.link(pkg, linkedfile)
        message, success = 'pkgs hardinked', 0

    elif link == 'symlink':
        for pkg in pkglisting:
            _path, _file = os.path.split(pkg)
            linkedfile = destdir + '/' + _file
            try:
        
                os.symlink(pkg, linkedfile)
            except OSError,e:
                log.warn(str(e))
                break
        message, success = 'pkgs symlinked', 0
    log.debug('Exiting assemble_repo(), trying to %s rpm pkgs, received message %s ' % (link, message))
    return message, success


def create_repo(destdir):
    """ Run createrepo on destdir, assembling the bits yum needs"""
    log.debug('Entering create_repo()')
    import subprocess
    try:
        mkrepo = subprocess.Popen(['/usr/bin/createrepo',destdir],
        success = subprocess.PIPE).communicate()[0]
    except:
        log.warn('something went wrong with creating repo %s' % destdir)
        mkrepo, success = 'making repo failed', 1
    log.debug('Exiting create_repo with the message %s about %s' % (message, mkrepo))
    return mkrepo, success


def create_repofile(reponame, dest_dir):
    """ Create a <name>.repo file to be used by yum on clients """
    log.debug('Entering create_repofile()')
    repofile = "TODO"
    log.warn('Repo file created for repo %s' % reponame)
    log.warn(repofile)
    log.debug('Exiting create_repofile() with nothing done yet')
    return repofile


def run(destdir, source_repo, linktype='symlink'):
    log.debug('Entering run()')
    # Assemble the package list, with locations
    pkgs = get_packagelist(args.source_repo)
    # Send package list, along with destdir and linktype
    # to assemble_repo to build the file structure.
    assemble_repo(pkgs, destdir, link)
    # And finaly, create the repo.
    create_repo(destdir)
    log.debug('Exiting run(), creating repo %s from pkglist %s' %(pkgs, destdir))


if "__main__" in __name__:
    """This is where we will begin when called from CLI"""

    import argparse
    args = get_options()

    if args.debug:
        log.setLevel(logging.DEBUG)

    if args.dryrun:
        message = 'dry run only'
        log.info(args)
        log.warn(message)
        sys.exit(0)

    if not args.source_repo:
        log.warn(args.usage + ' : need a source repo to clone from')
        sys.exit(1)
    else:
        source_repo = args.source_repo

    if not args.destdir:
        log.warn(args.usage + ': need a location to clone the repo into.')
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

    # and do the needful
    run(destdir,source_repo,link)
