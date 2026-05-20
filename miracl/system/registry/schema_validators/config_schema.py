"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Schema definitions for validating module entries loaded from YAML for registry.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from miracl.system.datamodels.miraclobj_enums import ModuleType, FlagMapMode


class UsageExample(BaseModel):
    """
    A single usage example declared in the YAML ``_meta`` block.

    We need a single usage example function so we can use it for iteration in case we
    want multiple examples.

    Attributes:
        cmd (str): The full command string for the example.
        help (str, optional): A short description of what the example does.
    """

    cmd: str
    help: Optional[str] = None

    class Config:
        extra = "forbid"


class MetaConfig(BaseModel):
    """
    Metadata declared under the ``_meta`` key in each module YAML.

    CLI description, help text, status badges, and runtime hints shown to the user.
    Will eventually replace the separate Python description files used by the legacy
    argparser.

    Pretty important for the parser...

    Attributes:
        title (str): Full display title of the command.
        module (str): Module group shown in ``miracl -h`` output (e.g. ``"reg"``).
        command (str): Sub-command name used in the usage line (e.g. ``"clar_allen"``).
        help (str): Short description shown in ``miracl <module> -h``.
        extended_help (str, optional): Multi-line extended help shown below the
            short description.
        examples (list of UsageExample, optional): Usage examples shown in the
            help epilog.
        docs_url (str, optional): URL to the full documentation page.
        deprecated (bool): Whether this command is deprecated. Defaults to
            ``False``.
        deprecation_message (str, optional): Required when ``deprecated`` is
            ``True``. Shown as a warning banner in the GUI header.
        experimental (bool): Whether this command is experimental. Defaults to
            ``False``.
        version (str, optional): Version string when this command was introduced.
        requires_gpu (bool): Whether this command requires a GPU. Defaults to
            ``False``.
        min_memory_gb (str, optional): Minimum RAM requirement (e.g. ``"128GB"``).
        estimated_runtime (str, optional): Rough runtime estimate (e.g.
            ``"1-12h"``).
        tags (list of str, optional): Free-form tags for CI/CD and test tooling.
        test_data (str, optional): Path or identifier for test data.
    """

    # NOTE: This is the routing part required to match the module correctly
    title: str
    module: str
    command: str
    help: str

    # Extended help
    extended_help: Optional[str] = None
    examples: Optional[List[UsageExample]] = None
    docs_url: Optional[str] = None

    # Status badges rendered by MiraclCLIBuilder._build_description()
    deprecated: bool = False
    deprecation_message: Optional[str] = None
    experimental: bool = False

    # Runtime info
    version: Optional[str] = None
    miracl_version: Optional[str] = None
    requires_gpu: bool = False
    min_memory_gb: Optional[str] = None
    estimated_runtime: Optional[str] = None

    # Testing/CI/CD
    tags: Optional[List[str]] = None
    test_data: Optional[str] = None

    @model_validator(mode="after")
    def deprecation_message_required_if_deprecated(self) -> MetaConfig:
        """
        Enforce that a deprecation message is provided when deprecated is True.

        Raises:
            ValueError: If ``deprecated`` is ``True`` and ``deprecation_message`` is
                not set.
        """
        if self.deprecated and not self.deprecation_message:
            raise ValueError("deprecation_message is required when deprecated is True.")
        return self

    class Config:
        extra = "forbid"


