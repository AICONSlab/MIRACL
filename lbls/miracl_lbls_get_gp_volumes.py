#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os
import re
import sys
from datetime import datetime

import nibabel as nib
import numpy as np
import pandas as pd

sys.path.insert(0, '%s/utils' % os.environ['MIRACL_HOME'])
import miracl_utils_endstatement as endstatement

# ---------
# help fn

def helpmsg():
    return '''
    miracl_lbls_get_gp_volumes.py -i [ input labels image ] -ln [ label names ] OR -la [ label acronyms ] -o [ out csv ]
    -s sort by size [ def: 0 -> no ]

    Extract volumes of labels of interest and their subdivisions from input label file (nii format)

    example: miracl_lbls_get_gp_volumes.py -i registered_labels.nii.gz -ln Thalamus Striatum -o gp_volumes.csv
                OR
             miracl_lbls_get_gp_volumes.py -i registered_labels.nii.gz -la TH STR -o gp_volumes.csv

    '''


# ---------
# Get input arguments

def parseinput():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
    parser.add_argument('-i', '--img', type=str, help="Input labels", required=False)
    parser.add_argument('-ln', '--names', type=str, nargs='+', help="Label names", required=False)
    parser.add_argument('-la', '--acronyms', type=str, nargs='+', help="Label acronyms", required=False)
    parser.add_argument('-s', '--sort', type=int, help="Sort by size", required=False, default=0)
    parser.add_argument('-o', '--outfile', type=str, help="Output file",
                        default='grand_parent_volumes.csv')

    args = parser.parse_args()

    # check if pars given
    if (args.names is None) & (args.acronyms is None):
        print(helpmsg())
        sys.exit("either label names [ -la ] or label acronyms [ -la ] must be specified")
    else:
        names = args.names
        acronyms = args.acronyms

    img = args.img
    assert (os.path.exists(img)), '%s does not exist! .. please double check & rerun' % img

    lbls = acronyms if names is None else names

    metric = 'acronym' if names is None else 'name'

    outfile = args.outfile

    s = args.sort

    return lbls, img, metric, outfile, s


def getalllbls(data):
    # get unique lblsfsl
    lbls = np.unique(list(data))
    lbls = lbls[lbls > 0]  # discard negative lbls

    return lbls


# get lbl volume if has chosenid as parent
def getlblvolume(atlasinfo, flatdata, inlblid, imglbl):
    # path id
    path = atlasinfo.structure_id_path[atlasinfo.id == imglbl]

    # remove /
    numpath = re.sub("[/]", ' ', str(path))

    # get digits
    digpath = [int(s) for s in numpath.split() if s.isdigit()]
    digpath = digpath[1:]  # drop 1st index

    return np.count_nonzero(flatdata == imglbl) if inlblid in digpath else 0


def computevolumes(aragraph, dataflat, inlbl, imglbls, metric):
    volumes = []
    # lbl id
    inlblid = aragraph.id[aragraph['%s' % metric] == inlbl].values[0]

    # loop over labels
    for l, imglbl in enumerate(imglbls):
        volume = getlblvolume(aragraph, dataflat, inlblid, imglbl)
        volumes.append(volume)

    return sum(volumes)


def main():
    starttime = datetime.now()

    inlbls, img, metric, outfile, s = parseinput()

    # load img
    print("Reading Input Labels")
    nii = nib.load(img)
    data = nii.get_data()

    # read graph
    print("Reading ARA ontology structure_graph")
    miracl_home = os.environ['MIRACL_HOME']
    arastrctcsv = "%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv" % miracl_home
    aragraph = pd.read_csv(arastrctcsv)

    # get lbls
    imglbls = getalllbls(data)

    # flatten
    dataflat = data.flatten()

    lblvols = []

    print("Computing volumes for input labels...")
    for i, inlbl in enumerate(inlbls):
        vol = computevolumes(aragraph, dataflat, inlbl, imglbls, metric)
        lblvols.append(vol)

    df = pd.DataFrame([inlbls, lblvols])
    if s == 1:
        df = df.T.sort_values(1, ascending=False)
    else:
        df = df.T

    df.columns = ['Labels', 'Volumes (# of voxels)']
    df.to_csv(outfile, index=False)

    # print ("\n Parent labels volume computation done in %s ... Have a good day!\n" % (datetime.now() - starttime))

    endstatement.main(task='Parent labels volume computation', timediff='%s' % (datetime.now() - starttime))


if __name__ == "__main__":
    main()
