import os
import sys
import argparse
import logging
from pathlib import Path

# logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
# logger = logging.getLogger()

from miracl.flow import cli_flow
from miracl.reg import cli_reg
from miracl.seg import cli_seg
from miracl.io import cli_io
from miracl.connect import cli_connect
from miracl.lbls import cli_lbls
from miracl.sta import cli_sta


def run_reg(parser, args):
    cli_reg(args)


def run_flow(parser, args):
    cli_flow.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # flow
    flow_parser = cli_flow.get_parser()
    parser_flow = subparsers.add_parser('flow', parents=[flow_parser], add_help=False,
                                        help="workflows to run")

    parser_flow.set_defaults(func=run_flow)

    # reg
    reg_parser = cli_reg.get_parser()
    parser_reg = subparsers.add_parser('reg', parents=[reg_parser], add_help=False,
                                       help="registration functions")

    parser_reg.set_defaults(func=run_reg)

    # seg
    seg_parser = cli_seg.get_parser()
    parser_seg = subparsers.add_parser('seg', parents=[seg_parser], add_help=False,
                                       help="segmentation functions")

    parser_seg.set_defaults(func=run_seg)

    # sta
    sta_parser = cli_sta.get_parser()
    parser_sta = subparsers.add_parser('sta', parents=[sta_parser], add_help=False,
                                       help="STA functions")

    parser_seg.set_defaults(func=run_sta)

    # connect
    connect_parser = cli_connect.get_parser()
    parser_connect = subparsers.add_parser('connect', parents=[connect_parser], add_help=False,
                                           help="connect functions")

    parser_connect.set_defaults(func=run_connect)

    # io
    io_parser = cli_io.get_parser()
    parser_io = subparsers.add_parser('io', parents=[seg_parser], add_help=False,
                                      help="io functions")

    parser_io.set_defaults(func=run_io)


    return parser


def main(args=None):
    """ main cli call"""
    if args is None:
        args = sys.argv[1:]

    # set miracl home
    if os.environ['MIRACL_HOME'] is None:
        cli_file = os.path.realpath(__file__)
        miracl_dir = Path(cli_file).parents[0]
        os.environ['MIRACL_HOME'] = miracl_dir

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
