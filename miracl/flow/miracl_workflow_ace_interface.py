import argparse
import os
import pathlib
import shutil
import subprocess
import typing
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from miracl import miracl_logger
from miracl.flow import (miracl_workflow_ace_correlation,
                         miracl_workflow_ace_parser, miracl_workflow_ace_stats)
from miracl.seg import ace_interface

logger = miracl_logger.logger

MIRACL_HOME = Path(os.environ["MIRACL_HOME"])


# DECLARE ABSTRACT METHODS #
class Segmentation(ABC):
    @abstractmethod
    def segment(self, args):
        pass


class Conversion(ABC):
    @abstractmethod
    def convert(self, args):
        pass


class Registration(ABC):
    @abstractmethod
    def register(self, args, **kwargs):
        pass


class Voxelization(ABC):
    @abstractmethod
    def voxelize(self, args, stacked_tif):
        pass


class Warping(ABC):
    @abstractmethod
    def warp(self, args, stacked_tif):
        pass


class Clusterwise(ABC):
    @abstractmethod
    def cluster(self, args, output_dir_arg):
        pass


class Correlation(ABC):
    @abstractmethod
    def correlate(self, args, corr_output_folder, p_value, f_obs, mean_diff):
        pass


class Heatmap(ABC):
    @abstractmethod
    def create_heatmap(self, heatmap_cmd):
        pass


# DECLARE CONCRETE METHODS #
class ACESegmentation(Segmentation):
    """ACE Segmentation module used for segmenting the input images.

    :param Segmentation: base abstract class for segmentation
    :type Segmentation: ABC
    """
    def segment(
        self,
        args: argparse.Namespace
    ):
        """Main method for segmentation module. Calls the `miracl seg ace` module.

        :param args: command line arguments needed for MIRACL ACE seg module.
        :type args: argparse.Namespace
        """
        print("  segmenting...")
        logger.debug("Calling ace_interface fn here")
        logger.debug(f"Example args: {args.sa_model_type}")
        ace_interface.main(args=args)


class ACEConversion(Conversion):
    """ACE Conversion module used for converting the segmented tif files to nifti.

    :param Conversion: base abstract class for conversion
    :type Conversion: ABC
    """
    def convert(
        self,
        args: argparse.Namespace
    ):
        """Main method for conversion module. Calls `miracl conv tiff_nii` module.

        :param args: command line arguments needed for MIRACL conv module.
        :type args: argparse.Namespace
        """
        print("  converting...")
        conv_cmd = f"python {MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
        --folder {args.single} \
        --work_dir {args.sa_output_folder} \
        --down {args.ctn_down} \
        --channum {args.ctn_channum} \
        --chanprefix {args.ctn_chanprefix} \
        --channame {args.ctn_channame} \
        --outnii {args.ctn_outnii} \
        --resx {args.ctn_resx} \
        --resz {args.ctn_resz} \
        --center {' '.join(map(str, args.ctn_center))} \
        --downzdim {args.ctn_downzdim} \
        --prevdown {args.ctn_prevdown}"
        subprocess.Popen(conv_cmd, shell=True).wait()
        logger.debug("Calling conversion fn here")
        logger.debug(f"Example args: {args.ctn_down}")


