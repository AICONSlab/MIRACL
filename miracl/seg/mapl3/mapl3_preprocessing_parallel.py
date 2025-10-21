"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)
This code use image processing techniques to preprocess raw LSFM data for deeptrace project

1. light sheet correction:
This is inspired by TubeMap (https://christophkirst.github.io/ClearMap2Documentation/html/tubemap.html)

  The routine implements a fast but efftice way to remove lightsheet artifacts.
  Effectively the percentile in an eleoganted structural element along the
  lightsheet direction centered around each pixel is calculated and then
  compared to the percentile in a symmetrical box like structural element
  at the same pixel. The former is an estimate of the lightsheet artifact
  the latter of the backgrond. The background is multiplied by the factor
  lightsheet_vs_background and then the minimum of both results is subtracted
  from the source.
  Adding an overall background estimate helps to not accidentally remove
  vessesl like structures along the light-sheet direction.

2. psuedo deconvolve
 High intensity voxels are indentified via a thr and blured using a 3D Gaussian filter.
 The blurred results is then subtracted from the original image and the image rectified while the values of the high intensity voxels are preserved

My ideas:
1. for step 1 I downsampled the image and used a 3D Kernel to estimate background and then upsample as doing 3D or larger kernel takes forever!
2. for step 2 I used 95% percentile to determine high intensity voxels.

main input:
1) input directory containing tif/tiff raw 3D image patches (the output directory of patch generation)
2) a directory for saving the generated image patches
output:
a directory containing image patches with the size of ZxYxX that are preprocessed

