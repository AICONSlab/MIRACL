from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_preprocessing_parallel import (
    PreprocessingParallel,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

mapl3_preprocessing_parallel_dict = {
    "script": "python /code/miracl/seg/mapl3/mapl3_preprocessing_parallel.py",
    "obj_class": PreprocessingParallel,
    "module_type": ModuleType.FLOW_MAPL3,
}
