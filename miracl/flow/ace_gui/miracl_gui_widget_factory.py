from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtGui import QRegularExpressionValidator
from PyQt5.QtCore import QRegularExpression

from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    WidgetType,
    InputRestrictionType,
)
from typing import List, Union, Dict, Any, Tuple
from enum import Enum

# Import logger
from miracl import miracl_logger

# Initialize logger
logger = miracl_logger.logger


class SectionLabel:
    """Class to represent a section label."""

    def __init__(self, text: str):
        self.text = text


class LabelFactory:
    """Factory class for creating labels."""

    @staticmethod
    def create_section_label(text: str) -> QLabel:
        """Create a bold section label."""
        label = QLabel(f"<b>{text}</b>")
        return label

    @staticmethod
    def create_indented_label(obj: MiraclObj) -> QLabel:
        """Create an indented label with a tooltip."""

        if not obj.gui_label or not obj.gui_label[0]:
            raise ValueError(f"'gui_label' attribute missing from obj: {obj}")
        gui_label = obj.gui_label[0]
        help_text = obj.cli_help
        placeholders = {
            "%(default)s": "obj_default",
            "%(type)s": "cli_obj_type",
        }
        for placeholder, attribute in placeholders.items():
            if placeholder in help_text and hasattr(obj, attribute):
                value = getattr(obj, attribute)
                if isinstance(value, (int, float)):
                    value = str(value)
                elif isinstance(value, Enum):
                    value = value.value
                help_text = help_text.replace(placeholder, value)

        if not gui_label.endswith(":"):
            gui_label += ":"
        label = QLabel("  " + gui_label)
        label.setToolTip(help_text)
        return label


