from miracl_datamodel import MiraclObj, ArgumentType, ArgumentAction


class RegClarAllenObjs:
    orient_code = MiraclObj(
        id="b0ae9b32-a66f-4eba-a39b-c238b752fb51",
        name="rca_orient_code",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="rcao",
        cli_l_flag="rca_orient_code",
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
        cli_s_flag="rcav",
        cli_l_flag="rca_voxel_size",
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
    )

    hemi = MiraclObj(
        id="867580eb-ea69-426b-97ae-82b52d8d730d",
        name="rca_hemi",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="rcam",
        cli_l_flag="rca_hemi",
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
        cli_s_flag="rcal",
        cli_l_flag="rca_allen_label",
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
        cli_s_flag="rcaa",
        cli_l_flag="rca_allen_atlas",
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
        cli_s_flag="rcas",
        cli_l_flag="rca_side",
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
        cli_s_flag="rcanm",
        cli_l_flag="rca_no_mosaic_fig",
        cli_help="by default a mosaic figure (.png) of allen labels registered to clarity will be saved. If this flag is set, the mosaic figure will not be saved.",
        gui_group={"ace_flow": "registration"},
        gui_label=["Create mosaic figure"],
        version_added="2.4.0",
        cli_metavar="",
        cli_action=ArgumentAction.STORE_CONST,
        cli_const=0,
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
        cli_s_flag="rcab",
        cli_l_flag="rca_olfactory_bulb",
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
        cli_s_flag="rcap",
        cli_l_flag="rca_skip_cor",
        cli_help="if utilfn intensity correction already ran, skip correction inside registration. '1' means skip (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Utilfn intensity correction"],
        gui_choice_override={
            "vals": ["run", "skip"],
            "default_val": "run",
        },
        module="clar_allen",
        module_group="reg",
        version_added="2.4.0",
        obj_default=0,
        cli_action=ArgumentAction.STORE_CONST,
        cli_const=1,
    )

    warp = MiraclObj(
        id="faaca013-3a95-4a3e-be24-f85e74841a83",
        name="rca_warp",
        tags=["clar_allen", "reg", "ace_flow"],
        cli_s_flag="rcaw",
        cli_l_flag="rca_warp",
        cli_help="warp high-res clarity to Allen space. '0' means do not warp (default: %(default)s)",
        gui_group={"ace_flow": "registration"},
        gui_label=["Warp CLARITY to Allen"],
        module="clar_allen",
        module_group="reg",
        obj_default=0,
        cli_action=ArgumentAction.STORE_CONST,
        cli_const=1,
        gui_choice_override={
            "vals": ["yes", "no"],
            "default_val": "no",
        },
        version_added="2.4.0",
    )


class RegWarpClarObjs:
    voxel_size = MiraclObj(
        id="7f3b5f21-7b07-4c6c-88d3-258c6289c12f",
        name="rwc_voxel_size",
        tags=["warp_clar", "reg", "ace_flow"],
        cli_s_flag="rwcv",
        cli_l_flag="rwc_voxel_size",
        obj_default=25,
        cli_choices=[10, 25, 50],
        cli_obj_type=ArgumentType.INTEGER,
        cli_help="voxel size/Resolution in um for warping (default: %(default)s)",
        gui_label=["Warping voxel size (um)"],
        gui_group={"ace_flow": "main"},
        gui_order=[12],
        module="warp_clar",
        module_group="reg",
        version_added="2.4.0",
    )

    input_folder = MiraclObj(
        id="9bb71e9f-b6de-4c30-a6da-449fe97cd45c",
        name="rwc_input_folder",
        tags=["warp_clar", "reg", "ace_flow"],
        cli_s_flag="rwcr",
        cli_l_flag="rwc_input_folder",
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to CLARITY registration folder",
        gui_group={"ace_flow": "vox_warp"},
        gui_label=["Path to CLARITY reg folder:"],
        module="warp_clar",
        module_group="reg",
        version_added="2.4.0",
        obj_default=None,
    )

    input_nii = MiraclObj(
        id="d0d81ddf-caab-465f-8aed-0bcf7600bfa6",
        name="rwc_input_nii",
        tags=["warp_clar", "reg", "ace_flow"],
        cli_s_flag="rwcn",
        cli_l_flag="rwc_input_nii",
        cli_obj_type=ArgumentType.STRING,
        cli_help="path to downsampled CLARITY nii file to warp",
        gui_group={"ace_flow": "vox_warp"},
        gui_label=["Path to dx CLARITY nii file:"],
        module="warp_clar",
        module_group="reg",
        version_added="2.4.0",
        obj_default=None,
    )

    seg_channel = MiraclObj(
        id="fc35cbe4-947b-4673-989a-f2d95db82c5e",
        name="rwc_seg_channel",
        tags=["warp_clar", "reg", "ace_flow"],
        cli_s_flag="rwcc",
        cli_l_flag="rwc_seg_channel",
        cli_obj_type=ArgumentType.STRING,
        cli_help="Segmentation channel (ex. green) - required if voxelized seg is input",
        gui_group={"ace_flow": "vox_warp"},
        gui_label=["Seg channel (ex: 'green'):"],
        version_added="2.4.0",
        module="warp_clar",
        module_group="reg",
        obj_default="green",
    )
