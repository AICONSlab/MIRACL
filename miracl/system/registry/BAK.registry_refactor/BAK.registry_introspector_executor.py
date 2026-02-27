from miracl.system.registry.registry_refactor.datamodels import (
    RegistryState,
    ModuleDataPackage,
    ExecutionContext,
    ResolvedObject,
    ArgMetadata,
)
from typing import Any, Dict
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


class Introspector:
    def __init__(self, registry: Any):
        # registry is an instance of MiraclRegistry
        self.registry = registry

    def get_registry_snapshot(self) -> RegistryState:
        """
        Captures state and metadata for ALL modules in the registry.
        Uses MiraclObj.resolve() to get context-aware metadata.
        """
        modules_map: Dict[str, ModuleDataPackage] = {}

        # 1. Iterate through the Registry catalog
        for module_name, entry in self.registry.list_modules().items():
            cls = entry["obj_class"]
            module_type = entry["module_type"]

            arg_metadata: Dict[str, ArgMetadata] = {}
            resolved_objects: Dict[str, ResolvedObject] = {}

            # 2. Introspect the Class for MiraclObj definitions
            for attr_name in dir(cls):
                if attr_name.startswith("_"):
                    continue

                attr_def = getattr(cls, attr_name)

                if not isinstance(attr_def, MiraclObj):
                    continue

                # 3. Use the 'resolve' logic from your example
                # This handles the ModuleType context (flags, required, etc.)
                resolved = attr_def.resolve(module_type)

                # Map to our ArgMetadata Pydantic model
                arg_metadata[attr_name] = ArgMetadata(
                    cli_l_flag=resolved["cli_l_flag"],
                    cli_required=resolved.get("cli_required", False),
                    gui_hidden=resolved.get("gui_hidden", False),
                )

                # 4. Resolve Live Content
                # Get the live instance from the global storage
                instance = MiraclObj.instances.get((module_name, attr_name))

                # If the module hasn't been instantiated yet, we fall back
                # to the default value from the resolved dictionary
                content = instance.content if instance else resolved.get("obj_default")

                resolved_objects[attr_name] = ResolvedObject(
                    id=resolved["id"], content=content
                )

            # 5. Package the Module into the state
            modules_map[module_name] = ModuleDataPackage(
                context=ExecutionContext(
                    script=entry["script"],
                    runner=entry["runner"],
                    arg_metadata=arg_metadata,
                    flag_map=entry["flag_map"],
                ),
                objects=resolved_objects,
            )

        return RegistryState(modules=modules_map)
