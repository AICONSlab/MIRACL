# Import required methods
from typing import Dict, Any
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger

# Import MAPL3 objects
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.seg.mapl3 import mapl3_interface

logger = miracl_logger.logger


def main() -> None:
    """
    Main function to run the MAPL3 pipeline.

    This function performs the following steps:
    1. Parses command-line arguments
    2. Processes MIRACL objects with parsed arguments
    3. Calls the MAPL3 module interface

    :return: None
    """
    # Run parser and return parsed args as dict
    parser: Mapl3Parser = Mapl3Parser()
    args: Dict[str, Any] = vars(parser.parser.parse_args())

    # Assign the parsed args to the attributes of their respective object
    processor: MiraclArgumentProcessor = MiraclArgumentProcessor()
    processor.process_miracl_objects(
        seg_mapl3_objs,
        args,
        MiraclArgumentProcessor.ModuleType.MODULE,
    )

    # Call the MAPL3 module interface
    mapl3_interface.main(seg_mapl3_objs)


if __name__ == "__main__":
    main()
