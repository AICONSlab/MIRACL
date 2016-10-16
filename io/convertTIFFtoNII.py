#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import sys
import nibabel as nib
import cv2
import glob
from datetime import datetime
import argparse
import os

startTime = datetime.now()

def helpmsg(name=None): 

    return '''convertTifftoNii.py -f [Tiff folder] -d [Downsample ratio] -cn [chan #] -cp [chan prefix] - ch [chan name] -o [out nii name] 

Converts Tiff images to Nifti 

Example: convertTifftoNii.py -f my_tifs -d 3 -cn 1 -cp C00 -ch Thy1YFP -o stroke2  

	Optional arguments:	-vs [voxel size] -c [nii center]  

		example: -vs 0.025 0.025 0.005  -c 5 10 -4  

		if not set will default to values in example (corresponding to Allen atlas nii template - 25um res)			

        '''

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())

parser.add_argument('-f','--folder', type=str, help="Tiff folder", required=True)
parser.add_argument('-d','--down', type=int, help="Downsample ratio", required=True)
parser.add_argument('-cn','--channum', type=int, help="Channel number", required=True)
parser.add_argument('-cp','--chanprefix', type=str, help="Channel prefix in file name", required=True)
parser.add_argument('-ch','--channame', type=str, help="Channel name", required=True)
parser.add_argument('-o','--outnii', type=str, help="Out nii name", required=True)
parser.add_argument('-vs','--voxelsize', type=int, nargs='+', help="Out nii voxel sizes")
parser.add_argument('-c','--center', type=int, nargs='+', help="Out nii image center")

args = parser.parse_args()

indir = args.folder
dr = args.down
chann = args.channum
chanp = args.chanprefix
chan = args.channame
vs = args.voxelsize
cent = args.center
outnii = args.outnii

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

def converttiff2nii(indir,dr,chann,chanp,chan,vs,cent,ounii):

	# Get file lis
	file_list=glob.glob("%s/*%s%01d*.tif" % (indir,chanp,chann))

	#down ratio
	down=(1.0/int(dr))

	print "\n Converting Tiff images to NII \n"

	# Par loop?!
	# For loop, Load an image,downsample, append into 3D

	data = []
	for x in file_list:
		m = cv2.imread(x,-1)	
		mres = cv2.resize(m,(0,0),fx=down,fy=down,interpolation=cv2.INTER_CUBIC)
		data.append(mres)

	# array type
	data_array = np.array(data,dtype='int16')    

	# roll dimensions
	data_array = np.rollaxis(data_array,0,3)

	# Voxel size & center default values (corresponding to Allen atlas nii template - 25um res)

	orgres = 0.005 # 5 um 

	if args.voxelsize is None:

		outvox = orgres * dr
		vs = [outvox,outvox,orgres]

	if args.center is None:

		cent = [5, 10, -4]

	# Create nifti
	mat = np.eye(4)
	mat[0,3] = cent[0]
	mat[1,3] = cent[1]
	mat[2,3] = cent[2]
	nii = nib.Nifti1Image(data_array,mat)

	# nifti header info
	nii.header.set_data_dtype(np.int16)
	nii.header.set_zooms([vs[0],vs[1],vs[2]])

	# make out dir
	outdir='niftis'

	if not os.path.exists(outdir):
	    os.makedirs(outdir)

	# Save nifti
	niiname = '%s/%s_%02ddown_%schan.nii.gz' % (outdir,outnii,dr,chan)
	nib.save(nii,niiname)

	print ("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - startTime)) 

# ---------

def main():
      	      
	scriptlog('convertTif2Nii.log')

	converttiff2nii()		
 
if __name__ == "__main__":
    main()