class ACERegistration(Registration):
    """ACE Registration module used for registering the converted nifti files to the Allen atlas.

    :param Registration: base abstract class for registration
    :type Registration: ABC
    """
    def register(
        self,
        args: argparse.Namespace,
        **kwargs
    ):
        """Main method for registration module. Calls `miracl reg clar_allen` module.

        :param args: command line arguments needed for MIRACL reg module.
        :type args: argparse.Namespace
        :raises FileNotFoundError: if no kwarg for 'depndent_folder' is passed
        :raises FileNotFoundError: if no kwarg for 'converted_nii_file' is passed
        """
        print("  registering...")
        if "dependent_folder" in kwargs:
            ace_flow_conv_output_folder = kwargs["dependent_folder"]
        else:
            raise FileNotFoundError("Output folder path variable not found!")

        if "converted_nii_file" in kwargs:
            converted_nii_file = kwargs["converted_nii_file"]
        else:
            raise FileNotFoundError("Converted nifti file not found!")

        reg_cmd = f"{MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        -i {converted_nii_file} \
        -r {args.sa_output_folder} \
        -o {args.rca_orient_code} \
        -m {args.rca_hemi} \
        -v {args.rca_voxel_size} \
        -l {args.rca_allen_label} \
        -a {args.rca_allen_atlas} \
        -s {args.rca_side} \
        -f {args.rca_no_mosaic_fig} \
        -b {args.rca_olfactory_bulb} \
        -p {args.rca_skip_cor} \
        -w {args.rca_warp}"
        subprocess.Popen(reg_cmd, shell=True).wait()
        logger.debug("Calling registration fn here")
        logger.debug(f"Example args: {args.rca_allen_atlas}")
        logger.debug(f"dependent_folder: {ace_flow_conv_output_folder}")
        logger.debug(f"nifti file: {converted_nii_file}")


class ACEVoxelization(Voxelization):
    """ACE Voxelization module used for voxelizing the segmented tif files.

    :param Voxelization: base abstract class for voxelization
    :type Voxelization: ABC
    """
    def voxelize(
        self,
        args: argparse.Namespace,
        stacked_tif: pathlib.Path
    ):
        """Main method for voxelization module. Calls `miracl seg voxelize` module.

        :param args: command line arguments needed for MIRACL seg module.
        :type args: argparse.Namespace
        :param stacked_tif: path to the stacked tif file ('stacked_seg_tif.tif')
        :type stacked_tif: pathlib.Path
        """
        print("  voxelizing stacked tif...")
        vox_cmd = f"miracl seg voxelize \
        --seg {stacked_tif} \
        --res {args.rca_voxel_size} \
        --down {args.ctn_down}"
        # -vx {args.} \
        # -vz {args.}"
        subprocess.Popen(vox_cmd, shell=True).wait()
        logger.debug("Calling voxelization fn here")
        logger.debug(f"ctn_down in voxelization: {args.ctn_down}")


class ACEWarping(Warping):
    """ACE Warping module used for warping the voxelized segmented tif files.

    :param Warping: base abstract class for warping
    :type Warping: ABC
    """
    def warp(
        self,
        args: argparse.Namespace,
        ace_flow_reg_output_folder: pathlib.Path,
        voxelized_segmented_tif: pathlib.Path,
        orientation_file: pathlib.Path,
    ):
        """Main method for warping module. Calls `miracl reg warp_clar` module.

        :param args: command line arguments needed for MIRACL reg module.
        :type args: argparse.Namespace
        :param ace_flow_reg_output_folder: path to the registration output folder ('clar_allen_reg')
        :type ace_flow_reg_output_folder: pathlib.Path
        :param voxelized_segmented_tif: path to the voxelized segmented tif file ('warp_final/voxelized_seg_*.nii.gz')
        :type voxelized_segmented_tif: pathlib.Path
        :param orientation_file: path to the orientation file ('warp_final/ort2std.txt')
        :type orientation_file: pathlib.Path
        """
        print("  warping stacked tif...")
        warp_cmd = f"miracl reg warp_clar \
                -r {ace_flow_reg_output_folder} \
                -i {voxelized_segmented_tif} \
                -o {orientation_file} \
                -s {args.rwc_seg_channel} \
                -v {args.rca_voxel_size}"
        subprocess.Popen(warp_cmd, shell=True).wait()
        logger.debug("Calling warping here")
        logger.debug(f"orientation_file: {orientation_file}")


