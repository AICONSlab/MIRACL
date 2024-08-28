from PyQt5.QtWidgets import QTabWidget
from integration_tab1 import Tab1  # Import Tab1


class TabController:
    def __init__(self, parent):
        """Initialize the TabController with a parent widget."""
        self.tab_widget = QTabWidget(parent)
        self.create_tabs()

    def create_tabs(self):
        """Create and add tabs to the tab widget."""
        # Create instances of each tab
        tab1 = Tab1()

        # Add tabs to the tab widget
        self.tab_widget.addTab(tab1, "Tab 1")

    def get_widget(self):
        """Return the tab widget for use in the main application."""
        return self.tab_widget
