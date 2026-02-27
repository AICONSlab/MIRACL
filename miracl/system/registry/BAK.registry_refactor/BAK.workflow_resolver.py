import shlex
import re
import ast
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union, Optional, Callable
from argparse import Namespace
from dataclasses import dataclass

from miracl.system.registry.registry_refactor.datamodels import (
    CommandPlan,
    ExecutionContext,
)

# Note: Ensure MiraclObj is imported if you need 'isinstance' checks,
# though we handle it dynamically below to avoid circular imports if possible.
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

# =============================================================================
# 0. DATAMODELS
# =============================================================================


@dataclass
class PythonPlan:
    """
    Standardized execution plan for Python function calls.
    """

    module_name: str
    instance_name: str
    runner: Callable
    args: Any  # Can be a Pydantic Model or argparse.Namespace
    execute: bool


# =============================================================================
# 1. DSL DEFINITIONS & AST NODES
# =============================================================================

ALLOWED_FUNCTIONS: Dict[str, Callable] = {
    "nifti_output_filename": lambda name, voxel: f"{name}_{voxel}um.nii.gz",
    "format_name": lambda name, voxel: f"MyOutput_{voxel}",
    "join_strings": lambda items: "_".join(str(i) for i in items),
    "dx_pad_zero": lambda x: f"0{x}" if 0 <= x <= 9 else str(x),
}


class Expression(ABC):
    @abstractmethod
    def evaluate(self, context: Dict[str, Any], cache: Dict[str, Any]) -> Any:
        raise NotImplementedError


class Literal(Expression):
    def __init__(self, value: Any):
        self.value = value

    def evaluate(self, context: Dict[str, Any], cache: Dict[str, Any]) -> Any:
        return self.value


class Reference(Expression):
    def __init__(self, key: str):
        self.key = key

    def evaluate(self, context, cache):
        if self.key in cache:
            return cache[self.key]
        if self.key not in context:
            raise KeyError(f"Reference key '{self.key}' not found in context")
        value = context[self.key]
        cache[self.key] = value
        return value


class FunctionCall(Expression):
    def __init__(self, func_name: str, args: List[Expression]):
        self.func_name = func_name
        self.args = args

    def evaluate(self, context: Dict[str, Any], cache: Dict[str, Any]) -> Any:
        if self.func_name not in ALLOWED_FUNCTIONS:
            raise ValueError(f"Function {self.func_name} is not whitelisted")
        func = ALLOWED_FUNCTIONS[self.func_name]
        evaluated_args = [arg.evaluate(context, cache) for arg in self.args]
        return func(*evaluated_args)


class Pattern(Expression):
    def __init__(self, template: str):
        self.parts: List[Union[str, Expression]] = []
        last_index = 0
        for match in re.finditer(r"\{([^{}]+)\}", template):
            if match.start() > last_index:
                self.parts.append(template[last_index : match.start()])
            self.parts.append(parse_expression(match.group(1).strip()))
            last_index = match.end()
        if last_index < len(template):
            self.parts.append(template[last_index:])

    def evaluate(self, context: Dict[str, Any], cache: Dict[str, Any]) -> str:
        evaluated_parts = [
            part.evaluate(context, cache) if isinstance(part, Expression) else part
            for part in self.parts
        ]
        return "".join(str(p) for p in evaluated_parts)


