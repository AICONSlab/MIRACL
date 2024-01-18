import argparse
import os
import subprocess
import shutil
import sys
from pathlib import Path
from miracl import miracl_logger
from abc import ABC, abstractmethod
from miracl.flow import miracl_workflow_ace_parser
from miracl.seg import ace_interface
from miracl.flow import miracl_workflow_ace_stats

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
    def cluster(self, args):
        pass


class Heatmap(ABC):
    @abstractmethod
    def create_heatmap(self, args):
        pass


# DECLARE CONCRETE METHODS #
class ACESegmentation(Segmentation):
    def segment(self, args):
        print("  segmenting...")
        logger.debug("Calling ace_interface fn here")
        logger.debug(f"Example args: {args.sa_model_type}")
        # ace_interface.main(args=args)


class ACEConversion(Conversion):
    def convert(self, args):
        print("  converting...")
        # conv_cmd = f"python {MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
        # --folder {args.single} \
        # --work_dir {args.sa_output_folder} \
        # --down {args.ctn_down} \
        # --channum {args.ctn_channum} \
        # --chanprefix {args.ctn_chanprefix} \
        # --channame {args.ctn_channame} \
        # --outnii {args.ctn_outnii} \
        # --resx {args.ctn_resx} \
        # --resz {args.ctn_resz} \
        # --center {' '.join(map(str, args.ctn_center))} \
        # --downzdim {args.ctn_downzdim} \
        # --prevdown {args.ctn_prevdown}"
        # # Call conversion fn
        # subprocess.Popen(conv_cmd, shell=True).wait()
        logger.debug("Calling conversion fn here")
        logger.debug(f"Example args: {args.ctn_down}")


class ACERegistration(Registration):
    def register(self, args, **kwargs):
        print("  registering...")
        if "dependent_folder" in kwargs:
            ace_flow_conv_output_folder = kwargs["dependent_folder"]
        else:
            raise FileNotFoundError("Output folder path variable not found!")

        if "converted_nii_file" in kwargs:
            converted_nii_file = kwargs["converted_nii_file"]
        else:
            raise FileNotFoundError("Converted nifti file not found!")

        # reg_cmd = f"{MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        # -i {converted_nii_file} \
        # -r {args.sa_output_folder} \
        # -o {args.rca_orient_code} \
        # -m {args.rca_hemi} \
        # -v {args.rca_voxel_size} \
        # -l {args.rca_allen_label} \
        # -a {args.rca_allen_atlas} \
        # -s {args.rca_side} \
        # -f {args.rca_no_mosaic_fig} \
        # -b {args.rca_olfactory_bulb} \
        # -p {args.rca_skip_cor} \
        # -w {args.rca_warp}"
        # subprocess.Popen(reg_cmd, shell=True).wait()
        logger.debug("Calling registration fn here")
        logger.debug(f"Example args: {args.rca_allen_atlas}")
        logger.debug(f"dependent_folder: {ace_flow_conv_output_folder}")
        logger.debug(f"nifti file: {converted_nii_file}")


class ACEVoxelization(Voxelization):
    def voxelize(self, args, stacked_tif):
        print("  voxelizing stacked tif...")
        vox_cmd = f"miracl seg voxelize \
        --seg {stacked_tif} \
        --res {args.rca_voxel_size} \
        --down {args.ctn_down}"
        # -vx {args.} \
        # -vz {args.}"
        # subprocess.Popen(vox_cmd, shell=True).wait()
        logger.debug("Calling voxelization fn here")
        logger.debug(f"ctn_down in voxelization: {args.ctn_down}")


class ACEWarping(Warping):
    def warp(
        self,
        args,
        ace_flow_reg_output_folder,
        voxelized_segmented_tif,
        orientation_file,
    ):
        print("  warping stacked tif...")
        warp_cmd = f"miracl reg warp_clar \
                -r {ace_flow_reg_output_folder} \
                -i {voxelized_segmented_tif} \
                -o {orientation_file} \
                -s {args.rwc_seg_channel} \
                -v {args.rca_voxel_size}"
        # subprocess.Popen(warp_cmd, shell=True).wait()
        logger.debug("Calling warping here")
        logger.debug(f"orientation_file: {orientation_file}")


