import argparse
import os
import subprocess
import sys

from miracl.seg.mapl3 import mapl3_cli_parser, mapl3_interface
from miracl.seg import (
    ace_interface,
    ace_parser,
    miracl_seg_feat_extract,
    miracl_seg_voxelize_parallel,
    miracl_seg_feats_cortex,
    miracl_instance_segmentation_interface,
    miracl_instance_segmentation_parser,
    miracl_seg_count_neurons_json,
    ace_finetune_model,
)


def run_seg_clar(parser, args):
    miracl_home = os.environ["MIRACL_HOME"]
    args = vars(args)

    if sys.argv[-2] == "seg" and sys.argv[-1] == "clar":
        subprocess.Popen(
            "%s/seg/miracl_seg_clarity_neurons_wrapper.sh" % miracl_home, shell=True
        )
    else:
        if args["help"]:
            subprocess.Popen(
                "%s/seg/miracl_seg_clarity_neurons_wrapper.sh -h" % miracl_home,
                shell=True,
            )
        else:
            bash_args = '-f "%s" -t "%s" -p "%s"' % (
                args["folder"],
                args["type"],
                args["chan_pre"],
            )

            subprocess.check_call(
                "%s/seg/miracl_seg_clarity_neurons_wrapper.sh %s"
                % (miracl_home, bash_args),
                shell=True,
                stderr=subprocess.STDOUT,
            )


def run_feat_extract(parser, args):
    miracl_seg_feat_extract.main(args)


def run_feat_extract_ctx(parser, args):
    miracl_seg_feats_cortex.main(args)


def run_voxelize(parser, args):
    miracl_seg_voxelize_parallel.main(args)


def run_mapl3(parser, args):
    mapl3_interface.main()


def run_ace(parser, args):
    ace_interface.main(args=args)


def run_ace_finetune(parser, args):
    args = vars(args)
    ace_finetune_model.main(args=args)


def run_instance_parallel(parser, args):
    miracl_instance_segmentation_interface.main(args=args)


def run_count_neurons_json(parser, args):
    miracl_seg_count_neurons_json.main(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # seg clar
    parser_seg_clar = subparsers.add_parser(
        "clar", add_help=False, help="segment CLARITY volume"
    )
    parser_seg_clar.add_argument("-f", "--folder", help="input registration folder")
    parser_seg_clar.add_argument("-t", "--type", metavar="", help="segmentation type")
    parser_seg_clar.add_argument("-p", "--chan_pre", metavar="", help="channel_prefix")
    parser_seg_clar.add_argument("-h", "--help", action="store_true")

    parser_seg_clar.set_defaults(func=run_seg_clar)

    # feat extract
    feat_extract_parser = miracl_seg_feat_extract.parsefn()
    parser_feat_extract = subparsers.add_parser(
        "feat_extract",
        parents=[feat_extract_parser],
        add_help=False,
        usage=feat_extract_parser.usage,
        help="Extract features from CLARITY seg",
    )

    parser_feat_extract.set_defaults(func=run_feat_extract)

    # feat extract_ctx
    feat_extract_ctx_parser = miracl_seg_feats_cortex.parsefn()
    parser_feat_ctx_extract = subparsers.add_parser(
        "feat_extract_ctx",
        parents=[feat_extract_ctx_parser],
        add_help=False,
        usage=feat_extract_ctx_parser.usage,
        help="Extract features from CLARITY seg",
    )

    parser_feat_ctx_extract.set_defaults(func=run_feat_extract_ctx)

    # voxelize
    voxelize_parser = miracl_seg_voxelize_parallel.parsefn()
    parser_voxelize = subparsers.add_parser(
        "voxelize",
        parents=[voxelize_parser],
        add_help=False,
        usage=voxelize_parser.usage,
        help="convert Tiff stacks to Nii",
    )

    parser_voxelize.set_defaults(func=run_voxelize)

    # MAPL3
    mapl3_parser_class = mapl3_cli_parser.Mapl3Parser
    mapl3_parsefn = mapl3_parser_class.parsefn()
    parser_mapl3 = subparsers.add_parser(
        "mapl3",
        parents=[mapl3_parsefn],
        add_help=False,
        usage=mapl3_parsefn.usage,
        help="mapping axonal projection in light sheet microscopy in 3d",
    )

    parser_mapl3.set_defaults(func=run_mapl3)

    # ace
    ace_parser_class = ace_parser.aceParser()
    ace_parsefn = ace_parser_class.parsefn()
    parser_ace = subparsers.add_parser(
        "ace",
        parents=[ace_parsefn],
        add_help=False,
        usage=ace_parsefn.usage,
        description=ace_parsefn.description,
        help="AI-based Cartography of neural Ensembles (ACE)",
    )

    parser_ace.set_defaults(func=run_ace)

    # ace finetune
    ace_finetune_parser = ace_finetune_model.parsefn()
    parser_ace_finetune = subparsers.add_parser(
        "ace_finetune",
        parents=[ace_finetune_parser],
        add_help=False,
        usage=ace_finetune_parser.usage,
        help="Fine-tune ACE model",
    )

    parser_ace_finetune.set_defaults(func=run_ace_finetune)

    # ace instance segmentation
    instance_parser_class = (
        miracl_instance_segmentation_parser.MIRACLInstanceSegParser()
    )
    instance_parsefn = instance_parser_class.parsefn()
    parser_instance = subparsers.add_parser(
        miracl_instance_segmentation_parser.PROG_NAME,
        parents=[instance_parsefn],
        add_help=False,
        usage=instance_parsefn.usage,
        description=instance_parsefn.description,
        help="Instance segmentation step of ACE segmentation",
    )

    parser_instance.set_defaults(func=run_instance_parallel)

    # count_neurons_json
    count_neurons_json_parser = miracl_seg_count_neurons_json.parsefn()
    parser_count_neurons_json = subparsers.add_parser(
        miracl_seg_count_neurons_json.PROG_NAME,
        parents=[count_neurons_json_parser],
        add_help=False,
        usage=count_neurons_json_parser.usage,
        description=count_neurons_json_parser.description,
        help="Count neurons in json file",
    )

    parser_count_neurons_json.set_defaults(func=run_count_neurons_json)

    return parser


def main(args=None):
    if args is None:
        args = sys.argv[2:]

    parser = get_parser()
    args = parser.parse_args(args)
    args.func(parser, args)


if __name__ == "__main__":
    main()
