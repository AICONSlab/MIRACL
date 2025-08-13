from typing import List, Tuple, Union
import re
from argparse import Namespace

# FIX: Import ModuleType from centralized ENUMS file
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.datamodels.miraclobj_enums import ModuleType


def should_include_in_cli(obj: MiraclObj, module_type_str: str) -> bool:
    """
    Determine whether the given `MiraclObj` should be included in the CLI
    for the specified module type.

    Args:
        obj (MiraclObj): The object to check.
        module_type_str (str): The current module context (e.g., "module", "ace", "mapl3").

    Returns:
        bool: True if the argument should be exposed in CLI, False otherwise.
    """
    if module_type_str == ModuleType.MODULE.value:
        return True  # Regular module args are always included

    # For workflow modules (ACE, MAPL3, etc), check flow config
    if obj.flow is None:
        return False

    flow_cfg = obj.flow.get(module_type_str)
    if not flow_cfg:
        return False

    return not flow_cfg.get("disabled", False)


def miraclobj_to_argparse(
    obj: MiraclObj, module_type_str: str
) -> Tuple[List[str], dict]:
    """
    Convert a `MiraclObj` instance into a tuple of command-line argument flags and keyword arguments
    suitable for use with `argparse.ArgumentParser.add_argument`.

    This function determines how the given argument should be exposed in a command-line interface,
    including its flags (e.g., `--input`, `-i`) and configuration options like type, default value,
    required status, choices, and more.

    Behavior differs depending on whether the `MiraclObj` is used in a standalone module or as part
    of a workflow (e.g., ACE, MAPL3). When used in a workflow, the flow-specific configuration in
    the `flow` field of the object takes precedence.

    Args:
        obj (MiraclObj): The argument definition object to convert.
        module_type_str (str): The module type context in which this object is used, e.g.,
            `"module"`, `"ace"`, or `"mapl3"`. Must correspond to a value from `ModuleType`.

    Returns:
        Tuple[List[str], dict]: A tuple containing:
            - A list of CLI flags (e.g., `["-i", "--input"]`)
            - A dictionary of keyword arguments for `add_argument()` (e.g., `{"type": str, "required": True}`)

    Example:
        >>> from miracl.models import MiraclObj
        >>> from miracl.enums import ModuleType
        >>> from miracl.serialization import miraclobj_to_argparse
        >>> obj = MiraclObj(
        ...     id="123",
        ...     name="input_path",
        ...     cli_l_flag="input",
        ...     cli_s_flag="i",
        ...     cli_help="Path to input file",
        ...     cli_obj_type=ArgumentType.STRING,
        ...     module="ace",
        ...     module_group="reg",
        ...     version_added="2.4.0"
        ... )
        >>> flags, kwargs = miraclobj_to_argparse(obj, ModuleType.MODULE.value)
        >>> print(flags)
        ['-i', '--input']
        >>> print(kwargs)
        {'help': 'Path to input file', 'required': False, 'type': <class 'str'>}

    Raises:
        None explicitly, but relies on the integrity of the `MiraclObj` fields.
    """

    flags: List[str] = []
    kwargs = {
        "help": getattr(obj, "cli_help", "No help available"),
    }

    if module_type_str == ModuleType.MODULE.value:
        if obj.cli_s_flag:
            flags.append(f"-{obj.cli_s_flag}")
        if obj.cli_l_flag:
            flags.append(f"--{obj.cli_l_flag}")
        kwargs["required"] = (
            obj.cli_required if obj.cli_required is not None else False
        )  # Use cli_required attr for argparse
    else:
        if obj.flow is None:
            raise ValueError(
                f"Flow configuration missing for object {obj.id} in module {module_type_str}"
            )
        if module_type_str not in obj.flow:
            raise ValueError(
                f"Flow configuration for module type '{module_type_str}' missing in object {obj.id}"
            )
        flow_cfg = obj.flow[module_type_str]
        if flow_cfg.get("disabled", False):
            return (
                [],
                {},
            )  # effectively skipping the arg from CLI for this module context
        if flow_cfg.get("cli_s_flag"):
            flags.append(f"-{flow_cfg['cli_s_flag']}")
        if flow_cfg.get("cli_l_flag"):
            flags.append(f"--{flow_cfg['cli_l_flag']}")
        kwargs["required"] = flow_cfg.get(
            "required", False
        )  # Use required dict key for argparse

    if not hasattr(obj, "name") or not obj.name:
        raise ValueError(
            f"MiraclObj missing required 'name' attribute for CLI argument"
        )
    kwargs["dest"] = (
        obj.name
    )  # assignment forced for deserializer from argparse arg back to MiraclObj

    if getattr(obj, "cli_obj_type", None) is not None:
        kwargs["type"] = obj.cli_obj_type.python_type

    if getattr(obj, "cli_metavar", None) is not None:
        kwargs["metavar"] = obj.cli_metavar

    if getattr(obj, "cli_nargs", None) is not None:
        kwargs["nargs"] = obj.cli_nargs

    if getattr(obj, "cli_choices", None) is not None:
        kwargs["choices"] = obj.cli_choices

    if getattr(obj, "obj_default", None) is not None:
        kwargs["default"] = obj.obj_default

    if getattr(obj, "cli_action", None) is not None:
        kwargs["action"] = obj.cli_action.value

    return flags, kwargs


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, dict], miracl_objs: List[MiraclObj]
) -> List[MiraclObj]:
    """
    Given parsed CLI args (Namespace or dict) and a list of MiraclObj,
    assign each parsed argument value to the corresponding MiraclObj.content
    by matching parsed argument keys to MiraclObj.name (dest).

    Args:
        parsed_args (Namespace or dict): Parsed CLI arguments from argparse.
        miracl_objs (List[MiraclObj]): List of MiraclObj instances to populate.

    Returns:
        List[MiraclObj]: Updated list of MiraclObj with 'content' fields set.
    """
    # Convert Namespace to dict if needed
    if isinstance(parsed_args, Namespace):
        parsed_args = vars(parsed_args)

    name_to_obj = {obj.name: obj for obj in miracl_objs}

    for dest, value in parsed_args.items():
        obj = name_to_obj.get(dest)
        if obj:
            # Assign the parsed value to content
            obj.content = value

    return miracl_objs
