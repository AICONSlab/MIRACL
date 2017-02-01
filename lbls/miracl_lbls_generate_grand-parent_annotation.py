#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os
import re
import sys
from datetime import datetime
from os.path import basename
from subprocess import call

import nibabel as nib
import numpy as np
import pandas as pd


# ---------
# help fn

def helpmsg():
    return '''Usage: miracl_lbls_generate_grand-parent_annotation.py -p [parent level (default: 3)] -m [hemisphere: split or combined (default: combined)] -v [voxel size in um: 10, 25 or 50 (default: 25)]

    Generate multi-resolution atlases from Allen labels

    example: miracl_lbls_generate_grand-parent_annotation.py -p 3 -m combined -v 10

    '''

# ---------
# Get input arguments

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-p', '--pl', type=int, help="parent level", required=False)
parser.add_argument('-m', '--hemi', type=str, help="hemisphere mirrored or not", required=False)
parser.add_argument('-v', '--res', type=int, help="voxel size in um", required=False)

args = parser.parse_args()

# check if pars given

if args.pl is None:
    pl = 3
    print("parent level not specified ... choosing default value of %d" % pl)
else:
    assert isinstance(args.pl, int)
    pl = args.pl

if args.hemi is None:
    hemi = "combined"
    print("hemisphere not specified ... choosing default value of %s" % hemi)
else:
    assert isinstance(args.hemi, str)
    hemi = args.hemi

if args.res is None:
    res = 25
    print("voxel size not specified ... choosing default value of %dum" % res)
else:
    assert isinstance(args.res, int)
    res = args.res


# --- Init pars ---

lblsplit = 20000  # number added to contra side
maxannotlbl = 13000  # > max lbl in ipsi

# ------------


def getalllbls(data):
    # get unique lblsfsl
    lbls = np.unique(list(data))
    lbls = lbls[lbls > 0]  # discard negative lbls

    return lbls


def getlblparent(clarinfo, lbls, pl, parentdata, lblsplit, maxannotlbl):
    for l in range(len(lbls)):

        lbl = lbls[l]

        # path id
        path = clarinfo.structure_id_path[clarinfo.id == lbl]

        # remove /
        numpath = re.sub("[/]", ' ', str(path))

        # get digits
        digpath = [int(s) for s in numpath.split() if s.isdigit()]
        digpath = digpath[1:]  # drop 1st index

        # get parent
        if len(path) == 0:
            parent = lbl
        elif len(digpath) < pl:
            parent = digpath[0]
        else:
            parent = digpath[-pl]

        # if np.max(lbls) > lblsplit:
        parent = parent + lblsplit if lbl > maxannotlbl else parent

        sys.stdout.write("\r processing label: %d ... its grand-parent label: %d " % (lbl, parent))
        sys.stdout.flush()

        # replace val
        parentdata[parentdata == lbl] = parent

    return parentdata


def saveniiparents(parentdata, vx, outnii):

    # save parent data as nifti
    mat = np.eye(4) * vx
    mat[3, 3] = 1

    # orient nii
    # tform = nib.orientations.axcodes2ornt(('P', 'I', 'L'))
    # parentort = nib.orientations.apply_orientation(parentdata, tform)

    # Create nifti
    nii = nib.Nifti1Image(parentdata, mat)

    # nifti header info
    nii.header.set_data_dtype(np.int32)
    nib.save(nii, outnii)


def main():
    starttime = datetime.now()

    # load annotations
    print("Reading ARA annotation with %s hemispheres and %d voxel size" % (hemi, res))

    miracl_home = os.environ['MIRACL_HOME']
    nii = '%s/atlases/ara/annotation/annotation_hemi_%s_%dum.nii.gz' % (miracl_home, hemi, res)
    img = nib.load(nii)
    data = img.get_data()

    # load structure graph
    print("Reading ARA ontology structure_graph")
    arastrctcsv = "%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv" % miracl_home
    aragraph = pd.read_csv(arastrctcsv)

    # get lbls
    lbls = getalllbls(data)

    # loop over intensities
    parentdata = np.copy(data)

    print("Computing parent labels at parent-level/generation %d" % pl)

    parentdata = getlblparent(aragraph, lbls, pl, parentdata, lblsplit, maxannotlbl)

    vx = img.header.get_zooms()[0]
    orgname = basename(nii).split('.')[0]
    outnii = '%s_parent-level_%s.nii.gz' % (orgname, pl)
    saveniiparents(parentdata, vx, outnii)

    # orient
    call(["c3d", "%s" % outnii, "-orient", "ASR", "-type", "ushort", "-o", "%s" % outnii])

    # set origin
    # aratemplate = "%s/atlases/ara/template/average_template_50um.nii.gz" % miracl_home
    # aranii = nib.load('%s' % aratemplate)
    #
    # sform = aranii.get_sform()
    # qx = sform[0,3]
    # qy = sform[1,3]
    # qz = sform[2,3]
    #
    # call(["c3d", "%s" % outnii, "-origin", "%fx%fx%fmm" %(qx,qy,qz), "-o", "%s" % outnii])

    print ("\n Grand-parent labels generation done in %s ... Have a good day!\n" % (datetime.now() - starttime))


if __name__ == "__main__":
    main()