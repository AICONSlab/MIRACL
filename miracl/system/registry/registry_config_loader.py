"""
Code written by Jonas Osmann. Contact at j.osmann@alumni.utoronto.ca or via
https://github.com/AICONSlab/MIRACL/issues

loader_clean.py
===============

Declarative YAML-to-registry loader for the new MIRACL module system.

This module is the entry point for bootstrapping the MIRACL registry.
It bridges the gap between human-readable YAML configuration files and the
in-memory :class:`~miracl.system.registry.registry_refactor.registry_clean.MiraclRegistry`
object that the rest of the system depends on at runtime.

What this module does
---------------------
This module has one job: it reads the YAML file that the dev declared and produces a
populated :class:`~miracl.system.registry.registry_refactor.registry_clean.MiraclRegistry`
(registry). The registry itself is a pure catalog. It only records what modules exist,
where their classes live, which runner is associated with each, and what their
flag maps declare. It does not execute anything or interpret the entries beyond storing
them.

Side note: Flag maps are mappings between the flags defined in the objects and
their corresponding flags in the script that is being called. This is unfortunately
necessary until all scripts have been ported into the new MIRACL architecture i.e.
have all of their flags defined as Pydantic objects.

Typical data flow
-----------------
::

    modules.yaml
        |
        V
    load_registry_from_yaml()
        |  validates the file path
        |  parses YAML (safe_load — no arbitrary Python execution)
        |  validates schema (Pydantic ModuleConfig)
        |  dynamically imports obj_class + runner for each entry
        |  enforces workflow-specific constraints (flag_map presence)
        |  calls registry.register() for each entry
        V
    MiraclRegistry (in-memory catalog)
        |
        +--> consumed by downstream components (introspector, executor, etc.)

Module-level responsibilities
------------------------------
- Path validation (raises :exc:`FileNotFoundError` -> early rather than cryptically later)
- YAML parsing (delegates to PyYAML's ``safe_load`` -> no arbitrary Python execution)
- Schema validation (delegates to Pydantic's ``ModuleConfig``)
- Dynamic import of ``obj_class`` and ``runner`` dotted paths
- Enum coercion of ``module_type`` strings
- Workflow-specific guard: ``FLOW_*`` modules **must** declare a ``flag_map``
- Populating the registry via ``registry.register()``

Adding a new module
-------------------
To register a new module you only need to add an entry to the YAML configuration file
e.g. ``modules.yaml``. No Python changes are required unless you are introducing a
custom new module class or runner. The YAML schema is validated by
:class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`.
"""

import yaml
import importlib
from typing import Callable, Type
from pathlib import Path

# from miracl.system.registry.registry_refactor.registry_clean import MiraclRegistry
from miracl.system.registry.registry import MiraclRegistry
from miracl.system.registry.schema_validators.config_schema import ModuleConfig
from miracl.system.datamodels.miraclobj_enums import ModuleType
from miracl.system.logger import get_logger

