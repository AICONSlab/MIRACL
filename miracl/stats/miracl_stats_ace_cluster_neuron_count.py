import argparse
import json
import multiprocessing
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import skimage.measure
import tifffile as tiff
from joblib import Parallel, delayed

ATLAS_DIR = Path(os.environ.get("aradir"))
PROG_NAME = "ace_neuron_count"
FULL_PROG_NAME = f"miracl seg {PROG_NAME}"


def parsefn():
    parser = argparse.ArgumentParser(
        prog=FULL_PROG_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    1) Filters cells based on a specified minimum area argument
    1) Computes cell count of segmented image and summarizes them per label
    2) Outputs clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)""",
        add_help=False,
    )
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "-s",
        "--seg",
        type=str,
        help="Binarized labeled segmentation tif file (3D)",
        required=True,
    )
    required_args.add_argument(
        "-l",
        "--lbl",
        type=str,
        help="""Allen labels directory (in native space) used to summarize features; from registration step.
        Can also be any other labels that you want to use to summarize the features, such as cluster labels.""",
        required=True,
    )
    optional_args = parser.add_argument_group("optional arguments")
    optional_args.add_argument(
        "--min-area",
        type=int,
        default=0,
        help="Minimum area of a neuron to be considered (default: %(default)s)",
        required=False,
    )
    optional_args.add_argument(
        "-m",
        "--mask",
        type=str,
        help="Mask to choose a region of interest (ROI) to analyze (binary image, 0 value outside ROI); needs to be in native space",
        required=False,
    )
    optional_args.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output directory (default: %(default)s)",
        required=False,
        default=".",
    )
    optional_args.add_argument(
        "--skip",
        type=int,
        help="""Number of slices to skip from start and end (default: %(default)s)
        Note: this helps to skip the slices that are poor quality due to the microscope""",
        required=False,
        default=0,
    )
    optional_args.add_argument(
        "-c",
        "--cpu-load",
        type=float,
        help="Percentage of CPU load to use (default: %(default)s)",
        required=False,
        default=0.3,
    )
    optional_args.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    return parser

class InputValidator:
    """Class to validate parsed inputs"""

    @staticmethod
    def validate_inputs(
        seg_dir: str,
        labels_dir: str,
        mask: str,
        output_dir: str,
        skip: int,
        cpu_load: float,
    ) -> Tuple[List[Path], List[Path], Path, int, float]:
        """Ensures input arguments are valid. Checks the shape of
        the segmentation image and the label tifs, and validates the mask.
        Ensures that the output directory exists.

        :param seg_tif: Path to the labeled segmentation directory (from instance seg)
        :type seg_tif: str
        :param labels_dir: Path to the directory containing label tifs from registration
        :type labels_dir: str
        :param mask: Path to the mask tif
        :type mask: str
        :param output_dir: Path to the output directory
        :type output_dir: str
        :param skip: Number of slices to skip from start and end
        :type skip: int
        :param cpu_load: Percentage of CPU load to use
        :type cpu_load: float
        :return: Segmentation tifs, label tifs, output directory, number of slices to skip,
        and CPU load
        :rtype: Tuple[List[Path], List[Path], Path, int, float]
        """
        # load in seg image
        seg_dir = Path(seg_dir)

        assert seg_dir.exists(), f"Segmentation directory does not exist: {seg_dir}"
        # count number of tifs in labels dir
        labels_dir = Path(labels_dir)

        assert labels_dir.exists(), f"Labels directory does not exist: {labels_dir}"
        label_files = sorted(labels_dir.glob("*.tif"))
        num_label_slices = len(label_files)
        assert (
            num_label_slices > 0
        ), f"No *.tif files found in labels directory: {labels_dir}"
        print(f"Found {num_label_slices} tif files in labels directory")

        # load in single tif from labels dir
        print("Loading single tif from labels directory...")
        lbls = tiff.imread(label_files[0])
        lbls_shape = (num_label_slices, *lbls.shape)

        # TODO: mask validation

        # ensure output directory exists
        output_dir = Path(output_dir)
        if not output_dir.exists():
            print(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        # ensure skip is >= 0
        assert skip >= 0, f"Number of slices to skip must be >= 0 (value provided: {skip})"

        # ensure cpu load is between 0 and 1
        assert (
            0 <= cpu_load <= 1
        ), f"CPU load must be between 0 and 1 (value provided: {cpu_load})"

        return label_files, output_dir, skip, cpu_load, lbls_shape

class BoundingBoxes:
    """Class for handling bounding box related methods"""

    @staticmethod
    def get_bbox(slice_path: Path, depth: int):
        slice_img = tiff.imread(slice_path)
        unique_lables = set(slice_img.ravel())
        label_bboxes = dict()

        for region_id in unique_lables:
            if region_id == 0:
                continue
            indices = np.nonzero(slice_img == region_id)

            # get the min and max of the indices
            min_coords = np.min(indices, axis=1)
            max_coords = np.max(indices, axis=1)
            bbox = (*min_coords, *max_coords)
            
            label_bboxes[region_id] = bbox
        return label_bboxes, depth

    @staticmethod
    def export_boxes(
            boxes: List[Tuple[Tuple[int, int, int, int, int, int], int]],
            output_dir: Path,
        ) -> Dict[int, Tuple[int, int, int, int, int, int]]:

        temp_res = defaultdict(lambda: [])
        for box, depth in boxes:
            for region_id, bbox in box.items():
                temp_res[int(region_id)].append((tuple(map(int, bbox)), int(depth)))

        overall_res = dict()
        # get min and max depth for each region
        # get min and max x coord for each region
        # get min and max y coord for each region
        for region_id, box_list in temp_res.items():
            overall_res[region_id] = (
                min([d for _, d in box_list]),
                min([box[0] for box, _ in box_list]),
                min([box[1] for box, _ in box_list]),
                max([d for _, d in box_list]),
                max([box[2] for box, _ in box_list]),
                max([box[3] for box, _ in box_list]),
            )
        
        # save to json
        with open(output_dir / "label_bboxes.json", "w") as f:
            json.dump(overall_res, f, indent=4)

        return overall_res

class NeuronInfo:
    """Class for handling methods of neuron computation and saving"""

    @staticmethod
    def computation_per_region(
        region_id: int,
        region_bbox_dict: Dict[int, Tuple[int, int, int, int, int, int]],
        min_area: int,
        memmap: np.memmap,
    ) -> Tuple[int, Dict[int, Dict[str, int]]]:
        neuron_info = dict()
        region_bbox = region_bbox_dict[region_id]

        seg_masked: np.ndarray = memmap[
            region_bbox[0]:region_bbox[3],
            region_bbox[1]:region_bbox[4],
            region_bbox[2]:region_bbox[5]
        ]

        seg_masked = skimage.measure.label(seg_masked.astype(np.bool_))

        # do regionprops
        region_out = skimage.measure.regionprops_table(
            seg_masked,
            properties=("label", "centroid", "area"),
        )
        # get the centroid and area
        for i, neuron_num in enumerate(region_out.get("label", [])):
            if region_out["area"][i] >= min_area:
                neuron_info[int(neuron_num)] = {
                    "centroid": (
                        float(region_out["centroid-0"][i]) + region_bbox[0],
                        float(region_out["centroid-1"][i]) + region_bbox[1],
                        float(region_out["centroid-2"][i]) + region_bbox[2],
                    ),
                    "area": float(region_out["area"][i]),
                }
        print("Done region: ", region_id, flush=True)
        print("Neurons found: ", len(neuron_info), flush=True)
        return region_id, neuron_info

    @staticmethod
    def export_neuron_info(
            neuron_info: List[Tuple[int, Dict[int, Dict[str, int]]]],
            output_dir: Path
        ):
        # convert to dict
        res_dict = dict()
        current_neuron_num = 0
        for region_id, neuron_info_dict in neuron_info:
            for neuron_id, neuron_stats in neuron_info_dict.items():
                res_dict[int(neuron_id + current_neuron_num)] = neuron_stats
            current_neuron_num += len(neuron_info_dict)
        # save to json
        with open(output_dir / "neuron_info.json", "w") as f:
            json.dump(res_dict, f, indent=4)
        return res_dict


def main(args):
    seg_dir = args.seg
    label_dir = args.lbl
    mask = args.mask
    output_dir = args.output
    skip = args.skip
    cpu_load = args.cpu_load
    min_area = args.min_area

    label_files, output_dir, skip, cpu_load, seg_shape = InputValidator.validate_inputs(
        seg_dir=seg_dir,
        labels_dir=label_dir,
        mask=mask,
        output_dir=output_dir,
        skip=skip,
        cpu_load=cpu_load,
    )

    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    print("Computing neuron count...")

    label_files = label_files[skip:-skip]

    # get bounding box
    print("Getting bbox")
    boxes = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(BoundingBoxes.get_bbox)(
            label_slice,
            depth,
        ) for depth, label_slice in enumerate(label_files)
    )
    
    region_bbox_dict = BoundingBoxes.export_boxes(boxes, output_dir)

    # load in memmap
    img = tiff.memmap(seg_dir)

    # loop over each region
    neuron_info = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(NeuronInfo.computation_per_region)(region_id, region_bbox_dict, min_area, img) for region_id in region_bbox_dict.keys()
    )

    neuron_info_dict = NeuronInfo.export_neuron_info(neuron_info, output_dir)

    # loop over all regions, then neurons
    for neuron_id, neuron_stats in neuron_info_dict.items():
        # get the centroid
        centroid = tuple(map(round, neuron_stats["centroid"]))
        # get the label value of the atlas where the centroid is
        arr_label = tiff.imread(str(label_files[centroid[0]]))
        label_val = arr_label[
            centroid[1],
            centroid[2],
        ]
        if int(label_val) > 0:
            # save that information to the centroid
            neuron_stats["label_val"] = int(label_val)
    
    remove = [k for k, v in neuron_info_dict.items() if "label_val" not in v.keys()]
    for k in remove:
        neuron_info_dict.pop(k, None)

    # save to json
    with open(output_dir / "neuron_info_with_label.json", "w") as f:
        json.dump(neuron_info_dict, f, indent=4)


if __name__ == "__main__":
    parser = parsefn()
    args = parser.parse_args()
    main(args)
