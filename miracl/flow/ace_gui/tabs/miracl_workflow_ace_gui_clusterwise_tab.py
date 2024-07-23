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
)
from PyQt5.QtCore import Qt
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow.ace_gui.miracl_workflow_ace_gui_flag_config import FlagConfig


class ClusterwiseTab(QWidget):
    def __init__(self):
        super().__init__()
        clusterwise_layout = QFormLayout()
        self.setLayout(clusterwise_layout)
        clust_dict = FlagConfig().create_clusterwise()

        (
            self.clust_atlasdir_label_input,
            self.clust_atlasdir_path_input,
            self.clust_atlasdir_button_input,
        ) = wu.create_path_input_widget(
            self,
            clusterwise_layout,
            clust_dict["clust_atlasdir"]["label"],
            clust_dict["clust_atlasdir"]["help"],
            "Select folder",
        )

        self.clust_numperm_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_numperm"]["label"],
            clust_dict["clust_numperm"]["help"],
            clust_dict["clust_numperm"]["default"],
        )

        self.clust_imgresolution_input = wu.create_multiple_choice(
            clusterwise_layout,
            clust_dict["clust_imgresolution"]["label"],
            clust_dict["clust_imgresolution"]["help"],
            clust_dict["clust_imgresolution"]["choices"],
            clust_dict["clust_imgresolution"]["default"],
        )

        self.clust_smoothingfwhm_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_smoothingfwhm"]["label"],
            clust_dict["clust_smoothingfwhm"]["help"],
            clust_dict["clust_smoothingfwhm"]["default"],
        )

        self.clust_tfcestart_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_tfcestart"]["label"],
            clust_dict["clust_tfcestart"]["help"],
            clust_dict["clust_tfcestart"]["default"],
            clust_dict["clust_tfcestart"]["type"],
        )

        self.clust_tfcestep_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_tfcestep"]["label"],
            clust_dict["clust_tfcestep"]["help"],
            clust_dict["clust_tfcestep"]["default"],
            clust_dict["clust_tfcestep"]["type"],
        )

        self.clust_cpuload_input = wu.create_digit_spinbox(
            clusterwise_layout,
            clust_dict["clust_cpuload"]["label"],
            clust_dict["clust_cpuload"]["help"],
            clust_dict["clust_cpuload"]["default"],
            clust_dict["clust_cpuload"]["min_val"],
            clust_dict["clust_cpuload"]["max_val"],
            clust_dict["clust_cpuload"]["type"],
            clust_dict["clust_cpuload"]["increment_val"],
            clust_dict["clust_cpuload"]["nr_decimals"],
        )

        self.clust_tfceh_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_tfceh"]["label"],
            clust_dict["clust_tfceh"]["help"],
            clust_dict["clust_tfceh"]["default"],
            clust_dict["clust_tfceh"]["type"],
        )

        self.clust_tfcee_input = wu.create_digit_text_field(
            clusterwise_layout,
            clust_dict["clust_tfcee"]["label"],
            clust_dict["clust_tfcee"]["help"],
            clust_dict["clust_tfcee"]["default"],
            clust_dict["clust_tfcee"]["type"],
        )

        self.clust_stepdownp_input = wu.create_digit_spinbox(
            clusterwise_layout,
            clust_dict["clust_stepdownp"]["label"],
            clust_dict["clust_stepdownp"]["help"],
            clust_dict["clust_stepdownp"]["default"],
            clust_dict["clust_stepdownp"]["min_val"],
            clust_dict["clust_stepdownp"]["max_val"],
            clust_dict["clust_stepdownp"]["type"],
            clust_dict["clust_stepdownp"]["increment_val"],
            clust_dict["clust_stepdownp"]["nr_decimals"],
        )

        self.clust_maskthr_input = wu.create_digit_spinbox(
            clusterwise_layout,
            clust_dict["clust_maskthr"]["label"],
            clust_dict["clust_maskthr"]["help"],
            clust_dict["clust_maskthr"]["default"],
            clust_dict["clust_maskthr"]["min_val"],
            clust_dict["clust_maskthr"]["max_val"],
            clust_dict["clust_maskthr"]["type"],
            clust_dict["clust_maskthr"]["increment_val"],
        )
