#! /usr/bin/env python

# coding: utf-8 

from pprint import pprint
import sys
import os
import matplotlib
from  matplotlib import colorbar
import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtCore, QtGui
import numpy as np
from math import nan

#heatmap GUI HELP window
class help_window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heatmap GUI Help")
        help_label=QtWidgets.QLabel()
        help_label.setText(
    '''
Returns mean group heatmap plots, mean-smoothed-masked nii files, and svg qc check registration on input data (expect input data file to be formatted as .nii.gz)

----------

Required arguments:
Group 1 Input Data Folder
Voxel Size/Resolution in um

Optional arguments:
Group 2 Input Data Folder
NOTE: If Group 1 and Group 2 are used then will return heatmaps and mean nii files for Group 1, Group 2, and the difference (Group 2- Group 1)

Gaussian Smoothing Sigma (Default: 4) 
Percentile (%) threshold for registration-to-input data check svg animation (Default: 10)
NOTE: Percentile must be non-negative integer below 100. If reg_check_... file has low visibility reduce default threshold

Colourmap for positive values (Default: Reds)
NOTE: website for custom colourmap options https://matplotlib.org/stable/tutorials/colors/colormaps.html   
Colourmap for negative values (Default: Blues)
NOTE: website for custom colourmap options https://matplotlib.org/stable/tutorials/colors/colormaps.html   

CUSTOM SLICING (Default: nan)
Click Checkbox [] Enable Custom Sagittal/Coronal/Axial Slicing to use
Note: Max slice index dependent on Voxel size/Resolution: 
10um max slice index -> sagittal: 1139 , coronal: 1319 , axial: 799 
25um max slice index -> sagittal: 455 , coronal: 527 , axial: 319
50um max slice index -> sagittal: 227 , coronal: 263 , axial: 159

axes slicing usage: start_slice, slice_increment, number_of_slices, number_of_rows, number_of_columns

Note: All arguments must be greater than zero. 
      number_of_rows x number_of_columns must be equal to or greater than number_of_slices

    Ex. Enabled Custom Sagittal Slicing: 60 50 7 2 4  
        sagittal direction start at slice #60, increment by 50, 7 slices total, 2 rows, 4 columns. 
        slice indexes chosen: 60, 110, 160, 210,   (row #1)
                                            260, 310, 360        (row #2) 
DEFAULT SLICING     
NOTE: If None of the custom slicing axes are enabled then default slicing parameters are used 


Figure dimensions: width, height (Max: 60 x 60. Default dependent on number of slices and axes)
CUSTOM FIGURE DIMENSIONS
Click Checkbox [] Enable Custom Figure Dimensions to use.

Output Directory (Default: current working directory)

Output filenames (Default: group_1) 
NOTE 1: use underscore for names instead of space 
NOTE 2: If only Group 1 used then specify Output Filename Group 1. If Group 2 specify all 3 arguments (Output Filename Group 1, Output Filename Group 2, Output Filename Difference of Groups (Group 2 - Group 1))
Ex. ACCEPTABLE   "control_group"       
    UNACCEPTABLE "control group" 

Figure extension (png, jpg, tiff, pdf, etc... (according to matplotlib.savefig documentation). Default: tiff) 

DPI dots per inch (Default: 500). If plotting over 100 images recommended to increase default DPI. If outline/edge is faint increase default DPI
''')

        self.layout = QtWidgets.QFormLayout()
        self.layout.addRow(help_label)
        self.setLayout(self.layout)

