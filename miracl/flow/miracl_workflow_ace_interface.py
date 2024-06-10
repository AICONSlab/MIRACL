import argparse
import os
import pathlib
import re
import shutil
import subprocess
import typing
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from miracl import miracl_logger
from miracl.flow import miracl_workflow_ace_parser
from miracl.seg import ace_interface
from miracl.stats import miracl_stats_ace_interface

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


class Stats(ABC):
    @abstractmethod
    def compute_stats(self, args):
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

    def segment(self, args: argparse.Namespace):
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

    def convert(self, args: argparse.Namespace):
        """Main method for conversion module. Calls `miracl conv tiff_nii` module.

        :param args: command line arguments needed for MIRACL conv module.
        :type args: argparse.Namespace
        """
        print("  converting...")
        vx, vy, vz = args.sa_resolution
        conv_cmd = f"python {MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
        --folder {args.single} \
        --work_dir {args.sa_output_folder} \
        --down {args.ctn_down} \
        --channum {args.ctn_channum} \
        --chanprefix {args.ctn_chanprefix} \
        --channame {args.ctn_channame} \
        --outnii {args.ctn_outnii} \
        --resx {vx} \
        --resz {vz} \
        --center {' '.join(map(str, args.ctn_center))} \
        --downzdim {args.ctn_downzdim} \
        --prevdown {args.ctn_prevdown} \
        --percentile_thr {args.ctn_percentile_thr}"
        subprocess.Popen(conv_cmd, shell=True).wait()
        logger.debug("Calling conversion fn here")
        logger.debug(f"Example args: {args.ctn_down}")


class ACERegistration(Registration):
    """ACE Registration module used for registering the converted nifti files to the Allen atlas.

    :param Registration: base abstract class for registration
    :type Registration: ABC
    """

    def register(self, args: argparse.Namespace, reg_cmd: str):
        """Main method for registration module. Calls `miracl reg clar_allen` module.

        :param args: command line arguments needed for MIRACL reg module.
        :type args: argparse.Namespace
        :param reg_cmd: registration command with args.
        :type reg_cmd: str
        """

        subprocess.Popen(reg_cmd, shell=True).wait()
        logger.debug("Calling registration fn here")
        logger.debug(f"Example args: {args.rca_allen_atlas}")
        # logger.debug(f"dependent_folder: {ace_flow_conv_output_folder}")
        # logger.debug(f"nifti file: {converted_nii_file}")


