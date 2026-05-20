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


class WarpClarAllen:
    _MRWCA_GROUP = CliGroup.MAPL3_WARP_CLAR_ALLEN

    reg_dir: MiraclObj = MiraclObj(
        name="rwca_regdir",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="regdir",
            obj_type=ArgumentType.STRING,
            help="Input clarity registration dir (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Input clarity registration dir"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrwca_r",
                    l_flag="mrwca_regdir",
                    group=CliGroup.MAPL3_WARP_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    nii_folder: MiraclObj = MiraclObj(
        name="rwca_nii_folder",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="inimg",
            obj_type=ArgumentType.STRING,
            help="Input downsampled CLARITY nii to warp (default: None)",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Nii input folder"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrwca_i",
                    l_flag="mrwca_inimg",
                    group=CliGroup.MAPL3_WARP_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    ort2std_file: MiraclObj = MiraclObj(
        name="rwca_ort2std_file",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="ort2std_file",
            obj_type=ArgumentType.STRING,
            help="File with orientation to standard code (default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Orientation code file"],
                widget_type=WidgetType.PATH_INPUT,
                order=9.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrwca_o",
                    l_flag="mrwca_ort2std_file",
                    group=CliGroup.MAPL3_WARP_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    seg_channel: MiraclObj = MiraclObj(
        name="rwca_seg_channel",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="seg_channel",
            obj_type=ArgumentType.STRING,
            help="Segmentation channel (ex. 'green') - required if voxelization is input (default: None)",
            required=False,
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Seg channel"],
                widget_type=WidgetType.LINE_EDIT,
                order=9.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrwca_s",
                    l_flag="mrwca_seg_channel",
                    group=CliGroup.MAPL3_WARP_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    vox_res: MiraclObj = MiraclObj(
        name="rwca_vox_res",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="v",
            l_flag="vox_res",
            obj_type=ArgumentType.INTEGER,
            help="Voxel resolution (10 or 25; default: %(default)s)",
            required=False,
            default=25,
            choices=[10, 25],
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Voxel resolution"],
                widget_type=WidgetType.COMBO_BOX,
                order=9.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrwca_v",
                    l_flag="mrwca_vox_res",
                    group=_MRWCA_GROUP,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    allen_lbls: MiraclObj = MiraclObj(
        name="rwca_allen_lbls",
        module="warp_clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="l",
            l_flag="allen_lbls",
            obj_type=ArgumentType.STRING,
            help="input Allen labels to warp (default: %(default)s)",
            required=False,
            default="None",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Allen labels"],
                widget_type=WidgetType.PATH_INPUT,
                order=9.0,
            )
        ),
        flow={
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrwca_l",
                    l_flag="mrwca_allen_lbls",
                    group=CliGroup.MAPL3_WARP_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
