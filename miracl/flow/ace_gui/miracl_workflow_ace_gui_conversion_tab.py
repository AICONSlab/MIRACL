# Conversion
from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
)

from PyQt5.QtCore import Qt
from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser


class ConversionTab(QWidget):
    def __init__(self):
        super().__init__()
        conversion_layout = QFormLayout()
        self.setLayout(conversion_layout)
        args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
        help_dict = wu.extract_help_texts(args_parser)

        ####################
        # METHOD SELECTION #
        ####################

        self.conversion_output_channel_name_input = wu.create_text_field(
            conversion_layout, "Output channel name:", help_dict["ctn_channame"], "auto"
        )

        self.conversion_output_nii_name_input = wu.create_text_field(
            conversion_layout, "Out nii name:", help_dict["ctn_outnii"], "SHIELD"
        )
