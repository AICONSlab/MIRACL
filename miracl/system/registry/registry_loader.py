import yaml
import importlib  # For dynamically importing modules by name
from miracl.system.registry.registry import MiraclRegistry, RegistryTemplate
from miracl.system.datamodels.miraclobj_enums import ModuleType


# Return attribute of dotted file path dynamically
def import_from_string(path: str):
    module_path, attr = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr)


def parse_module_type(module_type_str: str, module_name: str) -> ModuleType:
    """
    Convert a YAML string to a ModuleType enum, validating the input.

    Args:
        module_type_str (str): The module_type string from YAML.
        module_name (str): The name of the module (from YAML) for context.

    Returns:
        ModuleType: The corresponding enum member.

    Raises:
        ValueError: If the string does not match any ModuleType member name.
    """
    try:
        return ModuleType[module_type_str]
    except KeyError:
        valid_names = ", ".join([e.name for e in ModuleType])
        raise ValueError(
            f"Invalid module_type '{module_type_str}' for module '{module_name}' in YAML. Expected one of: {valid_names}"
        )


def load_modules_from_yaml(path: str) -> MiraclRegistry:
    """
    Load modules into a MiraclRegistry from a declarative YAML configuration file.

    This function reads a YAML file containing module definitions, each specifying:
        - module name
        - script path
        - associated object class
        - module type (e.g., FLOW_MAPL3, MODULE, etc.)
        - optional runner function override

    It then instantiates a `MiraclRegistry`, registers all modules defined in the YAML,
    and returns the populated registry ready for use.

    Args:
        yaml_path (str): Path to the YAML configuration file containing module definitions.

    Returns:
        MiraclRegistry: A registry instance with all modules from the YAML loaded.

    Notes:
        - If a module specifies a custom runner, it will be used; otherwise, the default runner
          is applied.
        - The registry can be used immediately for running modules or inspecting available modules.

    Examples:
        # Load registry from a YAML file
        reg = load_modules_from_yaml("/code/miracl/system/configs/modules.yaml")

        # Inspect loaded modules
        reg.list_modules()  # prints a summary

        # Run a module with optional overrides
        reg.run("conversion", overrides={"--tiff-folder": "/path/to/tiffs"})
    """
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    reg = MiraclRegistry()

    for name, cfg in config.items():
        obj_class = import_from_string(cfg["obj_class"])
        runner_func = import_from_string(cfg["runner"])
        # module_type = getattr(ModuleType, cfg["module_type"])
        module_type = parse_module_type(cfg["module_type"], module_name=name)
        flag_map = cfg.get("flag_map", {})
        execute = cfg.get("execute", False)

        def wrapped_runner(
            script, mapping, _runner=runner_func, _flag_map=flag_map, _execute=execute
        ):
            return _runner(script, mapping, flag_map=_flag_map, execute=_execute)

        # wrapped_runner._original_runner = runner_func
        setattr(wrapped_runner, "_original_runner", runner_func)

        template = RegistryTemplate(
            script=cfg["script"],
            obj_class=obj_class,
            module_type=module_type,
        )

        reg.register_from_template(name, template, wrapped_runner)

    return reg
