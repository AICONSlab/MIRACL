"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)
This code uses the probability map, raw image, and the brain mask to create a new probability map
It applies the mask to the probability map and then applies a linear mixation of the probability map and the raw image (normalized intensity)
It then binarizes the probability map and saves it

main inputs:
    -i/--input: input probability map directory
    -r/--raw_data: input raw image directory
    -m/--brain_mask: input brain mask directory
    -o/--out_dir: output directory
    -ne/--num_erosion: number of times to erode the mask
    -t/--thr: threshold for binarization
    -c/--cpu_load: fraction of cpus to be used for parallelization between 0-1

main outputs:
    - a binarized map that is saved in the output directory


"""

import numpy as np
import tifffile
import os
import sys
import argparse
from pathlib import Path
import multiprocessing
from joblib import Parallel, delayed, parallel_config
import multiprocessing
import scipy.ndimage as scp
import pandas as pd

# -------------------------------------------------------
# create parser
# -------------------------------------------------------
my_parser = argparse.ArgumentParser(description="Working directory")

# Add the arguments
my_parser.add_argument(
    "-i",
    "--input",
    help="input tif/tiff probability map",
    required=True,
)
my_parser.add_argument(
    "-r",
    "--raw_data",
    help="input tif/tiff raw",
    required=True,
)
my_parser.add_argument(
    "-m",
    "--brain_mask",
    help="input brain mask tif/tiff directory",
    required=True,
)
my_parser.add_argument(
    "-ne",
    "--num_erosion",
    help="how many times run binary erosion on the mask",
    required=False,
    default=50,
    type=int,
)
my_parser.add_argument(
    "-a",
    "--alpha",
    help="alpha for linear mixation of probability map and raw image; 0 (only model) 1 (only raw image)",
    required=False,
    default=0.5,
    type=float,
)
my_parser.add_argument(
    "-t",
    "--thr",
    help="threshold for binarization",
    required=False,
    default=0.5,
    type=float,
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
            "SizeX": img.shape[0],
            "SizeY": img.shape[1],
        },
    )


# -------------------------------------------------------
# skeletonize function
# -------------------------------------------------------
def aa_postprocessing_func(
    idx,
    file_names_paths,
    mask_names_paths,
    file_names_raw_paths,
    out_dir,
    num_erosion_iteration,
    thr,
    alpha,
):
    # Load the Probability Map
    prob_map = tifffile.imread(file_names_paths[idx])
    mask = tifffile.imread(mask_names_paths[idx]) > 0
    raw_img = tifffile.imread(file_names_raw_paths[idx])
    raw_img = raw_img / np.max(raw_img)  # normalize the raw image between 0-1

    print(f"image loaded from: {file_names_paths[idx]} shape: {prob_map.shape}")

    # erode the mask
    mask = scp.binary_erosion(mask, iterations=num_erosion_iteration)

    # check if mask has non-zero values (1000 voxels is just a threshold)
    if np.sum(mask) > 1000:
        # Apply the mask to the original image
        prob_map = np.multiply(prob_map, mask)

        # linear mixation of prob_map and raw_img
        prob_map = (1 - alpha) * prob_map + alpha * raw_img

        # binarize the prob_map
        prob_map_bin = prob_map > thr

        save_tiff(
            prob_map > thr, os.path.split(file_names_paths[idx])[1], out_dir, np.bool_
        )
        print(f"Image is saved / shape for {os.path.split(file_names_paths[idx])[1]}")

    else:
        print(f"mask is empty for {file_names_paths[idx]}")
        prob_map_bin = np.zeros_like(mask, dtype=bool)
        save_tiff(
            prob_map_bin, os.path.split(file_names_paths[idx])[1], out_dir, np.bool_
        )


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main():
    # Execute the parse_args() method
    args = vars(my_parser.parse_args())
    input_file_path = args["input"]
    out_dir = Path(args["out_dir"]) / "normalized_raw_data"
    cpu_load = args["cpu_load"]
    mask_file_path = args["brain_mask"]
    num_erosion_iteration = args["num_erosion"]
    raw_file_path = args["raw_data"]
    thr = args["thr"]
    alpha = args["alpha"]

    # print all the input parameters
    print("\nRunning RAW data normalization with the following settings:")
    print(f"  Input prob map:        {input_file_path}")
    print(f"  Path to output folder: {out_dir}")
    print(f"  CPU load:              {cpu_load}")
    print(f"  Brain mask path:       {mask_file_path}")
    print(f"  # erosions brain mask: {num_erosion_iteration}")
    print(f"  RAW Tiff folder:       {raw_file_path}")
    print(f"  Binarization thr:      {thr}")
    print(f"  Alpha:                 {alpha}")

    # create out dir
    isExist = os.path.exists(out_dir)
    if not isExist:
        os.mkdir(out_dir)

    # List all files in the input path
    file_names = os.listdir(input_file_path)
    file_names_paths = [
        os.path.join(input_file_path, file)
        for file in file_names
        if file.endswith(".tiff") or file.endswith(".tif")
    ]
    print(f"found {len(file_names_paths)} files in the input directory")

    # List all files in the mask path
    file_names_mask = os.listdir(mask_file_path)
    mask_names_paths = [
        os.path.join(mask_file_path, file)
        for file in file_names_mask
        if file.endswith(".tiff") or file.endswith(".tif")
    ]
    print(f"found {len(mask_names_paths)} files in the input directory")

    # List all files in the raw path
    file_names_raw = os.listdir(raw_file_path)
    file_names_raw_paths = [
        os.path.join(raw_file_path, file)
        for file in file_names_raw
        if file.endswith(".tiff") or file.endswith(".tif")
    ]
    print(f"found {len(file_names_raw_paths)} files in the input directory")

    # sort files and masks
    mask_names_paths.sort()
    file_names_paths.sort()
    file_names_raw_paths.sort()

    print(f"some file names: {file_names_paths[:20]}")
    print(f"some mask names: {mask_names_paths[:20]}")
    print(f"some raw names: {file_names_raw_paths[:20]}")
    print("------------------------------------")
    print("Note that the file names and mask names should match in terms of order")
    print("------------------------------------")

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    # run the parallelized function
    with parallel_config(backend="loky", n_jobs=ncpus):
        Parallel()(
            delayed(aa_postprocessing_func)(
                idx,
                file_names_paths,
                mask_names_paths,
                file_names_raw_paths,
                out_dir,
                num_erosion_iteration,
                thr,
                alpha,
            )
            for idx in range(len(file_names_paths))
        )


if __name__ == "__main__":
    main()
