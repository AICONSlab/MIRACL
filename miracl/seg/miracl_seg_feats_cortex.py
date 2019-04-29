#!/usr/bin/env python
# Maged Goubran @ 2018, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import sys

import numpy as np
import pandas as pd
import scipy as sp
import tifffile as tiff
from PyQt4.QtGui import QApplication
from skimage.measure import regionprops

sys.path.insert(0, '%s/conv' % os.environ['MIRACL_HOME'])
import miracl_conv_gui_options as gui_opts


# import commands

def helpmsg():
    return '''Usage: miracl_seg_feat_cortex.py -i [segmentation tif] -l [Labels] -m [ binary ROI mask ]

    Computes features of segmented image and summarizes them per label

    example: miracl_seg_feat_cortex.py -i segmentation_sparse/voxelized_seg_bin_sparse.tif -l reg_final/annotation_hemi_combined_25um_clar_vox.tif -m split

        arguments (required):

        i. Voxelized binarized segmentation tif file

        l. Allen labels (registered to clarity) used to summarize features

                reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif

    Optional arguments:

        -o Output file name

        -s Sort values by, options are:

            Mean or StdD or Max or Min or Count or Vol(mm^3)

            Mean -> mean intensity values
            Count -> number of voxels

        -m  Labels hemi (combined or split, default=combined)

        -d  Labels depth (default no depth chosen, all labels)

    ------

    Main Outputs

        clarity_segmentation_features_ara_labels.csv  (segmentation features summarized per ARA labels)

    ------

    Dependencies:

        Python 2.7

        '''


def parseinputs():
    if len(sys.argv) == 1:

        print("Running in GUI mode")

        title = 'Label Statistics'
        vols = ['Input Volume', 'Registered Labels']
        fields = ['Output file name', 'Sort (def = Mean)']

        app = QApplication(sys.argv)
        menu, linedits, labels = gui_opts.OptsMenu(title=title, vols=vols, fields=fields, helpfun=helpmsg())
        menu.show()
        app.exec_()
        app.processEvents()

        volstr = labels[vols[0]].text()
        invol = str(volstr.split(":")[1]).lstrip()

        lblsstr = labels[vols[1]].text()
        lbls = str(lblsstr.split(":")[1]).lstrip()

        outfile = 'clarity_label_statistics.csv' if not linedits[fields[0]].text() else str(linedits[fields[0]].text())
        sort = 'Mean' if not linedits[fields[1]].text() else str(linedits[fields[1]].text())

    else:

        print("\n running in script mode \n")

        parser = argparse.ArgumentParser(description='', usage=helpmsg())

        parser.add_argument('-i', '--invol', type=str, help="In volume", required=True)
        parser.add_argument('-l', '--lbls', type=str, help="Reg lbls", required=True)
        parser.add_argument('-s', '--sort', type=str, help="Sort by", default='Counts')
        parser.add_argument('-m', '--hemi', type=str, help="Labels hemi")
        parser.add_argument('-d', '--depth', type=int, help="Labels depth", default=None)
        parser.add_argument('-c', '--cortex', type=int, help="Filter by cortex", default=None)
        parser.add_argument('-o', '--outfile', type=str, help="Output file",
                            default='clarity_label_statistics.csv')

        args = parser.parse_args()

        invol = args.invol
        lbls = args.lbls
        outfile = args.outfile
        sort = args.sort
        hemi = args.hemi if args.hemi is not None else "combined"
        label_depth = args.depth 
        cortex = args.cortex

    # check if pars given

    assert isinstance(invol, str)
    assert os.path.exists(invol), '%s does not exist ... please check path and rerun script' % invol
    assert isinstance(lbls, str)
    assert os.path.exists(lbls), '%s does not exist ... please check path and rerun script' % lbls
    assert isinstance(outfile, str)
    assert isinstance(sort, str)

    return invol, lbls, outfile, sort, hemi, label_depth, cortex


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

            print ('Swapping x-y')
            reslbls = np.swapaxes(lbls, 1, 2)

        else:

            if segx > lblsx:

                print('Upsampling labels to clarity resolution')

            else:

                print('Downsampling labels to voxelized clarity resolution')

            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

            print('Segmentation shape:', seg.shape)

            print('Resampled labels shape:', reslbls.shape)

            resx = reslbls.shape[1]

            if segx != resx:
                print ('Swapping x-y')
                reslbls = np.swapaxes(reslbls, 1, 2)

    else:

        if segz != lblsz:

            if segx > lblsx:

                print('Upsampling labels to clarity resolution')

            else:

                print('Downsampling labels to voxelized clarity resolution')

            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

        else:

            reslbls = lbls

    return reslbls


