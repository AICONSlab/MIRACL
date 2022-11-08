#!/usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@sri.utoronto.ca

# coding: utf-8

import os
import sys
import argparse
import nibabel as nib
import statsmodels.stats.multitest as smm
from scipy import ndimage
import scipy.stats as stats
import multiprocessing
import fnmatch
from joblib import Parallel, delayed
import numpy as np
from datetime import datetime
import subprocess
import itertools
from miracl.utilfn import miracl_utilfn_endstatement as end_statement
import warnings

warnings.simplefilter("ignore", UserWarning)


def helpmsg():
    return '''miracl stats voxel_wise -w [wild-type dir] -d [disease dir] -t [type] -o [output dir]

    Runs voxel-wise stats on segmented, voxelized and registered/warped CLARITY data to the Allen atlas space
    (after running: miracl flow seg & miracl reg warp_clar)
    
    example: miracl stats voxel_wise -w wild_dir -d hunger_dir -t virus -o hunger_exp 

        arguments (required):

        w. wild type dir
        d. disease dir
        t. segmentation type
        o. output dir
        
        optional arguments:

        s. Gaussian resampling sigma (in voxels)
        n. number of permutations

    '''


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg(), add_help=False)
    parser.add_argument('-w', '--wild_dir', type=str, help="wild dir", required=True)
    parser.add_argument('-d', '--disease_dir', type=str, help="disease dir", required=True)
    parser.add_argument('-t', '--seg_type', type=str, help="segmentation type", required=True)
    parser.add_argument('-o', '--out_dir', type=str, help="output_dir", required=True)
    parser.add_argument('-s', '--sigma', type=int, help="resample sigma", default=2)
    parser.add_argument('-p', '--param', type=str, help="stats test: ttest (parametric) or mannw (non-parametric)",
                        default='ttest')
    # parser.add_argument('-n', '--num_perm', type=int, help="number of permutations", default=1000)

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    wild_dir = args.wild_dir
    disease_dir = args.disease_dir
    seg_type = args.seg_type
    out_dir = args.out_dir
    sigma = args.sigma
    param = args.param
    # num_perm = args.num_perm

    return wild_dir, disease_dir, seg_type, out_dir, sigma, param


def smooth_vox(v, vox, seg_type, out_dir, sigma, nv, group):
    smoothed_vox = os.path.join(out_dir, '%02d_%s_vox_%s_smooth_%svx.nii.gz' % (v, group, seg_type, sigma))

    subprocess.check_call('c3d %s -median 1x1x1vox -clip 0 inf -o %s' % (vox, smoothed_vox),
                          shell=True,
                          stderr=subprocess.STDOUT)

    subprocess.check_call('ResampleImage 3 %s %s %s 0 2' % (smoothed_vox, smoothed_vox, nv),
                          shell=True,
                          stderr=subprocess.STDOUT)


