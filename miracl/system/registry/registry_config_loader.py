"""
Code written and maintained by Jonas Osmann. Contact at j.osmann@alumni.utoronto.ca or
via https://github.com/AICONSlab/MIRACL/issues

Declarative loader that registers modules listed in YAML config into registry.
This is the base loader for the new MIRACL module system.

This module is super important (!!!) as it is the entry point for bootstrapping the
MIRACL registry. It bridges the gap between human-readable YAML configuration
files and the in-memory :class:`~miracl.system.registry.registry.MiraclRegistry`
object that the rest of the system depends on at runtime.

This module deliberately only has one job: it reads the YAML file that the dev
declared and produces a populated
:class:`~miracl.system.registry.registry.MiraclRegistry` i.e. a registry. The
registry itself is just a catalog and only a catalog. It only records what
modules exist, where their classes live, which runner is associated with each,
and what their flag maps declare. It does not execute anything or interpret the
entries beyond storing them.

Flag maps are mappings between the workflow-level flags defined in the
:class:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj` flow overrides
and the corresponding flags in the underlying script. Three declaration modes
are supported in the YAML:

- ``flag_map: "autogenerate"`` derives the mapping automatically from
  :attr:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj.flow`
  overrides at load time. Use this for any module whose ``MiraclObj``
  definitions are already fully ported to the new architecture.
- ``flag_map: {}`` explicitly declares that this step requires no flag
  translation (no mappings).
- ``flag_map: {"--flow_flag": "--module_flag", ...}`` explicit manual
  mapping. Use this as an escape hatch for scripts whose flags do not yet
  match their ``MiraclObj`` definitions.

Omitting ``flag_map`` entirely defaults to ``{}`` (no mappings) via Pydantic.
This is intentionally NOT treated as ``"autogenerate"`` omission and
auto-generation are different intents and should be stated explicitly.

Note:
    The flag map mechanism is transitional. Once all scripts are ported to
    the new MIRACL architecture, workflow-level and module-level flags will
    be identical and the flag map will be obsolete. At that point,
    ``FlagMapMode``, ``_resolve_flag_map``, ``_auto_generate_flag_map``, and
    the ``flag_map`` field on ``ModuleEntry``/``RegistryEntry`` can all be
    removed.

A typical data flow looks as follows:
    1) modules.yaml is defined by dev
    2) load_registry_from_yaml()
        - validates the file path
        - parses YAML (safe_load, no arbitrary Python execution)
        - validates schema (Pydantic ModuleConfig)
        - dynamically imports obj_class + runner for each entry
        - resolves flag_map via _resolve_flag_map()
        - calls registry.register() for each entry i.e. registers the module
    3) Created MiraclRegistry which is an in-memory catalog i.e. exists only
       during program lifetime and is consumed by downstream components
       (introspector, executor, etc.)

To register a new module, a dev only needs to add an entry to the YAML
configuration file e.g. ``modules.yaml``. No Python changes are required unless
a custom new module class or runner is introduced. In that case, this needs to
be done beforehand. The YAML schema is validated by
:class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`.
"""

#######################################################################################
# IMPORTS
#######################################################################################
from multiprocessing.sharedctypes import Value
import yaml
import importlib
from typing import Callable, Type, Tuple, Dict, Union
from pathlib import Path

from miracl.system.datamodels.miraclobj_datamodel import MiraclObj
from miracl.system.datamodels.miraclobj_enums import ModuleType, FlagMapMode
from miracl.system.registry.registry import MiraclRegistry
from miracl.system.registry.schema_validators.config_schema import ModuleConfig
from miracl.system.logger import get_logger

logger = get_logger(__name__)

#######################################################################################
# YAML LOADER
#######################################################################################


class RegistryLoader(yaml.SafeLoader):
    """
    Custom YAML loader scoped to this module.

    Subclassing SafeLoader rather than modifying it directly ensures that any
    constructors registered here (e.g. for ``!include``) do not leak into the
    global PyYAML registry and affect unrelated YAML parses elsewhere in the
    process.

    The ``!include`` constructor is registered per-call inside
    :func:`load_registry_from_yaml` because it must be relative to the
    directory of the YAML file being loaded, which is not known at import time.
    """

    pass


#######################################################################################
# PRIVATE HELPERS
#######################################################################################


