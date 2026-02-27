from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)
from pathlib import Path
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class WarpClarAllen:
    reg_dir = MiraclObj(
        name="rwca_regdir",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="r",
        cli_l_flag="regdir",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_r",
                "cli_l_flag": "mrwca_regdir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Input clarity registration dir (default: None)",
        obj_default=None,
        cli_required=True,
        gui_label=["Input clarity registration dir"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    nii_folder = MiraclObj(
        name="rwca_nii_folder",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="inimg",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_i",
                "cli_l_flag": "mrwca_inimg",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Input downsampled CLARITY nii to warp (default: None)",
        obj_default=None,
        cli_required=True,
        gui_label=["Nii input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    ort2std_file = MiraclObj(
        name="rwca_ort2std_file",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="o",
        cli_l_flag="ort2std_file",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_o",
                "cli_l_flag": "mrwca_ort2std_file",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="File with orientation to standard code (default: None)",
        gui_label=["Orientation code file"],
        gui_group={"ace_flow": "main"},
        gui_order=[9],
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    seg_channel = MiraclObj(
        name="rwca_seg_channel",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="s",
        cli_l_flag="seg_channel",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_s",
                "cli_l_flag": "mrwca_seg_channel",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        obj_default=None,
        cli_help="Segmentation channel (ex. 'green') - required if voxelization is input (default: None)",
        gui_label=["Seg channel"],
        gui_group={"ace_flow": "main"},
        gui_order=[9],
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    vox_res = MiraclObj(
        name="rwca_vox_res",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="v",
        cli_l_flag="vox_res",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_v",
                "cli_l_flag": "mrwca_vox_res",
                "cli_group": CliGroup.MAPL3_WARP_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Voxel resolution (10 or 25; default: %(default)s)",
        obj_default=25,
        gui_label=["Seg channel"],
        gui_group={"ace_flow": "main"},
        gui_order=[9],
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    allen_lbls = MiraclObj(
        name="rwca_allen_lbls",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="l",
        cli_l_flag="allen_lbls",
        flow={
            "mapl3": {
                "cli_s_flag": "mrwca_l",
                "cli_l_flag": "mrwca_allen_lbls",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input Allen labels to warp (default: average_template_{vox}um.nii.gz)",
        obj_default="None",
        gui_label=["Allen labels"],
        gui_group={"ace_flow": "main"},
        gui_order=[9],
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )
