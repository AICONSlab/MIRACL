#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import scipy as sp
from scipy import ndimage
import tifffile as tiff
import cv2
from joblib import Parallel, delayed
import os
import argparse
from datetime import datetime
import nibabel as nib
import multiprocessing
import sys
import logging

# ---------
# help fn

def helpmsg(name=None): 

	return '''mouse_par_voxelize_seg.py -s [binary segmentation tif]

	Voxelizes segmentation results into density maps with Allen atlas resolution

	example: mouse_single_corr_lbls.py -s seg_bin.tif  
	'''
# ---------
# Get input arguments

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-s','--seg', type=str, help="binary segmentation tif", required=True)

args = parser.parse_args()
seg = args.seg

# ---------
# Parameters

radius = 5
down = 5
cpuload = 0.95
cpus = multiprocessing.cpu_count()
ncpus = int(cpuload*cpus) # 80% of cores used

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

def vox(segflt,kernel,dr,i):
	'''
	Convolves image with input kernel then 
	downsamples using chosen interpolation
	'''

	# sys.stdout.write("\r processing slice %d ... " % i)
	# sys.stdout.flush()

	slf = segflt[i,:,:]

	cvmean = cv2.filter2D(slf,-1,kernel)
	circv = sp.ndimage.zoom(cvmean,dr,order=1)  

	return circv/255 

# ---------
# Vox seg

def parcomputevox(seg,radius,ncpus,down,outvox):
	'''
	Setups up convolution kernel & computes
	"Vox" fn in parallel
	'''

	# downsample ratio
	dr = 1.0/down

	print "\n Creating voxelized maps from Clarity segmentations"
	
	# read data
	segtif = tiff.imread("%s" % seg )  
	segflt = segtif.astype('float32')

	# ---------
	# Setup kernel 

	kernel = np.zeros((2*radius+1, 2*radius+1))
	y,x = np.ogrid[-radius:radius+1, -radius:radius+1]
	mask = x**2 + y**2 <= radius**2
	kernel[mask] = 1

	# ---------
	sx = segflt.shape[0]

	print "\n Computing in parallel using %d cpus" % ncpus

	# convolve image with kernel
	res = []
	res = Parallel(n_jobs=ncpus,backend='threading')(delayed (vox)(segflt,kernel,dr,i) for i in range(sx))

	marray = np.asarray(res)

	# save stack 
	tiff.imsave(outvox,marray)

	return marray	

# ---------
# save to nifti

def savenvoxnii(marray):
	'''
	Saves voxelized tif output to nifti (nii.gz)
	'''

	outvoxnii = 'voxelized_seg_bin.nii.gz' 

	if not os.path.exists(outvoxnii):

		mat = np.eye(4)
		mat[0,0] = 0.0025
		mat[1,1] = 0.025
		mat[2,2] = 0.025

		img = nib.Nifti1Image(marray, mat)
		nib.save(img, outvoxnii)

# ---------
# main fn

def main():

	scriptlog('voxelize.log')

	startTime = datetime.now()

	outvox = 'voxelized_seg_bin.tif'  

	if not os.path.exists(outvox):	

		marray = parcomputevox(seg,radius,ncpus,down,outvox)

		savenvoxnii(marray)

		print ("\n Voxelized maps generated in %s ... Have a good day!\n" % (datetime.now() - startTime)) 	

	else:

		print ('\n Voxelized map already created')

if __name__ == "__main__":
	# sys.exit(main())
	main()