class ACEClusterwise(Clusterwise):
    """ACE Clusterwise module used for performing clusterwise comparison.

    :param Clusterwise: base abstract class for clusterwise comparison
    :type Clusterwise: ABC
    """
    def cluster(
        self,
        args: argparse.Namespace,
        output_dir_arg: pathlib.Path
    ):
        """Main method for clusterwise comparison module. Calls `miracl stats ace` module.

        :param args: command line arguments needed for MIRACL stats module.
        :type args: argparse.Namespace
        :param output_dir_arg: path to the output directory ('clust_final/')
        :type output_dir_arg: pathlib.Path
        """
        print("  clusterwise comparison...")
        miracl_workflow_ace_stats.main(args, output_dir_arg)
        logger.debug("Calling clusterwise comparison fn here")
        logger.debug(f"Atlas dir arg: {args.u_atlas_dir}")


class ACECorrelation(Correlation):
    """ACE Correlation module used for performing correlation analysis.

    :param Correlation: base abstract class for correlation module
    :type Correlation: ABC
    """
    def correlate(
        self,
        args: argparse.Namespace,
        corr_output_folder: pathlib.Path,
        p_value: pathlib.Path,
        f_obs: pathlib.Path,
        mean_diff: pathlib.Path
    ):
        """Main method for correlation module. Module is not directly 
        callable through MIRACL CLI.

        :param args: arguments needed for correlation module.
        :type args: argparse.Namespace
        :param corr_output_folder: path to the correlation output folder ('corr_final/')
        :type corr_output_folder: pathlib.Path
        :param p_value: path to the p value file ('clust_final/diff_mean.nii.gz')
        :type p_value: pathlib.Path
        :param f_obs: path to the f obs file ('clust_final/f_obs.nii.gz')
        :type f_obs: pathlib.Path
        :param mean_diff: path to the mean diff file ('clust_final/p_values.nii.gz')
        :type mean_diff: pathlib.Path
        """
        print("  correlating...")
        miracl_workflow_ace_correlation.main(
            args, corr_output_folder, p_value, f_obs, mean_diff
        )
        logger.debug("Calling correlation fn here")
        logger.debug(f"Atlas dir arg: {args.u_atlas_dir}")


class ACEHeatmap(Heatmap):
    """ACE Heatmap module used for creating heatmaps.

    :param Heatmap: base abstract class for heatmap module
    :type Heatmap: ABC
    """
    def create_heatmap(
        self,
        heatmap_cmd: str
    ):
        """Main method for heatmap module. Calls `miracl stats heatmap_group` module.

        :param heatmap_cmd: miracl stats heatmap_group command with args.
        :type heatmap_cmd: str
        """
        print("  creating heatmaps...")
        subprocess.Popen(heatmap_cmd, shell=True).wait()
        logger.debug("Calling heatmap fn here")
        logger.debug(f"heatmap_cmd: {heatmap_cmd}")


