import os
import sys
import argparse
import subprocess
import logging


# logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
# logger = logging.getLogger()


def run_clar_allen_wb(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/miracl/reg/miracl_reg_clar-allen_whole_brain.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-i %s -o %s -m %s -v %s' % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'])

        subprocess.check_call('%s/miracl/reg/miracl_reg_clar-allen_whole_brain.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def run_mri_allen_ants(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/miracl/reg/miracl_reg_mri-allen.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-i %s -o %s -m %s -v %s -l %s -b %s -s % -f %s' \
                    % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'], args['lbls'], args['bulb'],
                       args['skull'], args['bet'])

        subprocess.check_call('%s/miracl/reg/miracl_reg_mri-allen.sh %s' % (miracl_home, bash_args), shell=True,
                              stderr=subprocess.STDOUT)


def run_warp_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/miracl/reg/miracl_reg_warp_clar_data_to_allen.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-i %s -o %s -r %s -s %s' % (args['in_nii'], args['ort_file'], args['reg_dir'], args['seg_chan'])

        subprocess.check_call('%s/miracl/reg/miracl_reg_warp_clar_data_to_allen.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def run_warp_mr(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/miracl/reg/miracl_reg_warp_mr_data_to_allen.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-i %s -o %s -r %s' % (args['in_nii'], args['ort_file'], args['reg_dir'])

        subprocess.check_call('%s/miracl/reg/miracl_reg_warp_mr_data_to_allen.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # clar allen
    parser_clar_allen_wb = subparsers.add_parser('clar_allen_wb', add_help=False,
                                                 help="whole-brain CLARITY registration to Allen atlas")
    parser_clar_allen_wb.add_argument('-i', '--in_nii', metavar='',
                                      help="input nifti")
    parser_clar_allen_wb.add_argument('-o', '--ort', metavar='',
                                      help="orientation tag")
    parser_clar_allen_wb.add_argument('-m', '--hemi', metavar='',
                                      help="whole brain or hemi")
    parser_clar_allen_wb.add_argument('-v', '--vox_res', metavar='',
                                      help="voxel resolution")
    parser_clar_allen_wb.add_argument('-h', '--help', action='store_true')

    parser_clar_allen_wb.set_defaults(func=run_clar_allen_wb)

    # mri allen ants
    parser_mri_allen = subparsers.add_parser('mri_allen_ants', add_help=False,
                                             help="MRI registration to Allen atlas")
    parser_mri_allen.add_argument('-i', '--in_nii', metavar='',
                                  help="input niti")
    parser_mri_allen.add_argument('-o', '--ort', metavar='',
                                  help="orientation tag")
    parser_mri_allen.add_argument('-m', '--hemi', metavar='',
                                  help="whole brain or hemi")
    parser_mri_allen.add_argument('-v', '--vox_res', metavar='',
                                  help="voxel resolution")
    parser_mri_allen.add_argument('-l', '--lbls', metavar='',
                                  help="input labels")
    parser_mri_allen.add_argument('-b', '--bulb', metavar='',
                                  help="olfactory bulb")
    parser_mri_allen.add_argument('-s', '--skull', metavar='',
                                  help="skull strip")
    parser_mri_allen.add_argument('-f', '--bet', metavar='',
                                  help="bet fractional intensity")
    parser_mri_allen.add_argument('-h', '--help', action='store_true')

    parser_mri_allen.set_defaults(func=run_mri_allen_ants)

    # warp clar
    parser_warp_clar = subparsers.add_parser('warp_clar', add_help=False,
                                             help="Warp CLARITY data to Allen space")
    parser_warp_clar.add_argument('-i', '--in_nii', metavar='',
                                  help="input nifti")
    parser_warp_clar.add_argument('-r', '--reg_dir', metavar='',
                                  help="registration dir")
    parser_warp_clar.add_argument('-o', '--ort_file', metavar='',
                                  help="file with ort tag")
    parser_warp_clar.add_argument('-s', '--seg_chan', metavar='',
                                  help="segmenation channel")
    parser_warp_clar.add_argument('-h', '--help', action='store_true')

    parser_warp_clar.set_defaults(func=run_warp_clar)

    # warp mr
    parser_warp_mr = subparsers.add_parser('warp_mr', add_help=False,
                                             help="Warp MRI data to Allen space")
    parser_warp_mr.add_argument('-i', '--in_nii', metavar='',
                                  help="input nifti")
    parser_warp_mr.add_argument('-r', '--reg_dir', metavar='',
                                  help="registration dir")
    parser_warp_mr.add_argument('-o', '--ort_file', metavar='',
                                  help="file with ort tag")
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
