"""
This code is written by Anthony Rinaldi, a.rinaldi@mail.utoronto.ca

This code reads the model's labeled CC output and stack them together to create a large 3D whole brain data and then save the image slice by slice

"""
import multiprocessing
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
import tifffile as tiff
from joblib import Parallel, delayed
from tqdm import tqdm

CPU_LOAD = 0.95

def tiff_parallel_loading(
        height_multiples: int,
        width_multiples: int,
        input_patch_dir: Path,
        depth: int,
        ncpus: int = int(multiprocessing.cpu_count() * CPU_LOAD),
):
    # create a dict of the required args for the parallel loading
    cnt = 0
    args = []
    for i in range(height_multiples):
        for j in range(width_multiples):
            args.append(
                {
                    "h": i,
                    "w": j,
                    "cnt_img": cnt,
                }
            )
            cnt += 1
    # args = [
    #     {
    #         "h": i,
    #         "w": j,
    #         "cnt_img": i+j,
    #     }
    #     for i in range(height_multiples)
    #     for j in range(width_multiples)
    # ]

    # load the images in parallel
    parallel_output = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(load_tif_single)(
            args=arg,
            input_patch_dir=input_patch_dir,
            depth=depth,
        ) for arg in args
    )

    # create nested list of images
    img_list = []
    for i in range(height_multiples):
        img_list.append(
            sorted(
                [img for img in parallel_output if img[1] == i],
                key=lambda x: x[2],
            )
        )

    return img_list


def load_tif_single(
        args: Dict[str, int],
        input_patch_dir: Path,
        depth: int,
):
    img_path = input_patch_dir / ("CC_patch_" + str(depth) + "_" + str(args["cnt_img"]) + ".tiff")
    img = tiff.imread(img_path)
    return (img, args["h"], args["w"])


def image_stacking(
    subj_w: int,
    subj_h: int,
    subj_depth: int,
    patch_size: int,
    image_type: str,
    input_patch_dir: Path,
    output_path: Path,
    img_list_name: List[Path],
):

    height_multiples = subj_h // patch_size + 1 * (subj_h % patch_size > 0)
    width_multiples = subj_w // patch_size + 1 * (subj_w % patch_size > 0)
    depth_multiples = subj_depth // patch_size + 1 * (subj_depth % patch_size > 0)

    depth_tracker = 1
    running_cell_count = 0
    for d in range(depth_multiples):
        img_one_depth = np.zeros(
            (patch_size, height_multiples * patch_size, width_multiples * patch_size),
            dtype=image_type,
        )
        # cnt_img = 0

        img_list = tiff_parallel_loading(
            height_multiples=height_multiples,
            width_multiples=width_multiples,
            input_patch_dir=input_patch_dir,
            depth=d,
            ncpus=int(multiprocessing.cpu_count() * CPU_LOAD),
        )

        for h in range(height_multiples):
            for w in range(width_multiples):
                img_temp = img_list[h][w][0]
                assert img_list[h][w][1] == h, \
                    f"Height index mismatch: {img_list[h][w][1]} != {h}"
                
                assert img_list[h][w][2] == w, \
                    f"Width index mismatch: {img_list[h][w][2]} != {w}"
                
                # filename = input_patch_dir / (
                #     "CC_patch_" + str(d) + "_" + str(cnt_img) + ".tiff"
                # )

                # cnt_img += 1

                # img_temp = tiff.imread(filename)

                # update image based on running cell count
                curr_cells = np.max(img_temp)
                img_mask = img_temp > 0
                img_temp[img_mask] += running_cell_count
                running_cell_count += curr_cells

                img_one_depth = img_one_depth[: img_temp.shape[0], :, :]

                img_one_depth[
                    :,
                    h * patch_size : (h + 1) * patch_size,
                    w * patch_size : (w + 1) * patch_size,
                ] = img_temp

        for z in tqdm(range(img_one_depth.shape[0])):
            img_save_slice = img_one_depth[z, :subj_h, :subj_w]

            if depth_tracker <= subj_depth:
                img_filename = output_path / ("CC_" + img_list_name[depth_tracker - 1].name)
                tiff.imwrite(
                    img_filename,
                    img_save_slice.astype(image_type),
                    metadata={
                        "DimensionOrder": "YX",
                        "SizeC": 1,
                        "SizeT": 1,
                        "SizeX": subj_w,
                        "SizeY": subj_h,
                    },
                )
            depth_tracker += 1

        del img_save_slice


def run_stacking(
    patches_dir: Path,
    raw_input_dir: Path,
    output_dir: Path,
):
    assert patches_dir.exists(), f"Input folder {patches_dir} not found."
    assert raw_input_dir.exists(), f"Raw input folder {raw_input_dir} not found."
    assert output_dir.exists(), f"Output folder {output_dir} not found."

    # read all the slices in the input directory
    img_list_name = [
        file
        for file in raw_input_dir.glob("**/*")
        if file.is_file() and file.name.lower().endswith((".tif", ".tiff"))
    ]

    img_list_name.sort()

    # find the h, w and depth of the image
    subj_depth = len(img_list_name)
    example_raw_img = img_list_name[0]
    img = tiff.imread(example_raw_img)
    subj_h = img.shape[0]
    subj_w = img.shape[1]

    print(f"the main input has the size of {subj_h} x {subj_w} x {subj_depth}")
    patch_size = tiff.imread(list(patches_dir.glob("*.tiff"))[0]).shape[0]

    image_stacking(
        subj_w=subj_w,
        subj_h=subj_h,
        subj_depth=subj_depth,
        patch_size=patch_size,
        input_patch_dir=patches_dir,
        output_path=output_dir,
        img_list_name=img_list_name,
        image_type="uint32",
    )