class ACEWorkflows:
    """Class used for executing each step in ACE workflow.

    :param segmentation: Module to be used for segmentation
    :type segmentation: Segmentation
    :param conversion: Module to be used for conversion
    :type conversion: Conversion
    :param registration: Module to be used for registration
    :type registration: Registration
    :param voxelization: Module to be used for voxelization
    :type voxelization: Voxelization
    :param warping: Module to be used for warping
    :type warping: Warping
    :param clustering: Module to be used for clusterwise comparison
    :type clustering: Clusterwise
    :param correlation: Module to be used for correlation
    :type correlation: Correlation
    :param heatmap: Module to be used for heatmap
    :type heatmap: Heatmap
    """
    def __init__(
        self,
        segmentation: Segmentation,
        conversion: Conversion,
        registration: Registration,
        voxelization: Voxelization,
        warping: Warping,
        clustering: Clusterwise,
        correlation: Correlation,
        heatmap: Heatmap,
    ):
        """Constructor method
        """
        self.segmentation = segmentation
        self.conversion = conversion
        self.registration = registration
        self.voxelization = voxelization
        self.warping = warping
        self.clustering = clustering
        self.correlation = correlation
        self.heatmap = heatmap

    def execute_workflow(
        self,
        args: argparse.Namespace, 
        **kwargs
    ):
        """Method that handles logic for single or comparison workflow.

        :param args: command line arguments from ACE parser
        :type args: argparse.Namespace
        :raises ValueError: If insufficient arguments are passed to handle single 
            or comparison workflow
        """

        # check for single or multi in the args
        if args.single:
            self._execute_single_workflow(args, **kwargs)
        elif args.control and args.experiment:
            self._execute_comparison_workflow(args, **kwargs)
        else:
            raise ValueError("Must specify either (-s/--single) or (-c/--control and -e/--experiment) in args.")
        
    def _execute_single_workflow(
        self,
        args: argparse.Namespace,
        **kwargs
    ) -> pathlib.Path:
        """Private method for executing the single workflow.

        :param args: command line arguments needed for single workflow
        :type args: argparse.Namespace
        :return: path to the final output folder at the same level as the 
            directory containing input tiff files
        :rtype: pathlib.Path
        """
        
        final_folder = f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"
        args.sa_output_folder = str((Path(args.sa_output_folder) / final_folder))

        ace_flow_seg_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "seg_final",
        )
        ace_flow_conv_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "conv_final"
        )
        ace_flow_reg_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "reg_final"
        )

        self.segmentation.segment(args)
        self.conversion.convert(args)
        converted_nii_file = GetConverterdNifti.get_nifti_file(
            ace_flow_conv_output_folder
        )
        self.registration.register(
            args,
            dependent_folder=ace_flow_conv_output_folder,
            converted_nii_file=converted_nii_file,
        )

        return args.sa_output_folder
    
    def _execute_comparison_workflow(
        self,
        args: argparse.Namespace,
        **kwargs
    ):
        """Private method for executing the comparison workflow.

        :param args: arguments needed for comparison workflow
        :type args: argparse.Namespace
        """

        overall_save_folder = args.sa_output_folder

        args_dict = vars(args)

        per_subject_final_folder = f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"

        nifti_save_location = {}

        CheckOverwriteFlag.validate_args(
            args.overwrite,
            per_subject_final_folder,
            args.experiment,
            args.control,
            args.sa_output_folder,
        )

        for type_ in ['control', 'experiment']:

            tiff_template = Path(args_dict[type_][1])
            base_dir = Path(args_dict[type_][0])

            tiff_extension = Path(*tiff_template.relative_to(base_dir).parts[1:])
            subject_folders = [dir_ for dir_ in base_dir.iterdir() if dir_.is_dir()]

            for subject in subject_folders:

                save_folder = (
                    (subject / tiff_extension).parent
                    / per_subject_final_folder
                ).as_posix()

                args.sa_output_folder = save_folder

                ace_flow_seg_output_folder = FolderCreator.create_folder(
                    args.sa_output_folder, "seg_final"
                )
                ace_flow_conv_output_folder = FolderCreator.create_folder(
                    args.sa_output_folder, "conv_final"
                )
                ace_flow_reg_output_folder = FolderCreator.create_folder(
                    args.sa_output_folder, "reg_final"
                )
                ace_flow_vox_output_folder = FolderCreator.create_folder(
                    args.sa_output_folder, "vox_final"
                )
                ace_flow_warp_output_folder = FolderCreator.create_folder(
                    args.sa_output_folder, "warp_final"
                )

                args.single = base_dir / subject.stem / tiff_extension

                if args.overwrite:
                    self.segmentation.segment(args)
                    self.conversion.convert(args)
                    converted_nii_file = GetConverterdNifti.get_nifti_file(
                        ace_flow_conv_output_folder
                    )
                    self.registration.register(
                        args,
                        dependent_folder=ace_flow_conv_output_folder,
                        converted_nii_file=converted_nii_file,
                    )
                    # Stack tiff files for use in voxelization method
                    fiji_file = ace_flow_vox_output_folder / "stack_seg_tifs.ijm"
                    stacked_tif = ace_flow_vox_output_folder / "stacked_seg_tif.tif"
                    StackTiffs.check_folders(fiji_file, stacked_tif)
                    StackTiffs.stacking(fiji_file, stacked_tif, ace_flow_seg_output_folder)
                    self.voxelization.voxelize(args, stacked_tif)
                
                # need to do this step regardless of overwrite or not
                (
                    voxelized_segmented_tif,
                    orientation_file,
                ) = GetVoxSegTif.check_warping_requirements(
                    ace_flow_vox_output_folder, ace_flow_warp_output_folder
                )
                
                if args.overwrite:
                    GetVoxSegTif.create_orientation_file(
                        orientation_file, ace_flow_warp_output_folder, args.rca_orient_code
                    )
                    self.warping.warp(
                        args, ace_flow_reg_output_folder.parent / "clar_allen_reg", voxelized_segmented_tif, orientation_file
                    )
            
            nifti_save_location[type_] = voxelized_segmented_tif # make sure this is the right file
        
        # reset the save folder to the original provided arg
        args.sa_output_folder = overall_save_folder
        args.pcs_control = (
            args.control[0],
            nifti_save_location['control'].as_posix()
        )
        args.pcs_experiment = (
            args.experiment[0],
            nifti_save_location['experiment'].as_posix()
        )

        ace_flow_cluster_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "clust_final"
        )
        ace_flow_heatmap_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "heat_final"
        )
        ace_flow_corr_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "corr_final"
        )

        self.clustering.cluster(args, ace_flow_cluster_output_folder)

        p_value_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "diff_mean.nii.gz"
        )
        f_obs_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "f_obs.nii.gz"
        )
        mean_diff_input = GetCorrInput.check_corr_input_exists(
            ace_flow_cluster_output_folder, "p_values.nii.gz"
        )

        self.correlation.correlate(
            args,
            ace_flow_corr_output_folder,
            p_value_input,
            f_obs_input,
            mean_diff_input,
        )

        tested_heatmap_cmd = ConstructHeatmapCmd.test_none_args(
            args.sh_sagittal, args.sh_coronal, args.sh_axial, args.sh_figure_dim
        )
        heatmap_cmd = ConstructHeatmapCmd.construct_final_heatmap_cmd(
            args, ace_flow_heatmap_output_folder, tested_heatmap_cmd
        )
        self.heatmap.create_heatmap(heatmap_cmd)


