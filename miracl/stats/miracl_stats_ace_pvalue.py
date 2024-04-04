"""
This code is originally from MIRACL software heatmap generatiom

Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca edited the code
it recieves cluster wise pvalue.nii and overlay it on atlas

"""

import argparse
import os
import sys
import time
import typing as th
from math import ceil, nan
from pathlib import Path

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from numpy import float32
from scipy.ndimage import gaussian_filter
from skimage import filters
from sklearn.preprocessing import binarize


# ----- Input Arguments ------
def helpmsg() -> str:
    return """miracl_stats_ace_pvalue.py -p [input path to pvalue image] -v [resolution (um)] 


    ----------

    For command-line / scripting

    example: miracl stats pvalue -p pvalue.nii.gz -v 25 
        Required arguments:
        p. p value image path
        atl. atlas directory path
        v. labels Voxel size/Resolution in um
        gs. Gaussian Smoothing Sigma (Default: 4)         
        cp. matplotlib colourmap for positive values (Default: Reds)
              NOTE: website for custom colourmap options https://matplotlib.org/stable/tutorials/colors/colormaps.html   
        cn. matplotlib colourmap for negative values (Default: Blues)
              NOTE: website for custom colourmap options https://matplotlib.org/stable/tutorials/colors/colormaps.html   


        CUSTOM SLICING (Default: nan)
            Note: Max custom slice index dependent on Voxel size/Resolution: 
            10um max slice index -> sagittal: 1140 , coronal: 1320 , axial: 800 
            25um max slice index -> sagittal: 456 , coronal: 528 , axial: 320
            50um max slice index -> sagittal: 228 , coronal: 264 , axial: 160

        s. slicing in sagittal direction usage: start_slice slice_increment number_of_slices number_of_rows number_of_columns
        c. slicing in coronal direction  usage: start_slice slice_increment number_of_slices number_of_rows number_of_columns 
        a. slicing in axial direction    usage: start_slice slice_increment number_of_slices number_of_rows number_of_columns

            Note: All arguments must be greater than zero. number_of_rows x number_of_columns must be equal to or greater than number_of_slices
            Ex. -s 60 50 7 2 4  
                sagittal direction start at slice #60, increment by 50, 7 slices total, 2 rows, 4 columns. 
                slice indexes chosen: 60, 110, 160, 210,   (row #1)
                                      260, 310, 360        (row #2) 
        DEFAULT SLICING     
        NOTE: If s, c, and a are not specified then default is used (7 slices spread across sagittal, coronal, and axial direction based on image size) 

        f. figure dimensions: width, height (Max: 60 60. Default dependent on number of slices and axes)

        d. directory output (Default: current working directory)
              NOTE: use underscore for names instead of space 
              Ex. ACCEPTABLE   "/data/control_group"       
                  UNACCEPTABLE "/data/control group" 
        o. output filename (Default: group_1 group_2 group_difference) 
              NOTE 1: use underscore for names instead of space 
              NOTE 2: If only -g1 used enter 1 name. If -g2 is used enter 3 names 
              Ex. ACCEPTABLE   "-f control_group treated_group group_difference"       
                  UNACCEPTABLE "-f control group treated group group difference" 
        e. heatmap figure extension (png, jpg, tiff, pdf, etc... (according to matplotlib.savefig documentation). Default: tiff) 
        d. dpi dots per inch (Default: 500). If plotting over 100 images recommended to increase default DPI. If outline/edges are faint increase default DPI
    """


