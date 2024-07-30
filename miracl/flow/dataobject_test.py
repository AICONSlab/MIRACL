from miracl_datamodel import MiraclObj, ArgumentType, ArgumentAction
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Dict, Union, cast, Optional
from pydantic import BaseModel


########
# MAIN #
########

# single_multi_args_group
# fa = Flow ACE

fa_single = MiraclObj(
    id="cb307bde-6cbd-46b1-a044-3acd1deeb13b",
    description="Run single group for ACE flow",
    name="fa_single",
    tags=["ace", "flow", "ace_flow"],
    cli_s_flag="s",
    cli_l_flag="single",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to single raw tif/tiff data folder",
    cli_metavar="SINGLE_TIFF_DIR",
    gui_label=["Single tif/tiff data folder"],
    gui_group={"ace_flow": "main"},
    gui_order=[1],
    gui_widget_type="textfield",
    module="ace",
    module_group="flow",
    version_added="2.4.0",
)

fa_control = MiraclObj(
    id="f17b25be-abec-42af-b1c5-4f4ab3e9ffab",
    name="fa_control",
    tags=["ace", "flow", "ace_flow"],
    cli_s_flag="c",
    cli_l_flag="control",
    cli_obj_type=ArgumentType.STRING,
    cli_help="FIRST: path to base control directory.\nSECOND: example path to control subject tiff directory",
    cli_metavar=("CONTROL_BASE_DIR", "CONTROL_TIFF_DIR_EXAMPLE"),
    gui_label=["Base control dir", "Base control tif/tiff dir"],
    gui_group={"ace_flow": "main"},
    gui_order=[2],
    cli_nargs=2,
    module="ace",
    module_group="flow",
    version_added="2.4.0",
)

fa_treated = MiraclObj(
    id="911bdad2-0359-445d-bc7c-a41257ee1a30",
    name="fa_treated",
    tags=["ace", "flow", "ace_flow"],
    cli_s_flag="t",
    cli_l_flag="treated",
    cli_obj_type=ArgumentType.STRING,
    cli_help="FIRST: path to base treated directory.\nSECOND: example path to treated subject tiff directory",
    cli_metavar=("TREATED_BASE_DIR", "TREATED_TIFF_DIR_EXAMPLE"),
    gui_label=["Base treated dir", "Base treated tif/tiff dir"],
    gui_group={"ace_flow": "main"},
    gui_order=[3.1, 3.2],
    cli_nargs=2,
    module="ace",
    module_group="flow",
    version_added="2.4.0",
)

# required_args
# sa = segmentation ACE

