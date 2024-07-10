#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tab Manager

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
from miracl_workflow_ace_gui_segmentation_tab import SegmentationTab
from miracl_workflow_ace_gui_clarity_registration_tab import ClarityRegistrationTab
from miracl_workflow_ace_gui_voxelizing_warping_tab import VoxelizingWarpingTab
from miracl_workflow_ace_gui_conversion_tab import ConversionTab
from miracl_workflow_ace_gui_clusterwise_tab import ClusterwiseTab
from miracl_workflow_ace_gui_correlation_stats_tab import CorrelationStatsTab
from miracl_workflow_ace_gui_heatmap_tab import HeatmapTab


class TabManager:
    def __init__(self, tab_widget):
        self.tab_widget = tab_widget

        self.main_tab = MainTab()
        self.conversion_tab = ConversionTab()
        self.segmentation_tab = SegmentationTab()
        self.clarity_registration_tab = ClarityRegistrationTab()
        self.voxelizing_warping_tab = VoxelizingWarpingTab()
        self.clusterwise_tab = ClusterwiseTab()
        self.correlation_stats_tab = CorrelationStatsTab()
        self.heatmap_tab = HeatmapTab()

        self.additional_tabs = [
            self.conversion_tab,
            self.segmentation_tab,
            self.clarity_registration_tab,
            self.voxelizing_warping_tab,
            self.clusterwise_tab,
            self.correlation_stats_tab,
            self.heatmap_tab,
        ]

        self.tab_widget.addTab(self.main_tab, "Main")
        self.tab_widget.addTab(self.conversion_tab, "Conversion")
        self.tab_widget.addTab(self.segmentation_tab, "Segmentation")
        self.tab_widget.addTab(self.clarity_registration_tab, "Registration")
        self.tab_widget.addTab(self.voxelizing_warping_tab, "Voxelizing/Warping")
        self.tab_widget.addTab(self.clusterwise_tab, "Cluster-wise")
        self.tab_widget.addTab(self.correlation_stats_tab, "Correlation/Stats")
        self.tab_widget.addTab(self.heatmap_tab, "Heatmap")
