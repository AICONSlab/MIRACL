from miracl.system.datamodels.datamodel_miracl_objs import (
    InputRestrictionType,
    LineEditConfig,
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from pathlib import Path
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class ConvTiffNiiObjs:
    tiff_folder = MiraclObj(
        name="ctn_tiff_folder",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="f",
        cli_l_flag="folder",
        flow={
            "ace": {
                "cli_s_flag": "actn_f",
                "cli_l_flag": "actn_folder",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_f",
                "cli_l_flag": "mctn_folder",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Input CLARITY TIFF folder/dir",
        obj_default=None,
        cli_required=True,
        gui_label=["TIFF input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
    )

    output_folder = MiraclObj(
        name="ctn_output_folder",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="w",
        cli_l_flag="work_dir",
        flow={
            "ace": {
                "cli_s_flag": "actn_w",
                "cli_l_flag": "actn_work_dir",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_w",
                "cli_l_flag": "mctn_work_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output directory (default: %(default)s)",
        obj_default=Path.cwd(),
        gui_label=["Results output folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
    )

    down = MiraclObj(
        name="ctn_down",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="d",
        cli_l_flag="down",
        flow={
            "ace": {
                "cli_s_flag": "actn_d",
                "cli_l_flag": "actn_down",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_d",
                "cli_l_flag": "mctn_down",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Down-sample ratio for conversion (default: %(default)s)",
        obj_default=5,
        gui_label=["Conversion dx"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        gui_order=[8],
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    channum = MiraclObj(
        name="ctn_channum",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="cn",
        cli_l_flag="channum",
        flow={
            "ace": {
                "cli_s_flag": "actn_cn",
                "cli_l_flag": "actn_channum",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_cn",
                "cli_l_flag": "mctn_channum",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Chan # for extracting single channel from multiple channel data (default: %(default)s)",
        obj_default=0,
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Channel #"],
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
        range_formatting_vals={
            "min_val": 0,
            "max_val": 10000,
            "increment_val": 1,
        },
    )

    chanprefix = MiraclObj(
        name="ctn_chanprefix",
        cli_s_flag="cp",
        cli_l_flag="chanprefix",
        flow={
            "ace": {
                "cli_s_flag": "actn_cp",
                "cli_l_flag": "actn_chanprefix",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_cp",
                "cli_l_flag": "mctn_chanprefix",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_obj_type=ArgumentType.STRING,
        cli_help="Chan prefix (string before channel number in file name). ex: C00",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Channel prefix"],
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        obj_default=None,
        gui_widget_type=WidgetType.LINE_EDIT,
        line_edit_settings=LineEditConfig(
            input_restrictions=InputRestrictionType.STRCON
        ),
    )

    channame = MiraclObj(
        name="ctn_channame",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="ch",
        cli_l_flag="channame",
        flow={
            "ace": {
                "cli_s_flag": "actn_ch",
                "cli_l_flag": "actn_channame",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_ch",
                "cli_l_flag": "mctn_channame",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output chan name (default: %(default)s). Channel used in registration.",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Output channel name"],
        version_added="2.4.0",
        module="tiff_nii",
        module_group="conv",
        obj_default="auto",
        gui_widget_type=WidgetType.LINE_EDIT,
        line_edit_settings=LineEditConfig(
            input_restrictions=InputRestrictionType.STRCON
        ),
    )

    outnii = MiraclObj(
        name="ctn_outnii",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="outnii",
        flow={
            "ace": {
                "cli_s_flag": "actn_o",
                "cli_l_flag": "actn_outnii",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_o",
                "cli_l_flag": "mctn_outnii",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output nii name (script will append downsample ratio & channel info to given name). Method of tissue clearing.",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Out nii name"],
        version_added="2.4.0",
        module="tiff_nii",
        module_group="conv",
        obj_default="SHIELD",
        gui_widget_type=WidgetType.LINE_EDIT,
        line_edit_settings=LineEditConfig(
            input_restrictions=InputRestrictionType.ALPHANUMERIC
        ),
    )

    resx = MiraclObj(
        name="ctn_resx",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="vx",
        cli_l_flag="resx",
        flow={
            "ace": {
                "cli_s_flag": "actn_vx",
                "cli_l_flag": "actn_resx",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_vx",
                "cli_l_flag": "mctn_resx",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="Original resolution in x-y plane in um (default: %(default)s)",
        obj_default=5,
        gui_label=["Orig res in x-y plane (um)"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    resz = MiraclObj(
        name="ctn_resz",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="vz",
        cli_l_flag="resz",
        flow={
            "ace": {
                "cli_s_flag": "actn_vz",
                "cli_l_flag": "actn_resz",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_vz",
                "cli_l_flag": "mctn_resz",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="Original thickness (z-axis resolution / spacing between slices) in um (default: %(default)s)",
        obj_default=5,
        gui_label=["Orig thickness (um)"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    center = MiraclObj(
        name="ctn_center",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="center",
        flow={
            "ace": {
                "cli_s_flag": "actn_c",
                "cli_l_flag": "actn_center",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_c",
                "cli_l_flag": "mctn_center",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.LIST,
        cli_help="Nii center (default: 0 0 3 ) corresponding to Allen atlas nii template",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Nii center"],
        version_added="2.4.0",
        cli_nargs=3,
        module="tiff_nii",
        module_group="conv",
        obj_default=[0, 0, 3],
        gui_widget_type=WidgetType.LINE_EDIT,
        line_edit_settings=LineEditConfig(input_restrictions=InputRestrictionType.INT),
    )

    downzdim = MiraclObj(
        name="ctn_downzdim",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="dz",
        cli_l_flag="downzdim",
        flow={
            "ace": {
                "cli_s_flag": "actn_dz",
                "cli_l_flag": "actn_downzdim",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_dz",
                "cli_l_flag": "mctn_downzdim",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Down-sample in z dimension, set to '0' for no, set to '1' for yes (default: %(default)s)",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Z-axis dx"],
        version_added="2.4.0",
        module="tiff_nii",
        module_group="conv",
        obj_default=1,
        cli_choices=[0, 1],
    )

    prevdown = MiraclObj(
        name="ctn_prevdown",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="pd",
        cli_l_flag="prevdown",
        flow={
            "ace": {
                "cli_s_flag": "actn_pd",
                "cli_l_flag": "actn_prevdown",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_pd",
                "cli_l_flag": "mctn_prevdown",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="Previous down-sample ratio, if already down-sampled",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["Previous dx"],
        version_added="2.4.0",
        module="tiff_nii",
        module_group="conv",
        obj_default=1,
        gui_widget_type=WidgetType.SPINBOX,
    )

    percentile_thr = MiraclObj(
        name="ctn_percentile_thr",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="pct",
        cli_l_flag="percentile_thr",
        flow={
            "ace": {
                "cli_s_flag": "actn_pct",
                "cli_l_flag": "actn_percentile_thr",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
            "mapl3": {
                "cli_s_flag": "mctn_pct",
                "cli_l_flag": "mctn_percentile_thr",
                "cli_group": CliGroup.CONV_TIFF_NII,
            },
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="Percentile threshold for intensity correction (default: %(default)s)",
        gui_group={"ace_flow": "conversion", "mapl3:": "conversion"},
        gui_label=["% threshold intensity corr"],
        version_added="2.4.0",
        module="tiff_nii",
        module_group="conv",
        obj_default=0.01,
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
        range_formatting_vals={
            "min_val": 0.000,
            "max_val": 1.000,
            "increment_val": 0.01,
            "nr_decimals": 3,
        },
    )
