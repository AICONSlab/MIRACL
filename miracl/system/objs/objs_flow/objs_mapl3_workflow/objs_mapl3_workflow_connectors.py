from miracl.system.datamodels.miraclobj_enums import WidgetType
from miracl.system.enums.enums_base_modules import CliGroup

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
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
    results_folder = MiraclObj(
        name="workflow_results_folder",
        module="mapl3",
        module_group="workflow_connectors",
        version_added="2.4.0",
        tags=["mapl3_flow", "workflow_connectors"],
        cli=CLISpec(
            s_flag="r",
            l_flag="results_folder",
            obj_type=ArgumentType.STRING,
            help="Results folder for the workflow",
            required=True,
            group=CliGroup.REQUIRED,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Workflow results folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.REQUIRED,
            )
        ),
    )

    tiff_folder = MiraclObj(
        name="workflow_tiff_folder",
        module="mapl3",
        module_group="workflow_connectors",
        version_added="2.4.0",
        tags=["mapl3_flow", "workflow_connectors"],
        cli=CLISpec(
            s_flag="t",
            l_flag="tiff_folder",
            obj_type=ArgumentType.STRING,
            help="Raw tiff folder for the workflow",
            required=True,
            group=CliGroup.REQUIRED,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Workflow raw tiff folder"],
                widget_type=WidgetType.PATH_INPUT,
                group=CliGroup.REQUIRED,
            )
        ),
    )
