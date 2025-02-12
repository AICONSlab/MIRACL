from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)


class Inference:
    config = MiraclObj(
        id="825659a4-a61c-417e-8266-6bd4360fcd7f",
        name="config",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_c",
        cli_l_flag="mi_config",
        flow={"mapl3": {"cli_s_flag": "mi_c", "cli_l_flag": "mi_config"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="path of config file used during training to define the model",
        cli_required=True,
        gui_label=["Config file"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    model_path = MiraclObj(
        id="3373b6c0-e88f-480f-8f21-4c5194d8eeb4",
        name="model_path",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_m",
        cli_l_flag="mi_model_path",
        flow={"mapl3": {"cli_s_flag": "mi_m", "cli_l_flag": "mi_model_path"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to trained model",
        cli_required=True,
        gui_label=["Path to trained model"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    tissue_percentage_threshold = MiraclObj(
        id="98dcf83e-aa71-4da5-aae8-c102fd100bdd",
        name="mi_tissue_percentage_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_p",
        cli_l_flag="mi_tissue_percentage_threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_p",
                "cli_l_flag": "mi_tissue_percentage_threshold",
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="whether to use json file to filter empty patches if passsed must be threshold between 0 and 1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.0,
        gui_label=["Tissue % threshold"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    gpu_index = MiraclObj(
        id="ebd46db3-d2f5-4c45-af3c-0e5c26a66520",
        name="mi_gpu_index",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_g",
        cli_l_flag="mi_gpu_index",
        flow={"mapl3": {"cli_s_flag": "mi_g", "cli_l_flag": "mi_gpu_index"}},
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="gpu index to be used; if you wanna use all the available gpus, pass '-1' as the flag argument (default: %(default)s)",
        cli_required=False,
        obj_default=0,
        gui_label=["GPU index"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    binarization_threshold = MiraclObj(
        id="a3972c44-0697-47bb-85fc-666a0cf18dd6",
        name="mi_binarization_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_b",
        cli_l_flag="mi_binarization_threshold",
        flow={
            "mapl3": {"cli_s_flag": "mi_b", "cli_l_flag": "mi_binarization_threshold"}
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold (between 0-1) to binarize the model probabilty map (default: %(default)s)",
        cli_required=False,
        obj_default=0.5,
        gui_label=["Tissue % threshold"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    save_prob_map = MiraclObj(
        id="63b30b27-13d5-464d-b9b6-e3749e1b7a36",
        name="mi_save_prob_map",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mi_s",
        cli_l_flag="mi_save_prob_map",
        flow={"mapl3": {"cli_s_flag": "mi_s", "cli_l_flag": "mi_save_prob_map"}},
        cli_action=ArgumentAction.STORE_FALSE,
        cli_help="set to save prob map (default: %(default)s)",
        cli_required=False,
        obj_default=True,
        gui_label=["Save prob map"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )
