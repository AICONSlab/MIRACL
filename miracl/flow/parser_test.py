import argparse
import os


def parsefn():
    parser = argparse.ArgumentParser(
        description="",
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False,
    )
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-f",
        "--folder",
        type=str,
        required=True,
        metavar="dir",
        help="Input CLARITY TIFF folder/dir",
    )

    optional = parser.add_argument_group("optional arguments")

    optional.add_argument(
        "-w",
        "--work_dir",
        type=str,
        metavar="",
        default=os.path.abspath(os.getcwd()),
        help="Output directory (default: working directory)",
    )
    optional.add_argument(
        "-d", "--down", type=int, metavar="", help="Down-sample ratio (default: 5)"
    )
    optional.add_argument(
        "-cn",
        "--channum",
        type=int,
        metavar="",
        help="Chan # for extracting single channel from multiple channel data (default: 0)",
    )
    optional.add_argument(
        "-cp",
        "--chanprefix",
        type=str,
        metavar="",
        help="Chan prefix (string before channel number in file name). ex: C00",
    )
    optional.add_argument(
        "-ch",
        "--channame",
        type=str,
        metavar="",
        help="Output chan name (default: eyfp) ",
    )
    optional.add_argument(
        "-o",
        "--outnii",
        type=str,
        metavar="",
        help="Output nii name (script will append downsample ratio & channel info to given name)",
    )
    optional.add_argument(
        "-vx",
        "--resx",
        type=float,
        metavar="",
        help="Original resolution in x-y plane in um (default: 5)",
    )
    optional.add_argument(
        "-vz",
        "--resz",
        type=float,
        metavar="",
        help="Original thickness (z-axis resolution / spacing between slices) in um (default: 5) ",
    )
    optional.add_argument(
        "-c",
        "--center",
        type=int,
        nargs="+",
        metavar="",
        help="Nii center (default: 0,0,0 ) corresponding to Allen atlas nii template",
    )
    optional.add_argument(
        "-dz",
        "--downzdim",
        type=int,
        metavar="",
        help="Down-sample in z dimension, binary argument, (default: 1) => yes",
    )
    optional.add_argument(
        "-pd",
        "--prevdown",
        type=int,
        metavar="",
        help="Previous down-sample ratio, if already downs-sampled",
    )

    optional.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )

    return parser


if __name__ == "__main__":
    parser = parsefn()
    args = parser.parse_args()
