from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)


class WorkflowInterfaceSubfolders:
    mapl3_workflow_reg_folder = MiraclObj(
        id="e9d4d091-b3fb-4307-abab-02737f900003",
        name="mapl3_workflow_reg_folder",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="mw_ro",
        cli_l_flag="mw_reg_output",
        flow={"mapl3": {"cli_s_flag": "mw_ro", "cli_l_flag": "mw_reg_output"}},
        cli_obj_type=ArgumentType.STRING,
        cli_help="Folder object for workflow interface reg output subfolder",
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )
