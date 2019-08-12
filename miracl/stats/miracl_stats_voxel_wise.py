#!/usr/bin/env python
# Maged Goubran @ 2019, maged..goubran@sri.utoronto.ca

# coding: utf-8

import argparse
import nibabel as nib
import os
import sys
import multiprocessing
import fnmatch
from joblib import Parallel, delayed
import numpy as np
from datetime import datetime
import subprocess
from miracl.utilfn import miracl_utilfn_endstatement as end_statement

import warnings

warnings.simplefilter("ignore", UserWarning)


def helpmsg():
    return '''miracl stats voxel_wise -w [wild-type dir] -d [disease dir] -t [type] -o [output dir]

    Runs voxel-wise stats on segmented, voxelized and registered/warped CLARITY data to the Allen atlas space
    (after running: miracl flow seg & miracl reg warp_clar)
    
    Uses non-parametric permutation to build a null distribution for inference on statistical maps and 
    threshold-free cluster enhancement 
    
    example: miracl stats voxel_wise -w wild_dir -d hunger_dir -t virus -o hunger_exp 

        arguments (required):

        w. wild type dir
        d. disease dir
        t. segmentation type
        o. output dir
        
        optional arguments:

        s. smoothing sigma (in voxels)
        n. number of permutations

    -----

    Main Outputs


    '''


def parse_fn():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg(), add_help=False)
    parser.add_argument('-w', '--wild_dir', type=str, help="wild dir", required=True)
    parser.add_argument('-d', '--disease_dir', type=str, help="disease dir", required=True)
    parser.add_argument('-t', '--seg_type', type=str, help="segmentation type", required=True)
    parser.add_argument('-o', '--out_dir', type=str, help="output_dir", required=True)
    parser.add_argument('-n', '--num_perm', type=int, help="number of permutations", default=1000)
    parser.add_argument('-s', '--sigma', type=int, help="smoothing sigma", default=2)

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    wild_dir = args.wild_dir
    disease_dir = args.disease_dir
    seg_type = args.seg_type
    out_dir = args.out_dir
    num_perm = args.num_perm
    sigma = args.sigma

    return wild_dir, disease_dir, seg_type, out_dir, num_perm, sigma


def smooth_vox(v, vox, seg_type, out_dir, sigma):
    smoothed_vox = os.path.join(out_dir, '%02d_vox_%s_smooth3vx.nii.gz' % (v, seg_type))

    subprocess.check_call('c3d %s -smooth %01dvox -clip 0 inf -o %s' % (vox, sigma, smoothed_vox),
                          shell=True,
                          stderr=subprocess.STDOUT)


def main(args):
    start_time = datetime.now()
    cpu_load = 0.9
    cpus = multiprocessing.cpu_count()
    n_cpus = int(cpu_load * cpus)  # 95% of cores used2

    parser = parse_fn()
    wild_dir, disease_dir, seg_type, out_dir, num_perm, sigma = parse_inputs(parser, args)

    # create out dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # find wilt type voxelized segs (not bin)
    wild_dir = os.path.realpath(wild_dir)
    wild_files = []
    for root, dirnames, filenames in os.walk(wild_dir):
        for filename in fnmatch.filter(filenames, 'voxelized_seg_%s_*_allen_space.nii.gz' % seg_type):
            wild_files.append(os.path.join(root, filename))

    w = len(wild_files)
    print('Found %02d wild-type voxelized segmentation files' % w)

    # get brain mask
    print('Extracting resolution and generating brain mask')
    voxel = int(nib.load(wild_files[0]).header.get_zooms()[0]*1000)
    miracl_home = os.environ['MIRACL_HOME']
    mask = os.path.join(miracl_home,'atlases','ara','template','average_template_%sum_brainmask.nii.gz' % voxel)
    # brain_mask.main(['-i', wild_files[0], '-o', '%s' % mask])

    # find disease
    disease_dir = os.path.realpath(disease_dir)
    disease_files = []
    for root, dirnames, filenames in os.walk(disease_dir):
        for filename in fnmatch.filter(filenames, 'voxelized_seg_%s_*_allen_space.nii.gz' % seg_type):
            disease_files.append(os.path.join(root, filename))
    # disease_files = glob.glob(os.path.join(disease_dir, '**', 'voxelized_seg_%snii.gz' % seg_type))
    h = len(disease_files)
    print('Found %02d disease voxelized segmentation files' % h)

    # smooth wild type and disease files
    all_files = wild_files + disease_files
    print('Smoothing wild-type and disease voxelized segmentation files')
    Parallel(n_jobs=n_cpus, backend='threading')(
        delayed(smooth_vox)(v, vox, seg_type, out_dir, sigma) for v, vox in enumerate(all_files))

    # stack
    print('Stacking all voxelized segmentation files')
    in_vols = os.path.join(out_dir, '*smooth*.nii.gz')
    four_dim = os.path.join(out_dir, '4D_vox_stack.nii.gz')
    subprocess.check_call("fslmerge -t %s %s" % (four_dim, in_vols), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    # fsl randomize

    # generate design matrix
    print('Generating design matrix and contrasts')
    n = 2
    l = w + h

    dmat = np.zeros((l, n))
    # dmat[:, 0] = 1
    dmat[0:w, 0] = 1
    dmat[w:, 1] = 1

    design_mat = os.path.join(out_dir, 'design.mat')
    np.savetxt(design_mat, dmat, delimiter=' ', fmt='%1d')

    # generate contrast
    cont = np.array(([1, -1], [-1, 1]))
    design_con = os.path.join(out_dir, 'design.con')
    np.savetxt(design_con, cont, delimiter=' ', fmt='%1d')

    design_vest_mat = os.path.join(out_dir, 'design_vest.mat')
    subprocess.check_call("Text2Vest %s %s" % (design_mat, design_vest_mat), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    design_vest_con = os.path.join(out_dir, 'design_vest.con')
    subprocess.check_call("Text2Vest %s %s" % (design_con, design_vest_con), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    print('Computing voxel-wise stats')
    subprocess.check_call(
        'randomise -i %s -o %s -d %s -t %s -m %s -n %s -T -D' % (four_dim, out_dir, design_vest_mat,
                                                              design_vest_con, mask, num_perm),
        shell=True,
        stderr=subprocess.STDOUT)

    # visualize results


    end_statement.main(['-f', 'Voxel-wise statistics', '-t', '%s' % (datetime.now() - start_time)])


if __name__ == "__main__":
    main(sys.argv)
