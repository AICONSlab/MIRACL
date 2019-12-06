import os
import sys
import argparse
import subprocess
from miracl.sta import miracl_sta_create_force_graph, miracl_sta_gen_tract_density


def run_sta_tensor(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'sta' and sys.argv[-1] == 'track_tensor':
        subprocess.Popen('%s/sta/miracl_sta_track_primary_eigen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/sta/miracl_sta_track_primary_eigen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -g %s -k %s -a %s -s %s -b %s -o %s' % (args['in_nii'], args['dog'], args['sigma'],
                                                                       args['angle'], args['seed_mask'], args['brain_mask'],
                                                                       args['out_dir'])

            subprocess.check_call('%s/sta/miracl_sta_track_primary_eigen.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_force_graph(parser, args):
    miracl_sta_create_force_graph.main(args)


def run_tract_density(parser, args):
    miracl_sta_gen_tract_density.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # sta
    parser_sta = subparsers.add_parser('track_tensor', add_help=False, help="")
    parser_sta.add_argument('-i', '--in_nii', metavar='',
                            help="Input down-sampled clarity nifti")
    parser_sta.add_argument('-g', '--dog', metavar='',
                            help="Derivative of Gaussian (dog) sigma")
    parser_sta.add_argument('-k', '--sigma', metavar='',
                            help="Gaussian smoothing sigma")
    parser_sta.add_argument('-a', '--angle', metavar='',
                            help="Tracking angle threshold")
    parser_sta.add_argument('-s', '--seed_mask', metavar='',
                            help="Seed mask")
    parser_sta.add_argument('-b', '--brain_mask', metavar='',
                            help="Brain mask")
    parser_sta.add_argument('-o', '--out_dir', metavar='',
                            help="Output dir")
    parser_sta.add_argument('-h', '--help', action='store_true')

    parser_sta.set_defaults(func=run_sta_tensor)

    # force graph
    force_graph_parser = miracl_sta_create_force_graph.parsefn()
    parser_force_graph = subparsers.add_parser('conn_graph', parents=[force_graph_parser], add_help=False,
                                               usage=force_graph_parser.usage,
                                               help="Generate connectivity graph")
    parser_force_graph.set_defaults(func=run_force_graph)

    # tract density
    tract_density_parser = miracl_sta_gen_tract_density.parsefn()
    parser_tract_density = subparsers.add_parser('tract_density', parents=[tract_density_parser], add_help=False,
                                                 usage=tract_density_parser.usage,
                                                 help="Generate tract density map")
    parser_tract_density.set_defaults(func=run_tract_density)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
