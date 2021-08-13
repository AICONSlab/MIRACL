#! /usr/bin/env python
# Maged Goubran @ 2017, mgoubran@stanford.edu

# coding: utf-8 

import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class STAmenu(QtWidgets.QWidget):

    def __init__(self):
        # create GUI
        QtWidgets.QMainWindow.__init__(self)
        # check
        super(STAmenu, self).__init__()

        self.setWindowTitle('STA analysis')
        # Set the window dimensions
        # self.resize(500,200)

        # Create a label which displays the path to our chosen file
        self.lbl = QtWidgets.QLabel('No CLARITY nii selected')
        self.lbl2 = QtWidgets.QLabel('No Seed Mask selected')
        self.lbl3 = QtWidgets.QLabel('No Brain Mask selected')

        # Create a push button labelled 'choose' and add it to our layout
        btn = QtWidgets.QPushButton('Select CLARITY nii', self)
        btn2 = QtWidgets.QPushButton('Select Seed Mask', self)
        btn3 = QtWidgets.QPushButton('Select Brain Mask', self)

        run = QtWidgets.QPushButton('Run', self)

        # Create inputs (line edts)
        self.outdir = QLineEdit()
        self.outdir.setAlignment(QtCore.Qt.AlignRight)
        self.dog = QLineEdit()
        self.dog.setAlignment(QtCore.Qt.AlignRight)
        self.gauss = QLineEdit()
        self.gauss.setAlignment(QtCore.Qt.AlignRight)
        self.angle = QLineEdit()
        self.angle.setAlignment(QtCore.Qt.AlignRight)
        self.step_length = QLineEdit()
        self.step_length.setAlignment(QtCore.Qt.AlignRight)

        # layout for widgets        
        self.layout = QtWidgets.QFormLayout()
        self.layout.addRow(self.lbl, btn)
        self.layout.addRow(self.lbl2, btn2)
        self.layout.addRow(self.lbl3, btn3)
        self.layout.addRow("Output directory name (default: clarity_sta)", self.outdir)
        self.layout.addRow("Derivative of Gaussian sigma (ex: 1 or 0.5 1 1.5)", self.dog)
        self.layout.addRow("Gaussian smoothing sigma (ex: 1 or 0.5 1 1.5)", self.gauss)
        self.layout.addRow("Tracking angle threshold (ex: 25 or 25 35 45)", self.angle)
        self.layout.addRow("Step length (ex: 0.1 or 0.1 0.01 0.05)", self.step_length)
        self.layout.addRow(run)
        self.setLayout(self.layout)

        # Connect the clicked signal to the get_fname handler
        btn.clicked.connect(self.get_fname)
        btn2.clicked.connect(self.get_fname2)
        btn3.clicked.connect(self.get_fname3)
        run.clicked.connect(self.print_input)

        # store the results of the STA flags in an obj similar to args
        self.inputs = type('', (), {})()

    def get_fname(self):
        clar = QtWidgets.QFileDialog.getOpenFileName(self, 'Select CLARITY nii')[0]
        if clar:
            clarstr = "CLARITY nii: " + clar
            self.lbl.setText(clarstr)
            self.inputs.input_clar = clar
            print('clarity path :%s' % str(clar).lstrip())
        else:
            self.lbl.setText('No file selected')

    def get_fname2(self):
        seed = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Seed Mask')[0]
        if seed:
            seedstr = "Seed Mask: " + seed
            self.lbl2.setText(seedstr)
            self.inputs.seedmask = seed
            print('seed path :%s' % str(seed).lstrip())
        else:
            self.lbl2.setText('No file selected')

    def get_fname3(self):
        brainmask = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Brain Mask')[0]
        if brainmask:
            brainstr = "Brain Mask: " + brainmask
            self.lbl3.setText(brainstr)
            self.inputs.brainmask = brainmask
            print('brain path :%s' % str(brainmask).lstrip())
        else:
            self.lbl3.setText('No file selected')

    def print_input(self):

        outdir = str(self.outdir.text())
        dogin = str(self.dog.text())
        gaussin = str(self.gauss.text())
        anglein = str(self.angle.text())
        step_length = str(self.step_length.text())
        self.inputs.outdir = outdir if outdir else 'clarity_sta'
        self.inputs.dogs = dogin.split()
        self.inputs.gausses = gaussin.split()
        self.inputs.angles = anglein.split()
        self.inputs.rk2 = False
        self.inputs.step_length = step_length.split()
        

        print('dog :%s' % dogin.lstrip())
        print('gauss :%s' % gaussin.lstrip())
        print('angle :%s' % anglein.lstrip())

        app.quit()

