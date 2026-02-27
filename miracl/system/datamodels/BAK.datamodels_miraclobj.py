from typing import (
    Any,
    Optional,
    List,
    Union,
    Tuple,
    Dict,
    ClassVar,
)
from typing_extensions import Literal
from pydantic import (
    BaseModel,
    Field,
    validator,
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
    ModuleType,  # <<< NEW: Added for resolve method >>>
)
from miracl.api.utils import (
    parser_true_or_false,
)
from argparse import ArgumentTypeError
from pathlib import Path
import re
from uuid import UUID, uuid4
import threading

#################
# CUSTOM FIELDS #
#################


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


# <<< NEW: Replaces TypedDict to allow exclude_unset logic >>>
class FlowOverride(BaseModel):
    """
    Delta-based override for workflow contexts.
    Only fields explicitly set here will override the base MiraclObj.
    """

    cli_s_flag: Optional[str] = None
    cli_l_flag: Optional[str] = None
    cli_required: Optional[bool] = None  # Named same as base for easy merge
    cli_group: Optional[CliGroup] = None
    cli_help: Optional[str] = None
    cli_metavar: Optional[Union[Tuple[str, ...], str]] = None
    disabled: bool = False


############
# MAIN OBJ #
############


class MiraclObj(BaseModel):
    _instances: ClassVar[Dict[Tuple[str, str], "MiraclObj"]] = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def model_post_init(self, __context):
        key = (self.module, self.name)
        with MiraclObj._lock:
            if key in MiraclObj._instances:
                raise RuntimeError(
                    f"Duplicate MiraclObj for module='{self.module}', name='{self.name}'"
                )
            MiraclObj._instances[key] = self

    # ---------------------------------------------------------------------------------
    # REQUIRED FIELDS
    # ---------------------------------------------------------------------------------
    id: UUID = Field(default_factory=uuid4, description="Unique id", frozen=True)
    name: str = Field(..., description="Name of cli arg")
    cli_l_flag: str = Field(..., description="Long flag for cli arg")

    # ---------------------------------------------------------------------------------
    # GENERAL
    # ---------------------------------------------------------------------------------
    content: Optional[Any] = Field(
        None, description="Content associated with flag input"
    )

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

    obj_default: Optional[
        Union[Path, int, float, List[Any], str, Dict[str, Any], bool]
    ] = Field(None)
    depends_on: Optional[List[str]] = Field(None)
    conflicts_with: Optional[List[str]] = Field(None)

    # ---------------------------------------------------------------------------------
    # CLI
    # ---------------------------------------------------------------------------------
    cli_s_flag: Optional[str] = Field(None)
    cli_const: Optional[int] = Field(None)
    cli_obj_type: Optional[ArgumentType] = Field(None)
    cli_required: Optional[bool] = Field(None)
    cli_choices: Optional[List[Any]] = Field(None)
    cli_action: Optional[ArgumentAction] = Field(None)
    cli_nargs: Optional[Union[int, str]] = Field(None)
    cli_help: str = Field(...)
    cli_metavar: Optional[Union[Tuple[str, ...], str]] = Field(None)
    cli_group: Optional[CliGroup] = Field(None)

    # ---------------------------------------------------------------------------------
    # GUI
    # ---------------------------------------------------------------------------------
    gui_choice_override: Optional[GuiChoiceOverrideConfig] = Field(None)
    gui_label: Optional[List[str]] = Field(None)
    gui_additional_labels: Optional[List[str]] = Field(None)
    gui_group: Optional[Dict[str, str]] = Field(None)
    gui_order: Optional[List[float]] = Field(None)
    gui_widget_type: Optional[WidgetType] = Field(None)
    range_formatting_vals: Optional[RangeFormConfig] = Field(None)
    line_edit_settings: Optional[LineEditConfig] = Field(None)

    # ---------------------------------------------------------------------------------
    # MIRACL
    # ---------------------------------------------------------------------------------
    module: str = Field(...)
    module_group: Literal["conv", "reg", "seg", "flow", "stats"] = Field(...)

    # <<< CHANGED: Flow updated from TypedDict to Dict[str, FlowOverride] >>>
    flow: Optional[Dict[Literal["ace", "mapl3"], FlowOverride]] = Field(
        None,
        description="Context-specific overrides for workflows",
    )

    description: Optional[str] = Field(None)
    deprecated: bool = Field(default=False)
    version_added: str = Field(...)
    examples: List[str] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(None, min_items=1, max_items=5)

    # <<< NEW: The logic that merges flow deltas into the base object >>>
    def resolve(self, context: ModuleType) -> Optional[Dict[str, Any]]:
        """
        Calculates final attributes by merging base with context overrides.
        Returns None if disabled in the given context.
        """
        # Base case: standalone module
        if context == ModuleType.MODULE:
            return self.model_dump(exclude={"flow"})

        # Workflow case: check for override
        if not self.flow or context.value not in self.flow:
            return None

        override = self.flow[context.value]
        if override.disabled:
            return None

        # Merge Logic: Base + Override (exclude_unset=True)
        resolved_data = self.model_dump(exclude={"flow"})
        delta = override.model_dump(exclude_unset=True, exclude={"disabled"})
        resolved_data.update(delta)

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
        raise ValueError(f"Invalid cli_nargs: {value}")

    @validator("obj_default")
    def validate_default(cls, value):
        if value is None:
            return value
        allowed_types = (Path, int, float, list, str, dict, bool)
        if not isinstance(value, allowed_types):
            raise ValueError(f"Invalid type for default: {type(value)}")
        return value

    @validator("content", always=True)
    def validate_content(cls, v, values):
        obj_type = values.get("cli_obj_type")
        if obj_type is not None and v is not None:
            try:
                return obj_type.python_type(v)
            except ValueError:
                raise ValueError(f"Cannot convert {v}")
        return v

    @field_validator("cli_s_flag", "cli_l_flag", mode="before")
    def check_flag(cls, v: str, info: FieldValidationInfo):
        if not v:
            return v  # Some flags might be None if handled by flow
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(f"Invalid characters in flag: {v}")
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
        validate_assignment = (
            True  # <<< CRITICAL: Ensures content is validated when set by CLI
        )
        validate_default = True
