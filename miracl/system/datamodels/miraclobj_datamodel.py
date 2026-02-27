"""
FULL ARCHITECTURAL REFACTOR - COMPLETE VERSION (PYDANTIC V2)
=============================================================

Includes ALL features from original datamodel + Fixes:
- Structured CLI/GUI/Metadata
- [RESTORED] Contextual flag validation errors (id, module)
- [RESTORED] Field constraints for tags (min_length, max_length)
- [RESTORED] GuiWidgetSpecifics (props) namespace
- [RESTORED] Strict Union for obj_default
- [V2 SYNTAX] Complete Pydantic V2 syntax migration (ConfigDict, field_validator)

EVERYTHING ANNOTATED WITH >>> MARKERS
"""

from typing import (
    Any,
    Optional,
    List,
    Union,
    Tuple,
    Dict,
    ClassVar,
)
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    DirectoryPath,
    FilePath,
    ConfigDict,
)
from pydantic_core.core_schema import ValidationInfo
from miracl.api.enums import (
    ArgumentType,
    ArgumentAction,
    WidgetType,
    InputRestrictionType,
    CliGroup,
    ModuleType,
)
from miracl.api.utils import parser_true_or_false
from argparse import ArgumentTypeError
import argparse
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4
import threading
import re


# ============================================================
# ENUMS
# ============================================================


class ArgumentSource(str, Enum):
    """Source/visibility of an argument"""

    USER = "user"  # Visible in CLI and GUI
    INTERNAL = "internal"  # Hidden from help/UI but available for module piping
    DISABLED = "disabled"  # Removed from context entirely


# ============================================================
# GUI STRUCTURE
# ============================================================


class RangeFormConfig(BaseModel):
    min_val: Optional[Union[int, float]] = Field(None, description="Min value")
    max_val: Optional[Union[int, float]] = Field(None, description="Max value")
    increment_val: Optional[Union[int, float]] = Field(
        None, description="Increment value"
    )
    nr_decimals: Optional[int] = Field(None, description="Nr decimals")


class GuiChoiceOverrideConfig(BaseModel):
    vals: Optional[List[str]] = Field(
        None, description="Values to use instead of cli choices"
    )
    default_val: Optional[str] = Field(None, description="Default value")


class LineEditConfig(BaseModel):
    input_restrictions: Optional[InputRestrictionType] = Field(
        None, description="Type of input restrictions"
    )


# >>> [RESTORED] Widget specifics namespace
class GuiWidgetSpecifics(BaseModel):
    """Container for generic widget configuration options"""

    range: Optional[RangeFormConfig] = Field(
        None, description="Range/formatting configuration for numeric widgets"
    )
    text: Optional[LineEditConfig] = Field(
        None, description="Settings for line edit widgets"
    )
    choices: Optional[GuiChoiceOverrideConfig] = Field(
        None, description="Override for choice labels in GUI"
    )


class GuiBase(BaseModel):
    """Frontend-agnostic GUI properties."""

    label: Optional[List[str]] = Field(None, description="Main label(s) used in GUI")
    widget_type: Optional[WidgetType] = Field(
        None, description="Type of widget to use in GUI"
    )
    additional_labels: Optional[List[str]] = Field(
        None, description="Additional label(s) used in GUI"
    )
    # group: Optional[CliGroup] = Field(
    group: str = Field(None, description="Group name for organizing in GUI")
    order: Optional[float] = Field(None, description="Order of appearance in GUI")

    # >>> [RESTORED] Props property instead of flattened attributes
    props: GuiWidgetSpecifics = Field(
        default_factory=GuiWidgetSpecifics,
        description="Widget-specific configuration",
    )


class GuiNamespace(BaseModel):
    """Complete GUI configuration with base + extensions."""

    base: GuiBase = Field(default_factory=GuiBase)
    extensions: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Frontend-specific attributes. Keys: 'qt', 'gradio', etc.",
    )


class GuiDelta(BaseModel):
    """Delta for GUI overrides in FlowOverride."""

    base: Optional[GuiBase] = None
    extensions: Optional[Dict[str, Dict[str, Any]]] = None


