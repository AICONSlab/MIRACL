from miracl_datamodel import MiraclObj, ArgumentType, ArgumentAction
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List, Dict, Union, cast, Optional
from objs_stats import StatsAceObjs as stats_ace
from objs_stats import StatsAceClustObjs as stats_ace_clust
from objs_stats import StatsAceCorrObjs as stats_ace_corr
from objs_stats import StatsHeatmapObjs as stats_heatmap
from objs_reg import RegClarAllenObjs as reg_clar_allen
from objs_reg import RegWarpClarObjs as reg_warp_clar
from objs_seg import SegAceObjs as seg_ace
from objs_seg import SegVoxObjs as seg_vox
from objs_conv import ConvTiffNiiObjs as conv_tiff_nii
from objs_flow import FlowAceObjs as flow_ace


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
                flow_ace.single,
                flow_ace.control,
                flow_ace.treated,
            ],
        },
        "required_args": {
            "title": "required arguments",
            "description": "(set the single or multi method arguments first)",
            "args": [
                seg_ace.out_dir,
                seg_ace.model_type,
                seg_ace.resolution,
            ],
        },
        "useful_args": {
            "title": "useful/important arguments",
            "args": [
                seg_ace.gpu_index,
                conv_tiff_nii.down,
                reg_clar_allen.orient_code,
                reg_clar_allen.voxel_size,
                seg_vox.downsample,
                reg_warp_clar.voxel_size,
                flow_ace.rerun_registration,
                flow_ace.rerun_segmentation,
                flow_ace.rerun_conversion,
            ],
        },
        "seg_args": {
            "title": "optional segmentation arguments",
            "args": [
                seg_ace.image_size,
                seg_ace.nr_workers,
                seg_ace.cache_rate,
                seg_ace.batch_size,
                seg_ace.monte_carlo,
                seg_ace.visualize_results,
                seg_ace.uncertainty_map,
                seg_ace.binarization_threshold,
                seg_ace.percentage_brain_patch_skip,
            ],
        },
        "conv_args": {
            "title": "optional conversion arguments",
            "args": [
                conv_tiff_nii.channum,
                conv_tiff_nii.chanprefix,
                conv_tiff_nii.channame,
                conv_tiff_nii.outnii,
                conv_tiff_nii.center,
                conv_tiff_nii.downzdim,
                conv_tiff_nii.prevdown,
                conv_tiff_nii.percentile_thr,
            ],
        },
        "reg_args": {
            "title": "optional registration arguments",
            "args": [
                reg_clar_allen.hemi,
                reg_clar_allen.allen_label,
                reg_clar_allen.allen_atlas,
                reg_clar_allen.side,
                reg_clar_allen.no_mosaic_fig,
                reg_clar_allen.olfactory_bulb,
                reg_clar_allen.skip_cor,
                reg_clar_allen.warp,
            ],
        },
        "vox_args": {
            "title": "optional voxelization arguments",
            "args": [
                seg_vox.xy_res,
                seg_vox.z_res,
            ],
        },
        "warp_args": {
            "title": "optional voxelization arguments",
            "args": [
                reg_warp_clar.input_folder,
                reg_warp_clar.input_nii,
                reg_warp_clar.seg_channel,
            ],
        },
        "clust_args": {
            "title": "optional cluster_wise arguments",
            "args": [
                stats_ace_clust.atlas_dir,
                stats_ace_clust.img_resolution,
                stats_ace_clust.smoothing_fwhm,
                stats_ace_clust.tfce_start,
                stats_ace_clust.tfce_step,
                stats_ace_clust.tfce_h,
                stats_ace_clust.tfce_e,
                stats_ace_clust.step_down_p,
                stats_ace_clust.mask_thr,
            ],
        },
        "corr_args": {
            "title": "optional correlational arguments",
            "args": [
                stats_ace_corr.pvalue_thr,
            ],
        },
        "heatmap_args": {
            "title": "optional heatmap arguments",
            "args": [
                stats_heatmap.group1,
                stats_heatmap.group2,
                stats_heatmap.vox,
                stats_heatmap.sigma,
                stats_heatmap.percentile,
                stats_heatmap.colourmap_pos,
                stats_heatmap.colourmap_neg,
                stats_heatmap.sagittal,
                stats_heatmap.coronal,
                stats_heatmap.axial,
                stats_heatmap.figure_dim,
                stats_heatmap.outfolder,
                stats_heatmap.outfile,
                stats_heatmap.extension,
                stats_heatmap.dpi,
            ],
        },
        "stats_args": {
            "title": "optional statistics arguments",
            "args": [
                stats_ace.atlas_dir,
                stats_ace.p_outfile,
            ],
        },
    }

    create_parser_arguments(parser, groups_dict)

    # Now you can use the parser as usual
    args = parser.parse_args()
