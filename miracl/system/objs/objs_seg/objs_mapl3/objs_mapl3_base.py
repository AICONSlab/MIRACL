from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)


class MAPL3Base:
    output = MiraclObj(
        id="d5fb45fb-6b8b-43e5-837f-286b9812ea67",
        name="mapl3_base_folder",
        tags=["mapl3", "seg", "mapl3_flow"],
        # cli_s_flag="o",
        # cli_l_flag="output",
        cli_s_flag="r",
        cli_l_flag="results",
        flow={"mapl3": {"cli_s_flag": "mb_o", "cli_l_flag": "mb_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="path of output directory i.e. MAPL3's base folder (default: None)",
        cli_required=True,
        gui_label=["Base output folder"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
