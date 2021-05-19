#! /usr/bin/env python

# Generation of .py from .ui so any changes on miracl_conv_set_orient_qt_gui.py will be lost.
# If you want to change the UI either edit the below class (Ui_MainWindowConnections) or 
# use QtDesigner to edit file miracl_conv_set_orient_qt_gui.ui
# Keep in mind that any changes on miracl_conv_set_orient_qt_gui.ui might require additional changes on this file.
import os
import sys

#import subprocess
#ui_file = os.getcwd() + "\\miracl_conv_set_orient_qt_gui.ui"
#out_file = os.getcwd() + "\\miracl_conv_set_orient_qt_gui.py"
#app_file = os.path.dirname(sys.executable) + '\\pyuic5'
#subprocess.run(app_file + ' ' + ui_file + ' -o ' + out_file)



import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets
import glob
from cv2 import cv2
from miracl_conv_set_orient_qt_gui import Ui_MainWindow








def _runException(parent,  exception):
    import inspect
    currentStack = inspect.stack()

    if parent is not None and not isinstance(parent, QtWidgets):    
        parent = None


    if(not isinstance(exception, BaseException)):         
        filename = os.path.split(currentStack[1][1])[1]
        lineNumber = str(currentStack[1][2])
        template = "An exception occurred on file {0} at line {1}: Exception parameter is not subclass of BaseException"
        message = template.format(filename, lineNumber)
    else:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        template = "An exception {0} occurred on file {1} at line {2}: {3}"
        message = template.format(exc_type, fname, exc_tb.tb_lineno, exception)

    QtWidgets.QMessageBox.critical(parent, "Exception occurred", message)
    # still need to raise that?
    raise exception




