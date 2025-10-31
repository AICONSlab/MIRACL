from typing import List, Tuple, Union, Dict, Type, Callable, Sequence
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


DeserializeParsedArgsToObjectsArgValue = Union[str, int, float, bool, None, List[str]]


def deserialize_parsed_args_to_objects(
    parsed_args: Union[Namespace, Dict[str, DeserializeParsedArgsToObjectsArgValue]],
    miracl_objs: List[MiraclObj],
) -> List[MiraclObj]:
    """
    Given parsed CLI arguments (Namespace or dict) and a list of MiraclObj instances,
    assign each parsed argument value to the corresponding MiraclObj.content by matching
    parsed argument keys to MiraclObj.id (used as argparse 'dest').

    Args:
        parsed_args (Namespace or dict): Parsed CLI arguments from argparse.
        miracl_objs (List[MiraclObj]): List of MiraclObj instances to populate.

    Returns:
        List[MiraclObj]: Updated list of MiraclObj with 'content' fields set to parsed values.
    """
    # Convert Namespace to dict if needed
    if isinstance(parsed_args, Namespace):
        parsed_args = vars(parsed_args)

    # name_to_obj = {obj.name: obj for obj in miracl_objs}
    id_to_obj = {str(obj.id): obj for obj in miracl_objs}

    for dest, value in parsed_args.items():
        # obj = name_to_obj.get(dest)
        # print(f"Looking up dest={dest}")
        obj = id_to_obj.get(dest)
        if obj:
            # Assign the parsed value to content
            # print(f"Matched to obj.name={obj.name}")
            obj.content = value

    return miracl_objs


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

    for attr_value in vars(obj_class).values():
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


def get_cli_flags_for_obj(
    obj: MiraclObj, module_type: ModuleType, include_disabled: bool = False
) -> List[str]:
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
    flags: List[str] = []

    if module_type == ModuleType.MODULE:  # If it's a module, not a workflow
        try:
            flags.append(f"-{obj.cli_s_flag}")
            flags.append(f"--{obj.cli_l_flag}")
        except KeyError as e:
            raise KeyError(
                f"Missing required CLI flag in flow config for '{obj.name}': {e}"
            )

        return flags

    # For workflow types
    # Check if the flow attribute is present
    if obj.flow is None:
        raise ValueError(
            f"Missing ('{obj.flow}') required flow attribute for '{obj.name}'"
        )
    # Check if the ModuleType keys are present
    if module_type not in obj.flow:
        raise KeyError(
            f"Missing required ModuleType for '{obj.name}' flow: {module_type}"
        )

    # if not obj.flow or module_type not in obj.flow:
    #     return []

    # If the object should not be included in the workflow, return empty flag dict
    flow_cfg = obj.flow[module_type.value]
    # if flow_cfg.get("disabled", False):
    if not include_disabled and flow_cfg.get("disabled", False):
        return []

    try:
        flags.append(f"-{flow_cfg['cli_s_flag']}")
        flags.append(f"--{flow_cfg['cli_l_flag']}")
    except KeyError as e:
        raise KeyError(
            f"Missing required CLI flag in flow config for '{obj.name}': {e}"
        )

    return flags


MiraclObjToArgparseKwargValue = Union[
    str, int, float, bool, None, Callable[[str], object], Sequence[str]
]


