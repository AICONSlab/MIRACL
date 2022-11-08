#! /usr/bin/env python
# Maged Goubran @ 2016, maged.goubran@utoronto.ca 

# coding: utf-8 

import argparse
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *


# Inputs #########

def helpmsg():
    return '''miracl_conv_gui_options.py -t title -f [ fields separated by space] -v [volumes to open] -d [dirs to open]
    -hf helpfun

Takes list of strings as options for entries for a gui options, and a gui title

example: miracl_conv_gui_options.py -t "Reg options" -v clar labels -f orient label resolution

Input options will be printed as output

'''


def parsefn():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
    parser.add_argument('-t', '--title', type=str, help="gui title", required=True)
    parser.add_argument('-f', '--fields', type=str, nargs='+', help="fields for options")
    parser.add_argument('-v', '--vols', type=str, nargs='+', help="volumes for reading")
    parser.add_argument('-d', '--dirs', type=str, nargs='+', help="directories for reading")
    parser.add_argument('-c', '--combo', type=str, nargs='+', help="dropdown of options")
    parser.add_argument('-hf', '--helpfun', type=str, help="help fun")

    return parser


def parse_inputs(parser, args):
    args, unknown = parser.parse_known_args()

    title = args.title
    fields = args.fields
    vols = args.vols
    dirs = args.dirs
    combo = args.combo if args.combo else None
    helpfun = args.helpfun

    return title, vols, dirs, fields, combo, helpfun


def OptsMenu(title, vols=None, dirs=None, fields=None, combo=None, helpfun=None):
    # create GUI
    main = QtWidgets.QMainWindow()

    widget = QtWidgets.QWidget()
    widget.setWindowTitle('%s' % title)

    layout = QFormLayout()
    layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

    linedits = {}
    buttons = {}
    labels = {}

    if vols:

        for v, vol in enumerate(vols):
            # Create buttons for vols
            labels["%s" % vol] = QtWidgets.QLabel('No file selected')
            buttons["%s" % vol] = QtWidgets.QPushButton('Select %s' % vol)

            # Layout for widgets
            layout.addRow(labels["%s" % vol], buttons["%s" % vol])

            buttons["%s" % vol].clicked.connect(lambda state, vol=vol: get_fname(main, labels, vol))

    if dirs:

        for d, dir in enumerate(dirs):
            # Create buttons for vols
            labels["%s" % dir] = QtWidgets.QLabel('No Dir selected')
            buttons["%s" % dir] = QtWidgets.QPushButton('Select %s' % dir)

            # Layout for widgets
            layout.addRow(labels["%s" % dir], buttons["%s" % dir])

            buttons["%s" % dir].clicked.connect(lambda state, dir=dir: get_dname(main, labels, dir))

    for f, field in enumerate(fields):
        # Create inputs (line edts)
        linedits["%s" % field] = QLineEdit()
        linedits["%s" % field].setAlignment(QtCore.Qt.AlignRight)

        # Layout for widgets        
        layout.addRow("%s" % field, linedits["%s" % field])

    if combo:
        combo_field = combo[0]
        cb = QtWidgets.QComboBox()
        cb.addItems(combo[1:])
        layout.addRow(combo_field, cb)
    else:
        combo_field = None
        cb = None

    # Create push button
    helpbutton = QtWidgets.QPushButton('Help')
    enter = QtWidgets.QPushButton('Enter')
    submit = QtWidgets.QPushButton('Run')

    layout.addRow(helpbutton, enter)
    layout.addWidget(submit)

    widget.setLayout(layout)

    helpbutton.clicked.connect(lambda: print_help(main, helpfun))
    enter.clicked.connect(lambda: print_input(labels, linedits, vols, dirs, fields, combo_field, cb))
    submit.clicked.connect(QtCore.QCoreApplication.instance().quit)

    return widget, linedits, labels


def get_fname(main, labels, vol):
    vfile = QtWidgets.QFileDialog.getOpenFileName(main, 'Select %s' % vol)[0]
    if vfile:
        vfilestr = "%s : %s" % (vol, str(vfile).lstrip())
        labels["%s" % vol].setText(vfilestr)
        # print('%s path: %s' % (vol, vfile))
    else:
        labels["%s" % vol].setText('No file selected')


def get_dname(main, labels, dir):
    dfile = str(QFileDialog.getExistingDirectory(main, "Select %s" % dir, "."))
    if dfile:
        dfilestr = "%s : %s" % (dir, dfile.lstrip())
        labels["%s" % dir].setText(dfilestr)
        # print('%s path: %s' % (dir, dfile))
    else:
        labels["%s" % dir].setText('No Dir selected')


def print_input(labels, linedits, volumes=None, dirs=None, fields=None, combo_field=None, cb=None):
    if volumes:
        for v, volume in enumerate(volumes):
            text = str(labels[volume].text()).lstrip()
            if text == 'No file selected':
                text = ''
            if volume in text:
                text = text.lstrip("%s :" % volume)
            print("%s :%s" % (volume, text))
    if dirs:
        for d, directory in enumerate(dirs):
            text = str(labels[directory].text()).lstrip()
            if text == 'No Dir selected':
                text = ''
            if directory in text:
                print(text)
                text = text.lstrip("%s :" % directory)
    if fields:
        for f, field in enumerate(fields):
            print("%s :%s" % (field, str(linedits["%s" % field].text()).lstrip()))
    if combo_field and cb:
        print("%s :%s" % (combo_field, cb.currentText()))


def print_help(main, helpfun):
    helpwidget = QtWidgets.QDialog()
    main.setCentralWidget(helpwidget)
    helpwidget.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    main.setWindowTitle('Help function')

    helplayout = QVBoxLayout()
    helplbl = QtWidgets.QLabel(helpfun)
    helplayout.addWidget(helplbl)

    helpwidget.setLayout(helplayout)

    main.show()

    QApplication.processEvents()


def main(args):
    parser = parsefn()
    title, vols, dirs, fields, combo, helpfun = parse_inputs(parser, args)

    # Create an PyQT4 application object.
    app = QApplication(sys.argv)
    menu, linedits, labels = OptsMenu(title=title, vols=vols, dirs=dirs, fields=fields, combo=combo, helpfun=helpfun)
    menu.show()
    app.exec_()
    app.processEvents()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