#heatmap GUI setup
class STATSHeatmapMenu(QtWidgets.QWidget):

    def __init__(self):
    # create GUI
        QtWidgets.QMainWindow.__init__(self)
        super(STATSHeatmapMenu, self).__init__()
        self.setWindowTitle('STATS Heatmap Group Analysis')

        mandatory_box = QtWidgets.QGroupBox("Mandatory Arguments")
        self.optional_box = QtWidgets.QGroupBox("Optional Arguments")
        self.opt_hide = QtWidgets.QCheckBox("Show Optional Arguments")
        self.opt_hide_status = self.opt_hide.isChecked()
        # Create labels which displays the path to our chosen file
        self.lbl1 = QtWidgets.QLabel('No folder selected for Group 1 input data')
        self.lbl2 = QtWidgets.QLabel('No folder selected for Group 2 input data')
        self.lbl3 = QtWidgets.QLabel('No folder selected for Output. Default: Current Working Directory')
        
        # Create labels for notes/text
        group2_note= QtWidgets.QLabel('NOTE: If Group 2 folder is selected then will generate heatmaps for Group 1, Group 2, and the Difference of Groups (Group 2 - Group 1)')
        title_cmap=QtWidgets.QLabel('Use Website or Button Below to Explore Colourmap Options')
        website=QtWidgets.QLabel('https://matplotlib.org/stable/tutorials/colors/colormaps.html') 
        website.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        custom_slice=QtWidgets.QLabel('NOTE: If None of the custom slicing axes are enabled (sagittal, coronal, axial) then the default slicing parameters will be used')
        default_dim=QtWidgets.QLabel('NOTE: Default Dimensions are calculated based on number of rows and columns')
        output_note=QtWidgets.QLabel('NOTE: Output Filenames MUST NOT uses spaces. Use underscore instead')
        group2_selected=QtWidgets.QLabel('NOTE: Must Specify All Output Filenames if Group 2 input data folder is selected')
        [x.setFont(QtGui.QFont("Sans Serif 10",weight=QtGui.QFont.Black)) for x in [group2_note, custom_slice, default_dim, output_note, group2_selected]]

        # Create push buttons for Folder Selection
        self.btn1 = QtWidgets.QPushButton('Select Group 1 input data folder', self)
        self.btn2 = QtWidgets.QPushButton('Select Group 2 input data folder', self)
        self.btn3 = QtWidgets.QPushButton('Select Output folder', self)

        #colourmap push button option
        btn4 = QtWidgets.QPushButton('Matplotlib Pyplot Colourmap Options', self)

        # Enable/Disabled Checkbox Options
        self.sagittal_enable = QtWidgets.QCheckBox("Enable  Custom Sagittal Slicing")
        self.sagittal_status = self.sagittal_enable.isChecked()
        self.coronal_enable = QtWidgets.QCheckBox("Enable Custom Coronal Slicing")
        self.coronal_status = self.coronal_enable.isChecked()
        self.axial_enable = QtWidgets.QCheckBox("Enable Custom Axial Slicing")
        self.axial_status = self.axial_enable.isChecked()
        self.fig_enable=QtWidgets.QCheckBox("Enable Custom Figure Dimensions")
        self.fig_status = self.fig_enable.isChecked()

        # Run GUI Button
        run = QtWidgets.QPushButton('Run', self)
        run.setStyleSheet("background-color: rgb(53,190,68);")
        #Help/Documention Button & Layout
        help_doc = QtWidgets.QPushButton('Help', self)
        help_doc.setStyleSheet("background-color: rgb(255,255,90);")
        help_run_layout = QtWidgets.QHBoxLayout()
        help_run_layout.addWidget(help_doc)
        help_run_layout.addWidget(run)

        # Create other inputs (Spinbox/line edits)
        self.gauss = QtWidgets.QDoubleSpinBox()
        self.gauss.setMinimum(0)
        self.gauss.setValue(4)
        self.gauss.setAlignment(QtCore.Qt.AlignRight)
        self.voxels = QtWidgets.QComboBox()
        self.voxels.setEditable(True)
        self.voxels.lineEdit().setReadOnly(True)
        self.voxels.showPopup = self.showPopupAndCheck
        self.voxels.addItems(["", "10", "25", "50"])
        self.voxels.setCurrentIndex(0)
        self.percentile=QtWidgets.QSpinBox()
        self.percentile.setValue(10)
        self.percentile.setMinimum(0)
        self.percentile.setMaximum(99)
        self.percentile.setAlignment(QtCore.Qt.AlignRight)
        self.cmap_pos = QtWidgets.QLineEdit()
        self.cmap_pos.setText("Reds")
        self.cmap_pos.setAlignment(QtCore.Qt.AlignRight)
        self.cmap_neg = QtWidgets.QLineEdit()
        self.cmap_neg.setText("Blues")
        self.cmap_neg.setAlignment(QtCore.Qt.AlignRight)

        #custom slice axis input and layout
        self.axis=[]
        self.slice_layout=[]
        for i in range(3):        
            slices=[]
            self.slice_layout.append(QtWidgets.QHBoxLayout())
            for j in range(5):
                slices.append(QtWidgets.QSpinBox())
                slices[j].setMinimum(1)
                slices[j].setMaximum(10000)
                slices[j].setAlignment(QtCore.Qt.AlignLeft)
                slices[j].setDisabled(True)
                self.slice_layout[i].addWidget(slices[j])
                slices[j].setStyleSheet("background: white")
            self.axis.append(slices)
        
        #custom figure dimensions input and layout
        fig_width = QtWidgets.QDoubleSpinBox()
        fig_width.setMinimum(1)
        fig_width.setMaximum(60.0)
        fig_width.setValue(7.0)
        fig_width.setAlignment(QtCore.Qt.AlignLeft)
        fig_width.setDisabled(True)
        fig_height = QtWidgets.QDoubleSpinBox()
        fig_height.setMinimum(1)
        fig_height.setMaximum(60.0)
        fig_height.setValue(3.0)
        fig_height.setAlignment(QtCore.Qt.AlignLeft)
        fig_height.setDisabled(True)
        self.fig_dim = [[fig_width,fig_height]]
        dim_layout=QtWidgets.QHBoxLayout()
        dim_layout.addWidget(fig_width)
        dim_layout.addWidget(fig_height)

        #Remaining inputs (Spinbox/line edits)
        self.outfiles_g1 = QtWidgets.QLineEdit()
        self.outfiles_g1.setText("group_1")
        self.outfiles_g1.setAlignment(QtCore.Qt.AlignRight)
        self.outfiles_g2 = QtWidgets.QLineEdit()
        self.outfiles_g2.setAlignment(QtCore.Qt.AlignRight)
        self.outfiles_dif = QtWidgets.QLineEdit()
        self.outfiles_dif.setAlignment(QtCore.Qt.AlignRight)
        self.extensions = QtWidgets.QLineEdit()
        self.extensions.setText("tiff")
        self.extensions.setAlignment(QtCore.Qt.AlignRight)                                   
        self.dots_per_inch = QtWidgets.QSpinBox()
        self.dots_per_inch.setMinimum(1)
        self.dots_per_inch.setMaximum(1200)
        self.dots_per_inch.setValue(500)
        self.dots_per_inch.setAlignment(QtCore.Qt.AlignRight)

        # layout for mandatory arguments input widgets
        mand_form= QtWidgets.QFormLayout()
        mand_form.addRow(self.lbl1, self.btn1)
        mand_form.addRow("Voxel Size/Resolution - Choose from 10, 25, or 50 um", self.voxels)
        mandatory_box.setLayout(mand_form)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(mandatory_box)
        layout.addWidget(self.opt_hide)
        layout.addWidget(self.scrollArea)
        layout.addLayout(help_run_layout)
        self.setLayout(layout)
        #layout optional arguments
        opt_form=QtWidgets.QFormLayout()
        opt_form.addRow(self.lbl2, self.btn2)
        opt_form.addRow(group2_note)
        opt_form.addRow("Gaussian smoothing sigma (Non-negative number. ex: 1, 2 or 2.5)", self.gauss)
        opt_form.addRow("percentile (%) threshold for registration-to-input data check svg animation", self.percentile)
        opt_form.addRow("", title_cmap)
        opt_form.addRow("", website)
        opt_form.addRow("", btn4)
        opt_form.addRow("Colourmap for Positive Values", self.cmap_pos)
        opt_form.addRow("Colourmap for Negative Values", self.cmap_neg)
        opt_form.addRow("Enable Custom Sagittal Slicing", self.sagittal_enable)
        opt_form.addRow("sagittal slicing: start_slice_number, interval, number_of_slices, number_of_rows, number_of_columns", self.slice_layout[0])
        opt_form.addRow("Enable Custom Coronal Slicing", self.coronal_enable)
        opt_form.addRow("coronal slicing: start_slice_number, interval, number_of_slices, number_of_rows, number_of_columns", self.slice_layout[1])
        opt_form.addRow("Enable Custom Axial Slicing", self.axial_enable)
        opt_form.addRow("axial slicing: start_slice_number, interval, number_of_slices, number_of_rows, number_of_columns", self.slice_layout[2])
        opt_form.addRow(custom_slice)
        opt_form.addRow("Enable Custom Figure Dimensions", self.fig_enable)
        opt_form.addRow(default_dim)
        opt_form.addRow("Figure Width and Height (inches)", dim_layout)
        opt_form.addRow(self.lbl3, self.btn3)
        opt_form.addRow(output_note)
        opt_form.addRow("Output/Figure Filename Group 1", self.outfiles_g1)
        opt_form.addRow(group2_selected)
        opt_form.addRow("Output/Figure Filename Group 2", self.outfiles_g2)
        opt_form.addRow("Output/Figure Filename Difference of Groups (Group 2 - Group 1)", self.outfiles_dif)
        opt_form.addRow("Figure Extension", self.extensions)
        opt_form.addRow("Dots Per Inch", self.dots_per_inch)
        self.optional_box.setFlat(True)
        self.optional_box.setLayout(opt_form)
        self.resize(1050, 200)

        #unhide optional arguments
        self.opt_hide.clicked.connect(lambda: self.optional_arg(self.scrollArea,"opt_hide", "opt_hide_status"))
        # Connect the clicked signal to the get_functions handlers
        self.btn1.clicked.connect(lambda: self.get_folder('Group 1 input data folder', self.lbl1, "group1"))
        self.btn2.clicked.connect(lambda: self.get_folder('Group 2 input data folder', self.lbl2, "group2"))
        self.btn3.clicked.connect(lambda: self.get_folder('Output folder', self.lbl3, "dir_outfile"))
        #Connect the clicked signal to message box to display Matplotlib Colour Options
        btn4.clicked.connect(lambda: self.color_plot('Matplotlib Colourmap Options', plt.colormaps()))

        # Connect the checked signal to the state_changed handlers
        self.sagittal_enable.stateChanged.connect(lambda: self.state_changed("sagittal_enable", "sagittal_status", 0, self.axis))
        self.coronal_enable.stateChanged.connect(lambda: self.state_changed("coronal_enable", "coronal_status", 1, self.axis))
        self.axial_enable.stateChanged.connect(lambda: self.state_changed("axial_enable", "axial_status", 2, self.axis))
        self.fig_enable.stateChanged.connect(lambda: self.state_changed("fig_enable", "fig_status", 0, self.fig_dim))
        #Connect the clicked signal to the print_input handler
        run.clicked.connect(self.print_input)
        #Connect clicked signal to launch help window
        help_doc.clicked.connect(self.help_window_show)
        # store the results of the STATS flags in an obj similar to args
        self.inputs = type('', (), {})()

    def optional_arg(self, box, check, status):
        '''window resizing for optional arguments'''
        check=getattr(self,check).isChecked()
        if check:
            box.setWidget(self.optional_box)
            box.resize(1025, 725)
            self.resize(1050, 900)
        else:
            box.takeWidget()
            box.setWidget(QtWidgets.QGroupBox("Optional Arguments"))
            box.resize(0, 0)
            self.resize(1050, 200)

    def get_folder(self, msg, lbl, var):
        '''get folder directories'''
        folder= str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Select ' + msg))
        if folder:
            lbl.setText(folder)
            setattr(self.inputs, var, folder)
            print(msg + " " + folder)
        elif var=="dir_outfile":
            lbl.setText(os.getcwd())
            print(f"default output directory: {os.getcwd()}")
            setattr(self.inputs, var, os.getcwd())
        else:
            lbl.setText('No Folder selected')
            setattr(self.inputs, var, None)

    def state_changed(self, check, status, ind, arr):
        '''check state of checkboxes'''
        check=getattr(self, check).isChecked()
        if check:
            [arr[ind][i].setDisabled(False) for i in range(np.shape(arr)[1])]
        else:
            [arr[ind][i].setDisabled(True) for i in range(np.shape(arr)[1])]
        setattr(self, status, check)

    def showPopupAndCheck(self):
        '''Make Combobox pop-up menu stationary'''
        QtWidgets.QComboBox.showPopup(self.voxels)
        popup=self.findChild(QtWidgets.QFrame)
        rect = popup.geometry()
        if not rect.contains(self.voxels.mapToGlobal(self.voxels.rect().center())):
            return      

    def msgbox(self, text):
        msg=QtWidgets.QMessageBox()   
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText(text)
        msg.setFont(QtGui.QFont("Sans Serif 8"))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
        closing=False
        return closing 

    def help_window_show(self): 
        self.help_window = help_window()
        self.help_window.show()

    def color_plot(self, title, colormaps):
        '''display matplotlib colorbar options'''
        size=len(colormaps[:])
        fig =plt.figure(figsize=(15, 8), dpi=100)
        fig.suptitle(title)
        for x in range(size):
            axes = fig.add_subplot(int(np.ceil(np.sqrt(size))), int(np.round_(np.sqrt(size), decimals=0)), x+1)
            cmap_name = colormaps[x]
            cmap = plt.get_cmap(cmap_name)
            colorbar.ColorbarBase(axes, cmap=cmap,orientation='horizontal')
            axes.set_title(cmap_name, fontsize=10)
            axes.tick_params(left=False, right=False, labelleft=False,
                           labelbottom=False, bottom=False)
        fig.subplots_adjust(left=0.01, right=0.99, top=0.875, bottom=0.01, hspace=2.5, wspace=0.25)
        plt.show()

    def print_input(self):
        '''validate inputs and convert to proper datatype, print and assign to self.inputs'''
        # validation functions
        def check_attr_folder(folder):
            '''check if folder input given'''
            if hasattr(self.inputs, folder)==False:
                if folder == "dir_outfile":
                    setattr(self.inputs, folder, os.getcwd())
                else:
                    setattr(self.inputs, folder, None)
        def cmap_check(cmap, select_box):
            '''check selected colourmap name is in current matplotlib version'''
            if cmap == "":
                select_box.setStyleSheet("background-color: rgb(255,255,159)")
                return(self.msgbox("Missing Colourmap for Positive Values"))
            elif cmap not in plt.colormaps():
                select_box.setStyleSheet("background-color: rgb(255,255,159)")
                return(self.msgbox('Invalid Colourmap Entered: {} \n'.format(cmap) + 'Matplotlib Colourmap Options: \n' + str(plt.colormaps()[:]).strip('[]').replace("'", "")))
            else:
                return(True)
        def contain_check(arr, value, select_box, msg):
            '''check if matching value'''
            if value not in arr:
                select_box.setStyleSheet("background-color :rgb(255,255,159)")
                return(self.msgbox(msg))
            else:
                return(True)
        def axis_append(attr, ind):
            '''check values of axis spinbox'''
            if getattr(self, attr):
                axis=[int(self.axis[ind][i].text()) for i in range(5)]
                return(axis)
            else:
                return([nan])

        #will close GUI after checking if arguments are valid
        self.closing=True

        #if run previously reset all highlighted objects back to white
        [x.setStyleSheet("background-color: white;") for x in [self.btn1, self.btn2, self.voxels, self.cmap_pos, self.cmap_neg, self.outfiles_g1,
                                                               self.outfiles_g2, self.outfiles_dif, self.extensions, self.fig_dim[0][0], self.fig_dim[0][1],
                                                               self.dots_per_inch, self.axis[0][3], self.axis[1][3], self.axis[2][3], self.axis[0][4],
                                                               self.axis[1][4], self.axis[2][4]]]

        #validate folder directories
        check_attr_folder("group1")
        check_attr_folder("group2")
        check_attr_folder("dir_outfile")

        if isinstance(self.inputs.group1, type(None)):
            self.btn1.setStyleSheet("background-color : rgb(255,255,159)") 
            self.closing=self.msgbox("Must Select Valid Group 1 Input Data Folder")
        elif self.inputs.group2 == self.inputs.group1:
            self.btn1.setStyleSheet("background-color : rgb(255,255,159)") 
            self.btn2.setStyleSheet("background-color : rgb(255,255,159)") 
            self.closing=self.msgbox("Group 1 and Group 2 Input Data must not be contained in the same folder")
        if self.inputs.group1 == self.inputs.dir_outfile:
            self.btn1.setStyleSheet("background-color : rgb(255,255,159)")
            self.btn3.setStyleSheet("background-color : rgb(255,255,159)")
            self.closing=self.msgbox("Group 1 Input Data Folder and Output Folder must not be the same folder")
        if self.inputs.group2 == self.inputs.dir_outfile:
            self.btn2.setStyleSheet("background-color : rgb(255,255,159)")
            self.btn3.setStyleSheet("background-color : rgb(255,255,159)")
            self.closing=self.msgbox("Group 2 Input Data Folder and Output Folder must not be the same folder")

        #retrieve other inputs
        gaussin = float(self.gauss.text())
        percentile=int(self.percentile.text())  

        #validate voxels
        voxel = self.voxels.currentText()
        self.closing=min(contain_check(["10", "25", "50"], voxel, self.voxels, "Must Select Valid Voxel Size"), self.closing)
        if self.closing:
            voxel=int(voxel)

        #validate colourmaps
        cmap_p = str(self.cmap_pos.text())
        cmap_n = str(self.cmap_neg.text())

        self.closing=min(cmap_check(cmap_p, self.cmap_pos), self.closing)
        if isinstance(self.inputs.group2, type(None)) == False:
            self.closing=min(cmap_check(cmap_n, self.cmap_neg), self.closing)

        #Retrieve any custom axis values
        s_cut=axis_append("sagittal_status", 0)
        c_cut=axis_append("coronal_status", 1)
        a_cut=axis_append("axial_status", 2)

        #retrieve outfiles and validate name properties
        g1=str(self.outfiles_g1.text())
        g2=str(self.outfiles_g2.text())
        dif=str(self.outfiles_dif.text())
        outfiles=[]

        if ((' ' in g1) or len(g1)==0) and isinstance(self.inputs.group2, type(None)):
            self.outfiles_g1.setStyleSheet("background-color : rgb(255,255,159)")
            self.closing = self.msgbox("Output Filename Group 1 must be filled and not contain a space character")
        elif isinstance(self.inputs.group2, type(None))==False:
            check=[outfile.setStyleSheet("background-color : rgb(255,255,159)") if ((' ' in string) or len(string)==0) else True
                   for string, outfile in zip([g1, g2, dif], [self.outfiles_g1, self.outfiles_g2, self.outfiles_dif])]
            if None in check:
                self.closing=False
                self.msgbox("All Output Filename Arguments must be filled and not contain a space character:"
                            "\n-Output Filename Group 1 \n-Output Filename Group 2 \n-Output Filename Difference of Groups (Group 2 - Group 1)")
            else:
                outfiles=[g1, g2, dif]
        else:
            outfiles=[g1]

        #retrieve extension and check if entered       
        extensions= str(self.extensions.text())
        if extensions=="":
            self.extensions.setStyleSheet("background-color :rgb(255,255,159)")
            self.closing=self.msgbox("Missing Figure Extension")
            
        dots_per_inch= int(self.dots_per_inch.text())
        #retrieve figure dimensions
        figure_dim=[float(self.fig_dim[0][0].text()), float(self.fig_dim[0][1].text())]
        if self.fig_status:
            #validate that height and width length x DPI doesn't exceed maximum pixel size
            if figure_dim[0]*dots_per_inch>65535:
                self.fig_dim[0][0].setStyleSheet("background-color: rgb(255,255,159)")
                self.dots_per_inch.setStyleSheet("background-color: rgb(255,255,159)")
                self.closing=self.msgbox("Width resolution exceeds maximum. Width: {}. DPI: {}. Width x DPI = {}. Cannot exceed 65535".format(fig_dim[0], dots_per_inch, fig_dim[0]*dots_per_inch))
            if figure_dim[1]*dots_per_inch>65535:
                self.fig_dim[0][1].setStyleSheet("background-color: rgb(255,255,159)")
                self.dots_per_inch.setStyleSheet("background-color: rgb(255,255,159)")
                self.closing=self.msgbox("Height resolution exceeds maximum. Height: {}. DPI: {}. Height x DPI = {}. Cannot exceed 65535".format(fig_dim[1], dots_per_inch, fig_dim[1]*dots_per_inch))
        else:
            figure_dim=None
            #validate that rows and columns length x DPI doesn't exceed maximum pixel size
            cuts=np.array([s_cut, c_cut, a_cut])
            #exclude nan values from calculation
            cuts_ind=[ind for ind, value in enumerate(cuts) if not isinstance(value[-1], float)]
            #validate col
            for i, axis in zip(cuts_ind, cuts[cuts_ind]):
                max_col = min(axis[4], 6)
                if max_col * dots_per_inch > 65535:
                    self.axis[i][4].setStyleSheet("background-color:rgb(255,255,159)")
                    self.closing = self.msgbox("Width Resolution exceeds maximum. Cols: {}. DPI: {}. (Min value of either Max Width or Max Col) x DPI = {} x {} = {}. Cannot exceed 65535. Note: Max Width is capped at 60".format(
                                    axis[4], dots_per_inch, max_col, dots_per_inch, max_col * dots_per_inch))
            #validate row
            max_row=min(sum([i[3] for i in cuts[cuts_ind]]), 60)
            if max_row * dots_per_inch > 65535:
                [self.axis[i][3].setStyleSheet("background-color:rgb(255,255,159)") for i in cuts_ind]
                self.closing = self.msgbox("Height Resolution exceeds maximum. Rows: {}. DPI: {}. (Min value of either Max Height or Total Rows) x DPI = {} x {} = {}. Cannot exceed 65535. Note Max Height is capped at 60".format(
                    [i[3] for i in cuts[cuts_ind]], dots_per_inch, max_row, dots_per_inch, max_row * dots_per_inch))

        #assign to self.input to return to heatmap script
        self.inputs.sigma = gaussin
        self.inputs.vox = voxel
        self.inputs.percentile = percentile
        self.inputs.colourmap_pos = cmap_p
        self.inputs.colourmap_neg = cmap_n
        self.inputs.sagittal = s_cut
        self.inputs.coronal = c_cut
        self.inputs.axial = a_cut
        self.inputs.figure_dim = figure_dim
        self.inputs.outfile=outfiles
        self.inputs.extension=extensions
        self.inputs.dpi=dots_per_inch

        print('Group 1 folder:%s', self.inputs.group1)
        print('Group 2 folder:%s', self.inputs.group2)
        print('Output folder:%s', self.inputs.dir_outfile)
        print('gauss :%f' % gaussin)
        print('voxel :%s' % voxel)
        print('percentile :%d' % percentile)
        print('colourmap_pos :%s' % cmap_p.lstrip())
        print('colourmap_neg :%s' % cmap_n.lstrip())
        print('sagittal : %s' % s_cut)
        print('coronal : %s' % c_cut)
        print('axial : %s' % a_cut)
        print('figure dimensions %s' % figure_dim)
        print('Output Filename(s): %s' % outfiles) 
        print('Figure Extension: %s' % extensions)
        print('DPI: %i' % dots_per_inch)

        if self.closing==True:
            self.inputs.run=True
            self.close()

    def closeEvent(self, event):
        for window in QtWidgets.QApplication.topLevelWidgets():
            window.close()

def main():
    # Create an PyQT5 application object.
    app_stats = QtWidgets.QApplication(sys.argv)
    stats_arg = STATSHeatmapMenu()
    stats_arg.show()
    app_stats.exec_()
    return stats_arg.inputs

if __name__ == "__main__":
    sys.exit(main())
    #sys.exit(app_stats.exec_())
    
