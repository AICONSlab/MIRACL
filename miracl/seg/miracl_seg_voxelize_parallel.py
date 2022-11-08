#!/usr/bin/env python
# Maged Goubran @ AICONSlab 2022, maged.goubran@utoronto.ca 

# coding: utf-8

import argparse
import logging
import multiprocessing
import os
import sys
import warnings
from datetime import datetime

warnings.simplefilter("ignore", UserWarning)

import cv2
import nibabel as nib
import numpy as np
import scipy as sp
import tifffile as tiff
from joblib import Parallel, delayed
from scipy import ndimage
from skimage.feature import peak_local_max


# ---------
# help fn

def helpmsg(name=None):
    return '''Usage: miracl seg voxelize -s [segmentation tif]

	Voxelizes segmentation results into density maps with Allen atlas resolution

	example: miracl seg voxelize -s seg_sparse.tif -v 10 -d 5

        arguments (required):

        s. Segmentation tif file

        optional arguments:

        v. Voxel size (10, 25, 50um) (def = 10)
        d. Down sample ratio (def = 2) - recommend 2 =< ratio =< 5

    -----

    Main Outputs

        voxelized_seg_sparse.(tif/nii) or nuclear (segmentation results voxelized to ARA resolution)
        voxelized_seg_bin_sparse.(tif/nii) (binarized version)

	'''


# ---------
# Get input arguments

def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg(), add_help=False)
    parser.add_argument('-s', '--seg', type=str, help="binary segmentation tif", required=True)
    parser.add_argument('-d', '--down', type=int, help="down-sample ratio")
    parser.add_argument('-v', '--res', type=int, help="voxel size")

    # parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    seg = args.seg

    res = 10 if args.res is None else args.res
    down = 2 if args.down is None else args.down

    return seg, res, down


# ---------
# Parameters

radius = 1
cpuload = 0.95
cpus = multiprocessing.cpu_count()
ncpus = int(cpuload * cpus)  # 95% of cores used2


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
            self.linebuf = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s" % logname,
        format='%(asctime)s:%(message)s',
        filemode='w')

    stdout_logger = logging.getLogger('STDOUT')
    handler = logging.StreamHandler()
    stdout_logger.addHandler(handler)
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger('STDERR')
    stderr_logger.addHandler(handler)
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)


# ---------
# Define convolution fn

def vox(segflt, kernel, down, i, radius):
    '''
	Convolves image with input kernel then downsamples 
	'''

    # sys.stdout.write("\r processing slice %d ... " % i)
    # sys.stdout.flush()

    # downsample ratio
    dr = 1.0 / down

    slf = segflt[i, :, :]

    cvmean = cv2.filter2D(slf, -1, kernel)
    circv = sp.ndimage.zoom(cvmean, dr, order=0)

    distance = ndimage.distance_transform_edt(circv)
    # local_maxi = peak_local_max(distance, indices=False, min_distance=dist, exclude_border=False, labels=circv)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((10, 10)), exclude_border=False,
                                labels=circv)
    conncomp = ndimage.label(local_maxi)[0]

    return conncomp


# ---------
# Vox seg

def parcomputevox(seg, radius, ncpus, down, outvox):
    '''
	Setups up convolution kernel & computes
	"Vox" fn in parallel
	'''

    filename = os.path.basename(seg)

    print("\n Creating voxelized maps from Clarity segmentations for %s" % filename)

    # read data
    segtif = tiff.imread("%s" % seg)
    segflt = segtif.astype('float32')

    # ---------
    # Setup kernel

    kernel = np.zeros((2 * radius + 1, 2 * radius + 1))
    y, x = np.ogrid[-radius:radius + 1, -radius:radius + 1]
    mask = x ** 2 + y ** 2 <= radius ** 2
    kernel[mask] = 1

    # ---------
    sx = segflt.shape[0]

    print("\n Computing in parallel using %d cpus" % ncpus)

    # convolve image with kernel
    res = []
    res = Parallel(n_jobs=ncpus, backend='threading')(delayed(vox)(segflt, kernel, down, i, radius) for i in range(sx))

    marray = np.asarray(res)

    # downsample ratio
    dr = 1.0 / down

    # down in z 
    # dz = 0.1;
    marray = sp.ndimage.zoom(marray, (dr, 1, 1), order=0)

    # save stack
    tiff.imsave(outvox, marray, bigtiff=True)

    return marray


# ---------
# save to nifti

def savenvoxnii(marray, outvoxnii, res):
    '''
	Saves voxelized tif output to nifti (nii.gz)
	'''

    if not os.path.exists(outvoxnii):
        mat = np.eye(4)

        vx = 0.001 * res

        mat[0, 0] = vx  # or vx/2
        mat[1, 1] = vx
        mat[2, 2] = vx

        img = nib.Nifti1Image(marray, mat)
        nib.save(img, outvoxnii)


# ---------
# main fn

def main(args):
    scriptlog('parallel_voxelization.log')

    startTime = datetime.now()

    parser = parsefn()

    seg, res, down = parse_inputs(parser, args)

    segdir = os.path.dirname(os.path.realpath(seg))

    base = os.path.basename(seg)

    fstr = os.path.splitext(base)

    type = fstr[0].split("_")[1]

    # outvox = '%s/voxelized_seg_%s.tiff' % (segdir, type)
    # outvoxnii = '%s/voxelized_seg_%s.nii.gz' % (segdir, type)

    # if not os.path.exists(outvox):

    #     marray = parcomputevox(seg, radius, ncpus, down, outvox)

    #     savenvoxnii(marray, outvoxnii, res)

    #     print("\n Voxelized maps generated in %s ... Have a good day!\n" % (datetime.now() - startTime))

    # else:

    #     print('\n Voxelized map already created')

    segbasebin = base.replace("seg", "seg_bin")
    segbin = segdir + "/" + segbasebin

    outvoxbin = '%s/voxelized_seg_%s.tiff' % (segdir, type)
    outvoxniibin = '%s/voxelized_seg_%s.nii.gz' % (segdir, type)

    if not os.path.exists(outvoxbin):

        marraybin = parcomputevox(segbin, radius, ncpus, down, outvoxbin)

        savenvoxnii(marraybin, outvoxniibin, res)

        print("\n Voxelized maps generated in %s ... Have a good day!\n" % (datetime.now() - startTime))

    else:

        print('\n Voxelized binarized map already created')


if __name__ == "__main__":
    main(sys.argv)
