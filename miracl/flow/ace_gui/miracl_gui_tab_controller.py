from miracl import miracl_logger
from PyQt5.QtWidgets import QTabWidget, QWidget
from typing import Dict, List
from miracl_gui_tab_factory import TabBuilder

logger = miracl_logger.logger


class TabController:
    """Controller for managing tabs in a QTabWidget.

    This class initializes a QTabWidget and populates it with tabs
    based on a predefined widget dictionary. It allows for the
    retrieval of the tab widget and the associated objects for each tab.
    """

    def __init__(self, parent: QWidget, widget_dict: Dict) -> None:
        """Initialize the TabController with a parent widget and a widget dictionary.

        This method sets up the tab controller, initializing the QTabWidget
        and storing the provided widget dictionary for later use.

        :param parent: The parent widget for the QTabWidget.
        :type parent: QWidget
        :param widget_dict: A dictionary mapping tab titles to their associated objects.
        :type widget_dict: Dict[str, List]
        """
        self.tab_widget: QTabWidget = QTabWidget(parent)
        self._tab_obj_dicts: Dict = {}  # Dict to store the widget objects
        self._tabs: List = []  # List to store tab objects
        self.widget_dict: Dict = widget_dict  # Dict to pass to tab builder

        self.create_tabs()

    def create_tabs(self, which_tab: str = "base_tab") -> None:
        """Create tabs based on the widget_dict using the specified method from TabBuilder.

        This method iterates over the widget_dict and creates tabs in the QTabWidget.
        Each tab is associated with its corresponding objects and stored for later access.
        The method to create tabs can be specified using the `which_tab` argument,
        which defaults to "base_tab" if not provided.

        :param which_tab: The name of the method to call from TabBuilder. Defaults to "base_tab".
        :type which_tab: str
        :return: None
        """
        for tab_title, tab_obj_list in self.widget_dict.items():
            logger.debug(f"Processing tab: {tab_title}")
            try:
                tab_builder = getattr(TabBuilder, which_tab)
                logger.debug(f"Using tab builder method: {which_tab}")
            except AttributeError:
                error_message = f"Method '{which_tab}' does not exist in TabBuilder."
                logger.error(error_message)
                raise ValueError(error_message)

            tmp_title, tmp_obj_dict = tab_builder(
                tab_title,
                tab_obj_list,
            )
            self.tab_widget.addTab(tmp_title, tmp_title._name)
            self._tab_obj_dicts.update(tmp_obj_dict)
            self._tabs.append(tmp_title)
            logger.info("Added tab: %s", tmp_title)

    # @property
    # def tabs(self) -> List:
    #     """Get the list of tab objects."""
    #     return self._tabs
    #
    # def add_tab(self, tab_title: str, tab_obj_list: List) -> None:
    #     """Add a new tab to the controller.
    #
    #     Args:
    #         tab_title (str): The title of the tab to add.
    #         tab_obj_list (List): The list of objects associated with the tab.
    #
    #     Raises:
    #         ValueError: If the tab already exists.
    #     """
    #     if tab_title in self._tabs:
    #         raise ValueError("Tab already exists.")
    #
    #     # Create the tab using the same logic as in create_tabs
    #     tab_builder = TabBuilder.base_tab  # Assuming base_tab is the method to use
    #     tmp_title, tmp_obj_dict = tab_builder(tab_title, tab_obj_list)
    #     self.tab_widget.addTab(tmp_title, tmp_title.name)
    #     self._tab_obj_dicts.update(tmp_obj_dict)
    #     self._tabs.append(tmp_title)
    #
    # def remove_tab(self, tab_title: str) -> None:
    #     """Remove a tab from the controller.
    #
    #     Args:
    #         tab_title (str): The title of the tab to remove.
    #
    #     Raises:
    #         ValueError: If the tab is not found.
    #     """
    #     if tab_title in self._tabs:
    #         self._tabs.remove(tab_title)
    #         index = self.tab_widget.indexOf(tab_title)
    #         if index != -1:
    #             self.tab_widget.removeTab(index)
    #     else:
    #         raise ValueError("Tab not found.")

    def __str__(self) -> str:
        """Return a string representation of the TabController.

        This method returns a string that includes the current state of the
        tab_widget, including the number of tabs and their titles, as well as
        the _tab_obj_dicts and the list of tab objects.

        :return: A formatted string representing the TabController's state,
                 including tab count, tab titles, tab object dictionaries,
                 and the list of tab objects.
        :rtype: str
        """
        tab_count = self.tab_widget.count()
        tab_titles = [self.tab_widget.tabText(i) for i in range(tab_count)]
        tab_widget_info = (
            f"Tab Widget: {tab_count} tabs - Titles: {', '.join(tab_titles)}"
        )

        tab_obj_dicts_info = f"Tab Object Dicts: {self._tab_obj_dicts}"

        tabs_info = f"Tabs: {', '.join(str(tab) for tab in self._tabs)}"

        return f"{tab_widget_info}\n{tab_obj_dicts_info}\n{tabs_info}"

    def get_widget(self) -> QTabWidget:
        """Return the tab widget for use in the main application.

        This method provides access to the QTabWidget instance that contains
        all the tabs created by this TabController.

        :return: The tab widget containing all the tabs.
        :rtype: QTabWidget
        """
        return self.tab_widget

    def get_tab_obj_dicts(self) -> Dict:
        """Return the obj_dicts for each tab.

        This method returns a dictionary containing the objects associated with
        each tab, allowing for easy access to the widget references.

        :return: A dictionary containing the objects associated with each tab.
        :rtype: Dict
        """
        return self._tab_obj_dicts

    def get_tabs(self) -> List:
        """Return a list of all tab objects.

        This method provides access to the list of tab objects created
        in the QTabWidget.

        :return: A list of all tab objects.
        :rtype: List
        """
        return self._tabs
