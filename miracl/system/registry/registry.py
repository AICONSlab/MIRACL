from typing import Dict, Type, Callable, Optional

# from miracl.system.registry.registry_refactor.registry_datamodels import RegistryEntry
from miracl.system.registry.registry_datamodel import RegistryEntry
from miracl.system.datamodels.miraclobj_enums import ModuleType
from miracl.system.logger import get_logger

logger = get_logger(__name__)  # >>> ADDED: Logger for deserialization


class MiraclRegistry:
    """
    Pure catalog/index of available MIRACL modules.

    The registry serves as a lightweight lookup table that answers:
    - "What modules are available?"
    - "Where can I find module X?"
    - "What metadata is associated with module X?"

    The registry does NOT:
    - Build flag maps (that's the serializer's job)
    - Resolve MiraclObj instances (that's the serializer's job)
    - Execute modules (that's the executor's job)
    - Introspect object classes (that's the serializer's job)

    This separation of concerns keeps the registry fast, simple, and focused.
    """

    def __init__(self):
        """Initialize an empty registry catalog."""
        self._registry: Dict[str, RegistryEntry] = {}
        logger.info("Initialized empty MiraclRegistry")

    def register(
        self,
        name: str,
        script: str,
        obj_class: Type,
        module_type: ModuleType,
        runner: Callable[[str, Dict[str, object], Dict[str, str], bool], object],
        flag_map: Optional[Dict[str, str]] = None,
        execute: bool = False,
    ) -> None:
        """
        Register a module in the catalog.

        Args:
            name: Unique identifier for the module (e.g., 'tfce', 'plot_warped_data')
            script: Path or command to execute the module
            obj_class: Class containing MiraclObj definitions for this module
            module_type: Context in which the module runs (MODULE, FLOW_MAPL3, etc.)
            runner: Function that executes the script with flags
            flag_map: Optional workflow-to-module flag mapping (e.g., {"--mpwd_atlas_dir": "--atlas_dir"})
            execute: Whether to actually execute the script or just prepare it

        Raises:
            ValueError: If a module with this name is already registered

        Examples:
            >>> registry.register(
            ...     name="tfce",
            ...     script="",
            ...     obj_class=TFCE,
            ...     module_type=ModuleType.MODULE,
            ...     runner=generic_runner,
            ...     flag_map={},
            ...     execute=False
            ... )
        """
        if name in self._registry:
            logger.error("Failed to register module '%s': already exists", name)
            raise ValueError(
                f"Module '{name}' is already registered. Use a different name or unregister the existing module first."
            )

        self._registry[name] = RegistryEntry(
            script=script,
            obj_class=obj_class,
            module_type=module_type,
            runner=runner,
            flag_map=flag_map or {},
            execute=execute,
        )
        logger.info(
            "Registered module '%s' | type=%s | execute=%s",
            name,
            module_type.name,
            execute,
        )

    def get(self, name: str) -> RegistryEntry:
        """
        Retrieve the full registry entry for a module.

        Args:
            name: Name of the registered module

        Returns:
            RegistryEntry: Complete metadata for the module

        Raises:
            KeyError: If no module with this name is registered

        Examples:
            >>> entry = registry.get("tfce")
            >>> print(entry["script"])
            ""
            >>> print(entry["module_type"])
            ModuleType.MODULE
        """
        if name not in self._registry:
            logger.error("Cannot unregister module '%s': not found", name)
            raise KeyError(
                f"Module '{name}' not found in registry. Available modules: {', '.join(self.list_modules().keys())}"
            )
        logger.debug("Retrieved module '%s' from registry", name)
        return self._registry[name]

    def list_modules(self, verbose: bool = False) -> Dict[str, RegistryEntry]:
        """
        List all registered modules.

        Args:
            verbose: If True, prints a formatted summary to stdout

        Returns:
            Dict mapping module names to their full registry entries

        Examples:
            >>> modules = registry.list_modules()
            >>> print(modules.keys())
            dict_keys(['tfce', 'plot_warped_data', 'conversion'])

            >>> registry.list_modules(verbose=True)
            Registered Modules (3 total):
            ============================================================
            - tfce
                Type    : MODULE
                Script  :
                Runner  : generic_runner
                Class   : TFCE
                Execute : False
            ...
        """
        if verbose:
            self._print_module_summary()

        return dict(self._registry)

    def has(self, name: str) -> bool:
        """
        Check if a module is registered.

        Args:
            name: Name of the module to check

        Returns:
            True if the module exists in the registry, False otherwise

        Examples:
            >>> registry.has("tfce")
            True
            >>> registry.has("nonexistent_module")
            False
        """
        return name in self._registry

    def unregister(self, name: str) -> None:
        """
        Remove a module from the registry.

        Args:
            name: Name of the module to unregister

        Raises:
            KeyError: If no module with this name is registered

        Examples:
            >>> registry.unregister("tfce")
            >>> registry.has("tfce")
            False
        """
        if name not in self._registry:
            raise KeyError(f"Cannot unregister '{name}': module not found in registry")
        del self._registry[name]
        logger.info("Unregistered module '%s'", name)

    def _print_module_summary(self) -> None:
        """Print a formatted summary of all registered modules."""
        if not self._registry:
            print("No modules registered.")
            return

        print(f"\nRegistered Modules ({len(self._registry)} total):")
        print("=" * 60)

        for name, entry in self._registry.items():
            runner_name = self._get_runner_name(entry["runner"])
            class_name = entry["obj_class"].__name__
            module_type_name = entry["module_type"].name

            print(f"* {name}")
            print(f"    Type    : {module_type_name}")
            print(f"    Script  : {entry['script'] or '(empty)'}")
            print(f"    Runner  : {runner_name}")
            print(f"    Class   : {class_name}")
            print(f"    Execute : {entry['execute']}")

            if entry["flag_map"]:
                print(f"    Flags   : {len(entry['flag_map'])} workflow mappings")
            print()

    @staticmethod
    def _get_runner_name(runner: Callable) -> str:
        """Extract a readable name from a runner function."""
        # Check if it's a wrapped runner with original stored
        if hasattr(runner, "_original_runner"):
            return runner._original_runner.__name__
        return runner.__name__

    def __len__(self) -> int:
        """Return the number of registered modules."""
        return len(self._registry)

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for checking module existence."""
        return self.has(name)

    def __repr__(self) -> str:
        """Return a string representation of the registry."""
        module_names = list(self._registry.keys())
        if len(module_names) > 5:
            shown = ", ".join(module_names[:5])
            return f"MiraclRegistry({len(self)} modules: {shown}, ...)"
        else:
            shown = ", ".join(module_names)
            return f"MiraclRegistry({len(self)} modules: {shown})"