def parsefn() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="", usage=helpmsg(), formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-p", "--pvalue", type=str, help="path to p value nii file", default=None
    )
    parser.add_argument(
        "-atl", "--atlas_dir", type=str, help="path to atlas dir", default=None
    )
    parser.add_argument(
        "-v",
        "--vox",
        type=int,
        choices=[10, 25, 50],
        help="voxel size/Resolution in um",
        default=None,
    )
    parser.add_argument(
        "-gs", "--sigma", type=int, help="Gaussian smoothing sigma", default=4
    )
    parser.add_argument(
        "-cp",
        "--colourmap_pos",
        type=str,
        help="matplotlib colourmap for p values",
        default="Reds",
    )
    parser.add_argument(
        "-cn",
        "--colourmap_neg",
        type=str,
        help="matplotlib colourmap for negative values",
        default="Blues",
    )
    parser.add_argument(
        "-s",
        "--sagittal",
        nargs=5,
        type=int,
        help="slicing across sagittal axis. \n 5 Arguments: start_slice slice_interval number_of_slices number_of_rows number_of_columns",
        default=[nan],
    )
    parser.add_argument(
        "-c",
        "--coronal",
        nargs=5,
        type=int,
        help="slicing across coronal axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
        default=[nan],
    )
    parser.add_argument(
        "-a",
        "--axial",
        nargs=5,
        type=int,
        help="slicing across axial axis. \n 5 Arguments: start_slice interval number_of_slices number_of_rows number_of_columns",
        default=[nan],
    )
    parser.add_argument(
        "-f",
        "--figure_dim",
        type=float,
        nargs=2,
        help="figure width and height",
        default=None,
    )
    parser.add_argument(
        "-d",
        "--dir_outfile",
        type=str,
        help="Output file directory",
        default=os.getcwd(),
    )
    parser.add_argument(
        "-o",
        "--outfile",
        nargs="+",
        type=str,
        help="Output filenames",
        default="cluster_wise_pvalue",
    )
    parser.add_argument(
        "-e", "--extension", type=str, help="heatmap figure extension", default="tiff"
    )
    parser.add_argument("--dpi", type=int, help="dots per inch", default=500)
    parser.add_argument('-m',
                        '--hemi',
                        type=str,
                        choices=["combined", "split"],
                        default="combined",
                        help="warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels/Mirrored) (default: %(default)s)",
                        )
    parser.add_argument("-si",
                        "--side",
                        type=str,
                        choices=["rh", "lh"],
                        default=None,
                        help="side, if only registering a hemisphere instead of whole brain (default: %(default)s)",)
    return parser


