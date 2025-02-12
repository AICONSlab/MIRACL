from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)


class PatchStacking:
    cpu_load = MiraclObj(
        id="075bf338-2eb9-4fda-a2a7-71898b307989",
        name="cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mps_c",
        cli_l_flag="mps_cpu_load",
        flow={"mapl3": {"cli_s_flag": "mps_c", "cli_l_flag": "mps_cpu_load"}},
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

    keep_image_type = MiraclObj(
        id="9bdf62e3-ef9d-44dc-8f28-770f74e90885",
        name="keep_image_type",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="mps_i",
        cli_l_flag="mps_keep_image_type",
        flow={
            "mapl3": {
                "cli_s_flag": "mps_i",
                "cli_l_flag": "mps_keep_image_type",
            }
        },
        cli_action=ArgumentAction.STORE_TRUE,
        cli_help="keep image type same as patches type (default: %(default)s)",
        cli_required=False,
        obj_default=False,
        gui_label=["Keep image type same as patches type"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )


# my_parser.add_argument('-i','--input', help='input directory containing .tif image patches', required=True)
# my_parser.add_argument('-m','--input_raw', help='input directory containing .tif or .tiff image slices of raw data', required=True)
# my_parser.add_argument('-o','--out_dir', help='path of output directory', required=True)
