from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
    ArgumentAction,
    WidgetType,
)
from pathlib import Path


class ClarAllen:
    nii_folder = MiraclObj(
        id="c38437cd-7055-4572-8cb0-64ccf53ab755",
        name="nii_folder",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="i",
        cli_l_flag="input",
        flow={
            "ace": {"cli_s_flag": "arca_i", "cli_l_flag": "arca_input"},
            "mapl3": {"cli_s_flag": "mrca_i", "cli_l_flag": "mrca_input"},
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
        id="0a3dc6fa-2f97-4979-ab12-00739784e4d2",
        name="tiff_folder",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="c",
        cli_l_flag="tiff_input",
        flow={
            "ace": {"cli_s_flag": "arca_ti", "cli_l_flag": "arca_tiff_input"},
            "mapl3": {"cli_s_flag": "mrca_ti", "cli_l_flag": "mrca_tiff_input"},
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
        id="original clarity tiff folder (stack) - folder used as input to convert from tiff to nii",
        name="output",
        tags=["clar_allen", "reg", "ace_flow", "mapl3_flow"],
        cli_s_flag="r",
        cli_l_flag="output",
        flow={
            "ace": {"cli_s_flag": "arca_r", "cli_l_flag": "arca_output"},
            "mapl3": {"cli_s_flag": "mrca_r", "cli_l_flag": "mrca_output"},
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
        id="b0ae9b32-a66f-4eba-a39b-c238b752fb51",
        name="rca_orient_code",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="o",
        cli_l_flag="orient_code",
        flow={
            "ace": {"cli_s_flag": "arca_o", "cli_l_flag": "arca_orient_code"},
            "mapl3": {"cli_s_flag": "mrca_o", "cli_l_flag": "mrca_orient_code"},
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
        id="3894569b-1935-49fe-b9e0-e518b0bbd661",
        name="rca_voxel_size",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="v",
        cli_l_flag="voxel_size",
        flow={
            "ace": {"cli_s_flag": "arca_v", "cli_l_flag": "arca_voxel_size"},
            "mapl3": {"cli_s_flag": "mrca_v", "cli_l_flag": "mrca_voxel_size"},
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
        id="867580eb-ea69-426b-97ae-82b52d8d730d",
        name="rca_hemi",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="m",
        cli_l_flag="hemi",
        flow={
            "ace": {"cli_s_flag": "arca_m", "cli_l_flag": "arca_hemi"},
            "mapl3": {"cli_s_flag": "mrca_m", "cli_l_flag": "mrca_hemi"},
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
        id="496d1355-fd08-4ab5-9aaf-ee2cc8d122d0",
        name="rca_allen_label",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="l",
        cli_l_flag="allen_label",
        flow={
            "ace": {"cli_s_flag": "arca_l", "cli_l_flag": "arca_allen_label"},
            "mapl3": {"cli_s_flag": "mrca_l", "cli_l_flag": "mrca_allen_label"},
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
        id="3ea0859d-2cb9-4304-bfa6-0dab29207a74",
        name="rca_allen_atlas",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="a",
        cli_l_flag="allen_atlas",
        flow={
            "ace": {"cli_s_flag": "arca_a", "cli_l_flag": "arca_allen_atlas"},
            "mapl3": {"cli_s_flag": "mrca_a", "cli_l_flag": "mrca_allen_atlas"},
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
        id="e3719c74-0b5a-4bdf-a336-d533a1faf7ec",
        name="rca_side",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="s",
        cli_l_flag="side",
        flow={
            "ace": {"cli_s_flag": "arca_s", "cli_l_flag": "arca_side"},
            "mapl3": {"cli_s_flag": "mrca_s", "cli_l_flag": "mrca_side"},
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
        id="0c3b2cac-4cb3-4b32-86fb-b1a64a49452a",
        name="rca_no_mosaic_fig",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="f",
        cli_l_flag="no_mosaic_fig",
        flow={
            "ace": {"cli_s_flag": "arcan_m", "cli_l_flag": "arca_no_mosaic_fig"},
            "mapl3": {"cli_s_flag": "mrcan_m", "cli_l_flag": "mrca_no_mosaic_fig"},
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
        id="dfd47b33-6f66-4a41-b42a-6264bb478f87",
        name="rca_olfactory_bulb",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="b",
        cli_l_flag="olfactory_bulb",
        flow={
            "ace": {"cli_s_flag": "arca_b", "cli_l_flag": "arca_olfactory_bulb"},
            "mapl3": {"cli_s_flag": "mrca_b", "cli_l_flag": "mrca_olfactory_bulb"},
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
        id="a58b7a5a-c253-41cd-87bb-ef3f9b232cb6",
        name="rca_skip_cor",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="p",
        cli_l_flag="skip_cor",
        flow={
            "ace": {"cli_s_flag": "arca_p", "cli_l_flag": "arca_skip_cor"},
            "mapl3": {"cli_s_flag": "mrca_p", "cli_l_flag": "mrca_skip_cor"},
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
        id="faaca013-3a95-4a3e-be24-f85e74841a83",
        name="rca_warp",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="w",
        cli_l_flag="warp",
        flow={
            "ace": {"cli_s_flag": "arca_w", "cli_l_flag": "arca_warp"},
            "mapl3": {"cli_s_flag": "mrca_w", "cli_l_flag": "mrca_warp"},
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
