#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import subprocess
import sys


# import commands

def helpmsg():
    return '''

    Creates brain mask (nii/nii.gz) for CLARITY data

    Usage: miracl_create_brainmask.py -i [input volume] -o [output brain mask]

Example: miracl_create_brainmask.py -i clarity_downsample_05x_virus_chan.nii.gz -o clarity_brain_mask.nii.gz

    Arguments (required):

        -i Input volume

    Optional arguments:

        -o Output brain mask

        '''

    # Dependencies:

    #     c3d
    #     Python 2.7


def parseinputs():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-i', '--invol', type=str, help="In volume", required=True)
    parser.add_argument('-o', '--outfile', type=str, help="Output file")

    args = parser.parse_args()

    # check if pars given

    assert isinstance(args.invol, str)
    invol = args.invol

    if not os.path.exists(invol):
        sys.exit('%s does not exist ... please check path and rerun script' % invol)

    if not args.outfile:
        outfile = 'clarity_brain_mask.nii.gz'
    else:
        assert isinstance(args.outfile, str)
        outfile = args.outfile

    return invol, outfile


# ---------

def main():
    # parse in args
    [invol, outfile] = parseinputs()

    # create mask
    print("\n Creating brain mask for CLARITY volume ...\n")

    thr = '60%'

    subprocess.check_call("c3d %s -thresh %s inf 1 0 -o %s" % (invol, thr, outfile), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)


if __name__ == "__main__":
    main()
