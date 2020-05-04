import os
import sys
import argparse
import subprocess
from miracl.reg import miracl_reg_check_results


def run_clar_allen(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'reg' and sys.argv[-1] == 'clar_allen':
        subprocess.Popen('%s/reg/miracl_reg_clar-allen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/reg/miracl_reg_clar-allen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -r %s -o %s -m %s -v %s -f %s -p %s -a %s -w %s -l %s' \
                        % (args['in_nii'], args['reg_out'], args['ort'], args['hemi'], args['vox_res'], args['fig'],
                           args['pass_int'], args['atlas'], args['warp'], args['lbls'])

            subprocess.check_call('%s/reg/miracl_reg_clar-allen.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_mri_allen_ants(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'reg' and sys.argv[-1] == 'mri_allen_ants':
        subprocess.Popen('%s/reg/miracl_reg_mri-allen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/reg/miracl_reg_mri-allen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -o %s -m %s -v %s -l %s -b %s -s % -f %s' \
                        % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'], args['lbls'], args['bulb'],
                           args['skull'], args['bet'])

            subprocess.check_call('%s/reg/miracl_reg_mri-allen.sh %s' % (miracl_home, bash_args), shell=True,
                                  stderr=subprocess.STDOUT)


def run_mri_allen_nifty(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'reg' and sys.argv[-1] == 'mri_allen_nifty':
        subprocess.Popen('%s/reg/miracl_reg_mri-allen_niftyreg.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/reg/miracl_reg_mri-allen_niftyreg.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -o %s -m %s -v %s -l %s -b %s -s % -f %s' \
                        % (args['in_nii'], args['ort'], args['hemi'], args['vox_res'], args['lbls'], args['bulb'],
                           args['skull'], args['bet'])

            subprocess.check_call('%s/reg/miracl_reg_mri-allen_niftyreg.sh %s' % (miracl_home, bash_args), shell=True,
                                  stderr=subprocess.STDOUT)


def run_warp_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'reg' and sys.argv[-1] == 'warp_clar':
        subprocess.Popen('%s/reg/miracl_reg_warp_clar_data_to_allen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/reg/miracl_reg_warp_clar_data_to_allen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -o %s -r %s -s %s' % (
                args['in_nii'], args['ort_file'], args['reg_dir'], args['seg_chan'])

            subprocess.check_call('%s/reg/miracl_reg_warp_clar_data_to_allen.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_warp_mr(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if sys.argv[-2] == 'reg' and sys.argv[-1] == 'warp_mr':
        subprocess.Popen('%s/reg/miracl_reg_warp_mr_data_to_allen.sh' % miracl_home,
                         shell=True)
    else:
        if args['help']:
            subprocess.Popen('%s/reg/miracl_reg_warp_mr_data_to_allen.sh -h' % miracl_home,
                             shell=True)
        else:
            bash_args = '-i %s -o %s -r %s' % (args['in_nii'], args['ort_file'], args['reg_dir'])

            subprocess.check_call('%s/reg/miracl_reg_warp_mr_data_to_allen.sh %s' % (miracl_home, bash_args),
                                  shell=True,
                                  stderr=subprocess.STDOUT)


def run_check_reg(parser, args):
    miracl_reg_check_results.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # clar allen
    parser_clar_allen = subparsers.add_parser('clar_allen', add_help=False,
                                                 help="whole-brain CLARITY registration to Allen atlas")
    parser_clar_allen.add_argument('-i', '--in_nii', metavar='',
                                      help="input nifti")
    parser_clar_allen.add_argument('-r', '--reg_out', metavar='', default=os.path.abspath(os.getcwd()),
                                      help="output registration dir")
    parser_clar_allen.add_argument('-o', '--ort', metavar='', default='ARS',
                                      help="orientation tag")
    parser_clar_allen.add_argument('-m', '--hemi', metavar='', default='combined',
                                      help="whole brain or hemi")
    parser_clar_allen.add_argument('-v', '--vox_res', metavar='', default=10,
                                      help="voxel resolution")
    parser_clar_allen.add_argument('-b', '--bulb', metavar='', default=0,
                                      help="olfactory bulb included in brain, binary option")
    parser_clar_allen.add_argument('-s', '--side', metavar='',
                                      help="voxel resolution")
    parser_clar_allen.add_argument('-a', '--atlas', metavar='',
                                      help="custom atlas")
    parser_clar_allen.add_argument('-l', '--lbls', metavar='',
                                      help="custom labels")
    parser_clar_allen.add_argument('-p', '--pass_int', metavar='', default=0,
                                      help="skip intensity correction")
    parser_clar_allen.add_argument('-f', '--fig', metavar='', default=1,
                                      help="save mosaic figure of results")
    parser_clar_allen.add_argument('-w', '--warp', metavar='', default=0,
                                      help="warp high resolution clarity")
    parser_clar_allen.add_argument('-h', '--help', action='store_true')

    parser_clar_allen.set_defaults(func=run_clar_allen)

    # mri allen ants
    parser_mri_allen = subparsers.add_parser('mri_allen_ants', add_help=False,
                                             help="MRI registration to Allen atlas using ANTs")
    parser_mri_allen.add_argument('-i', '--in_nii', metavar='',
                                  help="input nifti")
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

    # mri allen nifty
    parser_mri_allen_nifty = subparsers.add_parser('mri_allen_nifty', add_help=False,
                                                   help="MRI registration to Allen atlas using NiftyReg")
    parser_mri_allen_nifty.add_argument('-i', '--in_nii', metavar='',
                                        help="input nifti")
    parser_mri_allen_nifty.add_argument('-o', '--ort', metavar='',
                                        help="orientation tag")
    parser_mri_allen_nifty.add_argument('-m', '--hemi', metavar='',
                                        help="whole brain or hemi")
    parser_mri_allen_nifty.add_argument('-v', '--vox_res', metavar='',
                                        help="voxel resolution")
    parser_mri_allen_nifty.add_argument('-l', '--lbls', metavar='',
                                        help="input labels")
    parser_mri_allen_nifty.add_argument('-b', '--bulb', metavar='',
                                        help="olfactory bulb")
    parser_mri_allen_nifty.add_argument('-s', '--skull', metavar='',
                                        help="skull strip")
    parser_mri_allen_nifty.add_argument('-f', '--bet', metavar='',
                                        help="bet fractional intensity")
    parser_mri_allen_nifty.add_argument('-h', '--help', action='store_true')

    parser_mri_allen_nifty.set_defaults(func=run_mri_allen_nifty)

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
                                  help="segmentation channel")
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

    # check_reg
    check_reg_parser = miracl_reg_check_results.parsefn()
    parser_check_reg = subparsers.add_parser('check', parents=[check_reg_parser], add_help=False,
                                             usage=check_reg_parser.usage,
                                             help="Check registration")
    parser_check_reg.set_defaults(func=run_check_reg)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
