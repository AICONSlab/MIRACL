import copy
import functools
import re
from argparse import Namespace
from pathlib import Path
from unittest import mock
from unittest.mock import mock_open

import pytest

from miracl.flow import miracl_workflow_ace_interface as ACE

DIR = "mock_dir"
ACE_PATH = "miracl.flow.miracl_workflow_ace_interface"


class TestAceInterfaceFolderCreator:
    @mock.patch(ACE_PATH + ".Path.mkdir")
    def test_ace_folder_exists(self, mkdir_mock):
        ACE.FolderCreator.create_folder(DIR, "temp", "working")
        assert mkdir_mock.call_count == 1

    @mock.patch(ACE_PATH + ".Path.mkdir")
    def test_ace_folder_return(self, mkdir_mock):
        folder = ACE.FolderCreator.create_folder(DIR, "temp", "working")
        assert folder == Path(DIR + "/temp/working")


class TestAceInterfaceConvertedNifti:
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_get_converted_nifti(self, mock_glob):
        mock_glob.return_value = [Path(DIR + "/conv_final/conv_final.nii")]
        file = ACE.GetConverterdNifti.get_nifti_file(DIR + "/conv_final")
        assert file == Path(DIR + "/conv_final/conv_final.nii")

    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_get_converted_nifti_no_file_error(self, mock_glob):
        mock_glob.return_value = []
        with pytest.raises(FileNotFoundError) as e:
            ACE.GetConverterdNifti.get_nifti_file(DIR + "/conv_final")
        assert "No converted nifti files found in:" in str(e.value)

    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_get_converted_nifti_many_files_error(self, mock_glob):
        mock_glob.return_value = [
            Path(DIR + "/conv_final/conv_final.nii"),
            Path(DIR + "/conv_final/conv_final2.nii"),
        ]
        with pytest.raises(ValueError) as e:
            ACE.GetConverterdNifti.get_nifti_file(DIR + "/conv_final")
        assert "More than one nifti found in:" in str(e.value)


class TestAceInterfaceStackTiffs:
    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_stack_tiffs_folder_unlink_fiji_exists(self, mock_is_file, mock_unlink):
        fiji = Path(DIR + "/fiji.ijm")
        mock_is_file.return_value = True
        ACE.StackTiffs.check_folders(fiji, Path(""))
        assert mock_unlink.called

    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_stack_tiffs_folder_unlink_fiji_not_exists(
        self, mock_is_file, mock_unlink
    ):
        fiji = Path(DIR + "/fiji.ijm")
        mock_is_file.return_value = False
        ACE.StackTiffs.check_folders(fiji, Path(""))
        assert not mock_unlink.called

    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_stack_tiffs_folder_unlink_stacked_exists(
        self, mock_is_file, mock_unlink
    ):
        stacked = Path(DIR + " /stacked.tif")
        mock_is_file.return_value = True
        ACE.StackTiffs.check_folders(Path(""), stacked)
        assert mock_unlink.called

    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_stack_tiffs_folder_unlink_stacked_not_exists(
        self, mock_is_file, mock_unlink
    ):
        stacked = Path(DIR + " /stacked.tif")
        mock_is_file.return_value = False
        ACE.StackTiffs.check_folders(Path(""), stacked)
        assert not mock_unlink.called

    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_stack_tiffs_stack_subprocess(self, mock_subprocess):
        fiji = Path(DIR + "/fiji.ijm")
        stacked = Path(DIR + "/stacked.tif")
        seg_output = Path(DIR + "/seg_output")
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.StackTiffs.stacking(fiji, stacked, seg_output)
        assert mock_subprocess.called

    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_stack_tiffs_stack_subprocess_cmd(self, mock_subprocess):
        fiji = Path(DIR + "/fiji.ijm")
        stacked = Path(DIR + "/stacked.tif")
        seg_output = Path(DIR + "/seg_output")
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.StackTiffs.stacking(fiji, stacked, seg_output)
        assert "Fiji" in mock_subprocess.call_args_list[0][0][0]

    def test_ace_stack_tiffs_stack_open(self):
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.StackTiffs.stacking("fiji", "stacked", "output")
        open_mock.assert_called_once_with("fiji", "w")

    def test_ace_stack_tiffs_stack_write(self):
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.StackTiffs.stacking("fiji", "stacked", "output")
        assert "File.openSequence(" in open_mock().write.call_args_list[0][0][0]
        assert 'saveAs("Tiff",' in open_mock().write.call_args_list[1][0][0]
        open_mock().write.assert_called_with("close();\n")


