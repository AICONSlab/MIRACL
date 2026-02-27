# Import modules from API
from miracl.api_v2.registry import (
    load_registry_from_yaml,
    RegistryIntrospector,
    MiraclObjSerializer,
    deserialize_parsed_args_to_objects,
)
from miracl.api_v2.cli import (
    MiraclCLIBuilder,
)
from miracl.api_v2.workflow import (
    WorkflowOrchestrator,
    WorkFlowLoader,
)
from miracl.api_v2.workflow.builders import (
    CLICommandBuilder,
    PythonNamespaceBuilder,
)
from pprint import pprint

# Load modules into registry from config YAML
registry = load_registry_from_yaml(
    "/code/miracl/system/registry/configs/modules_resolver_test.yaml"
)

# Instantiate CLI introspector
cli_introspector = RegistryIntrospector(registry)
# Get data of registered modulesr
module_objects = cli_introspector.get_modules_as_dict()

pprint(module_objects)

# Instantiate CLI serializer
cli_serializer = MiraclObjSerializer()
# Serialize data for CLI builder
cli_builder_parser_input = cli_serializer.serialize_for_cli(module_objects)

# Instantiate CLI builder
cli_builder = MiraclCLIBuilder()
# Build CLI parser
_ = cli_builder.build_parser(cli_builder_parser_input)
# Parse args
parsed_args = cli_builder.parse()

# Instantiate deserializer
_ = deserialize_parsed_args_to_objects(parsed_args)

# Prepare data for executor serializer
parsed_module_objects = cli_introspector.get_modules_as_dict()
parsed_registry_metadata = cli_introspector.get_registry_metadata_as_dict()

# Load workflow config
workflow = WorkFlowLoader.load(
    "/code/miracl/system/registry/registry_refactor/workflow_example_conv_reg.yaml"
)

# cli_plan_builder = CLICommandBuilder()
cli_plan_builder = PythonNamespaceBuilder()
cli_orchestrator = WorkflowOrchestrator(builder=cli_plan_builder)
cli_plans = cli_orchestrator.generate_plans(
    parsed_module_objects=parsed_module_objects,
    parsed_registry_metadata=parsed_registry_metadata,
    workflow_config=workflow,
)
for plan in cli_plans:
    print(plan)

namespace_plan_builder = CLICommandBuilder()
namespace_orchestrator = WorkflowOrchestrator(builder=namespace_plan_builder)
namespace_plans = namespace_orchestrator.generate_plans(
    parsed_module_objects=parsed_module_objects,
    parsed_registry_metadata=parsed_registry_metadata,
    workflow_config=workflow,
)

for plan in namespace_plans:
    print(plan)
