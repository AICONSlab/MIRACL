from typing import Optional, Dict, Type
from typing_extensions import TypedDict

from miracl.system.datamodels.miraclobj_serializer import build_flag_map_from_class


class RegistryTemplate(TypedDict):
    script: str
    # flag_map: Dict[str, object]
    obj_class: Type
    module_type: str


class MiraclRegistry:
    def __init__(self):
        self._registry = {}

    def register(
        self,
        name: str,
        script: str,
        # mapping: dict,
        runner,
        obj_class: Type,
        module_type: str,
    ):
        self._registry[name] = {
            "script": script,
            # "mapping": mapping,
            "runner": runner,
            "obj_class": obj_class,
            "module_type": module_type,
        }

    def register_from_template(self, name: str, template: RegistryTemplate, runner):
        """Register a module from a standard { 'script', 'flag_map' } template"""
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

    def get(self, name: str) -> dict:
        return self._registry[name]

    def get_info(self) -> dict:
        """Return the entire registry dictionary"""
        return self._registry

    # UPDATED: now supports overrides
    def run(self, name: str, overrides: Optional[Dict] = None):
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
