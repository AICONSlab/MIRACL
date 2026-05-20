"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Utility fns for path validation stuff. Will probably grow beyond just validation.
"""

from pathlib import Path
from miracl.system.logger import get_logger

logger = get_logger(__name__)


class UtilfnsPaths:
    @staticmethod
    def ensure_folder_exists(folder_path: Path, dev_mode: bool = False) -> None:
        """
        Check if a folder exists and create it if it doesn't.

        Args:
            folder_path: A Path object representing the folder path.
            dev_mode: If True, simulates the operation without creating the folder on
                      disk. Useful for dry-run testing. Shows up in debug log msg.

        Raises:
            PermissionError: If the folder cannot be created due to insufficient
                permissions.
            OSError: If the folder cannot be created for any other OS-level reason.
        """
        if dev_mode:
            logger.info(f"dev_mode=True | Skipping folder creation: {folder_path}")
            return

        try:
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Folder created: {folder_path}")
            else:
                logger.debug(f"Folder already exists: {folder_path}")
        except PermissionError as e:
            logger.error(
                f"Permission denied creating folder: {folder_path}. Error: {e}"
            )
            raise
        except OSError as e:
            logger.error(f"Failed to create folder: {folder_path}. Error: {e}")
            raise

    @staticmethod
    def ensure_file_exists(file_path: Path) -> None:
        """
        Check if a file exists at a file path.

        :raises FileNotFoundError: If the file does not exist
        :raises OSError: If there's an issue accessing the file
        """
        try:
            if file_path.is_file():
                logger.debug(f"The file exists: {file_path}")
            else:
                raise FileNotFoundError(f"The file does not exist: {file_path}")
        except OSError as e:
            logger.error(f"Error accessing file: {file_path}. Error: {e}")
            raise