def _pick_flag(cli, mode: FlagMapMode, context: str) -> str:
    """
    Extract the correct flag string from a CLI spec according to mode. Raises ValueError
    if the requested flag type is not defined in object and therefore probably not
    defined in the respective script.
    """
    if mode is FlagMapMode.AUTOGENERATE_SHORT:
        if not cli.s_flag:
            raise ValueError(
                "autogenerate_short selected but the module-side `{context}' has no short flag attribute 's_flag'. You could either create short flags to the module or switch to 'autogenerate_long'."
            )
        return "-" + cli.s_flag
    else:  # AUTOGENERATE_LONG
        if not cli.l_flag:
            raise ValueError(
                "autogenerate_long selected but module-side `{context}' has no long flag attribute 'l_flag'. You could either create module long flags or switch to 'autogenerate_short'."
            )
        return "--" + cli.l_flag


def _auto_generate_flag_map(
    obj_class: Type,
    module_type: ModuleType,
    mode: FlagMapMode,
) -> Dict[str, str]:
    """
    Derive an explicit ``flag_map`` from :class:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj`
    flow overrides declared on ``obj_class``.

    Inspects every :class:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj`
    attribute of ``obj_class`` for a flow entry matching the given
    ``module_type``. For each matching object, maps the workflow-level flag
    (from the flow override) to the module-level flag (from the base CLI spec).

    Pairings are mapped explicitly even when the workflow flag and the module
    flag are identical, so the resulting dict is always the authoritative
    source of truth for the runner regardless of whether a translation is
    actually needed.

    Note:
        Uses :func:`vars` rather than :func:`dir` to iterate attributes.
        ``vars()`` returns only attributes declared directly on ``obj_class``,
        avoiding inherited dunder methods and parent class attributes that
        would otherwise be included by ``dir()``.

    :param obj_class: The class containing ``MiraclObj`` attribute definitions
        for this module.
    :type obj_class: Type

    :param module_type: The workflow context to generate mappings for.
        Only ``MiraclObj`` instances that declare a flow entry for this type
        are included.
    :type module_type: ModuleType

    :returns: A ``dict`` mapping workflow-level flags (e.g. ``"--mi_config"``)
        to module-level flags (e.g. ``"--config"``).
    :rtype: Dict[str, str]
    """
    flag_map = {}
    flow_key = module_type.value  # e.g. "mapl3"

    for attr_name, attr in vars(obj_class).items():
        if not isinstance(attr, MiraclObj):
            continue

        context = f"attribute '{attr_name}' on '{obj_class.__name__}'"
        module_flag = _pick_flag(attr.cli, mode, context)

        # for attr in vars(obj_class).values():
        #     if not isinstance(attr, MiraclObj):
        #         continue
        #
        #     if attr.cli.l_flag:
        #         module_flag = "--" + attr.cli.l_flag
        #     elif attr.cli.s_flag:
        #         module_flag = "-" + attr.cli.s_flag
        #     else:
        #         continue

        if not attr.flow or flow_key not in attr.flow:
            continue

        flow_override = attr.flow[flow_key]
        workflow_flag = module_flag

        if flow_override.cli:
            flow_context = f"flow override for '{attr_name}' on {obj_class.__name__}'"
            if not flow_override.cli.l_flag:
                raise ValueError(
                    "Missing required long flag (l_flag) for '{flow_context}'. Workflow side flag map keys must always be long flags."
                )
            workflow_flag = "--" + flow_override.cli.l_flag
            # workflow_flag = _pick_flag(flow_override.cli, mode, flow_context)

        # if flow_override.cli:
        #     if flow_override.cli.l_flag:
        #         workflow_flag = "--" + flow_override.cli.l_flag
        #     elif flow_override.cli.s_flag:
        #         workflow_flag = "-" + flow_override.cli.s_flag

        flag_map[workflow_flag] = module_flag

    logger.debug(
        "Auto-generated explicit flag_map | class=%s | mappings=%d",
        obj_class.__name__,
        len(flag_map),
    )
    return flag_map