class ACEVoxelization(Voxelization):
    """ACE Voxelization module used for voxelizing the segmented tif files.

    :param Voxelization: base abstract class for voxelization
    :type Voxelization: ABC
    """

    def voxelize(self, args: argparse.Namespace, stacked_tif: pathlib.Path):
        """Main method for voxelization module. Calls `miracl seg voxelize` module.

        :param args: command line arguments needed for MIRACL seg module.
        :type args: argparse.Namespace
        :param stacked_tif: path to the stacked tif file ('stacked_seg_tif.tif')
        :type stacked_tif: pathlib.Path
        """
        x_vox, y_vox, z_vox = args.sa_resolution
        print("  voxelizing stacked tif...")
        vox_cmd = f"miracl seg voxelize \
        --seg {stacked_tif} \
        --res {args.rca_voxel_size} \
        --down {args.rva_downsample} \
        -vx {x_vox} \
        -vz {z_vox}"
        subprocess.Popen(vox_cmd, shell=True).wait()
        logger.debug("Calling voxelization fn here")
        logger.debug(f"ctn_down in voxelization: {args.ctn_down}")
        logger.debug(f"x_vox: {x_vox}")
        logger.debug(f"y_vox: {y_vox}")
        logger.debug(f"z_vox: {z_vox}")


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
        :param voxelized_segmented_tif: path to the voxelized segmented tif file ('vox_final/voxelized_seg_*.nii.gz')
        :type voxelized_segmented_tif: pathlib.Path
        :param orientation_file: path to the orientation file ('warp_final/ort2std.txt')
        :type orientation_file: pathlib.Path
        """
        print("  warping stacked tif...")
        warp_cmd = f"miracl reg warp_clar \
                -r {ace_flow_reg_output_folder.as_posix()} \
                -i {voxelized_segmented_tif} \
                -o {orientation_file} \
                -s ace_flow \
                -v {args.rwc_voxel_size}"
        subprocess.Popen(warp_cmd, shell=True).wait()
        # move the output file to the right folder
        warp_file = list((Path.cwd() / "reg_final").glob("voxelized_*.nii.gz"))[0]
        shutil.move(
            str(warp_file), str(voxelized_segmented_tif.parent.parent / "warp_final")
        )
        logger.debug("Calling warping here")
        logger.debug(f"orientation_file: {orientation_file}")


class ACEStats(Stats):
    """ACE Stats module used for computing statistics (clusterwise and correlation) on warp files.

    :param Stats: base abstract class for stats
    :type Stats: ABC
    """

    def compute_stats(self, args: argparse.Namespace):
        """Main method for stats module. Calls `miracl stats ace` module.

        :param args: command line arguments needed for MIRACL stats module.
        :type args: argparse.Namespace
        """
        print("  computing ace stats...")
        miracl_stats_ace_interface.main(args)


class ACEHeatmap(Heatmap):
    """ACE Heatmap module used for creating heatmaps.

    :param Heatmap: base abstract class for heatmap module
    :type Heatmap: ABC
    """

    def create_heatmap(self, heatmap_cmd: str):
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
        stats: Stats,
        heatmap: Heatmap,
    ):
        """Constructor method"""
        self.segmentation = segmentation
        self.conversion = conversion
        self.registration = registration
        self.voxelization = voxelization
        self.warping = warping
        self.stats = stats
        self.heatmap = heatmap

    def execute_workflow(self, args: argparse.Namespace, **kwargs):
        """Method that handles logic for single or comparison workflow.

        :param args: command line arguments from ACE parser
        :type args: argparse.Namespace
        :raises ValueError: If insufficient arguments are passed to handle single
            or comparison workflow
        """

        # check for single or multi in the args
        if args.single:
            self._execute_single_workflow(args, **kwargs)
        elif args.control and args.treated:
            self._execute_comparison_workflow(args, **kwargs)
        else:
            raise ValueError(
                "Must specify either (-s/--single) or (-c/--control and -t/--treated) in args."
            )

    def _execute_single_workflow(
        self, args: argparse.Namespace, **kwargs
    ) -> pathlib.Path:
        """Private method for executing the single workflow.

        :param args: command line arguments needed for single workflow
        :type args: argparse.Namespace
        :return: path to the final output folder at the same level as the
            directory containing input tiff files
        :rtype: pathlib.Path
        """
        final_folder = (
            f"final_ctn_down_{args.ctn_down}_rca_voxel_size_{args.rca_voxel_size}"
        )
        args.sa_output_folder = str((Path(args.sa_output_folder) / final_folder))

        ace_flow_seg_output_folder = FolderCreator.create_folder(
            args.sa_output_folder,
            "seg_final",
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

        rerun_seg = SegmentationChecker.check_segmentation(
            args, ace_flow_seg_output_folder
        )

        if rerun_seg:
            self.segmentation.segment(args)

        rerun_conv = ConversionChecker.check_conversion(
            args, ace_flow_conv_output_folder
        )

        if rerun_conv:
            self.conversion.convert(args)

        converted_nii_file = GetConverterdNifti.get_nifti_file(
            ace_flow_conv_output_folder
        )
        rerun_subject = RegistrationChecker.check_registration(
            args, ace_flow_reg_output_folder
        )
        if rerun_subject:
            reg_cmd = RegistrationChecker.get_registration_cmd(
                args,
                converted_nii_file=converted_nii_file,
            )
            self.registration.register(args, reg_cmd)

        # Stack tiff files for use in voxelization method
        fiji_file = ace_flow_vox_output_folder / "stack_seg_tifs.ijm"
        stacked_tif = ace_flow_vox_output_folder / "stacked_seg_tif.tif"
        StackTiffs.check_folders(fiji_file, stacked_tif)
        StackTiffs.stacking(
            fiji_file, stacked_tif, ace_flow_seg_output_folder, args.sa_monte_carlo
        )
        self.voxelization.voxelize(args, stacked_tif)

        (
            voxelized_segmented_tif,
            orientation_file,
        ) = GetVoxSegTif.check_warping_requirements(
            ace_flow_vox_output_folder, ace_flow_warp_output_folder
        )

        GetVoxSegTif.create_orientation_file(
            orientation_file,
            ace_flow_warp_output_folder,
            args.rca_orient_code,
        )
        self.warping.warp(
            args,
            ace_flow_reg_output_folder.parent / "clar_allen_reg",
            voxelized_segmented_tif,
            orientation_file,
        )

    def _execute_comparison_workflow(self, args: argparse.Namespace, **kwargs):
        """Private method for executing the comparison workflow.

        :param args: arguments needed for comparison workflow
        :type args: argparse.Namespace
        """

        overall_save_folder = args.sa_output_folder

        args_dict = vars(args)

        per_subject_final_folder = (
            f"final_ctn_down_{args.ctn_down}_rca_voxel_size_{args.rca_voxel_size}"
        )

        nifti_save_location = {}

        for type_ in ["control", "treated"]:
            tiff_template = Path(args_dict[type_][1])
            base_dir = Path(args_dict[type_][0])

            tiff_extension = Path(*tiff_template.relative_to(base_dir).parts[1:])
            subject_folders = [dir_ for dir_ in base_dir.iterdir() if dir_.is_dir()]

            for subject in subject_folders:
                save_folder = (
                    (subject / tiff_extension).parent / per_subject_final_folder
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

                rerun_seg = SegmentationChecker.check_segmentation(
                    args, ace_flow_seg_output_folder
                )

                if rerun_seg:
                    self.segmentation.segment(args)

                rerun_conv = ConversionChecker.check_conversion(
                    args, ace_flow_conv_output_folder
                )

                if rerun_conv:
                    self.conversion.convert(args)

                converted_nii_file = GetConverterdNifti.get_nifti_file(
                    ace_flow_conv_output_folder
                )

                rerun_subject = RegistrationChecker.check_registration(
                    args, ace_flow_reg_output_folder
                )
                if rerun_subject:
                    reg_cmd = RegistrationChecker.get_registration_cmd(
                        args,
                        converted_nii_file=converted_nii_file,
                    )
                    self.registration.register(args, reg_cmd)
                # Stack tiff files for use in voxelization method
                fiji_file = ace_flow_vox_output_folder / "stack_seg_tifs.ijm"
                stacked_tif = ace_flow_vox_output_folder / "stacked_seg_tif.tif"
                StackTiffs.check_folders(fiji_file, stacked_tif)
                StackTiffs.stacking(fiji_file, stacked_tif, ace_flow_seg_output_folder)
                self.voxelization.voxelize(args, stacked_tif)

                (
                    voxelized_segmented_tif,
                    orientation_file,
                ) = GetVoxSegTif.check_warping_requirements(
                    ace_flow_vox_output_folder, ace_flow_warp_output_folder
                )

                GetVoxSegTif.create_orientation_file(
                    orientation_file,
                    ace_flow_warp_output_folder,
                    args.rca_orient_code,
                )
                self.warping.warp(
                    args,
                    ace_flow_reg_output_folder.parent / "clar_allen_reg",
                    voxelized_segmented_tif,
                    orientation_file,
                )

            nifti_save_location[type_] = list(
                ace_flow_warp_output_folder.glob("*voxelized_*.nii.gz")
            )[0]

        # reset the save folder to the original provided arg
        args.sa_output_folder = overall_save_folder
        args.pcs_control = (args.control[0], nifti_save_location["control"].as_posix())
        args.pcs_treated = (
            args.treated[0],
            nifti_save_location["treated"].as_posix(),
        )

        ace_flow_heatmap_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "heat_final"
        )

        self.stats.compute_stats(args)

        tested_heatmap_cmd = ConstructHeatmapCmd.test_none_args(
            args.sh_sagittal, args.sh_coronal, args.sh_axial, args.sh_figure_dim
        )
        heatmap_cmd = ConstructHeatmapCmd.construct_final_heatmap_cmd(
            args, ace_flow_heatmap_output_folder, tested_heatmap_cmd
        )
        self.heatmap.create_heatmap(heatmap_cmd)


class FolderCreator:
    """Class used for creating folders."""

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
    """Class used for finding the converted nifti file."""

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
    """Class for checking stacking requirements and stacking tiff files."""

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
    def stacking(
        fiji_file: pathlib.Path,
        stacked_tif: pathlib.Path,
        seg_output_dir: pathlib.Path,
        is_MC: bool,
    ):
        """Writes a Fiji macro and runs it to stack the segmented tif files.
        Needed to run before voxelization.

        :param fiji_file: path to the fiji file ('vox_final/stack_seg_tifs.ijm')
        :type fiji_file: pathlib.Path
        :param stacked_tif: path to the stacked tif file ('vox_final/stacked_seg_tif.tif')
        :type stacked_tif: pathlib.Path
        :param seg_output_dir: path to the segmented tif files ('seg_final/')
        :type seg_output_dir: pathlib.Path
        :param is_MC: flag for Monte Carlo or not
        :type is_MC: bool
        """
        print("  stacking segmented tifs...")
        filter = "MC_" if is_MC else "out_"
        with open(fiji_file, "w") as file:
            file.write(
                f'File.openSequence("{seg_output_dir}", "virtual filter={filter}");\n'
            )
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
        ace_flow_vox_output_folder: pathlib.Path,
        ace_flow_warp_output_folder: pathlib.Path,
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

        # # copy vox file to warp folder
        # shutil.copy(voxelized_segmented_tif, ace_flow_warp_output_folder)
        # voxelized_segmented_tif = list(
        #     ace_flow_warp_output_folder.glob("voxelized_seg_*.nii.gz")
        # )[0]

        return voxelized_segmented_tif, orientation_file

    @staticmethod
    def create_orientation_file(
        orientation_file: pathlib.Path,
        ace_flow_warp_output_folder: pathlib.Path,
        rca_orient_code: str,
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
        args: argparse.Namespace,
        ace_flow_heatmap_output_folder: pathlib.Path,
        tested_heatmap_cmd: str,
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
            -g2 {args.pcs_treated[0]} {args.pcs_treated[1]} \
            -v {args.rwc_voxel_size} \
            -gs {args.sh_sigma} \
            -p {args.sh_percentile} \
            -cp {args.sh_colourmap_pos} \
            -cn {args.sh_colourmap_neg} \
            -d {ace_flow_heatmap_output_folder} \
            -o {args.sh_outfile} \
            -e {args.sh_extension} \
            --dpi {args.sh_dpi} \
            -si {args.rca_side} \
            -m {args.rca_hemi} \
            -l {args.rca_allen_label}"

        return tested_heatmap_cmd


class RegistrationChecker:
    """Class for checking if each subject needs to re-run
    registration.
    """

    @staticmethod
    def check_registration(
        args: argparse.Namespace,
        reg_folder: Path,
    ) -> bool:
        """Checks if registration needs to be run based on user input and the file structure.
        If the user want to run registration (with the --rerun-registration flag), we run it. 
        Otherwise we check that all the necessary files are inplace before skipping.
        If they are not, we re-reun registration.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :param reg_folder: path to reg output folder (reg_final/)
        :type reg_folder: Path
        :return: Whether or no registration needs to be re-run
        :rtype: bool
        """
        if args.rerun_registration:
            RegistrationChecker._clear_reg_folders(reg_folder)
            return True

        # check for reg_final/ and clar_allen_reg/
        if (
            not reg_folder.is_dir()
            or not (reg_folder.parent / "clar_allen_reg").is_dir()
        ):
            RegistrationChecker._clear_reg_folders(reg_folder)
            return True

        # check in the directory if there is a file that contains this command
        if not (reg_folder / "reg_command.log").is_file():
            RegistrationChecker._clear_reg_folders(reg_folder)
            return True

        # check that annotation_*um_clar*.tif exists
        if not reg_folder.glob("annotation_*um_clar*.tif"):
            RegistrationChecker._clear_reg_folders(reg_folder)
            return True

        with open(reg_folder / "reg_command.log", "r") as f:
            received_cmd = f.read()

        received_cmd = received_cmd.strip().split("\n")
        # clean the expected command
        expected_command = [str(args.rca_voxel_size), str(args.rca_orient_code)]
        if expected_command == received_cmd:
            return False
        else:
            raise ValueError(
                f"Expected args (rca_voxel_size, rca_orient_code): {expected_command} does not match received args: {received_cmd}"
            )

    @staticmethod
    def get_registration_cmd(args: argparse.Namespace, **kwargs) -> str:
        """Generates the command to be run by the MIRACL registration module.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :raises FileNotFoundError: If no converted_nii_file is supplied
        :return: The command to run in the CLI
        :rtype: str
        """

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
        -w {args.rca_warp} \
        -c {args.single}"

        return reg_cmd

    @staticmethod
    def _clear_reg_folders(reg_folder: Path):
        """Clears the results from the registration folder.

        :param reg_folder: path to the registration output folder ('reg_final/')
        :type reg_folder: Path
        """

        if reg_folder.is_dir():
            shutil.rmtree(reg_folder)
        reg_folder.mkdir(parents=True, exist_ok=True)

        clar_allen_reg = reg_folder.parent / "clar_allen_reg"
        if clar_allen_reg.is_dir():
            shutil.rmtree(clar_allen_reg)
        clar_allen_reg.mkdir(parents=True, exist_ok=True)


class SegmentationChecker:
    """Class for checking if each subject needs to re-run
    segmentation.
    """

    @staticmethod
    def check_segmentation(
        args: argparse.Namespace,
        seg_folder: Path,
    ) -> bool:
        """Checks if segmentation needs to be run based on user input and the file structure.
        If the user wants to run seg (with the --rerun-segmentation flag), we run it.
        Otherwise, check that all the necessary files are in place before skipping.
        If they are not, we re-run seg.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :param seg_folder: path to seg output folder (seg_final/)
        :type seg_folder: Path
        :return: whether or not segmentation needs to be re-run
        :rtype: bool
        """

        if args.rerun_segmentation:
            SegmentationChecker._clear_seg_folders(seg_folder)
            return True

        # check for seg_final/
        if not seg_folder.is_dir():
            SegmentationChecker._clear_seg_folders(seg_folder)
            return True

        # check if generated_patches exists
        if not (seg_folder / "generated_patches").is_dir():
            SegmentationChecker._clear_seg_folders(seg_folder)
            return True

        # check if generated_patches is empty
        if not sorted(seg_folder.glob("generated_patches/*.tiff")):  # doule check names
            SegmentationChecker._clear_seg_folders(seg_folder)
            return True

        # check that the directory isn't empty
        if not list(seg_folder.glob("*.tif")):
            SegmentationChecker._clear_seg_folders(seg_folder)
            return True

    @staticmethod
    def _clear_seg_folders(seg_folder: Path):
        """Clears the results from the segmentation folder.

        :param seg_folder: path to the segmentation output folder ('seg_final/')
        :type seg_folder: Path
        """

        if seg_folder.is_dir():
            shutil.rmtree(seg_folder)
        seg_folder.mkdir(parents=True, exist_ok=True)


class ConversionChecker:
    """Class for checking if each subject needs to re-run
    conversion.
    """

    @staticmethod
    def check_conversion(
        args: argparse.Namespace,
        conv_folder: Path,
    ) -> bool:
        """Checks if conversion needs to be run based on user input and the file structure.
        If the user wants to run conv (with the --rerun-conversion flag), we run it.
        Otherwise, check that all the necessary files are in place before skipping.
        If they are not, we re-run conv.

        :param args: command line args from ACE parser
        :type args: argparse.Namespace
        :param conv_folder: path to conv output folder (conv_final/)
        :type conv_folder: Path
        :return: whether or not conversion needs to be re-run
        :rtype: bool
        """

        if args.rerun_conversion:
            ConversionChecker._clear_conv_folders(conv_folder)
            return True

        # check for conv_final/
        if not conv_folder.is_dir():
            ConversionChecker._clear_conv_folders(conv_folder)
            return True

        # check for the right downsample value
        if not list(conv_folder.glob(f"*_{args.ctn_down}x_down_*.nii.gz")):
            ConversionChecker._clear_conv_folders(conv_folder)
            return True

    @staticmethod
    def _clear_conv_folders(conv_folder: Path):
        """Clears the results from the conversion folder.

        :param conv_folder: path to the conversion output folder ('conv_final/')
        :type conv_folder: Path
        """

        if conv_folder.is_dir():
            shutil.rmtree(conv_folder)
        conv_folder.mkdir(parents=True, exist_ok=True)


def main():
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    segmentation = ACESegmentation()
    conversion = ACEConversion()
    registration = ACERegistration()
    voxelization = ACEVoxelization()
    warping = ACEWarping()
    stats = ACEStats()
    heatmap = ACEHeatmap()

    ace_workflow = ACEWorkflows(
        segmentation,
        conversion,
        registration,
        voxelization,
        warping,
        stats,
        heatmap,
    )
    result = ace_workflow.execute_workflow(args)


if __name__ == "__main__":
    main()
