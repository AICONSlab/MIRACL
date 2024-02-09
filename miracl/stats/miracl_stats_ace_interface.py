import argparse
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path

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
    def cluster(self, args, output_dir_arg):
        print("  clusterwise comparison...")
        miracl_stats_ace_clusterwise.main(args, output_dir_arg)
        logger.debug("Calling clusterwise comparison fn here")
        logger.debug(f"Atlas dir arg: {args.u_atlas_dir}")


class ACECorrelation(Correlation):
    def correlate(self, args, corr_output_folder, p_value, f_obs, mean_diff):
        print("  correlating...")
        miracl_stats_ace_correlation.main(
            args, corr_output_folder, p_value, f_obs, mean_diff
        )
        logger.debug("Calling correlation fn here")
        logger.debug(f"Atlas dir arg: {args.u_atlas_dir}")


class Interface:
    def __init__(self, clustering: Clusterwise, correlation: Correlation):
        self.clustering = clustering
        self.correlation = correlation

    def run_fns(self, args):
        if args.control is None or args.experiment is None:
            args.pcs_control = args.control
            args.pcs_experiment = args.experiment

        ace_flow_cluster_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "clust_final"
        )

        ace_flow_corr_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "corr_final"
        )

        self.clustering.cluster(args, ace_flow_cluster_output_folder)

        p_value_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "p_values.nii.gz"
        )
        f_obs_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "f_obs.nii.gz"
        )
        mean_diff_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "diff_mean.nii.gz"
        )

        # self.correlation.correlate(
        #     args,
        #     ace_flow_corr_output_folder,
        #     p_value_input,
        #     f_obs_input,
        #     mean_diff_input,
        # )


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


def main(args):
    clustering = ACEClusterwise()
    correlation = ACECorrelation()

    ace_stats_interface = Interface(clustering, correlation)
    results = ace_stats_interface.run_fns(args)


if __name__ == "__main__":
    args = miracl_stats_ace_parser.ACEStatsParser().parsefn().parse_args()
    main(args)
