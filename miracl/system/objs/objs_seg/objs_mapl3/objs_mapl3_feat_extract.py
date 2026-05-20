from miracl.system.enums.enums_base_modules import CliGroup
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    FlowOverride,
    ArgumentSource,
    ArgumentType,
    WidgetType,
)


class FeatExtract:
    _MFE_GROUP = CliGroup.MAPL3_FEAT_EXTRACT

    seg: MiraclObj = MiraclObj(
        name="mfe_seg",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="seg",
            obj_type=ArgumentType.STRING,
            help="segmentation tif (default: %(default)s)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Segmentation tif"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mfe_s",
                    l_flag="mfe_seg",
                    group=_MFE_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    lbl: MiraclObj = MiraclObj(
        name="mfe_lbl",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="l",
            l_flag="lbl",
            obj_type=ArgumentType.STRING,
            help="label annotation (default: %(default)s)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Label annotation"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mfe_l",
                    l_flag="mfe_lbl",
                    group=_MFE_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    mask: MiraclObj = MiraclObj(
        name="mfe_mask",
        module="mapl3",
        module_group="seg",
        version_added="2.4.0",
        tags=["mapl3", "seg", "mapl3_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="mask",
            obj_type=ArgumentType.STRING,
            help="ROI mask (default: %(default)s)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["ROI mask"],
                widget_type=WidgetType.PATH_INPUT,
                order=2.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mfe_m",
                    l_flag="mfe_mask",
                    group=_MFE_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
