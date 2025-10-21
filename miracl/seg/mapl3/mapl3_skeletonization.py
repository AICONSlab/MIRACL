"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)
This code use the following steps to skelotonize the input stitched probability map.

#### THIS IS THE GPU VERSION ####
it uses CUCIM (RAPIDS) for faster processing

1) it loads the prob map, outputs of deep learning model
2) binarize prob map with different threshold between 0.1 and 0.9
3) for each binarized map it applies medial_axis transform to optain distance transform of the image
4) sum up all the distance transform maps
5) find the ridge of the summed distance transform using peak_local_max function
6) filter objects using connected component analysis; objects are removed using their volume, elongation_thr and euler_number_thr

Optional:

User can pass raw data directory to it to create a linear mixation of probability map and raw data.
In this method, you need to pass alpha to the function as well (default is 0.5)
It applies the mask to the probability map and then applies a linear mixation of the probability map and the raw image (normalized intensity)



Main Inputs:
- input: input tif/tiff probability map
- out_dir: path of output directory
- remove_small_obj_thr: thr (number of voxels) for removing small object
- cpu_load: fraction of cpus to be used for parallelization between 0-1
- dilate_distance_transform_flag: whether to dilate distance transform

Outputs:
    a directory conatining processed and skeletonized binary maps
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
import pandas as pd
from scipy.ndimage import binary_erosion
from cucim.skimage.measure import label, regionprops_table
import cupy as cp
from cucim.skimage.morphology import medial_axis, dilation
from cucim.skimage.feature import peak_local_max
import time
from skimage import measure

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
    "-m",
    "--brain_mask",
    help="input brain mask tif/tiff directory",
    required=True,
)
my_parser.add_argument(
    "-t",
    "--threshold",
    help="threshold for skipping analysis based on the number of forground in mask",
    required=False,
    default=1000,
    type=int,
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
    "-o",
    "--out_dir",
    help="path of output directory",
    required=True,
)
my_parser.add_argument(
    "-ts",
    "--remove_small_obj_thr",
    help="thr (number of voxels) for removing small object",
    required=False,
    default=64,
    type=int,
)
my_parser.add_argument(
    "-tl",
    "--remove_large_obj_thr",
    help="thr (number of voxels) for removing large object",
    required=False,
    default=50000,
    type=int,
)
my_parser.add_argument(
    "-e",
    "--elongation_thr",
    help="elongation threshold of an object",
    required=False,
    default=5,
    type=int,
)
my_parser.add_argument(
    "-eu",
    "--euler_number_thr",
    help="number of holes allowed an object has",
    required=False,
    default=100,
    type=int,
)
my_parser.add_argument(
    "-c",
    "--cpu_load",
    help="fraction of cpus to be used for parallelization between 0-1",
    required=False,
    default=0.7,
    type=float,
)
my_parser.add_argument(
    "-d",
    "--dilate_distance_transform_flag",
    help="whether to dilate distance transform",
    required=False,
    default=True,
    type=bool,
)
my_parser.add_argument(
    "-r",
    "--raw_data",
    help="input tif/tiff raw",
    required=True,
    default=None,
)
my_parser.add_argument(
    "-a",
    "--alpha",
    help="alpha for linear mixation of probability map and raw image; 0 (only model) 1 (only raw image)",
    required=False,
    default=0.5,
    type=float,
)


