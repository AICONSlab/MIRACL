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
    QCheckBox,
)


class WidgetUtils:
    @staticmethod
    def create_path_input_widget(parent, layout, label_text, button_text):
        """
        Create and add a path input widget to the given layout.

        This method creates a widget consisting of a QLabel, QLineEdit, and QPushButton.
        The label is placed in the left column of the form layout, while the QLineEdit
        and QPushButton are combined in a QWidget and placed in the right column.

        :param parent: The parent widget for the file dialog.
        :type parent: QWidget
        :param layout: The QFormLayout to which the widget will be added.
        :type layout: QFormLayout
        :param label_text: The text to be displayed in the label.
        :type label_text: str
        :param button_text: The text to be displayed on the button.
        :type button_text: str
        :return: A tuple containing the created QLabel, QLineEdit, and QPushButton.
        :rtype: tuple(QLabel, QLineEdit, QPushButton)

        Example:
            >>> label, path_input, folder_button = WidgetUtils.create_path_input_widget(self, main_tab_layout, "Select folder:", "Browse")
        """
        # Create the label
        label = WidgetUtils.create_indented_label(label_text)

        # Create the widget to hold the QLineEdit and QPushButton
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)

        # Create and add input field
        path_input = QLineEdit()
        path_layout.addWidget(path_input)

        # Create and add button
        folder_test_button = QPushButton(button_text)
        folder_test_button.clicked.connect(
            lambda: WidgetUtils.openFileDialog(parent, path_input)
        )
        path_layout.addWidget(folder_test_button)

        path_layout.setContentsMargins(0, 0, 0, 0)

        # Add the label and the path widget to the form layout
        layout.addRow(label, path_widget)

        return label, path_input, folder_test_button

    @staticmethod
    def create_indented_label(text):
        """
        Create an indented label.

        :param text: The text for the label.
        :type text: str
        :return: A QLabel instance with indented text.
        :rtype: QLabel
        """
        return QLabel("  " + text)

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
    def create_multiple_choice(layout, lbl, choices, default_choice):
        """
        Create a multiple-choice widget and add it to the given layout.

        :param layout: The layout to which the multiple-choice widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the multiple-choice widget.
        :type lbl: str
        :param choices: A list of available choices for the multiple-choice widget.
        :type choices: list[str]
        :param default_choice: The default choice to be selected.
        :type default_choice: str
        :return: The created QComboBox instance.
        :rtype: QComboBox
        """
        label = WidgetUtils.create_indented_label(lbl)
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
    def create_resolution(layout, lbl, default_text):
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
        label = WidgetUtils.create_indented_label(lbl)
        text_field = QLineEdit()
        text_field.setPlaceholderText(default_text)
        layout.addRow(label, text_field)
        return text_field

    @staticmethod
    def create_digit_spinbox(layout, lbl, default_value):
        """
        Create a digit spinbox widget and add it to the given layout.

        :param layout: The layout to which the digit spinbox widget will be added.
        :type layout: QFormLayout
        :param lbl: The label text for the digit spinbox widget.
        :type lbl: str
        :param default_value: The default value for the digit spinbox widget.
        :type default_value: int
        :return: The created QSpinBox instance.
        :rtype: QSpinBox
        """
        label = WidgetUtils.create_indented_label(lbl)
        spinbox = WidgetUtils.create_spinbox(0, 99)
        spinbox.setValue(default_value)
        layout.addRow(label, spinbox)
        return spinbox

    @staticmethod
    def create_spinbox(min_value, max_value):
        """
        Create a QSpinBox with the given minimum and maximum values.

        :param min_value: The minimum value for the QSpinBox.
        :type min_value: int
        :param max_value: The maximum value for the QSpinBox.
        :type max_value: int
        :return: The created QSpinBox instance.
        :rtype: QSpinBox
        """
        spinbox = QSpinBox()
        spinbox.setRange(min_value, max_value)
        return spinbox

    @staticmethod
    def create_orientation_code(layout, lbl, default_text):
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
        label = WidgetUtils.create_indented_label(lbl)
        text_field_test = QLineEdit()
        text_field_test.setPlaceholderText(default_text)
        text_field_test.setText(default_text)
        layout.addRow(label, text_field_test)
        return text_field_test

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
