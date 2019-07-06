#! /usr/bin/env python
# Maged Goubran @ 2017, mgoubran@stanford.edu

# coding: utf-8

import argparse
import sys
import os
import pwd
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
    required.add_argument('-f', '--func', type=str, required=True, metavar='task',
                          help="Done taks")
    required.add_argument('-t', '--timediff', type=str, required=True, metavar='timediff',
                          help="Time diff")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    task = args.func
    timediff = args.timediff

    return task, timediff


def main(args):

    parser = parsefn()
    task, timediff = parse_inputs(parser, args)

    # try:
    #     fing = subprocess.Popen("finger $(whoami)",
    #                             shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #
    #     string = fing.communicate()[0]
    #     sub = string.split("Name: ", 1)[1]
    #     user = sub.split(" ", 1)[0]
    #
    #     if user is None:
    #         user = os.environ['USER']
    #
    # except:
    #     user = os.environ['USER']
    #     # user = subprocess.Popen('whoami',
    #     #         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    name = pwd.getpwuid(os.getuid())[4]

    if re.search('[a-zA-Z]', name):
        user = name.split(" ")[0]
    else:
        user = os.environ['USER']

    if 6 < datetime.now().hour < 12:
        timeday = 'morning'
    elif 12 <= datetime.now().hour < 18:
        timeday = 'afternoon'
    elif 18 <= datetime.now().hour < 22:
        timeday = 'evening'
    else:
        timeday = 'night'

    print("\n Good job %s! %s done in %s ... Have a good %s!\n" % (user, task, timediff, timeday))


if __name__ == "__main__":
    main(sys.argv)