class TestAceInterfaceGetVoxSegTif:
    @mock.patch(ACE_PATH + ".shutil.copy")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_check_warping_requirements_copy(self, glob_mock, copy_mock):
        ace_flow_vox_output_folder = Path(DIR + "/vox_final")
        ace_flow_warp_output_folder = Path(DIR + "/warp_output")
        glob_mock.side_effect = [
            [ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz"],
            [ace_flow_warp_output_folder / "warped_seg_seg.nii.gz"],
        ]
        ACE.GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )
        copy_mock.assert_called_once_with(
            ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz",
            ace_flow_warp_output_folder,
        )

    @mock.patch(ACE_PATH + ".shutil.copy")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_check_warping_requirements_glob_call1(self, glob_mock, copy_mock):
        ace_flow_vox_output_folder = Path(DIR + "/vox_final")
        ace_flow_warp_output_folder = Path(DIR + "/warp_output")
        glob_mock.side_effect = [
            [ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz"],
            [ace_flow_warp_output_folder / "warped_seg_seg.nii.gz"],
        ]
        ACE.GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )

        assert glob_mock.call_args_list[0][0][0] == "voxelized_seg_*.nii.gz"

    @mock.patch(ACE_PATH + ".shutil.copy")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_check_warping_requirements_glob_call2(self, glob_mock, copy_mock):
        ace_flow_vox_output_folder = Path(DIR + "/vox_final")
        ace_flow_warp_output_folder = Path(DIR + "/warp_output")
        glob_mock.side_effect = [
            [ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz"],
            [ace_flow_warp_output_folder / "warped_seg_seg.nii.gz"],
        ]
        ACE.GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )

        assert glob_mock.call_args_list[1][0][0] == "voxelized_seg_*.nii.gz"

    @mock.patch(ACE_PATH + ".shutil.copy")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_check_warping_requirements_glob_call2(self, glob_mock, copy_mock):
        ace_flow_vox_output_folder = Path(DIR + "/vox_final")
        ace_flow_warp_output_folder = Path(DIR + "/warp_output")
        glob_mock.side_effect = [
            [ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz"],
            [ace_flow_warp_output_folder / "warped_seg_seg.nii.gz"],
        ]
        ACE.GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )

        assert glob_mock.call_args_list[1][0][0] == "voxelized_seg_*.nii.gz"

    @mock.patch(ACE_PATH + ".shutil.copy")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_check_warping_requirements_glob_return(self, glob_mock, copy_mock):
        ace_flow_vox_output_folder = Path(DIR + "/vox_final")
        ace_flow_warp_output_folder = Path(DIR + "/warp_output")
        glob_mock.side_effect = [
            [ace_flow_vox_output_folder / "voxelized_seg_seg.nii.gz"],
            [ace_flow_warp_output_folder / "warped_seg_seg.nii.gz"],
        ]
        res = ACE.GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )

        assert res == (
            ace_flow_warp_output_folder / "warped_seg_seg.nii.gz",
            ace_flow_warp_output_folder / "ort2std.txt",
        )

    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_create_orientation_file_exists(self, mock_is_file, mock_unlink):
        orientation_file = Path(DIR + "/orientation.txt")
        warp_out = "warp_final/"
        rca_orient_code = "1"
        mock_is_file.return_value = True
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.GetVoxSegTif.create_orientation_file(
                orientation_file, warp_out, rca_orient_code
            )

        assert mock_unlink.called

    @mock.patch(ACE_PATH + ".Path.unlink")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_create_orientation_file_not_exists(self, mock_is_file, mock_unlink):
        orientation_file = Path(DIR + "/orientation.txt")
        warp_out = "warp_final/"
        rca_orient_code = "1"
        mock_is_file.return_value = False
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.GetVoxSegTif.create_orientation_file(
                orientation_file, warp_out, rca_orient_code
            )

        assert not mock_unlink.called

    def test_ace_create_orientation_file_open(self):
        orientation_file = Path(DIR + "/orientation.txt")
        warp_out = "warp_final/"
        rca_orient_code = "1"
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.GetVoxSegTif.create_orientation_file(
                orientation_file, warp_out, rca_orient_code
            )

        open_mock.assert_called_once_with(orientation_file, "w")

    def test_ace_create_orientation_file_write(self):
        orientation_file = Path(DIR + "/orientation.txt")
        warp_out = "warp_final/"
        rca_orient_code = "1"
        with mock.patch(ACE_PATH + ".open", mock_open()) as open_mock:
            ACE.GetVoxSegTif.create_orientation_file(
                orientation_file, warp_out, rca_orient_code
            )

        assert f"tifdir={warp_out}" in open_mock().write.call_args_list[0][0][0]
        assert "ortcode=" in open_mock().write.call_args_list[1][0][0]


class TestAceInterfaceGetCorrInput:
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_check_corr_input_exists_return(self, mock_is_file):
        mock_is_file.return_value = True
        dir_var = DIR
        nifti_name_var = "diff_mean.nii.gz"
        res = ACE.GetCorrInput.check_corr_input_exists(dir_var, nifti_name_var)

        assert res == Path(dir_var) / nifti_name_var

    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_check_corr_input_exists_error(self, mock_is_file):
        mock_is_file.return_value = False
        dir_var = DIR
        nifti_name_var = "diff_mean.nii.gz"
        with pytest.raises(FileNotFoundError) as e:
            res = ACE.GetCorrInput.check_corr_input_exists(dir_var, nifti_name_var)

        assert f"does not exist at '{dir_var}'" in str(e)


