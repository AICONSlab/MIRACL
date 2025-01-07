from abc import abstractmethod, ABC
import subprocess
import miracl.seg.mapl3.mapl3_interface as mapl3_seg_interface
from miracl.flow.mapl3.mapl3_workflow_cli_parser import Mapl3Parser
from miracl.system.objs.objs_reg.objs_clar_allen.objs_clar_allen_reg import (
    ClarAllen as obj_clar_allen,
)
from miracl import miracl_logger

logger = miracl_logger.logger


class Interface(ABC):
    @abstractmethod
    def execute_mapl3_interface(self):
        pass


class Registration(ABC):
    @abstractmethod
    def execute_miracl_registration(self, generate_patch_input_folder):
        pass


class MAPL3Interface(Interface):

    def execute_mapl3_interface(self):
        logger.debug("##################################")
        logger.debug("SEGMENTATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")
        obj_dict = mapl3_seg_interface.main(Mapl3Parser())

        return obj_dict["generate_patch_input_folder"]


class MIRACLRegistration(Registration):

    def execute_miracl_registration(self, generate_patch_input_folder):
        logger.debug("##################################")
        logger.debug("REGISTRATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")
        logger.debug(f"generate_patch_input_folder: {generate_patch_input_folder}")

        # reg_cmd = f"{MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        #         -i {converted_nii_file} \
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
        #         -w {args.rca_warp} \
        #         -c {args.single}"
        #
        # subprocess.Popen(reg_cmd, shell=True).wait()


def main():

    parser = Mapl3Parser()
    args = vars(parser.parser.parse_args())

    reg_clar_allen_hemi = obj_clar_allen.hemi
    reg_clar_allen_hemi.content = args[reg_clar_allen_hemi.flow["mapl3"]["cli_l_flag"]]

    logger.debug(f"OUTPUT: {reg_clar_allen_hemi}")

    mapl3_interface = MAPL3Interface()
    miracl_registration = MIRACLRegistration()

    generate_patch_input_folder = mapl3_interface.execute_mapl3_interface()
    miracl_registration.execute_miracl_registration(generate_patch_input_folder)


if __name__ == "__main__":
    main()