def parse_inputs(parser: argparse.ArgumentParser, args: list) -> th.Tuple:
    if sys.argv[-2] == "stats" and sys.argv[-1] == "pvalue":
        print("Running in GUI mode")
        # pass the results of the gui here
        args = miracl_stats_ace_pvalue_gui.main()
        if hasattr(args, "run") == False:
            print("Heatmap GUI Window was closed")
            sys.exit()
    else:
        if isinstance(args, list):
            args, unknown = parser.parse_known_args()
        print("\n running in script mode \n")

    pvalue = args.pvalue
    atlasdir = args.atlas_dir
    vox = args.vox
    sigma = args.sigma
    cp = args.colourmap_pos
    cn = args.colourmap_neg
    sagittal = args.sagittal
    coronal = args.coronal
    axial = args.axial
    figure_dim = args.figure_dim
    outdir = args.dir_outfile
    outfile = args.outfile
    extension = args.extension
    dpi = args.dpi
    hemi = args.hemi
    side = args.side
    side = {"rh": "right", "lh": "left"}.get(side, None)

    # create out dir
    Path(outdir).mkdir(parents=True, exist_ok=True)

    def min_check(arr, threshold, msg):
        if np.amin(arr) < threshold:
            raise Exception(msg)

    # Validate slicing arguments
    # NOTE: Image array is formatted as img[P, I, L]. Order in accordance with LPI convention. x-position -> img[:,:,x], y-position -> img[y,:,:], z-position-> img[:,z,:]
    x = -1
    y = -1
    z = -1
    # check if custom slicing and validate
    row = []
    col = []
    for axis, tag in zip(
        [sagittal, coronal, axial], ["s/sagittal", "c/coronal", "a/axial"]
    ):
        if type(axis[-1]) != float:
            min_check(axis[0], 0, "".join(
                    (
                        "-", tag + " start_slice must not be a negative number. Current value: {}".format(axis[0]),
                    )
                ),
            )
            min_check(axis[1], 1, "".join(
                    (
                        "-", tag + " interval must not less than 1. Current value: {}".format(axis[1]),
                    )
                ),
            )
            min_check(axis[2], 1, "".join(
                    (
                        "-", tag + " number_of_slices  must not be less than 1. Current value: {}".format(axis[2]),
                    )
                ),
            )
            min_check(axis[3] * axis[4], axis[2], "".join(
                    (
                        "-", tag + " number_of_rows x number_of_columns is less than number_of_slices. row x col value: {} x {} = {}. Number_of_slices {}".format(axis[3], axis[4], axis[3] * axis[4], axis[2]),
                    )
                ),
            )
            row.append(axis[3])
            col.append(axis[4])

            if tag == "s/sagittal":
                x = 0
            elif tag == "c/coronal":
                y = x + 1
            elif tag == "a/axial":
                z = max(x, y) + 1

    # if default slicing
    if x == y and y == z:
        x = 0
        y = 1
        z = 2

    # Validate DPI x row/col or height/width doesn't exceed maximum pixel size. Note: max width and height capped at 60
    if figure_dim == None and len(row) > 0:
        max_col = min(np.amax(col), 60)
        max_row = min(sum(row), 60)
        min_check(65536 / dpi, max_row, "".join(
                (
                    "Axis Rows and dpi, Height Resolution exceeds maximum. Rows: {}. DPI: {}. (Largest value of either Max Height or Total Rows) x DPI = {} x {} = {}. Cannot exceed 65535. Note: Max Height is capped at 60".format(row, dpi, max_row, dpi, max_row * dpi)
                )
            ),
        )
        min_check(65536 / dpi, max_col, "".join(
                (
                    "Axis Columns and dpi, Width Resolution exceeds maximum. Cols: {}. DPI: {}. (Largest value of either Max Width or Max Col) x DPI = {} x {} = {}. Cannot exceed 65535. Note: Max Width is capped at 60".format(col, dpi, max_col, dpi, max_col * dpi)
                )
            ),
        )
    if figure_dim != None:
        min_check(65536 / dpi, figure_dim[0], "".join(
                (
                    "-f/figure_dim and -dpi, Height resolution exceeds maximum. Height: {}. DPI: {}. Height x DPI = {}. Cannot exceed 65535".format(figure_dim[0], dpi, figure_dim[0] * dpi)
                )
            ),
        )
        min_check(65536 / dpi, figure_dim[1], "".join(
                (
                    "-f/figure_dim and -dpi, Width resolution exceeds maximum. Width: {}. DPI: {}. Width x DPI = {}. Cannot exceed 65535".format(figure_dim[1], dpi, figure_dim[1] * dpi)
                )
            ),
        )
    multi = False

    return (
        pvalue,
        vox,
        sigma,
        cp,
        cn,
        sagittal,
        coronal,
        axial,
        x,
        y,
        z,
        figure_dim,
        outdir,
        outfile,
        extension,
        dpi,
        multi,
        atlasdir,
        hemi,
        side,
    )


