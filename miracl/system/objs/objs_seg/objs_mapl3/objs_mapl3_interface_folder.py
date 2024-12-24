from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)


class InterfaceSubfolders:
    seg_output = MiraclObj(
        id="7e1be7ab-fc3e-499b-88a2-a2828acfc521",
        name="seg_output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="seg_o",
        cli_l_flag="seg_output",
        flow={"mapl3": {"cli_s_flag": "seg_o", "cli_l_flag": "seg_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for interface seg output subfolder",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )

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
