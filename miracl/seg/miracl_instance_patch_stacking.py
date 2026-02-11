import json
import multiprocessing
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import tifffile as tiff
from joblib import Parallel, delayed
from tqdm import tqdm

CPU_LOAD = 0.7


def tiff_parallel_loading(
    height_multiples: int,
    width_multiples: int,
    input_patch_dir: Path,
    depth: int,
    ncpus: int = int(multiprocessing.cpu_count() * CPU_LOAD),
) -> List[Tuple[np.ndarray, int, int, Path]]:
    """Load in image patches in parallel. Sort images based on their
    height and width in the overall images. This is used to load all patches
    for a given depth and stacking them together to form a single image slice
    with depth equal to patch size.

    :param height_multiples: Number of times the patch size fits into the height of the image.
    :type height_multiples: int
    :param width_multiples: Number of times the patch size fits into the width of the image.
    :type width_multiples: int
    :param input_patch_dir: Location of stored CC patches.
    :type input_patch_dir: Path
    :param depth: Current depth multiple of the image.
    :type depth: int
    :param ncpus: Number of threads to use for parallel loading,
        defaults to int(multiprocessing.cpu_count() * CPU_LOAD)
    :type ncpus: int, optional
    :return: A list of tuples containing the image, height index, width index and path to the image.
        The tuples are sorted for easier stacking.
    :rtype: List[Tuple[np.ndarray, int, int, Path]]
    """

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

    # load the images in parallel
    parallel_output = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(_load_tif_single)(
            args=arg,
            input_patch_dir=input_patch_dir,
            depth=depth,
        )
        for arg in args
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


def _load_tif_single(
    args: Dict[str, int],
    input_patch_dir: Path,
    depth: int,
) -> Tuple[np.ndarray, int, int, Path]:
    """Load a single tiff image patch. Used by the parallel
    loading function.

    :param args: Information needed to load the correct patch (height, width, index)
    :type args: Dict[str, int]
    :param input_patch_dir: Location of stored CC patches.
    :type input_patch_dir: Path
    :param depth: Current depth multiple of the image.
    :type depth: int
    :return: Numpy array of the image, height index, width index and path to the image.
        Used by the parallel loading function to sort the image patches.
    :rtype: Tuple[np.ndarray, int, int, Path]
    """
    img_path = input_patch_dir / (
        "CC_patch_" + str(depth) + "_" + str(args["cnt_img"]) + ".tiff"
    )
    img = tiff.imread(img_path)
    return (img, args["h"], args["w"], img_path)


