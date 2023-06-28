import argparse
import os
from pathlib import Path
# from typing import List, Tuple


class aceParser:
    """
    Command-line argument parser for AI-based Cartography of neural Ensembles (ACE) segmentation method.

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
        parser = argparse.ArgumentParser(
            description="AI-based Cartography of neural Ensembles (ACE) segmentation method"
        )
        # Parser for input folder i.e. location of the data
        parser.add_argument(
            "-i",
            "--input_folder",
            type=self._readable_file,
            required=True,
            help="input file path",
        )
        # Parser for output folder i.e. location where results are stored
        parser.add_argument(
            "-o",
            "--output_folder",
            type=self._readable_file,
            required=True,
            help="output file path",
        )
        # Parser to select model type
        parser.add_argument(
            "-m",
            "--model_type",
            type=self._model_format,
            choices=["unet", "unetr", "ensemble"],
            required=True,
            help="model type",
        )
        # Parser to select voxel size
        parser.add_argument(
            "-s",
            "--image_size",
            nargs=3,
            type=self._validate_img_size,
            required=True,
            metavar=("height", "width", "depth"),
            help="image size (type: %(type)s)"
        )
        # Parser to select voxel size
        parser.add_argument(
            "-r",
            "--voxel_res",
            nargs=3,
            type=self._validate_vox_res,
            required=False,
            metavar=("X-res", "Y-res", "Z-res"),
            help="voxel resolution (type: %(type)s)",
        )
        # Parser for number of workers
        parser.add_argument(
            "-w",
            "--nr_workers",
            type=int,
            required=False,
            default=4,
            help="set number of workers (type: %(type)s; default: %(default)s)"
        )
        # Parser for cache rate
        parser.add_argument(
            "-c",
            "--cache_rate",
            type=float,
            required=False,
            default=0.0,
            help="set cache rate (type: %(type)s; default: %(default)s)"
        )
        # Parser for sw batch size
        parser.add_argument(
            "-sw",
            "--sw_batch_size",
            type=int,
            required=False,
            default=4,
            help="set sw batch size (type: %(type)s; default: %(default)s)"
        )
        # Boolean to choose if whether it is needed to MC
        parser.add_argument(
            "-mc",
            "--monte_dropout",
            action="store_true",
            default=False,
            help="whether you need to MC (default: %(default)s)",
        )
        # Boolean to choose if results are visualized
        parser.add_argument(
            "-v",
            "--visualize_results",
            action="store_true",
            default=False,
            help="enable visualization (default: %(default)s)",
        )
        # Boolean to choose if an uncertainty map is created
        parser.add_argument(
            "-u",
            "--uncertainty_map",
            action="store_true",
            default=False,
            help="enable map (default: %(default)s)"
        )
        return parser

    # def parse_args(self) -> argparse.Namespace:
    #     """
    #     Parse the command-line arguments.
    #
    #     :returns: The parsed arguments.
    #     """
    #     args = self.parser.parse_args()
    #     self._validate_args(args)
    #     return args

    def _readable_file(self, folder_path):
        """
        Check if the path is a readable file.

        :param folder_path: The path to check.
        :returns: The path if it is a readable file.
        """
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            raise argparse.ArgumentTypeError(f"Folder '{folder_path}' does not exist")
        if not os.access(folder_path, os.R_OK):
            raise argparse.ArgumentTypeError(f"Folder '{folder_path}' is not readable")
        if not os.access(folder_path, os.W_OK):
            raise argparse.ArgumentTypeError(f"Folder '{folder_path}' is not writable")
        return folder_path.as_posix()

    def _model_format(self, choice: str) -> str:
        """
        Check if provided string is in correct format and converts it to lower case if it is not.

        :param choice: The user input string to check.
        :returns: The lower case version of the string input.
        """
        if isinstance(choice, str):
            return choice.lower()

    def _validate_vox_res(self, dim):
        """
        Validate the parsed arguments.

        :param args: The parsed arguments.
        """
        try:
            int_value = int(dim)
            if isinstance(int_value, int) and int_value <= 0:
                raise argparse.ArgumentTypeError(
                    f"'{int_value}' is an invalid integer. Voxel resolution must be in set N*."
                )
        except ValueError:
            try:
                float_value = float(dim)
                raise argparse.ArgumentTypeError(
                    f"'{float_value}' is an invalid float. Voxel resolution must be in set N*."
                )
            except ValueError:
                raise argparse.ArgumentTypeError(
                    f"'{dim}' is an invalid input. Voxel resolution must be in set N*."
                )

        return int(dim)

    def _validate_img_size(self, dim):
        """
        Validate the parsed arguments.

        :param args: The parsed arguments.
        """
        try:
            int_value = int(dim)
            if isinstance(int_value, int) and int_value <= 0:
                raise argparse.ArgumentTypeError(
                    f"'{int_value}' is an invalid integer. Image size must be in set N*."
                )
        except ValueError:
            try:
                float_value = float(dim)
                raise argparse.ArgumentTypeError(
                    f"'{float_value}' is an invalid float. Image size must be in set N*."
                )
            except ValueError:
                raise argparse.ArgumentTypeError(
                    f"'{dim}' is an invalid input. Image size must be in set N*."
                )

        return int(dim)


if __name__ == "__main__":
    args_parser = aceParser()
    args = args_parser.parse_args()