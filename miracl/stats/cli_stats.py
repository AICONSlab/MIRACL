import os
import sys
import argparse
import subprocess
from miracl.stats import miracl_stats_paired_ttest_ipsi_contra, miracl_stats_voxel_wise
from pathlib import Path


def run_paired_ttest(parser, args):
    miracl_stats_paired_ttest_ipsi_contra.main(args)


def run_voxel_wise(parser, args):
    miracl_stats_voxel_wise.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # paired t-test
    paired_parser = miracl_stats_paired_ttest_ipsi_contra.parsefn()
    parser_paired = subparsers.add_parser('paired_ttest', parents=[paired_parser], add_help=False,
                                            help='run paired ttest stats')

    parser_paired.set_defaults(func=run_paired_ttest)

    # voxel wise stats
    voxel_parser = miracl_stats_voxel_wise.parsefn()
    parser_voxel = subparsers.add_parser('voxel_wise', parents=[voxel_parser], add_help=False,
                                            help='run voxel wise stats')

    parser_voxel.set_defaults(func=run_voxel_wise)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
