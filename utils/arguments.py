#!/usr/bin/env python3

import sys
import argparse
from argparse import RawTextHelpFormatter


# Custom usage / help menu.
class HelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = ''
        return super(HelpFormatter, self).add_usage(
            usage, actions, groups, prefix)


# Custom help menu.
custom_usage = f"""
                                                    
   / \\(((_)))___ ___  ___ _    __    ___ __ __
  / _ \\ | | '__/ __| '_ ` _ \\ / _` |/ __| |/ /
 / ___ \\| | |  \\__ \\ | | | | | (_| | (__|   < 
/_/   \\_\\_|_|  |___/_| |_| |_|\\__,_|\\___|_|\\_\\
{'-'*50}\n
Usage Examples: 
  python airsmack.py -i wlan0 -p5
  
"""

# Define parser
parser = argparse.ArgumentParser(formatter_class=HelpFormatter, description='', usage=custom_usage, add_help=False)

# Mode-Select Options.
# mode_group = parser.add_argument_group('Modes')
# mode_group.add_argument('mode', type=str.lower, default='', choices=[''], metavar='{, }', help='Set mode []')

# Interface Options.
interface = parser.add_argument_group('Interface Arguments')
interface.add_argument('-i', dest='interface', type=str, required=True, default='wlan0', metavar='', help='Set interface <wlan0>')

# Aireplay-ng Options.
aireplay = parser.add_argument_group('Aireplay-ng Arguments')
aireplay.add_argument('-p', dest='packets', type=str, required=True, default='5', metavar='', help='Set number of deauthentication packets <5>')

# Global Options.
group1 = parser.add_argument_group('Global Arguments')
group1.add_argument('--debug', dest='loglevel', action='store_true', help='Set logging level [DEBUG]')

# Print 'help' if no options are defined.
if len(sys.argv) == 1 \
or sys.argv[1] == '-h' \
or sys.argv[1] == '--help':
  parser.print_help(sys.stderr)
  sys.exit(1)