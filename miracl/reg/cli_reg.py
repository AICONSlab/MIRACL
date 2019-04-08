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

    bash_args = '-i %s -o %s -m %s -v %s' % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'])

    subprocess.check_call('%s/reg/miracl_reg_clar-allen_whole_brain.sh %s' % (miracl_home, bash_args),
                          shell=True,
                          stderr=subprocess.STDOUT)


def run_mri_allen(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    bash_args = '-i %s -o %s -m %s -v %s' % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'])

    subprocess.check_call('%s/reg/miracl_reg_mri-allen.sh %s' % (miracl_home, bash_args), shell=True,
                          stderr=subprocess.STDOUT)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # clar allen
    parser_clar_allen_wb = subparsers.add_parser('clar_allen_wb',
                                                 help="whole-brain CLARITY registration to Allen atlas")
    parser_clar_allen_wb.add_argument('-i', '--in_nii', metavar='',
                                      help="input nifti")
    parser_clar_allen_wb.add_argument('-o', '--ort', metavar='',
                                      help="orientation tag")
    parser_clar_allen_wb.add_argument('-m', '--hemi', metavar='',
                                      help="whole brain or hemi")
    parser_clar_allen_wb.add_argument('-v', '--vox_res', metavar='',
                                      help="voxel resolution")

    parser_clar_allen_wb.set_defaults(func=run_clar_allen_wb)

    # mri allen
    parser_mri_allen = subparsers.add_parser('mri_allen', help="MRI registration to Allen atlas")
    parser_mri_allen.add_argument('-i', '--in_nii', metavar='',
                                      help="input niti")
    parser_mri_allen.add_argument('-o', '--ort', metavar='',
                                      help="orientation tag")
    parser_mri_allen.add_argument('-m', '--hemi', metavar='',
                                      help="whole brain or hemi")
    parser_mri_allen.add_argument('-v', '--vox_res', metavar='',
                                      help="voxel resolution")

    parser_mri_allen.set_defaults(func=run_mri_allen)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
