from abc import abstractmethod, ABC
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
import miracl.seg.mapl3.mapl3_generate_patch as mapl3_generate_patch
from miracl.system.objs.objs_seg.objs_mapl3.objs_maple3_generate_patch import (
    GeneratePatch as obj_generate_patch,
)


class GeneratePatch(ABC):
    @abstractmethod
    def generate_patch(self, args):
        pass


class MAPL3GeneratePatch(GeneratePatch):

    def generate_patch(self, args):
        print("IN INTERFACE:")
        print(f"Input file: {args[obj_generate_patch.input.cli_l_flag]}")
        print(f"Output file: {args[obj_generate_patch.output.cli_l_flag]}")
        print(f"CPU load: {args[obj_generate_patch.cpu_load.cli_l_flag]}")
        print(f"Patch size: {args[obj_generate_patch.patch_size.cli_l_flag]}")
        print(f"Gamma: {args[obj_generate_patch.gamma.cli_l_flag]}")

        mapl3_generate_patch.main(args)


def main():
    # Create an instance of the parser
    parser = Mapl3Parser()

    # Parse the command-line arguments
    args = vars(parser.parser.parse_args())
    patch_generator = MAPL3GeneratePatch()
    patch_generator.generate_patch(args)


if __name__ == "__main__":
    main()
