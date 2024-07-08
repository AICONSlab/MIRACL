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


class CorrelationStatsTab(QWidget):
    def __init__(self):
        super().__init__()
        correlation_stats_layout = QFormLayout()
        self.setLayout(correlation_stats_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        ###############
        # CORRELATION #
        ###############

        wu.create_section_title(correlation_stats_layout, "<b>Correlation</b>")
        self.correlation_stats_correlation_cf_pvalue_input = wu.create_digit_spinbox(
            correlation_stats_layout,
            "Threshold binarizing p-value:",
            help_dict["cf_pvalue_thr"],
            0.05,
            0.0000,
            1.0000,
            "float",
            0.01,
            4,
        )

        ##############
        # STATISTICS #
        ##############

        wu.create_section_title(correlation_stats_layout, "<b>Statistics</b>")
        (
            self.correlation_stats_stats_atlas_folder_label_input,
            self.correlation_stats_stats_atlas_folder_path_input,
            self.correlation_stats_stats_atlas_folder_button_input,
        ) = wu.create_path_input_widget(
            self,
            correlation_stats_layout,
            "Path to altas dir:",
            help_dict["u_atlas_dir"],
            "Select folder",
        )

        self.correlation_stats_stats_outfile_input = wu.create_text_field(
            correlation_stats_layout,
            "Output filename:",
            help_dict["p_outfile"],
            "pvalue_heatmap",
            "strcon",
        )
