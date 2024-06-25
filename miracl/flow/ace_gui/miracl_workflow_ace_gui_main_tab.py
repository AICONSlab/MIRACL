#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Utilities

Description:
    View for ACE main tab for ACE flow GUI.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
)
from PyQt5.QtCore import Qt
from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu


class MainTab(QWidget):
    def __init__(self):
        super().__init__()
        main_tab_layout = QFormLayout()
        self.setLayout(main_tab_layout)

        ####################
        # METHOD SELECTION #
        ####################

        wu.create_section_title(
            main_tab_layout, "<b>Single or multi method arguments</b>"
        )

        # Checkbox to toggle between methods
        self.single_checkbox = wu.create_method_checkbox(
            self,
            main_tab_layout,
            "Check for group, leave unchecked for single (default)",
        )

        (
            self.single_method_label_input,
            self.single_method_path_input,
            self.single_method_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Single tif/tiff data folder:", "Select folder"
        )

        (
            self.multi_method_ctrl_label_input,
            self.multi_method_ctrl_path_input,
            self.multi_method_ctrl_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Base control dir:", "Select folder"
        )

        (
            self.multi_method_ctrl_tif_label_input,
            self.multi_method_ctrl_tif_path_input,
            self.multi_method_ctrl_tif_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Base control tif/tiff dir:", "Select folder"
        )

        (
            self.multi_method_treated_label_input,
            self.multi_method_treated_path_input,
            self.multi_method_treated_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Base treated dir:", "Select folder"
        )

        (
            self.multi_method_treated_tif_label_input,
            self.multi_method_treated_tif_path_input,
            self.multi_method_treated_tif_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Base treated tif/tiff dir:", "Select folder"
        )

        ######################
        # REQUIRED ARGUMENTS #
        ######################

        wu.create_section_title(main_tab_layout, "<b>Required arguments</b>")

        (
            self.output_folder_label_input,
            self.output_folder_path_input,
            self.output_folder_button_input,
        ) = wu.create_path_input_widget(
            self, main_tab_layout, "Output folder:", "Select folder"
        )

        self.model_architecture_input = wu.create_multiple_choice(
            main_tab_layout,
            "Model architecture:",
            ["UNet", "UNETR", "Ensemble"],
            "UNet",
        )

        self.x_res_field_input = wu.create_resolution(
            main_tab_layout, "X-res:", "float"
        )
        self.y_res_field_input = wu.create_resolution(
            main_tab_layout, "Y-res:", "float"
        )
        self.z_res_field_input = wu.create_resolution(
            main_tab_layout, "Z-res:", "float"
        )

        ####################
        # USEFUL ARGUMENTS #
        ####################

        wu.create_section_title(main_tab_layout, "<b>Useful/important arguments</b>")

        self.gpu_index_input = wu.create_digit_spinbox(main_tab_layout, "GPU index:", 0)

        self.conversion_dx_input = wu.create_digit_spinbox(
            main_tab_layout, "Conversion_dx", 5
        )

        self.orientation_code_input = wu.create_orientation_code(
            main_tab_layout, "Orientation code:", "ALS"
        )

        self.labels_voxel_size_input = wu.create_multiple_choice(
            main_tab_layout, "Labels voxel size:", ["10", "25", "50"], "10"
        )

        self.voxelixation_dx_input = wu.create_digit_spinbox(
            main_tab_layout, "Voxelization dx:", 5
        )

        self.warping_voxel_size_input = wu.create_multiple_choice(
            main_tab_layout, "Warping voxel size:", ["10", "25", "50"], "25"
        )

        # self.create_rerun_registration(main_tab_layout)
        self.rerun_registration_input = wu.create_multiple_choice(
            main_tab_layout, "Rerun registration: ", ["Yes", "No"], "No"
        )
        self.rerun_segmentation_input = wu.create_multiple_choice(
            main_tab_layout, "Rerun segmentation: ", ["Yes", "No"], "No"
        )
        self.rerun_conversion_input = wu.create_multiple_choice(
            main_tab_layout, "Rerun conversion: ", ["Yes", "No"], "No"
        )

        ################
        # TOGGLE LOGIC #
        ################

        # Connect method checkbox to widgets
        self.single_checkbox.stateChanged.connect(self.toggle_single_mode)
        # Initialize with checkbox unchecked i.e. single mode enabled
        self.toggle_single_mode(Qt.Unchecked)

    def toggle_single_mode(self, state):
        """
        Toggle between single mode and multi mode based on the checkbox state.

        This method enables or disables widgets related to single mode and multi mode
        based on the state of the checkbox.

        :param state: The state of the checkbox. It can be Qt.Checked or Qt.Unchecked.
        :type state: int
        """
        single_mode_widgets = [
            self.single_method_label_input,
            self.single_method_path_input,
            self.single_method_button_input,
        ]

        multi_mode_widgets = [
            self.multi_method_ctrl_label_input,
            self.multi_method_ctrl_path_input,
            self.multi_method_ctrl_button_input,
            self.multi_method_ctrl_tif_label_input,
            self.multi_method_ctrl_tif_path_input,
            self.multi_method_ctrl_tif_button_input,
            self.multi_method_treated_label_input,
            self.multi_method_treated_path_input,
            self.multi_method_treated_button_input,
            self.multi_method_treated_tif_label_input,
            self.multi_method_treated_tif_path_input,
            self.multi_method_treated_tif_button_input,
        ]

        MainTab.set_widgets_enabled(single_mode_widgets, state != Qt.Checked)
        MainTab.set_widgets_enabled(multi_mode_widgets, state == Qt.Checked)

    @staticmethod
    def set_widgets_enabled(widgets, enabled):
        """
        Enable or disable a list of widgets.

        This static method iterates over a list of widgets and sets their enabled state
        based on the provided boolean value.

        :param widgets: A list of widgets to be enabled or disabled.
        :type widgets: list[QWidget]
        :param enabled: A boolean value indicating whether to enable or disable the widgets.
        :type enabled: bool
        """
        for widget in widgets:
            widget.setEnabled(enabled)
