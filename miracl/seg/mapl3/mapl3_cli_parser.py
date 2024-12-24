from argparse import (
    ArgumentError,
    ArgumentParser,
    RawDescriptionHelpFormatter,
    _HelpAction,
    SUPPRESS,
    Namespace,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import create_parser_arguments
from miracl.system.objs.objs_seg.objs_mapl3.objs_mapl3_generate_patch import (
    GeneratePatch as seg_mapl3_genpatch,
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


class Mapl3Parser:
    """
    Command-line argument parser for MAPL3.

    :param input: A required string argument that specifies the input file path.
    :param output: A required string argument that specifies the output file path.
    :param cpu_load: An optional float argument that specifies the fraction of CPU's used for parallelization.
    :param patch_size: An optional flag that of type int.
    :param gamma: An optional flag of type float for gamma correction.

    :returns: The parsed arguments.
    """

    def __init__(self) -> None:
        self.parser = self.parsefn()

    def parsefn(self) -> ArgumentParser:
        # Define custom parser
        parser = ArgumentParser(
            prog="miracl seg mapl3",
            add_help=True,
        )

        groups_dict = {
            "generate_patch": {
                "title": "generate patch arguments",
                "description": "arguments passed to generate patch fn",
                "args": [
                    seg_mapl3_genpatch.input,
                    seg_mapl3_genpatch.output,
                    seg_mapl3_genpatch.cpu_load,
                    seg_mapl3_genpatch.patch_size,
                    seg_mapl3_genpatch.gamma,
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

        # Create parser args and return group dicts
        create_parser_arguments(parser, groups_dict, "module")

        return parser


if __name__ == "__main__":
    args_parser = Mapl3Parser()
    args = args_parser.parser.parse_args()
