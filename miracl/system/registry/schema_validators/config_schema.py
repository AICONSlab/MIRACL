"""
Schema definitions for validating module entries loaded from YAML for registry.
"""

from pydantic import BaseModel, Field, RootModel, field_validator
from typing import Dict
from miracl.api.enums import ModuleType


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


class ModuleConfig(RootModel[Dict[str, ModuleEntry]]):
    """
    Pydantic root model representing the full modules dictionary
    loaded from YAML.

    Each key is a module name, and each value is a ModuleEntry object.
    """

    pass
