"""
Create an Otsu mask and masked image from an input volume using SimpleITK.

Usage:
    make_rat_brain_otsu_mask.py --input <input_image> --mask <output_mask> --masked <output_masked_image>
        [--inside <insideValue>] [--outside <outsideValue>] [--bins <numHistogramBins>]
        [--close-radius <voxels>]
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
    close_radius: int,
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
    close_radius : int
        Morphological closing radius in voxels, to bridge gaps in the raw
        Otsu mask (default 25).
    """

    # Load image as float32 to ensure stable histogram behavior
    img: sitk.Image = sitk.ReadImage(str(input_path), sitk.sitkFloat32)

    # Compute a binary Otsu mask.
    # Parameters: input, outsideValue=0, insideValue=1, numberOfHistogramBins=200
    # Settings inside/outside vals to 0 and 1 respectively means binarizing
    mask: sitk.Image = sitk.OtsuThreshold(img, outside_value, inside_value, num_bins)
    mask = sitk.Cast(mask, sitk.sitkUInt8)

    # The raw Otsu mask has internal holes where real (but dimmer) tissue gets
    # misclassified as background - a single global threshold splits the whole
    # intensity histogram into just two classes, and depth-dependent signal
    # attenuation means some real tissue voxels fall on the wrong side.
    # Confirmed on real data: the un-warped atlas itself is solid (~0.2%
    # internal gaps), but the raw mask had large holes, especially around
    # deeper structures like the hippocampus - most of them not enclosed
    # cavities but notches connected to the background at some other slice,
    # so plain hole-filling barely moved the foreground fraction (0.2119 ->
    # 0.2123). A brain mask has no biological reason to have holes; closing
    # (dilate then erode) bridges those notches regardless of topology.
    # Default radius (25) chosen empirically on real data: 20 still left one
    # hole, 25 closed it and the shape stayed stable through 35 (0.295 ->
    # 0.298 -> 0.300), so 25 has margin without over-growing the boundary.
    # Defect size varies by dataset, so override with --close-radius if a
    # different value is needed.
    if close_radius > 0:
        mask = sitk.BinaryMorphologicalClosing(mask, [close_radius] * 3, sitk.sitkBall, float(inside_value))
    mask = sitk.BinaryFillhole(mask, False, float(inside_value))

    # Apply mask (sets voxels where mask==0 to 0)
    masked_img: sitk.Image = sitk.Mask(img, mask)

    # Write outputs
    sitk.WriteImage(mask, str(mask_path))
    sitk.WriteImage(masked_img, str(masked_image_path))

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
    _ = parser.add_argument(
        "--close-radius",
        type=int,
        default=25,
        help="Morphological closing radius in voxels, to bridge gaps in the "
             "raw Otsu mask. Set to 0 to disable (default=%(default)s)",
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
        close_radius=args.close_radius,
    )


if __name__ == "__main__":
    main()
