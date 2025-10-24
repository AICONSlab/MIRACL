def str2bool(v: object) -> bool:
    """
    Convert a value to a boolean.

    This function interprets string values "True" and "False" as their corresponding
    boolean types. If the input is already a boolean, it is returned unchanged.
    Any other value will raise an ArgumentTypeError.

    Parameters
    ----------
    v : object
        The value to convert. Can be a boolean or one of the strings "True" or "False".

    Returns
    -------
    bool
        The corresponding boolean value.

    Raises
    ------
    argparse.ArgumentTypeError
        If `v` is not a boolean or a string representation of one.
    """
    if isinstance(v, bool):
        return v
    elif v == "True":
        return True
    elif v == "False":
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def none_or_float(value):
    """
    Convert a string to a float or None.

    This function allows users to specify "None" (case-insensitive) to represent
    a `None` value. Otherwise, it attempts to convert the input to a float.
    If the conversion fails, an ArgumentTypeError is raised.

    Parameters
    ----------
    value : str
        The string to convert. Can be a numeric string or "None".

    Returns
    -------
    float or None
        The corresponding float value, or `None` if the input is "None".

    Raises
    ------
    argparse.ArgumentTypeError
        If `value` is neither "None" nor a valid float representation.
    """
    if value.lower() == "none":
        return None
    try:
        return float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} must be a float or 'None'")
