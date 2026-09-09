"""
Create an Otsu mask and masked image from an input volume using SimpleITK.

Usage:
    make_rat_brain_otsu_mask.py --input <input_image> --mask <output_mask> --masked <output_masked_image>
        [--inside <insideValue>] [--outside <outsideValue>] [--bins <numHistogramBins>]
"""

from __future__ import annotations
from pathlib import Path
import argparse
import SimpleITK as sitk


def otsu_mask_image(
    input_path: Path,
    mask_path: Path,
    masked_image_path: Path,
    inside_value: int,
    outside_value: int,
    num_bins: int,
) -> None:
    """
    Compute a binary Otsu mask and apply it to the input image.

    Parameters
    ----------
    input_path : Path
        Path to the input 3D MRI/CT/NIfTI image.
    mask_path : Path
        Output path where the binary mask will be written.
    masked_image_path : Path
        Output path where the masked image will be written.
    inside_value : int
        Value assigned to voxels above threshold (default 1).
    outside_value : int
        Value assigned to voxels below threshold (default 0).
    num_bins : int
        Number of histogram bins used to compute threshold (default 200).
    """

    # Load image as float32 to ensure stable histogram behavior
    img: sitk.Image = sitk.ReadImage(str(input_path), sitk.sitkFloat32)

    # Compute a binary Otsu mask.
    # Parameters: input, outsideValue=0, insideValue=1, numberOfHistogramBins=200
    # Settings inside/outside vals to 0 and 1 respectively means binarizing
    mask: sitk.Image = sitk.OtsuThreshold(img, outside_value, inside_value, num_bins)

    # Apply mask (sets voxels where mask==0 to 0)
    masked_img: sitk.Image = sitk.Mask(img, mask)

    # Write outputs
    sitk.WriteImage(mask, str(out_mask_path))
    sitk.WriteImage(masked_img, str(out_masked_path))

    print(f"Otsu mask saved to:   {mask_path}")
    print(f"Masked image saved to: {masked_image_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Create a binary Otsu mask and masked image from an input volume using SimpleITK."
    )
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        required=True,
        help="Path to the input 3D Nifti image",
    )
    _ = parser.add_argument(
        "--mask",
        "-m",
        type=Path,
        required=True,
        help="Path where the binary mask will be saved",
    )
    _ = parser.add_argument(
        "--masked",
        "-o",
        type=Path,
        required=True,
        help="Path where the masked image will be saved",
    )
    _ = parser.add_argument(
        "--inside",
        type=int,
        default=1,
        help="Value assigned to voxels above threshold (default=%(default)s)",
    )
    _ = parser.add_argument(
        "--outside",
        type=int,
        default=0,
        help="Value assigned to voxels below threshold (default=%(default)s)",
    )
    _ = parser.add_argument(
        "--bins",
        type=int,
        default=200,
        help="Number of histogram bins used to compute threshold (default=%(default)s)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    otsu_mask_image(
        args.input,
        args.mask,
        args.masked,
        inside_value=args.inside,
        outside_value=args.outside,
        num_bins=args.bins,
    )


if __name__ == "__main__":
    main()