class ACEClusterwise(Clusterwise):
    def cluster(self, args):
        print("  clusterwise comparison...")
        clusterwise_cmd = f"python {MIRACL_HOME}/flow/miracl_workflow_ace_stats.py \
                --pcs_wild_type {args.pcs_wild_type} \
                --pcs_disease {args.pcs_disease} \
                --pcs_output {args.sa_output_folder} \
                --pcs_num_perm {args.pcs_num_perm} \
                --pcs_atlas_dir {args.pcs_atlas_dir} \
                --pcs_img_resolution {args.pcs_img_resolution} \
                --pcs_smoothing_fwhm {args.pcs_smoothing_fwhm} \
                --pcs_tfce_start {args.pcs_tfce_start} \
                --pcs_tfce_step {args.pcs_tfce_step} \
                --pcs_cpu_load {args.pcs_cpu_load} \
                --pcs_tfce_h {args.pcs_tfce_h} \
                --pcs_tfce_e {args.pcs_tfce_e} \
                --pcs_step_down_p {args.pcs_step_down_p} \
                --pcs_mask_thr {args.pcs_mask_thr}"
        # subprocess.Popen(clusterwise_cmd, shell=True).wait()
        logger.debug("Calling clusterwise comparison fn here")
        logger.debug(f"clusterwise_cmd: {clusterwise_cmd}")
        logger.debug(f"sample arg: {args.pcs_wild_type}")


class ACEHeatmap(Heatmap):
    def create_heatmap(self, args, heatmap_cmd):
        print("  creating heatmaps...")
        # subprocess.Popen(heatmap_cmd, shell=True).wait()
        logger.debug("Calling heatmap fn here")
        logger.debug(f"heatmap_cmd: {heatmap_cmd}")


class ACEWorkflows:
    def __init__(
        self,
        segmentation: Segmentation,
        conversion: Conversion,
        registration: Registration,
        voxelization: Voxelization,
        warping: Warping,
        clustering: Clusterwise,
        heatmap: Heatmap,
    ):
        self.segmentation = segmentation
        self.conversion = conversion
        self.registration = registration
        self.voxelization = voxelization
        self.warping = warping
        self.clustering = clustering
        self.heatmap = heatmap

    def execute_workflow(self, args, **kwargs):

        # check for single or multi in the args
        if args.single:
            self._execute_single_workflow(args, **kwargs)
        elif args.wild and args.disease:
            self._execute_comparison_workflow(args, **kwargs)
        else:
            raise ValueError("Must specify either (-s/--single) or (-w/--wild and -d/--disease) in args.")
        
    def _execute_single_workflow(self, args, **kwargs):
        
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
    
    def _execute_comparison_workflow(self, args, **kwargs):

        overall_save_folder = args.sa_output_folder

        args_dict = vars(args)

        per_subject_final_folder = f"final_ctn_down={args.ctn_down}_rca_voxel_size={args.rca_voxel_size}"

        nifti_save_location = {}

        for type_ in ['wild', 'disease']:

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

                # TODO: make sure we're getting the right dir
                args.single = base_dir / subject.stem / tiff_extension

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

                (
                    voxelized_segmented_tif,
                    orientation_file,
                ) = GetVoxSegTif.check_warping_requirements(
                    ace_flow_vox_output_folder, ace_flow_warp_output_folder
                )
                GetVoxSegTif.create_orientation_file(
                    orientation_file, ace_flow_warp_output_folder
                )
                self.warping.warp(
                    args, ace_flow_reg_output_folder.parent / "clar_allen_reg", voxelized_segmented_tif, orientation_file
                )
            
            nifti_save_location[type_] = voxelized_segmented_tif # make sure this is the right file
        
        # reset the save folder to the original provided arg
        args.sa_output_folder = overall_save_folder
        args.pcs_wild_type = nifti_save_location['wild']
        args.pcs_disease = nifti_save_location['disease']

        ace_flow_cluster_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "clust_final"
        )
        ace_flow_heatmap_output_folder = FolderCreator.create_folder(
            args.sa_output_folder, "heat_final"
        )

        self.clustering.cluster(args)

        tested_heatmap_cmd = ConstructHeatmapCmd.test_none_args(
            args.sh_sagittal, args.sh_coronal, args.sh_axial, args.sh_figure_dim
        )
        heatmap_cmd = ConstructHeatmapCmd.construct_final_heatmap_cmd(
            args, ace_flow_heatmap_output_folder, tested_heatmap_cmd
        )
        self.heatmap.create_heatmap(args, heatmap_cmd)


