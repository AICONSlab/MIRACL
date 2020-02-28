import os
import sys
import argparse
import subprocess
from miracl.conv import miracl_conv_convertTIFFtoNII, miracl_conv_gui_options, miracl_conv_convertNIItoTIFF


def run_tiff_nii(parser, args):
    miracl_conv_convertTIFFtoNII.main(args)


def run_nii_tiff(parser, args):
    miracl_conv_convertNIItoTIFF.main(args)


def run_set_orient(parser, args=None):
    miracl_home = os.environ['MIRACL_HOME']
    subprocess.check_call('%s/conv/miracl_conv_set_orient_gui.py' % miracl_home,
                          shell=True,
                          stderr=subprocess.STDOUT)


def run_gui_opts(parser, args):
    miracl_conv_gui_options.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # tiff_nii
    tiff_nii_parser = miracl_conv_convertTIFFtoNII.parsefn()
    parser_tiff_nii = subparsers.add_parser('tiff_nii', parents=[tiff_nii_parser], add_help=False,
                                            usage=tiff_nii_parser.usage,
                                            help='convert Tiff stacks to Nii')

    parser_tiff_nii.set_defaults(func=run_tiff_nii)

    # nii_tiff
    nii_tiff_parser = miracl_conv_convertNIItoTIFF.parsefn()
    parser_nii_tiff = subparsers.add_parser('nii_tiff', parents=[nii_tiff_parser], add_help=False,
                                            usage=nii_tiff_parser.usage,
                                            help='convert Nii volume to Tiff stack')

    parser_nii_tiff.set_defaults(func=run_nii_tiff)

    # set orient
    parser_set_orient = subparsers.add_parser('set_orient', help="Set orientation tag with GUI", add_help=False)
    parser_set_orient.set_defaults(func=run_set_orient)

    # gui_opts
    gui_opts_parser = miracl_conv_gui_options.parsefn()
    parser_gui_opts = subparsers.add_parser('gui_opts', parents=[gui_opts_parser], add_help=False,
                                            help="GUI options")
    parser_gui_opts.set_defaults(func=run_gui_opts)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
