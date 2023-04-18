# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QHBoxLayout, QVBoxLayout, QComboBox, QCheckBox

# class ACE(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         self.setWindowTitle('ACE')

#         # Create label for input folder
#         self.input_folder_label = QLabel('Input folder:', self)
#         # Create label for output folder
#         self.output_folder_label = QLabel('Output folder:', self)

#         # Create text input box for folder path
#         self.input_folder_textbox = QLineEdit(self)
#         # Create text input box for folder path
#         self.output_folder_textbox = QLineEdit(self)

#         # Create browse button
#         self.browse_button = QPushButton('Browse', self)
#         self.browse_button.clicked.connect(self.browse_folder)

#         # Create browse button
#         self.browse_button2 = QPushButton('Browse', self)
#         self.browse_button2.clicked.connect(self.browse_folder)

#         # Create combo box for model type
#         self.model_type_combobox = QComboBox(self)
#         self.model_type_combobox.addItem('U-Net')
#         self.model_type_combobox.addItem('UNETR')
#         self.model_type_combobox.addItem('Ensemble')

#         # Create checkbox for visualize results
#         self.visualize_results_checkbox = QCheckBox(self)

#         # Create checkbox for uncertainty map
#         self.uncertainty_map_checkbox = QCheckBox(self)
#         # self.visualize_results_checkbox.setText('Visualize results')

#         # Create horizontal layout for label, text input box, and button
#         hbox1 = QHBoxLayout()
#         hbox1.addWidget(self.input_folder_label)
#         hbox1.addWidget(self.input_folder_textbox)
#         hbox1.addWidget(self.browse_button)

#         hbox5 = QHBoxLayout()
#         hbox5.addWidget(self.output_folder_label)
#         hbox5.addWidget(self.output_folder_textbox)
#         hbox5.addWidget(self.browse_button2)

#         # Create horizontal layout for label and combo box
#         hbox2 = QHBoxLayout()
#         hbox2.addWidget(QLabel('Model type:', self))
#         hbox2.addWidget(self.model_type_combobox)

#         # Create horizontal layout for label and checkbox
#         hbox3 = QHBoxLayout()
#         hbox3.addWidget(QLabel('Visualize results:', self))
#         hbox3.addWidget(self.visualize_results_checkbox)

#         # Create horizontal layout for label and checkbox
#         hbox4 = QHBoxLayout()
#         hbox4.addWidget(QLabel('Uncertainty map:', self))
#         hbox4.addWidget(self.uncertainty_map_checkbox)

#         # Create vertical layout for label, text input box, button, combo box, and checkbox
#         vbox2 = QVBoxLayout()
#         vbox2.addLayout(hbox1)
#         vbox2.addLayout(hbox5)
#         vbox2.addLayout(hbox2)
#         # vbox2.addWidget(QLabel('Optional:', self))
#         vbox2.addLayout(hbox3)
#         vbox2.addLayout(hbox4)

#         
#         # hbox1.setSpacing(20)
#         # hbox5.setSpacing(20)

#         self.setLayout(vbox2)

#         # Set minimum width to 400px
#         self.setMinimumWidth(400)

#         # Set fixed height
#         self.setFixedHeight(self.sizeHint().height())

#         self.show()

#     def browse_folder(self):
#         folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')
#         self.input_folder_textbox.setText(folder_path)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = ACE()
#     sys.exit(app.exec_())

# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton

# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         label = QLabel('Label:', self)
#         label.setGeometry(10, 10, 50, 20)

#         text_input = QLineEdit(self)
#         text_input.setGeometry(70, 10, 100, 20)

#         button = QPushButton('Button', self)
#         button.setGeometry(180, 10, 60, 20)

#         self.setGeometry(300, 300, 250, 50)
#         self.setWindowTitle('Example')
#         self.show()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())


###############################################################################
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout, QComboBox

# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         grid = QGridLayout()

#         label1 = QLabel('Input directory:', self)
#         grid.addWidget(label1, 0, 0)

#         button1 = QPushButton('Button', self)
#         grid.addWidget(button1, 0, 1)

#         text_input1 = QLineEdit(self)
#         grid.addWidget(text_input1, 0, 2)

