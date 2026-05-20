"""
Top-level orchestration class for the MIRACL runtime! Kind of a big deal!

The MiraclRuntime is what pulls the workflow architecture together. It owns the startup
sequence and coordinates all of the subsystems that sit below it:
    RuntimeArgParser     ->  parse --gui/--dry-run
    load_registry        ->  build the in-memory module catalog
    WorkFlowLoader       ->  load the workflow configuration
    RegistryIntrospector ->  extract module objects and metadata
    FrontendDispatcher   ->  collect user inputs via the selected UI
    deserialize          ->  populate MiraclObj instances from raw inputs
    WorkflowOrchestrator ->  generate execution plans
    runners              ->  actually invoked by the orchestrator

This class doesn't do any parsing, knows which frontend adapters exist or builds
anything really. It just naively accepts the pre-build RuntimeArgs class and trusts it
completely (typing this out, I realize that I should maybe implement a safety check
here :D)

This is a nice separation that allows the orchestration logic in the run method to be
read and understood without knowing anything about argparse, PyQt, or other frontend
adapters. Each subsystem is replaceable independently.

For testing RuntimeArgs can be used to pass args with dependency injection!
"""

import sys
import logging
from typing import List, Optional

from miracl.api_v2.registry import load_registry_from_yaml, RegistryIntrospector
from miracl.api_v2.workflow import WorkflowOrchestrator, WorkFlowLoader
from miracl.api_v2.cli import deserialize_parsed_args_to_objects

from miracl.system.runtime.runtime_parser import RuntimeArgParser, RuntimeArgs
from miracl.system.runtime.frontend import FrontendDispatcher

# ADDED: WorkflowGraph integration
from miracl.system.workflow.workflow_graph import (
    WorkflowGraph,
    CircularDependencyError,
)

logger = logging.getLogger(__name__)


