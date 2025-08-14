from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.objs.objs_conv.objs_tiff_to_nii.objs_tiff_to_nii import (
    ConvTiffNiiObjs,
)
from miracl.system.registry.utilfns import build_flag_map_from_class


conv_tiff_nii_dict = {
    "script": "/code/miracl/conversion.py",
    "flag_map": build_flag_map_from_class(ConvTiffNiiObjs),
}
