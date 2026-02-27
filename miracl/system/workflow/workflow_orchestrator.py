from __future__ import annotations

from typing import Any, Dict, List, Optional

from miracl.system.workflow.command_builders.base_builder import (
    ExecutionPlanBuilder,
)
from miracl.system.workflow.workflow_resolver import WorkflowResolver

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
from miracl.system.datamodels.miraclobj_datamodel import (
    ResolvedMiraclObj,
)
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class WorkflowOrchestrator:
    """
    Coordinates the full workflow execution planning pipeline.

    Responsibilities:
        1. Delegate data resolution to WorkflowResolver.
        2. Delegate plan formatting to the injected ExecutionPlanBuilder.

    The builder is injected at construction time (Strategy pattern), so the
    orchestrator itself has no knowledge of CLI vs Python vs any future format.
    Swapping builders (e.g. for testing or a different execution target) requires
    no changes to the orchestrator.

    Example usage:
        orchestrator = WorkflowOrchestrator(builder=CLICommandBuilder())
        plans = orchestrator.generate_plans(
            parsed_module_objects=...,
            parsed_registry_metadata=...,
            workflow_config=...,
            external_context={"conv_instance.tiff_folder": "/data/tiffs"},
        )
    """

    def __init__(self, builder: ExecutionPlanBuilder) -> None:
        self.builder: ExecutionPlanBuilder = builder
        self.resolver = WorkflowResolver()

        logger.info(
            "WorkflowOrchestrator initialized with builder | builder=%s",
            type(builder).__name__,
        )

    def generate_plans(
        self,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        """
        Resolves all workflow variables and produces one execution plan per module instance.

        The two stages are deliberately separated:
            - Resolution (WorkflowResolver) is pure data transformation with no
              awareness of how data will be formatted or executed.
            - Building (ExecutionPlanBuilder) is pure formatting with no awareness
              of where data came from or how it was resolved.

        Args:
            parsed_module_objects:    Dict of class_name -> {var_name -> obj_dict}.
            parsed_registry_metadata: Dict of module_type -> registry metadata,
                                      including obj_class, script, runner, execute.
            workflow_config:          Workflow config with .modules, .execution_order,
                                      and optional .data_flow.
            external_context:         Optional flat dict of dot-notation overrides
                                      (e.g. from CLI arguments or test fixtures).

        Returns:
            Ordered list of execution plans (one per instance in execution_order).
            Plan type depends on the injected builder.
        """
        # Stage 1: Pure data resolution
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
            "Resolved workflow instances | instances=%s", resolved_instances.keys()
        )

        plans = []

        # Stage 2: Format each resolved instance into a typed execution plan
        for instance_name in workflow_config.execution_order:
            module_type = workflow_config.modules[instance_name].type
            registry_item = parsed_registry_metadata[module_type]
            class_name = registry_item["obj_class"].__name__
            module_param_defs = parsed_module_objects[class_name]
            resolved_data = resolved_instances[instance_name]

            plan = self.builder.build_plan(
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