class FolderCreator:
    """Class used for creating folders.
    """
    @staticmethod
    def create_folder(arg_var: str, *name_vars: typing.Iterable[str]) -> pathlib.Path:
        """Static method for creating folders of arbitrary depth.

        :param arg_var: root folder
        :type arg_var: str
        :return: path to the created folder
        :rtype: pathlib.Path
        """
        folder = Path(arg_var)
        for name_var in name_vars:
            folder = folder / name_var
        folder.mkdir(parents=True, exist_ok=True)
        return folder


class GetConverterdNifti:
    """Class used for finding the converted nifti file.
    """
    @staticmethod
    def get_nifti_file(dir_path_var: str) -> pathlib.Path:
        """Static method for finding the converted nifti file.

        :param dir_path_var: Path to search for converted nifti file.
        :type dir_path_var: str
        :raises FileNotFoundError: If there are no files in the supplied directory.
        :raises ValueError: If there are more than one files in the supplied directory.
        :return: path to the converted nifti file
        :rtype: pathlib.Path
        """
        directory_path = Path(dir_path_var)
        files = list(directory_path.glob("*"))
        if not files:
            raise FileNotFoundError(
                f"No converted nifti files found in: {directory_path}"
            )
        elif len(files) > 1:
            raise ValueError(f"More than one nifti found in: {directory_path}")
        else:
            logger.debug(f"get_nifti_file: {files[0]}")
            return files[0]


