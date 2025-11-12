#!/usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@utoronto.ca

# coding: utf-8

import argparse
import logging
import multiprocessing
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import scipy as sp
import tifffile as tiff
from joblib import Parallel, delayed
from scipy import ndimage
from skimage.measure import regionprops, label
import nibabel as nib
from miracl.system.miracl_utilfns import none_or_str


# ---------
# help fn


def helpmsg(name=None):
    return """Usage: miracl_seg_feat_extract.py -s [segmentation tif] -l [Labels] -m [ binary ROI mask ]

    Computes features of segmented image and summarizes them per label

    example: miracl_seg_feat_extract.py -s segmentation_sparse/voxelized_seg_bin_sparse.tif -l reg_final/annotation_hemi_combined_25um_clar_vox.tif -m mask.tif

        arguments (required):

        s. Voxelized binarized segmentation tif or nifti file

        l. Allen labels (registered to clarity) used to summarize features (tif or nifti)

               e.g. reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif

        optional arguments:

        m. Mask to choose a region of interest (ROI) to analyze (binary image, 0 value outside ROI)

                Will extract features from allen labels within ROI
                Should be in clarity space

    ------

    Main Outputs

        clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)

    """


# ---------
# Get input arguments


def parsefn():
    parser = argparse.ArgumentParser(description="", usage=helpmsg(), add_help=False)
    parser.add_argument(
        "-s",
        "--seg",
        type=str,
        help="segmentation tif",
        required=True,
    )
    parser.add_argument(
        "-l",
        "--lbl",
        type=str,
        help="label annotations",
        required=True,
    )
    parser.add_argument(
        "-m",
        "--mask",
        type=none_or_str,
        help="ROI mask",
    )

    # parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    inseg = args.seg
    inlbls = args.lbl

    return inseg, inlbls


# ---------
# Logging fn


def scriptlog(logname):
    class StreamToLogger(object):
        """
        Fake file-like stream object that redirects writes to a logger instance.
        """

        def __init__(self, logger, log_level=logging.INFO):
            self.logger = logger
            self.log_level = log_level
            self.linebuf = ""

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s" % logname,
        format="%(asctime)s:%(message)s",
        filemode="w",
    )

    stdout_logger = logging.getLogger("STDOUT")
    handler = logging.StreamHandler()
    stdout_logger.addHandler(handler)
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger("STDERR")
    stderr_logger.addHandler(handler)
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)


# ---------


def upsampleswplbls(seg, lbls):
    segx = seg.shape[1]
    segy = seg.shape[2]
    segz = seg.shape[0]

    lblsx = lbls.shape[1]
    lblsy = lbls.shape[2]
    lblsz = lbls.shape[0]

    if segx != lblsx:
        if segx == lblsy:
            print("Swapping x-y")
            reslbls = np.swapaxes(lbls, 1, 2)

        else:
            if segx > lblsx:
                print("Upsampling labels to clarity resolution")

            else:
                print("Downsampling labels to voxelized clarity resolution")

            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

            print("Segmentation shape:", seg.shape)

            print("Resampled labels shape:", reslbls.shape)

            resx = reslbls.shape[1]

            if segx != resx:
                print("Swapping x-y")
                reslbls = np.swapaxes(reslbls, 1, 2)

    else:
        if segz != lblsz:
            if segx > lblsx:
                print("Upsampling labels to clarity resolution")

            else:
                print("Downsampling labels to voxelized clarity resolution")

            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

        else:
            reslbls = lbls

    return reslbls


# ---------
# Get region prop fn


