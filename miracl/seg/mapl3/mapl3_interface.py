import sys
from abc import abstractmethod, ABC
from pathlib import Path

# Import MIRACL BaseModel and utility fns
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.utilfns.utilfns_paths import UtilfnsPaths
from miracl import miracl_logger

# Import MAPL3 scripts
import miracl.seg.mapl3.mapl3_generate_patch as mapl3_generate_patch
import miracl.seg.mapl3.mapl3_preprocessing_parallel as mapl3_preprocessing_parallel
import miracl.seg.mapl3.mapl3_inference as mapl3_inference
import miracl.seg.mapl3.mapl3_skeletonization as mapl3_skeletonization
import miracl.seg.mapl3.mapl3_patch_stacking as mapl3_patch_stacking

# Import MAPL3 objects
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
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_skeletonization import (
    Skeletonization as obj_skeletonization,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_patch_stacking import (
    PatchStacking as obj_patch_stacking,
)

###############################################################################

#############
# DEBUGGING #
#############

logger = miracl_logger.logger
production = False  # Set 'production' to False and set modules you want to run to True
generate_patch_enabled = False
preprocess_parallel_enabled = False
inference_enabled = False
skeletonization_enabled = False
patch_stacking_enabled = False

###############################################################################

####################
# ABSTRACT METHODS #
####################


class GeneratePatch(ABC):
    @abstractmethod
    def generate_patch(
        self,
        generate_patch_input_folder: MiraclObj,
        generate_patch_output_folder: MiraclObj,
        generate_patch_cpu_load: MiraclObj,
        generate_patch_patch_size: MiraclObj,
        generate_patch_gamma: MiraclObj,
    ) -> None:
        pass


class PreprocessingParallel(ABC):
    @abstractmethod
    def preprocess(
        self,
        generate_patch_output_folder: MiraclObj,
        preprocess_parallel_output_folder: MiraclObj,
        preprocess_parallel_cpu_load: MiraclObj,
        preprocess_parallel_cl_percentage: MiraclObj,
        preprocess_parallel_cl_lsm_footprint: MiraclObj,
        preprocess_parallel_cl_back_footprint: MiraclObj,
        preprocess_parallel_cl_back_downsample: MiraclObj,
        preprocess_parallel_cl_lsm_vs_back_weight: MiraclObj,
        preprocess_parallel_deconv_bin_thr: MiraclObj,
        preprocess_parallel_deconv_sigma: MiraclObj,
        preprocess_parallel_save_intermediate_results: MiraclObj,
    ) -> None:
        pass


class Inference(ABC):
    @abstractmethod
    def run_inference(
        self,
        preprocess_parallel_output_folder: MiraclObj,
        generate_patch_output_folder: MiraclObj,
        inference_output_folder: MiraclObj,
        inference_config: MiraclObj,
        inference_model_path: MiraclObj,
        inference_tissue_percentage_threshold: MiraclObj,
        inference_gpu_index: MiraclObj,
        inference_binarization_threshold: MiraclObj,
        inference_save_prob_map: MiraclObj,
    ) -> None:
        pass


class Skeletonization(ABC):
    @abstractmethod
    def run_skeletonization(
        self,
        inference_output_folder,
        generate_patch_output_folder,
        skeletonization_output_folder,
        skeletonization_remove_small_obj_thr,
        skeletonization_cpu_load,
        skeletonization_dilate_distance_transform,
        skeletonization_eccentricity_thr,
        skeletonization_orientation_thr,
    ) -> None:
        pass


class PatchStacking(ABC):
    @abstractmethod
    def stack_patches(
        self,
        patch_stacking_output_folder,
        generate_patch_input_folder,
        skeletonization_output_folder,
        patch_stacking_cpu_load,
        patch_stacking_keep_image_type,
    ):
        pass


###############################################################################

####################
# CONCRETE CLASSES #
####################


class MAPL3GeneratePatch(GeneratePatch):

    def generate_patch(
        self,
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    ):
        logger.debug("###########################")
        logger.debug("GENERATE PATCH IN INTERFACE")
        logger.debug("###########################")
        logger.debug(
            f"generate_patch_input_folder: {generate_patch_input_folder.input_dirpath}"
        )
        logger.debug(
            f"generate_patch_output_folder: {generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"generate_patch_cpu_load: {generate_patch_cpu_load.content}")
        logger.debug(f"generate_patch_patch_size: {generate_patch_patch_size.content}")
        logger.debug(f"generate_patch_gamma: {generate_patch_gamma.content}")

        if production or generate_patch_enabled:
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
        preprocess_parallel_output_folder,
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
        logger.debug("################################")
        logger.debug("PREPROCESS PARALLEL IN INTERFACE")
        logger.debug("################################")
        logger.debug(
            f"Input from generate patch -> output folder: {generate_patch_output_folder.dirpath}"
        )
        logger.debug(
            f"preprocess_parallel_output_folder: {preprocess_parallel_output_folder.dirpath}"
        )
        logger.debug(
            f"preprocess_parallel_cpu_load: {preprocess_parallel_cpu_load.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_percentage: {preprocess_parallel_cl_percentage.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_lsm_footprint: {preprocess_parallel_cl_lsm_footprint.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_back_footprint: {preprocess_parallel_cl_back_footprint.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_back_downsample: {preprocess_parallel_cl_back_downsample.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_lsm_vs_back_weight: {preprocess_parallel_cl_lsm_vs_back_weight.content}"
        )
        logger.debug(
            f"preprocess_parallel_deconv_bin_thr: {preprocess_parallel_deconv_bin_thr.content}"
        )
        logger.debug(
            f"preprocess_parallel_deconv_sigma: {preprocess_parallel_deconv_sigma.content}"
        )
        logger.debug(
            f"preprocess_parallel_save_intermediate_results: {preprocess_parallel_save_intermediate_results.content}"
        )

        if production or preprocess_parallel_enabled:
            mapl3_preprocessing_parallel.main(
                generate_patch_output_folder,
                preprocess_parallel_output_folder,
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


class MAPL3Inference(Inference):

    def run_inference(
        self,
        preprocess_parallel_output_folder,
        generate_patch_output_folder,
        inference_output_folder,
        inference_config,
        inference_model_path,
        inference_tissue_percentage_threshold,
        inference_gpu_index,
        inference_binarization_threshold,
        inference_save_prob_map,
    ):
        logger.debug("######################")
        logger.debug("INFERENCE IN INTERFACE")
        logger.debug("######################")
        logger.debug(
            f"Processed generated patches output: {preprocess_parallel_output_folder.dirpath}"
        )
        logger.debug(
            f"Generated patches folder i.e. json file location: {generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"inference_config: {inference_config.filepath}")
        logger.debug(f"inference_model_path: {inference_model_path.filepath}")
        logger.debug(f"inference_output_folder: {inference_output_folder.dirpath}")
        logger.debug(
            f"inference_tissue_percentage_threshold: {inference_tissue_percentage_threshold.content}"
        )
        logger.debug(f"inference_gpu_index: {inference_gpu_index.content}")
        logger.debug(
            f"inference_binarization_threshold: {inference_binarization_threshold.content}"
        )
        logger.debug(f"inference_save_prob_map: {inference_save_prob_map.content}")

        if production or inference_enabled:
            mapl3_inference.main(
                preprocess_parallel_output_folder,
                generate_patch_output_folder,
                inference_output_folder,
                inference_config,
                inference_model_path,
                inference_tissue_percentage_threshold,
                inference_gpu_index,
                inference_binarization_threshold,
                inference_save_prob_map,
            )


class MAPL3Skeletonization(Skeletonization):

    def run_skeletonization(
        self,
        inference_output_folder: MiraclObj,
        generate_patch_output_folder: MiraclObj,
        skeletonization_output_folder: MiraclObj,
        skeletonization_remove_small_obj_thr: MiraclObj,
        skeletonization_cpu_load: MiraclObj,
        skeletonization_dilate_distance_transform: MiraclObj,
        skeletonization_eccentricity_thr: MiraclObj,
        skeletonization_orientation_thr: MiraclObj,
    ) -> None:
        logger.debug("############################")
        logger.debug("SKELETONIZATION IN INTERFACE")
        logger.debug("############################")
        logger.debug(f"inference_output_folder: {inference_output_folder.dirpath}")
        logger.debug(f"json file folder path: {generate_patch_output_folder.dirpath}")
        logger.debug(
            f"skeletonization_output_folder: {skeletonization_output_folder.dirpath}"
        )
        logger.debug(
            f"skeletonization_remove_small_obj_thr: {skeletonization_remove_small_obj_thr.content}"
        )
        logger.debug(f"skeletonization_cpu_load: {skeletonization_cpu_load.content}")
        logger.debug(
            f"skeletonization_dilate_distance_transform: {skeletonization_dilate_distance_transform.content}"
        )
        logger.debug(
            f"skeletonization_eccentricity_thr: {skeletonization_eccentricity_thr.content}"
        )
        logger.debug(
            f"skeletonization_orientation_thr: {skeletonization_orientation_thr.content}"
        )

        if production or skeletonization_enabled:
            mapl3_skeletonization.main(
                inference_output_folder,
                generate_patch_output_folder,
                skeletonization_output_folder,
                skeletonization_remove_small_obj_thr,
                skeletonization_cpu_load,
                skeletonization_dilate_distance_transform,
                skeletonization_eccentricity_thr,
                skeletonization_orientation_thr,
            )


class MAPL3PatchStacking(PatchStacking):

    def stack_patches(
        self,
        patch_stacking_output_folder,
        generate_patch_input_folder,
        skeletonization_output_folder,
        patch_stacking_cpu_load,
        patch_stacking_keep_image_type,
    ):
        logger.debug("###########################")
        logger.debug("PATCH STACKING IN INTERFACE")
        logger.debug("###########################")
        logger.debug(
            f"patch_stacking_output_folder: {patch_stacking_output_folder.dirpath}"
        )
        logger.debug(
            f"generate_patch_input_folder: {generate_patch_input_folder.input_dirpath}"
        )
        logger.debug(
            f"skeletonization_output_folder: {skeletonization_output_folder.dirpath}"
        )
        logger.debug(f"patch_stacking_cpu_load: {patch_stacking_cpu_load.content}")
        logger.debug(
            f"patch_stacking_keep_image_type: {patch_stacking_keep_image_type.content}"
        )

        if production or patch_stacking_enabled:
            mapl3_patch_stacking.main(
                patch_stacking_output_folder,
                generate_patch_input_folder,
                skeletonization_output_folder,
                patch_stacking_cpu_load,
                patch_stacking_keep_image_type,
            )


###############################################################################

########
# MAIN #
########


def main(parser_var):

    # Workaround to not parse the `seg mapl3` part of the MIRACL command
    sys.argv = sys.argv[2:]

    # Create an instance of the parser
    # parser = Mapl3Parser()
    parser = parser_var

    # Parse the command-line arguments
    args = vars(parser.parser.parse_args())

    #############################################
    # ASSIGN CLI INPUT ARGS TO PYDANTIC OBJECTS #
    #############################################

    ##################
    # GENERATE PATCH #
    ##################

    generate_patch_input_folder = obj_generate_patch.input
    generate_patch_input_folder.input_dirpath = args[
        generate_patch_input_folder.cli_l_flag
    ]

    mapl3_results_folder = obj_generate_patch.output
    mapl3_results_folder.dirpath = (
        Path(args[mapl3_results_folder.cli_l_flag]) / "mapl3"
    )  # Input of "output_folder" flag

    mapl3_results_folder_seg = mapl3_results_folder.dirpath / "seg"

    generate_patch_cpu_load = obj_generate_patch.cpu_load
    generate_patch_cpu_load.content = args[generate_patch_cpu_load.cli_l_flag]

    generate_patch_patch_size = obj_generate_patch.patch_size
    generate_patch_patch_size.content = args[generate_patch_patch_size.cli_l_flag]

    generate_patch_gamma = obj_generate_patch.gamma
    generate_patch_gamma.content = args[generate_patch_gamma.cli_l_flag]

    generate_patch_output_folder = obj_subfolders.generated_patches_output
    generate_patch_output_folder.dirpath = (
        mapl3_results_folder_seg / "mapl3_generated_patches"
    )
    UtilfnsPaths.ensure_folder_exists(generate_patch_output_folder.dirpath)

    ###########################################################################

    #######################
    # PREPROCESS PARALLEL #
    #######################

    preprocess_parallel_output_folder = obj_subfolders.preprocessed_patches_output
    preprocess_parallel_output_folder.dirpath = (
        mapl3_results_folder_seg / "mapl3_preprocessed_patches"
    )
    UtilfnsPaths.ensure_folder_exists(preprocess_parallel_output_folder.dirpath)

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

    inference_output_folder = obj_subfolders.inference_output
    inference_output_folder.dirpath = mapl3_results_folder_seg / "mapl3_inference"
    UtilfnsPaths.ensure_folder_exists(inference_output_folder.dirpath)

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

    ###################
    # SKELETONIZATION #
    ###################

    skeletonization_remove_small_obj_thr = obj_skeletonization.remove_small_obj_thr
    skeletonization_remove_small_obj_thr.content = args[
        skeletonization_remove_small_obj_thr.cli_l_flag
    ]

    skeletonization_output_folder = obj_subfolders.skeletonization_output
    skeletonization_output_folder.dirpath = (
        mapl3_results_folder_seg / "mapl3_skeletonization"
    )
    UtilfnsPaths.ensure_folder_exists(skeletonization_output_folder.dirpath)

    skeletonization_cpu_load = obj_skeletonization.cpu_load
    skeletonization_cpu_load.content = args[skeletonization_cpu_load.cli_l_flag]

    skeletonization_dilate_distance_transform = (
        obj_skeletonization.dilate_distance_transform
    )
    skeletonization_dilate_distance_transform.content = args[
        skeletonization_dilate_distance_transform.cli_l_flag
    ]

    skeletonization_eccentricity_thr = obj_skeletonization.eccentricity_thr
    skeletonization_eccentricity_thr.content = args[
        skeletonization_eccentricity_thr.cli_l_flag
    ]

    skeletonization_orientation_thr = obj_skeletonization.orientation_thr
    skeletonization_orientation_thr.content = args[
        skeletonization_orientation_thr.cli_l_flag
    ]

    ###########################################################################

    ##################
    # PATCH STACKING #
    ##################

    patch_stacking_output_folder = obj_subfolders.patch_stacking_output
    patch_stacking_output_folder.dirpath = (
        mapl3_results_folder_seg / "mapl3_patch_stacking"
    )
    UtilfnsPaths.ensure_folder_exists(patch_stacking_output_folder.dirpath)

    patch_stacking_cpu_load = obj_patch_stacking.cpu_load
    patch_stacking_cpu_load.content = args[patch_stacking_cpu_load.cli_l_flag]

    patch_stacking_keep_image_type = obj_patch_stacking.keep_image_type
    patch_stacking_keep_image_type.content = args[
        patch_stacking_keep_image_type.cli_l_flag
    ]

    ###########################################################################

    #####################
    # METHOD INVOCATION #
    #####################

    patch_generator = MAPL3GeneratePatch()
    parallel_preprocessor = MAPL3PreprocessingParallel()
    inference = MAPL3Inference()
    skeletonization = MAPL3Skeletonization()
    patch_stacking = MAPL3PatchStacking()

    patch_generator.generate_patch(
        generate_patch_input_folder,
        generate_patch_output_folder,
        generate_patch_cpu_load,
        generate_patch_patch_size,
        generate_patch_gamma,
    )

    parallel_preprocessor.preprocess(
        generate_patch_output_folder,
        preprocess_parallel_output_folder,
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
        preprocess_parallel_output_folder,
        generate_patch_output_folder,
        inference_output_folder,
        inference_config,
        inference_model_path,
        inference_tissue_percentage_threshold,
        inference_gpu_index,
        inference_binarization_threshold,
        inference_save_prob_map,
    )

    skeletonization.run_skeletonization(
        inference_output_folder,
        generate_patch_output_folder,
        skeletonization_output_folder,
        skeletonization_remove_small_obj_thr,
        skeletonization_cpu_load,
        skeletonization_dilate_distance_transform,
        skeletonization_eccentricity_thr,
        skeletonization_orientation_thr,
    )

    patch_stacking.stack_patches(
        patch_stacking_output_folder,
        generate_patch_input_folder,
        skeletonization_output_folder,
        patch_stacking_cpu_load,
        patch_stacking_keep_image_type,
    )


###############################################################################

if __name__ == "__main__":
    main(Mapl3Parser())
