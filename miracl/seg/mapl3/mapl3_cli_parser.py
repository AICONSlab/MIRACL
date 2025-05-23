"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca) for
Ahmadreza Attapour's (a.attarpour@mail.utoronto.ca) MAPL3 implementation into
Maged Goubran's MIRACL.

This code is the parser for the the MAPL3 segmentation module.
"""

from argparse import (
    ArgumentParser,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_groups_dict


class Mapl3Parser:
    """
    Command-line argument parser for MAPL3.

    :param input: A required string argument that specifies the input file path.
    :param output: A required string argument that specifies the output file path.
    :param cpu_load: An optional float argument that specifies the fraction of CPU's used for parallelization.
    :param patch_size: An optional flag that of type int.
    :param gamma: An optional flag of type float for gamma correction.

    :returns: The parsed arguments.
    """

    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> ArgumentParser:
        # Define custom parser
        parser = ArgumentParser(
            prog="miracl seg mapl3",
            add_help=True,
        )

        # Create parser args
        parser_processor = MiraclArgumentProcessor()
        # parser_processor.create_parser_arguments(parser, mapl3_groups_dict, "module")
        parser_processor.create_parser_arguments(
            parser,
            mapl3_groups_dict,
            MiraclArgumentProcessor.ModuleType.MODULE,
        )

        return parser


if __name__ == "__main__":
    args_parser = Mapl3Parser()
    args = args_parser.parser.parse_args()
