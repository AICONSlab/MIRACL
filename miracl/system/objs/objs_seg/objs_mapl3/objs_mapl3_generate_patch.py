from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.datamodels.miraclobj_enums import (
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class GeneratePatch:
    input: MiraclObj = MiraclObj(
        name="mgp_input",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_i",
                "cli_l_flag": "mgp_input",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input directory containing .tiff or .tif slices (default: None)",
        cli_required=True,
        gui_label=["Input folder"],
        gui_group={"mapl3": "main"},
        gui_order=[1],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    brain_mask: MiraclObj = MiraclObj(
        name="mgp_brain_mask",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="brain_mask",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_m",
                "cli_l_flag": "mgp_brain_mask",
                "cli_group": CliGroup.MAPL3_GENERATE_PATCH,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input directory containing .tiff or .tif brain mask slices if not passed it will compute mask (default: %(default)s)",
        cli_required=False,
        gui_label=["Brain mask"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    out_dir: MiraclObj = MiraclObj(
        name="mgp_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_o",
                "cli_l_flag": "mgp_out_dir",
                "cli_group": CliGroup.REQUIRED,
                "required": True,
                "disabled": True,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="output directory for patches (default: None)",
        cli_required=True,
        gui_label=["Output directory for patches"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    cpu_load: MiraclObj = MiraclObj(
        name="mgp_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_c",
                "cli_l_flag": "mgp_cpu_load",
                "cli_group": CliGroup.MAPL3_GENERATE_PATCH,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="fraction of cpus to be used for parallelization. Value needs to be between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.7,
        gui_label=["CPU load"],
        gui_group={"mapl3": "main"},
        gui_order=[3],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    patch_size: MiraclObj = MiraclObj(
        name="mgp_patch_size",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="p",
        cli_l_flag="patch_size",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_p",
                "cli_l_flag": "mgp_patch_size",
                "cli_group": CliGroup.MAPL3_GENERATE_PATCH,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="the outputs will be patch size x patch size x patch size (ZxYxX; default: %(default)s)",
        cli_required=False,
        obj_default=256,
        gui_label=["Patch size"],
        gui_group={"mapl3": "main"},
        gui_order=[4],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    brain_mask_erosion: MiraclObj = MiraclObj(
        name="mgp_brain_mask_erosion_flag",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="e",
        cli_l_flag="brain_mask_erosion_flag",
        flow={
            "mapl3": {
                "cli_s_flag": "mgp_e",
                "cli_l_flag": "mgp_brain_mask_erosion_flag",
                "cli_group": CliGroup.MAPL3_GENERATE_PATCH,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="set if you want to erode the brain mask (default: %(default)s)",
        cli_required=False,
        obj_default=False,
        gui_label=["Erode brain mask"],
        gui_group={"mapl3": "main"},
        gui_order=[5],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )
