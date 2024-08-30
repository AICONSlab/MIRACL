from miracl import miracl_logger
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)
from typing import Dict
from miracl_gui_tab_controller import TabController
from miracl_gui_widget_factory import SectionLabel
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_seg import SegVoxObjs as seg_vox
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen
from miracl.system.objs.objs_reg import RegWarpClarObjs as reg_warp_clar
from miracl.system.objs.objs_conv import ConvTiffNiiObjs as conv_tiff_nii

logger = miracl_logger.logger


class MainWindow(QMainWindow):
    """
    The main window of the application.

    This class represents the main window of the ACE flow application. It sets
    up the user interface, including the tab widget, checkbox, buttons, and
    event handlers.

    Attributes:
        tab_widget (QTabWidget): The tab widget that holds the different tabs.
        tab_manager (TabManager): The manager for the tabs in the application.
        show_tabs_checkbox (QCheckBox): The checkbox to show or hide
        additional tabs.
    """

    def __init__(self):
        """
        Initialize the MainWindow.

        This method sets up the main window, including the central widget,
        main layout, tab widget, and various UI elements.
        """
        self.window_title = "ACE flow"

        super().__init__()

        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        widget_dict: Dict = {
            "main": [
                SectionLabel("Single or multi method arguments"),
                flow_ace.single,
                SectionLabel("Required arguments"),
                seg_ace.out_dir,
                seg_ace.model_type,
                SectionLabel("Useful/important arguments"),
                seg_ace.gpu_index,
                conv_tiff_nii.down,
                reg_clar_allen.voxel_size,
                seg_vox.downsample,
                # reg_warp_clar.voxel_size,
            ],
            "Conversion": [
                SectionLabel("Test label"),
                reg_warp_clar.voxel_size,
            ],
        }

        # Initialize the TabController and get the tab widget
        self.tab_controller = TabController(self, widget_dict)

        main_layout.addWidget(self.tab_controller.get_widget())
        self.tab_obj_dicts = self.tab_controller.get_tab_obj_dicts()
        self.tabs = self.tab_controller.get_tabs()

        # Access the obj_dicts for each tab
        print(self.tab_obj_dicts[flow_ace.single.name].cli_l_flag)
        print(self.tab_controller)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