class StackTiffs:
    """Class for checking stacking requirements and stacking tiff files.
    """
    @staticmethod
    def check_folders(fiji_file: pathlib.Path, stacked_tif: pathlib.Path):
        """Checks if folders exist and deletes them if they do.

        :param fiji_file: path to the fiji file ('vox_final/stack_seg_tifs.ijm')
        :type fiji_file: pathlib.Path
        :param stacked_tif: path to the stacked tif file ('vox_final/stacked_seg_tif.tif')
        :type stacked_tif: pathlib.Path
        """
        # Check if Fiji file already exists and delete if True
        if fiji_file.is_file():
            fiji_file.unlink()
        # Check if stacked tif file already exists and delete if True
        if stacked_tif.is_file():
            stacked_tif.unlink()

    @staticmethod
    def stacking(fiji_file: pathlib.Path, stacked_tif: pathlib.Path, seg_output_dir: pathlib.Path):
        """Writes a Fiji macro and runs it to stack the segmented tif files.
        Needed to run before voxelization.

        :param fiji_file: path to the fiji file ('vox_final/stack_seg_tifs.ijm')
        :type fiji_file: pathlib.Path
        :param stacked_tif: path to the stacked tif file ('vox_final/stacked_seg_tif.tif')
        :type stacked_tif: pathlib.Path
        :param seg_output_dir: path to the segmented tif files ('seg_final/')
        :type seg_output_dir: pathlib.Path
        """
        print("  stacking segmented tifs...")
        with open(fiji_file, "w") as file:
            file.write(f'File.openSequence("{seg_output_dir}", "virtual");\n')
            file.write(f'saveAs("Tiff", "{stacked_tif}");\n')
            file.write("close();\n")

        fiji_stack_cmd = f"Fiji \
                --headless \
                --console \
                -macro \
                {fiji_file}"
        subprocess.Popen(fiji_stack_cmd, shell=True).wait()


class GetVoxSegTif:
    """Class for checking warping requirements and creating orientation file
    before warping.
    """
    @staticmethod
    def check_warping_requirements(
        ace_flow_vox_output_folder: pathlib.Path, ace_flow_warp_output_folder: pathlib.Path
    ) -> typing.Tuple[pathlib.Path, pathlib.Path]:
        """Check that the voxelized segmented tif file exists, copy it to the
        warp folder and rget the path of the orientation file.

        :param ace_flow_vox_output_folder: path to the voxelized segmented tif file ('vox_final/')
        :type ace_flow_vox_output_folder: pathlib.Path
        :param ace_flow_warp_output_folder: path to the warp folder ('warp_final/')
        :type ace_flow_warp_output_folder: pathlib.Path
        :return: path to the voxelized segmented tif file (in the warp dir) 
            and path to the orientation file
        :rtype: typing.Tuple[pathlib.Path, pathlib.Path]
        """
        voxelized_segmented_tif = list(
            ace_flow_vox_output_folder.glob("voxelized_seg_*.nii.gz")
        )[0]
        orientation_file = ace_flow_warp_output_folder / "ort2std.txt"
        
        # copy vox file to warp folder
        shutil.copy(voxelized_segmented_tif, ace_flow_warp_output_folder)
        voxelized_segmented_tif = list(
            ace_flow_warp_output_folder.glob("voxelized_seg_*.nii.gz")
        )[0]

        return voxelized_segmented_tif, orientation_file

    @staticmethod
    def create_orientation_file(
        orientation_file: pathlib.Path,
        ace_flow_warp_output_folder: pathlib.Path,
        rca_orient_code: str
    ):
        """Check if orientation file exists and delete if it does. Then create
        the orientation file.

        :param orientation_file: path to the orientation file ('warp_final/ort2std.txt')
        :type orientation_file: pathlib.Path
        :param ace_flow_warp_output_folder: path to the warp folder ('warp_final/')
        :type ace_flow_warp_output_folder: pathlib.Path
        :param rca_orient_code: orientation code from the command line args
        :type rca_orient_code: str
        """
        if orientation_file.is_file():
            orientation_file.unlink()

        with open(orientation_file, "w") as file:
            file.write(f"tifdir={ace_flow_warp_output_folder}\n")
            file.write(f"ortcode={rca_orient_code}")


class GetCorrInput:
    """Class for checking correlation input files.
    """
    @staticmethod
    def check_corr_input_exists(dir_var: str, nifti_name_var: str) -> pathlib.Path:
        """Check a file exists in a given folder and return its path.

        :param dir_var: Directory to search
        :type dir_var: str
        :param nifti_name_var: Nifti file name to search for
        :type nifti_name_var: str
        :raises FileNotFoundError: If the file does not exist
        :return: Path to the file in the desired folder
        :rtype: pathlib.Path
        """
        dir_path = Path(dir_var)
        file_path = dir_path / nifti_name_var
        if file_path.is_file():
            return file_path
        else:
            raise FileNotFoundError(f"'{file_path}' does not exist at '{dir_path}'")


