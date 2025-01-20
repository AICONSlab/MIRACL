"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca) for
Ahmadreza Attapour's (a.attarpour@mail.utoronto.ca) MAPL3 implementation into
AICONs lab's MIRACL.

This code calls the MAPL3 workflow interface.
"""

from typing import Dict, Any
from miracl.flow.mapl3.mapl3_workflow_cli_parser import Mapl3WorkflowParser
from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger
from logging import Logger

# Import MAPL3 objects
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_object_dict as reg_mapl3_objs,
    conv_object_dict as conv_mapl3_objs,
)

from miracl.flow.mapl3 import mapl3_workflow_interface

logger: Logger = miracl_logger.logger


def main() -> None:
    """
    Main function to run the MAPL3 workflow.

    This function performs the following steps:
    1. Parses command-line arguments
    2. Combines MAPL3 object dictionaries
    3. Processes MIRACL objects with parsed arguments
    4. Calls the MAPL3 module interface

    :return: None
    """
    # Run parser and return parsed args as dict
    parser: Mapl3WorkflowParser = Mapl3WorkflowParser()
    args: Dict[str, Any] = vars(parser.parser.parse_args())

    # Combine objects dicts
    mapl3_workflow_objs: Dict[str, Any] = {
        **seg_mapl3_objs,
        **reg_mapl3_objs,
        **conv_mapl3_objs,
    }

    # Assign the parsed args to the attributes of their respective object
    processor: MiraclArgumentProcessor = MiraclArgumentProcessor()
    processor.process_miracl_objects(mapl3_workflow_objs, args)

    # Call the MAPL3 module interface
    mapl3_workflow_interface.main(mapl3_workflow_objs)


if __name__ == "__main__":
    main()