def smooth_plot(
    temp,
    img,
    outdir,
    outfile,
    x,
    y,
    z,
    cut_coords,
    sigma,
    fig,
    axes,
    cmap,
    group,
    mask,
    mask_slices,
    slice_len,
):
    """smooth mean data and superimpose template, mean data, and edge/contour onto plot"""
    img = gaussian_filter(img, sigma=(sigma, sigma, sigma))
    # mean_nii_export(img, outdir, outfile, mask)
    m_norm, img_max = cmap_norm(img, x, y, z, cut_coords, group)

    if x != -1:
        for i in range(slice_len[x]):
            # mean slice
            mean_img = img[:, :, cut_coords[x][i]]
            # threshold image
            if np.amin(mean_img) < 0:
                mean_img[
                    np.where((mean_img < img_max * 0.02) & (mean_img > -img_max * 0.02))
                ] = 0
            else:
                mean_img[np.where(mean_img < img_max * 0.02)] = 0
            # brain template
            mean_img = np.where(
                (mean_img == 0) & (temp[x][i] * binarize(mask_slices[x][i]) > 0),
                img_max / (255) * 1.5,
                mean_img,
            )
            # edge/contour
            mask_img = (
                255
                * (mask_slices[x][i] - np.min(mask_slices[x][i]))
                / np.ptp(mask_slices[x][i])
            ).astype(float32)
            roberts_edge = filters.apply_hysteresis_threshold(
                filters.roberts(mask_img), 0, 1
            ).astype(int)
            mean_img[np.where(roberts_edge == 1)] = np.nan
            # plot
            c = axes[x][i].imshow(
                np.rot90(mean_img, 3), norm=m_norm, cmap=cmap, zorder=2
            )
            axes[x][i].text(
                0.0,
                1,
                "s= {}".format((cut_coords[x][i])),
                horizontalalignment="left",
                verticalalignment="top",
                fontsize=2,
                transform=axes[x][i].transAxes,
            )
            axes[x][i].set_aspect(aspect=1, anchor="SW")

    if y != -1:
        for i in range(slice_len[y]):
            # mean slice
            mean_img = img[cut_coords[y][i], :, :]
            # threshold image
            if np.amin(mean_img) < 0:
                mean_img[
                    np.where((mean_img < img_max * 0.02) & (mean_img > -img_max * 0.02))
                ] = 0
            else:
                mean_img[np.where(mean_img < img_max * 0.02)] = 0
            # brain template
            mean_img = np.where(
                (mean_img == 0) & (temp[y][i] * binarize(mask_slices[y][i]) > 0),
                img_max / (255) * 1.5,
                mean_img,
            )
            # edge/contour
            mask_img = (
                255
                * (mask_slices[y][i] - np.min(mask_slices[y][i]))
                / np.ptp(mask_slices[y][i])
            ).astype(float32)
            roberts_edge = filters.apply_hysteresis_threshold(
                filters.roberts(mask_img), 0, 1
            ).astype(int)
            mean_img[np.where(roberts_edge == 1)] = np.nan
            c = axes[y][i].imshow(mean_img, norm=m_norm, cmap=cmap, zorder=2)
            axes[y][i].text(
                0.0,
                1,
                "c= {}".format(cut_coords[y][i]),
                horizontalalignment="left",
                verticalalignment="top",
                fontsize=2,
                transform=axes[y][i].transAxes,
            )
            axes[y][i].set_aspect(aspect=1, anchor="SW")

    if z != -1:
        for i in range(slice_len[z]):
            # mean slice
            mean_img = img[:, cut_coords[z][i], :]
            # threshold image
            if np.amin(mean_img) < 0:
                mean_img[
                    np.where((mean_img < img_max * 0.02) & (mean_img > -img_max * 0.02))
                ] = 0
            else:
                mean_img[np.where(mean_img < img_max * 0.02)] = 0
            # brain template
            mean_img = np.where(
                (mean_img == 0) & (temp[z][i] * binarize(mask_slices[z][i]) > 0),
                img_max / (255) * 1.5,
                mean_img,
            )
            # edge/contour
            mask_img = (
                255
                * (mask_slices[z][i] - np.min(mask_slices[z][i]))
                / np.ptp(mask_slices[z][i])
            ).astype(float32)
            roberts_edge = filters.apply_hysteresis_threshold(
                filters.roberts(mask_img), 0, 1
            ).astype(int)
            mean_img[np.where(roberts_edge == 1)] = np.nan
            # plot
            c = axes[z][i].imshow(mean_img, norm=m_norm, cmap=cmap, zorder=2)
            axes[z][i].text(
                0.0,
                1,
                "a= {}".format((cut_coords[z][i])),
                horizontalalignment="left",
                verticalalignment="top",
                fontsize=2,
                transform=axes[z][i].transAxes,
            )
            axes[z][i].set_aspect(aspect=1, anchor="SW")

    # add and position colourbar
    cb_ax = fig.add_axes([0, 0.01, 0.02, 0.875])
    cbar = fig.colorbar(c, cax=cb_ax)
    cbar.ax.tick_params(labelsize=3)
    cbar.ax.yaxis.offsetText.set_fontsize(2)
    cbar.ax.zorder = 6
    cb_ax.yaxis.tick_left()


