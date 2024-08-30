from PyQt5.QtWidgets import QWidget, QFormLayout
from gui_factory import WidgetFactory


class TabBuilder:
    @staticmethod
    def base_tab(name, obj_list):
        """Create and return an instance of BaseTab."""
        base_tab = QWidget()
        base_tab.name = name
        layout = QFormLayout()  # Use QFormLayout for better label alignment

        # Create widgets using WidgetFactory
        section, obj_dict = WidgetFactory.create_widgets_from_objects(
            obj_list,
            base_tab,
        )

        # Add the section to the layout
        layout.addRow(section)  # Add the section to the form layout

        base_tab.setLayout(layout)  # Set the layout for this tab
        return base_tab, obj_dict
