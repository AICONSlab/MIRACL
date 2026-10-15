from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    FlowOverride,
    LineEditConfig,
    GuiWidgetSpecifics,
    RangeFormConfig,
    GuiChoiceOverrideConfig,
    ArgumentType,
    ArgumentSource,
    WidgetType,
    InputRestrictionType,
)


# NOTE: Arg categories are adapted from Ahmadreza's original script
# Personally I would categorize these differently but it's more
# important here to keep this matching to the original script.


class PassingVsTerminating:
    _PVT_GROUP = CliGroup.MAPL3_PASSING_VS_TERMINATING

    # Required
    input: MiraclObj = MiraclObj(
        name="pvt_seg",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="seg",
            l_flag="seg",
            obj_type=ArgumentType.STRING,
            help="Voxelized segmentation NIfTI (Allen CCF space)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Voxelized segmentation NIfTI"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_seg",
                    l_flag="pvt_seg",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    atlas_annotation: MiraclObj = MiraclObj(
        name="pvt_ann",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ann",
            l_flag="ann",
            obj_type=ArgumentType.STRING,
            help="Atlas annotation NIfTI (e.g. annotation_hemi_split_25um.nii.gz)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Atlas annotation NIfTI"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_ann",
                    l_flag="pvt_ann",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    graph: MiraclObj = MiraclObj(
        name="pvt_graph",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="g",
            l_flag="graph",
            obj_type=ArgumentType.STRING,
            help="Allen structure graph CSV",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Allen structure graph CSV"],
                widget_type=WidgetType.PATH_INPUT,
                order=3.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_g",
                    l_flag="pvt_graph",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    injection_site: MiraclObj = MiraclObj(
        name="pvt_inj",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="inj",
            l_flag="inj",
            obj_type=ArgumentType.STRING,
            help="Injection site name or acronym (default: %(default)s)",
            required=False,
            default="RORB",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Injection site name or acronym"],
                widget_type=WidgetType.LINE_EDIT,
                order=4.0,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.STRCON)
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_inj",
                    l_flag="pvt_inj",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="pvt_out",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out",
            obj_type=ArgumentType.STRING,
            help="Output directory (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory"],
                widget_type=WidgetType.PATH_INPUT,
                order=5.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_o",
                    l_flag="pvt_out",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Optional data
    raw_nifti: MiraclObj = MiraclObj(
        name="pvt_raw",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="r",
            l_flag="raw",
            obj_type=ArgumentType.STRING,
            help=(
                "Raw fluorescence NIfTI (optional, used for background in viz) (default: None)"
            ),
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Raw fluorescence NIfTI (optional)"],
                widget_type=WidgetType.PATH_INPUT,
                order=6.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_r",
                    l_flag="pvt_raw",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    exclude: MiraclObj = MiraclObj(
        name="pvt_exclude",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="e",
            l_flag="exclude",
            obj_type=ArgumentType.STRING,
            help=(
                "Comma-separated region names/IDs to exclude (e.g. 'olfactory bulb') (default: %(default)s)"
            ),
            required=False,
            default="",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Region names/IDs to exclude (comma-separated)"],
                widget_type=WidgetType.LINE_EDIT,
                order=7.0,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.STRCON)
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_e",
                    l_flag="pvt_exclude",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Algorithm parameters
    axis: MiraclObj = MiraclObj(
        name="pvt_axis",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ax",
            l_flag="axis",
            obj_type=ArgumentType.INTEGER,
            help="MIP projection axis (0=Z, 1=Y, 2=X) (default: %(default)s)",
            required=False,
            default=1,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["MIP projection axis (0=Z, 1=Y, 2=X)"],
                widget_type=WidgetType.SPINBOX,
                order=8.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_ax",
                    l_flag="pvt_axis",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    sigma: MiraclObj = MiraclObj(
        name="pvt_sigma",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sg",
            l_flag="sigma",
            obj_type=ArgumentType.FLOAT,
            help="Gaussian sigma for structure tensor (default: %(default)s)",
            required=False,
            default=1.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Gaussian sigma for structure tensor"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=9.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=10.00,
                        increment_val=0.10,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_sg",
                    l_flag="pvt_sigma",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    min_sig: MiraclObj = MiraclObj(
        name="pvt_min_sig",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ms",
            l_flag="min_sig",
            obj_type=ArgumentType.FLOAT,
            help="Minimum signal threshold for voxel inclusion (default: %(default)s)",
            required=False,
            default=0.1,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Minimum signal threshold for voxel inclusion"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=10.0,
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
                    s_flag="pvt_ms",
                    l_flag="pvt_min_sig",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    min_vox: MiraclObj = MiraclObj(
        name="pvt_min_vox",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="mv",
            l_flag="min_vox",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Minimum signal voxels required to score a 3D region "
                "(default: %(default)s)"
            ),
            required=False,
            default=20,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Min signal voxels to score a 3D region"],
                widget_type=WidgetType.SPINBOX,
                order=11.0,
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
                    s_flag="pvt_mv",
                    l_flag="pvt_min_vox",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    min_pix: MiraclObj = MiraclObj(
        name="pvt_min_pix",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="mp",
            l_flag="min_pix",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Minimum signal pixels required to score a 2D (MIP) region "
                "(default: %(default)s)"
            ),
            required=False,
            default=10,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Min signal pixels to score a 2D (MIP) region"],
                widget_type=WidgetType.SPINBOX,
                order=12.0,
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
                    s_flag="pvt_mp",
                    l_flag="pvt_min_pix",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Score blending weights
    weight_fa: MiraclObj = MiraclObj(
        name="pvt_w_fa",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="wf",
            l_flag="w_fa",
            obj_type=ArgumentType.FLOAT,
            help="Weight for FA signal (default: %(default)s)",
            required=False,
            default=0.4,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Weight for FA signal"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=13.0,
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
                    s_flag="pvt_wf",
                    l_flag="pvt_w_fa",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    weight_dv: MiraclObj = MiraclObj(
        name="pvt_w_dv",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="wd",
            l_flag="w_dv",
            obj_type=ArgumentType.FLOAT,
            help="Weight for depth-variance signal (default: %(default)s)",
            required=False,
            default=0.3,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Weight for depth-variance signal"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=14.0,
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
                    s_flag="pvt_wd",
                    l_flag="pvt_w_dv",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    weight_di: MiraclObj = MiraclObj(
        name="pvt_w_di",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="wi",
            l_flag="w_di",
            obj_type=ArgumentType.FLOAT,
            help="Weight for injection-site distance signal (default: %(default)s)",
            required=False,
            default=0.3,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Weight for injection-site distance signal"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=15.0,
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
                    s_flag="pvt_wi",
                    l_flag="pvt_w_di",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Outputs
    save_nii: MiraclObj = MiraclObj(
        name="pvt_save_nii",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sn",
            l_flag="save_nii",
            obj_type=ArgumentType.BOOLEAN,
            help=(
                "also save termination score as a NIfTI volume (default: %(default)s)"
            ),
            required=False,
            default=True,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Save termination score volume as NIfTI"],
                widget_type=WidgetType.COMBO_BOX,
                order=16.0,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["Yes", "No"],
                        default_val="Yes",
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_sn",
                    l_flag="pvt_save_nii",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    save_intermediates: MiraclObj = MiraclObj(
        name="pvt_save_intermediates",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="si",
            l_flag="save_intermediates",
            obj_type=ArgumentType.BOOLEAN,
            help=(
                "save tractography input NIfTI files: FA.nii.gz, fiber_directions.nii.gz (4D Z×Y×X×3), injection_mask.nii.gz, signal_mask.nii.gz. All in the same Allen CCF space as --seg (default: %(default)s)"
            ),
            required=False,
            default=True,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Save tractography input NIfTI volumes"],
                widget_type=WidgetType.COMBO_BOX,
                order=17.0,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["Yes", "No"],
                        default_val="Yes",
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="pvt_si",
                    l_flag="pvt_save_intermediates",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    injection_dilation: MiraclObj = MiraclObj(
        name="pvt_inj_dilation",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="id",
            l_flag="inj_dilation",
            obj_type=ArgumentType.INTEGER,
            help=(
                "morphological dilation radius (voxels) applied to the injection mask after atlas∩signal intersection. 0 = no dilation (pure intersection). Default 2 voxels ≈ 50um at 25um resolution (default: %(default)s)"
            ),
            required=False,
            default=2,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Injection mask dilation radius (voxels)"],
                widget_type=WidgetType.SPINBOX,
                order=18.0,
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
                    s_flag="pvt_id",
                    l_flag="pvt_inj_dilation",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    sig_dilation: MiraclObj = MiraclObj(
        name="pvt_sig_dilation",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sd",
            l_flag="sig_dilation",
            obj_type=ArgumentType.INTEGER,
            help=(
                "morphological dilation radius (voxels) applied to the signal mask before saving. Fills gaps in the binary segmentation between cortex and white-matter tracts (e.g. corpus callosum), enabling tractography to bridge unsegmented white matter. 0 = no dilation. Recommended 10 voxels ≈ 250um at 25um resolution (default: %(default)s)"
            ),
            required=False,
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Signal mask dilation radius (voxels)"],
                widget_type=WidgetType.SPINBOX,
                order=19.0,
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
                    s_flag="pvt_sd",
                    l_flag="pvt_sig_dilation",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    hemi_clip: MiraclObj = MiraclObj(
        name="pvt_hemi_clip",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="hc",
            l_flag="hemi_clip",
            obj_type=ArgumentType.BOOLEAN,
            help=(
                "restrict injection mask to the ipsilateral (right) hemisphere (X < 228 in Allen CCF hemi-split 25um). Prevents contralateral axon terminals from being included as seeds after dilation. Streamlines can still travel to the left hemisphere via CC. (default: %(default)s)"
            ),
            required=False,
            default=False,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Restrict injection mask to ipsilateral hemisphere"],
                widget_type=WidgetType.COMBO_BOX,
                order=20.0,
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
                    s_flag="pvt_hc",
                    l_flag="pvt_hemi_clip",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    top_n: MiraclObj = MiraclObj(
        name="pvt_top_n",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "pvt", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="tn",
            l_flag="top_n",
            obj_type=ArgumentType.INTEGER,
            help="number of top/bottom regions shown in bar chart (default: %(default)s)",
            required=False,
            default=20,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Number of top/bottom regions in bar chart"],
                widget_type=WidgetType.SPINBOX,
                order=21.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=200,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="pvt_tn",
                    l_flag="pvt_top_n",
                    group=_PVT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
