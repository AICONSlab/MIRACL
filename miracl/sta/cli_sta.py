import os
import sys
import argparse
import subprocess


def run_sta_tensor(parser, args):
    miracl_home = os.environ['MIRACL_HOME']
    args = vars(args)

    if args['help']:
        subprocess.Popen('%s/sta/miracl_sta_track_primary_eigen.sh -h' % miracl_home,
                         shell=True)
    else:
        bash_args = '-f %s -n "%s" -r "%s"' % (args['folder'], args['conv_opts'][0], args['reg_opts'][0])

        subprocess.check_call('%s/sta/miracl_sta_track_primary_eigen.sh %s' % (miracl_home, bash_args),
                              shell=True,
                              stderr=subprocess.STDOUT)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # sta
    parser_sta = subparsers.add_parser('track_tensor', add_help=False, help="")
    parser_sta.add_argument('-f',
                            help="")
    parser_sta.add_argument('-o',
                            help="")
    parser_sta.add_argument('-n',
                            help="")
    parser_sta.add_argument('-h', '--help', action='store_true')

    parser_sta.set_defaults(func=run_sta_tensor)

    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
