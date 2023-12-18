"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca

This code zero pad images, and create normalized image batches with specific
size (512x512x512). It saves batches in ZYX order with naming of
batch_"part one according to slices"_"batch number". E.g., if we have 2100
slices and we choose 512 for the depth of our stack, it produces 4 different
stack in depth, which first number in naming is representative of this number.
The second number is associated to the number of stack in X and Y.

input:
    1) a directory containing .tiff light sheet image corresponding to depth
    2) a directory for saving the generated image patches
output:
    Image patches with the size of 512x512x512

"""

#######################################
# import libraries
#######################################

import skimage.io as io
import os
# import fnmatch
import numpy as np
from math import floor
import tifffile
from pathlib import Path
import logging


# def generate_patch_main(input_folder, output_folder):
#     input_path = input_folder
#     output_path = output_folder
#     output_dir_subfolder = "generated_patches"
#
#     print("generate_patch_main called")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


#######################################
# inputs
#######################################

def generate_patch_main(input_folder, output_folder):
    input_path = input_folder
    output_path = Path(output_folder)
    output_dir_subfolder = "generated_patches"

    # return input_path, output_path

    # def test_pass(input_folder, output_folder):
    #     tmp_in = input_folder
    #     tmp_out = output_folder
    #     logging.debug(f"Input path: {tmp_in}")
    #     logging.debug(f"Output path: {tmp_out}")
    #
    #     return tmp_in, tmp_out

    # input_path = args.input_folder
    # output_path = args.output_folder
    #######################################
    # create and saved patches
    #######################################

    # function to the windowing
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

    # batch size will be 512 * 512 * 512
    batch_size = 512

    print(f"  \nSubject: {input_path} has been found!")

    # read all the slices in the input directory
    # img_list_name = fnmatch.filter(os.listdir(input_path), "*.tif*")
    # img_list_name.sort()

    img_list_name = []

    with os.scandir(input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                img_list_name.append(entry.name)

    img_list_name.sort()

    # create equal size image slices for third dimension of batch - the last stack might have size of less than batch_size
    stack_index_img = [
        img_list_name[x: x + batch_size]
        for x in range(0, len(img_list_name), batch_size)
    ]

    # check last slice; if its length is less than 512; pick the last 512 as the final crop (overlapping)
    # if len(stack_index_img[-1]) < batch_size:
    #     last_slice = img_list_name[-batch_size:]
    #     stack_index_img = stack_index_img[:-1]
    #     stack_index_img.append(last_slice)

    # def print_dim(idx):
    #     return ["Z", "Y", "X"][idx]

    for idx1, stack in enumerate(stack_index_img):
        img_list = []

        print(f"  \nProcessing image slices for Z-dim...\n")
        for idx2, file in enumerate(stack):
            print("  Slice: ", file)
            fname_input_img = os.path.join(input_path, file)
            img = io.imread(fname_input_img)

            # check if the img needs zero padding
            if (img.shape[0] % batch_size) != 0:
                img_height = (floor(img.shape[0] / batch_size) + 1) * batch_size
            else:
                img_height = img.shape[0]

            if (img.shape[1] % batch_size) != 0:
                img_width = (floor(img.shape[1] / batch_size) + 1) * batch_size
            else:
                img_width = img.shape[1]

            img_padding = np.zeros((img_height, img_width), dtype=img.dtype)
            img_padding[: img.shape[0], : img.shape[1]] = img

            batch_arr_img = blockshaped(img_padding, batch_size, batch_size)

            img_list.append(batch_arr_img)

        img_batch = np.stack(img_list, axis=1)

        # save each data with size of 512 * 512 * 512
        print(
            f" \nSaving patches for Z-dim to '{output_path}/{output_dir_subfolder}/'..."
        )
        for i in range(img_batch.shape[0]):
            img_batch_single = img_batch[i, :, :, :]
            # img_batch_single_normalized = (img_batch_single - img_batch_single.min()) / (img_batch_single.max() - img_batch_single.min())
            file_img = "patch_" + str(idx1) + "_" + str(i) + ".tiff"

            # output_dir_img = os.path.join(output_path, output_dir_subfolder)
            output_dir_img = Path(output_path) / output_dir_subfolder
            # isExist = os.path.exists(output_dir_img)
            if not output_dir_img.is_dir():
                # os.mkdir(output_dir_img)
                output_dir_img.mkdir(parents=True)
                print(f"output_dir: {output_dir_img}")
            fname_output_img = os.path.join(output_dir_img, file_img)

            tifffile.imwrite(
                fname_output_img,
                img_batch_single.astype("uint16"),
                metadata={
                    "DimensionOrder": "ZYX",
                    "SizeC": 1,
                    "SizeT": 1,
                    "SizeX": batch_size,
                    "SizeY": batch_size,
                    "SizeZ": batch_size,
                },
            )

    print(
        f"  \nIn total, {img_batch.shape[0]} patches have been saved to '{output_path}/{output_dir_subfolder}/'!"
    )

    logging.debug("generate_patch_main called")

    gen_patch_folder = output_path / output_dir_subfolder
    return gen_patch_folder
