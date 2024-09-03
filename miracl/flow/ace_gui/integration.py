# Import PyQt reqs
from PyQt5.QtWidgets import (
    QApplication,
    QSizePolicy,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)

# Import type annotations
from typing import Dict

# Import observers/factories
from miracl_gui_widget_observer import WidgetObserver
from miracl_gui_tab_controller import TabController
from miracl_gui_widget_factory import SectionLabel
from miracl_gui_data_manager import DataManager

# Import objects
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_seg import SegVoxObjs as seg_vox
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen
from miracl.system.objs.objs_reg import RegWarpClarObjs as reg_warp_clar
from miracl.system.objs.objs_conv import ConvTiffNiiObjs as conv_tiff_nii

# Import logger
from miracl import miracl_logger

logger = miracl_logger.logger


class MainWindow(QMainWindow):
    """
    The main window of the application.

    This class represents the main window of the ACE flow application. It sets
    up the user interface, including the tab widget, checkbox, buttons, and
    event handlers.

    :ivar tab_controller: The controller managing the tabs in the application.
    :vartype tab_controller: TabController
    :ivar widget_dict: Dictionary of actual widget objects for interaction.
    :vartype widget_dict: Dict[str, QWidget]
    :ivar miracl_obj_dict: Dictionary of MiraclObj instances for default values.
    :vartype miracl_obj_dict: Dict[str, MiraclObj]
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

        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        widget_dict: Dict = {
            "Main": [
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

        self.main_layout.addWidget(self.tab_controller.get_widget())

        # Initialize the DataManager with existing widgets and obj_dict
        self.data_manager = DataManager(
            self.tab_controller.get_tab_obj_dicts(), self.tab_controller.get_obj_dict()
        )

        # Add IO buttons
        self.add_io_buttons()

        # Get the widget and MiraclObj dictionaries
        self.widget_dict = (
            self.tab_controller.get_tab_obj_dicts()
        )  # Actual widget objects
        self.miracl_obj_dict = self.tab_controller.get_obj_dict()  # MiraclObj instances

        # self.tab_obj_dicts = self.tab_controller.get_tab_obj_dicts()
        # self.tabs = self.tab_controller.get_tabs()
        # self.default_objs = self.tab_controller.get_obj_dict()

        # logger.debug("Contents of tab_obj_dicts:")
        # for name, widget in self.tab_obj_dicts.items():
        #     logger.debug(f"Widget: {name}, Type: {type(widget)}")

        # Set up change detection
        # WidgetObserver.setup_change_detection(self.tab_obj_dicts, self.on_value_changed)
        WidgetObserver.setup_change_detection(self.widget_dict, self.on_value_changed)

        # Access the obj_dicts for each tab
        # print(self.tab_obj_dicts[flow_ace.single.name].cli_l_flag)
        print(f"SINGLE: {self.miracl_obj_dict[flow_ace.single.name].cli_l_flag}")
        # print(self.tab_controller)
        print(f"SELF.MIRACL_OBJ_DICT: {self.miracl_obj_dict}")
        print()
        print()
        print()
        print()
        print()
        print(f"SELF.WIDGET_DICT: {self.widget_dict}")
        print()
        print()
        print()
        print()
        print()
        print(self.tab_controller)

    def add_io_buttons(self):
        """Add IO buttons to the layout."""
        io_widget = QWidget()
        io_layout = QHBoxLayout(io_widget)  # Layout for IO buttons (horizontal)

        # Create Load, Save, and Reset buttons
        io_load_button = QPushButton("Load")
        io_layout.addWidget(io_load_button)
        io_save_button = QPushButton("Save")
        io_layout.addWidget(io_save_button)
        io_reset_button = QPushButton("Reset")
        io_layout.addWidget(io_reset_button)

        # Set margins for the IO buttons
        io_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(io_widget)  # Add IO buttons to the main layout

        # Connect button signals to slots
        io_load_button.clicked.connect(
            self.data_manager.load_values
        )  # Connect to DataManager's load method
        io_save_button.clicked.connect(
            lambda: self.data_manager.save_values(
                "Save File",
                "",
                "MIRACL ACE Flow Files (*.aceflow)",
            )
        )  # Connect to DataManager's save method
        io_reset_button.clicked.connect(
            self.data_manager.confirm_reset
        )  # Connect to DataManager's confirm reset method

        # NEW: Add Help button
        help_button = QPushButton("Help")
        help_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )  # Ensure full width
        self.main_layout.addWidget(help_button)  # Add Help button to the main layout

        # NEW: Connect Help button to print statement
        help_button.clicked.connect(
            lambda: print("Help button pressed")
        )  # Prints to terminal

        # NEW: Add Run button
        run_button = QPushButton("Run")
        run_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )  # Ensure full width
        self.main_layout.addWidget(run_button)  # Add Run button to the main layout

        # NEW: Connect Run button to print statement
        run_button.clicked.connect(
            lambda: print("Run button pressed")
        )  # Prints to terminal

    # def add_io_buttons(self):
    #     """Add IO buttons to the layout."""
    #     io_widget = QWidget()
    #     io_layout = QHBoxLayout(io_widget)
    #     io_load_button = QPushButton("Load")
    #     io_layout.addWidget(io_load_button)
    #     io_save_button = QPushButton("Save")
    #     io_layout.addWidget(io_save_button)
    #     io_reset_button = QPushButton("Reset")
    #     io_layout.addWidget(io_reset_button)
    #     io_layout.setContentsMargins(0, 0, 0, 0)
    #     self.centralWidget().layout().addWidget(
    #         io_widget
    #     )  # Add IO buttons to the main layout
    #
    #     # Connect button signals to slots
    #     io_load_button.clicked.connect(self.data_manager.load_values)
    #     io_save_button.clicked.connect(
    #         lambda: self.data_manager.save_values(
    #             "Save File",
    #             "",
    #             "MIRACL ACE Flow Files (*.aceflow)",
    #         )
    #     )
    #     io_reset_button.clicked.connect(self.data_manager.confirm_reset)
    #
    #     # NEW: Add Help button
    #     help_button = QPushButton("Help")
    #     help_button.setSizePolicy(
    #         QSizePolicy.Expanding, QSizePolicy.Fixed
    #     )  # Ensure full width
    #     io_layout.addWidget(help_button)  # Add Help button to the same layout
    #
    #     # NEW: Connect Help button to print statement
    #     help_button.clicked.connect(
    #         lambda: print("Help button pressed")
    #     )  # Prints to terminal
    #
    #     # NEW: Add Run button
    #     run_button = QPushButton("Run")
    #     run_button.setSizePolicy(
    #         QSizePolicy.Expanding, QSizePolicy.Fixed
    #     )  # Ensure full width
    #     io_layout.addWidget(run_button)  # Add Run button to the same layout
    #
    #     # NEW: Connect Run button to print statement
    #     run_button.clicked.connect(
    #         lambda: print("Run button pressed")
    #     )  # Prints to terminal

    def on_value_changed(self, name, value):
        """
        Handle widget value changes.

        This method is called whenever a widget's value changes, allowing
        for dynamic updates and logging.

        :param name: The name of the widget that changed.
        :type name: str
        :param value: The new value of the widget.
        :type value: any
        """
        logger.debug(f"Value changed in {name}: {value}")


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
