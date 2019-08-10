import os
import sys
import argparse
import subprocess
from miracl.seg import miracl_seg_feat_extract, miracl_seg_voxelize_parallel


def run_seg_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/miracl/seg/miracl_seg_clarity_neurons_wrapper.sh -h' % miracl_home,
                         shell=True)
    else:

        bash_args = '-f "%s" -t "%s" -p "%s"' % (args['folder'], args['type'], args['chan_pre'])

        subprocess.check_call('%s/miracl/seg/miracl_seg_clarity_neurons_wrapper.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def run_feat_extract(parser, args):
    miracl_seg_feat_extract.main(args)


def run_voxelize(parser, args):
    miracl_seg_voxelize_parallel.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # seg clar
    parser_seg_clar = subparsers.add_parser('clar', add_help=False,
                                            help="segment CLARITY volume")
    parser_seg_clar.add_argument('-f', '--folder',
                                 help="input registration folder")
    parser_seg_clar.add_argument('-t', '--type', metavar='',
                                 help="segmentation type")
    parser_seg_clar.add_argument('-p', '--chan_pre', metavar='',
                                 help="channel_prefix")
    parser_seg_clar.add_argument('-h', '--help', action='store_true')

    parser_seg_clar.set_defaults(func=run_seg_clar)

    # feat extract
    feat_extract_parser = miracl_seg_feat_extract.parsefn()
    parser_feat_extract = subparsers.add_parser('feat_extract', parents=[feat_extract_parser], add_help=False,
                                            help='Extract features from CLARITY seg')

    parser_feat_extract.set_defaults(func=run_feat_extract)

    # voxelize
    voxelize_parser = miracl_seg_voxelize_parallel.parsefn()
    parser_voxelize = subparsers.add_parser('voxelize', parents=[voxelize_parser], add_help=False,
                                            help='convert Tiff stacks to Nii')

    parser_voxelize.set_defaults(func=run_voxelize)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
