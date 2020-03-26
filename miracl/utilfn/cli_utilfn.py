import sys
import argparse
from miracl.utilfn import miracl_utilfn_endstatement, miracl_utilfn_create_brainmask, miracl_utilfn_extract_lbl, \
    miracl_utilfn_int_corr_tiffs


def run_endstatement(parser, args):
    miracl_utilfn_endstatement.main(args)


def run_brainmask(parser, args):
    miracl_utilfn_create_brainmask.main(args)


def run_extract_lbl(parser, args):
    miracl_utilfn_extract_lbl.main(args)


def run_int_corr(parser, args):
    miracl_utilfn_int_corr_tiffs.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # end statement
    end_state_parser = miracl_utilfn_endstatement.parsefn()
    parser_end_state = subparsers.add_parser('end_state', parents=[end_state_parser], add_help=False,
                                             help='end statement')
    parser_end_state.set_defaults(func=run_endstatement)    

    # brain mask
    brain_mask_parser = miracl_utilfn_create_brainmask.parsefn()
    parser_brain_mask = subparsers.add_parser('brain_mask', parents=[brain_mask_parser], add_help=False,
                                              usage=brain_mask_parser.usage,
                                              help='Generate brain mask')
    parser_brain_mask.set_defaults(func=run_brainmask)

    # extract_lbl
    extract_lbl_parser = miracl_utilfn_extract_lbl.parsefn()
    parser_extract_lbl = subparsers.add_parser('extract_lbl', parents=[extract_lbl_parser], add_help=False,
                                               usage=extract_lbl_parser.usage,
                                               help='Extract label')
    parser_extract_lbl.set_defaults(func=run_extract_lbl)

    # int_corr
    int_corr_parser = miracl_utilfn_int_corr_tiffs.parsefn()
    parser_int_corr = subparsers.add_parser('int_corr', parents=[int_corr_parser], add_help=False,
                                            usage=int_corr_parser.usage,
                                            help='Intensity correct tiff stack')
    parser_int_corr.set_defaults(func=run_int_corr)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