def image_stacking(
    subj_w: int,
    subj_h: int,
    subj_depth: int,
    patch_size: int,
    image_type: str,
    input_patch_dir: Path,
    output_path: Path,
    img_list_name: List[Path],
    neuron_info_by_file: Dict[str, Dict[str, float]],
    ncpus: int = int(multiprocessing.cpu_count() * CPU_LOAD),
):
    """Stacks images together onen depth multiple at a time, and saves slices.
    Updates the neuron info dict with the new neuron ids based on running count
    of neurons found in each patch.

    :param subj_w: Width of the original image slice
    :type subj_w: int
    :param subj_h: Height of the original image slice
    :type subj_h: int
    :param subj_depth: Depth of the original image (number of slices)
    :type subj_depth: int
    :param patch_size: Size of one index of the patch so that the patch is
        `patch_size` x `patch_size` x `patch_size`
    :type patch_size: int
    :param image_type: Numpt data type string for the image
    :type image_type: str
    :param input_patch_dir: Location of CC patches
    :type input_patch_dir: Path
    :param output_path: Destination folder for the stacked image slices
    :type output_path: Path
    :param img_list_name: Slice names of the original image used for saving
        CC slices with the same format
    :type img_list_name: List[Path]
    :param neuron_info_by_file: Neuron information calculated during CC
        indexed by file name
    :type neuron_info_by_file: Dict[str, Dict[str, float]]
    :param ncpus: Number of threads to use for parallel loading of image patches,
        defaults to int(multiprocessing.cpu_count() * CPU_LOAD)
    :type ncpus: int, optional
    """
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

        img_list = tiff_parallel_loading(
            height_multiples=height_multiples,
            width_multiples=width_multiples,
            input_patch_dir=input_patch_dir,
            depth=d,
            ncpus=ncpus,
        )

        for h in range(height_multiples):
            for w in range(width_multiples):
                img_temp = img_list[h][w][0]
                assert (
                    img_list[h][w][1] == h
                ), f"Height index mismatch: {img_list[h][w][1]} != {h}"

                assert (
                    img_list[h][w][2] == w
                ), f"Width index mismatch: {img_list[h][w][2]} != {w}"

                # update image based on running cell count
                fname = img_list[h][w][3].name
                curr_cells = neuron_info_by_file[fname]["total_neurons"]
                assert curr_cells == np.max(
                    img_temp
                ), f"Cell count mismatch: {curr_cells} != {np.max(img_temp)}"
                img_mask = img_temp > 0
                img_temp[img_mask] += running_cell_count

                # add running cell count to each neuron in the dict
                old_neuron_ids = [
                    neuron_id
                    for neuron_id, _ in neuron_info_by_file[fname][
                        "neuron_info"
                    ].items()
                ]

                temp_dict = dict()
                for neuron_id, neuron_info in neuron_info_by_file[fname][
                    "neuron_info"
                ].items():
                    new_neuron_id = int(neuron_id) + running_cell_count
                    temp_dict[new_neuron_id] = neuron_info

                    neuron_info_by_file[fname]["height"] = h * patch_size
                    neuron_info_by_file[fname]["width"] = w * patch_size
                    neuron_info_by_file[fname]["depth"] = d * patch_size

                neuron_info_by_file[fname]["neuron_info"].update(temp_dict)

                # remove old neuron ids (strings)
                for neuron_id in old_neuron_ids:
                    neuron_info_by_file[fname]["neuron_info"].pop(neuron_id, None)

                running_cell_count += curr_cells

                # crop the image if it is larger than the original image
                img_one_depth = img_one_depth[: img_temp.shape[0], :, :]

                img_one_depth[
                    :,
                    h * patch_size : (h + 1) * patch_size,
                    w * patch_size : (w + 1) * patch_size,
                ] = img_temp

        for z in tqdm(range(img_one_depth.shape[0])):
            img_save_slice = img_one_depth[z, :subj_h, :subj_w]

            if depth_tracker <= subj_depth:
                img_filename = output_path / (
                    "CC_" + img_list_name[depth_tracker - 1].name
                )
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

    # save the neuron info dict
    with open(
        input_patch_dir / "neuron_info_from_patches_post_stacking.json", "w"
    ) as f:
        json.dump(neuron_info_by_file, f, indent=4)

    # merge the data into a single json file
    final_neuron_info_dict = dict()
    for fname, neuron_info in neuron_info_by_file.items():
        for neuron_id, neuron_props in neuron_info["neuron_info"].items():
            final_neuron_info_dict[neuron_id] = neuron_props
            final_neuron_info_dict[neuron_id]["depth"] = neuron_info["depth"]
            final_neuron_info_dict[neuron_id]["height"] = neuron_info["height"]
            final_neuron_info_dict[neuron_id]["width"] = neuron_info["width"]

    with open(
        input_patch_dir / "neuron_info_final.json", "w"
    ) as f:
        json.dump(final_neuron_info_dict, f, indent=4)


def run_stacking(
    patches_dir: Path,
    raw_input_dir: Path,
    output_dir: Path,
    neuron_info_by_file: Dict[str, Dict[str, float]],
    ncpus: int,
):
    """Main function of stacking the patches into a single image.
    Also updates the neuron info dict with the new neuron ids.

    :param patches_dir: Location of CC patches
    :type patches_dir: Path
    :param raw_input_dir: Location of raw input LSFM image slices
    :type raw_input_dir: Path
    :param output_dir: Destination folder for the stacked image slices
    :type output_dir: Path
    :param neuron_info_by_file: Neuron information calculated during CC
        indexed by file name
    :type neuron_info_by_file: Dict[str, Dict[str, float]]
    :param ncpus: Number of threads to use for parallel loading of images
    :type ncpus: int
    """
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
        neuron_info_by_file=neuron_info_by_file,
        image_type="uint32",
        ncpus=ncpus,
    )
