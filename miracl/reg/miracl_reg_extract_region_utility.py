import argparse
import sys

import nibabel as nib
import numpy as np


def compute_crop_offset(data, target_x, target_y, target_z):
    """
    Compute the voxel offset to extract a target_x x target_y x target_z region
    from data, reversing the symmetric padding added earlier in the pipeline
    (-pad 30% 30% 0, applied equally on both sides of every axis).

    This was previously changed to center on the bounding box of nonzero
    content instead, based on a misdiagnosis: the original all-zero crop that
    motivated that change was actually caused by a separate c3d `-region`
    overflow bug (see crop_and_save), not by this offset being wrong. Bounding-
    box centering doesn't know how much of that box is real padding vs where
    the pad step actually put the content, so it silently produces a crop
    that's shifted relative to the reference image - confirmed by the shift
    matching (symmetric_offset - bbox_offset) almost exactly. Since the pad
    is symmetric, (dim - target) / 2 is the correct offset.
    """
    dims = np.array(data.shape[:3])
    target = np.array([target_x, target_y, target_z])

    offset = (dims - target) // 2

    return offset


def crop_and_save(input_file, target_x, target_y, target_z, reference_file, output_file):
    """
    Extract a target_x x target_y x target_z region containing the real
    (nonzero) content of input_file, place it in reference_file's coordinate
    space, cast to uint32, and write it to output_file.

    Done directly in nibabel/numpy rather than via c3d (`-region`, then
    `-copy-transform`, then `-type uint`): both `-region` and the
    `-copy-transform ... -o` write path silently corrupt output on this data
    (confirmed separately for each - `-region` returns all-zero past 2^31
    elements; `-copy-transform`'s write truncated ~55% of the z-extent even
    without erroring). input_file here is ~7.5B elements, well past where
    c3d has been shown to break, so none of these three steps should shell
    out to c3d.
    """
    img = nib.load(input_file)
    data = np.asarray(img.dataobj)

    offset = compute_crop_offset(data, target_x, target_y, target_z)
    ox, oy, oz = offset

    cropped = data[ox:ox + target_x, oy:oy + target_y, oz:oz + target_z]

    reference_affine = nib.load(reference_file).affine
    cropped_img = nib.Nifti1Image(cropped.astype(np.uint32), reference_affine)
    nib.save(cropped_img, output_file)

    return offset


def main():
    parser = argparse.ArgumentParser(
        description="Extract a region containing the actual labeled content "
                    "of a nifti volume, place it in a reference image's "
                    "coordinate space, and cast to uint32."
    )
    parser.add_argument("input_file", type=str, help="Path to the input nifti file")
    parser.add_argument("target_x", type=int, help="Target region size in x")
    parser.add_argument("target_y", type=int, help="Target region size in y")
    parser.add_argument("target_z", type=int, help="Target region size in z")
    parser.add_argument("reference_file", type=str,
                        help="Path to the nifti whose affine/direction the output should adopt")
    parser.add_argument("output_file", type=str, help="Path to write the cropped nifti to")

    args = parser.parse_args()

    offset = crop_and_save(
        args.input_file, args.target_x, args.target_y, args.target_z,
        args.reference_file, args.output_file
    )
    print(f"offset used: {offset[0]} {offset[1]} {offset[2]}", file=sys.stderr)


if __name__ == "__main__":
    main()
