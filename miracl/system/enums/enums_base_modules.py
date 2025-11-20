from enum import Enum


class CliGroup(Enum):
    REG_CLAR_ALLEN = (
        "registration",
        "Args for CLARITY Allen image registration",
    )
    CONV_TIFF_NII = (
        "conversion",
        "Args for image conversion from tiff to nifti",
    )
    MAPL3_GENERATE_PATCH = (
        "generate patch",
        "Args for generating patches from Z-stack .tif files",
    )
    MAPL3_PREPROCESSING_PARALLEL = (
        "preprocessing parallel",
        "Args for preprocessing RAW LSFM data in parallel",
    )
    MAPL3_INFERENCE = (
        "inference",
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


# group_name = obj.cli_group  # instance of CliGroup
# parser.add_argument_group(title=group_name.label, description=group_name.description)
