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
from miracl.api_v2.registry import (
    load_registry_from_yaml,
)
from miracl.system.datamodels.datamodel_miracl_objs_refactored_introspector import (
    RegistryIntrospector,
)
from miracl.system.registry.registry_refactor.cli_serializer import (
    MiraclObjSerializer,
)
from miracl.system.registry.registry_refactor.cli_deserializer import (
    deserialize_parsed_args_to_objects,
)

# Load modules into registry from config YAML
registry = load_registry_from_yaml(
    "/code/miracl/system/registry/configs/modules_resolver_test.yaml"
)
# Load workflow config
workflow = WorkFlowLoader.load(
    "/code/miracl/system/registry/registry_refactor/workflow_example_workflow.yaml"
)

# Initialize registry introspector
introspector = RegistryIntrospector(registry)
module_objects = introspector.get_modules_as_dict()
registry_metadata = introspector.get_registry_metadata_as_dict()

cli_serializer = MiraclObjSerializer()
cli_builder_parser_input = cli_serializer.serialize_for_cli(module_objects)

# Instantiate CLI builder
cli_builder = MiraclCLIBuilder()
# Build CLI parser
_ = cli_builder.build_parser(cli_builder_parser_input)
# Parse args
parsed_args = cli_builder.parse()

populated_modules = deserialize_parsed_args_to_objects(
    parsed_args=parsed_args,
    resolved_objects=module_objects,
    strict=False,
)

# Initialize CLI command builder
cli_plan_builder = CLICommandBuilder()
# Initialize workflow orchestrator with CLI command builder
cli_orchestrator = WorkflowOrchestrator(builder=cli_plan_builder)
# Generate CLI commands for executor
cli_plans = cli_orchestrator.generate_plans(
    parsed_module_objects=populated_modules,
    parsed_registry_metadata=registry_metadata,
    workflow_config=workflow,
)

# Initialize namespace command builder
namespace_plan_builder = PythonNamespaceBuilder()
# Initialize workflow orchestrator with namespace command builder
namespace_orchestrator = WorkflowOrchestrator(builder=namespace_plan_builder)
# Generate namespace commands for executor
namespace_plans = namespace_orchestrator.generate_plans(
    parsed_module_objects=populated_modules,
    parsed_registry_metadata=registry_metadata,
    workflow_config=workflow,
)