# ---------------------------------------------------------------------------
# Module-level logger
# ---------------------------------------------------------------------------
# This is MIRACL's structured logger. The ``__name__`` dunder ensures log records
# are attributed to this module's fully-qualified dotted path, which makes it easy to
# filter in production logs.
logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _import_from_string(dotted_path: str) -> object:
    """
    Dynamically import and return an attribute from a module using its dotted path.

    This is the mechanism that allows YAML config files to reference Python
    classes and functions by name (as strings) without requiring hard-coded
    imports at the top of this file.  It is intentionally kept generic so that
    both ``obj_class`` *and* ``runner`` entries can be resolved through the same
    code path.

    .. note::
        I might have to rethink this design at some point in terms of separation of
        concerns but for now I like the generic nature of it.

    How it works
    ~~~~~~~~~~~~
    Given a dotted path such as ``"a.b.c.MyClass"``:

    1. The string is split on the **last** dot separator, yielding
       ``module_path = "a.b.c"`` and ``attr_name = "MyClass"``.
    2. ``importlib.import_module("a.b.c")`` is called - this honours the normal
       Python import method including ``sys.path``, ``__init__.py`` files,
       namespace packages etc.
    3. ``getattr(module, "MyClass")`` retrieves the class/function/constant from
       the now-imported module object.

    .. note::
        The parser can currently not traverse nested classes. However, this is by
        design since MIRACL's ``obj_classes`` entries are top level classes by convention.
        Nested class traversal needs to be added to ``_import_from_string`` if that ever
        becomes an issue.

    Why ``rsplit(".", 1)`` and not ``split(".", 1)``?
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ``rsplit`` splits from the **right**, which correctly handles deeply nested
    paths like ``"a.b.c.d.MyClass"`` - the module is everything up to the last
    dot, and the attribute is what follows it. Using left-split would incorrectly give
    ``module_path = "a"`` and ``attr_name = "b.c.d.MyClass"``.

    .. note::
        The right split method for the dotted notation also works because Python
        classes can't have '.' in their names.

    :param dotted_path: A fully-qualified dotted Python path such as
        ``'miracl.system.objs.objs_stats.objs_tfce.objs_tfce.TFCE'`` or
        ``'miracl.system.registry.runners.generic_runner.generic_runner'``.
    :type dotted_path: str

    :returns: The imported class, function, or other module-level attribute
        identified by ``dotted_path``.
    :rtype: object

    :raises ImportError: If the module portion of the path cannot be imported
        (e.g. the package does not exist, or there is a syntax error inside it).
    :raises AttributeError: If the module was imported successfully but does not
        expose an attribute with the given name.

    Examples::

        >>> TFCE = _import_from_string(
        ...     "miracl.system.objs.objs_stats.objs_tfce.objs_tfce.TFCE"
        ... )
        >>> runner = _import_from_string(
        ...     "miracl.system.registry.runners.generic_runner.generic_runner"
        ... )
    """
    # Split on the last dot so that "a.b.c.MyClass" → ("a.b.c", "MyClass").
    # If the path has no dot at all, rsplit returns a single-element list and
    # the unpacking will raise ValueError — which is intentional: a bare name
    # like "MyClass" is not a valid fully-qualified path.
    module_path, attr_name = dotted_path.rsplit(".", 1)

    # Import the parent module.  importlib.import_module is preferred over
    # __import__ because it returns the leaf module directly rather than the
    # top-level package, saving us from needing to walk the attribute chain.
    module = importlib.import_module(module_path)

    logger.debug(
        "Imported attribute successfully | module=%s | attribute=%s",
        module_path,
        attr_name,
    )

    # Retrieve and return the attribute.  getattr raises AttributeError if it
    # doesn't exist, which is propagated to the caller with a meaningful message.
    return getattr(module, attr_name)


def _parse_module_type(module_type_str: str, module_name: str) -> ModuleType:
    """
    Convert a raw YAML string to the corresponding :class:`ModuleType` enum member.

    YAML files store module types as plain strings (e.g. ``"MODULE"`` or
    ``"FLOW_MAPL3"``).  This helper validates that the string matches a known
    enum key and converts it, providing a clear error message when it doesn't.

    .. note::
        As of the Pydantic-validated config path in :func:`load_registry_from_yaml`,
        ``module_type`` is already coerced to a :class:`ModuleType` by the
        ``ModuleEntry`` schema **before** this function is reached.  This helper
        is therefore retained primarily for use in contexts where raw YAML dicts
        are consumed directly (e.g. tests, CLI tooling, or future loaders that
        bypass Pydantic).

    :param module_type_str: The raw string value read from YAML, expected to
        match one of the :class:`ModuleType` enum member **names** (not values).
        Example: ``"MODULE"``, ``"FLOW_MAPL3"``.
    :type module_type_str: str

    :param module_name: The name of the module being parsed.  Used only for
        producing a human-friendly error message.
    :type module_name: str

    :returns: The :class:`ModuleType` enum member whose ``name`` matches
        ``module_type_str``.
    :rtype: ModuleType

    :raises ValueError: If ``module_type_str`` does not correspond to any
        :class:`ModuleType` member.  The exception message lists all valid
        member names so the developer can fix the YAML without consulting the
        source code.

    Examples::

        >>> _parse_module_type("MODULE", "tfce")
        <ModuleType.MODULE: 'MODULE'>
        >>> _parse_module_type("FLOW_MAPL3", "plot_warped_data")
        <ModuleType.FLOW_MAPL3: 'FLOW_MAPL3'>
    """
    try:
        # Enum key-based lookup: ModuleType["MODULE"] → ModuleType.MODULE.
        # This is deliberately case-sensitive; YAML authors must use the exact
        # enum member name (all-caps by convention).
        return ModuleType[module_type_str]
    except KeyError:
        # Build a comma-separated list of all valid names for the error message.
        # e.name (not e.value) because lookups are by name, not by value.
        valid_types = ", ".join(e.name for e in ModuleType)

        logger.error(
            "Invalid module_type | module=%s | provided=%s | valid=%s",
            module_name,
            module_type_str,
            valid_types,
        )

        raise ValueError(
            f"Invalid module_type '{module_type_str}' for module '{module_name}'. Expected one of: {valid_types}"
        )


