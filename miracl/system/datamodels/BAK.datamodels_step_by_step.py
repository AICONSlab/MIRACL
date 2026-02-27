from miracl.api.enums import ModuleType, ArgumentType, CliGroup
from datamodels_miraclobj import MiraclObj, FlowOverride
from datamodel_miracl_objs_refactored import MiraclObj, FlowOverride


control_input_dir: MiraclObj = MiraclObj(
    name="tfce_control_input_dir",
    tags=["mapl3", "seg", "mapl3_flow", "ace", "ace_flow"],
    cli_s_flag="c",
    cli_l_flag="ctrl_input_dir",
    flow={
        "ace": FlowOverride(
            cli_s_flag="tfce_c",
            cli_l_flag="tfce_ctrl_input_dir",
            cli_group=CliGroup.STATS_TFCE,
            disabled=True,
        ),
        "mapl3": FlowOverride(
            cli_s_flag="tfce_c",
            cli_l_flag="tfce_ctrl_input_dir",
            cli_group=CliGroup.STATS_TFCE,
            disabled=True,
        ),
    },
    cli_obj_type=ArgumentType.STRING,
    cli_help="control group input directory (default: None)",
    cli_required=True,
    gui_label=["Ctrl input directory"],
    module="tfce",
    module_group="stats",
    version_added="2.4.0",
)

print(
    f"THIS IS THE FULL OBJECT:\n{control_input_dir}\nTHIS IS THE TYPE: {type(control_input_dir.resolve(ModuleType.MODULE))}"
)
print(
    f"THIS IS THE RESOLVED OBJECT MODULE:\n{control_input_dir.resolve(ModuleType.MODULE)}\nTHIS IS THE TYPE: {type(control_input_dir.resolve(ModuleType.MODULE))}"
)
print(
    f"THIS IS THE RESOLVED OBJECT FLOW_MAPL3:\n{control_input_dir.resolve(ModuleType.FLOW_MAPL3)}\nTHIS IS THE TYPE: {type(control_input_dir.resolve(ModuleType.FLOW_MAPL3))}"
)
