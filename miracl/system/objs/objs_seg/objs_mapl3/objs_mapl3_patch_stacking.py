from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class PatchStacking:
    input_dir: MiraclObj = MiraclObj(
        name="mps_input_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_i",
                "cli_l_flag": "mps_input",
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

    out_dir: MiraclObj = MiraclObj(
        name="mps_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_o",
                "cli_l_flag": "mps_out_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output directory for stitched Z-stack (default: None)",
        cli_required=True,
        gui_label=["Output directory"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="mps_tiff_folder",
        tags=["tiff_nii", "conv", "ace_flow", "mapl3_flow"],
        cli_s_flag="r",
        cli_l_flag="raw_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_r",
                "cli_l_flag": "mps_raw_dir",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Directory containing raw .tif slices for original dimensions (default: None)",
        obj_default=None,
        cli_required=True,
        gui_label=["TIFF input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="tiff_nii",
        module_group="conv",
        version_added="2.4.0",
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mps_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_c",
                "cli_l_flag": "mps_cpu_load",
                "cli_group": CliGroup.MAPL3_PATCH_STACKING,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="fraction of cpus to be used for parallelization between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.7,
        gui_label=["CPU load"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    metadata_file: MiraclObj = MiraclObj(
        name="mps_metadata",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="metadata_path",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_m",
                "cli_l_flag": "mps_metadata",
                "cli_group": CliGroup.MAPL3_PATCH_STACKING,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to metadata JSON file (default: None)",
        cli_required=True,
        gui_label=["Path to metadata JSON"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    dtype: MiraclObj = MiraclObj(
        name="mps_dtype",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="d",
        cli_l_flag="dtype",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_d",
                "cli_l_flag": "mps_dtype",
                "cli_group": CliGroup.MAPL3_PATCH_STACKING,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Output data type (e.g., uint16, bool; default: %(default)s)",
        cli_required=True,
        obj_default="uint16",
        gui_label=["Output data type"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )
