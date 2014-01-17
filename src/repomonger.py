#!/usr/bin/env python
# vim: set expandtab:

"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

"""
import os
import sys
from ConfigParser import SafeConfigParser
import logging
import shutil
import time

try:
    import rpm
    import yum
    import createrepo
    from createrepo import MDError
    from createrepo.utils import errorprint, _
    import yum.misc

except ImportError as error:
    logging.warn('Python says %s, please ensure you have access to the \
                 yum rpm, and createrepo python modules.' , error)
    sys.exit(1)


PROJECTNAME = 'repomonger'

#try:
#    from pymongo import Connection
#except ImportError as ERROR:
#    print 'Failed import of pymmongo, system says %s' % ERROR
#    sys.exit(1)


# Setup some basic default stuff
CONFIGFILE = '/etc/repomonger/repomonger.conf'


# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)


def run(_args, _config):
    """ Beginning the run """
    log.debug('in run(), running with args %s ' % _args)
    backend = _config.get('backend', 'db_type')
    if backend == 'flatfile':
        database = _config.get('backend', 'database')
    pkgs = get_packagelist(database, backend)
    _dir = '/tmp/wibble'
    assemble_repo(pkgs, _dir, linktype='copy')
    # And finaly, create the repo.
    create_repo(pkgs, _dir)
    log.debug('dest %s ' %  _dir )
    log.debug('Exiting run()')


def assemble_repo(pkglisting, _dir, linktype):
    """ copy or link files to cloned location. """
    log.debug('Entering assemble_repo()')
    msg, success = 'Beginning to assemble repo', 1
    try:
        if not os.path.exists(_dir):
            log.warn('destdir %s does not exist, creating it' % _dir)
            os.makedirs(_dir)
            msg = ('%s created' % _dir)
    except:
        msg = ('Can not create dir %s' % _dir)
    log.debug('in assemble_repo(), message is %s' % msg)

    if linktype == 'copy':
        for pkg in pkglisting:
            shutil.copy(pkg, _dir)
        msg, success = 'pkgs copied', 0
    # Now create the repo
    return msg, success

def create_repo(clone_target, clone_dest):
    """ Run createrepo on _dir, assembling the bits yum needs"""
    msg, success = 'starting to create repo', 1
    log.debug('Entering create_repo()')

    try:
        """createrepo from cli main flow"""
        start_st = time.time()
        conf = createrepo.MetaDataConfig()
        conf.basedir = clone_target
        conf.directory = clone_dest
        mid_st = time.time()
        try:
            mdgen = createrepo.SplitMetaDataGenerator(config_obj=conf,
                                                          callback=MDCallBack())
        except:
            log.warn('something when wrong with mdgen creation')

        try:
            pm_st = time.time()
            mdgen.doPkgMetadata()

            rm_st = time.time()
            mdgen.doRepoMetadata()

            fm_st = time.time()
            mdgen.doFinalMove()
        except:
            log.warn('something when wrong with mdgen usage')

    except:
        log.warn('something went wrong with creating repo %s' % clone_target)




def get_packagelist(database, backend):
    """ Build a dict of the files that are going to be linked or copied
        packagename = fq_Filename"""
    log.debug('Entering get_packagelist()')
    # For now, we are dealing only with flatfile database.
    # append each pkg listed in database to pkglisting, with fq filename
    print database
    pkglisting = [line.rstrip('\n') for line in open(database)]
    log.debug(pkglisting)
    log.debug('Exiting get_packagelist')
    return pkglisting


def get_config(_args, _CONFIGFILE):
    """  Now parse the config file.  Get any and all info from config file."""
    parser = SafeConfigParser()
    if os.path.isfile(_CONFIGFILE):
        config = _CONFIGFILE
    else:
        log.warn('No config file found at %s' % _CONFIGFILE)
        sys.exit(1)
    parser.read(config)
    return parser


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
    parser.add_argument('-r', '--readable', dest='human_readable',
        action='store_true', default=False,
        help='Display output in human readable formant (as opposed to json).')
    parser.add_argument('-c', '--config',
        action='store', default=None,
        help='Specify a path to an alternate config file')
    parser.add_argument('-R', '--repo', action='store', default=None,
        help='Name of repo to build. See definition in config')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME +".py [options]"


    return _args


if __name__ == "__main__":
    # Here we start if called directly (the usual case.)


    args = get_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    if args.config:
        CONFIGFILE = args.config

    _parse_config = get_config(args, CONFIGFILE)

    run(args,_parse_config)
