from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)


class InterfaceFolder:
    output = MiraclObj(
        id="7e1be7ab-fc3e-499b-88a2-a2828acfc521",
        name="output",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli_s_flag="o",
        cli_l_flag="output",
        flow={"mapl3": {"cli_s_flag": "mo", "cli_l_flag": "m_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Generic folder object for interface",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
    )
