"""
Code created and maintained by Jonas Osmann (j.osmann@alumni.utoronto.ca)

Utility fns for MIRACL to facilitate workflow specific tasks.
"""

from pathlib import Path
import re
import shutil
from miracl.system.logger import get_logger

logger = get_logger(__name__)


def create_ort2std_file(
    tifdir: str, ortcode: str, target_dir: str, dev_mode: bool = False
) -> Path:
    """
    Creates a configuration file named ort2std.txt in the specified target directory.

    The file contains two lines with the keys tifdir and ortcode set to the provided
    TIFF directory path and the uppercase orientation code, respectively.
    """
    if dev_mode:
        logger.info(
            "dev_mode=True: skipping ort2std file creation | tifdir=%s | ortcode=%s | target_dir=%s",
            tifdir,
            ortcode,
            target_dir,
        )
        return Path(target_dir) / "ort2std.txt"

    ortcode_upper = ortcode.upper()
    pattern = r"^[A-Z]{3}$"

    if not re.match(pattern, ortcode_upper):
        raise ValueError(
            f"Orientation '{ortcode} for warping must be exactly 3 letters"
        )

    tifdir_path = Path(tifdir)
    if not tifdir_path.is_dir():
        raise NotADirectoryError(f"Tiff folder path does not exist: {tifdir}")

    target_dir_path = Path(target_dir)
    if not target_dir_path.is_dir():
        raise NotADirectoryError(f"Target directory does not exist: {target_dir}")

    ort2std_file = Path(target_dir) / "ort2std.txt"

    try:
        with open(ort2std_file, "w", encoding="utf-8") as f:
            _ = f.write(f"tifdir={tifdir}\n")
            _ = f.write(f"ortcode={ortcode_upper}")
    except PermissionError:
        raise PermissionError(
            f"Permission denied: cannot write output to {ort2std_file}"
        )
    except OSError as e:
        raise OSError(f"Failed to write file {ort2std_file}: {e.strerror}") from e

    return ort2std_file


def move_warping_reg_final_contents(output_dir: str, dev_mode: bool = False) -> Path:
    """
    Move the contents of the reg_final folder in the current working directory to a
    user-specified output directory and delete reg_final.

    This is currently required since the function doesn't have an output directory flag.
    """
    if dev_mode:
        logger.info(
            "dev_mode=True: skipping reg_final move | output_dir=%s",
            output_dir,
        )
        return Path(output_dir)

    output_dir_path: Path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    reg_final: Path = Path.cwd() / "reg_final"

    try:
        if not reg_final.is_dir():
            raise FileNotFoundError(f"'reg_final' folder not found in {Path.cwd()}")

        for item in reg_final.iterdir():
            _ = shutil.move(str(item), output_dir_path)

        reg_final.rmdir()
        print(
            f"Contents of reg_final moved to {output_dir_path} and reg_final deleted."
        )

    except FileNotFoundError as e:
        raise FileNotFoundError("'reg_final' from warping is missing.") from e

    return output_dir_path


# WARNING: This function is currently not imported anywhere. Dead code?
def move_to_new_folder_and_rename(
    output_dir: str,
    input_file: str,
    identifier: str,
) -> None:
    """
    Move the specified file to a user-specified output directory and rename it.
    """
    input_file_path = Path(input_file)
    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    if not input_file_path.is_file():
        raise FileNotFoundError(f"{input_file_path} does not exist.")

    new_file_name = f"seg_feat_{identifier}_ara_lbls_split.csv"

    try:
        _ = shutil.move(input_file_path, output_dir_path / new_file_name)
        print(f"{input_file_path.name} moved to {output_dir_path}/{new_file_name}.")

    except FileNotFoundError as e:
        raise FileNotFoundError(f"Error with file: {e}")
    except PermissionError as e:
        raise PermissionError(f"Permission error: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to move the file: {e}")
