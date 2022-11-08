#!/usr/bin/env python
# Maged Goubran @ AICONSlab 2022, maged.goubran@utoronto.ca

# coding: utf-8

import argparse
import os
import subprocess
import sys
import scipy as sp
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication
from miracl.conv import miracl_conv_gui_options as gui_opts
from miracl.utilfn.depends_manager import add_paths

import nibabel as nib

from miracl import ATLAS_DIR

def helpmsg():
    return '''Usage: miracl_lbls_stats.py 

    Computes Allen label stats of input volume 

    A GUI will open to choose your:

        - < input volume > 

        - < registered Allen labels >

    ----------

    For command-line / scripting

    Usage: miracl_lbls_stats.py -i [input volume] -l [reg Allen labels] -o [ out csv ]

    Example: miracl_lbls_stats.py -i clarity_downsample_05x_virus_chan.nii.gz -l registered_labels.nii.gz -o label_stats.csv
        -s Count

    Arguments (required):

        -i Input volume

        -l Registered Allen labels

    Optional arguments:

        -o Output file name

        -s Sort values by, options are:

            Mean or StdD or Max or Min or Count or Vol(mm^3)

            Mean -> mean intensity values
            Count -> number of voxels

        -m  Labels hemi (combined or split, default=combined)

        -d  Labels depth (default no depth chosen, all labels)

        '''

    # Dependencies:

    #     ImageMaths (ANTs)
    #     Python 2.7


def parsefn():
    if len(sys.argv) >= 3 and sys.argv[-2] == 'lbl' and sys.argv[-1] == 'stats':
        parser = argparse.ArgumentParser(description='', usage=helpmsg())
    else:
        parser = argparse.ArgumentParser(description='', usage=helpmsg())

        parser.add_argument('-i', '--invol', type=str, help="In volume")
        parser.add_argument('-l', '--lbls', type=str, help="Reg lbls")
        parser.add_argument('-s', '--sort', type=str, help="Sort by", default='Mean')
        parser.add_argument('-m', '--hemi', type=str, help="Labels hemi")
        parser.add_argument('-d', '--depth', type=int, help="Labels depth")
        parser.add_argument('-r', '--ratio', type=str, help="Tractography (.trk) file used to generate tract ratio")
        parser.add_argument('-o', '--outfile', type=str, help="Output file",
                            default='clarity_label_statistics.csv')

        return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    if sys.argv[-2] == 'lbls' and sys.argv[-1] == 'stats':
        print("Running in GUI mode")

        title = 'Label Statistics'
        vols = ['Input Volume', 'Registered Labels']
        fields = ['Output file name', 'Sort (def = Mean)', 'Hemi', 'Label depth']

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
        hemi = 'Combined' if not linedits[fields[2]].text() else str(linedits[fields[2]].text())
        label_depth = '' if not linedits[fields[3]].text() else str(linedits[fields[3]].text())

    else:
        print("\n running in script mode \n")

        invol = args.invol
        lbls = args.lbls
        outfile = args.outfile
        sort = args.sort
        hemi = args.hemi if args.hemi is not None else "combined"
        label_depth = args.depth if args.depth is not None else None
        ratio = args.ratio if args.ratio is not None else None

        # check if pars given

        assert isinstance(invol, str)
        assert os.path.exists(invol), '%s does not exist ... please check path and rerun script' % invol
        assert isinstance(lbls, str)
        assert os.path.exists(lbls), '%s does not exist ... please check path and rerun script' % lbls
        assert isinstance(outfile, str)
        assert isinstance(sort, str)

    return invol, lbls, outfile, sort, hemi, ratio, label_depth


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

            print('Swapping x-y')
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
                print('Swapping x-y')
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


