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
except ImportError as e:
    print 'Failed import of pymmongo, system says %s' % e
    sys.exit(1)


# Setup some basic default stuff
CONFIGFILE = '/etc/repomonger/repomonger.conf'


""" Setup logging """
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)



def run(args):
    """ placeholder, need to flesh this out"""
    log.debug('in run(), running')


def get_config(args,CONFIGFILE):
    # Now parse the config file.  Get any and all info from config file.
    parser = SafeConfigParser()
    configuration = {}
    if os.path.isfile(CONFIGFILE):
        config = CONFIGFILE
    else:
        log.warn('No config file found at %s' % CONFIGFILE)
        sys.exit(1)
    try:
        if args.repo:
            repo = args.repo
        else:
            repo = parser.get('Repomonger','repo')
    except:
        log.warn('config parse failed')
        sys.exit(1)
    log.warn('building repo %s' % repo)
    parser.read(config)
    return parser



# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    """This is where we will begin when called from CLI"""


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

    args = parser.parse_args()
    args.usage = "repomonger.py [options]"


    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    if args.config:
        CONFIGFILE = args.config

    _parse_config = get_config(args,CONFIGFILE)

    run(args)