class ConstructHeatmapCmd:
    """Class for constructing the heatmap command used by 
    `miracl stats heatmap_group`.
    """
    @staticmethod
    def test_none_args(
        sagittal: argparse.Namespace,
        coronal: argparse.Namespace,
        axial: argparse.Namespace,
        dim: argparse.Namespace,
    ) -> str:
        """
        This function checks if arguments are provided for --sh_sagittal,
        --sh_coronal, --sh_axial and --sh_figure_dim and composes the
        'miracl stats heatmap_group' command accordingly. This is necessary
        because the heatmap fn requires nargs=5 for the axes and nargs=2 for
        the figure dimensions.

        :param sagittal: Argument for sagittal axis.
        :type sagittal: argparse.Namespace
        :param coronal: Argument for coronal axis.
        :type coronal: argparse.Namespace
        :param axial: Argument for axial axis.
        :type axial: argparse.Namespace
        :param dim: Figure dimensions argument.
        :type dim: argparse.Namespace
        :return: A string with the appropriately crafted heatmap command.
        :rtype: str
        """

        def arg_checker(
            prev_cmd: str, arg: argparse.Namespace, arg_name: str, flag: str
        ) -> str:
            """
            This is a nested function that performs the actual checks for
            each provided argument.
            """
            if arg is None:
                logger.debug(f"No arguments for {arg_name} provided")
            else:
                logger.debug(f"Arguments for {arg_name} provided")
                prev_cmd += f"-{flag} {' '.join(map(str, arg))} "

            return prev_cmd

        # Define base cmd to add on to
        base_cmd = "miracl stats heatmap_group "

        saggital_result = arg_checker(base_cmd, sagittal, "sagittal", "s")
        coronal_result = arg_checker(saggital_result, coronal, "coronal", "c")
        axial_result = arg_checker(coronal_result, axial, "axial", "a")
        final_result = arg_checker(axial_result, dim, "figure dimensions", "f")

        return final_result

    @staticmethod
    def construct_final_heatmap_cmd(
        args: argparse.Namespace, ace_flow_heatmap_output_folder: pathlib.Path, tested_heatmap_cmd: str
    ) -> str:
        """Take existing heatmap command and add additional arguments to it.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :param ace_flow_heatmap_output_folder: folder to save the heatmap to ('heat_final/')
        :type ace_flow_heatmap_output_folder: pathlib.Path
        :param tested_heatmap_cmd: existing heatmap command with args (from `test_none_args`)
        :type tested_heatmap_cmd: str
        :return: final heatmap command with args that can be executed in CLI
        :rtype: str
        """
        tested_heatmap_cmd += f"\
            -g1 {args.pcs_control[0]} {args.pcs_control[1]} \
            -g2 {args.pcs_experiment[0]} {args.pcs_experiment[1]} \
            -v {args.sh_vox} \
            -gs {args.sh_sigma} \
            -p {args.sh_percentile} \
            -cp {args.sh_colourmap_pos} \
            -cn {args.sh_colourmap_neg} \
            -d {ace_flow_heatmap_output_folder} \
            -o {args.sh_outfile} \
            -e {args.sh_extension} \
            --dpi {args.sh_dpi}"

        return tested_heatmap_cmd
    
