import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFormLayout,
    QComboBox,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt5.QtCore import Qt
from pydantic import BaseModel
from typing import List, Dict, Any, Union


class ArgumentType:
    INTEGER = "integer"
    FLOAT = "float"


class WidgetType:
    MULTIPLE_CHOICE = "multiple_choice"
    SPINBOX = "spinbox"


class MiraclObj(BaseModel):
    id: str
    name: str
    tags: List[str]
    cli_s_flag: str
    cli_l_flag: str
    flow: Dict[str, Any]
    obj_default: Union[int, float]
    cli_choices: List[Union[int, float]]
    cli_obj_type: str
    cli_help: str
    gui_label: List[str]
    gui_group: Dict[str, str]
    gui_order: List[int]
    module: str
    module_group: str
    version_added: str
    widget_type: str
    min_value: Union[int, float] = 0
    max_value: Union[int, float] = 99
    increment: Union[int, float] = 1
    decimals: int = 2


class WidgetUtils:
    @staticmethod
    def create_indented_label(text, help_text):
        label = QLabel(text)
        label.setToolTip(help_text)
        return label

    @staticmethod
    def create_combo(choices):
        combo = QComboBox()
        combo.addItems(map(str, choices))
        return combo

    @staticmethod
    def create_multiple_choice(layout, lbl, lbl_help_text, choices, default_choice):
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        model = WidgetUtils.create_combo(choices)
        model.setCurrentText(str(default_choice))
        layout.addRow(label, model)
        return model

    @staticmethod
    def create_spinbox(min_value, max_value, input_type, increment, decimals):
        if input_type == ArgumentType.INTEGER:
            spinbox = QSpinBox()
            spinbox.setRange(int(min_value), int(max_value))
            spinbox.setSingleStep(int(increment))
        elif input_type == ArgumentType.FLOAT:
            spinbox = QDoubleSpinBox()
            spinbox.setRange(float(min_value), float(max_value))
            spinbox.setSingleStep(float(increment))
            spinbox.setDecimals(decimals)
        return spinbox

    @staticmethod
    def create_digit_spinbox(
        layout,
        lbl,
        lbl_help_text,
        default_value,
        min_value,
        max_value,
        input_type,
        increment,
        decimals,
    ):
        label = WidgetUtils.create_indented_label(lbl, lbl_help_text)
        spinbox = WidgetUtils.create_spinbox(
            min_value, max_value, input_type, increment, decimals
        )

        if input_type == ArgumentType.INTEGER:
            spinbox.setValue(int(default_value))
        elif input_type == ArgumentType.FLOAT:
            spinbox.setValue(float(default_value))

        layout.addRow(label, spinbox)
        return spinbox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_title = "ACE flow"
        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # IO Widget
        io_widget = QWidget()
        io_layout = QHBoxLayout(io_widget)
        io_load_button = QPushButton("Load")
        io_load_button.clicked.connect(self.load_button_clicked)
        io_layout.addWidget(io_load_button)
        io_save_button = QPushButton("Save")
        io_save_button.clicked.connect(self.save_button_clicked)
        io_layout.addWidget(io_save_button)
        io_reset_button = QPushButton("Reset")
        io_reset_button.clicked.connect(self.confirm_reset)
        io_layout.addWidget(io_reset_button)
        io_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(io_widget)

        # Help Button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.help_button_clicked)
        main_layout.addWidget(help_button)

        # Run Button
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_ace_cli)
        main_layout.addWidget(run_button)

        # Form Layout for Widgets
        self.form_layout = QFormLayout()
        main_layout.addLayout(self.form_layout)

        # Dictionary to store widgets
        self.widgets = {}

    def create_widgets_from_object(self, obj):
        if obj.widget_type == WidgetType.MULTIPLE_CHOICE:
            widget = WidgetUtils.create_multiple_choice(
                self.form_layout,
                obj.gui_label[0],
                obj.cli_help,
                obj.cli_choices,
                obj.obj_default,
            )
        elif obj.widget_type == WidgetType.SPINBOX:
            widget = WidgetUtils.create_digit_spinbox(
                self.form_layout,
                obj.gui_label[0],
                obj.cli_help,
                obj.obj_default,
                obj.min_value,
                obj.max_value,
                obj.cli_obj_type,
                obj.increment,
                obj.decimals,
            )
        else:
            raise ValueError(f"Unknown widget type: {obj.widget_type}")

        # Store the widget with a unique key (using the object's name)
        self.widgets[obj.name] = widget

    def get_widget_value(self, widget_name):
        widget = self.widgets.get(widget_name)
        if widget is None:
            raise KeyError(f"No widget found with name: {widget_name}")

        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        else:
            raise TypeError(f"Unsupported widget type: {type(widget)}")

    def get_all_values(self):
        return {name: self.get_widget_value(name) for name in self.widgets}

    def load_button_clicked(self):
        print("Load button clicked")

    def save_button_clicked(self):
        print("Save button clicked")

    def confirm_reset(self):
        print("Reset button clicked")

    def help_button_clicked(self):
        print("Help button clicked")

    def run_ace_cli(self):
        print("Run button clicked")
        # Example of how to use the get_all_values method
        all_values = self.get_all_values()
        print("Current widget values:")
        for name, value in all_values.items():
            print(f"{name}: {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()

    # Example objects
    voxel_size = MiraclObj(
        id="3894569b-1935-49fe-b9e0-e518b0bbd661",
        name="rca_voxel_size",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="v",
        cli_l_flag="voxel_size",
        flow={"ace": {"cli_s_flag": "rcav", "cli_l_flag": "rca_voxel_size"}},
        obj_default=10,
        cli_choices=[10, 25, 50],
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="labels voxel size/Resolution in um (default: %(default)s)",
        gui_label=["Labels voxel size (um)"],
        gui_group={"ace_flow": "main"},
        gui_order=[10],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        widget_type=WidgetType.MULTIPLE_CHOICE,
    )

    spinbox_example = MiraclObj(
        id="spinbox-example",
        name="spinbox_example",
        tags=["example"],
        cli_s_flag="s",
        cli_l_flag="spinbox",
        flow={},
        obj_default=5.5,
        cli_choices=[],
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="Example spinbox",
        gui_label=["Spinbox Example"],
        gui_group={},
        gui_order=[1],
        module="example",
        module_group="example",
        version_added="1.0.0",
        widget_type=WidgetType.SPINBOX,
        min_value=0,
        max_value=10,
        increment=0.1,
        decimals=1,
    )

    # Create widgets from Pydantic objects
    main_window.create_widgets_from_object(voxel_size)
    main_window.create_widgets_from_object(spinbox_example)

    main_window.show()
    sys.exit(app.exec_())
