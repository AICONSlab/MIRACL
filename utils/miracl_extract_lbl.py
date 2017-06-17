#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import sys

import nibabel as nib
import numpy as np
import pandas as pd
import scipy.ndimage


def helpmsg():
    return ''' 

    Outputs nifti file with only chosen label

    Usage: miracl_extract_lbl.py -i [input (registered) labels] -l [output label] -d [down-sample ratio]

Example: miracl_extract_lbl.py -i clarity_registered_allen_labels.nii.gz -l PL -d 5

    Arguments (required):

        -i Input (registered) Allen labels 

        -l Output label (or seed mask) using Allen atlas ontology acronyms

    Optional arguments:

        -d Down-sample ratio

        '''

    # Dependencies:
    #     Python 2.7


def parseinputs():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-i', '--inlbls', type=str, help="In lbls", required=True)
    parser.add_argument('-l', '--outlbl', type=str, help="Out lbl", required=True)
    parser.add_argument('-d', '--down', type=int, help="Down-sample ratio")

    args = parser.parse_args()

    # check if pars given

    assert isinstance(args.inlbls, str)
    inlbls = args.inlbls

    if not os.path.exists(inlbls):
        sys.exit('%s does not exist ... please check path and rerun script' % inlbls)

    assert isinstance(args.lbls, str)
    outlbl = args.outlbl

    if args.down is None:
        d = 1
        print("\n down-sample ratio not specified ... preserving resolution" % d)
    else:
        assert isinstance(args.down, int)
        d = args.down

    return inlbls, outlbl, d


# ---------

def main():
    # parse in args
    [inlbls, outlbl, d] = parseinputs()

    # extract lbl
    print("\n Reading input labels ...\n")

    inlblsnii = nib.load("%s" % inlbls)
    inlblsdata = inlblsnii.get_data()

    # read Allen ontology
    miracl_home = os.environ['MIRACL_HOME']
    annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # outlbl to lblid
    lblid = annot_csv.id[annot_csv.acronym == "%s" % outlbl]

    mask = inlblsdata.copy()
    mask[mask != lblid] = 0
    mask[mask > 0] = 1  # binarize

    # assuming iso resolution
    vx = inlblsnii.header.get_zooms()[0]

    outvox = vx * d

    mat = np.eye(4) * outvox
    mat[3, 3] = 1

    outnii = "%s_mask.nii.gz" % outlbl

    if d > 1:
        print("\n\n down-sampling mask")

        down = (1.0 / int(d))
        zoom = [down, down, down]
        mask = scipy.ndimage.interpolation.zoom(mask, zoom, order=0)

    masknii = nib.Nifti1Image(mask, mat)
    nib.save(masknii, outnii)


if __name__ == "__main__":
    main()
