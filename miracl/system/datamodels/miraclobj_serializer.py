from typing import List, Tuple, Union, Dict, Type
from argparse import Namespace

# FIX: Import ModuleType from centralized ENUMS file
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.datamodels.miraclobj_enums import ModuleType

"""
Serializer utilities for Miracl CLI argument handling.

This module provides helper functions to bridge Pydantic MiraclObj data models
and CLI argument parsing. It abstracts the logic of translating MiraclObj instances
and their metadata into CLI flags and argparse-compatible parameters, enabling
functions to work with simple, flattened argument representations.

Key features:
- Determine CLI inclusion of arguments based on module context (workflow vs module).
- Deserialize parsed CLI arguments back into MiraclObj instances.
- Generate CLI flags and argparse argument configurations directly from MiraclObjs.
- Build flag-to-value mappings from MiraclObj classes for easy access.

By centralizing this serialization logic, downstream functions can operate on familiar
data formats without needing to parse or interpret the underlying data model structures.
"""


def should_include_in_cli(obj: MiraclObj, module_type: ModuleType) -> bool:
    """
    Determine whether the given `MiraclObj` should be included in the CLI
    for the specified module type.

    Args:
        obj (MiraclObj): The object to check.
        module_type (ModuleType): The current module context as an Enum member
            (e.g., ModuleType.MODULE, ModuleType.ACE, ModuleType.MAPL3).

    Returns:
        bool: True if the argument should be exposed in CLI, False otherwise.
    """
    if module_type == ModuleType.MODULE:
        return True  # Regular module args are always included

    # For workflow modules (ACE, MAPL3, etc), check flow config
    if obj.flow is None:
        return False

    flow_cfg = obj.flow.get(module_type.value)
    if not flow_cfg:
        return False

    return not flow_cfg.get("disabled", False)


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, dict], miracl_objs: List[MiraclObj]
) -> List[MiraclObj]:
    """
    Given parsed CLI arguments (Namespace or dict) and a list of MiraclObj instances,
    assign each parsed argument value to the corresponding MiraclObj.content by matching
    parsed argument keys to MiraclObj.name (dest).

    Args:
        parsed_args (Namespace or dict): Parsed CLI arguments from argparse.
        miracl_objs (List[MiraclObj]): List of MiraclObj instances to populate.

    Returns:
        List[MiraclObj]: Updated list of MiraclObj with 'content' fields set to parsed values.
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


def get_cli_flags_for_obj(obj: MiraclObj, module_type: ModuleType) -> List[str]:
    """
    Return the CLI flags (short and long) for the given MiraclObj, respecting
    the provided module_type context.

    Args:
        obj (MiraclObj): The MiraclObj to inspect.
        module_type (ModuleType): The module or workflow context enum.

    Returns:
        List[str]: List of CLI flags (e.g., ['-i', '--input']). Empty list if
        argument is disabled or no flags are defined.
    """
    flags = []

    if module_type == ModuleType.MODULE:  # If it's a module, not a workflow
        if obj.cli_s_flag:
            flags.append(f"-{obj.cli_s_flag}")
        if obj.cli_l_flag:
            flags.append(f"--{obj.cli_l_flag}")
        return flags

    # For workflow types
    if not obj.flow or module_type.value not in obj.flow:
        return []

    flow_cfg = obj.flow[module_type.value]
    if flow_cfg.get("disabled", False):
        return []

    if flow_cfg.get("cli_s_flag"):
        flags.append(f"-{flow_cfg['cli_s_flag']}")
    if flow_cfg.get("cli_l_flag"):
        flags.append(f"--{flow_cfg['cli_l_flag']}")

    return flags


def build_flag_map_from_class(
    obj_class: Type,
    module_type: ModuleType,
) -> Dict[str, object]:
    """
    Build a mapping from CLI long flags (e.g., '--input') to their values based on
    MiraclObj attributes of a class, respecting the provided module_type context.

    Args:
        obj_class (Type): Class containing MiraclObj attributes.
        module_type (ModuleType): Module or workflow context enum.

    Returns:
        Dict[str, object]: Mapping of CLI long flags to corresponding MiraclObj values
        (either 'content' if set, else 'obj_default').
    """
    mapping: Dict[str, object] = {}

    for _, attr_value in vars(obj_class).items():
        if isinstance(attr_value, MiraclObj):
            flags = get_cli_flags_for_obj(attr_value, module_type)
            long_flags = [f for f in flags if f.startswith("--")]
            if long_flags:
                val = (
                    attr_value.content
                    if attr_value.content is not None
                    else attr_value.obj_default
                )
                mapping[long_flags[0]] = val

    return mapping


def miraclobj_to_argparse(
    obj: MiraclObj,
    module_type: ModuleType,
) -> Tuple[List[str], dict]:
    """
    Convert a `MiraclObj` instance into CLI flags and corresponding argparse kwargs.

    Args:
        obj (MiraclObj): The argument definition object.
        module_type (ModuleType): Module or workflow context enum.

    Returns:
        Tuple[List[str], dict]: Tuple of (flags, kwargs) suitable for argparse's
        add_argument method.
    """

    flags = get_cli_flags_for_obj(obj, module_type)

    if not flags:
        return [], {}

    if not obj.cli_help:
        raise ValueError(f"Missing required 'cli_help' for object {obj.id}")

    kwargs = {
        "help": obj.cli_help,
        "dest": obj.name,
    }

    # Determine if argument is required
    if module_type == ModuleType.MODULE:
        kwargs["required"] = obj.cli_required if obj.cli_required is not None else False
    else:
        flow_cfg = obj.flow.get(module_type.value, {}) if obj.flow else {}
        kwargs["required"] = flow_cfg.get("required", False)

    # Add other argparse options if present
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