def _validate_workflow_config(
    module_name: str,
    module_type: ModuleType,
    flag_map: object,
) -> None:
    """
    Assert that workflow modules declare a ``flag_map`` in their YAML config.

    Background
    ~~~~~~~~~~
    ``MODULE`` type entries represent standalone tools that manage their own
    argument parsing internally.  They do **not** need a ``flag_map`` because
    the serializer does not need to translate workflow-level flags into
    module-level flags for them.

    ``FLOW_*`` type entries (e.g. ``FLOW_MAPL3``) are *steps inside a larger
    workflow pipeline*.  The pipeline's argument parser exposes a unified CLI
    surface, and the serializer uses ``flag_map`` to translate each pipeline-level
    flag into the flag(s) that the underlying module actually understands.
    Without ``flag_map`` being declared (even if empty), the serializer has no
    mapping to work from, which would cause a silent no-op or a cryptic
    ``KeyError`` deep inside the executor. As mentioned above, this is only true
    while not all MIRACL modules have been ported to the new architecture. Once
    that is done, the module parsers will be built on the same registrty as the
    workflow parses hence automatically matching flags.

    This validation runs after Pydantic has already confirmed the structural
    schema, so it is purely a *semantic* guard.

    :param module_name: Name of the module being validated (used in error messages).
    :type module_name: str

    :param module_type: The resolved :class:`ModuleType` enum value.
    :type module_type: ModuleType

    :param flag_map: The ``flag_map`` value extracted from the YAML entry.
        For workflow modules this must not be ``None``. An empty dict ``{}``
        is explicitly allowed (meaning "this step takes no flags from the
        pipeline CLI").
    :type flag_map: object

    :raises ValueError: If ``module_type`` is not ``MODULE`` and ``flag_map``
        is ``None`` (i.e. the key was entirely absent from the YAML and
        Pydantic defaulted it to ``None``).

    .. note::
        ``flag_map`` is allowed to be an empty dict — the error is only raised
        when the key is **completely absent** (``None``).  An empty dict is a
        valid explicit declaration that the workflow step has no flag translations.
    """
    # Return immediately as standalone MODULE entries are exempt from this check.
    # They handle their own CLI parsing, i.e. they don't have any flags that they
    # could match to, and therefore have no need for a flag_map.
    if module_type == ModuleType.MODULE:
        return

    # For all FLOW_* (and any future workflow-type) entries, flag_map must be
    # explicitly declared. None here means the key was missing from the YAML
    # entirely, which is detected as a misconfiguration.
    if flag_map is None:
        logger.error(
            "Workflow module missing flag_map | module=%s | type=%s",
            module_name,
            module_type.name,
        )
        raise ValueError(
            f"Workflow module '{module_name}' (type: {module_type.name}) must define a 'flag_map' in the YAML config. It can be empty (flag_map: {{}}) but cannot be omitted."
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_registry_from_yaml(yaml_path: str) -> MiraclRegistry:
    """
    Parse a YAML configuration file and return a fully populated :class:`MiraclRegistry`.

    This is the primary public function of this module. Virtually all
    production code that needs a registry (which eventually will be all production
    code) should call this function (or a higher-level wrapper that calls it).

    .. note::
        The migration to the new architecture poses several challenges. MIRACL is
        used in production so the refactoring can't break existing versions. The
        refactoring is happening on a per module/workflow basis.

    What this function does step by step
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    1. **Path validation** - Converts ``yaml_path`` to a :class:`pathlib.Path`
       and raises :exc:`FileNotFoundError` immediately if it does not exist.
       This surfaces misconfiguration early rather than as an opaque I/O error
       deep inside a pipeline run.

    2. **YAML parsing** - Reads the file with ``yaml.safe_load``. The
       ``safe_load`` variant is used deliberately: it refuses to deserialise
       arbitrary Python objects, preventing code execution from a config file
       that hasn't been declared by MIRACL devs.

    3. **Schema validation** - Wraps the parsed dict in
       :class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`
       (a Pydantic root model). This step:

       * Confirms every required field (``script``, ``obj_class``,
         ``module_type``, ``runner``) is present.
       * Applies type coercions (e.g. ``module_type`` string -> ``ModuleType``
         enum; ``execute`` absent -> ``False``; ``flag_map`` absent -> ``{}``).
       * Raises a descriptive :exc:`ValueError` for any schema violation,
         including the full Pydantic error detail.

    4. **Dynamic import loop** - For each module entry:

       a. Calls :func:`_import_from_string` twice. Once for ``obj_class``
          (the class that holds ``MiraclObj`` field definitions) and once for
          ``runner`` (the callable that executes the module).
       b. Calls :func:`_validate_workflow_config` to enforce the ``flag_map``
          requirement for workflow modules.
       c. Calls :meth:`~MiraclRegistry.register` to add the entry to the
          catalog.

    5. **Logging** - Emits ``logger.success`` after all modules are registered,
       reporting the total count. Individual modules streamed at ``INFO`` level but
       to the console and log files to avoid flooding production logs meant for the
       end user.

    Design decisions
    ~~~~~~~~~~~~~~~~
    * **Pure catalog**: The registry built here stores *references* to classes
      and functions.  It does not instantiate classes, invoke runners, or build
      flag maps. Those are the introspector's, serializer's and executor's jobs,
      respectively. This means the registry can be constructed at import time without
      triggering any side effects.

    * **Fail-fast**: All validation (path, schema, imports, workflow config)
      happens in this function before any module is registered. A single
      broken entry causes the entire load to fail with a clear error rather
      than partially populating the registry and causing subtle runtime bugs.

    * **Pydantic first**: Schema enforcement is delegated to Pydantic rather
      than implemented with ad-hoc ``if key not in config`` guards. This means
      automatic type coercions, default values, and rich error messages for free.

    :param yaml_path: Absolute or relative path to the YAML file containing
        module definitions. Example:
        ``"/code/miracl/system/configs/modules.yaml"``.
    :type yaml_path: str

    :returns: A :class:`MiraclRegistry` instance populated with one entry per
        module defined in the YAML file. The registry is ready to be handed
        to the registry introspector immediately.
    :rtype: MiraclRegistry

    :raises FileNotFoundError: If the file at ``yaml_path`` does not exist.
    :raises yaml.YAMLError: If the file exists but contains invalid YAML syntax.
    :raises ValueError: If:

        * The YAML file is empty.
        * The YAML structure fails Pydantic schema validation.
        * A ``module_type`` string is not a valid :class:`ModuleType` name.
        * A workflow module is missing its ``flag_map`` declaration.
        * A module definition references an ``obj_class`` or ``runner`` that
          cannot be imported (wrapped from :exc:`ImportError` /
          :exc:`AttributeError`).

    Examples::

        >>> registry = load_registry_from_yaml(
        ...     "/code/miracl/system/configs/modules.yaml"
        ... )
        >>> registry.list_modules(verbose=True)
        Registered Modules (2 total):
        ------------------------------------------------------------
        * tfce
            Type    : MODULE
            ...
        * plot_warped_data
            Type    : FLOW_MAPL3
            ...

        >>> # Retrieve a registered entry for downstream use
        >>> entry = registry.get("plot_warped_data")
        >>> entry["obj_class"]
        <class 'miracl.system.objs.objs_flow.objs_mapl3.PlotWarpedData'>

    .. seealso::
        * :class:`~miracl.system.registry.registry_refactor.registry_clean.MiraclRegistry`
          — the catalog object this function populates.
        * :class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`
          — the Pydantic model used for YAML schema validation.
        * :class:`~miracl.system.datamodels.miraclobj_enums.ModuleType`
          — enum of valid module type identifiers.
    """
    logger.info("Loading registry from YAML | path=%s", yaml_path)

    # ------------------------------------------------------------------
    # Step 1: Validate the file path
    # ------------------------------------------------------------------
    # Convert to a Path object for clean existence checking and future
    # operations (e.g. reading, getting the parent directory, etc.).
    yaml_file = Path(yaml_path)
    if not yaml_file.exists():
        # Log before raising so the error is captured in structured logs even
        # if the caller swallows the exception or re-wraps it.
        logger.error("YAML config file not found | path=%s", yaml_path)
        raise FileNotFoundError(f"YAML config file not found: {yaml_path}")

    logger.debug("Validated YAML path exists | path=%s", yaml_file)

    # ------------------------------------------------------------------
    # Step 2: Parse the YAML file
    # ------------------------------------------------------------------
    # safe_load is mandatory here. It restricts the YAML deserialiser to
    # basic Python types (dict, list, str, int, float, bool, None) and
    # refuses to construct arbitrary Python objects via !!python/object tags.
    # This prevents code execution from a misconfigured or tampered YAML file.
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)

    # safe_load returns None for an empty file, and may return non-dict types
    # for degenerate YAML. Both cases are treated as invalid config.
    if not config:
        logger.error("YAML file empty or invalid | path=%s", yaml_path)
        raise ValueError(f"YAML file is empty or invalid: {yaml_path}")

    logger.debug(
        "YAML loaded successfully | path=%s | top_level_entries=%d",
        yaml_path,
        len(config),
    )

    # ------------------------------------------------------------------
    # Step 3: Validate the schema with Pydantic
    # ------------------------------------------------------------------
    # ModuleConfig is a Pydantic RootModel[dict[str, ModuleEntry]].
    # Constructing it from ``config`` triggers full validation:
    #   - Required fields must be present.
    #   - module_type strings are coerced to ModuleType enums.
    #   - execute defaults to False if absent.
    #   - flag_map defaults to {} if absent (for MODULE types; workflows are
    #     checked more strictly below by _validate_workflow_config).
    #
    # On failure, Pydantic raises ValidationError, which we catch broadly
    # (as Exception) to re-raise as ValueError with a more informative message
    # that includes the original Pydantic details.
    try:
        validated_config = ModuleConfig(config)
        # .root extracts the underlying validated dict from the RootModel,
        # giving us plain Python objects to iterate over.
        config = validated_config.root  # Extract the validated dictionary
        logger.dev("config=%s", config)

        logger.debug(
            "YAML schema validation passed | path=%s | modules=%d",
            yaml_path,
            len(config),
        )
    except Exception as e:
        logger.error(
            "YAML schema validation failed | path=%s | error=%s",
            yaml_path,
            str(e),
        )
        raise ValueError(f"YAML schema validation failed for {yaml_path}: {e}") from e

    # Create empty registry
    registry = MiraclRegistry()

    # Track number of successful registrations for logging
    registered_count = 0

    # ------------------------------------------------------------------
    # Step 5: Import and register each module entry
    # ------------------------------------------------------------------
    # ``config`` is now a dict[str, ModuleEntry] where each value is a
    # Pydantic-validated ModuleEntry dataclass.  We use attribute access
    # (module_config.field) rather than dict access (module_config["field"])
    # because Pydantic models expose fields as attributes.
    for module_name, module_config in config.items():
        logger.debug("Processing module | name=%s", module_name)

        try:
            # -------------------------------------------------------
            # 5a. Dynamically import the obj_class and runner.
            #
            # obj_class: The class (not an instance) that holds the
            #   MiraclObj field definitions for this module. Stored as
            #   a live class reference so downstream components can
            #   introspect it directly without re-importing.
            #
            # runner_func: The callable that will be invoked to actually
            #   execute the module. Storing the function object (rather
            #   than its dotted-path string) means callers can invoke it
            #   directly without needing to import again.
            # -------------------------------------------------------
            obj_class: Type = _import_from_string(module_config.obj_class)
            runner_func: Callable = _import_from_string(module_config.runner)

            # module_type is already a ModuleType enum — Pydantic coerced it
            # from the raw string during validation in Step 3.
            module_type: ModuleType = module_config.module_type

            # -------------------------------------------------------
            # 5b. Extract remaining fields.
            #
            # These have already been validated and defaulted by Pydantic,
            # so we can trust their types without further checks here.
            #   script  : str   — command/path to execute
            #   flag_map: dict  — workflow-to-module flag translation table
            #   execute : bool  — whether the executor should actually run it
            # -------------------------------------------------------
            script: str = module_config.script
            flag_map: dict = (
                module_config.flag_map
            )  # Already defaults to {} via Pydantic
            execute: bool = (
                module_config.execute
            )  # Already defaults to False via Pydantic

            # -------------------------------------------------------
            # 5c. Semantic validation: workflow modules need a flag_map.
            #
            # Pydantic only checks structure; this guard enforces the
            # domain rule that FLOW_* entries cannot omit flag_map.
            # See _validate_workflow_config for the full rationale.
            # -------------------------------------------------------
            _validate_workflow_config(module_name, module_type, flag_map)

            # Create wrapped runner with bound parameters
            # wrapped_runner = _create_wrapped_runner(runner_func, flag_map, execute)

            # -------------------------------------------------------
            # 5d. Register the module.
            #
            # registry.register() stores all provided values in the
            # catalog keyed by module_name.  From this point forward,
            # consumers can retrieve the entry with registry.get(name).
            # -------------------------------------------------------
            registry.register(
                name=module_name,
                script=script,
                obj_class=obj_class,
                module_type=module_type,
                runner=runner_func,
                flag_map=flag_map,
                execute=execute,
            )

            registered_count += 1

            logger.debug(
                "Registered module | name=%s | type=%s | execute=%s",
                module_name,
                module_type.name,
                execute,
            )

        except KeyError as e:
            # This branch handles cases where a required field is missing
            # from the raw dict *before* Pydantic gets a chance to validate it,
            # or where a future code path accesses the config dict directly.
            logger.error(
                "Missing required field | module=%s | field=%s",
                module_name,
                str(e),
            )
            raise ValueError(
                f"Module '{module_name}' is missing required field: {e}"
            ) from e
        except (ImportError, AttributeError) as e:
            # Raised by _import_from_string when obj_class or runner dotted
            # paths point to a module or attribute that cannot be found.
            # Common causes: typo in YAML, module not installed, wrong package
            # structure after a refactor.
            logger.error(
                "Import failure | module=%s | error=%s",
                module_name,
                str(e),
            )
            raise ValueError(
                f"Failed to import component for module '{module_name}': {e}"
            ) from e

    # ------------------------------------------------------------------
    # Step 6: Final success log
    # ------------------------------------------------------------------
    # logger.success is a custom MIRACL log level (between INFO and WARNING)
    # that signals a significant positive outcome — useful for grepping logs
    # during post-deployment verification.
    logger.success(
        "Registry loaded successfully | path=%s | modules_registered=%d",
        yaml_path,
        registered_count,
    )

    return registry


