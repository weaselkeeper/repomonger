#!/usr/bin/env python
# vim: set expandtab:

"""

License: GPL V2 See LICENSE file
Author: Jim Richardson
email: weaselkeeper@gmail.com

"""
import os
import sys

# Default config file location.
configfile = '/etc/repomonger.conf'

#used in ConfigFile()
import ConfigParser

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S')

console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("usefulidiot").addHandler(console)
log = logging.getLogger("usefulidiot")


def config(config=configfile):
    # Now parse the config file, extracting the name of the repo, and the list
    # of files ( and locations)  it should contain.
    log.debug('building repo %s' % config.repo)


# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    """This is where we will begin when called from CLI"""

    import argparse

    cmd_parser = argparse.ArgumentParser(
        description='Time to build a yum repo')
    cmd_parser.add_argument('-n', '--dry-run', dest='dryrun',
        action='store_true', help='Dry run, do not actually perform action',
        default=False)
    cmd_parser.add_argument('-d', '--debug', dest='debug',
        action='store_true', help='Enable debugging during execution.',
        default=None)
    cmd_parser.add_argument('-r', '--readable', dest='human_readable',
        action='store_true', default=False,
        help='Display output in human readable formant (as opposed to json).')
    cmd_parser.add_argument('-c', '--config', dest='config_override',
        action='store', default=None,
        help='Specify a path to an alternate config file')
    cmd_parser.add_argument('-R', '--repo', dest='reponame',
        action='store', default=None,
        help='Name of repo to build. See definition in config')
