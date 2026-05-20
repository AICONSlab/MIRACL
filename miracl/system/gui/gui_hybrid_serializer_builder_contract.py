"""
Code written and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca).

Shared data models between MiraclGUISerializer and any GUI builder implementation (PyQt,
Gradio, etc.).
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ConfigDict, field_validator, model_validator


#######################################################################################
# SENTINEL
#######################################################################################
UNGROUPED_TAB_KEY: str = "_ungrouped"


#######################################################################################
# JSON TYPE ENUM
#######################################################################################

_JSON_TYPE_MAP: Dict["JSONType", Type] = {}

_PYTHON_TYPE_TO_JSON_VALUE: Dict[Type, str] = {}


class JSONType(str, Enum):
    """
    Closed enumeration of Python types that may appear as ArgumentType.python_type
    <miracl.system.datamodels.ArgumentType.python_type>, expressed as JSON-safe string
    values.
    """

    INTEGER = "int"
    FLOAT = "float"
    STRING = "str"
    BOOLEAN = "bool"
    LIST = "list"
    PATH = "Path"

    @property
    def python_type(self) -> Type:
        """
        Resolve this enum member back to the corresponding Python type.
        """
        return _JSON_TYPE_MAP[self]


_JSON_TYPE_MAP.update(
    {
        JSONType.INTEGER: int,
        JSONType.FLOAT: float,
        JSONType.STRING: str,
        JSONType.BOOLEAN: bool,
        JSONType.LIST: list,
        JSONType.PATH: Path,
    }
)

_PYTHON_TYPE_TO_JSON_VALUE.update(
    {
        int: JSONType.INTEGER.value,
        float: JSONType.FLOAT.value,
        str: JSONType.STRING.value,
        bool: JSONType.BOOLEAN.value,
        list: JSONType.LIST.value,
        Path: JSONType.PATH.value,
    }
)


#######################################################################################
# WIDGET TYPE ENUM
#######################################################################################


class WidgetType(str, Enum):
    """
    Complete enumeration of widget types that a GUI builder knows how to render.
    """

    SPINBOX = "SPINBOX"
    DOUBLE_SPINBOX = "DOUBLE_SPINBOX"
    NULLABLE_DOUBLE_SPINBOX = "NULLABLE_DOUBLE_SPINBOX"
    LINE_EDIT = "LINE_EDIT"
    COMBO_BOX = "COMBO_BOX"
    PATH_INPUT = "PATH_INPUT"
    CHECKBOX = "CHECKBOX"
    SLIDER = "SLIDER"
    TEXT_AREA = "TEXT_AREA"
    DATE_PICKER = "DATE_PICKER"
    COLOR_PICKER = "COLOR_PICKER"
    MULTI_LINE_EDIT = "MULTI_LINE_EDIT"


#######################################################################################
# EXCEPTION
#######################################################################################


class GuiSerializationError(ValueError):
    """
    Raised by miracl.system.gui.miracl_gui_serializer.MiraclGUISerializer when a
    miracl.system.datamodels.ResolvedMiraclObj is missing metadata that the GUI layer
    requires.
    """


#######################################################################################
# META
#######################################################################################


class GuiMeta(BaseModel):
    """
    Frozen snapshot of the registry _meta block, shaped for GUI consumption.
    """

    model_config = ConfigDict(frozen=True)

    title: Optional[str] = None
    module: str
    command: str

    help: Optional[str] = None
    extended_help: Optional[str] = None
    docs_url: Optional[str] = None

    experimental: bool = False
    deprecated: bool = False
    deprecation_message: Optional[str] = None

    version: Optional[str] = None
    requires_gpu: bool = False
    min_memory_gb: Optional[str] = None
    estimated_runtime: Optional[str] = None


#######################################################################################
# WIDGET PROPS
#######################################################################################


class GuiRangeProps(BaseModel):
    """
    Numeric range and step configuration for spinbox and slider widgets.
    """

    model_config = ConfigDict(frozen=True)

    min_val: Optional[float] = None
    max_val: Optional[float] = None
    increment_val: Optional[float] = None
    nr_decimals: Optional[int] = None


class GuiTextProps(BaseModel):
    """
    Input restriction configuration for line edit widgets.
    """

    model_config = ConfigDict(frozen=True)

    input_restrictions: Optional[str] = None


class GuiChoicesProps(BaseModel):
    """
    GUI-layer override labels and default for combo-box/choice widgets.
    """

    model_config = ConfigDict(frozen=True)

    vals: Optional[List[str]] = None
    default_val: Optional[str] = None


class GuiWidgetProps(BaseModel):
    """
    Container for all widget-specific configuration, flattened from the registry's
    GuiWidgetSpecifics object.
    """

    model_config = ConfigDict(frozen=True)

    range: Optional[GuiRangeProps] = None
    text: Optional[GuiTextProps] = None
    choices: Optional[GuiChoicesProps] = None


#######################################################################################
# TAB IDENTITY  —  label and description for one rendered tab
#######################################################################################


class GuiTabMeta(BaseModel):
    """
    Identity information for a single GUI tab, sourced from the
    miracl.system.enums.enums_base_modules.CliGroup enum.
    """

    model_config = ConfigDict(frozen=True)

    label: str
    description: str


#######################################################################################
# HIDDEN ARG
#######################################################################################


class GuiHiddenArg(BaseModel):
    """
    Minimal representation of an INTERNAL registry argument.
    """

    model_config = ConfigDict(frozen=True)

    dest: str  # UUID string
    name: str  # human-readable name for logging/debugging only
    default: Optional[Any] = None


#######################################################################################
# FIELD SPEC
#######################################################################################


class GuiFieldSpec(BaseModel):
    """
    Complete specification for one visible input widget in the GUI.
    """

    model_config = ConfigDict(frozen=True)

    dest: str
    name: str
    registry_class: str
    module: str
    module_group: str
    tab_label: str = UNGROUPED_TAB_KEY
    label: List[str]
    help_text: Optional[str] = None
    additional_labels: Optional[List[str]] = None
    widget_type: WidgetType

    value_type: Optional[str] = None

    default: Optional[Any] = None
    required: bool = False
    choices: Optional[List[Any]] = None
    order: Optional[float] = None
    props: GuiWidgetProps = GuiWidgetProps()
    extensions: Dict[str, Dict[str, Any]] = {}
    depends_on: Optional[List[str]] = None
    conflicts_with: Optional[List[str]] = None
    deprecated: bool = False

    @field_validator("value_type", mode="before")
    @classmethod
    def _validate_value_type(cls, v: Any) -> Optional[str]:
        """
        Pre-storage validator that normalises value_type to a JSONType value string
        regardless of the input form.
        """
        if v is None:
            return None

        if isinstance(v, JSONType):
            return v.value

        if isinstance(v, type):
            if issubclass(v, Path):
                return JSONType.PATH.value
            result = _PYTHON_TYPE_TO_JSON_VALUE.get(v)
            if result is None:
                raise ValueError(
                    f"No JSONType entry for type '{v.__name__}'. "
                    f"Add it to JSONType and the maps before using it as an ArgumentType."
                )
            return result

        if isinstance(v, str):
            try:
                return JSONType(v).value
            except ValueError:
                valid = [m.value for m in JSONType]
                raise ValueError(
                    f"'{v}' is not a valid JSONType value. Valid values: {valid}"
                )

        raise ValueError(
            f"value_type must be a type, JSONType member, or string — got {type(v)}"
        )

    @model_validator(mode="after")
    def _validate_spinbox_range(self) -> "GuiFieldSpec":
        _RANGE_REQUIRED = {
            WidgetType.SPINBOX,
            WidgetType.DOUBLE_SPINBOX,
            WidgetType.NULLABLE_DOUBLE_SPINBOX,
            WidgetType.SLIDER,
        }

        if self.widget_type in _RANGE_REQUIRED:
            if self.props.range is None or self.props.range.max_val is None:
                raise GuiSerializationError(
                    f"'{self.name}' is a {self.widget_type.value} but declares no max_val in props.range. Qt defaults all three numeric widget types to a maximum of 99/99.99, which will silently truncate values. Add a RangeFormConfig with an explicit max_val to the field's GuiWidgetSpecifics in the registry."
                )

        if self.widget_type == WidgetType.SPINBOX and self.get_value_type() is float:
            raise GuiSerializationError(
                f"'{self.name}' declares widget_type=SPINBOX but value_type=float. Use DOUBLE_SPINBOX for float fields."
            )
        if (
            self.widget_type == WidgetType.DOUBLE_SPINBOX
            and self.get_value_type() is int
        ):
            raise GuiSerializationError(
                f"'{self.name}' declares widget_type=DOUBLE_SPINBOX but value_type=int. Use SPINBOX for integer fields."
            )
        if (
            self.widget_type == WidgetType.NULLABLE_DOUBLE_SPINBOX
            and self.get_value_type() is int
        ):
            raise GuiSerializationError(
                f"'{self.name}' declares widget_type=NULLABLE_DOUBLE_SPINBOX but value_type=int. Use SPINBOX for integer fields."
            )

        return self

    def get_value_type(self) -> Optional[Type]:
        """
        Resolve value_type back to the real Python type object.
        """
        if self.value_type is None:
            return None
        return JSONType(self.value_type).python_type


#######################################################################################
# TAB
#######################################################################################


class GuiTab(BaseModel):
    """
    Represents one tab in the GUI, corresponding to one
    miracl.system.enums.enums_base_modules.CliGroup.
    """

    model_config = ConfigDict(frozen=True)

    tab_meta: GuiTabMeta
    args: List[GuiFieldSpec]


#######################################################################################
# SCHEMA
#######################################################################################


class GuiSchema(BaseModel):
    """
    Complete, validated output of
    miracl.system.gui.miracl_gui_serializer.MiraclGUISerializer.serialize.
    """

    model_config = ConfigDict(frozen=True)

    meta: GuiMeta
    tabs: Dict[str, GuiTab]
    hidden: List[GuiHiddenArg]
    by_module: Dict[str, List[str]]

    @model_validator(mode="after")
    def _validate_consistency(self) -> "GuiSchema":
        """
        Cross-field consistency validator, run automatically by Pydantic immediately
        after the model is constructed.
        """
        all_field_ids: set = {
            spec.dest for tab in self.tabs.values() for spec in tab.args
        }

        for tab in self.tabs.values():
            for spec in tab.args:
                if spec.tab_label not in self.tabs:
                    raise ValueError(
                        f"GuiFieldSpec '{spec.name}' has tab_label='{spec.tab_label}' "
                        f"which is not a key in GuiSchema.tabs."
                    )

        for module, ids in self.by_module.items():
            unknown = set(ids) - all_field_ids
            if unknown:
                raise ValueError(
                    f"by_module['{module}'] references unknown field dest IDs: {unknown}"
                )

        return self

    @property
    def fields(self) -> List[GuiFieldSpec]:
        """
        Flat ordered list of all visible GuiFieldSpec instances across all tabs.
        """
        return [spec for tab in self.tabs.values() for spec in tab.args]

    def fields_for_group(self, group: str) -> List[GuiFieldSpec]:
        """
        Return all visible GuiFieldSpec instances belonging to a specific tab.
        """
        tab = self.tabs.get(group)
        return list(tab.args) if tab else []

    def fields_for_module(self, module: str) -> List[GuiFieldSpec]:
        """
        Return all visible `GuiFieldSpec instances whose GuiFieldSpec.module matches
        module.
        """
        ids = set(self.by_module.get(module, []))
        return [f for f in self.fields if f.dest in ids]