# -------------------------------------------------------
# filter function
# -------------------------------------------------------
def filter_objects_gpu(
    binary_map, min_size=64, max_size=20000, elongation=5, num_holes=100
):
    """
    Filter objects in a binary map using GPU-accelerated connected component analysis.

    Args:
        binary_map (numpy.ndarray): Binary input image (2D)
        min_size (int): Minimum object size to keep
        max_size (int): Maximum object size to keep
        elongation (float): Minimum elongation ratio (λ1/λ2) to keep
        num_holes (int): Maximum number of holes allowed in an object

    Returns:
        numpy.ndarray: Filtered binary map where only qualifying objects remain
    """
    # Initialize output on CPU
    labeled_binary_map_2d_filtering = np.zeros_like(binary_map, dtype=np.bool_)

    # Transfer data to GPU
    binary_map_gpu = cp.asarray(binary_map.astype(np.uint8))

    # Label connected components on
    slice_labels_gpu = label(binary_map_gpu, connectivity=2)
    # save_tiff(cp.asnumpy(slice_labels_gpu), "labels.tif", "out", slice_labels_gpu.dtype)

    # Use regionprops_table for slice
    slice_labels_cpu = cp.asnumpy(slice_labels_gpu)
    props_table = measure.regionprops_table(
        slice_labels_cpu,
        properties=["label", "euler_number", "inertia_tensor_eigvals", "area"],
    )

    props_df = pd.DataFrame(props_table)

    # 1 - euler_number determines the number of holes in an object
    # inertia_tensor_eigvals gives us the eigenvalues of the inertia tensor which
    # describes how the pixel mass is distributed relative to the region's centroid (center of mass) and
    # is useful for understanding the region's shape and orientation.
    # eigenvalues of the inertia_tensor describes the spread of the object
    # the ratio of eigenvalues are usually >> 1 for elongated objects

    # Calculate the elongation ratio (λ1 / λ2), and include a difference term for more robust elongation
    props_df["elongation"] = props_df.apply(
        lambda row: row["inertia_tensor_eigvals-0"] / row["inertia_tensor_eigvals-1"]
        if row["inertia_tensor_eigvals-1"] > 0
        and abs(row["inertia_tensor_eigvals-0"] - row["inertia_tensor_eigvals-1"]) > 0.5
        else np.inf,
        axis=1,
    )

    props_df = pd.DataFrame(props_table)

    # Calculate elongation ratio
    props_df["elongation"] = props_df.apply(
        lambda row: row["inertia_tensor_eigvals-0"] / row["inertia_tensor_eigvals-1"]
        if row["inertia_tensor_eigvals-1"] > 0
        and abs(row["inertia_tensor_eigvals-0"] - row["inertia_tensor_eigvals-1"]) > 0.5
        else np.inf,
        axis=1,
    )

    #
    # Filter objects based on criteria
    valid_labels_2d = props_df.loc[
        ((1 - props_df["euler_number"]) <= num_holes)
        & (props_df["elongation"] > elongation)
        & (props_df["area"] > min_size)
        & (props_df["area"] < max_size),
        "label",
    ]

    # Transfer labels back to CPU for final filtering
    slice_labels_cpu = cp.asnumpy(slice_labels_gpu)

    # Apply filtering
    # for l in valid_labels_2d:
    #     labeled_binary_map_2d_filtering[slice_labels_cpu == l] = True
    labeled_binary_map_2d_filtering = np.isin(slice_labels_cpu, valid_labels_2d)

    return labeled_binary_map_2d_filtering


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
# postprocessing function
# -------------------------------------------------------
def aa_postprocessing_func(prob_map, mask, raw_img, alpha):
    # normalize the raw image between 0-1
    raw_img = raw_img / np.max(raw_img)

    # Apply the mask to the original image
    prob_map = np.multiply(prob_map, mask)

    # linear mixation of prob_map and raw_img; alpha = 0.25
    prob_map = (1 - alpha) * prob_map + alpha * raw_img

    return prob_map


