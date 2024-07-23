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
from miracl.flow.ace_gui.miracl_workflow_ace_gui_flag_config import FlagConfig


class ConversionTab(QWidget):
    def __init__(self):
        super().__init__()
        conversion_layout = QFormLayout()
        self.setLayout(conversion_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        parser_vals_dict = wu.extract_arguments_to_dict(args_parser)
        conv_dict = FlagConfig().create_conversion()
        print(f"CONV CONV CONV: {conv_dict}")

        ####################
        # METHOD SELECTION #
        ####################

        self.conv_channum_input = wu.create_digit_text_field(
            conversion_layout,
            conv_dict["conv_channum"]["label"],
            conv_dict["conv_channum"]["help"],
            conv_dict["conv_channum"]["default"],
        )

        self.conv_chanprefix_input = wu.create_text_field(
            conversion_layout,
            conv_dict["conv_chanprefix"]["label"],
            conv_dict["conv_chanprefix"]["help"],
            "none"
            if conv_dict["conv_chanprefix"]["default"] == "None"
            else conv_dict["conv_chanprefix"]["default"],
            conv_dict["conv_chanprefix"]["validator"],
        )

        self.conv_chanoutname_input = wu.create_text_field(
            conversion_layout,
            conv_dict["conv_chanoutname"]["label"],
            conv_dict["conv_chanoutname"]["help"],
            conv_dict["conv_chanoutname"]["default"],
            conv_dict["conv_chanoutname"]["validator"],
        )

        self.conv_outnii_input = wu.create_text_field(
            conversion_layout,
            conv_dict["conv_outnii"]["label"],
            conv_dict["conv_outnii"]["help"],
            conv_dict["conv_outnii"]["default"],
            conv_dict["conv_outnii"]["validator"],
        )

        (
            self.conv_center_label_input,
            self.conv_center_input_1,
            self.conv_center_input_2,
            self.conv_center_input_3,
        ) = wu.create_three_text_input_widget(
            conversion_layout,
            conv_dict["conv_center"]["label"],
            conv_dict["conv_center"]["help"],
            [str(num) for num in ast.literal_eval(conv_dict["conv_center"]["default"])],
            [parser_vals_dict["ctn_center"]["type"]]
            * len(
                [
                    str(num)
                    for num in ast.literal_eval(conv_dict["conv_center"]["default"])
                ]
            ),
        )

        self.conv_downzdim_input = wu.create_digit_spinbox(
            conversion_layout,
            conv_dict["conv_downzdim"]["label"],
            conv_dict["conv_downzdim"]["help"],
            conv_dict["conv_downzdim"]["default"],
        )

        self.conv_prevdown_input = wu.create_digit_spinbox(
            conversion_layout,
            conv_dict["conv_prevdown"]["label"],
            conv_dict["conv_prevdown"]["help"],
            conv_dict["conv_prevdown"]["default"],
        )

        self.conv_percentilethr_input = wu.create_digit_text_field(
            conversion_layout,
            conv_dict["conv_percentilethr"]["label"],
            conv_dict["conv_percentilethr"]["help"],
            conv_dict["conv_percentilethr"]["default"],
            conv_dict["conv_percentilethr"]["type"],
        )
