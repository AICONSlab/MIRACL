from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen,
)

from miracl.system.datamodels.miraclobj_enums import ModuleType

reg_clar_allen_dict = {
    "script": "/code/miracl/reg/miracl_reg_clar-allen.sh",
    "obj_class": ClarAllen,
    "module_type": ModuleType.FLOW_MAPL3,
}
