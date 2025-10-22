from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_voxelization import (
    Voxelization,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

mapl3_voxelization_dict = {
    "script": "python /code/miracl/seg/mapl3/mapl3_voxelization.py",
    "obj_class": Voxelization,
    "module_type": ModuleType.FLOW_MAPL3,
}
