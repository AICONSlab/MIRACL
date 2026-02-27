"""
Updated MiraclObj DataModel with GUI Namespace Structure

ALL CHANGES ANNOTATED WITH:
>>> CHANGE: [Description]
>>> NEW: [Description]
>>> REMOVED: [Description]
>>> UPDATED: [Description]
"""

from optparse import Option
from typing import (
    Any,
    Optional,
    List,
    Union,
    Tuple,
    Dict,
    ClassVar,
    TYPE_CHECKING,  # >>> NEW: Added for circular import prevention
)
from typing_extensions import Literal, TypedDict
from pydantic import (
    BaseModel,
    Field,
    validator,
    root_validator,
    DirectoryPath,
    FilePath,
    FieldValidationInfo,
    field_validator,
)
from miracl.api.enums import (
    ArgumentType,
    ArgumentAction,
    WidgetType,
    InputRestrictionType,
    CliGroup,
    ModuleType,
)
from miracl.api.utils import (
    parser_true_or_false,
)
from argparse import ArgumentTypeError
import argparse
from enum import Enum
from pathlib import Path
import re
from uuid import UUID, uuid4
import threading

# NOTE: This might become useful once type hint complexity increases and with it the
# potential for circular imports. However, it does nothign for now.
if TYPE_CHECKING:
    pass


#########
# ENUMS #
#########


class ArgumentSource(str, Enum):
    USER = "user"  # Visible in CLI and GUI
    INTERNAL = "internal"  # Hidden from help/UI but available for module piping
    DISABLED = "disabled"  # Removed from context entirely


# ============================================================================
# EXISTING HELPER CONFIGS
# ============================================================================


class RangeFormConfig(BaseModel):
    min_val: Optional[Union[int, float]] = Field(
        None,
        description="Min value",
    )
    max_val: Optional[Union[int, float]] = Field(
        None,
        description="Max value",
    )
    increment_val: Optional[Union[int, float]] = Field(
        None, description="Increment value,"
    )
    nr_decimals: Optional[int] = Field(
        None,
        description="Nr decimals",
    )


class GuiChoiceOverrideConfig(BaseModel):
    vals: Optional[List[str]] = Field(
        None,
        description="Values to use instead of cli choices",
    )
    default_val: Optional[str] = Field(
        None,
        description="Default value",
    )


class LineEditConfig(BaseModel):
    input_restrictions: Optional[InputRestrictionType] = Field(
        None, description="Type of input restrictions"
    )


class GuiWidgetSpecifics(BaseModel):
    """Container for generic widget configuration options"""

    range: Optional[RangeFormConfig] = Field(
        None,
        description="Range/formatting configuration for numeric widgets",
    )
    text: Optional[LineEditConfig] = Field(
        None,
        description="Settings for line edit widgets",
    )
    choices: Optional[GuiChoiceOverrideConfig] = Field(
        None,
        description="Override for choice labels in GUI",
    )


#################
# CUSTOM FIELDS #
#################


class GuiBase(BaseModel):
    """
    Frontend-agnostic GUI properties.

    Abstract GUI attributes that apply to all GUI frontends.
    Examples: label, widget_type, group, order

    These replace the old flat gui_* fields at the MiraclObj level.
    """

    label: Optional[List[str]] = Field(
        None,
        description="Main label(s) used in GUI",
        example=["Path to atlas dir"],
    )

    widget_type: Optional[WidgetType] = Field(
        None,
        description="Type of widget to use in GUI",
        example=WidgetType.SPINBOX,
    )

    additional_labels: Optional[List[str]] = Field(
        None,
        description="Additional label(s) used in GUI",
        example=["x-res", "y-res", "z-res"],
    )

    group: Optional[str] = Field(
        None,
        description="Group name for organizing in GUI",
        example="segmentation",
    )

    order: Optional[float] = Field(
        None,
        description="Order of appearance in GUI",
        example=5.0,
    )

    props: GuiWidgetSpecifics = Field(
        default_factory=GuiWidgetSpecifics,
        description="Widget-specific configuration",
    )
    # choice_override: Optional["GuiChoiceOverrideConfig"] = Field(
    #     None,
    #     description="Override for choice labels in GUI",
    # )
    #
    # range_formatting: Optional["RangeFormConfig"] = Field(
    #     None,
    #     description="Range/formatting configuration for numeric widgets",
    # )
    #
    # line_edit_settings: Optional["LineEditConfig"] = Field(
    #     None,
    #     description="Settings for line edit widgets",
    # )


