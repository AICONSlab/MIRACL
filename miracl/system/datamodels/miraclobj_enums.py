from enum import Enum
from typing_extensions import Literal
from argparse import ArgumentTypeError


def parser_true_or_false(arg: str) -> bool:
    """
    Convert a string argument to a boolean value.

    Accepts "true", "t" (case-insensitive) as True;
    "false", "f" as False. Raises an error for anything else.

    Args:
        arg (str): Input string to convert.

    Returns:
        bool: True or False

    Raises:
        ArgumentTypeError: If input is not one of the accepted values.
    """
    upper_arg = str(arg).upper()
    if upper_arg in ("TRUE", "T"):
        return True
    elif upper_arg in ("FALSE", "F"):
        return False
    else:
        raise ArgumentTypeError("Argument must be either 'True'/'T' or 'False'/'F'")


# NOTE: This should eventually be the only place where flows will have to be added/defined
class ModuleType(str, Enum):
    """
    Enum representing the type of module the argument belongs to.

    Used to distinguish between standalone modules and modules that are part
    of a workflow (e.g., ACE, MAPL3).
    """

    MODULE = "module"
    FLOW_ACE = "ace"
    FLOW_MAPL3 = "mapl3"


class ArgumentType(str, Enum):
    """
    Enum representing supported data types for command-line arguments.

    These types are used for parsing input from CLI and GUI interfaces.
    The `python_type` property returns the Python type or callable corresponding
    to the enum value.
    """

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"
    CUSTOM_BOOL = "custom_bool"

    @property
    def python_type(self):
        """
        Return the Python type or conversion function associated with the argument type.

        For CUSTOM_BOOL, a custom parser is imported at runtime.
        """

        if self == ArgumentType.CUSTOM_BOOL:
            # # from miracl.system.datamodels.miraclobj_utils import (
            # from miracl.api.ext import (
            #     parser_true_or_false,
            # )  # local import to prevent circular imports

            return parser_true_or_false

        return {
            ArgumentType.STRING: str,
            ArgumentType.INTEGER: int,
            ArgumentType.FLOAT: float,
            ArgumentType.BOOLEAN: bool,
            ArgumentType.LIST: list,
        }[self]


class ArgumentAction(str, Enum):
    """
    Enum representing the available actions for argparse when parsing CLI arguments.

    Mirrors the choices accepted by argparse’s `action` parameter.
    """

    STORE = "store"
    STORE_CONST = "store_const"
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    APPEND = "append"
    APPEND_CONST = "append_const"
    COUNT = "count"
    HELP = "help"
    VERSION = "version"


# GUI


class WidgetType(str, Enum):
    """
    Enum specifying GUI widget types for argument input.

    Each widget maps to a specific Qt widget in the interface.
    """

    LINE_EDIT = "line_edit"  # Text input (QLineEdit)
    SPINBOX = "spinbox"  # Integer input (QSpinBox)
    DOUBLE_SPINBOX = "double_spinbox"  # Float input (QDoubleSpinBox)
    DROPDOWN = "dropdown"  # Multiple choice (QComboBox)
    PATH_INPUT = "path_input"  # Custom path input


class InputRestrictionType(str, Enum):
    """
    Enum for restricting text input in GUI text fields (e.g., QLineEdit).

    Defines allowed character classes or formats
    """

    STR = "str"
    STRCON = "strcon"
    ALPHANUMERIC = "alphanumeric"
    INT = "numeric"
