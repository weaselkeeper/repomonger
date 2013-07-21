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
import shutil
import logging
import argparse
import ConfigParser

import rpm
import yum
import createrepo

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'
                    )

console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("clone_repo").addHandler(console)
log = logging.getLogger("clone_repo")


class ConfigFile(object):
    """ Object to handle config file """
    log.debug('in class ConfigFile()')

    filename = None
    configparser = None

    def __init__(self, filename):
        """Initialize ConfigFile object"""
        log.debug('in ConfigFile().init(self, %s)' % filename)
        self.filename = filename
        self.configparser = self.get_config(filename)

    def get_config(self, configfile):
        """ Load config file for parsing """
        log.debug('in ConfigFile().get_config(self, %s)' % configfile)
        config = ConfigParser.ConfigParser()
        config.read(configfile)
        log.debug('returning config %s' % config)
        return config

    def get_item(self, cfgitem, section='default', hard_fail=False):
        """Retrieve value for requested key from the config file"""
        log.debug('in ConfigFile().get_item(self, %s, %s, %s)' % (cfgitem,
                  section, hard_fail))

        def do_fail(err):
            log.debug('in ConfigFile().get_item().do_fail(%s)' % err)
            if hard_fail:
                log.error(err)
                sys.exit(1)
            else:
                log.debug(err)

        item = None
        try:
            item = self.configparser.get(section, cfgitem)
        except ConfigParser.NoOptionError, e:
            do_fail(e)
        except ConfigParser.NoSectionError, e:
            do_fail(e)

        log.debug('returning item: %s' % item)
        return item


class mungerepo(object):
    """ repo object, allows us to manipulate, clone, edit, a repo """
    log.debug('mungerepo class')

    def __init__(self, plugin, path):
        """ initialize the repo
        Plugin lets us munge a repo in various ways, create, clone, destroy,
        edit """
        log.debug('in mungerepo().__init__')
        import imp
        self.module = imp.load_source(plugin, path)

    def run(self):
        """ execute the plugin's run method """
        log.debug('In mungerepo().run()')
        self.status, self.message = self.module.run(self.options)

    def get_run_status(self):
        """ Retreive the return status/message of the moduel that was
        executed"""
        log.debug('in mungerepo().get_run_status*(')

        final_status = {}
        final_status['status'] = self.status
        final_status['message'] = self.message

        return final_status

    def assemble_repo(pkglisting, destdir, link):
        """ copy or link files to cloned location. """
        message, success = 'failed for some reason', 1
        try:
            if not os.path.exists(destdir):
                os.makedirs(destdir)
        except:
            log.warn('Can not create dir %s' % destdir)

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
                except OSError, e:
                    log.warn(str(e))
                    break
            message, success = 'pkgs symlinked', 0
        return message, success

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
                    log.debug(package + " " + str(e))
                pkglisting.append(package)
                os.close(fdno)
        log.debug(pkglisting)
        return pkglisting

    def create_repo(destdir):
        """ Run createrepo on destdir, assembling the bits yum needs"""
        message, success = 'createrepo failed', 1
        import subprocess
        mkrepo = subprocess.Popen(['/usr/bin/createrepo', destdir],
                                  stdout=subprocess.PIPE).communicate()[0]
        return mkrepo, success

    def create_repofile(reponame, dest_dir):
        """ Create a <name>.repo file to be used by yum on clients """
        repofile = "nothing yet"
        return repofile


def get_options():
    """ command-line options """
    parser = argparse.ArgumentParser(description='Pass cli options to \
        script')

    parser.add_argument('-s', '--src', action="store",
                        dest="source_repo", help='Repo to clone.')

    parser.add_argument('-d', '--dst', action="store",
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

    parser.add_argument('--debug', action="store_true", default=False)

    args = parser.parse_args()
    args.usage = "clone_repo.py [options]"
    return args


if "__main__" in __name__:
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

    # Assemble the package list, with locations
    pkgs = mungerepo().get_packagelist(args.source_repo)
    # Send package list, along with destdir and linktype
    # to assemble_repo to build the file structure.

    mungerepo().assemble_repo(pkgs, destdir, link)

    mungerepo().create_repo(destdir)