def get_count_stats(invol, lbls):
    ''' Given an input volume and a label mask, generate a table of statistics for each label in the label mask.
    Unlike c3d's "lstat", this method extracts the following statistics:

    "intensity count": within a label, the number of voxels in the input with an intensity greater than 0

    invol (str): path to a medical image
    lbls (str): path to a label image
    '''
    # load images
    invol_img = nib.load(invol)
    invol_arr = invol_img.get_data()
    
    lbls_img = nib.load(lbls)
    lbls_arr = lbls_img.get_data()

    # create list to store results
    res = []

    # for each intensity value in lbl array
    ids = list(np.unique(lbls_arr))
    for label_id in ids:
        masked_arr = invol_arr[lbls_arr == label_id]

        intensity_count = masked_arr > 0
        intensity_count = intensity_count.sum()

        # create dict that stores {intensity_value, count, total}
        res.append({'LabelID': int(label_id), "intensity_count": intensity_count})

    # convert list to pandas dataframe, return
    return pd.DataFrame(res)

def get_tract_count(tract_file):
    """ Given a tractography file, return the number of tracts
    
    Args: tract_file - trk file
    """
    print('reading sta streamlines')
    streamlines_file = nib.streamlines.load(tract_file)
    streams, hdr = streamlines_file.streamlines, streamlines_file.header

    return len(streams)


# ---------

def main(args):
    # parse in args
    parser = parsefn()
    invol, lbls, outfile, sort, hemi, ratio, label_depth = parse_inputs(parser, args)

    # extract stats
    print(" Extracting stats from input volume using registered labels ...\n")

    # subprocess.check_call('ImageIntensityStatistics 3 %s %s > %s' % (invol, lbls, outfile), shell=True,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)

    try:
        subprocess.check_call("c3d %s %s -lstat | sed -e 's/^[ ]*//' | tr -s '[:blank:]' ',' | sed -r '2,$s/(.*),(.*),/\\1 \\2 /'> %s" % (invol, lbls, outfile), shell=True)
    except subprocess.CalledProcessError as err:
        print("Error occurred during the function call. It is possible that %s and %s had different spacings" % (invol, lbls))
        sys.exit(1)
    except OSError:
        sys.exit(1)

    # read fwf
    out_stats = pd.read_csv('%s' % outfile)

    # read Allen ontology -- combined or split labels
    if hemi == "combined":
        annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_combined.csv' % ATLAS_DIR)
    else:
        annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_split.csv' % ATLAS_DIR)

    # extract labels at certain depth only
    if label_depth is not None:
        annot_csv = annot_csv[annot_csv.depth == label_depth]

    # generate additional stats, merge into output file
    count_stats = get_count_stats(invol, lbls)
    out_stats = out_stats.merge(count_stats, on="LabelID", how="left")
    # out_stats = pd.concat([out_stats, count_stats], axis=1, join="inner")

    # generate tract ratio
    if ratio:
        tract_count = get_tract_count(ratio)
        out_stats["tract_ratio"] = out_stats["Mean"] / tract_count

    # Add label Name, Abrv, PathID

    # make dic
    name_dict = annot_csv.set_index('id')['name'].to_dict()
    acronym_dict = annot_csv.set_index('id')['acronym'].to_dict()
    pathid_dict = annot_csv.set_index('id')['structure_id_path'].to_dict()
    parent_dict = annot_csv.set_index('id')['parent_structure_id'].to_dict()

    # replace label info
    out_stats['name'] = out_stats.LabelID.replace(name_dict)
    out_stats['acronym'] = out_stats.LabelID.replace(acronym_dict)
    out_stats['parent'] = out_stats.LabelID.replace(parent_dict)
    out_stats['pathid'] = out_stats.LabelID.replace(pathid_dict)

    # sort data-frame
    out_stats = out_stats.sort_values([sort], ascending=False)
    # remove background
    out_stats = out_stats[out_stats['LabelID'] != 0]

    # re-oder columns with info then sorted column of choice
    cols = ['LabelID', 'acronym', 'name', 'parent', sort]
    df_cols = out_stats.columns.values
    all_cols = np.hstack([cols, df_cols])
    _, idx = np.unique(all_cols, return_index=True)
    columns = all_cols[np.sort(idx)]

    out_stats = out_stats[columns]

    # remove labels not in allen graph (prob interp errors!)
    out_stats = out_stats[~out_stats.name.apply(lambda x: np.isreal(x))]

    # save to csv
    out_stats.to_csv('%s' % outfile, index=False)


if __name__ == "__main__":
    main(sys.argv)

# TODOlp
# copy tform if tolerance exceeds limit
