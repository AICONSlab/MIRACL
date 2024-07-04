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

from PyQt5.QtWidgets import QTabWidget
from miracl_workflow_ace_gui_main_tab import MainTab
from miracl_workflow_ace_gui_clarity_registration_tab import ClarityRegistrationTab
from miracl_workflow_ace_gui_voxelizing_warping_tab import VoxelizingWarpingTab
from miracl_workflow_ace_gui_conversion_tab import ConversionTab


class TabManager:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        self.main_tab = MainTab()
        self.conversion_tab = ConversionTab()
        self.clarity_registration_tab = ClarityRegistrationTab()
        self.voxelizing_warping_tab = VoxelizingWarpingTab()

        self.additional_tabs = [
            self.conversion_tab,
            self.clarity_registration_tab,
            self.voxelizing_warping_tab,
        ]

        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.conversion_tab, "Conversion")
        self.tab_widget.addTab(self.clarity_registration_tab, "Registration")
        self.tab_widget.addTab(self.voxelizing_warping_tab, "Voxelizing/Warping")
