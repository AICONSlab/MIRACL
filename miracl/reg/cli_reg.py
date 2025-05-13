import os
import sys
import argparse
import subprocess
from miracl.reg import miracl_reg_check_results


def int_or_float(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{value} is not an int or float")


def run_clar_allen(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if len(sys.argv) == 3 and sys.argv[-2] == "reg" and sys.argv[-1] == "clar_allen":
        subprocess.Popen("%s/reg/miracl_reg_clar-allen.sh" % miracl_home, shell=True)
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/reg/miracl_reg_clar-allen.sh -h" % miracl_home, shell=True
            )
        else:
            bash_args = (
                "-i %s -r %s -o %s -m %s -v %s -l %s -f %s -p %s -a %s -w %s -b %s -s %s -c %s"
                % (
                    args["in_nii"],  # -i
                    args["reg_out"],  # -r
                    args["ort"],  # -o
                    args["hemi"],  # -m
                    args["vox_res"],  # -v
                    args["lbls"],  # -l
                    args["fig"],  # -f
                    args["pass_int"],  # -p
                    args["atlas"],  # -a
                    args["warp"],  # -w
                    args["bulb"],  # -b
                    args["side"],  # -s
                    args["clar_dir"],  # -c
                )
            )

            subprocess.check_call(
                "%s/reg/miracl_reg_clar-allen.sh %s" % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_mri_ants(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if sys.argv[-2] == "reg" and sys.argv[-1] == "mri_ants":
        # subprocess.Popen("%s/reg/miracl_reg_mri-ants.sh" % miracl_home, shell=True)
        subprocess.Popen("%s/reg/miracl_reg_mri-ants.sh -h" % miracl_home, shell=True)
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/reg/miracl_reg_mri-ants.sh -h" % miracl_home, shell=True
            )
        else:
            bash_args = (
                "-i %s -o %s -a %s -l %s -m %s -v %s -b %s -s %s -f %s -n %s -u %s"
                % (
                    args["in_nii"],
                    args["ort"],
                    args["atlas"],
                    args["lbls"],
                    args["hemi"],
                    args["vox_res"],
                    args["bulb"],
                    args["skull"],
                    args["bet"],
                    args["noort"],
                    args["upsmpl_fct"],
                )
            )

            subprocess.check_call(
                "%s/reg/miracl_reg_mri-ants.sh %s" % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_mri_nifty(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if sys.argv[-2] == "reg" and sys.argv[-1] == "mri_nifty":
        subprocess.Popen("%s/reg/miracl_reg_mri-niftyreg.sh" % miracl_home, shell=True)
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/reg/miracl_reg_mri-niftyreg.sh -h" % miracl_home, shell=True
            )
        else:
            bash_args = (
                "-i %s -r %s -o %s -m %s -v %s -l %s -b %s -s %s -f %s -n %s -a %s -e %s -x %s"
                % (
                    args["in_nii"],
                    args["work_dir"],
                    args["ort"],
                    args["hemi"],
                    args["vox_res"],
                    args["lbls"],
                    args["bulb"],
                    args["skull"],
                    args["bet"],
                    args["noort"],
                    args["atlas"],
                    args["be"],
                    args["sx"],
                )
            )

            subprocess.check_call(
                "%s/reg/miracl_reg_mri-niftyreg.sh %s" % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_warp_clar(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if sys.argv[-2] == "reg" and sys.argv[-1] == "warp_clar":
        subprocess.Popen(
            "%s/reg/miracl_reg_warp_clar_data_to_allen.sh" % miracl_home, shell=True
        )
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/reg/miracl_reg_warp_clar_data_to_allen.sh -h" % miracl_home,
                shell=True,
            )
        else:
            bash_args = "-i %s -o %s -r %s -s %s -v %s -l %s" % (
                args["in_nii"],
                args["ort_file"],
                args["reg_dir"],
                args["seg_chan"],
                args["vox_res"],
                args["lbls"],
            )

            subprocess.check_call(
                "%s/reg/miracl_reg_warp_clar_data_to_allen.sh %s"
                % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_warp_mr(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if sys.argv[-2] == "reg" and sys.argv[-1] == "warp_mr":
        subprocess.Popen(
            "%s/reg/miracl_reg_warp_mr_data_to_allen.sh" % miracl_home, shell=True
        )
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/reg/miracl_reg_warp_mr_data_to_allen.sh -h" % miracl_home,
                shell=True,
            )
        else:
            bash_args = "-i %s -o %s -r %s" % (
                args["in_nii"],
                args["ort_file"],
                args["reg_dir"],
            )

            subprocess.check_call(
                "%s/reg/miracl_reg_warp_mr_data_to_allen.sh %s"
                % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_check_reg(parser, args):
    miracl_reg_check_results.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # clar allen
    parser_clar_allen = subparsers.add_parser(
        "clar_allen",
        add_help=False,
        help="whole-brain CLARITY registration to Allen atlas",
    )
    parser_clar_allen.add_argument("-i", "--in_nii", metavar="", help="input nifti")
    parser_clar_allen.add_argument(
        "-r",
        "--reg_out",
        metavar="",
        default=os.path.abspath(os.getcwd()),
        help="output registration dir",
    )
    parser_clar_allen.add_argument(
        "-o", "--ort", metavar="", default="ARS", help="orientation tag"
    )
    parser_clar_allen.add_argument(
        "-m", "--hemi", metavar="", default="combined", help="whole brain or hemi"
    )
    parser_clar_allen.add_argument(
        "-v", "--vox_res", metavar="", default=10, help="voxel resolution"
    )
    parser_clar_allen.add_argument(
        "-b",
        "--bulb",
        metavar="",
        default=0,
        help="olfactory bulb included in brain, binary option",
    )
    parser_clar_allen.add_argument("-s", "--side", metavar="", help="voxel resolution")
    parser_clar_allen.add_argument("-a", "--atlas", metavar="", help="custom atlas")
    parser_clar_allen.add_argument("-l", "--lbls", metavar="", help="custom labels")
    parser_clar_allen.add_argument(
        "-p", "--pass_int", metavar="", default=0, help="skip intensity correction"
    )
    parser_clar_allen.add_argument(
        "-f", "--fig", metavar="", default=1, help="save mosaic figure of results"
    )
    parser_clar_allen.add_argument(
        "-w", "--warp", metavar="", default=0, help="warp high resolution clarity"
    )
    parser_clar_allen.add_argument(
        "-c", "--clar_dir", metavar="", default="", help="original clarity tiff folder"
    )
    parser_clar_allen.add_argument("-h", "--help", action="store_true")

    parser_clar_allen.set_defaults(func=run_clar_allen)

    # mri allen ants
    parser_mri_ants = subparsers.add_parser(
        "mri_ants",
        add_help=False,
        help="MRI registration to mouse/rat atlases using ANTs",
    )
    parser_mri_ants.add_argument(
        "-i",
        "--in_nii",
        metavar="",
        help="input nifti",
    )
    parser_mri_ants.add_argument(
        "-o",
        "--ort",
        metavar="",
        help="orientation tag",
    )
    parser_mri_ants.add_argument(
        "-a", "--atlas", metavar="", help="which atlas to use for registration"
    )
    parser_mri_ants.add_argument("-m", "--hemi", metavar="", help="whole brain or hemi")
    parser_mri_ants.add_argument("-v", "--vox_res", metavar="", help="voxel resolution")
    parser_mri_ants.add_argument(
        "-l",
        "--lbls",
        metavar="",
        help="input labels",
    )
    parser_mri_ants.add_argument("-b", "--bulb", metavar="", help="olfactory bulb")
    parser_mri_ants.add_argument("-s", "--skull", metavar="", help="skull strip")
    parser_mri_ants.add_argument(
        "-f", "--bet", metavar="", help="bet fractional intensity"
    )
    parser_mri_ants.add_argument(
        "-n",
        "--noort",
        metavar="",
        help="no orientation needed (input image in 'standard' orientation), binary option (default: 0 -> orient)",
    )
    parser_mri_ants.add_argument("-h", "--help", action="store_true")
    parser_mri_ants.add_argument(
        "-u",
        "--upsmpl_fct",
        metavar="",
        default=2,
        type=int_or_float,
        help="upsample factor",
    )

    parser_mri_ants.set_defaults(func=run_mri_ants)

    # mri nifty
    parser_mri_nifty = subparsers.add_parser(
        "mri_nifty",
        add_help=False,
        help="MRI registration to mouse/rat atlases using NiftyReg",
    )
    parser_mri_nifty.add_argument(
        "-i",
        "--in_nii",
        metavar="",
        help="input nifti",
    )
    parser_mri_nifty.add_argument(
        "-r",
        "--work_dir",
        metavar="",
        help="set base dir for reg output (default: cwd)",
    )
    parser_mri_nifty.add_argument(
        "-o",
        "--ort",
        metavar="",
        help="orientation tag",
    )
    parser_mri_nifty.add_argument(
        "-m",
        "--hemi",
        metavar="",
        help="whole brain or hemi",
    )
    parser_mri_nifty.add_argument(
        "-v",
        "--vox_res",
        metavar="",
        help="voxel resolution",
    )
    parser_mri_nifty.add_argument(
        "-l",
        "--lbls",
        metavar="",
        help="input labels",
    )
    parser_mri_nifty.add_argument(
        "-b",
        "--bulb",
        metavar="",
        help="olfactory bulb",
    )
    parser_mri_nifty.add_argument(
        "-s",
        "--skull",
        metavar="",
        help="skull strip",
    )
    parser_mri_nifty.add_argument(
        "-f",
        "--bet",
        metavar="",
        help="bet fractional intensity",
    )
    parser_mri_nifty.add_argument(
        "-n",
        "--noort",
        metavar="",
        help="no orientation needed (input image in 'standard' orientation), binary option (default: 0 -> orient)",
    )
    parser_mri_nifty.add_argument(
        "-a",
        "--atlas",
        metavar="",
        help="atlas: use 'allen' or 'dsurqe' for mouse models and 'fischer' or 'waxholm' atlas for rat models (default: 'allen')",
    )
    parser_mri_nifty.add_argument(
        "-e",
        "--be",
        metavar="",
        help="Weight of the bending energy (second derivative of the transformation) penalty term (default: 1e-3)",
    )
    parser_mri_nifty.add_argument(
        "-x",
        "--sx",
        metavar="",
        help="Final grid spacing along the x axis in mm (in voxel if negative value) (default: -15)",
    )
    parser_mri_nifty.add_argument(
        "-h",
        "--help",
        action="store_true",
    )

    parser_mri_nifty.set_defaults(func=run_mri_nifty)

    # warp clar
    parser_warp_clar = subparsers.add_parser(
        "warp_clar", add_help=False, help="warp CLARITY data to Allen space"
    )
    parser_warp_clar.add_argument("-i", "--in_nii", metavar="", help="input nifti")
    parser_warp_clar.add_argument(
        "-r", "--reg_dir", metavar="", help="registration dir"
    )
    parser_warp_clar.add_argument(
        "-o", "--ort_file", metavar="", help="file with ort tag"
    )
    parser_warp_clar.add_argument(
        "-s", "--seg_chan", metavar="", help="segmentation channel"
    )
    parser_warp_clar.add_argument(
        "-v", "--vox_res", metavar="", help="voxel resolution"
    )
    parser_warp_clar.add_argument("-l", "--lbls", metavar="", help="labels")
    parser_warp_clar.add_argument("-h", "--help", action="store_true")

    parser_warp_clar.set_defaults(func=run_warp_clar)

    # warp mr
    parser_warp_mr = subparsers.add_parser(
        "warp_mr", add_help=False, help="warp MRI data to Allen space"
    )
    parser_warp_mr.add_argument("-i", "--in_nii", metavar="", help="input nifti")
    parser_warp_mr.add_argument("-r", "--reg_dir", metavar="", help="registration dir")
    parser_warp_mr.add_argument(
        "-o", "--ort_file", metavar="", help="file with ort tag"
    )
    parser_warp_mr.add_argument("-h", "--help", action="store_true")

    parser_warp_mr.set_defaults(func=run_warp_mr)

    # check_reg
    check_reg_parser = miracl_reg_check_results.parsefn()
    parser_check_reg = subparsers.add_parser(
        "check",
        parents=[check_reg_parser],
        add_help=False,
        usage=check_reg_parser.usage,
        help="check registration",
    )
    parser_check_reg.set_defaults(func=run_check_reg)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == "__main__":
    main()
