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
    QMessageBox,
)
from PyQt5.QtCore import Qt
from miracl_workflow_ace_gui_tab_manager import TabManager
from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser
from miracl import miracl_logger
from miracl_workflow_ace_gui_flag_creator import flag_creator
import subprocess, shlex
from pathlib import Path

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
        self.setGeometry(100, 100, 750, 600)

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

        #########
        # FLAGS #
        #########

        # Main tab
        main_tab = self.tab_manager.main_tab
        method_checkbox = (
            self.tab_manager.main_tab.single_checkbox
        )  # Checks if single or multiple method is used
        main_tab_flags = flag_creator.create_main_tab_flags(main_tab, method_checkbox)

        # CLARITY-Allen registration
        clarity_registration_tab = self.tab_manager.clarity_registration_tab
        clarity_registration_tab_flags = flag_creator.create_clarity_registration_flags(
            clarity_registration_tab
        )

        # Conversion
        conversion_tab = self.tab_manager.conversion_tab
        conversion_tab_flags = flag_creator.create_conversion_flags(conversion_tab)

        # Voxelizing/warping
        voxelizing_warping_tab = self.tab_manager.voxelizing_warping_tab
        voxelizing_warping_tab_flags = flag_creator.create_voxelization_warping_flags(
            voxelizing_warping_tab
        )

        # Clusterwise
        clusterwise_tab = self.tab_manager.clusterwise_tab
        clusterwise_tab_flags = flag_creator.create_clusterwise_flags(clusterwise_tab)

        # Correlation/stats
        correlation_stats_tab = self.tab_manager.correlation_stats_tab
        correlation_stats_tab_flags = flag_creator.create_correlation_stats_flags(
            correlation_stats_tab
        )

        # Heatmap
        heatmap_tab = self.tab_manager.heatmap_tab
        heatmap_tab_flags = flag_creator.create_heatmap_flags(heatmap_tab)

        # logger.debug(
        #     f"FULL CMD: miracl flow ace {wu.craft_flags(main_tab_flags)} {wu.craft_flags(conversion_tab_flags)} {wu.craft_flags(clarity_registration_tab_flags)} {wu.craft_flags(voxelizing_warping_tab_flags)} {wu.craft_flags(clusterwise_tab_flags)} {wu.craft_flags(correlation_stats_tab_flags)} {wu.craft_flags(heatmap_tab_flags)}"
        # )

        # full_command_split = full_command.split()[1:]
        current_script_path = Path(__file__).resolve()
        parent_dir = current_script_path.parent.parent
        script_path = parent_dir / "miracl_workflow_ace_interface.py"
        full_command = f"python {str(script_path)} {wu.craft_flags(main_tab_flags)} {wu.craft_flags(conversion_tab_flags)} {wu.craft_flags(clarity_registration_tab_flags)} {wu.craft_flags(voxelizing_warping_tab_flags)} {wu.craft_flags(clusterwise_tab_flags)} {wu.craft_flags(correlation_stats_tab_flags)} {wu.craft_flags(heatmap_tab_flags)}"
        full_command_split = shlex.split(full_command)
        logger.debug(f"FULL COMMAND: {full_command_split}")
        # subprocess.run(full_command_split)
        try:
            subprocess.run(
                full_command_split, capture_output=True, text=True, check=True
            )
            print("Command executed successfully!")
            return True
        # except subprocess.CalledProcessError as e:
        #     print(f"Command failed with error: {e}")
        #     print(f"Output: {e.stdout}")
        #     print(f"Error: {e.stderr}")
        #     QMessageBox()
        #     return False
        # except subprocess.CalledProcessError as e:
        #     error_message = f"Command failed with error: {e.stderr}"
        #     QMessageBox.critical(None, "Error", error_message)
        #     return False
        except subprocess.CalledProcessError as e:
            stderr_lines = e.stderr.strip().split("\n")
            error_message = "\n".join(stderr_lines[-1:])
            QMessageBox.critical(None, "Error", error_message)
            return False

        # parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        #
        # def validate_args(parser, args):
        #     # Save the original sys.argv
        #     original_argv = sys.argv
        #
        #     try:
        #         # Set sys.argv to our args (including a dummy script name)
        #         sys.argv = ["dummy_script.py"] + args
        #
        #         # Parse the arguments
        #         parsed_args = parser.parse_args()
        #
        #         # If we get here, parsing was successful
        #         return True, None
        #
        #     except SystemExit as e:
        #         # ArgumentParser calls sys.exit() when it encounters an error
        #         return False, str(e)
        #
        #     finally:
        #         # Restore the original sys.argv
        #         sys.argv = original_argv
        #
        # is_valid, error_message = validate_args(parser, args)

        # args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        # help_dict = wu.extract_help_texts(args_parser)
        # print(help_dict['rva_vx_res'])

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
