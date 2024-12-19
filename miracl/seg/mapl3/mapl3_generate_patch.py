"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
Modified for implementation into MIRACL by Jonas Osmann, j.osmann@alumni.utoronto.ca

This code zero pad images, and create image patches with specific
size (ZxYxX). It saves patches in ZYX order with naming of
patch_"part one according to slices"_"patch number". E.g., if we have 2100
slices and we choose 512 for the depth of our stack, it produces 4 different
stack in depth, which first number in naming is representative of this number.
The second number is associated to the number of stack in X and Y.

input:
    1) a directory containing .tiff or .tif light sheet image corresponding to depth
    2) a directory for saving the generated image patches
output:
    Image patches with the size of ZxYxX

"""

#######################################
# import libraries
#######################################

import skimage.io as io
import os
import sys
from miracl.system.objs.objs_seg.objs_mapl3.objs_maple3_generate_patch import (
    GeneratePatch as obj_generate_patch,
)

# import fnmatch
import numpy as np
from math import floor
import tifffile
from pathlib import Path
import logging
from skimage.exposure import adjust_gamma
from skimage.filters import threshold_otsu
from scipy.ndimage import binary_fill_holes, binary_erosion, binary_dilation
import json
from joblib import Parallel, delayed, parallel_config
import multiprocessing

# import argparse

# # -------------------------------------------------------
# # create parser
# # -------------------------------------------------------
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-i",
#     "--input",
#     help="input directory containing .tiff or .tif slices",
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
#     "-p",
#     "--patch_size",
#     help="the outputs will be patch size x patch size x patch size",
#     required=False,
#     default=256,
#     type=int,
# )
# my_parser.add_argument(
#     "-g",
#     "--gamma",
#     help="gamma for gamma correction algorithm",
#     required=False,
#     default=0.3,
#     type=float,
# )


# -------------------------------------------------------
# function for windowing
# -------------------------------------------------------
def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size
    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    assert h % nrows == 0, "{} rows is not evenly divisble by {}".format(h, nrows)
    assert w % ncols == 0, "{} cols is not evenly divisble by {}".format(w, ncols)
    return (
        arr.reshape(h // nrows, nrows, -1, ncols)
        .swapaxes(1, 2)
        .reshape(-1, nrows, ncols)
    )


# -------------------------------------------------------
# brain masker function
# -------------------------------------------------------
def brain_masker(img, gamma):

    # gamma correction
    img = adjust_gamma(img, gamma=gamma, gain=1)

    # Otsu thresholding
    thr = threshold_otsu(img)
    img_mask = img > thr

    # filling the holes in the foreground
    img_mask = binary_fill_holes(img_mask)

    # erosion and dilation to remove the small detected foreground in the backgroun
    img_mask = binary_erosion(img_mask, iterations=3)
    img_mask = binary_dilation(img_mask, iterations=3)

    return img_mask.astype(np.bool_)


# -------------------------------------------------------
# image saver function
# -------------------------------------------------------
def image_saver(
    i, idx1, img_batch, img_batch_binary, out_dir, patch_size, percentage_brain_patch
):

    img_batch_single = img_batch[i, :, :, :]
    img_batch_single_binary = img_batch_binary[i, :, :, :]

    # img_batch_single_normalized = (img_batch_single - img_batch_single.min()) / (img_batch_single.max() - img_batch_single.min())
    file_img = "patch_" + str(idx1) + "_" + str(i) + ".tif"
    fname_output_img = os.path.join(out_dir, file_img)

    # check if the image depth is less than patch_size and zero-pad
    if img_batch_single.shape[0] < patch_size:
        img_batch_single = np.pad(
            img_batch_single,
            ((0, patch_size - img_batch_single.shape[0]), (0, 0), (0, 0)),
            mode="constant",
            constant_values=0,
        )

    # check the image height is less than patch_size and zero-pad
    if img_batch_single.shape[1] < patch_size:
        img_batch_single = np.pad(
            img_batch_single,
            ((0, 0), (0, patch_size - img_batch_single.shape[1]), (0, 0)),
            mode="constant",
            constant_values=0,
        )

    # check the image width is less than patch_size and zero-pad
    if img_batch_single.shape[2] < patch_size:
        img_batch_single = np.pad(
            img_batch_single,
            ((0, 0), (0, 0), (0, patch_size - img_batch_single.shape[2])),
            mode="constant",
            constant_values=0,
        )

    tifffile.imwrite(
        fname_output_img,
        img_batch_single.astype("uint16"),
        metadata={
            "DimensionOrder": "ZYX",
            "SizeC": 1,
            "SizeT": 1,
            "SizeX": patch_size,
            "SizeY": patch_size,
            "SizeZ": patch_size,
        },
    )

    percentage_brain_patch[Path(fname_output_img).name] = (
        100 * img_batch_single_binary.sum() / (patch_size**3)
    )


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main(args):

    # get the arguments
    # cpu_load = args.cpu_load
    # input_path = args.input
    # output_dir = args.output
    # patch_size = args.patch_size
    # gamma = args.gamma

    # print("IN SUBFN:")
    # print(f"{cpu_load}, {input_path}, {output_dir}, {patch_size}, {gamma}")

    print("IN SUBFN:")
    print(f"Input file: {args[obj_generate_patch.input.cli_l_flag]}")
    print(f"Output file: {args[obj_generate_patch.output.cli_l_flag]}")
    print(f"CPU load: {args[obj_generate_patch.cpu_load.cli_l_flag]}")
    print(f"Patch size: {args[obj_generate_patch.patch_size.cli_l_flag]}")
    print(f"Gamma: {args[obj_generate_patch.gamma.cli_l_flag]}")

    sys.exit()

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    print(f"  \nSubject: {input_path} has been found!")
    print(f"  \npatches will be saved to: {output_dir}")

    # get the slices in the directory
    img_list_name = []

    with os.scandir(input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                img_list_name.append(entry.name)

    img_list_name.sort()

    # create equal size image slices for third dimension of batch - the last stack might have size of less than batch_size
    stack_index_img = [
        img_list_name[x : x + patch_size]
        for x in range(0, len(img_list_name), patch_size)
    ]

    # iterate over the stack of images
    percentage_brain_patch = {}
    for idx1, stack in enumerate(stack_index_img):
        img_list = []
        img_list_binary = []

        print(f"  \nProcessing image slices for Z-dim...\n")
        for idx2, file in enumerate(stack):
            print("  Slice: ", file)
            fname_input_img = os.path.join(input_path, file)
            img = io.imread(fname_input_img)

            # create a brain mask for the img
            img_binary = brain_masker(img, gamma=gamma)

            # check if the img needs zero padding
            if (img.shape[0] % patch_size) != 0:
                img_height = (floor(img.shape[0] / patch_size) + 1) * patch_size
            else:
                img_height = img.shape[0]

            if (img.shape[1] % patch_size) != 0:
                img_width = (floor(img.shape[1] / patch_size) + 1) * patch_size
            else:
                img_width = img.shape[1]

            img_padding = np.zeros((img_height, img_width), dtype=img.dtype)
            img_padding_binary = np.zeros((img_height, img_width), dtype=np.bool_)
            img_padding[: img.shape[0], : img.shape[1]] = img
            img_padding_binary[: img.shape[0], : img.shape[1]] = img_binary

            batch_arr_img = blockshaped(img_padding, patch_size, patch_size)
            batch_arr_img_binary = blockshaped(
                img_padding_binary, patch_size, patch_size
            )

            img_list.append(batch_arr_img)
            img_list_binary.append(batch_arr_img_binary)

        # now stack the lists of patch size x patch size x patch size images and their brain mask
        img_batch = np.stack(img_list, axis=1)
        img_batch_binary = np.stack(img_list_binary, axis=1)

        # free ram
        del img_list
        del img_list_binary

        # save each data with size of patch size * patch size * patch size
        print(f" \nSaving patches for Z-dim: {idx1} to {output_dir}...")

        # saving the images parallized
        with parallel_config(backend="threading", n_jobs=ncpus):

            Parallel()(
                delayed(image_saver)(
                    i,
                    idx1,
                    img_batch,
                    img_batch_binary,
                    output_dir,
                    patch_size,
                    percentage_brain_patch,
                )
                for i in range(img_batch.shape[0])
            )

    # save the brain percentage json file
    # save percentage of brain in each patch as json
    with open(os.path.join(output_dir, "percentage_brain_patch.json"), "w") as f:
        json.dump(percentage_brain_patch, f, indent=4)

    print(
        f"  \nIn total, {len(percentage_brain_patch)} patches have been saved to '{output_dir}'!"
    )


# if __name__ == "__main__":
# Execute the parse_args() method
# args = vars(my_parser.parse_args())
# main(args)
