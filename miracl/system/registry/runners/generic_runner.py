# # Keep as legacy reference in case of breakage
# import subprocess
# from typing import Optional, Dict
#
#
# def generic_runner(
#     script: str,
#     mapping: Dict[str, Optional[str]],
#     *,
#     flag_map: Optional[Dict[str, str]] = None,
#     execute: bool = False,
# ):
#     """A configurable runner that supports optional flag mapping and execution."""
#     flag_map = flag_map or {}
#     parts = [script]
#     for flag, value in mapping.items():
#         new_flag = flag_map.get(flag, flag)
#         # if isinstance(value, list):
#         #     value = " ".join(map(str, value))
#         # parts.append(f"{new_flag} {value}")
#         if isinstance(value, list):
#             # flatten any nested lists
#             flat_values = []
#             for v in value:
#                 if isinstance(v, list):
#                     flat_values.extend(v)
#                 else:
#                     flat_values.append(v)
#             parts.append(new_flag)
#             parts.extend(map(str, flat_values))
#         else:
#             parts.extend([new_flag, str(value)])
#
#     cmd_str = " ".join(map(str, parts))
#     print(f"Running: {cmd_str}")
#     if execute:
#         subprocess.run(cmd_str, shell=True, check=True)
#     return cmd_str

import subprocess
from typing import Optional, Dict, Any, Iterable, Tuple, Union, List

ValueType = Union[
    str, int, float, bool, None, List["ValueType"], Tuple["ValueType", ...]
]


def _flatten_list(
    values: Iterable[ValueType],
) -> List[Union[str, int, float, bool, None]]:
    """
    Recursively flatten a nested iterable (lists or tuples) into a single flat list.

    Args:
        values (Iterable): An iterable which may contain nested lists or tuples.

    Returns:
        list: A flat list containing all elements from the nested iterable.

    Notes:
        Strings are treated as atomic values and are not further iterated.
    """
    flat_list: List[Union[str, int, float, bool, None]] = []
    for v in values:
        if isinstance(v, (list, tuple)):
            flat_list.extend(_flatten_list(v))
        else:
            flat_list.append(v)
    return flat_list


def generic_runner(
    script: str,
    mapping: Dict[str, ValueType],
    *,
    flag_map: Optional[Dict[str, str]] = None,
    execute: bool = False,
):
    """
    Build and optionally execute a command-line string from a script and argument mapping.

    This function constructs a shell command by combining a script path with flags
    and their corresponding values. It handles nested lists of arguments, properly
    flattening them so that flags with multiple values are correctly represented
    in the command line. Optionally, it can execute the command using subprocess.

    Args:
        script (str): The path to the script or executable to run.
        mapping (Dict[str, Any]): A dictionary mapping CLI flags (e.g., '--input')
            to their values. Values can be single values or nested lists/tuples.
        flag_map (Optional[Dict[str, str]], optional): An optional mapping to rename
            flags (e.g., {'--workflow_flag': '--module_flag'}). Defaults to None.
        execute (bool, optional): If True, execute the constructed command using
            subprocess.run. Defaults to False.

    Returns:
        str: The fully constructed command-line string.

    Example:
        >>> mapping = {'--axial': [['3'], ['2'], ['1', ['3']], ['4']], '--dpi': 500}
        >>> generic_runner("python script.py", mapping)
        Running: python script.py --axial 3 2 1 3 4 --dpi 500
        'python script.py --axial 3 2 1 3 4 --dpi 500'
    """
    flag_map = flag_map or {}
    parts = [script]

    for flag, value in mapping.items():
        new_flag = flag_map.get(flag, flag)
        if isinstance(value, (list, tuple)):
            flat_values = _flatten_list(value)
            parts.append(new_flag)
            parts.extend(map(str, flat_values))
        else:
            parts.extend([new_flag, str(value)])

    cmd_str = " ".join(parts)
    print(f"Running: {cmd_str}")

    if execute:
        _ = subprocess.run(cmd_str, shell=True, check=True)

    return cmd_str
