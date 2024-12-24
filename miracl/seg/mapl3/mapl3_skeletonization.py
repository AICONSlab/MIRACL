"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca) 
This code use the following steps to skelotonize the input probability map.

1) it loads the prob map, outputs of deep learning model
2) binarize prob map with different threshold between 0.1 and 0.9
3) for each binarized map it applies medial_axis transform to optain distance transform of the image
4) sum up all the distance transform maps
5) find the ridge of the summed distance transform using peak_local_max function
6) filter objects using connected component analysis; objects are removed using their volume, orientation and eccentricity 

"""

import sys
import numpy as np
import tifffile
from skimage.morphology import medial_axis, remove_small_objects, dilation
import os
import argparse
from skimage.feature import peak_local_max
import multiprocessing
from joblib import Parallel, delayed, parallel_config
import multiprocessing
import scipy.ndimage as scp
from skimage import measure
import pandas as pd
from miracl import miracl_logger

logger = miracl_logger.logger

# # -------------------------------------------------------
# # create parser
# # -------------------------------------------------------
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-i", "--input", help="input tif/tiff probability map", required=True
# )
# my_parser.add_argument(
#     "-o", "--out_dir", help="path of output directory", required=True
# )
# my_parser.add_argument(
#     "-t",
#     "--remove_small_obj_thr",
#     help="thr (number of voxels) for removing small object",
#     required=False,
#     default=100,
#     type=int,
# )
# my_parser.add_argument(
#     "-c",
#     "--cpu_load",
#     help="fraction of cpus to be used for parallelization between 0-1",
#     required=False,
#     default=0.7,
#     type=float,
# )
# my_parser.add_argument(
#     "-d",
#     "--dilate_distance_transform_flag",
#     help="whether to dilate distance transform",
#     required=False,
#     default=True,
#     type=bool,
# )
# my_parser.add_argument(
#     "-e",
#     "--eccentricity_thr",
#     help="thr for removing small object based on eccentricity (between 0-1; circles have eccentricity of 0)",
#     required=False,
#     default=0.5,
#     type=float,
# )
# my_parser.add_argument(
#     "-or",
#     "--orientation_thr",
#     help="thr for removing small object based on orientation (degree)",
#     required=False,
#     default=70,
#     type=int,
# )


# -------------------------------------------------------
# filter function
# -------------------------------------------------------
def filter_objects(
    binary_map, min_size=100, eccentricity_threshold=0.5, orientation_threshold=70
):

    # binarize the input_map
    # binary_map_filtered = remove_small_objects(binary_map, min_size=min_size, connectivity=3)

    # run connected component analysis
    labeled_binary_map, _ = scp.label(
        binary_map.astype(np.uint8), structure=np.ones((3, 3, 3))
    )

    # Parameters for filtering
    eccentricity_threshold = eccentricity_threshold
    orientation_threshold = orientation_threshold  # In degrees
    area_threshold = min_size  # Minimum size in voxels

    # Step 1: 2D Slice Analysis
    labeled_binary_map_2d_filtering = np.zeros_like(labeled_binary_map, dtype=bool)

    for z in range(labeled_binary_map.shape[0]):  # Iterate over z-axis
        slice_labels = labeled_binary_map[z]

        # Use regionprops_table for slice
        props_table = measure.regionprops_table(
            slice_labels, properties=["label", "eccentricity", "orientation"]
        )

        props_df = pd.DataFrame(props_table)

        # Filter based on eccentricity and orientation
        # Orientation = 0°: The object’s major axis is aligned with the y-axis.
        # Orientation = 90°: The object’s major axis is aligned with the x-axis.
        # eccentricity When it is 0, the ellipse becomes a circle.
        valid_labels_2d = props_df.loc[
            (props_df["eccentricity"] >= eccentricity_threshold)
            & (abs(np.degrees(props_df["orientation"])) <= orientation_threshold),
            "label",
        ]

        # Use np.isin to filter regions
        labeled_binary_map_2d_filtering[z, ...] = np.isin(slice_labels, valid_labels_2d)

    # Step 2: 3D Analysis for Area
    # Label the 2D-filtered image in 3D again
    labeled_binary_map_3d_filtering, _ = scp.label(
        labeled_binary_map_2d_filtering, structure=np.ones((3, 3, 3))
    )

    # Use regionprops_table for 3D
    props_table_3d = measure.regionprops_table(
        labeled_binary_map_3d_filtering, properties=["label", "area"]
    )
    props_df_3d = pd.DataFrame(props_table_3d)

    # Filter based on area
    valid_labels_3d = props_df_3d.loc[props_df_3d["area"] >= area_threshold, "label"]

    # Use np.isin to filter based on area in 3D
    final_binary_image = np.isin(labeled_binary_map_3d_filtering, valid_labels_3d)

    return final_binary_image


# -------------------------------------------------------
# save function
# -------------------------------------------------------
def save_tiff(img, name, dir, type):

    tifffile.imwrite(
        os.path.join(dir, name),
        img.astype(type),
        metadata={
            "DimensionOrder": "ZYX",
            "SizeC": 1,
            "SizeT": 1,
            "SizeX": img.shape[0],
            "SizeY": img.shape[1],
            "SizeZ": img.shape[2],
        },
    )


# -------------------------------------------------------
# skeletonize function
# -------------------------------------------------------
def aa_skeletonize(
    idx,
    file_names_paths,
    out_dir,
    min_size_thr,
    eccentricity_thr,
    orientation_thr,
    dilate_distance_transform_flag,
):
    # Load the Probability Map
    prob_map = tifffile.imread(file_names_paths[idx])
    print(f"image loaded from: {file_names_paths[idx]} shape: {prob_map.shape}")

    # Binarize at Multiple Thresholds:
    thresholds = np.linspace(0.1, 0.9, 9)
    binarized_maps = [(prob_map > t).astype(np.uint8) for t in thresholds]

    # medial_axis filter to find the distance transform
    # skeletons = [skeletonize(binarized_map) for binarized_map in binarized_maps]
    # skeletons = []
    distances = []
    for img in binarized_maps:
        temp = np.zeros_like(img)
        dist = np.zeros_like(img)
        for z in range(img.shape[0]):
            # temp[z,...] = skeletonize(img[z,...])
            temp[z, ...], dist[z, ...] = medial_axis(img[z, ...], return_distance=True)
        # skeletons.append(temp)
        distances.append(dist)

    # Weight Skeletons and combine Distances by Initial Threshold
    # weighted_skeletons = [skeleton * t for skeleton, t in zip(skeletons, thresholds)]
    # combined_skeleton = np.sum(weighted_skeletons, axis=0)
    combined_distance = np.sum(distances, axis=0)
    # save_tiff(combined_distance, 'skeletonized_distance_' + os.path.split(input_file_path)[1], out_dir, 'float32')

    # Dilate combined Distances
    if dilate_distance_transform_flag:
        combined_distance = dilation(combined_distance, footprint=np.ones((2, 2, 2)))
    # save_tiff(combined_distance, 'skeletonized_distance_dilate_' + os.path.split(input_file_path)[1], out_dir, 'float32')

    # Detect local maxima (ridges) from distance transform
    combined_distance_ridge = np.zeros_like(combined_distance, dtype=bool)

    for z in range(combined_distance.shape[0]):  # Iterate over slices
        slice_distance_transform = combined_distance[z]

        # Detect local maxima in the 2D slice
        local_maxima = peak_local_max(
            slice_distance_transform,
            footprint=np.ones((1, 3)),  # Define 2D connectivity
            exclude_border=True,
            threshold_rel=0.05,
        )
        # Update ridge points for the current slice
        if local_maxima.size > 0:
            combined_distance_ridge[z][tuple(local_maxima.T)] = True

    # save_tiff(combined_distance_ridge, 'skeletonized_' + os.path.split(input_file_path)[1], out_dir, np.bool_)

    # print(f"skeleton is saved / shape: {combined_distance_ridge.shape}")

    # Binarize the output
    # binarized_thr = 0.1
    # combined_skeleton_bin = (combined_skeleton > binarized_thr).astype(np.uint8)

    # print(combined_skeleton_bin.shape)
    # save_tiff(combined_skeleton_bin, 'skeletonized_binarized_' + os.path.split(input_file_path)[1], out_dir, np.bool_)
    # print(f"combined_skeleton_binarized is saved / shape: {combined_skeleton_bin.shape}")

    # # filter small objects
    combined_distance_ridge_filtered = filter_objects(
        combined_distance_ridge,
        min_size=min_size_thr,
        eccentricity_threshold=eccentricity_thr,
        orientation_threshold=orientation_thr,
    )
    save_tiff(
        combined_distance_ridge_filtered,
        "skeletonized_filtered_" + os.path.split(file_names_paths[idx])[1],
        out_dir,
        np.bool_,
    )
    print(
        f"skeleton_filtered is saved / shape: {combined_distance_ridge_filtered.shape}"
    )


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main(
    inference_output_folder,
    skeletonization_output_folder,
    skeletonization_remove_small_obj_thr,
    skeletonization_cpu_load,
    skeletonization_dilate_distance_transform,
    skeletonization_eccentricity_thr,
    skeletonization_orientation_thr,
):

    # Execute the parse_args() method
    # args = vars(my_parser.parse_args())
    input_file_path = inference_output_folder.dirpath
    out_dir = skeletonization_output_folder.dirpath
    min_size_thr = skeletonization_remove_small_obj_thr.content
    cpu_load = skeletonization_cpu_load.content
    dilate_distance_transform_flag = skeletonization_dilate_distance_transform.content
    eccentricity_thr = skeletonization_eccentricity_thr.content
    orientation_thr = skeletonization_orientation_thr.content

    logger.debug("INSIDE SKELETONIZATION:")
    logger.debug(f"input_file_path: {input_file_path}")
    logger.debug(f"out_dir: {out_dir}")
    logger.debug(f"min_size_thr: {min_size_thr}")
    logger.debug(f"cpu_load: {cpu_load}")
    logger.debug(f"dilate_distance_transform_flag: {dilate_distance_transform_flag}")
    logger.debug(f"eccentricity_thr: {eccentricity_thr}")
    logger.debug(f"orientation_thr: {orientation_thr}")

    # create out dir
    # isExist = os.path.exists(out_dir)
    # if not isExist:
    #     os.mkdir(out_dir)

    # List all files in the input path
    file_names = os.listdir(input_file_path)
    file_names_paths = [
        os.path.join(input_file_path, file)
        for file in file_names
        if file.endswith(".tiff") or file.endswith(".tif")
    ]

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    # run the parallelized function
    with parallel_config(backend="threading", n_jobs=ncpus):

        Parallel()(
            delayed(aa_skeletonize)(
                idx,
                file_names_paths,
                out_dir,
                min_size_thr,
                eccentricity_thr,
                orientation_thr,
                dilate_distance_transform_flag,
            )
            for idx in range(len(file_names_paths))
        )
