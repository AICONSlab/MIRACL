from typing import Any, Optional, List, Union
from pydantic import BaseModel, Field
from enum import Enum


class ArgumentType(str, Enum):
    STRING = "str"
    INTEGER = "int"
    FLOAT = "float"
    BOOLEAN = "bool"
    LIST = "list"


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


class MiraclObj(BaseModel):
    # Core argument properties
    id: str = Field(
        ...,
        description="Unique id for object",
        example="67b62f10-a6b6-4d61-9e2c-19819373265d",
    )
    cli_name: str = Field(..., description="Name of cli arg", example="conv_outname")
    tags: Optional[List[str]] = Field(
        None,
        min_items=1,
        max_items=5,
        example=["flow", "ace"],
        description="Tags for categorizing or filtering arguments",
    )
    cli_s_flag: str = Field(..., description="Short flag for cli arg", example="-h")
    cli_l_flag: str = Field(..., description="Long flag for cli arg", example="--help")
    cli_group: str = Field(
        ..., description="Argument groups", example="single_multi_args_group"
    )

    # Argument behavior
    cli_obj_type: ArgumentType = Field(
        ..., description="Data type of cli arg", example=ArgumentType.STRING
    )
    cli_required: Optional[bool] = Field(
        None, description="Whether cli arg is required", example=True
    )

    cli_default: Optional[Any] = Field(
        None, description="Default cli value for arg, if any", example=25
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
    cli_nargs: Optional[int] = Field(
        None,
        description="Number of expected cli args",
        example=2,
    )

    # Help and documentation
    cli_help: str = Field(
        ...,
        description="Help text for cli arg",
        example="index of the GPU to use (type: %(type)s; default: %(default)s)",
    )
    cli_metavar: Optional[Union[tuple[str], str]] = Field(
        None,
        description="Name for cli arg in cli usage messages",
        example=("height", "width", "depth"),
    )

    # GUI-specific properties
    gui_label: Optional[str] = Field(
        None, description="Label to be used in GUI", example="Path to atlas dir"
    )
    gui_widget_name: Optional[str] = Field(
        None, description="Label to be used in GUI", example="Path to atlas dir"
    )
    gui_group: Optional[str] = Field(
        None, description="Group name for organizing in GUI", example="segmentation"
    )
    gui_order: Optional[int] = Field(
        None, description="Order of appearance in GUI", example=5
    )
    gui_widget_type: Optional[str] = Field(
        None, description="Specific widget to use in GUI", example="checkbox"
    )

    # Additional metadata
    module: str = Field(
        ...,
        description="Module or component this argument belongs to",
        example="registration",
    )
    description: Optional[str] = Field(
        None,
        description="Longer description of the argument's purpose",
        example="number of cpu cores deployed to pre-process image patches in parallel",
    )
    deprecated: bool = Field(
        default=False, description="Whether the argument is deprecated", example=True
    )
    version_added: str = Field(
        ..., description="Version in which this argument was added", example="2.4.0"
    )
    examples: List[str] = Field(
        default_factory=list,
        description="Usage examples for this argument",
        example="$ miracl reg clar_allen -i downsampled_niftis/SHIELD_03x_down_autoflor_chan.nii.gz -o ARI -m combined -b 1",
    )

    # Validation and constraints
    min_value: Optional[Union[int, float]] = Field(
        None, description="Minimum allowed value for numeric types", example=1
    )
    max_value: Optional[Union[int, float]] = Field(
        None, description="Maximum allowed value for numeric types", example=100
    )
    increment_value: Optional[Union[int, float]] = Field(
        None, description="Increment value", example=1
    )
    nr_decimals: Optional[int] = Field(
        None, description="Number of decimals", example=4
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
