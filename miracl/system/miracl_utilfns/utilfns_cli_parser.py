from __future__ import annotations
from argparse import ArgumentTypeError


def str2bool(v: object) -> bool:
    """
    Convert a value to a boolean.
    """
    if isinstance(v, bool):
        return v
    elif v == "True":
        return True
    elif v == "False":
        return False
    else:
        raise ArgumentTypeError("Boolean value expected.")


def none_or_float(value: str) -> float | None:
    """
    Convert a string to a float or None.
    """
    if value.lower() == "none":
        return None
    try:
        return float(value)
    except ValueError:
        raise ArgumentTypeError(f"{value} must be a float or 'None'")


def none_or_str(value: str) -> str | None:
    """
    Convert a string to itself or None.
    """
    if value.lower() == "none":
        return None
    return value
