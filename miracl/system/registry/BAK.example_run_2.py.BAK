### Import registry ###
from miracl.system.registry.registry import MiraclRegistry

# Import parser
from miracl.system.datamodels.to_argparse_class_test import MiraclCLIBuilder

### Import ENUMS
from miracl.system.datamodels.miraclobj_enums import ModuleType

### Import templates and runners ###
from miracl.system.registry.mapl3_workflow_runners import *
from miracl.system.registry.mapl3_workflow_templates import *

### Import utilfns
from miracl_utilfns import create_ort2std_file


reg = MiraclRegistry()
reg.register_from_template(
    "workflow_connectors",
    mapl3_workflow_connectors_dict,
    default_runner,
)
reg.register_from_template(
    "workflow_skips",
    workflow_skips_dict,
    default_runner,
)
reg.register_from_template(
    "conversion",
    conv_tiff_nii_dict,
    conv_runner,
)
reg.register_from_template(
    "registration",
    reg_clar_allen_dict,
    reg_runner,
)
reg.register_from_template(
    "generate_patch",
    mapl3_generate_patch_dict,
    gen_patch_runner,
)
reg.register_from_template(
    "preprocessing_parallel",
    mapl3_preprocessing_parallel_dict,
    preprocessing_parallel_runner,
)
reg.register_from_template(
    "inference",
    mapl3_inference_dict,
    inference_runner,
)
reg.register_from_template(
    "patch_stacking",
    mapl3_patch_stacking_dict,
    patch_stacking_runner,
)
reg.register_from_template(
    "raw_data_normalization",
    mapl3_raw_data_normalization_dict,
    raw_data_normalization_runner,
)
reg.register_from_template(
    "skeletonization",
    mapl3_skeletonization_dict,
    skeletonization_runner,
)
reg.register_from_template(
    "voxelization",
    mapl3_voxelization_dict,
    voxelization_runner,
)
reg.register_from_template(
    "warping",
    warp_clar_allen_dict,
    warping_runner,
)
reg.register_from_template(
    "feat_extract",
    mapl3_feat_extract_dict,
    feat_extract_runner,
)

cli_builder = MiraclCLIBuilder(reg)
parser = cli_builder.build_parser()
args, parsed_objs = cli_builder.parse()


def print_delimiter():
    print("\n######################################################\n")


print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_conversion_skip"):
    print("Skipping conversion module...")