def computearea(seg, lbls, l):
    sys.stdout.write("\r processing label %d ... " % l)
    sys.stdout.flush()

    # print 'processing label ', l

    lbl = lbls == l
    numvox = np.sum(lbl)
    ## AA CHANGE
    # mask = np.zeros(seg.shape, dtype=np.uint16)
    mask = np.zeros(seg.shape, dtype=seg.dtype)
    ## AA CHANGES END
    mask[lbl] = seg[lbl]

    # if np.max(mask) > 0:
    #     areas = (prop.area for prop in regionprops(mask))
    #     areas = np.array(list(areas))
    #     avgarea = np.nanmean(areas)
    #     stdarea = np.nanstd(areas)
    #     maxarea = np.nanmax(areas)
    #     cellnum = len(list(areas))
    #     celldens = (float(cellnum) / numvox) * 1e3  # assuming 1um res
    # else:
    #     avgarea = 0
    #     stdarea = 0
    #     maxarea = 0
    #     cellnum = 0
    #     celldens = 0

    ## AA CHANGES
    # Use binary threshold directly
    thr = 0.1
    mask = np.abs(mask)
    mask_binary = mask > thr

    if np.any(mask_binary):
        _, cc_num = label(mask_binary, return_num=True)

        # Compute stats only where signal exists
        mean_intensity = np.mean(mask[mask_binary])
        max_intensity = np.max(mask[mask_binary])
        std_intensity = np.std(mask[mask_binary])

        # Axon density = fraction of region occupied by axons
        density = float(np.sum(mask_binary)) / numvox
    else:
        cc_num = 0
        mean_intensity = 0.0
        std_intensity = 0.0
        density = 0.0
        max_intensity = 0

    return mean_intensity, std_intensity, max_intensity, cc_num, density, numvox
    ## AA CHANGES END

    # return avgarea, stdarea, maxarea, cellnum, celldens


# ---------
# Run feat extract for all lbls


def runalllblspar(seg, lbls, ncpus, alllbls):
    allprops = Parallel(n_jobs=ncpus, backend="threading")(
        delayed(computearea)(seg, lbls, l) for i, l in enumerate(alllbls)
    )
    # allprops = np.asarray(allprops)
    # allareas = allprops[:, 0]
    # allstdareas = allprops[:, 1]
    # allmaxareas = allprops[:, 2]
    # allnums = allprops[:, 3]
    # alldens = allprops[:, 4]

    # AA CHANGES
    allprops = np.asarray(allprops)
    allareas = allprops[:, 0]
    allstdareas = allprops[:, 1]
    allmaxareas = allprops[:, 2]
    allnums = allprops[:, 3]
    alldens = allprops[:, 4]
    allnumvox = allprops[:, 5]

    return allareas, allstdareas, allmaxareas, allnums, alldens, allnumvox
    ## AA CHANGES END
    # return allareas, allstdareas, allmaxareas, allnums, alldens


# ---------


def getlblvals(lbls):
    flat = np.ndarray.flatten(lbls)
    posflat = flat[flat > 0]
    counts = np.bincount(posflat)

    return np.nonzero(counts)[0]


# ---------
# main fn


