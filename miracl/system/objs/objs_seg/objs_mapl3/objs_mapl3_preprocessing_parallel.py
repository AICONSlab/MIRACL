from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)


class PreprocessingParallel:
    cpu_load = MiraclObj(
        id="9aa53f31-b9ca-4fef-8334-457c1c226192",
        name="cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mpp_c",
        cli_l_flag="mpp_cpu_load",
        flow={"mapl3": {"cli_s_flag": "mpp_c", "cli_l_flag": "mpp_cpu_load"}},
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
        id="d429fb1f-5797-4bb8-884c-030e3e27f61f",
        name="cl_percentage",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="clp",
        cli_l_flag="cl_percentage",
        flow={"mapl3": {"cli_s_flag": "mpp_clp", "cli_l_flag": "mpp_cl_percentage"}},
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
        id="cd82d8ed-afd1-4bcf-aab8-42ce8b5a1dd7",
        name="cl_lsm_footprint",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cl_lf",
        cli_l_flag="cl_lsm_footprint",
        flow={
            "mapl3": {"cli_s_flag": "mpp_cl_lf", "cli_l_flag": "mpp_cl_lsm_footprint"}
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
        id="c9e8b3ef-2718-4b1e-b66c-c5b31df7371c",
        name="cl_back_footprint",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cl_bf",
        cli_l_flag="cl_back_footprint",
        flow={
            "mapl3": {"cli_s_flag": "mpp_cl_bf", "cli_l_flag": "mpp_cl_back_footprint"}
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="structure for estimating backgroud default is VALUExVALUExVALUE (default: %(default)s)",
        cli_required=False,
        obj_default=16,
        gui_label=["Cl back footprint"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    cl_back_downsample = MiraclObj(
        id="33f6d75c-baa7-4aae-befc-f4e34b06bc0b",
        name="cl_back_downsample",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cl_bd",
        cli_l_flag="cl_back_downsample",
        flow={
            "mapl3": {"cli_s_flag": "mpp_cl_bd", "cli_l_flag": "mpp_cl_back_downsample"}
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="structure for estimating backgroud default is VALUExVALUExVALUE (default: %(default)s)",
        cli_required=False,
        obj_default=8,
        gui_label=["Cl back downsample"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    lsm_vs_back_weight = MiraclObj(
        id="88216e7b-7646-47c9-8a4d-4439402526c6",
        name="lsm_vs_back_weight",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="lvbw",
        cli_l_flag="lsm_vs_back_weight",
        flow={
            "mapl3": {"cli_s_flag": "mpp_lvbw", "cli_l_flag": "mpp_lsm_vs_back_weight"}
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
        id="22f5e652-ee4a-4380-9e69-4c09fdf686e8",
        name="deconv_bin_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="dbt",
        cli_l_flag="deconv_bin_thr",
        flow={"mapl3": {"cli_s_flag": "mpp_dbt", "cli_l_flag": "mpp_deconv_bin_thr"}},
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
        id="f1d42d1f-2d0a-4ba8-a4e8-3edd433ddd59",
        name="deconv_sigma",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ds",
        cli_l_flag="deconv_sigma",
        flow={"mapl3": {"cli_s_flag": "mpp_ds", "cli_l_flag": "mpp_deconv_sigma"}},
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
        id="cee55be6-0200-479f-951a-7ca8154ca1eb",
        name="save_intermediate_results",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="sir",
        cli_l_flag="save_intermediate_results",
        flow={
            "mapl3": {
                "cli_s_flag": "mpp_sir",
                "cli_l_flag": "mpp_save_intermediate_results",
            }
        },
        cli_action=ArgumentAction.STORE_TRUE,
        cli_help="whether to save intermediate results for debugging - set flag to save results (default: %(default)s)",
        obj_default=False,
        gui_label=["Save intermediate results"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )
