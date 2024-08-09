from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
)
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    WidgetType,
)
from typing import List, Callable, Union


class WidgetFactory:
    """Factory class for creating widgets based on MiraclObj instances."""

    @staticmethod
    def create_widgets_from_objects(objs: List[MiraclObj]) -> QWidget:
        """Create a QWidget containing form elements from a list of MiraclObj."""
        container_widget: QWidget = QWidget()
        layout: QFormLayout = QFormLayout(container_widget)

        for obj in objs:
            label: QLabel = WidgetFactory.create_indented_label(
                obj.gui_label[0], obj.cli_help
            )

            if obj.gui_widget_type == WidgetType.DROPDOWN:
                layout.addRow(label, WidgetFactory.create_dropdown(obj))
            elif obj.gui_widget_type == WidgetType.SPINBOX:
                layout.addRow(label, WidgetFactory.create_spinbox(obj))

        return container_widget

    @staticmethod
    def create_indented_label(text: str, help_text: str) -> QLabel:
        """Create an indented label with a tooltip."""
        if not text.endswith(":"):
            text += ":"
        label: QLabel = QLabel("  " + text)
        label.setToolTip(help_text)
        return label

    @staticmethod
    def setup_widget(widget: QWidget, obj: MiraclObj) -> None:
        """Set up common properties for widgets.

        :param widget: The widget to set up (QComboBox or QSpinBox).
        :param obj: The MiraclObj containing data for the widget.
        """
        widget.setObjectName(obj.flow["ace"]["cli_l_flag"])

    @staticmethod
    def create_dropdown(obj: MiraclObj) -> QComboBox:
        """Create a dropdown (combo box) widget from a MiraclObj."""
        dropdown: QComboBox = QComboBox()
        dropdown.addItems(obj.cli_choices)
        dropdown.setCurrentText(obj.obj_default)
        WidgetFactory.setup_widget(dropdown, obj)

        return dropdown

    @staticmethod
    def create_spinbox(obj: MiraclObj) -> QSpinBox:
        """Create a standard spinbox widget from a MiraclObj."""
        spinbox: QSpinBox = QSpinBox()
        spinbox.setValue(obj.obj_default)
        WidgetFactory.setup_widget(spinbox, obj)
        WidgetFactory.set_spinbox_ranges(spinbox, obj)

        return spinbox

    @staticmethod
    def create_double_spinbox(obj: MiraclObj) -> QDoubleSpinBox:
        """Create a double spinbox widget from a MiraclObj."""
        double_spinbox: QDoubleSpinBox = QDoubleSpinBox()
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
        attribute_methods: Dict[str, Callable] = {
            "min_val": spinbox.setMinimum,
            "max_val": spinbox.setMaximum,
            "increment_val": spinbox.setSingleStep,
        }

        if obj.range_formatting_vals:
            for attr, method in attribute_methods.items():
                if attr in obj.range_formatting_vals:
                    method(obj.range_formatting_vals[attr])

        # Set decimals for double spinbox if available
        if (
            isinstance(spinbox, QDoubleSpinBox)
            and "nr_decimals" in obj.range_formatting_vals
        ):
            spinbox.setDecimals(obj.range_formatting_vals["nr_decimals"])