# ---------------------------------------------------------------------------
# Commented-out multi-YAML loader
# ---------------------------------------------------------------------------
# The function below would allow splitting module definitions across multiple
# YAML files (e.g. stats.yaml, registration.yaml) and merging them into a
# single registry. It is preserved here as a design reference for when
# the module catalog grows large enough to warrant splitting.
#
# Key design points for when this is re-enabled:
#   - It creates a fresh MiraclRegistry per YAML file via load_registry_from_yaml,
#     leveraging all of the validation logic above.
#   - It then checks for name collisions before merging, ensuring module names
#     remain globally unique across all files.
#   - The merge is a simple re-registration loop; no deep copying is needed
#     because registry entries are immutable once registered.
#
# NOTE: This fn might need an update since I made a lot of changes to the above code
#
# def load_registry_from_multiple_yamls(yaml_paths: list[str]) -> MiraclRegistry:
#     """
#     Load a single registry from multiple YAML configuration files.
#
#     This is useful for organizing module definitions across multiple files
#     (e.g., stats.yaml, registration.yaml, segmentation.yaml).
#
#     :param yaml_paths: List of paths to YAML configuration files.
#     :type yaml_paths: list[str]
#
#     :returns: Single registry with modules from all files merged together.
#     :rtype: MiraclRegistry
#
#     :raises ValueError: If module names conflict across files.
#
#     Examples::
#
#         >>> registry = load_registry_from_multiple_yamls([
#         ...     "/code/miracl/configs/stats.yaml",
#         ...     "/code/miracl/configs/registration.yaml",
#         ... ])
#     """
#     combined_registry = MiraclRegistry()
#
#     for yaml_path in yaml_paths:
#         temp_registry = load_registry_from_yaml(yaml_path)
#
#         # Check for conflicts before merging to avoid silently overwriting
#         # an existing entry with a same-named one from a different file.
#         for module_name in temp_registry.list_modules().keys():
#             if combined_registry.has(module_name):
#                 raise ValueError(
#                     f"Module name conflict: '{module_name}' is defined in multiple "
#                     f"YAML files. Each module must have a unique name."
#                 )
#
#         # Merge by re-registering each entry from the temporary registry.
#         for module_name, entry in temp_registry.list_modules().items():
#             combined_registry.register(
#                 name=module_name,
#                 script=entry["script"],
#                 obj_class=entry["obj_class"],
#                 module_type=entry["module_type"],
#                 runner=entry["runner"],
#                 flag_map=entry["flag_map"],
#                 execute=entry["execute"],
#             )
#
#     return combined_registry