def parse_expression(raw: str) -> Expression:
    raw = raw.strip()
    if raw.startswith("ref:"):
        return Reference(raw[len("ref:") :])
    elif raw.startswith("pattern:"):
        return Pattern(raw[len("pattern:") :])
    elif raw.startswith("fn:"):
        expr_text = raw[len("fn:") :]
        tree = ast.parse(expr_text, mode="eval")
        if isinstance(tree.body, ast.Call) and isinstance(tree.body.func, ast.Name):
            func_name = tree.body.func.id
            args: List[Expression] = []
            for a in tree.body.args:
                val = None
                # Compatilibilty shim until MIRACL's Python version is upgraded
                if sys.version_info >= (3, 8) and isinstance(a, ast.Constant):
                    val = a.value
                elif isinstance(a, ast.Str):
                    val = a.s
                elif isinstance(a, ast.Num):
                    val = a.n
                else:
                    raise ValueError(f"Unsupported AST arg type: {ast.dump(a)}")

                if isinstance(val, str) and (
                    val.startswith("ref:") or val.startswith("pattern:")
                ):
                    args.append(parse_expression(val))
                else:
                    args.append(Literal(val))
            return FunctionCall(func_name, args)
        else:
            raise ValueError(f"Cannot parse function expression: {raw}")
    elif raw.startswith("literal:"):
        return Literal(raw[len("literal:") :])
    else:
        raise ValueError(f"Unknown expression prefix in: {raw}")


# =============================================================================
# 2. THE RESOLVER (Data Logic Only)
# =============================================================================


class WorkflowResolver:
    """
    Decoupled Resolver:
    Returns pure Python dictionaries with preserved types (int, list, etc.).
    """

    @staticmethod
    def _build_flat_context(
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
    ) -> Dict[str, Any]:
        flat_context = {}
        for instance_name, module_config in workflow_config.modules.items():
            module_type = module_config.type
            class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

            if class_name in parsed_module_objects:
                for variable_name, obj_dict in parsed_module_objects[
                    class_name
                ].items():
                    flat_key = f"{instance_name}.{variable_name}"
                    flat_context[flat_key] = obj_dict["content"]
        return flat_context

    @staticmethod
    def resolve(
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        cache: Dict[str, Any] = {}

        # 1. Initialize context with defaults
        flat_context = WorkflowResolver._build_flat_context(
            parsed_module_objects, parsed_registry_metadata, workflow_config
        )

        # 2. INJECT EXTERNAL OVERRIDES
        if external_context:
            for key, val in external_context.items():
                flat_context[key] = val

        # 3. Resolve Data Flow Dependencies
        if workflow_config.data_flow:
            for module_instance in workflow_config.execution_order:
                data_flow_config = workflow_config.data_flow.get(module_instance)
                if not data_flow_config:
                    continue

                for variable_name_target, expression in data_flow_config.items():
                    node = (
                        expression
                        if isinstance(expression, Expression)
                        else parse_expression(expression)
                    )
                    resolved_value = node.evaluate(flat_context, cache)

                    target_key = f"{module_instance}.{variable_name_target}"
                    # NOTE: We preserve the raw types here.
                    flat_context[target_key] = resolved_value

        # 4. Restructure output for the Builders
        resolved_instances = {}
        for instance_name in workflow_config.execution_order:
            module_type = workflow_config.modules[instance_name].type
            class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

            instance_data = {}
            if class_name in parsed_module_objects:
                for var_name, ctn in parsed_module_objects[class_name].items():
                    key = f"{instance_name}.{var_name}"
                    # Get the final resolved value, or the default if untouched
                    instance_data[var_name] = flat_context.get(key, ctn["content"])

            resolved_instances[instance_name] = instance_data

        return resolved_instances


# =============================================================================
# 3. THE BUILDERS (Formatting Strategy)
# =============================================================================
class ExecutionPlanBuilder(ABC):
    @staticmethod
    def _validate_against_miracl_obj(
        var_name: str,
        value: Any,
        definition: MiraclObj,
        instance_name: str,
    ) -> Any:
        """
        Coerces and validates a single value against its MiraclObj type definition.
        """
        obj_type = definition.cli_obj_type

        if obj_type is None or value is None:
            return value

        python_type = obj_type.python_type

        try:
            if python_type is list:
                if not isinstance(value, list):
                    raise ValueError(f"Expected list, got {type(value).__name__}")
                return list(value)
            elif isinstance(value, list):
                return [python_type(item) for item in value]
            else:
                return python_type(value)
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Validation failed for parameter '{var_name}' "
                f"in module '{instance_name}': {e}"
            ) from e

    def _resolve_final_data(
        self,
        resolved_data: Dict[str, Any],
        ParamClass: Any,
        instance_name: str,
    ) -> Dict[str, Any]:
        """
        Validates all resolved values against their MiraclObj definitions.
        Returns a flat dict of validated values, builder-agnostic.
        """
        final_data = {}

        for var_name, value in resolved_data.items():
            if hasattr(ParamClass, var_name):
                definition = getattr(ParamClass, var_name)
                if isinstance(definition, MiraclObj):
                    final_data[var_name] = self._validate_against_miracl_obj(
                        var_name, value, definition, instance_name
                    )
                else:
                    final_data[var_name] = value
            else:
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
        pass


