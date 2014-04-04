#!/usr/bin/env python
# vim: set expandtab:
###
# Copyright (c) 2013, Jim Richardson <weaselkeeper@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

""" Repomonger is a simple repo clone/build script.  You can clone an existing
repo in a new location, using copies, hardlinks, or symlinks.  Or you can
create a new repo from a list of file locations, again, either copying, or
linking to the specified files.


License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com
Date:   18 Jul 2013


"""
import os
import sys
from ConfigParser import SafeConfigParser
import logging
import shutil


# Setup some basic default stuff
CONFIGFILE = '/etc/repomonger/repomonger.conf'
PROJECTNAME = 'repomonger'

# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)

try:
    import rpm
    import createrepo

except ImportError as error:
    logging.warn('Python says %s, please ensure you have access to the \
yum rpm, and createrepo python modules.', error)
    sys.exit(1)

try:
    from pymongo import Connection

except ImportError as error:
    log.warn('Failed import of pymmongo, system says %s', error)



class MDCallBack(object):
    """cli callback object for createrepo, stolen shamelessly from upstream
    Didn't need the rest of it"""
    @classmethod
    def errorlog(cls, thing):
        """error log output"""
        print >> sys.stderr, thing

    @classmethod
    def log(cls, thing):
        """log output"""
        print thing

    @classmethod
    def progress(cls, item, current, total):
        """progress bar"""
        beg = "%*d/%d - " % (len(str(total)), current, total)
        left = 80 - len(beg)
        sys.stdout.write("\r%s%-*.*s" % (beg, left, left, item))
        sys.stdout.flush()


def get_config(_CONFIGFILE):
    """  Now parse the config file.  Get any and all info from config file."""
    parser = SafeConfigParser()
    if os.path.isfile(_CONFIGFILE):
        config = _CONFIGFILE
    else:
        log.warn('No config file found at %s', _CONFIGFILE)
        sys.exit(1)
    parser.read(config)
    return parser


def run(_args, _config):
    """ Beginning the run """

    backend = _config.get('backend', 'db_type')
    if backend == 'flatfile':
        database = _config.get('backend', 'filelist')
    else:
        col = mongo_connection(_config)
        # pull list from col
        database = col
    if _args.linktype:
        linktype = _args.linktype
    else:
        linktype = 'copy'
    # destdir arg overrides config
    if _args.destdir:
        dest_dir = _args.destdir
        log.debug('putting repo in %s', dest_dir)
    else:
        dest_dir = _config.get('reponame', 'dest_dir')
    # Are we cloning, or creating anew?
    if _args.clone:
        log.debug('in run(), cloning repo with args %s ', _args)
        pkgs = get_clonepackagelist(_args.source_repo)
    else:
        log.debug('in run(), creating new repo with args %s:', _args)
        pkgs = get_packagelist(database, backend)
    assemble_pkgs(pkgs, dest_dir, linktype)
    # And finaly, create the repo.
    create_repo(pkgs, dest_dir)
    log.debug('dest %s ', dest_dir)
    log.debug('Exiting run()')


def assemble_pkgs(pkglisting, _dir, linktype):
    """ copy or link files to cloned location. """
    log.debug('Entering assemble_pkgs()')
    msg, success = 'Beginning to assemble repo', 1
    try:
        if not os.path.exists(_dir):
            log.warn('_dir %s does not exist, creating it', _dir)
            os.makedirs(_dir)
            msg = ('%s created' % _dir)

    except OSError, e:
        log.warn(str(e))
        msg = ('Can not create dir %s' % _dir)
    log.debug('in assemble_pkgs(), message is %s', msg)

    if linktype == 'copy':
        for pkg in pkglisting:
            shutil.copy(pkg, _dir)
        msg, success = 'pkgs copied', 0
        log.debug(msg, success)

    elif linktype == 'hardlink':
        for pkg in pkglisting:
            _file = os.path.split(pkg)[1]
            linkedfile = _dir + '/' + _file
            os.link(pkg, linkedfile)
        msg, success = 'pkgs hardinked', 0
        log.debug(msg, success)

    elif linktype == 'symlink':
        for pkg in pkglisting:
            _file = os.path.split(pkg)[1]
            linkedfile = _dir + '/' + _file
            try:

                os.symlink(pkg, linkedfile)
            except OSError, e:
                log.warn(str(e))
                break
        msg, success = 'pkgs symlinked', 0
        log.debug(msg, success)
    log.debug('Exiting assemble_pkgs(), trying to %s pkgs, got error %s ',
              linktype, msg)
    return msg, success


