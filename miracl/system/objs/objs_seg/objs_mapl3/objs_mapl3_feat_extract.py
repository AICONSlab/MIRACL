from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class FeatExtract:
    vox_file: MiraclObj = MiraclObj(
        name="mfe_seg",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="s",
        cli_l_flag="seg",
        flow={
            "mapl3": {
                "cli_s_flag": "mfe_s",
                "cli_l_flag": "mfe_seg",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="segmentation tif (default: None)",
        cli_required=True,
        gui_label=["Segmentation tif"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    lbl: MiraclObj = MiraclObj(
        name="mfe_lbl",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="l",
        cli_l_flag="lbl",
        flow={
            "mapl3": {
                "cli_s_flag": "mfe_l",
                "cli_l_flag": "mfe_lbl",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="label annotation (default: None)",
        cli_required=True,
        gui_label=["Label annotation"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    mask: MiraclObj = MiraclObj(
        name="mfe_mask",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="mask",
        flow={
            "mapl3": {
                "cli_s_flag": "mfe_m",
                "cli_l_flag": "mfe_mask",
                "cli_group": CliGroup.MAPL3_FEAT_EXTRACT,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="ROI mask (default: None)",
        cli_required=False,
        gui_label=["ROI mask"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
