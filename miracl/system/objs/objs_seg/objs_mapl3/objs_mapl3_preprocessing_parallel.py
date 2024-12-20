from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)


class PreprocessingParallel:
    output = MiraclObj(
        id="beffa5d5-23c9-4152-8688-94724b6a829f",
        name="mgp_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="output",
        flow={"mapl3": {"cli_s_flag": "mgpo", "cli_l_flag": "mgp_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="path of output directory (default: None)",
        cli_required=True,
        gui_label=["Output folder"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