class Ui_MainWindowConnections(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.MainWindow.resize(1250, 1000)




class ApplicationWindow(QtWidgets.QMainWindow):

    # creates a signal as class attribute
    write_File = QtCore.pyqtSignal(name='writeFile')

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindowConnections()
        self.ui.setupUi(self)

        self.indir = ""
        self.dynamic_canvas = None
        self.toolbar = None

        self.AOVar = 1
        self.SOVar = 0
        self.COVar = 0

        self.SLVar = 1
        self.ILVar = 0
        self.RLVar = 0
        self.LLVar = 0
        self.ALVar = 0
        self.PLVar = 0

        self.SRVar = 1
        self.IRVar = 0
        self.RRVar = 0
        self.LRVar = 0
        self.ARVar = 0
        self.PRVar = 0

        self.STVar = 1
        self.ITVar = 0
        self.RTVar = 0
        self.LTVar = 0
        self.ATVar = 0
        self.PTVar = 0

        self.orientationList = [self.AOVar, self.SOVar, self.COVar]
        self.orientationLeftList = [self.SLVar, self.ILVar, self.RLVar, self.LLVar, self.ALVar, self.PLVar]
        self.orientationRightList = [self.SRVar, self.IRVar, self.RRVar, self.LRVar, self.ARVar, self.PRVar]
        self.orientationTopList = [self.STVar, self.ITVar, self.RTVar, self.LTVar, self.ATVar, self.PTVar]        

        # pop menus variable
        self.annotation_left_qMenu = None
        self.annotation_right_qMenu = None
        self.annotation_top_qMenu = None

        # do not change order of below 3 methods
        self.openDirectory()
        self.ortbutton()        
        self.initializeMatplolibObjects()


        # connects UI components to their methods
        self.ui.annotation_left_pushButton.clicked.connect(self.leftbutton)
        self.ui.annotation_right_pushButton.clicked.connect(self.rightbutton)
        self.ui.annotation_top_pushButton.clicked.connect(self.topbutton)
        self.write_File.connect(self.writeOrientationFile)

        self.dynamic_canvas.mpl_connect('key_press_event', self.on_key_event)

        self.ui.prev_image_pushButton.clicked.connect(self.previmg)
        self.ui.next_image_pushButton.clicked.connect(self.nextimg)
        self.ui.image_number_spinBox.valueChanged.connect(self.gotoimg)



    def initializeMatplolibObjects(self):
        try:
            print('\n Reading images and automatically adjusting contrast \n')

            n = len(self.flist)
            if n == 0:
                QtWidgets.QMessageBox.critical(None, "Path not found", "%s does not contain .tif files. Please check path and rerun script" % self.indir, QtWidgets.QMessageBox.Ok)
                sys.exit()

            self.index = int(n / 2.0)
            self.evar = self.index + 1
            self.ui.image_number_spinBox.setMinimum(1)
            self.ui.image_number_spinBox.setMaximum(n)
            self.ui.image_number_spinBox.setValue(self.evar)
            
            self.figureView = Figure(figsize=(8, 8), dpi=100, facecolor='royalblue', edgecolor='white', linewidth=2)
            self.axis = self.figureView.add_subplot(111)
            self.img = cv2.imread(self.flist[self.index], 0)
            self.clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
            self.cl = self.clahe.apply(self.img)
            self.axis.imshow(self.cl, 'gray')
            self.axis.axis('off')
            self.axis.set_title(os.path.basename(self.flist[self.index]), color='white', y=1.05, fontsize=10)


            # creating canvas and toolbar
            self.dynamic_canvas = FigureCanvasQTAgg(self.figureView)
            self.dynamic_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.dynamic_canvas.setFocus()
            self.ui.image_gridLayout.addWidget(self.dynamic_canvas, 1, 1, 1, 3)
            self.toolbar = NavigationToolbar2QT(self.dynamic_canvas, self)
            self.toolbar.setFixedWidth(400)
            
            
            # Setting tool tips for relevant buttons on the navigation tool bar
            #https://matplotlib.org/3.1.1/users/navigation_toolbar.html
            toolTipDict = {
                "Reset original view": "Reset original view (h or r or home)",
                "Back to previous view": "Back to previous view (c or left arrow or backspace)",
                "Forward to next view": "Forward to next view (v or right arrow)",
                "Left button pans, Right button zooms\nx/y fixes axis, CTRL fixes aspect": "Left button pans, Right button zooms\nx/y fixes axis, CTRL fixes aspect (p)",
                "Zoom to rectangle\nx/y fixes axis, CTRL fixes aspect": "Zoom to rectangle\nx/y fixes axis, CTRL fixes aspect (o)",
                "Save the figure": "Save the figure (ctrl + s)",
            }
            actionList = self.toolbar.actions()
            for action in actionList:
                ss = action.toolTip()
                item = toolTipDict.get(ss)
                if(item is not None):
                    action.setToolTip(item)


            self.ui.footer_gridLayout.addWidget(self.toolbar, 1, 6, 1, 2)
        except BaseException as ex:
            _runException(None,  ex)




    def openDirectory(self):
        try:
            #self.indir = "C:\\source\\repos\\newui\\data\\tiff"
            self.indir = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open clarity dir (with .tif files) by double clicking then "Choose"',
              os.getcwd(), QtWidgets.QFileDialog.ShowDirsOnly)

            if not self.indir:
                QtWidgets.QMessageBox.critical(None, "Path not found", "Path cannot be empty/null. Please check path and rerun script", QtWidgets.QMessageBox.Ok)
                sys.exit(0)

            if not os.path.exists(self.indir):
                QtWidgets.QMessageBox.critical(None, "Path not found", "%s does not exist. Please check path and rerun script" % self.indir, QtWidgets.QMessageBox.Ok)
                sys.exit(0)

            self.flist = glob.glob(os.path.join(self.indir, '*.tif*'))
            self.flist.sort()
        except BaseException as ex:
            if isinstance(ex, SystemExit):
                raise ex
            else:
                _runException(None,  ex)




    '''
    Intercepts the closeEvent event to ask for user confirmation
    '''
    def closeEvent(self, event):
        try:
            if(not isinstance(event, QtGui.QCloseEvent)):
                raise TypeError("event is not of a type QtGui.QCloseEvent")

            res = QtWidgets.QMessageBox.question(self, "Quit", "Done setting orientation, want to quit?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if res == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        except BaseException as ex:
            _runException(self,  ex)


    '''
    Writes the orientation file 
    '''
    def writeOrientationFile(self):
        try:
            ortstr = self.set_orientation()
            fileName = "ort2std.txt"
            with open(fileName, "w") as myfile:
                myfile.write("tifdir=%s \nortcode=%s \n" % (self.indir, ortstr))              
        except BaseException as ex:
            _runException(self,  ex)


    '''
    Captures and forward keypress events to the matplot toolbar.
    User needs to bring focus to dynamic_canvas by mouse clicking on it to activate the forward properly
    '''
    def on_key_event(self, event):
        try:
            #print('you pressed %s' % event.key)
            if not isinstance(event, matplotlib.backend_bases.KeyEvent):
                raise TypeError("event is not of type matplotlib.backend_bases.KeyEvent")

            key_press_handler(event, self.dynamic_canvas, self.toolbar)
        except BaseException as ex:
            _runException(self,  ex)


    '''
    Adds menu options and connections into Orientation menu
    '''
    def ortbutton(self):
        try:
            self.menuOrientationActionGroup = QtWidgets.QActionGroup(self.ui.menuOrientation)
            texts = ["Axial", "Sagittal", "Coronal"]   
            for text in texts:
                action = QtWidgets.QAction(text, self.ui.menuOrientation, checkable=True, checked=text==texts[0])
                self.ui.menuOrientation.addAction(action)
                action.triggered.connect(self.ortbuttonOnTriggered)
                self.menuOrientationActionGroup.addAction(action)

            self.menuOrientationActionGroup.setExclusive(True)
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(None, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex




    '''
    Called when an action from Orientation menu is picked
    '''
    def ortbuttonOnTriggered(self):      
        try:
            actions = self.ui.menuOrientation.findChildren(QtWidgets.QAction)
            out = []
            for action in actions:
                if len(action.text()) != 0 and self.ui.menuOrientation.title() != action.text():
                    out.append(action.isChecked())

            self.AOVar = out[0]
            self.SOVar = out[1]
            self.COVar = out[2]
            self.orientationList = [self.AOVar, self.SOVar, self.COVar]
            self.write_File.emit()
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Adds actions into a given menu
    '''
    def createFloatMenu(self, floatMenu, group):  
        try:
            if not isinstance(floatMenu, QtWidgets.QMenu):
                raise TypeError("floatMenu is not of a type QtWidgets.QMenu")

            if not isinstance(group, QtWidgets.QActionGroup):
                raise TypeError("floatMenu is not of a type QtWidgets.QActionGroup")

            texts = ["Superior", "Inferior", "Right","Left","Anterior","Posterior"]   
            for text in texts:
                action = QtWidgets.QAction(text, floatMenu, checkable=True, checked=text==texts[0])
                floatMenu.addAction(action)
                group.addAction(action)

            group.setExclusive(True)
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(None, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex

        

    '''
    Adds a float menu and connections into Annotation_left_pushButton
    '''
    def leftbutton(self):
        try:
            if self.annotation_left_qMenu is None:
                self.annotation_left_qMenu = QtWidgets.QMenu(self.ui.annotation_left_pushButton)        
                self.annotation_left_qActionGroup = QtWidgets.QActionGroup(self.annotation_left_qMenu)
            
                self.createFloatMenu(self.annotation_left_qMenu, self.annotation_left_qActionGroup)
            
                # ToDo connect actions to methods
                actions = self.annotation_left_qMenu.findChildren(QtWidgets.QAction)
                for action in actions:
                    action.triggered.connect(self.leftbuttonOnTriggered)

            pos = QtGui.QCursor.pos()
            self.annotation_left_qMenu.popup(pos)
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(None, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Triggered by a click on any annotation_left_qMenu option
    Populate left orientation variables using option selected
    '''
    def leftbuttonOnTriggered(self):
        try:
            actions = self.annotation_left_qMenu.findChildren(QtWidgets.QAction)
            out = []
            for action in actions:
                if len(action.text()) != 0:
                    out.append(action.isChecked())

            self.SLVar = out[0]
            self.ILVar = out[1]
            self.RLVar = out[2]
            self.LLVar = out[3]
            self.ALVar = out[4]
            self.PLVar = out[5]
            self.orientationLeftList = [self.SLVar, self.ILVar, self.RLVar, self.LLVar, self.ALVar, self.PLVar]
            self.write_File.emit()
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Adds a float menu and connections into Annotation_top_pushButton
    '''
    def topbutton(self):
        try:
            if self.annotation_top_qMenu is None:
                self.annotation_top_qMenu = QtWidgets.QMenu(self.ui.annotation_top_pushButton)        
                self.annotation_top_qActionGroup = QtWidgets.QActionGroup(self.annotation_top_qMenu)
            
                self.createFloatMenu(self.annotation_top_qMenu, self.annotation_top_qActionGroup)
            
                # ToDo connect actions to methods
                actions = self.annotation_top_qMenu.findChildren(QtWidgets.QAction)
                for action in actions:
                    action.triggered.connect(self.topbuttonOnTriggered)

            pos = QtGui.QCursor.pos()
            self.annotation_top_qMenu.popup(pos) 
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(None, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex
       


    '''
    Triggered by a click on any annotation_top_qMenu option
    Populate top orientation variables using option selected
    '''
    def topbuttonOnTriggered(self):
        try:
            actions = self.annotation_top_qMenu.findChildren(QtWidgets.QAction)
            out = []
            for action in actions:
                if len(action.text()) != 0:
                    out.append(action.isChecked())

            self.STVar = out[0]
            self.ITVar = out[1]
            self.RTVar = out[2]
            self.LTVar = out[3]
            self.ATVar = out[4]
            self.PTVar = out[5]        
            self.orientationTopList = [self.STVar, self.ITVar, self.RTVar, self.LTVar, self.ATVar, self.PTVar]
            self.write_File.emit()
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Adds a float menu and connections into Annotation_right_pushButton
    '''
    def rightbutton(self):
        try:
            if self.annotation_right_qMenu is None:
                self.annotation_right_qMenu = QtWidgets.QMenu(self.ui.annotation_right_pushButton)        
                self.annotation_right_qActionGroup = QtWidgets.QActionGroup(self.annotation_right_qMenu)
            
                self.createFloatMenu(self.annotation_right_qMenu, self.annotation_right_qActionGroup)
            
                actions = self.annotation_right_qMenu.findChildren(QtWidgets.QAction)
                for action in actions:
                    action.triggered.connect(self.rightbuttonOnTriggered)

            pos = QtGui.QCursor.pos()
            self.annotation_right_qMenu.popup(pos)
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex
  


    '''
    Triggered by a click on any annotation_right_qMenu option
    Populate top orientation variables using option selected
    '''
    def rightbuttonOnTriggered(self):
        try:
            actions = self.annotation_right_qMenu.findChildren(QtWidgets.QAction)
            out = []
            for action in actions:
                if len(action.text()) != 0:
                    out.append(action.isChecked())

            self.SRVar = out[0]
            self.IRVar = out[1]
            self.RRVar = out[2]
            self.LRVar = out[3]
            self.ARVar = out[4]
            self.PRVar = out[5]        
            self.orientationRightList = [self.SRVar, self.IRVar, self.RRVar, self.LRVar, self.ARVar, self.PRVar]
            self.write_File.emit()    
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Returns the image file inddex to be displayed
    '''
    def nextframe(self, i=1, imgnum=-1):
        try:
            if not isinstance(i, int):
                raise TypeError("i is not of a type int")

            if not isinstance(imgnum, int):
                raise TypeError("imgnum is not of a type int")


            if imgnum == -1:
                self.index += i
            else:
                self.index = imgnum - 1
            if self.index >= len(self.flist):
                self.index = 0
            elif self.index < 0:
                self.index = len(self.flist) - 1

            self.evar = (self.index + 1)
            
            return self.index
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception", "{0}".format(ex), QtWidgets.QMessageBox.Ok)
            raise ex



    '''
    Slot to increment spinBox when next button is pressed
    '''
    def nextimg(self):
        self.ui.image_number_spinBox.setValue( self.ui.image_number_spinBox.value() + 1)


    '''
    Slot to decrement spinBox when previous button is pressed
    '''
    def previmg(self):
        self.ui.image_number_spinBox.setValue( self.ui.image_number_spinBox.value() -1)
  

    '''
    Loads image identified by value [1...n]
    '''
    def gotoimg(self, value):
        try:
            if not isinstance(value, int):
                raise TypeError("value is not of a type int")

            self.index = self.nextframe(imgnum=value)
            self.img = cv2.imread(self.flist[self.index], 0)
            self.clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
            self.cl = self.clahe.apply(self.img)
            self.axis.imshow(self.cl, 'gray')
            self.axis.axis('off')
            self.axis.set_title(os.path.basename(self.flist[self.index]), color='white', y=1.05, fontsize=10)
            self.dynamic_canvas.draw()
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception ocurred", "{0}".format(ex), QtWidgets.QMessageBox.Ok)    
            raise ex        


    '''
    Get orientation and annotations
    '''
    def set_orientation(self):
        try:
            # Axial
            if self.AOVar == 1:
                ort = list('ARS')

                # get Top
                if self.ATVar == 1:
                    ort[0] = 'A'
                elif self.PTVar == 1:
                    ort[0] = 'P'

                # get Right
                if self.RRVar == 1:
                    ort[1] = 'L'
                elif self.LRVar == 1:
                    ort[1] = 'R'

                # get into page (left button)
                if self.SLVar == 1:
                    ort[2] = 'I'
                elif self.ILVar == 1:
                    ort[2] = 'S'

            # Sagittal
            elif self.SOVar == 1:
                ort = list('ASR')

                # get Top
                if self.ATVar == 1:
                    ort[0] = 'A'
                elif self.PTVar == 1:
                    ort[0] = 'P'

                # get Right
                if self.SRVar == 1:
                    ort[1] = 'I'
                elif self.IRVar == 1:
                    ort[1] = 'S'

                # get into page
                if self.RLVar == 1:
                    ort[2] = 'R'
                elif self.LLVar == 1:
                    ort[2] = 'L'

            # Coronal
            elif self.COVar == 1:
                ort = list('RAS')

                # get Top
                if self.STVar == 1:
                    ort[0] = 'R'
                elif self.ITVar == 1:
                    ort[0] = 'L'

                # get Right
                if self.RRVar == 1:
                    ort[1] = 'A'
                elif self.LRVar == 1:
                    ort[1] = 'P'

                # get into page
                if self.ALVar == 1:
                    ort[2] = 'S'
                elif self.PLVar == 1:
                    ort[2] = 'I'

            ortstr = ''.join(ort)
            return ortstr
        except BaseException as ex:
            QtWidgets.QMessageBox.critical(self, "Exception ocurred", "{0}".format(ex), QtWidgets.QMessageBox.Ok)    
            raise ex 






'''
Fires up application
'''
app = QtWidgets.QApplication(sys.argv)
MainWindow = ApplicationWindow()
MainWindow.show()
sys.exit(app.exec_())
