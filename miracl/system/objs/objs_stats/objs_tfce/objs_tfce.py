from miracl.api.enums import (
    CliGroup,
    ArgumentType,
)
from miracl.api.core import (
    MiraclObj,
)
from pathlib import Path
from miracl.system.datamodels.datamodel_miracl_objs import ArgumentSource


class TFCE:
    control_input_dir: MiraclObj = MiraclObj(
        name="tfce_control_input_dir",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="c",
        cli_l_flag="ctrl_input_dir",
        flow={
            "ace": {
                "cli_s_flag": "tfce_c",
                "cli_l_flag": "tfce_ctrl_input_dir",
                "cli_group": CliGroup.REQUIRED,
                "source": ArgumentSource.INTERNAL,
            },
            "mapl3": {
                "cli_s_flag": "tfce_c",
                "cli_l_flag": "tfce_ctrl_input_dir",
                "cli_group": CliGroup.REQUIRED,
                "source": ArgumentSource.INTERNAL,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_group=CliGroup.REQUIRED,
        cli_help="FIRST: path to base control directory.\nSECOND: example path to control subject voxelized tif file (voxelized_seg_*.nii.gz) (default: None)",
        cli_metavar=(
            "CONTROL BASE DIR, CONTROL VOXELIZED SEGMENTED TIFF EXAMPLE PATH",
        ),
        cli_nargs="+",
        cli_required=True,
        gui_label=["Ctrl input directory"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    treated_input_dir: MiraclObj = MiraclObj(
        name="tfce_treated_input_dir",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="t",
        cli_l_flag="treated_input_dir",
        flow={
            "ace": {
                "cli_s_flag": "tfce_t",
                "cli_l_flag": "tfce_treated_input_dir",
                "cli_group": CliGroup.REQUIRED,
                "source": ArgumentSource.INTERNAL,
            },
            "mapl3": {
                "cli_s_flag": "tfce_t",
                "cli_l_flag": "tfce_treated_input_dir",
                "cli_group": CliGroup.REQUIRED,
                "source": ArgumentSource.INTERNAL,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_group=CliGroup.REQUIRED,
        cli_help="FIRST: path to base treated directory.\nSECOND: example path to treated subject voxelized tif file (voxelized_seg_*.nii.gz) (default: None)",
        cli_metavar=(
            "TREATED BASE DIR, TREATED VOXELIZED SEGMENTED TIFF EXAMPLE PATH",
        ),
        cli_nargs="+",
        cli_required=True,
        gui_label=["Treated input directory"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    output_dir: MiraclObj = MiraclObj(
        name="tfce_output_dir",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="o",
        cli_l_flag="output_dir",
        flow={
            "ace": {
                "cli_s_flag": "tfce_o",
                "cli_l_flag": "tfce_output_dir",
                "cli_group": CliGroup.STATS_TFCE,
                "source": ArgumentSource.INTERNAL,
            },
            "mapl3": {
                "cli_s_flag": "tfce_o",
                "cli_l_flag": "tfce_output_dir",
                "cli_group": CliGroup.STATS_TFCE,
                "source": ArgumentSource.INTERNAL,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="output directory (default: %(default)s)",
        obj_default=Path.cwd(),
        gui_label=["Output directory"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    number_permutations: MiraclObj = MiraclObj(
        name="tfce_num_perm",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="n",
        cli_l_flag="num_perm",
        flow={
            "ace": {
                "cli_s_flag": "tfce_n",
                "cli_l_flag": "tfce_num_perm",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_n",
                "cli_l_flag": "tfce_num_perm",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="number of permutations (default: %(default)s)",
        obj_default=100,
        gui_label=["# permutations"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    atlas_directory: MiraclObj = MiraclObj(
        name="tfce_atlas_dir",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="atl",
        cli_l_flag="atlas_dir",
        flow={
            "ace": {
                "cli_s_flag": "tfce_atl",
                "cli_l_flag": "tfce_atlas_dir",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_atl",
                "cli_l_flag": "tfce_atlas_dir",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to atlas directory (default (cwd): %(default)s)",
        obj_default="/code/atlases/ara",
        gui_label=["Atlas dir"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    voxel_size: MiraclObj = MiraclObj(
        name="tfce_voxel_size",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="v",
        cli_l_flag="voxel_size",
        flow={
            "ace": {
                "cli_s_flag": "tfce_v",
                "cli_l_flag": "tfce_voxel_size",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_v",
                "cli_l_flag": "tfce_voxel_size",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="voxel size/res in um for warping (default: %(default)s)",
        obj_default=25,
        cli_choices=[10, 25, 50],
        gui_label=["Voxel size warping (um)"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    smoothing_fwhm: MiraclObj = MiraclObj(
        name="tfce_smoothing_fwhm",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="sm",
        cli_l_flag="smoothing_fwhm",
        flow={
            "ace": {
                "cli_s_flag": "tfce_sm",
                "cli_l_flag": "tfce_smoothing_fwhm",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_sm",
                "cli_l_flag": "tfce_smoothing_fwhm",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="fwhm of Gaussian kernel in pixel (default: %(default)s)",
        obj_default=3,
        gui_label=["Smoothing fwhm"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    start: MiraclObj = MiraclObj(
        name="tfce_start",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="st",
        cli_l_flag="start",
        flow={
            "ace": {
                "cli_s_flag": "tfce_st",
                "cli_l_flag": "tfce_start",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_st",
                "cli_l_flag": "tfce_start",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold start (default: %(default)s)",
        obj_default=0.01,
        gui_label=["Threshold start"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    step: MiraclObj = MiraclObj(
        name="tfce_step",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="sp",
        cli_l_flag="step",
        flow={
            "ace": {
                "cli_s_flag": "tfce_sp",
                "cli_l_flag": "tfce_step",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_sp",
                "cli_l_flag": "tfce_step",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold step (default: %(default)s)",
        obj_default=5,
        gui_label=["Threshold step"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    h_power: MiraclObj = MiraclObj(
        name="tfce_h_power",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="hp",
        cli_l_flag="h_power",
        flow={
            "ace": {
                "cli_s_flag": "tfce_hp",
                "cli_l_flag": "tfce_h_power",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_hp",
                "cli_l_flag": "tfce_h_power",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="TFCE H power (default: %(default)s)",
        obj_default=0.5,
        gui_label=["TFCE H power"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    e_power: MiraclObj = MiraclObj(
        name="tfce_e_power",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="ep",
        cli_l_flag="e_power",
        flow={
            "ace": {
                "cli_s_flag": "tfce_e",
                "cli_l_flag": "tfce_e_power",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_e",
                "cli_l_flag": "tfce_e_power",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="TFCE E power (default: %(default)s)",
        obj_default=2.0,
        gui_label=["TFCE E power"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    cpu_load: MiraclObj = MiraclObj(
        name="tfce_cpu_load",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="cpu",
        cli_l_flag="cpu_load",
        flow={
            "ace": {
                "cli_s_flag": "tfce_cpu",
                "cli_l_flag": "tfce_cpu_load",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_cpu",
                "cli_l_flag": "tfce_cpu_load",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="CPU load (default: %(default)s)",
        obj_default=0.9,
        gui_label=["CPU load"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    step_down_p: MiraclObj = MiraclObj(
        name="tfce_step_down_p",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="p",
        cli_l_flag="step_down_p",
        flow={
            "ace": {
                "cli_s_flag": "tfce_p",
                "cli_l_flag": "tfce_step_down_p",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_p",
                "cli_l_flag": "tfce_step_down_p",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="step down p-value (default: %(default)s)",
        obj_default=0.3,
        gui_label=["Step down p-value"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    mask_thr: MiraclObj = MiraclObj(
        name="tfce_mask_thr",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="mt",
        cli_l_flag="step_mask_thr",
        flow={
            "ace": {
                "cli_s_flag": "tfce_mt",
                "cli_l_flag": "tfce_mask_thr",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_mt",
                "cli_l_flag": "tfce_mask_thr",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="percentile to be used for binarizing difference of the mean (default: %(default)s)",
        obj_default=95,
        gui_label=["Mask threshold"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    hemi: MiraclObj = MiraclObj(
        name="tfce_hemi",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="hm",
        cli_l_flag="hemi",
        flow={
            "ace": {
                "cli_s_flag": "tfce_hm",
                "cli_l_flag": "tfce_hemi",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_hm",
                "cli_l_flag": "tfce_hemi",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="hemisphere: 'combined' or 'split' (default: %(default)s)",
        obj_default="combined",
        cli_choices=["combined", "split"],
        gui_label=["Hemisphere"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )

    side: MiraclObj = MiraclObj(
        name="tfce_side",
        tags=[
            "mapl3",
            "seg",
            "mapl3_flow",
            "ace",
            "ace_flow",
            "tfce",
        ],
        cli_s_flag="s",
        cli_l_flag="side",
        flow={
            "ace": {
                "cli_s_flag": "tfce_s",
                "cli_l_flag": "tfce_side",
                "cli_group": CliGroup.STATS_TFCE,
            },
            "mapl3": {
                "cli_s_flag": "tfce_s",
                "cli_l_flag": "tfce_side",
                "cli_group": CliGroup.STATS_TFCE,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="side: 'lh' or 'rh' (default: %(default)s)",
        cli_choices=["lh", "rh"],
        gui_label=["Side"],
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
    )
