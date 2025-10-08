from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.objs.objs_conv.objs_tiff_to_nii.objs_tiff_to_nii import (
    ConvTiffNiiObjs,
)
from miracl.system.datamodels.miraclobj_enums import ModuleType

conv_tiff_nii_dict = {
    "script": "/code/miracl/conversion.py",
    "obj_class": ConvTiffNiiObjs,
    "module_type": ModuleType.FLOW_MAPL3,
}
