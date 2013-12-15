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
PROJECTNAME = 'repomonger'

try:
    from pymongo import Connection
except ImportError as ERROR:
    print 'Failed import of pymmongo, system says %s' % ERROR
    sys.exit(1)


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



def run(_args):
    """ placeholder, need to flesh this out"""
    log.debug('in run(), running with args %s ' % _args)


def get_config(_args, _CONFIGFILE):
    """  Now parse the config file.  Get any and all info from config file.""" 
    parser = SafeConfigParser()
    configuration = {}
    if os.path.isfile(_CONFIGFILE):
        config = _CONFIGFILE
    else:
        log.warn('No config file found at %s' % _CONFIGFILE)
        sys.exit(1)
    try:
        if _args.repo:
            repo = _args.repo
        else:
            repo = parser.get('Repomonger','repo')
    except:
        log.warn('config parse failed')
        sys.exit(1)
    log.warn('building repo %s' % repo)
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

    run(args)
