#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correlation and Stats

Description:
    View for correlation and statistics.

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
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser
from miracl.flow.ace_gui.miracl_workflow_ace_gui_flag_config import FlagConfig


class CorrelationStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        correlation_stats_layout = QFormLayout()
        self.setLayout(correlation_stats_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)
        corr_stats_dict = FlagConfig().create_correlation_stats()

        ###############
        # CORRELATION #
        ###############

        wu.create_section_title(correlation_stats_layout, "<b>Correlation</b>")
        self.corr_pvaluethr_input = wu.create_digit_spinbox(
            correlation_stats_layout,
            corr_stats_dict["corr_pvaluethr"]["label"],
            corr_stats_dict["corr_pvaluethr"]["help"],
            corr_stats_dict["corr_pvaluethr"]["default"],
            corr_stats_dict["corr_pvaluethr"]["min_val"],
            corr_stats_dict["corr_pvaluethr"]["max_val"],
            corr_stats_dict["corr_pvaluethr"]["type"],
            corr_stats_dict["corr_pvaluethr"]["increment_val"],
            corr_stats_dict["corr_pvaluethr"]["nr_decimals"],
        )

        ##############
        # STATISTICS #
        ##############

        wu.create_section_title(correlation_stats_layout, "<b>Statistics</b>")
        (
            self.stats_atlasdir_label_input,
            self.stats_atlasdir_path_input,
            self.stats_atlasdir_button_input,
        ) = wu.create_path_input_widget(
            self,
            correlation_stats_layout,
            corr_stats_dict["stats_atlasdir"]["label"],
            corr_stats_dict["stats_atlasdir"]["help"],
            "Select folder",
        )

        self.stats_poutfile_input = wu.create_text_field(
            correlation_stats_layout,
            corr_stats_dict["stats_poutfile"]["label"],
            corr_stats_dict["stats_poutfile"]["help"],
            corr_stats_dict["stats_poutfile"]["default"],
            corr_stats_dict["stats_poutfile"]["validator"],
        )
