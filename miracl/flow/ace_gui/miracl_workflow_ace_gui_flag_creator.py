#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget Utilities

Description:
    Tab manager for ACE flow GUI.

Copyright:
    (c) 2024 AICONs Lab. All rights reserved.

Author:
    Jonas Osmann
    j.osmann@mail.utoronto.ca

License:
    GPL-3.0
"""

from miracl_workflow_ace_gui_widget_utils import WidgetUtils as wu


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
            ),
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
            "--rca_no_mosaic_fig": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_mosaic_figure_input", "multiplechoice"
            )
            == "yes"
            else "0",
            "--rca_olfactory_bulb": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_olfactory_bulb_input", "multiplechoice"
            )
            == "included"
            else "0",
            "--rca_skip_cor": "1"
            if wu.get_tab_var(
                clarity_registration_tab,
                "reg_util_int_correction_input",
                "multiplechoice",
            )
            == "run"
            else "0",
            "--rca_warp": "1"
            if wu.get_tab_var(
                clarity_registration_tab, "reg_warp_to_allen_input", "multiplechoice"
            )
            == "yes"
            else "0",
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
