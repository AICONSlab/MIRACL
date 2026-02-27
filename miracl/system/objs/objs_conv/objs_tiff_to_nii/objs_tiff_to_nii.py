from pathlib import Path
from miracl.system.enums.enums_base_modules import CliGroup

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    GuiWidgetSpecifics,
    RangeFormConfig,
    LineEditConfig,
    GuiChoiceOverrideConfig,
    FlowOverride,
    ArgumentType,
    WidgetType,
    InputRestrictionType,
    ArgumentSource,
)


class ConvTiffNiiObjs:
    tiff_folder = MiraclObj(
        name="ctn_tiff_folder",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="f",
            l_flag="folder",
            obj_type=ArgumentType.STRING,
            help="Input CLARITY TIFF folder/dir",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["TIFF input folder"],
                widget_type=WidgetType.LINE_EDIT,
                props=GuiWidgetSpecifics(range=RangeFormConfig(min_val=5.0)),
            ),
            extensions={"qt": {"placeholder_text": "Select folder"}},
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_f",
                    l_flag="actn_folder",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mctn_f",
                    l_flag="mctn_folder",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
        },
    )

    output_folder = MiraclObj(
        name="ctn_output_folder",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="w",
            l_flag="work_dir",
            obj_type=ArgumentType.STRING,
            help="Output directory (default: %(default)s)",
            default=Path.cwd(),
        ),
        gui=GuiNamespace(base=GuiBase(label=["Results output folder"])),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_w",
                    l_flag="actn_work_dir",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mctn_w",
                    l_flag="mctn_work_dir",
                    group=CliGroup.REQUIRED,
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
        },
    )

    down = MiraclObj(
        name="ctn_down",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="d",
            l_flag="down",
            obj_type=ArgumentType.INTEGER,
            help="Down-sample ratio for conversion (default: %(default)s)",
            default=5,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Conversion dx"],
                widget_type=WidgetType.SPINBOX,
                order=8.0,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_d", l_flag="actn_down", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_d", l_flag="mctn_down", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
        },
    )

    channum = MiraclObj(
        name="ctn_channum",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cn",
            l_flag="channum",
            obj_type=ArgumentType.INTEGER,
            help="Chan # for extracting single channel from multiple channel data (default: %(default)s)",
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Channel #"],
                widget_type=WidgetType.SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(min_val=0, max_val=10000, increment_val=1)
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_cn",
                    l_flag="actn_channum",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_cn",
                    l_flag="mctn_channum",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    chanprefix = MiraclObj(
        name="ctn_chanprefix",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="cp",
            l_flag="chanprefix",
            obj_type=ArgumentType.STRING,
            help="Chan prefix (string before channel number in file name). ex: C00",
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Channel prefix"],
                widget_type=WidgetType.LINE_EDIT,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.STRCON)
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_cp",
                    l_flag="actn_chanprefix",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_cp",
                    l_flag="mctn_chanprefix",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    channame = MiraclObj(
        name="ctn_channame",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="ch",
            l_flag="channame",
            obj_type=ArgumentType.STRING,
            help="Output chan name (default: %(default)s). Channel used in registration.",
            default="auto",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Output channel name"],
                widget_type=WidgetType.LINE_EDIT,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.STRCON)
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_ch",
                    l_flag="actn_channame",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_ch",
                    l_flag="mctn_channame",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    outnii = MiraclObj(
        name="ctn_outnii",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="outnii",
            obj_type=ArgumentType.STRING,
            help="Output nii name (script will append downsample ratio & channel info to given name). Method of tissue clearing (default: %(default)s).",
            default="SHIELD",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Out nii name"],
                widget_type=WidgetType.LINE_EDIT,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(
                        input_restrictions=InputRestrictionType.ALPHANUMERIC
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_o", l_flag="actn_outnii", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_o", l_flag="mctn_outnii", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    resx = MiraclObj(
        name="ctn_resx",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="vx",
            l_flag="resx",
            obj_type=ArgumentType.FLOAT,
            help="Original resolution in x-y plane in um (default: %(default)s)",
            default=5.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Orig res in x-y plane (um)"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_vx", l_flag="actn_resx", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_vx", l_flag="mctn_resx", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
        },
    )

    resz = MiraclObj(
        name="ctn_resz",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="vz",
            l_flag="resz",
            obj_type=ArgumentType.FLOAT,
            help="Original thickness (z-axis resolution / spacing between slices) in um (default: %(default)s)",
            default=5.0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Orig thickness (um)"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_vz", l_flag="actn_resz", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_vz", l_flag="mctn_resz", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="main")),
            ),
        },
    )

    center = MiraclObj(
        name="ctn_center",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="center",
            obj_type=ArgumentType.LIST,
            nargs=3,
            help="Nii center (default: 0 0 3 ) corresponding to Allen atlas nii template",
            default=[0, 0, 3],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Nii center"],
                widget_type=WidgetType.LINE_EDIT,
                props=GuiWidgetSpecifics(
                    text=LineEditConfig(input_restrictions=InputRestrictionType.INT)
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_c", l_flag="actn_center", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_c", l_flag="mctn_center", group=CliGroup.CONV_TIFF_NII
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    downzdim = MiraclObj(
        name="ctn_downzdim",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="dz",
            l_flag="downzdim",
            obj_type=ArgumentType.INTEGER,
            help="Down-sample in z dimension, set to '0' for no, set to '1' for yes (default: %(default)s)",
            default=1,
            choices=[0, 1],
        ),
        gui=GuiNamespace(base=GuiBase(label=["Z-axis dx"])),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_dz",
                    l_flag="actn_downzdim",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_dz",
                    l_flag="mctn_downzdim",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    prevdown = MiraclObj(
        name="ctn_prevdown",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="pd",
            l_flag="prevdown",
            obj_type=ArgumentType.INTEGER,
            help="Previous down-sample ratio, if already down-sampled",
            default=1,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Previous dx"],
                widget_type=WidgetType.SPINBOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_pd",
                    l_flag="actn_prevdown",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_pd",
                    l_flag="mctn_prevdown",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )

    percentile_thr = MiraclObj(
        name="ctn_percentile_thr",
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="pct",
            l_flag="percentile_thr",
            obj_type=ArgumentType.FLOAT,
            help="Percentile threshold for intensity correction (default: %(default)s)",
            default=0.01,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["% threshold intensity corr"],
                widget_type=WidgetType.DOUBLE_SPINBOX,
                props=GuiWidgetSpecifics(
                    range=RangeFormConfig(
                        min_val=0.000, max_val=1.000, increment_val=0.01, nr_decimals=3
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="actn_pct",
                    l_flag="actn_percentile_thr",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mctn_pct",
                    l_flag="mctn_percentile_thr",
                    group=CliGroup.CONV_TIFF_NII,
                ),
                gui=GuiDelta(base=GuiBase(group="conversion")),
            ),
        },
    )
