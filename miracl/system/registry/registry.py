from typing import Optional, Dict, Type, Callable
from typing_extensions import TypedDict

from miracl.system.datamodels.miraclobj_serializer import build_flag_map_from_class
from miracl.system.datamodels.miraclobj_enums import ModuleType


# FlagMap = flag_map: Dict[str, object]


class RegistryTemplate(TypedDict):
    script: str
    obj_class: Type
    module_type: ModuleType


class RegistryEntry(TypedDict):
    script: str
    runner: Callable[[str, Dict[str, object]], object]
    obj_class: Type
    module_type: ModuleType


class MiraclRegistry:
    def __init__(self):
        """
        Initialize an empty MiraclRegistry.
        """
        self._registry: Dict[str, RegistryEntry] = {}

    def register(
        self,
        name: str,
        script: str,
        # mapping: dict,
        runner: Callable[[str, Dict[str, object]], object],
        obj_class: Type,
        module_type: ModuleType,
    ) -> None:
        """
        Register a module with the registry.

        Args:
            name (str): Unique name for the module.
            script (str): Path or identifier of the script to run.
            runner (Callable): Function that executes the script with flags.
            obj_class (Type): Class containing miracl object definitions.
            module_type (ModuleType): The module type (e.g., FLOW_MAPL3, etc.).
        """
        self._registry[name] = {
            "script": script,
            # "mapping": mapping,
            "runner": runner,
            "obj_class": obj_class,
            "module_type": module_type,
        }

    def register_from_template(
        self,
        name: str,
        template: RegistryTemplate,
        runner: Callable[[str, Dict[str, object]], object],
    ) -> None:
        """
        Register a module using a RegistryTemplate.

        Args:
            name (str): Unique name for the module.
            template (RegistryTemplate): Dict with 'script', 'obj_class', 'module_type'.
            runner (Callable): Function that executes the script with flags.
        """
        flag_map = build_flag_map_from_class(
            template["obj_class"],
            template["module_type"],
        )
        self.register(
            name,
            template["script"],
            # flag_map,
            runner,
            template["obj_class"],
            template["module_type"],
        )

    def get(self, name: str) -> RegistryEntry:
        """
        Get the full registry entry for a given module.

        Args:
            name (str): Name of the registered module.

        Returns:
            Dict[str, Any]: The full registry entry.
        """
        return self._registry[name]

    def get_info(self) -> Dict[str, RegistryEntry]:
        """
        Return the entire registry.

        Returns:
            Dict[str, Dict[str, Any]]: All registered modules.
        """
        return self._registry

    def get_class(self, name: str) -> Type:
        """
        Return the obj_class for a given module name.

        Args:
            name (str): The module name.

        Returns:
            Type: The registered class associated with the module.
        """
        if name not in self._registry:
            raise ValueError(f"Module '{name}' not found in registry")
        return self._registry[name]["obj_class"]

    # def get_class(
    #     self,
    #     name: str,
    #     include_all: bool = True,
    # ) -> Dict[str, object]:
    #     if name not in self._registry:
    #         raise ValueError(f"Module '{name}' not found in registry")
    #
    #     entry = self._registry[name]
    #     obj_class = entry["obj_class"]
    #     module_type = entry["module_type"]
    #
    #     # Return the flattened flag map, optionally including disabled flags
    #     return build_flag_map_from_class(
    #         obj_class, module_type, include_all=include_all
    #     )

    # UPDATED: now supports overrides
    def run(
        self,
        name: str,
        overrides: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Execute the registered runner function for a module, with optional overrides.

        Args:
            name (str): The module name.
            overrides (Optional[Dict[str, Any]]): Optional flag overrides.

        Returns:
            Any: The result of the runner execution.
        """
        if name not in self._registry:
            raise ValueError(f"Module '{name}' not found in registry")

        entry = self._registry[name]

        obj_class = entry["obj_class"]
        module_type = entry["module_type"]

        flag_map = build_flag_map_from_class(obj_class, module_type)
        # Copy mapping so we don't modify stored defaults
        # final_mapping = entry["mapping"].copy()
        final_mapping = flag_map.copy()

        # Apply overrides if provided
        if overrides:
            final_mapping.update(overrides)

        # Run with merged mapping
        return entry["runner"](entry["script"], final_mapping)

    def get_override_flag(
        self,
        registry_key: str,
        obj_name: str,
        manual_module_type: Optional[ModuleType] = None,
    ) -> Optional[str]:
        """
        Get the CLI flag associated with a specific object in a registered module.

        Args:
            registry_key (str): The name of the registered module.
            obj_name (str): The attribute name of the object.

        Returns:
            Optional[str]: The CLI flag (e.g., '--tiff-folder'), or None if not found.
        """
        if registry_key not in self._registry:
            raise ValueError(f"Module '{registry_key}' not found in registry")

        entry = self._registry[registry_key]
        cls = self.get_class(registry_key)
        if manual_module_type is None:
            module_type = entry["module_type"]
        else:
            module_type = manual_module_type

        attr_instance = getattr(cls, obj_name)

        if module_type == ModuleType.MODULE:
            return f"--{attr_instance.cli_l_flag}"
        else:
            return f"--{attr_instance.flow.get(module_type, {}).get('cli_l_flag')}"

    def get_override_value(
        self,
        registry_key: str,
        obj_name: str,
    ) -> object:
        """
        Get the content value associated with a specific object in a registered module.

        Args:
            registry_key (str): The name of the registered module.
            obj_name (str): The attribute name of the object.

        Returns:
            Any: The 'content' value of the object.
        """
        cls = self.get_class(registry_key)
        attr_instance = getattr(cls, obj_name)

        # return getattr(cls, obj_name).content
        return (
            attr_instance.content
            if attr_instance.content is not None
            else attr_instance.obj_default
        )
