import argparse
import json
import multiprocessing as mp
import os
import time
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import tifffile as tiff

ATLAS_DIR = Path(os.environ.get("aradir"))
PROG_NAME = "count_neurons"
FULL_PROG_NAME = f"miracl seg {PROG_NAME}"


def parsefn():
    parser = argparse.ArgumentParser(
        prog=FULL_PROG_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
    1) Filters cells based on a specified minimum (and maximum) area argument
    1) Computes cell count of segmented image and summarizes them per label
    2) Outputs clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)""",
        add_help=False,
    )
    required_args = parser.add_argument_group("required arguments")
    required_args.add_argument(
        "-l",
        "--lbl",
        type=str,
        help="""Allen labels directory (in native space) used to summarize features; from registration step.
        Can also be any other labels that you want to use to summarize the features, such as cluster labels.""",
        required=True,
    )
    required_args.add_argument(
        "--min-area",
        type=int,
        help="Minimum area of a neuron to be considered",
        required=True,
    )
    required_args.add_argument(
        "--neuron-info-dict",
        type=str,
        help="Path to the neuron info dict from instance segmentation (neuron_info_final.json)",
        required=True,
    )
    optional_args = parser.add_argument_group("optional arguments")
    optional_args.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output directory (default: %(default)s)",
        required=False,
        default=".",
    )
    optional_args.add_argument(
        "--max-area",
        type=int,
        help="Maximum area of a neuron to be considered (default: %(default)s)",
        required=False,
        default=1000000,
    )
    optional_args.add_argument(
        "--hemi",
        type=str,
        help="Hemisphere of the brain (split or combined) (default: %(default)s)",
        required=False,
        default="combined",
        choices=["split", "combined"],
    )
    optional_args.add_argument(
        "--skip",
        type=int,
        help="""Number of slices to skip from start and end (default: %(default)s)
        Note: this helps to skip the slices that are poor quality due to the microscope""",
        required=False,
        default=50,
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
        "-v",
        "--verbose",
        action="store_true",
        help="Prints out more information (default: %(default)s)",
        required=False,
    )
    optional_args.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    return parser


def validate_inputs(
    labels_dir: str,
    output_dir: str,
    skip: int,
    cpu_load: float,
    min_area: int,
    max_area: int,
    verbose: bool,
    neuron_info_dict_path: str,
) -> Tuple[
    List[Path],
    Path,
    float,
    int,
    Tuple[int, int, int],
    int,
    int,
    bool,
    Path,
]:
    """Ensures input arguments are valid. Checks the shape of
    the segmentation image and the label tifs, and validates the mask.
    Ensures that the output directory exists.

    :param labels_dir: Path to the directory containing label tifs from registration
    :type labels_dir: str
    :param output_dir: Path to the output directory
    :type output_dir: str
    :param skip: Number of slices to skip from start and end
    :type skip: int
    :param cpu_load: Percentage of CPU load to use
    :type cpu_load: float
    :param min_area: Minimum number of voxels required for a neuron to be considered
    in the count
    :type min_area: int
    :param max_area: Maximum number of voxels required for a neuron to be considered
    in the count
    :type max_area: int
    :param verbose: Print out more information
    :type verbose: bool
    :param neuron_info_dict_path: Path to the neuron info dict from instance segmentation
    :type neuron_info_dict_path: Path
    :return: Label tifs, output directory, CPU load, number of slices to skip,
    the shape (3D) of the data, the minimum area filter, the maximum area filter,
    the verbosity, and the path to the neuron info dict
    :rtype: Tuple[List[Path], Path, float, int, Tuple[int, int, int], int, int, bool, Path]
    """
    # ensure skip is >= 0
    assert skip >= 0, f"Number of slices to skip must be >= 0 (value provided: {skip})"

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
    lbls = tiff.imread(label_files[0])
    lbls_shape = (num_label_slices, *lbls.shape)

    # ensure output directory exists
    output_dir = Path(output_dir)
    if not output_dir.exists():
        print(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    # ensure cpu load is between 0 and 1
    assert (
        0 <= cpu_load <= 1
    ), f"CPU load must be between 0 and 1 (value provided: {cpu_load})"

    # ensure minimum area is >= 0
    assert (
        min_area >= 0
    ), f"Minimum area must be greater than 0 (value provided {min_area})"

    # ensure max area is > min area
    assert (
        max_area > min_area
    ), f"Maximum area must be greater than minimum area (values provided: {min_area}, {max_area})"

    # ensure neuron info dict exists
    neuron_info_dict_path = Path(neuron_info_dict_path)

    assert (
        neuron_info_dict_path.exists()
    ), f"Neuron info dict does not exist: {neuron_info_dict_path}"

    return (
        label_files,
        output_dir,
        cpu_load,
        skip,
        lbls_shape,
        min_area,
        max_area,
        verbose,
        neuron_info_dict_path,
    )


def save_results(
    result_dict: Dict[int, Dict[str, int]],
    output_dir: Path,
    hemi: str,
):
    """Save the final results to a CSV file that includes atlas information about regions.

    :param result_dict: Result of the feature extraction containing neuron information and label
    :type result_dict: Dict[int, Dict[str, int]]
    :param output_dir: Directory to save CSV file
    :type output_dir: Path
    :param hemi: Half or whole brain atlas
    :type hemi: str
    """
    # load it atlas csv
    graph = pd.read_csv(ATLAS_DIR / f"ara_mouse_structure_graph_hemi_{hemi}.csv")

    # create dataframe from neuron info
    neuron_df = pd.DataFrame(
        dict(
            NeuronID=[k for k in result_dict.keys()],
            Area=[v["area"] for v in result_dict.values()],
            Centroid=[v["centroid"] for v in result_dict.values()],
            LabelID=[v["label_val"] for v in result_dict.values()],
        )
    )

    # summarize by label/region
    count_df = (
        neuron_df.groupby(
            by=["LabelID"],
            axis=0,
        )
        .agg(
            {
                "Area": ["min", "std", "mean", "max", "sum", "count"],
            }
        )
        .reset_index()
    )

    # save results to csv
    count_df = count_df[count_df.LabelID.isin(graph.id)]

    # make dicts
    name_dict = dict(zip(graph.id, graph.name))
    acronym_dict = dict(zip(graph.id, graph.acronym))
    parent_id_dict = dict(zip(graph.id, graph.parent_structure_id))
    path_dict = dict(zip(graph.id, graph.structure_id_path))
    depth_dict = dict(zip(graph.id, graph.depth))

    # add columns from atlas
    count_df["LabelName"] = count_df["LabelID"].map(name_dict)
    count_df["LabelAbrv"] = count_df["LabelID"].map(acronym_dict)
    count_df["ParentID"] = count_df["LabelID"].map(parent_id_dict)
    count_df["IDPath"] = count_df["LabelID"].map(path_dict)
    count_df["Depth"] = count_df["LabelID"].map(depth_dict)

    count_df.columns = [c[0] + "_" + c[1] if c[1] else c[0] for c in count_df.columns]
    count_df = count_df.rename(
        {"Area_count": "Count"},
        axis=1,
    )

    # reorder columns
    cols = [
        "LabelID",
        "LabelAbrv",
        "LabelName",
        "ParentID",
        "IDPath",
        "Depth",
        "Area_min",
        "Area_max",
        "Area_mean",
        "Area_std",
        "Area_sum",
        "Count",
    ]
    count_df = count_df[cols]

    count_df_sorted = count_df.sort_values(
        ["Count"],
        ascending=False,
    )

    count_csv_path = output_dir / f"clarity_segmentation_features_ara_labels_{hemi}.csv"
    count_df_sorted.to_csv(count_csv_path)

    print(f"Features saved to: {count_csv_path}")


def _init_label(shared_arr_: Tuple[mp.RawArray, np.dtype, Tuple[int, int, int]]):
    """Allocate the shared array to global variables for reference
    in the parallel function.

    :param shared_arr_: The shared array pointer is a global variable so that it
    can be accessed by the child processes. It is a tuple (pointer, dtype, shape).
    :type shared_arr_: Tuple[mp.RawArray, np.dtype, Tuple[int, int, int]]
    """
    global global_shared_arr_label
    global_shared_arr_label = shared_arr_


def shared_to_numpy(
    shared_arr: mp.RawArray, dtype: np.dtype, shape: Tuple[int, int, int]
):
    """Get a NumPy array from a shared memory buffer, with a given dtype and shape.
    No copy is involved, the array reflects the underlying shared buffer.

    :param shared_arr: The shared array pointer.
    :type shared_arr: mp.RawArray
    :param dtype: The data type of the array.
    :type dtype: np.dtype
    :param shape: The shape of the array.
    :type shape: Tuple[int, int, int]
    :return: The NumPy array view of the shared memory buffer.
    :rtype: np.ndarray
    """
    return np.frombuffer(shared_arr, dtype=dtype).reshape(shape)


def create_shared_array(
    dtype: np.dtype, shape: Tuple[int, int, int]
) -> Tuple[mp.RawArray, np.ndarray]:
    """Create a new shared array. Return the shared array pointer, and a NumPy array view to it.
    Note that the buffer values are not initialized.

    :param dtype: Data type of initialized array
    :type dtype: np.dtype
    :param shape: Shape of initialized array
    :type shape: Tuple[int, int, int]
    :return: Shared array pointer and numpy array with data from shared array
    :rtype: Tuple[mp.RawArray, np.ndarray]
    """
    dtype = np.dtype(dtype)
    # Get a ctype type from the NumPy dtype.
    cdtype = np.ctypeslib.as_ctypes_type(dtype)
    # Create the RawArray instance.
    shared_arr = mp.RawArray(cdtype, shape[0] * shape[1] * shape[2])
    # Get a NumPy array view.
    arr = shared_to_numpy(shared_arr=shared_arr, dtype=dtype, shape=shape)
    return shared_arr, arr


def _load_slice(file: Path, slice: int):
    """Load in a slice of an image and place it in a shared
    memory array

    :param file: Location of slice to load
    :type file: Path
    :param slice: Depth index of slice to place in
    shared array
    :type slice: int
    """
    img = tiff.imread(file)
    arr = shared_to_numpy(*global_shared_arr_label)
    arr[slice, :, :] = img


def load_image_parallel(
    files: List[Path],
    shape: Tuple[int, int, int],
    dtype: np.dtype,
    ncpus: int,
    pool_args: Dict[str, Any],
    verbose: bool = False,
) -> Tuple[mp.RawArray, np.ndarray]:
    """Load in large 3d images in parallel slice-by-slice. This function
    uses a shared memory array for each process to write the contents of the
    image slices to.

    :param files: Slice filenames
    :type files: List[Path]
    :param shape: Shape of overall 3D image
    :type shape: Tuple[int, int, int]
    :param dtype: Data type to store in shared array
    :type dtype: np.dtype
    :param ncpus: Number of processes to load in data in parallel
    :type ncpus: int
    :param pool_args: Arguments needed to initialize the pool of workers
    :type pool_args: Dict[str, Any]
    :param verbose: Print out more information, defaults to False
    :type verbose: bool, optional
    :return: The pointer to the shared array in memory and the numpy view of the data
    :rtype: Tuple[mp.RawArray, np.ndarray]
    """
    start = time.perf_counter()
    if verbose:
        print("Loading in array")
    shared_arr, arr = create_shared_array(dtype=dtype, shape=shape)
    if verbose:
        print(f"Done creating array... in {time.perf_counter() - start} seconds")
    # fill in the array
    arr[:] = np.zeros(shape, dtype=dtype)

    with closing(
        mp.Pool(
            ncpus, initializer=pool_args["init"], initargs=((shared_arr, dtype, shape),)
        )
    ) as p:
        # Call parallel_function in parallel.
        p.starmap(
            _load_slice,
            ((file, slice) for slice, file in enumerate(files)),
        )
    # Close the processes.
    p.join()

    if verbose:
        print("Done filling array...")
        print(f"Time taken: {time.perf_counter() - start}")

    return shared_arr, arr


def get_neuron_labels(
    neuron_info_dict: Dict[int, Dict[str, int]],
    arr_label: np.ndarray,
    output_dir: Path,
    min_area: int,
    max_area: int,
    skip: int,
    verbose: bool = False,
) -> Dict[int, Dict[str, int]]:
    """Get neuron labels by indexing the label array at the centroid of
    each neuron. Note: the dictionary will be the same as the input
    but with an additional key `label_val` representing the region the
    neuron belongs to. Any neurons that have their centroid in the background
    (i.e., label=0) are removed.

    :param neuron_info_dict: Neuron information indexed by neuron ID
    :type neuron_info_dict: Dict[int, Dict[str, int]]
    :param arr_label: Label array to index
    :type arr_label: np.ndarray
    :param output_dir: Location to save labeled json file
    :type output_dir: Path
    :param min_area: Minimum voxel area needed to consider a neuron
    :type min_area: int
    :param max_area: Maximum voxel area needed to consider a neuron
    :type max_area: int
    :param skip: Number of slices to skip from start and end
    :type skip: int
    :param verbose: Print out more information, defaults to False
    :type verbose: bool, optional
    :return: Neuron information with label information added.
    :rtype: Dict[int, Dict[str, int]]
    """
    start = time.perf_counter()
    if verbose:
        print("Getting label for each neuron...")

    min_slice = skip
    max_slice = arr_label.shape[0] - skip

    # loop over all regions, then neurons
    for neuron_id, neuron_stats in neuron_info_dict.items():
        # get the centroid
        centroid = tuple(map(round, neuron_stats["centroid"]))

        # check that the centroid is not in the skipping region
        if (
            centroid[0] + neuron_stats["depth"] < min_slice
            or centroid[0] + neuron_stats["depth"] >= max_slice
        ):
            continue

        # get the label value of the atlas where the centroid is
        label_val = arr_label[
            centroid[0] + neuron_stats["depth"],
            centroid[1] + neuron_stats["height"],
            centroid[2] + neuron_stats["width"],
        ]
        if (
            neuron_stats["area"] >= min_area
            and neuron_stats["area"] <= max_area
            and int(label_val) > 0
        ):
            # save that information to the centroid
            neuron_stats["label_val"] = int(label_val)

    remove = [k for k, v in neuron_info_dict.items() if "label_val" not in v.keys()]
    for k in remove:
        neuron_info_dict.pop(k, None)

    # save to json
    with open(output_dir / "neuron_info_final_with_label.json", "w") as f:
        json.dump(neuron_info_dict, f, indent=4)

    if verbose:
        print(f"Time taken: {time.perf_counter() - start}")

    return neuron_info_dict


def main(args):
    label_dir = args.lbl
    output_dir = args.output
    hemi = args.hemi
    skip = args.skip
    cpu_load = args.cpu_load
    min_area = args.min_area
    max_area = args.max_area
    verbose = args.verbose
    neuron_info_dict_path = args.neuron_info_dict

    start_time = time.perf_counter()

    (
        label_files,
        output_dir,
        cpu_load,
        skip,
        label_shape,
        min_area,
        max_area,
        verbose,
        neuron_info_dict_path,
    ) = validate_inputs(
        labels_dir=label_dir,
        output_dir=output_dir,
        skip=skip,
        cpu_load=cpu_load,
        min_area=min_area,
        max_area=max_area,
        verbose=verbose,
        neuron_info_dict_path=neuron_info_dict_path,
    )

    cpus = mp.cpu_count()
    ncpus = int(cpu_load * cpus)

    print("Computing Feature extraction...")

    shared_arr_label, arr_label = load_image_parallel(
        files=label_files,
        shape=label_shape,
        dtype=np.uint16,
        ncpus=ncpus,
        pool_args={
            "init": _init_label,
        },
        verbose=verbose,
    )

    # load in neuron info dict
    with open(neuron_info_dict_path, "r") as f:
        neuron_info_dict = json.load(f)

    neuron_info_with_label = get_neuron_labels(
        neuron_info_dict=neuron_info_dict,
        arr_label=arr_label,
        output_dir=output_dir,
        verbose=verbose,
        min_area=min_area,
        max_area=max_area,
        skip=skip,
    )

    save_results(
        result_dict=neuron_info_with_label,
        output_dir=output_dir,
        hemi=hemi,
    )

    print(
        f"\nFeatures Computation done in {time.perf_counter() - start_time} ... Have a good day!"
    )


if __name__ == "__main__":
    parser = parsefn()
    args = parser.parse_args()
    main(args)
