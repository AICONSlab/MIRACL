from collections import defaultdict
from typing_extensions import override
from typing import Dict, Any
from miracl.system.registry.registry_refactor.registry_clean import MiraclRegistry
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.registry.registry_refactor.registry_datamodels import RegistryEntry


class RegistryIntrospector:
    """
    Utility class to introspect a MiraclRegistry and extract all registered
    module objects as a nested dictionary.
    """

    def __init__(self, registry: MiraclRegistry) -> None:
        """
        Initialize the introspector with a MiraclRegistry instance.

        Args:
            registry (MiraclRegistry): The registry to introspect.
        """
        self.registry = registry

    def get_modules_as_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Resolve all MiraclObj attributes for each registered module in the registry
        and return them as a nested dictionary.

        Returns:
            Dict[str, Dict[str, Any]]: A nested dictionary where the outer keys
            are module class names, the inner keys are MiraclObj names, and the
            values are the resolved object values.
        """
        resolved_objects: defaultdict[str, dict[str, Any]] = defaultdict(dict)

        # for key, entry in self.registry._registry.items():
        for key in self.registry.list_modules().keys():
            entry = self.registry.get(key)
            module_type = entry["module_type"]
            obj_class = entry["obj_class"]
            class_name = obj_class.__name__

            # for attr in vars(obj_class).values():
            #     if not isinstance(attr, MiraclObj):
            #         continue
            #
            #     resolved = attr.resolve(module_type)
            #
            #     if resolved is None:
            #         continue
            #
            #     resolved_objects[class_name][attr.name] = resolved

            for attr_name, attr in vars(obj_class).items():
                if not isinstance(attr, MiraclObj):
                    continue

                resolved = attr.resolve(module_type)

                if resolved is None:
                    continue

                resolved_objects[class_name][attr_name] = resolved

        return dict(resolved_objects)

    def get_registry_metadata_as_dict(self) -> Dict[str, RegistryEntry]:
        """
        List all registered modules.

        Args:
            None

        Returns:
            Dict mapping module names to their full registry entries

        Examples:
            >>> modules = registry.list_modules()
            >>> print(modules.keys())
            dict_keys(['tfce', 'plot_warped_data', 'conversion'])
        """
        return self.registry.list_modules(verbose=False)

    @override
    def __repr__(self) -> str:
        module_names = ", ".join(self.registry.list_modules().keys())
        return f"<RegistryIntrospector: Introspecting {len(module_names.split(', '))} registered module(s) ({module_names})>"
