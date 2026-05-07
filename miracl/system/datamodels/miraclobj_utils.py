"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Currently just one convenience function to hopefully improve the user experience.
"""

from argparse import ArgumentTypeError
from typing import Any


def parser_true_or_false(arg: Any) -> bool:
    """
    Convert a string argument to a boolean value.

    Accepts "true", "t" (case-insensitive) as True;
    "false", "f" as False. Raises an error for anything else.

    Attributes:
        arg: Input string to convert, most likely a str from CLI.

    Raises:
        ArgumentTypeError: If input is not one of the accepted values.
    """
    if isinstance(arg, bool):
        return arg

    upper_arg = str(arg).upper()
    if upper_arg in ("TRUE", "T"):
        return True
    elif upper_arg in ("FALSE", "F"):
        return False
    else:
        raise ArgumentTypeError(
            "Argument must be either 'True'/'true'/'T'/'t' or 'False'/'false'/'F'/'f'"
        )
