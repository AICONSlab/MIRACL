from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)


class InterfaceSubfolders:
    generated_patches_output = MiraclObj(
        id="d0e788f5-6802-4c88-bd52-b31ec432d309",
        name="generated_patches_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="gp_o",
        cli_l_flag="gp_output",
        flow={"mapl3": {"cli_s_flag": "gp_o", "cli_l_flag": "gp_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface generated patches output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    preprocessed_patches_output = MiraclObj(
        id="a7c29fa7-a83a-48da-bc12-b051c5a9925d",
        name="preprocessed_patches_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="pp_o",
        cli_l_flag="pp_output",
        flow={"mapl3": {"cli_s_flag": "pp_o", "cli_l_flag": "pp_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface preprocessed patches output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    inference_output = MiraclObj(
        id="3cfaf9d7-68b7-4e4b-8b74-505079699e94",
        name="inference_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="i_o",
        cli_l_flag="i_output",
        flow={"mapl3": {"cli_s_flag": "i_o", "cli_l_flag": "i_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface inference output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    skeletonization_output = MiraclObj(
        id="dfd537ae-8b17-4463-9702-5904c50e95ba",
        name="skeletonization_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="s_o",
        cli_l_flag="s_output",
        flow={"mapl3": {"cli_s_flag": "s_o", "cli_l_flag": "s_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface skeletonization output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

    patch_stacking_output = MiraclObj(
        id="f68ef3cf-61cd-4337-8975-a09498a5e272",
        name="patch_stacking_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="p_o",
        cli_l_flag="p_output",
        flow={"mapl3": {"cli_s_flag": "p_o", "cli_l_flag": "p_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface patch stacking output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )
