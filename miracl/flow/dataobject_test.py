from miracl_datamodel import MiraclObj, ArgumentType, ArgumentAction
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Dict, Union, cast, Optional
from pathlib import Path


########
# MAIN #
########

# single_multi_args_group
# fa = Flow ACE

flow_ace_single = MiraclObj(
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

flow_ace_control = MiraclObj(
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

flow_ace_treated = MiraclObj(
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

seg_ace_out_dir = MiraclObj(
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

seg_ace_model_type = MiraclObj(
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

seg_ace_resolution = MiraclObj(
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

seg_ace_gpu_index = MiraclObj(
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

conv_tiff_nii_down = MiraclObj(
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

reg_clar_allen_orient_code = MiraclObj(
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

reg_clar_allen_voxel_size = MiraclObj(
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

seg_vox_downsample = MiraclObj(
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

reg_warp_clar_voxel_size = MiraclObj(
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

flow_ace_rerun_registration = MiraclObj(
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

flow_ace_rerun_segmentation = MiraclObj(
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

flow_ace_rerun_conversion = MiraclObj(
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

seg_ace_image_size = MiraclObj(
    id="7555410b-aa43-41ed-bb1d-e35c971d733f",
    name="sa_image_size",
    cli_s_flag="sas",
    cli_l_flag="sa_image_size",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.STRING,
    cli_help="image size (type: int; default: fetched from image header)",
    cli_required=False,
    cli_metavar=("height", "width", "depth"),
    gui_group={"ace_flow": "segmentation"},
    gui_label=["Path to atlas dir"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    cli_nargs=3,
)

seg_ace_nr_workers = MiraclObj(
    id="56492d95-7c57-4b4f-bcf4-5a5cd4a4eae1",
    name="sa_nr_workers",
    cli_s_flag="saw",
    cli_l_flag="sa_nr_workers",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    cli_required=False,
    cli_help="number of cpu cores deployed to pre-process image patches in parallel (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
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

seg_ace_cache_rate = MiraclObj(
    id="ab6fddae-0bec-446f-809f-c343746f9ac6",
    name="sa_cache_rate",
    cli_s_flag="sac",
    cli_l_flag="sa_cache_rate",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.FLOAT,
    cli_required=False,
    cli_help="percentage of raw data that is loaded into cpu during segmentation (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
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

seg_ace_batch_size = MiraclObj(
    id="d1721e62-4db7-488b-8783-1135aeb2a603",
    name="sa_batch_size",
    cli_s_flag="sab",
    cli_l_flag="sa_batch_size",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    cli_required=False,
    cli_help="number of image patches being processed by the model in parallel on gpu (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
    gui_label=["Batch size"],
    version_added="2.4.0",
    module="ace",
    module_group="seg",
    default=4,
)

seg_ace_monte_carlo = MiraclObj(
    id="a1a89191-3e2d-42e0-a4c9-5d09faaafd3b",
    name="sa_monte_carlo",
    cli_s_flag="samc",
    cli_l_flag="sa_monte_carlo",
    tags=["ace", "seg", "ace_flow"],
    cli_obj_type=ArgumentType.INTEGER,
    default=0,
    cli_help="use Monte Carlo dropout (default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
    gui_label=["Use Monte Carlo dropout"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

seg_ace_visualize_results = MiraclObj(
    id="ab24debf-f832-4234-86e1-e2c4815cd4e3",
    name="sa_visualize_results",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sav",
    cli_l_flag="sa_visualize_results",
    cli_help="visualizing model output after predictions (default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
    cli_action=ArgumentAction.STORE_TRUE,
    gui_label=["Visualize model output:"],
    module="ace",
    module_group="seg",
    version_added="2.4.0",
    default=False,
)

seg_ace_uncertainty_map = MiraclObj(
    id="dc289246-3b55-4679-92e4-45c91815a0dc",
    name="sa_uncertainty_map",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sau",
    cli_l_flag="sa_uncertainty_map",
    cli_help="enable map (default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
    gui_label=["Enable uncertainty map"],
    default=False,
    cli_action=ArgumentAction.STORE_TRUE,
    module="ace",
    module_group="seg",
    version_added="2.4.0",
)

seg_ace_binarization_threshold = MiraclObj(
    id="f0af9d66-6282-4fd2-a47e-893da57e3627",
    name="sa_binarization_threshold",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sat",
    cli_l_flag="sa_binarization_threshold",
    cli_obj_type=ArgumentType.FLOAT,
    cli_required=False,
    default=0.5,
    cli_help="threshold value for binarization (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
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

seg_ace_percentage_brain_patch_skip = MiraclObj(
    id="2e2cdd0b-c1ac-424a-beef-77500615664f",
    name="sa_percentage_brain_patch_skip",
    tags=["ace", "seg", "ace_flow"],
    cli_s_flag="sap",
    cli_l_flag="sa_percentage_brain_patch_skip",
    cli_required=False,
    cli_obj_type=ArgumentType.FLOAT,
    default=0.0,
    cli_help="percentage threshold of patch that is brain to skip during segmentation (type: %(type)s; default: %(default)s)",
    gui_group={"ace_flow": "segmentation"},
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


conv_tiff_nii_channum = MiraclObj(
    id="6576193e-df63-4e5f-a417-b6dcf509412d",
    name="ctn_channum",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctncn",
    cli_l_flag="ctn_channum",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Chan # for extracting single channel from multiple channel data (default: %(default)s)",
    default=0,
    gui_group={"ace_flow": "conversion"},
    gui_label=["Channel #"],
    module="tiff_nii",
    module_group="conv",
    version_added="2.4.0",
)

conv_tiff_nii_chanprefix = MiraclObj(
    id="b5f0c95d-4b45-490b-832a-f2f989309ced",
    name="ctn_chanprefix",
    cli_s_flag="ctncp",
    cli_l_flag="ctn_chanprefix",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_obj_type=ArgumentType.STRING,
    cli_help="Chan prefix (string before channel number in file name). ex: C00 (default: %(default)s)",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Channel prefix"],
    module="tiff_nii",
    module_group="conv",
    version_added="2.4.0",
    default=None,
)

conv_tiff_nii_channame = MiraclObj(
    id="9bc9b99b-78e2-46db-8711-f05adc6f507d",
    name="ctn_channame",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnch",
    cli_l_flag="ctn_channame",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Output chan name (default: %(default)s). Channel used in registration.",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Output channel name"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default="auto",
)

conv_tiff_nii_outnii = MiraclObj(
    id="7eb5121f-8520-4848-9911-9eada299aabf",
    name="ctn_outnii",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctno",
    cli_l_flag="ctn_outnii",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Output nii name (script will append downsample ratio & channel info to given name). Method of tissue clearing.",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Out nii name"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default="SHIELD",
)

conv_tiff_nii_center = MiraclObj(
    id="8ea2f396-6c8c-46f7-9c5b-2768ef765a22",
    name="ctn_center",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnc",
    cli_l_flag="ctn_center",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Nii center (default: 0 0 0 ) corresponding to Allen atlas nii template",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Nii center"],
    version_added="2.4.0",
    cli_nargs="+",
    module="tiff_nii",
    module_group="conv",
    default=[0, 0, 0],
)

conv_tiff_nii_downzdim = MiraclObj(
    id="9c7e4953-87eb-4979-aae4-0fb774a77f82",
    name="ctn_downzdim",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctndz",
    cli_l_flag="ctn_downzdim",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Down-sample in z dimension, binary argument, (default: %(default)s) => yes",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Z-axis dx"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=1,
)

conv_tiff_nii_prevdown = MiraclObj(
    id="8b53183d-389a-40f6-b8b5-4fd1cac90fc8",
    name="ctn_prevdown",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnpd",
    cli_l_flag="ctn_prevdown",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Previous down-sample ratio, if already down-sampled",
    gui_group={"ace_flow": "conversion"},
    gui_label=["Previous dx"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=1,
)

conv_tiff_nii_percentile_thr = MiraclObj(
    id="8f676ee1-5621-40a7-befd-2d1e94ed6312",
    name="ctn_percentile_thr",
    tags=["tiff_nii", "conv", "ace_flow"],
    cli_s_flag="ctnpct",
    cli_l_flag="ctn_percentile_thr",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="Percentile threshold for intensity correction (default: %(default)s)",
    gui_group={"ace_flow": "conversion"},
    gui_label=["% threshold intensity corr"],
    version_added="2.4.0",
    module="tiff_nii",
    module_group="conv",
    default=0.01,
)


reg_clar_allen_hemi = MiraclObj(
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
    default="combined",
)

reg_clar_allen_allen_label = MiraclObj(
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
    default=None,
)

reg_clar_allen_allen_atlas = MiraclObj(
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
    default="None",
)

reg_clar_allen_side = MiraclObj(
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
    default="rh",
    gui_choice_override={
        "vals": ["right hemisphere", "left hemisphere"],
        "default_val": "right hemisphere",
    },
    module="clar_allen",
    module_group="reg",
)

reg_clar_allen_no_mosaic_fig = MiraclObj(
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
    default=1,
    gui_choice_override={
        "vals": ["yes", "no"],
        "default_val": "yes",
    },
    module="clar_allen",
    module_group="reg",
)

reg_clar_allen_olfactory_bulb = MiraclObj(
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
    default=0,
)

reg_clar_allen_skip_cor = MiraclObj(
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
    default=0,
    cli_action=ArgumentAction.STORE_CONST,
    cli_const=1,
)

reg_clar_allen_warp = MiraclObj(
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
    default=0,
    cli_action=ArgumentAction.STORE_CONST,
    cli_const=1,
    gui_choice_override={
        "vals": ["yes", "no"],
        "default_val": "no",
    },
    version_added="2.4.0",
)


seg_vox_xy_res = MiraclObj(
    id="1575ba9e-bdae-4f6d-9ee9-7c31c7e3d3bc",
    name="rva_vx_res",
    tags=["voxelize", "seg", "ace_flow"],
    cli_s_flag="rvavx",
    cli_l_flag="rva_vx_res",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="voxel size (x, y dims) in um (default: %(default)s)",
    gui_group={"ace_flow": "vox_warp"},
    gui_label=["Voxel sizes (um):"],
    version_added="2.4.0",
    module="voxelize",
    module_group="seg",
    default=1,
)

seg_vox_z_res = MiraclObj(
    id="2f576c3a-d62f-4e37-aae1-2bae9d09ae36",
    name="rva_vz_res",
    tags=["voxelize", "seg", "ace_flow"],
    cli_s_flag="rvavz",
    cli_l_flag="rva_vz_res",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="voxel size (z dim) in um (default: %(default)s)",
    gui_group={"ace_flow": "vox_warp"},
    gui_label=["Voxel sizes (um):"],
    version_added="2.4.0",
    module="voxelize",
    module_group="seg",
    default=1,
)

reg_warp_clar_input_folder = MiraclObj(
    id="9bb71e9f-b6de-4c30-a6da-449fe97cd45c",
    name="rwc_input_folder",
    tags=["warp_clar", "reg", "ace_flow"],
    cli_s_flag="rwcr",
    cli_l_flag="rwc_input_folder",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to CLARITY registration folder",
    gui_group={'ace_flow': 'vox_warp'},
    gui_label=["Path to CLARITY reg folder:"],
    module="warp_clar",
    module_group="reg",
    version_added="2.4.0",
    default=None,
)

reg_warp_clar_input_nii = MiraclObj(
    id="d0d81ddf-caab-465f-8aed-0bcf7600bfa6",
    name="rwc_input_nii",
    tags=["warp_clar", "reg", "ace_flow"],
    cli_s_flag="rwcn",
    cli_l_flag="rwc_input_nii",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to downsampled CLARITY nii file to warp",
    gui_group={'ace_flow': 'vox_warp'},
    gui_label=["Path to dx CLARITY nii file:"],
    module="warp_clar",
    module_group="reg",
    version_added="2.4.0",
    default=None,
)

reg_warp_clar_seg_channel = MiraclObj(
    id="fc35cbe4-947b-4673-989a-f2d95db82c5e",
    name="rwc_seg_channel",
    tags=["warp_clar", "reg", "ace_flow"],
    cli_s_flag="rwcc",
    cli_l_flag="rwc_seg_channel",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Segmentation channel (ex. green) - required if voxelized seg is input",
    gui_group={'ace_flow': 'vox_warp'},
    gui_label=["Seg channel (ex: 'green'):"],
    version_added="2.4.0",
    module="warp_clar",
    module_group="reg",
    default="green",
)

stats_ace_clust_atlas_dir = MiraclObj(
    id="e7824ae1-af2d-4d51-8322-2ade4cf68379",
    name="pcs_atlas_dir",
    tags=["ace", "stats", "cluserwise", "ace_flow"],
    cli_s_flag="pcsa",
    cli_l_flag="pcs_atlas_dir",
    cli_help="path of atlas directory",
    gui_label=["Path to atlas dir"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default="miracl_home",
    module="ace",
    module_group="stats",
)

stats_ace_clust_num_perm = MiraclObj(
    id="4c6a1223-4347-4634-a3b0-475967a967f0",
    name="pcs_num_perm",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsn",
    cli_l_flag="pcs_num_perm",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="number of permutations (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["# permutations"],
    version_added="2.4.0",
    default=500,
    module="ace",
    module_group="stats",
)

stats_ace_clust_img_resolution = MiraclObj(
    id="5978055a-6c10-49d1-8b6f-c531f9b92d63",
    name="pcs_img_resolution",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsr",
    cli_l_flag="pcs_img_resolution",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="resolution of images in um (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["Resolution of images (um)"],
    version_added="2.4.0",
    cli_choices=[10, 25, 50],
    default=25,
    module="ace",
    module_group="stats",
)

stats_ace_clust_smoothing_fwhm = MiraclObj(
    id="b84ab2a5-27e5-429d-a015-a8df2335271b",
    name="pcs_smoothing_fwhm",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsfwhm",
    cli_l_flag="pcs_smoothing_fwhm",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="fwhm of Gaussian kernel in pixel (default: %(default)s)",
    gui_label=["fwhm of Gaussian kernel (px)"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=3,
    module="ace",
    module_group="stats",
)

stats_ace_clust_tfce_start = MiraclObj(
    id="95bbc02a-1d5b-4b66-87c3-fe54c735aa18",
    name="pcs_tfce_start",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsstart",
    cli_l_flag="pcs_tfce_start",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="tfce threshold start (default: %(default)s)",
    gui_label=["tfce threshold start"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=0.01,
    module="ace",
    module_group="stats",
)

stats_ace_clust_tfce_step = MiraclObj(
    id="9c282d72-bf43-4d15-9da2-11cf64e605de",
    name="pcs_tfce_step",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsstep",
    cli_l_flag="pcs_tfce_step",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="tfce threshold step (default: %(default)s)",
    gui_label=["tfce threshold step"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=5,
    module="ace",
    module_group="stats",
)

stats_ace_clust_cpu_load = MiraclObj(
    id="86dcfae0-b98b-4523-aaac-41b60529a31a",
    name="pcs_cpu_load",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsc",
    cli_l_flag="pcs_cpu_load",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="Percent of cpus used for parallelization (default: %(default)s)",
    gui_label=["% CPU's for parallelization"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=0.9,
    module="ace",
    module_group="stats",
)

stats_ace_clust_tfce_h = MiraclObj(
    id="5237ff1a-4cbb-4cb9-ab38-2fb2a23131b2",
    name="pcs_tfce_h",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsh",
    cli_l_flag="pcs_tfce_h",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="tfce H power (default: %(default)s)",
    gui_label=["tfce H power"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=2,
    module="ace",
    module_group="stats",
)

stats_ace_clust_tfce_e = MiraclObj(
    id="54dfc9df-0d3d-4b93-920f-40f70365a881",
    name="pcs_tfce_e",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcse",
    cli_l_flag="pcs_tfce_e",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="tfce E power (default: %(default)s)",
    gui_label=["tfce E power"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=0.5,
    module="ace",
    module_group="stats",
)

stats_ace_clust_step_down_p = MiraclObj(
    id="85596967-b0ce-41a8-b4b3-676a3281e607",
    name="pcs_step_down_p",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcssp",
    cli_l_flag="pcs_step_down_p",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="step down p-value (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["Step down p-value"],
    version_added="2.4.0",
    default=0.3,
    module="ace",
    module_group="stats",
    range_formatting_vals={
        "min_val": 0.0000,
        "max_val": 1.0000,
        "increment_val": 0.01,
        "nr_decimals": 4,
    },
)

stats_ace_clust_mask_thr = MiraclObj(
    id="bfddb1db-0d53-4908-877a-2f6c87d8024e",
    name="pcs_mask_thr",
    tags=["ace", "stats", "clusterwise", "ace_flow"],
    cli_s_flag="pcsm",
    cli_l_flag="pcs_mask_thr",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="percentile to be used for binarizing difference of the mean (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["% for binarizing mean diff"],
    version_added="2.4.0",
    default=95,
    module="ace",
    module_group="stats",
    range_formatting_vals={
        "min_val": 0,
        "max_val": 100,
        "increment_val": 1,
    },
)

stats_ace_corr_pvalue_thr = MiraclObj(
    id="c0cf81cb-8ad1-4982-974b-a5b2e589d6d1",
    name="cf_pvalue_thr",
    tags=["ace", "stats", "correlation", "ace_flow"],
    cli_s_flag="cft",
    cli_l_flag="cf_pvalue_thr",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="threshold for binarizing p value (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    gui_label=["Threshold binarizing p-value"],
    version_added="2.4.0",
    default=0.05,
    module="ace",
    module_group="stats",
    range_formatting_vals={
        "min_val": 0.0000,
        "max_val": 1.0000,
        "increment_val": 0.01,
        "nr_decimals": 4,
    },
)

stats_heatmap_group1 = MiraclObj(
    id="3a7bc2f7-2eb8-45aa-aa32-0d11762b7565",
    name="sh_group1",
    tags=["heatmap", "stats", "ace_flow"],
    cli_s_flag="shg1",
    cli_l_flag="sh_group1",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to group 1 directory",
    gui_label=["Path to group 1 dir"],
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=None,
    module="heatmap_group",
    module_group="stats",
)

stats_heatmap_group2 = MiraclObj(
    id="8e0ef0a5-419c-48b4-9d11-e61aa9e69297",
    name="sh_group2",
    tags=["heatmap", "stats", "ace_flow"],
    cli_s_flag="shg2",
    cli_l_flag="sh_group2",
    cli_obj_type=ArgumentType.STRING,
    cli_help="path to group 2 directory",
    gui_group={'ace_flow': 'main'},
    gui_label=["Path to group 1 dir"],
    version_added="2.4.0",
    module="heatmap_group",
    module_group="stats",
    default=None,
)

stats_heatmap_vox = MiraclObj(
    id="68cc3699-25a4-4b28-9407-9c22c6a2b880",
    name="sh_vox",
    tags=["heatmap", "stats", "ace_flow"],
    cli_s_flag="shv",
    cli_l_flag="sh_vox",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="voxel size/Resolution in um",
    gui_group={'ace_flow': 'main'},
    gui_label=["Voxel size (um)"],
    version_added="2.4.0",
    cli_choices=[10, 25, 50],
    module="heatmap_group",
    module_group="stats",
    default=None,
)

stats_heatmap_sigma = MiraclObj(
    id="a8578f34-5f92-4788-8eb9-3f39c8279dd8",
    name="sh_sigma",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Guassian smoothing sigma"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shgs",
    cli_l_flag="sh_sigma",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="Gaussian smoothing sigma (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=4,
    range_formatting_vals={
        "min_val": 0,
        "max_val": 1000,
        "increment_val": 1,
    },
)

stats_heatmap_percentile = MiraclObj(
    id="dcb8da8a-1a45-4e33-8489-5acc71049c3b",
    name="sh_percentile",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["% threshold svg"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shp",
    cli_l_flag="sh_percentile",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="percentile (%%) threshold for registration-to-input data check svg animation (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=10,
    range_formatting_vals={
        "min_val": 0,
        "max_val": 100,
        "increment_val": 1,
    },
)

stats_heatmap_colourmap_pos = MiraclObj(
    id="55fba010-fcf3-4aab-95ca-6dcd1891f3a4",
    name="sh_colourmap_pos",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Matplotlib colourmap pos values"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shcp",
    cli_l_flag="sh_colourmap_pos",
    cli_obj_type=ArgumentType.STRING,
    cli_help="matplotlib colourmap for positive values (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default="Reds",
)

stats_heatmap_colourmap_neg = MiraclObj(
    id="b462edc4-bd58-44a8-9a26-25d786f17dcd",
    name="sh_colourmap_neg",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Matplotlib colourmap neg values"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shcn",
    cli_l_flag="sh_colourmap_neg",
    cli_obj_type=ArgumentType.STRING,
    cli_help="matplotlib colourmap for negative values (default: %(default)s)",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default="Blues",
)

stats_heatmap_sagittal = MiraclObj(
    id="6de23309-e0d4-43dd-aa7b-317e566d4cf8",
    name="sh_sagittal",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Slicing across sagittal axis"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shs",
    cli_l_flag="sh_sagittal",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="slicing across sagittal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    cli_nargs=5,
    default=None,
)

stats_heatmap_coronal = MiraclObj(
    id="01d626c7-ba22-4b32-a49a-dbcf2d1b249a",
    name="sh_coronal",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Slicing across coronal axis"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shc",
    cli_l_flag="sh_coronal",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    cli_nargs=5,
)

stats_heatmap_axial = MiraclObj(
    id="b30c0ced-4a0d-48a2-9ff5-49cd3c59bf66",
    name="sh_axial",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Slicing across axial axis"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="sha",
    cli_l_flag="sh_axial",
    cli_obj_type=ArgumentType.INTEGER,
    cli_help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    cli_nargs=5,
)

stats_heatmap_figure_dim = MiraclObj(
    id="b8405406-07e7-45bc-929a-87d480e9c91e",
    name="sh_figure_dim",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Figure dimensions"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shf",
    cli_l_flag="sh_figure_dim",
    cli_obj_type=ArgumentType.FLOAT,
    cli_help="figure width and height",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    cli_nargs=2,
    default=None,
)

stats_heatmap_dir_outfile = MiraclObj(
    id="650a0bdf-d7f2-4f97-8e24-2854bb21a403",
    name="sh_dir_outfile",
    tags=["heatmap", "stats", "ace_flow"],
    gui_label=["Output folder"],
    module="heatmap_group",
    module_group="stats",
    cli_s_flag="shd",
    cli_l_flag="sh_dir_outfile",
    cli_obj_type=ArgumentType.STRING,
    cli_help="Output file directory (default is cwd: %(default)s)",
    gui_group={'ace_flow': 'main'},
    version_added="2.4.0",
    default=Path.cwd(),
)

# sh_outfile = MiraclObj(
#     id="2a74cd39-83d2-4e69-b326-3ad36d8d1034",
#     name="sh_outfile",
#     cli_s_flag="sho",
#     cli_l_flag="sh_outfile",
#     cli_obj_type="ArgumentType.STRING",
#     cli_help="Output filenames (default: group_1 group_2 group_difference)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     cli_nargs="+",
#     default=['group_1', 'group_2', 'group_difference'],
# )

# sh_extension = MiraclObj(
#     id="8ec70813-f78b-444a-9431-36c58435aa2c",
#     name="sh_extension",
#     cli_s_flag="she",
#     cli_l_flag="sh_extension",
#     cli_obj_type="ArgumentType.STRING",
#     cli_help="heatmap figure extension (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     default="tiff",
# )

# sh_dpi = MiraclObj(
#     id="885d3bcc-6dd9-41ad-ac09-b52272da275f",
#     name="sh_dpi",
#     cli_s_flag="shdpi",
#     cli_l_flag="sh_dpi",
#     cli_obj_type="ArgumentType.INTEGER",
#     cli_help="dots per inch (default: %(default)s)",
#     gui_group={'ace_flow': 'main'},
#     version_added="2.4.0",
#     default=500,
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
            "args": [
                flow_ace_single,
                flow_ace_control,
                flow_ace_treated,
            ],
        },
        "required_args": {
            "title": "required arguments",
            "description": "(set the single or multi method arguments first)",
            "args": [
                seg_ace_out_dir,
                seg_ace_model_type,
                seg_ace_resolution,
            ],
        },
        "useful_args": {
            "title": "useful/important arguments",
            "args": [
                seg_ace_gpu_index,
                conv_tiff_nii_down,
                reg_clar_allen_orient_code,
                reg_clar_allen_voxel_size,
                seg_vox_downsample,
                reg_warp_clar_voxel_size,
                flow_ace_rerun_registration,
                flow_ace_rerun_segmentation,
                flow_ace_rerun_conversion,
            ],
        },
        "seg_args": {
            "title": "optional segmentation arguments",
            "args": [
                seg_ace_image_size,
                seg_ace_nr_workers,
                seg_ace_cache_rate,
                seg_ace_batch_size,
                seg_ace_monte_carlo,
                seg_ace_visualize_results,
                seg_ace_uncertainty_map,
                seg_ace_binarization_threshold,
                seg_ace_percentage_brain_patch_skip,
            ],
        },
        "conv_args": {
            "title": "optional conversion arguments",
            "args": [
                conv_tiff_nii_channum,
                conv_tiff_nii_chanprefix,
                conv_tiff_nii_channame,
                conv_tiff_nii_outnii,
                conv_tiff_nii_center,
                conv_tiff_nii_downzdim,
                conv_tiff_nii_prevdown,
                conv_tiff_nii_percentile_thr,
            ],
        },
        "reg_args": {
            "title": "optional registration arguments",
            "args": [
                reg_clar_allen_hemi,
                reg_clar_allen_allen_label,
                reg_clar_allen_allen_atlas,
                reg_clar_allen_side,
                reg_clar_allen_no_mosaic_fig,
                reg_clar_allen_olfactory_bulb,
                reg_clar_allen_skip_cor,
                reg_clar_allen_warp,
            ],
        },
        "vox_args": {
            "title": "optional voxelization arguments",
            "args": [
                seg_vox_xy_res,
                seg_vox_z_res,
            ],
        },
        "warp_args": {
            "title": "optional voxelization arguments",
            "args": [
                reg_warp_clar_input_folder,
                reg_warp_clar_input_nii,
                reg_warp_clar_seg_channel,
            ],
        },
        "clust_args": {
            "title": "optional cluster_wise arguments",
            "args": [
                stats_ace_clust_atlas_dir,
                stats_ace_clust_img_resolution,
                stats_ace_clust_smoothing_fwhm,
                stats_ace_clust_tfce_start,
                stats_ace_clust_tfce_step,
                stats_ace_clust_tfce_h,
                stats_ace_clust_tfce_e,
                stats_ace_clust_step_down_p,
                stats_ace_clust_mask_thr,
            ],
        },
        "corr_args": {
            "title": "optional correlational arguments",
            "args": [
                stats_ace_corr_pvalue_thr,
            ],
        },
        "heatmap_args": {
            "title": "optional heatmap arguments",
            "args": [
                stats_heatmap_group1,
                stats_heatmap_group2,
                stats_heatmap_vox,
                stats_heatmap_sigma,
                stats_heatmap_percentile,
                stats_heatmap_colourmap_pos,
                stats_heatmap_colourmap_neg,
                stats_heatmap_sagittal,
                stats_heatmap_coronal,
                stats_heatmap_axial,
                stats_heatmap_figure_dim,
                stats_heatmap_dir_outfile,
            ],
        },
    }

    create_parser_arguments(parser, groups_dict)

    # Now you can use the parser as usual
    args = parser.parse_args()