def main(args):
    scriptlog("feature_extraction.log")

    startTime = datetime.now()

    cpuload = 0.8
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)  # 95% of cores used
    parser = parsefn()
    inseg, inlbls = parse_inputs(parser, args)

    print("\nRunning feature extraction with the following settings")
    print(f"Segmentation tif: {inseg}")
    print(f"Label annotation: {inlbls}")
    tmp_args, tmp_unknown = parser.parse_known_args()
    print(f"Mask:             {tmp_args.mask}")

    # open seg
    ## AA CHANGE
    # print("Reading segmentation")
    # seg = tiff.imread(inseg)
    if inseg.endswith((".tif", ".tiff")):
        seg = tiff.imread(inseg)
    elif inseg.endswith((".nii", ".nii.gz")):
        seg = nib.load(inseg).get_fdata()

    # # open lbls
    # print("Reading labels")
    # lbls = tiff.imread(inlbls)
    if inlbls.endswith((".tif", ".tiff")):
        lbls = tiff.imread(inlbls)
    elif inlbls.endswith((".nii", ".nii.gz")):
        lbls = nib.load(inlbls).get_fdata()

    print(f"seg and lbls loaded with the shape of {seg.shape} and {lbls.shape}")
    ## AA CHANGE ENDED

    if (
        (lbls.dtype == np.float64)
        or (lbls.dtype == np.float32)
        or (lbls.dtype == np.int32)
    ):
        lbls = lbls.astype(np.int16)

    # check mask
    if tmp_args.mask is None:
        # get all lbls
        alllbls = getlblvals(lbls)

        # upsample or swap if needed
        reslbls = upsampleswplbls(seg, lbls)

    else:
        inmas = tmp_args.mask
        maslbls = np.copy(lbls)

        maslbls[inmas == 0] = 0

        # get all lbls
        alllbls = getlblvals(maslbls)

        # upsample or swap if needed
        reslbls = upsampleswplbls(seg, maslbls)

    print("Computing Feature extraction...")
    ## AA CHANGES
    # [allareas, allstdareas, allmaxareas, allnums, alldens] = runalllblspar(seg, reslbls, ncpus, alllbls)
    [allareas, allstdareas, allmaxareas, allnums, alldens, allnumvox] = runalllblspar(
        seg, reslbls, ncpus, alllbls
    )
    ## AA CHANGES END

    print("\n Exporting features to csv file")

    # This will extract '/code' from MIRACL_HOME variable ('/code/miracl')
    # to set the correct path to the atlases
    atlases_home = os.path.split(os.environ["MIRACL_HOME"])[0]

    if np.max(alllbls) > 20000:
        graph = pd.read_csv(
            "%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv" % atlases_home
        )

    else:
        graph = pd.read_csv(
            "%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv" % atlases_home
        )

    # get attributes
    # names = graph.name[graph.id.isin(alllbls)]
    # abrvs = graph.acronym[graph.id.isin(alllbls)]
    # parents = graph.parent_structure_id[graph.id.isin(alllbls)]
    # paths = graph.structure_id_path[graph.id.isin(alllbls)]

    # nrows = allareas

    # propsdf = pd.DataFrame(
    #     dict(LabelID=alllbls, LabelAbrv=abrvs, LabelName=names, ParentID=parents, IDPath=paths, Count=allnums,
    #          Density=alldens, VolumeAvg=allareas, VolumeStd=allstdareas, VolumeMax=allmaxareas))

    # Filter labels not included

    ## AA CHANGE
    # propsdf = pd.DataFrame(
    #     dict(LabelID=alllbls, Count=allnums, Density=alldens, VolumeAvg=allareas, VolumeStd=allstdareas,
    #          VolumeMax=allmaxareas))

    propsdf = pd.DataFrame(
        dict(
            LabelID=alllbls,
            Count=allnums,
            Density=alldens,
            VolumeAvg=allareas,
            VolumeStd=allstdareas,
            VolumeMax=allmaxareas,
            Numvox=allnumvox,
        )
    )
    propsdf = propsdf[propsdf.LabelID.isin(graph.id)]

    # make dicts
    name_dic = dict(zip(graph.id, graph.name))
    abrv_dic = dict(zip(graph.id, graph.acronym))
    parents_dic = dict(zip(graph.id, graph.parent_structure_id))
    paths_dic = dict(zip(graph.id, graph.structure_id_path))

    propsdf["LabelName"] = propsdf.LabelID
    propsdf["LabelAbrv"] = propsdf.LabelID
    propsdf["ParentID"] = propsdf.LabelID
    propsdf["IDPath"] = propsdf.LabelID

    propsdf = propsdf.replace({"LabelName": name_dic})
    propsdf = propsdf.replace({"LabelAbrv": abrv_dic})
    propsdf = propsdf.replace({"IDPath": paths_dic})
    propsdf["ParentID"] = propsdf.ParentID.map(parents_dic)

    cols = [
        "LabelID",
        "LabelAbrv",
        "LabelName",
        "ParentID",
        "IDPath",
        "Count",
        "Density",
        "VolumeAvg",
        "VolumeStd",
        "VolumeMax",
        "Numvox",
    ]
    propsdf = propsdf[cols]

    segdir = os.path.dirname(os.path.realpath(inseg))

    propscsv = "%s/clarity_segmentation_features_ara_labels_split.csv" % segdir
    propsdf.to_csv(propscsv)

    print(
        "\n Features Computation done in %s ... Have a good day!\n"
        % (datetime.now() - startTime)
    )


if __name__ == "__main__":
    main(sys.argv)
