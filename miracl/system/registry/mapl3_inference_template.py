from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_inference import (
    Inference,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

mapl3_inference_dict = {
    "script": "python /code/miracl/seg/mapl3/mapl3_inference.py",
    "obj_class": Inference,
    "module_type": ModuleType.FLOW_MAPL3,
}
