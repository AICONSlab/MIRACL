#! /usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@utoronto.ca

# coding: utf-8

import argparse
import sys
import os
import pwd
import getpass
import re
from argparse import RawTextHelpFormatter

from datetime import datetime


def helpmsg():
    return '''
    Generates end statement based on function/task and time difference
    '''


def parsefn():
    parser = argparse.ArgumentParser(description=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False,
                                     usage='%(prog)s -f [ function ] -t [ time diff ]')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', '--function', type=str, required=True, metavar='task',
                          help="Done taks")
    required.add_argument('-t', '--timediff', type=str, required=True, metavar='timediff',
                          help="Time diff")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    task = args.function
    timediff = args.timediff

    return task, timediff


def main(args):

    parser = parsefn()
    task, timediff = parse_inputs(parser, args)

    real_name = pwd.getpwuid(os.getuid()).pw_gecos
    getpass_user_name = getpass.getuser()
    environ_user_name = os.environ.get("USER")
    anon_user_name = "dear user of MIRACL"

    try:
        if sys.platform == "linux" or sys.platform == "linux2":
            if re.search('^([^,])+', real_name) is not None:
                user = real_name.split(" ")[0].title()
            elif getpass_user_name:
                user = getpass_user_name
            elif environ_user_name:
                user = os.environ.get("USER")
            else:
                user = os.popen('whoami').readline().rstrip('\n')
        else:
            user = anon_user_name

    except Exception:
        user = anon_user_name

    if 6 < datetime.now().hour < 12:
        timeday = 'morning'
    elif 12 <= datetime.now().hour < 18:
        timeday = 'afternoon'
    elif 18 <= datetime.now().hour < 22:
        timeday = 'evening'
    else:
        timeday = 'night'

    print(f"\n Good job {user}! {task} done in {timediff} ... Have a good {timeday}!\n")


if __name__ == "__main__":
    main(sys.argv)
