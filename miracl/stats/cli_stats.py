import sys
import argparse
from miracl.stats import (
    miracl_stats_paired_ttest_ipsi_contra,
    miracl_stats_voxel_wise,
    miracl_stats_paired_ttest_group,
    miracl_plot_single_subj,
    miracl_stats_heatmap_group,
    miracl_stats_ace_interface,
    miracl_stats_ace_parser,
)


def run_paired_ttest(parser, args):
    miracl_stats_paired_ttest_ipsi_contra.main(args)


def run_voxel_wise(parser, args):
    miracl_stats_voxel_wise.main(args)


def run_group_ttest(parser, args):
    miracl_stats_paired_ttest_group.main(args)


def plot_subj(parser, args):
    miracl_plot_single_subj.main(args)


def heatmap_group(parser, args):
    miracl_stats_heatmap_group.main(args)


def ace(parser, args):
    miracl_stats_ace_interface.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # heatmap
    heatmap_parser = miracl_stats_heatmap_group.parsefn()
    parser_heat = subparsers.add_parser(
        "heatmap_group",
        parents=[heatmap_parser],
        add_help=False,
        usage=heatmap_parser.usage,
        help="run heatmap group stats",
    )
    parser_heat.set_defaults(func=heatmap_group)

    # paired t-test
    paired_parser = miracl_stats_paired_ttest_ipsi_contra.parsefn()
    parser_paired = subparsers.add_parser(
        "paired_ttest",
        parents=[paired_parser],
        add_help=False,
        usage=paired_parser.usage,
        help="run paired ttest stats",
    )

    parser_paired.set_defaults(func=run_paired_ttest)

    # voxel wise stats
    voxel_parser = miracl_stats_voxel_wise.parsefn()
    parser_voxel = subparsers.add_parser(
        "voxel_wise",
        parents=[voxel_parser],
        add_help=False,
        usage=voxel_parser.usage,
        help="run voxel wise stats",
    )

    parser_voxel.set_defaults(func=run_voxel_wise)

    # group wise t-test

    group_parser = miracl_stats_paired_ttest_group.parsefn()
    parser_group = subparsers.add_parser(
        "group_ttest",
        parents=[group_parser],
        add_help=False,
        usage=group_parser.usage,
        help="run groupwise ttest stats",
    )

    parser_group.set_defaults(func=run_group_ttest)

    # single subject, plotting results

    subj_parser = miracl_plot_single_subj.parsefn()
    parser_subj = subparsers.add_parser(
        "plot_subj",
        parents=[subj_parser],
        add_help=False,
        usage=subj_parser.usage,
        help="plot results for one subject",
    )

    parser_subj.set_defaults(func=plot_subj)

    ace_parser = miracl_stats_ace_parser.ACEStatsParser().parsefn()
    parser_ace = subparsers.add_parser(
        "ace",
        parents=[ace_parser],
        add_help=False,
        usage=ace_parser.usage,
        help="run ACE stats",
    )
    parser_ace.set_defaults(func=ace)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    print(args)
    args.func(parser, args)


if __name__ == "__main__":
    main()
