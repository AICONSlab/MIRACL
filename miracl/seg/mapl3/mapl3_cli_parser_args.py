from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_generate_patch import (
    GeneratePatch as seg_genpatch,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_preprocessing_parallel import (
    PreprocessingParallel as seg_preprocessing_parallel,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_inference import (
    Inference as seg_inference,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_skeletonization import (
    Skeletonization as seg_skeletonization,
)
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_patch_stacking import (
    PatchStacking as seg_patch_stacking,
)

mapl3_groups_dict = {
    "generate_patch": {
        "title": "generate patch arguments",
        "description": "arguments passed to generate patch fn",
        "args": [
            seg_genpatch.input,
            seg_genpatch.output,
            seg_genpatch.cpu_load,
            seg_genpatch.patch_size,
            seg_genpatch.gamma,
        ],
    },
    "preprocessing_parallel": {
        "title": "parallel preprocessing",
        "description": "arguments passed to parallel preprocessing fn",
        "args": [
            seg_preprocessing_parallel.cpu_load,
            seg_preprocessing_parallel.cl_percentage,
            seg_preprocessing_parallel.cl_lsm_footprint,
            seg_preprocessing_parallel.cl_back_footprint,
            seg_preprocessing_parallel.cl_back_downsample,
            seg_preprocessing_parallel.lsm_vs_back_weight,
            seg_preprocessing_parallel.deconv_bin_thr,
            seg_preprocessing_parallel.deconv_sigma,
            seg_preprocessing_parallel.save_intermediate_results,
        ],
    },
    "inference": {
        "title": "inference",
        "description": "arguments passed to inference fn",
        "args": [
            seg_inference.config,
            seg_inference.model_path,
            seg_inference.tissue_percentage_threshold,
            seg_inference.gpu_index,
            seg_inference.binarization_threshold,
            seg_inference.save_prob_map,
        ],
    },
    "skeletonization": {
        "title": "skeletonization",
        "description": "arguments passed to skeletonization fn",
        "args": [
            seg_skeletonization.remove_small_obj_thr,
            seg_skeletonization.cpu_load,
            seg_skeletonization.dilate_distance_transform,
            seg_skeletonization.eccentricity_thr,
            seg_skeletonization.orientation_thr,
        ],
    },
    "patch_stacking": {
        "title": "patch stacking",
        "description": "arguments passed to patch stacking fn",
        "args": [
            seg_patch_stacking.cpu_load,
            seg_patch_stacking.keep_image_type,
        ],
    },
}

mapl3_object_dict = {
    "seg_genpatch": seg_genpatch,
    "seg_preprocessing_parallel": seg_preprocessing_parallel,
    "seg_inference": seg_inference,
    "seg_skeletonization": seg_skeletonization,
    "seg_patch_stacking": seg_patch_stacking,
}
