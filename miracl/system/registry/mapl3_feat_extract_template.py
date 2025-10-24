from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_feat_extract import (
    FeatExtract,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

mapl3_feat_extract_dict = {
    "script": "python /code/miracl/seg/mapl3/mapl3_feat_extract.py",
    "obj_class": FeatExtract,
    "module_type": ModuleType.FLOW_MAPL3,
}