class WidgetFactory:
    """Factory class for creating widgets based on MiraclObj instances."""

    @staticmethod
    def create_widgets_from_objects(
        objs: List[Union[MiraclObj, SectionLabel]], parent: QWidget
    ) -> Tuple[QWidget, Dict[str, MiraclObj]]:
        """Create a QWidget containing form elements from a list of MiraclObj and SectionLabel.

        Returns a tuple containing the QWidget and a dictionary of MiraclObj instances.
        """
        container_widget: QWidget = QWidget(parent)  # Ensure the parent is set
        layout: QFormLayout = QFormLayout(container_widget)

        obj_dict: Dict[str, MiraclObj] = {}

        for obj in objs:
            if isinstance(obj, SectionLabel):
                label = LabelFactory.create_section_label(obj.text)
                layout.addRow(label)
            elif isinstance(obj, MiraclObj):
                label: QLabel = LabelFactory.create_indented_label(obj)

                # Store the MiraclObj instance in the dictionary using its name as the key
                obj_dict[obj.name] = obj

                widget = None
                if obj.gui_widget_type == WidgetType.DROPDOWN:
                    widget = WidgetFactory.create_dropdown(obj, parent)
                    widget.setObjectName(obj.name)
                    layout.addRow(label, widget)
                elif obj.gui_widget_type == WidgetType.LINE_EDIT:
                    widget = WidgetFactory.create_line_edit(obj, parent)
                    widget.setObjectName(obj.name)
                    layout.addRow(label, widget)
                elif obj.gui_widget_type == WidgetType.SPINBOX:
                    widget = WidgetFactory.create_spinbox(obj, parent)
                    widget.setObjectName(obj.name)
                    layout.addRow(label, widget)
                elif obj.gui_widget_type == WidgetType.DOUBLE_SPINBOX:
                    widget = WidgetFactory.create_double_spinbox(obj, parent)
                    widget.setObjectName(obj.name)
                    layout.addRow(label, widget)
                elif obj.gui_widget_type == WidgetType.PATH_INPUT:
                    # Update to unpack the returned values from create_path_input_widget
                    path_widget, path_input = WidgetFactory.create_path_input_widget(
                        obj, parent
                    )
                    path_input.setObjectName(obj.name)
                    layout.addRow(label, path_widget)

        return container_widget, obj_dict

    @staticmethod
    def setup_widget(widget: QWidget, obj: MiraclObj) -> None:
        """Set up common properties for widgets.

        :param widget: The widget to set up (QComboBox, QSpinBox and path selection).
        :param obj: The MiraclObj containing data for the widget.
        """
        if hasattr(obj, "flow") and obj.flow is not None:
            widget.setObjectName(obj.flow["ace"]["cli_l_flag"])
        else:
            widget.setObjectName(obj.cli_l_flag)

    @staticmethod
    def create_dropdown(obj: MiraclObj, parent: QWidget) -> QComboBox:
        """Create a dropdown (combo box) widget from a MiraclObj."""
        if obj.cli_choices:
            string_choices = [str(choice) for choice in obj.cli_choices]
        else:
            raise ValueError("Missing list of choices in {obj.name}")
        dropdown: QComboBox = QComboBox(parent)
        dropdown.addItems(string_choices)
        dropdown.setCurrentText(str(obj.obj_default))
        WidgetFactory.setup_widget(dropdown, obj)

        return dropdown

    @staticmethod
    def create_line_edit(obj: MiraclObj, parent: QWidget) -> QLineEdit:
        """Create a line edit widget from a MiraclObj."""
        line_edit: QLineEdit = QLineEdit(parent)

        # Set placeholder text and default value
        if obj.obj_default is not None:
            placeholder_text = str(obj.obj_default)
            line_edit.setText(placeholder_text)
        else:
            placeholder_text = "None"

        line_edit.setPlaceholderText(placeholder_text)

        WidgetFactory.setup_widget(line_edit, obj)

        # Set maximum length if available
        if hasattr(obj, "max_length"):
            line_edit.setMaxLength(obj.max_length)

        # Set validator if input_restrictions are specified
        if obj.line_edit_settings and obj.line_edit_settings.input_restrictions:
            validator = WidgetFactory.create_line_edit_validator(
                obj.line_edit_settings.input_restrictions
            )
            line_edit.setValidator(validator)

        return line_edit

    @staticmethod
    def create_line_edit_validator(
        restriction_type: InputRestrictionType,
    ) -> QRegularExpressionValidator:
        if restriction_type == InputRestrictionType.STR:
            regex = QRegularExpression("^[A-Za-z]+$")
        elif restriction_type == InputRestrictionType.STRCON:
            regex = QRegularExpression("^[A-Za-z0-9_-]+$")
        else:  # default to alphanumeric
            regex = QRegularExpression("^[A-Za-z0-9]+$")
        return QRegularExpressionValidator(regex)

    @staticmethod
    def create_spinbox(obj: MiraclObj, parent: QWidget) -> QSpinBox:
        """Create a standard spinbox widget from a MiraclObj."""
        spinbox: QSpinBox = QSpinBox(parent)
        spinbox.setValue(obj.obj_default)
        WidgetFactory.setup_widget(spinbox, obj)
        WidgetFactory.set_spinbox_ranges(spinbox, obj)

        return spinbox

    @staticmethod
    def create_double_spinbox(obj: MiraclObj, parent: QWidget) -> QDoubleSpinBox:
        """Create a double spinbox widget from a MiraclObj."""
        double_spinbox: QDoubleSpinBox = QDoubleSpinBox(parent)
        double_spinbox.setValue(obj.obj_default)
        WidgetFactory.setup_widget(double_spinbox, obj)
        WidgetFactory.set_spinbox_ranges(double_spinbox, obj)

        return double_spinbox

    @staticmethod
    def set_spinbox_ranges(
        spinbox: Union[QSpinBox, QDoubleSpinBox],
        obj: MiraclObj,
    ) -> None:
        """Set the range and increment properties for a spinbox.

        :param spinbox: The spinbox instance to configure.
        :type spinbox: QSpinBox or QDoubleSpinBox
        :param obj: The MiraclObj containing range information.
        :type obj: MiraclObj
        """
        # Check if the range_formatting_vals attribute exists
        if hasattr(obj, "range_formatting_vals"):
            logger.debug(
                f"{obj.name} has range_formatting_vals: {obj.range_formatting_vals}"
            )

            # Initialize default values for spinbox properties
            min_val = None
            max_val = None
            increment_val = None
            nr_decimals = None

            # Check if range_formatting_vals is not None
            if obj.range_formatting_vals is not None:
                logger.debug(
                    f"Setting ranges for {obj.name} with range_formatting_vals: {obj.range_formatting_vals}"
                )

                min_val = obj.range_formatting_vals.min_val
                max_val = obj.range_formatting_vals.max_val
                increment_val = obj.range_formatting_vals.increment_val
                nr_decimals = obj.range_formatting_vals.nr_decimals

                if min_val is not None:
                    spinbox.setMinimum(min_val)
                    logger.debug(f"Set minimum value to {min_val} for {obj.name}")
                if max_val is not None:
                    spinbox.setMaximum(max_val)
                    logger.debug(f"Set maximum value to {max_val} for {obj.name}")
                if increment_val is not None:
                    spinbox.setSingleStep(increment_val)
                    logger.debug(
                        f"Set increment value to {increment_val} for {obj.name}"
                    )

            # Set decimals only for double spinbox
            if isinstance(spinbox, QDoubleSpinBox) and nr_decimals is not None:
                spinbox.setDecimals(nr_decimals)
                logger.debug(f"Set number of decimals to {nr_decimals} for {obj.name}")
        else:
            logger.debug(
                f"{obj.name} does not have range_formatting_vals attribute, skipping range setup."
            )

    @staticmethod
    def create_path_input_widget(
        obj: MiraclObj, parent: QWidget
    ) -> Tuple[QWidget, QLineEdit]:
        """Create a path input widget from a MiraclObj."""
        path_widget = QWidget(parent)
        path_layout = QHBoxLayout(path_widget)

        # Create the QLineEdit for path input
        path_input = QLineEdit()
        path_input.setPlaceholderText(obj.cli_help)
        path_layout.addWidget(path_input)

        # Create the button for selecting the folder
        path_select_button = QPushButton("Select folder")
        path_select_button.clicked.connect(
            lambda: WidgetFactory.open_path_dialog(parent, path_input)
        )
        path_layout.addWidget(path_select_button)
        path_layout.setContentsMargins(0, 0, 0, 0)

        WidgetFactory.setup_widget(path_input, obj)

        # Return both the container widget and the QLineEdit
        return path_widget, path_input  # Return the QWidget and QLineEdit

    @staticmethod
    def open_path_dialog(parent: QWidget, path_input: QLineEdit):
        """Open a directory selection dialog and set the selected path in the QLineEdit."""
        path = QFileDialog.getExistingDirectory(parent, "Select Directory")
        if path:
            path_input.setText(path)
