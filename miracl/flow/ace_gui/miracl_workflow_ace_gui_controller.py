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
from miracl import miracl_logger

# import sys
# import os
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = miracl_logger.logger

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

        ############
        # MAIN TAB #
        ############

        main_tab = self.tab_manager.main_tab
        method_checkbox = (
            self.tab_manager.main_tab.single_checkbox
        )  # Checks if single or multiple method is used
        main_tab_flags = {
            "-s": wu.get_tab_var(main_tab, "single_method_path_input", "textfield")
            if not method_checkbox.isChecked()
            else None,
            "-c": f"{wu.get_tab_var(main_tab, 'multi_method_ctrl_path_input', 'textfield')} {wu.get_tab_var(main_tab, 'multi_method_ctrl_tif_path_input', 'textfield')}"
            if method_checkbox.isChecked()
            else None,
            "-t": f"{wu.get_tab_var(main_tab, 'multi_method_treated_path_input', 'textfield')} {wu.get_tab_var(main_tab, 'multi_method_treated_tif_path_input', 'textfield')}",
            "--sa_output_folder": wu.get_tab_var(
                main_tab, "output_folder_path_input", "textfield"
            ),
            "--sa_model_type": wu.get_tab_var(
                main_tab, "model_architecture_input", "multiplechoice"
            ),
            "--sa_resolution": f"{wu.get_tab_var(main_tab, 'x_res_field_input', 'textfield')} {wu.get_tab_var(main_tab, 'y_res_field_input', 'textfield')} {wu.get_tab_var(main_tab, 'z_res_field_input', 'textfield')}",
            "--sa_gpu_index": str(
                wu.get_tab_var(main_tab, "gpu_index_input", "spinbox")
            ),
            "--ctn_down": str(
                wu.get_tab_var(main_tab, "conversion_dx_input", "spinbox")
            ),
            "--rca_orient_code": wu.get_tab_var(
                main_tab, "orientation_code_input", "textfield"
            ),
            "--rca_voxel_size": wu.get_tab_var(
                main_tab, "labels_voxel_size_input", "multiplechoice"
            ),
            "--rva_downsample": wu.get_tab_var(
                main_tab, "voxelization_dx_input", "spinbox"
            ),
            "--rwc_voxel_size": wu.get_tab_var(
                main_tab, "warping_voxel_size_input", "multiplechoice"
            ),
            "--rerun-registration": "true"
            if wu.get_tab_var(main_tab, "rerun_registration_input", "multiplechoice")
            == "yes"
            else "false",
            "--rerun-segmentation": "true"
            if wu.get_tab_var(main_tab, "rerun_segmentation_input", "multiplechoice")
            == "yes"
            else "false",
            "--rerun-conversion": "true"
            if wu.get_tab_var(main_tab, "rerun_conversion_input", "multiplechoice")
            == "yes"
            else "false",
        }
        # print(f"command: miracl flow ace {wu.craft_flags(main_tab_flags)}")

        ############################
        # CLARITY REGISTRATION TAB #
        ############################

        clarity_registration_tab = self.tab_manager.clarity_registration_tab
        clarity_registration_tab_flags = {
            "--rca_hemi": wu.get_tab_var(
                clarity_registration_tab, "reg_hemi_input", "multiplechoice"
            ),
            "--rca_allen_label": wu.get_tab_var(
                clarity_registration_tab, "reg_allen_lbl_warp_path_input", "textfield"
            ),
            "--rca_allen_atlas": wu.get_tab_var(
                clarity_registration_tab, "reg_cust_allen_atlas_path_input", "textfield"
            ),
            "--rca_side": "rh"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_side_input", "multiplechoice"
            )
            == "right hemisphere"
            else "lh",
            "--rca_no_mosaic_fig": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_mosaic_figure_input", "multiplechoice"
            )
            == "yes"
            else "0",
            "--rca_olfactory_bulb": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_olfactory_bulb_input", "multiplechoice"
            )
            == "included"
            else "0",
            "--rca_skip_cor": "1"
            if wu.get_tab_var(
                clarity_registration_tab,
                "reg_util_int_correction_input",
                "multiplechoice",
            )
            == "run"
            else "0",
            "--rca_warp": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_warp_to_allen_input", "multiplechoice"
            )
            == "yes"
            else "0",
        }
        # print(
        #     f"command: miracl flow ace {wu.craft_flags(clarity_registration_tab_flags)}"
        # )

        # if method_checkbox.isChecked():
        #     print("MULTIPLE METHOD")
        # else:
        #     print("SINGLE METHOD")

        logger.debug(f"FULL CMD: miracl flow ace {wu.craft_flags(main_tab_flags)} {wu.craft_flags(clarity_registration_tab_flags)}")

        # reg_side_test = wu.translate_choice_to_parser_value(
        #     {"right hemisphere": "rh", "left hemisphere": "lh"},
        #     self.tab_manager.clarity_registration_tab.reg_side_input.currentText(),
        # )
        # print(reg_side_test)
        #
        # reg_olfactory_test = wu.translate_choice_to_parser_value(
        #     {"not included": 0, "included": 1},
        #     self.tab_manager.clarity_registration_tab.reg_olfactory_bulb_input.currentText(),
        # )
        # print(reg_olfactory_test)
        #
        # reg_util_int_correction_test = wu.translate_choice_to_parser_value(
        #     {"run": 0, "skip": 1},
        #     self.tab_manager.clarity_registration_tab.reg_util_int_correction_input.currentText(),
        # )
        # print(reg_util_int_correction_test)

        # reg_warp_to_allen = wu.translate_choice_to_parser_value(
        #     {"yes": True, "no": False},
        #     self.tab_manager.clarity_registration_tab.reg_util_int_correction_input.currentText(),
        # )
        # print(reg_warp_to_allen)

        # x_res = self.tab_manager.main_tab.x_res_field_input.text()
        # gpu_index = self.tab_manager.main_tab.gpu_index_input.value()
        # conversion_dx = self.tab_manager.main_tab.conversion_dx_input.value()
        # orientation_code = self.tab_manager.main_tab.orientation_code_input.text()
        # print(f"x_res: {x_res}")
        # print(f"GPU index: {gpu_index}")
        # print(f"Conversion dx: {conversion_dx}")
        # print(f"Orientation code: {orientation_code if orientation_code else 'ALS'}")
        # args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        # test_dict = wu.extract_help_texts(args_parser)
        # print(test_dict["single"])


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
