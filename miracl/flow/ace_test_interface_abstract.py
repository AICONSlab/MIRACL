import argparse
import os
import sys
from pathlib import Path
from miracl import miracl_logger
from abc import ABC, abstractmethod
from miracl.flow import miracl_workflow_ace_parser
from miracl.seg import ace_interface

logger = miracl_logger.logger


class ACEInterface(ABC):
    @abstractmethod
    def ace_seg_method(self, args):
        pass

    @abstractmethod
    def conv_method(self, args):
        pass

    @abstractmethod
    def reg_method(self, args):
        pass


class ACEImplementation(ACEInterface):
    MIRACL_HOME = Path(os.environ["MIRACL_HOME"])

    def ace_seg_method(self, args):
        # INFO: Create ACE seg output folder -> returns path of seg_out
        self.ace_flow_seg_output_folder = Path(args.sa_output_folder) / "seg_final"
        self.ace_flow_seg_output_folder.mkdir(parents=True, exist_ok=True)
        # Call ACE interface
        logger.debug("Calling ace_interface fn here")
        logger.debug(f"Example args: {args.sa_model_type}")
        # ace_interface.main(args=args)

        return self

    def conv_method(self, args):
        # INFO: Call conversion here and set output folder -> returns path
        self.ace_flow_conv_output_folder = Path(args.sa_output_folder) / "conv_final"
        self.ace_flow_conv_output_folder.mkdir(parents=True, exist_ok=True)
        # Construct conversion cmd
        conv_cmd = f"python {self.MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
        --folder {args.sa_input_folder} \
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
        # Call conversion fn
        # subprocess.Popen(conv_cmd, shell=True).wait()
        logger.debug("Calling conversion fn here")
        logger.debug(f"Example args: {args.ctn_down}")
        logger.debug(f"ACE dir: {self.ace_flow_seg_output_folder}")

        return self

    def _search_dir_for_files(self, dir_path_var):
        directory_path = Path(dir_path_var)
        files = list(directory_path.glob("*"))
        if not files:
            raise FileNotFoundError(
                f"No converted nifti files found in: {directory_path}"
            )
        elif len(files) > 1:
            raise ValueError(f"More than one nifti found in: {directory_path}")
        else:
            return files[0]

    def reg_method(self, args):
        # INFO: Call registration here
        # INFO: Pass args.seg_input_folder
        # INFO: Set output folder

        try:
            # self.converted_nii_file = next(self.ace_flow_conv_output_folder.glob("*"))
            self.converted_nii_file = self._search_dir_for_files(
                self.ace_flow_conv_output_folder
            )
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        reg_cmd = f"{self.MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        -i {self.converted_nii_file} \
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
        # subprocess.Popen(reg_cmd, shell=True).wait()
        logger.debug("Calling registration fn here")
        logger.debug(f"Example args: {args.rca_allen_atlas}")
        logger.debug(f"ACE dir: {self.ace_flow_seg_output_folder}")
        logger.debug(f"Glob: {self.converted_nii_file}")

        return self


if __name__ == "__main__":
    args_parser = miracl_workflow_ace_parser.ACEWorkflowParser()
    args = args_parser.parse_args()

    # # Assign parsed arguments to constants
    # X_CONSTANT = args.x
    # Y_CONSTANT = args.y
    #
    # my_impl = MyImplementation()
    ace_flow = ACEImplementation()
    ace_flow.ace_seg_method(args).conv_method(args).reg_method(args)
    # result1 = my_impl.method1(X_CONSTANT)
    # result2 = my_impl.method2(Y_CONSTANT)
