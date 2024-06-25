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


class TabManager:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        self.main_tab = MainTab()
        self.clarity_registration_tab = ClarityRegistrationTab()
        self.voxelizing_warping_tab = VoxelizingWarpingTab()

        self.additional_tabs = [
            self.clarity_registration_tab,
            self.voxelizing_warping_tab,
        ]

        self.tab_widget.addTab(self.main_tab, "ACE")
        self.tab_widget.addTab(self.clarity_registration_tab, "CLARITY registration")
        self.tab_widget.addTab(self.voxelizing_warping_tab, "Voxelizing/warping")
