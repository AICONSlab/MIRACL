import argparse
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
import subprocess
import pathlib

from miracl import miracl_logger
from miracl.stats import (
    miracl_stats_ace_clusterwise,
    miracl_stats_ace_correlation,
    miracl_stats_ace_parser,
)

logger = miracl_logger.logger

MIRACL_HOME = Path(os.environ["MIRACL_HOME"])


class Clusterwise(ABC):
    @abstractmethod
    def cluster(self, args, output_dir_arg):
        pass


class Correlation(ABC):
    @abstractmethod
    def correlate(self, args, corr_output_folder, p_value, f_obs, mean_diff):
        pass


class ACEClusterwise(Clusterwise):
    def cluster(self, args, output_dir_arg, pvalue_plot_cmd):
        print("  clusterwise comparison...")
        miracl_stats_ace_clusterwise.main(args, output_dir_arg)
        logger.debug("Calling clusterwise comparison fn here")
        logger.debug(f"Atlas dir arg: {args.u_atlas_dir}")
        print("  plotting p-values...")
        subprocess.Popen(pvalue_plot_cmd, shell=True).wait()

class ACECorrelation(Correlation):
    def correlate(self, args, corr_output_folder, p_value, f_obs, mean_diff):
        print("  correlating...")
        # TODO: update python version for correlation function
        # miracl_stats_ace_correlation.main(
        #     args, corr_output_folder, p_value, f_obs, mean_diff
        # )
        print("  correlation function not currently available...skipping")
        print("  correlation will be available in a future release.")


class Interface:
    def __init__(self, clustering: Clusterwise, correlation: Correlation):
        self.clustering = clustering
        self.correlation = correlation

    def run_fns(self, args):
        if not hasattr(args, "pcs_control") or not hasattr(args, "pcs_treated"):
            args.pcs_control = args.control
            args.pcs_treated = args.treated
            # assert they are not None
            assert args.pcs_control is not None, \
                "Control group voxelized segmented tif file path is required (--control)."
            assert args.pcs_treated is not None, \
                "Treated group voxelized segmented tif file path is required (--treated)."

        ace_flow_cluster_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "clust_final"
        )

        ace_flow_corr_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "corr_final"
        )

        pvalue_plot_cmd = ConstructPvalueCmd.test_none_args(
            args.sh_sagittal, args.sh_coronal, args.sh_axial, args.sh_figure_dim
        )
        pvalue_plot_cmd = ConstructPvalueCmd.construct_final_pvalue_cmd(
            args, ace_flow_cluster_output_folder, pvalue_plot_cmd
        )

        self.clustering.cluster(args, ace_flow_cluster_output_folder, pvalue_plot_cmd)

        p_value_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "p_values.nii.gz"
        )
        f_obs_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "f_obs.nii.gz"
        )
        mean_diff_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "diff_mean.nii.gz"
        )

        self.correlation.correlate(
            args,
            ace_flow_corr_output_folder,
            p_value_input,
            f_obs_input,
            mean_diff_input,
        )


class FolderCreator:
    @staticmethod
    def create_folder(arg_var, *name_vars):
        folder = Path(arg_var)
        for name_var in name_vars:
            folder = folder / name_var
        folder.mkdir(parents=True, exist_ok=True)
        return folder


class GetCorrInput:
    @staticmethod
    def check_corr_input_exists(dir_var, nifti_name_var):
        dir_path = Path(dir_var)
        file_path = dir_path / nifti_name_var
        if file_path.is_file():
            return file_path
        else:
            raise FileNotFoundError(
                f"'{Path(file_path.name)}' does not exist at '{dir_path}'. Did you run the ACE workflow yet?"
            )
        
class ConstructPvalueCmd:
    """Class for constructing the p-value command used by
    `miracl/stats/miracl_stats_ace_pvalue.py`
    """

    @staticmethod
    def test_none_args(
        sagittal: argparse.Namespace,
        coronal: argparse.Namespace,
        axial: argparse.Namespace,
        dim: argparse.Namespace,
    ) -> str:
        """This funcrion checks if arguments are provided for --sh_sagittal,
        --sh_coronal, --sh_axial and --sh_figure_dim and composes the
        'miracl/stats/miracl_stats_ace_pvalue.py' command accordingly. This is necessary
        because the pvalue fn requires nargs=5 for the axes and nargs=2 for
        the figure dimensions.

        :param sagittal: Argument for sagittal axis.
        :type sagittal: argparse.Namespace
        :param coronal: Argument for coronal axis.
        :type coronal: argparse.Namespace
        :param axial: Argument for axial axis.
        :type axial: argparse.Namespace
        :param dim: Figure dimensions argument.
        :type dim: argparse.Namespace
        :return: A string with the appropriately crafted pvalue command.
        :rtype: str
        """

        def arg_checker(
            prev_cmd: str, arg: argparse.Namespace, arg_name: str, flag: str
        ) -> str:
            """
            This is a nested function that performs the actual checks for
            each provided argument.
            """
            if arg is None:
                logger.debug(f"No arguments for {arg_name} provided")
            else:
                logger.debug(f"Arguments for {arg_name} provided")
                prev_cmd += f"-{flag} {' '.join(map(str, arg))} "

            return prev_cmd

        # Define base cmd to add on to
        base_cmd = "python /code/miracl/stats/miracl_stats_ace_pvalue.py "

        saggital_result = arg_checker(base_cmd, sagittal, "sagittal", "s")
        coronal_result = arg_checker(saggital_result, coronal, "coronal", "c")
        axial_result = arg_checker(coronal_result, axial, "axial", "a")
        final_result = arg_checker(axial_result, dim, "figure dimensions", "f")

        return final_result
    
    @staticmethod
    def construct_final_pvalue_cmd(
        args: argparse.Namespace,
        ace_flow_pvalue_output_folder: pathlib.Path,
        tested_pvalue_cmd: str,
    ) -> str:
        """Take existing pvalue command and add additional arguments to it.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :param ace_flow_pvalue_output_folder: folder to save the plot to ('clust_final/')
        :type ace_flow_pvalue_output_folder: pathlib.Path
        :param tested_pvalue_cmd: existing pvalue command with args (from `test_none_args`)
        :type tested_pvalue_cmd: str
        :return: final pvalue command with args that can be executed in CLI
        :rtype: str
        """
        tested_pvalue_cmd += f"\
            -p {ace_flow_pvalue_output_folder / 'p_values.nii.gz'} \
            -atl {'/code/atlases/ara'} \
            -v {args.rwc_voxel_size} \
            -gs {args.sh_sigma} \
            -cp {args.sh_colourmap_pos} \
            -cn {args.sh_colourmap_neg} \
            -d {ace_flow_pvalue_output_folder} \
            -o {args.p_outfile} \
            -e {args.sh_extension} \
            --dpi {args.sh_dpi} \
            -m {args.rca_hemi} \
            -si {args.rca_side}"

        return tested_pvalue_cmd


def main(args):
    clustering = ACEClusterwise()
    correlation = ACECorrelation()

    ace_stats_interface = Interface(clustering, correlation)
    results = ace_stats_interface.run_fns(args)


if __name__ == "__main__":
    args = miracl_stats_ace_parser.ACEStatsParser().parsefn().parse_args()
    main(args)
