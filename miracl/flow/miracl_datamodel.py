from typing import Any, Optional, List, Union, Tuple, Dict
from typing_extensions import Literal
from pydantic import BaseModel, Field, validator
from enum import Enum
from argparse import ArgumentTypeError


def parser_true_or_false(arg: str) -> bool:
    upper_arg = str(arg).upper()
    if upper_arg in ("TRUE", "T"):
        return True
    elif upper_arg in ("FALSE", "F"):
        return False
    else:
        raise ArgumentTypeError("Argument must be either 'True'/'T' or 'False'/'F'")


class ArgumentType(str, Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"
    CUSTOM_BOOL = "custom_bool"

    @property
    def python_type(self):
        return {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "custom_bool": parser_true_or_false,
        }[self.value]


class ArgumentAction(str, Enum):
    STORE = "store"
    STORE_CONST = "store_const"
    STORE_TRUE = "store_true"
    STORE_FALSE = "store_false"
    APPEND = "append"
    APPEND_CONST = "append_const"
    COUNT = "count"
    HELP = "help"
    VERSION = "version"


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


class MiraclObj(BaseModel):
    # Core argument properties
    id: str = Field(
        ...,
        description="Unique id for object",
        example="67b62f10-a6b6-4d61-9e2c-19819373265d",
    )

    name: str = Field(
        ...,
        description="Name of cli arg",
        example="conv_outname",
    )

    tags: Optional[List[str]] = Field(
        None,
        min_items=1,
        max_items=5,
        example=["flow", "ace"],
        description="Tags for categorizing or filtering arguments",
    )

    cli_s_flag: Optional[str] = Field(
        None,
        description="Short flag for cli arg",
        example="-h",
    )

    cli_l_flag: str = Field(
        ...,
        description="Long flag for cli arg",
        example="--help",
    )

    cli_const: Optional[int] = Field(
        None, description="Argparse const option", example=0
    )

    # Argument behavior
    cli_obj_type: Optional[ArgumentType] = Field(
        None,
        description="Data type of cli arg",
        example=ArgumentType.STRING,
    )

    @validator("default")
    def validate_default(cls, v, values):
        if (
            "cli_obj_type" in values
            and values["cli_obj_type"] == ArgumentType.CUSTOM_BOOL
        ):
            return parser_true_or_false(str(v))
        return v

    cli_required: Optional[bool] = Field(
        None,
        description="Whether cli arg is required",
        example=True,
    )

    default: Optional[Any] = Field(
        None,
        description="Default cli value for arg, if any",
        example=25,
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

    gui_choice_override: Optional[GuiChoiceOverrideConfig] = Field(
        None,
        description="Strings to override the choice labels in the GUI with",
        example={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
    )

    cli_nargs: Optional[Union[int, str]] = Field(
        None,
        description="Number of expected cli args",
        example=2,
    )

    @validator("cli_nargs")
    def validate_nargs(cls, value):
        if value is None:
            return value

        valid_nargs = {"+", "*", "?", "...", "N"}

        # Check if the value is an integer
        if isinstance(value, int):
            return value

        # Check if the value is a valid nargs string
        if isinstance(value, str) and value in valid_nargs:
            return value

        # If the value is a string but not valid, raise a ValueError
        if isinstance(value, str):
            raise ValueError(
                f"Invalid string value for cli_nargs: '{value}'. Must be one of {valid_nargs}."
            )

        # Raise an ArgumentTypeError for any other invalid types
        raise ArgumentTypeError(
            f"Invalid type for cli_nargs: {value}. Must be an int or one of {valid_nargs}."
        )

    # Help and documentation
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

    # GUI-specific properties
    gui_label: Optional[List[str]] = Field(
        None,
        description="Label(s) to be used in GUI",
        example=["Path to atlas dir"],
    )

    gui_group: Optional[Dict[str, str]] = Field(
        None,
        description="Group name for organizing in GUI",
        example="segmentation",
    )

    gui_order: Optional[List[float]] = Field(
        None,
        description="Order of appearance in GUI",
        example=5,
    )

    gui_widget_type: Optional[str] = Field(
        None,
        description="Specific widget to use in GUI",
        example="checkbox",
    )

    # Additional metadata
    module: str = Field(
        ...,
        description="Module or component this argument belongs to",
        example="ace",
    )

    module_group: Literal["conv", "reg", "seg", "flow"] = Field(
        ...,
        description="Module group this argument belongs to",
        example="reg",
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

    range_formatting_vals: Optional[RangeFormConfig] = Field(
        None,
        description="Config for range/formatting parameters",
        example={
            "min_val": 0,
            "max_val": 100,
            "increment_val": 1,
            "nr_decimals": 2,
        },
    )

    # Relationships
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

    class Config:
        extra = "forbid"  # Prevent additional attributes from being added
        validate_assignment = True
        validate_default = True
