from pathlib import Path
from tkinter import Widget
from miracl.system.enums.enums_base_modules import CliGroup

# from miracl.system.datamodels.datamodel_miracl_objs_refactored import (
from miracl.system.datamodels.miraclobj_datamodel import (
    MiraclObj,
    CLISpec,
    CLIDelta,
    GuiNamespace,
    GuiBase,
    GuiDelta,
    GuiWidgetSpecifics,
    RangeFormConfig,
    LineEditConfig,
    GuiChoiceOverrideConfig,
    FlowOverride,
    ArgumentType,
    WidgetType,
    InputRestrictionType,
    ArgumentSource,
)


class ClarAllen:
    nii_folder = MiraclObj(
        name="rca_nii_folder",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="i",
            l_flag="input",
            obj_type=ArgumentType.STRING,
            help="input down-sampled clarity nii. Preferably auto-fluorescence channel data (or Thy1_EYFP if no auto chan). file name should have '##x_down' like '05x_down' (meaning 5x downsampled)  -> ex. stroke13_05x_down_Ref_chan.nii.gz",
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
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_i",
                    l_flag="arca_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                    required=True,
                ),
                gui=GuiDelta(
                    base=GuiBase(),
                ),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrca_i",
                    l_flag="mrca_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(
                    base=GuiBase(),
                ),
            ),
            "conv_reg": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="rrca_i",
                    l_flag="rrca_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(
                    base=GuiBase(),
                ),
            ),
        },
    )

    tiff_folder = MiraclObj(
        name="rca_tiff_folder",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="c",
            l_flag="tiff_input",
            obj_type=ArgumentType.STRING,
            help="original clarity tiff folder (stack) - folder used as input to convert from tiff to nii",
            required=True,
            default=None,
        ),
        gui=GuiNamespace(base=GuiBase(label=["tiff input folder"])),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_ti",
                    l_flag="arca_tiff_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrca_ti",
                    l_flag="mrca_tiff_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "conv_reg": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="rrca_ti",
                    l_flag="rrca_tiff_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    output_path = MiraclObj(
        name="rca_output",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="r",
            l_flag="output",
            obj_type=ArgumentType.STRING,
            help="output (results) directory (default: %(default)s)",
            default=Path.cwd(),
        ),
        gui=GuiNamespace(base=GuiBase(label=["Output path/folder"])),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_r",
                    l_flag="arca_output",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="mrca_r",
                    l_flag="mrca_output",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "conv_reg": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="rrca_r",
                    l_flag="rrca_output",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    orient_code = MiraclObj(
        name="rca_orient_code",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="o",
            l_flag="orient_code",
            obj_type=ArgumentType.STRING,
            help="to orient nifti from original orientation to 'standard/Allen' orientation, (default: %(default)s)",
            default="ALS",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Orientation code"],
                order=9.0,
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_o",
                    l_flag="arca_orient_code",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_o",
                    l_flag="mrca_orient_code",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_o",
                    l_flag="rrca_orient_code",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    voxel_size = MiraclObj(
        name="rca_voxel_size",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="v",
            l_flag="voxel_size",
            obj_type=ArgumentType.INTEGER,
            help="labels voxel size/Resolution in um (default: %(default)s)",
            choices=[10, 25, 50],
            default=10,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Labels voxel size (um)"],
                widget_type=WidgetType.COMBO_BOX,
                order=10.0,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_v",
                    l_flag="arca_voxel_size",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_v",
                    l_flag="mrca_voxel_size",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_v",
                    l_flag="rrca_voxel_size",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    hemi = MiraclObj(
        name="rca_hemi",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="m",
            l_flag="hemi",
            obj_type=ArgumentType.STRING,
            help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
            choices=["combined", "split"],
            default="combined",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Labels hemisphere"],
                widget_type=WidgetType.COMBO_BOX,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_m",
                    l_flag="arca_hemi",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_m",
                    l_flag="mrca_hemi",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_m",
                    l_flag="rrca_hemi",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    allen_label = MiraclObj(
        name="rca_allen_label",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="l",
            l_flag="allen_label",
            obj_type=ArgumentType.STRING,
            help="input Allen labels to warp. Input labels could be at a different depth than default labels, If l. is specified (m & v cannot be specified) (default: %(default)s)",
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Allen labels to warp"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_l",
                    l_flag="arca_allen_label",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_l",
                    l_flag="mrca_allen_label",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_l",
                    l_flag="rrca_allen_label",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    allen_atlas = MiraclObj(
        name="rca_allen_atlas",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="a",
            l_flag="allen_atlas",
            obj_type=ArgumentType.STRING,
            help="custom Allen atlas (default: %(default)s)",
            default=None,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Custom Allen atlas"],
                widget_type=WidgetType.PATH_INPUT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_a",
                    l_flag="arca_allen_atlas",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_a",
                    l_flag="mrca_allen_atlas",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_a",
                    l_flag="rrca_allen_atlas",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    side = MiraclObj(
        name="rca_side",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="s",
            l_flag="side",
            obj_type=ArgumentType.STRING,
            help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
            choices=["rh", "lh"],
            default="rh",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Side"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["right hemisphere", "left hemisphere"],
                        default_val="right hemisphere",
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_s",
                    l_flag="arca_side",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_s",
                    l_flag="mrca_side",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_s",
                    l_flag="rrca_side",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    no_mosaic_fig = MiraclObj(
        name="rca_no_mosaic_fig",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="f",
            l_flag="no_mosaic_fig",
            obj_type=ArgumentType.INTEGER,
            help="set to '1' to save mosaic figure (.png) of allen labels registered to clarity. Set to '0' to not save the mosaic figure (default: %(default)s)",
            metavar="",
            choices=[0, 1],
            default=1,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Create mosaic figure"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["yes", "no"], default_val="yes"
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arcan_m",
                    l_flag="arca_no_mosaic_fig",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrcan_m",
                    l_flag="mrca_no_mosaic_fig",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrcan_m",
                    l_flag="rrca_no_mosaic_fig",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    olfactory_bulb = MiraclObj(
        name="rca_olfactory_bulb",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="b",
            l_flag="olfactory_bulb",
            obj_type=ArgumentType.INTEGER,
            help="include olfactory bulb in brain. '0' means 'not included' (default: %(default)s)",
            choices=[0, 1],
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Olfactory bulb incl."],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["not included", "included"], default_val="not included"
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_b",
                    l_flag="arca_olfactory_bulb",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_b",
                    l_flag="mrca_olfactory_bulb",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_b",
                    l_flag="rrca_olfactory_bulb",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    skip_cor = MiraclObj(
        name="rca_skip_cor",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="p",
            l_flag="skip_cor",
            obj_type=ArgumentType.INTEGER,
            help="if utilfn intensity correction already ran, skip correction inside registration. '0' means don't skip, '1' means skip (default: %(default)s)",
            choices=[0, 1],
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Utilfn intensity correction"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["run", "skip"], default_val="run"
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_p",
                    l_flag="arca_skip_cor",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_p",
                    l_flag="mrca_skip_cor",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_p",
                    l_flag="rrca_skip_cor",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    warp = MiraclObj(
        name="rca_warp",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow"],
        cli=CLISpec(
            s_flag="w",
            l_flag="warp",
            obj_type=ArgumentType.INTEGER,
            help="warp high-res clarity to Allen space. '0' means do not warp, '1' means warp (default: %(default)s)",
            choices=[0, 1],
            default=0,
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Warp CLARITY to Allen"],
                widget_type=WidgetType.COMBO_BOX,
                props=GuiWidgetSpecifics(
                    choices=GuiChoiceOverrideConfig(
                        vals=["yes", "no"],
                        default_val="no",
                    )
                ),
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_w",
                    l_flag="arca_warp",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_w",
                    l_flag="mrca_warp",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
            "conv_reg": FlowOverride(
                cli=CLIDelta(
                    s_flag="rrca_w",
                    l_flag="rrca_warp",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
            ),
        },
    )

    chan_num = MiraclObj(
        name="rca_chan_num",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="n",
            l_flag="chan_num",
            obj_type=ArgumentType.STRING,
            help="chan # for extracting single channel from multiple channel data (default: %(default)s)",
            default="-999999",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Channel #"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_i",
                    l_flag="arca_input",
                    group=CliGroup.REG_CLAR_ALLEN,
                    required=True,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_n",
                    l_flag="mrca_chan_num",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "conv_reg": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="rrca_n",
                    l_flag="rrca_chan_num",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )

    chan_prefix = MiraclObj(
        name="rca_chan_prefix",
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli=CLISpec(
            s_flag="x",
            l_flag="chan_prefix",
            obj_type=ArgumentType.STRING,
            help="chan prefix (string before channel number in file name). ex: C00 (default: %(default)s)",
            default="-999999",
        ),
        gui=GuiNamespace(
            base=GuiBase(
                label=["Channel prefix"],
                widget_type=WidgetType.LINE_EDIT,
            )
        ),
        flow={
            "ace": FlowOverride(
                cli=CLIDelta(
                    s_flag="arca_i", l_flag="arca_input", group=CliGroup.REG_CLAR_ALLEN
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "mapl3": FlowOverride(
                cli=CLIDelta(
                    s_flag="mrca_x",
                    l_flag="mrca_chan_prefix",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
            "conv_reg": FlowOverride(
                source=ArgumentSource.INTERNAL,
                cli=CLIDelta(
                    s_flag="rrca_x",
                    l_flag="rrca_chan_prefix",
                    group=CliGroup.REG_CLAR_ALLEN,
                ),
                gui=GuiDelta(base=GuiBase()),
            ),
        },
    )
