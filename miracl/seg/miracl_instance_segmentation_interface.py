import json
import multiprocessing
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import tifffile
from joblib import Parallel, delayed
from skimage import measure
from tqdm import tqdm

from miracl.seg import (
    miracl_instance_patch_stacking,
    miracl_instance_segmentation_parser,
)

ACE_MATCH_PATTERN = re.compile(r"(patch_.*)")
ACE_REPLACE_PATTERN = re.compile(r"(.*)patch_.*")


def get_brain_patch_percentage_json(dir: Path) -> dict:
    """Get the brain patch percentage from the JSON file.

    :param dir: Path to the directory containing the JSON file.
    :type dir: Path
    :return: Dictionary containing the brain patch percentage.
    :rtype: dict
    """

    with open(dir / "percentage_brain_patch.json") as f:
        percentage_brain_patch = json.load(f)

    return percentage_brain_patch


def get_all_model_outputs(dir: Path, pattern: str) -> List[Path]:
    """Get all model outputs (segmentation) from the directory.

    :param dir: Path to the directory containing the model outputs.
    :type dir: Path
    :param pattern: Pattern to match files in the directory.
    :type pattern: str
    :return: List of paths to the model outputs.
    :rtype: List[Path]
    """

    return sorted(list(dir.glob(pattern)))


def process_single_file(
    output_folder: Path,
    input_file: Path,
    percentage_brain_patch: dict,
    percentage_brain_patch_skip: float,
    props: List[str],
    img_size: Optional[Tuple[int, int, int]] = None,
) -> Tuple[int, Path, Dict[str, Dict[str, float]]]:
    """Load and process a single file.
    Performs CC analysis on the segmentation output.
    Also takes into account the running total number of cells in the brain.

    :param output_folder: Destination folder to save files.
    :type output_folder: Path
    :param input_file: File to load from input folder.
    :type input_file: Path
    :param percentage_brain_patch: Portion of the patch that is brain.
    :type percentage_brain_patch: dict
    :param percentage_brain_patch_skip: Minimum percentage of brain patch to not skip.
    :type percentage_brain_patch_skip: float
    :param props: Properties to compute for each nejuron
    :type props: List[str]
    :param img_size: Size of the image.
    :type img_size: Optional[Tuple[int, int, int]]
    :return: Total number of cells in brain patch and Path to saved patch.
    :rtype: Tuple[int, Path]
    """

    original_img_name = re.findall(ACE_MATCH_PATTERN, str(input_file))[0]
    save_cc_file = output_folder / str(input_file).replace(
        re.findall(ACE_REPLACE_PATTERN, str(input_file))[0], "CC_"
    )

    if (
        percentage_brain_patch.get(original_img_name, 100.0)
        < percentage_brain_patch_skip * 100.0
    ):
        if img_size is None:
            seg_img = tifffile.imread(input_file)
            img_size = seg_img.shape
        # save an empty file of the same size
        tifffile.imwrite(
            save_cc_file,
            np.zeros(img_size, dtype=np.uint16),
            metadata={
                "DimensionOrder": "ZYX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeZ": img_size[0],
                "SizeY": img_size[1],
                "SizeX": img_size[2],
            },
        )
        return 0, save_cc_file, dict()

    # load in the file
    seg_img = tifffile.imread(input_file)

    # perform connected components analysis
    seg_img_cc, num_cells = measure.label(seg_img.astype(np.bool_), return_num=True)

    # compute region properties
    region_props_out = measure.regionprops(
        label_image=seg_img_cc,
    )

    neuron_info_dict = dict()
    for region in region_props_out:
        neuron_info_dict[str(region["label"])] = dict()
        for prop in props:
            if prop == "label":
                continue
            if hasattr(region[prop], "__iter__"):
                if np.issubdtype(type(region[prop][0]), np.integer):
                    neuron_info_dict[str(region["label"])][prop] = list(
                        map(int, region[prop])
                    )
                elif np.issubdtype(type(region[prop][0]), np.floating):
                    neuron_info_dict[str(region["label"])][prop] = list(
                        map(float, region[prop])
                    )
                else:
                    neuron_info_dict[str(region["label"])][prop] = region[prop]
            else:
                if np.issubdtype(type(region[prop]), np.integer):
                    neuron_info_dict[str(region["label"])][prop] = int(region[prop])
                elif np.issubdtype(type(region[prop]), np.floating):
                    neuron_info_dict[str(region["label"])][prop] = float(region[prop])
                else:
                    neuron_info_dict[str(region["label"])][prop] = region[prop]

    # save the connected components image
    tifffile.imwrite(
        save_cc_file,
        seg_img_cc.astype(np.uint16),
        metadata={
            "DimensionOrder": "ZYX",
            "SizeC": 1,
            "SizeT": 1,
            "SizeZ": seg_img.shape[0],
            "SizeY": seg_img.shape[1],
            "SizeX": seg_img.shape[2],
        },
    )
    return num_cells, save_cc_file, neuron_info_dict


