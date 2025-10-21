from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class RawDataNormalization:
    input_dir: MiraclObj = MiraclObj(
        name="mrdn_input_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn",
                "cli_l_flag": "mrdn_input",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input tif/tiff probability map (default: None)",
        cli_required=True,
        gui_label=["Input directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="mrdn_tiff_folder",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="r",
        cli_l_flag="raw_data",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_r",
                "cli_l_flag": "mrdn_raw_data",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Directory containing raw .tif slices for original dimensions (default: None)",
        cli_required=True,
        gui_label=["TIFF input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
    )

    brain_mask: MiraclObj = MiraclObj(
        name="mrdn_brain_mask",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="brain_mask",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_m",
                "cli_l_flag": "mrdn_brain_mask",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input brain mask tif/tiff directory (default: None)",
        cli_required=True,
        gui_label=["Brain mask"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    num_erosion: MiraclObj = MiraclObj(
        name="mrdn_num_erosion",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ne",
        cli_l_flag="num_erosion",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_ne",
                "cli_l_flag": "mrdn_num_erosion",
                "cli_group": CliGroup.MAPL3_RAW_DATA_NORMALIZATION,
                "disabled": False,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="how many times run binary erosion on the mask (default: %(default)s)",
        cli_required=False,
        obj_default=50,
        gui_label=["# of erosions"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    alpha: MiraclObj = MiraclObj(
        name="mrdn_alpha",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="a",
        cli_l_flag="num_alpha",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_a",
                "cli_l_flag": "mrdn_alpha",
                "cli_group": CliGroup.MAPL3_RAW_DATA_NORMALIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="alpha for linear mixation of probability map and raw image; 0 (only model) 1 (only raw image) (default: %(default)s)",
        cli_required=False,
        obj_default=0.5,
        gui_label=["Alpha"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    threshold: MiraclObj = MiraclObj(
        name="mrdn_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="t",
        cli_l_flag="num_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_t",
                "cli_l_flag": "mrdn_thr",
                "cli_group": CliGroup.MAPL3_RAW_DATA_NORMALIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="threshold for binarization (default: %(default)s)",
        cli_required=False,
        obj_default=0.5,
        gui_label=["Binarization thr"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    out_dir: MiraclObj = MiraclObj(
        name="mrdn_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_o",
                "cli_l_flag": "mrdn_out_dir",
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
        name="mrdn_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "mrdn_c",
                "cli_l_flag": "mrdn_cpu_load",
                "cli_group": CliGroup.MAPL3_RAW_DATA_NORMALIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="fraction of cpus to be used for parallelization between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.5,
        gui_label=["CPU load"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )
