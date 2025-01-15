from os import environ
from pathlib import Path
import subprocess

from abc import abstractmethod, ABC
from dataclasses import dataclass

# Import MAPL3 module interface for implementation into the workflow interface
from miracl.seg.mapl3 import mapl3_interface
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
from miracl.system.objs.objs_flow.objs_mapl3_workflow.mapl3_workflow_interface_folders import (
    WorkflowInterfaceSubfolders,
)

from miracl.flow.mapl3.mapl3_workflow_cli_parser import Mapl3WorkflowParser
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_object_dict as reg_mapl3_objs,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger

###############################################################################

#############
# DEBUGGING #
#############

logger = miracl_logger.logger

############
# ENV VARS #
############

MIRACL_HOME = Path(environ["MIRACL_HOME"])

###############################################################################


@dataclass
class Mapl3InterfaceParams:
    objs: dict


class Interface(ABC):
    @abstractmethod
    def call_mapl3_interface(self, params: Mapl3InterfaceParams) -> None:
        pass


@dataclass
class RegistrationParams:
    mapl3_objs: dict
    subfolder_objs: dict
    reg_output: MiraclObj


class Registration(ABC):
    @abstractmethod
    def call_miracl_registration(self, params: RegistrationParams) -> None:
        pass


class MAPL3Interface(Interface):

    def call_mapl3_interface(self, params: Mapl3InterfaceParams):
        logger.debug("##################################")
        logger.debug("SEGMENTATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")

        mapl3_subfolders_objs_dict = mapl3_interface.main(params.objs)
        return mapl3_subfolders_objs_dict


class MIRACLRegistration(Registration):

    def call_miracl_registration(self, params: RegistrationParams):
        logger.debug("##################################")
        logger.debug("REGISTRATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")

        reg_cmd = f"{MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        -i {params.mapl3_objs['reg_clar_allen_reg'].nii_folder.dirpath} \
        -c {params.subfolder_objs['patch_stacking_output'].dirpath} \
        -r {params.reg_output.dirpath} \
        -o {params.mapl3_objs['reg_clar_allen_reg'].orient_code.content} \
        -m {params.mapl3_objs['reg_clar_allen_reg'].hemi.content} \
        -v {params.mapl3_objs['reg_clar_allen_reg'].voxel_size.content} \
        -l {params.mapl3_objs['reg_clar_allen_reg'].allen_label.content} \
        -a {params.mapl3_objs['reg_clar_allen_reg'].allen_atlas.content} \
        -s {params.mapl3_objs['reg_clar_allen_reg'].side.content} \
        -f {params.mapl3_objs['reg_clar_allen_reg'].no_mosaic_fig.content} \
        -b {params.mapl3_objs['reg_clar_allen_reg'].olfactory_bulb.content} \
        -p {params.mapl3_objs['reg_clar_allen_reg'].skip_cor.content} \
        -w {params.mapl3_objs['reg_clar_allen_reg'].warp.content}"

        subprocess.Popen(reg_cmd, shell=True).wait()


def main(objs):

    mapl3_interface = MAPL3Interface()
    miracl_registration = MIRACLRegistration()

    # Run MAPL3 module interface and return subfolder objs dict
    mapl3_subfolders_objs_dict = mapl3_interface.call_mapl3_interface(
        Mapl3InterfaceParams(objs=objs)
    )

    # Assign base registration output
    WorkflowInterfaceSubfolders.mapl3_workflow_reg_folder.dirpath = (
        mapl3_subfolders_objs_dict["mapl3_results_base_folder"].dirpath / "reg"
    )

    # Run registration using MAPL3 and subfolder objs
    miracl_registration.call_miracl_registration(
        RegistrationParams(
            mapl3_objs=objs,
            subfolder_objs=mapl3_subfolders_objs_dict,
            reg_output=WorkflowInterfaceSubfolders.mapl3_workflow_reg_folder,
        )
    )


if __name__ == "__main__":
    parser = Mapl3WorkflowParser()
    args = vars(parser.parser.parse_args())

    # Combine objects dicts
    seg_mapl3_objs.update(reg_mapl3_objs)
    mapl3_workflow_objs = seg_mapl3_objs

    # Assign the parsed args to the attributes of their respective object
    processor = MiraclArgumentProcessor()
    processor.process_miracl_objects(mapl3_workflow_objs, args)

    main(mapl3_workflow_objs)