# ============================================================
# CLI STRUCTURE
# ============================================================


class CLISpec(BaseModel):
    """Complete CLI specification."""

    s_flag: Optional[str] = Field(None, description="Short flag for cli arg")
    l_flag: str = Field(..., description="Long flag for cli arg")
    help: str = Field(..., description="Help text for cli arg")
    required: Optional[bool] = Field(None, description="Whether cli arg is required")
    obj_type: Optional[ArgumentType] = Field(None, description="Data type of cli arg")

    # >>> [RESTORED] Strict Union typing for default value
    default: Optional[Union[Path, int, float, List[Any], str, Dict[str, Any], bool]] = (
        Field(None, description="Default obj value for arg, if any")
    )

    nargs: Optional[Union[int, str]] = Field(
        None, description="Number of expected cli args"
    )
    choices: Optional[List[Any]] = Field(
        None, description="List of allowed choices/values for the cli arg"
    )
    action: Optional[ArgumentAction] = Field(
        None, description="Action to be taken when cli arg is encountered"
    )
    const: Optional[Any] = Field(None, description="Argparse const option")
    metavar: Optional[Union[str, Tuple[str, ...]]] = Field(
        None, description="Name for cli arg in cli usage messages"
    )
    group: Optional[CliGroup] = Field(
        None, description="Argparse group the object belongs to"
    )

    # >>> [V2 SYNTAX] Replaced @validator with @field_validator
    @field_validator("nargs", mode="before")
    @classmethod
    def validate_nargs(cls, value):
        if value is None:
            return value
        valid_nargs = {"+", "*", "?", "...", "N"}
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value in valid_nargs:
            return value
        if isinstance(value, str):
            raise ValueError(
                f"Invalid string value for nargs: '{value}'. Must be one of {valid_nargs}."
            )
        raise ArgumentTypeError(
            f"Invalid type for nargs: {value}. Must be an int or one of {valid_nargs}."
        )

    # >>> [V2 SYNTAX] Replaced @validator with @field_validator
    @field_validator("obj_type", mode="before")
    @classmethod
    def validate_type(cls, v):
        if v == ArgumentType.CUSTOM_BOOL:
            return parser_true_or_false(str(v))
        return v

    # >>> [V2 SYNTAX] Replaced @validator with @field_validator
    @field_validator("default", mode="before")
    @classmethod
    def validate_default(cls, value):
        if value is None:
            return value
        allowed_types = (Path, int, float, list, str, dict, bool)
        if not isinstance(value, allowed_types):
            raise ValueError(
                f"Invalid type for default: {type(value)}. Must be one of {allowed_types}."
            )
        return value


class CLIDelta(BaseModel):
    """Delta for CLI overrides in FlowOverride."""

    s_flag: Optional[str] = None
    l_flag: Optional[str] = None
    help: Optional[str] = None
    required: Optional[bool] = None
    obj_type: Optional[ArgumentType] = None
    default: Optional[Union[Path, int, float, List[Any], str, Dict[str, Any], bool]] = (
        None
    )
    nargs: Optional[Union[int, str]] = None
    choices: Optional[List[Any]] = None
    action: Optional[ArgumentAction] = None
    const: Optional[Any] = None
    metavar: Optional[Union[str, Tuple[str, ...]]] = None
    group: Optional[CliGroup] = None


# ============================================================
# RESOLVED RUNTIME OBJECT
# ============================================================