def _resolve_flag_map(
    flag_map: Union[Dict[str, str], FlagMapMode],
    obj_class: Type,
    module_type: ModuleType,
    module_name: str,
) -> Dict[str, str]:
    """
    Resolve the final ``flag_map`` dict for a module given its declared mode.

    Three modes are supported:

    - :attr:`~miracl.system.datamodels.miraclobj_enums.FlagMapMode.AUTOGENERATE`
      — derives the mapping automatically from
      :class:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj` flow
      overrides via :func:`_auto_generate_flag_map`.
    - ``{}`` (empty dict) — no flag translation needed. Returned as-is.
    - ``{"--flow_flag": "--module_flag", ...}`` — explicit manual mapping.
      Returned as-is.

    :param flag_map: The ``flag_map`` value from the validated
        :class:`~miracl.system.registry.schema_validators.config_schema.ModuleEntry`.
    :type flag_map: Union[Dict[str, str], FlagMapMode]

    :param obj_class: The class containing ``MiraclObj`` definitions.
        Only used when ``flag_map`` is ``FlagMapMode.AUTOGENERATE``.
    :type obj_class: Type

    :param module_type: The workflow context. Only used when ``flag_map`` is
        ``FlagMapMode.AUTOGENERATE``.
    :type module_type: ModuleType

    :param module_name: The registry name of the module. Used only in log
        messages.
    :type module_name: str

    :returns: The resolved ``flag_map`` dict, ready for storage in the
        registry entry.
    :rtype: Dict[str, str]
    """
    if isinstance(flag_map, FlagMapMode):
        logger.debug(
            "Resolving flag_map via auto-generation | module=%s | mode=%s",
            module_name,
            flag_map.value,
        )
        return _auto_generate_flag_map(obj_class, module_type, mode=flag_map)

    return flag_map


def _import_from_string(dotted_path: str) -> object:
    """
    Dynamically import and return an attribute from a module using its dotted
    path. Chosen for this because it allows YAML config files to reference
    Python classes and functions by name, as strings, without requiring
    hardcoded imports at the top of this file. Intentionally kept generic so
    that both ``obj_class`` and ``runner`` entries can be resolved through the
    same code path.

    Example: Given ``"a.b.c.MyClass"``:

    1. Split on the last dot: ``module_path = "a.b.c"``, ``attr_name = "MyClass"``.
    2. ``importlib.import_module("a.b.c")`` — honours normal Python import rules.
    3. ``getattr(module, "MyClass")`` — retrieves the class from the module.

    Note:
        Cannot traverse nested classes. This is by design since MIRACL's
        ``obj_class`` entries are top-level classes by convention.

    Note:
        ``rsplit(".", 1)`` is used rather than ``split(".", 1)`` to correctly
        handle deeply nested paths like ``"a.b.c.d.MyClass"``. Left-split would
        incorrectly give ``module_path = "a"`` and
        ``attr_name = "b.c.d.MyClass"``.

    :param dotted_path: A fully-qualified dotted Python path such as
        ``'miracl.system.objs.objs_stats.objs_tfce.TFCE'`` or
        ``'miracl.system.registry.runners.generic_runner.generic_runner'``.
    :type dotted_path: str

    :returns: The imported class, function, or other module-level attribute.
    :rtype: object

    :raises ImportError: If the module portion of the path cannot be imported.
    :raises AttributeError: If the module does not expose the named attribute.

    Examples::

        >>> TFCE = _import_from_string(
        ...     "miracl.system.objs.objs_stats.objs_tfce.TFCE"
        ... )
        >>> runner = _import_from_string(
        ...     "miracl.system.registry.runners.generic_runner.generic_runner"
        ... )
    """
    module_path, attr_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)

    logger.debug(
        "Imported attribute successfully | module=%s | attribute=%s",
        module_path,
        attr_name,
    )

    return getattr(module, attr_name)


def _load_and_unwrap_shared_file(include_path: Path) -> Tuple[str, dict]:
    """
    Load a shared module YAML file, validate its structure, and return the declared
    module name and its body dict.

    A module YAML can be declared once and then imported (via ``!include`` or
    ``$include``) into multiple workflow configs. This function is the single
    authoritative validation point for both mechanisms, ensuring identical
    structural checks regardless of which include syntax was used.

    :param include_path: Absolute path to the shared module YAML file.
    :type include_path: Path

    :returns: A tuple of ``(declared_name, body)`` where ``declared_name`` is
        the single top-level key and ``body`` is the dict of module fields.
    :rtype: Tuple[str, dict]

    :raises FileNotFoundError: If the file does not exist.
    :raises ValueError: If the file does not declare exactly one top-level key,
        or if the body under that key is not a dict.
    :raises yaml.YAMLError: If the file contains invalid YAML syntax.
    """
    if not include_path.exists():
        raise FileNotFoundError(f"Shared module file not found: {include_path}")

    logger.debug("Loading shared module file | path=%s", include_path)

    with open(include_path, "r") as f:
        content = yaml.load(f, Loader=RegistryLoader)

    if not isinstance(content, dict) or len(content) != 1:
        raise ValueError(
            f"Shared module file must declare exactly one top-level key (the module name). Got {len(content) if isinstance(content, dict) else type(content).__name__} top-level keys in: {include_path}"
        )

    declared_name, body = next(iter(content.items()))

    if not isinstance(body, dict):
        raise ValueError(
            f"Module body under '{declared_name}' must be a key-value mapping "
            f"in: {include_path}"
        )

    return declared_name, body


