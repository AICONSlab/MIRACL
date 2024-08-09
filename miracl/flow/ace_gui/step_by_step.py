# # main.py
#
# from PyQt5.QtWidgets import (
#     QApplication,
#     QHBoxLayout,
#     QMainWindow,
#     QWidget,
#     QVBoxLayout,
#     QPushButton,
# )
# from widget_factory import WidgetFactory
# from miracl.system.datamodels.datamodel_miracl_objs import (
#     MiraclObj,
#     WidgetType,
#     ArgumentType,
# )
# from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.window_title = "ACE flow"
#         self.setWindowTitle(self.window_title)
#         self.setGeometry(100, 100, 720, 600)
#
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#
#         main_layout = QVBoxLayout()
#         central_widget.setLayout(main_layout)
#
#         # Add the widgets to the main layout
#         first_section = WidgetFactory.create_widgets_from_objects(
#             [
#                 seg_ace.model_type,
#                 seg_ace.nr_workers,
#             ]
#         )
#         main_layout.addWidget(first_section)
#
#         # IO Buttons
#         io_widget = QWidget()
#         io_layout = QHBoxLayout(io_widget)
#         io_load_button = QPushButton("Load")
#         io_layout.addWidget(io_load_button)
#         io_save_button = QPushButton("Save")
#         io_layout.addWidget(io_save_button)
#         io_reset_button = QPushButton("Reset")
#         io_layout.addWidget(io_reset_button)
#         io_layout.setContentsMargins(0, 0, 0, 0)
#         main_layout.addWidget(io_widget)
#
#
# def main():
#     app = QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()

