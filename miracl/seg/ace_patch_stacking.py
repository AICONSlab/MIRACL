"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca

This code reads the model's output and stack them together to create a large 3D whole brain data and then save the image slice by slice


"""
# load libraries
import os
import argparse
import fnmatch
from subprocess import check_output

# from monai.handlers.utils import from_engine
import numpy as np
import tifffile
from math import floor


def run_stacking(
    patches_path, main_input_folder_path, output_folder_path, h, w, z, monte_carlo
):
    input_path = patches_path
    main_input_path = main_input_folder_path
    output_path = output_folder_path
    subj_height = h
    subj_width = w
    subj_depth = z
    MC_flag = monte_carlo

    print("  calling patch_stacking")
    print(f"  MC_flag: {MC_flag}")

    # # Create the parser
    #     my_parser = argparse.ArgumentParser(description="Working directory")
    #
    # # Add the arguments
    #     my_parser.add_argument(
    #         "-in", "--input_path", help="path to generated_patches folder", required=True
    #     )
    #     my_parser.add_argument(
    #         "-in_main",
    #         "--main_input",
    #         help="the first input from user conatinig .tiff files",
    #         required=True,
    #     )
    #     my_parser.add_argument("-out", "--output_path", help="output directory", required=True)
    #     my_parser.add_argument("-h", "--height", help="image height", required=True)
    #     my_parser.add_argument("-w", "--width", help="image width", required=True)
    #     my_parser.add_argument("-z", "--depth", help="image depth", required=True)
    #     my_parser.add_argument(
    #         "-MC", "--monte_carlo_dropout", help="monte_carlo_dropout flag", required=True
    #     )
    #
    # # Execute the parse_args() method
    #     args = vars(my_parser.parse_args())

    # input_path = args["input_path"]
    # main_input_path = args["main_input"]
    # MC_flag = int(args["monte_carlo_dropout"])
    # if MC_flag > 0:
    #     MC_flag = True
    # else:
    #     MC_flag = False
    # output_path = args["output_path"]
    # check_output_path = Path(output_path)
    # if not check_output_path.exists():
    #     check_output_path.mkdir(parents=True)
    #     print(f"  {output_path} does not exists. Creating...")
    # else:
    #     print(f"  {output_path exists.}")
    # subj_height = args["height"]
    # subj_width = args["width"]
    # subj_depth = args["depth"]

    # read all the slices in the input directory
    img_list_name = []

    with os.scandir(main_input_path) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.lower().endswith((".tif", ".tiff")):
                img_list_name.append(entry.name)

    img_list_name.sort()
    # img_list_name = fnmatch.filter(os.listdir(main_input_path), "*.tif*")
    # img_list_name.sort()

    # image patch size used in the first script to create patches and save them in generate_patches folder
    PATCH_SIZE = 512

    def image_stacking(image_mode, image_type):
        height = floor(subj_height / PATCH_SIZE) + 1
        width = floor(subj_width / PATCH_SIZE) + 1
        depth = floor(subj_depth / PATCH_SIZE) + 1

        cnt_depth = 0
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

                    cnt_img += 1

                    img_temp = tifffile.imread(filename)

                    img = img[: img_temp.shape[0], :, :]

                    img[
                        :,
                        h * PATCH_SIZE : h * PATCH_SIZE + PATCH_SIZE,
                        w * PATCH_SIZE : w * PATCH_SIZE + PATCH_SIZE,
                    ] = img_temp

            for z in range(img_temp.shape[0]):
                img_main = img[z, :height, :width]

                img_filename = os.path.join(
                    output_path, image_mode, img_list_name[cnt_depth - 1]
                )

                # print("saving img: ", img_filename)

                if cnt_depth < depth:
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
    if not MC_flag:
        image_stacking("out_", "uint8")
    else:
        image_stacking("uncertainty_", "float32")
        image_stacking("MC_", "uint8")
