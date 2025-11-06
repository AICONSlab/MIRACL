from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class Inference:
    config = MiraclObj(
        name="mi_config",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="config",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_c",
                "cli_l_flag": "mi_config",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
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

    out_dir: MiraclObj = MiraclObj(
        name="mi_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="output_path",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_o",
                "cli_l_flag": "mi_out_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path of output directory (default: None)",
        cli_required=True,
        gui_label=["Output directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    model_path = MiraclObj(
        name="mi_model_path",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="model_path",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_m",
                "cli_l_flag": "mi_model_path",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
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

    input_dir: MiraclObj = MiraclObj(
        name="mi_input_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_i",
                "cli_l_flag": "mi_input_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to input directory containing patches (default: None)",
        cli_required=True,
        gui_label=["Input directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    gpu_index = MiraclObj(
        name="mi_gpu_index",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="g",
        cli_l_flag="gpu_index",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_g",
                "cli_l_flag": "mi_gpu_index",
                "cli_group": CliGroup.MAPL3_INFERENCE,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="gpu index to be used; if you wanna use all the available gpus, pass 'all' as the flag argument (default: %(default)s)",
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
        name="mi_binarization_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="b",
        cli_l_flag="binarization_threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_b",
                "cli_l_flag": "mi_binarization_threshold",
                "cli_group": CliGroup.MAPL3_INFERENCE,
            }
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
        name="mi_save_prob_map_flag",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="s",
        cli_l_flag="save_prob_map_flag",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_s",
                "cli_l_flag": "mi_save_prob_map_flag",
                "cli_group": CliGroup.MAPL3_INFERENCE,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="set to save prob map (default: %(default)s)",
        cli_required=False,
        obj_default=False,
        gui_label=["Save prob map"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mi_metadata",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="j",
        cli_l_flag="metadata",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_j",
                "cli_l_flag": "mi_metadata",
                "cli_group": CliGroup.MAPL3_INFERENCE,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to metadata JSON file (default: None)",
        cli_required=False,
        obj_default=None,
        gui_label=["Path to metadata JSON"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    tissue_percentage_threshold = MiraclObj(
        name="mi_tissue_percentage_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="p",
        cli_l_flag="tissue_percentage_threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "mi_p",
                "cli_l_flag": "mi_tissue_percentage_threshold",
                "cli_group": CliGroup.MAPL3_INFERENCE,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold between 0-100 to filter empty patches (default: None)",
        cli_required=False,
        obj_default=None,
        gui_label=["Tissue % threshold"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )
