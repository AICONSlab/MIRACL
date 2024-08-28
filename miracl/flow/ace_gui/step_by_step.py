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
    QLineEdit,
)
from PyQt5.QtCore import pyqtSignal
from gui_factory import WidgetFactory, SectionLabel
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
)
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_seg import SegVoxObjs as seg_vox
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace
from miracl.system.objs.objs_reg import RegClarAllenObjs as reg_clar_allen
from miracl.system.objs.objs_reg import RegWarpClarObjs as reg_warp_clar
from miracl.system.objs.objs_conv import ConvTiffNiiObjs as conv_tiff_nii
import json
from uuid import uuid4
from datetime import datetime
from miracl import miracl_logger

logger = miracl_logger.logger


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

        self.main_layout = QVBoxLayout(self.central_widget)

        section, self.obj_dict = WidgetFactory.create_widgets_from_objects(
            [
                SectionLabel("Single or multi method arguments"),
                flow_ace.single,
                SectionLabel("Required arguments"),
                seg_ace.out_dir,
                seg_ace.model_type,
                SectionLabel("Useful/important arguments"),
                seg_ace.gpu_index,
                conv_tiff_nii.down,
                reg_clar_allen.voxel_size,
                seg_vox.downsample,
                reg_warp_clar.voxel_size,
            ],
            self,
        )

        self.main_layout.addWidget(section)

        # Store widgets in the dictionary
        self.widgets = {}
        self.store_widgets(self.central_widget)

        self.value_changed.connect(self.on_value_changed)

        self.add_io_buttons()

    def add_io_buttons(self):
        """Add IO buttons to the layout."""
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
        io_load_button.clicked.connect(
            self.load_values,
        )
        io_save_button.clicked.connect(
            lambda: self.save_values(
                "Save File",
                "",
                "MIRACL ACE Flow Files (*.aceflow)",
            )
        )
        io_reset_button.clicked.connect(self.confirm_reset)

    def store_widgets(self, parent: QWidget):
        for child in parent.findChildren(QWidget):
            object_name = child.objectName()

            # Skip processing for internal QLineEdit widgets
            if isinstance(child, QLineEdit) and object_name.startswith("qt_"):
                continue

            # Log the object name only if it is not empty
            if object_name:
                logger.debug(f"Processing widget: {object_name}")  # Debug print

                # Check if the child is a relevant widget type
                if isinstance(child, (QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit)):
                    self.widgets[object_name] = child  # Add to the widgets dictionary

                    # Connect signals to the slot based on widget type
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
                    elif isinstance(child, QLineEdit):
                        child.textChanged.connect(
                            lambda text, name=object_name: self.value_changed.emit(
                                name, text
                            )
                        )

    def on_value_changed(self, name, value):
        """Handle widget value changes."""
        logger.debug(f"Value changed in {name}: {value}")

    def load_values(self):
        """Open a dialog to load values from a JSON file."""
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Load File", "", "MIRACL ACE Flow Files (*.aceflow)", options=options
        )
        if file_name:
            self.load_from_json(file_name)

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

            # Check for missing fields
            missing_fields = expected_fields - self.user_input_pairs.keys()
            if missing_fields:
                error_message = (
                    f"Warning: Missing field(s) in loaded data: {', '.join(missing_fields)}. "
                    "Field(s) will not be updated."
                )
                print(error_message)
                QMessageBox.warning(self, "Missing Fields", error_message)

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

    def reset_values(self):
        """Reset values in the widgets to their default values.

        Uses the miracl_objs dictionary to access default values from MiraclObj instances.
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


def main():
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