class ModuleEntry(BaseModel):
    """
    A single module definition as declared in the YAML file.

    Every field here corresponds directly to a key in the YAML module entry.
    Unknown fields are rejected (``extra = "forbid"``).

    Attributes:
        script (str): Path or command passed to the runner at execution time.
        obj_class (str): Dotted import path to the class containing
            ``MiraclObj`` definitions for this module. Example:
            ``"miracl.system.objects.ConvTiffNiiObjs"``.
        runner (str): Dotted import path to the runner function that executes
            the module. Example:
            ``"miracl.system.registry.runners.generic_runner.generic_runner"``.
        module_type (ModuleType): Execution context of the module (e.g.
            ``MODULE``, ``FLOW_MAPL3``). Parsed and validated automatically by
            Pydantic from the raw YAML string.
        flag_map (Union[Dict[str, str], FlagMapMode]): Flag translation
            strategy. **Required — omission raises a validation error.**

            Three valid declarations:

              - ``"autogenerate"`` — derives the mapping automatically from
                :class:`~miracl.system.datamodels.miraclobj_datamodel.MiraclObj`
                flow overrides.
              - ``{}`` — explicit declaration that no flag translation is needed.
              - ``{"--flow_flag": "--module_flag", ...}`` — explicit manual
                mapping. Use as an escape hatch when script flags do not yet
                match their ``MiraclObj`` definitions.

        execute (bool): Whether the runner should actually execute the command
            or perform a dry run. Defaults to ``False``.

    Note:
        The ``flag_map`` mechanism is transitional. Once all scripts are ported
        to the new MIRACL architecture, ``flag_map``, ``FlagMapMode``, and the
        related loader helpers can be removed cleanly.
    """

    script: str
    obj_class: str
    runner: str
    module_type: ModuleType

    # NOTE: flag_map is a required field with no default. Omitting it from a YAML entry
    # raises a Pydantic validation error, which is the intended behaviour. Every module
    # must state its flag_map intent explicitly. The three valid values are described
    # in the class # docstring above.
    flag_map: Union[Dict[str, str], FlagMapMode] = Field(default=None)

    execute: bool = False

    class Config:
        extra = "forbid"

    @field_validator("module_type", mode="before")
    @classmethod
    def parse_module_type(cls, v: Any) -> ModuleType:
        """
        Coerce a raw YAML string to a ``ModuleType`` enum member.

        Args:
            v: The raw value from the YAML file. Expected to be a string
                matching a ``ModuleType`` member name (e.g. ``"MODULE"`` or
                ``"FLOW_MAPL3"``), but may already be a ``ModuleType`` instance.

        Returns:
            ModuleType: The corresponding enum member.

        Raises:
            ValueError: If the string does not match any ``ModuleType`` member.
        """
        if isinstance(v, str):
            try:
                return ModuleType[v]
            except KeyError:
                valid_names = ", ".join(e.name for e in ModuleType)
                raise ValueError(
                    f"Invalid module_type '{v}'. Must be one of: {valid_names}"
                )
        return v

    @model_validator(mode="after")
    def validate_flag_map_for_workflow(self) -> ModuleEntry:
        """
        Enforce flag_map semantics for workflow modules.

        ``MODULE`` type entries manage their own argument parsing and do not
        participate in flag translation, so no constraints apply to them here.

        For all workflow types (``FLOW_*``), ``flag_map`` must be one of the
        three valid declaration modes. Since ``flag_map`` is a required field
        with no default, omitting it is already caught by Pydantic before this
        validator runs which makes the validator a semantic guard for any remaining
        invalid states.

        Note:
            Eventually, flag maps will be deprecated. They are used while MIRACL
            is being transitioned to v2.

        Returns:
            ModuleEntry: The validated instance.

        Raises:
            ValueError: If the module is a workflow type and ``flag_map`` is
                ``None``. In practice this should not be reachable because
                ``flag_map`` has no default, but it is retained as a defensive
                check.
        """
        if self.flag_map is None:
            raise ValueError(
                f"Workflow module (type: {self.module_type.name}) must declare 'flag_map'. Valid options: 'autogenerate', {{}} for no mappings, or an explicit dict mapping workflow flags to module flags."
            )
        if self.module_type == ModuleType.MODULE:
            return self

        return self


class ModuleConfig(BaseModel):
    """
    Validated container for a full module config YAML file.

    Accepts the raw parsed YAML dict. The ``mode="before"`` validator splits the
    ``_meta`` block from the module entries before Pydantic validates each field,
    producing a clean model with typed ``.meta`` and ``.modules`` attributes for use
    by the introspector and loader.

    Attributes:
        meta (MetaConfig): Metadata block from the ``_meta`` YAML key.
        modules (Dict[str, ModuleEntry]): All non-``_meta`` entries, keyed by
            module name.
    """

    meta: MetaConfig
    modules: Dict[str, ModuleEntry]

    @model_validator(mode="before")
    @classmethod
    def split_meta_and_modules(cls, raw: Any) -> Dict[str, Any]:
        """
        Separate the ``_meta`` block from module entries before validation.

        Runs before field validation and returns a plain dict with two keys:
        ``"meta"`` (the ``_meta`` block) and ``"modules"`` (all other entries).
        Pydantic then validates the returned dict against the field definitions.

        Args:
            raw: The raw parsed YAML dict.

        Returns:
            dict: A dict with ``"meta"`` and ``"modules"`` keys ready for
                Pydantic field validation.

        Raises:
            ValueError: If ``raw`` is not a dict, or if the ``_meta`` block is
                missing.

        Note:
            The ``isinstance`` check here is technically redundant because
            ``load_registry_from_yaml`` validates the config structure before
            calling ``model_validate``. It is retained as a defensive guard for
            any caller that constructs ``ModuleConfig`` directly.
        """
        if not isinstance(raw, dict):
            raise ValueError(
                f"YAML config must be a key-value structure (got {type(raw).__name__}). Check that your YAML file is not empty or incorrectly formatted."
            )

        if "_meta" not in raw:
            raise ValueError(
                "YAML config is missing required '_meta' block. Every module config must declare '_meta' with at least: title, module, command, and help."
            )

        return {
            "meta": raw["_meta"],
            "modules": {name: entry for name, entry in raw.items() if name != "_meta"},
        }


# WARNING: model_rebuild() is required because ModuleEntry.flag_map uses
# Union[Dict[str, str], FlagMapMode], which introduces a type that Pydantic
# cannot fully resolve at ModuleConfig class definition time when ModuleEntry
# is nested inside it. Calling model_rebuild() after all classes are defined
# forces Pydantic to re-evaluate the deferred type annotations and complete
# the validator compilation. Without this call, model_validate() raises PydanticUserError.
ModuleConfig.model_rebuild()