def slice_extract(input_path, cut_coords, x, y, z, atlas):
    """get image slices, check if slice is blank image. Raise error if blank image"""
    img = nib.load(input_path)
    img = np.asanyarray(img.dataobj)
    slices = []
    blank_slices = ""
    if x != -1:
        x_slices = []
        for i in cut_coords[x]:
            if np.min(img[:, :, i]) != np.max(img[:, :, i]):
                x_slices.append(img[:, :, i])
            else:
                blank_slices = "\n".join(
                    (
                        blank_slices,
                        "{} AXIS s/sagittal slice {} is blank ".format(atlas, i),
                    )
                )
        slices.append(x_slices)
    if y != -1:
        y_slices = []
        for i in cut_coords[y]:
            if np.min(img[i, :, :]) != np.max(img[i, :, :]):
                y_slices.append(img[i, :, :])
            else:
                blank_slices = "\n".join(
                    (
                        blank_slices,
                        "{} AXIS c/coronal slice {} is blank".format(atlas, i),
                    )
                )
        slices.append(y_slices)
    if z != -1:
        z_slices = []
        for i in cut_coords[z]:
            if np.min(img[:, i, :]) != np.max(img[:, i, :]):
                z_slices.append(img[:, i, :])
            else:
                blank_slices = "\n".join(
                    (blank_slices, "{} AXIS a/axial slice {} is blank".format(atlas, i))
                )
        slices.append(z_slices)
    if len(blank_slices) > 0:
        raise Exception(blank_slices)
    else:
        return slices


def slice_display(atlas, sagittal, coronal, axial, x, y, z):
    """slicing parameters"""
    img_shape = np.shape(np.asanyarray(nib.load(atlas).dataobj))
    cut_len = max(x, y, z) + 1
    cut_coords = []

    img_shape = [
        img_shape[2],
        img_shape[0],
        img_shape[1],
    ]  # arrange as [L, P, I] order from [P, I, L]
    # default slices
    if (
        type(sagittal[-1]) == float
        and type(coronal[-1]) == float
        and type(axial[-1]) == float
    ):
        for i in range(3):
            cut_coords.append(
                list(
                    range(
                        ceil(img_shape[i] / 17 * 3),
                        ceil(img_shape[i] / 17) * 15 + 1,
                        ceil(img_shape[i] / 17 * 2),
                    )
                )
            )
        cut_len = 3
    # custom slices
    else:
        ind = 0
        for axis, tag in zip(
            [sagittal, coronal, axial], ["s/sagittal", "c/coronal", "a/axial"]
        ):
            if type(axis[-1]) != float:
                cut_coords.append(
                    list(range(axis[0], axis[0] + (axis[2] - 1) * axis[1] + 1, axis[1]))
                )
                print("AXIS {} slices {}".format(tag, cut_coords[-1]))
                if max(cut_coords[-1]) > img_shape[ind]:
                    raise Exception(
                        "AXIS {} slice {}, is greater than max slice size {}".format(
                            tag, max(cut_coords[-1]), img_shape[ind]
                        )
                    )
                if min(cut_coords[-1]) < 0:
                    raise Exception(
                        "AXIS {} slice {} is below zero".format(
                            tag, min(cut_coords[-1])
                        )
                    )
            ind = ind + 1
    return (cut_len, cut_coords)


