import sys
import argparse
from miracl.seg import miracl_seg_feat_extract, ace_parser, ace
import importlib

# INFO: Runs segmentation script
def run_feat_extract(parser, args):
    miracl_seg_feat_extract.main(args)

def run_ace(parser, args):
    ace.main(args)

def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # feat extract
    feat_extract_parser = miracl_seg_feat_extract.parsefn()
    parser_feat_extract = subparsers.add_parser('feat_extract', parents=[feat_extract_parser], add_help=False,
                                                usage=feat_extract_parser.usage,
                                                help='Extract features from CLARITY seg')

    parser_feat_extract.set_defaults(func=run_feat_extract)

    # ace
    ace_parser_class = ace_parser.aceParser()
    ace_parsefn = ace_parser_class.parsefn()
    parser_ace = subparsers.add_parser('ace', parents=[ace_parsefn],
                                       add_help=False,
                                       usage=ace_parsefn.usage,
                                       description=ace_parsefn.description,
                                       help='AI-based Cartography of neural Ensembles (ACE)')

    # parser_ace.set_defaults(func=lambda parser, args: print(args.voxel_size))
    parser_ace.set_defaults(func=run_ace)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    print(args)
    args.func(parser, args)


if __name__ == '__main__':
    main()
