from types import ModuleType
from miracl.system.registry.registry_refactor.deserializer import (
    deserialize_parsed_args_to_objects,
)
from miracl.system.registry.registry_refactor.loader_clean import (
    load_registry_from_yaml,
)
from miracl.system.registry.registry_refactor.registry_introspector import (
    RegistryIntrospector,
)
from miracl.system.registry.registry_refactor.executor import (
    MiraclExecutor,
)
from miracl.system.registry.registry_refactor.serializer import MiraclObjSerializer
from miracl.system.registry.registry_refactor.cli_builder import MiraclCLIBuilder
from miracl.system.registry.registry_refactor.serializer_executor import (
    SerializerExecutor,
)
from miracl.system.registry.registry_refactor.workflow_loader import WorkFlowLoader
from pprint import pprint

from miracl.api.enums import ModuleType

registry = load_registry_from_yaml(
    # "/code/miracl/system/registry/configs/tfce_module.yaml"
    # "/code/miracl/system/registry/configs/modules.yaml"
    "/code/miracl/system/registry/configs/modules_resolver_test.yaml"
)

CLIIntrospector = RegistryIntrospector(registry)
module_objects = CLIIntrospector.get_modules_as_dict()

cli_builder_parser_input = MiraclObjSerializer.serialize_for_cli(module_objects)

# pprint(cli_builder_parser_input)

cli_builder = MiraclCLIBuilder()
_ = cli_builder.build_parser(cli_builder_parser_input)
parsed_args = cli_builder.parse()

# pprint(parsed_args)


_ = deserialize_parsed_args_to_objects(parsed_args)

parsed_module_objects = CLIIntrospector.get_modules_as_dict()
parsed_registry_metadata = CLIIntrospector.get_registry_metadata_as_dict()

print(f"PARSED_MODULE_OBJECTS: {parsed_module_objects}")
print(f"PARSED_REGISTRY_METADATA: {parsed_registry_metadata}")


workflow = WorkFlowLoader.load(
    "/code/miracl/system/registry/registry_refactor/tfce_workflow.yaml"
)

execution_plans = SerializerExecutor.create_execution_plan(
    parsed_module_objects, parsed_registry_metadata
)

print(f"EXECUTION_PLANS: {execution_plans}")

MiraclExecutor.execute(execution_plans)
for i in execution_plans:
    print(f"\n{'=' * 60}")
    print(f"Module:  {i.module_name}")
    print(f"Tokens:   {i.tokens}")
    print(f"Execute: {i.execute}")
    print(f"{'=' * 60}")
