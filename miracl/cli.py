import sys
import argparse
import logging

logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger()

from miracl.flow import cli_flow

# from miracl.reg import cli_reg

# def run_reg(parser, args):
#     cli_reg(args)

def run_flow(parser, args):
    cli_flow.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # flow
    parser_flow = subparsers.add_parser(
        'flow',
        help=""
    )
    parser_flow.add_argument(
        'reg_clar',
        help="Wrapper for registering clarity data to allen Reference brain atlas"
    )
    parser_flow.add_argument(
        'sta',
        help="Wrapper for structure tensor analysis (STA), uses registered labels to create"
    )
    parser_flow.add_argument(
        'seg',
        help="Wrapper for segmentation, segments neurons in cleared mouse brain of sparse or nuclear"
    )

    parser_flow.set_defaults(func=run_flow)

    #

    return parser


def main(args=None):
    """ main cli call"""
    if args is None:
        args = sys.argv[1:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()