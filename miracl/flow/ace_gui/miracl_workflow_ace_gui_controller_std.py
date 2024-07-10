from pandas.core.dtypes.common import conversion
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QCheckBox,
    QPushButton,
    QTabWidget,
    QMessageBox,
    QTextEdit,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from miracl.flow.ace_gui.miracl_workflow_ace_gui_tab_manager import TabManager
from miracl.flow.ace_gui.miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu
from miracl.flow import miracl_workflow_ace_parser
from miracl import miracl_logger
from miracl.flow.ace_gui.miracl_workflow_ace_gui_flag_creator import flag_creator
import subprocess, shlex
from pathlib import Path

logger = miracl_logger.logger


class CommandThread(QThread):
    error_signal = pyqtSignal(str)
    success_signal = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(result.stdout)  # This will go to the CLI
            self.success_signal.emit()
        except subprocess.CalledProcessError as e:
            self.error_signal.emit(e.stderr)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ACE flow")
        self.setGeometry(100, 100, 720, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.tab_manager = TabManager(self.tab_widget)

        show_tabs_checkbox = QCheckBox("Show tabs for all modules used by ACE")
        show_tabs_checkbox.stateChanged.connect(self.toggle_additional_tabs)
        main_layout.addWidget(show_tabs_checkbox)

        help_button = QPushButton("Help")
        main_layout.addWidget(help_button)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_ace_cli)
        main_layout.addWidget(run_button)

        self.error_output = QTextEdit()
        self.error_output.setReadOnly(True)
        main_layout.addWidget(self.error_output)

        # Hide additional tabs initially
        for tab in self.tab_manager.additional_tabs:
            tab_index = self.tab_widget.indexOf(tab)
            self.tab_widget.setTabVisible(tab_index, False)

    def toggle_additional_tabs(self, state):
        for tab in self.tab_manager.additional_tabs:
            tab_index = self.tab_widget.indexOf(tab)
            self.tab_widget.setTabVisible(tab_index, state == Qt.Checked)

    def run_ace_cli(self):
        """
        Run ACE by invoking it through the cli.

        This method retrieves various input values from the main tab and prints
        them to the console. It also checks the state of the "Single or multi
        method arguments" checkbox and prints the corresponding mode.
        """

        #########
        # FLAGS #
        #########

        # Main tab
        main_tab = self.tab_manager.main_tab
        method_checkbox = (
            self.tab_manager.main_tab.single_checkbox
        )  # Checks if single or multiple method is used
        main_tab_flags = flag_creator.create_main_tab_flags(main_tab, method_checkbox)

        # CLARITY-Allen registration
        clarity_registration_tab = self.tab_manager.clarity_registration_tab
        clarity_registration_tab_flags = flag_creator.create_clarity_registration_flags(
            clarity_registration_tab
        )

        # Conversion
        conversion_tab = self.tab_manager.conversion_tab
        conversion_tab_flags = flag_creator.create_conversion_flags(conversion_tab)

        # segmentation
        segmentation_tab = self.tab_manager.segmentation_tab
        segmentation_tab_flags = flag_creator.create_segmentation_flags(
            segmentation_tab
        )

        # Voxelizing/warping
        voxelizing_warping_tab = self.tab_manager.voxelizing_warping_tab
        voxelizing_warping_tab_flags = flag_creator.create_voxelization_warping_flags(
            voxelizing_warping_tab
        )

        # Clusterwise
        clusterwise_tab = self.tab_manager.clusterwise_tab
        clusterwise_tab_flags = flag_creator.create_clusterwise_flags(clusterwise_tab)

        # Correlation/stats
        correlation_stats_tab = self.tab_manager.correlation_stats_tab
        correlation_stats_tab_flags = flag_creator.create_correlation_stats_flags(
            correlation_stats_tab
        )

        # Heatmap
        heatmap_tab = self.tab_manager.heatmap_tab
        heatmap_tab_flags = flag_creator.create_heatmap_flags(heatmap_tab)

        # Run ACE
        ace_gui_controller_path = Path(__file__).resolve()
        ace_interface_dir = ace_gui_controller_path.parent.parent
        ace_interface_script_path = (
            ace_interface_dir / "miracl_workflow_ace_interface.py"
        )
        full_command = f"python {str(ace_interface_script_path)} {wu.craft_flags(main_tab_flags)} {wu.craft_flags(conversion_tab_flags)} {wu.craft_flags(segmentation_tab_flags)} {wu.craft_flags(clarity_registration_tab_flags)} {wu.craft_flags(voxelizing_warping_tab_flags)} {wu.craft_flags(clusterwise_tab_flags)} {wu.craft_flags(correlation_stats_tab_flags)} {wu.craft_flags(heatmap_tab_flags)}"

        self.thread = CommandThread(full_command)
        self.thread.error_signal.connect(self.display_error)
        self.thread.success_signal.connect(self.command_success)
        self.thread.start()

    def display_error(self, error_message):
        self.error_output.setText(error_message)

    def command_success(self):
        QMessageBox.information(self, "Success", "Command executed successfully!")
        self.close()


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