class ResolvedMiraclObj(BaseModel):
    """Immutable runtime object used by builders/serializers."""

    # >>> [V2 SYNTAX] Using model_config for immutability
    model_config = ConfigDict(frozen=True)

    id: UUID
    name: str
    module: str
    module_group: str
    source: ArgumentSource

    cli: CLISpec
    gui: Optional[GuiNamespace]

    content: Optional[Any] = Field(None, description="Runtime value for this argument")
    gui_hidden: bool = Field(
        default=False, description="Whether this argument should be hidden in GUI"
    )
    gui_extensions: Optional[Dict[str, Dict[str, Any]]] = Field(
        None, description="Copy of gui.extensions"
    )

    depends_on: Optional[List[str]]
    conflicts_with: Optional[List[str]]
    description: Optional[str]
    deprecated: bool
    version_added: str
    examples: List[str]

    # >>> [RESTORED] Tags constraints using V2 syntax
    tags: Optional[List[str]] = Field(None, min_length=1, max_length=10)

    # >>> [V2 SYNTAX] Updated to ValidationInfo
    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v, info: ValidationInfo):
        cli_spec = info.data.get("cli")
        if cli_spec is None or cli_spec.obj_type is None or v is None:
            return v

        python_type = cli_spec.obj_type.python_type

        if python_type is list:
            if not isinstance(v, list):
                raise ValueError(f"Expected list for content, got {type(v).__name__}")
            return list(v)

        if isinstance(v, list):
            try:
                return [python_type(item) for item in v]
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert elements in {v} to {python_type}")

        try:
            return python_type(v)
        except (ValueError, TypeError):
            raise ValueError(f"Cannot convert {v} to {python_type}")


# ============================================================
# FLOW OVERRIDE
# ============================================================


class FlowOverride(BaseModel):
    cli: Optional[CLIDelta] = None
    gui: Optional[GuiDelta] = None
    source: Optional[ArgumentSource] = None


# ============================================================
# MAIN OBJECT
# ============================================================


