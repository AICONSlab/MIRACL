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


class Mapl3WorkflowConnectors:
    mapl3_workflow_raw_autoflor_tiff_folder = MiraclObj(
        name="mapl3_workflow_raw_autoflor_tiff_folder",
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="autoflor_tiff_folder",
            obj_type=ArgumentType.STRING,
            help="RAW Tiff folder object i.e. path to the folder with autoflor Tiffs in it",
            required=True,
            default=None,
            group=CliGroup.REQUIRED,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Raw autoflor TIFF folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.REQUIRED,
            )
        ),
    )

    mapl3_workflow_raw_signal_tiff_folder = MiraclObj(
        name="mapl3_workflow_raw_signal_tiff_folder",
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="signal_tiff_folder",
            obj_type=ArgumentType.STRING,
            help="RAW Tiff folder object i.e. path to the folder with signal Tiffs in it",
            required=True,
            default=None,
            group=CliGroup.REQUIRED,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Raw signal TIFF folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.REQUIRED,
            )
        ),
    )

    mapl3_workflow_results_folder = MiraclObj(
        name="mapl3_workflow_results_folder",
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="results_folder",
            obj_type=ArgumentType.STRING,
            help="Path to MAPL3 workflow results folder",
            required=True,
            default=None,
            group=CliGroup.REQUIRED,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["MAPL3 results folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.REQUIRED,
            )
        ),
    )