# -------------------------------------------------------
# skeletonize function
# -------------------------------------------------------
def aa_skeletonize(
    idx,
    file_names_paths,
    mask_names_paths,
    raw_names_paths,
    out_dir,
    min_size_thr,
    max_size_thr,
    elongation_thr,
    euler_number_thr,
    dilate_distance_transform_flag,
    num_erosion_iteration,
    thr,
    alpha,
):
    # Load the Probability Map
    prob_map = tifffile.imread(file_names_paths[idx])
    mask = tifffile.imread(mask_names_paths[idx]) > 0
    if raw_names_paths is not None:
        raw_img = tifffile.imread(raw_names_paths[idx])
    print(f"image loaded from: {file_names_paths[idx]} shape: {prob_map.shape}")

    # erode the mask
    mask = binary_erosion(mask, iterations=num_erosion_iteration)

    # check if mask has non-zero values (thr voxels is just a threshold)
    if np.sum(mask) > thr:
        # if raw data passed by user; it applies the linear mixation of raw data with prob_map
        if raw_names_paths is not None:
            prob_map = aa_postprocessing_func(prob_map, mask, raw_img, alpha)

        # Find bounding box coordinates before cropping
        rows, cols = np.where(mask == True)
        y_min, y_max = np.min(rows), np.max(rows)
        x_min, x_max = np.min(cols), np.max(cols)

        # crop the image based on the mask (reduce the field of view)
        cropped_prob_map = prob_map[y_min : y_max + 1, x_min : x_max + 1]

        # first filter the image
        cropped_prob_mask = filter_objects_gpu(
            cropped_prob_map >= 0.5,
            min_size=min_size_thr,
            max_size=max_size_thr,
            elongation=elongation_thr,
            num_holes=euler_number_thr,
        )
        # Create a full-size mask with the same dimensions as original
        prob_mask = np.zeros_like(mask, dtype=bool)
        # Place the filtered result back in the original position
        prob_mask[y_min : y_max + 1, x_min : x_max + 1] = cropped_prob_mask

        # save_tiff(prob_mask, "filtered_" + os.path.split(file_names_paths[idx])[1], out_dir, np.bool_)

        # Apply the mask to the original image
        prob_map = np.multiply(prob_map, prob_mask)

        # crop the image based on the mask (reduce the field of view)
        cropped_prob_map = prob_map[y_min : y_max + 1, x_min : x_max + 1]

        # Binarize at Multiple Thresholds:
        thresholds = np.linspace(0.1, 0.9, 9)
        binarized_maps = [(cropped_prob_map > t).astype(np.uint8) for t in thresholds]

        # medial_axis filter to find the distance transform
        # Parallel medial_axis transform
        distances = []
        for img in binarized_maps:
            _, dist = medial_axis(cp.asarray(img), return_distance=True)
            distances.append(cp.asnumpy(dist))

        combined_distance = np.sum(distances, axis=0)
        # save_tiff(combined_distance, 'skeletonized_distance_' + os.path.split(input_file_path)[1], out_dir, 'float32')

        # Dilate combined Distances
        if dilate_distance_transform_flag:
            combined_distance = dilation(
                cp.asarray(combined_distance), footprint=cp.asarray(np.ones((2, 2)))
            )
            combined_distance = cp.asnumpy(combined_distance)
        # save_tiff(combined_distance, 'skeletonized_distance_dilate_' + os.path.split(input_file_path)[1], out_dir, 'float32')

        # Detect local maxima (ridges) from distance transform
        # Parallel peak detection
        combined_distance_ridge = np.zeros_like(combined_distance, dtype=bool)
        local_maxima = peak_local_max(
            cp.asarray(combined_distance),
            footprint=np.ones((1, 5)),
            exclude_border=True,
            threshold_rel=0.05,
        )
        local_maxima = cp.asnumpy(local_maxima)
        # Reconstruct the ridge map from parallel results
        if local_maxima.size > 0:
            combined_distance_ridge[tuple(local_maxima.T)] = True

        # restore the size of the image
        combined_distance_ridge_full = np.zeros_like(mask, dtype=bool)
        combined_distance_ridge_full[y_min : y_max + 1, x_min : x_max + 1] = (
            combined_distance_ridge
        )
        save_tiff(
            combined_distance_ridge_full,
            os.path.split(file_names_paths[idx])[1],
            out_dir,
            np.bool_,
        )
        print(
            f"skeleton_filtered is saved / shape for {os.path.split(file_names_paths[idx])[1]}"
        )

    else:
        print(f"mask is empty for {file_names_paths[idx]}")
        combined_distance_ridge = np.zeros_like(mask, dtype=bool)
        save_tiff(
            combined_distance_ridge,
            os.path.split(file_names_paths[idx])[1],
            out_dir,
            np.bool_,
        )


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main():
    # Execute the parse_args() method
    args = vars(my_parser.parse_args())
    input_file_path = args["input"]
    out_dir = Path(args["out_dir"]) / "skeletonized"
    min_size_thr = args["remove_small_obj_thr"]
    max_size_thr = args["remove_large_obj_thr"]
    elongation_thr = args["elongation_thr"]
    euler_number_thr = args["euler_number_thr"]
    cpu_load = args["cpu_load"]
    dilate_distance_transform_flag = args["dilate_distance_transform_flag"]
    mask_file_path = args["brain_mask"]
    thr = args["threshold"]
    num_erosion_iteration = args["num_erosion"]
    input_file_path_raw = args["raw_data"]
    alpha = args["alpha"]

    # print all the input parameters
    print("\nRunning skeletonization with the following settings:")
    print(f"  input_file_path: {input_file_path}")
    print(f"  out_dir: {out_dir}")
    print(f"  remove_small_obj_thr: {min_size_thr}")
    print(f"  remove_large_obj_thr: {max_size_thr}")
    print(f"  elongation_thr: {elongation_thr}")
    print(f"  euler_number_thr: {euler_number_thr}")
    print(f"  cpu_load: {cpu_load}")
    print(f"  dilate_distance_transform_flag: {dilate_distance_transform_flag}")
    print(f"  mask_file_path: {mask_file_path}")
    print(f"  thr: {thr}")
    print(f"  num_erosion_iteration: {num_erosion_iteration}")
    print(f"  input_file_path_raw: {input_file_path_raw}")
    print(f"  alpha: {alpha}")

    sys.exit()

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

    # List all files in the raw data path
    if input_file_path_raw is not None:
        file_names_raw = os.listdir(input_file_path_raw)

        raw_names_paths = [
            os.path.join(input_file_path_raw, file)
            for file in file_names_raw
            if file.endswith(".tiff") or file.endswith(".tif")
        ]
        print(f"found {len(raw_names_paths)} files in the input directory")

    # sort files and masks
    mask_names_paths.sort()
    file_names_paths.sort()
    if input_file_path_raw is not None:
        raw_names_paths.sort()

    print(f"some file names: {file_names_paths[:20]}")
    print(f"some mask names: {mask_names_paths[:20]}")
    print(f"some raw names: {raw_names_paths[:20]}")
    print("------------------------------------")
    print(
        "Note that the file names, mask names, and raw data name should match in terms of name files (order)"
    )
    print("------------------------------------")

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    # run the parallelized function
    with parallel_config(backend="threading", n_jobs=ncpus):
        Parallel()(
            delayed(aa_skeletonize)(
                idx,
                file_names_paths,
                mask_names_paths,
                raw_names_paths,
                out_dir,
                min_size_thr,
                max_size_thr,
                elongation_thr,
                euler_number_thr,
                dilate_distance_transform_flag,
                num_erosion_iteration,
                thr,
                alpha,
            )
            for idx in range(len(file_names_paths))
        )


if __name__ == "__main__":
    main()
