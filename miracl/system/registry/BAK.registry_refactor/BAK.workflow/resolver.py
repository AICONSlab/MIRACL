from __future__ import annotations

from typing import Any, Dict, Optional

from miracl.system.registry.registry_refactor.workflow. import (
    Context,
    Expression,
    RESERVED_NAMESPACES,
    parse_expression,
)
from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
    ResolvedMiraclObj,
)


class WorkflowResolver:
    """
    Resolves workflow variable values by merging layers in order:

        1. Module defaults  — extracted from parsed module objects
        2. Vars expressions — evaluated against module defaults
        3. External overrides — injected by the caller (e.g. CLI args)
        4. Data flow expressions — computed cross-module dependencies

    Refactors:
      - The resolver now uses a namespaced Context instead of a flat
        dict. Each module instance and the optional 'vars' block each get their
        own namespace, making key collisions structurally impossible.
      - vars resolution is now a dedicated Step 2 (previously vars were
        registered as plain strings in _build_context). Vars values are now parsed
        as DSL expressions, allowing them to reference CLI-provided module values.
      - Both methods are @classmethods rather than @staticmethods so that
        subclasses can override individual steps. For example, a
        CachingWorkflowResolver could override _build_context() and
        resolve() would automatically call the overridden version via
        the class method.

    The resolver is stateless by design — it holds no instance data.
    """

    @classmethod
    def _validate_instance_names(cls, workflow_config: Any) -> None:
        """
        Validate that no module instance name collides with a reserved
        namespace name.

        Called once at the start of resolve() before any context is built.
        Failing here is preferable to a confusing KeyError or silent overwrite
        during resolution.

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
        Replaces _build_flat_context().

        Builds a Context by registering one namespace per module instance,
        each pre-loaded with that module's default values from parsed_module_objects.

        All module namespaces are registered upfront before any resolution
        begins. This ensures that expressions in later modules can safely
        reference variables from earlier modules (including their defaults),
        regardless of whether those earlier modules have data_flow entries.

        The vars namespace is now registered here as an empty dict
        (if workflow_config.vars is defined) rather than pre-populated with
        plain string values. Actual vars resolution happens in Step 2 of
        resolve(), where vars expressions are evaluated as DSL expressions
        against the already-populated module namespaces.

        Args:
            parsed_module_objects:    Dict of class_name -> {var_name -> obj_dict}.
            parsed_registry_metadata: Dict of module_type -> registry metadata.
            workflow_config:          Workflow config with .modules and .execution_order.

        Returns:
            Context with one namespace per module instance, all pre-loaded
            with defaults. The vars namespace is registered but empty —
            it is populated in resolve() Step 2.
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
                # for var_name, obj_dict in parsed_module_objects[class_name].items():
                #     instance_defaults[var_name] = obj_dict["content"]
                for var_name, obj in parsed_module_objects[class_name].items():
                    instance_defaults[var_name] = obj.content

            # register_namespace() raises if name is already taken, which
            # catches duplicate instance names that slipped past the loader.
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
        if namespace == "vars":
            # Check if 'vars' block exists in config
            vars_config = getattr(workflow_config, "vars", None)
            if vars_config is None:
                return set()
            return set(vars_config.keys())

        # Handle module instances
        if namespace not in workflow_config.modules:
            return set()

        module_config = workflow_config.modules[namespace]
        module_type = module_config.type

        if module_type not in parsed_registry_metadata:
            raise ValueError(
                f"System Error: Registry metadata missing for module type '{module_type}' reference in instance '{namespace}'"
            )

        class_name = parsed_registry_metadata[module_type]["obj_class"].__name__

        # Check object schema
        if class_name not in parsed_module_objects:
            raise ValueError(
                f"System Error: Schema missing for class '{class_name}' (type: {module_type})."
            )

        return set(parsed_module_objects[class_name].keys())

    @classmethod
    def resolve(
        cls,
        parsed_module_objects: Dict[str, Dict[str, ResolvedMiraclObj]],
        parsed_registry_metadata: Dict[str, Any],
        workflow_config: Any,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Resolves all variable values for every module instance in the workflow.

        Resolution order (later layers overwrite earlier ones):
            1. Module defaults (from parsed_module_objects)   — via _build_context()
            2. Vars expressions (from workflow_config.vars)   — evaluated as DSL
            3. External overrides (from external_context)     — written into Context
            4. Data flow expressions (from workflow_config.data_flow)

        Uses Context throughout instead of a flat dict.
        External overrides still use "namespace.variable" dot-notation, but
        are now written via Context.set() which enforces that the namespace
        exists. This means an override targeting a non-existent instance will
        raise a KeyError immediately rather than silently creating a dangling key.

        vars resolution is now Step 2 — a dedicated pass that
        evaluates each vars entry as a DSL expression against the module
        defaults populated in Step 1. This allows vars to reference
        CLI-provided module values (e.g. "ref:conv.base_dir").

        Ordering note: vars are evaluated against module default values as
        they exist after Step 1. If a module variable is later overridden by
        data_flow (Step 4), any vars expression that referenced it will hold
        the pre-data_flow value, not the updated one. For values that are
        modified by data_flow, reference the module variable directly in
        data_flow expressions rather than routing through vars.

        Args:
            parsed_module_objects:    Dict of class_name -> {var_name -> obj_dict}.
            parsed_registry_metadata: Dict of module_type -> registry metadata.
            workflow_config:          Workflow config with .modules, .execution_order,
                                      and optional .data_flow and .vars.
            external_context:         Optional flat dict of overrides in
                                      "namespace.variable" dot-notation, e.g.
                                      {"conv.tiff_folder": "/custom/path"}.

        Returns:
            Dict of instance_name -> {var_name -> resolved_value} for every
            instance in workflow_config.execution_order.
        """
        cache: Dict[str, Any] = {}

        # Validate instance names before doing any work
        cls._validate_instance_names(workflow_config)

        context = cls._build_context(
            parsed_module_objects,
            parsed_registry_metadata,
            workflow_config,
        )
        # Step 2: Resolve vars expressions
        # Vars values are now parsed as DSL expressions and evaluated
        # against the module namespaces populated in Step 1. This allows vars
        # to reference CLI-provided module values such as "ref:conv.base_dir".
        # The vars namespace was registered as empty in _build_context() and
        # is populated here entry by entry.
        if workflow_config.vars:
            for var_name, expression in workflow_config.vars.items():
                node = (
                    expression
                    if isinstance(expression, Expression)
                    else parse_expression(expression)
                )
                resolved_value = node.evaluate(context, cache)
                context.set("vars", var_name, resolved_value)

        # Step 3: Inject external overrides
        # Previously Step 2. Instead of flat_context[key] = val,
        # we parse the "namespace.variable" key and write via Context.set(),
        # which raises if the namespace doesn't exist rather than silently
        # creating it. External overrides can target any namespace including
        # "vars", allowing runtime override of any vars entry if needed.
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
                        err_msg = f"Override '{key}' rejected: This workflow configuration does not define a 'vars' block, so no global variables can be overriden."
                    elif not allowed_vars:
                        err_msg = f"Override '{key}' rejected: Namespace '{namespace}' is not a valid module instance."
                    else:
                        err_msg = f"Override '{key}' rejected: Variable '{variable}' is not defined in module '{namespace}'. Availabe variables: {sorted(allowed_vars)}"

                    raise ValueError(err_msg)

                context.set(namespace, variable, val)

        # Step 4: Resolve data flow expressions in execution order
        # Previously Step 3. Execution order matters — later modules
        # may reference values set by earlier modules in the same flow.
        # context.set() replaces flat_context[target_key] = ...
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

                # This is an important validation step. It checks the override key
                # value against the class object keys and raises an error if the
                # key is not present in the dict. Not checking this will cause a
                # non-existent variable to be added which also causes the dsl
                # resolution to fail.
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
                    # Pass Context instead of flat dict
                    resolved_value = node.evaluate(context, cache)
                    # Write result back into the instance's namespace
                    context.set(module_instance, variable_name_target, resolved_value)

        # Step 5: Restructure into per-instance dicts for the builders
        # Previously Step 4. Reads from Context.get() instead of
        # flat_context.get().
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
                        # Fallback to raw default if somehow absent from context.
                        # In practice this should never trigger given Step 1
                        # pre-populates all namespaces, but kept for safety.
                        # instance_data[var_name] = parsed_module_objects[class_name][
                        #     var_name
                        # ]["content"]
                        instance_data[var_name] = parsed_module_objects[class_name][
                            var_name
                        ].content

            resolved_instances[instance_name] = instance_data

        return resolved_instances
