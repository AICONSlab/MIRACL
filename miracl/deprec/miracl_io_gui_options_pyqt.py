#! /usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8 

import argparse
import sys

from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import *, QtWidgetsfrom PyQt5.QtWidgets import *


# Inputs #########

def helpmsg():
    return '''miracl_conv_gui_options.py -t title -f fields [separated by space] -hf helpfun

Takes list of strings as options for entries for a gui options, and a gui title

example: miracl_conv_gui_options.py -t "Reg options" -f orient label resolution

Input options will be printed as output

'''


def parseargs():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
    parser.add_argument('-t', '--title', type=str, help="gui title", required=True)
    parser.add_argument('-f', '--fields', type=str, nargs='+', help="fields for options", required=True)
    parser.add_argument('-hf', '--helpfun', type=str, help="help fun")

    args = parser.parse_args()

    title = args.title
    fields = args.fields
    helpfun = args.helpfun

    return title, fields, helpfun


def optsmenu(title, fields, helpfun):
    # create GUI
    main = QtWidgets.QMainWindow()

    widget = QtWidgets.QWidget()
    widget.setWindowTitle('%s' % title)

    layout = QFormLayout()
    layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

    linedits = {}

    for f, field in enumerate(fields):
        # Create inputs (line edts)
        linedits["%s" % field] = QLineEdit()
        linedits["%s" % field].setAlignment(QtCore.Qt.AlignRight)

        # Layout for widgets        
        layout.addRow("%s" % field, linedits["%s" % field])

    # Create push button
    helpbutton = QtWidgets.QPushButton('Help')
    submit = QtWidgets.QPushButton('Submit')

    layout.addRow(helpbutton, submit)
    widget.setLayout(layout)

    widget.connect(submit, QtCore.SIGNAL('clicked()'), lambda: print_input(linedits, fields))
    widget.connect(helpbutton, QtCore.SIGNAL('clicked()'), lambda: print_help(main, helpfun))

    return widget


def print_input(linedits, fields):
    for f, field in enumerate(fields):
        text = str(linedits["%s" % field].text())
        print("%s :%s" % (field, text.lstrip()))

    app.quit()


def print_help(main, helpfun):
    helpwidget = QtWidgets.QDialog()
    main.setCentralWidget(helpwidget)
    helpwidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    main.setWindowTitle('Help function')

    helplbl = QtWidgets.QLabel(helpfun)

    scrollarea = QScrollArea()
    scrollarea.setWidgetResizable(False)
    scrollarea.setWidget(helplbl)

    helplayout = QVBoxLayout()
    helplayout.addWidget(scrollarea)

    helpwidget.setLayout(helplayout)

    main.show()

    app.processEvents()


def main():
    [title, fields, helpfun] = parseargs()

    # Create an PyQT4 application object.
    global app
    app = QApplication(sys.argv)
    menu = optsmenu(title, fields, helpfun)
    menu.show()
    app.exec_()
    app.processEvents()


if __name__ == "__main__":
    sys.exit(main())
