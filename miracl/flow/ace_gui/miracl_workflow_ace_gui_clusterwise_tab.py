#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Utilities

Description:
    Tab manager for ACE flow GUI.

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
from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser


class ClusterwiseTab(QWidget):
    def __init__(self):
        super().__init__()
        clusterwise_layout = QFormLayout()
        self.setLayout(clusterwise_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        (
            self.clusterwise_atlas_folder_label_input,
            self.clusterwise_atlas_folder_path_input,
            self.clusterwise_atlas_folder_button_input,
        ) = wu.create_path_input_widget(
            self,
            clusterwise_layout,
            "Path to altas dir:",
            help_dict["pcs_atlas_dir"],
            "Select folder",
        )

        self.clusterwise_nr_permutations_input = wu.create_digit_text_field(
            clusterwise_layout, "# permutations:", help_dict["pcs_num_perm"], "500"
        )

        self.clusterwise_image_resolution_input = wu.create_multiple_choice(
            clusterwise_layout,
            "Resolution of images (um):",
            help_dict["pcs_img_resolution"],
            ["10", "25", "50"],
            "25",
        )

        self.clusterwise_fwhm_smoothing_input = wu.create_digit_text_field(
            clusterwise_layout,
            "fwhm of Gaussian kernel (px):",
            help_dict["pcs_smoothing_fwhm"],
            "3",
        )

        self.clusterwise_thr_start_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce threshold start:",
            help_dict["pcs_tfce_start"],
            "0.01",
            "float",
        )

        self.clusterwise_thr_step_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce threshold step:",
            help_dict["pcs_tfce_step"],
            "5",
            "int",
        )

        self.clusterwise_cpu_load_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "% CPU's for parallelization:",
            help_dict["pcs_cpu_load"],
            0.90,
            0.00,
            1.00,
            "float",
            0.01,
            2
        )

        self.clusterwise_tfce_h_input = wu.create_digit_text_field(
            clusterwise_layout, "tfce H power:", help_dict["pcs_tfce_h"], "2", "float"
        )

        self.clusterwise_tfce_e_input = wu.create_digit_text_field(
            clusterwise_layout, "tfce E power:", help_dict["pcs_tfce_e"], "0.5", "float"
        )

        self.clusterwise_step_down_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "Step down p-value:",
            help_dict["pcs_step_down_p"],
            0.3,
            0.0000,
            1.0000,
            "float",
            0.01,
            4
        )

        self.clusterwise_mask_thr_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "% for binarizing mean diff:",
            help_dict["pcs_mask_thr"],
            95,
            0,
            100,
            "int",
            1,
        )
