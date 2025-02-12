from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen as reg_clar_allen,
)
from miracl.system.objs.objs_conv.objs_tiff_to_nii.objs_tiff_to_nii import (
    ConvTiffNiiObjs as conv_tiff_to_nii,
)

reg_groups_dict = {
    "registration": {
        "title": "registration arguments",
        "description": "arguments passed to registration fn",
        "args": [
            reg_clar_allen.nii_folder,
            reg_clar_allen.tiff_folder,
            reg_clar_allen.output_path,
            reg_clar_allen.orient_code,
            reg_clar_allen.voxel_size,
            reg_clar_allen.hemi,
            reg_clar_allen.allen_label,
            reg_clar_allen.allen_atlas,
            reg_clar_allen.side,
            reg_clar_allen.no_mosaic_fig,
            reg_clar_allen.olfactory_bulb,
            reg_clar_allen.skip_cor,
            reg_clar_allen.warp,
        ],
    }
}

conv_groups_dict = {
    "conversion": {
        "title": "conversion arguments",
        "description": "arguments passed to conversion fn",
        "args": [
            conv_tiff_to_nii.tiff_folder,
            conv_tiff_to_nii.output_folder,
            conv_tiff_to_nii.down,
            conv_tiff_to_nii.channum,
            conv_tiff_to_nii.chanprefix,
            conv_tiff_to_nii.channame,
            conv_tiff_to_nii.outnii,
            conv_tiff_to_nii.resx,
            conv_tiff_to_nii.resz,
            conv_tiff_to_nii.center,
            conv_tiff_to_nii.downzdim,
            conv_tiff_to_nii.prevdown,
            conv_tiff_to_nii.percentile_thr,
        ],
    }
}


reg_object_dict = {
    "reg_clar_allen_reg": reg_clar_allen,
}

conv_object_dict = {
    "conv_tiff_to_nii": conv_tiff_to_nii,
}
