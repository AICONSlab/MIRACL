#!/usr/bin/env python
# Maged Goubran @ AICONSlab 2022, maged.goubran@utoronto.ca

# coding: utf-8

import argparse
import subprocess
import sys
import os


def helpmsg():
    return '''

    Generate a tract endpoints map from input STA tractography streamlines. Uses mrtrix

    Usage: miracl_sta_gen_tract_endpoints.py -t [ input tracts (.tck) ]  -r [ reference volume ] -o [ output tract density ]

        '''

    # Dependencies:
    #     c3d
    #     mrtrix 2.7


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-t', '--tracts', type=str, help="Input tractography (.tck) file", required=True)
    parser.add_argument('-r', '--ref_vol', type=str, help="Reference nifti volume, generated alongside the tractography file", required=True)
    parser.add_argument('-o', '--output', type=str, help="Output filename; the endpoints will be stored here", default='endpoints.nii.gz')

    return parser


def parse_inputs(parser, args):
    tracts = args.tracts
    ref_vol = args.ref_vol
    output = args.output

    return tracts, ref_vol, output


def gen_endpoints(input_tck, ref_vol, out_endpoints=None):
    ''' Run tckmap to extract endpoints from tck file. File output should be in the same space as the reference file
    '''
    if not out_endpoints:
        out_dir = os.path.dirname(input_tck)
        out_endpoints = os.path.join(out_dir, 'endpoints.nii.gz')

    # generate endpoints
    CMD = "tckmap -ends_only -template {} {} {}".format(ref_vol, input_tck, out_endpoints)
    print(CMD)
    subprocess.check_call(CMD, shell=True, stderr=subprocess.STDOUT)

# ---------

def main(args):
    # parse in args
    parser = parsefn()
    tracts, ref_vol, output = parse_inputs(parser, args)

    # create dens map
    gen_endpoints(tracts, ref_vol, output)


if __name__ == "__main__":
    main(sys.argv)
