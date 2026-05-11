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
from miracl.system.workflow.workflow_dsl import parse_expression, Context
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

        resolved_instances, context = WorkflowResolver.resolve_with_context(
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

            instance_config = workflow_config.modules[instance_name]
            plan.hooks = self._bake_hooks(
                {
                    "pre_run": list(instance_config.hooks.pre_run),
                    "post_run": list(instance_config.hooks.post_run),
                    "on_failure": list(instance_config.hooks.on_failure),
                    "on_success": list(instance_config.hooks.on_success),
                },
                context,
                instance_name,
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

        For each plan, executes hooks in the following order:
            1. pre_run hooks (before module runner)
            2. Module runner
            3a. on_success + post_run hooks (if runner succeeds)
            3b. on_failure hooks (if runner fails)

        Pre-resolved hooks (callables) are stored in the plan and executed directly.
        This separation ensures the resolver handles evaluation and the orchestrator
        handles execution only.

        Args:
            plans: Ordered list of ExecutionPlan objects from generate_plans().

        Returns:
            List of results in execution order. Each result is whatever the runner
            returns (e.g., CompletedProcess for CLI runners).

        Raises:
            UnregisteredRunnerError: If a runner is not in the runner map.
            Exception: Re-raises any exception from the runner or hooks.
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

            # -------------------------------------------------------------------------
            # 1. Execute pre_run hooks (pre-resolved)
            # -------------------------------------------------------------------------
            self._execute_hooks(
                plan.hooks.get("pre_run", []), "pre_run", plan.instance_name
            )

            # -------------------------------------------------------------------------
            # 2. Execute the module runner
            # -------------------------------------------------------------------------
            try:
                result = plan.runner(*runner_config.get_payload(plan))

                # ---------------------------------------------------------------------
                # 3a. Success: Execute on_success and post_run hooks
                # ---------------------------------------------------------------------
                self._execute_hooks(
                    plan.hooks.get("on_success", []), "on_success", plan.instance_name
                )
                self._execute_hooks(
                    plan.hooks.get("post_run", []), "post_run", plan.instance_name
                )

                results.append(result)

            except Exception as e:
                # ---------------------------------------------------------------------
                # 3b. Failure: Execute on_failure hooks, then re-raise
                # ---------------------------------------------------------------------
                logger.error(
                    "Plan '%s' failed with error: %s",
                    plan.instance_name,
                    str(e),
                )

                self._execute_hooks(
                    plan.hooks.get("on_failure", []), "on_failure", plan.instance_name
                )

                raise  # Re-raise the original exception

        logger.success("All plans executed | total=%d", len(results))
        return results

    @staticmethod
    def _bake_hooks(
        hook_lists: Dict[str, List[str]],
        context: Context,
        instance_name: str,
    ) -> Dict[str, List[Any]]:
        """
        Parse hook DSL strings and bake each one into a zero-arg callable that
        closes over the resolved context.

        Baking happens during generate_plans() while the context is alive.
        execute_plans() then just calls each closure without needing the context.

        Args:
            hook_lists: Raw hook strings from the workflow config, keyed by hook type.
            context: Fully resolved workflow context.

        Returns:
            Dict of hook_type -> list of zero-arg callables.

        Raises:
            ValueError: On unknown hook type or unparseable DSL expression.
        """
        VALID_HOOKS = {"pre_run", "post_run", "on_failure", "on_success"}
        baked: Dict[str, List[Any]] = {k: [] for k in VALID_HOOKS}

        def _make_hook(node: Any, ctx: Context) -> Any:
            """Factory that captures node and context correctly in a closure."""
            cache: Dict[str, Any] = {}

            def _hook() -> None:
                node.evaluate(ctx, cache)

            return _hook

        for hook_type, hook_strings in hook_lists.items():
            if hook_type not in VALID_HOOKS:
                raise ValueError(
                    f"Unknown hook type: '{hook_type}'. Valid hooks: {sorted(VALID_HOOKS)}"
                )
            for hook_str in hook_strings:
                node = parse_expression(hook_str)
                baked[hook_type].append(_make_hook(node, context))
                logger.debug(
                    "Hook baked | instance=%s | type=%s | expr=%s",
                    instance_name,
                    hook_type,
                    hook_str,
                )

        return baked

    def _execute_hooks(
        self,
        hook_list: List[Any],
        hook_type: str,
        instance_name: str,
    ) -> None:
        for hook in hook_list:
            try:
                hook()
                logger.debug(
                    "Hook executed | type=%s | instance=%s",
                    hook_type,
                    instance_name,
                )
            except Exception as e:
                logger.error(
                    "Hook '%s' failed for instance '%s': %s",
                    hook_type,
                    instance_name,
                    str(e),
                )
                raise

    # def _execute_hooks(
    #     self,
    #     hook_list: List[Any],
    #     hook_type: str,
    #     instance_name: str,
    # ) -> None:
    #     """Execute a list of pre-resolved hook results.
    #
    #     Hooks are pre-evaluated by the resolver. This method only executes
    #     the stored callable results. Any exceptions from hooks propagate up.
    #
    #     Args:
    #         hook_list: List of pre-resolved hook results (callables or values).
    #         hook_type: Type of hooks being executed (e.g., 'pre_run', 'on_failure').
    #         instance_name: Module instance name for logging context.
    #
    #     Raises:
    #         Exception: Propagates any errors from hook execution.
    #     """
    #     for hook_result in hook_list:
    #         try:
    #             if callable(hook_result):
    #                 hook_result()  # Execute the resolved function
    #             # Non-callable results (e.g., reference values) are silently ignored
    #             # as hooks are intended for side-effects only.
    #         except Exception as e:
    #             logger.error(
    #                 "Hook '%s' failed for instance '%s': %s",
    #                 hook_type,
    #                 instance_name,
    #                 str(e),
    #             )
    #             raise

    # def execute_plans(self, plans: List[ExecutionPlan]) -> List[Any]:
    #     """
    #     Execute a list of previously generated execution plans.
    #
    #     Hooks are executed in the following order:
    #         1. pre_run hooks (before module)
    #         2. Module runner
    #         3a. on_success + post_run hooks (if runner succeeds)
    #         3b. on_failure hooks (if runner fails)
    #
    #     The payload extractor is resolved from the runner map so the orchestrator never
    #     inspects plan fields or plan types directly.
    #
    #     Returns:
    #         List of results in the same order as the input plans. Each result is
    #         whatever the plan's runner returns: a CompletedProcess for CLI plans,
    #         a Namespace for Python plans, or raw tokens/args for dry runs (execute=False).
    #
    #     Raises:
    #         UnregisteredRunnerError: If a runner is not in the runner map.
    #         subprocess.CalledProcessError: Propagated from generic_runner
    #                                        on non-zero exit codes.
    #     """
    #     logger.info("Executing plans | total=%d", len(plans))
    #     results = []
    #
    #     for plan in plans:
    #         logger.info(
    #             "Executing plan | instance=%s | module=%s | execute=%s",
    #             plan.instance_name,
    #             plan.module_name,
    #             plan.execute,
    #         )
    #
    #         runner_config = self._get_runner_config(
    #             plan.runner,
    #             context=f"instance '{plan.instance_name}'",
    #         )
    #
    #         # -------------------------------------------------------------------------
    #         # 1. Execute pre_run hooks
    #         # -------------------------------------------------------------------------
    #         if plan.hooks and plan.hooks.get("pre_run"):
    #             for hook_str in plan.hooks["pre_run"]:
    #                 self._execute_hook("pre_run", hook_str, plan.instance_name)
    #
    #         # ------------------------------------------------------------
    #         # 2. Execute the module runner
    #         # ------------------------------------------------------------
    #         try:
    #             logger.debug(
    #                 "Dispatching plan | instance=%s | plan_type=%s",
    #                 plan.instance_name,
    #                 runner_config.plan_type.__name__,
    #             )
    #
    #             result = plan.runner(*runner_config.get_payload(plan))
    #
    #             logger.debug(
    #                 "Plan executed | instance=%s | result=%s",
    #                 plan.instance_name,
    #                 result,
    #             )
    #
    #             # ---------------------------------------------------------------------
    #             # 3a. Success: Execute on_success and post_run hooks
    #             # ---------------------------------------------------------------------
    #             if plan.hooks:
    #                 for hook_str in plan.hooks.get("on_success", []):
    #                     self._execute_hook("on_success", hook_str, plan.instance_name)
    #                 for hook_str in plan.hooks.get("post_run", []):
    #                     self._execute_hook("post_run", hook_str, plan.instance_name)
    #
    #             results.append(result)
    #
    #         except Exception as e:
    #             # ------------------------------------------------------------
    #             # 3b. Failure: Execute on_failure hooks, then re-raise
    #             # ------------------------------------------------------------
    #             logger.error(
    #                 "Plan '%s' failed with error: %s",
    #                 plan.instance_name,
    #                 str(e),
    #             )
    #
    #             if plan.hooks:
    #                 for hook_str in plan.hooks.get("on_failure", []):
    #                     self._execute_hook("on_failure", hook_str, plan.instance_name)
    #
    #             raise  # Re-raise the original exception
    #
    #     logger.success("All plans executed | total=%d", len(plans))
    #     return results

    # def _execute_hook(
    #     self,
    #     hook_type: str,
    #     hook_str: str,
    #     instance_name: str,
    # ) -> None:
    #     """
    #     Parse and execute a single hook expression.
    #
    #     Args:
    #         hook_type: Type of hook (pre_run, post_run, etc.) for logging.
    #         hook_str: DSL expression string (e.g., "fn:create_file(...)").
    #         instance_name: Module instance name for logging.
    #
    #     Raises:
    #         Exception: Propagates any errors from hook execution.
    #     """
    #     from miracl.system.workflow.workflow_dsl import parse_expression
    #
    #     try:
    #         node = parse_expression(hook_str)
    #         # Execute the hook. Result is discarded for side-effect functions
    #         node.evaluate(context, cache)
    #         logger.debug(
    #             "Hook executed | type=%s | instance=%s | hook=%s",
    #             hook_type,
    #             instance_name,
    #             hook_str,
    #         )
    #     except Exception as e:
    #         logger.error(
    #             "Hook '%s' failed for instance '%s': %s",
    #             hook_type,
    #             instance_name,
    #             str(e),
    #         )
    #         raise

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
