# from pathlib import Path
# import logging
# from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj
#
# logging.basicConfig(level=logging.INFO)
#
#
# class MAPL3BaseFolderHandler:
#     """
#     A handler for managing and validating `dirpath` attributes of the MIRACL
#     objects holding the filepaths to the base results folder that contains all
#     subfolders for the methods.
#
#     This class encapsulates the logic for ensuring that the `dirpath` attribute of one
#     `MiraclObj` object (`full_base_folder`) is correctly set based on another `MiraclObj` object (`parsed_base_folder`).
#     It also ensures that the corresponding directory exists on the filesystem.
#
#     :param full_base_folder: The primary object whose `dirpath` is being managed.
#     :type full_base_folder: MiraclObj
#     :param parsed_base_folder: The secondary object providing the base path for validation.
#     :type parsed_base_folder: MiraclObj
#
#     :raises AttributeError: If `full_base_folder` does not have a `dirpath` attribute.
#     :raises ValueError: If `parsed_base_folder.dirpath` is `None`, or if `full_base_folder.dirpath` does not match
#                         the expected path derived from `parsed_base_folder.dirpath`.
#     """
#
#     def __init__(self, full_base_folder: MiraclObj, parsed_base_folder: MiraclObj):
#         self.full_base_folder = full_base_folder
#         self.parsed_base_folder = parsed_base_folder
#
#     def validate_full_base_folder_dirpath(self) -> None:
#         if not hasattr(self.full_base_folder, "dirpath"):
#             raise AttributeError(
#                 "The first object does not have a 'dirpath' attribute."
#             )
#
#     def validate_parsed_base_folder_dirpath(self) -> None:
#         if self.parsed_base_folder.dirpath is None:
#             raise ValueError("The second object's 'dirpath' attribute cannot be None.")
#
#     def create_directory(self, path: Path) -> None:
#         if path.exists():
#             logging.info(f"The folder {path} already exists.")
#         else:
#             path.mkdir(parents=True, exist_ok=True)
#             logging.info(f"Created the folder {path}")
#
#     def handle_dirpath(self) -> None:
#         """
#         Handle the 'dirpath' attribute of two MiraclObj objects.
#
#         :raises AttributeError: If full_base_folder does not have a 'dirpath' attribute.
#         :raises ValueError: If parsed_base_folder's dirpath is None or if full_base_folder's dirpath doesn't match the expected path.
#         :return: None
#         :rtype: None
#
#         .. note::
#            This method may modify full_base_folder's dirpath attribute and create a new directory on the filesystem.
#         """
#         self.validate_full_base_folder_dirpath()
#         self.validate_parsed_base_folder_dirpath()
#
#         expected_path = self.parsed_base_folder.dirpath / "mapl3"
#
#         if self.full_base_folder.dirpath is None:
#             self.full_base_folder.dirpath = expected_path
#             logging.info(
#                 f"Assigned dirpath for object 1: {self.full_base_folder.dirpath}"
#             )
#         elif self.full_base_folder.dirpath != expected_path:
#             raise ValueError(
#                 f"The dirpath of object 1 is incorrect. Expected {expected_path}, but got {self.full_base_folder.dirpath}"
#             )
#
#         self.create_directory(self.full_base_folder.dirpath)
#
#
# # Example usage
# if __name__ == "__main__":
#     # Assuming MiraclObj is imported and properly defined
#     parsed_base_folder = MiraclObj(dirpath=Path("/home/user"))
#     full_base_folder = MiraclObj(dirpath=None)
#     handler = MAPL3BaseFolderHandler(full_base_folder, parsed_base_folder)
#     handler.handle_dirpath()

from pathlib import Path
from miracl import miracl_logger
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

logger = miracl_logger.logger


class MAPL3BaseFolderHandler:
    """
    A handler for managing and validating `dirpath` attributes of the MIRACL
    objects holding the filepaths to the base results folder that contains all
    subfolders for the methods.

    This class encapsulates the logic for ensuring that the `dirpath` attribute of one
    `MiraclObj` object (`full_base_folder`) is correctly set based on another `MiraclObj`
    object (`parsed_base_folder`). It also ensures that the corresponding directory
    exists on the filesystem.

    :raises AttributeError: If either `full_base_folder` or `parsed_base_folder` does not
                            have a `dirpath` attribute.
    :raises ValueError: If `parsed_base_folder.dirpath` is `None`, or if
                        `full_base_folder.dirpath` does not match the expected path
                        derived from `parsed_base_folder.dirpath`.
    """

    @staticmethod
    def validate_dirpath_attribute(obj: MiraclObj) -> None:
        if not hasattr(obj, "dirpath"):
            raise AttributeError(
                f"The {obj.__class__.__name__} does not have a 'dirpath' attribute."
            )

    @staticmethod
    def validate_dirpath_value(obj: MiraclObj) -> None:
        if obj.dirpath is None:
            raise ValueError(
                f"The {obj.__class__.__name__}'s 'dirpath' attribute cannot be None."
            )

    @staticmethod
    def create_directory(path: Path) -> None:
        if path.exists():
            logger.debug(f"The folder {path} already exists.")
        else:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created the folder {path}")

    @classmethod
    def handle_dirpath(
        cls, full_base_folder: MiraclObj, parsed_base_folder: MiraclObj
    ) -> None:
        """
        Handle the 'dirpath' attribute of two MiraclObj objects.

        :param full_base_folder: The primary object whose `dirpath` is being managed.
        :type full_base_folder: MiraclObj
        :param parsed_base_folder: The secondary object providing the base path for validation.
        :type parsed_base_folder: MiraclObj
        :raises AttributeError: If either object does not have a 'dirpath' attribute.
        :raises ValueError: If parsed_base_folder's dirpath is None or if full_base_folder's
                            dirpath doesn't match the expected path.
        :return: None
        :rtype: None

        .. note::
           This method may modify full_base_folder's dirpath attribute and create a new
           directory on the filesystem.
        """
        cls.validate_dirpath_attribute(full_base_folder)
        cls.validate_dirpath_attribute(parsed_base_folder)
        cls.validate_dirpath_value(parsed_base_folder)

        assert (
            parsed_base_folder.dirpath is not None
        ), "parsed_base_folder.dirpath should not be None after validation"

        expected_path = parsed_base_folder.dirpath / "mapl3"

        if full_base_folder.dirpath is None:
            full_base_folder.dirpath = expected_path
            logger.debug(
                f"Assigned dirpath for full_base_folder: {full_base_folder.dirpath}"
            )
        elif full_base_folder.dirpath != expected_path:
            raise ValueError(
                f"The dirpath of full_base_folder is incorrect. "
                f"Expected {expected_path}, but got {full_base_folder.dirpath}"
            )

        cls.create_directory(full_base_folder.dirpath)


# Example usage
# if __name__ == "__main__":
#     parsed_base_folder = MiraclObj(dirpath=Path("/home/user"))
#     full_base_folder = MiraclObj(dirpath=None)
#     MAPL3BaseFolderHandler.handle_dirpath(full_base_folder, parsed_base_folder)
