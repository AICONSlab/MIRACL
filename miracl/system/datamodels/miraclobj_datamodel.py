"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca)

MiraclObj Basemodel defintions and resolver using Pydantic v2.

This is the blueprint for all MIRACL object singletons!

NOTE: Some recommended settings for conf.py:

     extensions = [
         'sphinx.ext.napoleon',
         'sphinx_contrib.autodoc_pydantic',
     ]

     # autodoc_pydantic settings
     autodoc_pydantic_model_show_json = False
     autodoc_pydantic_model_show_config_summary = False
     autodoc_pydantic_field_list_validators = False
     autodoc_pydantic_model_member_order = "bysource"

     # Napoleon settings
     napoleon_google_docstring = True
     napoleon_use_ivar = True

"""

# =====================================================================================
# IMPORTS
# =====================================================================================

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
from argparse import ArgumentTypeError
import argparse
from enum import Enum
from pathlib import Path
from uuid import UUID, uuid4
import threading
import re


# =====================================================================================
# ENUMS
# =====================================================================================


class ArgumentSource(str, Enum):
    """
    Source/visibility of an argument within the system.

    Attributes:
        USER: Visible in both CLI and GUI.
        INTERNAL: Hidden from help/UI; used for module piping. In 99% of the cases,
            a MIRACL dev will want to use this as the default for required args in
            workflows.
        DISABLED: Completely removed from context i.e. not passed procedurally.
    """

    USER = "user"
    INTERNAL = "internal"
    DISABLED = "disabled"


# =====================================================================================
# GUI STRUCTURE
# =====================================================================================


class RangeFormConfig(BaseModel):
    """Definitions for range-based widgets like SPINBOX or SLIDER."""

    min_val: Optional[Union[int, float]] = Field(
        None,
        description="Min allowed value for widget",
    )
    max_val: Optional[Union[int, float]] = Field(
        None,
        description="Max allowed value for widget",
    )
    increment_val: Optional[Union[int, float]] = Field(
        None,
        description="Step size for increments",
    )
    nr_decimals: Optional[int] = Field(
        None,
        description="Number of decimal places to display",
    )


class GuiChoiceOverrideConfig(BaseModel):
    """
    Overrides default choices for dropdown widgets with custom labels.

    Useful for mapping internally used values to more user-friendly labels
    without changing the underlying :class:`~.ArgumentSource` logic.
    """

    vals: Optional[List[str]] = Field(
        None,
        description="Human-readable labels for the dropdown",
    )
    default_val: Optional[str] = Field(
        None,
        description="Default value, must match vals label",
    )


class LineEditConfig(BaseModel):
    """
    Configuration for line edit widgets.

    :class:`~miracl.api.enums.InputRestrictionType` is used to define the restriction
    type.
    """

    input_restrictions: Optional[InputRestrictionType] = Field(
        None,
        description="Type of input restrictions applied to text input",
    )


class GuiWidgetSpecifics(BaseModel):
    """Generic widget configuration options."""

    range: Optional[RangeFormConfig] = Field(
        None,
        description="Range/formatting configuration for numeric widgets and sliders",
    )
    text: Optional[LineEditConfig] = Field(
        None,
        description="Input restriction settings for line edit widgets",
    )
    choices: Optional[GuiChoiceOverrideConfig] = Field(
        None,
        description="Override for choice labels in GUI",
    )


class GuiBase(BaseModel):
    """
    Frontend-agnostic GUI properties. Ideally these properties can be used for all
    GUI frontends e.g. PyQt, webbased etc.
    """

    label: List[str] = Field(
        None,
        description="Main label(s) used in GUI, can be more than one for custom widgets",
    )
    widget_type: Optional[WidgetType] = Field(
        None,
        description="Type of widget to use in GUI",
    )
    additional_labels: Optional[List[str]] = Field(
        None,
        description="Additional label(s) used in GUI, also used for custom widgets",
    )
    group: CliGroup = Field(
        None,
        description="Group name for organizing in GUI",
    )
    order: Optional[float] = Field(
        None,
        description="Order of appearance in GUI",
    )

    props: GuiWidgetSpecifics = Field(
        default_factory=GuiWidgetSpecifics,
        description="Widget-specific configuration properties",
    )


class GuiNamespace(BaseModel):
    """
    Complete GUI configuration including base properties and extensions. This is the
    full GUI config. It holds the actual GUI settings that will be used at runtime.
    """

    base: GuiBase = Field(
        default_factory=GuiBase,
        description="The core GUI properties, should be the same for all frontends",
    )
    extensions: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description="Frontend-specific attributes. Keys: 'qt', 'gradio', etc.",
    )


class GuiDelta(BaseModel):
    """
    Delta object for overriding GUI properties in a FlowOverride. This is a delta i.e.
    a partial config. It holds only the overrides that will be applied on top of the
    base config hence why all of these fields are optional.

    Attributes:
        base: Optional overrides for core GUI properties.
        extensions: Optional overrides for frontend-specific attributes.
    """

    base: Optional[GuiBase] = None
    extensions: Optional[Dict[str, Dict[str, Any]]] = None


# =====================================================================================
# CLI STRUCTURE
# =====================================================================================


class CLISpec(BaseModel):
    """
    Complete CLI specification for an argument. This is the core definition for a
    singleton!
    """

    s_flag: Optional[str] = Field(
        None,
        description="Short flag for cli arg",
        examples=["-i"],
    )
    l_flag: str = Field(
        ...,
        description="Long flag for CLI arg",
        examples=["--input"],
    )
    help: str = Field(
        ...,
        description="Help text for CLI arg and overlay help for the GUI",
    )
    required: Optional[bool] = Field(
        None,
        description="Whether CLI arg is required",
    )
    obj_type: Optional[ArgumentType] = Field(
        None,
        description="Data type of CLI arg",
    )

    default: Optional[Union[Path, int, float, List[Any], str, Dict[str, Any], bool]] = (
        Field(None, description="Default obj value for arg, if any")
    )

    nargs: Optional[Union[int, str]] = Field(
        None,
        description="Number of expected CLI args",
    )
    choices: Optional[List[Any]] = Field(
        None,
        description="List of allowed choices/values for the CLI arg",
    )
    action: Optional[ArgumentAction] = Field(
        None,
        description="Action to be taken when CLI arg is encountered",
    )
    const: Optional[Any] = Field(
        None,
        description="Argparse const option i.e. constant value for specific argparse actions",
    )
    metavar: Optional[Union[str, Tuple[str, ...]]] = Field(
        None,
        description="Name for CLI arg in CLI usage messages, can be more user-friendly considering how verbose MIRACL args can be",
    )
    group: Optional[CliGroup] = Field(
        None,
        description="Argparse group the object belongs to",
        examples=["CliGroup.STATS_TFCE"],
    )

    @field_validator("nargs", mode="before")
    @classmethod
    def validate_nargs(cls, value):
        """
        Validates the 'nargs' field to ensure it matches argparse conventions.

        Args:
            value: The value to validate.

        Returns:
            The validated integer or string value.

        Raises:
            ValueError: If the string value is not a valid argparse symbol.
            ArgumentTypeError: If the type is neither an integer nor a valid string.
        """
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

    @field_validator("default", mode="before")
    @classmethod
    def validate_default(cls, value):
        """
        Validates that default value is of a type that is supported in the CLI.

        Args:
            value: The default value to validate.

        Returns:
            The validated value.

        Raises:
            ValueError: If the type is not in the allowed list of types.
        """
        if value is None:
            return value
        allowed_types = (Path, int, float, list, str, dict, bool)
        if not isinstance(value, allowed_types):
            raise ValueError(
                f"Invalid type for default: {type(value)}. Must be one of {allowed_types}."
            )
        return value


class CLIDelta(BaseModel):
    """
    Delta for CLI overrides in FlowOverride. All of these are optional overrides for
    the base values in the CLI.
    """

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


# =====================================================================================
# RESOLVED RUNTIME OBJECT
# =====================================================================================


class ResolvedMiraclObj(BaseModel):
    """
    Immutable runtime representation of a MIRACL object.

    This object is used by builders and serializers during execution after all
    overrides and context-specific logic have been resolved.

    This is super important as it provides the final object that is registered to the
    registry based on the ModuleType. So for example for ModuleType.MODULE, the
    resolver will return the attributes (e.g. s_flag) used in the model whereas
    ModuleType.FLOW_MAPL3 will return whatever is defined in the flow definition for,
    in this case, MAPL3.

    Attributes:
        id: Unique identifier that gets newly generated at runtime. It only lives for
            the duration of the runtime.
        name: Name of the argument.
        module: Module the argument belongs to.
        module_group: Grouping of the module.
        source: Resolved visibility/source of the argument.
        cli: Resolved CLI specification.
        gui: Resolved GUI specification.
        content: The actual runtime value for this argument. This will get assigned once.
            In the DAG, the content value will actually belong to a dictionary copy, not
            to the original singleton registered to the registry.
        gui_hidden: Whether the argument is hidden in the GUI.
        gui_extensions: Frontend-specific GUI extensions.
        depends_on: List of other objects this object depends on. This is useful, for
            example in the GUI when a widget can only be used based on whether another
            widget is or isn't used.
        conflicts_with: List of other objects this object conflicts with.
        description: Human-readable description.
        deprecated: Whether the object is deprecated.
        version_added: Version in which the object was introduced.
        examples: Usage examples.
        tags: Optional tags for categorization.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID
    name: str
    module: str
    module_group: str
    source: ArgumentSource

    cli: CLISpec
    gui: Optional[GuiNamespace]

    content: Optional[Any] = Field(
        None,
        description="Runtime value for this argument",
    )
    gui_hidden: bool = Field(
        default=False,
        description="Whether this argument should be hidden in GUI",
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

    tags: Optional[List[str]] = Field(None, min_length=1, max_length=10)

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, val, info: ValidationInfo):
        """
        Validates and parses the value in the 'content' attribute using the CLI parser.
        This is also super important for example when the object type is an int but
        the input is a string. This validator will convert the string input to what
        is expected based on the type definition of the Pydantic object.

        Args:
            val: The value to validate.
            info: Pydantic validation info containing the CLI spec.

        Returns:
            The parsed and validated Python object.

        Raises:
            ValueError: If validation or conversion fails.
        """

        cli_spec = info.data.get("cli")
        if cli_spec is None or cli_spec.obj_type is None or val is None:
            return val

        parser_func = cli_spec.obj_type.cli_parser

        python_type = cli_spec.obj_type.python_type

        if python_type is list:
            if not isinstance(val, list):
                raise ValueError(f"Expected list for content, got {type(val).__name__}")
            return list(val)

        if isinstance(val, list):
            try:
                return [parser_func(item) for item in val]
            except (ValueError, TypeError):
                raise ValueError(f"Cannot convert elements in {val} to {python_type}")

        try:
            return parser_func(val)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Validation failed for {cli_spec.obj_type}: {e}")


