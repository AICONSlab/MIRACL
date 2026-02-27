from miracl.system.registry.registry_refactor.workflow_loader import WorkFlowLoader
from pprint import pprint

workflow = WorkFlowLoader.load(
    "/code/miracl/system/registry/registry_refactor/workflow_example.yaml"
)

print(workflow.name)
print(workflow.description)
print(workflow.version)


print(f"\nExecution Order ({len(workflow.execution_order)} modules):")
for i, module in enumerate(workflow.execution_order, 1):
    print(f"  {i}. {module}")

print(f"\nData Flow Connections:")
if workflow.data_flow:
    for target_module, overrides in workflow.data_flow.items():
        print(f"\n  {target_module}:")
        for target_input, source_ref in overrides.items():
            print(f"    {target_input} <- {source_ref}")
else:
    print("  (none)")

print(f"\nDict Object:")
pprint(workflow.model_dump())