class CheckOverwriteFlag:
    """Class to handle the logic behind overwriting existing per-subject results folders.
    """
    @staticmethod
    def validate_args(
        overwrite: bool,
        folder_name: str,
        control: List[str],
        experiment: List[str],
        output_folder: str,
    ):
        """Validate the arguments for the save directories and the overwrite flag.

        :param overwrite: Whether to overwrite existing results folders.
        :type overwrite: bool
        :param folder_name: Format of the results folder per subject.
        :type folder_name: str
        :param control: Base dir and tiff template for control subjects.
        :type control: List[str]
        :param experiment: Base dir and tiff template for experiment subjects.
        :type experiment: List[str]
        :param output_folder: Output folder to clear
        :type output_folder: str
        :raises ValueError: If not all subjects have existing results folders and overwrite is False.
        """
        # if we don't overwrite, check if the folder exists
        if not overwrite:
            folder_locations = CheckOverwriteFlag._get_dirs(
                folder_name,
                control,
                experiment
            )

            # check that all the folders exist
            if not all([folder.is_dir() for folder in folder_locations]):
                raise ValueError(
                    f"Not all subjects have existing results folder of the form \"{folder_name}\". "
                    "Please specify --overwrite flag to create them."
                )
        
        # clear the folders if we overwite
        if overwrite:
            CheckOverwriteFlag._clear_dirs(
                folder_name,
                control,
                experiment,
                output_folder,
            )
            
    @staticmethod
    def _clear_dirs(
        folder_name: str,
        control: List[str],
        experiment: List[str],
        output_folder: Optional[str] = None,
    ):
        """Clear the given directories for all subjects. This is used
        when the overwrite flag is set to True.

        :param folder_name: Directory name that must be removed for each subject.
        :type folder_name: str
        :param control: Base control dir and tiff template.
        :type control: List[str]
        :param experiment: Base experiment dir and tiff template.
        :type experiment: List[str]
        :param output_folder: Output folder to clear, defaults to None
        :type output_folder: Optional[str]
        """
        # clear the folders
        folder_locations = CheckOverwriteFlag._get_dirs(
            folder_name,
            control,
            experiment
        )

        for folder in folder_locations:
            if folder.is_dir():
                shutil.rmtree(folder)

        if output_folder is not None:
            output_folder = Path(output_folder)
            if output_folder.is_dir():
                shutil.rmtree(output_folder)
    
    @staticmethod
    def _get_dirs(
        folder_name: str,
        control: List[str],
        experiment: List[str]
    ) -> List[Path]:
        """Get the folder locations for all subjects.
        Uses the base directory and the tiff template to find the
        folders.

        :param folder_name: Per subject folder name to look for.
        :type folder_name: str
        :param control: Base control dir and tiff template.
        :type control: List[str]
        :param experiment: Base experiment dir and tiff template.
        :type experiment: List[str]
        :return: List of the folder locations for control and experiment subjects.
        :rtype: List[Path]
        """
        folder_locations = []
        # get the folder location for all subjects
        control_tiff_template = Path(control[1])
        control_base_dir = Path(control[0])

        control_tiff_extension = Path(*control_tiff_template.relative_to(control_base_dir).parts[1:])
        subject_folders = [dir_ for dir_ in control_base_dir.iterdir() if dir_.is_dir()]
        save_folders = [
            (subject / control_tiff_extension).parent / folder_name
            for subject in subject_folders
        ]
        folder_locations.extend(save_folders)

        experiment_tiff_template = Path(experiment[1])
        experiment_base_dir = Path(experiment[0])

        experiment_tiff_extension = Path(*experiment_tiff_template.relative_to(experiment_base_dir).parts[1:])
        subject_folders = [dir_ for dir_ in experiment_base_dir.iterdir() if dir_.is_dir()]
        save_folders = [
            (subject / experiment_tiff_extension).parent / folder_name
            for subject in subject_folders
        ]
        folder_locations.extend(save_folders)

        return folder_locations
        
def main():
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    segmentation = ACESegmentation()
    conversion = ACEConversion()
    registration = ACERegistration()
    voxelization = ACEVoxelization()
    warping = ACEWarping()
    clustering = ACEClusterwise()
    correlation = ACECorrelation()
    heatmap = ACEHeatmap()

    ace_workflow = ACEWorkflows(
        segmentation,
        conversion,
        registration,
        voxelization,
        warping,
        clustering,
        correlation,
        heatmap,
    )
    result = ace_workflow.execute_workflow(args)

if __name__ == "__main__":
    main()