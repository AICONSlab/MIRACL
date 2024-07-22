#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voxelizing and Warping

Description:
    Voxelization and warping view.

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
    QLabel,
    QComboBox,
)
from PyQt5.QtCore import Qt
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser


class VoxelizingWarpingTab(QWidget):
    def __init__(self):
        super().__init__()
        voxelizing_warping_layout = QFormLayout()
        self.setLayout(voxelizing_warping_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        ################
        # VOXELIZATION #
        ################

        wu.create_section_title(voxelizing_warping_layout, "<b>Voxelization</b>")

        (
            self.vox_warp_vox_axes_label_input,
            self.vox_warp_vox_axes_x_input,
            self.vox_warp_vox_axes_y_input,
            self.vox_warp_vox_axes_z_input,
        ) = wu.create_multiple_text_input_widget(
            voxelizing_warping_layout,
            "Voxel sizes (um):",
            help_dict["rva_vz_res"],
            ["1", "1", "1"],
            ["x:", "y:", "z:"],
        )

        ###########
        # WARPING #
        ###########

        wu.create_section_title(voxelizing_warping_layout, "<b>Warping</b>")

        (
            self.vox_warp_warp_input_folder_label_input,
            self.vox_warp_warp_input_folder_path_input,
            self.vox_warp_warp_input_folder_button_input,
        ) = wu.create_path_input_widget(
            self,
            voxelizing_warping_layout,
            "Path to CLARITY reg folder:",
            help_dict["rwc_input_folder"],
            "Select folder",
        )

        (
            self.vox_warp_warp_input_nii_file_label_input,
            self.vox_warp_warp_input_nii_file_path_input,
            self.vox_warp_warp_input_nii_file_button_input,
        ) = wu.create_path_input_widget(
            self,
            voxelizing_warping_layout,
            "Path to dx CLARITY nii file:",
            help_dict["rwc_input_nii"],
            "Select file",
            select_files=True,
            file_filter="All Files (*)",
        )

        self.vox_warp_warp_seg_channel_input = wu.create_text_field(
            voxelizing_warping_layout,
            "Seg channel (ex: 'green'):",
            help_dict["rwc_seg_channel"],
            "none",
            "alphanumeric",
        )
