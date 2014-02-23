#!/usr/bin/env python
# vim: set expandtab:
""" Koji scan grabs all the packages for a given tag in koji, and creates a
list of path locations for repomonger to use. Needs some info from koji server
on where stuff is stored, but for now, just dumps a list of NVR package names.


License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com
Date:   21 Feb 2014


"""
import os
import sys
from ConfigParser import SafeConfigParser
import logging
import koji

# Setup some basic default stuff
CONFIGFILE = '/etc/repomonger/kojiscan.conf'
PROJECTNAME = 'kojiscan'

# Setup logging
logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

# Setup logging to console.
console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger(PROJECTNAME).addHandler(console)
log = logging.getLogger(PROJECTNAME)


def koji_packagelist():
    """ for now, just get a list of the packages for a given tag """
    log.debug('in koji_packagelist')
    packages = []
    tag = args.kojitag
    kojiserver = args.kojiserver
    log.debug('Opening client session to %s', kojiserver)
    kojiclient = koji.ClientSession(kojiserver, {})
    pkglist = kojiclient.getLatestBuilds(tag)
    for pkg in pkglist:
        packages.append(pkg['nvr'])
    return packages


def run():
    """ Beginning the run """
    if args.config:
        CONFIG = args.config
    else:
        CONFIG = CONFIGFILE
    parsed_config = parse_config(CONFIGFILE)
    log.debug('entering run()')
    kojipkgs = koji_packagelist()
    for pkg in kojipkgs:
        print pkg
    log.debug('Exiting run()')

def get_args():
    """ Parse the command line options """

    import argparse

    parser = argparse.ArgumentParser(
        description='Scan data from koji')
    parser.add_argument('-d', '--debug', dest='debug',
        action='store_true', help='Enable debugging during execution.',
        default=None)
    parser.add_argument('-c', '--config',
        action='store', default=None,
        help='Specify a path to an alternate config file')
    parser.add_argument('-D', '--dst', action='store',
                        dest="destdir", help='Topdir of cloned repo')
    parser.add_argument('-k', '--koji', action='store',
                        dest="kojiserver", help='koji server to get info from')
    parser.add_argument('-t', '--tag', action='store',
                        dest="kojitag", help='koji tag to get info for')

    _args = parser.parse_args()
    _args.usage = PROJECTNAME + ".py [options]"

    return _args


def parse_config(_CONFIGFILE):
    """  Now parse the config file.  Get any and all info from config file.
    Push items into args, but args override config settings"""
    parser = SafeConfigParser()
    if os.path.isfile(_CONFIGFILE):
        config = _CONFIGFILE
    else:
        log.warn('no config file at %s', _CONFIGFILE)
        sys.exit(1)
    parser.read(config)
    return parser

if __name__ == "__main__":
    # Here we start if called directly (the usual case.), currently, the only
    # case.

    args = get_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARN)
    if args.config:
        CONFIGFILE = args.config

    run()
