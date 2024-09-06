from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit
from miracl import miracl_logger

logger = miracl_logger.logger


# class WidgetObserver:
#     @staticmethod
#     def setup_change_detection(widgets, callback):
#         """Set up change detection for widgets."""
#         logger.debug(f"Setting up change detection for {len(widgets)} widgets")
#         for name, widget in widgets.items():
#             logger.debug(
#                 f"Setting up detection for widget: {name}, type: {type(widget)}"
#             )
#             if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
#                 widget.valueChanged.connect(
#                     lambda value, name=name: callback(name, value)
#                 )
#             elif isinstance(widget, QComboBox):
#                 widget.currentTextChanged.connect(
#                     lambda text, name=name: callback(name, text)
#                 )
#             elif isinstance(widget, QLineEdit):
#                 widget.textChanged.connect(lambda text, name=name: callback(name, text))
#             else:
#                 logger.warning(f"Unsupported widget type for {name}: {type(widget)}")


class WidgetObserver:
    @staticmethod
    def setup_change_detection(widgets, callback):
        """Set up change detection for widgets."""
        logger.debug(f"Setting up change detection for {len(widgets)} widgets")
        for name, widget in widgets.items():
            logger.debug(
                f"Setting up detection for widget: {name}, type: {type(widget)}"
            )
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.valueChanged.connect(
                    lambda value, name=name: callback(name, value)
                )
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(
                    lambda text, name=name: callback(name, text)
                )
            elif isinstance(widget, QLineEdit):
                widget.textChanged.connect(lambda text, name=name: callback(name, text))
            elif hasattr(
                widget, "inputs"
            ):  # Check if it's a container with QLineEdit inputs
                for input_field in widget.inputs:
                    input_field.textChanged.connect(
                        lambda text, name=name: callback(name, text)
                    )
            else:
                logger.warning(f"Unsupported widget type for {name}: {type(widget)}")
