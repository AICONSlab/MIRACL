import os
import sys
import argparse
import subprocess


def run_reg_clar(parser, args):
    miracl_home = os.environ['MIRACL_HOME']

    args = vars(args)

    bash_args = '-f "%s" -n "%s" -r "%s"' % (args['folder'][0], args['conv_opts'][0], args['reg_opts'][0])

    subprocess.check_call('%s/flow/miracl_workflow_registration_clarity-allen_wb.sh %s' % (miracl_home, bash_args),
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
    parser_regclar.add_argument('-f', '--folder', nargs='+',
                                 help="input registration folder")
    parser_regclar.add_argument('-n', '--conv_opts', nargs='+', metavar='',
                                 help="file conversion options")
    parser_regclar.add_argument('-r', '--reg_opts', nargs='+', metavar='',
                                 help="registration options")


    parser_regclar.set_defaults(func=run_reg_clar)

    # sta
    parser_sta = subparsers.add_parser('sta', help="")
    parser_sta.add_argument('-f',
                            help="")
    parser_sta.add_argument('-o',
                            help="")
    parser_sta.add_argument('-n',
                            help="")

    parser_sta.set_defaults(func=run_sta)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(parser, args)


if __name__ == '__main__':
    main()
