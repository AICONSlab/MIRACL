import sys
from abc import abstractmethod, ABC
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser

import miracl.seg.mapl3.mapl3_generate_patch as mapl3_generate_patch
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_generate_patch import (
    GeneratePatch as obj_generate_patch,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_preprocessing_parallel import (
    PreprocessingParallel as obj_preprocess_parallel,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_interface_folder import (
    InterfaceFolder as obj_interface_folder,
)
from miracl import miracl_logger

logger = miracl_logger.logger


class GeneratePatch(ABC):
    @abstractmethod
    def generate_patch(
        self,
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    ):
        pass


class PreprocessingParallel(ABC):
    @abstractmethod
    def preprocess(self, generate_patch_output_folder):
        pass


class MAPL3GeneratePatch(GeneratePatch):

    def generate_patch(
        self,
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    ):
        logger.debug("GENERATE PATCH IN INTERFACE:")
        logger.debug(f"Input file: {generate_patch_input_folder.dirpath}")
        logger.debug(f"Output file: {generate_patch_output_folder.dirpath}")
        logger.debug(f"CPU load: {generate_patch_cpu_load.content}")
        logger.debug(f"Patch size: {generate_patch_patch_size.content}")
        logger.debug(f"Gamma: {generate_patch_gamma.content}")

        mapl3_generate_patch.main(
            generate_patch_input_folder,
            generate_patch_output_folder,
            generate_patch_cpu_load,
            generate_patch_patch_size,
            generate_patch_gamma,
        )


class MAPL3PreprocessingParallel(PreprocessingParallel):

    def preprocess(self, generate_patch_output_folder):
        logger.debug("PREPROCESS PARALLEL IN INTERFACE:")
        logger.debug(
            f"Input from generate patch -> output folder: {generate_patch_output_folder.dirpath}"
        )


def main():
    # Create an instance of the parser
    parser = Mapl3Parser()

    # Parse the command-line arguments
    args = vars(parser.parser.parse_args())

    # Assign cli input args to Pydantic objects
    generate_patch_input_folder = obj_generate_patch.input
    generate_patch_input_folder.dirpath = args[generate_patch_input_folder.cli_l_flag]

    mapl3_results_folder = obj_generate_patch.output
    mapl3_results_folder.dirpath = args[
        mapl3_results_folder.cli_l_flag
    ]  # Input of "output_folder" flag

    generate_patch_cpu_load = obj_generate_patch.cpu_load
    generate_patch_cpu_load.content = args[generate_patch_cpu_load.cli_l_flag]

    generate_patch_patch_size = obj_generate_patch.patch_size
    generate_patch_patch_size.content = args[generate_patch_patch_size.cli_l_flag]

    generate_patch_gamma = obj_generate_patch.gamma
    generate_patch_gamma.content = args[generate_patch_gamma.cli_l_flag]

    seg_output_folder = obj_interface_folder.output
    seg_output_folder.dirpath = mapl3_results_folder.dirpath / "mapl3_seg"

    generate_patch_output_folder = obj_generate_patch.output
    generate_patch_output_folder.dirpath = (
        seg_output_folder.dirpath / "generated_patches"
    )

    patch_generator = MAPL3GeneratePatch()
    parallel_preprocessor = MAPL3PreprocessingParallel()

    patch_generator.generate_patch(
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    )

    parallel_preprocessor.preprocess(generate_patch_output_folder)


if __name__ == "__main__":
    main()
