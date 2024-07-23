#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cluster-wise

Description:
    View for cluster-wise statistics.

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


class ClusterwiseTab(QWidget):
    def __init__(self):
        super().__init__()
        clusterwise_layout = QFormLayout()
        self.setLayout(clusterwise_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        parser_vals_dict = wu.extract_arguments_to_dict(args_parser)

        print(f"PARSER PARSER PARSER: {parser_vals_dict}")

        (
            self.clusterwise_atlas_folder_label_input,
            self.clusterwise_atlas_folder_path_input,
            self.clusterwise_atlas_folder_button_input,
        ) = wu.create_path_input_widget(
            self,
            clusterwise_layout,
            "Path to altas dir:",
            parser_vals_dict["pcs_atlas_dir"]["help"],
            "Select folder",
        )

        self.clusterwise_nr_permutations_input = wu.create_digit_text_field(
            clusterwise_layout,
            "# permutations:",
            parser_vals_dict["pcs_num_perm"]["help"],
            parser_vals_dict["pcs_num_perm"]["default"],
        )

        self.clusterwise_image_resolution_input = wu.create_multiple_choice(
            clusterwise_layout,
            "Resolution of images (um):",
            parser_vals_dict["pcs_img_resolution"]["help"],
            parser_vals_dict["pcs_img_resolution"]["choices"],
            parser_vals_dict["pcs_img_resolution"]["default"],
        )

        self.clusterwise_fwhm_smoothing_input = wu.create_digit_text_field(
            clusterwise_layout,
            "fwhm of Gaussian kernel (px):",
            parser_vals_dict["pcs_smoothing_fwhm"]["help"],
            parser_vals_dict["pcs_smoothing_fwhm"]["default"],
        )

        self.clusterwise_thr_start_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce threshold start:",
            parser_vals_dict["pcs_tfce_start"]["help"],
            parser_vals_dict["pcs_tfce_start"]["default"],
            parser_vals_dict["pcs_tfce_start"]["type"],
        )

        self.clusterwise_thr_step_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce threshold step:",
            parser_vals_dict["pcs_tfce_step"]["help"],
            parser_vals_dict["pcs_tfce_step"]["default"],
            parser_vals_dict["pcs_tfce_step"]["type"],
        )

        self.clusterwise_cpu_load_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "% CPU's for parallelization:",
            parser_vals_dict["pcs_cpu_load"]["help"],
            parser_vals_dict["pcs_cpu_load"]["default"],
            0.00,
            1.00,
            parser_vals_dict["pcs_cpu_load"]["type"],
            0.01,
            2,
        )

        self.clusterwise_tfce_h_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce H power:",
            parser_vals_dict["pcs_tfce_h"]["help"],
            parser_vals_dict["pcs_tfce_h"]["default"],
            "float",
        )

        self.clusterwise_tfce_e_input = wu.create_digit_text_field(
            clusterwise_layout,
            "tfce E power:",
            parser_vals_dict["pcs_tfce_e"]["help"],
            parser_vals_dict["pcs_tfce_e"]["default"],
            parser_vals_dict["pcs_tfce_e"]["type"],
        )

        self.clusterwise_step_down_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "Step down p-value:",
            parser_vals_dict["pcs_step_down_p"]["help"],
            parser_vals_dict["pcs_step_down_p"]["default"],
            0.0000,
            1.0000,
            parser_vals_dict["pcs_step_down_p"]["type"],
            0.01,
            4,
        )

        self.clusterwise_mask_thr_input = wu.create_digit_spinbox(
            clusterwise_layout,
            "% for binarizing mean diff:",
            parser_vals_dict["pcs_mask_thr"]["help"],
            parser_vals_dict["pcs_mask_thr"]["default"],
            0,
            100,
            parser_vals_dict["pcs_mask_thr"]["type"],
            1,
        )
