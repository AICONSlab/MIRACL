from __future__ import annotations
import shlex
from typing import Any, Dict, List
from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
    ArgumentAction,
    ResolvedMiraclObj,
)
from miracl.system.registry.registry_refactor.workflow.builders.base import (
    ExecutionPlanBuilder,
)
from miracl.system.registry.registry_refactor.workflow. import CommandPlan
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class CLICommandBuilder(ExecutionPlanBuilder):
    """
    Builds CommandPlan instances containing subprocess-ready CLI token lists.

    Handles two flag categories:
        - Boolean/store flags (STORE_TRUE / STORE_FALSE): emits the flag only,
          no value token. The flag is only emitted when content is truthy.
        - Value flags (all others): emits the flag followed by stringified
          value tokens. Both flag and tokens are skipped if content is empty.

    Variables not present in module_param_defs are skipped entirely —
    they have no CLI flag and must not produce orphaned value tokens.
    """

    def _flatten_and_stringify(self, value: Any) -> List[str]:
        """
        Recursively flattens nested lists/tuples and converts atomic values
        to strings. None values are silently dropped.

        Args:
            value: Any value — scalar, list, tuple, or nested combination.

        Returns:
            Flat list of string tokens ready for CLI insertion.
        """
        result: List[str] = []
        if isinstance(value, (list, tuple)):
            for item in value:
                result.extend(self._flatten_and_stringify(item))
        elif value is None:
            pass
        else:
            result.append(str(value))
        return result

    def build_plan(
        self,
        instance_name: str,
        module_type: str,
        resolved_data: Dict[str, Any],
        module_param_defs: Dict[str, ResolvedMiraclObj],
        registry_item: Dict[str, Any],
    ) -> CommandPlan:
        """
        Validates resolved data and produces a CommandPlan with CLI tokens.

        Steps:
            1. Retrieve and verify obj_class from registry metadata.
            2. Validate all resolved values via _resolve_final_data().
            3. Build CLI token list from script base + per-variable flags/values.

        Args:
            instance_name:     Name of this module instance in the workflow.
            module_type:       Registry key for this module type.
            resolved_data:     Raw {var_name -> value} from the resolver.
            module_param_defs: {var_name -> obj_dict} used for CLI flag lookup.
            registry_item:     Registry metadata including script, runner, execute,
                               obj_class, and optional flag_map.

        Returns:
            CommandPlan with fully assembled token list.

        Raises:
            ValueError: If obj_class is missing or validation fails.
        """
        logger.info(
            "Building CLI command plan | instance=%s | module_type=%s",
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
                f"Module '{module_type}' (instance: '{instance_name}') has no 'obj_class' in the registry metadata. Cannot validate or build command."
            )

        # Step 1: Validate — shared, builder-agnostic
        final_data = self._resolve_final_data(resolved_data, ParamClass, instance_name)

        logger.debug(
            "Resolved data ready for CLI plan | instance=%s | data=%s",
            instance_name,
            final_data,
        )

        # Step 2: Build CLI tokens
        tokens = shlex.split(registry_item["script"])

        for var_name, content in final_data.items():
            # Variables with no CLI flag definition are skipped entirely.
            # This covers internal/piped variables that have no CLI representation.
            if var_name not in module_param_defs:
                logger.warning(
                    "Skipping unresolved CLI variable | instance=%s | var=%s | content=%s",
                    instance_name,
                    var_name,
                    content,
                )
                continue

            param_def = module_param_defs[var_name]
            # cli_flag_base = param_def.get("cli_l_flag")
            cli_flag_base = param_def.cli.l_flag
            cli_action = param_def.cli.action

            if not cli_flag_base:
                logger.debug(
                    "No CLI flag for variable | instance=%s | var=%s",
                    instance_name,
                    var_name,
                )
                continue

            flag = f"--{cli_flag_base}"
            # Apply flag remapping if the registry defines aliases
            flag = registry_item.get("flag_map", {}).get(flag, flag)

            # cli_action = param_def.get("cli_action")

            if cli_action in (ArgumentAction.STORE_TRUE, ArgumentAction.STORE_FALSE):
                # Boolean flag — emit flag only when the value is truthy.
                # No value token follows the flag.
                if content:
                    tokens.append(flag)
                    logger.debug(
                        "Boolean CLI flag added | instance=%s | var=%s | flag=%s",
                        instance_name,
                        var_name,
                        flag,
                    )
                else:
                    logger.debug(
                        "Boolean CLI flag skipped | instance=%s | var=%s | flag=%s | content=%s",
                        instance_name,
                        var_name,
                        flag,
                        content,
                    )
            else:
                # Value flag — emit flag + stringified value tokens as a unit.
                # Skip entirely if the content resolves to nothing (None / empty).
                value_tokens = self._flatten_and_stringify(content)
                if value_tokens:
                    tokens.append(flag)
                    tokens.extend(value_tokens)
                    logger.debug(
                        "Value CLI flag added | instance=%s | var=%s | flag=%s | tokens=%s",
                        instance_name,
                        var_name,
                        flag,
                        value_tokens,
                    )
                else:
                    logger.debug(
                        "Value CLI flag skipped | instance=%s | var=%s | flag=%s | content=%s",
                        instance_name,
                        var_name,
                        flag,
                        content,
                    )

        logger.info(
            "CLI command plan built successfully | instance=%s | total_tokens=%d",
            instance_name,
            len(tokens),
        )

        return CommandPlan(
            module_name=module_type,
            instance_name=instance_name,
            tokens=tokens,
            runner=registry_item["runner"],
            execute=registry_item["execute"],
        )