def main():
    # Create an PyQT4 application object.
    global app
    app = QApplication(sys.argv)
    sta = STAmenu()
    sta.show()
    app.exec_()

    return sta.inputs


class STATractDensityMenu(QtWidgets.QWidget):

    def __init__(self):
        # create GUI
        QtWidgets.QMainWindow.__init__(self)
        # check
        super(STATractDensityMenu, self).__init__()

        self.setWindowTitle('STA analysis')
        # Set the window dimensions
        # self.resize(500,200)

        # Create a label which displays the path to our chosen file
        self.lbl1 = QtWidgets.QLabel('No tractography file selected')
        self.lbl2 = QtWidgets.QLabel('No reference nifti volume selected')

        # Create a push button labelled 'choose' and add it to our layout
        btn = QtWidgets.QPushButton('Select tractography file', self)
        btn2 = QtWidgets.QPushButton('Select reference nifti volume', self)

        run = QtWidgets.QPushButton('Run', self)

        # Create inputs (line edts)
        self.out_dens = QLineEdit()
        self.out_dens.setAlignment(QtCore.Qt.AlignRight)

        # layout for widgets        
        self.layout = QtWidgets.QFormLayout()
        self.layout.addRow(self.lbl1, btn)
        self.layout.addRow(self.lbl2, btn2)
        self.layout.addRow("Output tract density nifti filename", self.out_dens)
        self.layout.addRow(run)
        self.setLayout(self.layout)

        # Connect the clicked signal to the get_fname handler
        btn.clicked.connect(self.get_tractography)
        btn2.clicked.connect(self.get_reference)
        run.clicked.connect(self.print_input)

        # store the results of the STA flags in an obj similar to args
        self.inputs = type('', (), {})()

    def get_tractography(self):
        tracts = QtWidgets.QFileDialog.getOpenFileName(self, 'Select tractography file')[0]
        if tracts:
            tracts_str = "Tractography file: " + tracts
            self.lbl1.setText(tracts_str)
            self.inputs.tracts = tracts
            print('tractography file :%s' % str(tracts).lstrip())
        else:
            self.lbl1.setText('No file selected')

    def get_reference(self):
        ref_vol = QtWidgets.QFileDialog.getOpenFileName(self, 'Select reference nifti volume')[0]
        if ref_vol:
            ref_vol_str = "Reference image: " + ref_vol
            self.lbl2.setText(ref_vol_str)
            self.inputs.ref_vol = ref_vol
            print('Reference image :%s' % str(ref_vol).lstrip())
        else:
            self.lbl2.setText('No file selected')

    def print_input(self):

        out_dens = str(self.out_dens.text())
        if out_dens:
            self.inputs.out_dens = out_dens
        else:
            self.inputs.out_dens = 'sta_streamlines_density_map.nii.gz'

        print('Output tract density :%s' % out_dens)

        app.quit()

def tractDensityMain():
    # Create an PyQT4 application object.
    global app
    app = QApplication(sys.argv)
    sta = STATractDensityMenu()
    sta.show()
    app.exec_()

    return sta.inputs


if __name__ == "__main__":
    sys.exit(main())


