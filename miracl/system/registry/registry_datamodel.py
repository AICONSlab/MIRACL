from typing_extensions import TypedDict
from typing import Dict, Type, Callable
from miracl.system.datamodels.miraclobj_enums import ModuleType


class RegistryEntry(TypedDict):
    """
    Represents a single registered module with all its metadata.

    Attributes:
        script: Path or command to execute the module
        obj_class: Class containing MiraclObj definitions
        module_type: Context in which the module runs (MODULE, FLOW_MAPL3, etc.)
        runner: Function that executes the script
        flag_map: Workflow-to-module flag mapping (empty for standalone modules)
        execute: Whether to actually execute the script or just prepare it
    """

    script: str
    obj_class: Type
    module_type: ModuleType
    runner: Callable[[str, Dict[str, object], Dict[str, str], bool], object]
    flag_map: Dict[str, str]
    execute: bool
