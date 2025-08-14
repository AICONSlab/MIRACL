from typing import Optional, Dict


class MiraclRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, name: str, script: str, mapping: dict, runner):
        self._registry[name] = {
            "script": script,
            "mapping": mapping,
            "runner": runner,
        }

    def register_from_template(self, name: str, template: dict, runner):
        """Register a module from a standard { 'script', 'flag_map' } template"""
        self.register(
            name,
            template["script"],
            template["flag_map"],
            runner,
        )

    def get(self, name: str) -> dict:
        return self._registry[name]

    # UPDATED: now supports overrides
    def run(self, name: str, overrides: Optional[Dict] = None):
        if name not in self._registry:
            raise ValueError(f"Module '{name}' not found in registry")

        entry = self._registry[name]

        # Copy mapping so we don't modify stored defaults
        final_mapping = entry["mapping"].copy()

        # Apply overrides if provided
        if overrides:
            final_mapping.update(overrides)

        # Run with merged mapping
        return entry["runner"](entry["script"], final_mapping)
