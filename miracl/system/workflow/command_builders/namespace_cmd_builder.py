from __future__ import annotations
from argparse import Namespace
from typing import Any, Dict
from miracl.system.workflow.command_builders.base_builder import (
    ExecutionPlanBuilder,
)
from miracl.system.workflow.workflow_datamodels import PythonPlan

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
from miracl.system.datamodels.miraclobj_datamodel import (
    ResolvedMiraclObj,
)
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class PythonNamespaceBuilder(ExecutionPlanBuilder):
    """
    Builds PythonPlan instances wrapping an argparse.Namespace.

    Intended for modules that are called directly as Python functions
    rather than dispatched as subprocesses. The Namespace mirrors the
    structure argparse would produce, so module runner functions that
    already accept a parsed Namespace can be used without modification.
    """

    def build_plan(
        self,
        instance_name: str,
        module_type: str,
        resolved_data: Dict[str, Any],
        module_param_defs: Dict[str, ResolvedMiraclObj],
        registry_item: Dict[str, Any],
    ) -> PythonPlan:
        """
        Validates resolved data and produces a PythonPlan with an argparse.Namespace.

        Steps:
            1. Retrieve and verify obj_class from registry metadata.
            2. Validate all resolved values via _resolve_final_data().
            3. Set each validated value as an attribute on a Namespace.

        Args:
            instance_name:     Name of this module instance in the workflow.
            module_type:       Registry key for this module type.
            resolved_data:     Raw {var_name -> value} from the resolver.
            module_param_defs: Accepted (to satisfy abstract signature) but not
                               used — Namespace-based runners don't need flag lookup.
            registry_item:     Registry metadata including runner, execute, obj_class.

        Returns:
            PythonPlan with a populated Namespace as args.

        Raises:
            ValueError: If obj_class is missing or validation fails.
        """
        logger.info(
            "Building Python Namespace plan | instance=%s | module_type=%s",
            instance_name,
            module_type,
        )

        ParamClass = registry_item.get("obj_class")
        if not ParamClass:
            logger.error(
                "Missing obj_class in registry for module_type=%s | instance=%s",
                module_type,
                instance_name,
            )
            raise ValueError(
                f"Module '{module_type}' (instance: '{instance_name}') has no 'obj_class' in the registry metadata."
            )

        # Step 1: Validate — shared, builder-agnostic
        final_data = self._resolve_final_data(resolved_data, ParamClass, instance_name)

        logger.debug(
            "Resolved data for Python Namespace | instance=%s | data=%s",
            instance_name,
            final_data,
        )

        # Step 2: Populate Namespace
        ns = Namespace()
        for var_name, value in final_data.items():
            setattr(ns, var_name, value)
            logger.debug(
                "Set Namespace attribute | instance=%s | var=%s | value=%s",
                instance_name,
                var_name,
                value,
            )

        logger.info(
            "Python Namespace plan built successfully | instance=%s | total_vars=%d",
            instance_name,
            len(final_data),
        )

        return PythonPlan(
            module_name=module_type,
            instance_name=instance_name,
            runner=registry_item.get("runner"),
            args=ns,
            execute=registry_item.get("execute", False),
        )
