# Edward Ntiri, 2021 February

import argparse
import os
import sys
import subprocess

from miracl.conv import miracl_conv_gui_options as gui_opts
from miracl.sta import sta_gui
from miracl.utilfn.misc import get_orient


def helpmsg():
	return '''
	1) Performs Structure Tensor Analysis (STA) on CLARITY viral tracing or stains

	Usage: miracl sta track_tensor

	A GUI will open to choose your input down-sampled clarity nifti, brain mask, seed mask

		----------
	For command-line / scripting

	Usage: miracl sta track_tensor -i <down-sampled clarity nifti> -g <dog sigma> -k <gaussian sigma> -a <tracking angle threshold>
	                     -b <brain mask> -s <seed> -o <output dir>

	Example: miracl sta track_tensor -i clarity_03x_down_virus_chan.nii.gz -g 0.5 -k 0.5 -a 25 -b brain_mask.nii.gz -s seed.nii.gz -o sta

	OR using multiple parameters:

	miracl sta track_tensor -i clarity_03x_down_virus_chan.nii.gz -g 0.5,1.5 -k 0.5,2 -a 25,35 -b brain_mask.nii.gz -s seed.nii.gz -o sta

		required arguments:
			i. Input down-sampled clarity nifti (.nii/.nii.gz)
			g. Derivative of Gaussian (dog) sigma
			k. Gaussian smoothing sigma
			a. Tracking angle threshold
			b. Brain mask (.nii/.nii.gz)
			s. Seed mask (.nii/.nii.gz)

		optional arguments:
			o. Out dir

		----------
	Main Outputs
		fiber.trk => Fiber tracts

		----------
	Dependencies:
		- Matlab
		- Diffusion Toolkit

	-----------------------------------
	(c) Qiyuan Tian @ Stanford University, 2016
	qytian@stanford.edu
	(c) Maged Goubran @ AICONSlab, 2022
	maged.goubran@utoronto.ca
	-----------------------------------
	'''


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    if len(sys.argv) > 3:
    	parser.add_argument('-i', '--input_clar', type=str, help="Input down-sampled clarity nifti (.nii/.nii.gz)", required=True)
    	parser.add_argument('-b', '--brainmask', type=str, help="Brain mask (.nii/.nii.gz)", required=True)
    	parser.add_argument('-s', '--seedmask', type=str, help="Seed mask (.nii/.nii.gz)", required=True)
    	parser.add_argument('-a', '--angles', nargs='*', help="Tracking angle threshold", default=[45, 60])
    	parser.add_argument('-g', '--dogs', nargs='*', help="derivative of gaussian (dog) sigma", default=[3,5])
    	parser.add_argument('-k', '--gausses', nargs='*', help="Gaussian smoothing sigma", default=[3,5])
    	parser.add_argument('-sl', '--step_length', nargs='*', help="Step length, in the unit of minimum voxel size", default=[0.1])
    	parser.add_argument('-rk', '--rk2', action='store_true',
                            help="use 2nd order runge-kutta method for tracking")
    	parser.add_argument('-o', '--outdir', type=str, help="Output directory", default='clarity_sta')

    return parser


def parse_inputs(parser, args):
    if sys.argv[-2] == 'sta' and sys.argv[-1] == 'track_tensor':

        print("Running in GUI mode")

        # pass the results of the gui here
        args = sta_gui.main()

    input_clar = args.input_clar
    brainmask = args.brainmask
    seedmask = args.seedmask
    outdir = args.outdir if args.outdir else 'clarity_sta'
    rk2 = True if args.rk2 else False

    # cast input lists from strs to ints
    try:
        angles = args.angles.split(',') if ',' in args.angles else list(map(int, args.angles))
        dogs = args.dogs.split(',') if ',' in args.dogs else list(map(float, args.dogs))
        gausses = args.gausses.split(',') if ',' in args.gausses else list(map(float, args.gausses))
        step_lengths = args.step_length.split(',') if ',' in args.step_length else list(map(float, args.step_length))
    except Exception as e:
        raise

    return input_clar, brainmask, seedmask, angles, dogs, gausses, step_lengths, rk2, outdir


def track_primary_eigen(input_clar, dog_sigmas, gauss_sigmas, brain_mask, seed_mask, angles, step_lengths, rk2, outdir):
	rk = 1 if rk2 else 0
	orient = get_orient(input_clar)

	for dog_sigma in dog_sigmas:
		for gauss_sigma in gauss_sigmas:
			for angle in angles:
				for step_length in step_lengths:
					print("\n Running Structure Tensor Analysis with the following command \n")

					CMD = '{}/utilfn/runMatlabCmd sta_track "\'{}\'" "{}" "{}" "{}" "\'{}\'" "\'{}\'" "\'{}\'" "{}" "{}" "\'{}\'"'.format(
						os.environ['MIRACL_HOME'], input_clar, dog_sigma, 
						gauss_sigma, angle, brain_mask, seed_mask, outdir, step_length, rk, orient)

					print(CMD)
					subprocess.check_call(CMD, shell=True, stderr=subprocess.STDOUT)


def main(args):
    parser = parsefn()
    filename, bmask, smask, angles, dog_sigmas, gauss_sigmas, step_lengths, rk2, output_dir = parse_inputs(parser, args)

    # run sta tract generation
    print('Running Structure Tensor Analysis\n')
    track_primary_eigen(filename, dog_sigmas, gauss_sigmas, bmask, smask, angles, step_lengths, rk2, output_dir)


if __name__ == "__main__":
    main(sys.argv)