class FolderCreator:
    @staticmethod
    def create_folder(arg_var, *name_vars):
        folder = Path(arg_var)
        for name_var in name_vars:
            folder = folder / name_var
        folder.mkdir(parents=True, exist_ok=True)
        return folder


class GetConverterdNifti:
    @staticmethod
    def get_nifti_file(dir_path_var):
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
    @staticmethod
    def check_folders(fiji_file, stacked_tif):
        # Check if Fiji file already exists and delete if True
        if fiji_file.is_file():
            fiji_file.unlink()
        # Check if stacked tif file already exists and delete if True
        if stacked_tif.is_file():
            stacked_tif.unlink()

    @staticmethod
    def stacking(fiji_file, stacked_tif, seg_output_dir):
        print("  stacking segmented tifs...")
        with open(fiji_file, "w") as file:
            file.write(f'File.openSequence("{seg_output_dir}/generated_pathches", "virtual");\n')
            file.write(f'saveAs("Tiff", "{stacked_tif}");\n')
            file.write("close();\n")

        fiji_stack_cmd = f"Fiji \
                --headless \
                --console \
                -macro \
                {fiji_file}"
        # subprocess.Popen(fiji_stack_cmd, shell=True).wait()


class GetVoxSegTif:
    @staticmethod
    def check_warping_requirements(
        ace_flow_vox_output_folder, ace_flow_warp_output_folder
    ):
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
    def create_orientation_file(orientation_file, ace_flow_warp_output_folder):
        if orientation_file.is_file():
            orientation_file.unlink()

        with open(orientation_file, "w") as file:
            file.write(f"tifdir={ace_flow_warp_output_folder}\n")
            file.write(f"ortcode={args.rca_orient_code}")

# TODO: may have to change for our new usage
class ConstructHeatmapCmd:
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
        args, ace_flow_heatmap_output_folder, tested_heatmap_cmd
    ):
        # TODO: fix the params this function recieves
        tested_heatmap_cmd += f"-g1 {args.sh_group1} -g2 {args.sh_group2} -v {args.sh_vox} -gs {args.sh_sigma} -p {args.sh_percentile} -cp {args.sh_colourmap_pos} -cn {args.sh_colourmap_neg} -d {ace_flow_heatmap_output_folder} -o {args.sh_outfile} -e {args.sh_extension} --dpi {args.sh_dpi}"

        return tested_heatmap_cmd


if __name__ == "__main__":
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    segmentation = ACESegmentation()
    conversion = ACEConversion()
    registration = ACERegistration()
    voxelization = ACEVoxelization()
    warping = ACEWarping()
    clustering = ACEClusterwise()
    heatmap = ACEHeatmap()

    ace_workflow = ACEWorkflows(
        segmentation,
        conversion,
        registration,
        voxelization,
        warping,
        clustering,
        heatmap,
    )
    result = ace_workflow.execute_workflow(args)


