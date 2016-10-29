#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import nibabel as nib
import cv2
import glob
from datetime import datetime
import argparse
import os
from Tkinter import Tk
import tkFileDialog

startTime = datetime.now()


def helpmsg(name=None):
    return '''convertTifftoNii.py

Converts Tiff images to Nifti 

    Usage: convertTifftoNii.py

    A GUI will open to choose your:

        - < Input clarity tif dir > : images of only one channel

    ----------

    For command-line / scripting

    Usage: convertTifftoNii.py -f [Tiff folder] -d [Downsample ratio] -o [out nii name]

Example: convertTifftoNii.py -f my_tifs -d 3 -o stroke2

    Optional arguments:

        -cn [chan # for extracting single channel from multiple channel data (default: 1) ]
        -cp [chan prefix (string before channel number in file name). ex: C00 ]
        -ch [chan name (default: thy1_yfp)]
        -vs [voxel size (default: 25um) ]
        -c  [nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

        example: convertTifftoNii.py -f my_tifs -d 3 -o stroke2 -cn 1 -cp C00 -ch Thy1YFP  -vs 0.025 0.025 0.005  -c 5 10 -4

        '''


parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())

parser.add_argument('-f', '--folder', type=str, help="Tiff folder")
parser.add_argument('-d', '--down', type=int, help="Downsample ratio")
parser.add_argument('-cn', '--channum', type=int, help="Channel number")
parser.add_argument('-cp', '--chanprefix', type=str, help="Channel prefix in file name")
parser.add_argument('-ch', '--channame', type=str, help="Channel name")
parser.add_argument('-o', '--outnii', type=str, help="Out nii name")
parser.add_argument('-vs', '--voxelsize', type=int, nargs='+', help="Out nii voxel sizes")
parser.add_argument('-c', '--center', type=int, nargs='+', help="Out nii image center")

args = parser.parse_args()

if args is None:

    print("Running in GUI mode")

    Tk().withdraw()
    indir = tkFileDialog.askdirectory(title='Open clarity dir (with .tif files) by double clicking then OK')

else:

    print("Running in script mode")

    indir = args.folder
    assert isinstance(args.indir, str)
    dr = args.down
    assert isinstance(args.dr, int)
    chann = args.channum
    assert isinstance(args.chann, int)
    chanp = args.chanprefix
    assert isinstance(args.channame, str)
    chan = args.channame
    assert isinstance(args.chan, str)
    vs = args.voxelsize
    assert isinstance(args.vs, int)
    cent = args.center
    assert isinstance(args.cent, int)
    outnii = args.outnii
    assert isinstance(args.outnii, str)

# check if pars given

if args.dr is None:
    dr = 1
    print("down sample ratio not specified ... choosing default value of %d" % dr)

if args.chann is None:
    chann = 1
    print("# channels not specified ... choosing default value of %d" % chann)

if args.chan is None:
    chan = 'thy1_yfp'
    print("channel name not specified ... choosing default value of %s" % chan)

# ---------

def converttiff2nii(indir, dr, chann, chan, vs, cent, ot=None, cp=None):
    """
    :param indir:
    :param dr:
    :param chann:
    :param chan:
    :param vs:
    :param cent:
    :param ot:
    :param cp:
    :return:
    """

    outnii = ot
    chanp = cp

    # Get file lis
    if chanp is None:
        file_list = glob.glob("%s/*.tif" % indir)
    else:
        file_list = glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann))

    # down ratio
    down = (1.0 / int(dr))

    print "\n Converting Tiff images to NII \n"

    # For loop, Load an image,downsample, append into 3D

    data = []
    for x in file_list:
        m = cv2.imread(x, -1)
        mres = cv2.resize(m, (0, 0), fx=down, fy=down, interpolation=cv2.INTER_CUBIC)
        data.append(mres)

    # array type
    data_array = np.array(data, dtype='int16')

    # roll dimensions
    data_array = np.rollaxis(data_array, 0, 3)

    # Voxel size & center default values (corresponding to Allen atlas nii template - 25um res)

    orgres = 0.005  # 5 um

    if args.voxelsize is None:
        outvox = orgres * dr
        vs = [outvox, outvox, orgres]

    if args.center is None:
        cent = [5.7, -6.6, -4]

    # Create nifti
    mat = np.eye(4)
    mat[0, 3] = cent[0]
    mat[1, 3] = cent[1]
    mat[2, 3] = cent[2]
    nii = nib.Nifti1Image(data_array, mat)

    # nifti header info
    nii.header.set_data_dtype(np.int16)
    nii.header.set_zooms([vs[0], vs[1], vs[2]])

    # make out dir
    outdir = 'niftis'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # Save nifti
    if outnii is None:
        niiname = '%s/%schan.nii.gz' % (outdir, chan)
    else:
        niiname = '%s/%s_%02ddown_%schan.nii.gz' % (outdir, outnii, dr, chan)
    nib.save(nii, niiname)

    print ("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - startTime))


# ---------

def main():
    """
    :rtype: nifti file
    """
    converttiff2nii(indir, dr, chann, chan, vs, cent, ot=outnii, cp=chanp)


if __name__ == "__main__":
    main()
