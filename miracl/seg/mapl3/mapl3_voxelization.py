"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)

This script voxelizes the segmentation output by downsampling a 3D TIFF file (passed as a series of 2D slices) along the YX and Z axes.
It supports parallel processing for efficient computation and allows the user to specify the downsampling method
(e.g., max, mean, sum, min) and factors for each axis.

Command-line Arguments:
------------------------
-i, --input: Path to the input TIFF file (required).
-o, --out_dir: Path to the output directory (required).
-c, --cpu_load: Fraction of CPUs to use for parallel processing (default: 0.5).
-dx, --downsample_yx_axis: Downsampling factor for the Y and X axes (default: 10).
-dz, --downsample_z_axis: Downsampling factor for the Z axis (default: 10).
-m, --method: Downsampling method (e.g., max, mean, sum, min) (default: 'max').
Usage:
------
Run the script from the command line with the required arguments. For example:
    python aa_deeptrace_voxelization.py -i input.tif -o output_dir -c 0.8 -dx 8 -dz 5 -m mean

"""

import numpy as np
import tifffile
import os
import sys
import argparse
import multiprocessing
from joblib import Parallel, delayed, parallel_config
import multiprocessing
from scipy import ndimage
from skimage.measure import block_reduce
import nibabel as nib

# -------------------------------------------------------
# create parser
# -------------------------------------------------------
my_parser = argparse.ArgumentParser(description="Working directory")

# Add the arguments
my_parser.add_argument(
    "-i",
    "--input",
    help="input tif/tiff directory; this should be a folder containing binary slices through z",
    required=True,
)
my_parser.add_argument(
    "-o",
    "--out_dir",
    help="path of output directory",
    required=True,
)
my_parser.add_argument(
    "-c",
    "--cpu_load",
    help="fraction of cpus to be used for parallelization between 0-1",
    required=False,
    default=0.5,
    type=float,
)
my_parser.add_argument(
    "-dx",
    "--downsample_yx_axis",
    help="downsample ration for y and x axis",
    required=False,
    default=10,
    type=int,
)
my_parser.add_argument(
    "-dz",
    "--downsample_z_axis",
    help="downsample ration for z axis",
    required=False,
    default=10,
    type=int,
)
my_parser.add_argument(
    "-m",
    "--method",
    help="method for downsampling acceptable sum, min, max, mean, median",
    required=False,
    default="sum",
    type=str,
    choices=["sum", "min", "max", "mean", "median"],
)
my_parser.add_argument(
    "-n",
    "--out_name",
    help="output name",
    required=False,
    default="voxelized_results",
    type=str,
)
my_parser.add_argument(
    "-vx",
    "--res_xy",
    help="resolution of the input in x and y in um",
    required=False,
    default=1.0,
    type=float,
)
my_parser.add_argument(
    "-vz",
    "--res_z",
    help="resolution of the input in z in um",
    required=False,
    default=1.0,
    type=float,
)


# -------------------------------------------------------
# save function
# -------------------------------------------------------
def save_tiff(img, name, dir, type):
    tifffile.imwrite(
        os.path.join(dir, name),
        img.astype(type),
        metadata={
            "DimensionOrder": "YX",
            "SizeC": 1,
            "SizeT": 1,
            "SizeX": img.shape[1],
            "SizeY": img.shape[0],
        },
    )


# -------------------------------------------------------
# downsample functions (modified to return index)
# -------------------------------------------------------
def downsample_yx_slice(file_name_paths, z_idx, factor_xy, method="max"):
    """
    Downsample a single YX slice and return it with its original z-index.

    Args:
        slice_2d (np.ndarray): 2D slice (Y, X).
        z_idx (int): Original z-index of the slice.
        factor_xy (int): Downsampling factor for X and Y.
        method (str): 'max' or 'mean'.

    Returns:
        tuple: (z_idx, downsampled_slice)
    """
    print(f"voxelizing slice: {z_idx} ...")
    slice_2d = tifffile.imread(file_name_paths[z_idx]).astype("uint8")

    # Map user-input strings to NumPy functions
    FUNC_MAP = {
        "max": np.max,
        "mean": np.mean,
        "sum": np.sum,
        "min": np.min,
        # Add more as needed
    }
    # Get the reduction function from the dictionary
    try:
        func = FUNC_MAP[method.lower()]
    except KeyError:
        raise ValueError(
            f"Unknown method '{method}'. Valid options: {list(FUNC_MAP.keys())}"
        )

    return (z_idx, block_reduce(slice_2d, block_size=(factor_xy, factor_xy), func=func))


def downsample_z(volume, factor_z):
    """
    Downsample along Z axis using nearest-neighbor interpolation.
    """
    print(f"downsampling in depth (z)...")
    zoom_factors = (1.0 / factor_z, 1, 1)  # Only downsample Z
    return ndimage.zoom(volume, zoom_factors, order=0)


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main():
    # Execute the parse_args() method
    args = vars(my_parser.parse_args())
    input_file_path = args["input"]
    out_dir = args["out_dir"]
    cpu_load = args["cpu_load"]
    dx = args["downsample_yx_axis"]
    dz = args["downsample_z_axis"]
    method = args["method"]
    vx = args["res_xy"]
    vz = args["res_z"]
    out_name = args["out_name"]

    # print all the input parameters
    print("\nRunning voxelization with the following settings:")
    print(f"input_file_path:    {input_file_path}")
    print(f"out_dir:            {out_dir}")
    print(f"cpu_load:           {cpu_load}")
    print(f"downsample_yx_axis: {dx}")
    print(f"downsample_z_axis:  {dz}")
    print(f"method:             {method}")
    print(f"res_x:              {vx}")
    print(f"res_z:              {vz}")
    print(f"out_name:           {out_name}")

    # create out dir
    isExist = os.path.exists(out_dir)
    if not isExist:
        os.mkdir(out_dir)

    # load image
    file_names = os.listdir(input_file_path)
    file_names.sort()
    file_names_paths = [
        os.path.join(input_file_path, file)
        for file in file_names
        if file.endswith(".tiff") or file.endswith(".tif")
    ]
    print(f"found {len(file_names_paths)} files in the input directory")

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    # Downsample XY slices in parallel
    with parallel_config(backend="loky", n_jobs=ncpus):
        results = Parallel()(
            delayed(downsample_yx_slice)(
                file_names_paths,  # Pass the 2D slice
                z,  # Pass its original index
                factor_xy=dx,  # Example factor
                method=method,  # Preserve fibers
            )
            for z in range(len(file_names_paths))
        )

    # Sort results by z-index and stack
    results_sorted = sorted(results, key=lambda x: x[0])
    downsampled_yx = np.stack([result[1] for result in results_sorted], axis=0)

    # Downsample Z axis
    downsampled_zyx = downsample_z(downsampled_yx, factor_z=dz)

    # Save output as tiff
    save_tiff(downsampled_zyx, out_name + ".tif", out_dir, np.uint8)

    # save output as nifti
    mat = np.eye(4)
    vx = (vx / 1000) * dx
    vz = (vz / 1000) * dz

    mat[0, 0] = vx
    mat[1, 1] = vx
    mat[2, 2] = vz

    img = nib.Nifti1Image(downsampled_zyx.astype("uint8"), mat)
    nib.save(img, os.path.join(out_dir, out_name + ".nii.gz"))
    print(f"results saved in '{out_dir}'")


if __name__ == "__main__":
    main()