class TestAceInterfaceConstructHeatmapCmd:
    base_heatmap_cmd = "miracl stats heatmap_group "
    heatmap_cmd_expected = [
        (
            (1, 2, 3, 4, 5),
            None,
            None,
            (10, 10),
            base_heatmap_cmd + "-s 1 2 3 4 5 -f 10 10 ",
        ),
        (
            None,
            (1, 2, 3, 4, 5),
            None,
            (10, 10),
            base_heatmap_cmd + "-c 1 2 3 4 5 -f 10 10 ",
        ),
        (
            None,
            None,
            (1, 2, 3, 4, 5),
            (10, 10),
            base_heatmap_cmd + "-a 1 2 3 4 5 -f 10 10 ",
        ),
        ((1, 2, 3, 4, 5), None, None, None, base_heatmap_cmd + "-s 1 2 3 4 5 "),
        (None, None, None, None, base_heatmap_cmd),
    ]

    final_heatmap_cmd_expected = [
        (
            Namespace(
                pcs_control=["ctrl_dir/", "ctrl_dir/subj1/cells"],
                pcs_experiment=["exp_dir/", "exp_dir/subj1/cells"],
                sh_vox="10",
                sh_sigma="1",
                sh_percentile="95",
                sh_colourmap_pos="-1",
                sh_colourmap_neg="false",
                sh_outfile="heatmap_final/out",
                sh_extension="png",
                sh_dpi="1000",
            ),
            "heatmap_final",
            "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 ",
            "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 "
            + "-g1 ctrl_dir/ ctrl_dir/subj1/cells -g2 exp_dir/ exp_dir/subj1/cells"
            + " -v 10 -gs 1 -p 95 -cp -1 -cn false -d heatmap_final -o heatmap_final/out "
            + "-e png --dpi 1000",
        ),
    ]

    @pytest.mark.parametrize(
        "sagittal, coronal, axial, dim, expected", heatmap_cmd_expected
    )
    def test_ace_heatmap_cmd_none_args_base(
        self, sagittal, coronal, axial, dim, expected
    ):
        res = ACE.ConstructHeatmapCmd.test_none_args(sagittal, coronal, axial, dim)
        assert res == expected

    @pytest.mark.parametrize(
        "args, heatmap_output, heatmap_cmd, final_cmd", final_heatmap_cmd_expected
    )
    def test_ace_final_heatmap_cmd(self, args, heatmap_output, heatmap_cmd, final_cmd):
        res = ACE.ConstructHeatmapCmd.construct_final_heatmap_cmd(
            args, heatmap_output, heatmap_cmd
        )
        print(re.sub(" +", " ", res))
        assert re.sub(" +", " ", res) == final_cmd


class TestAceInterfaceACESegmentation:
    @mock.patch("miracl.seg.ace_interface.main")
    def test_ace_segment_call(self, mock_seg_interface):
        args = Namespace(sa_model_type="test")
        ACE.ACESegmentation().segment(args)

        assert mock_seg_interface.called


class TestAceInterfaceACEConversion:
    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_convert_call(self, popen_mock):
        args = Namespace(
            single="dir/",
            sa_output_folder="out_dir/",
            ctn_down=1,
            ctn_channum=1,
            ctn_chanprefix=1,
            ctn_channame="x",
            ctn_outnii="y",
            ctn_resx=1,
            ctn_resz=1,
            ctn_center="111",
            ctn_downzdim=1,
            ctn_prevdown=1,
        )
        ACE.ACEConversion().convert(args)

        assert popen_mock.called


class TestAceInterfaceACERegistration:
    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_register_call(self, popen_mock):
        args = Namespace(
            sa_output_folder="out_dir/",
            rca_orient_code="1",
            rca_hemi="2",
            rca_voxel_size=5,
            rca_allen_label="label",
            rca_allen_atlas="atlas",
            rca_side="side",
            rca_no_mosaic_fig=True,
            rca_olfactory_bulb=False,
            rca_skip_cor=True,
            rca_warp=True,
        )
        ACE.ACERegistration().register(args, "")

        assert popen_mock.called