def cmap_norm(img, x, y, z, cut_coords, group):
    """colour map boundaries, bounded by absolute max/min of selected slices"""
    img_max = []
    if x != -1:
        img_max.append(
            max(
                np.amax(img[:, :, cut_coords[x][:]]),
                np.abs(np.amin(img[:, :, cut_coords[x][:]])),
            )
        )
    if y != -1:
        img_max.append(
            max(
                np.amax(img[cut_coords[y][:], :, :]),
                np.abs(np.amin(img[cut_coords[y][:], :, :])),
            )
        )
    if z != -1:
        img_max.append(
            max(
                np.amax(img[:, cut_coords[z][:], :]),
                np.abs(np.amin(img[:, cut_coords[z][:], :])),
            )
        )
    img_max = max(img_max)
    # symmetrical colourbar if difference plot
    if group == 2:
        img_min = -img_max
    else:
        img_min = 0
    m_norm = mcolors.Normalize(vmin=img_min, vmax=img_max, clip=True)
    return (m_norm, img_max)


def colormap(c1, c2, group):
    """heatmap colours and thresholding"""
    if group != 2:
        colors1 = plt.get_cmap(c2)(range(0, 256))[::-1]
        # threshold out first two shades of colourmap
        colors1[1:2, :] = [0.41176, 0.41176, 0.41176, 1]
        colors1[0:1, :] = [0.95703125, 0.95703125, 0.95703125, 1]
        cmap = mcolors.ListedColormap(colors1)
        # set color of np.nan values (contour)
        cmap.set_bad(color="black")
        return cmap
    else:
        colors1 = plt.get_cmap(c1)(range(0, 256))[::1]
        colors2 = plt.get_cmap(c2)(range(0, 256))[::-1]
        colors = np.vstack((colors1, colors2))
        # threshold out two middle shades of positive and negative bins around zero for colourmap
        colors[254:255, :] = [0.41176, 0.41176, 0.41176, 1]
        colors[255:257, :] = [0.95703125, 0.95703125, 0.95703125, 1]
        colors[257:258, :] = [0.41176, 0.41176, 0.41176, 1]
        cmap = mcolors.ListedColormap(colors)
        # set color of np.nan values (contour)
        cmap.set_bad(color="black")
        return cmap


def figure_setup(cut_coords, cut_len, sagittal, coronal, axial, figure_dim, dpi):
    """plot configurations"""
    # default option  7" x 3"
    w = 7
    h = 3
    ax = []
    # format ex. sagittal -> start_slice, slice_increment, number_of_slices, number_of_rows, number_of_columns
    # number of columns
    cols = np.array([sagittal[-1], coronal[-1], axial[-1]])
    selected = ~np.isnan(cols)
    cols = cols[selected].astype(int)
    # rows/height ratio for subfigures
    if len(cols) > 0:
        rows = np.array([sagittal, coronal, axial])[selected]
        rows = np.array([row[-2] for row in rows]).astype(int)
    else:
        rows = [1, 1, 1]
    # figure dimensions. Cap at 60 in x 60 in
    if isinstance(figure_dim, type(None)) == False:
        w = figure_dim[0]
        h = figure_dim[1]
    elif len(cols) > 0:
        w = np.nanmax(cols)
        h = np.nansum(rows)
    slice_len = [len(x) for x in cut_coords]
    # figure creation
    fig = plt.figure(figsize=(min(w, 60), min(h, 60)), dpi=dpi)
    fig.set_facecolor("whitesmoke")

    # subfigure creation
    subfigs = fig.subfigures(
        cut_len, 1, wspace=0, hspace=0, squeeze=False, height_ratios=rows
    )
    if len(cols) > 0:
        for i in range(cut_len):
            subfigs[i][0].patch.set_alpha(0.0)
            ax.append(subfigs[i][0].subplots(rows[i], cols[i], sharey=True))
    else:
        for i in range(cut_len):
            subfigs[i][0].patch.set_alpha(0.0)
            ax.append(subfigs[i][0].subplots(1, 7, sharey=True))

    # subplots convert to 2-D array to keep consistent array indexing
    for i in range(len(ax)):
        if hasattr(ax[i], "plot"):
            ax[i] = [ax[i]]
        else:
            ax[i] = ax[i].ravel()
    for axes in ax:
        for axes in axes:
            axes.axis("off")
    return (fig, ax, slice_len)


