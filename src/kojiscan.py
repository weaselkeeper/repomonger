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
CONFIGFILE = '/etc/repomonger/repomonger.conf'
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


def koji_conn(server):
    """ create connection to koji server """
    log.debug('Starting in koji_conn')
    conn = koji.ClientSession(server, {})
    log.debug('leaving koji_conn')
    return conn


def koji_packagelist(kojiclient, tag):
    """ for now, just get a list of the packages for a given tag """
    log.debug('in koji_packagelist looking for %s', tag)
    packages = []
    log.debug('Opening client session to ')
    pkglist = kojiclient.getLatestRPMS(tag)
    for pkg in pkglist[1]:
        packages.append(pkg['name'])
        log.debug(pkg['name'])
    log.debug('leaving koji_packagelist')
    return packages


def koji_rpmlist(conn, tag, basepath, pkg):
    """ get a list of rpms for package, and make full pathname to return """
    log.debug('in koji_rpmlist')
    files = []
    details = conn.getLatestRPMS(tag, package=pkg)
    for rpm_pkg in details[0]:
        filename = rpm_pkg['name'] + '-' + rpm_pkg['version'] + '-' +\
            rpm_pkg['release'] + '.' + rpm_pkg['arch'] + '.rpm'
        path = basepath, pkg, rpm_pkg['version'], rpm_pkg['release'], \
            rpm_pkg['arch']
        pathname = '/'.join(path)
        fullpath = pathname + '/' + filename
        files.append(fullpath)
        log.debug(fullpath)
    log.debug('leaving koji_rpmlist')
    return files


def run(_args):
    """ Beginning the run """
    log.debug('entering run()')
    _filelist = []
    if _args.config:
        CONFIG = _args.config
    else:
        CONFIG = CONFIGFILE
    if _args.basepath:
        basepath = _args.basepath
    else:
        basepath = '/mnt/koji/packages'

    parsed_config = parse_config(CONFIG)

    if _args.kojitag:
        tag = _args.kojitag
    else:
        tag = parsed_config.get('koji', 'tag')

    if _args.kojiserver:
        server = _args.kojiserver
    else:
        server = parsed_config.get('koji', 'serverurl')

    conn = koji_conn(server)

    kojipkgs = koji_packagelist(conn, tag)
    for pkg in kojipkgs:
        pkgrpms = koji_rpmlist(conn, tag, basepath, pkg)
        for pkg in pkgrpms:
            _filelist.append(pkg)
    if _args.debug:
        for _file in _filelist:
            log.debug(_file)
    log.debug('Exiting run()')
    return _filelist


def get_args():
    """ Parse the command line options """

    import argparse

    parser = argparse.ArgumentParser(
        description='Scan data from koji')
    parser.add_argument('-d', '--debug', dest='debug',
                        action='store_true', help='Enable debugging.',
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
    parser.add_argument('-b', '--basepath', action='store',
                        help='basepath of koji packages')

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

    filelist = run(args)
