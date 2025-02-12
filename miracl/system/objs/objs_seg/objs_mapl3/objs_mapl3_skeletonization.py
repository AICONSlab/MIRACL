from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)


class Skeletonization:
    remove_small_obj_thr = MiraclObj(
        id="71ae99ad-b53e-4b3a-932d-72a65fad8065",
        name="remove_small_obj_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ms_r",
        cli_l_flag="ms_remove_small_obj_thr",
        flow={"mapl3": {"cli_s_flag": "ms_r", "cli_l_flag": "ms_remove_small_obj_thr"}},
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="thr (number of voxels) for removing small object (default: %(default)s)",
        cli_required=False,
        obj_default=100,
        gui_label=["Remove small obj thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )

    cpu_load = MiraclObj(
        id="0ec61c67-e2da-4c18-a748-58b8654b1aa9",
        name="cpu_load",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ms_c",
        cli_l_flag="ms_cpu_load",
        flow={"mapl3": {"cli_s_flag": "ms_c", "cli_l_flag": "ms_cpu_load"}},
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

    dilate_distance_transform = MiraclObj(
        id="1696e1da-fd43-4085-9641-4fddf061ba53",
        name="dilate_distance_transform",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ms_d",
        cli_l_flag="ms_dilate_distance_transform",
        flow={
            "mapl3": {
                "cli_s_flag": "ms_d",
                "cli_l_flag": "ms_dilate_distance_transform",
            }
        },
        cli_action=ArgumentAction.STORE_FALSE,
        cli_help="whether to dilate distance transform (default: %(default)s)",
        cli_required=False,
        obj_default=True,
        gui_label=["Dilate distance transform"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    eccentricity_thr = MiraclObj(
        id="6e816656-b1d3-40b3-be78-c212d20834c6",
        name="eccentricity_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ms_e",
        cli_l_flag="ms_eccentricity_thr",
        flow={"mapl3": {"cli_s_flag": "ms_e", "cli_l_flag": "ms_eccentricity_thr"}},
        cli_obj_type=ArgumentType.FLOAT,
        cli_help="thr for removing small object based on eccentricity. Value between 0-1 with circles having an eccentricity of 0 (default: %(default)s)",
        cli_required=False,
        obj_default=0.5,
        gui_label=["Eccentritcity thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DOUBLE_SPINBOX,
    )

    orientation_thr = MiraclObj(
        id="276a366b-e5fe-420d-adec-4dbf80b7b96f",
        name="orientation_thr",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="ms_o",
        cli_l_flag="ms_orientation_thr",
        flow={"mapl3": {"cli_s_flag": "ms_o", "cli_l_flag": "ms_orientation_thr"}},
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="thr for removing small object based on orientation in degrees (default: %(default)s)",
        cli_required=False,
        obj_default=70,
        gui_label=["Remove small obj thr"],
        gui_group={"mapl3": "main"},
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.SPINBOX,
    )


# my_parser.add_argument('-i','--input', help='input tif/tiff probability map', required=True)
# my_parser.add_argument('-o','--out_dir', help='path of output directory', required=True)
