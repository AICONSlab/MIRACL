"""
Schema definitions for validating module entries loaded from YAML for registry.
"""

from __future__ import annotations
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Dict, List, Optional, Any
from miracl.api.enums import ModuleType


class UsageExample(BaseModel):
    """A single usage example declared in the YAML _meta block"""

    cmd: str
    help: Optional[str] = None

    class Config:
        extra = "forbid"


class MetaConfig(BaseModel):
    """
    Metadata in '_meta' key in each module YAML for each command.
    This will replace the sperate Python description file for the
    argparser desciption.
    """

    # Routing
    # These are required to correctly match the module
    module: str  # Ex.: "reg" - shown in `miracl -h` output
    command: str  # Ex.: "clar_allen" - used in usage line
    help: str  # Short module description - shown in `miracl reg -h`

    # Extended help
    extended_help: Optional[str] = None
    examples: Optional[List[UsageExample]] = None  # Usage example in help epilog
    docs_url: Optional[str] = None

    # Status badges rendered by MiraclCLIBuilder._build_description()
    deprecated: bool = False
    deprecation_message: Optional[str]
    experimental: bool = False

    # Runtime info
    version: Optional[str] = None
    requires_gpu: bool = False
    min_memory_gb: Optional[str] = None
    estimated_runtime: Optional[str] = None

    # Testing/CI/CD
    tags: Optional[List[str]] = None
    test_data: Optional[str] = None

    @model_validator(mode="after")
    def deprecation_message_required_if_deprecated(self) -> MetaConfig:
        if self.deprecated and not self.deprecation_message:
            raise ValueError("deprecation_message is required when deprecated is True.")
        return self

    class Config:
        extra = "forbid"


class ModuleEntry(BaseModel):
    """
    Represents a single module definition as declared in the YAML file.

    Fields:
        script (str):
            Path or command that will be passed to the runner.

        obj_class (str):
            Dotted import path pointing to the MiraclObj subclass associated
            with this module. Example:
                "miracl.system.objects.ConvTiffNiiObjs"

        runner (str):
            Dotted import path pointing to the runner function responsible
            for executing the module. Example:
                "miracl.runners.generic_runner"

        module_type (ModuleType):
            Enum describing the module’s classification (e.g., MODULE, ACE, MAPL3).
            Parsed and validated automatically by Pydantic.

        flag_map (Dict[str, str]):
            Mapping of workflow-level CLI flags to module-level flags.
            May be empty `{}`. Auto-generated for workflow modules if empty.

        execute (bool):
            Whether the runner should execute the underlying command or only
            construct it. Default: False.

    Notes:
        - Unknown fields in YAML result in a validation error.
        - The `flag_map` is always a dict, never None.
    """

    script: str
    obj_class: str  # dotted import path
    runner: str  # dotted import path
    module_type: ModuleType  # validated enum from YAML
    flag_map: Dict[str, str] = Field(default_factory=dict)
    execute: bool = False

    class Config:
        extra = "forbid"

    @field_validator("module_type", mode="before")
    def parse_module_type(cls, v):
        if isinstance(v, str):
            try:
                return ModuleType[v]
            except KeyError:
                valid_names = ", ".join([e.name for e in ModuleType])
                raise ValueError(
                    f"Invalid module_type '{v}'. Must be one of: {valid_names}"
                )
        return v


class ModuleConfig(BaseModel):
    """
    Validated container for a module config YAML file.

    Accepts the raw YAML dict. The mode="before" validator splits _meta from module
    entries before Pydantic validates each field.

    This gives us a clean model with .meta and .modules as direct typed attr for use
    in introspector!
    """

    meta: MetaConfig
    modules: Dict[str, ModuleEntry]

    @model_validator(mode="before")
    @classmethod
    def split_meta_and_modules(cls, raw: dict) -> dict[str, Any]:
        """
        Serializes the raw YAML dict into the format expected by Pydantic.

        Runs before field validation and returns a plain dict with two keys:
          "meta": the _meta block, validated by MetaConfig
          "modules": all other keys i.e. modules, each validated by ModuleEntry

        Once created, Pydantic then validates the returned dict against the model's
        field definitions.
        """

        # NOTE: This might actually be dead code. Technically a non-empty config is
        # already guaranteed here. This check would only ever happen if ModuleConfig()
        # got called directly but load_registry_from_yaml() should be the only construction
        # path. I leave it in here for now after more testing has been done.
        if not isinstance(raw, dict):
            raise ValueError(
                f"YAML config must be a key-value structure (got {type(raw).__name__}). Check that your YAML file is not empty or incorrectly formatted."
            )

        if "_meta" not in raw:
            raise ValueError(
                "YAML config is missing required _meta block! Every module config must declare _meta with at least: module, command and help!"
            )

        return {
            "meta": raw["_meta"],
            "modules": {name: entry for name, entry in raw.items() if name != "_meta"},
        }