def _make_include_constructor(base_dir: Path) -> Callable:
    """
    Build a PyYAML constructor that resolves ``!include`` tags relative to
    ``base_dir``.

    Delegates all file loading and structural validation to
    :func:`_load_and_unwrap_shared_file`. Injects ``_declared_name`` into the
    returned body so :func:`load_registry_from_yaml` can validate it against
    the key used in the parent YAML.

    Use ``!include`` when importing a shared module with no field overrides.
    Use ``$include`` (handled in :func:`load_registry_from_yaml`) when you
    need to override specific fields for a given workflow.

    :param base_dir: Absolute path to the directory containing the YAML file
        being parsed. All ``!include`` paths are resolved relative to this.
    :type base_dir: Path

    :returns: A PyYAML constructor function compatible with
        ``yaml.add_constructor``.
    :rtype: Callable
    """

    def constructor(loader: yaml.SafeLoader, node: yaml.ScalarNode) -> dict:
        include_path = base_dir / loader.construct_scalar(node)
        declared_name, body = _load_and_unwrap_shared_file(include_path)
        body["_declared_name"] = declared_name
        return body

    return constructor


#######################################################################################
# PUBLIC API
#######################################################################################
def load_registry_from_yaml(yaml_path: str) -> MiraclRegistry:
    """
    Parse a YAML configuration file and return a fully populated
    :class:`~miracl.system.registry.registry.MiraclRegistry`.

    This is the primary public function of this module. All production code
    that needs a registry should call this function or a higher-level wrapper
    that calls it.

    Note:
        The migration to the new architecture is happening on a per-module /
        per-workflow basis. MIRACL is used in production so the refactoring
        cannot break existing versions.

    Performs the following steps in order:

    1. Path validation: raises :exc:`FileNotFoundError` immediately if
       the file does not exist, surfacing misconfiguration before any
       pipeline work begins.

    2. YAML parsing: reads the file with :class:`RegistryLoader`, a
       :class:`~yaml.SafeLoader` subclass. ``safe_load`` semantics prevent
       arbitrary Python object deserialisation from config files. The
       ``!include`` constructor is registered per-call so it is relative to
       the directory of the file being loaded.

    3. Pre-processing loop: resolves ``$include`` merges and validates
       ``!include``-injected ``_declared_name`` metadata before Pydantic sees
       the config dict.

    4. Schema validation: wraps the pre-processed dict in
       :class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`
       (Pydantic). Confirms required fields, coerces types, and enforces
       semantic constraints (including the ``flag_map`` workflow requirement,
       which is now a ``model_validator`` on ``ModuleEntry``).

    5. Registration loop: for each module entry: dynamically imports
       ``obj_class`` and ``runner``, resolves the ``flag_map`` via
       :func:`_resolve_flag_map`, and calls
       :meth:`~miracl.system.registry.registry.MiraclRegistry.register`.

    The registry is a pure catalog. It only stores references to classes and
      functions. It does not instantiate classes, invoke runners, or build
      flag maps. Those are the introspector's, serializer's, and executor's
      jobs. All validation in the registry happens before any module is registered.
      A single broken entry causes the entire load to fail and raises an error! Schema
      enforcement is done with Pydantic.

    :param yaml_path: Absolute or relative path to the YAML file containing
        module definitions.
    :type yaml_path: str

    :returns: A :class:`~miracl.system.registry.registry.MiraclRegistry`
        instance populated with one entry per module defined in the YAML file.
    :rtype: MiraclRegistry

    :raises FileNotFoundError: If the file at ``yaml_path`` does not exist.
    :raises yaml.YAMLError: If the file contains invalid YAML syntax.
    :raises ValueError: If the YAML is empty, fails schema validation, or a
        component (``obj_class``/``runner``) cannot be imported.

    Examples::

        >>> registry = load_registry_from_yaml(
        ...     "/code/miracl/system/configs/modules.yaml"
        ... )
        >>> entry = registry.get("mapl3_inference")
        >>> entry["obj_class"]
        <class 'miracl.system.objs.objs_flow.objs_mapl3.Inference'>

    .. seealso::
        * :class:`~miracl.system.registry.registry.MiraclRegistry`
        * :class:`~miracl.system.registry.schema_validators.config_schema.ModuleConfig`
        * :class:`~miracl.system.datamodels.miraclobj_enums.ModuleType`
        * :class:`~miracl.system.datamodels.miraclobj_enums.FlagMapMode`
    """
    logger.info("Loading registry from YAML | path=%s", yaml_path)

    yaml_file = Path(yaml_path)
    if not yaml_file.exists():
        logger.error("YAML config file not found | path=%s", yaml_path)
        raise FileNotFoundError(f"YAML config file not found: {yaml_path}")

    logger.debug("Validated YAML path exists | path=%s", yaml_file)

    RegistryLoader.add_constructor(
        "!include",
        _make_include_constructor(yaml_file.parent),
    )

    with open(yaml_file, "r") as f:
        config = yaml.load(f, Loader=RegistryLoader)

    if not config or not isinstance(config, dict):
        logger.error("YAML file empty or invalid | path=%s", yaml_path)
        raise ValueError(f"YAML file is empty or invalid: {yaml_path}")

    logger.debug(
        "YAML loaded successfully | path=%s | top_level_entries=%d",
        yaml_path,
        len(config),
    )

    for module_name, module_entry in list(config.items()):
        if module_name == "_meta" or not isinstance(module_entry, dict):
            continue

        if "flag_map" not in module_entry:
            raise ValueError(
                f"Module '{module_name}' is missing required 'flag_map'. Valid options: 'autogenerate', {{}} for no mappings, or an explicit mapping dict. Omission is not allowed."
            )
        if "$include" in module_entry:
            rel_path = module_entry.pop("$include")
            include_path = yaml_file.parent / rel_path

            declared_name, base_body = _load_and_unwrap_shared_file(include_path)

            if declared_name != module_name:
                logger.error(
                    "Module name mismatch | parent_key=%s | declared=%s",
                    module_name,
                    declared_name,
                )
                raise ValueError(
                    f"Module name mismatch: parent YAML uses key '{module_name}' but shared file declares '{declared_name}'. Either rename the key in the parent YAML or update the shared file."
                )

            config[module_name] = {**base_body, **module_entry}
            module_entry = config[module_name]

        declared_name = module_entry.pop("_declared_name", None)
        if declared_name is not None and declared_name != module_name:
            logger.error(
                "Module name mismatch | parent_key=%s | declared=%s",
                module_name,
                declared_name,
            )
            raise ValueError(
                f"Module name mismatch: parent YAML uses key '{module_name}' but shared file declares '{declared_name}'. Either rename the key in the parent YAML or update the shared file."
            )

    try:
        split = ModuleConfig.model_validate(config)
        logger.debug(
            "YAML schema validation passed | path=%s | modules=%d | meta.command=%s",
            yaml_path,
            len(split.modules),
            split.meta.command,
        )
    except Exception as e:
        logger.error(
            "YAML schema validation failed | path=%s | error=%s",
            yaml_path,
            str(e),
        )
        raise ValueError(f"YAML schema validation failed for {yaml_path}: {e}") from e

    registry = MiraclRegistry()
    registry.register_meta(split.meta)
    logger.debug(
        "Meta registered | module=%s | command=%s",
        split.meta.module,
        split.meta.command,
    )

    registered_count = 0

    for module_name, module_config in split.modules.items():
        logger.debug("Processing module | name=%s", module_name)

        try:
            obj_class: Type = _import_from_string(module_config.obj_class)
            runner_func: Callable = _import_from_string(module_config.runner)

            flag_map = _resolve_flag_map(
                flag_map=module_config.flag_map,
                obj_class=obj_class,
                module_type=module_config.module_type,
                module_name=module_name,
            )

            logger.debug(
                "Resolved flag_map | module=%s | flag_map=%s",
                module_name,
                flag_map,
            )

            registry.register(
                name=module_name,
                script=module_config.script,
                obj_class=obj_class,
                module_type=module_config.module_type,
                runner=runner_func,
                flag_map=flag_map,
                execute=module_config.execute,
            )

            registered_count += 1

            logger.debug(
                "Registered module | name=%s | type=%s | execute=%s",
                module_name,
                module_config.module_type.name,
                module_config.execute,
            )

        except (ImportError, AttributeError) as e:
            logger.error(
                "Import failure | module=%s | error=%s",
                module_name,
                str(e),
            )
            raise ValueError(
                f"Failed to import component for module '{module_name}': {e}"
            ) from e

    logger.success(
        "Registry loaded successfully | path=%s | modules_registered=%d",
        yaml_path,
        registered_count,
    )

    return registry
