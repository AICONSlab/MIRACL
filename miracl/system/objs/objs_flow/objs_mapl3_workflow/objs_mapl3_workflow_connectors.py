from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)
from miracl.system.enums.enums_base_modules import CliGroup


# class WorkflowInterfaceSubfolders:
class MAPL3_connectors:
    # mapl3_workflow_reg_folder: MiraclObj = MiraclObj(
    #     id="e9d4d091-b3fb-4307-abab-02737f900003",
    #     name="mapl3_workflow_reg_folder",
    #     tags=["mapl3", "flow", "mapl3_flow"],
    #     cli_s_flag="mw_ro",
    #     cli_l_flag="mw_reg_output",
    #     flow={
    #         "mapl3": {
    #             "cli_s_flag": "mw_ro",
    #             "cli_l_flag": "mw_reg_output",
    #             "disabled": True,
    #         }
    #     },
    #     cli_obj_type=ArgumentType.STRING,
    #     cli_help="Folder object for workflow interface reg output subfolder",
    #     module="mapl3",
    #     module_group="flow",
    #     version_added="2.4.0",
    # )
    #
    # mapl3_workflow_conv_folder: MiraclObj = MiraclObj(
    #     id="119fa9cd-f61a-4220-a945-2cea704cb9d0",
    #     name="mapl3_workflow_conv_folder",
    #     tags=["mapl3", "flow", "mapl3_flow"],
    #     cli_s_flag="mw_co",
    #     cli_l_flag="mw_conv_output",
    #     flow={
    #         "mapl3": {
    #             "cli_s_flag": "mw_co",
    #             "cli_l_flag": "mw_conv_output",
    #             "disabled": True,
    #         }
    #     },
    #     cli_obj_type=ArgumentType.STRING,
    #     cli_help="Folder object for workflow interface conv output subfolder",
    #     module="mapl3",
    #     module_group="flow",
    #     version_added="2.4.0",
    # )

    mapl3_workflow_raw_autoflor_tiff_folder: MiraclObj = MiraclObj(
        name="mapl3_workflow_raw_autoflor_tiff_folder",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="mwfc_ratf",
        cli_l_flag="mwfc_raw_autoflor_tiff_folder",
        flow={
            "mapl3": {
                "cli_s_flag": "mwfc_ratf",
                "cli_l_flag": "mwfc_raw_autoflor_tiff_folder",
                "required": True,
                "cli_group": CliGroup.REQUIRED,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="RAW Tiff folder object i.e. path to the folder with autoflor Tiffs in it",
        obj_default=None,
        cli_required=True,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    mapl3_workflow_raw_signal_tiff_folder: MiraclObj = MiraclObj(
        name="mapl3_workflow_raw_signal_tiff_folder",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="mwfc_rstf",
        cli_l_flag="mwfc_raw_signal_tiff_folder",
        flow={
            "mapl3": {
                "cli_s_flag": "mwfc_rstf",
                "cli_l_flag": "mwfc_raw_signal_tiff_folder",
                "required": True,
                "cli_group": CliGroup.REQUIRED,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="RAW Tiff folder object i.e. path to the folder with signal Tiffs in it",
        obj_default=None,
        cli_required=True,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    mapl3_workflow_results_folder: MiraclObj = MiraclObj(
        name="mapl3_workflow_results_folder",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="mwfc_crf",
        cli_l_flag="mwfc_conv_results_folder",
        flow={
            "mapl3": {
                "cli_s_flag": "mwfc_cof",
                "cli_l_flag": "mwfc_results_folder",
                "required": True,
                "cli_group": CliGroup.REQUIRED,
            }
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="Path to MAPL3 workflow results folder",
        obj_default=None,
        cli_required=True,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    mapl3_workflow_clusterwise_analysis: MiraclObj = MiraclObj(
        name="mapl3_workflow_clusterwise_analysis",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="mwfc_cwa",
        cli_l_flag="mwfc_clusterwise_analysis",
        flow={
            "mapl3": {
                "cli_s_flag": "mwfc_cwa",
                "cli_l_flag": "mwfc_clusterwise_analysis",
                "required": False,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="Run clusterwise analysis",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )
