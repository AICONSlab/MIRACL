from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger

# Import MAPL3 objects
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.seg.mapl3 import mapl3_interface

logger = miracl_logger.logger


def main():
    # Run parser and return parsed args as dict
    parser = Mapl3Parser()
    args = vars(parser.parser.parse_args())

    # Assign the parsed args to the attributes of their respective object
    processor = MiraclArgumentProcessor()
    processor.process_miracl_objects(seg_mapl3_objs, args)

    # Call the MAPL3 module interface
    mapl3_interface.main(seg_mapl3_objs)


if __name__ == "__main__":
    main()