def main(args):
    start_time = datetime.now()
    cpu_load = 0.9
    cpus = multiprocessing.cpu_count()
    n_cpus = int(cpu_load * cpus)  # 95% of cores used2

    parser = parsefn()
    wild_dir, disease_dir, seg_type, out_dir, sigma, param = parse_inputs(parser, args)

    # create out dir
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # find wild type voxelized segs (not bin)
    wild_name = wild_dir
    wild_dir = os.path.realpath(wild_dir)
    wild_files = []
    for root, dirnames, filenames in os.walk(wild_dir):
        for filename in fnmatch.filter(filenames, '*voxelized_seg_%s_*_allen_space.nii.gz' % seg_type):
            wild_files.append(os.path.join(root, filename))

    w = len(wild_files)
    print('Found %02d wild-type voxelized segmentation files' % w)

    print('Generating mean wild-type voxelized image')
    mean_wild = os.path.join(out_dir, 'mean_%s_vox.nii.gz' % wild_name)
    in_wilds = os.path.join(wild_dir, '*voxelized_seg_%s_*_allen_space.nii.gz' % seg_type)
    if not os.path.exists(mean_wild):
        subprocess.check_call("c3d %s -mean -o %s" % (in_wilds, mean_wild), shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    # find disease
    disease_name = disease_dir
    disease_dir = os.path.realpath(disease_dir)
    disease_files = []
    for root, dirnames, filenames in os.walk(disease_dir):
        for filename in fnmatch.filter(filenames, '*voxelized_seg_%s_*_allen_space.nii.gz' % seg_type):
            disease_files.append(os.path.join(root, filename))
    # disease_files = glob.glob(os.path.join(disease_dir, '**', 'voxelized_seg_%snii.gz' % seg_type))
    h = len(disease_files)
    print('Found %02d disease voxelized segmentations' % h)

    print('Generating mean disease-type voxelized image')
    mean_dis = os.path.join(out_dir, 'mean_%s_vox.nii.gz' % disease_name)
    in_dis = os.path.join(disease_dir, '*voxelized_seg_%s_*_allen_space.nii.gz' % seg_type)
    if not os.path.exists(mean_dis):
        subprocess.check_call("c3d %s -mean -o %s" % (in_dis, mean_dis), shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    print('Generating difference image')
    diff_img = os.path.join(out_dir, 'diff_group_means_vox.nii.gz')
    if not os.path.exists(diff_img):
        subprocess.check_call("c3d %s %s -scale -1 -add -o %s" % (mean_wild, mean_dis, diff_img), shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    # get brain mask
    print('Extracting resolution and generating brain mask')
    voxel = int(nib.load(wild_files[0]).header.get_zooms()[0] * 1000)
    miracl_home = os.environ['MIRACL_HOME']
    mask_file = os.path.join(miracl_home, 'atlases', 'ara', 'template',
                             'average_template_%sum_brainmask.nii.gz' % voxel)
    # brain_mask.main(['-i', wild_files[0], '-o', '%s' % mask])

    # smooth wild type and disease files
    nv = (sigma * voxel) / 1000.0
    # all_files = wild_files + disease_files
    four_dim_wild = os.path.join(out_dir, '4D_%s_vox_stack_smooth_%svx.nii.gz' % (wild_name, sigma))
    four_dim_dis = os.path.join(out_dir, '4D_%s_vox_stack_smooth_%svx.nii.gz' % (disease_name, sigma))

    print('Median filtering & Gaussian resampling voxelized segmentations')
    if not os.path.exists(four_dim_wild):
        Parallel(n_jobs=n_cpus, backend='threading')(
            delayed(smooth_vox)(v, vox, seg_type, out_dir, sigma, nv, wild_name) for v, vox in enumerate(wild_files))

    if not os.path.exists(four_dim_dis):
        Parallel(n_jobs=n_cpus, backend='threading')(
            delayed(smooth_vox)(v, vox, seg_type, out_dir, sigma, nv, disease_name) for v, vox in enumerate(disease_files))

    # stack
    print('Stacking all wild segmentation files')
    in_wilds = os.path.join(out_dir, '*%s*smooth*%s*.nii.gz' % (wild_name, sigma))
    if not os.path.exists(four_dim_wild):
        subprocess.check_call("fslmerge -t %s %s" % (four_dim_wild, in_wilds), shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    print('Stacking all disease segmentation files')
    in_dis = os.path.join(out_dir, '*%s*smooth*%s*.nii.gz' % (disease_name, sigma))
    if not os.path.exists(four_dim_dis):
        subprocess.check_call("fslmerge -t %s %s" % (four_dim_dis, in_dis), shell=True,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

    def mann(stack_wild, stack_dis, mask, vl, param, xdim):
        sys.stdout.write("\rprocessing voxel %d %d %d ... " % (vl[0], vl[1], vl[2]))
        # rem = int((xdim - vl[0]/xdim) * 100)
        # sys.stdout.write("\r%d percent remaining..." % rem)
        sys.stdout.flush()

        # mask_res = ndimage.zoom(mask, 1.0/sigma)
        # mask_res[mask_res > 0.5] = 1
        mv = mask[vl[0], vl[1], vl[2]]

        if mv == 1:
            wild_vals = stack_wild[vl[0], vl[1], vl[2], :]
            disease_vals = stack_dis[vl[0], vl[1], vl[2], :]

            try:
                if param == 'ttest':
                    t, p = stats.ttest_ind(wild_vals, disease_vals, equal_var=False)
                else:
                    t, p = stats.mannwhitneyu(wild_vals, disease_vals)
            except ValueError:
                p = 1.0
        else:
            p = 1.0

        return p

    cpuload = 0.9
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)  # 95% of cores used

    print('Reading 4D stack')
    stack_wild_img = nib.load(four_dim_wild)
    stack_wild = stack_wild_img.get_data()
    stack_dis_img = nib.load(four_dim_dis)
    stack_dis = stack_dis_img.get_data()

    xdim = stack_wild_img.shape[0]
    x_dim = range(stack_wild_img.shape[0])
    y_dim = range(stack_wild_img.shape[1])
    z_dim = range(stack_wild_img.shape[2])

    mask_res = os.path.join(out_dir, 'mask_res.nii.gz')
    subprocess.check_call('ResampleImage 3 %s %s %s 0 0' % (mask_file, mask_res, nv),
                          shell=True,
                          stderr=subprocess.STDOUT)
    subprocess.check_call('c3d %s -thresh 0.5 1 1 0 -erode 1 1x1x1vox -o %s' % (mask_res, mask_res),
                          shell=True,
                          stderr=subprocess.STDOUT)

    org_mask = nib.load(mask_file)
    mask_img = nib.load(mask_res)
    mask = mask_img.get_data()

    vox_list = list(itertools.product(x_dim, y_dim, z_dim))

    print('Computing voxel-wise stats')
    res = []
    res = Parallel(n_jobs=ncpus, backend='threading')(delayed(mann)(stack_wild, stack_dis, mask, vl, param, xdim) for vl in vox_list)
    p_array = np.asarray(res, dtype=np.float64)
    p_array[np.isnan(p_array)] = 1.0
    print('Done voxel-wise stats')

    print('FDR correcting')
    p_array[p_array == 0] = 1.0
    rej, corr_pvals = smm.fdrcorrection(p_array, alpha=0.05)
    corr_pvals[np.isnan(corr_pvals)] = 1.0
    # corr_pvals = np.nan_to_num(corr_pvals, nan=1.0)

    print('Saving images')
    p_arr = p_array.reshape((stack_wild_img.shape[0], stack_wild_img.shape[1], stack_wild_img.shape[2]))
    p_arr = 1.0 - p_arr
    # p_arr = -np.log(p_arr)

    corr_p_arr = corr_pvals.reshape((stack_wild_img.shape[0], stack_wild_img.shape[1], stack_wild_img.shape[2]))
    corr_p_arr = 1.0 - corr_p_arr
    # corr_p_arr = -np.log(corr_p_arr)

    # mask_mm2vox = np.linalg.inv(mask_img.affine)
    # mask_to_org_vox = mask_mm2vox.dot(org_mask.affine)
    # mat, vec = nib.affines.to_matvec(mask_to_org_vox)
    # p_arr_res = ndimage.affine_transform(p_arr, mat, vec, output_shape=org_mask.shape, order=1)
    # corr_p_arr_res = ndimage.affine_transform(corr_p_arr, mat, vec, output_shape=org_mask.shape, order=1)

    p_arr_res = os.path.join(out_dir, 'p_vals_%svx_%s.nii.gz' % (sigma, param))
    p_nii = nib.Nifti1Image(p_arr, affine=mask_img.affine)
    nib.save(p_nii, p_arr_res)

    corr_p_arr_res = os.path.join(out_dir, 'corrp_vals_%svx_%s.nii.gz' % (sigma, param))
    corr_p_nii = nib.Nifti1Image(corr_p_arr, affine=mask_img.affine)
    nib.save(corr_p_nii, corr_p_arr_res)

    subprocess.check_call('ResampleImage 3 %s %s %sx%sx%s 1 0' % (p_arr_res, p_arr_res, org_mask.shape[0],
                                                                  org_mask.shape[1], org_mask.shape[2]),
                          shell=True,
                          stderr=subprocess.STDOUT)

    subprocess.check_call('ResampleImage 3 %s %s %sx%sx%s 1 0' % (corr_p_arr_res, corr_p_arr_res, org_mask.shape[0],
                                                                  org_mask.shape[1], org_mask.shape[2]),
                          shell=True,
                          stderr=subprocess.STDOUT)

    ####
    # fsl randomize
    # # generate design matrix
    # print('Generating design matrix and contrasts')
    # n = 2
    # l = w + h
    #
    # dmat = np.zeros((l, n))
    # # dmat[:, 0] = 1
    # dmat[0:w, 0] = 1
    # dmat[w:, 1] = 1
    #
    # design_mat = os.path.join(out_dir, 'design.mat')
    # np.savetxt(design_mat, dmat, delimiter=' ', fmt='%1d')
    #
    # # generate contrast
    # cont = np.array(([1, -1], [-1, 1]))
    # design_con = os.path.join(out_dir, 'design.con')
    # np.savetxt(design_con, cont, delimiter=' ', fmt='%1d')
    #
    # design_vest_mat = os.path.join(out_dir, 'design_vest.mat')
    # subprocess.check_call("Text2Vest %s %s" % (design_mat, design_vest_mat), shell=True,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)
    #
    # design_vest_con = os.path.join(out_dir, 'design_vest.con')
    # subprocess.check_call("Text2Vest %s %s" % (design_con, design_vest_con), shell=True,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)
    #
    # print('Computing voxel-wise stats')
    # subprocess.check_call(
    #     'randomise -i %s -o %s -d %s -t %s -m %s -n %s -T -v %.3f -x --uncorrp' %
    #      (four_dim, out_dir, design_vest_mat, design_vest_con, mask, num_perm, (10*voxel),
    #     shell=True,
    #     stderr=subprocess.STDOUT)

    # visualize results

    print(datetime.now() - start_time)
    # end_statement.main(['-f', 'Voxel-wise statistics', '-t', '%s' % (datetime.now() - start_time)])


if __name__ == "__main__":
    main(sys.argv)
