import os
import sys
from shutil import copyfile
from datetime import datetime
from nipype.interfaces.ants import N4BiasFieldCorrection
from nipype.interfaces.fsl import maths, ImageStats, ExtractROI, BET
from nipype.interfaces.c3 import C3d
from nipype.interfaces import niftyreg
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

	Usage: miracl reg mri_allen_niftyreg -i [ input invivo or exvivo MRI nii ] -o [ orient code ] -m [ hemi mirror ] -v [ labels vox ] -l [ input labels ] -b [ olfactory bulb ] -s [ skull strip ] -n [ no orient needed ]

    Example: miracl reg mri_allen_niftyreg -i inv_mri.nii.gz -o RSP -m combined -v 25

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
	
		- NiftyReg
		http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg		

		- FSL

		- c3d
		https://sourceforge.net/projects/c3d

	-----------------------------------
	
	(c) Maged Goubran @ Stanford University, 2018
	mgoubran@stanford.edu
	
	-----------------------------------

	registration based on NiftyReg 	

	-----------------------------------'''


def parse_function():
	parser = argparse.ArgumentParser(description="", usage=helpmsg())
	
	required = parser.add_argument_group('required arguments')
	required.add_argument('-i', '--img', type=str, help='input MRI nii; Preferably T2-weighted', required=True)

	optional = parser.add_argument_group("optional arguments")
	optional.add_argument('-o', '--orient', type=str, help='orientation code (default: RSP)', default='RSP')
	optional.add_argument('-m', '--mirror', choices=['split', 'combined'], default='combined')
	optional.add_argument('-v', '--voxel_size', type=int, choices=[10, 25, 50], default=10)
	optional.add_argument('-l', '--labels', help='input Allen labels to warp (default: annotation_hemi_combined_10um.nii.gz )' + \
		'\n\tinput labels could be at a different depth than default labels' + \
		'\n\tIf l. is specified (m & v cannot be specified)', default='annotation_hemi_combined_10um.nii.gz')
	optional.add_argument('-b', '--olfactory_bulb', action='store_true', help='olfactory bulb included in brain, binary option (default: 0 -> not included)')
	optional.add_argument('-s', '--skullstrip', action='store_true', help='skull strip or not, binary option (default: 1 -> skull-strip)')
	optional.add_argument('-f', '--fract_intensity', type=float, default=0.3, help='FSL skull striping fractional intensity (default: 0.3), smaller values give larger brain outlines')
	optional.add_argument('-n', '--no_orientation', action='store_true', help='No orientation needed (input image in "standard" orientation), binary option (default: False -> orient)')

	return parser


def parse_inputs(parser, args):
	img = args.img
	orient = args.orient
	hemi = args.mirror
	voxel_size = args.voxel_size
	labels = args.labels
	olfactory_bulb = args.olfactory_bulb
	skullstrip = args.skullstrip
	frac = args.fract_intensity
	no_orientation = args.no_orientation

	return img, orient, hemi, voxel_size, labels, olfactory_bulb, skullstrip, frac, no_orientation


def biasfieldcorr(unbiasmr, biasmr):
	""" Apply the N4 bias field correction algorithm to the input image
	"""
	if not os.path.exists(biasmr):
		print("Bias-correcting %s with N4" % unbiasmr)

		# input image, reduce it by a factor of 2 to lessen computational time
		input_image = sitk.ReadImage(unbiasmr)
		input_image = sitk.Shrink(input_image, [2] * input_image.GetDimension())
		input_image = sitk.Cast(input_image, sitk.sitkFloat32)

		# create N4 filter, apply it to the input image
		corrector = sitk.N4BiasFieldCorrectionImageFilter()
		output = corrector.execute(input_image)

		sitk.WriteImage(output, biasmr)

		# print("Bias-correcting MRI image with N4")
		# n4 = N4BiasFieldCorrection()
		# n4.inputs.dimension = 3
		# n4.inputs.input_image = unbiasmr
		# n4.inputs.shrink_factor = 2
		# n4.inputs.output_image = biasmr
		# print(n4.cmdline)
		# n4.run()


def thresh(biasmr, thr, thrmr):
	if not os.path.exists(thrmr):
		print("Thresholding MRI image")
		thresh = maths.Threshold()
		thresh.inputs.in_file(biasmr)
		thresh.inputs.thresh(thr)
		thresh.inputs.direction('below')
		thresh.inputs.out_file(thrmr)
		thresh.run()


def croptosmall(thrmr, cropmr):
	if not os.path.exists(cropmr):
		stats = ImageStats(in_file=thrmr, op_string=' -w')
		dims = stats.run()

		print("Cropping MRI image to smallest ROI")
		fslroi = ExtractROI(in_file=thrmr, roi_file=cropmr)
		fslroi.cmdline = '{} {}'.format(fslroi.cmdline, dims)
		fslroi.run()


def mulheader(unhdmr, mulfac, hdmr):
	image = sitk.ReadImage(unhdmr)
	spacing = image.GetSpacing()

	if not os.path.exists(hdmr):
		result_image = sitk.Image()

		result_image.CopyInformation(image)
		result_spacing = [dim * mulfac for dim in spacing]
		result_image.SetSpacing(result_spacing)

		sitk.WriteImage(result_image, hdmr)


def skullstrip(skullmr, betmr, frac):
	if not os.path.exists(betmr):
		print("Skull stripping MRI image")

		stats = ImageStats(in_file = skullmr, op_string=' -C')
		centerofmass = stats.run()

		bet = BET()
		bet.inputs.in_file = skullmr
		bet.inputs.out_file = betmr
		bet.inputs.center = centerofmass
		bet.inputs.frac = frac
		bet.inputs.robust = True
		bet.run()


def register_aladin(allen_ref, mrimage, aladin_out, aladin_xfm):
	if not os.path.exists():
		aladin = niftyreg.RegAladin()
		aladin.inputs.ref_file = allen_ref
		aladin.inputs.flo_file = mrimage
		aladin.inputs.res_file = aladin_out
		aladin.inputs.aff_file = aladin_xfm
		aladin.inputs.maxit_val = 10
		aladin.inputs.ln_val = 4
		aladin.run()


def orientimg(unortmr, orttag, ortint, orttype, ortmr):
	if not os.path.exists(ortmr):
		print("Orienting MRI to standard orientation")
		c3 = C3d()
		c3.inputs.in_file = unortmr
		c3.inputs.out_file = ortmr
		c3.inputs.orientation = orttag
		c3.inputs.interp =  ortint
		c3.inputs.pix_type = orttype
		c3.run()


def smoothimg(ortmr, sigma, smmr):
	if not os.path.exists(smmr):
		print("Smoothing MRI image")
		process = subprocess.Popen(['SmoothImage', '3', ortmr, sigma, \
			smmr, '0', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def reg_transform(reg_image, string):
	transform = niftyreg.RegTransform()


def reg_resample(ref_file, float_file, resampled_image):
	resample = niftyreg.RegResample()
	resample.inputs.ref_file = ref_file
	resample.inputs.flo_file = float_file
	resample.inputs.inter_val = 0
	resample.inputs.type = 'res'
	resample.inputs.out_file = resampled_image
	print(resample.cmdline)
	resample.run()


def main(args):
	starttime = datetime.now()

	parser = parse_function()
	img, orientation, hemi, voxel_size, labels, olfactory_bulb, skullstrip, frac, no_orientation = parse_inputs(parser, args)

	curr_dir = os.getcwd()
	regdir_final = os.path.join(curr_dir, 'reg_final')
	regdir = os.path.join(curr_dir, 'mr_allen_reg')

	# step 1: process MRI
	# N4 bias correct, threshold, and reorient the image
	bias_mr = os.path.join(regdir, "mr_bias.nii.gz")
	biasfieldcorr(img, bias_mr)

	# apply threshold
	threshold_mr = os.path.join(regdir, "mr_bias_thr.nii.gz")
	thresh(bias_mr, 40, threshold_mr)

	# reorient if needed
	orient_mr = os.path.join(regdir, "mr_bias_thr_ort.nii.gz")
	if no_orientation:
		orient_mr = threshold_mr
	else:
		orientimg(threshold_mr, orientation, 'Cubic', 'short', orient_mr)

	# crop to smallest roi
	mr_roi = os.path.join(regdir, "mr_bias_thr_roi.nii.gz")
	croptosmall(orient_mr, mr_roi)

	if skullstrip:
		# multiply the header dims by 10, skullstrip, and revert header
		header_mr = os.path.join(regdir, "mr_bias_thr_ort_hd.nii.gz")
		mulheader(mr_roi, 10, header_mr)

		bet_mr = os.path.join(regdir, "mr_bias_thr_ort_bet.nii.gz")
		skullstrip(header_mr, bet_mr, frac)

		orghdmr = os.path.join(regdir, "mr_bias_thr_ort_bet_orghd.nii.gz")
		mulheader(bet_mr, "0.1", orghdmr)
	else:
		orghdmr = mr_roi
	
	mr_copy = os.path.join(regdir, "mr.nii.gz")
	if not os.path.exists(mr_copy):
		copyfile(orghdmr, mr_copy)

	# step 2: initiate and register to Allen atlas
	if olfactory_bulb:
		allen_ref = os.path.join('', "ara/template/average_template_50um.nii.gz")
	else:
		allen_ref = os.path.join('', 'ara/template/average_template_50um_OBmasked.nii.gz')
	
	aladin_xfm=os.path.join(regdir, "mr_allen_affine.xfm")
	aladin_out=os.path.join(regdir, "mr_allen_aladin.nii.gz")

	if not os.path.exists(aladin_xfm):
		print("Registering MRI data to allen atlas using affine reg")
		register_aladin(allen_ref, mr_copy, aladin_out, aladin_xfm)

	cpp = os.path.join(regdir, "mr_allen_cpp.nii.gz")

	# step 3: warp allen labels to mri
	base = os.path.basename(labels)
	labelname = base.split('.')[0]

	warplabels = os.path.join(regdir_final, "%s_f3d.nii.gz" % (labelname))
	inverted_aff = os.path.join(regdir, "mr_allen_affine_inv.xfm")


	print('\n Registration and Allen label warping done in %s', (datetime.now() - starttime))
	pass


def miracl_reg_mri():
	curr_dir = os.getcwd()
	regdir_final = os.path.join(curr_dir, 'reg_final')
	regdir = os.path.join(curr_dir, 'mr_allen_reg')

	if not os.path.isdir(regdir):
		print('Creating registration folder')
		os.makedirs(regdir)
		os.makedirs(regdir_final)
