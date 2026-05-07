"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)


This is where modules are registered. Add a module here to reference it in the config
files.

Note:
  This needs some refactoring. I want to add a third item to the tuple that can be used
  as the parser group header. Currently, the first argument is used for that but it's
  also used to match the module in the workflow config. Horrible design! These should
  be independant of each other so they can be changed independantly from each other.
"""

from enum import Enum


class CliGroup(Enum):
    STATS_TFCE = (
        "TFCE",
        "Args for TFCE stats method",
    )
    REG_CLAR_ALLEN = (
        "reg_clar_allen",
        "Args for CLARITY Allen image registration",
    )
    CONV_TIFF_NII = (
        "conv_tiff_nii",
        "Args for image conversion from tiff to nifti",
    )
    MAPL3_GENERATE_PATCH = (
        "mapl3_gen_patch",
        "Args for generating patches from Z-stack .tif files",
    )
    MAPL3_PREPROCESSING_PARALLEL = (
        "mapl3_preproc_para",
        "Args for preprocessing RAW LSFM data in parallel",
    )
    MAPL3_INFERENCE = (
        "mapl3_inference",
        "Args for inference",
    )
    MAPL3_PATCH_STACKING = (
        "patch stacking",
        "Args for patch stacking",
    )
    MAPL3_RAW_DATA_NORMALIZATION = (
        "RAW data normalization",
        "Args for RAW data normalization",
    )
    MAPL3_SKELETONIZATION = (
        "skeletonization",
        "Args for skeletonization",
    )
    MAPL3_VOXELIZATION = (
        "voxelization",
        "Args for voxelization",
    )
    MAPL3_WARP_CLAR_ALLEN = (
        "warping",
        "Args for CLARITY Allen warping",
    )
    MAPL3_FEAT_EXTRACT = (
        "feature extraction",
        "Args for feature extraction",
    )
    MAPL3_PLOT_WARPED_DATA = (
        "plot warped data",
        "Args for heatmap plot",
    )
    MAPL3_SKIPS = (
        "workflow skips",
        "set to True to skip a particular workflow - all relevant args still need to be provided!",
    )
    REQUIRED = (
        "required",
        "required arguments",
    )

    @property
    def description(self):
        return self.value[1]

    @property
    def label(self):
        return self.value[0]
