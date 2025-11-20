from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from pathlib import Path
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)
from pathlib import Path


class PlotWarpedData:
    pvalue: MiraclObj = MiraclObj(
        name="mpwd_pvalue",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="p",
        cli_l_flag="pvalue",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_p",
                "cli_l_flag": "mpwd_pvalue",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to p-value nii file (default: None)",
        gui_label=["P-Value nii file"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    atlas_dir: MiraclObj = MiraclObj(
        name="mpwd_atlas_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="atl",
        cli_l_flag="atlas_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_atl",
                "cli_l_flag": "mpwd_atlas_dir",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to atlas dir (default: None)",
        gui_label=["Atlas dir"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    vox: MiraclObj = MiraclObj(
        name="mpwd_vox",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="v",
        cli_l_flag="vox",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_v",
                "cli_l_flag": "mpwd_vox",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="voxel size/resolution in um (default: None)",
        cli_choices=[10, 25, 50],
        gui_label=["Voxel res"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    sigma: MiraclObj = MiraclObj(
        name="mpwd_sigma",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="gs",
        cli_l_flag="sigma",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_gs",
                "cli_l_flag": "mpwd_sigma",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Gaussian smoothing sigma (default: %(default)s)",
        obj_default=4,
        gui_label=["Sigma"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    colourmap_pos: MiraclObj = MiraclObj(
        name="mpwd_colourmap_pos",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="pos",
        cli_l_flag="colourmap_pos",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_pos",
                "cli_l_flag": "mpwd_colourmap_pos",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Matplotlib colourmap for p-values (default: %(default)s)",
        obj_default="Reds",
        gui_label=["Colourmap p-values"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    colourmap_neg: MiraclObj = MiraclObj(
        name="mpwd_colourmap_neg",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="cn",
        cli_l_flag="colourmap_neg",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_cn",
                "cli_l_flag": "mpwd_colourmap_neg",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Matplotlib colourmap for negative values (default: %(default)s)",
        obj_default="Blues",
        gui_label=["Colourmap neg values"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    sagittal: MiraclObj = MiraclObj(
        name="mpwd_sagittal",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="s",
        cli_l_flag="sagittal",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_s",
                "cli_l_flag": "mpwd_sagittal",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
        obj_default=float("nan"),
        cli_nargs=5,
        gui_label=["Sagittal axis"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    coronal: MiraclObj = MiraclObj(
        name="mpwd_coronal",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="coronal",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_c",
                "cli_l_flag": "mpwd_coronal",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
        obj_default=float("nan"),
        cli_nargs=5,
        gui_label=["Coronal axis"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    axial: MiraclObj = MiraclObj(
        name="mpwd_axial",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="a",
        cli_l_flag="axial",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_a",
                "cli_l_flag": "mpwd_axial",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns (default: %(default)s)",
        obj_default=float("nan"),
        cli_nargs=5,
        gui_label=["axial axis"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    figure_dim: MiraclObj = MiraclObj(
        name="mpwd_figure_dim",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="f",
        cli_l_flag="figure_dim",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_f",
                "cli_l_flag": "mpwd_figure_dim",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="figure width and height (default: None)",
        cli_nargs=2,
        gui_label=["Figure w and h"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    dir_outfile: MiraclObj = MiraclObj(
        name="mpwd_dir_outfile",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="d",
        cli_l_flag="dir_outfile",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_d",
                "cli_l_flag": "mpwd_dir_outfile",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        obj_default=Path.cwd(),
        cli_help="Output file directory (default: %(default)s)",
        gui_label=["Output dir"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    outfile: MiraclObj = MiraclObj(
        name="mpwd_outfile",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="outfile",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_o",
                "cli_l_flag": "mpwd_outfile",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="output filenames (default: %(default)s)",
        obj_default="heatmap_figure_extension",
        cli_nargs="+",
        gui_label=["Output filenames"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    extension: MiraclObj = MiraclObj(
        name="mpwd_extension",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="e",
        cli_l_flag="extension",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_e",
                "cli_l_flag": "mpwd_extension",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="heatmap figure extension (default: %(default)s)",
        obj_default="tiff",
        gui_label=["Figure extension"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    dpi: MiraclObj = MiraclObj(
        name="mpwd_dpi",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="dpi",
        cli_l_flag="dpi",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_dpi",
                "cli_l_flag": "mpwd_dpi",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="dots per inch (default: %(default)s)",
        obj_default=500,
        gui_label=["DPI"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    hemi: MiraclObj = MiraclObj(
        name="mpwd_hemi",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="hemi",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_m",
                "cli_l_flag": "mpwd_hemi",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
        obj_default="combined",
        cli_choices=["combined", "split"],
        gui_label=["Hemisphere"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    side: MiraclObj = MiraclObj(
        name="mpwd_side",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="si",
        cli_l_flag="side",
        flow={
            "mapl3": {
                "cli_s_flag": "mpwd_si",
                "cli_l_flag": "mpwd_side",
                "cli_group": CliGroup.MAPL3_PLOT_WARPED_DATA,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
        obj_default=None,
        cli_choices=["rh", "lh"],
        gui_label=["Hemi side"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