def create_repo(clone_target, clone_dest):
    """ Run createrepo on _dir, assembling the bits yum needs"""
    log.debug('Entering create_repo()')

    try:
        # createrepo from cli main flow
        #start_st = time.time()
        conf = createrepo.MetaDataConfig()
        conf.basedir = clone_target
        conf.directory = clone_dest
        #mid_st = time.time()
        try:
            mdgen = createrepo.SplitMetaDataGenerator(config_obj=conf,
                                                          callback=MDCallBack())
        except:
            log.warn('something when wrong with mdgen creation')

        try:
            #pm_st = time.time()
            mdgen.doPkgMetadata()

            #rm_st = time.time()
            mdgen.doRepoMetadata()

            #fm_st = time.time()
            mdgen.doFinalMove()
        except:
            log.warn('something when wrong with mdgen usage')

    except:
        log.warn('something went wrong with creating repo %s', clone_target)


def get_clonepackagelist(src_repo):
    """ Build a list of the files that are going to be linked or copied
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
                # Ensuring this is an RPM pkg, not just some file with rpm ext.
                ts.hdrFromFdno(fdno)
            except rpm.error, e:
                # Eating errors from signed packages where
                # we don't have the key
                log.debug(package + " " + str(e))
            pkglisting.append(package)
            os.close(fdno)
    log.debug('Exiting get_packagelist')
    return pkglisting


def get_packagelist(database, backend='flatfile'):
    """ Build a dict of the files that are going to be linked or copied
        packagename = fq_Filename"""
    log.debug('Entering get_packagelist()')
    if backend == 'clone':
        # get listing from _args.source_repo
        pkglisting = get_packagelist(args.source_repo)
    # For now, we are dealing only with flatfile database.
    # append each pkg listed in database to pkglisting, with fq filename
    pkglisting = [line.rstrip('\n') for line in open(database)]
    log.debug(pkglisting)
    log.debug('Exiting get_packagelist')
    return pkglisting


def get_args():
    """ Parse the command line options """

    import argparse

    parser = argparse.ArgumentParser(
        description='Time to build a yum repo')
    parser.add_argument('-n', '--dry-run', dest='dryrun',
        action='store_true', help='Dry run, do not actually perform action',
        default=False)
    parser.add_argument('-d', '--debug', dest='debug',
        action='store_true', help='Enable debugging during execution.',
        default=None)
    parser.add_argument('-C', '--clone', action='store_true',
        help='clone existing repo rather than create from a list of pkgs')
    parser.add_argument('-c', '--config',
        action='store', default=None,
        help='Specify a path to an alternate config file')
    parser.add_argument('-R', '--repo', action='store', default=None,
        help='Name of repo to build. See definition in config')
    parser.add_argument('-S', '--src', action='store',
                        dest='source_repo', help='Repo to clone.')
    parser.add_argument('-D', '--dst', action='store',
                        dest="destdir", help='Topdir of cloned repo')
    parser.add_argument('-l', '--linktype',
                        action='store', dest='linktype',
                        default='symlink', help='symlink, hardlink, or copy')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


def mongo_connection(_config):
    """ Connect to mongo backend """
    _host = _config.get('backend', 'db_host')
    _database = _config.get('backend', 'database')
    _collection = _config.get('backend', 'collection')
    try:
        log.debug('connecting to host %s for collection %s', _host,
                _collection)
        con = Connection(_host)
        col = con[_database][_collection]
        return col
    except  Exception as e:
        log.warn('Error, python reports %s', e)
        sys.exit(1)

if __name__ == "__main__":
    # Here we start if called directly (the usual case.)

    args = get_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    if args.config:
        CONFIGFILE = args.config

    _parse_config = get_config(CONFIGFILE)

    sys.exit(run(args, _parse_config))
