from pathlib import Path
from miracl import miracl_logger
from miracl.system.datamodels.datamodel_miracl_objs import MiraclObj

logger = miracl_logger.logger


class MAPL3BaseFolderHandler:
    """
    A handler for managing and validating `dirpath` attributes of the MIRACL objects
    holding the filepaths to the base results folder that contains all
    subfolders for the methods.
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
        Handle the dirpath attribute of two MiraclObj objects.
        """
        cls.validate_dirpath_attribute(full_base_folder)
        cls.validate_dirpath_attribute(parsed_base_folder)
        cls.validate_dirpath_value(parsed_base_folder)

        assert parsed_base_folder.dirpath is not None, (
            "parsed_base_folder.dirpath should not be None after validation"
        )

        expected_path = parsed_base_folder.dirpath / "mapl3"

        if full_base_folder.dirpath is None:
            full_base_folder.dirpath = expected_path
            logger.debug(
                f"Assigned dirpath for full_base_folder: {full_base_folder.dirpath}"
            )
        elif full_base_folder.dirpath != expected_path:
            raise ValueError(
                f"The dirpath of full_base_folder is incorrect. Expected {expected_path}, but got {full_base_folder.dirpath}"
            )

        cls.create_directory(full_base_folder.dirpath)
