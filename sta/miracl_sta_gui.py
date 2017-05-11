#! /usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8 

import sys

from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *


class STAmenu(QtGui.QWidget):

    def __init__(self):
        # create GUI
        QtGui.QMainWindow.__init__(self)
        # check
        super(STAmenu, self).__init__()

        self.setWindowTitle('STA analysis')
        # Set the window dimensions
        # self.resize(500,200)

        # Create a label which displays the path to our chosen file
        self.lbl = QtGui.QLabel('No CLARITY nii selected')
        self.lbl2 = QtGui.QLabel('No Seed Mask selected')
        self.lbl3 = QtGui.QLabel('No Brain Mask selected')

        # Create a push button labelled 'choose' and add it to our layout
        btn = QtGui.QPushButton('Select CLARITY nii', self)
        btn2 = QtGui.QPushButton('Select Seed Mask', self)
        btn3 = QtGui.QPushButton('Select Brain Mask', self)

        run = QtGui.QPushButton('Run', self)

        # Create inputs (line edts)
        self.dog = QLineEdit()
        self.dog.setAlignment(QtCore.Qt.AlignRight)
        self.gauss = QLineEdit()
        self.gauss.setAlignment(QtCore.Qt.AlignRight)
        self.angle = QLineEdit()
        self.angle.setAlignment(QtCore.Qt.AlignRight)

        # layout for widgets        
        self.layout = QtGui.QFormLayout()
        self.layout.addRow(self.lbl, btn)
        self.layout.addRow(self.lbl2, btn2)
        self.layout.addRow(self.lbl3, btn3)
        self.layout.addRow("Derivative of Gauss sigma", self.dog)
        self.layout.addRow("Gaussian smoothing sigma", self.gauss)
        self.layout.addRow("Tracking angle threshold", self.angle)
        self.layout.addRow(run)
        self.setLayout(self.layout)

        # Connect the clicked signal to the get_fname handler
        self.connect(btn, QtCore.SIGNAL('clicked()'), self.get_fname)
        self.connect(btn2, QtCore.SIGNAL('clicked()'), self.get_fname2)
        self.connect(btn3, QtCore.SIGNAL('clicked()'), self.get_fname3)
        self.connect(run, QtCore.SIGNAL('clicked()'), self.print_input)

    def get_fname(self):
        clar = QtGui.QFileDialog.getOpenFileName(self, 'Select CLARITY nii')
        if clar:
            clarstr = "CLARITY nii: " + clar
            self.lbl.setText(clarstr)
            print 'clarity path :%s' % str(clar).lstrip()
        else:
            self.lbl.setText('No file selected')

    def get_fname2(self):
        seed = QtGui.QFileDialog.getOpenFileName(self, 'Select Seed Mask')
        if seed:
            seedstr = "Seed Mask: " + seed
            self.lbl2.setText(seedstr)
            print 'seed path :%s' % str(seed).lstrip()
        else:
            self.lbl2.setText('No file selected')

    def get_fname3(self):
        brainmask = QtGui.QFileDialog.getOpenFileName(self, 'Select Brain Mask')
        if brainmask:
            brainstr = "Brain Mask: " + brainmask
            self.lbl3.setText(brainstr)
            print 'brain path :%s' % str(brainmask).lstrip()
        else:
            self.lbl3.setText('No file selected')

    def print_input(self):

        dogin = str(self.dog.text())
        gaussin = str(self.gauss.text())
        anglein = str(self.angle.text())

        print 'dog :%s' % dogin.lstrip()
        print 'gauss :%s' % gaussin.lstrip()
        print 'angle :%s' % anglein.lstrip()

        app.quit()

def main():
    # Create an PyQT4 application object.
    global app
    app = QApplication(sys.argv)
    sta = STAmenu()
    sta.show()
    app.exec_()


if __name__ == "__main__":
    sys.exit(main())