def validate_args(args):
    if not Path(args.input_folder).exists():
        raise FileNotFoundError(f"Input folder {args.input_folder} not found.")
    if not Path(args.raw_input_folder).exists():
        raise FileNotFoundError(f"Raw input folder {args.raw_input_folder} not found.")
    if not Path(args.output_folder).exists():
        print(f"Output folder {args.output_folder} not found...creating")
        Path(args.output_folder).mkdir(parents=True, exist_ok=True)


def main(args):
    validate_args(args)

    input_folder = Path(args.input_folder)
    raw_input_folder = Path(args.raw_input_folder)
    output_folder = Path(args.output_folder)
    glob_pattern = args.glob_pattern
    percentage_brain_patch_skip = args.percentage_brain_patch_skip
    props = args.properties
    no_stack = args.no_stack
    cpu_load = args.cpu_load

    # add area, centroid, and label, bbox to properties
    props = list(set(props + ["area", "centroid", "label", "bbox"]))

    print("The following parameters will be used for instance segmentation:\n")
    print(f"  Input folder:                {input_folder}")
    print(f"  Raw input folder:            {raw_input_folder}")
    print(f"  Output folder:               {output_folder}")
    print(f"  Glob pattern:                {glob_pattern}")
    print(f"  Percentage brain patch skip: {percentage_brain_patch_skip}")
    print(f"  Properties:                  {props}")
    print(f"  Stack patches:               {no_stack}")
    print(f"  CPU load:                    {cpu_load}\n")

    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    if percentage_brain_patch_skip > 0.0:
        percentage_brain_patch = get_brain_patch_percentage_json(dir=input_folder)
    else:
        percentage_brain_patch = dict()

    cc_patch_output_folder = input_folder / "cc_patches"
    cc_patch_output_folder.mkdir(parents=True, exist_ok=True)

    all_output_files = get_all_model_outputs(dir=input_folder, pattern=glob_pattern)
    print(f"Number of files: {len(all_output_files)}")

    img_size = tifffile.imread(all_output_files[0]).shape
    print(f"Image size: {img_size}")

    parallel_res = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(process_single_file)(
            output_folder=cc_patch_output_folder,
            input_file=output_file,
            percentage_brain_patch=percentage_brain_patch,
            percentage_brain_patch_skip=percentage_brain_patch_skip,
            props=props,
            img_size=img_size,
        )
        for output_file in tqdm(all_output_files)
    )

    # format the dict to save it
    neuron_info_by_file = dict()
    for cell_count, file, neuron_info in parallel_res:
        neuron_info_by_file[file.name] = {
            "total_neurons": int(cell_count),
            "neuron_info": neuron_info,
        }

    # save file as json in output dir
    with open(cc_patch_output_folder / "neuron_info_from_patches_pre_stacking.json", "w") as f:
        json.dump(neuron_info_by_file, f, indent=5)

    # do patch stacking on the completed files
    if no_stack:
        print("Skipping patch stacking...")
        return

    print("Starting patch stacking...")
    miracl_instance_patch_stacking.run_stacking(
        patches_dir=cc_patch_output_folder,
        raw_input_dir=raw_input_folder,
        output_dir=output_folder,
        neuron_info_by_file=neuron_info_by_file,
        ncpus=ncpus,
    )


if __name__ == "__main__":
    parser = miracl_instance_segmentation_parser.MIRACLInstanceSegParser().parsefn()
    args = parser.parse_args()
    main(args)
