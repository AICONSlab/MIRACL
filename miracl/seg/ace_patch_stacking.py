"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca

This code reads the model's output and stack them together to create a large 3D whole brain data and then save the image slice by slice

"""
# load libraries
import os

# from monai.handlers.utils import from_engine
import numpy as np
import tifffile
from math import floor

def run_stacking(
    patches_path,
    main_input_folder_path,
    output_folder_path,
    monte_carlo,
    model_name_var,
):
    input_path = patches_path
    main_input_path = main_input_folder_path
    output_path = output_folder_path
    MC_flag = monte_carlo
    model_name = model_name_var

    print("  calling patch_stacking")
    print(f"  MC_flag: {MC_flag}")

    # read all the slices in the input directory
    img_list_name = []

    with os.scandir(main_input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                img_list_name.append(entry.name)

    img_list_name.sort()
    # img_list_name = fnmatch.filter(os.listdir(main_input_path), "*.tif*")
    # img_list_name.sort()

    # find the h, w and depth of the image
    subj_depth = len(img_list_name)
    fname_input_img = os.path.join(main_input_path, img_list_name[0])
    img = tifffile.imread(fname_input_img)
    subj_height = img.shape[0]
    subj_width = img.shape[1]

    print(
        "the main input has the size of ", subj_height, "x", subj_width, "x", subj_depth
    )
    # image patch size used in the first script to create patches and save them in generate_patches folder
    PATCH_SIZE = 512

    def image_stacking(image_mode, image_type):
        height = floor(subj_height / PATCH_SIZE) + 1
        width = floor(subj_width / PATCH_SIZE) + 1
        depth = floor(subj_depth / PATCH_SIZE) + 1

        cnt_depth = 1
        # for each subject we have 4 depth (0-3); each depth has multiple 512^3 image patches
        for d in range(depth):
            img = np.zeros(
                (PATCH_SIZE, height * PATCH_SIZE, width * PATCH_SIZE), dtype=image_type
            )
            cnt_img = 0

            for h in range(height):
                for w in range(width):
                    filename = os.path.join(
                        input_path,
                        image_mode
                        + "patch"
                        + "_"
                        + str(d)
                        + "_"
                        + str(cnt_img)
                        + ".tiff",
                    )
                    print("reading ", filename)

                    cnt_img += 1

                    img_temp = tifffile.imread(filename)

                    img = img[: img_temp.shape[0], :, :]

                    img[
                        :,
                        h * PATCH_SIZE:h * PATCH_SIZE + PATCH_SIZE,
                        w * PATCH_SIZE:w * PATCH_SIZE + PATCH_SIZE,
                    ] = img_temp

            for z in range(img_temp.shape[0]):
                img_main = img[z, :subj_height, :subj_width]

                if cnt_depth <= subj_depth:
                    img_filename = os.path.join(
                        output_path, image_mode + img_list_name[cnt_depth - 1]
                    )
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

                cnt_depth += 1

            del img_main

    print("stacking images")
    if MC_flag:
        image_stacking("uncertainty_" + model_name + "_", "float32")
        image_stacking("MC_" + model_name + "_", "uint8")
    else:
        image_stacking("out_", "uint8")
