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


class Voxelization:
    _MV_GROUP = CliGroup.MAPL3_VOXELIZATION

    input_dir: MiraclObj = MiraclObj(
        name="mv_input_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input tif/tiff directory; this should be a folder containing binary slices through z (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Input directory"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mv",
                    l_flag="mv_input",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_dir: MiraclObj = MiraclObj(
        name="mv_out_dir",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_dir",
            obj_type=ArgumentType.STRING,
            help="Path to output directory (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output directory"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mv_o",
                    l_flag="mv_out_dir",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mv_cpu_load",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="cpu_load",
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
                        min_val=0.0,
                        max_val=1.0,
                        increment_val=0.01,
                        nr_decimals=2,
                    )
                ),
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_c",
                    l_flag="mv_cpu_load",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    downsample_yx_axis: MiraclObj = MiraclObj(
        name="mv_downsample_yx_axis",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="dx",
            l_flag="downsample_yx_axis",
            obj_type=ArgumentType.INTEGER,
            help="downsample ration for y and x axis (default: %(default)s)",
            required=False,
            default=10,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Dx ratio for x/y axes"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_dx",
                    l_flag="mv_downsample_yx_axis",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    downsample_z_axis: MiraclObj = MiraclObj(
        name="mv_downsample_z_axis",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="dz",
            l_flag="downsample_z_axis",
            obj_type=ArgumentType.INTEGER,
            help="downsample ration for z axis (default: %(default)s)",
            required=False,
            default=10,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Dx ratio for z axis"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=1,
                        max_val=10000,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_dz",
                    l_flag="mv_downsample_z_axis",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    method: MiraclObj = MiraclObj(
        name="mv_method",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="method",
            obj_type=ArgumentType.STRING,
            help="method for downsampling acceptable sum, min, max, mean, median (default: %(default)s)",
            required=False,
            default="sum",
            choices=["sum", "min", "max", "mean", "median"],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Dx method"],
                widget_type=WidgetType.COMBO_BOX,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_m",
                    l_flag="mv_method",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    out_name: MiraclObj = MiraclObj(
        name="mv_out_name",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="out_name",
            obj_type=ArgumentType.STRING,
            help="Output name (default: %(default)s)",
            default="voxelized_results",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output name"],
                widget_type=WidgetType.LINE_EDIT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_n",
                    l_flag="mv_out_name",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    res_xy: MiraclObj = MiraclObj(
        name="mv_res_xy",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="vx",
            l_flag="res_xy",
            obj_type=ArgumentType.FLOAT,
            help="resolution of the input in x and y in um (default: %(default)s)",
            required=False,
            default=1.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Resolution of input in xy (um)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=100.00,
                        increment_val=0.1,
                        nr_decimals=2,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_vx",
                    l_flag="mv_res_xy",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    res_z: MiraclObj = MiraclObj(
        name="mv_res_z",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="vz",
            l_flag="res_z",
            obj_type=ArgumentType.FLOAT,
            help="resolution of the input in z in um (default: %(default)s)",
            required=False,
            default=1.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Resolution of input in z (um)"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.00,
                        max_val=100.00,
                        increment_val=0.1,
                        nr_decimals=2,
                    )
                ),
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mv_vz",
                    l_flag="mv_res_z",
                    group=_MV_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
