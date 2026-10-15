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
#
class Tractography:
    _TRACT_GROUP = CliGroup.MAPL3_TRACTOGRAPHY

    # Required
    # Since they are required and provided by pvt in the MAPL3 workflow,
    # they are set to `ArgumentSource.INTERNAL` for the workflow as well.
    fa: MiraclObj = MiraclObj(
        name="t_fa",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="fa",  # <<UNCERTAIN>> mnemonic guess, not checked for clashes
            l_flag="fa",
            obj_type=ArgumentType.STRING,
            help="FA.nii.gz (from aa_passing_vs_terminating.py --save_intermediates)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["FA.nii.gz"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_fa",
                    l_flag="t_fa",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    dirs: MiraclObj = MiraclObj(
        name="t_dirs",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="dr",  # <<UNCERTAIN>>
            l_flag="dirs",
            obj_type=ArgumentType.STRING,
            help="fiber_directions.nii.gz (4D Z×Y×X×3)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Fiber directions NIfTI (4D Z×Y×X×3)"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_dr",
                    l_flag="t_dirs",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    seeds: MiraclObj = MiraclObj(
        name="t_seeds",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sd",  # <<UNCERTAIN>>
            l_flag="seeds",
            obj_type=ArgumentType.STRING,
            help="injection_mask.nii.gz (seed mask)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Injection mask NIfTI (seed mask)"],
                widget_type=WidgetType.PATH_INPUT,
                order=3.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_sd",
                    l_flag="t_seeds",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    mask: MiraclObj = MiraclObj(
        name="t_mask",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="mk",  # <<UNCERTAIN>>
            l_flag="mask",
            obj_type=ArgumentType.STRING,
            help="signal_mask.nii.gz (tracking boundary)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Signal mask NIfTI (tracking boundary)"],
                widget_type=WidgetType.PATH_INPUT,
                order=4.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_mk",
                    l_flag="t_mask",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="t_out",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="o",  # <<UNCERTAIN>>
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="Output directory (default: %(default)s)",
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
                    s_flag="t_o",
                    l_flag="t_out_dir",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Optional input
    scores: MiraclObj = MiraclObj(
        name="t_scores",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sc",  # <<UNCERTAIN>>
            l_flag="scores",
            obj_type=ArgumentType.STRING,
            help=(
                "termination_score_vol.nii.gz (optional; enables passing/terminating split) (default: %(default)s)"
            ),
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Termination score volume NIfTI (optional)"],
                widget_type=WidgetType.PATH_INPUT,
                order=6.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_sc",
                    l_flag="t_scores",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Atlas annotation for region-based features (CSV output and endpoint filtering)
    ann: MiraclObj = MiraclObj(
        name="t_ann",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ann",  # <<UNCERTAIN>>
            l_flag="ann",
            obj_type=ArgumentType.STRING,
            help=(
                "Atlas annotation NIfTI (uint32, Allen CCF space). Same file used by aa_passing_vs_terminating.py --ann. Required for --csv and --exclude_* options. (default: %(default)s)"
            ),
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Atlas annotation NIfTI"],
                widget_type=WidgetType.PATH_INPUT,
                order=7.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_ann",
                    l_flag="t_ann",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    graph: MiraclObj = MiraclObj(
        name="t_graph",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="gr",  # <<UNCERTAIN>>
            l_flag="graph",
            obj_type=ArgumentType.STRING,
            help=(
                "Allen structure graph CSV with columns id, name, acronym. Required when --ann is provided. (default: %(default)s)"
            ),
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Allen structure graph CSV"],
                widget_type=WidgetType.PATH_INPUT,
                order=8.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="t_gr",
                    l_flag="t_graph",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Tracking parameters
    step_vox: MiraclObj = MiraclObj(
        name="t_step_vox",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sv",  # <<UNCERTAIN>>
            l_flag="step_vox",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Step size in voxels (0.5 = 12.5um at 25um resolution). Direction field has 1-voxel resolution so steps < 0.5 add smoothness with no direction fidelity gain. Larger steps (1.0) are faster but miss tight turns. 0.5 recommended (default: %(default)s)"
            ),
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Step size (voxels)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=9.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.10,
                        max_val=100.00,
                        increment_val=0.10,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_sv",
                    l_flag="t_step_vox",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    max_angle: MiraclObj = MiraclObj(
        name="t_max_angle",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ma",  # <<UNCERTAIN>>
            l_flag="max_angle",
            obj_type=ArgumentType.FLOAT,
            help="Maximum turning angle per step in degrees (default: %(default)s)",
            required=False,
            default=30.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Max turning angle per step (degrees)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=10.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.0,
                        max_val=180.0,
                        increment_val=1.0,
                        nr_decimals=1,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_ma",
                    l_flag="t_max_angle",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    min_length_mm: MiraclObj = MiraclObj(
        name="t_min_length_mm",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="mnl",  # <<UNCERTAIN>>
            l_flag="min_length_mm",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Minimum streamline length in mm (shorter streamlines discarded) "
                "(default: %(default)s)"
            ),
            required=False,
            default=2.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Min streamline length (mm)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=11.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=100.00,
                        increment_val=0.10,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_mnl",
                    l_flag="t_min_length_mm",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    max_length_mm: MiraclObj = MiraclObj(
        name="t_max_length_mm",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="mxl",  # <<UNCERTAIN>>
            l_flag="max_length_mm",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Maximum streamline length in mm (longer streamlines truncated at stop) "
                "(default: %(default)s)"
            ),
            required=False,
            default=30.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Max streamline length (mm)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=12.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.10,
                        max_val=300.00,
                        increment_val=1.00,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_mxl",
                    l_flag="t_max_length_mm",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    fa_thr: MiraclObj = MiraclObj(
        name="t_fa_thr",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ft",  # <<UNCERTAIN>>
            l_flag="fa_thr",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Stop tracking if FA drops below this value (0 = disable FA check) (default: %(default)s)"
            ),
            required=False,
            default=0.05,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["FA stop threshold (0 = disabled)"],
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
                    s_flag="t_ft",
                    l_flag="t_fa_thr",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    gap_tol: MiraclObj = MiraclObj(
        name="t_gap_tol",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="gt",  # <<UNCERTAIN>>
            l_flag="gap_tol",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Consecutive out-of-mask steps tolerated before stopping. Bridges small holes in the binary segmentation caused by noise or missed detections. 5 voxels = 125um at 25um resolution (default: %(default)s)"
            ),
            required=False,
            default=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Gap tolerance (voxels)"],
                widget_type=WidgetType.SPINBOX,
                order=14.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=1000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_gt",
                    l_flag="t_gap_tol",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    smooth_dirs: MiraclObj = MiraclObj(
        name="t_smooth_dirs",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="sm",  # <<UNCERTAIN>>
            l_flag="smooth_dirs",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Gaussian smoothing sigma (voxels) applied to the fiber direction field after loading, before tracking. 0 = disabled. Recommended 1.0-1.5 to improve corpus callosum and other interhemispheric tract tracking where cortex->CC direction transitions cause abrupt ~90 deg turns that exceed --max_angle (default: %(default)s)"
            ),
            required=False,
            default=0.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Direction field smoothing sigma (voxels)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=15.0,
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
                    s_flag="t_sm",
                    l_flag="t_smooth_dirs",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Seeding
    max_seeds: MiraclObj = MiraclObj(
        name="t_max_seeds",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="ms",  # <<UNCERTAIN>>
            l_flag="max_seeds",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Maximum seeds; random subset drawn if injection mask is larger (default: %(default)s)"
            ),
            required=False,
            default=20000,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Maximum seeds"],
                widget_type=WidgetType.SPINBOX,
                order=16.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_ms",
                    l_flag="t_max_seeds",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    rng_seed: MiraclObj = MiraclObj(
        name="t_rng_seed",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="rs",  # <<UNCERTAIN>>
            l_flag="rng_seed",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Random seed for reproducible seed subsampling (default: %(default)s)"
            ),
            required=False,
            default=42,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Random seed"],
                widget_type=WidgetType.SPINBOX,
                order=17.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=100000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_rs",
                    l_flag="t_rng_seed",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Classification
    score_thr: MiraclObj = MiraclObj(
        name="t_score_thr",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="st",  # <<UNCERTAIN>>
            l_flag="score_thr",
            obj_type=ArgumentType.FLOAT,
            help=(
                "Termination score threshold for splitting streamlines (requires --scores) (default: %(default)s)"
            ),
            required=False,
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Termination score threshold for split"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                order=18.0,
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
                    s_flag="t_st",
                    l_flag="t_score_thr",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # CSV output
    csv: MiraclObj = MiraclObj(
        name="t_csv",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="csv",  # <<UNCERTAIN>>
            l_flag="csv",
            obj_type=ArgumentType.BOOLEAN,
            help=(
                "Export per-streamline metadata CSV (origin region, end region, length, traversed regions, classification, endpoint score). Requires --ann and --graph (default: %(default)s)"
            ),
            required=False,
            default=True,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Export per-streamline metadata CSV"],
                widget_type=WidgetType.COMBO_BOX,
                order=19.0,
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
                    s_flag="t_csv",
                    l_flag="t_csv",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    csv_sample_n: MiraclObj = MiraclObj(
        name="t_csv_sample_n",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="csn",  # <<UNCERTAIN>>
            l_flag="csv_sample_n",
            obj_type=ArgumentType.INTEGER,
            help=(
                "Sample every N points along each streamline for region-traversal lookup in the CSV. 5 is every 62.5um at 25um resolution (default: %(default)s)"
            ),
            required=False,
            default=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["CSV region-traversal sample interval (N points)"],
                widget_type=WidgetType.SPINBOX,
                order=20.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=1000,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_csn",
                    l_flag="t_csv_sample_n",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Endpoint filtering
    exclude_outside_brain: MiraclObj = MiraclObj(
        name="t_exclude_outside_brain",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="eob",  # <<UNCERTAIN>>
            l_flag="exclude_outside_brain",
            obj_type=ArgumentType.BOOLEAN,
            help=(
                "Remove streamlines where either endpoint is outside the brain (atlas_id == 0). Requires --ann (default: %(default)s)"
            ),
            required=False,
            default=True,
            choices=[True, False],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Exclude streamlines ending outside brain"],
                widget_type=WidgetType.COMBO_BOX,
                order=21.0,
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
                    s_flag="t_eob",
                    l_flag="t_exclude_outside_brain",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    exclude_end_regions: MiraclObj = MiraclObj(
        name="t_exclude_end_regions",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="eer",  # <<UNCERTAIN>>
            l_flag="exclude_end_regions",
            obj_type=ArgumentType.STRING,
            help=(
                "Comma-separated region names, acronyms, or integer IDs. Streamlines where either endpoint falls in any of these regions are removed. Example: 'fiber tracts,VS,1009'. Requires --ann and --graph (default: %(default)s)"
            ),
            required=False,
            default="",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Region names/IDs to exclude at endpoints"],
                widget_type=WidgetType.LINE_EDIT,
                order=22.0,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.STRCON)
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_eer",
                    l_flag="t_exclude_end_regions",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    # Compute
    n_jobs: MiraclObj = MiraclObj(
        name="t_n_jobs",
        module="mapl3",
        module_group="tract",
        version_added="2.4.0",
        tags=["mapl3", "tract", "mapl3_flow", "tractography"],
        cli=CLISpec(
            s_flag="nj",  # <<UNCERTAIN>>
            l_flag="n_jobs",
            obj_type=ArgumentType.INTEGER,
            help="Parallel worker processes (0 = 70%% of CPU count) (default: %(default)s)",
            required=False,
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Parallel workers (0 = auto)"],
                widget_type=WidgetType.SPINBOX,
                order=23.0,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0,
                        max_val=256,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="t_nj",
                    l_flag="t_n_jobs",
                    group=_TRACT_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

