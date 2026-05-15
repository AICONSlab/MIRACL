"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Definition of MIRACL runtime frontend layer. Includes adapter contract and
implmementations and the dispatcher that selects and invokes the appropriate adapter
at runtime.

I separated this logic from the original runtime script because clustering them all
together would cause the file to grow too large whenever a new frontend would be added
and, more importantly, I wanted to minimize coupling between adding a new frontend and
opening the runtime module. The separation means I can add new adapters here and also
lazy load them easily. As a bonus, the lazy imports don't pollute the top-level
namespace of the runtime and heavy imports like PyQt are not loaded when the CLI is
used.

I decided to duck type the contract instead of using an ABC to keep the adapter classes
lightweight. The protocol is the blueprint for what the dispatcher expects.
"""

import logging
from typing import Dict, Any, Type
from typing_extensions import Protocol

from miracl.system.workflow.workflow_config import WorkFlowConfig

logger = logging.getLogger(__name__)


#######################################################################################
# ADAPTER CONTRACT
#######################################################################################


class FrontendAdapter(Protocol):
    """
    This is the contract that defines the structure that every frontend adapter must
    adhere to. A frontend adapter only needs to gather user inputs and return them as a
    dict in the format that the downstream deserializer expects. The adapter is purely
    collecting stuff. It doesn't do any validation of inputs or registry loading etc.
    That all happens in the runtime.

    Args:
        module_objects (Dict[str, Any]): Resolved MiraclObj instances keyed by module name, as produced
        by RegistryIntrospector.get_modules_as_dict().
        meta_block (Dict[str, Any]): The registry meta block from by
        RegistryIntrospector.get_meta().
        registry_metadata (Dict[str, Any]): Flat registry metadata dict, as produced by
        RegistryIntrospector.get_registry_metadata_as_dict().
        workflow (WorkFlowConfig): The loaded workflow configuration, used by adapters
        that need to know module ordering. Currently only the PyQt adapter.

    Returns:
        dict: A dict of user-supplied values in whatever shape the deserializer expects.
    """

    def get_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
        workflow: WorkFlowConfig,
    ) -> dict: ...


#######################################################################################
# CONCRETE ADAPTERS
#######################################################################################


class CLIAdapter:
    """
    CLI frontend adapter. Serializes the resolved MiraclObj instances into an
    argparse-compatible schema, builds a CLI parser, and returns the parsed args
    namespace as a dict.

    Note:
        This is the default adapter, used whenever the user has not requested a GUI
        frontend, i.e. no --gui for sys.argv.
    """

    def get_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
        workflow: WorkFlowConfig,
    ) -> dict:
        """
        Build a CLI parser from the module schema and return parsed arguments.

        Steps:
            1. Serialize module objects and meta into a CLI-compatible schema.
            2. Build an argparse parser from that schema.
            3. Parse sys.argv which by now contains only module-level flags since
               RuntimeArgParser has already stripped runtime flags.
            4. Return the parsed result.

        Returns:
            rtype: Parsed CLI arguments as a dict-like namespace.
        """
        # Lazy import: only load the CLI subsystem when the CLI adapter is actually
        # being used.
        from miracl.api_v2.cli import MiraclCLIBuilder, MiraclObjSerializer

        serializer = MiraclObjSerializer()
        cli_input = serializer.serialize_for_cli(module_objects, meta_block)

        builder = MiraclCLIBuilder()
        builder.build_parser(cli_input)

        logger.debug("CLIAdapter: parser built, parsing sys.argv")
        return builder.parse()


class PyQtAdapter:
    """
    Frontend adapter for PyQt GUI.

    Serializes the resolved MiraclObj instances into a GUI schema and hands it to
    the GUI builder. Tab ordering is resolved from the workflow configuration with the
    idea being that the tabs are in the same order as the modules in the execution
    order in the workflow YAML. So pretty much the order that the user would expect.

    Lazy loading is particularly important here since PyQt is pretty heavyweight.
    """

    def get_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
        workflow: WorkFlowConfig,
    ) -> dict:
        """
        Build and display the PyQt GUI form and return the submitted inputs.

        Steps:
            1. Serialize module objects and meta into a GUI schema. Tab order is
               derived from the workflow so the UI matches the execution sequence.
            2. Build the PyQt form from the schema and block until submission.
            3. Return the submitted values.

        Returns:
             rtype: User-submitted form values as a dict.
        """
        # Lazy import: only load PyQt and the GUI serializers when the PyQt adapter is
        # actually being invoked.
        from miracl.system.gui.gui_hybrid_serializer import MiraclGUISerializer
        from miracl.system.gui.gui_hybrid_builder import MiraclPyQtGuiBuilder

        serializer = MiraclGUISerializer()
        schema = serializer.serialize(
            resolved_objects=module_objects,
            meta=meta_block,
            module_order=workflow.resolve_tab_order(set(registry_metadata.keys())),
        )

        builder = MiraclPyQtGuiBuilder()

        logger.debug("PyQtAdapter: form built, awaiting user submission")
        return builder.build_form(schema)


class GradioAdapter:
    """
    Frontend adapter for a Gradio web UI. Doesn't actually work. I just leave it in
    here because I experimented with Gradio when designing the adapter architecture.

    Warning:
        Again, there is no Gradio implementation in MIRACL currently. Invoking this
        adapter will raise a NotImplementedError. I leave it in here as an example of
        how a new frontend would be implemented.
    """

    def get_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
        workflow: WorkFlowConfig,
    ) -> dict:
        """
        Not yet implemented.

        Raises:
            NotImplementedError: Always.
        """
        raise NotImplementedError(
            "The Gradio frontend adapter has not been implemented yet. See the class docstring for guidance on implementing new adapters."
        )


#######################################################################################
# DISPATCHER
#######################################################################################


class FrontendDispatcher:
    """
    Selects the correct FrontendAdapter for a given frontend name and delegates
    collecting input to it.

    Importantly, the dispatcher is the single point of coupling between the runtime
    orchestrator and the adapter implementations. MiraclRuntime constructs a
    FrontendDispatcher with the frontend name from RuntimeArgs and calls gather_inputs.
    It never actually references individual adapter classes directly.

    So this is basically a local, mini registry. You add an adapter class to _registry
    with its string key. That is the only change required. The string key must match a
    valid VALID_GUI_ENGINES entry in
    miracl.system.runtime.runtime_parser.RuntimeArgParser, or "cli" for the default, so
    that RuntimeArgParser can produce a RuntimeArgs.frontend value that the dispatcher
    will accept.

    Args:
    frontend (frontend): The name of the frontend to use. Must be a key in _registry.

    Raises:
        ValueError: If frontend is not a registered key.
    """

    # Registry mapping frontend name strings to their adapter classes. The reason I'm
    # keeping this as a class-level dict is to make patching in test more straightforward.
    # However, I'm still thinking about how to approach test in MIRACL in general...
    _registry: Dict[str, Type[FrontendAdapter]] = {
        "cli": CLIAdapter,
        "pyqt": PyQtAdapter,
        "gradio": GradioAdapter,
    }

    def __init__(self, frontend: str) -> None:
        if frontend not in self._registry:
            # Raise immediately at construction time rather than at gather_inputs()
            # time so that misconfiguration is surfaced as early as possible in the
            # runtime startup sequence.
            raise ValueError(
                f"Unknown frontend engine: '{frontend}'. Valid options: {sorted(self._registry.keys())}"
            )
        self.frontend = frontend
        logger.debug("FrontendDispatcher initialised | frontend=%s", frontend)

    def gather_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
        workflow: WorkFlowConfig,
    ) -> dict:
        """
        Instantiate the selected adapter and let it collect input.

        A new adapter instance is created on each call rather than cached on the
        dispatcher. This keeps adapters stateless and avoids any risk of stale state in
        case gather_inputs would ever be  called more than once on the same dispatcher
        instance.

        Returns:
             rtype: User inputs as returned by the selected adapter's get_inputs() method.
        """
        adapter = self._registry[self.frontend]()

        logger.debug(
            "Dispatching input gathering | frontend=%s | adapter=%s",
            self.frontend,
            type(adapter).__name__,
        )

        return adapter.get_inputs(
            module_objects,
            meta_block,
            registry_metadata,
            workflow,
        )
