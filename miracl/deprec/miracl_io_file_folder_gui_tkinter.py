#!/usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@utoronto.ca 

# coding: utf-8

import argparse
import sys
import tkFileDialog
from Tkinter import Tk
from tkFileDialog import askopenfilename


### Inputs #########

def helpmsg(name=None):
    return '''miracl_conv_file_folder_gui -f [file/folder] -s string

Opens gui to choose file / folder & shows input string as message

example: miracl_conv_file_folder_gui -f file -s "Please open your picture"

File/Folder path will be printed in output
'''


parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-f', '--filfol', type=str, help="file or folder", required=True)
parser.add_argument('-s', '--string', type=str, help="string for message", required=True)

args = parser.parse_args()

filfol = args.filfol
msg = args.string


def openfile(msg):
    '''
    Opens file with gui with tkinter
    '''
    # read file
    Tk().withdraw()
    filename = askopenfilename(title='%s' % msg)

    if len(filename) > 0:
        print("\n File chosen for reading is: %s" % filename)
    else:
        print("No file was chosen")

        # with open("path.txt", "w") as myfile:
        #     myfile.write(filename)


def openfolder(msg):
    '''
    Opens folder with gui with tkinter
    '''

    # read Dir
    Tk().withdraw()
    dirname = tkFileDialog.askdirectory(title='%s' % msg)

    if len(dirname) > 0:
        print("\n Directory chosen for reading is: %s" % dirname)
    else:
        print("No folder was chosen")

        # with open("path.txt", "w") as myfile:
        #     myfile.write(dirname)


def main():
    try:
        if (filfol == 'file'):
            openfile(msg)
        else:
            openfolder(msg)

        return 0

    except:
        return 1


if __name__ == "__main__":
    sys.exit(main())