# from PyQt5.QtWidgets import (
#     QApplication,
#     QHBoxLayout,
#     QMainWindow,
#     QWidget,
#     QVBoxLayout,
#     QPushButton,
#     QSpinBox,
#     QDoubleSpinBox,
#     QComboBox,
# )
# from widget_factory import WidgetFactory
# from miracl.system.datamodels.datamodel_miracl_objs import (
#     MiraclObj,
#     WidgetType,
#     ArgumentType,
# )
# from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
#
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.window_title = "ACE flow"
#         self.setWindowTitle(self.window_title)
#         self.setGeometry(100, 100, 720, 600)
#
#         self.central_widget = QWidget()
#         self.setCentralWidget(self.central_widget)
#
#         self.main_layout = QVBoxLayout()
#         self.central_widget.setLayout(self.main_layout)
#
#         # Dictionary to store widget references
#         self.widgets = {}
#
#         # Add the widgets to the main layout
#         first_section = WidgetFactory.create_widgets_from_objects(
#             [
#                 seg_ace.model_type,
#                 seg_ace.nr_workers,
#             ]
#         )
#         self.main_layout.addWidget(first_section)
#
#         # Store widgets in the dictionary
#         self.store_widgets(first_section)
#
#         # IO Buttons
#         io_widget = QWidget()
#         io_layout = QHBoxLayout(io_widget)
#         io_load_button = QPushButton("Load")
#         io_layout.addWidget(io_load_button)
#         io_save_button = QPushButton("Save")
#         io_layout.addWidget(io_save_button)
#         io_reset_button = QPushButton("Reset")
#         io_layout.addWidget(io_reset_button)
#         io_layout.setContentsMargins(0, 0, 0, 0)
#         self.main_layout.addWidget(io_widget)
#
#         # Connect button signals to slots
#         io_load_button.clicked.connect(self.load_values)
#         io_save_button.clicked.connect(self.save_values)
#         io_reset_button.clicked.connect(self.reset_values)
#
#     def store_widgets(self, widget: QWidget):
#         """Store the widgets in the dictionary using their object names."""
#         for child in widget.findChildren(QWidget):
#             # Only store top-level widgets like QSpinBox, QDoubleSpinBox, or QComboBox
#             if isinstance(child, (QSpinBox, QDoubleSpinBox, QComboBox)):
#                 object_name = child.objectName()
#                 if object_name:
#                     self.widgets[object_name] = child
#
#     def load_values(self):
#         """Load values from the widgets."""
#         self.process_widget_values("Load")
#         print(self.widgets["sa_model_type"])
#
#     def save_values(self):
#         """Save values from the widgets (implement your logic here)."""
#         self.process_widget_values("Save")
#
#     def process_widget_values(self, action: str):
#         """Process the values of the widgets based on the action.
#
#         :param action: The action to perform ("Load" or "Save").
#         """
#         for name, widget in self.widgets.items():
#             if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
#                 value = widget.value()
#                 print(f"{action} {name}: {value}")
#             elif isinstance(widget, QComboBox):
#                 value = widget.currentText()
#                 print(f"{action} {name}: {value}")
#
#     def reset_values(self):
#         """Reset values in the widgets to their default values."""
#         for name, widget in self.widgets.items():
#             # Retrieve the MiraclObj associated with the widget
#             miracl_obj = self.get_miracl_obj_by_name(name)
#             if miracl_obj:
#                 if isinstance(widget, QSpinBox):
#                     widget.setValue(miracl_obj.obj_default)  # Reset to default value
#                 elif isinstance(widget, QDoubleSpinBox):
#                     widget.setValue(miracl_obj.obj_default)  # Reset to default value
#                 elif isinstance(widget, QComboBox):
#                     widget.setCurrentText(
#                         miracl_obj.obj_default
#                     )  # Reset to default choice
#
#     def get_miracl_obj_by_name(self, name: str) -> MiraclObj:
#         """Retrieve the MiraclObj associated with the given widget name.
#
#         :param name: The object name of the widget.
#         :type name: str
#         :return: The corresponding MiraclObj.
#         :rtype: MiraclObj
#         :raises ValueError: If no matching MiraclObj is found.
#         """
#         for obj in [
#             seg_ace.model_type,
#             seg_ace.nr_workers,
#         ]:  # Replace with your actual list of objects
#             if obj.flow["ace"]["cli_l_flag"] == name:
#                 return obj
#         raise ValueError(f"No MiraclObj found for widget name: {name}")
#
#
# def main():
#     app = QApplication([])
#     window = MainWindow()
#     window.show()
#     app.exec_()
#
#
# if __name__ == "__main__":
#     main()

from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import pyqtSignal
from widget_factory import WidgetFactory
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    WidgetType,
    ArgumentType,
)
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
import json
from uuid import uuid4
from datetime import datetime


