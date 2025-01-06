from abc import abstractmethod, ABC
import miracl.seg.mapl3.mapl3_interface as mapl3_seg_interface
from miracl.seg.mapl3.mapl3_cli_parser import Mapl3Parser
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


def main():
    mapl3_interface = MAPL3Interface()
    miracl_registration = MIRACLRegistration()

    generate_patch_input_folder = mapl3_interface.execute_mapl3_interface()
    miracl_registration.execute_miracl_registration(generate_patch_input_folder)


if __name__ == "__main__":
    main()