class CLICommandBuilder(ExecutionPlanBuilder):
    def _flatten_and_stringify(self, value: Any) -> List[str]:
        result = []
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
        instance_name,
        module_type,
        resolved_data,
        module_param_defs,
        registry_item,
    ) -> CommandPlan:
        ParamClass = registry_item.get("obj_class")
        if not ParamClass:
            raise ValueError(
                f"Module '{module_type}' (instance: {instance_name}) "
                "has no 'obj_class' in the registry metadata."
            )

        # 1. Validate — shared step
        final_data = self._resolve_final_data(resolved_data, ParamClass, instance_name)

        # 2. Format — CLI-specific
        tokens = shlex.split(registry_item["script"])
        for var_name, content in final_data.items():
            if var_name in module_param_defs:
                flag = f"--{module_param_defs[var_name]['cli_l_flag']}"
                flag = registry_item.get("flag_map", {}).get(flag, flag)
                tokens.append(flag)
                tokens.extend(self._flatten_and_stringify(content))

        return CommandPlan(
            module_name=module_type,
            instance_name=instance_name,
            tokens=tokens,
            runner=registry_item["runner"],
            execute=registry_item["execute"],
        )


class PythonNamespaceBuilder(ExecutionPlanBuilder):
    def build_plan(
        self,
        instance_name,
        module_type,
        resolved_data,
        module_param_defs,
        registry_item,
    ) -> PythonPlan:
        ParamClass = registry_item.get("obj_class")
        if not ParamClass:
            raise ValueError(
                f"Module '{module_type}' (instance: {instance_name}) "
                "has no 'obj_class' in the registry metadata."
            )

        # 1. Validate — shared step
        final_data = self._resolve_final_data(resolved_data, ParamClass, instance_name)

        # 2. Format — Namespace-specific
        ns = Namespace()
        for var_name, value in final_data.items():
            setattr(ns, var_name, value)

        return PythonPlan(
            module_name=module_type,
            instance_name=instance_name,
            runner=registry_item.get("runner"),
            args=ns,
            execute=registry_item.get("execute", False),
        )


# =============================================================================
# 4. THE ORCHESTRATOR (The Manager)
# =============================================================================


class WorkflowOrchestrator:
    """
    Coordinates the process:
    1. Asks the Resolver to calculate the data.
    2. Asks the Builder to format that data.
    """

    def __init__(self, builder: ExecutionPlanBuilder):
        self.builder = builder
        self.resolver = WorkflowResolver()

    def generate_plans(
        self,
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        # 1. Resolve Data (Pure State)
        resolved_instances = self.resolver.resolve(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
            external_context,
        )

        plans = []

        # 2. Build Formatted Plans based on chosen Strategy
        for instance_name in workflow_config.execution_order:
            module_type = workflow_config.modules[instance_name].type

            # Retrieve metadata (contains 'obj_class' needed for validation)
            registry_item = parsed_registry_metadata[module_type]

            class_name = registry_item["obj_class"].__name__

            # Retrieve parameter definitions (needed for flags lookup)
            module_param_defs = parsed_module_objects[class_name]

            # Retrieve the purely resolved data for this specific instance
            resolved_data = resolved_instances[instance_name]

            # Let the specific Builder decide how to format (and validate) this
            plan = self.builder.build_plan(
                instance_name=instance_name,
                module_type=module_type,
                resolved_data=resolved_data,
                module_param_defs=module_param_defs,
                registry_item=registry_item,
            )
            plans.append(plan)

        return plans
