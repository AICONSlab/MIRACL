import os
import sys
import argparse
import subprocess
from miracl.connect import miracl_connect_label_graph_proj_dens, miracl_connect_ROI_matrix_connectogram


def run_proj_dens(parser, args):
    miracl_connect_label_graph_proj_dens.main(args)


def run_roi_mat(parser, args):
    miracl_connect_ROI_matrix_connectogram.main(args)


def run_csd_track(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    args = vars(args)

    bash_args = '-d %s -m %s -r %s -b %s -s %s -v %s -t %s -f %s' % (args['dti_data'], args['mask'], args['bvecs'],
                                                                     args['bvals'], args['seed'], args['vox'],
                                                                     args['tract_name'], args['folder'])

    subprocess.check_call('%s/connect/miracl_connect_csd_tractography.sh %s' % (miracl_home, bash_args),
                          shell=True,
                          stderr=subprocess.STDOUT)


def run_sta(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    args = vars(args)

    subprocess.check_call('%s/miracl/flow/miracl_workflow_sta.sh %s' % (miracl_home, args), shell=True,
                          stderr=subprocess.STDOUT)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # csd_track
    parser_csd_track = subparsers.add_parser('csd_track', help="Performs CSD tractography and "
                                                               "track density mapping for a seed region using MRtrix3")
    parser_csd_track.add_argument('-d', '--dti_data', metavar='',
                                  help="input DTI data")
    parser_csd_track.add_argument('-m', '--mask', metavar='',
                                  help="DTI mask")
    parser_csd_track.add_argument('-r', '--bvecs', metavar='',
                                  help="DTI bvecs")
    parser_csd_track.add_argument('-b', '--bvals', metavar='',
                                  help="DTI bvals")
    parser_csd_track.add_argument('-s', '--seed', metavar='',
                                  help="Tractography seed")
    parser_csd_track.add_argument('-v', '--vox', metavar='',
                                  help="Tract density map voxel size (in mm)")
    parser_csd_track.add_argument('-t', '--tract_name', metavar='',
                                  help="Output tract name")
    parser_csd_track.add_argument('-f', '--folder', metavar='',
                                  help="Folder containing DTI data")
    parser_csd_track.set_defaults(func=run_csd_track)

    # proj_dens
    proj_dens_parser = miracl_connect_label_graph_proj_dens.parsefn()
    parser_proj_dens = subparsers.add_parser('proj_dens', parents=[proj_dens_parser], add_help=False,
                                             help="Query Allen connectivity API for injection experiments &"
                                                  "Outputs a connectivity graph of that experiment & "
                                                  "its projection density images")
    parser_proj_dens.set_defaults(func=run_proj_dens)

    # roi_mat
    roi_mat_parser = miracl_connect_ROI_matrix_connectogram.parsefn()
    parser_roi_mat = subparsers.add_parser('roi_mat', parents=[roi_mat_parser], add_help=False,
                                           help="Finds the largest N Allen labels in the Region of Interest & "
                                                "extracts its N closely connected regions")
    parser_roi_mat.set_defaults(func=run_roi_mat)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
