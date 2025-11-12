from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)
from pathlib import Path
from miracl.system.enums.enums_base_modules import (
    CliGroup,
)


class ClarAllen:
    nii_folder = MiraclObj(
        name="rca_nii_folder",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "ace": {
                "cli_s_flag": "arca_i",
                "cli_l_flag": "arca_input",
                "cli_group": CliGroup.REQUIRED,
                "required": True,
            },
            "mapl3": {
                "cli_s_flag": "mrca_i",
                "cli_l_flag": "mrca_input",
                "cli_group": CliGroup.REQUIRED,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input down-sampled clarity nii. Preferably auto-fluorescence channel data (or Thy1_EYFP if no auto chan). file name should have '##x_down' like '05x_down' (meaning 5x downsampled)  -> ex. stroke13_05x_down_Ref_chan.nii.gz",
        obj_default=None,
        cli_required=True,
        gui_label=["Nii input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    tiff_folder = MiraclObj(
        name="rca_tiff_folder",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="tiff_input",
        flow={
            "ace": {
                "cli_s_flag": "arca_ti",
                "cli_l_flag": "arca_tiff_input",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_ti",
                "cli_l_flag": "mrca_tiff_input",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="original clarity tiff folder (stack) - folder used as input to convert from tiff to nii",
        obj_default=None,
        cli_required=True,
        gui_label=["tiff input folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    output_path = MiraclObj(
        name="rca_output",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="r",
        cli_l_flag="output",
        flow={
            "ace": {
                "cli_s_flag": "arca_r",
                "cli_l_flag": "arca_output",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_r",
                "cli_l_flag": "mrca_output",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
                "disabled": True,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="output (results) directory (default: %(default)s)",
        obj_default=Path.cwd(),
        gui_label=["Output path/folder"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    orient_code = MiraclObj(
        name="rca_orient_code",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="o",
        cli_l_flag="orient_code",
        flow={
            "ace": {
                "cli_s_flag": "arca_o",
                "cli_l_flag": "arca_orient_code",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_o",
                "cli_l_flag": "mrca_orient_code",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="to orient nifti from original orientation to 'standard/Allen' orientation, (default: %(default)s)",
        obj_default="ALS",
        gui_label=["Orientation code"],
        gui_group={"ace_flow": "main"},
        gui_order=[9],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    voxel_size = MiraclObj(
        name="rca_voxel_size",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="v",
        cli_l_flag="voxel_size",
        flow={
            "ace": {
                "cli_s_flag": "arca_v",
                "cli_l_flag": "arca_voxel_size",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_v",
                "cli_l_flag": "mrca_voxel_size",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        obj_default=10,
        cli_choices=[10, 25, 50],
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="labels voxel size/Resolution in um (default: %(default)s)",
        gui_label=["Labels voxel size (um)"],
        gui_group={"ace_flow": "main"},
        gui_order=[10],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        gui_widget_type=WidgetType.DROPDOWN,
    )

    hemi = MiraclObj(
        name="rca_hemi",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="m",
        cli_l_flag="hemi",
        flow={
            "ace": {
                "cli_s_flag": "arca_m",
                "cli_l_flag": "arca_hemi",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_m",
                "cli_l_flag": "mrca_hemi",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Labels hemisphere"],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        cli_choices=["combined", "split"],
        obj_default="combined",
    )

    allen_label = MiraclObj(
        name="rca_allen_label",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="l",
        cli_l_flag="allen_label",
        flow={
            "ace": {
                "cli_s_flag": "arca_l",
                "cli_l_flag": "arca_allen_label",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_l",
                "cli_l_flag": "mrca_allen_label",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="input Allen labels to warp. Input labels could be at a different depth than default labels, If l. is specified (m & v cannot be specified) (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Allen labels to warp"],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        obj_default=None,
    )

    allen_atlas = MiraclObj(
        name="rca_allen_atlas",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="a",
        cli_l_flag="allen_atlas",
        flow={
            "ace": {
                "cli_s_flag": "arca_a",
                "cli_l_flag": "arca_allen_atlas",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_a",
                "cli_l_flag": "mrca_allen_atlas",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="custom Allen atlas (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Custom Allen atlas"],
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        obj_default="None",
    )

    side = MiraclObj(
        name="rca_side",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="s",
        cli_l_flag="side",
        flow={
            "ace": {
                "cli_s_flag": "arca_s",
                "cli_l_flag": "arca_side",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_s",
                "cli_l_flag": "mrca_side",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Side"],
        version_added="2.4.0",
        cli_choices=["rh", "lh"],
        obj_default="rh",
        gui_choice_override={
            "vals": ["right hemisphere", "left hemisphere"],
            "default_val": "right hemisphere",
        },
        module="clar_allen",
        module_group="reg",
    )

    no_mosaic_fig = MiraclObj(
        name="rca_no_mosaic_fig",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="f",
        cli_l_flag="no_mosaic_fig",
        flow={
            "ace": {
                "cli_s_flag": "arcan_m",
                "cli_l_flag": "arca_no_mosaic_fig",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrcan_m",
                "cli_l_flag": "mrca_no_mosaic_fig",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_help="set to '1' to save mosaic figure (.png) of allen labels registered to clarity. Set to '0' to not save the mosaic figure (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Create mosaic figure"],
        version_added="2.4.0",
        cli_metavar="",
        cli_obj_type=ArgumentType.INTEGER,
        cli_choices=[0, 1],
        obj_default=1,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "yes",
        },
        module="clar_allen",
        module_group="reg",
    )

    olfactory_bulb = MiraclObj(
        name="rca_olfactory_bulb",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="b",
        cli_l_flag="olfactory_bulb",
        flow={
            "ace": {
                "cli_s_flag": "arca_b",
                "cli_l_flag": "arca_olfactory_bulb",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_b",
                "cli_l_flag": "mrca_olfactory_bulb",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="include olfactory bulb in brain. '0' means no (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Olfactory bulb incl."],
        gui_choice_override={
            "vals": ["not included", "included"],
            "default_val": "not included",
        },
        version_added="2.4.0",
        cli_choices=[0, 1],
        module="clar_allen",
        module_group="reg",
        obj_default=0,
    )

    skip_cor = MiraclObj(
        name="rca_skip_cor",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="p",
        cli_l_flag="skip_cor",
        flow={
            "ace": {
                "cli_s_flag": "arca_p",
                "cli_l_flag": "arca_skip_cor",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_p",
                "cli_l_flag": "mrca_skip_cor",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_help="if utilfn intensity correction already ran, skip correction inside registration. '0' means don't skip, '1' means skip (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Utilfn intensity correction"],
        gui_choice_override={
            "vals": ["run", "skip"],
            "default_val": "run",
        },
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        cli_choices=[0, 1],
        obj_default=0,
        cli_obj_type=ArgumentType.INTEGER,
    )

    warp = MiraclObj(
        name="rca_warp",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="w",
        cli_l_flag="warp",
        flow={
            "ace": {
                "cli_s_flag": "arca_w",
                "cli_l_flag": "arca_warp",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_w",
                "cli_l_flag": "mrca_warp",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_help="warp high-res clarity to Allen space. '0' means do not warp, '1' means warp (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Warp CLARITY to Allen"],
        module="clar_allen",
        module_group="reg",
        obj_default=0,
        cli_choices=[0, 1],
        cli_obj_type=ArgumentType.INTEGER,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
        version_added="2.4.0",
    )

    chan_num: MiraclObj = MiraclObj(
        name="rca_chan_num",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="n",
        cli_l_flag="chan_num",
        flow={
            "ace": {
                "cli_s_flag": "arca_i",
                "cli_l_flag": "arca_input",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
                "required": True,
            },
            "mapl3": {
                "cli_s_flag": "mrca_n",
                "cli_l_flag": "mrca_chan_num",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="chan # for extracting single channel from multiple channel data (default: -999999)",
        obj_default="-999999",
        gui_label=["Channel #"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )

    chan_prefix: MiraclObj = MiraclObj(
        name="rca_chan_prefix",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="x",
        cli_l_flag="chan_prefix",
        flow={
            "ace": {
                "cli_s_flag": "arca_i",
                "cli_l_flag": "arca_input",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
            "mapl3": {
                "cli_s_flag": "mrca_x",
                "cli_l_flag": "mrca_chan_prefix",
                "cli_group": CliGroup.REG_CLAR_ALLEN,
            },
        },
        cli_obj_type=ArgumentType.STRING,
        cli_help="chan prefix (string before channel number in file name). ex: C00 (default: -999999)",
        obj_default="-999999",
        gui_label=["Channel prefix"],
        gui_group={"ace_flow": "main", "mapl3:": "main"},
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
    )
