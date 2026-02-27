"""
Example usage of the clean MiraclRegistry design.

This demonstrates how the registry serves as a pure catalog/index,
while serializers and executors handle the actual work.
"""

from miracl.system.registry.registry_refactor.registry_clean import MiraclRegistry
from miracl.system.registry.registry_refactor.loader_clean import (
    load_registry_from_yaml,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType


# =============================================================================
# Example 1: Loading a registry from YAML
# =============================================================================


def example_load_registry():
    """Load and inspect a registry from a YAML config file."""

    # Load the registry
    registry = load_registry_from_yaml(
        "/code/miracl/system/registry/configs/modules.yaml"
    )

    # List all modules
    print("=== All Registered Modules ===")
    registry.list_modules(verbose=True)

    # Check if specific modules exist
    print("\n=== Module Existence Checks ===")
    print(f"Has 'tfce': {registry.has('tfce')}")
    print(f"Has 'plot_warped_data': {registry.has('plot_warped_data')}")
    print(f"Has 'nonexistent': {registry.has('nonexistent')}")

    # Alternative syntax
    print(f"'plot_warped_data' in registry: {'plot_warped_data' in registry}")

    return registry


# =============================================================================
# Example 2: Accessing registry entries
# =============================================================================


def example_access_entries(registry: MiraclRegistry):
    """Demonstrate accessing individual registry entries."""

    print("\n=== Accessing Registry Entries ===")

    # Get a module entry
    # tfce_entry = registry.get("tfce")
    # print(f"\nTFCE Module:")
    # print(f"  Script: {tfce_entry['script']}")
    # print(f"  Class: {tfce_entry['obj_class'].__name__}")
    # print(f"  Type: {tfce_entry['module_type'].name}")
    # print(f"  Execute: {tfce_entry['execute']}")
    # print(f"  Flag map: {tfce_entry['flag_map']}")

    # Get a workflow entry
    plot_entry = registry.get("plot_warped_data")
    print(f"\nPlot Warped Data Module:")
    print(f"  Script: {plot_entry['script']}")
    print(f"  Class: {plot_entry['obj_class'].__name__}")
    print(f"  Type: {plot_entry['module_type'].name}")
    print(f"  Execute: {plot_entry['execute']}")
    print(f"  Flag map entries: {len(plot_entry['flag_map'])}")

    # Show some flag mappings
    if plot_entry["flag_map"]:
        print(f"  Sample mappings:")
        for workflow_flag, module_flag in list(plot_entry["flag_map"].items())[:3]:
            print(f"    {workflow_flag} -> {module_flag}")


# =============================================================================
# Example 3: Registry as a pure index (what it should NOT do)
# =============================================================================


def example_separation_of_concerns(registry: MiraclRegistry):
    """
    Demonstrate what the registry DOES and DOES NOT do.

    The registry is a pure catalog - it provides metadata but doesn't:
    - Build flag maps (serializer's job)
    - Execute modules (executor's job)
    - Introspect MiraclObj instances (serializer's job)
    """

    print("\n=== Separation of Concerns ===")

    # ✓ CORRECT: Registry provides metadata
    entry = registry.get("plot_warped_data")
    print(f"✓ Registry provides: {entry.keys()}")

    # ✓ CORRECT: Registry checks existence
    exists = registry.has("plot_warped_data")
    print(f"✓ Registry checks existence: {exists}")

    # ✓ CORRECT: Registry lists available modules
    modules = registry.list_modules()
    print(f"✓ Registry lists modules: {list(modules.keys())[:3]}...")

    print("\n❌ Registry does NOT:")
    print("  - Build flag maps (use serializer)")
    print("  - Resolve MiraclObj instances (use serializer)")
    print("  - Execute modules (use executor)")
    print("  - Introspect class attributes (use serializer)")


# =============================================================================
# Example 4: How to use registry with serializer and executor (conceptual)
# =============================================================================


def example_workflow_with_serializer(registry: MiraclRegistry):
    """
    Demonstrate the intended workflow using registry + serializer + executor.

    Note: This is conceptual - serializer and executor are not implemented yet.
    """

    print("\n=== Conceptual Workflow ===")

    # Step 1: Get module metadata from registry
    entry = registry.get("plot_warped_data")
    print(f"1. Registry provides metadata for '{entry['obj_class'].__name__}'")

    # Step 2: Serializer builds flag map (not implemented yet)
    print(f"2. Serializer would call:")
    print(
        f"   serializer.build_flag_map({entry['obj_class'].__name__}, {entry['module_type'].name})"
    )
    print(f"   → Returns: {{'--atlas_dir': '/path', '--dpi': 300, ...}}")

    # Step 3: Serializer applies workflow mapping (if needed)
    if entry["flag_map"]:
        print(f"3. Serializer would apply workflow mapping:")
        print(
            f"   serializer.apply_workflow_mapping(flag_map, {len(entry['flag_map'])} mappings)"
        )
        print(f"   → Returns: {{'--mpwd_atlas_dir': '/path', '--mpwd_dpi': 300, ...}}")

    # Step 4: Executor runs the module
    print(f"4. Executor would call:")
    print(f"   executor.run('{entry['script']}', final_flag_map)")
    print(f"   → Executes: {entry['script'] or '(empty script)'}")


# =============================================================================
# Example 5: Manual registration (programmatic)
# =============================================================================


def example_manual_registration():
    """Demonstrate registering modules programmatically without YAML."""

    print("\n=== Manual Registration ===")

    # Create empty registry
    registry = MiraclRegistry()

    # Mock imports (in reality, these would be actual classes/functions)
    class MockClass:
        pass

    def mock_runner(script, mapping, flag_map, execute):
        print(f"Mock runner called with script: {script}")

    # Register a module manually
    registry.register(
        name="test_module",
        script="/path/to/script.py",
        obj_class=MockClass,
        module_type=ModuleType.MODULE,
        runner=mock_runner,
        flag_map={},
        execute=False,
    )

    print(f"Registered 'test_module': {registry.has('test_module')}")
    print(f"Total modules: {len(registry)}")

    # Unregister
    registry.unregister("test_module")
    print(f"After unregister: {registry.has('test_module')}")


# =============================================================================
# Run examples
# =============================================================================

if __name__ == "__main__":
    # Example 1: Load registry
    registry = example_load_registry()

    # Example 2: Access entries
    example_access_entries(registry)

    # Example 3: Separation of concerns
    example_separation_of_concerns(registry)

    # Example 4: Conceptual workflow
    # example_workflow_with_serializer(registry)

    # Example 5: Manual registration
    # example_manual_registration()
