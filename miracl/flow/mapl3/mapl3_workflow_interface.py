"""
This code is written by Jonas Osmann (j.osmann@alumni.utoronto.ca) for
Ahmadreza Attapour's (a.attarpour@mail.utoronto.ca) MAPL3 implementation into
AICONs lab's MIRACL.

This code is an interface for the the MAPL3 workflow.
"""

# Import Python libs to load MIRACL env var, handle file/folder paths as Path
# objects and to call Bash modules (reg) from this Python script
from os import environ
from pathlib import Path
import subprocess
from typing import Dict, Any

# Import class modules to construct interface in Python
from abc import abstractmethod, ABC
from dataclasses import dataclass

# Import MAPL3 module interface for implementation into the workflow interface
from miracl.seg.mapl3 import mapl3_interface
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

# Subfolder objs used to create results folders for modules in workflow
from miracl.system.objs.objs_flow.objs_mapl3_workflow.objs_mapl3_workflow_interface_folders import (
    WorkflowInterfaceSubfolders,
)

from miracl.flow.mapl3.mapl3_workflow_cli_parser import Mapl3WorkflowParser
from miracl.seg.mapl3.mapl3_cli_parser_args import mapl3_object_dict as seg_mapl3_objs
from miracl.flow.mapl3.mapl3_workflow_cli_parser_args import (
    reg_object_dict as reg_mapl3_objs,
    conv_object_dict as conv_mapl3_objs,
)

from miracl.system.utilfns.utilfn_cli_parser_creator import MiraclArgumentProcessor
from miracl import miracl_logger
from logging import Logger

###############################################################################

#############
# DEBUGGING #
#############

logger: Logger = miracl_logger.logger

############
# ENV VARS #
############

MIRACL_HOME = Path(environ["MIRACL_HOME"])

###############################################################################

####################
# ABSTRACT METHODS #
####################


@dataclass
class Mapl3InterfaceParams:
    """
    Parameters for the MAPL3 interface.

    :param objs: Dictionary containing MAPL3 objects
    :type objs: dict
    """

    objs: dict


class Interface(ABC):
    @abstractmethod
    def call_mapl3_interface(self, params: Mapl3InterfaceParams) -> Dict[str, Any]:
        """
        Abstract method to call the MAPL3 interface.

        :param params: Parameters for the MAPL3 interface
        :type params: Mapl3InterfaceParams
        :return: Dictionary containing MAPL3 subfolder objects
        :rtype: Dict[str, Any]
        """
        pass


@dataclass
class ConversionParams:
    """
    Parameters for the conversion process.

    :param mapl3_objs: Dictionary containing MAPL3 objects
    :type mapl3_objs: dict
    :param conv_output: Output object for conversion
    :type conv_output: MiraclObj
    """

    mapl3_objs: dict
    conv_output: MiraclObj


class Conversion(ABC):
    @abstractmethod
    def call_miracl_conversion(self, params: ConversionParams) -> None:
        """
        Abstract method to call the MIRACL's conversion module.

        :param params: Parameters for the conversion process
        :type params: ConversionParams
        :return: None
        """
        pass


@dataclass
class RegistrationParams:
    """
    Parameters for the registration process.

    :param mapl3_objs: Dictionary containing MAPL3 objects
    :type mapl3_objs: dict
    :param subfolder_objs: Dictionary containing subfolder objects
    :type subfolder_objs: dict
    :param reg_output: Output object for registration
    :type reg_output: MiraclObj
    :param nii_file: Path to the NIfTI file
    :type nii_file: Path
    """

    mapl3_objs: dict
    subfolder_objs: dict
    reg_output: MiraclObj
    nii_file: Path


class Registration(ABC):
    @abstractmethod
    def call_miracl_registration(self, params: RegistrationParams) -> None:
        """
        Abstract method to call MIRACL's registration module.

        :param params: Parameters for the registration process
        :type params: RegistrationParams
        :return: None
        """
        pass


###############################################################################

####################
# CONCRETE CLASSES #
####################


class MAPL3Interface(Interface):

    def call_mapl3_interface(self, params: Mapl3InterfaceParams) -> Dict[str, Any]:
        """
        Call the MAPL3 interface for segmentation.

        :param params: Parameters for the MAPL3 interface
        :type params: Mapl3InterfaceParams
        :return: Dictionary of MAPL3 subfolder objects
        :rtype: dict
        """

        logger.debug("##################################")
        logger.debug("SEGMENTATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")

        mapl3_subfolders_objs_dict = mapl3_interface.main(params.objs)
        return mapl3_subfolders_objs_dict


class MIRACLConversion(Conversion):

    def call_miracl_conversion(self, params: ConversionParams) -> None:
        """
        Call the MIRACL's conversion module.

        :param params: Parameters for the conversion process
        :type params: ConversionParams
        :return: None
        """

        logger.debug("################################")
        logger.debug("CONVERSION IN WORKFLOW INTERFACE")
        logger.debug("################################")

        # RAW TIFF files folder is a variables from the genpatch MAPL3 module
        # The output folder for the conversion results is generated here in
        # the workflow
        conv_cmd = f"{MIRACL_HOME}/conv/miracl_conv_convertTIFFtoNII.py \
        --{params.mapl3_objs['conv_tiff_to_nii'].tiff_folder.cli_l_flag} \
        {params.mapl3_objs['seg_genpatch'].input.dirpath} \
        --{params.mapl3_objs['conv_tiff_to_nii'].output_folder.cli_l_flag} \
        {params.conv_output.dirpath} \
        --{params.mapl3_objs['conv_tiff_to_nii'].down.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].down.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].channum.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].channum.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].chanprefix.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].chanprefix.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].channame.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].channame.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].outnii.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].outnii.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].resx.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].resx.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].resz.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].resz.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].center.cli_l_flag} \
        {' '.join(map(str, params.mapl3_objs['conv_tiff_to_nii'].center.content))} \
        --{params.mapl3_objs['conv_tiff_to_nii'].downzdim.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].downzdim.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].prevdown.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].prevdown.content} \
        --{params.mapl3_objs['conv_tiff_to_nii'].percentile_thr.cli_l_flag} \
        {params.mapl3_objs['conv_tiff_to_nii'].percentile_thr.content}"

        logger.debug(f"conv_cmd: {' '.join(conv_cmd.split())}")
        subprocess.Popen(conv_cmd, shell=True).wait()


