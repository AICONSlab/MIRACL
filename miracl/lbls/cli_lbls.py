import os
import sys
import argparse
import subprocess
from miracl.lbls import miracl_lbls_stats, miracl_lbls_get_graph_info, miracl_lbls_generate_parents_at_depth, \
    miracl_lbls_get_gp_volumes


def run_lbl_stats(parser, args):
    miracl_lbls_stats.main(args)


def run_graph_info(parser, args):
    miracl_lbls_get_graph_info.main(args)


def run_gen_parents_depth(parser, args):
    miracl_lbls_generate_parents_at_depth.main(args)


def run_gp_volumes(parser, args):
    miracl_lbls_get_gp_volumes.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # lbl stats
    lbl_stats_parser = miracl_lbls_stats.parsefn()
    parser_lbl_stats = subparsers.add_parser('stats', parents=[lbl_stats_parser], add_help=False,
                                             usage=lbl_stats_parser.usage,
                                             help="Get label stats")
    parser_lbl_stats.set_defaults(func=run_lbl_stats)

    # graph info
    graph_info_parser = miracl_lbls_get_graph_info.parsefn()
    parser_graph_info = subparsers.add_parser('graph_info', parents=[graph_info_parser], add_help=False,
                                              usage=graph_info_parser.usage,
                                              help="Get label Allen graph info")
    parser_graph_info.set_defaults(func=run_graph_info)

    # gen parents @ depths
    parents_depth_parser = miracl_lbls_generate_parents_at_depth.parsefn()
    parser_parents_depth = subparsers.add_parser('parents_at_depth', parents=[parents_depth_parser], add_help=False,
                                                 usage=parents_depth_parser.usage,
                                                 help="Generate parent labels at depth")
    parser_parents_depth.set_defaults(func=run_gen_parents_depth)

    # gp volumes
    gp_vols_parser = miracl_lbls_get_gp_volumes.parsefn()
    parser_gp_vols = subparsers.add_parser('grandparent_volumes', parents=[gp_vols_parser], add_help=False,
                                           usage=gp_vols_parser.usage,
                                           help="Get grand parent volumes")
    parser_gp_vols.set_defaults(func=run_gp_volumes)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
