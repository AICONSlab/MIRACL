import os
import sys
import argparse
from miracl.utilfn import miracl_utilfn_endstatement


def run_endstatmenet(parser, args):
    miracl_utilfn_endstatement.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # end statement
    end_state_parser = miracl_utilfn_endstatement.parsefn()
    parser_end_state = subparsers.add_parser('endstate', parents=[end_state_parser], add_help=False,
                                            help='end statement')

    parser_end_state.set_defaults(func=run_endstatmenet)


    return parser


def main(args=sys.argv[1:]):
    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
