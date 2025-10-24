from pathlib import Path
import os
import re


def create_ort2std_file(tifdir: str, ortcode: str, target_dir: str) -> None:
    """
    Creates a configuration file named 'ort2std.txt' in the specified target directory.

    The file contains two lines with the keys 'tifdir' and 'ortcode' set to the provided
    TIFF directory path and the uppercase orientation code, respectively.

    Args:
        tifdir (str): Path to the TIFF directory. Must exist and be a directory.
        ortcode (str): Orientation code string. Must be exactly three alphabetic characters.
        target_dir (str): Directory path where the 'ort2std.txt' file will be created.
                          Must be writable.

    Raises:
        ValueError: If `ortcode` is not exactly three alphabetic characters.
        NotADirectoryError: If `tifdir` does not exist or is not a directory.
        PermissionError: If the program lacks permission to write to the `target_dir`.
        OSError: If writing the file fails due to other OS-related errors.
    """
    ortcode_upper = ortcode.upper()
    pattern = r"^[A-Z]{3}$"

    if not re.match(pattern, ortcode_upper):
        raise ValueError(
            f"Orientation '{ortcode} for warping must be exactly 3 letters"
        )

    tifdir_path = Path(tifdir)
    if not tifdir_path.is_dir():
        raise NotADirectoryError(f"Tiff folder path does not exist: {tifdir}")

    if not os.access(tifdir_path, os.W_OK):
        raise PermissionError(f"No write permission for directory: {tifdir}")

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
