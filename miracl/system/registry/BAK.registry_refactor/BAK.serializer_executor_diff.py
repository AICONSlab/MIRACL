import shlex
import re
import ast
import sys  # ADDED: Needed for version check in AST parsing
from typing import Dict, Any, List, Union, Optional

from miracl.system.registry.registry_refactor.datamodels import (
    CommandPlan,
    ExecutionContext,
)

# --- Whitelisted functions ---
ALLOWED_FUNCTIONS: Dict[str, callable] = {
    "nifti_output_filename": lambda name, voxel: f"{name}_{voxel}um.nii.gz",
    "format_name": lambda name, voxel: f"MyOutput_{voxel}",
    "join_strings": lambda items: "_".join(str(i) for i in items),
}


# --- AST nodes ---
class Expression:
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

    def evaluate(self, context: Dict[str, Any], cache: Dict[str, Any]) -> Any:
        if self.key in cache:
            return cache[self.key]
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


# --- Expression parser ---
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
                # CHANGED: Added support for Python < 3.8 and Recursive Parsing
                val = None

                # 1. Extract value based on Python version
                if sys.version_info >= (3, 8) and isinstance(a, ast.Constant):
                    val = a.value
                elif isinstance(a, ast.Str):  # Python < 3.8 strings
                    val = a.s
                elif isinstance(a, ast.Num):  # Python < 3.8 numbers
                    val = a.n
                else:
                    raise ValueError(f"Unsupported AST arg type: {ast.dump(a)}")

                # 2. Recursive check: If string looks like a DSL command, parse it
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


# --- Flatten utility ---
def flatten_to_str(values: Any) -> List[str]:
    flat: List[str] = []
    if isinstance(values, (list, tuple)):
        for v in values:
            flat.extend(flatten_to_str(v))
    else:
        flat.append(str(values))
    return flat


# --- Executor ---
class SerializerExecutor:
    """
    Serializes registry objects into CLI execution plans using a nested AST DSL
    with caching, pattern/function evaluation, literals, and flattening.
    """

    @staticmethod
    def _build_flat_context(
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
    ) -> Dict[str, Any]:
        """
        Build flat context for references.
        Returns: Flat dict mapping "instance.variable" to content values
        """
        flat_context = {}

        for instance_name, module_config in workflow_config.modules.items():
            module_type = module_config.type
            class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

            for variable_name, obj_dict in parsed_module_objects[class_name].items():
                flat_key = f"{instance_name}.{variable_name}"
                flat_context[flat_key] = obj_dict["content"]

        return flat_context

    @staticmethod
    def _resolve_expression(
        expression: Union[str, Expression],
        context: Dict[str, Any],
        cache: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if cache is None:
            cache = {}
        node = (
            expression
            if isinstance(expression, Expression)
            else parse_expression(expression)
        )
        return node.evaluate(context, cache)

    @staticmethod
    def create_execution_plan(
        parsed_module_objects: Dict[str, Any],
        parsed_registry_metadata: ExecutionContext,
        workflow_config: Any,
    ) -> List[CommandPlan]:
        plans: List[CommandPlan] = []
        cache: Dict[str, Any] = {}

        # Build flat context (Snapshot of default values per instance)
        flat_context = SerializerExecutor._build_flat_context(
            parsed_module_objects, parsed_registry_metadata, workflow_config
        )

        # --- Resolve cross-module data ---
        if workflow_config.data_flow:
            for module_instance in workflow_config.execution_order:
                if module_instance not in workflow_config.data_flow:
                    continue
                data_flow_config = workflow_config.data_flow[module_instance]
                if not data_flow_config:
                    continue

                for variable_name_target, expression in data_flow_config.items():
                    resolved_value = SerializerExecutor._resolve_expression(
                        expression,
                        flat_context,
                        cache,
                    )
                    flat_value = flatten_to_str(resolved_value)

                    # CHANGED: Do NOT mutate parsed_module_objects (the class definition).
                    # Instead, update the flat_context (the instance definition).
                    target_key = f"{module_instance}.{variable_name_target}"
                    flat_context[target_key] = flat_value

        # --- Build execution plans ---
        execution_order = workflow_config.execution_order
        instance_to_module_type = {
            instance: config.type
            for instance, config in workflow_config.modules.items()
        }

        for instance_name in execution_order:
            module_type = instance_to_module_type[instance_name]

            if module_type not in parsed_registry_metadata:
                raise ValueError(f"Module type '{module_type}' not found in registry.")

            registry_item = parsed_registry_metadata[module_type]
            class_name = registry_item["obj_class"].__name__

            if class_name not in parsed_module_objects:
                raise ValueError(f"Class '{class_name}' not found in parsed objects.")

            module_item = parsed_module_objects[class_name]

            tokens = shlex.split(registry_item["script"])

            # CHANGED: Iterate over the class keys, but fetch values from the Instance Context
            for var_name, ctn in module_item.items():
                flag = f"--{ctn['cli_l_flag']}"
                if flag in registry_item["flag_map"]:
                    flag = registry_item["flag_map"][flag]

                tokens.append(flag)

                # CHANGED: Lookup Logic
                # 1. Construct the unique key for this specific instance
                context_key = f"{instance_name}.{var_name}"

                # 2. Fetch value from flat_context (modified by data_flow),
                #    fallback to class default if untouched
                content = flat_context.get(context_key, ctn["content"])

                if isinstance(content, (list, tuple)):
                    tokens.extend(str(item) for item in content)
                else:
                    tokens.append(str(content))

            plan = CommandPlan(
                module_name=module_type,
                instance_name=instance_name,
                tokens=tokens,
                runner=registry_item["runner"],
                execute=registry_item["execute"],
            )
            plans.append(plan)

        return plans
