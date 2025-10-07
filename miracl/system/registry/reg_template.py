from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen,
)

# from miracl.system.registry.utilfns import build_flag_map_from_class
from miracl.system.datamodels.miraclobj_serializer import build_flag_map_from_class

reg_clar_allen_dict = {
    "script": "/code/miracl/registration.py",
    # "flag_map": build_flag_map_from_class(ClarAllen),
    "obj_class": ClarAllen,
}
