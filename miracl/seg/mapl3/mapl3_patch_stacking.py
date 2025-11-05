"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca

This code reads the model's output and stack them together to create a large 3D whole brain data and then save the image slice by slice

Main Inputs:
- input: input directory containing patches
- out_dir: output directory for stitched Z-stack
- raw_dir: directory containing raw .tif slices for original dimensions
- cpu_load: fraction of CPUs to use for parallelization (0-1)
- metadata_path: path to the metadata.json file (original one should contain the info for all patches)
    *** it'll check if the patch exist in the input directory otherwise it'll create an empty patch and use it
- dtype: output data type (e.g., uint16, bool)

Output:
- stitched Z-stack saved to the output directory
"""

import os
import sys
from pathlib import Path
import numpy as np
import tifffile
from joblib import Parallel, delayed, parallel_config
import multiprocessing
import argparse
from pathlib import Path
import json

# -------------------------------------------------------
# Argument parser
# -------------------------------------------------------
my_parser = argparse.ArgumentParser(
    description="Stitch patches back into the original Z-stack."
)
my_parser.add_argument(
    "-i",
    "--input",
    help="Input directory containing patches",
    required=True,
)
my_parser.add_argument(
    "-o",
    "--out_dir",
    help="Output directory for stitched Z-stack",
    required=True,
)
my_parser.add_argument(
    "-r",
    "--raw_dir",
    help="Directory containing raw .tif slices for original dimensions",
    required=True,
)
my_parser.add_argument(
    "-c",
    "--cpu_load",
    help="Fraction of CPUs to use for parallelization (0-1)",
    required=False,
    default=0.7,
    type=float,
)
my_parser.add_argument(
    "-m",
    "--metadata_path",
    help="Path to the metadata.json file",
    required=True,
)
my_parser.add_argument(
    "-d",
    "--dtype",
    help="Output data type (e.g., uint16, bool)",
    required=False,
    default="uint16",
)


# -------------------------------------------------------
# Stitch patches for a single Z-index
# -------------------------------------------------------
# def stitch_z_index(z_index, patches_dir, original_height, original_width, patch_size, dtype):
#     """Stitch all patches for a given Z-index."""
#     # Initialize an empty array for the stitched volume
#     height = original_height // patch_size + 1 * (original_height % patch_size > 0)
#     width = original_width // patch_size + 1 * (original_width % patch_size > 0)
#     stitched_volume = np.zeros((patch_size, height*patch_size, width*patch_size), dtype=dtype)

#     # Find all patches for the current Z-index
#     z_patches = [f for f in os.listdir(patches_dir) if f.startswith(f'patch_{z_index}_')]
#     z_patches.sort()

#     # Load and place each patch in the correct location
#     for patch_name in z_patches:
#         # Extract Y and X indices from the patch name
#         _, y_start, x_start = patch_name.split('_')[1:]
#         y_start = int(y_start)
#         x_start = int(x_start.split('.')[0])  # Remove .tif extension
#         # print(f"y_start: {y_start}, x_start: {x_start}")

#         # Load the patch
#         patch_path = os.path.join(patches_dir, patch_name)
#         print(f"Loading patch: {patch_path}")
#         patch = tifffile.imread(patch_path)

#         # Place the patch in the stitched volume
#         stitched_volume[:, y_start:y_start + patch_size, x_start:x_start + patch_size] = patch


#     return stitched_volume
# -------------------------------------------------------
# Stitch patches for a single Z-index
# -------------------------------------------------------
def stitch_z_index(
    z_index, patches_dir, original_height, original_width, patch_size, dtype, metadata
):
    """Stitch all patches for a given Z-index."""
    # Initialize an empty array for the stitched volume
    height = original_height // patch_size + 1 * (original_height % patch_size > 0)
    width = original_width // patch_size + 1 * (original_width % patch_size > 0)
    stitched_volume = np.zeros(
        (patch_size, height * patch_size, width * patch_size), dtype=dtype
    )

    # Find all patches for the current Z-index
    z_patches = [p for p in metadata["patches"] if p["coordinates"][0] == z_index]
    z_patches.sort(
        key=lambda x: (x["coordinates"][1], x["coordinates"][2])
    )  # Sort by Y, then X

    # Load and place each patch in the correct location
    for patch_info in z_patches:
        patch_name = patch_info["filename"]
        y_start, x_start = patch_info["coordinates"][1], patch_info["coordinates"][2]
        print(f"y_start: {y_start}, x_start: {x_start}")

        # Check if the patch exists
        patch_path = os.path.join(patches_dir, patch_name)
        if os.path.exists(patch_path):
            print(f"Loading patch: {patch_path}")
            patch = tifffile.imread(patch_path)
        else:
            print(f"Patch not found: {patch_path}. Using zero-filled patch.")
            patch = np.zeros((patch_size, patch_size, patch_size), dtype=dtype)

        # Place the patch in the stitched volume
        stitched_volume[
            :, y_start : y_start + patch_size, x_start : x_start + patch_size
        ] = patch

    return stitched_volume


# -------------------------------------------------------
# Save a single slice
# -------------------------------------------------------
def save_slice(
    z, cnt_depth, original_depth, stitched_volume, output_dir, raw_slice_name, dtype
):
    """Save a single slice of the stitched volume."""
    slice_data = stitched_volume[z, :, :].astype(dtype)
    # remove ome from the name if exists
    raw_slice_name = raw_slice_name.replace(".ome.tif", ".tif").replace(
        ".OME.tif", ".tif"
    )
    if cnt_depth <= original_depth:
        img_filename = os.path.join(output_dir, raw_slice_name)
        print("saving img: ", img_filename)
        tifffile.imwrite(
            img_filename,
            slice_data,
            metadata={
                "DimensionOrder": "YX",
                "SizeC": 1,
                "SizeT": 1,
                "SizeX": slice_data.shape[1],
                "SizeY": slice_data.shape[0],
            },
        )


# -------------------------------------------------------
# Main function
# -------------------------------------------------------
def main(args):
    # Get arguments
    patches_dir = args["input"]
    output_dir = Path(args["out_dir"]) / "stacked_patches"
    raw_dir = args["raw_dir"]
    cpu_load = args["cpu_load"]
    metadata_path = args["metadata_path"]
    dtype = np.dtype(args["dtype"])  # Convert string to numpy dtype

    print("\nRunning patch stacking with the following settings:")
    print(f"  Patches directory: {patches_dir}")
    print(f"  Results directory: {output_dir}")
    print(f"  RAW Tiff folder:   {raw_dir}")
    print(f"  CPU load:          {cpu_load}")
    print(f"  Metadata path:     {metadata_path}")
    print(f"  dtype:             {dtype}")

    # Get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load metadata
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
    original_height = metadata["original_dimensions"]["height"]
    original_width = metadata["original_dimensions"]["width"]
    original_depth = metadata["original_dimensions"]["depth"]
    print(f"Original dimensions: {original_depth}x{original_height}x{original_width}")
    patch_size = metadata["patches"][1]["coordinates"][
        2
    ]  # Patch size in X (assuming square patches)

    # Get the list of raw slice names
    raw_slice_names = sorted(
        [f for f in os.listdir(raw_dir) if f.endswith((".tif", ".tiff"))]
    )
    raw_slice_names.sort()
    print(f"Found {len(raw_slice_names)} slices in {raw_dir}.")
    print(
        f"this order should be the same as the order in the directory of raw data: {raw_slice_names[:10]}"
    )

    # Get the number of Z-indices
    # z_indices = sorted(set(int(patch_name.split('_')[1]) for patch_name in os.listdir(patches_dir) if patch_name.startswith('patch_')))
    z_indices = sorted(set(p["coordinates"][0] for p in metadata["patches"]))
    # print(f"Z-indices: {z_indices}")
    print(f"Z-indices: {z_indices}")

    # Stitch patches for each Z-index in series
    cnt_depth = 1
    for z_index in z_indices:
        print(f"Stitching Z-index: {z_index}")
        stitched_volume = stitch_z_index(
            z_index,
            patches_dir,
            original_height,
            original_width,
            patch_size,
            dtype,
            metadata,
        )
        print(f"Stitched volume shape: {stitched_volume.shape}")

        # Get the raw slice names for the current Z-index
        start_slice_idx = z_index  # Z-index is already the starting index
        end_slice_idx = start_slice_idx + patch_size
        current_raw_slice_names = raw_slice_names[start_slice_idx:end_slice_idx]

        # Calculate the number of valid slices in the last chunk
        num_valid_slices = min(patch_size, original_depth - z_index)

        # Save slices in parallel
        with parallel_config(backend="threading", n_jobs=ncpus):
            Parallel()(
                delayed(save_slice)(
                    z,
                    cnt_depth + z,
                    original_depth,
                    stitched_volume[:, :original_height, :original_width],
                    output_dir,
                    current_raw_slice_names[z],
                    dtype,
                )
                for z in range(num_valid_slices)  # Only process valid slices
            )

        cnt_depth += patch_size

    print(f"Stitched Z-stack saved to {output_dir}.")


if __name__ == "__main__":
    args = vars(my_parser.parse_args())
    main(args)
