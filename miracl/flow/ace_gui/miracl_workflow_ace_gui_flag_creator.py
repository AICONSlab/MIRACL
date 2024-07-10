#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flag Creator

Description:
    Creates flag dictionaries for use in controller.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from .miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu

REG_BOOL_FLAGS = "set_bool"

class flag_creator:
    @staticmethod
    def create_main_tab_flags(main_tab, method_checkbox):
        main_tab_flags = {
            "-s": wu.get_tab_var(main_tab, "single_method_path_input", "textfield")
            if not method_checkbox.isChecked()
            else None,
            "-c": f"{wu.get_tab_var(main_tab, 'multi_method_ctrl_path_input', 'textfield')} {wu.get_tab_var(main_tab, 'multi_method_ctrl_tif_path_input', 'textfield')}"
            if method_checkbox.isChecked()
            else None,
            "-t": f"{wu.get_tab_var(main_tab, 'multi_method_treated_path_input', 'textfield')} {wu.get_tab_var(main_tab, 'multi_method_treated_tif_path_input', 'textfield')}",
            "--sa_output_folder": wu.get_tab_var(
                main_tab, "output_folder_path_input", "textfield"
            ),
            "--sa_model_type": wu.get_tab_var(
                main_tab, "model_architecture_input", "multiplechoice"
            ).lower(),
            "--sa_resolution": f"{wu.get_tab_var(main_tab, 'x_res_field_input', 'textfield')} {wu.get_tab_var(main_tab, 'y_res_field_input', 'textfield')} {wu.get_tab_var(main_tab, 'z_res_field_input', 'textfield')}",
            "--sa_gpu_index": str(
                wu.get_tab_var(main_tab, "gpu_index_input", "spinbox")
            ),
            "--ctn_down": str(
                wu.get_tab_var(main_tab, "conversion_dx_input", "spinbox")
            ),
            "--rca_orient_code": wu.get_tab_var(
                main_tab, "orientation_code_input", "textfield"
            ),
            "--rca_voxel_size": wu.get_tab_var(
                main_tab, "labels_voxel_size_input", "multiplechoice"
            ),
            "--rva_downsample": wu.get_tab_var(
                main_tab, "voxelization_dx_input", "spinbox"
            ),
            "--rwc_voxel_size": wu.get_tab_var(
                main_tab, "warping_voxel_size_input", "multiplechoice"
            ),
            "--rerun-registration": "true"
            if wu.get_tab_var(main_tab, "rerun_registration_input", "multiplechoice")
            == "yes"
            else "false",
            "--rerun-segmentation": "true"
            if wu.get_tab_var(main_tab, "rerun_segmentation_input", "multiplechoice")
            == "yes"
            else "false",
            "--rerun-conversion": "true"
            if wu.get_tab_var(main_tab, "rerun_conversion_input", "multiplechoice")
            == "yes"
            else "false",
        }
        return main_tab_flags

    @staticmethod
    def create_conversion_flags(conversion_tab):
        conversion_tab_flags = {
            "--ctn_channum": wu.get_tab_var(
                conversion_tab, "conversion_channel_number_input", "textfield"
            ),
            "--ctn_chanprefix": wu.get_tab_var(
                conversion_tab, "conversion_channel_prefix_input", "textfield"
            ),
            "--ctn_channame": wu.get_tab_var(
                conversion_tab, "conversion_output_channel_name_input", "textfield"
            ),
            "--ctn_outnii": wu.get_tab_var(
                conversion_tab, "conversion_output_nii_name_input", "textfield"
            ),
            "--ctn_center": f"{wu.get_tab_var(conversion_tab, 'conversion_center_input_1', 'textfield')} {wu.get_tab_var(conversion_tab, 'conversion_center_input_2', 'textfield')} {wu.get_tab_var(conversion_tab, 'conversion_center_input_3', 'textfield')}",
            "--ctn_downzdim": wu.get_tab_var(
                conversion_tab, "conversion_dx_z_input", "spinbox"
            ),
            "--ctn_prevdown": wu.get_tab_var(
                conversion_tab, "conversion_prev_dx_input", "spinbox"
            ),
            "--ctn_percentile_thr": wu.get_tab_var(
                conversion_tab, "conversion_percentile_thr_input", "textfield"
            ),
        }

        return conversion_tab_flags

    @staticmethod
    def create_segmentation_flags(segmentation_tab):
        segmentation_tab_flags = {
            "--sa_image_size": f"{wu.get_tab_var(segmentation_tab, 'segmentation_image_size_height_input', 'textfield')} {wu.get_tab_var(segmentation_tab, 'segmentation_image_size_width_input', 'textfield')} {wu.get_tab_var(segmentation_tab, 'segmentation_image_size_depth_input', 'textfield')}",
            "--sa_nr_workers": wu.get_tab_var(
                segmentation_tab, "segmentation_nr_workers_input", "spinbox"
            ),
            "--sa_cache_rate": wu.get_tab_var(
                segmentation_tab, "segmentation_cache_rate_input", "spinbox"
            ),
            "--sa_batch_size": wu.get_tab_var(
                segmentation_tab, "segmentation_batch_size_input", "spinbox"
            ),
            "--sa_monte_carlo": "1"
            if wu.get_tab_var(
                segmentation_tab, "segmentation_monte_carlo_input", "multiplechoice"
            )
            == "yes"
            else "0",
            "--sa_visualize_results": REG_BOOL_FLAGS if wu.get_tab_var(
                segmentation_tab,
                "segmentation_visualize_results_input",
                "multiplechoice",
            ) == "yes" else None,
            "--sa_uncertainty_map": REG_BOOL_FLAGS
            if wu.get_tab_var(
                segmentation_tab, "segmentation_uncertainty_map_input", "multiplechoice"
            )
            == "yes"
            else None,
            "--sa_binarization_threshold": wu.get_tab_var(
                segmentation_tab, "segmentation_binarization_thr_input", "spinbox"
            ),
            "--sa_percentage_brain_patch_skip": wu.get_tab_var(
                segmentation_tab, "segmentation_brain_patch_skip_input", "spinbox"
            ),
        }

        return segmentation_tab_flags

    @staticmethod
    def create_clarity_registration_flags(clarity_registration_tab):
        clarity_registration_tab_flags = {
            "--rca_hemi": wu.get_tab_var(
                clarity_registration_tab, "reg_hemi_input", "multiplechoice"
            ),
            "--rca_allen_label": wu.get_tab_var(
                clarity_registration_tab, "reg_allen_lbl_warp_path_input", "textfield"
            ),
            "--rca_allen_atlas": wu.get_tab_var(
                clarity_registration_tab, "reg_cust_allen_atlas_path_input", "textfield"
            ),
            "--rca_side": "rh"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_side_input", "multiplechoice"
            )
            == "right hemisphere"
            else "lh",
            "--rca_no_mosaic_fig": None
            if wu.get_tab_var(
                clarity_registration_tab, "reg_mosaic_figure_input", "multiplechoice"
            )
            == "yes"
            else REG_BOOL_FLAGS,
            "--rca_olfactory_bulb": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_olfactory_bulb_input", "multiplechoice"
            )
            == "included"
            else "0",
            "--rca_skip_cor": REG_BOOL_FLAGS
            if wu.get_tab_var(
                clarity_registration_tab,
                "reg_util_int_correction_input",
                "multiplechoice",
            )
            == "skip"
            else None,
            "--rca_warp": REG_BOOL_FLAGS
            if wu.get_tab_var(
                clarity_registration_tab, "reg_warp_to_allen_input", "multiplechoice"
            )
            == "yes"
            else None,
        }

        return clarity_registration_tab_flags

    @staticmethod
    def create_voxelization_warping_flags(vox_warp_tab):
        voxelization_warping_tab_flags = {
            "--rva_vx_res": wu.get_tab_var(
                vox_warp_tab, "vox_warp_vox_axes_x_input", "textfield"
            ),
            "--rva_vz_res": wu.get_tab_var(
                vox_warp_tab, "vox_warp_vox_axes_z_input", "textfield"
            ),
            "--rwc_input_folder": wu.get_tab_var(
                vox_warp_tab, "vox_warp_warp_input_folder_path_input", "textfield"
            ),
            "--rwc_input_nii": wu.get_tab_var(
                vox_warp_tab, "vox_warp_warp_input_nii_file_path_input", "textfield"
            ),
        }

        return voxelization_warping_tab_flags

    @staticmethod
    def create_clusterwise_flags(clusterwise_tab):
        clusterwise_tab_flags = {
            "--pcs_atlas_dir": wu.get_tab_var(
                clusterwise_tab, "clusterwise_atlas_folder_path_input", "textfield"
            ),
            "--pcs_num_perm": wu.get_tab_var(
                clusterwise_tab, "clusterwise_nr_permutations_input", "textfield"
            ),
            "--pcs_img_resolution": wu.get_tab_var(
                clusterwise_tab, "clusterwise_image_resolution_input", "multiplechoice"
            ),
            "--pcs_smoothing_fwhm": wu.get_tab_var(
                clusterwise_tab, "clusterwise_fwhm_smoothing_input", "textfield"
            ),
            "--pcs_tfce_start": wu.get_tab_var(
                clusterwise_tab, "clusterwise_thr_start_input", "textfield"
            ),
            "--pcs_tfce_step": wu.get_tab_var(
                clusterwise_tab, "clusterwise_thr_step_input", "textfield"
            ),
            "--pcs_cpu_load": wu.get_tab_var(
                clusterwise_tab, "clusterwise_cpu_load_input", "textfield"
            ),
            "--pcs_tfce_h": wu.get_tab_var(
                clusterwise_tab, "clusterwise_tfce_h_input", "textfield"
            ),
            "--pcs_tfce_e": wu.get_tab_var(
                clusterwise_tab, "clusterwise_tfce_e_input", "textfield"
            ),
            "--pcs_step_down_p": wu.get_tab_var(
                clusterwise_tab, "clusterwise_step_down_input", "textfield"
            ),
            "--pcs_mask_thr": wu.get_tab_var(
                clusterwise_tab, "clusterwise_mask_thr_input", "textfield"
            ),
        }

        return clusterwise_tab_flags

    @staticmethod
    def create_correlation_stats_flags(correlation_stats_tab):
        correlation_stats_tab_flags = {
            "--cf_pvalue_thr": wu.get_tab_var(
                correlation_stats_tab,
                "correlation_stats_correlation_cf_pvalue_input",
                "textfield",
            ),
            "--u_atlas_dir": wu.get_tab_var(
                correlation_stats_tab,
                "correlation_stats_stats_atlas_folder_path_input",
                "textfield",
            ),
            "--p_outfile": wu.get_tab_var(
                correlation_stats_tab,
                "correlation_stats_stats_outfile_input",
                "textfield",
            ),
        }

        return correlation_stats_tab_flags

    @staticmethod
    def create_heatmap_flags(heatmap_tab):
        heatmap_tab_flags = {
            "--sh_group1": wu.get_tab_var(
                heatmap_tab,
                "heatmap_group_1_path_input",
                "textfield",
            ),
            "--sh_group2": wu.get_tab_var(
                heatmap_tab,
                "heatmap_group_2_path_input",
                "textfield",
            ),
            "--sh_vox": wu.get_tab_var(
                heatmap_tab, "heatmap_voxel_size_input", "multiplechoice"
            ),
            "--sh_sigma": str(
                wu.get_tab_var(heatmap_tab, "heatmap_sigma_input", "spinbox")
            ),
            "--sh_percentile": str(
                wu.get_tab_var(heatmap_tab, "heatmap_percentile_input", "spinbox")
            ),
            "--sh_colourmap_pos": wu.get_tab_var(
                heatmap_tab, "heatmap_colourmap_positive_input", "textfield"
            ),
            "--sh_colourmap_neg": wu.get_tab_var(
                heatmap_tab, "heatmap_colourmap_negative_input", "textfield"
            ),
            "--sh_sagittal": f"{wu.get_tab_var(heatmap_tab, 'heatmap_slicing_sagittal_axis_start_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_sagittal_axis_interval_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_sagittal_axis_nr_slices_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_sagittal_axis_nr_rows_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_sagittal_axis_nr_cols_input', 'textfield')}",
            "--sh_coronal": f"{wu.get_tab_var(heatmap_tab, 'heatmap_slicing_coronal_axis_start_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_coronal_axis_interval_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_coronal_axis_nr_slices_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_coronal_axis_nr_rows_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_coronal_axis_nr_cols_input', 'textfield')}",
            "--sh_axial": f"{wu.get_tab_var(heatmap_tab, 'heatmap_slicing_axial_axis_start_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_axial_axis_interval_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_axial_axis_nr_slices_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_axial_axis_nr_rows_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_slicing_axial_axis_nr_cols_input', 'textfield')}",
            "--sh_figure_dim": f"{wu.get_tab_var(heatmap_tab, 'heatmap_figure_dims_width_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_figure_dims_height_input', 'textfield')}",
            "--sh_dir_outfile": wu.get_tab_var(
                heatmap_tab, "heatmap_output_folder_path_input", "textfield"
            ),
            "--sh_outfile": f"{wu.get_tab_var(heatmap_tab, 'heatmap_output_filenames_group_1_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_output_filenames_group_2_input', 'textfield')} {wu.get_tab_var(heatmap_tab, 'heatmap_output_filenames_group_diff_input', 'textfield')}",
            "--sh_extension": wu.get_tab_var(
                heatmap_tab, "heatmap_extension_input", "textfield"
            ),
            "--sh_dpi": wu.get_tab_var(heatmap_tab, "heatmap_dpi_input", "textfield"),
        }

        return heatmap_tab_flags
