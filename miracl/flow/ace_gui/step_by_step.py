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
)
from PyQt5.QtCore import pyqtSignal
from widget_factory import WidgetFactory
from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    WidgetType,
    ArgumentType,
)
from miracl.system.objs.objs_seg import SegAceObjs as seg_ace


class MainWindow(QMainWindow):
    value_changed = pyqtSignal(str, object)  # Signal to emit on value change

    def __init__(self):
        super().__init__()
        self.window_title = "ACE flow"
        self.setWindowTitle(self.window_title)
        self.setGeometry(100, 100, 720, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Dictionary to store widget references
        self.widgets = {}

        # Add the widgets to the main layout
        first_section = WidgetFactory.create_widgets_from_objects(
            [
                seg_ace.model_type,
                seg_ace.nr_workers,
            ]
        )
        self.main_layout.addWidget(first_section)

        # Store widgets in the dictionary
        self.store_widgets(first_section)

        # IO Buttons
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


