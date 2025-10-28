from miracl.system.datamodels.datamodel_miracl_objs import (
    MiraclObj,
    ArgumentType,
)
from miracl.system.enums.enums_base_modules import CliGroup


class WorkflowSkips:
    workflow_conversion_skip: MiraclObj = MiraclObj(
        name="workflow_conversion_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sc",
        cli_l_flag="skip_conversion",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_cs",
                "cli_l_flag": "skip_conversion",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip conversion module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_registration_skip: MiraclObj = MiraclObj(
        name="workflow_registration_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sr",
        cli_l_flag="skip_registration",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_rs",
                "cli_l_flag": "skip_registration",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip registration module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_generate_patch_skip: MiraclObj = MiraclObj(
        name="workflow_generate_patch_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sgp",
        cli_l_flag="skip_generate_patch",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_gps",
                "cli_l_flag": "skip_generate_patch",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip generate patch module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_preprocessing_parallel_skip: MiraclObj = MiraclObj(
        name="workflow_preprocessing_parallel_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="spp",
        cli_l_flag="skip_preprocessing_parallel",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_pps",
                "cli_l_flag": "skip_preprocessing_parallel",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip preprocessing parallel module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_inference_skip: MiraclObj = MiraclObj(
        name="workflow_inference_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="si",
        cli_l_flag="skip_inference",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_is",
                "cli_l_flag": "skip_inference",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip inference module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_patch_stacking_skip: MiraclObj = MiraclObj(
        name="workflow_patch_stacking_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sps",
        cli_l_flag="skip_patch_stacking",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_pss",
                "cli_l_flag": "skip_patch_stacking",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip patch stacking module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_data_normalization_skip: MiraclObj = MiraclObj(
        name="workflow_data_normalization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sdn",
        cli_l_flag="skip_data_normalization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_dns",
                "cli_l_flag": "skip_data_normalization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip data normalization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_skeletonization_skip: MiraclObj = MiraclObj(
        name="workflow_skeletonization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="ss",
        cli_l_flag="skip_skeletonization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_ss",
                "cli_l_flag": "skip_skeletonization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip skeletonization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_voxelized_skeletonization_skip: MiraclObj = MiraclObj(
        name="workflow_voxelized_skeletonization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="svs",
        cli_l_flag="skip_voxelized_skeletonization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_vss",
                "cli_l_flag": "skip_voxelized_skeletonization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip voxelized skeletonization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_voxelized_normalization_skip: MiraclObj = MiraclObj(
        name="workflow_voxelized_normalization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="svn",
        cli_l_flag="skip_voxelized_normalization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_vn",
                "cli_l_flag": "skip_voxelized_normalization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip voxelized normalization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_warped_voxelized_skeletonization_skip: MiraclObj = MiraclObj(
        name="workflow_warped_voxelized_skeletonization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="swvs",
        cli_l_flag="skip_warped_voxelized_skeletonization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_swvs",
                "cli_l_flag": "skip_warped_voxelized_skeletonization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip warped voxelized skeletonization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_warped_voxelized_normalization_skip: MiraclObj = MiraclObj(
        name="workflow_warped_voxelized_normalization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="swvn",
        cli_l_flag="skip_warped_voxelized_normalization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_swvn",
                "cli_l_flag": "skip_warped_voxelized_normalization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip warped voxelized normalization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_feat_extract_skeletonization_skip: MiraclObj = MiraclObj(
        name="workflow_feat_extract_skeletonization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sfes",
        cli_l_flag="skip_feat_extract_skeletonization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_sfes",
                "cli_l_flag": "skip_feat_extract_skeletonization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip feature extraction skeletonization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )

    workflow_feat_extract_normalization_skip: MiraclObj = MiraclObj(
        name="workflow_feat_extract_normalization_skip",
        tags=["mapl3", "flow", "mapl3_flow"],
        cli_s_flag="sfen",
        cli_l_flag="skip_feat_extract_normalization",
        flow={
            "mapl3": {
                "cli_s_flag": "mws_sfen",
                "cli_l_flag": "skip_feat_extract_normalization",
                "cli_group": CliGroup.MAPL3_SKIPS,
            }
        },
        cli_obj_type=ArgumentType.CUSTOM_BOOL,
        cli_help="skip feature extraction normalization module",
        obj_default=False,
        module="mapl3",
        module_group="flow",
        version_added="2.4.0",
    )
