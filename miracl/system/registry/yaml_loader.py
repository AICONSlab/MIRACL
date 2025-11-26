import yaml
import importlib
from typing import Dict, Callable

from miracl.api.ext import (
    MiraclRegistry,
    RegistryTemplate,
    build_workflow_to_module_flag_map,
)
from miracl.api.enums import ModuleType
from miracl.system.registry.schema_validators.config_schema import ModuleEntry


def _import_from_string(path: str) -> object:
    """
    Dynamically import and return an attribute from a dotted import path.

    Example:
        _import_from_string("pkg.module.Class")  ->  pkg.module.Class

    Args:
        path (str): Dotted path to import.

    Returns:
        object: The attribute referenced by the final component.
    """
    module_path, attr = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def load_modules_from_yaml(path: str) -> MiraclRegistry:
    """
    Load a Miracl module registry from a YAML configuration file.

    This function performs the following steps:
        1. Parse raw YAML into Python dictionaries.
        2. Validate and normalize module entries using Pydantic.
           - `module_type` strings are converted to ModuleType enums.
           - Unknown fields in YAML raise a validation error.
        3. Dynamically import `obj_class` and `runner` functions.
        4. Determine the flag map:
           - If `flag_map` is empty `{}` for a workflow module, it is auto-generated.
           - For MODULE types, the flag map is always empty.
        5. Wrap the runner function in `wrapped_runner` with the resolved flag map and execute flag.
        6. Register all modules in a `MiraclRegistry`.

    YAML Format:
        module_name:
            script: "python run.py"
            obj_class: "mypkg.objects.MyClass"
            runner: "mypkg.runners.generic_runner"
            module_type: "MAPL3"        # Valid ModuleType name
            flag_map: {}                # Empty dict triggers auto-generation for workflow modules
            execute: false              # Optional, default False

    Args:
        path (str): Filesystem path to a YAML module definition file.

    Returns:
        MiraclRegistry: Fully populated registry containing all modules defined in YAML.

    Notes:
        - `module_type` values are validated against `ModuleType` enum.
        - `flag_map` must be defined in YAML; empty dict `{}` is valid and triggers auto-generation.
        - `execute` determines whether the runner executes commands or just constructs them.
        - Each runner function is wrapped to include the resolved flag map and execute setting.
    """
    with open(path, "r") as f:
        raw_yaml = yaml.safe_load(f)

    validated_dict = {k: ModuleEntry.model_validate(v) for k, v in raw_yaml.items()}

    reg = MiraclRegistry()

    for name, cfg in validated_dict.items():
        obj_class = _import_from_string(cfg.obj_class)
        runner_func = _import_from_string(cfg.runner)
        module_type = cfg.module_type
        execute = cfg.execute

        yaml_flag_map = cfg.flag_map

        if module_type == ModuleType.MODULE:
            flag_map = {}
        elif yaml_flag_map is None:
            raise ValueError(
                f"Workflow '{name}' (type {module_type.name}) must define a flag_map in YAML. flag_map can be empty, but not omitted."
            )
        elif yaml_flag_map == {}:
            flag_map = build_workflow_to_module_flag_map(obj_class, module_type)
        else:
            flag_map = yaml_flag_map

        def wrapped_runner(script: str, mapping: Dict[str, object]) -> object:
            """
            Wrapped runner that injects the resolved flag map and execute setting.

            Args:
                script (str): Script or command to run.
                mapping (Dict[str, object]): Mapping of input variables.

            Returns:
                object: Result of the underlying runner
            """
            return runner_func(script, mapping, flag_map=flag_map, execute=execute)

        setattr(wrapped_runner, "_original_runner", runner_func)

        template = RegistryTemplate(
            script=cfg.script,
            obj_class=obj_class,
            module_type=module_type,
        )

        reg.register_from_template(name, template, wrapped_runner)

    return reg
