#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Heatmap

Description:
    View for heatmap.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

import ast
from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
)

from PyQt5.QtCore import Qt
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser


class HeatmapTab(QWidget):
    def __init__(self):
        super().__init__()
        heatmap_layout = QFormLayout()
        self.setLayout(heatmap_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)
        parser_vals_dict = wu.extract_arguments_to_dict(args_parser)

        (
            self.heatmap_group_1_label_input,
            self.heatmap_group_1_path_input,
            self.heatmap_group_1_button_input,
        ) = wu.create_path_input_widget(
            self,
            heatmap_layout,
            "Path to group 1 dir:",
            help_dict["sh_group1"],
            "Select folder",
        )

        (
            self.heatmap_group_2_label_input,
            self.heatmap_group_2_path_input,
            self.heatmap_group_2_button_input,
        ) = wu.create_path_input_widget(
            self,
            heatmap_layout,
            "Path to group 2 dir:",
            help_dict["sh_group2"],
            "Select folder",
        )

        self.heatmap_voxel_size_input = wu.create_multiple_choice(
            heatmap_layout,
            "Voxel size (um):",
            help_dict["sh_vox"],
            ["10", "25", "50"],
            "10",
        )

        self.heatmap_sigma_input = wu.create_digit_spinbox(
            heatmap_layout,
            "Guassian smoothing sigma:",
            help_dict["sh_sigma"],
            4,
            0,
            1000,
            "int",
            1,
        )

        self.heatmap_percentile_input = wu.create_digit_spinbox(
            heatmap_layout,
            "% threshold svg:",
            help_dict["sh_percentile"],
            10,
            0,
            100,
            "int",
            1,
        )

        self.heatmap_colourmap_positive_input = wu.create_text_field(
            heatmap_layout,
            "Matplotlib colourmap pos values:",
            help_dict["sh_colourmap_pos"],
            "Reds",
            "str",
        )

        self.heatmap_colourmap_negative_input = wu.create_text_field(
            heatmap_layout,
            "Matplotlib colourmap neg values:",
            help_dict["sh_colourmap_neg"],
            "Blues",
            "str",
        )

        (
            self.heatmap_slicing_sagittal_axis_label_input,
            self.heatmap_slicing_sagittal_axis_start_input,
            self.heatmap_slicing_sagittal_axis_interval_input,
            self.heatmap_slicing_sagittal_axis_nr_slices_input,
            self.heatmap_slicing_sagittal_axis_nr_rows_input,
            self.heatmap_slicing_sagittal_axis_nr_cols_input,
        ) = wu.create_multiple_text_input_widget(
            heatmap_layout,
            "Slicing across sagittal axis:",
            help_dict["sh_sagittal"],
            ["none", "none", "none", "none", "none"],
            ["Start:", "Interval:", "#Slices:", "#Rows:", "#Cols:"],
        )

        (
            self.heatmap_slicing_coronal_axis_label_input,
            self.heatmap_slicing_coronal_axis_start_input,
            self.heatmap_slicing_coronal_axis_interval_input,
            self.heatmap_slicing_coronal_axis_nr_slices_input,
            self.heatmap_slicing_coronal_axis_nr_rows_input,
            self.heatmap_slicing_coronal_axis_nr_cols_input,
        ) = wu.create_multiple_text_input_widget(
            heatmap_layout,
            "Slicing across coronal axis:",
            help_dict["sh_coronal"],
            ["none", "none", "none", "none", "none"],
            ["Start:", "Interval:", "#Slices:", "#Rows:", "#Cols:"],
        )

        (
            self.heatmap_slicing_axial_axis_label_input,
            self.heatmap_slicing_axial_axis_start_input,
            self.heatmap_slicing_axial_axis_interval_input,
            self.heatmap_slicing_axial_axis_nr_slices_input,
            self.heatmap_slicing_axial_axis_nr_rows_input,
            self.heatmap_slicing_axial_axis_nr_cols_input,
        ) = wu.create_multiple_text_input_widget(
            heatmap_layout,
            "Slicing across axial axis:",
            help_dict["sh_axial"],
            ["none", "none", "none", "none", "none"],
            ["Start:", "Interval:", "#Slices:", "#Rows:", "#Cols:"],
        )

        (
            self.heatmap_figure_dims_label_input,
            self.heatmap_figure_dims_width_input,
            self.heatmap_figure_dims_height_input,
        ) = wu.create_multiple_text_input_widget(
            heatmap_layout,
            "Figure dimensions:",
            help_dict["sh_figure_dim"],
            ["none", "none"],
            ["Width:", "Height:"],
        )

        (
            self.heatmap_output_folder_label_input,
            self.heatmap_output_folder_path_input,
            self.heatmap_output_folder_button_input,
        ) = wu.create_path_input_widget(
            self,
            heatmap_layout,
            "Output folder:",
            help_dict["sh_dir_outfile"],
            "Select folder",
        )

        (
            self.heatmap_output_filenames_label_input,
            self.heatmap_output_filenames_group_1_input,
            self.heatmap_output_filenames_group_2_input,
            self.heatmap_output_filenames_group_diff_input,
        ) = wu.create_three_text_input_widget(
            heatmap_layout,
            "Output filenames:",
            help_dict["sh_outfile"],
            [
                str(num)
                for num in ast.literal_eval(parser_vals_dict["sh_outfile"]["default"])
            ],
            ["strcon"]
            * len(
                [
                    str(num)
                    for num in ast.literal_eval(
                        parser_vals_dict["sh_outfile"]["default"]
                    )
                ]
            ),
        )

        self.heatmap_extension_input = wu.create_text_field(
            heatmap_layout,
            "Heatmap fig extension:",
            help_dict["sh_extension"],
            "tiff",
            "strint",
        )

        self.heatmap_dpi_input = wu.create_digit_text_field(
            heatmap_layout,
            "Dots per inch:",
            help_dict["sh_dpi"],
            500,
            "int",
        )
