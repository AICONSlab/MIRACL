from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.datamodels.miraclobj_enums import (
    ArgumentType,
    WidgetType,
    ArgumentAction,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class PreprocessingParallel:
    input: MiraclObj = MiraclObj(
        name="mpp_input",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_i",
                "cli_l_flag": "mpp_input",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input directory containing tif/tiff raw 3D image patches (default: None)",
        cli_required=True,
        gui_label=["TIFF input folder"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    out_dir: MiraclObj = MiraclObj(
        name="mpp_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_o",
                "cli_l_flag": "mpp_out_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path of output directory (default: None)",
        cli_required=True,
        gui_label=["Output directory for patches"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    cpu_load = MiraclObj(
        name="mpp_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mpp_c",
        cli_l_flag="mpp_cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_c",
                "cli_l_flag": "mpp_cpu_load",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="fraction of cpus to be used for parallelization. Value needs to be between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.7,
        gui_label=["CPU load"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    cl_percentage = MiraclObj(
        name="mpp_cl_percentage",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="clp",
        cli_l_flag="cl_percentage",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_clp",
                "cli_l_flag": "mpp_cl_percentage",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="percentage used in percentile filter between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.25,
        gui_label=["Cl percentage"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    cl_lsm_footprint = MiraclObj(
        name="mpp_cl_lsm_footprint",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cl_lf",
        cli_l_flag="cl_lsm_footprint",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_cl_lf",
                "cli_l_flag": "mpp_cl_lsm_footprint",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="structure for estimating lsm stripes 1x1xVALUE (default: %(default)s)",
        cli_required=False,
        obj_default=100,
        gui_label=["Cl lsm footprint"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    cl_back_footprint = MiraclObj(
        name="mpp_cl_back_footprint",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cl_bf",
        cli_l_flag="cl_back_footprint",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_cl_bf",
                "cli_l_flag": "mpp_cl_back_footprint",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="structure for estimating background: VALUExVALUExVALUE (default: %(default)s)",
        cli_required=False,
        obj_default=16,
        gui_label=["Cl back footprint"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    lsm_vs_back_weight = MiraclObj(
        name="mpp_lsm_vs_back_weight",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="lvbw",
        cli_l_flag="lsm_vs_back_weight",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_lvbw",
                "cli_l_flag": "mpp_lsm_vs_back_weight",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="lsm signal vs background weight (default: %(default)s)",
        cli_required=False,
        obj_default=2,
        gui_label=["Lsm signal vs background weight"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    deconv_bin_thr = MiraclObj(
        name="mpp_deconv_bin_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="dbt",
        cli_l_flag="deconv_bin_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_dbt",
                "cli_l_flag": "mpp_deconv_bin_thr",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="threshold uses to detect high intensity voxels for pseudo deconvolution between 0-100 (default: %(default)s)",
        cli_required=False,
        obj_default=95,
        gui_label=["Thr high intensity voxels pseudo deconv"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    deconv_sigma = MiraclObj(
        name="mpp_deconv_sigma",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ds",
        cli_l_flag="deconv_sigma",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_ds",
                "cli_l_flag": "mpp_deconv_sigma",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="sigma of Gaussian blurring filter in the pseudo deconvolution (default: %(default)s)",
        cli_required=False,
        obj_default=3,
        gui_label=["Sigma Gaussuian blurring filter in pseudo"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    save_intermediate_results = MiraclObj(
        name="mpp_save_intermediate_results_flag",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="sir",
        cli_l_flag="save_intermediate_results_flag",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_sirf",
                "cli_l_flag": "mpp_save_intermediate_results_flag",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="whether to save intermediate results for debugging (default: %(default)s)",
        obj_default=False,
        gui_label=["Save intermediate results"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mpp_metadata",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="metadata",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_m",
                "cli_l_flag": "mpp_metadata",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to metadata JSON file (default: None)",
        cli_required=False,
        gui_label=["Path to metadata JSON"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    tissue_percentage_threshold: MiraclObj = MiraclObj(
        name="mpp_tissue_percentage_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="p",
        cli_l_flag="tissue_percentage_threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_tpt",
                "cli_l_flag": "mpp_tissue_percentage_threshold",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold between 0-100 to filter empty patches (required if metadata is provided; default: None)",
        cli_required=False,
        gui_label=["Threshold to filter empty patches"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    intensity_threshold: MiraclObj = MiraclObj(
        name="mpp_intensity_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="t",
        cli_l_flag="intensity_threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_it",
                "cli_l_flag": "mpp_intensity_threshold",
                "cli_group": CliGroup.MAPL3_PREPROCESSING_PARALLEL,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold between 0-100 (percent of int16: around 65K) to filter the patches whos 95 percentile of intensity falls below this (default: None)",
        cli_required=False,
        gui_label=["Threshold between 0-100"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )
