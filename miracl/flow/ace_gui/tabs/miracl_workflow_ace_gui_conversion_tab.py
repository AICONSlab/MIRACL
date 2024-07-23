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

import ast
from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
)

from PyQt5.QtCore import Qt
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser


class ConversionTab(QWidget):
    def __init__(self):
        super().__init__()
        conversion_layout = QFormLayout()
        self.setLayout(conversion_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)
        parser_vals_dict = wu.extract_arguments_to_dict(args_parser)

        ####################
        # METHOD SELECTION #
        ####################

        self.conversion_channel_number_input = wu.create_digit_text_field(
            conversion_layout,
            "Channel #:",
            parser_vals_dict["ctn_channum"]["help"],
            "0",
        )

        self.conversion_channel_prefix_input = wu.create_text_field(
            conversion_layout,
            "Channel prefix:",
            parser_vals_dict["ctn_chanprefix"]["help"],
            "none"
            if parser_vals_dict["ctn_chanprefix"]["default"] == "None"
            else parser_vals_dict["ctn_chanprefix"]["default"],
            "alphanumeric",
        )

        self.conversion_output_channel_name_input = wu.create_text_field(
            conversion_layout,
            "Output channel name:",
            parser_vals_dict["ctn_channame"]["help"],
            parser_vals_dict["ctn_channame"]["default"],
            "alphanumeric",
        )

        self.conversion_output_nii_name_input = wu.create_text_field(
            conversion_layout,
            "Out nii name:",
            parser_vals_dict["ctn_outnii"]["help"],
            parser_vals_dict["ctn_outnii"]["default"],
            "alphanumeric",
        )

        (
            self.conversion_center_label_input,
            self.conversion_center_input_1,
            self.conversion_center_input_2,
            self.conversion_center_input_3,
        ) = wu.create_three_text_input_widget(
            conversion_layout,
            "Nii center:",
            parser_vals_dict["ctn_center"]["help"],
            [
                str(num)
                for num in ast.literal_eval(parser_vals_dict["ctn_center"]["default"])
            ],
            [parser_vals_dict["ctn_center"]["type"]]
            * len(
                [
                    str(num)
                    for num in ast.literal_eval(
                        parser_vals_dict["ctn_center"]["default"]
                    )
                ]
            ),
        )

        self.conversion_dx_z_input = wu.create_digit_spinbox(
            conversion_layout, "Z-axis dx:", parser_vals_dict["ctn_downzdim"]["help"], 1
        )

        self.conversion_prev_dx_input = wu.create_digit_spinbox(
            conversion_layout,
            "Previous dx:",
            parser_vals_dict["ctn_prevdown"]["help"],
            1,
        )

        self.conversion_percentile_thr_input = wu.create_digit_text_field(
            conversion_layout,
            "% threshold intensity corr:",
            parser_vals_dict["ctn_percentile_thr"]["help"],
            "0.01",
            "float",
        )