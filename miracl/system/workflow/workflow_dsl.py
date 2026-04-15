"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Workflow DSL parser and evaluator.

Provides a domain-specific language (DSL) for workflow configuration, supporting:
    - ref:     Reference to workflow variables
    - pattern: String templating with embedded expressions
    - fn:      Whitelisted function calls
    - literal: Static values i.e. actual string is parsed

Example:
    >>> expr = parse_expression("pattern:{ref:vars.base}/output/{ref:conv.name}.nii.gz")
    >>> result = expr.evaluate(context, {})
"""

# =====================================================================================
# IMPORTS
# =====================================================================================

from __future__ import annotations
import ast
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union

# =====================================================================================
# FUNCTION REGISTRY
# =====================================================================================


class LazyFunctionRegistry(dict):
    """
    A registry that supports both direct callables and lazy-loaded string paths.
    This is supposed to prevent import coupling of functions to the DSL system.
    Instead of importing the functions, they will be resolved as string paths and
    only imported when called in a worklfow config file.

    Example:
        "my_func": "path.to.module:function_name"
    """

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if isinstance(value, str) and ":" in value:
            import importlib

            try:
                module_path, func_name = value.split(":")
                module = importlib.import_module(module_path)
                value = getattr(module, func_name)
                self[key] = value  # Neat little cache for resolved function
            except (ImportError, AttributeError) as e:
                raise ImportError(
                    f"MIRACLang could not lazy-load function '{key}' from '{value}': {e}"
                )
        return value

    def __contains__(self, key):
        return super().__contains__(key)


# -------------------------------------------------------------------------------------
# WHITELISTED FUNCTIONS
# -------------------------------------------------------------------------------------
# Only functions registered here can be called in the workflow configuration!
# This prevents malicious function injections.
# -------------------------------------------------------------------------------------

ALLOWED_FUNCTIONS = LazyFunctionRegistry(
    {
        "nifti_output_filename": lambda name, voxel: f"{name}_{voxel}um.nii.gz",
        "format_name": lambda name, voxel: f"MyOutput_{voxel}",
        "join_strings": lambda items: "_".join(str(i) for i in items),
        "dx_pad_zero": lambda x: f"0{x}" if 0 <= x <= 9 else str(x),
        "create_ort2std_file": "miracl.system.miracl_utilfns.utilfns_module_helpers:create_ort2std_file",
    }
)


# =====================================================================================
# NAMESPACED CONTEXT
# =====================================================================================
# Replaces the flat Dict[str, Any] that was previously threaded through
# evaluate() calls. Instead of a single dict with "instance.var" string keys,
# we now have explicit namespaces: one per module instance, plus "vars" for
# workflow-level variables.
#
# This eliminates the key collision risk that existed when two instances of the
# same module type (e.g. conv and convtest) or a module named "vars" could
# silently overwrite each other in the flat dict.
#
# RESERVED_NAMESPACES: names that cannot be used as module instance names.
# "vars" is reserved for the workflow-level variables block.
# =====================================================================================

RESERVED_NAMESPACES = {"vars"}


class Context:
    """
    Namespaced key-value store for DSL expression evaluation.

    Each namespace is a separate dict. Module instances, workflow vars, and
    any future groupings each get their own namespace, making collisions
    structurally impossible!

    Key format in DSL expressions:  namespace.variable
        e.g.  ref:conv.tiff_folder
              ref:vars.base_dir

    Raises:
        ValueError: On duplicate namespace registration.
        KeyError:   On unknown namespace or missing key, with full context
                    included in the error message to aid debugging.
    """

    def __init__(self) -> None:
        self._namespaces: Dict[str, Dict[str, Any]] = {}

    def register_namespace(self, name: str, data: Dict[str, Any]) -> None:
        """
        Register a new namespace with its initial data.

        Args:
            name: Namespace name. Must not already be registered.
            data: Initial key-value pairs for this namespace.

        Raises:
            ValueError: If the namespace name is already registered.
        """
        if name in self._namespaces:
            raise ValueError(
                f"Namespace '{name}' is already registered. Registered namespaces: {sorted(self._namespaces)}"
            )
        self._namespaces[name] = dict(data)

    def get(self, namespace: str, key: str) -> Any:
        """
        Retrieve a value from a specific namespace.

        Args:
            namespace: The namespace to look in.
            key:       The variable name within that namespace.

        Returns:
            The stored value.

        Raises:
            KeyError: If namespace or key is not found.
        """
        if namespace not in self._namespaces:
            raise KeyError(
                f"Unknown namespace '{namespace}'. Available namespaces: {sorted(self._namespaces)}"
            )
        ns = self._namespaces[namespace]
        if key not in ns:
            raise KeyError(
                f"Key '{key}' not found in namespace '{namespace}'. Available keys: {sorted(ns)}"
            )
        return ns[key]

    def set(self, namespace: str, key: str, value: Any) -> None:
        """
        Write or overwrite a value in an existing namespace.

        The namespace must already be registered. Callers should register
        namespaces explicitly via register_namespace() before writing to them.

        Args:
            namespace: Must already exist.
            key:       Variable name to set.
            value:     Value to store.

        Raises:
            KeyError: If the namespace has not been registered.
        """
        if namespace not in self._namespaces:
            raise KeyError(
                f"Cannot set key in unknown namespace '{namespace}'. Call register_namespace() first."
            )
        self._namespaces[namespace][key] = value

    def all_keys(self) -> List[str]:
        """
        Return every resolvable key in 'namespace.key' form.

        Useful for debugging and error messages.
        """
        return [f"{ns}.{k}" for ns, d in self._namespaces.items() for k in d]


# =====================================================================================
# AST NODE BASE CLASS
# =====================================================================================


class Expression(ABC):
    """
    Abstract base class for all DSL expression nodes.

    Every subclass MUST implement evaluate(). Using ABC with @abstractmethod
    ensures this is enforced at class instantiation time, not at runtime when
    evaluate() is first called.

    evaluate() accepts a Context instead of Dict[str, Any]. The cache parameter is a
    flat dict keyed by "namespace.variable" strings for caching.
    """

    @abstractmethod
    def evaluate(self, context: Context, cache: Dict[str, Any]) -> Any:
        """
        Evaluate this expression node against the namespaced context.

        Additional info regarding the Strategy Pattern that I'm using here:

            Expression (ABC)
                |-> ConstantNode.evaluate() -> returns self.value
                |-> Reference.evaluate()    -> looks up context.get()
                |-> FunctionCall.evaluate() -> calls whitelisted function
                |-> Pattern.evaluate()      -> interpolates template strings

            The point here is that each subclass has different evaluation logic but
            shares the same interface. The abstract method ensures all expression types
            can be called uniformly i.e. using a polymorphic call that works for any
            Expression type.

        Args:
            context: Namespaced store of resolved variable values.
            cache:   Memoization cache keyed by "namespace.variable" strings.

        Returns:
            The evaluated result of this expression.
        """
        ...


# =============================================================================
# CONCRETE EXPRESSION NODES
# =============================================================================


class ConstantNode(Expression):
    """
    A leaf node holding a static value that evaluates to itself.

    Named ConstantNode (not Literal) to avoid shadowing typing.Literal
    if both modules are ever used in the same namespace.
    """

    def __init__(self, value: Any) -> None:
        self.value = value

    def evaluate(self, context: Context, cache: Dict[str, Any]) -> Any:
        return self.value


class Reference(Expression):
    """
    A leaf node that resolves a namespace.key pair from the Context.

    Splits on the first dot to extract (namespace, variable) and delegates to
    Context.get(), which enforces namespace boundaries.

    Example key: "conv.tiff_folder"  ->  namespace="conv", variable="tiff_folder"
    Example key: "vars.base_dir"     ->  namespace="vars", variable="base_dir"

    The cache key remains the full "namespace.variable".

    Raises:
        ValueError: If the key does not contain a dot separator.
        KeyError:   If the namespace or variable is not found in context, with the
                    full list of available keys included.
    """

    def __init__(self, key: str) -> None:
        # Validate dot-notation at construction time
        if "." not in key:
            raise ValueError(
                f"Reference key '{key}' must use 'namespace.variable' dot-notation. Example: 'ref:conv.tiff_folder' or 'ref:vars.base_dir'"
            )
        self.key = key
        self.namespace, self.variable = key.split(".", 1)

    def evaluate(self, context: Context, cache: Dict[str, Any]) -> Any:
        if self.key in cache:
            return cache[self.key]

        try:
            value = context.get(self.namespace, self.variable)
        except KeyError:
            raise KeyError(
                f"Reference '{self.key}' could not be resolved. Available keys: {context.all_keys()}"
            )

        cache[self.key] = value
        return value


class FunctionCall(Expression):
    """
    A node that calls a whitelisted function with evaluated arguments.

    Only functions present in ALLOWED_FUNCTIONS may be called.
    This is the primary security gate for the DSL.
    """

    def __init__(self, func_name: str, args: List[Expression]) -> None:
        self.func_name = func_name
        self.args = args

    def evaluate(self, context: Context, cache: Dict[str, Any]) -> Any:
        if self.func_name not in ALLOWED_FUNCTIONS:
            raise ValueError(
                f"Function '{self.func_name}' is not whitelisted. Allowed functions: {sorted(ALLOWED_FUNCTIONS.keys())}"
            )
        func = ALLOWED_FUNCTIONS[self.func_name]
        evaluated_args = [arg.evaluate(context, cache) for arg in self.args]
        return func(*evaluated_args)


class Pattern(Expression):
    """
    A template string node that interpolates embedded expressions.

    Template syntax: "prefix_{ref:instance.var}_suffix". Expressions inside {} are
    parsed recursively via parse_expression().

    Template parts are parsed eagerly at construction time so faulty templates fail
    immediately rather than at evaluation time.
    """

    def __init__(self, template: str) -> None:
        self.parts: List[Union[str, Expression]] = []
        last_index = 0

        for match in re.finditer(r"\{([^{}]+)\}", template):
            if match.start() > last_index:
                self.parts.append(template[last_index : match.start()])
            self.parts.append(parse_expression(match.group(1).strip()))
            last_index = match.end()

        if last_index < len(template):
            self.parts.append(template[last_index:])

    def evaluate(self, context: Context, cache: Dict[str, Any]) -> str:
        evaluated_parts = [
            part.evaluate(context, cache) if isinstance(part, Expression) else part
            for part in self.parts
        ]
        return "".join(str(p) for p in evaluated_parts)


# =====================================================================================
# EXPRESSION FACTORY HELPER
# =====================================================================================


def _parse_ast_arg(node: ast.expr) -> Expression:
    """
    Recursively parse a single AST argument node into an Expression.

    Python version compatibility:
        3.7.3+  — ast.Str, ast.Num (older constant nodes)
        3.8+    — ast.Constant (unified constant node, replaces ast.Str/ast.Num)
        No dependency on ast.unparse (added in 3.9).

    Args:
        node: An AST expression node from a parsed fn: argument list.

    Returns:
        An Expression node: FunctionCall for nested calls, ConstantNode for plain
        values, or a parsed Reference/Pattern if the constant value is a DSL string
        starting with ref: or pattern:.

    Raises:
        ValueError: If the node type is not supported or a nested call uses a
                    non-plain-name function (e.g. attribute access).
    """
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError(
                f"Nested fn: calls must use plain function names, got: {ast.dump(node)}"
            )
        nested_func_name = node.func.id
        nested_args = [_parse_ast_arg(a) for a in node.args]
        return FunctionCall(nested_func_name, nested_args)

    val = None
    if isinstance(node, ast.Str):
        val = node.s
    elif isinstance(node, ast.Num):
        val = node.n
    elif isinstance(node, ast.Constant):
        val = node.value
    else:
        raise ValueError(f"Unsupported AST arg type: {ast.dump(node)}")

    # If the constant string is itself a DSL expression, parse it recursively
    if isinstance(val, str) and (val.startswith("ref:") or val.startswith("pattern:")):
        return parse_expression(val)

    return ConstantNode(val)


# =====================================================================================
# EXPRESSION FACTORY
# =====================================================================================


def parse_expression(raw: str) -> Expression:
    """
    Factory function that parses a raw DSL string into an Expression node.

    Supported prefixes:
        ref:      -> Reference node       e.g. "ref:conv.tiff_folder"
        pattern:  -> Pattern node         e.g. "pattern:{ref:conv.channame}_{ref:conv.channum}um"
        fn:       -> FunctionCall node    e.g. "fn:nifti_output_filename('ref:conv.channame', 'ref:conv.channum')"
        literal:  -> ConstantNode         e.g. "literal:some_fixed_string"

    Note:
        This function is not aware of Context! It only builds the Expression tree.
        Context is only needed at evaluate() time.

    Raises:
        ValueError: If the prefix is unknown or the fn: expression cannot be parsed.
    """
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
            args = [_parse_ast_arg(a) for a in tree.body.args]
            return FunctionCall(func_name, args)

        else:
            raise ValueError(
                f"Cannot parse fn expression — expected a plain function call: '{raw}'"
            )

    elif raw.startswith("literal:"):
        return ConstantNode(raw[len("literal:") :])

    else:
        raise ValueError(
            f"Unknown expression prefix in: '{raw}'. Expected one of: ref:, pattern:, fn:, literal:"
        )
