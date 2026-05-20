"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Enums required by modules and workflows.
"""

#######################################################################################
# IMPORTS
#######################################################################################
from enum import Enum
from miracl.api.utils import parser_true_or_false

#######################################################################################
# CLI
#######################################################################################


# TODO: This should eventually be the only place where flows will have to be
# added/defined. I should map out the current way to add/define flows in a dev guide.
# FIX: Or should it? Is this actually the best place for the flow and module enums?
# This is very important since they add/define the workflows. Consider moving them to
# their own file.
class ModuleType(str, Enum):
    """
    Module execution context within the MIRACL system.

    Distinguishes between standalone CLI/GUI execution and workflow-based execution.

    Attributes:
        MODULE: Standalone module execution via CLI or GUI.
        FLOW_ACE: Module executed as part of the ACE workflow.
        FLOW_MAPL3: Module executed as part of the MAPL3 workflow.
        FLOW_CONV_REG: Module executed as part othe Conversion/Registration workflow.

    Note:
        All new modules or workflows must be registered here before use.
    """

    MODULE = "module"
    FLOW_ACE = "ace"
    FLOW_MAPL3 = "mapl3"
    FLOW_CONV_REG = "conv_reg"


class FlagMapMode(str, Enum):
    """
    Used in the module config to automatically build flag maps between workflow and
    the parser of the actual script that is being called. This can only be used if
    the module flags in the objects match the flags of the parser from the script. It
    creates a mapping between the object's module flags and the respective workflow
    flags.
    """

    AUTOGENERATE_LONG = "autogenerate_long"
    AUTOGENERATE_SHORT = "autogenerate_short"


class ArgumentType(str, Enum):
    """
    Data types supported by MIRACL command-line and GUI arguments.

    Used by the MIRACLang (workflow DSL) and validation layer to determine how to
    parse and validate user input. Each type has two associated conversion strategies:

    - :attr:`python_type`: The resulting Python type after parsing.
    - :attr:`cli_parser`: The function used to convert CLI string input.

    Example:
        >>> arg_type = ArgumentType.INTEGER
        >>> arg_type.python_type
        <class 'int'>
        >>> arg_type.cli_parser("42")
        42

        >>> arg_type = ArgumentType.BOOLEAN
        >>> arg_type.python_type
        <class 'bool'>
        >>> arg_type.cli_parser("false")
        False
    """

    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    # FIX: BOOLEAN enum should be fully replaced by CUSTOM_BOOL.
    BOOLEAN = "bool"
    LIST = "list"
    CUSTOM_BOOL = "custom_bool"

    @property
    def python_type(self):
        """
        The Python type resulting from parsing an argument of this type.

        Used by Pydantic to validate values and generate schemas.
        """

        return {
            ArgumentType.STRING: str,
            ArgumentType.INTEGER: int,
            ArgumentType.FLOAT: float,
            ArgumentType.BOOLEAN: bool,
            ArgumentType.CUSTOM_BOOL: bool,
            ArgumentType.LIST: list,
        }[self]

    @property
    def cli_parser(self):
        """
        The function used to parse string input from the CLI.

        For boolean types, this uses :func:`~miracl.api.utils.parser_true_or_false`
        to handle string values like ``"true"`` and ``"false"`` correctly.
        """

        parser_map = {
            ArgumentType.STRING: str,
            ArgumentType.INTEGER: int,
            ArgumentType.FLOAT: float,
            ArgumentType.BOOLEAN: parser_true_or_false,
            ArgumentType.CUSTOM_BOOL: parser_true_or_false,
            ArgumentType.LIST: list,
        }
        return parser_map[self]


class ArgumentAction(str, Enum):
    """
    Argparse action types available for CLI argument parsing.

    Maps directly to argparse's built-in actions. See :mod:`argparse`
    documentation for detailed behavior of each action.

    Attributes:
        STORE: Store the associated value (default).
        STORE_CONST: Store a constant value.
        STORE_TRUE: Store ``True`` when the flag is present.
        STORE_FALSE: Store ``False`` when the flag is present.
        APPEND: Append this value to a list.
        APPEND_CONST: Append a constant to a list.
        COUNT: Count occurrences of this flag.
        HELP: Show the help message and exit.
        VERSION: Show the version and exit.
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


#######################################################################################
# GUI
#######################################################################################


class WidgetType(str, Enum):
    """
    GUI widget types for argument input to the PyQt frontend.

    Each enum value maps to a specific Qt widget for rendering the argument.

    Attributes:
        LINE_EDIT: Single-line text input (:class:`PyQt5.QtWidgets.QLineEdit`).
        SPINBOX: Integer input with up/down controls (:class:`PyQt5.QtWidgets.QSpinBox`).
        DOUBLE_SPINBOX: Floating-point input (:class:`PyQt5.QtWidgets.QDoubleSpinBox`).
        NULLABLE_DOUBLE_SPINBOX: Optional float with checkbox (:class:`PyQt5.QtWidgets.QDoubleSpinBox`).
            Returns 'None' if unchecked, int value when checked.
        COMBO_BOX: Dropdown selection (:class:`PyQt5.QtWidgets.QComboBox`).
        PATH_INPUT: File or directory path picker (custom widget).
    """

    LINE_EDIT = "LINE_EDIT"
    SPINBOX = "SPINBOX"
    DOUBLE_SPINBOX = "DOUBLE_SPINBOX"
    NULLABLE_DOUBLE_SPINBOX = "NULLABLE_DOUBLE_SPINBOX"
    COMBO_BOX = "COMBO_BOX"
    PATH_INPUT = "PATH_INPUT"
    MULTI_LINE_EDIT = "MULTI_LINE_EDIT"


class InputRestrictionType(str, Enum):
    """Input restrictions for GUI text fields.

    Defines the character classes or formats allowed in text-based GUI widgets.
    These restrictions are enforced by the frontend to provide immediate
    user feedback before submission.

    Attributes:
        STR: No restrictions.
        STRCON: Constrained string with custom validation.
        ALPHANUMERIC: Letters and digits only.
        INTEGERS_ONLY: Whole numbers only.
        FLOATS_ONLY: Numeric values including decimals.
    """

    STR = "str"
    STRCON = "strcon"
    ALPHANUMERIC = "alphanumeric"
    INTEGERS_ONLY = "INTEGERS_ONLY"
    FLOATS_ONLY = "FLOATS_ONLY"