# =====================================================================================
# FLOW OVERRIDE
# =====================================================================================


class FlowOverride(BaseModel):
    """
    Container for context-specific overrides of CLI, GUI, and source settings.

    Attributes:
        cli: CLI property overrides.
        gui: GUI property overrides.
        source: Visibility/source override.
    """

    cli: Optional[CLIDelta] = None
    gui: Optional[GuiDelta] = None
    source: Optional[ArgumentSource] = None


# =====================================================================================
# MAIN OBJECT
# =====================================================================================


class MiraclObj(BaseModel):
    """
    Definition-time MIRACL object singleton.

    This class acts as the blueprint for all MIRACL objects, handling registration,
    flag validation, and context-aware resolution. Super, super important!!

    Attributes:
        instances: Registry of all MiraclObj instances.
        id: Unique identifier. Auto-generated UUID at runtime. Lifetime == runtime.
        name: Name of the object.
        module: Module path.
        module_group: Group name for the module.
        source: Default visibility/source.
        cli: Base CLI specification.
        gui: Base GUI specification.
        flow: Mapping of workflow contexts to overrides.
        input_dirpath: Directory path used as input.
        dirpath: Directory path (created automatically if missing).
        filepath: File path.
        depends_on: Dependencies.
        conflicts_with: Conflicts.
        description: Description.
        deprecated: Deprecation status.
        version_added: Version added.
        examples: List of examples.
        tags: Search tags.
    """

    # I defined these to make the model defensive for development. This should catch
    # invalid data at construction, re-assignment and also prevent accidental extra
    # fields and typos. It's relatively strict since this is a critical data model.
    model_config = ConfigDict(
        extra="forbid",  # Don't allow fields not defined in the object class. Enforces schemas and catches typos.
        validate_assignment=True,  # Validate fields every time they are reassigned, not only at initialization.
        validate_default=True,  # Validate default values when model is first created.
    )

    instances: ClassVar[Dict[Tuple[str, str], "MiraclObj"]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def model_post_init(self, __context):
        """
        Registers the object instance in the global registry.

        Ensures that no duplicate objects are defined for the same module and name.
        Obviously also very important since successful execution of the entire
        workflow depends on the correctness of the registry and its registered modules.

        Args:
            __context: Pydantic initialization context.

        Raises:
            RuntimeError: If a duplicate object is detected.
        """

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
        """Property for accessing the input directory path."""
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
        """Property for accessing the directory path."""
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
        """Property for accessing the file path."""
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

    tags: Optional[List[str]] = Field(None, min_length=1, max_length=10)

    @field_validator("dirpath_field", mode="before")
    @classmethod
    def create_directory_if_not_exists(cls, value):
        """
        Pre-validator that creates the directory on disk if it doesn't exist.

        Args:
            value: The directory path to check/create.

        Returns:
            The Path object.
        """

        if value is not None:
            path = Path(value)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return value

    # =================================================================================
    # CONTEXTUAL FLAG VALIDATION
    # =================================================================================

    @model_validator(mode="after")
    def validate_flags_with_context(self) -> "MiraclObj":
        """
        Validates CLI flag formats after model construction.

        Ensures that flags contain only allowed characters and provides detailed error
        context including object ID and module name.

        Runs after all field-level validators (like field_validator) have completed.
        At this point, the entire model is validated, so we can access any field
        including nested objects like self.flow which allows us to validate override
        flags as well.


        Returns:
            The validated MiraclObj instance.
        """

        # Validate base CLI
        self._check_flag_format(
            self.cli.s_flag,
            "cli.s_flag",
        )
        self._check_flag_format(
            self.cli.l_flag,
            "cli.l_flag",
        )

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
        """
        Helper method to validate individual flag strings against a regex.

        Args:
            flag_value: The string value of the flag.
            field_context: Descriptive name of the field for error reporting.

        Raises:
            ValueError: If the flag is empty or contains invalid characters.
        """

        # Skip validation for unset flags. Flags can be None for example when a method
        # only has a short flag but no long flag.
        if flag_value is None:
            return

        if not flag_value:
            raise ValueError(
                f"Empty flag '{field_context}' for object '{self.id}' in module '{self.module}'"
            )

        if not re.match(r"^[a-zA-Z0-9_-]+$", flag_value):
            raise ValueError(
                f"Invalid characters in flag '{field_context}' ('{flag_value}') for object '{self.id}' in module '{self.module}'"
            )

    # =================================================================================
    # RESOLVE METHOD
    # =================================================================================

    def resolve(self, context: ModuleType) -> Optional[ResolvedMiraclObj]:
        """
        Resolves the definition-time object into a runtime object based on context.

        Super, mega, hyper important!!

        Applies workflow-specific overrides and calculates visibility states (e.g.,
        hiding internal arguments).

        Args:
            context: The execution context (e.g., ModuleType.MODULE or a specific
            workflow like ModuleType.CliType).

        Returns:
            A ResolvedMiraclObj if visible, otherwise None.

        Raises:
            ValueError: If a required workflow entry is missing or configuration is invalid.
        """
        final_cli = self.cli.model_copy()
        final_gui = self.gui.model_copy() if self.gui else None
        final_source = self.source

        if context != ModuleType.MODULE:
            if not self.flow or context.value not in self.flow:
                raise ValueError(
                    f"Configuration Error: MiraclObj '{self.name}' (ID: {self.id}) is missing required workflow entry for '{context.value}'. Every object used in a workflow must explicitly define its flow settings."
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
