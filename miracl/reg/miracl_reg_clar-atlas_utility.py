from pathlib import Path
import tifffile
import numpy as np
from typing import Union
from os import PathLike
import argparse


def extract_tiff_slices(
    input_file: Union[str, PathLike],
    output_dir: Union[str, PathLike],
    raw_slice_name_template: str,
) -> None:
    """
    Extract slices from a TIFF stack.

    Args:
        input_file (Union[str, PathLike]): Path to the input TIFF file.
        output_dir (Union[str, PathLike]): Directory to save extracted slices.
        raw_slice_name_template (str): Template for naming output files (e.g., "lbls_slice_%06d.tif").

    Raises:
        FileNotFoundError: If input_file doesn't exist.
        NotADirectoryError: If output_dir is not a directory.
    """
    input_path = Path(input_file)
    output_path = Path(output_dir)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not output_path.is_dir():
        raise NotADirectoryError(f"Output directory is not valid: {output_path}")

    with tifffile.TiffFile(input_path) as tif:
        stack = tif.asarray()

    for z in range(stack.shape[0]):
        slice_data = stack[z, :, :].astype(np.uint16)
        img_filename = output_path / (raw_slice_name_template % z)
        print(f"Saving img: {img_filename}")
        tifffile.imwrite(
            img_filename,
            slice_data,
            metadata={
                "DimensionOrder": "YX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": slice_data.shape[1],
                "SizeY": slice_data.shape[0],
            },
        )


def main() -> None:
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Extract slices from a tif stack.")

    # Add arguments to the parser
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input tif file",
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Directory to save extracted tiff slices",
    )
    parser.add_argument(
        "raw_slice_name_template",
        type=str,
        help="Template for naming extracted tif slices files",
    )

    # Parse arguments
    args = parser.parse_args()

    # Call the function with parsed arguments
    extract_tiff_slices(args.input_file, args.output_dir, args.raw_slice_name_template)


# Ensure the script runs only when called directly
if __name__ == "__main__":
    main()
