from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen as reg_clar_allen,
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

reg_object_dict = {
    "reg_clar_allen_reg": reg_clar_allen,
}
