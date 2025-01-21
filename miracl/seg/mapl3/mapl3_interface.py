"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca) for
Ahmadreza Attapour's (a.attarpour@mail.utoronto.ca) MAPL3 implementation into
AICONs lab's MIRACL.

This code is an interface for the the MAPL3 segmentation module.
"""

from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Dict, Any

# Import MIRACL BaseModel and utility fns
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
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
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


@dataclass
class GeneratePatchParams:
    """
    Parameters for generating patches.

    :param input_folder: Input folder containing RAW TIFF files
    :type input_folder: MiraclObj
    :param output_folder: Output folder for generated patches
    :type output_folder: MiraclObj
    :param cpu_load: CPU load for parallelization
    :type cpu_load: MiraclObj
    :param patch_size: Size of patches to generate
    :type patch_size: MiraclObj
    :param gamma: Gamma for gamma correction algo
    :type gamma: MiraclObj
    """

    input_folder: MiraclObj
    output_folder: MiraclObj
    cpu_load: MiraclObj
    patch_size: MiraclObj
    gamma: MiraclObj


class GeneratePatch(ABC):
    @abstractmethod
    def generate_patch(
        self,
        params: GeneratePatchParams,
    ) -> None:
        pass


@dataclass
class PreprocessingParallelParams:
    """
    Parameters for parallel preprocessing.

    :param generate_patch_output_folder: Folder with generated patches
    :type generate_patch_output_folder: MiraclObj
    :param output_folder: Output folder for preprocessing results
    :type output_folder: MiraclObj
    :param cpu_load: CPU load for parallelization
    :type cpu_load: MiraclObj
    :param cl_percentage: Percentage used in percentile filter
    :type cl_percentage: MiraclObj
    :param cl_lsm_footprint: Estimating LSM stripes
    :type cl_lsm_footprint: MiraclObj
    :param cl_back_footprint: Estimating backgroud default
    :type cl_back_footprint: MiraclObj
    :param cl_back_downsample: Estimating background default
    :type cl_back_downsample: MiraclObj
    :param cl_lsm_vs_back_weight: lsm signal vs background weight
    :type cl_lsm_vs_back_weight: MiraclObj
    :param deconv_bin_thr: Binary threshold for high intensity voxels for pseudo deconvolution
    :type deconv_bin_thr: MiraclObj
    :param deconv_sigma: Sigma value for pseudo deconvolution
    :type deconv_sigma: MiraclObj
    :param save_intermediate_results: Flag to save intermediate results
    :type save_intermediate_results: MiraclObj
    """

    generate_patch_output_folder: MiraclObj
    output_folder: MiraclObj
    cpu_load: MiraclObj
    cl_percentage: MiraclObj
    cl_lsm_footprint: MiraclObj
    cl_back_footprint: MiraclObj
    cl_back_downsample: MiraclObj
    cl_lsm_vs_back_weight: MiraclObj
    deconv_bin_thr: MiraclObj
    deconv_sigma: MiraclObj
    save_intermediate_results: MiraclObj


class PreprocessingParallel(ABC):
    @abstractmethod
    def preprocess(
        self,
        params: PreprocessingParallelParams,
    ) -> None:
        pass


@dataclass
class InferenceParams:
    """
    Parameters for inference.

    :param preprocess_parallel_output_folder: Folder with parallel preprocessing results
    :type preprocess_parallel_output_folder: MiraclObj
    :param generate_patch_output_folder: Folder with patch generation results
    :type generate_patch_output_folder: MiraclObj
    :param output_folder: Output folder for inference results
    :type output_folder: MiraclObj
    :param config: Path to config file used during training to define model
    :type config: MiraclObj
    :param model_path: Path to the trained model
    :type model_path: MiraclObj
    :param tissue_percentage_threshold: Whether to use json file to filter empty patches
    :type tissue_percentage_threshold: MiraclObj
    :param gpu_index: GPU index to use for inference
    :type gpu_index: MiraclObj
    :param binarization_threshold: Threshold for model probability map binarization
    :type binarization_threshold: MiraclObj
    :param save_prob_map: Flag to save probability map
    :type save_prob_map: MiraclObj
    """

    preprocess_parallel_output_folder: MiraclObj
    generate_patch_output_folder: MiraclObj
    output_folder: MiraclObj
    config: MiraclObj
    model_path: MiraclObj
    tissue_percentage_threshold: MiraclObj
    gpu_index: MiraclObj
    binarization_threshold: MiraclObj
    save_prob_map: MiraclObj


class Inference(ABC):
    @abstractmethod
    def run_inference(
        self,
        params: InferenceParams,
    ) -> None:
        pass


@dataclass
class SkeletonizationParams:
    """
    Parameters for skeletonization.

    :param inference_output_folder: Folder with inference results
    :type inference_output_folder: MiraclObj
    :param generate_patch_output_folder: Folder with patch generation results
    :type generate_patch_output_folder: MiraclObj
    :param output: Output folder for skeletonization results
    :type output: MiraclObj
    :param remove_small_obj_thr: Threshold for removing small objects
    :type remove_small_obj_thr: MiraclObj
    :param cpu_load: CPU load for parallelization
    :type cpu_load: MiraclObj
    :param dilate_distance_transform: Whether to dilate distance transform
    :type dilate_distance_transform: MiraclObj
    :param eccentricity_thr: Threshold for removing small objects based on eccentricity
    :type eccentricity_thr: MiraclObj
    :param orientation_thr: Threshold for removing small objects based on orientation
    :type orientation_thr: MiraclObj
    """

    inference_output_folder: MiraclObj
    generate_patch_output_folder: MiraclObj
    output: MiraclObj
    remove_small_obj_thr: MiraclObj
    cpu_load: MiraclObj
    dilate_distance_transform: MiraclObj
    eccentricity_thr: MiraclObj
    orientation_thr: MiraclObj


class Skeletonization(ABC):
    @abstractmethod
    def run_skeletonization(
        self,
        params: SkeletonizationParams,
    ) -> None:
        pass


@dataclass
class PatchStackingParams:
    """
    Parameters for patch stacking.

    :param generate_patch_input_folder: Folder with generated patches
    :type generate_patch_input_folder: MiraclObj
    :param skeletonization_output_folder: Folder with skeletonization results
    :type skeletonization_output_folder: MiraclObj
    :param output: Output folder for stacked patches
    :type output: MiraclObj
    :param cpu_load: CPU load for parallelization
    :type cpu_load: MiraclObj
    :param keep_image_type: Flag to keep image type same as patches type
    :type keep_image_type: MiraclObj
    """

    generate_patch_input_folder: MiraclObj
    skeletonization_output_folder: MiraclObj
    output: MiraclObj
    cpu_load: MiraclObj
    keep_image_type: MiraclObj


class PatchStacking(ABC):
    @abstractmethod
    def stack_patches(self, params: PatchStackingParams):
        pass


###############################################################################

####################
# CONCRETE CLASSES #
####################


class MAPL3GeneratePatch(GeneratePatch):

    def generate_patch(
        self,
        params: GeneratePatchParams,
    ) -> None:
        """
        Generate patches.

        :param params: Parameters for generating patches
        :type params: GeneratePatchParams
        """

        logger.debug("###########################")
        logger.debug("GENERATE PATCH IN INTERFACE")
        logger.debug("###########################")
        logger.debug(f"generate_patch_input_folder: {params.input_folder.dirpath}")
        logger.debug(f"generate_patch_output_folder: {params.output_folder.dirpath}")
        logger.debug(f"generate_patch_cpu_load: {params.cpu_load.content}")
        logger.debug(f"generate_patch_patch_size: {params.patch_size.content}")
        logger.debug(f"generate_patch_gamma: {params.gamma.content}")

        if production or generate_patch_enabled:
            mapl3_generate_patch.main(
                params.input_folder,
                params.output_folder,
                params.cpu_load,
                params.patch_size,
                params.gamma,
            )


class MAPL3PreprocessingParallel(PreprocessingParallel):

    def preprocess(
        self,
        params: PreprocessingParallelParams,
    ) -> None:
        """
        Run parallel preprocessing.

        :param params: Parameters for parallel preprocessing
        :type params: PreprocessingParallelParams
        """

        logger.debug("################################")
        logger.debug("PREPROCESS PARALLEL IN INTERFACE")
        logger.debug("################################")
        logger.debug(
            f"Input from generate patch -> output folder: {params.output_folder.dirpath}"
        )
        logger.debug(
            f"preprocess_parallel_output_folder: {params.output_folder.dirpath}"
        )
        logger.debug(f"preprocess_parallel_cpu_load: {params.cpu_load.content}")
        logger.debug(
            f"preprocess_parallel_cl_percentage: {params.cl_percentage.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_lsm_footprint: {params.cl_lsm_footprint.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_back_footprint: {params.cl_back_footprint.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_back_downsample: {params.cl_back_downsample.content}"
        )
        logger.debug(
            f"preprocess_parallel_cl_lsm_vs_back_weight: {params.cl_lsm_vs_back_weight.content}"
        )
        logger.debug(
            f"preprocess_parallel_deconv_bin_thr: {params.deconv_bin_thr.content}"
        )
        logger.debug(f"preprocess_parallel_deconv_sigma: {params.deconv_sigma.content}")
        logger.debug(
            f"preprocess_parallel_save_intermediate_results: {params.save_intermediate_results.content}"
        )

        if production or preprocess_parallel_enabled:
            mapl3_preprocessing_parallel.main(
                params.generate_patch_output_folder,
                params.output_folder,
                params.cpu_load,
                params.cl_percentage,
                params.cl_lsm_footprint,
                params.cl_back_footprint,
                params.cl_back_downsample,
                params.cl_lsm_vs_back_weight,
                params.deconv_bin_thr,
                params.deconv_sigma,
                params.save_intermediate_results,
            )


class MAPL3Inference(Inference):

    def run_inference(
        self,
        params: InferenceParams,
    ) -> None:
        """
        Run inference.

        :param params: Parameters for inference
        :type params: InferenceParams
        """

        logger.debug("######################")
        logger.debug("INFERENCE IN INTERFACE")
        logger.debug("######################")
        logger.debug(
            f"Processed generated patches output: {params.preprocess_parallel_output_folder.dirpath}"
        )
        logger.debug(
            f"Generated patches folder i.e. json file location: {params.generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"inference_config: {params.config.filepath}")
        logger.debug(f"inference_model_path: {params.model_path.filepath}")
        logger.debug(f"inference_output_folder: {params.output_folder.dirpath}")
        logger.debug(
            f"inference_tissue_percentage_threshold: {params.tissue_percentage_threshold.content}"
        )
        logger.debug(f"inference_gpu_index: {params.gpu_index.content}")
        logger.debug(
            f"inference_binarization_threshold: {params.binarization_threshold.content}"
        )
        logger.debug(f"inference_save_prob_map: {params.save_prob_map.content}")

        if production or inference_enabled:
            mapl3_inference.main(
                params.preprocess_parallel_output_folder,
                params.generate_patch_output_folder,
                params.output_folder,
                params.config,
                params.model_path,
                params.tissue_percentage_threshold,
                params.gpu_index,
                params.binarization_threshold,
                params.save_prob_map,
            )


class MAPL3Skeletonization(Skeletonization):

    def run_skeletonization(
        self,
        params: SkeletonizationParams,
    ) -> None:
        """
        Run skeletonization.

        :param params: Parameters for skeletonization
        :type params: SkeletonizationParams
        """

        logger.debug("############################")
        logger.debug("SKELETONIZATION IN INTERFACE")
        logger.debug("############################")
        logger.debug(
            f"inference_output_folder: {params.inference_output_folder.dirpath}"
        )
        logger.debug(
            f"json file folder path: {params.generate_patch_output_folder.dirpath}"
        )
        logger.debug(f"skeletonization_output_folder: {params.output.dirpath}")
        logger.debug(
            f"skeletonization_remove_small_obj_thr: {params.remove_small_obj_thr.content}"
        )
        logger.debug(f"skeletonization_cpu_load: {params.cpu_load.content}")
        logger.debug(
            f"skeletonization_dilate_distance_transform: {params.dilate_distance_transform.content}"
        )
        logger.debug(
            f"skeletonization_eccentricity_thr: {params.eccentricity_thr.content}"
        )
        logger.debug(
            f"skeletonization_orientation_thr: {params.orientation_thr.content}"
        )

        if production or skeletonization_enabled:
            mapl3_skeletonization.main(
                params.inference_output_folder,
                params.generate_patch_output_folder,
                params.output,
                params.remove_small_obj_thr,
                params.cpu_load,
                params.dilate_distance_transform,
                params.eccentricity_thr,
                params.orientation_thr,
            )


class MAPL3PatchStacking(PatchStacking):

    def stack_patches(
        self,
        params: PatchStackingParams,
    ) -> None:
        """
        Run patch stacking.

        :param params: Parameters for patch stacking
        :type params: PatchStackingParams
        """

        logger.debug("###########################")
        logger.debug("PATCH STACKING IN INTERFACE")
        logger.debug("###########################")
        logger.debug(
            f"generate_patch_input_folder: {params.generate_patch_input_folder.dirpath}"
        )
        logger.debug(
            f"skeletonization_output_folder: {params.skeletonization_output_folder.dirpath}"
        )
        logger.debug(f"patch_stacking_output_folder: {params.output.dirpath}")
        logger.debug(f"patch_stacking_cpu_load: {params.cpu_load.content}")
        logger.debug(
            f"patch_stacking_keep_image_type: {params.keep_image_type.content}"
        )

        if production or patch_stacking_enabled:
            mapl3_patch_stacking.main(
                params.generate_patch_input_folder,
                params.skeletonization_output_folder,
                params.output,
                params.cpu_load,
                params.keep_image_type,
            )


###############################################################################

########
# MAIN #
########


# def main(parser_var, objs):
def main(objs: Dict[str, Any]) -> Dict[str, MiraclObj]:
    """
    Main function to run the MAPL3 module/pipeline.

    :param objs: Dictionary containing MAPL3 objects
    :type objs: Dict[str, Any]
    :return: Dictionary of MAPL3 subfolder objects
    :rtype: Dict[str, MiraclObj]
    """

    ########################
    # CREATE MAPL3 FOLDERS #
    ########################

    # FIX: Do I need another check here with the utils fn for filepaths?

    mapl3_interface_folders.mapl3_results_base_folder.dirpath = (
        objs["seg_genpatch"].output.dirpath / "mapl3"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.mapl3_results_base_folder.dirpath
    )

    # Create segmentation subfolder under base folder
    mapl3_interface_folders.mapl3_results_seg_folder.dirpath = (
        mapl3_interface_folders.mapl3_results_base_folder.dirpath / "seg"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
    )

    # Create folder with generated patches
    mapl3_interface_folders.generated_patches_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_generated_patches"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.generated_patches_output.dirpath
    )

    # Create folder for preprocess parallel
    mapl3_interface_folders.preprocessed_patches_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_preprocessed_patches"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.preprocessed_patches_output.dirpath
    )

    # Create folder for inference
    mapl3_interface_folders.inference_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath / "mapl3_inference"
    )
    UtilfnsPaths.ensure_folder_exists(mapl3_interface_folders.inference_output.dirpath)

    # Create folder for skeletonization
    mapl3_interface_folders.skeletonization_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_skeletonization"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.skeletonization_output.dirpath
    )

    # Create folder for patch stacking
    mapl3_interface_folders.patch_stacking_output.dirpath = (
        mapl3_interface_folders.mapl3_results_seg_folder.dirpath
        / "mapl3_patch_stacking"
    )
    UtilfnsPaths.ensure_folder_exists(
        mapl3_interface_folders.patch_stacking_output.dirpath
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
        GeneratePatchParams(
            input_folder=objs["seg_genpatch"].input,
            output_folder=mapl3_interface_folders.generated_patches_output,
            cpu_load=objs["seg_genpatch"].cpu_load,
            patch_size=objs["seg_genpatch"].patch_size,
            gamma=objs["seg_genpatch"].gamma,
        )
    )

    parallel_preprocessor.preprocess(
        PreprocessingParallelParams(
            generate_patch_output_folder=mapl3_interface_folders.generated_patches_output,
            output_folder=mapl3_interface_folders.preprocessed_patches_output,
            cpu_load=objs["seg_preprocessing_parallel"].cpu_load,
            cl_percentage=objs["seg_preprocessing_parallel"].cl_percentage,
            cl_lsm_footprint=objs["seg_preprocessing_parallel"].cl_lsm_footprint,
            cl_back_footprint=objs["seg_preprocessing_parallel"].cl_back_footprint,
            cl_back_downsample=objs["seg_preprocessing_parallel"].cl_back_downsample,
            cl_lsm_vs_back_weight=objs["seg_preprocessing_parallel"].lsm_vs_back_weight,
            deconv_bin_thr=objs["seg_preprocessing_parallel"].deconv_bin_thr,
            deconv_sigma=objs["seg_preprocessing_parallel"].deconv_sigma,
            save_intermediate_results=objs[
                "seg_preprocessing_parallel"
            ].save_intermediate_results,
        )
    )

    inference.run_inference(
        InferenceParams(
            preprocess_parallel_output_folder=mapl3_interface_folders.preprocessed_patches_output,
            generate_patch_output_folder=mapl3_interface_folders.generated_patches_output,
            output_folder=mapl3_interface_folders.inference_output,
            config=objs["seg_inference"].config,
            model_path=objs["seg_inference"].model_path,
            tissue_percentage_threshold=objs[
                "seg_inference"
            ].tissue_percentage_threshold,
            gpu_index=objs["seg_inference"].gpu_index,
            binarization_threshold=objs["seg_inference"].binarization_threshold,
            save_prob_map=objs["seg_inference"].save_prob_map,
        )
    )

    skeletonization.run_skeletonization(
        SkeletonizationParams(
            inference_output_folder=mapl3_interface_folders.inference_output,
            generate_patch_output_folder=mapl3_interface_folders.generated_patches_output,
            output=mapl3_interface_folders.skeletonization_output,
            remove_small_obj_thr=objs["seg_skeletonization"].remove_small_obj_thr,
            cpu_load=objs["seg_skeletonization"].cpu_load,
            dilate_distance_transform=objs[
                "seg_skeletonization"
            ].dilate_distance_transform,
            eccentricity_thr=objs["seg_skeletonization"].eccentricity_thr,
            orientation_thr=objs["seg_skeletonization"].orientation_thr,
        )
    )

    patch_stacking.stack_patches(
        PatchStackingParams(
            generate_patch_input_folder=mapl3_interface_folders.generated_patches_output,
            skeletonization_output_folder=mapl3_interface_folders.skeletonization_output,
            output=mapl3_interface_folders.patch_stacking_output,
            cpu_load=objs["seg_patch_stacking"].cpu_load,
            keep_image_type=objs["seg_patch_stacking"].keep_image_type,
        )
    )

    mapl3_subfolders_objs_dict = {
        "mapl3_results_base_folder": mapl3_interface_folders.mapl3_results_base_folder,
        "mapl3_results_seg_folder": mapl3_interface_folders.mapl3_results_seg_folder,
        "generated_patches_output": mapl3_interface_folders.generated_patches_output,
        "preprocessed_patches_output": mapl3_interface_folders.preprocessed_patches_output,
        "inference_output": mapl3_interface_folders.inference_output,
        "skeletonization_output": mapl3_interface_folders.skeletonization_output,
        "patch_stacking_output": mapl3_interface_folders.patch_stacking_output,
    }

    # For use in workflow
    return mapl3_subfolders_objs_dict


###############################################################################

if __name__ == "__main__":
    main(seg_mapl3_objs)
