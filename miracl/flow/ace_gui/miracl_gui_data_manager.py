# Import PyQt reqs
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QDoubleSpinBox,
    QSpinBox,
)

# Import modules for reset/save/load functionality
import json
from datetime import datetime
from uuid import uuid4
from pathlib import Path


# Import Pydantic datamodel
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

# Import type annotations
from typing import Dict

# Import logger
from miracl import miracl_logger

logger = miracl_logger.logger


class DataManager:
    """
    A class to manage loading, saving, and resetting widget values.

    :ivar widgets: A dictionary of widget objects to manage.
    :vartype widgets: Dict[str, QWidget]
    :ivar obj_dict: A dictionary of MiraclObj instances for default values.
    :vartype obj_dict: Dict[str, MiraclObj]
    """

    def __init__(self, widgets: Dict[str, QWidget], obj_dict: Dict[str, MiraclObj]):
        """Initialize the DataManager with widgets and their corresponding objects."""
        self.widgets = widgets
        self.obj_dict = obj_dict

    def load_values(self):
        """Open a dialog to load values from a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            None, "Load File", "", "MIRACL ACE Flow Files (*.aceflow)", options=options
        )
        if file_name:
            self.load_from_json(file_name)

    def load_from_json(self, file_path: str):
        """Load settings from a JSON file and update the UI."""
        try:
            with open(file_path, "r") as file:
                loaded_data = json.load(file)

            # Extract metadata and user input pairs
            metadata = loaded_data.get("metadata", {})
            user_input_pairs = loaded_data.get("user_input_pairs", {})

            # Update the last_loaded field
            metadata["last_loaded"] = str(datetime.now())

            # List of expected widget names
            expected_fields = set(self.widgets.keys())

            # Check for unexpected fields
            for name in user_input_pairs.keys():
                if name not in expected_fields:
                    error_message = (
                        f"Warning: Unexpected field '{name}' found in loaded data. "
                        "Was the data saved with an older version of MIRACL? "
                        f"You could try to delete '{name}' to load the rest of the data."
                    )
                    print(error_message)
                    QMessageBox.warning(None, "Unexpected Field", error_message)
                    return  # Exit the function to avoid further processing

            # Check for missing fields
            missing_fields = expected_fields - user_input_pairs.keys()
            if missing_fields:
                error_message = (
                    f"Warning: Missing field(s) in loaded data: {', '.join(missing_fields)}. "
                    "Field(s) will not be updated."
                )
                print(error_message)
                QMessageBox.warning(None, "Missing Fields", error_message)

            # Update the UI with loaded values using the stored widgets
            for name, value in user_input_pairs.items():
                widget = self.widgets.get(name)
                if widget:
                    self.update_widget_value(widget, value)

            # Save the updated metadata back to the file
            loaded_data["metadata"] = metadata
            with open(file_path, "w") as file:
                json.dump(loaded_data, file, indent=4)

            QMessageBox.information(
                None, "Success", f"Settings loaded from {file_path}"
            )

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while loading: {e}")

    def update_widget_value(self, widget, value):
        """Update the widget with the given value."""
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value)
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        elif isinstance(widget, QLineEdit):
            widget.setText(value)

    def save_values(self, s_title: str, s_default: str, s_file_type: str):
        """Open a dialog to save values to a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            None,
            s_title,
            s_default,
            s_file_type,
            options=options,
        )
        if file_name:
            if not file_name.endswith(".aceflow"):
                file_name += ".aceflow"
            file_name = file_name.lower().replace(" ", "_")

            self.save_to_json(file_name)

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
            elif isinstance(widget, QLineEdit):
                data[name] = widget.text()
        return data

    def save_to_json(self, file_name: str):
        """Save settings to a JSON file."""
        user_input_pairs = self.get_settings_data()

        # Use pathlib to check if the file already exists
        file_path = Path(file_name)  # Create a Path object for the file
        metadata = {}

        if file_path.exists():  # Check if the file exists
            # Load existing data to retain the UUID
            with file_path.open("r") as file:
                existing_data = json.load(file)
                metadata = existing_data.get("metadata", {})
        else:
            # Generate a new UUID for new files
            metadata = {
                "uuid": str(uuid4()),
                "module_name": "ace",
                "last_saved": str(datetime.now()),
                "last_loaded": None,
            }

        # Update last saved time
        metadata["last_saved"] = str(datetime.now())

        data_to_save = {
            "metadata": metadata,
            "user_input_pairs": user_input_pairs,
        }

        try:
            json_data = json.dumps(data_to_save, indent=4)
            with file_path.open("w") as file:  # Use pathlib to open the file
                file.write(json_data)
            QMessageBox.information(None, "Success", f"Settings saved to {file_name}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while saving: {e}")

    # def save_to_json(self, file_name: str):
    #     """Save settings to a JSON file."""
    #     user_input_pairs = self.get_settings_data()
    #     metadata = {
    #         "uuid": str(uuid4()),
    #         "module_name": "ace",
    #         "last_saved": str(datetime.now()),
    #         "last_loaded": None,
    #     }
    #     data_to_save = {
    #         "metadata": metadata,
    #         "user_input_pairs": user_input_pairs,
    #     }
    #     try:
    #         json_data = json.dumps(data_to_save, indent=4)
    #         with open(file_name, "w") as file:
    #             file.write(json_data)
    #         QMessageBox.information(None, "Success", f"Settings saved to {file_name}")
    #     except Exception as e:
    #         QMessageBox.critical(None, "Error", f"An error occurred while saving: {e}")

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

    def reset_values(self):
        """Reset values in the widgets to their default values.

        Uses the obj_dict dictionary to access default values from MiraclObj instances.
        If obj_default is not present for string-based widgets, sets the widget to an empty string.
        """
        print("Resetting values...")  # Indicate the start of the function
        logger.debug(
            f"Widgets dictionary: {self.widgets}"
        )  # Print the entire widgets dictionary
        logger.debug(
            f"Object dictionary: {self.obj_dict}"
        )  # Print the entire object dictionary

        for name, widget in self.widgets.items():
            logger.debug(
                f"Widget Name: {name}, Widget Type: {type(widget)}"
            )  # Print widget details

            miracl_obj = self.obj_dict.get(name)
            if miracl_obj:
                if isinstance(widget, QSpinBox):
                    logger.debug(f"Resetting QSpinBox: {name}")
                    widget.setValue(miracl_obj.obj_default)
                elif isinstance(widget, QDoubleSpinBox):
                    logger.debug(f"Resetting QDoubleSpinBox: {name}")
                    widget.setValue(miracl_obj.obj_default)
                elif isinstance(widget, QComboBox):
                    logger.debug(f"Resetting QComboBox: {name}")
                    default_value = (
                        miracl_obj.obj_default
                        if hasattr(miracl_obj, "obj_default")
                        else ""
                    )
                    widget.setCurrentText(str(default_value))
                elif isinstance(widget, QLineEdit):
                    logger.debug(
                        f"Resetting QLineEdit: {name}"
                    )  # Debug print for QLineEdit
                    widget.clear()  # Clear current value
                    default_value = (
                        miracl_obj.obj_default
                        if hasattr(miracl_obj, "obj_default")
                        else ""
                    )
                    if default_value:  # If there is a default value, set it
                        widget.setText(str(default_value))
                else:
                    print(f"Unhandled widget type for {name}: {type(widget)}")
            else:
                print(f"No corresponding MiraclObj found for {name}")
