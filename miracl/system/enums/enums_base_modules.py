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
from typing import NamedTuple


class CliGroupValue(NamedTuple):
    ref: str
    label: str
    description: str


class CliGroup(Enum):
    STATS_TFCE = CliGroupValue(
        ref="TFCE",
        label="TFCE",
        description="Args related to TFCE stats method",
    )
    REG_CLAR_ALLEN = CliGroupValue(
        ref="reg_clar_allen",
        label="CLARITY Allen/Waxholm registration",
        description="Args related to CLARITY Allen image registration",
    )
    CONV_TIFF_NII = CliGroupValue(
        ref="conv_tiff_nii",
        label="Tiff to Nifti conversion",
        description="Args related to image conversion from tiff to nifti",
    )
    CONV_REG_WORKFLOW_CONNECTORS = CliGroupValue(
        ref="conv_reg_workflow_connectors",
        label="Required args",
        description="Arguments required by the Conversion/Registration workflow",
    )
    MAPL3_WORKFLOW_CONNECTORS = CliGroupValue(
        ref="mapl3_workflow_connectors",
        label="Required args",
        description="Arguments required by the MAPL3 workflow",
    )
    MAPL3_GENERATE_PATCH = CliGroupValue(
        ref="mapl3_gen_patch",
        label="Patch generation",
        description="Args related to generating patches from Z-stack .tif files",
    )
    MAPL3_PREPROCESSING_PARALLEL = CliGroupValue(
        ref="mapl3_preproc_para",
        label="Preprocessing RAW LSFM data",
        description="Args related to preprocessing RAW LSFM data in parallel",
    )
    MAPL3_INFERENCE = CliGroupValue(
        ref="mapl3_inference",
        label="Inference",
        description="Args related to inference",
    )
    MAPL3_PATCH_STACKING = CliGroupValue(
        ref="patch stacking",
        label="Patch stacking",
        description="Args related to patch stacking",
    )
    MAPL3_RAW_DATA_NORMALIZATION = CliGroupValue(
        ref="RAW data normalization",
        label="RAW data normalization",
        description="Args related to RAW data normalization",
    )
    MAPL3_SKELETONIZATION = CliGroupValue(
        ref="skeletonization",
        label="Skeletonization",
        description="Args related to skeletonization",
    )
    MAPL3_VOXELIZATION = CliGroupValue(
        ref="voxelization",
        label="Voxelization",
        description="Args related to voxelization",
    )
    MAPL3_WARP_CLAR_ALLEN = CliGroupValue(
        ref="warping",
        label="Warping",
        description="Args related to CLARITY Allen warping",
    )
    MAPL3_FEAT_EXTRACT = CliGroupValue(
        ref="feature extraction",
        label="Feature extraction",
        description="Args related to feature extraction",
    )
    MAPL3_PLOT_WARPED_DATA = CliGroupValue(
        ref="plot warped data",
        label="Plot warped data",
        description="Args related to heatmap plot",
    )
    MAPL3_SKIPS = CliGroupValue(
        ref="workflow skips",
        label="Workflow skips",
        description="set to True to skip a particular workflow - all relevant args still need to be provided!",
    )

    @property
    def ref(self) -> str:
        return self.value.ref

    @property
    def label(self):
        return self.value.label

    @property
    def description(self):
        return self.value.description
