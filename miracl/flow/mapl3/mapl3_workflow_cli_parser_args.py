from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen as reg_clar_allen_reg,
)

reg_flow_groups_dict = {
    "registration": {
        "title": "registration arguments",
        "description": "arguments passed to registration fn",
        "args": [
            reg_clar_allen_reg.nii_folder,
            reg_clar_allen_reg.tiff_folder,
            reg_clar_allen_reg.output_path,
            reg_clar_allen_reg.orient_code,
            reg_clar_allen_reg.voxel_size,
            reg_clar_allen_reg.hemi,
            reg_clar_allen_reg.allen_label,
            reg_clar_allen_reg.allen_atlas,
            reg_clar_allen_reg.side,
            # reg_clar_allen_reg.no_mosaic_fig,
            reg_clar_allen_reg.olfactory_bulb,
            # reg_clar_allen_reg.skip_cor,
            # reg_clar_allen_reg.warp,
        ],
    }
}
