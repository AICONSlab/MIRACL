#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Utilities

Description:
    A collection of utility functions for creating and managing widgets in PyQt5.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QSpinBox,
    QLineEdit,
    QPushButton,
    QLabel,
    QFileDialog,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QCheckBox,
    QDoubleSpinBox,
)
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator, QDoubleValidator
from PyQt5.QtCore import QRegularExpression
import argparse
from typing import Dict, Any, Optional


class WidgetUtils:
    # @staticmethod
    # def create_path_input_widget(parent, layout, lbl, lbl_help_text, button_text):
    #     """
    #     Create and add a path input widget to the given layout.
    #
    #     This method creates a widget consisting of a QLabel, QLineEdit, and QPushButton.
    #     The label is placed in the left column of the form layout, while the QLineEdit
    #     and QPushButton are combined in a QWidget and placed in the right column.
    #
    #     :param parent: The parent widget for the file dialog.
    #     :type parent: QWidget
    #     :param layout: The QFormLayout to which the widget will be added.
    #     :type layout: QFormLayout
    #     :param label_text: The text to be displayed in the label.
    #     :type label_text: str
    #     :param button_text: The text to be displayed on the button.
    #     :type button_text: str
    #     :return: A tuple containing the created QLabel, QLineEdit, and QPushButton.
    #     :rtype: tuple(QLabel, QLineEdit, QPushButton)
    #
    #     Example:
    #         >>> label, path_input, folder_button = WidgetUtils.create_path_input_widget(self, main_tab_layout, "Select folder:", "Browse")
    #     """
    #     label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
    #     path_widget = QWidget()
    #     path_layout = QHBoxLayout(path_widget)
    #     path_input = QLineEdit()
    #     path_layout.addWidget(path_input)
    #     folder_test_button = QPushButton(button_text)
    #     folder_test_button.clicked.connect(
    #         lambda: WidgetUtils.openFileDialog(parent, path_input)
    #     )
    #     path_layout.addWidget(folder_test_button)
    #     path_layout.setContentsMargins(0, 0, 0, 0)
    #     layout.addRow(label, path_widget)
    #
    #     return label, path_input, folder_test_button

    @staticmethod
    def create_path_input_widget(
        parent,
        layout,
        lbl,
        lbl_help_text,
        button_text,
        select_files=False,
        file_filter="All Files (*)",
    ):
        """
        Create and add a path input widget to the given layout.

        This method creates a widget consisting of a QLabel, QLineEdit, and QPushButton.
        The label is placed in the left column of the form layout, while the QLineEdit
        and QPushButton are combined in a QWidget and placed in the right column.
        The button opens a file or folder selection dialog based on the select_files argument.

        :param parent: The parent widget for the file dialog.
        :type parent: QWidget
        :param layout: The QFormLayout to which the widget will be added.
        :type layout: QFormLayout
        :param lbl: The text to be displayed in the label.
        :type lbl: str
        :param lbl_help_text: The help text for the label.
        :type lbl_help_text: str
        :param button_text: The text to be displayed on the button.
        :type button_text: str
        :param select_files: If True, the dialog will allow file selection; otherwise, folder selection.
        :type select_files: bool
        :param file_filter: The file filter for the file dialog (default: "All Files (*)").
        :type file_filter: str
        :return: A tuple containing the created QLabel, QLineEdit, and QPushButton.
        :rtype: tuple(QLabel, QLineEdit, QPushButton)

        Example:
            >>> label, path_input, path_button = WidgetUtils.create_path_input_widget(
            ...     self, main_tab_layout, "Select path:", "Help text", "Browse", select_files=True, file_filter="Text Files (*.txt)")
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_input = QLineEdit()
        path_layout.addWidget(path_input)
        path_select_button = QPushButton(button_text)
        path_select_button.clicked.connect(
            lambda: WidgetUtils.open_path_dialog(
                parent, path_input, select_files, file_filter
            )
        )
        path_layout.addWidget(path_select_button)
        path_layout.setContentsMargins(0, 0, 0, 0)
        layout.addRow(label, path_widget)

        return label, path_input, path_select_button

    @staticmethod
    def open_path_dialog(parent, line_edit, select_files, file_filter):
        if select_files:
            path, _ = QFileDialog.getOpenFileName(
                parent, "Select File", "", file_filter
            )
        else:
            path = QFileDialog.getExistingDirectory(parent, "Select Directory")

        if path:
            line_edit.setText(path)

    # @staticmethod
    # def create_three_text_input_widget(layout, lbl, lbl_help_text, default_values):
    #     """
    #     Create and add a path input widget with three validated text fields to the given layout.
    #
    #     :param layout: The QFormLayout to which the widget will be added.
    #     :type layout: QFormLayout
    #     :param lbl: The text to be displayed in the label.
    #     :type lbl: str
    #     :param lbl_help_text: The help text for the label.
    #     :type lbl_help_text: str
    #     :param default_values: A list of three default values for the input fields.
    #     :type default_values: list
    #     :return: A tuple containing the created QLabel and three QLineEdit widgets.
    #     :rtype: tuple(QLabel, QLineEdit, QLineEdit, QLineEdit)
    #     """
    #     label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
    #
    #     input_widget = QWidget()
    #     input_layout = QHBoxLayout(input_widget)
    #     input_layout.setContentsMargins(0, 0, 0, 0)
    #
    #     inputs = []
    #     for default_value in default_values:
    #         input_field = QLineEdit()
    #         input_field.setPlaceholderText(str(default_value))
    #         input_field.setText(str(default_value))
    #
    #         validator = QDoubleValidator()
    #         validator.setNotation(QDoubleValidator.StandardNotation)
    #         input_field.setValidator(validator)
    #
    #         input_layout.addWidget(input_field)
    #         inputs.append(input_field)
    #
    #     layout.addRow(label, input_widget)
    #
    #     return (label, *inputs)

    @staticmethod
    def create_three_text_input_widget(
        layout, lbl, lbl_help_text, default_values, input_types
    ):
        """
        Create and add a path input widget with three validated text fields to the given layout.

        :param layout: The QFormLayout to which the widget will be added.
        :type layout: QFormLayout
        :param lbl: The text to be displayed in the label.
        :type lbl: str
        :param lbl_help_text: The help text for the label.
        :type lbl_help_text: str
        :param default_values: A list of three default values for the input fields.
        :type default_values: list
        :param input_types: A list of three input types for the fields ("int", "float", "str", "strcon", or "alphanum").
        :type input_types: list
        :return: A tuple containing the created QLabel and three QLineEdit widgets.
        :rtype: tuple(QLabel, QLineEdit, QLineEdit, QLineEdit)
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)

        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)

        inputs = []
        for default_value, input_type in zip(default_values, input_types):
            input_field = QLineEdit()
            input_field.setPlaceholderText(str(default_value))
            input_field.setText(str(default_value))

            if input_type == "int":
                validator = QIntValidator()
            elif input_type == "float":
                validator = QDoubleValidator()
                validator.setNotation(QDoubleValidator.StandardNotation)
            elif input_type == "str":
                regex = QRegularExpression("^[A-Za-z]+$")
                validator = QRegularExpressionValidator(regex)
            elif input_type == "strcon":
                regex = QRegularExpression("^[A-Za-z0-9_-]+$")
                validator = QRegularExpressionValidator(regex)
            elif input_type == "alphanum":
                regex = QRegularExpression("^[A-Za-z0-9]+$")
                validator = QRegularExpressionValidator(regex)
            else:
                raise ValueError(f"Invalid input type: {input_type}")

            input_field.setValidator(validator)
            input_layout.addWidget(input_field)
            inputs.append(input_field)

        layout.addRow(label, input_widget)

        return (label, *inputs)

    @staticmethod
    def create_multiple_text_input_widget(
        layout, lbl, lbl_help_text, default_values, field_labels
    ):
        """
        Create and add a widget with multiple validated text fields to the given layout.

        :param layout: The QFormLayout to which the widget will be added.
        :type layout: QFormLayout
        :param lbl: The text to be displayed in the main label.
        :type lbl: str
        :param lbl_help_text: The help text for the main label.
        :type lbl_help_text: str
        :param default_values: A list of default values for the input fields.
        :type default_values: list
        :param field_labels: A list of labels for each input field.
        :type field_labels: list
        :return: A tuple containing the created main QLabel and the QLineEdit widgets.
        :rtype: tuple(QLabel, QLineEdit, ...)
        """
        main_label = WidgetUtils.create_indented_label(lbl, lbl_help_text)

        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 0)

        inputs = []
        for i, (default_value, field_label) in enumerate(
            zip(default_values, field_labels)
        ):
            label = QLabel(field_label)
            input_layout.addWidget(label)

            input_field = QLineEdit()
            if default_value != "none":
                input_field.setPlaceholderText(str(default_value))
                input_field.setText(str(default_value))
            else:
                input_field.setPlaceholderText("None")
            # input_field.setPlaceholderText(str(default_value))
            # input_field.setText(str(default_value))

            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            input_field.setValidator(validator)

            input_layout.addWidget(input_field)
            inputs.append(input_field)

            if i < len(default_values) - 1:
                input_layout.addItem(
                    QSpacerItem(0.5, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)
                )

        layout.addRow(main_label, input_widget)

        return (main_label, *inputs)

    @staticmethod
    def create_indented_label(text, help_text):
        """
        Create an indented label.

        :param text: The text for the label.
        :type text: str
        :return: A QLabel instance with indented text.
        :rtype: QLabel
        """
        label = QLabel("  " + text)
        label.setToolTip(help_text)
        return label
        # return QLabel("  " + text)

    @staticmethod
    def openFileDialog(parent, path_input):
        """
        Open a file dialog and set the selected path to the given QLineEdit.

        :param parent: The parent widget for the file dialog.
        :type parent: QWidget
        :param path_input: The QLineEdit to update with the selected path.
        :type path_input: QLineEdit
        """
        options = QFileDialog.Options()
        path = QFileDialog.getExistingDirectory(
            parent, "Select Directory", "", options=options
        )
        if path:
            path_input.setText(path)

    @staticmethod
    def create_section_title(layout, text):
        """
        Add a section title to the given layout.

        :param layout: The layout to which the section title will be added.
        :type layout: QFormLayout
        :param text: The text to be displayed as the section title.
        :type text: str
        """
        layout.addRow(QLabel(text))

    @staticmethod
    def create_multiple_choice(layout, lbl, lbl_help_text, choices, default_choice):
        """
        Create a multiple-choice widget and add it to the given layout.

        :param layout: The layout to which the multiple-choice widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the multiple-choice widget.
        :type lbl: str
        :param lbl_help_text: The help text to be displayed as a tooltip for the label.
        :type lbl_help_text: str
        :param choices: A list of available choices for the multiple-choice widget.
        :type choices: list[str]
        :param default_choice: The default choice to be selected.
        :type default_choice: str
        :return: The created QComboBox instance.
        :rtype: QComboBox
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        model = WidgetUtils.create_combo(choices)
        model.setCurrentText(default_choice)
        layout.addRow(label, model)
        return model

    @staticmethod
    def create_combo(items):
        """
        Create a QComboBox with the given items.

        :param items: A list of items to be added to the QComboBox.
        :type items: list[str]
        :return: The created QComboBox instance.
        :rtype: QComboBox
        """
        combo = QComboBox()
        combo.addItems(items)
        return combo

    @staticmethod
    def create_resolution(
        layout, lbl, lbl_help_text, default_placeholder, default_text
    ):
        """
        Create a resolution input widget and add it to the given layout.

        :param layout: The layout to which the resolution input widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the resolution input widget.
        :type lbl: str
        :param default_text: The default text to be displayed in the resolution input widget.
        :type default_text: str
        :return: The created QLineEdit instance.
        :rtype: QLineEdit
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        float_validator = QDoubleValidator()
        text_field = QLineEdit()
        text_field.setValidator(float_validator)
        text_field.setPlaceholderText(default_placeholder)
        if default_text != "none":
            text_field.setText(default_text)
        layout.addRow(label, text_field)
        return text_field

    # @staticmethod
    # def create_digit_spinbox(layout, lbl, lbl_help_text, default_value):
    #     """
    #     Create a digit spinbox widget and add it to the given layout.
    #
    #     :param layout: The layout to which the digit spinbox widget will be added.
    #     :type layout: QFormLayout
    #     :param lbl: The label text for the digit spinbox widget.
    #     :type lbl: str
    #     :param default_value: The default value for the digit spinbox widget.
    #     :type default_value: int
    #     :return: The created QSpinBox instance.
    #     :rtype: QSpinBox
    #     """
    #     label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
    #     spinbox = WidgetUtils.create_spinbox(0, 99)
    #     spinbox.setValue(default_value)
    #     layout.addRow(label, spinbox)
    #     return spinbox
    #
    # @staticmethod
    # def create_spinbox(min_value, max_value):
    #     """
    #     Create a QSpinBox with the given minimum and maximum values.
    #
    #     :param min_value: The minimum value for the QSpinBox.
    #     :type min_value: int
    #     :param max_value: The maximum value for the QSpinBox.
    #     :type max_value: int
    #     :return: The created QSpinBox instance.
    #     :rtype: QSpinBox
    #     """
    #     spinbox = QSpinBox()
    #     spinbox.setRange(min_value, max_value)
    #     return spinbox

    @staticmethod
    def create_digit_spinbox(
        layout,
        lbl,
        lbl_help_text,
        default_value,
        min_value=0,
        max_value=99,
        input_type="int",
        increment=1,
        decimals=2,
    ):
        """
        Create a digit spinbox widget and add it to the given layout.

        :param layout: The layout to which the digit spinbox widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the digit spinbox widget.
        :type lbl: str
        :param lbl_help_text: The help text for the label.
        :type lbl_help_text: str
        :param default_value: The default value for the digit spinbox widget.
        :type default_value: int or float
        :param min_value: The minimum value for the spinbox (default is 0).
        :type min_value: int or float
        :param max_value: The maximum value for the spinbox (default is 99).
        :type max_value: int or float
        :param input_type: The type of input to accept, either "int" or "float" (default is "int").
        :type input_type: str
        :param increment: The increment value for the spinbox (default is 1 for int, 0.01 for float).
        :type increment: int or float
        :param decimals: The number of decimal places to display (default is 2).
        :type decimals: int
        :return: The created QSpinBox or QDoubleSpinBox instance.
        :rtype: QSpinBox or QDoubleSpinBox
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        spinbox = WidgetUtils.create_spinbox(
            min_value, max_value, input_type, increment, decimals
        )

        if input_type == "int":
            spinbox.setValue(int(default_value))
        elif input_type == "float":
            spinbox.setValue(float(default_value))

        layout.addRow(label, spinbox)
        return spinbox

    @staticmethod
    def create_spinbox(min_value, max_value, input_type="int", increment=1, decimals=2):
        """
        Create a QSpinBox or QDoubleSpinBox with the given minimum and maximum values.

        :param min_value: The minimum value for the spinbox.
        :type min_value: int or float
        :param max_value: The maximum value for the spinbox.
        :type max_value: int or float
        :param input_type: The type of input to accept, either "int" or "float" (default is "int").
        :type input_type: str
        :param increment: The increment value for the spinbox (default is 1 for int, 0.01 for float).
        :type increment: int or float
        :param decimals: The number of decimal places to display (default is 2).
        :type decimals: int
        :return: The created QSpinBox or QDoubleSpinBox instance.
        :rtype: QSpinBox or QDoubleSpinBox
        """
        if input_type == "int":
            spinbox = QSpinBox()
            spinbox.setRange(int(min_value), int(max_value))
            spinbox.setSingleStep(int(increment))
        elif input_type == "float":
            spinbox = QDoubleSpinBox()
            spinbox.setRange(float(min_value), float(max_value))
            spinbox.setSingleStep(float(increment))
            spinbox.setDecimals(decimals)
        else:
            raise ValueError("Invalid input_type. Must be 'int' or 'float'.")
        return spinbox

    @staticmethod
    def create_text_field(layout, lbl, lbl_help_text, default_text, validator):
        """
        Create an orientation code input widget and add it to the given layout.

        :param layout: The layout to which the orientation code input widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the orientation code input widget.
        :type lbl: str
        :param default_text: The default text to be displayed in the orientation code input widget.
        :type default_text: str
        :return: The created QLineEdit instance.
        :rtype: QLineEdit
        """
        if validator == "str":
            regex = QRegularExpression("^[A-Za-z]+$")
        elif validator == "strcon":
            regex = QRegularExpression("^[A-Za-z0-9_-]+$")
        else:
            regex = QRegularExpression("^[A-Za-z0-9]+$")
        str_validator = QRegularExpressionValidator(regex)
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        text_field_test = QLineEdit()
        if default_text != "none":
            text_field_test.setPlaceholderText(default_text)
            text_field_test.setText(default_text)
        else:
            text_field_test.setPlaceholderText("None")
        text_field_test.setValidator(str_validator)
        layout.addRow(label, text_field_test)
        return text_field_test

    # @staticmethod
    # def create_digit_text_field(layout, lbl, lbl_help_text, default_digit):
    #     """
    #     Create an orientation code input widget and add it to the given layout.
    #
    #     :param layout: The layout to which the orientation code input widget will be added.
    #     :type layout: QFormLayout
    #     :param lbl: The label text for the orientation code input widget.
    #     :type lbl: str
    #     :param default_text: The default text to be displayed in the orientation code input widget.
    #     :type default_text: str
    #     :return: The created QLineEdit instance.
    #     :rtype: QLineEdit
    #     """
    #     label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
    #     digit_text_field_test = QLineEdit()
    #     if default_digit != "none":
    #         digit_text_field_test.setPlaceholderText(default_digit)
    #         digit_text_field_test.setText(default_digit)
    #     else:
    #         digit_text_field_test.setPlaceholderText("None")
    #     digit_text_field_test.setValidator(QIntValidator())
    #     digit_text_field_test.setPlaceholderText(default_digit)
    #     digit_text_field_test.setText(default_digit)
    #     layout.addRow(label, digit_text_field_test)
    #     return digit_text_field_test

    @staticmethod
    def create_digit_text_field(
        layout, lbl, lbl_help_text, default_digit, input_type="int"
    ):
        """
        Create a validated text field widget and add it to the given layout.

        :param layout: The layout to which the text field widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the text field widget.
        :type lbl: str
        :param lbl_help_text: The help text for the label.
        :type lbl_help_text: str
        :param default_digit: The default value for the text field.
        :type default_digit: str
        :param input_type: The type of input to accept, either "int" or "float" (default is "int").
        :type input_type: str
        :return: The created QLineEdit instance.
        :rtype: QLineEdit
        """
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        digit_text_field = QLineEdit()

        if input_type == "int":
            validator = QIntValidator()
        elif input_type == "float":
            validator = QDoubleValidator()
        else:
            raise ValueError("Invalid input_type. Must be 'int' or 'float'.")

        if default_digit != "none":
            digit_text_field.setPlaceholderText(str(default_digit))
            digit_text_field.setText(str(default_digit))
        else:
            digit_text_field.setPlaceholderText("None")

        digit_text_field.setValidator(validator)
        layout.addRow(label, digit_text_field)

        return digit_text_field

    @staticmethod
    def create_method_checkbox(parent, layout, lbl):
        """
        Create a method checkbox and add it to the given layout.

        :param parent: The parent widget for the checkbox.
        :type parent: QWidget
        :param layout: The layout to which the checkbox will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the checkbox.
        :type lbl: str
        :return: The created QCheckBox instance.
        :rtype: QCheckBox
        """
        parent.single_checkbox = QCheckBox(lbl)
        layout.addRow(parent.single_checkbox)
        return parent.single_checkbox

    @staticmethod
    def translate_choice_to_parser_value(dictionary, input_key):
        """
        Check if the input_key exists in the dictionary and return its corresponding value.

        Parameters:
        dictionary (dict): The dictionary to search in.
        input_key: The key to look for in the dictionary.

        Returns:
        The value corresponding to the input_key if found.

        Raises:
        KeyError: If the input_key is not found in the dictionary.
        """
        if input_key in dictionary:
            return dictionary[input_key]
        else:
            raise KeyError(f"Key '{input_key}' not found in the dictionary.")

    # Use once we updated to newer Python version. This uses match!
    # @staticmethod
    # def get_tab_var(tab, input_field_name, widget_type):
    #     """
    #     Retrieve the value from a specified input field in a given tab.
    #
    #     This function dynamically accesses the specified input field,
    #     and returns the value of the input field based on the widget type.
    #
    #     :param tab: The tab object containing the input field
    #     :type tab: object
    #     :param input_field_name: The name of the input field
    #     :type input_field_name: str
    #     :param widget_type: The type of the widget
    #     :type widget_type: str
    #     :return: The value of the specified input field
    #     :rtype: Any
    #     :raises AttributeError: If the specified input field or method does not exist
    #     :raises ValueError: If an unsupported widget type is provided
    #
    #     :example:
    #
    #     >>> main_tab = self.tab_manager.main_tab
    #     >>> main_tab_single_method_path = YourClass.get_tab_var(
    #     ...     main_tab, "single_method_path_input", "qlineedit"
    #     ... )
    #     '/path/to/single/method'
    #     >>> selected_option = YourClass.get_tab_var(
    #     ...     main_tab, "some_combo_box", "qcombobox"
    #     ... )
    #     'Selected Option'
    #     >>> numeric_value = YourClass.get_tab_var(
    #     ...     main_tab, "some_spin_box", "qspinbox"
    #     ... )
    #     42
    #     """
    #     input_field = getattr(tab, input_field_name)
    #
    #     match widget_type.lower():
    #         case "qlineedit":
    #             return input_field.text()
    #         case "qcombobox":
    #             return input_field.currentText()
    #         case "qspinbox" | "qdoublespinbox":
    #             return input_field.value()
    #         case _:
    #             raise ValueError(f"Unsupported widget type: {widget_type}")

    @staticmethod
    def get_tab_var(tab: object, input_field_name: str, widget_type: str) -> Any:
        """
        Retrieve the value from a specified input field in a given tab.

        This function dynamically accesses the specified input field,
        and returns the value of the input field based on the widget type.

        :param tab: The tab object containing the input field
        :type tab: object
        :param input_field_name: The name of the input field
        :type input_field_name: str
        :param widget_type: The type of the widget
        :type widget_type: str
        :return: The value of the specified input field
        :rtype: Any
        :raises AttributeError: If the specified input field or method does not exist
        :raises ValueError: If an unsupported widget type is provided

        :example:

        >>> main_tab = self.tab_manager.main_tab
        >>> main_tab_single_method_path = YourClass.get_tab_var(
        ...     main_tab, "single_method_path_input", "textfield"
        ... )
        '/path/to/single/method'
        >>> selected_option = YourClass.get_tab_var(
        ...     main_tab, "some_combo_box", "multiplechoice"
        ... )
        'Selected Option'
        >>> numeric_value = YourClass.get_tab_var(
        ...     main_tab, "some_spin_box", "spinbox"
        ... )
        42
        """
        input_field = getattr(tab, input_field_name)

        widget_type = widget_type.lower()
        if widget_type == "textfield":
            return input_field.text()
        elif widget_type == "multiplechoice":
            return input_field.currentText()
        elif widget_type in ["spinbox", "doublespinbox"]:
            return input_field.value()
        else:
            raise ValueError(f"Unsupported widget type: {widget_type}")

    @staticmethod
    def craft_flags(flags: Dict[str, Optional[str]]) -> str:
        """
        Construct a string of flags and arguments from the provided dictionary.

        This function takes a dictionary of flags and their corresponding values,
        and constructs a string by concatenating the flags and values that have non-empty values.

        :param flags: A dictionary where the keys are the flags and the values are the corresponding text (or None or empty string).
        :type flags: Dict[str, Optional[str]]
        :return: The constructed string of flags and arguments.
        :rtype: str

        :example:

        >>> flags = {
        ...     "-t": "/path/to/single/method",
        ...     "-a": "/path/to/multi/method",
        ...     "-o": None,
        ...     "-p": ""
        ... }
        >>> flag_string = YourClass.craft_flags(flags)
        >>> print(flag_string)
        -t /path/to/single/method -a /path/to/multi/method
        """
        # flag_pairs = (
        #     f"{flag} {value}"
        #     for flag, value in flags.items()
        #     if value and str(value).strip()
        # )
        flag_pairs = (
            f"{flag} {value}" if str(value).strip() != "set_bool" else f"{flag}"
            for flag, value in flags.items()
            if value and str(value).strip()
        )

        return " ".join(flag_pairs)

    @staticmethod
    def extract_help_texts(parser: argparse.ArgumentParser) -> Dict[str, str]:
        """
        Extracts help texts from an ArgumentParser object and returns them in a dictionary.

        This function efficiently processes all actions in the given parser, extracting the help text
        for each long-form option (starting with '--'), and stores it in a dictionary. It handles
        placeholders like %(default)s, %(type)s, and others that might be present in the help text.
        It also removes any newline characters (\n) from the help text.

        :param parser: The ArgumentParser object to extract help texts from.
        :type parser: argparse.ArgumentParser or a custom parser class

        :return: A dictionary where keys are the long-form flags (without '--') and values are the help texts.
        :rtype: dict

        :example:

        >>> from argparse import ArgumentParser
        >>> parser = ArgumentParser()
        >>> parser.add_argument('--flag', help='This is a flag\nwith multiple lines', default='value')
        >>> help_texts = YourClass.extract_help_texts(parser)
        >>> print(help_texts)
        {'flag': 'This is a flag with multiple lines'}
        """
        # Ensure we are working with an ArgumentParser instance
        if not isinstance(parser, argparse.ArgumentParser):
            if hasattr(parser, "parser") and isinstance(
                parser.parser, argparse.ArgumentParser
            ):
                parser = parser.parser
            else:
                raise TypeError(
                    "The provided parser is not an instance of argparse.ArgumentParser"
                )

        help_texts = {}
        for action in parser._actions:
            if action.help == argparse.SUPPRESS:
                continue

            # Find the first long option (if any)
            long_option = next(
                (opt for opt in action.option_strings if opt.startswith("--")), None
            )
            if long_option:
                flag = long_option[2:]  # Remove the '--'
                help_text = action.help

                # Prepare a dictionary with all possible placeholders
                format_dict = {
                    "default": action.default,
                    "type": action.type.__name__ if action.type else None,
                    "choices": ", ".join(map(str, action.choices))
                    if action.choices
                    else None,
                    "required": action.required,
                }

                # Replace placeholders in the help text
                try:
                    help_text = help_text % format_dict
                except KeyError as e:
                    # If a placeholder is not in our dictionary, we'll leave it as is
                    print(f"Warning: Unhandled placeholder {e} in help text for {flag}")

                # Remove newline characters from the help text
                help_text = help_text.replace("\n", " ")

                help_texts[flag] = help_text

        return help_texts

    @staticmethod
    def extract_arguments_to_dict(parser):
        if not isinstance(parser, argparse.ArgumentParser):
            if hasattr(parser, "parser") and isinstance(
                parser.parser, argparse.ArgumentParser
            ):
                parser = parser.parser
            else:
                raise TypeError(
                    "The provided parser is not an instance of argparse.ArgumentParser"
                )
        args_dict = {}

        # Iterate over the parser's actions to extract argument details
        for action in parser._actions:
            # Separate flags based on the number of leading hyphens
            short_flags = [
                flag
                for flag in action.option_strings
                if flag.startswith("-") and not flag.startswith("--")
            ]
            long_flags = [
                flag for flag in action.option_strings if flag.startswith("--")
            ]

            # Default value handling
            default_value = (
                str(action.default) if action.default is not argparse.SUPPRESS else ""
            )

            # Help message with the actual default value and type
            help_message = action.help if action.help else ""

            # Create a format dictionary for the help message
            format_dict = {
                "default": default_value,
                "type": action.type.__name__ if action.type else "None",
            }

            # Attempt to format the help message
            try:
                help_message = help_message % format_dict
            except KeyError as e:
                print(
                    f"Warning: Unhandled placeholder {e} in help text for {long_flags}"
                )

            # Prepare choices information as a list of strings
            if action.choices is not None:
                choices_info = [
                    str(choice) for choice in action.choices
                ]  # Convert choices to strings
            else:
                choices_info = None

            # Store the information in the dictionary using long flags as keys (without '--')
            for flag in long_flags:
                key = flag.lstrip("--")  # Remove the '--' prefix
                args_dict[key] = {
                    "default": default_value,
                    "help": help_message,
                    "choices": choices_info,
                    "type": action.type.__name__ if action.type else "None",
                }

        return args_dict
