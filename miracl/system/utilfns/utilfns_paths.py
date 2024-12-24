from pathlib import Path
from miracl import miracl_logger

logger = miracl_logger.logger


class UtilfnsPaths:
    @staticmethod
    def ensure_folder_exists(folder_path: Path) -> None:
        """
        Check if a folder exists and create it if it doesn't.

        This method checks for the existence of a folder at the specified path.
        If the folder doesn't exist, it creates it along with any necessary
        parent directories.

        :param folder_path: A Path object representing the folder path
        :type folder_path: Path
        :return: None
        :rtype: None

        :raises OSError: If the folder cannot be created due to permissions or other OS-level issues

        :example:
        >>> from pathlib import Path
        >>> UtilfnsPaths.ensure_folder_exists(Path("/path/to/new/folder"))
        Folder created: /path/to/new/folder
        """
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Folder created: {folder_path}")
        else:
            logger.debug(f"Folder already exists: {folder_path}")