sa_out_dir = MiraclObj(
    id="40e90259-ab81-49e0-8eba-c21eb57587f5",
    name="sa_out_dir",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sao",
    cli_l_flag="sa_output_folder",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to output file folder",
    gui_label=["path to output file folder"],
    gui_group={"ace_flow": "main"},
    gui_order=[4.1, 4.2],
    cli_nargs=2,
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

sa_model_type = MiraclObj(
    id="18183868-cd27-417f-b76c-ae8455494f1c",
    name="sa_model_type",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sam",
    cli_l_flag="sa_model_type",
    cli_choices=["unet", "unetr", "ensemble"],
    cli_obj_type=ArgumentType.STRING,
    cli_help="model architecture",
    gui_label=["Model architecture"],
    gui_group={"ace_flow": "main"},
    gui_order=[5],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

sa_resolution = MiraclObj(
    id="ede3f8e1-1a1c-4f8c-93a0-46c7f4f5028c",
    name="sa_resolution",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sar",
    cli_l_flag="sa_resolution",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="voxel size (type: %(type)s)",
    cli_metavar=("X-res", "Y-res", "Z-res"),
    gui_label=["X-res", "Y-res", "Z-res"],
    gui_group={"ace_flow": "main"},
    gui_order=[6.1, 6.2, 6.3],
    cli_nargs=3,
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

# useful_args
# sa = segmentation ACE
# ctn = conversion tiff to nifti

sa_gpu_index = MiraclObj(
    id="04cc0683-6a7a-43e1-8367-cc224553b793",
    name="sa_gpu_index",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sag",
    cli_l_flag="sa_gpu_index",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="index of the GPU to use (type: %(type)s; default: %(default)s)",
    default=0,
    cli_required=False,
    gui_label=["GPU index"],
    gui_group={"ace_flow": "main"},
    gui_order=[7],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

ctn_down = MiraclObj(
    id="87682780-e060-43a3-850a-08252c3f52a5",
    name="ctn_down",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnd",
    cli_l_flag="ctn_down",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Down-sample ratio for conversion (default: %(default)s)",
    default=5,
    gui_label=["Conversion dx"],
    gui_group={"ace_flow": "main"},
    gui_order=[8],
    module="tiff_nii",
    module_group="conv",
    version_added="2.4.0",
)

rca_orient_code = MiraclObj(
    id="b0ae9b32-a66f-4eba-a39b-c238b752fb51",
    name="rca_orient_code",
    tags=["clar_allen", "reg", "ace_flow"],
    cli_s_flag="rcao",
    cli_l_flag="rca_orient_code",
    cli_obj_type=ArgumentType.STRING,
    cli_help="to orient nifti from original orientation to 'standard/Allen' orientation, (default: %(default)s)",
    default="ALS",
    gui_label=["Orientation code"],
    gui_group={"ace_flow": "main"},
    gui_order=[9],
    module="clar_allen",
    module_group="reg",
    version_added="2.4.0",
)

rca_voxel_size = MiraclObj(
    id="3894569b-1935-49fe-b9e0-e518b0bbd661",
    name="rca_voxel_size",
    tags=["clar_allen", "reg", "ace_flow"],
    cli_s_flag="rcav",
    cli_l_flag="rca_voxel_size",
    default=10,
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

sv_downsample = MiraclObj(
    id="a9c7df29-3a9b-492d-a6fe-ed9d964fb527",
    name="sv_downsample",
    tags=["voxelize", "seg", "ace_flow"],
    cli_s_flag="rvad",
    cli_l_flag="rva_downsample",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="downsample ratio for voxelization, recommended: 5 <= ratio <= 10 (default: %(default)s)",
    default=10,
    gui_label=["Voxelization dx"],
    gui_group={"ace_flow": "main"},
    gui_order=[11],
    module="voxelize",
    module_group="seg",
    version_added="2.4.0",
)

rwc_voxel_size = MiraclObj(
    id="7f3b5f21-7b07-4c6c-88d3-258c6289c12f",
    name="rwc_voxel_size",
    tags=["warp_clar", "reg", "ace_flow"],
    cli_s_flag="rwcv",
    cli_l_flag="rwc_voxel_size",
    default=25,
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

fa_rerun_registration = MiraclObj(
    id="4f0b36ff-b51c-4168-a109-65b516088147",
    name="fa_rerun_registration",
    tags=["ace", "flow", "ace_flow"],
    cli_l_flag="rerun-registration",
    cli_obj_type=ArgumentType.CUSTOM_BOOL,
    cli_help="whether to rerun registration step of flow; True => Force re-run (default: %(default)s)",
    cli_metavar=("TRUE/FALSE",),
    gui_group={"ace_flow": "main"},
    gui_label=["Rerun registration"],
    version_added="2.4.0",
    module="ace",
    module_group="flow",
    default=False,
    gui_choice_override={
        "vals": ["yes", "no"],
        "default_val": "no",
    },
)

fa_rerun_segmentation = MiraclObj(
    id="a73230bf-d291-4fb6-8f8b-becae5db2b96",
    name="fa_rerun_segmentation",
    tags=["ace", "flow", "ace_flow"],
    cli_l_flag="rerun-segmentation",
    cli_obj_type=ArgumentType.CUSTOM_BOOL,
    cli_help="whether to rerun segmentation step of flow; True => Force re-run (default: %(default)s)",
    cli_metavar=("TRUE/FALSE",),
    gui_group={"ace_flow": "main"},
    gui_label=["Rerun segmentation"],
    version_added="2.4.0",
    module="ace",
    module_group="flow",
    default=False,
    gui_choice_override={
        "vals": ["yes", "no"],
        "default_val": "no",
    },
)

fa_rerun_conversion = MiraclObj(
    id="ecd4878f-c115-498b-8683-0dfa88d375aa",
    name="fa_rerun_conversion",
    cli_l_flag="rerun-conversion",
    tags=["ace", "flow", "ace_flow"],
    cli_obj_type=ArgumentType.CUSTOM_BOOL,
    cli_help="whether to rerun conversion step of flow; True => Force re-run (default: %(default)s)",
    cli_metavar=("TRUE/FALSE",),
    gui_group={"ace_flow": "main"},
    gui_label=["Rerun conversion"],
    version_added="2.4.0",
    module="ace",
    module_group="flow",
    default=False,
    gui_choice_override={
        "vals": ["yes", "no"],
        "default_val": "no",
    },
)

sa_image_size = MiraclObj(
    id="7555410b-aa43-41ed-bb1d-e35c971d733f",
    name="sa_image_size",
    cli_s_flag="sas",
    cli_l_flag="sa_image_size",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.STRING,
    cli_help="image size (type: int; default: fetched from image header)",
    cli_required=False,
    cli_metavar=("height", "width", "depth"),
    gui_group={"ace_flow": "main"},
    gui_label=["Path to atlas dir"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    cli_nargs=3,
)

sa_nr_workers = MiraclObj(
    id="56492d95-7c57-4b4f-bcf4-5a5cd4a4eae1",
    name="sa_nr_workers",
    cli_s_flag="saw",
    cli_l_flag="sa_nr_workers",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    cli_required=False,
    cli_help="number of cpu cores deployed to pre-process image patches in parallel (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["# parallel CPU cores pre-processing"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    range_formatting_vals={
        "min_val": 0,
        "max_val": 1000,
        "increment_val": 1,
        "nr_decimals": 5,
    },
    default=4,
)

sa_cache_rate = MiraclObj(
    id="ab6fddae-0bec-446f-809f-c343746f9ac6",
    name="sa_cache_rate",
    cli_s_flag="sac",
    cli_l_flag="sa_cache_rate",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.FLOAT,
    cli_required=False,
    cli_help="percentage of raw data that is loaded into cpu during segmentation (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["% raw data loaded into CPU"],
    version_added="2.4.0",
    module="ace",
    module_group="seg",
    range_formatting_vals={
        "min_val": 0.0,
        "max_val": 100.0,
        "increment_val": 1,
        "nr_decimals": 1,
    },
    default=0.0,
)

sa_batch_size = MiraclObj(
    id="d1721e62-4db7-488b-8783-1135aeb2a603",
    name="sa_batch_size",
    cli_s_flag="sab",
    cli_l_flag="sa_batch_size",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    cli_required=False,
    cli_help="number of image patches being processed by the model in parallel on gpu (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["Batch size"],
    version_added="2.4.0",
    module="ace",
    module_group="seg",
    default=4,
)

sa_monte_carlo = MiraclObj(
    id="a1a89191-3e2d-42e0-a4c9-5d09faaafd3b",
    name="sa_monte_carlo",
    cli_s_flag="samc",
    cli_l_flag="sa_monte_carlo",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    default=0,
    cli_help="use Monte Carlo dropout (default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["Use Monte Carlo dropout"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

sa_visualize_results = MiraclObj(
    id="ab24debf-f832-4234-86e1-e2c4815cd4e3",
    name="sa_visualize_results",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sav",
    cli_l_flag="sa_visualize_results",
    cli_help="visualizing model output after predictions (default: %(default)s)",
    gui_group={"ace_flow": "main"},
    cli_action=ArgumentAction.STORE_TRUE,
    gui_label=["Visualize model output:"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    default=False,
)

sa_uncertainty_map = MiraclObj(
    id="dc289246-3b55-4679-92e4-45c91815a0dc",
    name="sa_uncertainty_map",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sau",
    cli_l_flag="sa_uncertainty_map",
    cli_help="enable map (default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["Enable uncertainty map"],
    default=False,
    cli_action=ArgumentAction.STORE_TRUE,
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

sa_binarization_threshold = MiraclObj(
    id="f0af9d66-6282-4fd2-a47e-893da57e3627",
    name="sa_binarization_threshold",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sat",
    cli_l_flag="sa_binarization_threshold",
    cli_obj_type=ArgumentType.FLOAT,
    cli_required=False,
    default=0.5,
    cli_help="threshold value for binarization (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["Binarization threshold"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    range_formatting_vals={
        "min_val": 0.0,
        "max_val": 100.0,
        "increment_val": 0.1,
        "nr_decimals": 1,
    },
)

sa_percentage_brain_patch_skip = MiraclObj(
    id="2e2cdd0b-c1ac-424a-beef-77500615664f",
    name="sa_percentage_brain_patch_skip",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sap",
    cli_l_flag="sa_percentage_brain_patch_skip",
    cli_required=False,
    cli_obj_type=ArgumentType.FLOAT,
    default=0.0,
    cli_help="percentage threshold of patch that is brain to skip during segmentation (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["% threshold of brain patch to skip:"],
    range_formatting_vals={
        "min_val": 0.0,
        "max_val": 100.0,
        "increment_val": 1,
        "nr_decimals": 1,
    },
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)


ctn_channum = MiraclObj(
    id="6576193e-df63-4e5f-a417-b6dcf509412d",
    name="ctn_channum",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctncn",
    cli_l_flag="ctn_channum",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Chan # for extracting single channel from multiple channel data (default: %(default)s)",
    default=0,
    gui_group={"ace_flow": "main"},
    gui_label=["Channel #"],
    module="tiff_nii",
    module_group="conv",
    version_added="2.4.0",
)

ctn_chanprefix = MiraclObj(
    id="b5f0c95d-4b45-490b-832a-f2f989309ced",
    name="ctn_chanprefix",
    cli_s_flag="ctncp",
    cli_l_flag="ctn_chanprefix",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_obj_type=ArgumentType.STRING,
    cli_help="Chan prefix (string before channel number in file name). ex: C00 (default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["Channel prefix"],
    module="tiff_nii",
    module_group="conv",
    version_added="2.4.0",
    default=None,
)

ctn_channame = MiraclObj(
    id="9bc9b99b-78e2-46db-8711-f05adc6f507d",
    name="ctn_channame",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnch",
    cli_l_flag="ctn_channame",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Output chan name (default: %(default)s). Channel used in registration.",
    gui_group={"ace_flow": "main"},
    gui_label=["Output channel name"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default="auto",
)

ctn_outnii = MiraclObj(
    id="7eb5121f-8520-4848-9911-9eada299aabf",
    name="ctn_outnii",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctno",
    cli_l_flag="ctn_outnii",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Output nii name (script will append downsample ratio & channel info to given name). Method of tissue clearing.",
    gui_group={"ace_flow": "main"},
    gui_label=["Out nii name"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default="SHIELD",
)

ctn_center = MiraclObj(
    id="8ea2f396-6c8c-46f7-9c5b-2768ef765a22",
    name="ctn_center",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnc",
    cli_l_flag="ctn_center",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Nii center (default: 0 0 0 ) corresponding to Allen atlas nii template",
    gui_group={"ace_flow": "main"},
    gui_label=["Nii center"],
    version_added="2.4.0",
    cli_nargs="+",
    module="tiff_nii",
    module_group="conv",
    default=[0, 0, 0],
)

ctn_downzdim = MiraclObj(
    id="9c7e4953-87eb-4979-aae4-0fb774a77f82",
    name="ctn_downzdim",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctndz",
    cli_l_flag="ctn_downzdim",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Down-sample in z dimension, binary argument, (default: %(default)s) => yes",
    gui_group={"ace_flow": "main"},
    gui_label=["Z-axis dx"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=1,
)

ctn_prevdown = MiraclObj(
    id="8b53183d-389a-40f6-b8b5-4fd1cac90fc8",
    name="ctn_prevdown",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnpd",
    cli_l_flag="ctn_prevdown",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Previous down-sample ratio, if already down-sampled",
    gui_group={"ace_flow": "main"},
    gui_label=["Previous dx"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=1,
)

ctn_percentile_thr = MiraclObj(
    id="8f676ee1-5621-40a7-befd-2d1e94ed6312",
    name="ctn_percentile_thr",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnpct",
    cli_l_flag="ctn_percentile_thr",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="Percentile threshold for intensity correction (default: %(default)s)",
    gui_group={"ace_flow": "main"},
    gui_label=["% threshold intensity corr"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=0.01,
)

































rca_hemi = MiraclObj(
    id="867580eb-ea69-426b-97ae-82b52d8d730d",
    name="rca_hemi",
    tags=["clar_allen", "reg", "ace_flow"],
    cli_s_flag="rcam",
    cli_l_flag="rca_hemi",
    cli_obj_type=ArgumentType.STRING,
    cli_help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["Labels hemisphere"],
    module="clar_allen",
    module_group="reg",
    version_added="2.4.0",
    cli_choices=['combined', 'split'],
    default="combined",
)

# rca_allen_label = MiraclObj(
#     id="496d1355-fd08-4ab5-9aaf-ee2cc8d122d0",
#     name="rca_allen_label",
#     cli_s_flag="rcal",
#     cli_l_flag="rca_allen_label",
#     cli_obj_type=ArgumentType.STRING,
#     cli_help="input Allen labels to warp. Input labels could be at a different depth than default labels, If l. is specified (m & v cannot be specified) (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     gui_label=["Allen labels to warp"],
#     module="clar_allen",
#     module_group="reg",
#     version_added="2.4.0",
# )

# rca_allen_atlas = MiraclObj(
#     id="3ea0859d-2cb9-4304-bfa6-0dab29207a74",
#     name="rca_allen_atlas",
#     cli_s_flag="rcaa",
#     cli_l_flag="rca_allen_atlas",
#     cli_obj_type=ArgumentType.STRING,
#     cli_help="custom Allen atlas (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     default="None",
# )
#
# rca_side = MiraclObj(
#     id="e3719c74-0b5a-4bdf-a336-d533a1faf7ec",
#     name="rca_side",
#     cli_s_flag="rcas",
#     cli_l_flag="rca_side",
#     cli_obj_type=ArgumentType.STRING,
#     cli_help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     cli_choices=['rh', 'lh'],
# )
#
# rca_no_mosaic_fig = MiraclObj(
#     id="0c3b2cac-4cb3-4b32-86fb-b1a64a49452a",
#     name="rca_no_mosaic_fig",
#     cli_s_flag="rcanm",
#     cli_l_flag="rca_no_mosaic_fig",
#     cli_obj_type=ArgumentType.NONE,
#     cli_help="by default a mosaic figure (.png) of allen labels registered to clarity will be saved. If this flag is set, the mosaic figure will not be saved.",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     default=1,
# )
#
# rca_olfactory_bulb = MiraclObj(
#     id="dfd47b33-6f66-4a41-b42a-6264bb478f87",
#     name="rca_olfactory_bulb",
#     cli_s_flag="rcab",
#     cli_l_flag="rca_olfactory_bulb",
#     cli_obj_type=ArgumentType.INTEGER,
#     cli_help="include olfactory bulb in brain (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     cli_choices=[0, 1],
# )
#
# rca_skip_cor = MiraclObj(
#     id="a58b7a5a-c253-41cd-87bb-ef3f9b232cb6",
#     name="rca_skip_cor",
#     cli_s_flag="rcap",
#     cli_l_flag="rca_skip_cor",
#     cli_obj_type=ArgumentType.NONE,
#     cli_help="if utilfn intensity correction already ran, skip correction inside registration (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
# )
#
# rca_warp = MiraclObj(
#     id="faaca013-3a95-4a3e-be24-f85e74841a83",
#     name="rca_warp",
#     cli_s_flag="rcaw",
#     cli_l_flag="rca_warp",
#     cli_obj_type=ArgumentType.NONE,
#     cli_help="warp high-res clarity to Allen space (default: False)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
# )






























def create_parser_arguments(
    parser: ArgumentParser,
    groups_dict: Dict[str, Dict[str, Union[str, List[MiraclObj]]]],
) -> None:
    """
    Create argument parser groups based on a dictionary of MiraclObj instances.

    Each group will contain command-line arguments defined by the attributes
    of the MiraclObj instances.

    :param parser: The ArgumentParser instance to which the arguments will be added.
    :param groups_dict: A dictionary mapping group names to lists of MiraclObj instances and descriptions.
    """
    optional_attrs = {
        "cli_obj_type": "type",
        "cli_metavar": "metavar",
        "cli_nargs": "nargs",
        "cli_choices": "choices",
        "default": "default",
        "cli_required": "required",
    }

    for group_info in groups_dict.values():
        title = cast(str, group_info["title"])
        description = cast(
            Optional[str],
            group_info.get("description"),
        )

        current_parser = parser.add_argument_group(
            title=title,
            description=description,
        )

        for obj in group_info["args"]:
            arg_dict = {"help": obj.cli_help}
            for attr, key in optional_attrs.items():
                if hasattr(obj, attr) and getattr(obj, attr) is not None:
                    value = getattr(obj, attr)
                    if attr == "cli_obj_type":
                        arg_dict[key] = value.python_type
                    else:
                        arg_dict[key] = value

            flags = [f"-{obj.cli_s_flag}" for obj in [obj] if obj.cli_s_flag]
            flags.extend(f"--{obj.cli_l_flag}" for obj in [obj] if obj.cli_l_flag)

            if flags:
                current_parser.add_argument(*flags, **arg_dict)


# def create_parser_arguments(
#     parser: ArgumentParser, groups_dict: Dict[str, List[BaseModel]]
# ) -> None:
#     """
#     Create argument parser groups based on a dictionary of MiraclObj instances.
#
#     Each group will contain command-line arguments defined by the attributes
#     of the MiraclObj instances.
#
#     :param parser: The ArgumentParser instance to which the arguments will be added.
#     :param groups_dict: A dictionary mapping group names to lists of MiraclObj instances.
#     """
#     # Define the optional attributes that can be added to the argument
#     optional_attrs = {
#         "cli_metavar": "metavar",
#         "cli_nargs": "nargs",
#         "cli_choices": "choices",
#         "default": "default",
#         "cli_required": "required",
#     }
#
#     for group_name, obj_list in groups_dict.items():
#         # Create a new argument group for each group name
#         current_parser = parser.add_argument_group(group_name)
#
#         for obj in obj_list:
#             # Prepare the base argument dictionary
#             arg_dict = {
#                 "type": obj.cli_obj_type.python_type,
#                 "help": obj.cli_help,
#             }
#
#             # Add optional attributes directly if they exist
#             for attr, key in optional_attrs.items():
#                 if hasattr(obj, attr):  # Check if the attribute exists
#                     arg_dict[key] = getattr(obj, attr)  # Safe to access since it exists
#
#             # Prepare the flags
#             flags = []
#             if hasattr(obj, "cli_s_flag") and obj.cli_s_flag:
#                 flags.append(f"-{obj.cli_s_flag}")
#             if hasattr(obj, "cli_l_flag") and obj.cli_l_flag:
#                 flags.append(f"--{obj.cli_l_flag}")
#
#             # Add the argument to the current parser group
#             current_parser.add_argument(*flags, **arg_dict)

if __name__ == "__main__":
    # args = parser.parse_args()
    # args_dict = vars(args)  # Instead of dict -> Pydantic serializer
    # print(type(args_dict[fa_single.cli_l_flag]))
    # print(f"Value for {fa_single.cli_l_flag}: {args_dict[fa_single.cli_l_flag]}")
    # print(f"Value for {fa_control.cli_l_flag}: {args_dict[fa_control.cli_l_flag]}")
    # Usage remains the same
    # parser = ArgumentParser(description="Your program description")
    # objects_list = [
    #     fa_single,
    #     fa_control,
    #     fa_treated,
    #     sa_out_dir,
    # ]  # Add all your MiraclObj instances here
    # create_parser_arguments(parser, objects_list)
    #
    # # Now you can use the parser as usual
    # args = parser.parse_args()

    ARA_ENV = "aradir"
    FULL_PROG_NAME = "miracl flow ace"

    parser = ArgumentParser(
        prog=FULL_PROG_NAME,
        formatter_class=RawDescriptionHelpFormatter,
        # add_help=False,  # Used for separating args
        description="""
  1) Segments images with ACE
  2) Convert raw tif/tiff files to nifti for registration
  3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
  4) Voxelizes segmentation results into density maps with Allen atlas resolution
  5) Warps downsampled CLARITY data/channels from native space to Allen atlas""",
        usage=f"""{FULL_PROG_NAME}
        [-s SINGLE_TIFF_DIR]
        [-c CONTROL_BASE_DIR CONTROL_TIFF_DIR_EXAMPLE]
        [-t TREATED_BASE_DIR TREATED_TIFF_DIR_EXAMPLE]
        -sao SA_OUTPUT_FOLDER
        -sam {{unet,unetr,ensemble}}
        -sar X-res Y-res Z-res
        [-sag SA_GPU_INDEX]
        [-ctnd CTN_DOWN]
        [-rcao RCA_ORIENT_CODE]
        [-rcav {{10,25,50}}]
        [-rvad RVA_DOWNSAMPLE]
        [-rwcv {{10,25,50}}]
        [--rerun-registration TRUE/FALSE]
        [--rerun-segmentation TRUE/FALSE]
        [--rerun-conversion TRUE/FALSE]""",
    )

    groups_dict = {
        "single_multi_args_group": {
            "title": "single or multi method arguments",
            "description": "user is required to pass either single or multi method arguments",
            "args": [fa_single, fa_control, fa_treated],
        },
        "required_args": {
            "title": "required arguments",
            "description": "(set the single or multi method arguments first)",
            "args": [sa_out_dir, sa_model_type, sa_resolution],
        },
        "useful_args": {
            "title": "useful/important arguments",
            "args": [
                sa_gpu_index,
                ctn_down,
                rca_orient_code,
                rca_voxel_size,
                fa_rerun_registration,
                fa_rerun_segmentation,
                fa_rerun_conversion,
            ],
        },
        "seg_args": {
            "title": "optional segmentation arguments",
            "args": [
                sa_image_size,
                sa_nr_workers,
                sa_cache_rate,
                sa_batch_size,
                sa_monte_carlo,
                sa_visualize_results,
                sa_uncertainty_map,
                sa_binarization_threshold,
                sa_percentage_brain_patch_skip,
            ],
        },
        "conv_args": {
            "title": "optional conversion arguments",
            "args": [
                ctn_channum,
                ctn_chanprefix,
                ctn_channame,
                ctn_outnii,
                ctn_center,
                ctn_downzdim,
                ctn_prevdown,
                ctn_percentile_thr,
            ],
        },
        "reg_args": {
            "title": "optional registration arguments",
            "args": [
                rca_hemi,
            ],
        },
    }

    create_parser_arguments(parser, groups_dict)

    # Now you can use the parser as usual
    args = parser.parse_args()
