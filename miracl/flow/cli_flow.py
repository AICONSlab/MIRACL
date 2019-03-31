import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path

logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger()


def run_reg_clar(parser, args):

    flow_cli = os.path.realpath(__file__)
    flow_dir = Path(flow_cli).parents[2]

    subprocess.check_call('%s/miracl_workflow_registration_clarity-allen_wb.sh %s' % (flow_dir, args), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)


def run_sta(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    subprocess.check_call('%s/miracl/flow/miracl_workflow_sta.sh %s' % (miracl_home, args), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # reg_clarity
    parser_regclar = subparsers.add_parser(
        'reg_clar',
        help=""
    )
    parser_regclar.add_argument(
        '-f',
        help=""
    )
    parser_regclar.add_argument(
        '-o',
        help=""
    )
    parser_regclar.add_argument(
        '-n',
        help=""
    )
    parser_regclar.add_argument(
        '-h',
        help="help func"
    )

    parser_regclar.set_defaults(func=run_reg_clar)

    # sta
    parser_sta = subparsers.add_parser(
        'sta',
        help=""
    )
    parser_sta.add_argument(
        '-f',
        help=""
    )
    parser_sta.add_argument(
        '-o',
        help=""
    )
    parser_sta.add_argument(
        '-l',
        help=""
    )

    parser_sta.set_defaults(func=run_sta)

    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()