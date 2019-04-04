import os
import sys
import argparse
import subprocess
import logging
from pathlib import Path


# logging.basicConfig(format='%(asctime)15s - %(levelname)s - %(message)s', level=logging.DEBUG)
# logger = logging.getLogger()


def run_reg_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    print "%s" % miracl_home

    args = vars(args)

    bash_args = '-f %s -n "%s" -r "%s"' % (args['folder'], args['conv_opts'][0], args['reg_opts'][0])
    print "running CLARITY to Allen registration workflow with the following arguments: \n %s" % bash_args

    subprocess.check_call('%s/flow/miracl_workflow_registration_clarity-allen_wb.sh %s' % (miracl_home, bash_args),
                          shell=True,
                          stderr=subprocess.STDOUT)


def run_seg(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    args = vars(args)

    bash_args = '-f %s -t %s -v %s -s "%s" -e "%s"' % (args['folder'], args['type'], args['vox_res'],
                                                       args['seg_opts'][0], args['ext_opts'][0])

    subprocess.check_call('%s/flow/miracl_workflow_segmentation_clarity.sh %s' % (miracl_home, bash_args),
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

    # reg_clarity
    parser_regclar = subparsers.add_parser('reg_clar', help="whole-brain clarity registration to Allen atlas")
    parser_regclar.add_argument('-f', '--folder', metavar='',
                                help="input registration folder")
    parser_regclar.add_argument('-n', '--conv_opts', nargs='+', metavar='',
                                help="file conversion options")
    parser_regclar.add_argument('-r', '--reg_opts', nargs='+', metavar='',
                                help="registration options")

    parser_regclar.set_defaults(func=run_reg_clar)

    # sta
    parser_sta = subparsers.add_parser('sta', help="Structure Tensor Analysis (STA)")
    parser_sta.add_argument('-f',
                            help="")
    parser_sta.add_argument('-o',
                            help="")
    parser_sta.add_argument('-n',
                            help="")

    parser_sta.set_defaults(func=run_sta)

    # seg
    parser_seg = subparsers.add_parser('seg', help="CLARITY segmentation")
    parser_seg.add_argument('-f', '--folder', metavar='',
                            help="input segmentation folder")
    parser_seg.add_argument('-t', '--type', metavar='',
                            help="segmentation type: virus, cFOS, sparse or nuclear")
    parser_seg.add_argument('-v', '--vox_res', metavar='',
                            help="voxel resolution/size")
    parser_seg.add_argument('-s', '--seg_opts', nargs='+', metavar='',
                            help="segmentation options")
    parser_seg.add_argument('-e', '--ext_opts', nargs='+', metavar='',
                            help="feature extraction options")

    parser_seg.set_defaults(func=run_seg)

    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