class MainWindow(QMainWindow):
    value_changed = pyqtSignal(str, object)  # Signal to emit on value change

    def initialize_ui(self):
        """Initialize the UI and store widgets."""
        self.store_widgets(self)

    def __init__(self):
        super().__init__()
        self.window_title = "ACE flow"
        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

        self.initialize_ui()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.widgets = {}

        first_section = WidgetFactory.create_widgets_from_objects(
            [
                seg_ace.model_type,
                seg_ace.nr_workers,
            ]
        )
        self.main_layout.addWidget(first_section)

        self.store_widgets(first_section)

        io_widget = QWidget()
        io_layout = QHBoxLayout(io_widget)
        io_load_button = QPushButton("Load")
        io_layout.addWidget(io_load_button)
        io_save_button = QPushButton("Save")
        io_layout.addWidget(io_save_button)
        io_reset_button = QPushButton("Reset")
        io_layout.addWidget(io_reset_button)
        io_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(io_widget)

        # Connect button signals to slots
        io_load_button.clicked.connect(self.load_values)
        io_save_button.clicked.connect(
            lambda: self.save_values(
                "Save File",
                "",
                "MIRACL ACE Flow Files (*.aceflow)",
            )
        )
        io_reset_button.clicked.connect(self.confirm_reset)

        # Connect the custom signal to a slot
        self.value_changed.connect(self.on_value_changed)

    def store_widgets(self, widget: QWidget):
        """Store the widgets in the dictionary using their object names."""
        for child in widget.findChildren(QWidget):
            if isinstance(child, (QSpinBox, QDoubleSpinBox, QComboBox)):
                object_name = child.objectName()
                if object_name:
                    self.widgets[object_name] = child
                    # Connect signals to the slot
                    if isinstance(child, (QSpinBox, QDoubleSpinBox)):
                        child.valueChanged.connect(
                            lambda value, name=object_name: self.value_changed.emit(
                                name, value
                            )
                        )
                    elif isinstance(child, QComboBox):
                        child.currentTextChanged.connect(
                            lambda text, name=object_name: self.value_changed.emit(
                                name, text
                            )
                        )

    def on_value_changed(self, name, value):
        """Handle widget value changes."""
        print(f"Value changed in {name}: {value}")

    # def load_values(self):
    #     """Load values from the widgets."""
    #     self.process_widget_values("Load")

    def load_values(self):
        """Open a dialog to load values from a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load File", "", "MIRACL ACE Flow Files (*.aceflow)", options=options
        )
        if file_name:
            self.load_from_json(file_name)

    # def save_values(self):
    #     """Save values from the widgets (implement your logic here)."""
    #     self.process_widget_values("Save")

    # def load_from_json(self, file_path: str):
    #     """Load settings from a JSON file and update the UI."""
    #     try:
    #         with open(file_path, "r") as file:
    #             loaded_data = json.load(file)
    #
    #         # Extract metadata and user input pairs
    #         self.metadata = loaded_data.get("metadata", {})
    #         self.user_input_pairs = loaded_data.get("user_input_pairs", {})
    #
    #         # Update the last_loaded field
    #         self.metadata["last_loaded"] = str(datetime.now())
    #
    #         # List of expected widget names
    #         expected_fields = set(self.widgets.keys())
    #
    #         # Check for unexpected fields
    #         for name in self.user_input_pairs.keys():
    #             if name not in expected_fields:
    #                 error_message = (
    #                     f"Warning: Unexpected field '{name}' found in loaded data. "
    #                     "Was the data saved with an older version of MIRACL? "
    #                     f"You could try to delete '{name}' to load the rest of the data."
    #                 )
    #                 QMessageBox.warning(self, "Unexpected Field", error_message)
    #                 return  # Exit the function to avoid further processing
    #
    #         # Update the UI with loaded values
    #         for name, value in self.user_input_pairs.items():
    #             widget = self.widgets.get(name)
    #             if widget:
    #                 self.update_widget_value(widget, value)
    #
    #         # Save the updated metadata back to the file
    #         loaded_data["metadata"] = self.metadata
    #         with open(file_path, "w") as file:
    #             json.dump(loaded_data, file, indent=4)
    #
    #         QMessageBox.information(
    #             self, "Success", f"Settings loaded from {file_path}"
    #         )
    #
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"An error occurred while loading: {e}")

    def load_from_json(self, file_path: str):
        """Load settings from a JSON file and update the UI."""
        try:
            with open(file_path, "r") as file:
                loaded_data = json.load(file)

            # Extract metadata and user input pairs
            self.metadata = loaded_data.get("metadata", {})
            self.user_input_pairs = loaded_data.get("user_input_pairs", {})

            # Update the last_loaded field
            self.metadata["last_loaded"] = str(datetime.now())

            # List of expected widget names
            expected_fields = set(self.widgets.keys())

            # Check for unexpected fields
            for name in self.user_input_pairs.keys():
                if name not in expected_fields:
                    error_message = (
                        f"Warning: Unexpected field '{name}' found in loaded data. "
                        "Was the data saved with an older version of MIRACL? "
                        f"You could try to delete '{name}' to load the rest of the data."
                    )
                    print(error_message)
                    QMessageBox.warning(self, "Unexpected Field", error_message)
                    return  # Exit the function to avoid further processing

            # Update the UI with loaded values using the stored widgets
            for name, value in self.user_input_pairs.items():
                widget = self.widgets.get(name)
                if widget:
                    self.update_widget_value(widget, value)

            # Save the updated metadata back to the file
            loaded_data["metadata"] = self.metadata
            with open(file_path, "w") as file:
                json.dump(loaded_data, file, indent=4)

            QMessageBox.information(
                self, "Success", f"Settings loaded from {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while loading: {e}")

    def update_widget_value(self, widget, value):
        """Update the widget with the given value."""
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value)
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(value)

    def save_values(self, s_title, s_default, s_file_type):
        """Open a dialog to save values to a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(
            self,
            s_title,
            s_default,
            s_file_type,
            options=options,
        )
        if fileName:
            if not fileName.endswith(".aceflow"):
                fileName += ".aceflow"
            fileName = fileName.lower().replace(" ", "_")

            self.save_to_json(fileName)

    def get_settings_data(self) -> dict:
        """Gather data from widgets to prepare for saving."""
        data = {}
        for name, widget in self.widgets.items():
            if isinstance(widget, QSpinBox):
                data[name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                data[name] = widget.value()
            elif isinstance(widget, QComboBox):
                data[name] = widget.currentText()
        return data

    def save_to_json(self, file_name: str):
        """Save settings to a JSON file."""
        user_input_pairs = self.get_settings_data()
        metadata = {
            "uuid": str(uuid4()),
            "module_name": "ace",
            "last_saved": str(datetime.now()),
            "last_loaded": None,
        }
        data_to_save = {
            "metadata": metadata,
            "user_input_pairs": user_input_pairs,
        }
        try:
            json_data = json.dumps(data_to_save, indent=4)
            with open(file_name, "w") as file:
                file.write(json_data)
            QMessageBox.information(self, "Success", f"Settings saved to {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving: {e}")

    def process_widget_values(self, action: str):
        """Process the values of the widgets based on the action."""
        for name, widget in self.widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                print(f"{action} {name}: {value}")
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
                print(f"{action} {name}: {value}")

    def confirm_reset(self):
        """Show a confirmation dialog before resetting values."""
        # Create the QMessageBox
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setText("Are you sure you want to reset?")
        msg_box.setWindowTitle("Confirm Reset")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Cancel)

        # Execute the message box and check the response
        response = msg_box.exec_()

        if response == QMessageBox.Yes:
            self.reset_values()

    # def reset_values(self):
    #     """Reset values in the widgets to their default values."""
    #     for name, widget in self.widgets.items():
    #         miracl_obj = self.get_miracl_obj_by_name(name)
    #         if miracl_obj:
    #             if isinstance(widget, QSpinBox):
    #                 widget.setValue(miracl_obj.obj_default)
    #             elif isinstance(widget, QDoubleSpinBox):
    #                 widget.setValue(miracl_obj.obj_default)
    #             elif isinstance(widget, QComboBox):
    #                 widget.setCurrentText(miracl_obj.obj_default)

    def reset_values(self):
        """Reset values in the widgets to their default values."""
        for name, widget in self.widgets.items():
            miracl_obj = self.get_miracl_obj_by_name(name)
            if miracl_obj:
                if isinstance(widget, QSpinBox):
                    widget.setValue(miracl_obj.obj_default)
                elif isinstance(widget, QDoubleSpinBox):
                    widget.setValue(miracl_obj.obj_default)
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(miracl_obj.obj_default)

    def get_miracl_obj_by_name(self, name: str) -> MiraclObj:
        """Retrieve the MiraclObj associated with the given widget name."""
        for obj in [seg_ace.model_type, seg_ace.nr_workers]:
            if obj.flow["ace"]["cli_l_flag"] == name:
                return obj
        raise ValueError(f"No MiraclObj found for widget name: {name}")


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
