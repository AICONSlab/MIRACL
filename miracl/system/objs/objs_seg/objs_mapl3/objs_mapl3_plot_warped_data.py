from pathlib import Path
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiWidgetSpecifics,
    RangeFormConfig,
    GuiDelta,
    FlowOverride,
    ArgumentSource,
    ArgumentType,
    WidgetType,
)


class PlotWarpedData:
    _MPWD_GROUP = CliGroup.MAPL3_PLOT_WARPED_DATA

    pvalue: MiraclObj = MiraclObj(
        name="mpwd_pvalue",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="p",
            l_flag="pvalue",
            obj_type=ArgumentType.STRING,
            help="path to p-value nii file (default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["P-Value nii file"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpwd_p",
                    l_flag="mpwd_pvalue",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    atlas_dir: MiraclObj = MiraclObj(
        name="mpwd_atlas_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="atl",
            l_flag="atlas_dir",
            obj_type=ArgumentType.STRING,
            help="path to atlas dir (default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Atlas dir"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_atl",
                    l_flag="mpwd_atlas_dir",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    vox: MiraclObj = MiraclObj(
        name="mpwd_vox",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="v",
            l_flag="vox",
            obj_type=ArgumentType.INTEGER,
            help="voxel size/resolution in um (default: None)",
            required=False,
            default=None,
            choices=[10, 25, 50],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Voxel res"],
                widget_type=WidgetType.COMBO_BOX,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpwd_v",
                    l_flag="mpwd_vox",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    sigma: MiraclObj = MiraclObj(
        name="mpwd_sigma",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="gs",
            l_flag="sigma",
            obj_type=ArgumentType.INTEGER,
            help="Gaussian smoothing sigma (default: %(default)s)",
            required=False,
            default=4,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Sigma"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10_000,
                    )
                ),
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpwd_gs",
                    l_flag="mpwd_sigma",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    colourmap_pos: MiraclObj = MiraclObj(
        name="mpwd_colourmap_pos",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="pos",
            l_flag="colourmap_pos",
            obj_type=ArgumentType.STRING,
            help="Matplotlib colourmap for p-values (default: %(default)s)",
            required=False,
            default="Reds",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Colourmap p-values"],
                widget_type=WidgetType.LINE_EDIT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_pos",
                    l_flag="mpwd_colourmap_pos",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    colourmap_neg: MiraclObj = MiraclObj(
        name="mpwd_colourmap_neg",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cn",
            l_flag="colourmap_neg",
            obj_type=ArgumentType.STRING,
            help="Matplotlib colourmap for negative values (default: %(default)s)",
            required=False,
            default="Blues",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Colourmap neg values"],
                widget_type=WidgetType.LINE_EDIT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_cn",
                    l_flag="mpwd_colourmap_neg",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    sagittal: MiraclObj = MiraclObj(
        name="mpwd_sagittal",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="sagittal",
            obj_type=ArgumentType.LIST,
            help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
            required=False,
            default=[
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            ],
            nargs=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Sagittal axis"],
                widget_type=WidgetType.LINE_EDIT,  # NOTE: inherited from original; likely should be MULTI_INPUT
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_s",
                    l_flag="mpwd_sagittal",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    coronal: MiraclObj = MiraclObj(
        name="mpwd_coronal",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="coronal",
            obj_type=ArgumentType.LIST,
            help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
            required=False,
            default=[
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            ],
            nargs=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Coronal axis"],
                widget_type=WidgetType.LINE_EDIT,  # NOTE: inherited from original; likely should be MULTI_INPUT
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_c",
                    l_flag="mpwd_coronal",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    axial: MiraclObj = MiraclObj(
        name="mpwd_axial",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="axial",
            obj_type=ArgumentType.LIST,
            help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
            required=False,
            default=[
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
            ],
            nargs=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["axial axis"],
                widget_type=WidgetType.LINE_EDIT,  # NOTE: inherited from original; likely should be MULTI_INPUT
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_a",
                    l_flag="mpwd_axial",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    figure_dim: MiraclObj = MiraclObj(
        name="mpwd_figure_dim",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="f",
            l_flag="figure_dim",
            obj_type=ArgumentType.LIST,
            help="figure width and height (default: None)",
            required=False,
            default=[float("nan"), float("nan")],
            nargs=2,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Figure w and h"],
                widget_type=WidgetType.LINE_EDIT,  # NOTE: inherited from original; likely should be MULTI_INPUT
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_f",
                    l_flag="mpwd_figure_dim",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    dir_outfile: MiraclObj = MiraclObj(
        name="mpwd_dir_outfile",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="d",
            l_flag="dir_outfile",
            obj_type=ArgumentType.STRING,
            help="Output file directory (default: %(default)s)",
            required=False,
            default=Path.cwd(),
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output dir"],
                widget_type=WidgetType.PATH_INPUT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpwd_d",
                    l_flag="mpwd_dir_outfile",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    outfile: MiraclObj = MiraclObj(
        name="mpwd_outfile",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="outfile",
            obj_type=ArgumentType.STRING,
            help="output filenames (default: %(default)s)",
            required=False,
            default="heatmap_figure_extension",
            nargs="+",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output filenames"],
                widget_type=WidgetType.LINE_EDIT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mpwd_o",
                    l_flag="mpwd_outfile",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    extension: MiraclObj = MiraclObj(
        name="mpwd_extension",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="e",
            l_flag="extension",
            obj_type=ArgumentType.STRING,
            help="heatmap figure extension (default: %(default)s)",
            required=False,
            default="tiff",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Figure extension"],
                widget_type=WidgetType.LINE_EDIT,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_e",
                    l_flag="mpwd_extension",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    dpi: MiraclObj = MiraclObj(
        name="mpwd_dpi",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="dpi",
            l_flag="dpi",
            obj_type=ArgumentType.INTEGER,
            help="dots per inch (default: %(default)s)",
            required=False,
            default=500,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["DPI"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=100_000,
                    )
                ),
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_dpi",
                    l_flag="mpwd_dpi",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    hemi: MiraclObj = MiraclObj(
        name="mpwd_hemi",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="hemi",
            obj_type=ArgumentType.STRING,
            help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
            required=False,
            default="combined",
            choices=["combined", "split"],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Hemisphere"],
                widget_type=WidgetType.COMBO_BOX,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_m",
                    l_flag="mpwd_hemi",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    side: MiraclObj = MiraclObj(
        name="mpwd_side",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="si",
            l_flag="side",
            obj_type=ArgumentType.STRING,
            help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
            required=False,
            default=None,
            choices=["rh", "lh", "None"],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Hemi side"],
                widget_type=WidgetType.COMBO_BOX,
                order=1.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mpwd_si",
                    l_flag="mpwd_side",
                    group=_MPWD_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
