#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Utilities

Description:
    Controller for ACE flow GUI.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from pandas.core.dtypes.common import conversion
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QTabWidget,
)
from PyQt5.QtCore import Qt
from miracl_workflow_ace_gui_tab_manager import TabManager
from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainWindow(QMainWindow):
    """
    The main window of the application.

    This class represents the main window of the ACE flow application. It sets
    up the user interface, including the tab widget, checkbox, buttons, and
    event handlers.

    Attributes:
        tab_widget (QTabWidget): The tab widget that holds the different tabs.
        tab_manager (TabManager): The manager for the tabs in the application.
        show_tabs_checkbox (QCheckBox): The checkbox to show or hide
        additional tabs.
    """

    def __init__(self):
        """
        Initialize the MainWindow.

        This method sets up the main window, including the central widget,
        main layout, tab widget, and various UI elements.
        """
        super().__init__()
        self.setWindowTitle("ACE flow")
        self.setGeometry(100, 100, 600, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tab_manager = TabManager(self.tab_widget)

        show_tabs_checkbox = QCheckBox("Show tabs for all modules used by ACE")
        show_tabs_checkbox.stateChanged.connect(self.toggle_additional_tabs)
        main_layout.addWidget(show_tabs_checkbox)

        help_button = QPushButton("Help")
        main_layout.addWidget(help_button)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.test_run_routine)
        main_layout.addWidget(run_button)

        # Hide additional tabs initially
        for tab in self.tab_manager.additional_tabs:
            tab_index = self.tab_widget.indexOf(tab)
            self.tab_widget.setTabVisible(tab_index, False)

    def toggle_additional_tabs(self, state):
        """
        Toggle the visibility of additional tabs.

        This method is called when the "Show tabs for all modules used by ACE"
        checkbox is checked or unchecked. It sets the visibility of the
        additional tabs based on the checkbox state.

        Args:
            state (int): The state of the checkbox. It can be Qt.Checked or Qt.Unchecked.
        """
        for tab in self.tab_manager.additional_tabs:
            tab_index = self.tab_widget.indexOf(tab)
            self.tab_widget.setTabVisible(tab_index, state == Qt.Checked)

    def test_run_routine(self):
        """
        Perform a test run of the application.

        This method retrieves various input values from the main tab and prints
        them to the console. It also checks the state of the "Single or multi
        method arguments" checkbox and prints the corresponding mode.
        """
        model_architecture = (
            self.tab_manager.main_tab.model_architecture_input.currentText()
        )
        x_res = self.tab_manager.main_tab.x_res_field_input.text()
        gpu_index = self.tab_manager.main_tab.gpu_index_input.value()
        conversion_dx = self.tab_manager.main_tab.conversion_dx_input.value()
        orientation_code = self.tab_manager.main_tab.orientation_code_input.text()
        method_checkbox = self.tab_manager.main_tab.single_checkbox

        print(f"x_res: {x_res}")
        print(f"Model architecture: {model_architecture}")
        print(f"GPU index: {gpu_index}")
        print(f"Conversion dx: {conversion_dx}")
        print(f"Orientation code: {orientation_code if orientation_code else 'ALS'}")
        if method_checkbox.isChecked():
            print("MULTIPLE METHOD")
        else:
            print("SINGLE METHOD")

        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        test_dict = wu.extract_help_texts(args_parser)
        print(test_dict["single"])

        reg_side_test = wu.translate_choice_to_parser_value(
            {"right hemisphere": "rh", "left hemisphere": "lh"},
            self.tab_manager.clarity_registration_tab.reg_side_input.currentText(),
        )
        print(reg_side_test)

        reg_olfactory_test = wu.translate_choice_to_parser_value(
            {"not included": 0, "included": 1},
            self.tab_manager.clarity_registration_tab.reg_olfactory_bulb_input.currentText(),
        )
        print(reg_olfactory_test)

        reg_util_int_correction_test = wu.translate_choice_to_parser_value(
            {"run": 0, "skip": 1},
            self.tab_manager.clarity_registration_tab.reg_util_int_correction_input.currentText(),
        )
        print(reg_util_int_correction_test)

        reg_warp_to_allen = wu.translate_choice_to_parser_value(
            {"yes": True, "no": False},
            self.tab_manager.clarity_registration_tab.reg_util_int_correction_input.currentText(),
        )
        print(reg_warp_to_allen)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
