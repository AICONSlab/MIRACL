import argparse
from pathlib import Path
import os

from numpy import require
from miracl.seg import ace_parser


class ACEWorkflowParser:
    """
    Command-line argument parser for AI-based Cartography of Ensembles (ACE) segmentation method workflow.

    :param input: A required string argument that specifies the input file path.
    :param output: A required string argument that specifies the output file path.
    :param model: A required string argument that specifies the model type. It has three possible choices: 'unet', 'unetr', and 'ensemble'.
    :param voxel: A required flag that takes three arguments of type int.
    :param visualize: An optional boolean flag that is set to `True` if present.
    :param map: An optional boolean flag that is set to `True` if present.

    :returns: The parsed arguments.
    """

    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> argparse.ArgumentParser:
        # Define custom parser
        parser = argparse.ArgumentParser(
            prog="miracl flow ace",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False,  # Used for separating args
            description="""
  1) Segments images with ACE
  2) Convert raw tif/tiff files to nifti for registration
  3) Registers CLARITY data (down-sampled images) to Allen Reference mouse brain atlas
  4) Voxelizes segmentation results into density maps with Allen atlas resolution
  5) Warps downsampled CLARITY data/channels from native space to Allen atlas""",
            usage="""%(prog)s -sai input_folder -sao output_folder -sam model_type -pcsw wild_type_dir -pcsd disease_group_dir -pcso output_directory""",
        )

        # Define custom headers for args to separate required and optional
        required_args = parser.add_argument_group("required arguments")
        seg_args = parser.add_argument_group("Optional segmentation arguments")
        conv_args = parser.add_argument_group("optional conversion arguments")
        reg_args = parser.add_argument_group("Optional registration arguments")
        vox_args = parser.add_argument_group("Optional voxelization arguments")
        warp_args = parser.add_argument_group("Optional warping arguments")
        heatmap_args = parser.add_argument_group("Optional heatmap arguments")
        perm_args = parser.add_argument_group("optional permutation arguments")
        optional_args = parser.add_argument_group("optional arguments")

        # INFO: ACE segmentation parser

        # Parser for input folder i.e. location of the data
        required_args.add_argument(
            "-sai",
            "--sa_input_folder",
            type=str,
            required=True,
            help="path to raw tif/tiff data folder",
        )
        # Parser for output folder i.e. location where results are stored
        required_args.add_argument(
            "-sao",
            "--sa_output_folder",
            type=str,
            required=True,
            help="path to output file folder",
        )
        # Parser to select model type
        required_args.add_argument(
            "-sam",
            "--sa_model_type",
            type=str,
            choices=["unet", "unetr", "ensemble"],
            required=True,
            help="model architecture",
        )
        # Parser to select voxel size
        seg_args.add_argument(
            "-sas",
            "--sa_image_size",
            nargs=3,
            type=str,
            required=False,
            metavar=("height", "width", "depth"),
            help="image size (type: int; default: fetched from image header)",
        )
        # Parser to select voxel size
        seg_args.add_argument(
            "-sar",
            "--sa_resolution",
            nargs=3,
            type=str,
            required=False,
            metavar=("X-res", "Y-res", "Z-res"),
            help="voxel size (type: %(type)s)",
        )
        # Parser for number of workers
        seg_args.add_argument(
            "-saw",
            "--sa_nr_workers",
            type=int,
            required=False,
            default=4,
            help="number of cpu cores deployed to pre-process image patches in parallel (type: %(type)s; default: %(default)s)",
        )
        # Parser for cache rate
        seg_args.add_argument(
            "-sac",
            "--sa_cache_rate",
            type=float,
            required=False,
            default=0.0,
            help="percentage of raw data that is loaded into cpu during segmentation (type: %(type)s; default: %(default)s)",
        )
        # Parser for sw batch size
        seg_args.add_argument(
            "-sasw",
            "--sa_sw_batch_size",
            type=int,
            required=False,
            default=4,
            help="number of image patches being processed by the model in parallel on gpu (type: %(type)s; default: %(default)s)",
        )
        # Boolean to choose if whether it is needed to MC
        seg_args.add_argument(
            "-samc",
            "--sa_monte_dropout",
            action="store_true",
            default=False,
            help="use Monte Carlo dropout (default: %(default)s)",
        )
        # Boolean to choose if results are visualized
        seg_args.add_argument(
            "-sav",
            "--sa_visualize_results",
            action="store_true",
            default=False,
            help="visualizing model output after predictions (default: %(default)s)",
        )
        # Boolean to choose if an uncertainty map is created
        seg_args.add_argument(
            "-sau",
            "--sa_uncertainty_map",
            action="store_true",
            default=False,
            help="enable map (default: %(default)s)",
        )

        # INFO: Conversion parser

        # required_args.add_argument(
        #     "-ctnf",
        #     "--ctn_folder",
        #     type=str,
        #     required=True,
        #     metavar="dir",
        #     help="Input CLARITY TIFF folder/dir",
        # )
        #
        # optional_args.add_argument(
        #     "-ctnw",
        #     "--ctn_work_dir",
        #     type=str,
        #     metavar="dir",
        #     default=os.path.abspath(os.getcwd()),
        #     help="Output directory (default: %(default)s)",
        # )
        conv_args.add_argument(
            "-ctnd",
            "--ctn_down",
            type=int,
            metavar="",
            default=5,
            help="Down-sample ratio (default: %(default)s)",
        )
        conv_args.add_argument(
            "-ctncn",
            "--ctn_channum",
            type=int,
            default=0,
            metavar="",
            help="Chan # for extracting single channel from multiple channel data (default: %(default)s)",
        )
        conv_args.add_argument(
            "-ctncp",
            "--ctn_chanprefix",
            type=str,
            metavar="",
            default=None,
            help="Chan prefix (string before channel number in file name). ex: C00",
        )
        conv_args.add_argument(
            "-ctnch",
            "--ctn_channame",
            type=str,
            metavar="",
            default="eyfp",
            help="Output chan name (default: %(default)s) ",
        )
        conv_args.add_argument(
            "-ctno",
            "--ctn_outnii",
            type=str,
            metavar="",
            default='clarity',
            help="Output nii name (script will append downsample ratio & channel info to given name)",
        )
        conv_args.add_argument(
            "-ctnvx",
            "--ctn_resx",
            type=float,
            metavar="",
            default=5,
            help="Original resolution in x-y plane in um (default: %(default)s)",
        )
        conv_args.add_argument(
            "-ctnvz",
            "--ctn_resz",
            type=float,
            metavar="",
            default=5,
            help="Original thickness (z-axis resolution / spacing between slices) in um (default: %(default)s) ",
        )
        conv_args.add_argument(
            "-ctnc",
            "--ctn_center",
            type=int,
            nargs="+",
            metavar="",
            default=[0, 0, 0],
            help="Nii center (default: 0,0,0 ) corresponding to Allen atlas nii template",
        )
        conv_args.add_argument(
            "-ctndz",
            "--ctn_downzdim",
            type=int,
            metavar="",
            default=1,
            help="Down-sample in z dimension, binary argument, (default: %(default)s) => yes",
        )
        conv_args.add_argument(
            "-ctnpd",
            "--ctn_prevdown",
            type=int,
            metavar="",
            default=1,
            help="Previous down-sample ratio, if already downs-sampled",
        )

        # INFO: Registration parser

        # FIX: This should be the input folder from ACE?
        # required_args.add_argument(
        #     "-rcai",
        #     "--rca_input_nii",
        #     type=str,
        #     required=True,
        #     help="input down-sampled clarity nii\nPreferably auto-fluorescence channel data (or Thy1_EYFP if no auto chan) file name should have '##x_down' like '05x_down' (meaning 5x downsampled) -> ex. stroke13_05x_down_Ref_chan.nii.gz [this should be accurate as it is used for allen label upsampling to clarity]",
        # )
        # FIX: This should be the input folder from ACE?
        # required_args.add_argument(
        #     "-rcar",
        #     "--rca_output_folder",
        #     type=str,
        #     required=True,
        #     help="path to results directory",
        # )
        reg_args.add_argument(
            "-rcao",
            "--rca_orient_code",
            type=str,
            default="ALS",
            help="to orient nifti from original orientation to 'standard/Allen' orientation, (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcam",
            "--rca_hemi",
            type=str,
            choices=["combined", "split"],
            default="combined",
            help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcav",
            "--rca_voxel_size",
            type=int,
            choices=[10, 25, 50],
            default=10,
            help="labels voxel size/Resolution in um (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcal",
            "--rca_allen_label",
            type=str,
            default="annotation_hemi_combined_10um.nii.gz",
            help="input Allen labels to warp. Input labels could be at a different depth than default labels, If l. is specified (m & v cannot be specified) (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcaa",
            "--rca_allen_atlas",
            type=str,
            default="None",
            help="custom Allen atlas (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcas",
            "--rca_side",
            type=str,
            choices=["rh", "lh"],
            default="rh",
            help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcanm",
            "--rca_no_mosaic_fig",
            action="store_const",
            const=0,
            default=1,
            help="by default a mosaic figure (.png) of allen labels registered to clarity will be saved. If this flag is set, the mosaic figure will not be saved.",
        )
        reg_args.add_argument(
            "-rcab",
            "--rca_olfactory_bulb",
            type=int,
            choices=[0, 1],
            default=0,
            help="include olfactory bulb in brain (default: %(default)s)",
        )
        reg_args.add_argument(
            "-rcap",
            "--rca_skip_cor",
            action="store_const",
            const=1,
            default=0,
            help="if utilfn intensity correction already ran, skip correction inside registration (default: False)",
        )
        reg_args.add_argument(
            "-rcaw",
            "--rca_warp",
            action="store_const",
            const=1,
            default=0,
            help="warp high-res clarity to Allen space (default: False)",
        )

        # INFO: Voxelization parser

        vox_args.add_argument(
            "-rvas",
            "--rva_input_tif",
            type=str,
            default=None,
            help="segmented tif file",
        )
        # FIX: Should be inherited from above -rcav argument
        vox_args.add_argument(
            "-rvav",
            "--rva_voxel_size",
            type=int,
            choices=[10, 25, 50],
            default=10,
            help="labels voxel size/Resolution in um (default: %(default)s)",
        )
        vox_args.add_argument(
            "-rvad",
            "--rva_downsample",
            type=int,
            default=2,
            help="down sample ratio, recommended: 2 <= ratio <= 5 (default: %(default)s)",
        )

        # INFO: Warping parser

        # FIX: This should be the input folder from ACE?
        warp_args.add_argument(
            "-rwcr",
            "--rwc_input_folder",
            type=str,
            default=None,
            help="path to CLARITY registration folder",
        )
        warp_args.add_argument(
            "-rwcn",
            "--rwc_input_nii",
            type=str,
            default=None,
            help="path to downsampled CLARITY nii file to warp",
        )
        # FIX: Maybe exclude? Should be coming from ACE?
        warp_args.add_argument(
            "-rwcf",
            "--rwc_file",
            type=str,
            required=True,
            help="path to downsampled CLARITY nii file to warp",
        )
        # FIX: Will always be required as data is piped from voxelization fn
        warp_args.add_argument(
            "-rwcc",
            "--rwc_seg_channel",
            type=str,
            default="green",
            help="Segmentation channel (ex. green) - required if voxelized seg is input",
        )

        # INFO: Permutation cluster stats parser

        required_args.add_argument(
            "-pcsw",
            "--pcs_wild_type",
            help="wild type group directory (should contain warped voxelized nifti files)",
            required=True,
        )
        required_args.add_argument(
            "-pcsd",
            "--pcs_disease",
            help="disease group directory (should contain warped voxelized nifti files)",
            required=True,
        )
        required_args.add_argument(
            "-pcso", "--pcs_output", help="path of output directory", required=True
        )
        perm_args.add_argument(
            "-pcsa",
            "--pcs_atlas_dir",
            help="path of atlas directory",
            default="miracl_home",
        )
        perm_args.add_argument(
            "-pcsn",
            "--pcs_num_perm",
            type=int,
            help="number of permutations",
            default=100,
        )
        perm_args.add_argument(
            "-pcsr",
            "--pcs_img_resolution",
            type=int,
            help="resolution of images in um",
            default=25,
        )
        perm_args.add_argument(
            "-pcsfwhm",
            "--pcs_smoothing_fwhm",
            type=int,
            help="fwhm of Gaussian kernel in pixel",
            default=3,
        )
        perm_args.add_argument(
            "-pcsstart",
            "--pcs_tfce_start",
            type=float,
            help="tfce threshold start",
            default=0.01,
        )
        perm_args.add_argument(
            "-pcsstep",
            "--pcs_tfce_step",
            type=float,
            help="tfce threshold step",
            default=10,
        )
        perm_args.add_argument(
            "-pcsc",
            "--pcs_cpu_load",
            type=float,
            help="Percent of cpus used for parallelization",
            default=0.9,
        )
        perm_args.add_argument(
            "-pcsh", "--pcs_tfce_h", type=float, help="tfce H power", default=2
        )
        perm_args.add_argument(
            "-pcse", "--pcs_tfce_e", type=float, help="tfce E power", default=0.5
        )
        perm_args.add_argument(
            "-pcssp",
            "--pcs_step_down_p",
            type=float,
            help="step_down_p value",
            default=0.3,
        )
        perm_args.add_argument(
            "-pcsm",
            "--pcs_mask_thr",
            type=int,
            help="percentile to be used for binarizing difference of the mean",
            default=95,
        )

        # INFO: Heatmap parser

        heatmap_args.add_argument(
            "-shg1",
            "--sh_group1",
            type=str,
            help="path to group 1 directory",
            default=None,
        )
        heatmap_args.add_argument(
            "-shg2",
            "--sh_group2",
            type=str,
            help="path to group 2 directory",
            default=None,
        )
        heatmap_args.add_argument(
            "-shv",
            "--sh_vox",
            type=int,
            choices=[10, 25, 50],
            help="voxel size/Resolution in um",
            default=None,
        )
        heatmap_args.add_argument(
            "-shgs",
            "--sh_sigma",
            type=int,
            help="Gaussian smoothing sigma (default: %(default)s)",
            default=4,
        )
        heatmap_args.add_argument(
            "-shp",
            "--sh_percentile",
            type=int,
            help="percentile (%%) threshold for registration-to-input data check svg animation (default: %(default)s)",
            default=10,
        )
        heatmap_args.add_argument(
            "-shcp",
            "--sh_colourmap_pos",
            type=str,
            help="matplotlib colourmap for positive values (default: %(default)s)",
            default="Reds",
        )
        heatmap_args.add_argument(
            "-shcn",
            "--sh_colourmap_neg",
            type=str,
            help="matplotlib colourmap for negative values (default: %(default)s)",
            default="Blues",
        )

        heatmap_args.add_argument(
            "-shs",
            "--sh_sagittal",
            nargs=5,
            type=int,
            help="slicing across sagittal axis. \n 5 Arguments: start_slice slice_interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        heatmap_args.add_argument(
            "-shc",
            "--sh_coronal",
            nargs=5,
            type=int,
            help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        heatmap_args.add_argument(
            "-sha",
            "--sh_axial",
            nargs=5,
            type=int,
            help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        heatmap_args.add_argument(
            "-shf",
            "--sh_figure_dim",
            type=float,
            nargs=2,
            help="figure width and height",
            default=None,
        )
        heatmap_args.add_argument(
            "-shd",
            "--sh_dir_outfile",
            type=str,
            help="Output file directory (default: %(default)s)",
            default=os.getcwd(),
        )
        heatmap_args.add_argument(
            "-sho",
            "--sh_outfile",
            nargs="+",
            type=str,
            help="Output filenames (default: %(default)s)",
            default=["group_1", "group_2", "group_difference"],
        )
        heatmap_args.add_argument(
            "-she",
            "--sh_extension",
            type=str,
            help="heatmap figure extension (default: %(default)s)",
            default="tiff",
        )
        heatmap_args.add_argument(
            "-shdpi",
            "--sh_dpi",
            type=int,
            help="dots per inch (default: %(default)s)",
            default=500,
        )

        # Add help back under optional args header
        optional_args.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="show this help message and exit",
        )

        return parser

    def parse_args(self):
        return self.parser.parse_args()


if __name__ == "__main__":
    args_parser = ACEWorkflowParser()
    args = args_parser.parse_args()