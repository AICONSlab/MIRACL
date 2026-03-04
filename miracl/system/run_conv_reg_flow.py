from miracl.api_v2.registry import (
    load_registry_from_yaml,
    RegistryIntrospector,
)
from miracl.api_v2.cli import (
    MiraclCLIBuilder,
    MiraclObjSerializer,
    deserialize_parsed_args_to_objects,
)
from miracl.api_v2.workflow import (
    WorkflowOrchestrator,
    WorkFlowLoader,
)
from miracl.api_v2.workflow.cmd_builders import (
    CLICommandBuilder,
    PythonNamespaceBuilder,
)

# Load modules into registry from config YAML
registry = load_registry_from_yaml("/code/miracl/system/conv_reg_modules_config.yaml")
# Load workflow config
workflow = WorkFlowLoader.load("/code/miracl/system/conv_reg_workflow_config.yaml")

# Initialize registry introspector
introspector = RegistryIntrospector(registry)

module_objects = introspector.get_modules_as_dict()
registry_metadata = introspector.get_registry_metadata_as_dict()
meta_block = introspector.get_meta()

cli_serializer = MiraclObjSerializer()
cli_builder_parser_input = cli_serializer.serialize_for_cli(
    module_objects,
    meta_block,
)

# Instantiate CLI builder
cli_builder = MiraclCLIBuilder()
# Build CLI parser
_ = cli_builder.build_parser(cli_builder_parser_input)
# Parse args
parsed_args = cli_builder.parse()
#
# populated_modules = deserialize_parsed_args_to_objects(
#     parsed_args=parsed_args,
#     resolved_objects=module_objects,
#     strict=False,
# )
#
# # Initialize CLI command builder
# cli_plan_builder = CLICommandBuilder()
# # Initialize workflow orchestrator with CLI command builder
# cli_orchestrator = WorkflowOrchestrator(builder=cli_plan_builder)
# # Generate CLI commands for executor
# cli_plans = cli_orchestrator.generate_plans(
#     parsed_module_objects=populated_modules,
#     parsed_registry_metadata=registry_metadata,
#     workflow_config=workflow,
# )
#
# # Initialize namespace command builder
# namespace_plan_builder = PythonNamespaceBuilder()
# # Initialize workflow orchestrator with namespace command builder
# namespace_orchestrator = WorkflowOrchestrator(builder=namespace_plan_builder)
# # Generate namespace commands for executor
# namespace_plans = namespace_orchestrator.generate_plans(
#     parsed_module_objects=populated_modules,
#     parsed_registry_metadata=registry_metadata,
#     workflow_config=workflow,
# )
