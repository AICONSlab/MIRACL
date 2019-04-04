import os
import sys
import argparse
import subprocess
import logging
from miracl.io import miracl_io_convertTIFFtoNII, miracl_io_gui_options

# logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
# logger = logging.getLogger()


def run_tiff_nii(parser, args):
    miracl_io_convertTIFFtoNII.main()


def run_set_orient(parser):
    miracl_home = os.environ['MIRACL_HOME']
    subprocess.check_call('%s/io/miracl_io_set_orient_gui.py' % miracl_home,
                          shell=True,
                          stderr=subprocess.STDOUT)


def run_gui_opts(parser, args):
    miracl_io_gui_options.main()


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # tiff_nii
    tiff_nii_parser = miracl_io_convertTIFFtoNII.parsefn()
    parser_tiff_nii = subparsers.add_parser('tiff_nii', parents=[tiff_nii_parser], add_help=False,
                                            help="convert Tiff stacks to Nii")
    # parser_regclar.add_argument('-f', '--folder', nargs='+',
    #                             help="input registration folder")

    parser_tiff_nii.set_defaults(func=run_tiff_nii)

    # set orient
    parser_set_orient = subparsers.add_parser('set_orient', help="Set orientation tag with GUI")
    parser_set_orient.set_defaults(func=run_set_orient)

    # gui_opts
    gui_opts_parser = miracl_io_gui_options.parsefn()
    parser_gui_opts = subparsers.add_parser('gui_opts', parents=[gui_opts_parser], add_help=False,
                                            help="GUI options")
    parser_gui_opts.set_defaults(func=run_gui_opts)

    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
