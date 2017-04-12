#! /usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8 

import argparse
import sys

from PyQt4.QtGui import *


# ---------
# Inputs #

def helpmsg():
    return '''miracl_io_file_folder_gui -f [file/folder] -s string

Opens gui to choose file / folder & shows input string as message

example: miracl_io_file_folder_gui -f file -s "Please open your picture"

File/Folder path will be printed in output
'''


def parseargs():
    parser = argparse.ArgumentParser(description='pyqt gui', usage=helpmsg())
    parser.add_argument('-f', '--filfol', type=str, help="file or folder", required=True)
    parser.add_argument('-s', '--string', type=str, help="string for message", required=True)

    args = parser.parse_args()

    filfol = args.filfol
    msg = args.string

    return filfol, msg


def showdialog(self, filfol, msg):
    """
    Get file / folder with gui with QFileDialog
    """

    if filfol == 'file':

        filename = QFileDialog.getOpenFileName(self, "%s" % msg, ".")

        if len(filename) > 0:
            print "\n File chosen for reading is: %s" % filename
        else:
            print "No file was chosen"

    else:

        folder = str(QFileDialog.getExistingDirectory(self, "%s" % msg, "."))

        if len(folder) > 0:
            print "\n Folder chosen for reading is: %s" % folder
        else:
            print "No folder was chosen"


def main():
    [filfol, msg] = parseargs()

    # Create an PyQT4 application object.
    QApplication(sys.argv)
    w = QWidget()

    showdialog(w, filfol, msg)


if __name__ == "__main__":
    sys.exit(main())