class GuiNamespace(BaseModel):
    """
    Complete GUI configuration with base + extensions.

    Structure:
    - base: Abstract GUI properties (all frontends use)
    - extensions: Concrete frontend-specific properties (Qt, Gradio, etc.)

    Design principles:
    - Loader is agnostic to extensions content (opaque Dict[str, Any])
    - GUI serializer validates extensions for specific frontends
    - Can have multiple frontends: {"qt": {...}, "gradio": {...}}

    Example:
        gui=GuiNamespace(
            base=GuiBase(
                label=["Input Folder"],
                widget_type=WidgetType.LINE_EDIT,
            ),
            extensions={
                "qt": {
                    "placeholder_text": "Select folder...",
                    "clear_button_enabled": True,
                },
                "gradio": {
                    "placeholder": "Choose folder",
                }
            }
        )
    """

    base: GuiBase = Field(
        default_factory=GuiBase,
        description="Abstract GUI properties (frontend-agnostic)",
    )

    extensions: Optional[Dict[str, Dict[str, Any]]] = Field(
        None,
        description=(
            "Frontend-specific attributes. Keys: 'qt', 'gradio', etc. "
            "Content is opaque to loader (Dict[str, Any]), validated by GUI serializers."
        ),
    )


############
# SUB OBJS #
############


class FlowOverride(BaseModel):
    """
    Delta-based override. Anything left as None is inherited from the base MiraclObj.

    Can override GUI settings per workflow
    """

    cli_s_flag: Optional[str] = None
    cli_l_flag: Optional[str] = None
    cli_required: Optional[bool] = None
    cli_help: Optional[str] = None
    cli_group: Optional[CliGroup] = None
    cli_metavar: Optional[Union[Tuple[str, ...], str]] = None
    cli_choices: Optional[List[Any]] = None

    # Workflow visibility logic
    source: Optional[ArgumentSource] = None

    # Logic/UI overrides
    obj_default: Optional[Any] = None

    # Can override GUI namespace per workflow
    # Allows different workflows to have different GUI labels/configs
    gui: Optional["GuiNamespace"] = None


############
# MAIN OBJ #
############


