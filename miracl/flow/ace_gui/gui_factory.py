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
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    WidgetType,
)
from typing import List, Callable, Union, Dict


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
    def create_indented_label(text: str, help_text: str) -> QLabel:
        """Create an indented label with a tooltip."""
        if not text.endswith(":"):
            text += ":"
        label = QLabel("  " + text)
        label.setToolTip(help_text)
        return label


class WidgetFactory:
    """Factory class for creating widgets based on MiraclObj instances."""

    # @staticmethod
    # def create_widgets_from_objects(
    #     objs: List[Union[MiraclObj, SectionLabel]],
    #     parent: QWidget,
    # ) -> QWidget:
    #     """Create a QWidget containing form elements from a list of MiraclObj."""
    #     container_widget: QWidget = QWidget()
    #     layout: QFormLayout = QFormLayout(container_widget)
    #
    #     for obj in objs:
    #         label: QLabel = WidgetFactory.create_indented_label(
    #             obj.gui_label[0], obj.cli_help
    #         )
    #
    #         if obj.gui_widget_type == WidgetType.DROPDOWN:
    #             layout.addRow(label, WidgetFactory.create_dropdown(obj, parent))
    #         elif obj.gui_widget_type == WidgetType.SPINBOX:
    #             layout.addRow(label, WidgetFactory.create_spinbox(obj, parent))
    #         elif obj.gui_widget_type == WidgetType.PATH_INPUT:
    #             layout.addRow(
    #                 label, WidgetFactory.create_path_input_widget(obj, parent)
    #             )
    #
    #     return container_widget

    @staticmethod
    def create_widgets_from_objects(
        objs: List[Union[MiraclObj, SectionLabel]], parent: QWidget
    ) -> QWidget:
        """Create a QWidget containing form elements from a list of MiraclObj and SectionLabel."""
        container_widget: QWidget = QWidget()
        layout: QFormLayout = QFormLayout(container_widget)

        for obj in objs:
            if isinstance(obj, SectionLabel):
                # Use LabelFactory to create a section label
                label = LabelFactory.create_section_label(obj.text)
                layout.addRow(label)  # Add the section label to the layout
            elif isinstance(obj, MiraclObj):
                label: QLabel = LabelFactory.create_indented_label(
                    obj.gui_label[0], obj.cli_help
                )

                if obj.gui_widget_type == WidgetType.DROPDOWN:
                    layout.addRow(label, WidgetFactory.create_dropdown(obj, parent))
                elif obj.gui_widget_type == WidgetType.SPINBOX:
                    layout.addRow(label, WidgetFactory.create_spinbox(obj, parent))
                elif obj.gui_widget_type == WidgetType.PATH_INPUT:
                    layout.addRow(
                        label, WidgetFactory.create_path_input_widget(obj, parent)
                    )

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
        if hasattr(obj, "flow") and obj.flow is not None:
            widget.setObjectName(obj.flow["ace"]["cli_l_flag"])
        else:
            widget.setObjectName(obj.cli_l_flag)

    @staticmethod
    def create_dropdown(obj: MiraclObj, parent: QWidget) -> QComboBox:
        """Create a dropdown (combo box) widget from a MiraclObj."""
        dropdown: QComboBox = QComboBox(parent)
        dropdown.addItems(obj.cli_choices)
        dropdown.setCurrentText(obj.obj_default)
        WidgetFactory.setup_widget(dropdown, obj)

        return dropdown

    @staticmethod
    def create_spinbox(obj: MiraclObj, parent: QWidget) -> QSpinBox:
        """Create a standard spinbox widget from a MiraclObj."""
        spinbox: QSpinBox = QSpinBox(parent)
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
        # Define the attribute methods for range setting
        attribute_methods: Dict[str, Callable] = {
            "min_val": spinbox.setMinimum,
            "max_val": spinbox.setMaximum,
            "increment_val": spinbox.setSingleStep,
        }

        # Set ranges that are attributes of obj
        if obj.range_formatting_vals:
            for attr, method in attribute_methods.items():
                if attr in obj.range_formatting_vals:
                    method(obj.range_formatting_vals[attr])

        # Set decimals only for double spinbox
        if (
            isinstance(spinbox, QDoubleSpinBox)
            and "nr_decimals" in obj.range_formatting_vals
        ):
            spinbox.setDecimals(obj.range_formatting_vals["nr_decimals"])

    @staticmethod
    def create_path_input_widget(obj: MiraclObj, parent: QWidget) -> QWidget:
        """Create a path input widget from a MiraclObj."""
        path_widget = QWidget(parent)
        path_layout = QHBoxLayout(path_widget)
        path_input = QLineEdit()
        path_input.setPlaceholderText(obj.cli_help)
        path_layout.addWidget(path_input)
        path_select_button = QPushButton("Browse")
        path_select_button.clicked.connect(
            lambda: WidgetFactory.open_path_dialog(parent, path_input)
        )
        path_layout.addWidget(path_select_button)
        path_layout.setContentsMargins(0, 0, 0, 0)

        WidgetFactory.setup_widget(path_input, obj)

        return path_widget

    @staticmethod
    def open_path_dialog(parent: QWidget, path_input: QLineEdit):
        """Open a directory selection dialog and set the selected path in the QLineEdit."""
        path = QFileDialog.getExistingDirectory(parent, "Select Directory")
        if path:
            path_input.setText(path)
