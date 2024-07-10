#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLARITY Registration

Description:
    View for CLARITY registration. 

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


class ClarityRegistrationTab(QWidget):
    def __init__(self):
        super().__init__()
        clarity_registration_layout = QFormLayout()
        self.setLayout(clarity_registration_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        self.reg_hemi_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Labels hemisphere",
            help_dict["rca_hemi"],
            ["combined", "split"],
            "combined",
        )

        (
            self.reg_allen_lbl_warp_label_input,
            self.reg_allen_lbl_warp_path_input,
            self.reg_allen_lbl_warp_button_input,
        ) = wu.create_path_input_widget(
            self,
            clarity_registration_layout,
            "Allen labels to warp:",
            help_dict["rca_allen_label"],
            "Select file",
            select_files=True,
            file_filter="All Files (*)",
        )

        (
            self.reg_cust_allen_atlas_label_input,
            self.reg_cust_allen_atlas_path_input,
            self.reg_cust_allen_atlas_button_input,
        ) = wu.create_path_input_widget(
            self,
            clarity_registration_layout,
            "Custom Allen atlas:",
            help_dict["rca_allen_atlas"],
            "Select file",
            select_files=True,
            file_filter="All Files (*)",
        )

        self.reg_side_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Side:",
            help_dict["rca_side"],
            ["right hemisphere", "left hemisphere"],
            "right hemisphere",
        )

        self.reg_mosaic_figure_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Create mosaic figure:",
            help_dict["rca_no_mosaic_fig"],
            ["yes", "no"],
            "yes",
        )

        self.reg_olfactory_bulb_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Olfactory bulb incl.:",
            help_dict["rca_olfactory_bulb"],
            ["not included", "included"],
            "not included",
        )

        self.reg_util_int_correction_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Utilfn intensity correction:",
            help_dict["rca_skip_cor"],
            ["run", "skip"],
            "run",
        )

        self.reg_warp_to_allen_input = wu.create_multiple_choice(
            clarity_registration_layout,
            "Warp CLARITY to Allen:",
            help_dict["rca_warp"],
            ["yes", "no"],
            "no",
        )
