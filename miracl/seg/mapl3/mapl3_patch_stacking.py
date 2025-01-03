"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
Modified for implementation into MIRACL by Jonas Osmann, j.osmann@alumni.utoronto.ca

This code reads the model's output and stack them together to create a large 3D whole brain data and then save the image slice by slice

"""

# load libraries
import os
import argparse
import sys
import numpy as np
import tifffile
from joblib import Parallel, delayed, parallel_config
import multiprocessing
from miracl import miracl_logger

logger = miracl_logger.logger

# # Create the parser
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-i", "--input", help="input directory containing .tif image patches", required=True
# )
# my_parser.add_argument(
#     "-m",
#     "--input_raw",
#     help="input directory containing .tif or .tiff image slices of raw data",
#     required=True,
# )
# my_parser.add_argument(
#     "-o", "--out_dir", help="path of output directory", required=True
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
#     "--image_type",
#     help="image type; if pass keep, it will keep the type same as patches type",
#     required=False,
#     default="bool",
#     type=str,
# )


# -------------------------------------------------------
# image slice saver function to be paralleled
# -------------------------------------------------------
def image_slice_saver(
    z,
    cnt_depth,
    img,
    img_list_name,
    subj_depth,
    subj_height,
    subj_width,
    output_dir,
    image_type,
    width,
    height,
):

    img_main = img[z, :subj_height, :subj_width]

    if cnt_depth <= subj_depth:

        img_filename = os.path.join(output_dir, img_list_name[cnt_depth - 1])

        print("saving img: ", img_filename)

        tifffile.imwrite(
            img_filename,
            img_main.astype(image_type),
            metadata={
                "DimensionOrder": "YX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": width,
                "SizeY": height,
            },
        )

    return cnt_depth


def main(
    patch_stacking_output_folder,
    generate_patch_input_folder,
    skeletonization_output_folder,
    patch_stacking_cpu_load,
    patch_stacking_keep_image_type,
):

    # get the arguments
    cpu_load = patch_stacking_cpu_load.content
    input_path = skeletonization_output_folder.dirpath
    output_dir = patch_stacking_output_folder.dirpath
    input_raw = generate_patch_input_folder.input_dirpath
    image_type = patch_stacking_keep_image_type.content

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    logger.info("##############")
    logger.info("PATCH STACKING")
    logger.info("##############")
    logger.info(f"Skeletonization folder: {input_path}"),
    logger.info(f"RAW data: {input_raw}"),
    logger.info(f"Generated patches output folder: {output_dir}"),
    logger.info(f"CPU load: {cpu_load}"),
    logger.info(f"Keep image type: {image_type}"),

    (
        print(f"\nPath: '{input_path}' has been found!")
        if input_path.exists()
        else exit(f"\nError: Path '{input_path}' does not exist.")
    )
    (
        print(f"Slices will be saved to: '{output_dir}'")
        if output_dir.exists()
        else exit(f"Error: Path '{output_dir}' does not exist.")
    )

    # get the slices in the directory
    img_list_name = []

    with os.scandir(input_raw) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                img_list_name.append(entry.name)

    img_list_name.sort()

    # find the h, w and depth of the image
    img_temp = tifffile.imread(os.path.join(input_raw, img_list_name[0]))

    image_type = img_temp.dtype if image_type else np.bool_

    subj_depth = len(img_list_name)
    subj_height = img_temp.shape[0]
    subj_width = img_temp.shape[1]
    print(
        "the main input has the size of ", subj_height, "x", subj_width, "x", subj_depth
    )

    # get patch size
    patch_size = tifffile.imread(os.path.join(input_path, "patch_0_0.tif")).shape[0]
    print("patch size is ", patch_size, "x", patch_size, "x", patch_size)

    height = subj_height // patch_size + 1 * (subj_height % patch_size > 0)
    width = subj_width // patch_size + 1 * (subj_width % patch_size > 0)
    depth = subj_depth // patch_size + 1 * (subj_depth % patch_size > 0)

    cnt_depth = 1
    # for each subject we have depth; each depth has multiple patch_size^3 image patches
    for d in range(depth):

        img = np.zeros(
            (patch_size, height * patch_size, width * patch_size), dtype=image_type
        )
        cnt_img = 0

        for h in range(height):

            for w in range(width):

                filename = os.path.join(
                    input_path, "patch" + "_" + str(d) + "_" + str(cnt_img) + ".tif"
                )
                print("reading ", filename)

                cnt_img += 1

                img_temp = tifffile.imread(filename)

                img = img[: img_temp.shape[0], :, :]

                img[
                    :,
                    h * patch_size : h * patch_size + patch_size,
                    w * patch_size : w * patch_size + patch_size,
                ] = img_temp

        # saving the images parallized
        with parallel_config(backend="threading", n_jobs=ncpus):
            cnt_depths = Parallel()(
                delayed(image_slice_saver)(
                    z,
                    cnt_depth + z,
                    img,
                    img_list_name,
                    subj_depth,
                    subj_height,
                    subj_width,
                    output_dir,
                    image_type,
                    width,
                    height,
                )
                for z in range(img_temp.shape[0])
            )

        cnt_depth = max(cnt_depths)
