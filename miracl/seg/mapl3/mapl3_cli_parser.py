from argparse import (
    ArgumentError,
    ArgumentParser,
    RawDescriptionHelpFormatter,
    _HelpAction,
    SUPPRESS,
    Namespace,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import create_parser_arguments
from miracl.seg.mapl3.mapl3_cli_parser_args import groups_dict


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
        create_parser_arguments(parser, groups_dict, "module")

        return parser


if __name__ == "__main__":
    args_parser = Mapl3Parser()
    args = args_parser.parser.parse_args()
