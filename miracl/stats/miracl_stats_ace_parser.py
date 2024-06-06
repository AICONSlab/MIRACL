import argparse
import os
from pathlib import Path

ARA_ENV = "aradir"

class ACEStatsParser:
    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Statistics functions for AI-based Cartography of Ensembles (ACE) segmentation method. These functions assume that the ACE workflow has already been completed."
        )

        single_multi_args_group = parser.add_argument_group("Comparison arguments")
        required_args = parser.add_argument_group("required arguments")
        utility_args = parser.add_argument_group("utility arguments")
        corr_args = parser.add_argument_group("optional correlation arguments")
        perm_args = parser.add_argument_group("optional permutation arguments")
        pvalue_args = parser.add_argument_group("optional pvalue plot arguments")

        single_multi_args_group.add_argument(
            "-c",
            "--control",
            type=str,
            metavar=(
                "CONTROL_BASE_DIR",
                "CONTROL_VOXILIZED_SEGMENTED_TIF_EXAMPLE_PATH",
            ),
            help="FIRST: path to base control directory.\nSECOND: example path to control subject voxelized tif file (voxelized_seg_*.nii.gz)",
            nargs="+",
        )

        single_multi_args_group.add_argument(
            "-t",
            "--treated",
            type=str,
            metavar=(
                "TREATED_BASE_DIR",
                "TREATED_VOXILIZED_SEGMENTED_TIF_EXAMPLE_PATH",
            ),
            help="FIRST: path to base treated directory.\nSECOND: example path to treated subject voxelized tif file (voxelized_seg_*.nii.gz)",
            nargs="+",
        )

        required_args.add_argument(
            "-sao",
            "--sa_output_folder",
            type=str,
            required=True,
            help="path to output file folder",
        )

        utility_args.add_argument(
            "-ua",
            "--u_atlas_dir",
            default=os.environ.get(ARA_ENV, None),
            help="path of atlas directory (default: %(default)s)",
        )

        utility_args.add_argument(
            "-rcav",
            "--rca_voxel_size",
            type=int,
            choices=[10, 25, 50],
            default=10,
            help="labels voxel size/Resolution in um (default: %(default)s)",
        )

        utility_args.add_argument(
            "-rcam",
            "--rca_hemi",
            type=str,
            choices=["combined", "split"],
            default="combined",
            help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
        )
        utility_args.add_argument(
            "-rcas",
            "--rca_side",
            type=str,
            choices=["rh", "lh"],
            default="rh",
            help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",
        )

        corr_args.add_argument(
            "-cft",
            "--cf_pvalue_thr",
            type=float,
            help="threshold for binarizing p value",
            default=0.05,
        )

        perm_args.add_argument(
            "-sctpn",
            "--sctp_num_perm",
            type=int,
            help="number of permutations",
            default=100,
        )
        perm_args.add_argument(
            "-sctpfwhm",
            "--sctp_smoothing_fwhm",
            type=int,
            help="fwhm of Gaussian kernel in pixel",
            default=3,
        )
        perm_args.add_argument(
            "-sctpstart",
            "--sctp_tfce_start",
            type=float,
            help="tfce threshold start",
            default=0.01,
        )
        perm_args.add_argument(
            "-sctpstep",
            "--sctp_tfce_step",
            type=float,
            help="tfce threshold step",
            default=10,
        )
        perm_args.add_argument(
            "-sctpc",
            "--sctp_cpu_load",
            type=float,
            help="Percent of cpus used for parallelization",
            default=0.9,
        )
        perm_args.add_argument(
            "-sctph",
            "--sctp_tfce_h",
            type=float,
            help="tfce H power",
            default=2
        )
        perm_args.add_argument(
            "-sctpe",
            "--sctp_tfce_e",
            type=float,
            help="tfce E power",
            default=0.5
        )
        perm_args.add_argument(
            "-sctpsp",
            "--sctp_step_down_p",
            type=float,
            help="step_down_p value",
            default=0.3,
        )
        perm_args.add_argument(
            "-sctpm",
            "--sctp_mask_thr",
            type=int,
            help="percentile to be used for binarizing difference of the mean",
            default=95,
        )

        required_args.add_argument(
            "-rwcv",
            "--rwc_voxel_size",
            type=int,
            default=25,
            choices=[10, 25, 50],
            help="voxel size/Resolution in um for warping (default: %(default)s)",
        )

        pvalue_args.add_argument(
            "-shgs",
            "--sh_sigma",
            type=int,
            help="Gaussian smoothing sigma (default: %(default)s)",
            default=4,
        )
        pvalue_args.add_argument(
            "-shcp",
            "--sh_colourmap_pos",
            type=str,
            help="matplotlib colourmap for positive values (default: %(default)s)",
            default="Reds",
        )
        pvalue_args.add_argument(
            "-shcn",
            "--sh_colourmap_neg",
            type=str,
            help="matplotlib colourmap for negative values (default: %(default)s)",
            default="Blues",
        )

        pvalue_args.add_argument(
            "-shs",
            "--sh_sagittal",
            nargs=5,
            type=int,
            help="slicing across sagittal axis. \n 5 Arguments: start_slice slice_interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        pvalue_args.add_argument(
            "-shc",
            "--sh_coronal",
            nargs=5,
            type=int,
            help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        pvalue_args.add_argument(
            "-sha",
            "--sh_axial",
            nargs=5,
            type=int,
            help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
            default=None,
        )
        pvalue_args.add_argument(
            "-shf",
            "--sh_figure_dim",
            type=float,
            nargs=2,
            help="figure width and height",
            default=None,
        )
        pvalue_args.add_argument(
            "-po",
            "--p_outfile",
            type=str,
            help="Output filenames (default: %(default)s)",
            default="pvalue_heatmap",
        )
        pvalue_args.add_argument(
            "-she",
            "--sh_extension",
            type=str,
            help="heatmap figure extension (default: %(default)s)",
            default="tiff",
        )
        pvalue_args.add_argument(
            "-shdpi",
            "--sh_dpi",
            type=int,
            help="dots per inch (default: %(default)s)",
            default=500,
        )

        return parser


if __name__ == "__main__":
    args_parser = ACEStatsParser()
    args = args_parser.parsefn().parse_args()
