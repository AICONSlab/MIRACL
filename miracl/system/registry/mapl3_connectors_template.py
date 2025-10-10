from miracl.system.objs.objs_flow.objs_mapl3_workflow.objs_mapl3_workflow_connectors import (
    MAPL3_connectors,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

mapl3_workflow_connectors_dict = {
    "script": "/code/miracl/conversion.py",
    "obj_class": MAPL3_connectors,
    "module_type": ModuleType.FLOW_MAPL3,
}
