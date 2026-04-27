from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    FlowOverride,
    ArgumentSource,
    LineEditConfig,
    GuiWidgetSpecifics,
    RangeFormConfig,
    GuiChoiceOverrideConfig,
    ArgumentType,
    WidgetType,
    InputRestrictionType,
)


class PreprocessingParallel:
    _MPP_GROUP = CliGroup.MAPL3_PREPROCESSING_PARALLEL

    input: MiraclObj = MiraclObj(
        name="mpp_input",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input directory containing tif/tiff raw 3D image patches (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["TIFF input folder"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpp_i",
                    l_flag="mpp_input",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mpp_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="path of output directory (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory for patches"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpp_o",
                    l_flag="mpp_out_dir",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mpp_cpu_load",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="mpp_c",
            l_flag="mpp_cpu_load",
            obj_type=ArgumentType.FLOAT,
            help="fraction of cpus to be used for parallelization. Value needs to be between 0-1 (default: %(default)s)",
            required=False,
            default=0.7,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["CPU load"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=1.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_c",
                    l_flag="mpp_cpu_load",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cl_percentage: MiraclObj = MiraclObj(
        name="mpp_cl_percentage",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="clp",
            l_flag="cl_percentage",
            obj_type=ArgumentType.FLOAT,
            help="percentage used in percentile filter between 0-1 (default: %(default)s)",
            required=False,
            default=0.25,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Cl percentage"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=1.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_clp",
                    l_flag="mpp_cl_percentage",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cl_lsm_footprint: MiraclObj = MiraclObj(
        name="mpp_cl_lsm_footprint",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cl_lf",
            l_flag="cl_lsm_footprint",
            obj_type=ArgumentType.INTEGER,
            help="structure for estimating lsm stripes 1x1xVALUE (default: %(default)s)",
            required=False,
            default=100,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Cl lsm footprint"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_cl_lf",
                    l_flag="mpp_cl_lsm_footprint",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cl_back_footprint: MiraclObj = MiraclObj(
        name="mpp_cl_back_footprint",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cl_bf",
            l_flag="cl_back_footprint",
            obj_type=ArgumentType.INTEGER,
            help="structure for estimating background: VALUExVALUExVALUE (default: %(default)s)",
            required=False,
            default=16,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Cl back footprint"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_cl_bf",
                    l_flag="mpp_cl_back_footprint",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cl_back_downsample: MiraclObj = MiraclObj(
        name="mpp_cl_back_downsample",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cl_bd",
            l_flag="cl_back_downsample",
            obj_type=ArgumentType.INTEGER,
            help="downsample ratio applied for background stimation; patch size should be devidable by this value (default: %(default)s)",
            required=False,
            default=8,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Cl back downsample"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_cl_bd",
                    l_flag="mpp_cl_back_downsample",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    lsm_vs_back_weight: MiraclObj = MiraclObj(
        name="mpp_lsm_vs_back_weight",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="lvbw",
            l_flag="lsm_vs_back_weight",
            obj_type=ArgumentType.INTEGER,
            help="lsm signal vs background weight (default: %(default)s)",
            required=False,
            default=2,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Lsm signal vs background weight"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_lvbw",
                    l_flag="mpp_lsm_vs_back_weight",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    deconv_bin_thr: MiraclObj = MiraclObj(
        name="mpp_deconv_bin_thr",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="dbt",
            l_flag="deconv_bin_thr",
            obj_type=ArgumentType.INTEGER,
            help="threshold uses to detect high intensity voxels for pseudo deconvolution between 0-100 (default: %(default)s)",
            required=False,
            default=95,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Thr high intensity voxels pseudo deconv"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=100,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_dbt",
                    l_flag="mpp_deconv_bin_thr",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    deconv_sigma: MiraclObj = MiraclObj(
        name="mpp_deconv_sigma",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="ds",
            l_flag="deconv_sigma",
            obj_type=ArgumentType.INTEGER,
            help="sigma of Gaussian blurring filter in the pseudo deconvolution (default: %(default)s)",
            required=False,
            default=3,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Sigma Gaussuian blurring filter in pseudo"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_ds",
                    l_flag="mpp_deconv_sigma",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    save_intermediate_results: MiraclObj = MiraclObj(
        name="mpp_save_intermediate_results_flag",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="sir",
            l_flag="save_intermediate_results_flag",
            obj_type=ArgumentType.CUSTOM_BOOL,
            help="whether to save intermediate results for debugging (default: %(default)s)",
            required=False,
            choices=[True, False],
            default=False,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Save intermediate results"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["Yes", "No"],
                        default_val="No",
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_sirf",
                    l_flag="mpp_save_intermediate_results_flag",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mpp_metadata",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="metadata",
            obj_type=ArgumentType.STRING,
            help="path to metadata JSON file (default: %(default)s)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Path to metadata JSON"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpp_m",
                    l_flag="mpp_metadata",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    tissue_percentage_threshold: MiraclObj = MiraclObj(
        name="mpp_tissue_percentage_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="p",
            l_flag="tissue_percentage_threshold",
            obj_type=ArgumentType.FLOAT,
            help="threshold between 0-100 to filter empty patches (required if metadata is provided; default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Threshold to filter empty patches between 0-100"],
                widget_type=WidgetType.NULLABLE_DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=100.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_tpt",
                    l_flag="mpp_tissue_percentage_threshold",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    intensity_threshold: MiraclObj = MiraclObj(
        name="mpp_intensity_threshold",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="t",
            l_flag="intensity_threshold",
            obj_type=ArgumentType.FLOAT,
            help="threshold between 0-100 (percent of int16: around 65K) to filter the patches whos 95 percentile of intensity falls below this (default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Intensity threshold between 0-100"],
                widget_type=WidgetType.NULLABLE_DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=100.00,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpp_it",
                    l_flag="mpp_intensity_threshold",
                    group=_MPP_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
