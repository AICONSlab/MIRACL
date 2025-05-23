"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca) 
Modified for implementation into MIRACL by Jonas Osmann, j.osmann@alumni.utoronto.ca
This code use image processing techniques to preprocess raw LSFM data for MAPL3 project

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

import sys
import numpy as np
import tifffile
import scipy.ndimage as ndimage
import os
import argparse
from tqdm import tqdm
from joblib import Parallel, delayed, parallel_config
import multiprocessing
from miracl import miracl_logger

logger = miracl_logger.logger

# -------------------------------------------------------
# create parser
# -------------------------------------------------------
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-i",
#     "--input",
#     help="input directory containing tif/tiff raw 3D image patches",
#     required=True,
# )
# my_parser.add_argument(
#     "-o", "--out_dir", help="path of output directory", required=True
# )
# my_parser.add_argument(
#     "-cpu",
#     "--cpu_load",
#     help="fraction of cpus to be used for parallelization between 0-1",
#     required=False,
#     default=0.7,
#     type=float,
# )
# my_parser.add_argument(
#     "-clp",
#     "--cl_percentage",
#     help="percentage used in percentile filter between 0-1",
#     required=False,
#     default=0.25,
#     type=float,
# )
# my_parser.add_argument(
#     "-cllf",
#     "--cl_lsm_footprint",
#     help="structure for estimating lsm stripes 1x1xVALUE",
#     required=False,
#     default=100,
#     type=int,
# )
# my_parser.add_argument(
#     "-clbf",
#     "--cl_back_footprint",
#     help="structure for estimating backgroud default is VALUExVALUExVALUE",
#     required=False,
#     default=16,
#     type=int,
# )
# my_parser.add_argument(
#     "-clbd",
#     "--cl_back_downsample",
#     help="downsample ratio applied for background stimation; patch size should be devidable by this value",
#     required=False,
#     default=8,
#     type=int,
# )
# my_parser.add_argument(
#     "-lvbw",
#     "--lsm_vs_back_weight",
#     help="lsm signal vs background weight",
#     required=False,
#     default=2,
#     type=int,
# )
# my_parser.add_argument(
#     "-dbt",
#     "--deconv_bin_thr",
#     help="threshold uses to detect high intensity voxels for psuedo deconvolution between 0-100",
#     required=False,
#     default=95,
#     type=int,
# )
# my_parser.add_argument(
#     "-ds",
#     "--deconv_sigma",
#     help="sigma of Gaussian blurring filter in the psuedo deconvolution",
#     required=False,
#     default=3,
#     type=int,
# )
# my_parser.add_argument(
#     "-sirf",
#     "--save_intermediate_results_flag",
#     help="whether to save intermediate results for debugging",
#     required=False,
#     default=False,
#     action="store_true",
# )

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

    # apply light sheet correction
    img_corrected, l, b = correct_lightsheet(
        img,
        percentile=correct_lightsheet_perc,
        lightsheet_footprint=correct_lightsheet_lsm_footprint,
        background_footprint=correct_lightsheet_back_footprint,
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

    save_tiff(
        img_corrected_filtered_deconvolved,
        "corrected_deconvolved_" + os.path.basename(file_names_paths[idx]),
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


def main(
    generate_patch_output_folder,
    preprocess_parallel_output_folder,
    preprocess_parallel_cpu_load,
    preprocess_parallel_cl_percentage,
    preprocess_parallel_cl_lsm_footprint,
    preprocess_parallel_cl_back_footprint,
    preprocess_parallel_cl_back_downsample,
    preprocess_parallel_cl_lsm_vs_back_weight,
    preprocess_parallel_deconv_bin_thr,
    preprocess_parallel_deconv_sigma,
    preprocess_parallel_save_intermediate_results,
):

    cpu_load = preprocess_parallel_cpu_load.content
    input_file_path = generate_patch_output_folder.dirpath
    out_dir = preprocess_parallel_output_folder.dirpath
    correct_lightsheet_perc = preprocess_parallel_cl_percentage.content
    correct_lightsheet_lsm_footprint = tuple(
        [1, 1, preprocess_parallel_cl_lsm_footprint.content]
    )
    correct_lightsheet_back_footprint = tuple(
        [preprocess_parallel_cl_back_footprint.content] * 3
    )
    correct_lightsheet_back_downsample = preprocess_parallel_cl_back_downsample.content
    correct_lightsheet_lsm_vs_back = preprocess_parallel_cl_lsm_vs_back_weight.content
    deconvolve_bin_thr = preprocess_parallel_deconv_bin_thr.content
    deconvolve_sigma = preprocess_parallel_deconv_sigma.content
    save_intermediate_results_flag = (
        preprocess_parallel_save_intermediate_results.content
    )

    logger.info("###################")
    logger.info("PREPROCESS PARALLEL")
    logger.info("###################")
    logger.info(f"Generated patches folder: {input_file_path}")
    logger.info(f"Preprocessing output folder: {out_dir}")
    logger.info(f"CPU load: {cpu_load}")
    logger.info(f"Percentage percentile filter: {correct_lightsheet_perc}")
    logger.info(f"LSM footprint: {correct_lightsheet_lsm_footprint}")
    logger.info(f"Back footprint: {correct_lightsheet_back_footprint}")
    logger.info(f"Back downsample: {correct_lightsheet_back_downsample}")
    logger.info(f"LSM vs back: {correct_lightsheet_lsm_vs_back}")
    logger.info(f"Pseudo deconv threshold: {deconvolve_bin_thr}")
    logger.info(f"Sigma of gauss blur filter: {deconvolve_sigma}")
    logger.info(f"Save intermediate results: {save_intermediate_results_flag}")

    print(
        "the following parameters will be used: \n",
        "1. light sheet correction: ",
        f"perc = {correct_lightsheet_perc}",
        f"lsm_foot = {correct_lightsheet_lsm_footprint}",
        f"back_foot = {correct_lightsheet_back_footprint}",
        f"back_downsample = {correct_lightsheet_back_downsample}",
        f"lsm_vs_back = {correct_lightsheet_lsm_vs_back} \n",
        "2. psuedo deconv.: ",
        f"binarization thr = {deconvolve_bin_thr}",
        f"blurring sigma = {deconvolve_sigma}",
    )

    # create out dir
    # isExist = os.path.exists(out_dir)
    # if not isExist:
    #     os.mkdir(out_dir)

    # List all files in the input path
    file_names = os.listdir(input_file_path)
    file_names_paths = [
        os.path.join(input_file_path, file)
        for file in file_names
        if file.endswith(".tiff") or file.endswith(".tif")
    ]

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


# if __name__ == "__main__":
#     # Execute the parse_args() method
#     args = vars(my_parser.parse_args())
#     main(args)
