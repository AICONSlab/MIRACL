from miracl.system.registry.mapl3_connectors_template import (
    mapl3_workflow_connectors_dict,
)
from miracl.system.registry.workflow_skips_template import workflow_skips_dict
from miracl.system.registry.conv_template import conv_tiff_nii_dict
from miracl.system.registry.reg_template import reg_clar_allen_dict
from miracl.system.registry.mapl3_preprocessing_parallel_template import (
    mapl3_preprocessing_parallel_dict,
)
from miracl.system.registry.mapl3_generate_patch_template import (
    mapl3_generate_patch_dict,
)
from miracl.system.registry.mapl3_inference_template import (
    mapl3_inference_dict,
)
from miracl.system.registry.mapl3_patch_stacking_template import (
    mapl3_patch_stacking_dict,
)
from miracl.system.registry.mapl3_raw_data_normalization_template import (
    mapl3_raw_data_normalization_dict,
)
from miracl.system.registry.mapl3_skeletonization_template import (
    mapl3_skeletonization_dict,
)
from miracl.system.registry.mapl3_voxelization_template import (
    mapl3_voxelization_dict,
)
from miracl.system.registry.mapl3_warping_template import warp_clar_allen_dict
from miracl.system.registry.mapl3_feat_extract_template import mapl3_feat_extract_dict

__all__ = [
    "mapl3_workflow_connectors_dict",
    "conv_tiff_nii_dict",
    "reg_clar_allen_dict",
    "mapl3_preprocessing_parallel_dict",
    "mapl3_generate_patch_dict",
    "mapl3_inference_dict",
    "mapl3_patch_stacking_dict",
    "mapl3_raw_data_normalization_dict",
    "mapl3_skeletonization_dict",
    "mapl3_voxelization_dict",
    "warp_clar_allen_dict",
    "mapl3_feat_extract_dict",
    "workflow_skips_dict",
]
