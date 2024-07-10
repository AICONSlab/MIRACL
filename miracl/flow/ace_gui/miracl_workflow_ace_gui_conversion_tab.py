#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversion

Description:
    View for conversion.

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


class ConversionTab(QWidget):
    def __init__(self):
        super().__init__()
        conversion_layout = QFormLayout()
        self.setLayout(conversion_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        ####################
        # METHOD SELECTION #
        ####################

        self.conversion_channel_number_input = wu.create_digit_text_field(
            conversion_layout, "Channel #:", help_dict["ctn_channum"], "0"
        )

        self.conversion_channel_prefix_input = wu.create_text_field(
            conversion_layout,
            "Channel prefix:",
            help_dict["ctn_chanprefix"],
            "none",
            "alphanumeric",
        )

        self.conversion_output_channel_name_input = wu.create_text_field(
            conversion_layout,
            "Output channel name:",
            help_dict["ctn_channame"],
            "auto",
            "alphanumeric",
        )

        self.conversion_output_nii_name_input = wu.create_text_field(
            conversion_layout,
            "Out nii name:",
            help_dict["ctn_outnii"],
            "SHIELD",
            "alphanumeric",
        )

        (
            self.conversion_center_label_input,
            self.conversion_center_input_1,
            self.conversion_center_input_2,
            self.conversion_center_input_3,
        ) = wu.create_three_text_input_widget(
            conversion_layout, "Nii center:", help_dict["ctn_center"], ["0", "0", "0"], ["int", "int", "int"]
        )

        self.conversion_dx_z_input = wu.create_digit_spinbox(
            conversion_layout, "Z-axis dx:", help_dict["ctn_downzdim"], 1
        )

        self.conversion_prev_dx_input = wu.create_digit_spinbox(
            conversion_layout, "Previous dx:", help_dict["ctn_prevdown"], 1
        )

        self.conversion_percentile_thr_input = wu.create_digit_text_field(
            conversion_layout,
            "% threshold intensity corr:",
            help_dict["ctn_percentile_thr"],
            "0.01",
            "float",
        )