class MiraclObj(BaseModel):
    """Definition-time object."""

    # >>> [V2 SYNTAX] ConfigDict for config
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        validate_default=True,
    )

    instances: ClassVar[Dict[Tuple[str, str], "MiraclObj"]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def model_post_init(self, __context):
        key = (self.module, self.name)
        with MiraclObj._lock:
            if key in MiraclObj.instances:
                raise RuntimeError(
                    f"Duplicate MiraclObj for module='{self.module}', name='{self.name}'"
                )
            MiraclObj.instances[key] = self

    id: UUID = Field(default_factory=uuid4, frozen=True)
    name: str = Field(...)
    module: str = Field(...)
    module_group: str = Field(...)
    source: ArgumentSource = Field(default=ArgumentSource.USER)

    cli: CLISpec
    gui: Optional[GuiNamespace] = None

    flow: Optional[Dict[str, FlowOverride]] = None

    input_dirpath_field: Optional[DirectoryPath] = Field(
        default=None, alias="input_dirpath"
    )

    @property
    def input_dirpath(self) -> Optional[DirectoryPath]:
        return self.input_dirpath_field

    @input_dirpath.setter
    def input_dirpath(self, value: Optional[DirectoryPath]):
        if self.input_dirpath_field is None:
            self.input_dirpath_field = value
        else:
            raise ValueError("input_dirpath cannot be changed once set")

    dirpath_field: Optional[DirectoryPath] = Field(default=None, alias="dirpath")

    @property
    def dirpath(self) -> Optional[DirectoryPath]:
        return self.dirpath_field

    @dirpath.setter
    def dirpath(self, value: Optional[DirectoryPath]):
        if self.dirpath_field is None:
            self.dirpath_field = value
        else:
            raise ValueError("dirpath cannot be changed once set")

    filepath_field: Optional[FilePath] = Field(default=None, alias="filepath")

    @property
    def filepath(self) -> Optional[FilePath]:
        return self.filepath_field

    @filepath.setter
    def filepath(self, value: Optional[FilePath]):
        if self.filepath_field is None:
            self.filepath_field = value
        else:
            raise ValueError("filepath cannot be changed once set")

    depends_on: Optional[List[str]] = Field(None)
    conflicts_with: Optional[List[str]] = Field(None)
    description: Optional[str] = Field(None)
    deprecated: bool = Field(default=False)
    version_added: str = Field(...)
    examples: List[str] = Field(default_factory=list)

    # >>> [RESTORED] Tags constraints using V2 syntax
    tags: Optional[List[str]] = Field(None, min_length=1, max_length=10)

    # >>> [V2 SYNTAX] Replaced @validator with @field_validator
    @field_validator("dirpath_field", mode="before")
    @classmethod
    def create_directory_if_not_exists(cls, value):
        if value is not None:
            path = Path(value)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return value

    # ============================================================
    # >>> [RESTORED] CONTEXTUAL FLAG VALIDATION
    # ============================================================

    @model_validator(mode="after")
    def validate_flags_with_context(self) -> "MiraclObj":
        """
        Validates the format of CLI flags AFTER the model is constructed.
        This restores the ability to provide exact error contexts (id, module)
        if a flag contains invalid characters or is empty.
        """
        # Validate base CLI
        self._check_flag_format(self.cli.s_flag, "cli.s_flag")
        self._check_flag_format(self.cli.l_flag, "cli.l_flag")

        # Validate overrides
        if self.flow:
            for flow_name, override in self.flow.items():
                if override.cli:
                    self._check_flag_format(
                        override.cli.s_flag, f"flow['{flow_name}'].cli.s_flag"
                    )
                    self._check_flag_format(
                        override.cli.l_flag, f"flow['{flow_name}'].cli.l_flag"
                    )

        return self

    def _check_flag_format(self, flag_value: Optional[str], field_context: str):
        """Helper to ensure flags match the required regex."""
        if flag_value is None:
            return

        if not flag_value:
            raise ValueError(
                f"Empty flag '{field_context}' for object '{self.id}' in module '{self.module}'"
            )

        if not re.match(r"^[a-zA-Z0-9_-]+$", flag_value):
            raise ValueError(
                f"Invalid characters in flag '{field_context}' ('{flag_value}') "
                f"for object '{self.id}' in module '{self.module}'"
            )

    # ============================================================
    # RESOLVE METHOD
    # ============================================================

    def resolve(self, context: ModuleType) -> Optional[ResolvedMiraclObj]:
        final_cli = self.cli.model_copy()
        final_gui = self.gui.model_copy() if self.gui else None
        final_source = self.source

        if context != ModuleType.MODULE:
            if not self.flow or context.value not in self.flow:
                raise ValueError(
                    f"Configuration Error: MiraclObj '{self.name}' (ID: {self.id}) is missing "
                    f"required workflow entry for '{context.value}'. Every object used in a "
                    f"workflow must explicitly define its flow settings."
                )

            override = self.flow[context.value]

            if override.cli:
                delta = override.cli.model_dump(exclude_unset=True)
                final_cli = final_cli.model_copy(update=delta)

            if override.gui:
                if final_gui is None:
                    if override.gui.base:
                        final_gui = GuiNamespace(
                            base=override.gui.base, extensions=override.gui.extensions
                        )
                else:
                    if override.gui.base:
                        base_delta = override.gui.base.model_dump(exclude_unset=True)
                        new_base = final_gui.base.model_copy(update=base_delta)
                        final_gui = GuiNamespace(
                            base=new_base,
                            extensions=override.gui.extensions or final_gui.extensions,
                        )
                    elif override.gui.extensions:
                        final_gui = GuiNamespace(
                            base=final_gui.base, extensions=override.gui.extensions
                        )

            if override.source:
                final_source = override.source

        if final_source == ArgumentSource.DISABLED:
            return None

        gui_hidden = False
        if final_source == ArgumentSource.INTERNAL:
            final_cli = final_cli.model_copy(
                update={
                    "help": argparse.SUPPRESS,
                    "required": False,
                }
            )
            gui_hidden = True

        gui_extensions = None
        if final_gui and final_gui.extensions:
            gui_extensions = final_gui.extensions.copy()

        return ResolvedMiraclObj(
            id=self.id,
            name=self.name,
            module=self.module,
            module_group=self.module_group,
            source=final_source,
            cli=final_cli,
            gui=final_gui,
            content=None,
            gui_hidden=gui_hidden,
            gui_extensions=gui_extensions,
            depends_on=self.depends_on,
            conflicts_with=self.conflicts_with,
            description=self.description,
            deprecated=self.deprecated,
            version_added=self.version_added,
            examples=self.examples,
            tags=self.tags,
        )
