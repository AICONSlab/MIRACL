from miracl.system.miracl_utilfns.utilfns_module_helpers import (
    move_to_new_folder_and_rename,
)
from miracl.system.registry.mapl3_cli_parser_description import (
    MAPL3_CLI_PARSER_DESCRIPTION,
)
from miracl.system.registry.registry_loader import load_modules_from_yaml
from miracl.system.datamodels.to_argparse_class_test import MiraclCLIBuilder
from miracl.system.datamodels.miraclobj_enums import ModuleType

# FIX: These should not have to be imported. This should be handled declaratively.
from miracl.system.miracl_utilfns import (
    create_ort2std_file,
    move_warping_reg_final_contents,
    move_to_new_folder_and_rename,
)
import subprocess
from pathlib import Path


# FIX: None of the overrides should be declared imperatively
def main():
    reg = load_modules_from_yaml("/code/miracl/system/registry/configs/modules.yaml")

    cli_builder = MiraclCLIBuilder(
        registry=reg,
        description=MAPL3_CLI_PARSER_DESCRIPTION,
    )
    parser = cli_builder.build_parser()
    args, parsed_objs = cli_builder.parse()

    reg.list_modules()

    # info = reg.list_modules(verbose=False)
    # print(info["preprocessing_parallel"]["script"])

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
        # print("")
        print_delimiter()
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
                # reg.get_override_flag(
                #     "preprocessing_parallel",
                #     "tissue_percentage_threshold",
                #     manual_module_type=ModuleType.MODULE,
                # ): 20,
                # reg.get_override_flag(
                #     "preprocessing_parallel",
                #     "intensity_threshold",
                #     manual_module_type=ModuleType.MODULE,
                # ): 1,
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
                # reg.get_override_flag(
                #     "inference",
                #     "metadata_file",
                #     manual_module_type=ModuleType.MODULE,
                # ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/generated_patches/metadata.json",
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
            dx = int(str(reg.get_override_value("conversion", "down")))
            dx = f"0{dx}" if 0 <= dx <= 9 else str(dx)
            reg.run(
                "warping",
                overrides={
                    "-r": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/clar_allen_reg",
                    # "-i": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/conv_final",
                    "-i": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['output']}/voxelized_results.nii.gz",
                    "-o": f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/{vals['output']}/ort2std.txt",
                    "-s": vals["channel"],
                    # "-l": f"average_template_{reg.get_override_value('warping', 'vox_res')}um.nii.gz",
                    "-l": "None",
                },
            )
            move_warping_reg_final_contents(
                f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/warped_results"
            )
        print_delimiter()

    # FIX: Must be added as a module!!!

    heatmaps_path = (
        Path(
            f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}"
        )
        / "heatmaps"
    )
    heatmaps_path.mkdir(parents=True, exist_ok=True)
    for step in [
        "mapl3_skel",
        "mapl3_norm",
    ]:
        # command = [
        #     "python",
        #     "/code/miracl/seg/mapl3/mapl3_plot_warped_data.py",
        #     "-p",
        #     f"/data3/projects/josmann/mapl3/preprocessed/warped_results/voxelized_results_{step}_channel_allen_space.nii.gz",
        #     "-v",
        #     str(25),
        #     "-gs",
        #     "2",
        #     "-d",
        #     heatmaps_path,
        #     "-o",
        #     f"heatmap_{step}",
        # ]
        # _ = subprocess.run(command)
        # print_delimiter()
        reg.run(
            "plot_warped_data",
            overrides={
                reg.get_override_flag(
                    "plot_warped_data",
                    "pvalue",
                    manual_module_type=ModuleType.MODULE,
                ): f"/data3/projects/josmann/mapl3/preprocessed/warped_results/voxelized_results_{step}_channel_allen_space.nii.gz",
                reg.get_override_flag(
                    "plot_warped_data",
                    "vox",
                    manual_module_type=ModuleType.MODULE,
                ): str(25),
                reg.get_override_flag(
                    "plot_warped_data",
                    "sigma",
                    manual_module_type=ModuleType.MODULE,
                ): 2,
                reg.get_override_flag(
                    "plot_warped_data",
                    "dir_outfile",
                    manual_module_type=ModuleType.MODULE,
                ): heatmaps_path,
                reg.get_override_flag(
                    "plot_warped_data",
                    "outfile",
                    manual_module_type=ModuleType.MODULE,
                ): f"heatmap_{step}",
            },
        )
        print_delimiter()

    for step_name, vals in {
        "feat_extract_skeletonization": {
            "channel": "voxelized_results_mapl3_skel_channel_allen_space.nii.gz",
            "skip": reg.get_override_value(
                "workflow_skips", "workflow_feat_extract_skeletonization_skip"
            ),
            "identifier": "mapl3_skel",
        },
        "feat_extract_normlization": {
            "channel": "voxelized_results_mapl3_norm_channel_allen_space.nii.gz",
            "skip": reg.get_override_value(
                "workflow_skips", "workflow_feat_extract_normalization_skip"
            ),
            "identifier": "mapl3_norm",
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
                    ): f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/warped_results/{vals['channel']}",
                    reg.get_override_flag(
                        "feat_extract",
                        "lbl",
                        manual_module_type=ModuleType.MODULE,
                    ): "/code/atlases/ara/annotation/annotation_hemi_split_10um.nii.gz",
                },
            )
            # FIX: Should be declared somehow instead of being called here imperatively
            move_to_new_folder_and_rename(
                f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/extracted_features",
                f"{reg.get_override_value('workflow_connectors', 'mapl3_workflow_results_folder')}/warped_results/clarity_segmentation_features_ara_labels_split.csv",
                str(vals["identifier"]),
            )
        print_delimiter()