def plot(
    mean_img,
    mask,
    group,
    vox,
    cut_coords,
    cut_len,
    sagittal,
    coronal,
    axial,
    figure_dim,
    outdir,
    outfile,
    sigma,
    cn,
    cp,
    mask_slices,
    temp_slices,
    x,
    y,
    z,
    extension,
    dpi,
):
    """call figure and plot creation"""
    fig, axes, slice_len = figure_setup(
        cut_coords, cut_len, sagittal, coronal, axial, figure_dim, dpi
    )
    # plot layers
    smooth_plot(
        temp_slices,
        mean_img,
        outdir,
        outfile,
        x,
        y,
        z,
        cut_coords,
        sigma,
        fig,
        axes,
        colormap(cn, cp, group=group),
        group,
        mask,
        mask_slices,
        slice_len,
    )
    # Figure output adjustments
    fig.subplots_adjust(
        left=0.1, right=0.99, top=0.875, bottom=0.01, hspace=0, wspace=0
    )
    fig.suptitle(
        "".join(("Mean of ", outfile)),
        horizontalalignment="left",
        verticalalignment="top",
        fontsize=10 / 3 * cut_len,
        x=0.4,
    )
    if extension == "tiff":
        fig.savefig(
            Path(outdir) / f"{outfile}_mean_plot.tiff",
            bbox_inches="tight",
            pil_kwargs={"compression": "tiff_lzw"},
            pad_inches=0,
        )
    else:
        fig.savefig(
            Path(outdir) / f"{outfile}_mean_plot.{extension}",
            bbox_inches="tight",
            pad_inches=0,
        )
    print("".join((outfile, " mean plot saved")))


# mg change
def main(args):
    parser = parsefn()
    (
        pval,
        vox,
        sigma,
        cp,
        cn,
        sagittal,
        coronal,
        axial,
        x,
        y,
        z,
        figure_dim,
        outdir,
        outfile,
        extension,
        dpi,
        multi,
        atlasdir,
        hemi,
        side,
    ) = parse_inputs(parser, args)

    pval_img = nib.load(pval)
    img1 = pval_img.get_fdata()

    if hemi == "combined":
        mask = os.path.join(
            atlasdir, f"annotation/annotation_hemi_combined_{vox}um.nii.gz"
        )
        brain_template = os.path.join(
            atlasdir, f"template/average_template_{vox}um.nii.gz" # TODO
        )
    elif hemi == "split":
        mask = os.path.join(
            atlasdir, f"annotation/annotation_hemi_{side}_{vox}um.nii.gz"
        )
        brain_template = os.path.join(
            atlasdir, f"template/average_template_{vox}um_{side}.nii.gz"
        )
    brain_mask = nib.load(brain_template).get_fdata()
    

    start_time = time.time()
    cut_len, cut_coords = slice_display(mask, sagittal, coronal, axial, x, y, z)
    # extract Atlas slices for background and outline
    mask_slices = slice_extract(mask, cut_coords, x, y, z, mask.split("/")[-1])
    temp_slices = slice_extract(
        brain_template, cut_coords, x, y, z, brain_template.split("/")[-1]
    )

    # plot first heatmap
    plot(
        img1,
        mask,
        0,
        vox,
        cut_coords,
        cut_len,
        sagittal,
        coronal,
        axial,
        figure_dim,
        outdir,
        outfile[0],
        sigma,
        cn,
        cp,
        mask_slices,
        temp_slices,
        x,
        y,
        z,
        extension,
        dpi,
    )
    end_time = time.time()
    print("Completed in {} seconds".format(end_time - start_time))


if __name__ == "__main__":
    main(sys.argv)
