"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Workflow variable resolver for MIRACL pipelines.

Takes a workflow configuration and registry metadata, then resolves all variable values
for every module instance before execution.

Each module instance gets its own namespace in a Context object, preventing accidental
key collisions between instances.

Used by WorkflowOrchestrator to prepare execution plans before module runners are
invoked.
"""

# =====================================================================================
# IMPORTS
# =====================================================================================

from __future__ import annotations
from typing import Any, Dict, Optional, List, Tuple
from miracl.system.workflow.workflow_dsl import (
    Context,
    Expression,
    RESERVED_NAMESPACES,
    parse_expression,
)
from miracl.system.datamodels.miraclobj_datamodel import (
    ResolvedMiraclObj,
)

# =====================================================================================
# RESOLVERS
# =====================================================================================


class WorkflowResolver:
    """
    Resolves workflow variable values by merging layers in order:

        1. Module defaults:       extracted from parsed module objects
        2. Vars expressions:      evaluated against module defaults
        3. External overrides:    injected by the caller (e.g. CLI args)
        4. Data flow expressions: computed cross-module dependencies

    Note:
        The resolver uses a namespaced Context. Each module instance and the optional
        'vars' block each get their own namespace, basically making key collisions
        impossible.

    The resolver is stateless by design, it holds no instance data!
    """

    @classmethod
    def _validate_instance_names(cls, workflow_config: Any) -> None:
        """
        Validate that no module instance name collides with a reserved namespace name.

        Called once at the start of resolve() before any context is built. Failing here
        is preferable to a confusing KeyError or silent overwrite during resolution.

        Args:
            workflow_config: Workflow config with .modules dict.

        Raises:
            ValueError: If any instance name is a reserved namespace name.
        """
        for instance_name in workflow_config.modules:
            if instance_name in RESERVED_NAMESPACES:
                raise ValueError(
                    f"Module instance name '{instance_name}' is reserved. Reserved names: {sorted(RESERVED_NAMESPACES)}. Please rename this instance in your workflow config."
                )

    @classmethod
    def _build_context(
        cls,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
    ) -> Context:
        """
        Builds a Context by registering one namespace per module instance, each
        pre-loaded with that module's default values from parsed_module_objects.

        All module namespaces are registered upfront before any resolution begins. This
        ensures that expressions in later modules can safely reference variables from
        earlier modules (including their defaults), regardless of whether those earlier
        modules have data_flow entries.
        """
        context = Context()

        # Register vars as an empty namespace if the workflow defines a vars block.
        # Previously this registered vars values as plain strings. Now we register
        # empty so vars expressions can be evaluated in Step 2 of resolve() after
        # module defaults are available.
        if getattr(workflow_config, "vars", None):
            context.register_namespace("vars", {})

        # Register one namespace per module instance, pre-loaded with defaults.
        # We iterate execution_order (not modules.items()) to respect ordering,
        # though for default population the order doesn't affect correctness.
        for instance_name in workflow_config.execution_order:
            module_config = workflow_config.modules[instance_name]
            module_type = module_config.type
            class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

            instance_defaults: Dict[str, Any] = {}
            if class_name in parsed_module_objects:
                for var_name, obj in parsed_module_objects[class_name].items():
                    instance_defaults[var_name] = obj.content

            # register_namespace() raises if name is already taken. Catches duplicate
            # instance names that somehow made it past the loader
            # TODO: I should actually double-check how the latter could possibly happen...
            context.register_namespace(instance_name, instance_defaults)

        return context

    @classmethod
    def _get_allowed_vars(
        cls,
        namespace: str,
        workflow_config: Any,
        parsed_registry_metadata: Dict[str, Any],
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
    ) -> set[str]:
        """Get the set of valid variable names for a namespace.

        Used to validate that data_flow expressions and external overrides
        target only variables that actually exist.

        Args:
            namespace: The namespace to check (module instance name or "vars").
            workflow_config: Workflow configuration.
            parsed_registry_metadata: Registry metadata.
            parsed_module_objects: Parsed module objects.

        Returns:
            Set of valid variable names for this namespace.
        """

        if namespace == "vars":
            vars_config = getattr(workflow_config, "vars", None)
            if vars_config is None:
                return set()
            return set(vars_config.keys())

        if namespace not in workflow_config.modules:
            return set()

        module_config = workflow_config.modules[namespace]
        module_type = module_config.type

        if module_type not in parsed_registry_metadata:
            raise ValueError(
                f"System Error: Registry metadata missing for module type '{module_type}' reference in instance '{namespace}'"
            )

        class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

        if class_name not in parsed_module_objects:
            raise ValueError(
                f"System Error: Schema missing for class '{class_name}' (type: {module_type})."
            )

        return set(parsed_module_objects[class_name].keys())

    @classmethod
    def resolve_hooks(
        cls,
        hook_lists: Dict[str, List[str]],
        context: Context,
        cache: Dict[str, Any],
    ) -> Dict[str, List[Any]]:
        """
        Evaluate lifecycle hook expressions against the namespaced context.

        Hooks are evaluated immediately so that:
        1. Errors in hooks are caught early (before module execution).
        2. DSL expressions (ref:, pattern:, fn:) are resolved using the current
           context.

        Args:
            hook_lists: Dict of hook_type -> list of DSL expression strings.
                        e.g. {"pre_run": ["fn:create_file(...)"]}
            context: The namespaced context with resolved variable values.
            cache: Cache for DSL expression evaluation.

        Returns:
            Dict of hook_type -> list of evaluated results.
            Note: For fn: calls, the return value is discarded but errors are raised.
        """
        VALID_HOOKS = {
            "pre_run",
            "post_run",
            "on_failure",
            "on_success",
        }

        resolved_hooks: Dict[str, List[Any]] = {k: [] for k in VALID_HOOKS}

        for hook_type, hook_strings in hook_lists.items():
            if hook_type not in VALID_HOOKS:
                raise ValueError(
                    f"Unknown hook type: '{hook_type}'. Valid hooks are: {sorted(VALID_HOOKS)}"
                )

            for hook_str in hook_strings:
                node = parse_expression(hook_str)
                node.evaluate(context, cache)

        return resolved_hooks

    @classmethod
    def resolve_with_context(
        cls,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Dict[str, Any]], Context]:
        """
        Resolves all variable values for every module instance in the workflow, and
        returns the fully populated Context alongside the flat resolved data.

        The Context is needed by callers that must evaluate DSL expressions after
        resolution. Most importantly WorkflowOrchestrator._bake_hooks() which closes
        over the Context to produce zero-arg hook callables while it is still alive.
        Once plan generation is complete the Context is no longer needed and goes out
        of scope.

        Resolution proceeds in four layers (later layers overwrite earlier ones):
            1. Module defaults:       extracted from parsed module objects.
            2. Vars expressions:      evaluated against module defaults.
            3. External overrides:    injected by the caller (e.g. CLI args).
            4. Data flow expressions: computed cross-module dependencies.

        Args:
            parsed_module_objects:    Dict of class_name -> {var_name -> ResolvedMiraclObj}.
            parsed_registry_metadata: Dict of module_type -> registry metadata.
            workflow_config:          WorkflowConfig with .modules, .execution_order, etc.
            external_context:         Optional overrides in "namespace.variable" dot-notation.

        Returns:
            Tuple of:
                - Dict of instance_name -> {var_name -> resolved_value}
                - Fully-populated Context, with one namespace per module instance
                  plus an optional "vars" namespace.

        Raises:
            ValueError: On reserved namespace names or invalid overrides.
        """
        cache: Dict[str, Any] = {}

        cls._validate_instance_names(workflow_config)

        context = cls._build_context(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
        )

        if workflow_config.vars:
            for var_name, expression in workflow_config.vars.items():
                node = (
                    expression
                    if isinstance(expression, Expression)
                    else parse_expression(expression)
                )
                resolved_value = node.evaluate(context, cache)
                context.set("vars", var_name, resolved_value)

        # Inject overrides
        if external_context:
            for key, val in external_context.items():
                if "." not in key:
                    raise ValueError(
                        f"External context key '{key}' must use 'namespace.variable' dot-notation."
                    )
                namespace, variable = key.split(".", 1)

                allowed_vars = cls._get_allowed_vars(
                    namespace,
                    workflow_config,
                    parsed_registry_metadata,
                    parsed_module_objects,
                )

                if variable not in allowed_vars:
                    if namespace == "vars" and not allowed_vars:
                        err_msg = f"Override '{key}' rejected: This workflow configuration does not define a 'vars' block, so no global variables can be overridden."
                    elif not allowed_vars:
                        err_msg = f"Override '{key}' rejected: Namespace '{namespace}' is not a valid module instance."
                    else:
                        err_msg = f"Override '{key}' rejected: Variable '{variable}' is not defined in module '{namespace}'. Available variables: {sorted(allowed_vars)}"

                    raise ValueError(err_msg)

                context.set(namespace, variable, val)

        if workflow_config.data_flow:
            for module_instance in workflow_config.execution_order:
                data_flow_config = workflow_config.data_flow.get(module_instance)
                if not data_flow_config:
                    continue

                allowed_vars = cls._get_allowed_vars(
                    module_instance,
                    workflow_config,
                    parsed_registry_metadata,
                    parsed_module_objects,
                )

                for variable_name_target, expression in data_flow_config.items():
                    if variable_name_target not in allowed_vars:
                        raise ValueError(
                            f"Variable '{variable_name_target}' is not a known variable of instance '{module_instance}'. Available variables: {sorted(allowed_vars)}. Variable incorrectly defined in YAML config?"
                        )

                    node = (
                        expression
                        if isinstance(expression, Expression)
                        else parse_expression(expression)
                    )
                    resolved_value = node.evaluate(context, cache)
                    context.set(module_instance, variable_name_target, resolved_value)

        resolved_instances: Dict[str, Dict[str, Any]] = {}

        for instance_name in workflow_config.execution_order:
            module_type = workflow_config.modules[instance_name].type
            class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

            instance_data: Dict[str, Any] = {}
            if class_name in parsed_module_objects:
                for var_name in parsed_module_objects[class_name]:
                    try:
                        instance_data[var_name] = context.get(instance_name, var_name)
                    except KeyError:
                        instance_data[var_name] = parsed_module_objects[class_name][
                            var_name
                        ].content

            resolved_instances[instance_name] = instance_data

        return resolved_instances, context

    @classmethod
    def resolve(
        cls,
        parsed_module_objects,
        parsed_registry_metadata,
        workflow_config,
        external_context=None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Thin wrapper around resolve_with_context() for callers that only need
        the flat resolved data and not the Context.

        Preserves the original public API so existing callers are unaffected. Use
        resolve_with_context() directly when the Context is needed after resolution,
        such as for baking hook expressions into callables.

        Note:
            At some point I will go through all resolve() calls to change them to
            resolve_with_context().

        Args:
            parsed_module_objects:    Dict of class_name -> {var_name -> ResolvedMiraclObj}.
            parsed_registry_metadata: Dict of module_type -> registry metadata.
            workflow_config:          WorkflowConfig with .modules, .execution_order, etc.
            external_context:         Optional overrides in "namespace.variable" dot-notation.

        Returns:
            Dict of instance_name -> {var_name -> resolved_value}.

        Raises:
            ValueError: On reserved namespace names or invalid overrides.
        """
        resolved_instances, _ = cls.resolve_with_context(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
            external_context,
        )
        return resolved_instances
