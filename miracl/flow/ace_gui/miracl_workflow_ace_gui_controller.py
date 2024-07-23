#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Controller

Description:
    Controller for ACE flow GUI from MVC design.

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
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QFileDialog,
    QCheckBox,
    QPushButton,
    QTabWidget,
    QMessageBox,
    QComboBox,
    QLineEdit,
)
from PyQt5.QtCore import Qt
from miracl.flow.ace_gui.miracl_workflow_ace_gui_tab_manager import TabManager
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow.ace_gui.miracl_workflow_ace_gui_help_window import HelpMessageBox
from miracl.flow import miracl_workflow_ace_parser
from miracl import miracl_logger
from miracl.flow.ace_gui.miracl_workflow_ace_gui_flag_creator import flag_creator
import subprocess, shlex
from pathlib import Path
from miracl.system.io_utils import UserInputPairsManager

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
        self.window_title = "ACE flow"

        super().__init__()

        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

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

        io_widget = QWidget()
        io_layout = QHBoxLayout(io_widget)
        io_load_button = QPushButton("Load")
        io_load_button.clicked.connect(self.load_button_clicked)
        io_layout.addWidget(io_load_button)
        io_save_button = QPushButton("Save")
        io_save_button.clicked.connect(self.save_button_clicked)
        io_layout.addWidget(io_save_button)
        io_reset_button = QPushButton("Reset")
        io_reset_button.clicked.connect(self.reset_button_clicked)
        io_layout.addWidget(io_reset_button)
        io_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(io_widget)

        help_button = QPushButton("Help")
        help_button.clicked.connect(self.help_button_clicked)
        main_layout.addWidget(help_button)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_ace_cli)
        main_layout.addWidget(run_button)

        # Hide additional tabs initially
        for tab in self.tab_manager.additional_tabs:
            tab_index = self.tab_widget.indexOf(tab)
            self.tab_widget.setTabVisible(tab_index, False)

    def get_script_path(self, module_interface):
        gui_controller_path = Path(__file__).resolve()
        interface_dir = gui_controller_path.parent.parent
        interface_script_path = interface_dir / module_interface
        return interface_script_path

    def create_cmd_dict(self):
        all_user_input_pairs_dicts = {
            "main_tab": flag_creator.create_main_tab_flags(
                self.tab_manager.main_tab, self.tab_manager.main_tab.single_checkbox
            ),
            "clarity_registration_tab": flag_creator.create_clarity_registration_flags(
                self.tab_manager.clarity_registration_tab
            ),
            "conversion_tab": flag_creator.create_conversion_flags(
                self.tab_manager.conversion_tab
            ),
            "segmentation_tab": flag_creator.create_segmentation_flags(
                self.tab_manager.segmentation_tab
            ),
            "voxelizing_warping_tab": flag_creator.create_voxelization_warping_flags(
                self.tab_manager.voxelizing_warping_tab
            ),
            "clusterwise_tab": flag_creator.create_clusterwise_flags(
                self.tab_manager.clusterwise_tab
            ),
            "correlation_stats_tab": flag_creator.create_correlation_stats_flags(
                self.tab_manager.correlation_stats_tab
            ),
            "heatmap_tab": flag_creator.create_heatmap_flags(
                self.tab_manager.heatmap_tab
            ),
        }

        return all_user_input_pairs_dicts

    def reset_button_clicked(self):
        pass

    def save_button_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "MIRACL ACE Flow Files (*.aceflow)", options=options
        )
        if fileName:
            if not fileName.endswith(".aceflow"):
                fileName += ".aceflow"

            user_input_pairs_dicts = self.create_cmd_dict()
            manager = UserInputPairsManager(self.window_title.lower().replace(" ", "_"))
            manager.set_user_input_pairs(user_input_pairs_dicts)
            manager.save_to_json(fileName)
            print(f"File saved as: {fileName}")

    def load_widget_iterator(self, tab_name, flag_name, loaded_flag_arguments):
        tab = getattr(self.tab_manager, tab_name)  # Get tab object dynamically
        widget_name = f"{flag_name}_input"  # Construct widget name
        widget = getattr(tab, widget_name)  # Get widget object dynamically

        try:
            value = loaded_flag_arguments[tab_name][f"--{flag_name}"]
        except KeyError as e:
            raise KeyError(
                f"Could not find value for '{tab_name}' with flag '{flag_name}' in loaded_flag_arguments."
            ) from e

        if isinstance(widget, QComboBox) and hasattr(widget, "setCurrentText"):
            widget.setCurrentText(str(value))
        elif isinstance(widget, QLineEdit) and hasattr(widget, "setText"):
            widget.setText(str(value))
        else:
            raise TypeError(
                f"Widget '{widget_name}' is of an unsupported type: {type(widget).__name__} or does not support setting a value."
            )

    def load_button_clicked(self):
        manager = UserInputPairsManager("ace_flow")
        loaded_flag_arguments, metadata = manager.load_from_json(
            "/code/miracl/flow/ace_gui/test.mdat"
        )
        print(loaded_flag_arguments)
        print(metadata)
        # temp_load = loaded_flag_arguments["clusterwise_tab"]["--pcs_num_perm"]
        # self.tab_manager.clusterwise_tab.pcs_num_perm_input.setText(temp_load)
        test_dict = {
            "num_perm": ["clusterwise_tab", "pcs_num_perm"],
            "img_res": ["clusterwise_tab", "pcs_img_resolution"],
            "chan_num": ["conversion_tab", "ctn_channum"],
            "chan_pre": ["conversion_tab", "ctn_chanprefix"],
        }
        for value in test_dict.values():
            try:
                self.load_widget_iterator(value[0], value[1], loaded_flag_arguments)
            except KeyError as e:
                print(e)

    def help_button_clicked(self):
        """
        Handle the click event of the help button.

        This method is called when the help button is clicked. It displays
        help information to the user.
        """

        help_message_box = HelpMessageBox()
        help_message_box.exec_()

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

    def run_ace_cli(self):
        """
        Run ACE by invoking it through the cli.

        This method retrieves various input values from the main tab and prints
        them to the console. It also checks the state of the "Single or multi
        method arguments" checkbox and prints the corresponding mode.
        """

        all_user_input_pairs_dicts = self.create_cmd_dict()

        # Run ACE
        ace_interface_script_path = self.get_script_path(
            "miracl_workflow_ace_interface.py"
        )
        full_command = (
            f"python {str(ace_interface_script_path)} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['main_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['conversion_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['segmentation_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['clarity_registration_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['voxelizing_warping_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['clusterwise_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['correlation_stats_tab'])} "
            f"{wu.craft_flags(all_user_input_pairs_dicts['heatmap_tab'])}"
        )  # Crafts cmd
        full_command_split = shlex.split(full_command)  # Split cmd for subprocess use

        logger.debug(f"FULL COMMAND: {full_command_split}")
        process = subprocess.Popen(
            full_command_split,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())

        stdout, stderr = process.communicate()

        if stdout:
            print(stdout)

        if stderr:
            print(stderr)

        if process.returncode != 0:
            stderr_lines = stderr.strip().split("\n")
            error_message = "\n".join(stderr_lines[-1:])
            QMessageBox.critical(None, "Error", error_message)
            return False

        print("Command executed successfully!")
        return True

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


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
