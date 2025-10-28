from miracl.system.objs.objs_flow.objs_mapl3_workflow.objs_mapl3_workflow_connectors import (
    MAPL3_connectors,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType
from .registry import RegistryTemplate

mapl3_workflow_connectors_dict: RegistryTemplate = {
    "script": "/code/miracl/connectors.py",
    "obj_class": MAPL3_connectors,
    "module_type": ModuleType.FLOW_MAPL3,
}
