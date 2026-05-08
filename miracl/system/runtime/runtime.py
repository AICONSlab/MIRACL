"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

This is a convenient runtime wrapper for MIRACL devs. Instead of constructing the
runtime from scratch every time this wrapper only requires the paths to the module and
workflow configs.
"""

import sys
import logging
from typing_extensions import Protocol
from typing import Dict, Any, Type
from miracl.api_v2.registry import load_registry_from_yaml, RegistryIntrospector
from miracl.api_v2.workflow import WorkflowOrchestrator, WorkFlowLoader
from miracl.api_v2.cli import deserialize_parsed_args_to_objects

logger = logging.getLogger(__name__)


class FrontendAdapter(Protocol):
    """
    Contract that all frontend adapters must follow.
    """

    def get_inputs(
        self,
        module_objects: Dict[str, Any],
        meta_block: Dict[str, Any],
        registry_metadata: Dict[str, Any],
    ) -> dict: ...


class CLIAdapter:
    def get_inputs(self, module_objects, meta_block, registry_metadata):
        from miracl.api_v2.cli import MiraclCLIBuilder, MiraclObjSerializer

        serializer = MiraclObjSerializer()
        cli_input = serializer.serialize_for_cli(module_objects, meta_block)

        builder = MiraclCLIBuilder()
        builder.build_parser(cli_input)
        return builder.parse()


class PyQtAdapter:
    def get_inputs(self, module_objects, meta_block, registry_metadata):
        from miracl.system.gui.gui_hybrid_serializer import MiraclGUISerializer
        from miracl.system.gui.gui_hybrid_builder import MiraclPyQtGuiBuilder

        serializer = MiraclGUISerializer()
        schema = serializer.serialize(
            resolved_objects=module_objects,
            meta=meta_block,
            module_order=list(registry_metadata.keys()),
        )

        builder = MiraclPyQtGuiBuilder()
        return builder.build_form(schema)


# WARNING: There currently is no Gradio implementation. This was just used to test web
# UI's. There will probably never be a Gradio adapter but I keep it in for now to give
# MIRACL devs an indication on how to add new adapters/frontends.
class GradioAdapter:
    def get_inputs(self, module_objects, meta_block, registry_metadata):
        raise NotImplementedError("Gradio frontend is not yet implemented.")


FRONTEND_REGISTRY: Dict[str, Type[FrontendAdapter]] = {
    "cli": CLIAdapter,
    "pyqt": PyQtAdapter,
    "gradio": GradioAdapter,
}


# NOTE: Runtime orchestrator
class MiraclRuntime:
    def __init__(
        self,
        registry_config: str,
        workflow_config: str,
    ):
        self.registry_config = registry_config
        self.workflow_config = workflow_config

        self.frontend_name = self._extract_frontend_type()
        self.dry_run = self._pop_sys_flag("--dry-run")
        if self.frontend_name != "cli" and len(sys.argv) > 1:
            logger.warning(
                f"Ignoring leftover CLI arguments {sys.argv[1:]} because the '{self.frontend_name}' GUI was requested."
            )

    def _extract_frontend_type(self) -> str:
        """
        Looks for '--gui'. If found, checks if the next token is a known GUI engine.
        Removes the matched tokens from sys.argv and returns 'cli', 'pyqt' (default),
        or the explicitly requested engine.
        """
        if "--gui" not in sys.argv:
            return "cli"

        idx = sys.argv.index("--gui")
        sys.argv.pop(idx)  # Remove the '--gui' flag

        valid_guis = [k for k in FRONTEND_REGISTRY.keys() if k != "cli"]

        if idx < len(sys.argv) and sys.argv[idx] in valid_guis:
            return sys.argv.pop(idx)

        return "pyqt"

    def _pop_sys_flag(self, flag: str) -> bool:
        """
        Removes a flag from sys.argv if present and returns True.
        """
        if flag in sys.argv:
            sys.argv.remove(flag)
            return True
        return False

    def _parse_frontend_inputs(
        self, module_objects, meta_block, registry_metadata
    ) -> dict:
        """
        Delegates input gathering to the registered frontend adapter.
        """

        adapter_class = FRONTEND_REGISTRY.get(self.frontend_name)

        if not adapter_class:
            raise ValueError(f"Unknown frontend engine: '{self.frontend_name}'")

        adapter = adapter_class()

        logger.debug(f"Routing user inputs to {adapter_class.__name__}...")

        return adapter.get_inputs(module_objects, meta_block, registry_metadata)

    def run(self):
        logger.info(
            f"Initializing MiraclRuntime | Frontend: {self.frontend_name.upper()} | Dry Run: {self.dry_run}"
        )

        registry = load_registry_from_yaml(self.registry_config)
        workflow = WorkFlowLoader.load(self.workflow_config)

        introspector = RegistryIntrospector(registry)
        module_objects = introspector.get_modules_as_dict()
        registry_metadata = introspector.get_registry_metadata_as_dict()
        meta_block = introspector.get_meta()

        user_inputs = self._parse_frontend_inputs(
            module_objects,
            meta_block,
            registry_metadata,
        )

        populated_modules = deserialize_parsed_args_to_objects(
            parsed_args=user_inputs,
            resolved_objects=module_objects,
        )

        orchestrator = WorkflowOrchestrator()
        plans = orchestrator.generate_plans(
            parsed_module_objects=populated_modules,
            parsed_registry_metadata=registry_metadata,
            workflow_config=workflow,
        )

        if self.dry_run:
            logger.info("--- DRY RUN ENABLED: Generated Execution Plans ---")
            for plan in plans:
                logger.info(
                    f"Plan | Instance: {plan.instance_name} | "
                    f"Runner: {getattr(plan, 'runner', type(plan).__name__)} | "
                    f"Command: {getattr(plan, 'execute', 'N/A')}"
                )
            return plans

        return orchestrator.execute_plans(plans)
