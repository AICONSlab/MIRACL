import sys
from abc import abstractmethod, ABC
from pathlib import Path

# Import MIRACL BaseModel and utility fns
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.utilfns.utilfns_paths import UtilfnsPaths
from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger

# Import MAPL3 scripts
import miracl.seg.mapl3.mapl3_generate_patch as mapl3_generate_patch
import miracl.seg.mapl3.mapl3_preprocessing_parallel as mapl3_preprocessing_parallel
import miracl.seg.mapl3.mapl3_inference as mapl3_inference
import miracl.seg.mapl3.mapl3_skeletonization as mapl3_skeletonization
import miracl.seg.mapl3.mapl3_patch_stacking as mapl3_patch_stacking

# Import MAPL3 objects
from miracl.seg.mapl3.mapl3_cli_parser_args import object_dict as seg_mapl3_objs
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_interface_folder import (
    InterfaceSubfolders as mapl3_interface_folders,
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
            f"generate_patch_input_folder: {generate_patch_input_folder.dirpath}"
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
            f"generate_patch_input_folder: {generate_patch_input_folder.dirpath}"
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
    # It's important to note here that the interface has to be called
    # through MIRACL's cli parser because the submodule and module from the
    # miracl command will be removed with the below command
    # FIX: Could this be done in MIRACL's cli parser instead?
    sys.argv = sys.argv[2:]

    # Create an instance of the parser
    parser = parser_var

    # Parse the command-line arguments
    args = vars(parser.parser.parse_args())

    #############################################
    # ASSIGN CLI INPUT ARGS TO PYDANTIC OBJECTS #
    #############################################

    # Process the results of the parsed cli args
    # Processing here refers to assigning the results to their respective
    # objects/attribute
    processor = MiraclArgumentProcessor(parser)
    processor.process_miracl_objects(seg_mapl3_objs, args)

    ########################
    # CREATE MAPL3 FOLDERS #
    ########################

    # NOTE: Do I need another check here with the utils fn for filepaths?

    mapl3_interface_folders.mapl3_results_base_folder.dirpath = (
        seg_mapl3_objs["seg_genpatch"].output.dirpath / "mapl3"
    )

    # Create segmentation subfolder under base folder
    mapl3_interface_folders.mapl3_results_seg_folder.dirpath = (
        mapl3_interface_folders.mapl3_results_base_folder.dirpath / "seg"
    )

    # Create folder with generated patches
    mapl3_interface_folders.generated_patches_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_generated_patches"
    )

    # Create folder for preprocess parallel
    mapl3_interface_folders.preprocessed_patches_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_preprocessed_patches"
    )

    # Create folder for inference
    mapl3_interface_folders.inference_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath / "mapl3_inference"
    )

    # Create folder for skeletonization
    mapl3_interface_folders.skeletonization_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_skeletonization"
    )

    # Create folder for patch stacking
    mapl3_interface_folders.patch_stacking_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_patch_stacking"
    )

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
        seg_mapl3_objs["seg_genpatch"].input,
        mapl3_interface_folders.generated_patches_output,
        seg_mapl3_objs["seg_genpatch"].cpu_load,
        seg_mapl3_objs["seg_genpatch"].patch_size,
        seg_mapl3_objs["seg_genpatch"].gamma,
    )

    parallel_preprocessor.preprocess(
        mapl3_interface_folders.generated_patches_output,
        mapl3_interface_folders.preprocessed_patches_output,
        seg_mapl3_objs["seg_preprocessing_parallel"].cpu_load,
        seg_mapl3_objs["seg_preprocessing_parallel"].cl_percentage,
        seg_mapl3_objs["seg_preprocessing_parallel"].cl_lsm_footprint,
        seg_mapl3_objs["seg_preprocessing_parallel"].cl_back_footprint,
        seg_mapl3_objs["seg_preprocessing_parallel"].cl_back_downsample,
        seg_mapl3_objs["seg_preprocessing_parallel"].lsm_vs_back_weight,
        seg_mapl3_objs["seg_preprocessing_parallel"].deconv_bin_thr,
        seg_mapl3_objs["seg_preprocessing_parallel"].deconv_sigma,
        seg_mapl3_objs["seg_preprocessing_parallel"].save_intermediate_results,
    )

    inference.run_inference(
        mapl3_interface_folders.preprocessed_patches_output,
        mapl3_interface_folders.generated_patches_output,
        mapl3_interface_folders.inference_output,
        seg_mapl3_objs["seg_inference"].config,
        seg_mapl3_objs["seg_inference"].model_path,
        seg_mapl3_objs["seg_inference"].tissue_percentage_threshold,
        seg_mapl3_objs["seg_inference"].gpu_index,
        seg_mapl3_objs["seg_inference"].binarization_threshold,
        seg_mapl3_objs["seg_inference"].save_prob_map,
    )

    skeletonization.run_skeletonization(
        mapl3_interface_folders.inference_output,
        mapl3_interface_folders.generated_patches_output,
        mapl3_interface_folders.skeletonization_output,
        seg_mapl3_objs["seg_skeletonization"].remove_small_obj_thr,
        seg_mapl3_objs["seg_skeletonization"].cpu_load,
        seg_mapl3_objs["seg_skeletonization"].dilate_distance_transform,
        seg_mapl3_objs["seg_skeletonization"].eccentricity_thr,
        seg_mapl3_objs["seg_skeletonization"].orientation_thr,
    )

    patch_stacking.stack_patches(
        mapl3_interface_folders.patch_stacking_output,
        mapl3_interface_folders.generated_patches_output,
        mapl3_interface_folders.skeletonization_output,
        seg_mapl3_objs["seg_patch_stacking"].cpu_load,
        seg_mapl3_objs["seg_patch_stacking"].keep_image_type,
    )

    return {
        "generate_patch_input_folder": mapl3_interface_folders.generated_patches_output.dirpath
    }


###############################################################################

if __name__ == "__main__":
    main(Mapl3Parser())
