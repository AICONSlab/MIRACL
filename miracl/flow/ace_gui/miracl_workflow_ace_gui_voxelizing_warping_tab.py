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


class VoxelizingWarpingTab(QWidget):
    def __init__(self):
        super().__init__()
        voxelizing_warping_layout = QFormLayout()
        self.setLayout(voxelizing_warping_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        ################
        # VOXELIZATION #
        ################

        wu.create_section_title(voxelizing_warping_layout, "<b>Voxelization</b>")

