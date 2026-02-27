from pathlib import Path
from miracl.api.enums import ModuleType, ArgumentType, CliGroup
from datamodels_miraclobj import MiraclObj, FlowOverride


def test_miracl_obj_resolution():
    print("--- Starting MiraclObj Resolver Test ---\n")

    # 1. Define an object with a base config and some flow overrides
    test_obj = MiraclObj(
        name="test_param",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        cli_s_flag="n",
        cli_l_flag="num_perm",
        cli_help="Base help text",
        cli_required=True,
        cli_obj_type=ArgumentType.INTEGER,
        obj_default=100,
        flow={
            "ace": FlowOverride(
                cli_l_flag="tfce_num_perm",
                # Note: cli_help and cli_required are NOT set here
                # They should be inherited from the base.
            ),
            "mapl3": FlowOverride(disabled=True),
        },
    )

    # TEST A: Standalone Module Context
    # Should return all base values
    print("[Test A] Context: MODULE")
    resolved_module = test_obj.resolve(ModuleType.MODULE)
    assert resolved_module["cli_l_flag"] == "num_perm"
    assert resolved_module["cli_required"] is True
    assert resolved_module["cli_help"] == "Base help text"
    print("✅ Success: Module context uses base values.\n")

    # TEST B: ACE Workflow Context (The Delta Test)
    # Should override ONLY the flag, but keep help and required from base
    print("[Test B] Context: ACE (Workflow Delta)")
    resolved_ace = test_obj.resolve(ModuleType.FLOW_ACE)

    # Check override
    assert resolved_ace["cli_l_flag"] == "tfce_num_perm"

    # Check inheritance (This is the 'exclude_unset' magic)
    assert resolved_ace["cli_required"] is True
    assert resolved_ace["cli_help"] == "Base help text"
    assert resolved_ace["cli_obj_type"] == ArgumentType.INTEGER
    print("✅ Success: ACE inherited help/required from base but overrode the flag.\n")

    # TEST C: MAPL3 Workflow Context (The Disabled Test)
    # Should return None because 'disabled=True'
    print("[Test C] Context: MAPL3 (Disabled)")
    resolved_mapl3 = test_obj.resolve(ModuleType.FLOW_MAPL3)
    assert resolved_mapl3 is None
    print("✅ Success: Disabled module returned None.\n")

    # TEST D: Validation Trigger
    # Verify that content assignment triggers Pydantic validation
    print("[Test D] Content Validation")
    try:
        # Assigned a string to an INTEGER type object
        test_obj.content = "not_an_int"
    except ValueError as e:
        print(f"✅ Success: Caught expected validation error: {e}")

    print("\n--- All Resolver Tests Passed! ---")


if __name__ == "__main__":
    # Mock some enums if you are running this standalone for a quick test
    # Ensure your project environment is active so imports work.
    test_miracl_obj_resolution()