def miraclobj_to_argparse(
    obj: MiraclObj,
    module_type: ModuleType,
) -> Tuple[List[str], Dict[str, MiraclObjToArgparseKwargValue]]:
    """
    Convert a `MiraclObj` instance into CLI flags and corresponding argparse kwargs.

    This includes:
    - Generating CLI flags using module-specific config (e.g. `-f`, `--folder`)
    - Assigning a UUID as the `dest` to ensure uniqueness across arguments
    - Choosing a display name for help output using `cli_metavar` or falling back to `obj.name.upper()`
    - Populating additional argparse options like `type`, `required`, `default`, `nargs`, `choices`, and `action`

    Args:
        obj (MiraclObj): The argument definition object.
        module_type (ModuleType): Module or workflow context enum.

    Returns:
        Tuple[List[str], dict]: Tuple of (flags, kwargs) suitable for argparse's
        `add_argument` method.
    """

    flags = get_cli_flags_for_obj(obj, module_type)

    if not flags:
        return [], {}

    # if module_type == ModuleType.MODULE:
    #     include = {
    #         "id",
    #         "name",
    #         "cli_s_flag",
    #         "cli_l_flag",
    #         "cli_obj_type",
    #         "cli_help",
    #         "cli_metavar",
    #         "cli_nargs",
    #         "cli_choices",
    #         "obj_default",
    #         "cli_required",
    #         "cli_action",
    #         "content",
    #     }
    # else:
    #     include = {
    #         "id": True,
    #         "name": True,
    #         "flow": {module_type},
    #         "content": True,
    #     }
    #
    # selected_data = obj.model_dump(include=include)

    if not obj.cli_help:
        raise ValueError(f"Missing required 'cli_help' for object {obj.id}")

    kwargs: Dict[str, MiraclObjToArgparseKwargValue] = {
        "help": obj.cli_help,
        "dest": str(obj.id),
        # "dest": str(obj.cli_l_flag) if ModuleType.MODULE else str(obj.id),
        "metavar": obj.cli_metavar
        if obj.cli_metavar not in (None, "")
        else obj.name.upper(),
    }

    # Determine if argument is required
    if module_type == ModuleType.MODULE:
        kwargs["required"] = obj.cli_required if obj.cli_required is not None else False
    else:
        if obj.flow:
            flow_cfg = obj.flow.get(module_type.value)
            if flow_cfg is None:
                raise ValueError(
                    f"Missing flow configuration for module type '{module_type.value}' in flow for '{obj.name}'"
                )
        else:
            raise ValueError(f"Missing 'flow' configuration for '{obj.name}'")
        # flow_cfg = obj.flow.get(module_type.value, {}) if obj.flow else {}
        kwargs["required"] = flow_cfg.get("required", False)

    # FIX: Add all options from argparser docs -> also add in datamodel

    # Add other argparse options if present
    if getattr(obj, "cli_obj_type", None) is not None:
        kwargs["type"] = obj.cli_obj_type.python_type

    if getattr(obj, "cli_nargs", None) is not None:
        kwargs["nargs"] = obj.cli_nargs

    if getattr(obj, "cli_choices", None) is not None:
        kwargs["choices"] = obj.cli_choices

    if getattr(obj, "obj_default", None) is not None:
        kwargs["default"] = obj.obj_default

    if getattr(obj, "cli_action", None) is not None:
        kwargs["action"] = obj.cli_action.value

    if getattr(obj, "cli_const", None) is not None:
        kwargs["const"] = obj.cli_const

    return flags, kwargs


def build_workflow_to_module_flag_map(
    obj_class: Type,
    module_type: ModuleType,
) -> Dict[str, str]:
    """
     Build a mapping from workflow long flags to module long flags for a given class.

    This function iterates over all `MiraclObj` attributes in `obj_class` and generates
    a dictionary mapping workflow-specific CLI flags (e.g., '--mgp_input') to the
    corresponding module flags (e.g., '--input').

    Only attributes that have exactly one long flag in both workflow and module contexts
    are valid. Attributes without a workflow long flag (disabled or not included) are skipped.
    If an attribute has multiple long flags in either context, an error is raised.

    Args:
        obj_class (type): Class containing `MiraclObj` attributes.
        module_type (ModuleType): Module/workflow context enum for which to extract workflow flags.

    Returns:
        dict[str, str]: Mapping of workflow long flags to module long flags.
                        Example: {'--mgp_input': '--input'}

    Raises:
        ValueError: If an attribute has multiple long flags in either the workflow
                    or module context.
    """
    flow_module_flag_map: Dict[str, str] = {}
    for attr_value in vars(obj_class).values():
        if isinstance(attr_value, MiraclObj):
            flow_flags = get_cli_flags_for_obj(attr_value, module_type)
            long_flow_flag = [f for f in flow_flags if f.startswith("--")]
            module_flags = get_cli_flags_for_obj(attr_value, ModuleType.MODULE)
            long_module_flag = [f for f in module_flags if f.startswith("--")]

            # Skip attributes not included in workflow
            if not long_flow_flag:
                continue

            # Enforce strict one-to-one mapping
            if len(long_flow_flag) != 1:
                raise ValueError(
                    f"Expected exactly one long workflow flag for '{attr_value.name}', "
                    f"found {len(long_flow_flag)}: {long_flow_flag}"
                )

            if len(long_module_flag) != 1:
                raise ValueError(
                    f"Expected exactly one long module flag for '{attr_value.name}', "
                    f"found {len(long_module_flag)}: {long_module_flag}"
                )

            flow_module_flag_map[long_flow_flag[0]] = long_module_flag[0]

    return flow_module_flag_map
