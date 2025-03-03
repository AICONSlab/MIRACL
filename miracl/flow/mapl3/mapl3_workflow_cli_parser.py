"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca) for
Ahmadreza Attapour's (a.attarpour@mail.utoronto.ca) MAPL3 implementation into
Maged Goubran's MIRACL.

This code is the parser for the the MAPL3 workflow.
"""

from argparse import (
    ArgumentParser,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_groups_dict
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_groups_dict,
    conv_groups_dict,
)


class Mapl3WorkflowParser:
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
            prog="miracl flow mapl3",
            add_help=True,
        )

        # Combine the MAPL3 module parser with the additional args of the flow,
        # in this case the registration module
        combined_groups_dict = {
            **mapl3_groups_dict,
            **conv_groups_dict,
            **reg_groups_dict,
        }

        # Create parser args
        parser_processor = MiraclArgumentProcessor()
        # parser_processor.create_parser_arguments(parser, combined_groups_dict, "mapl3")
        parser_processor.create_parser_arguments(
            parser,
            combined_groups_dict,
            MiraclArgumentProcessor.ModuleType.FLOW_MAPL3,
        )

        return parser


if __name__ == "__main__":
    args_parser = Mapl3WorkflowParser()
    args = args_parser.parser.parse_args()
