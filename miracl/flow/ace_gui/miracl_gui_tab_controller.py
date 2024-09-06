# Import PyQt reqs
from PyQt5.QtWidgets import (
    QTabWidget,
    QWidget,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
)

# Import type annotations
from typing import Dict, List

# Import factory
from miracl_gui_tab_factory import TabBuilder

# Import Pydantic datamodel
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

# Import logger
from miracl import miracl_logger

logger = miracl_logger.logger


class TabController:
    """
    Controller for managing tabs in a QTabWidget.

    This class initializes a QTabWidget and populates it with tabs
    based on a predefined widget dictionary. It allows for the
    retrieval of the tab widget, the associated widget objects, and
    the MiraclObj instances for each tab.

    :param parent: The parent widget for the QTabWidget.
    :type parent: QWidget
    :param widget_dict: A dictionary mapping tab titles to their associated objects.
    :type widget_dict: Dict[str, List]

    :ivar _miracl_obj_dict: Dictionary to store MiraclObj instances for each tab.
    :vartype _miracl_obj_dict: Dict[str, MiraclObj]
    :ivar _widget_dict: Dictionary to store the actual widget objects.
    :vartype _widget_dict: Dict[str, QWidget]
    :ivar _tabs: List to store tab objects.
    :vartype _tabs: List
    :ivar initial_widget_dict: Dictionary passed to the tab builder.
    :vartype initial_widget_dict: Dict
    """

    def __init__(self, parent: QWidget, widget_dict: Dict) -> None:
        """Initialize the TabController."""
        self.tab_widget: QTabWidget = QTabWidget(parent)
        self._miracl_obj_dict: Dict[str, MiraclObj] = (
            {}
        )  # Dict to store MiraclObj instances
        self._widget_dict: Dict[str, QWidget] = (
            {}
        )  # Dict to store actual widget objects
        self._tabs: List = []  # List to store tab objects
        self.initial_widget_dict: Dict = widget_dict  # Dict to pass to tab builder

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
        for tab_title, tab_obj_list in self.initial_widget_dict.items():
            logger.debug(f"Processing tab: {tab_title}")
            try:
                tab_builder = getattr(TabBuilder, which_tab)
                logger.debug(f"Using tab builder method: {which_tab}")
            except AttributeError:
                error_message = f"Method '{which_tab}' does not exist in TabBuilder."
                logger.error(error_message)
                raise ValueError(error_message)

            tmp_title, tmp_obj_dict = tab_builder(tab_title, tab_obj_list)
            self.tab_widget.addTab(tmp_title, tmp_title._name)

            # Update the MiraclObj dictionary
            self._miracl_obj_dict.update(tmp_obj_dict)

            # Populate the widget dictionary with actual widget objects
            self._populate_widget_dict(tmp_title)

            self._tabs.append(tmp_title)
            logger.info("Added tab: %s", tmp_title)

    # def _populate_widget_dict(self, tab: QWidget):
    #     """Populate the widget dictionary with actual widget objects from the given tab.
    #
    #     This method searches for all relevant child widgets in the specified tab
    #     and adds them to the _widget_dict for later access.
    #
    #     :param tab: The tab widget from which to find child widgets.
    #     :type tab: QWidget
    #     :return: None
    #     """
    #     for child in tab.findChildren((QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit)):
    #         if child.objectName():
    #             self._widget_dict[child.objectName()] = child

    # def _populate_widget_dict(self, tab: QWidget):
    #     """Populate the widget dictionary with actual widget objects from the given tab."""
    #     # Find all relevant child widgets in the specified tab
    #     for child in tab.findChildren(
    #         (QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QWidget)
    #     ):
    #         if hasattr(
    #             child, "inputs"
    #         ):  # Check if it's a container with QLineEdit inputs
    #             if child.objectName():  # Ensure it has an object name
    #                 self._widget_dict[child.objectName()] = (
    #                     child  # Store the container widget
    #                 )
    #         elif isinstance(child, (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
    #             if child.objectName():  # Ensure it has an object name
    #                 self._widget_dict[child.objectName()] = (
    #                     child  # Store the individual widget
    #                 )

    def _populate_widget_dict(self, tab: QWidget):
        """Populate the widget dictionary with actual widget objects from the given tab."""
        # Find all relevant child widgets in the specified tab
        for child in tab.findChildren(
            (QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QWidget)
        ):
            # Check if it's a container with QLineEdit inputs
            if hasattr(child, "inputs"):
                if child.objectName():  # Ensure it has an object name
                    self._widget_dict[child.objectName()] = (
                        child  # Store the container widget
                    )
            elif isinstance(child, (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)):
                if child.objectName():  # Ensure it has an object name
                    # Exclude specific widgets by their object name
                    if (
                        child.objectName() != "qt_spinbox_lineedit"
                    ):  # Add more conditions as needed
                        self._widget_dict[child.objectName()] = (
                            child  # Store the individual widget
                        )

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self.widget_dict."""
    #     current_values = {}
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             current_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             current_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             current_values[name] = [
    #                 input_field.text() for input_field in widget.inputs
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     return current_values

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self._widget_dict."""
    #     current_values = {}
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             current_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             current_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             current_values[name] = [
    #                 input_field.text() for input_field in widget.inputs
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     # Validate the collected values against the expected types in MiraclObj
    #     for name, value in current_values.items():
    #         miracl_obj = self._miracl_obj_dict.get(name)
    #         if miracl_obj:
    #             expected_type = miracl_obj.cli_obj_type
    #             if expected_type:
    #                 # Check if the value matches the expected type
    #                 if not isinstance(value, expected_type.python_type):
    #                     raise TypeError(
    #                         f"Value for '{name}' is of type {type(value).__name__}, "
    #                         f"expected type {expected_type.python_type.__name__}."
    #                     )
    #
    #     return current_values

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self._widget_dict."""
    #     current_values = {}
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             current_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             current_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             current_values[name] = [
    #                 input_field.text() for input_field in widget.inputs
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     # Validate and convert types based on MiraclObj
    #     for name, value in current_values.items():
    #         miracl_obj = self._miracl_obj_dict.get(name)
    #         if miracl_obj:
    #             expected_type = miracl_obj.cli_obj_type.python_type
    #             # Convert values to the expected type
    #             if expected_type is int:
    #                 current_values[name] = int(value)
    #             elif expected_type is float:
    #                 current_values[name] = float(value)
    #             elif expected_type is str:
    #                 current_values[name] = str(value)
    #             else:
    #                 raise TypeError(
    #                     f"Value for '{name}' is of type {type(value).__name__}, "
    #                     f"expected type {expected_type.__name__}."
    #                 )
    #
    #     return current_values

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self._widget_dict."""
    #     current_values = {}
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             current_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             current_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             current_values[name] = [
    #                 input_field.text() for input_field in widget.inputs
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     # Validate and convert types based on MiraclObj
    #     for name, value in current_values.items():
    #         miracl_obj = self._miracl_obj_dict.get(name)
    #         if miracl_obj:
    #             expected_type = miracl_obj.cli_obj_type.python_type
    #
    #             # Handle conversion for expected types
    #             if expected_type is int:
    #                 # If the value is a list, check each element
    #                 if isinstance(value, list):
    #                     current_values[name] = [
    #                         int(item) for item in value
    #                     ]  # Convert each item to int
    #                 else:
    #                     # Convert single value to int
    #                     try:
    #                         current_values[name] = int(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to int, got '{value}'."
    #                         )
    #
    #             elif expected_type is float:
    #                 if isinstance(value, list):
    #                     current_values[name] = [
    #                         float(item) for item in value
    #                     ]  # Convert each item to float
    #                 else:
    #                     try:
    #                         current_values[name] = float(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to float, got '{value}'."
    #                         )
    #
    #             elif expected_type is str:
    #                 # No conversion needed for strings
    #                 current_values[name] = str(value)
    #
    #             else:
    #                 raise TypeError(
    #                     f"Value for '{name}' is of type {type(value).__name__}, "
    #                     f"expected type {expected_type.__name__}."
    #                 )
    #
    #     return current_values

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self._widget_dict."""
    #     current_values = {}
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             current_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             current_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             current_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             current_values[name] = [
    #                 input_field.text() for input_field in widget.inputs
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     # Validate and convert types based on MiraclObj
    #     for name, value in current_values.items():
    #         miracl_obj = self._miracl_obj_dict.get(name)
    #         if miracl_obj:
    #             expected_type = miracl_obj.cli_obj_type.python_type
    #
    #             # Handle conversion for expected types
    #             if expected_type is int:
    #                 # If the value is a list, check each element
    #                 if isinstance(value, list):
    #                     current_values[name] = [
    #                         int(item) for item in value
    #                     ]  # Convert each item to int
    #                 else:
    #                     # Convert single value to int
    #                     try:
    #                         current_values[name] = int(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to int, got '{value}'."
    #                         )
    #
    #             elif expected_type is float:
    #                 if isinstance(value, list):
    #                     current_values[name] = [
    #                         float(item) for item in value
    #                     ]  # Convert each item to float
    #                 else:
    #                     try:
    #                         current_values[name] = float(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to float, got '{value}'."
    #                         )
    #
    #             elif expected_type is str:
    #                 # No conversion needed for strings
    #                 current_values[name] = str(value)
    #
    #             else:
    #                 raise TypeError(
    #                     f"Value for '{name}' is of type {type(value).__name__}, "
    #                     f"expected type {expected_type.__name__}."
    #                 )
    #
    #     return current_values

    # def get_current_widget_values(self):
    #     """Retrieve current values from the widgets in self._widget_dict."""
    #     widget_dict_values = {}  # Use the correct name for the dictionary
    #
    #     for name, widget in self._widget_dict.items():
    #         if isinstance(widget, QLineEdit):
    #             widget_dict_values[name] = widget.text()
    #         elif isinstance(widget, QSpinBox):
    #             widget_dict_values[name] = widget.value()
    #         elif isinstance(widget, QDoubleSpinBox):
    #             widget_dict_values[name] = widget.value()
    #         elif isinstance(widget, QComboBox):
    #             widget_dict_values[name] = widget.currentText()
    #         elif hasattr(widget, "inputs"):  # Check for container widget
    #             # Collect values from all QLineEdit inputs in the container
    #             widget_dict_values[name] = [
    #                 int(input_field.text())
    #                 for input_field in widget.inputs
    #                 if input_field.text().isdigit()
    #             ]
    #         else:
    #             raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")
    #
    #     # Validate and convert types based on MiraclObj
    #     for name, value in widget_dict_values.items():
    #         miracl_obj = self._miracl_obj_dict.get(name)
    #         if miracl_obj:
    #             expected_type = miracl_obj.cli_obj_type.python_type
    #
    #             # Handle conversion for expected types
    #             if expected_type is int:
    #                 if isinstance(value, list):
    #                     widget_dict_values[name] = [int(item) for item in value]
    #                 else:
    #                     try:
    #                         widget_dict_values[name] = int(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to int, got '{value}'."
    #                         )
    #
    #             elif expected_type is float:
    #                 if isinstance(value, list):
    #                     widget_dict_values[name] = [float(item) for item in value]
    #                 else:
    #                     try:
    #                         widget_dict_values[name] = float(value)
    #                     except ValueError:
    #                         raise TypeError(
    #                             f"Value for '{name}' must be convertible to float, got '{value}'."
    #                         )
    #
    #             elif expected_type is str:
    #                 widget_dict_values[name] = str(value)
    #
    #             else:
    #                 raise TypeError(
    #                     f"Value for '{name}' is of type {type(value).__name__}, "
    #                     f"expected type {expected_type.__name__}."
    #                 )
    #
    #     return widget_dict_values  # Return the correctly named dictionary

    def get_current_widget_values(self):
        """Retrieve current values from the widgets in self._widget_dict."""
        widget_dict_values = {}  # Correctly name the dictionary

        for name, widget in self._widget_dict.items():
            if isinstance(widget, QLineEdit):
                widget_dict_values[name] = widget.text()
            elif isinstance(widget, QSpinBox):
                widget_dict_values[name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                widget_dict_values[name] = widget.value()
            elif isinstance(widget, QComboBox):
                widget_dict_values[name] = widget.currentText()
            elif hasattr(widget, "inputs"):  # Check for container widget
                # Collect values from all QLineEdit inputs in the container
                widget_dict_values[name] = [
                    int(input_field.text())
                    for input_field in widget.inputs
                    if input_field.text().isdigit()
                ]
            else:
                raise TypeError(f"Unsupported widget type for {name}: {type(widget)}")

        # Validate and convert types based on MiraclObj
        for name, value in widget_dict_values.items():
            miracl_obj = self._miracl_obj_dict.get(name)
            if miracl_obj:
                expected_type = miracl_obj.cli_obj_type.python_type

                # Handle conversion for expected types
                if expected_type is int:
                    if isinstance(value, list):
                        widget_dict_values[name] = [int(item) for item in value]
                    else:
                        try:
                            widget_dict_values[name] = int(value)
                        except ValueError:
                            raise TypeError(
                                f"Value for '{name}' must be convertible to int, got '{value}'."
                            )

                elif expected_type is float:
                    if isinstance(value, list):
                        widget_dict_values[name] = [float(item) for item in value]
                    else:
                        try:
                            widget_dict_values[name] = float(value)
                        except ValueError:
                            raise TypeError(
                                f"Value for '{name}' must be convertible to float, got '{value}'."
                            )

                elif expected_type is str:
                    widget_dict_values[name] = str(value)

                else:
                    raise TypeError(
                        f"Value for '{name}' is of type {type(value).__name__}, "
                        f"expected type {expected_type.__name__}."
                    )

        # Log the dictionary with the correct name
        logger.debug(f"widget_dict_values: {widget_dict_values}")

        return widget_dict_values  # Return the correctly named dictionary

    def get_widget(self) -> QTabWidget:
        """Return the tab widget for use in the main application.

        This method provides access to the QTabWidget instance that contains
        all the tabs created by this TabController.

        :return: The tab widget containing all the tabs.
        :rtype: QTabWidget
        """
        return self.tab_widget

    def get_tab_obj_dicts(self) -> Dict[str, QWidget]:
        """Return the actual widget objects for each tab.

        This method provides access to the dictionary containing the actual
        widget instances created for each tab.

        :return: A dictionary containing the actual widget objects.
        :rtype: Dict[str, QWidget]
        """
        return self._widget_dict

    def get_tabs(self) -> List:
        """Return a list of all tab objects.

        This method provides access to the list of tab objects created
        in the QTabWidget.

        :return: A list of all tab objects.
        :rtype: List
        """
        return self._tabs

    def get_obj_dict(self) -> Dict[str, MiraclObj]:
        """Return the dictionary of MiraclObj instances.

        This method provides access to the dictionary containing all MiraclObj
        instances used to create the widgets.

        :return: A dictionary of MiraclObj instances.
        :rtype: Dict[str, MiraclObj]
        """
        return self._miracl_obj_dict

    def __str__(self) -> str:
        """Return a string representation of the TabController.

        This method returns a string that includes the current state of the
        tab_widget, including the number of tabs and their titles, as well as
        the _miracl_obj_dict and the list of tab objects.

        :return: A formatted string representing the TabController's state,
                 including tab count, tab titles, tab object dictionaries,
                 and the list of tab objects.
        :rtype: str
        """
        tab_count: int = self.tab_widget.count()
        tab_titles: List[str] = [self.tab_widget.tabText(i) for i in range(tab_count)]
        tab_widget_info: str = (
            f"Tab Widget: {tab_count} tabs - Titles: {', '.join(tab_titles)}"
        )

        miracl_obj_dict_info: str = f"MiraclObj Dict: {self._miracl_obj_dict}"

        tabs_info: str = f"Tabs: {', '.join(str(tab) for tab in self._tabs)}"

        return f"{tab_widget_info}\n{miracl_obj_dict_info}\n{tabs_info}"
