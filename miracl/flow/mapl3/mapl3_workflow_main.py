from miracl.flow.mapl3.mapl3_workflow_cli_parser import Mapl3WorkflowParser
from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger

# Import MAPL3 objects
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_object_dict as reg_mapl3_objs,
    conv_object_dict as conv_mapl3_objs,
)

from miracl.flow.mapl3 import mapl3_workflow_interface

logger = miracl_logger.logger


def main():
    # Run parser and return parsed args as dict
    parser = Mapl3WorkflowParser()
    args = vars(parser.parser.parse_args())

    # Combine objects dicts
    mapl3_workflow_objs = {**seg_mapl3_objs, **reg_mapl3_objs, **conv_mapl3_objs}

    # Assign the parsed args to the attributes of their respective object
    processor = MiraclArgumentProcessor()
    processor.process_miracl_objects(mapl3_workflow_objs, args)

    # Call the MAPL3 module interface
    mapl3_workflow_interface.main(mapl3_workflow_objs)


if __name__ == "__main__":
    main()
