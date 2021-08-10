import os
import sys
import argparse

import nipype.interfaces.diffusion_toolkit as dtk


def parsefn():
	parser = argparse.ArgumentParser(description='', usage=helpmsg())

	parser.add_argument('-i', '--input_track', type=str, help="Input down-sampled clarity nifti (.nii/.nii.gz)", required=True)
	parser.add_argument('-sl', '--step_length', type=str, help="Unit of minimum voxel size", required=True)
	parser.add_argument('-o', '--output_track', type=str, help="Output directory", default='clarity_sta')
	
	return parser


def parse_inputs(parser, args):
	input_track = args.input_track
	output_track = args.output_track
	step_length = args.step_length
	
	return input_track, output_track, step_length


def spline_filter(input_file, output_file, step_length=0.1):
	''' Executes spline_filter, a TrackVis method that smoothes TrackVIs track files with a B-Spline filter
	'''
	filt = dtk.SplineFilter()
	filt.inputs.track_file = input_file
	filt.inputs.output_file = output_file
	filt.inputs.step_length = step_length
	filt.run()


def main(args):
	parser = parsefn()
	input_file, output_file, step_length = parse_inputs(parser, args)
	
	spline_filter(input_file, output_file, step_length)


if __name__ == "__main__":
	main(sys.argv)