class MiraclRuntime:
    """
    Convenient orchestration wrapper for MIRACL pipelines.

    Given paths to a registry config i.e. modules YAML and a workflow config YAML, this
    class drives the full pipeline from argument collection to plan generation in a
    single, sweet run call.

    Example usage:
        from miracl.system.runtime.bootstrap import configure_runtime
        configure_runtime()

        from miracl.system.runtime import MiraclRuntime
        runtime = MiraclRuntime(
            registry_config="/path/to/modules.yaml",
            workflow_config="/path/to/workflow.yaml",
        )
        runtime.run()

    Args:
       registry_config (str): Path to module YAML config
       workflow_config (str): Path to workflow YAML config
       args (Runtime args | None): Pre-built runtime arguments. When None (default),
                                   RuntimeArgParser().parse() is called automatically
                                   and sys.argv is used as the source. Pass an explicit
                                   RuntimeArgs instance to skip sys.argv entirely. This
                                   is mostly useful for testing
    """

    def __init__(
        self,
        registry_config: str,
        workflow_config: str,
        args: Optional[RuntimeArgs] = None,
    ) -> None:
        self.registry_config = registry_config
        self.workflow_config = workflow_config

        # If no RuntimeArgs were injected, parse them from sys.argv now. This is the
        # only place in the runtime that touches sys.argv and it does so by delegating
        # entirely to RuntimeArgParser, which handles the mutation in a more controlled
        # manner.
        self.args: RuntimeArgs = (
            args if args is not None else RuntimeArgParser().parse()
        )

        # Warn if leftover CLI tokens are present when a GUI was requested. A non-CLI
        # frontend does not use sys.argv for module inputs, so any remaining tokens are
        # likely a user mistake (e.g. they added --help but forgot to remove the --gui
        # flag, or they are mixing GUI and CLI invocation styles, or they are
        # biologists in which case they are not reading this).
        if self.args.frontend != "cli" and len(sys.argv) > 1:
            logger.warning(
                "Ignoring leftover CLI arguments %s because the '%s' GUI was requested. Remove these arguments or omit --gui.",
                sys.argv[1:],
                self.args.frontend,
            )

        logger.debug(
            "MiraclRuntime initialised | frontend=%s | dry_run=%s",
            self.args.frontend,
            self.args.dry_run,
        )

    def run(self) -> Optional[List]:
        """
        Execute the full MIRACL pipeline.

        This is kind of important so the docstring will be very detailed.

        The pipeline runs in a fixed sequence:
          1.  Registry loading: Reads registry_config and builds the in-memory
                                miracl.system.registry.registry.MiraclRegistry.
          2.  Workflow loading: Reads workflow_config and builds a
                                miracl.system.workflow.workflow_config.WorkFlowConfig
                                that describes module ordering and tab structure.
          2b. DAG construction: Builds and validates the WorkflowGraph from the
                                workflow config. Fails fast on circular dependencies
                                before any user input is gathered.
          3.  Introspection: Extracts the module objects, registry metadata, and meta
                             block from the registry. These are the inputs that every
                             frontend adapter and the deserializer expect.
          4.  Input gathering: Delegates to FrontendDispatcher, which selects the
                               correct adapter (CLI or PyQt etc.) and returns the raw
                               user inputs as a dict.
          5.  Deserialisation: Populates
                               miracl.system.datamodels.miraclobj_datamodel.MiraclObj
                               instances from the raw inputs dict. This is where string
                               values from argparse (or the GUI) are coerced into the
                               correct Python types and validated against the module
                               schemas.
          6.  Plan generation: The miracl.api_v2.workflow.WorkflowOrchestrator converts
                               populated module objects into execution plans. Each plan
                               describes the runner, the command, and the arguments for
                               one module invocation.
          7.  Dry-run short-circuit: If --dry-run was set, the plans and DAG structure
                                     are logged and returned without invoking any
                                     runners.
          8.  Execution: execute_plans() is called with the graph for status tracking.

        Returns:
            list | None: The list of ExecutionPlan instances when dry_run is True,
                         otherwise the return value of execute_plans().
        """
        logger.info(
            "MiraclRuntime.run() starting | frontend=%s | dry_run=%s",
            self.args.frontend,
            self.args.dry_run,
        )

        ###############################################################################
        # STEP 1: LOAD THE REGISTRY
        ###############################################################################
        # The registry is a pure in-memory catalog of module classes, runners, flag
        # maps, and metadata. It does not execute anything.
        registry = load_registry_from_yaml(self.registry_config)

        ###############################################################################
        # STEP 2: LOAD THE WORKFLOW CONFIGURATION
        ###############################################################################
        # The workflow config describes which modules participate in this pipeline,
        # their execution order, and (for GUI frontends) their tab order.
        workflow = WorkFlowLoader.load(self.workflow_config)

        ###############################################################################
        # STEP 2b: BUILD AND VALIDATE THE EXECUTION DAG
        ###############################################################################
        # Built here — before input gathering — because the graph depends only on the
        # workflow config, not on user input. A circular dependency in the config should
        # fail immediately with a clear error rather than deadlocking at runtime after
        # the user has already filled in a form.
        graph = WorkflowGraph(workflow)
        try:
            graph.validate()
        except CircularDependencyError as exc:
            logger.error(
                "Workflow DAG validation failed — aborting before user input | error=%s",
                exc,
            )
            raise

        logger.debug(
            "Workflow DAG validated | nodes=%d | edges=%d",
            len(graph.nodes),
            len(graph.edges),
        )

        ###############################################################################
        # STEP 3: INTROSPECT THE REGISTRY
        ###############################################################################
        # The introspector translates the raw registry entries into the structured
        # dicts that the frontend adapters and the deserializer expect. Separating
        # introspection from the registry itself keeps the registry as a plain catalog
        # and gives us one place to evolve the output schema.
        introspector = RegistryIntrospector(registry)
        module_objects = introspector.get_modules_as_dict()
        registry_metadata = introspector.get_registry_metadata_as_dict()
        meta_block = introspector.get_meta()

        logger.debug(
            "Introspection complete | modules=%d",
            len(module_objects),
        )

        ###############################################################################
        # STEP 4: GATHER USER INPUTS VIA THE SELECTED FRONTEND
        ###############################################################################
        # FrontendDispatcher owns all knowledge of which adapter to use and how to
        # invoke it. The runtime only knows that it will get back a dict of user inputs.
        dispatcher = FrontendDispatcher(self.args.frontend)
        user_inputs = dispatcher.gather_inputs(
            module_objects,
            meta_block,
            registry_metadata,
            workflow,
        )

        ###############################################################################
        # STEP 5: DESERIALISE RAW INPUTS INTO POPULATED MiraclObj INSTANCES
        ###############################################################################
        # The deserializer coerces and validates the raw string/value inputs from the
        # frontend into the typed MiraclObj fields that the orchestrator needs.
        populated_modules = deserialize_parsed_args_to_objects(
            parsed_args=user_inputs,
            resolved_objects=module_objects,
        )

        ###############################################################################
        # STEP 6: GENERATE EXECUTION PLANS
        ###############################################################################
        # The orchestrator combines the populated module objects with the registry
        # metadata (runner references, flag maps, execute strings) and the workflow
        # config (ordering) to produce one ExecutionPlan per module invocation.
        orchestrator = WorkflowOrchestrator()
        plans = orchestrator.generate_plans(
            parsed_module_objects=populated_modules,
            parsed_registry_metadata=registry_metadata,
            workflow_config=workflow,
        )

        logger.debug("Execution plans generated | count=%d", len(plans))

        ###############################################################################
        # STEP 7: DRY-RUN SHORT-CIRCUIT
        ###############################################################################
        # When --dry-run is set we log the plans and DAG structure, then return without
        # executing. This lets callers (e.g. CI, tests) inspect what would have run.
        if self.args.dry_run:
            logger.info("DRY RUN enabled — skipping execution | plans=%d", len(plans))

            logger.info("--- Workflow DAG: Parallel Stages ---")
            for i, stage in enumerate(graph.parallel_stages()):
                logger.info("  Stage %d: %s", i, ", ".join(stage))

            logger.info("--- Workflow DAG: Status Summary ---")
            for instance, status in graph.status_summary().items():
                logger.info("  %s: %s", instance, status)

            graph.to_dot(path="dry_run_graph.dot", show_vars=False)

            for plan in plans:
                logger.info(
                    "Plan | instance=%s | runner=%s | command=%s",
                    plan.instance_name,
                    getattr(plan, "runner", type(plan).__name__),
                    getattr(plan, "execute", "N/A"),
                )
            return plans

        ###############################################################################
        # STEP 8: EXECUTE PLANS
        ###############################################################################
        # Passes the graph so execute_plans() can update node statuses as each module
        # runs (PENDING → RUNNING → DONE, or FAILED with cascade on error).
        # WorkflowOrchestrator.execute_plans() accepts graph=None for backward
        # compatibility with callers that don't have a graph.
        return orchestrator.execute_plans(plans, graph=graph)