class TestAceInterfaceRegistrationChecker:
    def test_ace_registration_get_cmd_no_conv(self):
        args = Namespace()
        with pytest.raises(FileNotFoundError) as e:
            ACE.RegistrationChecker.get_registration_cmd(args)

        assert "Converted nifti file not found!" in str(e)

    def test_ace_registration_get_cmd_return(self):
        args = Namespace(
            sa_output_folder="out_dir/",
            rca_orient_code="ALS",
            rca_hemi="2",
            rca_voxel_size=25,
            rca_allen_label="label",
            rca_allen_atlas="atlas",
            rca_side="side",
            rca_no_mosaic_fig=True,
            rca_olfactory_bulb=False,
            rca_skip_cor=True,
            rca_warp=True,
        )
        converted_nii_file = "dir/file.nii.gz"
        res = ACE.RegistrationChecker.get_registration_cmd(
            args, converted_nii_file=converted_nii_file
        )

        assert "/reg/miracl_reg_clar-allen.sh" in res
        assert "-i dir/file.nii.gz" in res

    @mock.patch(ACE_PATH + ".shutil.rmtree")
    @mock.patch(ACE_PATH + ".Path")
    def test_ace_registration_clear_reg_folders_no_reg(self, mock_path, mock_rmtree):
        mock_path.is_dir.return_value = False
        ACE.RegistrationChecker._clear_reg_folders(Path("reg_final/"))

        assert not mock_rmtree.called

    @mock.patch(ACE_PATH + ".shutil.rmtree")
    @mock.patch(ACE_PATH + ".Path")
    def test_ace_registration_clear_reg_folders_clear_reg(self, mock_path, mock_rmtree):
        mock_path.is_dir.return_value = True
        ACE.RegistrationChecker._clear_reg_folders(Path("reg_final/"))

        assert mock_rmtree.call_count == 2

    @mock.patch(ACE_PATH + ".Path.mkdir")
    def test_ace_registration_clear_reg_folders_mkdir(self, mock_mkdir):
        ACE.RegistrationChecker._clear_reg_folders(Path("reg_final/"))

        assert mock_mkdir.call_count == 2

    def test_ace_registration_check_registration_rerun(self):
        args = Namespace(
            rerun_registration=True,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    def test_ace_registration_check_registration_no_reg_dir(self, mock_is_dir):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_is_dir.side_effect = [False, True]

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    def test_ace_registration_check_registration_no_clar_dir(self, mock_is_dir):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_is_dir.side_effect = [True, False]

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    def test_ace_registration_check_registration_no_both_dir(self, mock_is_dir):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_is_dir.side_effect = [False, False]

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    @mock.patch(ACE_PATH + ".Path.is_file")
    def test_ace_registration_check_registration_no_reg_command(
        self, mock_is_file, mock_is_dir
    ):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")
        mock_is_dir.return_value = True
        mock_is_file.return_value = False

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    @mock.patch(ACE_PATH + ".Path.is_file")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_registration_check_registration_no_glob(
        self, mock_glob, mock_is_file, mock_is_dir
    ):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_glob.return_value = []
        mock_is_file.return_value = True
        mock_is_dir.return_value = True

        res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    @mock.patch(ACE_PATH + ".Path.is_file")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_registration_check_registration_open_call(
        self, mock_glob, mock_is_file, mock_is_dir
    ):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_glob.return_value = []
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        mock_glob.return_value = ["_clar.tif"]

        with mock.patch(
            ACE_PATH + ".open", mock_open(read_data="25\nALS")
        ) as open_mock:
            ACE.RegistrationChecker.check_registration(args, reg_folder)

        open_mock.assert_called_once_with(reg_folder / "reg_command.log", "r")

    @mock.patch(ACE_PATH + ".Path.is_dir")
    @mock.patch(ACE_PATH + ".Path.is_file")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_registration_check_registration_matching_command(
        self, mock_glob, mock_is_file, mock_is_dir
    ):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_glob.return_value = []
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        mock_glob.return_value = ["_clar.tif"]

        with mock.patch(
            ACE_PATH + ".open", mock_open(read_data="25\nALS")
        ) as open_mock:
            res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert not res

    @mock.patch(ACE_PATH + ".Path.is_dir")
    @mock.patch(ACE_PATH + ".Path.is_file")
    @mock.patch(ACE_PATH + ".Path.glob")
    def test_ace_registration_check_registration_not_matching_command(
        self, mock_glob, mock_is_file, mock_is_dir
    ):
        args = Namespace(
            rerun_registration=False,
            rca_voxel_size=25,
            rca_orient_code="ALS",
        )
        reg_folder = Path("reg_final/")

        mock_glob.return_value = []
        mock_is_file.return_value = True
        mock_is_dir.return_value = True
        mock_glob.return_value = ["_clar.tif"]

        with pytest.raises(ValueError) as e:
            with mock.patch(
                ACE_PATH + ".open", mock_open(read_data="10\nALS")
            ) as open_mock:
                res = ACE.RegistrationChecker.check_registration(args, reg_folder)

        assert (
            "Expected args (rca_voxel_size, rca_orient_code): ['25', 'ALS'] does not match received args: ['10', 'ALS']"
            in str(e)
        )


class TestAceInterfaceACEVoxelization:
    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_voxelize_call(self, popen_mock):
        args = Namespace(rca_voxel_size=5, ctn_down=1, sa_resolution=(1.4, 1.4, 5))
        ACE.ACEVoxelization().voxelize(args, "file.tif")

        assert popen_mock.called


class TestAceInterfaceACEWarping:
    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_warp_call(self, popen_mock):
        args = Namespace(
            rwc_seg_channel="x",
            rca_voxel_size=5,
        )
        ACE.ACEWarping().warp(args, "reg_final", "seg.nii.gz", "ort2std.txt")

        assert popen_mock.called


class TestAceInterfaceACEClusterwise:
    @mock.patch("miracl.flow.miracl_workflow_ace_stats.main")
    def test_ace_cluster_call(self, main_mock):
        args = Namespace(
            u_atlas_dir="allen",
        )
        ACE.ACEClusterwise().cluster(
            args,
            "sa_output_dir",
        )

        assert main_mock.called


class TestAceInterfaceACECorrelation:
    @mock.patch("miracl.flow.miracl_workflow_ace_correlation.main")
    def test_ace_correlate_call(self, main_mock):
        args = Namespace(
            u_atlas_dir="allen",
        )
        ACE.ACECorrelation().correlate(
            args,
            "corr_final",
            0.05,
            0.05,
            0.05,
        )

        assert main_mock.called


class TestAceInterfaceACEHeatmap:
    @mock.patch(ACE_PATH + ".subprocess.Popen")
    def test_ace_heatmap_call(self, popen_mock):
        ACE.ACEHeatmap().create_heatmap("heatmap_cmd")

        assert popen_mock.called


class TestAceInterfaceACEWorkflows:
    def single_decorator(function):
        @functools.wraps(function)
        @mock.patch(ACE_PATH + ".RegistrationChecker")
        @mock.patch(ACE_PATH + ".GetConverterdNifti.get_nifti_file")
        @mock.patch(ACE_PATH + ".ACERegistration.register")
        @mock.patch(ACE_PATH + ".ACEConversion.convert")
        @mock.patch(ACE_PATH + ".ACESegmentation.segment")
        @mock.patch(ACE_PATH + ".FolderCreator.create_folder")
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    comparison_args = Namespace(
        ctn_down=5,
        rca_voxel_size=10,
        sa_output_folder="sa_output_dir/",
        overwrite=True,
        control=["ctrl_dir/", "ctrl_dir/subj1/cells"],
        experiment=["exp_dir/", "exp_dir/subj1/cells"],
        rca_orient_code="1",
        sh_sagittal="1",
        sh_coronal="2",
        sh_axial="3",
        sh_figure_dim="5",
    )

    comparison_folder_creator_side_effect = [
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "seg_final",
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final",
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "reg_final",
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "vox_final",
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "warp_final",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "seg_final",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "reg_final",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "vox_final",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "warp_final",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "seg_final",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "reg_final",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "vox_final",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "warp_final",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "seg_final",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "reg_final",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "vox_final",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "warp_final",
        Path("sa_output_dir/") / "clust_final",
        Path("sa_output_dir/") / "heat_final",
        Path("sa_output_dir/") / "corr_final",
    ]

    mock_nifti_side_effect = [
        Path("ctrl_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final"
        / "file.nii.gz",
        Path("ctrl_dir/subj2/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final"
        / "file.nii.gz",
        Path("exp_dir/subj1/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final"
        / "file.nii.gz",
        Path("exp_dir/subj10/")
        / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
        / "conv_final"
        / "file.nii.gz",
    ]

    mock_warping_req_side_effect = [
        (
            Path("ctrl_dir/subj1/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz",
            Path("ctrl_dir/subj1/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt",
        ),
        (
            Path("ctrl_dir/subj2/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz",
            Path("ctrl_dir/subj2/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt",
        ),
        (
            Path("exp_dir/subj1/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz",
            Path("exp_dir/subj1/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt",
        ),
        (
            Path("exp_dir/subj10/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz",
            Path("exp_dir/subj10/")
            / f"final_ctn_down={comparison_args.ctn_down}_rca_voxel_size={comparison_args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt",
        ),
    ]

    mock_corr_input_side_effect = [
        Path("sa_output_dir/") / "clust_final" / "diff_mean.nii.gz",
        Path("sa_output_dir/") / "clust_final" / "f_obs.nii.gz",
        Path("sa_output_dir/") / "clust_final" / "p_values.nii.gz",
    ]

    def combined_decorator(function):
        @functools.wraps(function)
        @mock.patch(ACE_PATH + ".RegistrationChecker")
        @mock.patch(ACE_PATH + ".ACEHeatmap.create_heatmap")
        @mock.patch(ACE_PATH + ".ConstructHeatmapCmd.construct_final_heatmap_cmd")
        @mock.patch(ACE_PATH + ".ConstructHeatmapCmd.test_none_args")
        @mock.patch(ACE_PATH + ".ACECorrelation.correlate")
        @mock.patch(ACE_PATH + ".GetCorrInput.check_corr_input_exists")
        @mock.patch(ACE_PATH + ".ACEClusterwise.cluster")
        @mock.patch(ACE_PATH + ".ACEWarping.warp")
        @mock.patch(ACE_PATH + ".GetVoxSegTif.create_orientation_file")
        @mock.patch(ACE_PATH + ".GetVoxSegTif.check_warping_requirements")
        @mock.patch(ACE_PATH + ".ACEVoxelization.voxelize")
        @mock.patch(ACE_PATH + ".StackTiffs.stacking")
        @mock.patch(ACE_PATH + ".StackTiffs.check_folders")
        @mock.patch(ACE_PATH + ".ACERegistration.register")
        @mock.patch(ACE_PATH + ".GetConverterdNifti.get_nifti_file")
        @mock.patch(ACE_PATH + ".ACEConversion.convert")
        @mock.patch(ACE_PATH + ".ACESegmentation.segment")
        @mock.patch(ACE_PATH + ".FolderCreator.create_folder")
        @mock.patch(ACE_PATH + ".Path.is_dir")
        @mock.patch(ACE_PATH + ".Path.iterdir")
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    @mock.patch(ACE_PATH + ".ACEWorkflows._execute_single_workflow")
    def test_ace_execute_workflow_single_call(self, mock_method):
        args = Namespace(
            single="dir/",
        )
        ACE.ACEWorkflows(
            None, None, None, None, None, None, None, None
        ).execute_workflow(args)

        assert mock_method.called_once_with(args)

    @mock.patch(ACE_PATH + ".ACEWorkflows._execute_comparison_workflow")
    def test_ace_execute_workflow_comparison_call(self, mock_method):
        args = Namespace(
            single=None,
            control="ctrl_dir/",
            experiment="exp_dir/",
        )
        ACE.ACEWorkflows(
            None, None, None, None, None, None, None, None
        ).execute_workflow(args)

        assert mock_method.called_once_with(args)

    def test_ace_execute_workflow_error(Self):
        args = Namespace(
            single=None,
            control=None,
            experiment=None,
        )
        with pytest.raises(ValueError) as e:
            ACE.ACEWorkflows(
                None, None, None, None, None, None, None, None
            ).execute_workflow(args)

        assert (
            "Must specify either (-s/--single) or (-c/--control and -e/--experiment) in args."
            in str(e)
        )

    @single_decorator
    def test_ace_single_workflow_create_folder(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        assert mock_folder_creator.call_count == 3
        assert mock_folder_creator.call_args_list[0][0] == (
            f"sa_output_dir/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}",
            "seg_final",
        )
        assert mock_folder_creator.call_args_list[1][0] == (
            f"sa_output_dir/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}",
            "conv_final",
        )
        assert mock_folder_creator.call_args_list[2][0] == (
            f"sa_output_dir/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}",
            "reg_final",
        )

    @single_decorator
    def test_ace_single_workflow_return(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        res = ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        assert (
            res
            == "sa_output_dir/"
            + f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
        )

    @single_decorator
    def test_ace_single_workflow_segment_call(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        mock_segment.assert_called_once_with(args)

    @single_decorator
    def test_ace_single_workflow_convert_call(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        mock_convert.assert_called_once_with(args)

    @single_decorator
    def test_ace_single_workflow_get_nifti_call(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        mock_nifti.assert_called_once_with(Path("sa_output_dir/") / "conv_final")

    @single_decorator
    def test_ace_single_workflow_register_call(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")
        mock_registration_checker.get_registration_cmd.return_value = (
            "miracl reg clar_allen args"
        )

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        mock_register.assert_called_once_with(args, "miracl reg clar_allen args")

    @single_decorator
    def test_ace_single_workflow_check_get_reg_cmd_call(
        self,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_register,
        mock_nifti,
        mock_registration_checker,
    ):
        args = Namespace(
            ctn_down=5,
            rca_voxel_size=10,
            sa_output_folder="sa_output_dir/",
            rca_orient_code=(1.4, 1.4, 5),
        )
        mock_folder_creator.side_effect = [
            Path("sa_output_dir/") / "seg_final",
            Path("sa_output_dir/") / "conv_final",
            Path("sa_output_dir/") / "reg_final",
        ]
        mock_nifti.return_value = Path("dir/file.nii")

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_single_workflow(args)

        mock_registration_checker.get_registration_cmd.assert_called_once_with(
            args, converted_nii_file=Path("dir/file.nii")
        )

    @combined_decorator
    def test_ace_comparison_workflow_folder_creator(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_folder_creator.call_count == 23

    @combined_decorator
    def test_ace_comparison_workflow_segment_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_segment.call_count == 4

    @combined_decorator
    def test_ace_comparison_workflow_convert_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_convert.call_count == 4

    @combined_decorator
    def test_ace_comparison_workflow_nifti_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_nifti.call_count == 4
        assert (
            mock_nifti.call_args_list[0][0][0]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "conv_final"
        )
        assert (
            mock_nifti.call_args_list[1][0][0]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "conv_final"
        )
        assert (
            mock_nifti.call_args_list[2][0][0]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "conv_final"
        )
        assert (
            mock_nifti.call_args_list[3][0][0]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "conv_final"
        )

    @combined_decorator
    def test_ace_comparison_workflow_check_registration_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        mock_registration_checker.check_registration.call_args_list[0][0][1] == Path(
            "ctrl_dir/subj1/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "reg_final"
        mock_registration_checker.check_registration.call_args_list[1][0][1] == Path(
            "ctrl_dir/subj2/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "reg_final"
        mock_registration_checker.check_registration.call_args_list[2][0][1] == Path(
            "exp_dir/subj1/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "reg_final"
        mock_registration_checker.check_registration.call_args_list[3][0][1] == Path(
            "exp_dir/subj10/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "reg_final"

    @combined_decorator
    def test_ace_comparison_workflow_get_reg_cmd_no_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        mock_registration_checker.check_registration.return_value = False

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert not mock_registration_checker.get_registration_cmd.called

    @combined_decorator
    def test_ace_comparison_workflow_get_reg_cmd_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        mock_registration_checker.check_registration.return_value = True

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        mock_registration_checker.get_registration_cmd.call_args_list[0][1][
            "converted_nii_file"
        ] == Path(
            "ctrl_dir/subj1/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "conv_final/file.nii.gz"
        mock_registration_checker.get_registration_cmd.call_args_list[1][1][
            "converted_nii_file"
        ] == Path(
            "ctrl_dir/subj2/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "conv_final/file.nii.gz"
        mock_registration_checker.get_registration_cmd.call_args_list[2][1][
            "converted_nii_file"
        ] == Path(
            "exp_dir/subj1/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "conv_final/file.nii.gz"
        mock_registration_checker.get_registration_cmd.call_args_list[3][1][
            "converted_nii_file"
        ] == Path(
            "exp_dir/subj10/"
        ) / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}" / "conv_final/file.nii.gz"

    @combined_decorator
    def test_ace_comparison_workflow_register_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        mock_registration_checker.check_registration.return_value = True

        mock_registration_checker.get_registration_cmd.side_effect = [
            "miracl reg clar_allen args1",
            "miracl reg clar_allen args2",
            "miracl reg clar_allen args3",
            "miracl reg clar_allen args4",
        ]

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_register.call_args_list[0][0][1] == "miracl reg clar_allen args1"
        assert mock_register.call_args_list[1][0][1] == "miracl reg clar_allen args2"
        assert mock_register.call_args_list[2][0][1] == "miracl reg clar_allen args3"
        assert mock_register.call_args_list[3][0][1] == "miracl reg clar_allen args4"

    @combined_decorator
    def test_ace_comparison_workflow_register_no_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = False

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        mock_registration_checker.check_registration.return_value = False

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert not mock_register.called

    @combined_decorator
    def test_ace_comparison_workflow_check_folders_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_check_folders.call_args_list[0][0][0]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_check_folders.call_args_list[0][0][1]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_check_folders.call_args_list[1][0][0]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_check_folders.call_args_list[1][0][1]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_check_folders.call_args_list[2][0][0]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_check_folders.call_args_list[2][0][1]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_check_folders.call_args_list[3][0][0]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_check_folders.call_args_list[3][0][1]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )

    @combined_decorator
    def test_ace_comparison_workflow_stacking_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_stacking.call_args_list[0][0][0]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_stacking.call_args_list[0][0][1]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_stacking.call_args_list[0][0][2]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "seg_final"
        )
        assert (
            mock_stacking.call_args_list[1][0][0]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_stacking.call_args_list[1][0][1]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_stacking.call_args_list[1][0][2]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "seg_final"
        )
        assert (
            mock_stacking.call_args_list[2][0][0]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_stacking.call_args_list[2][0][1]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_stacking.call_args_list[2][0][2]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "seg_final"
        )
        assert (
            mock_stacking.call_args_list[3][0][0]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stack_seg_tifs.ijm"
        )
        assert (
            mock_stacking.call_args_list[3][0][1]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_stacking.call_args_list[3][0][2]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "seg_final"
        )

    @combined_decorator
    def test_ace_comparison_workflow_voxelize_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_voxelize.call_args_list[0][0][1]
            == Path(
                f"ctrl_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_voxelize.call_args_list[1][0][1]
            == Path(
                f"ctrl_dir/subj2/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_voxelize.call_args_list[2][0][1]
            == Path(
                f"exp_dir/subj1/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )
        assert (
            mock_voxelize.call_args_list[3][0][1]
            == Path(
                f"exp_dir/subj10/final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}/"
            )
            / "vox_final"
            / "stacked_seg_tif.tif"
        )

    @combined_decorator
    def test_ace_comparison_workflow_check_warping_inputs(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_warping_req.call_args_list[0][0] == (
            Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "vox_final",
            Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final",
        )
        assert mock_warping_req.call_args_list[1][0] == (
            Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "vox_final",
            Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final",
        )
        assert mock_warping_req.call_args_list[2][0] == (
            Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "vox_final",
            Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final",
        )
        assert mock_warping_req.call_args_list[3][0] == (
            Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "vox_final",
            Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final",
        )

    @combined_decorator
    def test_ace_comparison_workflow_orientation_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_orientation_file.call_args_list[0][0][0]
            == Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_orientation_file.call_args_list[0][0][1]
            == Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
        )
        assert mock_orientation_file.call_args_list[0][0][2] == args.rca_orient_code
        assert (
            mock_orientation_file.call_args_list[1][0][0]
            == Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_orientation_file.call_args_list[1][0][1]
            == Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
        )
        assert mock_orientation_file.call_args_list[1][0][2] == args.rca_orient_code
        assert (
            mock_orientation_file.call_args_list[2][0][0]
            == Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_orientation_file.call_args_list[2][0][1]
            == Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
        )
        assert mock_orientation_file.call_args_list[2][0][2] == args.rca_orient_code
        assert (
            mock_orientation_file.call_args_list[3][0][0]
            == Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_orientation_file.call_args_list[3][0][1]
            == Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
        )
        assert mock_orientation_file.call_args_list[3][0][2] == args.rca_orient_code

    @combined_decorator
    def test_ace_comparison_workflow_warp_call(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)
        args.overwrite = True

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_warp.call_args_list[0][0][1]
            == Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "clar_allen_reg"
        )
        assert (
            mock_warp.call_args_list[0][0][2]
            == Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz"
        )
        assert (
            mock_warp.call_args_list[0][0][3]
            == Path("ctrl_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_warp.call_args_list[1][0][1]
            == Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "clar_allen_reg"
        )
        assert (
            mock_warp.call_args_list[1][0][2]
            == Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz"
        )
        assert (
            mock_warp.call_args_list[1][0][3]
            == Path("ctrl_dir/subj2/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_warp.call_args_list[2][0][1]
            == Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "clar_allen_reg"
        )
        assert (
            mock_warp.call_args_list[2][0][2]
            == Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz"
        )
        assert (
            mock_warp.call_args_list[2][0][3]
            == Path("exp_dir/subj1/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )
        assert (
            mock_warp.call_args_list[3][0][1]
            == Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "clar_allen_reg"
        )
        assert (
            mock_warp.call_args_list[3][0][2]
            == Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "voxelized_seg_seg.nii.gz"
        )
        assert (
            mock_warp.call_args_list[3][0][3]
            == Path("exp_dir/subj10/")
            / f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
            / "warp_final"
            / "ort2std.txt"
        )

    @combined_decorator
    def test_ace_comparison_workflow_cluster(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_cluster.call_args_list[0][0][1]
            == Path("sa_output_dir/") / "clust_final"
        )

    @combined_decorator
    def test_ace_comparison_workflow_check_corr_input(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_corr_input.call_args_list[0][0] == (
            Path("sa_output_dir/") / "clust_final",
            "diff_mean.nii.gz",
        )
        assert mock_corr_input.call_args_list[1][0] == (
            Path("sa_output_dir/") / "clust_final",
            "f_obs.nii.gz",
        )
        assert mock_corr_input.call_args_list[2][0] == (
            Path("sa_output_dir/") / "clust_final",
            "p_values.nii.gz",
        )

    @combined_decorator
    def test_ace_comparison_workflow_correlate(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_correlate.call_args_list[0][0][1]
            == Path("sa_output_dir/") / "corr_final"
        )
        assert (
            mock_correlate.call_args_list[0][0][2]
            == Path("sa_output_dir/") / "clust_final" / "p_values.nii.gz"
        )
        assert (
            mock_correlate.call_args_list[0][0][3]
            == Path("sa_output_dir/") / "clust_final" / "f_obs.nii.gz"
        )
        assert (
            mock_correlate.call_args_list[0][0][4]
            == Path("sa_output_dir/") / "clust_final" / "diff_mean.nii.gz"
        )

    @combined_decorator
    def test_ace_comparison_workflow_test_none_args(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = ""

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert mock_test_none_args.call_args_list[0][0] == ("1", "2", "3", "5")

    @combined_decorator
    def test_ace_comparison_workflow_final_heatmap_cmd(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = (
            "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 "
        )

        mock_final_heatmap_cmd.return_value = ""

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        assert (
            mock_final_heatmap_cmd.call_args_list[0][0][1]
            == Path("sa_output_dir/") / "heat_final"
        )
        assert (
            mock_final_heatmap_cmd.call_args_list[0][0][2]
            == "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 "
        )

    @combined_decorator
    def test_ace_comparison_workflow_create_heatmap(
        self,
        mock_iterdir,
        mock_is_dir,
        mock_folder_creator,
        mock_segment,
        mock_convert,
        mock_nifti,
        mock_register,
        mock_check_folders,
        mock_stacking,
        mock_voxelize,
        mock_warping_req,
        mock_orientation_file,
        mock_warp,
        mock_cluster,
        mock_corr_input,
        mock_correlate,
        mock_test_none_args,
        mock_final_heatmap_cmd,
        mock_create_heatmap,
        mock_registration_checker,
    ):
        args = copy.deepcopy(self.comparison_args)

        mock_is_dir.return_value = True
        mock_iterdir.side_effect = [
            [Path("ctrl_dir/subj1/"), Path("ctrl_dir/subj2/")],
            [Path("exp_dir/subj1/"), Path("exp_dir/subj10/")],
        ]

        mock_folder_creator.side_effect = self.comparison_folder_creator_side_effect
        mock_nifti.side_effect = self.mock_nifti_side_effect

        mock_warping_req.side_effect = self.mock_warping_req_side_effect

        mock_corr_input.side_effect = self.mock_corr_input_side_effect

        mock_test_none_args.return_value = (
            "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 "
        )

        mock_final_heatmap_cmd.return_value = "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 -g1 ctrl_dir/ ctrl_dir/subj1/cells -g2 exp_dir/ exp_dir/subj1/cells"

        ACE.ACEWorkflows(
            ACE.ACESegmentation(),
            ACE.ACEConversion(),
            ACE.ACERegistration(),
            ACE.ACEVoxelization(),
            ACE.ACEWarping(),
            ACE.ACEClusterwise(),
            ACE.ACECorrelation(),
            ACE.ACEHeatmap(),
        )._execute_comparison_workflow(args)

        mock_create_heatmap.assert_called_once_with(
            "miracl stats heatmap_group -s 1 2 3 4 5 -f 10 10 -g1 ctrl_dir/ ctrl_dir/subj1/cells -g2 exp_dir/ exp_dir/subj1/cells"
        )


class TestAceInterfaceMain:
    def decorator(function):
        @functools.wraps(function)
        @mock.patch(ACE_PATH + ".ACEWorkflows")
        @mock.patch(ACE_PATH + ".ACEHeatmap")
        @mock.patch(ACE_PATH + ".ACECorrelation")
        @mock.patch(ACE_PATH + ".ACEClusterwise")
        @mock.patch(ACE_PATH + ".ACEWarping")
        @mock.patch(ACE_PATH + ".ACEVoxelization")
        @mock.patch(ACE_PATH + ".ACERegistration")
        @mock.patch(ACE_PATH + ".ACEConversion")
        @mock.patch(ACE_PATH + ".ACESegmentation")
        @mock.patch(ACE_PATH + ".miracl_workflow_ace_parser.ACEWorkflowParser")
        def wrapper(*args, **kwargs):
            return function(*args, **kwargs)

        return wrapper

    @decorator
    def test_ace_main_parser_creation(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        ACE.main()
        assert mock_parser.call_count == 1

    @decorator
    def test_ace_main_parser_call(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_parser().parse_args.call_count == 1

    @decorator
    def test_ace_main_segmentation(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_segmentation.call_count == 1

    @decorator
    def test_ace_main_conversion(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_conversion.call_count == 1

    @decorator
    def test_ace_main_registration(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_registration.call_count == 1

    @decorator
    def test_ace_main_voxelization(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_voxelization.call_count == 1

    @decorator
    def test_ace_main_warping(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_warping.call_count == 1

    @decorator
    def test_ace_main_clusterwise(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_clusterwise.call_count == 1

    @decorator
    def test_ace_main_correlation(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_correlation.call_count == 1

    @decorator
    def test_ace_main_heatmap(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_heatmap.call_count == 1

    @decorator
    def test_ace_main_workflow_creation(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_workflows.called_once_with(
            mock_segmentation(),
            mock_conversion(),
            mock_registration(),
            mock_voxelization(),
            mock_warping(),
            mock_clusterwise(),
            mock_correlation(),
            mock_heatmap(),
        )

    @decorator
    def test_ace_main_execute_workflow_call(
        self,
        mock_parser,
        mock_segmentation,
        mock_conversion,
        mock_registration,
        mock_voxelization,
        mock_warping,
        mock_clusterwise,
        mock_correlation,
        mock_heatmap,
        mock_workflows,
    ):
        mock_parser().parse_args.return_value = Namespace()
        ACE.main()

        assert mock_workflows().execute_workflow.call_count == 1
