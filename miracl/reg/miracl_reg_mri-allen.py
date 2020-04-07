import os
import sys
from shutil import datetime
from datetime import datetime
import nibabel
import subprocess
import SimpleITK as sitk
import argparse


def get_version():
    pass


def helpmsg():
    return '''
    1) Registers in-vivo or ex-vivo MRI data to Allen Reference mouse brain Atlas
	2) Warps Allen annotations to the MRI space

	if no inputs are given function will run in GUI mode

	For command-line / scripting

	Usage: `basename $0` -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ]

    Example: `basename $0` -i inv_mri.nii.gz -o RSP -m combined -v 25

    arguments (required):

		i.  input MRI nii
            Preferably T2-weighted

    optional arguments:

        o.  orient code (default: RSP)
            to orient nifti from original orientation to "standard/Allen" orientation

        m.  hemisphere mirror (default: combined)
            warp allen labels with hemisphere split (Left different than Right labels) or combined (L & R same labels / Mirrored)
			accepted inputs are: <split> or <combined>

        v.  labels voxel size/Resolution in um (default: 10)
			accepted inputs are: 10, 25 or 50

        l.  input Allen labels to warp (default: annotation_hemi_combined_10um.nii.gz )
			input labels could be at a different depth than default labels

			If l. is specified (m & v cannot be specified)

        b.  olfactory bulb included in brain, binary option (default: 0 -> not included)

        s.  skull strip or not, binary option (default: 1 -> skull-strip)

        f.  FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines

        n.  No orientation needed (input image in "standard" orientation), binary option (default: 0 -> orient)

	----------		

	Dependencies:
	
		- ANTs
		https://github.com/stnava/ANTs			

		- FSL

		- c3d
		https://sourceforge.net/projects/c3d

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2018
	mgoubran@stanford.edu
	
	-----------------------------------

	registration based on ANTs	

	-----------------------------------
    '''


def parsefn():
    parser = argparse.ArgumentParser(description=''. usage = helpmsg())
    parser.add_argument('-i', '--input', type=str, help='input MRI nii (preferably T2 weighted)', required=True)
    parser.add_argument('-o', '--orient', type=str, help='to orient nifti from original orienation to "standard/Allen" orientation', default='RSP')
    parser.add_argument('-m', '--mirror', choices=['split', 'combined'], help='hemisphere mirror (default: combined)', default='combined')
    parser.add_argument('-v', '--voxel_size', type=int, choices=[10, 25, 50], help='voxel size of the label; accepted inputs are: 10, 25, 50', default=10)
    parser.add_argument('-l', '--input_labels', type=str, default='annotation_hemi_combined_10um.nii.gz', help='Allen labels to warp; NOTE: if option is specified, m and v cannot be specified')
    parser.add_argument('-b', '--olfactory_bulb', action='store_true', help='flag indicating that olfactory bulb is included in brain')
    parser.add_argument('-s', '--skull_strip', action='store_true', help='flag to skull strip the image')
    parser.add_argument('-f', '--fsl_skstrip_intensity', type=float, default=0.3, help='FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines')
    parser.add_argument('-n', '--no_orientation', type=str, help='No orientation needed (input image in "standard" orientation)')

    return parser

def parse_inputs(parser, args):
    img = args.input
    orient = args.orient
    voxel_size = args.voxel_size
    input_labels = args.input_labels
    mirror = args.mirror
    no_orientation = args.no_orientation
    if input_labels:
        mirror = None
        no_orientation = None
    skullstrip = args.skull_strip
    fsl_intensity = args.fsl_skstrip_intensity
    no_orientation = args.no_orientation 
    olfactory = args.olfactory_bulb

    return img, orient, voxel_size, input_labels, mirror, no_orientation, input_labels, skullstrip, fsl_intensity, no_orientation, olfactory

