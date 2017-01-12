#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import glob
import os
import re
import sys
import tkFileDialog
from Tkinter import Tk
from datetime import datetime

import cv2
import nibabel as nib
import numpy as np

startTime = datetime.now()


# TODOlp: another script for very large files [COLM] with one or multiple stacks
# TODOlp: add check if dir exists (in name correct)
# TODOlp: check center output
# TODOlp: GUI with options to enter

def helpmsg(name=None):
    return '''convertTifftoNii.py

Converts Tiff images to Nifti 

    A GUI will open to choose your:

        - < Input clarity tif dir > : images of only one channel

    ----------

    For command-line / scripting

    Usage: miracl_convertTifftoNii.py -f [Tiff folder]  -o [out nii name]

Example: miracl_convertTifftoNii.py -f my_tifs -o stroke2

    Arguments (required):

        -f Input Clarity tif dir/folder

        -o Output nii name (script will append downsample ratio and channel info to given name)

    Optional arguments:

        -d  [ Downsample ratio (default: 5) ]
        -cn [ chan # for extracting single channel from multiple channel data (default: 1) ]
        -cp [ chan prefix (string before channel number in file name). ex: C00 ]
        -ch [ output chan name (default: eyfp) ]
        -vx [ original resolution in x-y plane in um (default: 5) ]
        -vz [ original thickness (z-axis resolution / spacing between slices) in um (default: 5) ]
        -c  [ nii center (default: 5.7 -6.6 -4) corresponding to Allen atlas nii template ]

        example: miracl_convertTifftoNii.py -f my_tifs -d 3 -o stroke2 -cn 1 -cp C00 -ch Thy1YFP -vx 2.5 -vz 5

        '''


if len(sys.argv) == 1:

    print("Running in GUI mode")

    Tk().withdraw()
    indir = tkFileDialog.askdirectory(title='Open clarity dir (with .tif files) by double clicking then OK')

    outnii = 'clarity'
    d = 5
    chann = 1
    chan = 'eyfp'
    vx = 0.005
    vz = 0.005
    cent = [11.4, 0, 0]
    chanp = None

else:

    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())

    parser.add_argument('-f', '--folder', type=str, help="Tiff folder", required=True)
    parser.add_argument('-d', '--down', type=int, help="Downsample ratio")
    parser.add_argument('-cn', '--channum', type=int, help="Channel number")
    parser.add_argument('-cp', '--chanprefix', type=str, help="Channel prefix in file name")
    parser.add_argument('-ch', '--channame', type=str, help="Channel name")
    parser.add_argument('-o', '--outnii', type=str, help="Out nii name", required=True)
    parser.add_argument('-vx', '--resx', type=float, help="Original x resolution")
    parser.add_argument('-vz', '--resz', type=float, help="Original z resolution")
    parser.add_argument('-c', '--center', type=int, nargs='+', help="Out nii image center")

    args = parser.parse_args()

    print("Running in script mode")

    # check if pars given

    assert isinstance(args.folder, str)
    indir = args.folder

    if args.outnii is None:
        outnii = 'clarity'
    else:
        assert isinstance(args.outnii, str)
        outnii = args.outnii

    if args.down is None:
        d = 5
        print("down sample ratio not specified ... choosing default value of %d" % d)
    else:
        assert isinstance(args.down, int)
        d = args.down

    if args.channum is None:
        chann = 1
        print("channel # not specified ... choosing default value of %d" % chann)
    else:
        assert isinstance(args.channum, int)
        chann = args.channum

        if args.chanprefix is None:
            sys.exit('-cp (channel prefix) not specified ')

        chanp = args.chanprefix if args.chanprefix is not None else None

    if args.channame is None:
        chan = 'eyfp'
        print("channel name not specified ... choosing default value of %s" % chan)
    else:
        assert isinstance(args.channame, str)
        chan = args.channame

    if args.resx is None:
        vx = 0.005  # 5 um
    else:
        vx = args.resx
        vx /= float(1000)

    if args.resz is None:
        vz = 0.005  # 5 um
    else:
        vz = args.resz
        vz /= float(1000)

    if args.center is None:
        cent = [11.4, 0, 0]
    else:
        cent = args.center


# ---------

# sort fn


def numericalSort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


# ---------

def converttiff2nii(indir, d, chann, chan, vx=None, vz=None, cent=None, ot=None, cp=None):
    """
    :param indir:
    :param d:
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

    outvox = vx * d
    vs = [outvox, outvox, vz]

    # Get file lis

    # sort files
    if chanp is None:
        file_list = sorted(glob.glob("%s/*.tif" % indir), key=numericalSort)
    else:
        file_list = sorted(glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann)), key=numericalSort)

    # down ratio
    down = (1.0 / int(d))

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

    # Create nifti
    mat = np.eye(4) * outvox
    mat[0, 3] = cent[0]
    mat[1, 3] = cent[1]
    mat[2, 3] = cent[2]
    mat[2, 2] = vz
    mat[3, 3] = 1

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
        niiname = '%s/%s_%02dx_down_%s_chan.nii.gz' % (outdir, outnii, d, chan)
    nib.save(nii, niiname)

    print ("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - startTime))


# ---------

def main():
    """
    :rtype: nifti file
    """
    converttiff2nii(indir, d, chann, chan, vx, vz, cent, ot=outnii, cp=chanp)

if __name__ == "__main__":
    main()
