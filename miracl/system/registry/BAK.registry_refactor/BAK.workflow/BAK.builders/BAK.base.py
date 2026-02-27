from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from miracl.system.datamodels.datamodel_miracl_objs_refactored import MiraclObj


class ExecutionPlanBuilder(ABC):
    """
    Abstract base class for all execution plan builders.

    Defines the shared contract (build_plan) and provides two protected
    validation helpers that every concrete builder can use:

        _validate_against_miracl_obj  — validates and coerces a single value
        _resolve_final_data           — applies validation across all resolved data

    Keeping validation here means concrete builders never duplicate this logic.
    A subclass can override _validate_against_miracl_obj if it needs different
    coercion behaviour (e.g. stricter validation for a dry-run builder).
    """

    @staticmethod
    def _validate_against_miracl_obj(
        var_name: str,
        value: Any,
        definition: MiraclObj,
        instance_name: str,
    ) -> Any:
        """
        Coerces and validates a single value against its MiraclObj type definition.

        Handles three cases:
            - Target type is list  -> value must already be a list
            - Value is a list, target is scalar -> element-wise coercion
            - Both scalar -> direct coercion

        After coercion, validates against cli_choices if defined.

        This is a @staticmethod because it is a pure function — it reads only
        its arguments and touches no instance state.

        Args:
            var_name:      Name of the variable being validated (for error messages).
            value:         The raw resolved value to validate.
            definition:    The MiraclObj whose cli_obj_type defines the expected type.
            instance_name: Module instance name (for error messages).

        Returns:
            The coerced value, guaranteed to match cli_obj_type.

        Raises:
            ValueError: If coercion fails or the value is not in cli_choices.
        """
        # obj_type = definition.cli_obj_type
        obj_type = definition.cli.obj_type

        # Emit None as the string "None" so downstream scripts
        # receive the flag + "None" rather than having the flag dropped entirely.
        if value is None:
            return "None"

        if obj_type is None:
            return value

        python_type = obj_type.python_type

        try:
            if python_type is list:
                if not isinstance(value, list):
                    raise ValueError(f"Expected list, got {type(value).__name__}")
                coerced = list(value)
            elif isinstance(value, list):
                coerced = [python_type(item) for item in value]
            else:
                coerced = python_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Type coercion failed for parameter '{var_name}' "
                f"in module '{instance_name}': {e}"
            ) from e

        cli_choices = definition.cli.choices
        # if definition.cli_choices is not None:
        if cli_choices is not None:
            values_to_check = coerced if isinstance(coerced, list) else [coerced]
            # invalid = [v for v in values_to_check if v not in definition.cli_choices]
            invalid = [v for v in values_to_check if v not in cli_choices]
            if invalid:
                raise ValueError(
                    # f"Invalid value(s) {invalid} for parameter '{var_name}' in module '{instance_name}'. Allowed choices: {definition.cli_choices}"
                    f"Invalid value(s) {invalid} for parameter '{var_name}' in module '{instance_name}'. Allowed choices: {cli_choices}"
                )

        return coerced

    def _resolve_final_data(
        self,
        resolved_data: Dict[str, Any],
        ParamClass: Any,
        instance_name: str,
    ) -> Dict[str, Any]:
        """
        Validates all resolved values against their MiraclObj definitions.

        For each variable:
            - If ParamClass defines it as a MiraclObj, run full validation.
            - If ParamClass defines it as something else, pass it through.
            - If ParamClass doesn't define it at all (internal variables),
              pass it through unchanged.

        This is an instance method (not @staticmethod) so subclasses can
        override it if they need to inject extra logic around the iteration,
        such as logging or skipping certain fields.

        Args:
            resolved_data: Dict of {var_name -> raw_value} from the resolver.
            ParamClass:    The container class holding MiraclObj class attributes.
            instance_name: Module instance name (for error messages).

        Returns:
            Dict of {var_name -> validated_value}, builder-agnostic.
        """
        final_data: Dict[str, Any] = {}

        for var_name, value in resolved_data.items():
            if hasattr(ParamClass, var_name):
                definition = getattr(ParamClass, var_name)
                if isinstance(definition, MiraclObj):
                    final_data[var_name] = self._validate_against_miracl_obj(
                        var_name, value, definition, instance_name
                    )
                else:
                    # Regular class attribute — pass through unchanged
                    final_data[var_name] = value
            else:
                # Not on ParamClass — internal/piped variable, pass through
                final_data[var_name] = value

        return final_data

    @abstractmethod
    def build_plan(
        self,
        instance_name: str,
        module_type: str,
        resolved_data: Dict[str, Any],
        module_param_defs: Dict[str, Any],
        registry_item: Dict[str, Any],
    ) -> Any:
        """
        Build a typed execution plan from resolved data.

        Implementations must:
            1. Call self._resolve_final_data() to validate resolved_data.
            2. Format the validated data into the target output type.

        Args:
            instance_name:    Name of this module instance in the workflow.
            module_type:      Registry key identifying the module type.
            resolved_data:    Raw {var_name -> value} dict from the resolver.
            module_param_defs: {var_name -> obj_dict} for CLI flag lookups.
            registry_item:    Full registry metadata dict for this module.

        Returns:
            A typed execution plan (CommandPlan, PythonPlan, or future types).
        """
        ...
