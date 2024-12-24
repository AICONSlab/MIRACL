import sys
from abc import abstractmethod, ABC
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser

import miracl.seg.mapl3.mapl3_generate_patch as mapl3_generate_patch
import miracl.seg.mapl3.mapl3_preprocessing_parallel as mapl3_preprocessing_parallel
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_generate_patch import (
    GeneratePatch as obj_generate_patch,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_preprocessing_parallel import (
    PreprocessingParallel as obj_preprocess_parallel,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_interface_folder import (
    InterfaceSubfolders as obj_subfolders,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_inference import (
    Inference as obj_inference,
)
from miracl import miracl_logger

logger = miracl_logger.logger
production = False


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
    def preprocess(
        self,
        generate_patch_output_folder,
        preprocess_parallel_cpu_load,
        preprocess_parallel_cl_percentage,
        preprocess_parallel_cl_lsm_footprint,
        preprocess_parallel_cl_back_footprint,
        preprocess_parallel_cl_back_downsample,
        preprocess_parallel_cl_lsm_vs_back_weight,
        preprocess_parallel_deconv_bin_thr,
        preprocess_parallel_deconv_sigma,
        preprocess_parallel_save_intermediate_results,
    ):
        pass


class Inference(ABC):
    @abstractmethod
    def run_inference(
        self,
        generate_patch_output_folder,
        inference_output_folder,
        inference_config,
        inference_model_path,
        inference_tissue_percentage_threshold,
        inference_gpu_index,
        inference_binarization_threshold,
        inference_save_prob_map,
    ):
        pass


class MAPL3Inference(Inference):

    def run_inference(
        self,
        generate_patch_output_folder,
        inference_output_folder,
        inference_config,
        inference_model_path,
        inference_tissue_percentage_threshold,
        inference_gpu_index,
        inference_binarization_threshold,
        inference_save_prob_map,
    ):
        logger.debug("INFERENCE IN INTERFACE:")
        logger.debug(
            f"Generated patches output: {generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"Config file: {inference_config.filepath}")
        logger.debug(f"Model path: {inference_model_path.filepath}")
        logger.debug(f"Ouput folder path: {inference_output_folder.dirpath}")
        logger.debug(
            f"Tissue percentage threshold: {inference_tissue_percentage_threshold.content}"
        )
        logger.debug(f"GPU index: {inference_gpu_index.content}")
        logger.debug(
            f"Binarization threshold: {inference_binarization_threshold.content}"
        )
        logger.debug(f"Save prob map: {inference_save_prob_map.content}")


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

        if production:
            mapl3_generate_patch.main(
                generate_patch_input_folder,
                generate_patch_output_folder,
                generate_patch_cpu_load,
                generate_patch_patch_size,
                generate_patch_gamma,
            )


class MAPL3PreprocessingParallel(PreprocessingParallel):

    def preprocess(
        self,
        generate_patch_output_folder,
        preprocess_parallel_cpu_load,
        preprocess_parallel_cl_percentage,
        preprocess_parallel_cl_lsm_footprint,
        preprocess_parallel_cl_back_footprint,
        preprocess_parallel_cl_back_downsample,
        preprocess_parallel_cl_lsm_vs_back_weight,
        preprocess_parallel_deconv_bin_thr,
        preprocess_parallel_deconv_sigma,
        preprocess_parallel_save_intermediate_results,
    ):
        logger.debug("PREPROCESS PARALLEL IN INTERFACE:")
        logger.debug(
            f"Input from generate patch -> output folder: {generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"cpu_load: {preprocess_parallel_cpu_load.content}")
        logger.debug(f"cl_percentage: {preprocess_parallel_cl_percentage.content}")
        logger.debug(
            f"cl_lsm_footprint: {preprocess_parallel_cl_lsm_footprint.content}"
        )
        logger.debug(
            f"cl_back_footprint: {preprocess_parallel_cl_back_footprint.content}"
        )
        logger.debug(
            f"cl_back_downsample: {preprocess_parallel_cl_back_downsample.content}"
        )
        logger.debug(
            f"cl_lsm_vs_back_weight: {preprocess_parallel_cl_lsm_vs_back_weight.content}"
        )
        logger.debug(f"deconv_bin_thr: {preprocess_parallel_deconv_bin_thr.content}")
        logger.debug(f"deconv_sigma: {preprocess_parallel_deconv_sigma.content}")
        logger.debug(
            f"save_intermediate_results: {preprocess_parallel_save_intermediate_results.content}"
        )

        if production:
            mapl3_preprocessing_parallel.main(
                generate_patch_output_folder,
                preprocess_parallel_cpu_load,
                preprocess_parallel_cl_percentage,
                preprocess_parallel_cl_lsm_footprint,
                preprocess_parallel_cl_back_footprint,
                preprocess_parallel_cl_back_downsample,
                preprocess_parallel_cl_lsm_vs_back_weight,
                preprocess_parallel_deconv_bin_thr,
                preprocess_parallel_deconv_sigma,
                preprocess_parallel_save_intermediate_results,
            )


def main():
    # Create an instance of the parser
    parser = Mapl3Parser()

    # Parse the command-line arguments
    args = vars(parser.parser.parse_args())

    #############################################
    # ASSIGN CLI INPUT ARGS TO PYDANTIC OBJECTS #
    #############################################

    ##################
    # GENERATE PATCH #
    ##################

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

    seg_output_folder = obj_subfolders.seg_output
    seg_output_folder.dirpath = mapl3_results_folder.dirpath / "mapl3_seg"

    generate_patch_output_folder = obj_subfolders.generated_patches_output
    generate_patch_output_folder.dirpath = (
        seg_output_folder.dirpath / "generated_patches"
    )

    ###########################################################################

    #######################
    # PREPROCESS PARALLEL #
    #######################

    preprocess_parallel_cpu_load = obj_preprocess_parallel.cpu_load
    preprocess_parallel_cpu_load.content = args[preprocess_parallel_cpu_load.cli_l_flag]

    preprocess_parallel_cl_percentage = obj_preprocess_parallel.cl_percentage
    preprocess_parallel_cl_percentage.content = args[
        preprocess_parallel_cl_percentage.cli_l_flag
    ]

    preprocess_parallel_cl_lsm_footprint = obj_preprocess_parallel.cl_lsm_footprint
    preprocess_parallel_cl_lsm_footprint.content = args[
        preprocess_parallel_cl_lsm_footprint.cli_l_flag
    ]

    preprocess_parallel_cl_back_footprint = obj_preprocess_parallel.cl_back_footprint
    preprocess_parallel_cl_back_footprint.content = args[
        preprocess_parallel_cl_back_footprint.cli_l_flag
    ]

    preprocess_parallel_cl_back_downsample = obj_preprocess_parallel.cl_back_downsample
    preprocess_parallel_cl_back_downsample.content = args[
        preprocess_parallel_cl_back_downsample.cli_l_flag
    ]

    preprocess_parallel_cl_lsm_vs_back_weight = (
        obj_preprocess_parallel.lsm_vs_back_weight
    )
    preprocess_parallel_cl_lsm_vs_back_weight.content = args[
        preprocess_parallel_cl_lsm_vs_back_weight.cli_l_flag
    ]

    preprocess_parallel_deconv_bin_thr = obj_preprocess_parallel.deconv_bin_thr
    preprocess_parallel_deconv_bin_thr.content = args[
        preprocess_parallel_deconv_bin_thr.cli_l_flag
    ]

    preprocess_parallel_deconv_sigma = obj_preprocess_parallel.deconv_sigma
    preprocess_parallel_deconv_sigma.content = args[
        preprocess_parallel_deconv_sigma.cli_l_flag
    ]

    preprocess_parallel_save_intermediate_results = (
        obj_preprocess_parallel.save_intermediate_results
    )
    preprocess_parallel_save_intermediate_results.content = args[
        preprocess_parallel_save_intermediate_results.cli_l_flag
    ]

    ###########################################################################

    #############
    # INFERENCE #
    #############

    inference_config = obj_inference.config
    inference_config.filepath = args[inference_config.cli_l_flag]

    inference_model_path = obj_inference.model_path
    inference_model_path.filepath = args[inference_model_path.cli_l_flag]

    print(f"HERHERHERHEHREHE: {args[inference_model_path.cli_l_flag]}")
    print(f"HERHERHEHREHREHR: {inference_model_path.filepath}")

    inference_output_folder = obj_subfolders.inference_output
    inference_output_folder.dirpath = mapl3_results_folder.dirpath / "mapl3_inference"

    inference_tissue_percentage_threshold = obj_inference.tissue_percentage_threshold
    inference_tissue_percentage_threshold.content = args[
        inference_tissue_percentage_threshold.cli_l_flag
    ]

    inference_gpu_index = obj_inference.gpu_index
    inference_gpu_index.content = args[inference_gpu_index.cli_l_flag]

    inference_binarization_threshold = obj_inference.binarization_threshold
    inference_binarization_threshold.content = args[
        inference_binarization_threshold.cli_l_flag
    ]

    inference_save_prob_map = obj_inference.save_prob_map
    inference_save_prob_map.content = args[inference_save_prob_map.cli_l_flag]

    ###########################################################################

    patch_generator = MAPL3GeneratePatch()
    parallel_preprocessor = MAPL3PreprocessingParallel()
    inference = MAPL3Inference()

    patch_generator.generate_patch(
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    )

    parallel_preprocessor.preprocess(
        generate_patch_output_folder,
        preprocess_parallel_cpu_load,
        preprocess_parallel_cl_percentage,
        preprocess_parallel_cl_lsm_footprint,
        preprocess_parallel_cl_back_footprint,
        preprocess_parallel_cl_back_downsample,
        preprocess_parallel_cl_lsm_vs_back_weight,
        preprocess_parallel_deconv_bin_thr,
        preprocess_parallel_deconv_sigma,
        preprocess_parallel_save_intermediate_results,
    )

    inference.run_inference(
        generate_patch_output_folder,
        inference_output_folder,
        inference_config,
        inference_model_path,
        inference_tissue_percentage_threshold,
        inference_gpu_index,
        inference_binarization_threshold,
        inference_save_prob_map,
    )


if __name__ == "__main__":
    main()
