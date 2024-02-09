import argparse
import os
from pathlib import Path


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

        single_multi_args_group.add_argument(
            "-c",
            "--control",
            type=str,
            metavar=(
                "CONTROL_BASE_DIR",
                "CONTROL_VOXILIZED_SEGMENTED_TIF_EXAMPLE_PATH",
            ),
            help="FIRST: path to base control directory.\nSECOND: example path to control subject voxelized tif file (voxelized_seg_*.nii.gz)",
            nargs=2,
        )

        single_multi_args_group.add_argument(
            "-e",
            "--experiment",
            type=str,
            metavar=(
                "EXPERIMENT_BASE_DIR",
                "EXPERIMENT_VOXILIZED_SEGMENTED_TIF_EXAMPLE_PATH",
            ),
            help="FIRST: path to base experiment directory.\nSECOND: example path to experiment subject voxelized tif file (voxelized_seg_*.nii.gz)",
            nargs=2,
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
            default="miracl_home",
            help="path of atlas directory (default: '/code/atlases/ara/')",
        )

        utility_args.add_argument(
            "-rcav",
            "--rca_voxel_size",
            type=int,
            choices=[10, 25, 50],
            default=10,
            help="labels voxel size/Resolution in um (default: %(default)s)",
        )

        corr_args.add_argument(
            "-cft",
            "--cf_pvalue_thr",
            type=float,
            help="threshold for binarizing p value",
            default=0.05,
        )

        perm_args.add_argument(
            "-pcsn",
            "--pcs_num_perm",
            type=int,
            help="number of permutations",
            default=100,
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

        required_args.add_argument(
            "-rwcv",
            "--rwc_voxel_size",
            type=int,
            default=25,
            choices=[10, 25, 50],
            help="voxel size/Resolution in um for warping (default: %(default)s)",
        )

        return parser


if __name__ == "__main__":
    args_parser = ACEStatsParser()
    args = args_parser.parsefn().parse_args()
