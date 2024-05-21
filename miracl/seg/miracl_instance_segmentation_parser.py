import argparse
from pathlib import Path

PROG_NAME = "instance"
FULL_PROG_NAME = f"miracl seg {PROG_NAME}"

class MIRACLInstanceSegParser(argparse.ArgumentParser):
    """
    Command-line argument parser for instance segmentation step of ACE segmentation.
    """

    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=FULL_PROG_NAME,
            description="Instance segmentation step of ACE segmentation",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            usage="""%(prog)s -i <input_seg_folder> [ -o <output_folder> ] [ -g <glob_pattern> ] [ -p <percentage_brain_patch_skip> ]""",
            add_help=False,
        )
        required_args = parser.add_argument_group("Required arguments")
        optional_args = parser.add_argument_group("Optional arguments")
        # Parser for input folder i.e. location of the data
        required_args.add_argument(
            "-i",
            "--input_folder",
            type=str,
            required=True,
            action=InputAction,
            help="Path to ACE segmentation output folder (generated_patches/)",
        )
        required_args.add_argument(
            "-r",
            "--raw_input_folder",
            type=str,
            required=True,
            help="Path to raw clarity tiff folder",
        )
        # Parser for output folder i.e. location where results are stored
        optional_args.add_argument(
            "-o",
            "--output_folder",
            type=str,
            required=False,
            default=None,
            help="Path to output folder (default: <input_folder>.parent /cc_slices/)",
        )
        # Parser for glob pattern i.e. pattern to match files
        optional_args.add_argument(
            "-g",
            "--glob_pattern",
            type=str,
            required=False,
            default="[A-Zo]*patch_*.tiff",
            help="Glob pattern to match files in <input_folder> (default: %(default)s)",
        )
        # Parser for percentage of brain patch skip
        optional_args.add_argument(
            "-p",
            "--percentage_brain_patch_skip",
            type=float,
            required=False,
            default=0.0,
            help="Percentage of brain patch skip (default: %(default)s)",
        )
        optional_args.add_argument(
            "--no-stack",
            action="store_true",
            help="Stack the patches to form image slices. Default is to stack the patches.",
        )
        optional_args.add_argument(
            "-c",
            "--cpu-load",
            type=float,
            help="Percentage of CPU load to use (default: %(default)s)",
            required=False,
            default=0.95,
        )
        # Parser for help
        optional_args.add_argument(
            "-h", "--help", action="help", help="Show this help message and exit"
        )
        return parser


class InputAction(argparse.Action):
    FIELD_NAME = "output_folder"

    def __call__(self, parser, namespace, values, option_string=None):
        # set the value for input folder
        setattr(namespace, self.dest, Path(values).absolute())
        default_output_dir = Path(values).absolute().parent / "cc_slices"
        # set the value for the output folder
        setattr(namespace, self.FIELD_NAME, default_output_dir)
