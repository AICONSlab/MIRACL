from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    WidgetType,
)
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class Skeletonization:
    input_dir: MiraclObj = MiraclObj(
        name="ms_input_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "mapl3": {
                "cli_s_flag": "ms",
                "cli_l_flag": "ms_input",
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

    brain_mask: MiraclObj = MiraclObj(
        name="ms_brain_mask",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="m",
        cli_l_flag="brain_mask",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_m",
                "cli_l_flag": "ms_brain_mask",
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

    threshold: MiraclObj = MiraclObj(
        name="ms_threshold",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="t",
        cli_l_flag="threshold",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_t",
                "cli_l_flag": "ms_threshold",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="threshold for skipping analysis based on the number of forground in mask (default: %(default)s)",
        cli_required=False,
        obj_default=1000,
        gui_label=["Skipping analysis thr"],
        gui_group={"mapl3": "main"},
        gui_order=[2],
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.PATH_INPUT,
    )

    num_erosion: MiraclObj = MiraclObj(
        name="ms_num_erosion",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ne",
        cli_l_flag="num_erosion",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_ne",
                "cli_l_flag": "ms_num_erosion",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
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

    out_dir: MiraclObj = MiraclObj(
        name="ms_out_dir",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="out_dir",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_o",
                "cli_l_flag": "ms_out_dir",
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

    remove_small_obj_thr: MiraclObj = MiraclObj(
        name="ms_remove_small_obj_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ts",
        cli_l_flag="remove_small_obj_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_r",
                "cli_l_flag": "ms_remove_small_obj_thr",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="thr (number of voxels) for removing small object (default: %(default)s)",
        cli_required=False,
        obj_default=64,
        gui_label=["Remove small obj thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    remove_large_obj_thr: MiraclObj = MiraclObj(
        name="ms_remove_large_obj_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="tl",
        cli_l_flag="remove_large_obj_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_tl",
                "cli_l_flag": "ms_remove_large_obj_thr",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="thr (number of voxels) for removing large object (default: %(default)s)",
        cli_required=False,
        obj_default=50_000,
        gui_label=["Remove large obj thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    elongation_thr: MiraclObj = MiraclObj(
        name="ms_elongation_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="e",
        cli_l_flag="elongation_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_e",
                "cli_l_flag": "ms_elongation_thr",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="elongation threshold of an object (number of voxels) for removing large object (default: %(default)s)",
        cli_required=False,
        obj_default=5,
        gui_label=["Elongation thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    euler_number_thr: MiraclObj = MiraclObj(
        name="ms_euler_number_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="eu",
        cli_l_flag="euler_number_thr",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_eu",
                "cli_l_flag": "ms_euler_number_thr",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="number of holes allowed an object has (default: %(default)s)",
        cli_required=False,
        obj_default=100,
        gui_label=["Euler number thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    cpu_load: MiraclObj = MiraclObj(
        name="ms_cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="cpu_load",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_c",
                "cli_l_flag": "ms_cpu_load",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="fraction of cpus to be used for parallelization. Value needs to be between 0-1 (default: %(default)s)",
        cli_required=False,
        obj_default=0.7,
        gui_label=["CPU load"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    dilate_distance_transform_flag: MiraclObj = MiraclObj(
        name="dilate_distance_transform_flag",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="d",
        cli_l_flag="dilate_distance_transform_flag",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_d",
                "cli_l_flag": "ms_dilate_distance_transform_flag",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
            }
        },
        cli_obj_type=ArgumentType.BOOLEAN,
        cli_help="whether to dilate distance transform (default: %(default)s)",
        cli_required=False,
        obj_default=True,
        gui_label=["Dilate distance transform"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    tiff_folder: MiraclObj = MiraclObj(
        name="ms_raw_data",
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

    alpha: MiraclObj = MiraclObj(
        name="ms_alpha",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="a",
        cli_l_flag="alpha",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_a",
                "cli_l_flag": "ms_alpha",
                "cli_group": CliGroup.MAPL3_SKELETONIZATION,
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
