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


def run_warp_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'lbls' and sys.argv[-1] == 'warp_clar':
        subprocess.Popen('%s/lbls/miracl_lbls_warp_to_clar_space.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/lbls/miracl_lbls_warp_to_clar_space.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-r %s -l %s -o %s -c %s -d %s -f %s -i %s -t %s' % (args['reg_dir'], args['in_lbl'],
                                                                             args['ort_file'], args['clar_dir'],
                                                                             args['output_dir'], args['output_file'],
                                                                             args['interpolation'], args['output_type'])

            subprocess.check_call('%s/lbls/miracl_lbls_warp_to_clar_space.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_warp_mr(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'lbls' and sys.argv[-1] == 'warp_mri':
        subprocess.Popen('%s/lbls/miracl_lbls_warp_to_mri_space.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/lbls/miracl_lbls_warp_to_mri_space.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-f %s -t %s -v %s -s "%s" -e "%s"' % (args['folder'], args['type'], args['vox_res'],
                                                               args['seg_opts'][0], args['ext_opts'][0])

            subprocess.check_call('%s/lbls/miracl_lbls_warp_to_mri_space.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


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
    parser_parents_depth = subparsers.add_parser('gp_at_depth', parents=[parents_depth_parser], add_help=False,
                                                 usage=parents_depth_parser.usage,
                                                 help="Generate parent labels at depth")
    parser_parents_depth.set_defaults(func=run_gen_parents_depth)

    # gp volumes
    gp_vols_parser = miracl_lbls_get_gp_volumes.parsefn()
    parser_gp_vols = subparsers.add_parser('gp_vols', parents=[gp_vols_parser], add_help=False,
                                           usage=gp_vols_parser.usage,
                                           help="Get grand parent volumes")
    parser_gp_vols.set_defaults(func=run_gp_volumes)

    # warp clar space
    parser_warp_clar = subparsers.add_parser('warp_clar', add_help=False,
                                             help="Warps Allen annotations to the original high-res CLARITY space")
    parser_warp_clar.add_argument('-r', '--reg_dir', metavar='',
                            help="Clarity registration folder")
    parser_warp_clar.add_argument('-l', '--in_lbl', metavar='',
                            help="Input Allen labels to warp")
    parser_warp_clar.add_argument('-o', '--ort_file', metavar='',
                            help="file with orientation to standard code")
    parser_warp_clar.add_argument('-c', '--clar_dir', metavar='',
                            help="Original clarity tiff folder")
    parser_warp_clar.add_argument("-d", "--output_dir", metavar='',
                            help="Output directory")
    parser_warp_clar.add_argument("-f", "--output_file", metavar='',
                            help="Output warped labels name")
    parser_warp_clar.add_argument("-i", "--interpolation", metavar='',
                            help="Interpolation method", default="MultiLabel", required=False)
    parser_warp_clar.add_argument("-t", "--output_type", metavar='',
                            help="Output file type", default="short", required=False)
    parser_warp_clar.add_argument('-h', '--help', action='store_true')

    parser_warp_clar.set_defaults(func=run_warp_clar)

    # warp mr space
    parser_warp_mr = subparsers.add_parser('warp_mr', add_help=False,
                                             help="Warps Allen annotations to the original MRI space")
    parser_warp_mr.add_argument('-r', '--reg_dir', metavar='',
                            help="Clarity registration folder")
    parser_warp_mr.add_argument('-l', '--in_lbl', metavar='',
                            help="Input Allen labels to warp")
    parser_warp_mr.add_argument('-o', '--ort_file', metavar='',
                            help="file with orientation to standard code")
    parser_warp_mr.add_argument('-h', '--help', action='store_true')

    parser_warp_mr.set_defaults(func=run_warp_mr)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
