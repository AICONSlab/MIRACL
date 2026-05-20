from miracl.system.datamodels.miraclobj_enums import WidgetType
from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    GuiNamespace,
    GuiBase,
    ArgumentType,
    CliGroup,
    WidgetType,
)


class ConvRegWorkflowConnectors:
    conv_reg_workflow_raw_autoflor_tiff_folder = MiraclObj(
        name="conv_reg_workflow_raw_autoflor_tiff_folder",
        module="conv_reg",
        module_group="flow",
        version_added="2.4.0",
        tags=["conversion", "registrationflow", "conv_reg_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="autoflor_tiff_folder",
            obj_type=ArgumentType.STRING,
            help="RAW Tiff folder object i.e. path to the folder with autoflor Tiffs in it",
            required=True,
            default=None,
            metavar="RAW TIFF FOLDER",
            group=CliGroup.CONV_REG_WORKFLOW_CONNECTORS,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Raw autoflor TIFF folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.CONV_REG_WORKFLOW_CONNECTORS,
            )
        ),
    )

    conv_reg_workflow_results_folder = MiraclObj(
        name="conv_reg_workflow_results_folder",
        module="conv_reg",
        module_group="flow",
        version_added="2.4.0",
        tags=["conversion", "registrationflow", "conv_reg_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="results_folder",
            obj_type=ArgumentType.STRING,
            help="Path to workflow results folder",
            required=True,
            default=None,
            metavar="RESULTS FOLDER",
            group=CliGroup.CONV_REG_WORKFLOW_CONNECTORS,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Results folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.CONV_REG_WORKFLOW_CONNECTORS,
            )
        ),
    )