if __name__ == "__main__":
    main()

# Running: /code/miracl/system/venvs/mapl3-skeletonization-env/bin/python /code/miracl/seg/mapl3/mapl3_skeletonization.py --threshold 1000 --num_erosion 50 --remove_small_obj_thr 64 --remove_large_obj_thr 50000 --elongation_thr 5 --euler_number_thr 100 --cpu_load 0.7 --dilate_distance_transform_flag True --alpha 0.5 --input /data3/projects/josmann/mapl3/preprocessed/stacked_patches --brain_mask /data3/projects/josmann/mapl3/preprocessed/reg_final/annotation_hemi_combined_10um_tiff_clar --raw_data /data3/projects/ahmadreza/deeptrace/datasets/ssl_pretrain/20230928_MO15_Brain2/Ex_488_Em_525_stitched --out_dir /data3/projects/josmann/mapl3/preprocessed

# josmann@nao:/code/miracl/system/registry$ python run_mapl3_workflow.py --mwfc_raw_autoflor_tiff_folder /data3/projects/ahmadreza/deeptrace/datasets/ssl_pretrain/20230928_MO15_Brain2/Ex_647_Em_680_stitched --mwfc_raw_signal_tiff_folder /data3/projects/ahmadreza/deeptrace/datasets/ssl_pretrain/20230928_MO15_Brain2/Ex_488_Em_525_stitched --mwfc_results_folder /data3/projects/josmann/mapl3/preprocessed -mctn_vx 1.8 -mctn_vz 3 --mgp_brain_mask_erosion_flag True --mps_dtype float32 --mrca_orient_code PLI --mv_res_xy 1.8 --mv_res_z 3 --mv_downsample_yx_axis 10 --mv_downsample_z_axis 6 -mctn_d 20 --mpp_intensity_threshold 1 --mpp_tissue_percentage_threshold 20 --mi_gpu_index all --mi_save_prob_map True --skip_conversion True --skip_registration True --skip_generate_patch True --skip_preprocessing_parallel True --skip_inference True --skip_patch_stacking True --skip_data_normalization True --skip_skeletonization False --skip_voxelized_skeletonization True --skip_voxelized_normalization True --skip_warped_voxelized_normalization True --skip_warped_voxelized_skeletonization True --skip_feat_extract_skeletonization True --skip_feat_extract_normalization True
