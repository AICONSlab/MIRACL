#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import subprocess
import sys
import pandas as pd
import nibabel as nib
import numpy as np

from miracl import ATLAS_DIR


def helpmsg():
    return ''' 

    Outputs nifti file with only chosen label

    Usage: miracl_utilfn_extract_lbl.py -i [input (registered) labels] -l [output label] -d [down-sample ratio]

    Example: miracl_utilfn_extract_lbl.py -i clarity_registered_allen_labels.nii.gz -l PL -m combined -d 5
    
    OR for right PL:
    
    Example: miracl_utilfn_extract_lbl.py -i clarity_registered_allen_labels.nii.gz -l RPL -m split -d 5

    Arguments (required):

        -i Input (registered) Allen labels 

        -l Output label (or seed mask) using Allen atlas ontology acronyms

        -m Labels are combined or split by side

    Optional arguments:

        -d Down-sample ratio

        '''

    # Dependencies:
    #     Python 2.7


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-i', '--inlbls', type=str, help="In lbls", required=True)
    parser.add_argument('-l', '--outlbl', type=str, help="Out lbl", required=True)
    parser.add_argument('-m', '--side', type=str, help="Labels combined or split by side", required=True)
    parser.add_argument('-d', '--down', type=int, help="Down-sample ratio")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    # check if pars given

    assert isinstance(args.inlbls, str)
    inlbls = args.inlbls

    if not os.path.exists(inlbls):
        sys.exit('%s does not exist ... please check path and rerun script' % inlbls)

    assert isinstance(args.outlbl, str)
    outlbl = args.outlbl

    if args.down is None:
        d = 1
        print("\n down-sample ratio not specified ... preserving resolution ")
    else:
        assert isinstance(args.down, int)
        d = args.down

    if args.side is None:
        m = 'combined'
    else:
        m = args.side

    return inlbls, outlbl, d, m


# ---------

def main(args):
    # parse in args
    parser = parsefn()
    inlbls, outlbl, d, m = parse_inputs(parser, args)

    # extract lbl
    print("\n reading input labels ...")

    # in python
    inlblsnii = nib.load("%s" % inlbls)
    inlblsdata = inlblsnii.get_data()
    
    if d > 1:
        print("\n down-sampling mask")
    
        down = (1.0 / int(d))
        inlblsdata = scipy.ndimage.interpolation.zoom(inlblsdata, down, order=0)

    # read Allen ontology
    if m == "combined":
        annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_combined.csv' % ATLAS_DIR)
    else:
        annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_split.csv' % ATLAS_DIR)

    # outlbl to lblid
    lblid = annot_csv.id[annot_csv.acronym == "%s" % outlbl].values[0]

    # in python

    # mask = inlblsdata.copy()
    #
    # print(mask.shape)
    # print(lblid)
    #
    # # extract lbl
    # print("\n extracting label ...")
    #
    # mask[mask != lblid] = 0
    # mask[mask > 0] = 1  # binarize
    #
    # # assuming iso resolution
    # vx = inlblsnii.header.get_zooms()[0]
    #
    # outvox = vx * d
    #
    # mat = np.eye(4) * outvox
    # mat[3, 3] = 1
    #
    # outnii = "%s_mask.nii.gz" % outlbl
    #
    # # extract lbl
    # print("\n saving label image ...")
    #
    # masknii = nib.Nifti1Image(mask, mat)
    # nib.save(masknii, outnii)

    outnii = "%s_mask.nii.gz" % outlbl

    subprocess.check_call("c3d %s -threshold %s %s 1 0 -o %s" % (inlbls, lblid, lblid, outnii),
                     shell=True, stderr=subprocess.STDOUT)



if __name__ == "__main__":
    main(sys.argv)