# class ACEInterface(ABC):
#     @abstractmethod
#     def ace_seg_method(self, args):
#         pass
#
#     @abstractmethod
#     def conv_method(self, args):
#         pass
#
#     @abstractmethod
#     def reg_method(self, args):
#         pass
#
#
# class ACEImplementation(ACEInterface):
#     MIRACL_HOME = Path(os.environ["MIRACL_HOME"])
#
#     def ace_seg_method(self, args):
#         # INFO: Create ACE seg output folder -> returns path of seg_out
#         self.ace_flow_seg_output_folder = Path(args.sa_output_folder) / "seg_final"
#         self.ace_flow_seg_output_folder.mkdir(parents=True, exist_ok=True)
#         # Call ACE interface
#         logger.debug("Calling ace_interface fn here")
#         logger.debug(f"Example args: {args.sa_model_type}")
#         # ace_interface.main(args=args)
#
#         return self
#
#     def conv_method(self, args):
#         # INFO: Call conversion here and set output folder -> returns path
#         self.ace_flow_conv_output_folder = Path(args.sa_output_folder) / "conv_final"
#         self.ace_flow_conv_output_folder.mkdir(parents=True, exist_ok=True)
#         # Construct conversion cmd
#         conv_cmd = f"python {self.MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
#         --folder {args.sa_input_folder} \
#         --work_dir {args.sa_output_folder} \
#         --down {args.ctn_down} \
#         --channum {args.ctn_channum} \
#         --chanprefix {args.ctn_chanprefix} \
#         --channame {args.ctn_channame} \
#         --outnii {args.ctn_outnii} \
#         --resx {args.ctn_resx} \
#         --resz {args.ctn_resz} \
#         --center {' '.join(map(str, args.ctn_center))} \
#         --downzdim {args.ctn_downzdim} \
#         --prevdown {args.ctn_prevdown}"
#         # Call conversion fn
#         # subprocess.Popen(conv_cmd, shell=True).wait()
#         logger.debug("Calling conversion fn here")
#         logger.debug(f"Example args: {args.ctn_down}")
#         logger.debug(f"ACE dir: {self.ace_flow_seg_output_folder}")
#
#         return self
#
#     def _search_dir_for_files(self, dir_path_var):
#         directory_path = Path(dir_path_var)
#         files = list(directory_path.glob("*"))
#         if not files:
#             raise FileNotFoundError(
#                 f"No converted nifti files found in: {directory_path}"
#             )
#         elif len(files) > 1:
#             raise ValueError(f"More than one nifti found in: {directory_path}")
#         else:
#             return files[0]
#
#     def reg_method(self, args):
#         # INFO: Call registration here
#         # INFO: Pass args.seg_input_folder
#         # INFO: Set output folder
#
#         try:
#             # self.converted_nii_file = next(self.ace_flow_conv_output_folder.glob("*"))
#             self.converted_nii_file = self._search_dir_for_files(
#                 self.ace_flow_conv_output_folder
#             )
#         except Exception as e:
#             print(f"An unexpected error occurred: {e}")
#
#         reg_cmd = f"{self.MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
#         -i {self.converted_nii_file} \
#         -r {args.sa_output_folder} \
#         -o {args.rca_orient_code} \
#         -m {args.rca_hemi} \
#         -v {args.rca_voxel_size} \
#         -l {args.rca_allen_label} \
#         -a {args.rca_allen_atlas} \
#         -s {args.rca_side} \
#         -f {args.rca_no_mosaic_fig} \
#         -b {args.rca_olfactory_bulb} \
#         -p {args.rca_skip_cor} \
#         -w {args.rca_warp}"
#         # subprocess.Popen(reg_cmd, shell=True).wait()
#         logger.debug("Calling registration fn here")
#         logger.debug(f"Example args: {args.rca_allen_atlas}")
#         logger.debug(f"ACE dir: {self.ace_flow_seg_output_folder}")
#         logger.debug(f"Glob: {self.converted_nii_file}")
#
#         return self
#
#
# if __name__ == "__main__":
#     args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
#     args = args_parser.parse_args()
#
#     # # Assign parsed arguments to constants
#     # X_CONSTANT = args.x
#     # Y_CONSTANT = args.y
#     #
#     # my_impl = MyImplementation()
#     ace_flow = ACEImplementation()
#     ace_flow.ace_seg_method(args).conv_method(args).reg_method(args)
#     # result1 = my_impl.method1(X_CONSTANT)
#     # result2 = my_impl.method2(Y_CONSTANT)