"""

import numpy as np
import tifffile
import scipy.ndimage as ndimage
import os
from pathlib import Path
import sys
import argparse
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_config
import multiprocessing
import json
from miracl.system.utilfns.utilfns_cli_parser import str2bool

# # -------------------------------------------------------
# # custom action to handle metadata file
# # -------------------------------------------------------
# class MetadataAction(argparse.Action):
#     def __call__(self, parser, namespace, values, option_string=None):
#         if values:  # If a metadata file is provided
#             if not os.path.isfile(values):
#                 parser.error(f"The file {values} does not exist.")
#             with open(values, 'r') as f:
#                 try:
#                     metadata = json.load(f)
#                     setattr(namespace, 'metadata', metadata)
#                 except json.JSONDecodeError:
#                     parser.error(f"The file {values} is not a valid JSON file.")

#             # Check if the threshold is provided when metadata is provided
#             if not hasattr(namespace, 'tissue_percentage_threshold'):
#                 parser.error("When a metadata file is provided, --tissue_percentage_threshold must also be specified.")
#         else:
#             setattr(namespace, 'metadata', None)


# -------------------------------------------------------
# create parser
# -------------------------------------------------------


my_parser = argparse.ArgumentParser(description="Working directory")

# Add the arguments
my_parser.add_argument(
    "-i",
    "--input",
    help="input directory containing tif/tiff raw 3D image patches",
    required=True,
)
my_parser.add_argument(
    "-o",
    "--out_dir",
    help="path of output directory",
    required=True,
)
my_parser.add_argument(
    "-cpu",
    "--cpu_load",
    help="fraction of cpus to be used for parallelization between 0-1",
    required=False,
    default=0.7,
    type=float,
)
my_parser.add_argument(
    "-clp",
    "--cl_percentage",
    help="percentage used in percentile filter between 0-1",
    required=False,
    default=0.25,
    type=float,
)
my_parser.add_argument(
    "-cllf",
    "--cl_lsm_footprint",
    help="structure for estimating lsm stripes 1x1xVALUE",
    required=False,
    default=100,
    type=int,
)
my_parser.add_argument(
    "-clbf",
    "--cl_back_footprint",
    help="structure for estimating backgroud default is VALUExVALUExVALUE",
    required=False,
    default=16,
    type=int,
)
my_parser.add_argument(
    "-clbd",
    "--cl_back_downsample",
    help="downsample ratio applied for background stimation; patch size should be devidable by this value",
    required=False,
    default=8,
    type=int,
)
my_parser.add_argument(
    "-lvbw",
    "--lsm_vs_back_weight",
    help="lsm signal vs background weight",
    required=False,
    default=2,
    type=int,
)
my_parser.add_argument(
    "-dbt",
    "--deconv_bin_thr",
    help="threshold uses to detect high intensity voxels for psuedo deconvolution between 0-100",
    required=False,
    default=95,
    type=int,
)
my_parser.add_argument(
    "-ds",
    "--deconv_sigma",
    help="sigma of Gaussian blurring filter in the psuedo deconvolution",
    required=False,
    default=3,
    type=int,
)
my_parser.add_argument(
    "-sirf",
    "--save_intermediate_results_flag",
    help="whether to save intermediate results for debugging",
    required=False,
    default=False,
    type=str2bool,
    # action="store_true",
)
# my_parser.add_argument('-m', '--metadata', help='path to metadata JSON file (optional)', required=False, default=None, action=MetadataAction)
my_parser.add_argument(
    "-m",
    "--metadata",
    help="path to metadata JSON file (optional,)",
    required=False,
    default=None,
)
my_parser.add_argument(
    "-p",
    "--tissue_percentage_threshold",
    help="threshold between 0-100 to filter empty patches (required if metadata is provided,)",
    required=False,
    default=None,
    type=float,
)
my_parser.add_argument(
    "-t",
    "--intensity_threshold",
    help="threshold between 0-100 (percent of int16: around 65K,) to filter the patches that their 95 percentile of intensity fall below this",
    required=False,
    default=None,
    type=float,
)

# -------------------------------------------------------
# background estimation function
# -------------------------------------------------------


def background_estimation_subsample(source, down_ratio, percentile, footprint):
    # Downsample the image
    downsampled = source[::down_ratio, ::down_ratio, ::down_ratio]
    # Estimate the background on the downsampled image
    b = ndimage.percentile_filter(downsampled, percentile * 100, size=footprint)
    # Upsample the background estimate back to original size
    b_upsampled = ndimage.zoom(
        b, (down_ratio, down_ratio, down_ratio), order=1
    )  # Linear interpolation
    return b_upsampled


# -------------------------------------------------------
# light sheet correction function
# -------------------------------------------------------
def correct_lightsheet(
    source,
    percentile=0.25,
    lightsheet_footprint=(1, 1, 150),
    background_footprint=(1, 200, 200),
    correct_lightsheet_back_downsample=8,
    lightsheet_vs_background=2,
):
    # input order axis should be ZYX

    # Light-sheet artifact estimate
    l = ndimage.percentile_filter(source, percentile * 100, size=lightsheet_footprint)
    # print(f"Light-sheet artifact estimate is done!")

    # Background estimate
    # this takes a lot of time:
    # b = ndimage.percentile_filter(source, percentile*100, size=background_footprint)
    # downsample and then estimate:
    b = background_estimation_subsample(
        source, correct_lightsheet_back_downsample, percentile, background_footprint
    )
    # print(f"Background estimate is done!")

    # Combined estimate
    lb = np.minimum(l, lightsheet_vs_background * b)

    # Corrected image
    corrected = source - np.minimum(source, lb)

    return corrected, l, b


# -------------------------------------------------------
# pseudo deconve for blurring artifact
# -------------------------------------------------------
def deconvolve(source, binarized_thr_percentile=95, sigma=10):
    """
    Apply a pseudo-deconvolution step to correct for 'blur artifact' in a 3D image.

    Parameters:
    - source: 3D numpy array (the original image)
    - sigma: float (the standard deviation for the Gaussian filter)

    Returns:
    - deconvolved: 3D numpy array (the deconvolved image)
    """

    # binarized: 3D boolean array (high intensity voxels identified by thresholding)
    binarized = source > np.percentile(source, binarized_thr_percentile)
    convolved = np.zeros(source.shape, dtype=float)
    convolved[binarized] = source[binarized]

    for z in range(convolved.shape[0]):
        convolved[z, :, :] = ndimage.gaussian_filter(convolved[z, :, :], sigma=sigma)

    # convolved = ndimage.gaussian_filter(convolved, sigma=sigma)

    deconvolved = source - np.minimum(source, convolved)  # to avoid negative values
    deconvolved[binarized] = source[binarized]
    return deconvolved, convolved, binarized


# -------------------------------------------------------
# save function
# -------------------------------------------------------
def save_tiff(img, name, dir, type):
    tifffile.imwrite(
        os.path.join(dir, name),
        img.astype(type),
        metadata={
            "DimensionOrder": "ZYX",
            "SizeC": 1,
            "SizeT": 1,
            "SizeX": img.shape[0],
            "SizeY": img.shape[1],
            "SizeZ": img.shape[2],
        },
    )


# -------------------------------------------------------
# save empty outputs for empty patches
# -------------------------------------------------------
def save_empty_out(root_dir, img_list_name, save_intermediate_results_flag):
    for img in img_list_name:
        temp = tifffile.imread(img)
        D, H, W = temp.shape

        out = np.zeros((D, H, W), dtype=temp.dtype)

        # save_tiff(out, 'corrected_deconvolved_' + os.path.basename(img), root_dir, temp.dtype)
        save_tiff(out, os.path.basename(img), root_dir, temp.dtype)

        if save_intermediate_results_flag:
            save_tiff(out, "convolved_" + os.path.basename(img), root_dir, img.dtype)
            save_tiff(out, "binarized_" + os.path.basename(img), root_dir, img.dtype)


# -------------------------------------------------------
# overall function
# -------------------------------------------------------
def my_filter(
    idx,
    file_names_paths,
    out_dir,
    correct_lightsheet_perc,
    correct_lightsheet_lsm_footprint,
    correct_lightsheet_back_footprint,
    correct_lightsheet_back_downsample,
    correct_lightsheet_lsm_vs_back,
    deconvolve_bin_thr,
    deconvolve_sigma,
    save_intermediate_results_flag,
):
    # Load the TIFF image

    img = tifffile.imread(file_names_paths[idx])
    if img.shape != (256, 256, 256):
        print(
            f"Image {file_names_paths[idx]} is not isotropic and devisable by down sample factor!"
        )

    # apply light sheet correction
    img_corrected, l, b = correct_lightsheet(
        img,
        percentile=correct_lightsheet_perc,
        lightsheet_footprint=correct_lightsheet_lsm_footprint,
        background_footprint=correct_lightsheet_back_footprint,
        correct_lightsheet_back_downsample=correct_lightsheet_back_downsample,
        lightsheet_vs_background=correct_lightsheet_lsm_vs_back,
    )

    if save_intermediate_results_flag:
        save_tiff(
            img_corrected,
            "corrected_" + os.path.basename(file_names_paths[idx]),
            out_dir,
            img.dtype,
        )
        save_tiff(
            l,
            "lsfm_estimate_" + os.path.basename(file_names_paths[idx]),
            out_dir,
            img.dtype,
        )
        save_tiff(
            b,
            "background_estimate_" + os.path.basename(file_names_paths[idx]),
            out_dir,
            img.dtype,
        )

    # apply deconvolve filter
    img_corrected_filtered_deconvolved, convolved, binarized = deconvolve(
        img_corrected,
        binarized_thr_percentile=deconvolve_bin_thr,
        sigma=deconvolve_sigma,
    )

    # save_tiff(img_corrected_filtered_deconvolved, 'corrected_deconvolved_' + os.path.basename(file_names_paths[idx]), out_dir, img.dtype)
    save_tiff(
        img_corrected_filtered_deconvolved,
        os.path.basename(file_names_paths[idx]),
        out_dir,
        img.dtype,
    )

    if save_intermediate_results_flag:
        save_tiff(
            convolved,
            "convolved_" + os.path.basename(file_names_paths[idx]),
            out_dir,
            img.dtype,
        )
        save_tiff(
            binarized,
            "binarized_" + os.path.basename(file_names_paths[idx]),
            out_dir,
            img.dtype,
        )

    print(f"{file_names_paths[idx]} is corrected, deconvolved, and saved!")


# -------------------------------------------------------
# main function
# -------------------------------------------------------


def main(args):
    # get the arguments
    cpu_load = args["cpu_load"]
    input_file_path = args["input"]
    out_dir = Path(args["out_dir"]) / "preprocessing_parallel"
    correct_lightsheet_perc = args["cl_percentage"]
    correct_lightsheet_lsm_footprint = tuple([1, 1, args["cl_lsm_footprint"]])
    correct_lightsheet_back_footprint = tuple([args["cl_back_footprint"]] * 3)
    correct_lightsheet_back_downsample = args["cl_back_downsample"]
    correct_lightsheet_lsm_vs_back = args["lsm_vs_back_weight"]
    deconvolve_bin_thr = args["deconv_bin_thr"]
    deconvolve_sigma = args["deconv_sigma"]
    save_intermediate_results_flag = args["save_intermediate_results_flag"]
    percentage_brain_patch_skip = args["tissue_percentage_threshold"]
    intensity_threshold_skip = args["intensity_threshold"]
    metadata_path = args["metadata"]
    # Additional validation
    if (
        metadata_path is not None
        and percentage_brain_patch_skip is None
        and intensity_threshold_skip is None
    ):
        my_parser.error(
            "When a metadata file is provided, --tissue_percentage_threshold and --intensity_threshold must also be specified."
        )

    # get the threshold intensity
    # data are int16, so 1 percent of it is around 655
    if intensity_threshold_skip == 1:
        intensity_threshold_skip = (
            int((intensity_threshold_skip / 100) * (2**16 - 1)) + 1
        )

    print(
        f"\nthe following parameters will be used: \n",
        f" 1. light sheet correction: ",
        f"perc = {correct_lightsheet_perc} ",
        f"lsm_foot = {correct_lightsheet_lsm_footprint} ",
        f"back_foot = {correct_lightsheet_back_footprint} ",
        f"back_downsample = {correct_lightsheet_back_downsample} "
        f"lsm_vs_back = {correct_lightsheet_lsm_vs_back} \n",
        f" 2. psuedo deconv.: ",
        f"binarization thr = {deconvolve_bin_thr} ",
        f"bluring sigma = {deconvolve_sigma} \n",
        f"metadata json file = {metadata_path} ",
        f"tissue_percentage_threshold = {percentage_brain_patch_skip} ",
        f"intensity_threshold_skip = {intensity_threshold_skip} ",
    )

    sys.exit()

    # create out dir
    isExist = os.path.exists(out_dir)
    if not isExist:
        os.mkdir(out_dir)

    # List all files in the input path
    file_names = os.listdir(input_file_path)

    if percentage_brain_patch_skip is not None:
        # Load metadata
        with open(os.path.join(metadata_path)) as f:
            metadata = json.load(f)["patches"]

        # Filter filenames to include only .tif or .tiff files
        file_names_paths = [
            file
            for file in file_names
            if file.endswith(".tiff") or file.endswith(".tif")
        ]

        # Create a dictionary to map filenames to their tissue_percentage
        metadata_dict = {
            patch["filename"]: patch["tissue_percentage"] for patch in metadata
        }
        metadata_dict_int = {
            patch["filename"]: patch["intensity_max"] for patch in metadata
        }

        # Filter non-empty images (tissue_percentage > threshold)
        images_non_empty = [
            os.path.join(input_file_path, image)
            for image in file_names_paths
            if (
                metadata_dict.get(image, 0) > percentage_brain_patch_skip
                and metadata_dict_int.get(image, 0) > intensity_threshold_skip
            )
        ]
        images_non_empty.sort()

        # Filter empty images (tissue_percentage <= threshold)
        images_empty = [
            os.path.join(input_file_path, image)
            for image in file_names_paths
            if metadata_dict.get(image, 0)
            <= percentage_brain_patch_skip  # Opposite condition
        ]
        images_empty.sort()

        # save output for empty patches
        # save_empty_out(out_dir, file_names_paths_empty, save_intermediate_results_flag)

        print(
            f"metadata file is selected, and the following files will be processed: \n",
            f"Number of empty patches: {len(images_empty)} \n",
            f"Number of non-empty patches: {len(images_non_empty)}",
        )

        # file_names_paths = [os.path.join(input_file_path, file) for file in images_non_empty]
        file_names_paths = images_non_empty

    else:
        file_names_paths = [
            os.path.join(input_file_path, file)
            for file in file_names
            if file.endswith(".tiff") or file.endswith(".tif")
        ]
        print(
            f"metadata file is not selected, and all files will be processed: \n",
            f"Number of patches: {len(file_names_paths)}",
        )

    # get the number of cpus
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpu_load * cpus)

    with parallel_config(backend="threading", n_jobs=ncpus):
        Parallel()(
            delayed(my_filter)(
                idx,
                file_names_paths,
                out_dir,
                correct_lightsheet_perc=correct_lightsheet_perc,
                correct_lightsheet_lsm_footprint=correct_lightsheet_lsm_footprint,
                correct_lightsheet_back_footprint=correct_lightsheet_back_footprint,
                correct_lightsheet_back_downsample=correct_lightsheet_back_downsample,
                correct_lightsheet_lsm_vs_back=correct_lightsheet_lsm_vs_back,
                deconvolve_bin_thr=deconvolve_bin_thr,
                deconvolve_sigma=deconvolve_sigma,
                save_intermediate_results_flag=save_intermediate_results_flag,
            )
            for idx in range(len(file_names_paths))
        )


if __name__ == "__main__":
    # Execute the parse_args() method
    args = vars(my_parser.parse_args())
    main(args)
