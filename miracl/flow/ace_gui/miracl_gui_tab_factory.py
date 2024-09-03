from __future__ import annotations
from typing import List
from pydantic import BaseModel
from PyQt5.QtWidgets import QWidget, QFormLayout
from miracl_gui_widget_factory import WidgetFactory


class TabBuilder:
    @staticmethod
    def base_tab(tab_title: str, obj_list: List[BaseModel]) -> tuple[QWidget, dict]:
        """Create and return an instance of a QWidget configured as a tab.

        This method creates a new tab widget and populates it with widgets created from the provided
        list of Pydantic objects. It returns the tab widget and a dictionary containing references
        to the created widgets.

        :param tab_title: The name to assign to the tab.
        :type tab_title: str
        :param obj_list: A list of Pydantic BaseModel instances used to create the widgets for the tab.
        :type obj_list: List[BaseModel]
        :return: A tuple containing the QWidget instance and a dictionary of created widget references.
        :rtype: tuple[QWidget, Dict[str, Any]]
        """
        base_tab = QWidget()
        base_tab._name = tab_title
        layout = QFormLayout()

        section, obj_dict = WidgetFactory.create_widgets_from_objects(
            obj_list,
            base_tab,
        )

        layout.addRow(section)

        base_tab.setLayout(layout)
        return base_tab, obj_dict
