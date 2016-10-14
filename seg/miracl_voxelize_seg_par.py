#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import scipy as sp
from scipy import ndimage
import tifffile as tiff
import cv2
from joblib import Parallel, delayed
import glob
import sys
import os
import argparse
from datetime import datetime
import nibabel as nib

# ---------

# Parameters

radius = 5
ncpus = 32 

down = 5

# ---------

# help fn

def helpmsg(name=None): 

    return '''mouse_par_voxelize_seg.py -g [group] -m [mouse id]

Voxelizes segmentation results into density maps with Allen atlas resolution

example: mouse_single_corr_lbls.py -g stroke -m 01  
        '''

# ---------

# Get input arguments

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-g','--group', type=str, help="stroke/control", required=True)
parser.add_argument('-m','--mouse', type=int, help="mouse id", required=True)

args = parser.parse_args()

mouse = m = args.mouse
grp = args.group

m = "%02d" % m

projdir='/data/clarity_project/mouse/stroke_study'

# ---------

startTime = datetime.now()

# ---------

print "\n Creating voxelized maps from Clarity segmentations \n"

# Get stacks and loop over
subjdir = '%s/%s/%s/CLARITY/tifs/filter0' % (projdir,grp,m)

# Get stack list
stack_list = glob.glob("%s/stack*" % subjdir)

# downsample ratio
dr = 1.0/down

marrays = []

# ---------

# Define convolution fn

def vox(segflt,i):
    
    slf = segflt[i,:,:]
    
    cvmean = cv2.filter2D(slf,-1,kernel)
    circv = sp.ndimage.zoom(cvmean,dr,order=5)  

    return circv/255 

# ---------

# Loop over stacks 

iterlist = iter(stack_list)
next(iterlist) # skip first stack

segdir = '%s/%s/%s/seg' % (projdir,grp,m)

outtif = '%s/comb_vox_seg.tif' % segdir 

if not os.path.exists(outtif):

	for i,stack in enumerate(iterlist):

		i = i+2 # indx 0 & skip 1

		outvox = '%s/vox_seg.tif' % stack 

		if not os.path.exists(outvox):	

			# print 

			sys.stdout.write("\r Creating voxelized map for Stack %d ... " % i)
			sys.stdout.flush()
			
			# read data
			
			tt = tiff.imread("%s/seg_bin.tif" % (stack) )  
			segflt = tt.astype('float32')

			# ---------

			# Setup kernel 

			kernel = np.zeros((2*radius+1, 2*radius+1))
			y,x = np.ogrid[-radius:radius+1, -radius:radius+1]
			mask = x**2 + y**2 <= radius**2
			kernel[mask] = 1

			# ---------

			sx = segflt.shape[0]

			# convolve image with kernel

			res = []
			res = Parallel(n_jobs=ncpus)(delayed (vox)(segflt,i) for i in range(sx))

			marray = np.asarray(res)

			# save stack 
			tiff.imsave('%s/vox_seg.tif' % stack , marray)

		else:

			print 'Voxelized map already created for stack %d' % i 

			intiff = tiff.imread('%s/vox_seg.tif' % stack)
			marray = np.asarray(intiff)
			print marray.shape

		marrays.append(marray)

# get stack dims

	sx = marray.shape[0]
	sy = marray.shape[1]
	sz = marray.shape[2]	

	# combine voxelized stacks

	sxd = 125

	sxm = (sxd*(len(stack_list)-2))

	del marrays[len(stack_list)-2] # drop last stack

	combvox = np.asarray(marrays).reshape(sxm,sy,sz)

	# save comb stack 

	tiff.imsave(outtif, combvox)

else:

	print 'Voxelized map already created for mouse %s' % m

# ---------

# save to nifti

outnii = '%s/vox_seg.nii.gz' % segdir

if not os.path.exists(outnii):

	if os.path.exists(outtif):

		combvox = tiff.imread(outtif);

	mat = np.eye(4)
	mat[0,0] = 0.0025
	mat[1,1] = 0.025
	mat[2,2] = 0.025

	img = nib.Nifti1Image(combvox, mat)
	nib.save(img, outnii)

# ---------

print ("\n Voxelized maps generated in %s ... Have a good day!\n" % (datetime.now() - startTime)) 



# old fn

# def pargf(segflt,i):
    
#     slf=segflt[i,:,:]
#     circmean = gf(slf, np.mean, footprint=kernel, mode='constant')
    
#     return sp.ndimage.zoom(circmean,0.1,order=5) 