class MiraclObj(BaseModel):
    instances: ClassVar[Dict[Tuple[str, str], "MiraclObj"]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def model_post_init(self, __context):
        """
        Called by Pydantic after object initialization.
        Registers the instance in the singleton registry.

        (unchanged)
        """
        key = (self.module, self.name)
        with MiraclObj._lock:
            if key in MiraclObj.instances:
                raise RuntimeError(
                    f"Duplicate MiraclObj for module='{self.module}', name='{self.name}'"
                )
            MiraclObj.instances[key] = self

    id: UUID = Field(
        default_factory=uuid4,
        description="Unique id for object",
        example="67b62f10-a6b6-4d61-9e2c-19819373265d",
        frozen=True,
    )

    name: str = Field(
        ...,
        description="Name of cli arg",
        example="conv_outname",
    )

    cli_l_flag: str = Field(
        ...,
        description="Long flag for cli arg",
        example="--help",
    )

    content: Optional[Any] = Field(
        None, description="Content associated with flag variable input"
    )

    source: ArgumentSource = Field(
        default=ArgumentSource.USER,
        description="Visibility/availability of this argument",
    )

    input_dirpath_field: Optional[DirectoryPath] = Field(
        default=None,
        description="Input folder path for raw data",
        alias="input_dirpath",
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

    dirpath_field: Optional[DirectoryPath] = Field(
        default=None,
        description="Used for MIRACL interfaces to pass directory paths. This uses an alias and can only be set once.",
        alias="dirpath",
    )

    @property
    def dirpath(self) -> Optional[DirectoryPath]:
        return self.dirpath_field

    @dirpath.setter
    def dirpath(self, value: Optional[DirectoryPath]):
        if self.dirpath_field is None:
            self.dirpath_field = value
        else:
            raise ValueError("dirpath cannot be changed once set")

    filepath_field: Optional[FilePath] = Field(
        default=None,
        description="Used for MIRACL interfaces to pass file paths. This uses an alias and can only be set once.",
        alias="filepath",
    )

    @property
    def filepath(self) -> Optional[FilePath]:
        return self.filepath_field

    @filepath.setter
    def filepath(self, value: Optional[FilePath]):
        if self.filepath_field is None:
            self.filepath_field = value
        else:
            raise ValueError("filepath cannot be changed once set")

    obj_default: Optional[
        Union[Path, int, float, List[Any], str, Dict[str, Any], bool]
    ] = Field(
        None,
        description="Default obj value for arg, if any, for e.g. cli or gui",
        example=25,
    )

    depends_on: Optional[List[str]] = Field(
        None,
        description="IDs of arguments this one depends on",
        example=["67b62f10-a6b6-4d61-9e2c-19819373265d"],
    )

    conflicts_with: Optional[List[str]] = Field(
        None,
        description="IDs of arguments this one conflicts with",
        example=["4ca6271e-c351-4230-bd20-b0f606101c42"],
    )

    cli_s_flag: Optional[str] = Field(
        None,
        description="Short flag for cli arg",
        example="-h",
    )

    cli_const: Optional[int] = Field(
        None, description="Argparse const option", example=0
    )

    cli_obj_type: Optional[ArgumentType] = Field(
        None,
        description="Data type of cli arg",
        example=ArgumentType.STRING,
    )

    cli_required: Optional[bool] = Field(
        None,
        description="Whether cli arg is required",
        example=True,
    )

    cli_choices: Optional[List[Any]] = Field(
        None,
        description="List of allowed choices/values for the cli arg",
        example=[10, 25, 50],
    )

    cli_action: Optional[ArgumentAction] = Field(
        None,
        description="Action to be taken when cli arg is encountered",
        example=ArgumentAction.STORE_FALSE,
    )

    cli_nargs: Optional[Union[int, str]] = Field(
        None,
        description="Number of expected cli args",
        example=2,
    )

    cli_help: str = Field(
        ...,
        description="Help text for cli arg",
        example="index of the GPU to use (type: %(type)s; default: %(default)s)",
    )

    cli_metavar: Optional[Union[Tuple[str, ...], str]] = Field(
        None,
        description="Name for cli arg in cli usage messages",
        example=("height", "width", "depth"),
    )

    cli_group: Optional[CliGroup] = Field(
        None,
        description="Argparse group the object belongs to when used in a stand-alone module",
        example=CliGroup.CONV_TIFF_NII,
    )

    # ---------------------------------------------------------------------------------
    # DEPRECATED: FLAT GUI FIELDS
    #
    # These fields are DEPRECATED and kept only for backward compatibility.
    # New code should use the `gui` namespace field instead.
    # These will be removed in a future version.
    #
    # Migration path:
    # OLD: gui_label=["Input Folder"]
    # NEW: gui=GuiNamespace(base=GuiBase(label=["Input Folder"]))
    # ---------------------------------------------------------------------------------
    gui_choice_override: Optional[GuiChoiceOverrideConfig] = Field(
        None,
        description="DEPRECATED: Use gui.base.choice_override instead",
        deprecated=True,
    )

    gui_label: Optional[List[str]] = Field(
        None,
        description="DEPRECATED: Use gui.base.label instead",
        deprecated=True,
    )

    gui_additional_labels: Optional[List[str]] = Field(
        None,
        description="DEPRECATED: Use gui.base.additional_labels instead",
        deprecated=True,
    )

    gui_group: Optional[Dict[str, str]] = Field(
        None,
        description="DEPRECATED: Use gui.base.group instead",
        deprecated=True,
    )

    gui_order: Optional[List[float]] = Field(
        None,
        description="DEPRECATED: Use gui.base.order instead",
        deprecated=True,
    )

    gui_widget_type: Optional[WidgetType] = Field(
        None,
        description="DEPRECATED: Use gui.base.widget_type instead",
        deprecated=True,
    )

    range_formatting_vals: Optional[RangeFormConfig] = Field(
        None,
        description="DEPRECATED: Use gui.base.range_formatting instead",
        deprecated=True,
    )

    line_edit_settings: Optional[LineEditConfig] = Field(
        None,
        description="DEPRECATED: Use gui.base.line_edit_settings instead",
        deprecated=True,
    )

    # ---------------------------------------------------------------------------------
    # NEW: GUI NAMESPACE FIELD
    #
    # This is the new way to define GUI properties.
    # Replaces all the flat gui_* fields above.
    # ---------------------------------------------------------------------------------
    gui: Optional[GuiNamespace] = Field(
        None,
        description="GUI configuration namespace (base + frontend extensions)",
    )

    module: str = Field(
        ...,
        description="Module or component this argument belongs to",
        example="ace",
    )

    module_group: str = Field(
        ...,
        description="Module group this argument belongs to",
        example="reg",
    )

    flow: Optional[Dict[str, FlowOverride]] = Field(
        None,
        description="Workflow specific overrides (key = workflow name from ModuleType enum)",
    )

    description: Optional[str] = Field(
        None,
        description="Longer description of the argument's purpose",
        example="number of cpu cores deployed to pre-process image patches in parallel",
    )

    deprecated: bool = Field(
        default=False,
        description="Whether the argument is deprecated",
        example=True,
    )

    version_added: str = Field(
        ...,
        description="Version in which this argument was added",
        example="2.4.0",
    )

    examples: List[str] = Field(
        default_factory=list,
        description="Usage examples for this argument",
        example="$ miracl reg clar_allen -i downsampled_niftis/SHIELD_03x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1",
    )

    tags: Optional[List[str]] = Field(
        None,
        min_items=1,
        max_items=10,
        example=["flow", "ace"],
        description="Tags for categorizing or filtering arguments",
    )

    ###########################
    # Central object resolver #
    ###########################

    def resolve(self, context: ModuleType) -> Optional[Dict[str, Any]]:
        """
        Merges base attributes with context overrides using Pydantic Delta logic.

        >>> CHANGES from original:
        1. Excludes 'gui' from initial dump (was only 'flow')
        2. Phase 4: Populates gui_* fields from gui.base
        3. Phase 5: Populates gui_extensions with ALL frontend data
        4. Handles GUI overrides from flow

        Args:
            context: Workflow context (MODULE, FLOW_ACE, etc.)

        Returns:
            Resolved object dict with ALL data (CLI + GUI base + ALL GUI extensions)
            Returns None if source is DISABLED

        What gets returned:
        {
            # CLI fields
            "cli_l_flag": "input",
            "cli_required": True,
            ...

            # >>> NEW: GUI base fields (prefixed with gui_)
            "gui_label": ["Input Folder"],
            "gui_widget_type": WidgetType.LINE_EDIT,
            "gui_group": "Input/Output",
            ...

            # >>> NEW: ALL GUI extensions (all frontends)
            "gui_extensions": {
                "qt": {"placeholder_text": "...", ...},
                "gradio": {"placeholder": "...", ...}
            }
        }
        """

        # >>> CHANGE: Phase 1 - Exclude both 'flow' AND 'gui' from initial dump
        # Reason: We handle GUI separately to support namespace structure
        resolved_data = self.model_dump(exclude={"flow", "gui"})

        # Phase 2: Apply workflow overrides if not MODULE context
        if context != ModuleType.MODULE:
            if not self.flow or context.value not in self.flow:
                raise ValueError(
                    f"Configuration Error: MiraclObj '{self.name}' (ID: {self.id}) is missing a required workflow entry for '{context.value}'. Every object used in a workflow must explicitly define its flow settings."
                )

            # Merge override into resolved data
            override = self.flow[context.value]
            # >>> CHANGE: Exclude 'gui' from delta dump initially
            # Reason: GUI overrides handled separately below
            delta = override.model_dump(exclude_unset=True, exclude={"gui"})
            resolved_data.update(delta)

        # Phase 3: Check source and handle DISABLED/INTERNAL
        if "source" not in resolved_data:
            raise RuntimeError(
                f"Internal error: 'source' field missing from resolved data for "
                f"MiraclObj '{self.name}' (ID: {self.id}). This indicates a serious "
                f"model configuration problem."
            )

        final_source = resolved_data["source"]

        # Handle DISABLED - filter out entirely
        if final_source == ArgumentSource.DISABLED:
            return None

        # Handle INTERNAL - modify help and requirements
        if final_source == ArgumentSource.INTERNAL:
            resolved_data["cli_help"] = argparse.SUPPRESS
            resolved_data["cli_required"] = False
            resolved_data["gui_hidden"] = True

        # >>> NEW: Phase 4 - Add GUI base attributes (abstract, frontend-agnostic)
        # These are prefixed with gui_ and come from gui.base
        gui_to_use = self.gui

        # >>> NEW: Check if flow override has GUI settings
        # Allows different workflows to have different GUI labels/configs
        if context != ModuleType.MODULE and self.flow and context.value in self.flow:
            override = self.flow[context.value]
            if override.gui:
                gui_to_use = override.gui  # Use flow's GUI override instead of base

        if gui_to_use and gui_to_use.base:
            gui_base = gui_to_use.base.model_dump(exclude_unset=True)
            # Add each GUI base field with gui_ prefix
            for key, value in gui_base.items():
                resolved_data[f"gui_{key}"] = value

        # >>> NEW: Phase 5 - Add ALL GUI extensions (all frontends)
        # Returns complete extensions dict so introspector gets everything
        # Serializers will extract the frontend they need
        if gui_to_use and gui_to_use.extensions:
            resolved_data["gui_extensions"] = gui_to_use.extensions.copy()
            # This returns: {"qt": {...}, "gradio": {...}, ...}
            # ALL frontends included - serializer picks what it needs

        return resolved_data

    #####################
    # CUSTOM VALIDATORS #
    #####################

    @validator("cli_obj_type")
    def validate_type(cls, v, values):
        if (
            "cli_obj_type" in values
            and values["cli_obj_type"] == ArgumentType.CUSTOM_BOOL
        ):
            return parser_true_or_false(str(v))
        return v

    @validator("cli_nargs")
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
                f"Invalid string value for cli_nargs: '{value}'. Must be one of {valid_nargs}."
            )

        raise ArgumentTypeError(
            f"Invalid type for cli_nargs: {value}. Must be an int or one of {valid_nargs}."
        )

    @validator("obj_default")
    def validate_default(cls, value):
        if value is None:
            return value

        allowed_types = (Path, int, float, list, str, dict, bool)

        if not isinstance(value, allowed_types):
            raise ValueError(
                f"Invalid type for default: {type(value)}. Must be one of {allowed_types}."
            )

        return value

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v, info: FieldValidationInfo):
        obj_type = info.data.get("cli_obj_type")

        if obj_type is None or v is None:
            return v

        python_type = obj_type.python_type

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

    @field_validator("cli_s_flag", "cli_l_flag", mode="before")
    def check_flag(cls, v: str, info: FieldValidationInfo):
        flag_name = info.field_name
        obj_id = info.data.get("id", "unknown-id")
        module_type_str = info.data.get("module", "unknown-module")

        if not v:
            raise ValueError(
                f"Empty flag '{flag_name}' for object '{obj_id}' in module '{module_type_str}'"
            )

        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                f"Invalid characters in flag '{flag_name}' ('{v}') for object '{obj_id}' in module '{module_type_str}'"
            )

        return v

    @field_validator("dirpath_field", mode="before")
    def create_directory_if_not_exists(cls, value):
        if value is not None:
            path = Path(value)
            path.mkdir(parents=True, exist_ok=True)
            return path
        return value

    ################
    # CLASS CONFIG #
    ################

    class Config:
        extra = "forbid"
        validate_assignment = True
        validate_default = True
