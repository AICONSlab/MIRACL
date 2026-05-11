import yaml
from typing import Dict
from pathlib import Path

from miracl.system.workflow.workflow_config import (
    WorkFlowConfig,
    ModuleInstanceConfig,
)
from miracl.system.logger import get_logger

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
# This is MIRACL's structured logger. The ``__name__`` dunder ensures log records
# are attributed to this module's fully-qualified dotted path, which makes it easy to
# filter in production logs.
logger = get_logger(__name__)


class WorkFlowLoader:
    """
    Loads workflow YAML files.

    Simple loader that just parses YAML and creates a WorkflowConfig object.
    No validation - just parsing.
    """

    @staticmethod
    def _expand_modules(modules: Dict) -> Dict:
        """
        Expand shorthand module definitions:

            conversion@raw: {}
            ->
            raw:
              type: conversion
              params: {}

            conversion@raw:           conversion@raw:
              params:                   hooks:
                down: 10         or       pre_run:
            ->                              - "fn:create_ort2std_file(...)"
            raw:                ->
              type: conversion          raw:
              params:                     type: conversion
                down: 10                  hooks:
                                            pre_run:
                                              - "fn:create_ort2std_file(...)"

        The value dict is unpacked as keyword arguments into ModuleInstanceConfig,
        so any field defined on that model (params, hooks) is supported transparently.
        """
        logger.debug("Expanding workflow modules | raw_modules=%s", modules)

        expanded = {}

        for key, value in modules.items():
            if "@" not in key:
                logger.error("Invalid module declaration: '%s'", key)
                raise ValueError(
                    f"Invalid module declaration '{key}'. Expected '<module_type>@<instance_name>'."
                )

            module_type, instance_name = key.split("@", 1)

            if not module_type or not instance_name:
                logger.error("Module declaration missing type or instance: '%s'", key)
                raise ValueError(
                    f"Invalid module declaration '{key}'. Both type and instance name are required."
                )

            if instance_name in expanded:
                logger.error(
                    "Duplicate module instance name detected: '%s'", instance_name
                )
                raise ValueError(f"Duplicate module instance name '{instance_name}'.")

            # NOTE: When a module has no content ({}), value is None or {}. However,
            # for a module with hooks, value is {"hooks": {"pre_run": [...], "post_run": [...]}}.
            # The entire dict is being passed as params here, so that hooks is silently
            # swallowed and ModuleInstanceConfig is constructed with empty hooks.
            expanded[instance_name] = ModuleInstanceConfig(
                type=module_type,
                **(value or {}),
            )
            logger.debug(
                "Created ModuleInstanceConfig | instance_name=%s | type=%s | params=%s | object=%s",
                instance_name,
                module_type,
                value or {},
                expanded[instance_name],
            )

        logger.info("Completed module expansion | total=%d", len(expanded))
        return expanded

    @staticmethod
    def load(yaml_path: str) -> WorkFlowConfig:
        """
        Load a workflow YAML file.

        Args:
            yaml_path: Path to workflow YAML file

        Returns:
            WorkflowConfig object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is malformed or missing required fields
        """
        logger.info("Loading workflow YAML | path=%s", yaml_path)

        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            logger.error("Workflow YAML file not found | path=%s", yaml_path)
            raise FileNotFoundError(f"Workflow file not found: {yaml_path}")

        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)

        logger.debug("Raw workflow YAML loaded | data=%s", data)

        if not data:
            logger.error("Workflow YAML file is empty | path=%s", yaml_path)
            raise ValueError(f"Workflow file is empty: {yaml_path}")

        if "modules" not in data:
            logger.error("Workflow YAML missing 'modules' section | path=%s", yaml_path)
            raise ValueError("Workflow YAML must define 'modules'")

        logger.info("Expanding modules in workflow YAML | path=%s", yaml_path)
        data["modules"] = WorkFlowLoader._expand_modules(data["modules"])

        try:
            workflow = WorkFlowConfig(**data)
            logger.success("Workflow YAML parsed successfully | path=%s", yaml_path)
            logger.debug("Parsed workflow object | workflow=%s", workflow)
        except Exception as e:
            logger.error(
                "Failed to parse workflow YAML | path=%s | error=%s", yaml_path, e
            )
            raise ValueError(f"Failed to parse workflow YAML {yaml_path}: {e}") from e

        return workflow
