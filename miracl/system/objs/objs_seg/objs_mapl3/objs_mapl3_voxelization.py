from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class Voxelization:
    input_dir: MiraclObj = MiraclObj(
        name="mv_input_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "mv",
                "cli_l_flag": "mv_input",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input tif/tiff directory; this should be a folder containing binary slices through z (default: None)",
        cli_required=True,
        gui_label=["Input directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    out_dir: MiraclObj = MiraclObj(
        name="mv_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_o",
                "cli_l_flag": "mv_out_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Path to output directory (default: None)",
        cli_required=True,
        gui_label=["Output directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mv_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_c",
                "cli_l_flag": "mv_cpu_load",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
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

    downsample_yx_axis: MiraclObj = MiraclObj(
        name="mv_downsample_yx_axis",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="dx",
        cli_l_flag="downsample_yx_axis",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_dx",
                "cli_l_flag": "mv_downsample_yx_axis",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="downsample ration for y and x axis (default: %(default)s)",
        cli_required=False,
        obj_default=10,
        gui_label=["Dx ratio for x/y axes"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    downsample_z_axis: MiraclObj = MiraclObj(
        name="mv_downsample_yx_axis",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="dz",
        cli_l_flag="downsample_z_axis",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_dz",
                "cli_l_flag": "mv_downsample_z_axis",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="downsample ration for z axis (default: %(default)s)",
        cli_required=False,
        obj_default=10,
        gui_label=["Dx ratio for z axis"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    method: MiraclObj = MiraclObj(
        name="mv_method",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="method",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_m",
                "cli_l_flag": "mv_method",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="method for downsampling acceptable sum, min, max, mean, median (default: %(default)s)",
        cli_required=False,
        cli_choices=["sum", "min", "max", "mean", "median"],
        obj_default="sum",
        gui_label=["Dx method"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    out_name: MiraclObj = MiraclObj(
        name="mv_out_name",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_name",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_n",
                "cli_l_flag": "mv_out_name",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output name (default: %(default)s)",
        obj_default="voxelized_results",
        cli_required=True,
        gui_label=["Output name"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    res_xy: MiraclObj = MiraclObj(
        name="mv_res_xy",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="vx",
        cli_l_flag="res_xy",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_vx",
                "cli_l_flag": "mv_res_xy",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="resolution of the input in x and y in um (default: %(default)s)",
        cli_required=False,
        obj_default=1.0,
        gui_label=["Res of input in z (um)"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    res_z: MiraclObj = MiraclObj(
        name="mv_res_z",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="vz",
        cli_l_flag="res_z",
        flow={
            "mapl3": {
                "cli_s_flag": "mv_vz",
                "cli_l_flag": "mv_res_z",
                "cli_group": CliGroup.MAPL3_VOXELIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="resolution of the input in z in um (default: %(default)s)",
        cli_required=False,
        obj_default=1.0,
        gui_label=["Res of input in z (um)"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
