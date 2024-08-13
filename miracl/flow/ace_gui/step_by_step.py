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
)
from PyQt5.QtCore import pyqtSignal
from gui_factory import WidgetFactory, SectionLabel
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
)
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace
from miracl.system.objs.objs_flow import FlowAceObjs as flow_ace


class MainWindow(QMainWindow):
    value_changed = pyqtSignal(str, object)  # Signal to emit on value change

    def __init__(self):
        super().__init__()
        self.window_title = "ACE flow"
        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # self.main_layout = QVBoxLayout()
        # self.central_widget.setLayout(self.main_layout)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Dictionary to store widget references
        # self.widgets = {}

        # # Add the widgets to the main layout
        # test = WidgetFactory.create_widgets_from_objects(
        #     [
        #         seg_ace.model_type,
        #     ],
        #     self,
        # )
        # self.main_layout.addWidget(test)
        #
        # single_multi_method_args_section = WidgetFactory.create_widgets_from_objects(
        #     [
        #         seg_ace.model_type,
        #         seg_ace.nr_workers,
        #     ],
        #     self,
        # )
        # self.main_layout.addWidget(single_multi_method_args_section)
        #
        # required_args_section = WidgetFactory.create_widgets_from_objects(
        #     [
        #         seg_ace.out_dir,
        #         seg_ace.model_type,
        #         seg_ace.nr_workers,
        #     ],
        #     self,
        # )
        # self.main_layout.addWidget(required_args_section)
        section = WidgetFactory.create_widgets_from_objects(
            [
                SectionLabel("First Section"),
                seg_ace.model_type,
                seg_ace.nr_workers,
                SectionLabel("Second Section"),
                seg_ace.out_dir,
            ],
            self,
        )

        self.main_layout.addWidget(section)

        # Store widgets in the dictionary
        self.widgets = {}
        self.store_widgets(self.central_widget)

        self.value_changed.connect(self.on_value_changed)

        self.add_io_buttons()

        # # IO Buttons
        # io_widget = QWidget()
        # io_layout = QHBoxLayout(io_widget)
        # io_load_button = QPushButton("Load")
        # io_layout.addWidget(io_load_button)
        # io_save_button = QPushButton("Save")
        # io_layout.addWidget(io_save_button)
        # io_reset_button = QPushButton("Reset")
        # io_layout.addWidget(io_reset_button)
        # io_layout.setContentsMargins(0, 0, 0, 0)
        # self.main_layout.addWidget(io_widget)
        #
        # # Connect button signals to slots
        # io_load_button.clicked.connect(self.load_values)
        # io_save_button.clicked.connect(self.save_values)
        # io_reset_button.clicked.connect(self.reset_values)
        #
        # # Connect the custom signal to a slot
        # self.value_changed.connect(self.on_value_changed)

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
        io_load_button.clicked.connect(self.load_values)
        io_save_button.clicked.connect(self.save_values)
        io_reset_button.clicked.connect(self.reset_values)

    def store_widgets(self, parent: QWidget):
        """Store the widgets in the dictionary using their object names."""
        for child in parent.findChildren(QWidget):
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

    def load_values(self):
        """Load values from the widgets."""
        self.process_widget_values("Load")

    def save_values(self):
        """Save values from the widgets (implement your logic here)."""
        self.process_widget_values("Save")

    def process_widget_values(self, action: str):
        """Process the values of the widgets based on the action."""
        for name, widget in self.widgets.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                print(f"{action} {name}: {value}")
            elif isinstance(widget, QComboBox):
                value = widget.currentText()
                print(f"{action} {name}: {value}")

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
