from collections import defaultdict
from typing import Dict, Any, Type, Callable
from typing_extensions import override
from miracl.system.registry.registry_refactor.registry_clean import MiraclRegistry
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj


class RegistryIntrospector:
    """
    Utility class to introspect a MiraclRegistry and extract all information
    needed for serialization and execution.
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

        for key in self.registry.list_modules().keys():
            entry = self.registry.get(key)
            module_type = entry["module_type"]
            obj_class = entry["obj_class"]
            class_name = obj_class.__name__

            for attr in vars(obj_class).values():
                if not isinstance(attr, MiraclObj):
                    continue

                resolved = attr.resolve(module_type)

                if resolved is None:
                    continue

                resolved_objects[class_name][attr.name] = resolved

        return dict(resolved_objects)

    def get_execution_context(self, module_name: str) -> Dict[str, Any]:
        """
        Get all information needed to execute a module.

        This is the ONLY place where registry execution metadata is extracted.
        The executor receives this and doesn't need to know about the registry.

        Args:
            module_name: Name of the module (e.g., 'conversion', 'tfce')

        Returns:
            Dict containing:
                - script: Script path to execute
                - runner: Runner function (with flag_map/execute bound)
                - obj_class: Class containing MiraclObj definitions
                - class_name: Name of the class
                - module_type: Context (MODULE, FLOW_MAPL3, etc.)

        Examples:
            >>> ctx = introspector.get_execution_context('conversion')
            >>> ctx['script']
            'python /code/miracl/conv/miracl_conv_convertTIFFtoNII.py'
            >>> ctx['runner']
            <function wrapped_runner at 0x...>
            >>> ctx['class_name']
            'ConvTiffNiiObjs'
        """
        entry = self.registry.get(module_name)

        return {
            "script": entry["script"],
            "runner": entry["runner"],
            "obj_class": entry["obj_class"],
            "class_name": entry["obj_class"].__name__,
            "module_type": entry["module_type"],
            "flag_map": entry["flag_map"],
            "execute": entry["execute"],
        }

    @override
    def __repr__(self) -> str:
        module_names = ", ".join(self.registry.list_modules().keys())
        return f"<RegistryIntrospector: {len(module_names.split(', '))} registered module(s) ({module_names})>"