class MIRACLRegistration(Registration):

    def call_miracl_registration(self, params: RegistrationParams) -> None:
        """
        Call MIRACL's registration module.

        :param params: Parameters for the registration process
        :type params: RegistrationParams
        :return: None
        """

        logger.debug("##################################")
        logger.debug("REGISTRATION IN WORKFLOW INTERFACE")
        logger.debug("##################################")

        # The file path to the converted NIFTI files comes from the conversion
        # RAW TIFF files folder is a variables from the genpatch MAPL3 module
        # The output folder for the registration results is generated here in
        # the workflow
        reg_cmd = f"{MIRACL_HOME}/reg/miracl_reg_clar-allen.sh \
        -{params.mapl3_objs['reg_clar_allen_reg'].nii_folder.cli_s_flag} \
        {params.nii_file} \
        -{params.mapl3_objs['reg_clar_allen_reg'].tiff_folder.cli_s_flag} \
        {params.subfolder_objs['patch_stacking_output'].dirpath} \
        -{params.mapl3_objs['reg_clar_allen_reg'].output_path.cli_s_flag} \
        {params.reg_output.dirpath} \
        -{params.mapl3_objs['reg_clar_allen_reg'].orient_code.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].orient_code.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].hemi.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].hemi.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].voxel_size.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].voxel_size.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].allen_label.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].allen_label.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].allen_atlas.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].allen_atlas.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].side.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].side.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].no_mosaic_fig.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].no_mosaic_fig.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].olfactory_bulb.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].olfactory_bulb.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].skip_cor.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].skip_cor.content} \
        -{params.mapl3_objs['reg_clar_allen_reg'].warp.cli_s_flag} \
        {params.mapl3_objs['reg_clar_allen_reg'].warp.content}"

        logger.debug(f"reg_cmd: {' '.join(reg_cmd.split())}")
        subprocess.Popen(reg_cmd, shell=True).wait()


def main(objs: dict) -> None:
    """
    Main function to run the MAPL3 workflow.

    This function orchestrates the MAPL3 interface, conversion, and registration modules.

    :param objs: Dictionary containing MAPL3 objects
    :type objs: dict
    :return: None
    """

    #####################
    # METHOD INVOCATION #
    #####################

    mapl3_interface = MAPL3Interface()
    miracl_registration = MIRACLRegistration()
    miracl_conversion = MIRACLConversion()

    # Run MAPL3 module interface and return subfolder objs dict
    mapl3_subfolders_objs_dict = mapl3_interface.call_mapl3_interface(
        Mapl3InterfaceParams(objs=objs)
    )

    # Assign base conversion output folder
    WorkflowInterfaceSubfolders.mapl3_workflow_conv_folder.dirpath = (
        mapl3_subfolders_objs_dict["mapl3_results_base_folder"].dirpath / "conv"
    )

    # Run conversion
    miracl_conversion.call_miracl_conversion(
        ConversionParams(
            mapl3_objs=objs,
            conv_output=WorkflowInterfaceSubfolders.mapl3_workflow_conv_folder,
        )
    )

    # Assign base registration output folder
    WorkflowInterfaceSubfolders.mapl3_workflow_reg_folder.dirpath = (
        mapl3_subfolders_objs_dict["mapl3_results_base_folder"].dirpath / "reg"
    )

    # Construct NIFTI file string from conv output
    nii_file_outnii: str = objs["conv_tiff_to_nii"].outnii.content
    nii_file_down_int: int = objs["conv_tiff_to_nii"].down.content
    nii_file_down: str = (
        f"0{nii_file_down_int}"
        if 1 <= int(nii_file_down_int) <= 9
        else str(nii_file_down_int)
    )
    nii_file_channame: str = objs["conv_tiff_to_nii"].channame.content
    nii_file_from_conv: Path = (
        WorkflowInterfaceSubfolders.mapl3_workflow_conv_folder.dirpath
        / f"{nii_file_outnii}_{nii_file_down}dx_down_{nii_file_channame}_chan.nii.gz"
    )

    # Run registration
    miracl_registration.call_miracl_registration(
        RegistrationParams(
            mapl3_objs=objs,
            subfolder_objs=mapl3_subfolders_objs_dict,
            reg_output=WorkflowInterfaceSubfolders.mapl3_workflow_reg_folder,
            nii_file=nii_file_from_conv,
        )
    )


if __name__ == "__main__":
    parser: Mapl3WorkflowParser = Mapl3WorkflowParser()
    args: Dict[str, Any] = vars(parser.parser.parse_args())

    # Combine objects dicts
    mapl3_workflow_objs: Dict[str, Any] = {
        **seg_mapl3_objs,
        **reg_mapl3_objs,
        **conv_mapl3_objs,
    }

    # Assign the parsed args to the attributes of their respective object
    processor: MiraclArgumentProcessor = MiraclArgumentProcessor()
    processor.process_miracl_objects(mapl3_workflow_objs, args)

    main(mapl3_workflow_objs)
