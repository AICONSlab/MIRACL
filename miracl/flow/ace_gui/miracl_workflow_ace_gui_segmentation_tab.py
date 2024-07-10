#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmentation

Description:
    Segmentation view

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
from miracl.flow import miracl_workflow_ace_parser


class SegmentationTab(QWidget):
    def __init__(self):
        super().__init__()
        segmentation_layout = QFormLayout()
        self.setLayout(segmentation_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        (
            self.segmentation_image_size_label_input,
            self.segmentation_image_size_height_input,
            self.segmentation_image_size_width_input,
            self.segmentation_image_size_depth_input,
        ) = wu.create_multiple_text_input_widget(
            segmentation_layout,
            "Image size (default: from header):",
            help_dict["sa_image_size"],
            ["none", "none", "none"],
            ["height:", "width:", "depth:"],
        )

        self.segmentation_nr_workers_input = wu.create_digit_spinbox(
            segmentation_layout,
            "# parallel CPU cores pre-processing:",
            help_dict["sa_nr_workers"],
            4,
            0,
            1000,
            "int",
            1,
            5,
        )

        self.segmentation_cache_rate_input = wu.create_digit_spinbox(
            segmentation_layout,
            "% raw data loaded into CPU:",
            help_dict["sa_cache_rate"],
            0.0,
            0.0,
            100.0,
            "float",
            1,
            1,
        )

        self.segmentation_batch_size_input = wu.create_digit_spinbox(
            segmentation_layout, "Batch size:", help_dict["sa_batch_size"], 4
        )

        self.segmentation_monte_carlo_input = wu.create_multiple_choice(
            segmentation_layout,
            "Use Monte Carlo dropout:",
            help_dict["sa_monte_carlo"],
            ["yes", "no"],
            "no",
        )

        self.segmentation_visualize_results_input = wu.create_multiple_choice(
            segmentation_layout,
            "Visualize model output:",
            help_dict["sa_visualize_results"],
            ["yes", "no"],
            "no",
        )

        self.segmentation_uncertainty_map_input = wu.create_multiple_choice(
            segmentation_layout,
            "Enable uncertainty map:",
            help_dict["sa_uncertainty_map"],
            ["yes", "no"],
            "no",
        )

        self.segmentation_binarization_thr_input = wu.create_digit_spinbox(
            segmentation_layout,
            "Binarization threshold:",
            help_dict["sa_binarization_threshold"],
            0.5,
            0.0,
            100.0,
            "float",
            0.1,
            1,
        )

        self.segmentation_brain_patch_skip_input = wu.create_digit_spinbox(
            segmentation_layout,
            "% threshold of brain patch to skip:",
            help_dict["sa_percentage_brain_patch_skip"],
            0.0,
            0.0,
            100.0,
            "float",
            1,
            1,
        )
