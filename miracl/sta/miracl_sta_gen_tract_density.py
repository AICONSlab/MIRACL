#!/usr/bin/env python
# Maged Goubran @ Stanford 2018, mgoubran@stanford.edu

# coding: utf-8

import argparse
import sys
import nibabel as nib
from dipy.tracking import utils
from nibabel import trackvis


def helpmsg():
    return '''

    Generate a tract density map from input STA tractography streamlines

    Usage: miracl_sta_gen_tract_density.py -t [ input tracts (.trk) ]  -r [ reference volume ] -o [ output tract density ]

    Example: miracl_sta_gen_tract_density.py -t  -r  -o

    Arguments (required):

        -t Input tracts (.trk)

        -r Reference nifti volume

    Optional arguments:

        -o Output tract density

        '''

    # Dependencies:
    #     dipy
    #     Python 2.7


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-t', '--tracts', type=str, help="Input tracts ", required=True)
    parser.add_argument('-r', '--ref_vol', type=str, help="Reference nifti volume", required=True)
    parser.add_argument('-o', '--out_dens', type=str, help="Output tract density")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    # check if pars given

    assert isinstance(args.tracts, str)
    tracts = args.tracts

    assert isinstance(args.ref_vol, str)
    ref_vol = args.ref_vol

    if not args.out_dens:
        out_dens = 'sta_streamlines_density_map.nii.gz'
    else:
        assert isinstance(args.out_dens, str)
        out_dens = args.out_dens

    return tracts, ref_vol, out_dens


# ---------

def gen_dens(tracts, ref_vol, out_dens):
    print('reading sta streamlines')
    streams, hdr = trackvis.read(tracts)
    streamlines = [s[0] for s in streams]

    print('reading reference volume')
    niihdr = nib.load(ref_vol)
    nii = niihdr.get_data()

    print('generating density map from tracts')
    dm = utils.density_map(streamlines, nii.shape, affine=niihdr.affine)
    dm_img = nib.Nifti1Image(dm.astype("int16"), niihdr.affine)

    print('saving tracts map')
    dm_img.to_filename(out_dens)


# ---------

def main(args):
    # parse in args
    parser = parsefn()
    tracts, ref_vol, out_dens = parse_inputs(parser, args)

    # create dens map
    gen_dens(tracts, ref_vol, out_dens)


if __name__ == "__main__":
    main(sys.argv)