def getlblvals(lbls):
    flat = np.ndarray.flatten(lbls)
    posflat = flat[flat > 0]
    counts = np.bincount(posflat)

    return np.nonzero(counts)[0]


# ---------

def main():
    # parse in args

    invol, lbls, outfile, sort, hemi, label_depth, cortex = parseinputs()

    # extract stats
    print(" Extracting stats from input volume using registered labels ...\n")

    # read invol
    # invol = nib.load(invol)
    # voldata = invol.get_data()
    voldata = tiff.imread(invol)

    # read lbls
    # inlbls = nib.load(lbls)
    # lbldata = inlbls.get_data()
    lbldata = tiff.imread(lbls)

    # upsample or swap if needed
    reslbls = upsampleswplbls(voldata, lbldata)

    reslbldata = reslbls.astype(np.uint16)

    # get lbl vals
    # alllbls = getlblvals(reslbldata)

    # compute regionprops
    props = regionprops(reslbldata, intensity_image=voldata)

    # Extract the mean intensities

    print(" Computing region properties \n ")

    # mean_int = np.array([prop.mean_intensity for prop in props])

    # print(" Computing Mean, Max, Min intensities \n ")

    # max_int = np.array([prop.max_intensity for prop in props])
    # min_int = np.array([prop.min_intensity for prop in props])
    areas = np.array([prop.area for prop in props])
    labels = np.array([prop.label for prop in props])

    cellnums = labels.copy()

    # for l, lbl in enumerate(alllbls):
    for l, lbl in enumerate(labels):

        # print("\r processing label:", lbl)

        mask = np.zeros(voldata.shape, dtype=np.uint16)
        mask[reslbldata == lbl] = voldata[reslbldata == lbl]

        if np.max(mask) > 0:
            lbl_areas = [prop.area for prop in regionprops(mask)]
            cellnums[l] = len(list(lbl_areas))
        else:
            cellnums[l] = 0

    # make dataframe 
    # cols = ['LabelID', 'Mean_int', 'Max_int', 'Min_int']
    stats = pd.DataFrame(dict(LabelID=labels, Counts=cellnums, Areas=areas))

    # read fwf
    # outtxt = pd.read_fwf('%s' % outfile)

    # read Allen ontology
    miracl_home = os.environ['MIRACL_HOME']

    # combined or split labels
    if hemi == "combined":
        annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)
    else:
        annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    # extract labels at certain depth only
    if label_depth is not None:
        annot_csv = annot_csv[annot_csv.depth == label_depth]

    # Add label Name, Abrv, PathID

    print(" Creating stats output \n ")

    # make dic
    name_dict = annot_csv.set_index('id')['name'].to_dict()
    acronym_dict = annot_csv.set_index('id')['acronym'].to_dict()
    pathid_dict = annot_csv.set_index('id')['structure_id_path'].to_dict()
    parent_dict = annot_csv.set_index('id')['parent_structure_id'].to_dict()
    depth_dict = annot_csv.set_index('id')['depth'].to_dict()

    # replace label info
    stats['Name'] = stats.LabelID.replace(name_dict)
    stats['Acronym'] = stats.LabelID.replace(acronym_dict)
    stats['Parent'] = stats.LabelID.replace(parent_dict)
    stats['PathID'] = stats.LabelID.replace(pathid_dict)
    stats['Depth'] = stats.LabelID.replace(depth_dict)

    # sort data-frame
    stats = stats.sort_values([sort], ascending=False)
    # remove background
    stats = stats[stats['LabelID'] != 0]

    # re-oder columns with info then sorted column of choice
    cols = ['LabelID', 'Acronym', 'Name', 'Parent', sort]
    dfcols = stats.columns.values
    allcols = np.hstack([cols, dfcols])
    _, idx = np.unique(allcols, return_index=True)
    columns = allcols[np.sort(idx)]

    stats = stats[columns]

    # remove labels not in allen graph (prob interp errors!)
    stats = stats[~stats.Name.apply(lambda x: np.isreal(x))]

    # remove zero counts
    # stats = stats[stats['Counts'] != 0]

    # filter labels not in cortex (isocortex - lbl: 315)
    if cortex:
        stats = stats[stats['PathID'].str.contains('315')]

    # filter by depth
    if label_depth:
        stats = stats[stats['Depth'] <= label_depth]

    # save to csv
    stats.to_csv('%s' % outfile, index=False)


if __name__ == "__main__":
    main()
