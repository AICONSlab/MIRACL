import os
import sys
import argparse
import subprocess
from miracl.sta import miracl_sta_create_force_graph, miracl_sta_gen_tract_density, miracl_sta_track_primary_eigen, miracl_sta_gen_tract_endpoints, miracl_sta_track


def run_sta_tensor(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    miracl_sta_track.main(args)
    # miracl_sta_track_primary_eigen.main(args)


def run_force_graph(parser, args):
    miracl_sta_create_force_graph.main(args)


def run_tract_density(parser, args):
    miracl_sta_gen_tract_density.main(args)

def run_tract_endpoints(parser, args):
    miracl_sta_gen_tract_endpoints.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # sta tensor
    sta_tensor_parser = miracl_sta_track.parsefn()
    #sta_tensor_parser = miracl_sta_sta_track.parsefn()
    parser_sta_tensor = subparsers.add_parser('track_tensor', parents=[sta_tensor_parser], add_help=False,
        usage=sta_tensor_parser.usage, help='Perform Structure Tensor Analysis (STA) on CLARITY viral tracing or stains')
    parser_sta_tensor.set_defaults(func=run_sta_tensor)

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

    # tract endpoints
    tract_endpoints_parser = miracl_sta_gen_tract_endpoints.parsefn()
    parser_tract_density = subparsers.add_parser('tract_endpoints', parents=[tract_endpoints_parser], add_help=False,
                                                 usage=tract_endpoints_parser.usage,
                                                 help="Generate tract endpoints map")
    parser_tract_density.set_defaults(func=run_tract_endpoints)



    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
