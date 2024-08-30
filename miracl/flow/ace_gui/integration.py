from miracl import miracl_logger
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
)

from integration_tab_controller import TabController
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace

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

        # Initialize the TabController and get the tab widget
        self.tab_controller = TabController(self)
        main_layout.addWidget(self.tab_controller.get_widget())

        self.tab_obj_dicts = self.tab_controller.get_tab_obj_dicts()

        # Access the obj_dicts for each tab
        print(self.tab_obj_dicts[flow_ace.single.name].cli_l_flag)


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
