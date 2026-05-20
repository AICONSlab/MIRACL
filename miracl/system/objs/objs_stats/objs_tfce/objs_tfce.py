from pathlib import Path

# Adjust these imports according to your exact project structure
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    FlowOverride,
    WidgetType,
    ArgumentType,
    ArgumentSource,
)


class TFCE:
    control_input_dir = MiraclObj(
        name="tfce_control_input_dir",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="c",
            l_flag="ctrl_input_dir",
            obj_type=ArgumentType.STRING,
            help="Path to the base control directory.",
            group=CliGroup.STATS_TFCE,
            required=True,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Ctrl input directory"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_c",
                    l_flag="tfce_ctrl_input_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_c",
                    l_flag="tfce_ctrl_input_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    control_file_pattern = MiraclObj(
        name="tfce_control_pattern",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="cp",
            l_flag="ctrl_pattern",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="Glob pattern to locate NIfTI files inside the control directory (default: %(default)s). Supports nested directories (e.g. '*/voxelized_seg_*.nii.gz').",
            default="*.nii.gz",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Ctrl file pattern"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_cp",
                    l_flag="tfce_ctrl_pattern",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_cp",
                    l_flag="tfce_ctrl_pattern",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    treated_input_dir = MiraclObj(
        name="tfce_treated_input_dir",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="t",
            l_flag="treated_input_dir",
            obj_type=ArgumentType.STRING,
            help="Path to the base treated directory.",
            group=CliGroup.STATS_TFCE,
            required=True,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Treated input directory"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_t",
                    l_flag="tfce_treated_input_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_t",
                    l_flag="tfce_treated_input_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    treated_file_pattern = MiraclObj(
        name="tfce_treated_pattern",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="tp",
            l_flag="treated_pattern",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="Glob pattern to locate NIfTI files inside the treated directory (default: %(default)s). Supports nested directories.",
            default="*.nii.gz",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Treated file pattern"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_tp",
                    l_flag="tfce_treated_pattern",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_tp",
                    l_flag="tfce_treated_pattern",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    output_dir = MiraclObj(
        name="tfce_output_dir",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="o",
            l_flag="output_dir",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="output directory (default: %(default)s)",
            default=Path.cwd(),
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_o",
                    l_flag="tfce_output_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="tfce_o",
                    l_flag="tfce_output_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    number_permutations = MiraclObj(
        name="tfce_num_perm",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="n",
            l_flag="num_perm",
            obj_type=ArgumentType.INTEGER,
            group=CliGroup.STATS_TFCE,
            help="number of permutations (default: %(default)s)",
            default=100,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["# permutations"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_n",
                    l_flag="tfce_num_perm",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_n",
                    l_flag="tfce_num_perm",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    atlas_directory = MiraclObj(
        name="tfce_atlas_dir",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="atl",
            l_flag="atlas_dir",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="path to atlas directory (default (cwd): %(default)s)",
            default="/code/atlases/ara",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Atlas dir"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_atl",
                    l_flag="tfce_atlas_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_atl",
                    l_flag="tfce_atlas_dir",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    voxel_size = MiraclObj(
        name="tfce_voxel_size",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="v",
            l_flag="voxel_size",
            obj_type=ArgumentType.INTEGER,
            group=CliGroup.STATS_TFCE,
            help="voxel size/res in um for warping (default: %(default)s)",
            default=25,
            choices=[10, 25, 50],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Voxel size warping (um)"],
                widget_type=WidgetType.DROPDOWN,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_v",
                    l_flag="tfce_voxel_size",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_v",
                    l_flag="tfce_voxel_size",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    smoothing_fwhm = MiraclObj(
        name="tfce_smoothing_fwhm",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="sm",
            l_flag="smoothing_fwhm",
            obj_type=ArgumentType.INTEGER,
            group=CliGroup.STATS_TFCE,
            help="fwhm of Gaussian kernel in pixel (default: %(default)s)",
            default=3,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Smoothing fwhm"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_sm",
                    l_flag="tfce_smoothing_fwhm",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_sm",
                    l_flag="tfce_smoothing_fwhm",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    start = MiraclObj(
        name="tfce_start",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="st",
            l_flag="start",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="threshold start (default: %(default)s)",
            default=0.01,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Threshold start"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_st",
                    l_flag="tfce_start",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_st",
                    l_flag="tfce_start",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    step = MiraclObj(
        name="tfce_step",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="sp",
            l_flag="step",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="threshold step (default: %(default)s)",
            default=5.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Threshold step"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_sp",
                    l_flag="tfce_step",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_sp",
                    l_flag="tfce_step",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    h_power = MiraclObj(
        name="tfce_h_power",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="hp",
            l_flag="h_power",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="TFCE H power (default: %(default)s)",
            default=0.5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["TFCE H power"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_hp",
                    l_flag="tfce_h_power",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_hp",
                    l_flag="tfce_h_power",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    e_power = MiraclObj(
        name="tfce_e_power",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="ep",
            l_flag="e_power",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="TFCE E power (default: %(default)s)",
            default=2.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["TFCE E power"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_e",
                    l_flag="tfce_e_power",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_e",
                    l_flag="tfce_e_power",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load = MiraclObj(
        name="tfce_cpu_load",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="cpu",
            l_flag="cpu_load",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="CPU load (default: %(default)s)",
            default=0.9,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["CPU load"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_cpu",
                    l_flag="tfce_cpu_load",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_cpu",
                    l_flag="tfce_cpu_load",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    step_down_p = MiraclObj(
        name="tfce_step_down_p",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="p",
            l_flag="step_down_p",
            obj_type=ArgumentType.FLOAT,
            group=CliGroup.STATS_TFCE,
            help="step down p-value (default: %(default)s)",
            default=0.3,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Step down p-value"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_p",
                    l_flag="tfce_step_down_p",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_p",
                    l_flag="tfce_step_down_p",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    mask_thr = MiraclObj(
        name="tfce_mask_thr",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="mt",
            l_flag="step_mask_thr",
            obj_type=ArgumentType.INTEGER,
            group=CliGroup.STATS_TFCE,
            help="percentile to be used for binarizing difference of the mean (default: %(default)s)",
            default=95,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Mask threshold"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_mt",
                    l_flag="tfce_mask_thr",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_mt",
                    l_flag="tfce_mask_thr",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    hemi = MiraclObj(
        name="tfce_hemi",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="hm",
            l_flag="hemi",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="hemisphere: 'combined' or 'split' (default: %(default)s)",
            default="combined",
            choices=["combined", "split"],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Hemisphere"],
                widget_type=WidgetType.DROPDOWN,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_hm",
                    l_flag="tfce_hemi",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_hm",
                    l_flag="tfce_hemi",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    side = MiraclObj(
        name="tfce_side",
        module="tfce",
        module_group="stats",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow", "tfce"],
        cli=CLISpec(
            s_flag="s",
            l_flag="side",
            obj_type=ArgumentType.STRING,
            group=CliGroup.STATS_TFCE,
            help="side: 'lh' or 'rh' (default: %(default)s)",
            choices=["lh", "rh"],
            default="rh",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Side"],
                widget_type=WidgetType.DROPDOWN,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_s",
                    l_flag="tfce_side",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="tfce_s",
                    l_flag="tfce_side",
                    group=CliGroup.STATS_TFCE,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
