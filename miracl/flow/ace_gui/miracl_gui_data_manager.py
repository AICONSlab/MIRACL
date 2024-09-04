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

    def __init__(
        self, widgets: Dict[str, QWidget], miracl_obj_dict: Dict[str, MiraclObj]
    ):
        """Initialize the DataManager with widgets and their corresponding objects."""
        self.widgets = widgets
        self.miracl_obj_dict = miracl_obj_dict

    def load_values(self, l_title: str, l_default: str, l_file_type: str):
        """Open a dialog to load values from a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            # None, "Load File", "", "MIRACL ACE Flow Files (*.aceflow)", options=options
            None,
            l_title,
            l_default,
            l_file_type,
            options=options,
        )
        if file_name:
            self.load_from_json(file_name)

    def load_from_json(self, file_path: str):
        try:
            # Load existing data to retain metadata
            with open(file_path, "r") as file:
                loaded_data = json.load(file)

            # Update the last_loaded field in the metadata
            if "metadata" in loaded_data:
                loaded_data["metadata"]["last_loaded"] = str(datetime.now())

            loaded_user_inputs = loaded_data.get("user_input_pairs", {})
            valid_keys = set(self.miracl_obj_dict.keys())
            cleaned_user_inputs = {
                k: v for k, v in loaded_user_inputs.items() if k in valid_keys
            }

            validation_errors = []  # List to collect validation error messages
            valid_updates = {}  # Dictionary to hold valid updates

            for name, value in cleaned_user_inputs.items():
                if name in self.miracl_obj_dict:
                    existing_obj = self.miracl_obj_dict[name]

                    # Validate the loaded value against the expected type
                    expected_type = existing_obj.cli_obj_type.python_type

                    # Check if the loaded value is of the expected type
                    if not isinstance(value, expected_type):
                        error_message = f"Invalid type for {name}: expected {expected_type.__name__}, got {type(value).__name__}"
                        validation_errors.append(
                            error_message
                        )  # Collect the error message
                        print(error_message)  # Print the error to the terminal
                    else:
                        valid_updates[name] = value  # Store valid updates

            # Check if there were any validation errors
            if validation_errors:
                QMessageBox.warning(
                    None, "Validation Errors", "\n".join(validation_errors)
                )  # Show all errors in one message box
            else:
                # If there are no validation errors, update the GUI with valid values
                for name, value in valid_updates.items():
                    widget = self.widgets.get(name)
                    if widget:
                        self.update_widget_value(
                            widget, value
                        )  # Set the value directly on the widget

                # Save the updated metadata back to the JSON file
                with open(file_path, "w") as file:
                    json.dump(loaded_data, file, indent=4)

                QMessageBox.information(
                    None, "Success", f"Settings loaded from {file_path}"
                )

        except Exception as e:
            QMessageBox.critical(None, "Error", f"An error occurred while loading: {e}")

    def update_widget_value(self, widget, value):
        """Update the widget with the given value, converting types as necessary."""
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            # Convert to float or int based on the widget type
            if isinstance(value, (int, float)):
                widget.setValue(value)
            else:
                try:
                    # Attempt to convert to float (or int if needed)
                    widget.setValue(
                        float(value)
                    )  # You can change this to int(value) if you prefer
                except ValueError:
                    print(f"Warning: Unable to convert value for {widget}: {value}")

        elif isinstance(widget, QComboBox):
            # Convert to string for combo boxes
            if isinstance(value, str):
                widget.setCurrentText(value)
            else:
                widget.setCurrentText(str(value))  # Convert to string if not already

        elif isinstance(widget, QLineEdit):
            # Convert to string for line edits
            widget.setText(str(value))  # Always convert to string

        else:
            print(f"Unhandled widget type for {widget}: {type(widget)}")

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

    def save_to_json(self, file_name: str):
        """Save settings to a JSON file."""
        user_input_pairs = {}

        # Define a set of keys to exclude from saving
        excluded_keys = {"qt_spinbox_lineedit"}

        # Pull current values from the widgets and convert accordingly
        for name, widget in self.widgets.items():
            if name in excluded_keys:
                continue  # Skip excluded keys

            if isinstance(widget, QSpinBox):
                user_input_pairs[name] = widget.value()  # Get integer value
            elif isinstance(widget, QDoubleSpinBox):
                user_input_pairs[name] = widget.value()  # Get float value
            elif isinstance(widget, QComboBox):
                user_input_pairs[name] = widget.currentText()  # Get string value
            elif isinstance(widget, QLineEdit):
                user_input_pairs[name] = widget.text()  # Get string value

        # Validate and convert values against expected types
        for name, value in user_input_pairs.items():
            if name in self.miracl_obj_dict:
                expected_type = self.miracl_obj_dict[name].cli_obj_type.python_type

                # Convert the value to the expected type if necessary
                if isinstance(value, str) and expected_type in (int, float):
                    try:
                        if expected_type == int:
                            value = int(value)  # Convert to int
                        elif expected_type == float:
                            value = float(value)  # Convert to float
                    except ValueError:
                        raise ValueError(
                            f"Invalid value for {name}: cannot convert '{value}' to {expected_type.__name__}"
                        )

                # Validate the converted value
                if not isinstance(value, expected_type):
                    raise ValueError(
                        f"Invalid type for {name}: expected {expected_type.__name__}, got {type(value).__name__}"
                    )

                # Update the user_input_pairs with the converted value
                user_input_pairs[name] = value

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

    # def process_widget_values(self, action: str):
    #     """Process the values of the widgets based on the action."""
    #     for name, widget in self.widgets.items():
    #         if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
    #             value = widget.value()
    #             print(f"{action} {name}: {value}")
    #         elif isinstance(widget, QComboBox):
    #             value = widget.currentText()
    #             print(f"{action} {name}: {value}")

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

        Uses the miracl_obj_dict dictionary to access default values from MiraclObj instances.
        If obj_default is not present for string-based widgets, sets the widget to an empty string.
        """
        print("Resetting values...")  # Indicate the start of the function
        logger.debug(
            f"Widgets dictionary: {self.widgets}"
        )  # Print the entire widgets dictionary
        logger.debug(
            f"Object dictionary: {self.miracl_obj_dict}"
        )  # Print the entire object dictionary

        for name, widget in self.widgets.items():
            logger.debug(
                f"Widget Name: {name}, Widget Type: {type(widget)}"
            )  # Print widget details

            miracl_obj = self.miracl_obj_dict.get(name)
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
