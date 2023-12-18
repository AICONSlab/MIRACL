import nibabel as nib
import tifffile
from pathlib import Path
import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--root_dir", default=Path.cwd(), help="root directory for batch conversion and appended directory for single file conversion")
    parser.add_argument(
        "-s",
        "--single",
        help="use if you only want to convert a single file - output path is root_dir",
    )
    args = parser.parse_args()
    if args.single:
        return args.root_dir, Path(args.single)
    return args.root_dir, args.single


def convert_single(input_dir, single_file):
    full_path_single_file = input_dir / single_file
    if full_path_single_file.is_file():
        print(f"dir: {input_dir}; file: {single_file}")
        img_filename = input_dir / single_file
        print(f"img filename: {img_filename}")
        while single_file.suffixes:
            single_file = single_file.with_suffix("")
        fname_out = input_dir / single_file.with_suffix(".tif")
        print(f"fname out: {fname_out}")
        img = nib.load(input_dir / img_filename)
        img_ndarray = img.get_fdata()
        print(f"Converting '{img_filename}' to '{fname_out}'")
        tifffile.imwrite(
            fname_out,
            img_ndarray.astype("float32"),
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": img_ndarray.shape[0],
                "SizeY": img_ndarray.shape[1],
                "SizeZ": img_ndarray.shape[2],
            },
        )
    else:
        print("DOES NOT WORK")


def convert_to_tif(root_dir):
    input_dir = Path(root_dir)
    for item in input_dir.iterdir():
        # if str(item) == "/data3/projects/Ahmadreza/deepneuronseg/dataset/dataset3/walking_exp/annotation_hemi_combined_10um.nii.gz":
        if (
            item.is_file()
            and item.name
            == "voxelized_seg_unetr_None_channel_allen_space_eroded.nii.gz"
        ):
            img_filename = input_dir / Path(item)
            print(f"img filename: {img_filename}")
            while item.suffixes:
                item = item.with_suffix("")
            fname_out = input_dir / item.with_suffix(".tif")
            print(f"fname out: {fname_out}")
            img = nib.load(input_dir / img_filename)
            img_ndarray = img.get_fdata()
            print(f"Converting '{img_filename}' to '{fname_out}'")
            tifffile.imwrite(
                fname_out,
                img_ndarray.astype("float32"),
                metadata={
                    "DimensionOrder": "ZYX",
                    "SizeC": 1,
                    "SizeT": 1,
                    "SizeX": img_ndarray.shape[0],
                    "SizeY": img_ndarray.shape[1],
                    "SizeZ": img_ndarray.shape[2],
                },
            )
        elif item.is_dir():
            convert_to_tif(item)


if __name__ == "__main__":
    root_dir, single_file = parse_args()
    print(f"root_dir: {root_dir}; single_file: {single_file}")
    if single_file:
        convert_single(root_dir, single_file)
    sys.exit()
    convert_to_tif(root_dir)
