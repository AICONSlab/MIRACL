import sys
from typing import Any, Dict
from pydantic import BaseModel, Field, ValidationError, constr
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QLabel,
)
from PyQt5.QtCore import pyqtSignal, QObject


# Define constants for widget types
class WidgetType:
    LINE_EDIT = "line_edit"
    SPIN_BOX = "spin_box"
    DOUBLE_SPIN_BOX = "double_spin_box"


# Define the Pydantic model for user input
# This model describes the structure of the data and includes widget information
class UserInput(BaseModel):
    # The name field is now required and must not be an empty string
    # constr(min_length=1) ensures that the string is not empty
    name: constr(min_length=1) = Field(
        ..., title="Name", widget_type=WidgetType.LINE_EDIT
    )
    age: int = Field(..., title="Age", ge=0, widget_type=WidgetType.SPIN_BOX)
    height: float = Field(
        ..., title="Height", ge=0, widget_type=WidgetType.DOUBLE_SPIN_BOX
    )


# This class represents a dynamic widget that can adapt to different field types
class DynamicWidget(QObject):
    # Signal emitted when the widget's value changes
    value_changed = pyqtSignal(object)

    def __init__(self, field_name: str, field: Field, parent: QWidget):
        super().__init__()
        self.field_name = field_name  # Name of the field this widget represents
        self.field = field  # Pydantic Field object containing field metadata
        self.parent = parent  # Parent widget
        self.widget = self.create_widget()  # Create the actual Qt widget

    def create_widget(self):
        # Determine the widget type from the field's metadata
        widget_type = self.field.json_schema_extra.get(
            "widget_type", WidgetType.LINE_EDIT
        )

        # Create the appropriate widget based on the widget_type
        if widget_type == WidgetType.LINE_EDIT:
            widget = QLineEdit(self.parent)
            widget.textChanged.connect(self.on_value_changed)
        elif widget_type == WidgetType.SPIN_BOX:
            widget = QSpinBox(self.parent)
            widget.valueChanged.connect(self.on_value_changed)
        elif widget_type == WidgetType.DOUBLE_SPIN_BOX:
            widget = QDoubleSpinBox(self.parent)
            widget.valueChanged.connect(self.on_value_changed)
        else:
            raise ValueError(f"Unsupported widget type: {widget_type}")

        return widget

    def on_value_changed(self, value):
        # Emit the value_changed signal when the widget's value changes
        self.value_changed.emit(value)

    def get_value(self):
        # Retrieve the current value from the widget
        if isinstance(self.widget, QLineEdit):
            return self.widget.text()
        elif isinstance(self.widget, (QSpinBox, QDoubleSpinBox)):
            return self.widget.value()

    def set_value(self, value):
        # Set a new value for the widget
        if isinstance(self.widget, QLineEdit):
            self.widget.setText(str(value))
        elif isinstance(self.widget, (QSpinBox, QDoubleSpinBox)):
            self.widget.setValue(value)


# Main window of the application
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Widget Example")
        self.setGeometry(100, 100, 400, 300)

        # Create a central widget and set the main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Dictionary to store the dynamic widgets
        self.widgets: Dict[str, DynamicWidget] = {}

        # Create widgets based on the Pydantic model
        self.create_widgets(main_layout)

        # Create a "Run" button
        button_layout = QHBoxLayout()
        run_button = QPushButton("Run", self)
        run_button.clicked.connect(self.run_action)
        button_layout.addWidget(run_button)
        main_layout.addLayout(button_layout)

        # Label to display validation status
        self.status_label = QLabel("", self)
        main_layout.addWidget(self.status_label)

    def create_widgets(self, layout):
        # Iterate through the fields in the UserInput model
        for field_name, field in UserInput.model_fields.items():
            # Create a label for the field
            label = QLabel(field.title, self)
            layout.addWidget(label)

            # Create a dynamic widget for the field
            dynamic_widget = DynamicWidget(field_name, field, self)
            # Connect the widget's value_changed signal to the validation method
            dynamic_widget.value_changed.connect(self.on_widget_value_changed)
            layout.addWidget(dynamic_widget.widget)

            # Store the dynamic widget in the dictionary
            self.widgets[field_name] = dynamic_widget

    def on_widget_value_changed(self, value):
        # Validate the input whenever any widget's value changes
        self.validate_input()

    def validate_input(self):
        # Collect the current values from all widgets
        data = {name: widget.get_value() for name, widget in self.widgets.items()}
        try:
            # Attempt to create a UserInput instance with the collected data
            # This will trigger Pydantic's validation
            user_input = UserInput(**data)
            self.status_label.setText("Valid input")
            self.status_label.setStyleSheet("color: green;")
            print(f"Valid input: {user_input}")
            return user_input
        except ValidationError as e:
            # If validation fails, display the error
            error_msg = str(e)
            self.status_label.setText(f"Validation Error: {error_msg}")
            self.status_label.setStyleSheet("color: red;")
            print(f"Validation Error: {e}")
            return None

    def run_action(self):
        # This method is called when the "Run" button is clicked
        user_input = self.validate_input()
        if user_input:
            print(f"Running with input: {user_input}")
            # Here you can use the validated user_input in your script
            # For example: process_data(user_input)


# Main application entry point
def main():
    # Create the Qt application
    app = QApplication(sys.argv)
    # Create and show the main window
    main_window = MainWindow()
    main_window.show()
    # Start the event loop
    sys.exit(app.exec_())


# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
