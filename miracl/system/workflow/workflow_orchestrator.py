"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Workflow orchestration for MIRACL pipelines.

Coordinates the execution pipeline:
    1. Resolve variables (via WorkflowResolver)
    2. Generate execution plans (via builder classes)
    3. Execute plans (via runners)

The orchestrator itself is agnostic to runner types, plan structures, and builder
implementations. All specifics live in runners/runner_plan_type_map.py.
"""

# =====================================================================================
# IMPORTS
# =====================================================================================

from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from miracl.system.workflow.workflow_resolver import WorkflowResolver
from miracl.system.datamodels.miraclobj_datamodel import ResolvedMiraclObj
from miracl.system.workflow.runners.runner_plan_type_map import (
    RUNNER_PLAN_TYPE_MAP,
    ExecutionPlan,
    RunnerConfig,
    UnregisteredRunnerError,
)
from miracl.system.logger import get_logger

logger = get_logger(__name__)

# =====================================================================================
# ORCHESTRATION
# =====================================================================================


class WorkflowOrchestrator:
    """
    Coordinates the full workflow execution planning pipeline.

    Responsibilities:
        1. Delegate data resolution to WorkflowResolver.
        2. Look up the correct builder class per module instance from the
           runner map and instantiate it fresh for each plan.
        3. Execute the generated plans via execute_plans().

    The orchestrator is fully agnostic to runner types, plan types, payload fields,
    and builder classes. All of that knowledge lives exclusively in:
        runners/runner_plan_type_map.py

    The runner map is injected at construction time, defaulting to the global
    RUNNER_PLAN_TYPE_MAP. Injecting a custom map in tests avoids touching global state.
    """

    def __init__(
        self,
        runner_map: Optional[Dict[Callable, RunnerConfig]] = None,
    ) -> None:
        """
        Initialize the orchestrator.

        Args:
            runner_map: Optional custom runner map. Defaults to global
                        RUNNER_PLAN_TYPE_MAP. Pass a custom map in tests to avoid
                        global state.
        """
        self._runner_map = runner_map or RUNNER_PLAN_TYPE_MAP
        logger.info(
            "WorkflowOrchestrator initialized | runner_map_entries=%d",
            len(self._runner_map),
        )

    def _get_runner_config(
        self,
        runner: Callable,
        context: str,
    ) -> RunnerConfig:
        """
        Look up the RunnerConfig for a runner, raising a domain-specific exception if
        it is not registered.

        Args:
            runner:  The runner callable to look up.
            context: Human-readable description of the call site, included in the error
                     message to help locate the problem.

        Returns:
            The RunnerConfig registered for this runner.

        Raises:
            UnregisteredRunnerError: If the runner is not in the runner map.
        """
        config = self._runner_map.get(runner)
        if config is None:
            raise UnregisteredRunnerError(
                f"Runner '{runner.__name__}' ({context}) is not registered in the runner map. Add it to 'runners/runner_plan_type_map.py' before use."
            )
        return config

    def generate_plans(
        self,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> List[ExecutionPlan]:
        """
        Resolves all workflow variables and produces one execution plan per module
        instance in workflow_config.execution_order.

        The builder class is resolved from the runner map per instance and instantiated
        fresh for each plan, avoiding shared state across plans, runs, and threads.

        Raises:
            UnregisteredRunnerError: If a runner declared in the registry is
                                     not in the runner map.
        """
        logger.info(
            "Generating execution plans | workflow_instances=%d | external_context=%s",
            len(workflow_config.execution_order),
            external_context,
        )

        resolved_instances = WorkflowResolver.resolve(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
            external_context,
        )

        logger.debug(
            "Resolved workflow instances | instances=%s",
            list(resolved_instances.keys()),
        )

        plans: List[ExecutionPlan] = []

        for instance_name in workflow_config.execution_order:
            module_type = workflow_config.modules[instance_name].type
            registry_item = parsed_registry_metadata[module_type]
            class_name = registry_item["obj_class"].__name__
            module_param_defs = parsed_module_objects[class_name]
            resolved_data = resolved_instances[instance_name]
            runner = registry_item["runner"]

            runner_config = self._get_runner_config(
                runner,
                context=f"module '{module_type}', instance '{instance_name}'",
            )

            builder = runner_config.builder_class()

            logger.debug(
                "Resolved builder | instance=%s | runner=%s | builder=%s",
                instance_name,
                runner.__name__,
                type(builder).__name__,
            )

            plan = builder.build_plan(
                instance_name=instance_name,
                module_type=module_type,
                resolved_data=resolved_data,
                module_param_defs=module_param_defs,
                registry_item=registry_item,
            )

            logger.debug(
                "Built execution plan | instance=%s | module_type=%s | plan=%s",
                instance_name,
                module_type,
                plan,
            )
            plans.append(plan)

        logger.success("All execution plans generated | total=%d", len(plans))
        return plans

    def execute_plans(self, plans: List[ExecutionPlan]) -> List[Any]:
        """
        Execute a list of previously generated execution plans.

        The payload extractor is resolved from the runner map so the orchestrator never
        inspects plan fields or plan types directly.

        Returns:
            List of results in the same order as the input plans. Each result is
            whatever the plan's runner returns: a CompletedProcess for CLI plans,
            a Namespace for Python plans, or raw tokens/args for dry runs (execute=False).

        Raises:
            UnregisteredRunnerError: If a runner is not in the runner map.
            subprocess.CalledProcessError: Propagated from generic_runner
                                           on non-zero exit codes.
        """
        logger.info("Executing plans | total=%d", len(plans))
        results = []

        for plan in plans:
            logger.info(
                "Executing plan | instance=%s | module=%s | execute=%s",
                plan.instance_name,
                plan.module_name,
                plan.execute,
            )

            runner_config = self._get_runner_config(
                plan.runner,
                context=f"instance '{plan.instance_name}'",
            )

            logger.debug(
                "Dispatching plan | instance=%s | plan_type=%s",
                plan.instance_name,
                runner_config.plan_type.__name__,
            )

            result = plan.runner(*runner_config.get_payload(plan))

            logger.debug(
                "Plan executed | instance=%s | result=%s",
                plan.instance_name,
                result,
            )
            results.append(result)

        logger.success("All plans executed | total=%d", len(plans))
        return results

    def run(
        self,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        This is just a convenience method. It generates plans and execute them in one call.

        generate_plans() plus execute_plans() is called separately in case a dev wants
        to inspect or modify plans before execution. Otherwise this method is fine.

        Equivalent to:
            plans = orchestrator.generate_plans(...)
            return orchestrator.execute_plans(plans)

        Use generate_plans() separately if you need to inspect or modify plans before
        execution.
        """
        logger.info(
            "run() called | workflow=%s",
            getattr(workflow_config, "name", "unknown"),
        )
        plans = self.generate_plans(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
            external_context,
        )
        return self.execute_plans(plans)
