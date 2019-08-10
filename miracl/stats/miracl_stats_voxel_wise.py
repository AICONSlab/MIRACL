#!/usr/bin/env python
# Maged Goubran @ 2019, maged..goubran@sri.utoronto.ca

# coding: utf-8

import argparse
import glob
import os
import sys
import multiprocessing
from joblib import Parallel, delayed
import numpy as np
from datetime import datetime
import subprocess
from miracl.utilfn import miracl_utilfn_create_brainmask as brain_mask
from miracl.utilfn import miracl_utilfn_endstatement as end_statement

import warnings

warnings.simplefilter("ignore", UserWarning)


def helpmsg():
    return '''Usage: miracl stats voxel_wise -w [wild-type dir] -d [disease dir] -t [type] -o [output dir]

    Runs voxel-wise stats on voxelized, segmented CLARITY data

    example: miracl stats voxel_wise -w wild_dir -d hunger_dir -t virus -o 

        arguments (required):

        w. wild type dir
        d. disease dir
        t. segmentation type
        o. output dir
        
        optional arguments:

        n. number of permutations

    -----

    Main Outputs


    '''


def parse_fn():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg(), add_help=False)
    parser.add_argument('-w', '--wild', type=str, help="wild dir", required=True)
    parser.add_argument('-d', '--disease', type=str, help="disease dir", required=True)
    parser.add_argument('-t', '--type', type=str, help="segmentation type", required=True)
    parser.add_argument('-o', '--out_dir', type=str, help="output_dir", required=True)

    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    wild = args.wild
    disease = args.wild
    seg_type = args.wild
    out_dir = args.out_dir

    return wild, disease, seg_type, out_dir


def smooth_vox(v, vox, seg_type, out_dir):
    smoothed_vox = os.path.join(out_dir, '%02d_vox_%s_smooth3vx.nii.gz' % (v, seg_type))

    subprocess.check_call('c3d %s -smooth 3vox %s' % (vox, smoothed_vox),
                          shell=True,
                          stderr=subprocess.STDOUT)


def main(args):
    start_time = datetime.now()
    cpu_load = 0.9
    cpus = multiprocessing.cpu_count()
    n_cpus = int(cpu_load * cpus)  # 95% of cores used2

    parser = parse_fn()
    wild, disease, seg_type, out_dir = parse_inputs(parser, args)

    # create out dir
    os.makedirs(out_dir)

    # find wilt type voxelized segs (not bin)
    wild_files = glob.glob(os.path.join(wild, 'voxelized_seg_%s.nii.gz' % seg_type))

    # create brain mask
    mask = os.path.join(out_dir, 'brain_mask.nii.gz')
    brain_mask.main(['-i', wild_files[0], '-o', '%s' % mask])

    # find disease
    disease_files = glob.glob(os.path.join(wild, 'voxelized_seg_%s.nii.gz' % seg_type))

    # smooth wild types
    Parallel(n_jobs=n_cpus, backend='threading')(
        delayed(smooth_vox)(wv, wild_vox, seg_type, out_dir) for wv, wild_vox in enumerate(wild_files))

    # smooth disease
    Parallel(n_jobs=n_cpus, backend='threading')(
        delayed(smooth_vox)(dv, dis_vox, seg_type, out_dir) for dv, dis_vox in enumerate(disease_files))

    # stack
    four_dim = os.path.join(out_dir, '4D_vox_stack.nii.gz')

    # fsl randomize

    # generate design matrix
    n = 3
    w = len(wild_files)
    h = len(disease_files)
    l = w + h

    dmat = np.zeros((l, n))
    dmat[:, 0] = 1
    dmat[0:w, 1] = 1
    dmat[w:, 2] = 1

    design_mat = os.path.join(out_dir, 'design.mat')
    np.savetxt(design_mat, dmat, delimiter=' ')

    # generate contrast
    cont = np.array(([1, -1], [-1, 1]))
    design_con = os.path.join(out_dir, 'design.con')
    np.savetxt(design_con, cont, delimiter=' ')

    subprocess.check_call(
        'randomize -i %s -o clarity -d %s -t %s -m %s -n 500 -D -T' % (four_dim, design_mat, design_con, mask),
        shell=True,
        stderr=subprocess.STDOUT)

    # visualize results


    end_statement.main(['-f', 'Voxel-wise statistics', '-t', '%s' % (datetime.now() - start_time)])


if __name__ == "__main__":
    main(sys.argv)
