from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_generate_patch import (
    GeneratePatch,
)

from miracl.system.datamodels.miraclobj_serializer import build_flag_map_from_class

mapl3_generate_patch_dict = {
    "script": "/code/miracl/mapl3_generate_patch.py",
    # "flag_map": build_flag_map_from_class(GeneratePatch),
    "obj_class": GeneratePatch,
}
