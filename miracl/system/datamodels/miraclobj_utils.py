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