else:
    reg.run(
        "conversion",
        overrides={
            reg.get_override_flag(
                "conversion",
                "tiff_folder",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_autoflor_tiff_folder",
            ),
            reg.get_override_flag(
                "conversion",
                "output_folder",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_registration_skip"):
    print("Skipping registration module...")
    print_delimiter()
else:
    dx = int(str(reg.get_override_value("conversion", "down")))
    dx = f"0{dx}" if 0 <= dx <= 9 else str(dx)
    reg.run(
        "registration",
        overrides={
            "-c": reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_autoflor_tiff_folder",
            ),
            "-i": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/conv_final/{reg.get_override_value('conversion', 'outnii')}_{dx}x_down_{reg.get_override_value('conversion', 'channame')}_chan.nii.gz",
            "-r": reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
        },
    )
    print("")
if reg.get_override_value("workflow_skips", "workflow_generate_patch_skip"):
    print("Skipping generating patch module...")
else:
    reg.run(
        "generate_patch",
        overrides={
            reg.get_override_flag(
                "generate_patch",
                "input",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_signal_tiff_folder",
            ),
            reg.get_override_flag(
                "generate_patch",
                "brain_mask",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/reg_final/annotation_hemi_{reg.get_override_value('registration', 'hemi')}_{reg.get_override_value('registration', 'voxel_size')}um_tiff_clar",
            reg.get_override_flag(
                "generate_patch",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_preprocessing_parallel_skip"):
    print("Skipping preprocessing parallel module...")
else:
    reg.run(
        "preprocessing_parallel",
        overrides={
            reg.get_override_flag(
                "preprocessing_parallel",
                "input",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/generated_patches",
            reg.get_override_flag(
                "preprocessing_parallel",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
            reg.get_override_flag(
                "preprocessing_parallel",
                "metadata_file",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/generated_patches/metadata.json",
            reg.get_override_flag(
                "preprocessing_parallel",
                "tissue_percentage_threshold",
                manual_module_type=ModuleType.MODULE,
            ): 20,
            reg.get_override_flag(
                "preprocessing_parallel",
                "intensity_threshold",
                manual_module_type=ModuleType.MODULE,
            ): 1,
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_inference_skip"):
    print("Skipping inference module...")
else:
    reg.run(
        "inference",
        overrides={
            reg.get_override_flag(
                "inference",
                "config",
                manual_module_type=ModuleType.MODULE,
            ): "/code/miracl/seg/mapl3/config_finetune.yml",
            reg.get_override_flag(
                "inference",
                "input_dir",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/preprocessing_parallel",
            reg.get_override_flag(
                "inference",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
            reg.get_override_flag(
                "inference",
                "model_path",
                manual_module_type=ModuleType.MODULE,
            ): "/code/miracl/seg/mapl3/models/best_metric_model.pth",
            reg.get_override_flag(
                "inference",
                "gpu_index",
                manual_module_type=ModuleType.MODULE,
            ): "all",
            reg.get_override_flag(
                "inference",
                "save_prob_map",
                manual_module_type=ModuleType.MODULE,
            ): "True",
            reg.get_override_flag(
                "inference",
                "metadata_file",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/generated_patches/metadata.json",
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_patch_stacking_skip"):
    print("Skipping patch stacking module...")
else:
    reg.run(
        "patch_stacking",
        overrides={
            reg.get_override_flag(
                "patch_stacking",
                "input_dir",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/inference/out_prob",
            reg.get_override_flag(
                "patch_stacking",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
            reg.get_override_flag(
                "patch_stacking",
                "tiff_folder",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_signal_tiff_folder",
            ),
            reg.get_override_flag(
                "patch_stacking",
                "metadata_file",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/generated_patches/metadata.json",
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_data_normalization_skip"):
    print("Skipping data normalization module...")
else:
    reg.run(
        "raw_data_normalization",
        overrides={
            reg.get_override_flag(
                "raw_data_normalization",
                "input_dir",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/stacked_patches",
            reg.get_override_flag(
                "raw_data_normalization",
                "tiff_folder",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_signal_tiff_folder",
            ),
            reg.get_override_flag(
                "raw_data_normalization",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
            reg.get_override_flag(
                "raw_data_normalization",
                "brain_mask",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/reg_final/annotation_hemi_{reg.get_override_value('registration', 'hemi')}_{reg.get_override_value('registration', 'voxel_size')}um_tiff_clar",
        },
    )
print_delimiter()
if reg.get_override_value("workflow_skips", "workflow_skeletonization_skip"):
    print("Skipping skeletonization module...")
else:
    reg.run(
        "skeletonization",
        overrides={
            reg.get_override_flag(
                "raw_data_normalization",
                "input_dir",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/stacked_patches",
            reg.get_override_flag(
                "raw_data_normalization",
                "brain_mask",
                manual_module_type=ModuleType.MODULE,
            ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/reg_final/annotation_hemi_{reg.get_override_value('registration', 'hemi')}_{reg.get_override_value('registration', 'voxel_size')}um_tiff_clar",
            reg.get_override_flag(
                "raw_data_normalization",
                "tiff_folder",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_raw_signal_tiff_folder",
            ),
            reg.get_override_flag(
                "skeletonization",
                "out_dir",
                manual_module_type=ModuleType.MODULE,
            ): reg.get_override_value(
                "workflow_connectors",
                "mapl3_workflow_results_folder",
            ),
        },
    )
print_delimiter()
for step_name, vals in {
    "normalized_raw_data": {
        "input": "normalized_raw_data",
        "output": "voxelized_normalization",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_voxelized_normalization_skip"
        ),
    },
    "skeletonized": {
        "input": "skeletonized",
        "output": "voxelized_skeletonization",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_voxelized_skeletonization_skip"
        ),
    },
}.items():
    if vals["skip"]:
        print(f"Skipping {vals['output']}...")
    else:
        reg.run(
            "voxelization",
            overrides={
                reg.get_override_flag(
                    "voxelization",
                    "input_dir",
                    manual_module_type=ModuleType.MODULE,
                ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['input']}",
                reg.get_override_flag(
                    "voxelization",
                    "out_dir",
                    manual_module_type=ModuleType.MODULE,
                ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['output']}",
            },
        )
    print_delimiter()
for step_name, vals in {
    "voxelized_normalized_raw_data": {
        "channel": "mapl3_norm",
        "output": "voxelized_normalization",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_warped_voxelized_normalization_skip"
        ),
    },
    "voxelized_skeletonized": {
        "channel": "mapl3_skel",
        "output": "voxelized_skeletonization",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_warped_voxelized_skeletonization_skip"
        ),
    },
}.items():
    if vals["skip"]:
        print(f"Skipping warped_{vals['output']}...")
    else:
        create_ort2std_file(
            reg.get_override_value(
                "workflow_connectors", "mapl3_workflow_raw_signal_tiff_folder"
            ),
            reg.get_override_value("registration", "orient_code"),
            f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['output']}",
        )
        reg.run(
            "warping",
            overrides={
                "-r": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/clar_allen_reg",
                "-i": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/conv_final",
                "-o": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['output']}/ort2std.txt",
                "-s": vals["channel"],
                "-l": f"average_template_{reg.get_override_value('warping', 'vox_res')}um.nii.gz",
            },
        )
    print_delimiter()
for step_name, vals in {
    "feat_extract_skeletonization": {
        "channel": "vox_seg_mapl3_skel_res.nii.gz",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_feat_extract_skeletonization_skip"
        ),
    },
    "feat_extract_normlization": {
        "channel": "vox_seg_mapl3_norm_res.nii.gz",
        "skip": reg.get_override_value(
            "workflow_skips", "workflow_feat_extract_normalization_skip"
        ),
    },
}.items():
    if vals["skip"]:
        print(f"Skipping {step_name}...")
    else:
        reg.run(
            "feat_extract",
            overrides={
                reg.get_override_flag(
                    "feat_extract",
                    "vox_file",
                    manual_module_type=ModuleType.MODULE,
                ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/reg_final/{vals['channel']}",
                reg.get_override_flag(
                    "feat_extract",
                    "lbl",
                    manual_module_type=ModuleType.MODULE,
                ): "/code/atlases/ara/annotation/annotation_hemi_combined_10um.nii.gz",
            },
        )
    print_delimiter()

# josmann@maghz:/code/miracl/system/registry$ python example_run_2.py -mwfc_rtf /input/tiffs -mwfc_cof /output/mapl3
