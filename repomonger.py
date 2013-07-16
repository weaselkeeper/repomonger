#!/usr/bin/env python
# vim: set expandtab:
"""
**********************************************************************
GPL License
***********************************************************************
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

***********************************************************************/

:author: Jim Richardson
:email: weaselkeeper@gmail.com

"""
import os
import sys

#used in ConfigFile()
import ConfigParser

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s %(levelname)s - %(message)s',
                    datefmt='%y.%m.%d %H:%M:%S'

console = logging.StreamHandler(sys.stderr)
console.setLevel(logging.WARN)
logging.getLogger("usefulidiot").addHandler(console)
log = logging.getLogger("usefulidiot")






# Here we start if called directly (the usual case.)
if __name__ == "__main__":
    """This is where we will begin when called from CLI"""

    import argparse



    cmd_parser = argparse.ArgumentParser(
        description='Time to build a yum repo')
    cmd_parser.add_argument('-n', '--dry-run',dest='dryrun',
        action='store_true', help='Dry run, do not actually perform action',default=False)
    cmd_parser.add_argument('-d', '--debug', dest='debug',
        action='store_true', help='Enable debugging during execution.',
        default=None)
    cmd_parser.add_argument('-r', '--readable', dest='human_readable',
        action='store_true', default=False,
        help='Display output in human readable formant (as opposed to json).')
    cmd_parser.add_argument('-c', '--config', dest='config_override',
        action='store', default=None,
        help='Specify a path to an alternate config file')