#         label2 = QLabel('Output directory:', self)
#         grid.addWidget(label2, 1, 0)

#         button2 = QPushButton('Button', self)
#         grid.addWidget(button2, 1, 1)

#         text_input2 = QLineEdit(self)
#         grid.addWidget(text_input2, 1, 2)

#         label3 = QLabel('Model type:', self)
#         grid.addWidget(label3, 2, 0)

#         combo_box = QComboBox(self)
#         combo_box.addItem('U-Net')
#         combo_box.addItem('UNETR')
#         combo_box.addItem('Ensemble')
#         grid.addWidget(combo_box, 2, 1)

#         vbox = QVBoxLayout()
#         vbox.addLayout(grid)

#         self.setLayout(vbox)

#         self.setMinimumWidth(400)
#         self.setGeometry(300, 300, 400, 100)
#         self.setMaximumHeight(100)
#         self.setWindowTitle('Example')
#         self.show()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())
###############################################################################
# import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QVBoxLayout, QComboBox

# class Example(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         grid = QGridLayout()

#         label1 = QLabel('Input directory:', self)
#         grid.addWidget(label1, 0, 0)

#         button1 = QPushButton('Button', self)
#         grid.addWidget(button1, 0, 1)

#         text_input1 = QLineEdit(self)
#         grid.addWidget(text_input1, 0, 2)

#         label2 = QLabel('Output directory:', self)
#         grid.addWidget(label2, 1, 0)

#         button2 = QPushButton('Button', self)
#         grid.addWidget(button2, 1, 1)

#         text_input2 = QLineEdit(self)
#         grid.addWidget(text_input2, 1, 2)

#         label3 = QLabel('Model type:', self)
#         grid.addWidget(label3, 2, 0)

#         combo_box = QComboBox(self)
#         combo_box.addItem('U-Net')
#         combo_box.addItem('UNETR')
#         combo_box.addItem('Ensemble')
#         grid.addWidget(combo_box, 2, 1)

#         label4 = QLabel('Voxel size:', self)
#         grid.addWidget(label4, 3, 0)

#         text_input3 = QLineEdit(self)
#         text_input3.setPlaceholderText('x')
#         text_input3.setStyleSheet('color: grey')
#         text_input3.textChanged.connect(self.on_text_changed)
#         grid.addWidget(text_input3, 3, 1)

#         text_input4 = QLineEdit(self)
#         text_input4.setPlaceholderText('y')
#         text_input4.setStyleSheet('color: grey')
#         text_input3.textChanged.connect(self.on_text_changed)
#         grid.addWidget(text_input3, 3, 1)
#         grid.addWidget(text_input4, 3, 2)

#         text_input5 = QLineEdit(self)
#         text_input5.setPlaceholderText('z')
#         text_input5.setStyleSheet('color: grey')
#         text_input3.textChanged.connect(self.on_text_changed)
#         grid.addWidget(text_input3, 3, 1)
#         grid.addWidget(text_input5, 3, 3)

#         vbox = QVBoxLayout()
#         vbox.addLayout(grid)

#         self.setLayout(vbox)

#         self.setMinimumWidth(400)
#         self.setGeometry(300, 300, 400, 130)
#         self.setMaximumHeight(130)
#         self.setWindowTitle('Example')
#         self.show()

#     def on_text_changed(self, text):
#         sender = self.sender()
#         if text:
#             sender.setStyleSheet('')
#             sender.setText(text)
#         else:
#             sender.setStyleSheet('color: grey')
#             sender.setText(sender.placeholderText())

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = Example()
#     sys.exit(app.exec_())
###############################################################################

import sys
from PyQt5 import QtWidgets

class Example(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        textEdit1 = QtWidgets.QTextEdit("LHS rectangle")
        textEdit2 = QtWidgets.QTextEdit("Bottom rectangle")
        textEdit3 = QtWidgets.QTextEdit("Central square")

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.addWidget(textEdit1, 0, 0)
        self.gridLayout.addWidget(textEdit2, 1, 1)
        self.gridLayout.addWidget(textEdit3, 0, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 3)
        self.gridLayout.setRowStretch(0, 3)
        self.gridLayout.setRowStretch(1, 1)

        self.setLayout(self.gridLayout)
        self.show()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

