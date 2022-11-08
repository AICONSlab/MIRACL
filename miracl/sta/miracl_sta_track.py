# Edward Ntiri, 2021 Jan

# 3D structure tensor
# Code adapted from Qiyan Tian, McNab Lab, 2015 Dec

# import libraries
import argparse
import nibabel as nib
import numpy as np
import os
import sys

from scipy import signal
import scipy.ndimage
from skimage import io
import subprocess

from miracl.utilfn.misc import get_orient


def helpmsg():
    return '''1) Performs Structure Tensor Analysis (STA) on CLARITY viral tracing or stains

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
        - Diffusion Toolkit

    -----------------------------------
    (c) Qiyuan Tian @ AICONSlab, 2022
    qytian@stanford.edu
    (c) Maged Goubran @ AICONSlab, 2022
    maged.goubran@utoronto.ca
    -----------------------------------
    '''

def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-i', '--input_clar', type=str, help="Input down-sampled clarity nifti (.nii/.nii.gz)", required=True)
    parser.add_argument('-b', '--brainmask', type=str, help="Brain mask (.nii/.nii.gz)", required=True)
    parser.add_argument('-s', '--seedmask', type=str, help="Seed mask (.nii/.nii.gz)", required=True)
    parser.add_argument('-a', '--angles', nargs='*', help="Tracking angle threshold", default=[45, 60])
    parser.add_argument('-g', '--dogs', nargs='*', help="derivative of gaussian (dog) sigma", default=[3,5])
    parser.add_argument('-k', '--gausses', nargs='*', help="Gaussian smoothing sigma", default=[3,5])
    parser.add_argument('-sl', '--step_length', nargs='*', help="Step length, in the unit of minimum voxel size", default=[0.1])
    parser.add_argument('-o', '--outdir', type=str, help="Output directory", default='clarityy_sta')

    return parser

def parse_inputs(parser, args):
    input_clar = args.input_clar
    brainmask = args.brainmask
    seedmask = args.seedmask
    outdir = args.outdir

    # cast input lists from strs to ints
    try:
        angles = ','.split(args.angles) if ',' in args.angles else list(map(int, args.angles))
        dogs = ','.split(args.dogs) if ',' in args.dogs else list(map(float, args.dogs))
        gausses = ','.split(args.gausses) if ',' in args.gausses else list(map(float, args.gausses))
        step_lengths = args.step_length.split(',') if ',' in args.step_length else list(map(float, args.step_length))
    except Exception as e:
        raise

    return input_clar, brainmask, seedmask, angles, dogs, gausses, outdir, step_lengths


# ---------------------------------
# functions  - main
# ---------------------------------

def doggen(sigma=None, X=None, Y=None, Z=None):
    """Function to generate derivative of Gaussian kernels, in 1D, 2D and 3D.
    
    (c) Qiyuan Tian, McNab Lab, AICONSlab, September 2015

    Args:
        sigma ():
        X:
        Y:
        Z:

    Return:
        Derivative of Gaussian kernel
    """
    halfsize = np.ceil(3 * np.max(sigma))
    x = np.arange(-halfsize,halfsize+1)
    dim = len(sigma)

    if dim == 1:
        if X is None:
            X = x
        k = (-1)*X * np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) )
    if dim == 2:
        if X is None or Y is None:
            [X,Y] =np.meshgrid(x,x)
        k = (-1)*X * np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) ) * np.exp( (-1)*np.power(Y,2)/(2 * np.power(sigma[1],2)) )
    if dim == 3:
        if X is None or Y is None or Z is None:
            [X,Y,Z] =np.meshgrid(x,x,x)
        k = (-1)*X * np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) ) * np.exp( (-1)*np.power(Y,2)/(2 * np.power(sigma[1],2)) ) * np.exp( (-1)*np.power(Z,2)/(2 * np.power(sigma[2],2)))
    if dim > 3:
        print ('Only support up to dimension 3')
    
    return k /np.sum(np.abs(k))

def gaussgen(sigma):
    """ Function to generate Gaussian kernels, in 1D, 2D and 3D.
    
    (c) Qiyuan Tian, McNab Lab, AICONSlab, September 2015

    Args:
        sigma:

    Returns:
        Gaussian kernel
    """
    halfsize = np.ceil(3 * np.max(sigma))
    x = np.arange(-halfsize,halfsize+1)

    if len(sigma) == 1:
        k = np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) )
    if len(sigma) == 2:
        [X,Y] =np.meshgrid(x,x)
        k = np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) ) * np.exp( (-1)*np.power(Y,2)/(2 * np.power(sigma[1],2)) )
    if len(sigma) == 3:
        [X,Y,Z] =np.meshgrid(x,x,x)
        k = np.exp( (-1)*np.power(X,2)/(2 * np.power(sigma[0],2)) ) * np.exp( (-1)*np.power(Y,2)/(2 * np.power(sigma[1],2)) ) * np.exp( (-1)*np.power(Z,2)/(2 * np.power(sigma[2],2)))
    if len(sigma) > 3:
        print('Only support up to dimension 3')

    return k /np.sum(np.abs(k))


def gradCompute(img, dogsigma, mode='same'):
    """ Given an image as well as a dog sigma, return the gradient poduct, as well as the gradient amplitude

    """

    # derivative of gaussian kernel
    dogkercc = doggen([dogsigma, dogsigma, dogsigma])  # column
    dogkerrr = np.transpose( dogkercc, (1, 0, 2) )  # row
    dogkerzz = np.transpose( dogkercc, (0, 2, 1) )  # z-axis

    gcc = signal.convolve(img, dogkercc, mode).astype(np.float32)
    grr = signal.convolve(img, dogkerrr, mode).astype(np.float32)
    gzz = signal.convolve(img, dogkerzz, mode).astype(np.float32)

    # Gradient products
    gp = type('', (), {})()
    gp.gprrrr = grr * grr
    gp.gprrcc = grr * gcc
    gp.gprrzz = grr * gzz
    gp.gpcccc = gcc * gcc
    gp.gpcczz = gcc * gzz
    gp.gpzzzz = gzz * gzz

    # Gradient amplitude
    ga = np.sqrt(gp.gprrrr + gp.gpcccc + gp.gpzzzz).astype(np.float32)

    # Gradient vector
    gv = np.stack((grr, gcc, gzz), axis=3).astype(np.float32)
    # source for next line: https://stackoverflow.com/q/32238227
    gv = gv / np.tile(ga[..., None], [1, 1, 1, 3])  # add singleton-dim to properly tile

    return ga, gv, gp


def gradBlur(gp, gaussker, mode='same'):
    """ Blur the gradient product using the gaussian kernel
    """
    gpgauss = type('', (), {})()
    gpgauss.gprrrrgauss = signal.convolve(gp.gprrrr, gaussker, mode)
    gpgauss.gprrccgauss = signal.convolve(gp.gprrcc, gaussker, mode)
    gpgauss.gprrzzgauss = signal.convolve(gp.gprrzz, gaussker, mode)
    gpgauss.gpccccgauss = signal.convolve(gp.gpcccc, gaussker, mode)
    gpgauss.gpcczzgauss = signal.convolve(gp.gpcczz, gaussker, mode)
    gpgauss.gpzzzzgauss = signal.convolve(gp.gpzzzz, gaussker, mode)

    return gpgauss


def cropVol(volume, size):
    """ Crop the edges of the input volume by variable size, based on shape
    """
    vol = np.copy(volume)
    end = vol.shape
    dims = len(end)

    if dims == 3:
        vol[:size, :, :] = 0
        vol[end[0]-size:, :, :] = 0

        vol[:, :size, :] = 0
        vol[:, end[1]-size:, :] = 0

        vol[:, :, :size] = 0
        vol[:, :, end[2]-size:] = 0
    elif dims == 4:
        vol[:size, :, :, :] = 0
        vol[end[0]-size:, :, :, :] = 0

        vol[:, :size, :, :] = 0
        vol[:, end[1]-size:, :, :] = 0

        vol[:, :, :size, :] = 0
        vol[:, :, end[2]-size:, :] = 0
    else:
        raise ValueError('Variable had {} dimensions, expected either 3 or 4.')

    return vol


def generateAffine(vox_size=[1,1,1]):
    ''' Generate affine for NIFTI image
    '''
    affine = np.eye(4)
    affine[0,0] = vox_size[0]
    affine[1,1] = vox_size[1]
    affine[2,2] = vox_size[2]

    return affine


# ---------------------------------
# read and compute structure tensor
# ---------------------------------
def sta_track(stack, dog_sigmas, gauss_sigmas, fpBmask, fp_smask, angles, dpResult, step_lengths):
    # read image
    img = nib.load(stack)
    img_data = img.get_data()
    img_affine = img.affine

    # get voxel order from image
    vox_order = get_orient(stack)

    # for each dog_sigmas
    for dog_sigma in dog_sigmas:

        # compute gradient amplitude, vector, product
        [ga, gv, gp] = gradCompute(img_data, dog_sigma)
        dogkercc = doggen([dog_sigma, dog_sigma, dog_sigma])

        for gauss_sigma in gauss_sigmas:

            for step_length in step_lengths:

                # create output directory based on dog_sigma, gauss_sigma
                out_dir = os.path.join(dpResult, 'dog{}gau{}step{}'.format(dog_sigma, gauss_sigma, step_length))
                if not os.path.exists(out_dir):
                    print('\n Creating directory:', out_dir)
                    os.makedirs(out_dir)

                # create gaussian kernel
                gaussker = gaussgen([gauss_sigma, gauss_sigma, gauss_sigma])

                # half kernel size
                halfsize = int((max(gaussker.shape[0], dogkercc.shape[0]) + 1) / 2)

                # store gradient amplitude, gradient vector
                ga_res = cropVol(ga, halfsize)
                ga_res = nib.Nifti1Image(ga_res, img_affine)
                nib.save(ga_res, os.path.join(out_dir, 'ga.nii.gz'))

                gv_res = cropVol(gv, halfsize)
                gv_res = nib.Nifti1Image(gv_res, img_affine)
                nib.save(gv_res, os.path.join(out_dir, 'gv.nii.gz'))

                # blur gradient product
                gp_gauss = gradBlur(gp, gaussker)

                # crop and store FSL tensor
                fsl_tensor = np.stack((gp_gauss.gprrrrgauss, gp_gauss.gprrccgauss, gp_gauss.gprrzzgauss, gp_gauss.gpccccgauss, gp_gauss.gpcczzgauss, gp_gauss.gpzzzzgauss), axis=3)
                fsl_crop = nib.Nifti1Image(cropVol(fsl_tensor, halfsize).astype(np.float32), img_affine)
                nib.save(fsl_crop, os.path.join(out_dir, 'fsl_tensor.nii.gz'))

                # crop and store DTK tensor
                dtk_tensor = np.stack((gp_gauss.gprrrrgauss, gp_gauss.gprrccgauss, gp_gauss.gpccccgauss, gp_gauss.gprrzzgauss, gp_gauss.gpcczzgauss, gp_gauss.gpzzzzgauss), axis=3)
                dtk_crop = nib.Nifti1Image(cropVol(dtk_tensor, halfsize).astype(np.float32), img_affine)
                nib.save(dtk_crop, os.path.join(out_dir, 'dtk_tensor.nii.gz'))

                # crop brain mask
                brain_mask = nib.load(fpBmask)
                bmask = brain_mask.get_data()
                bmask = cropVol(bmask, halfsize)
                bmask = np.uint(bmask > 0)
                bmask = nib.Nifti1Image(bmask, brain_mask.affine)
                fp_bmask_crop = os.path.join(out_dir, 'bmask.nii.gz')
                nib.save(bmask, fp_bmask_crop)

                # crop seed mask
                seed_mask = nib.load(fp_smask)
                smask = seed_mask.get_data()
                smask = cropVol(smask, halfsize)
                smask = np.uint(smask > 0)
                smask = nib.Nifti1Image(cropVol(smask, halfsize), seed_mask.affine)
                fp_smask_crop = os.path.join(out_dir, 'smask.nii.gz')
                nib.save(smask, fp_smask_crop)

                ##
                # Test after
                ##
                for ang in angles:
                    fp_dtk_tensor = os.path.join(out_dir, 'dtk')
                    fp_track = os.path.join(out_dir, 'fiber_ang{}.trk'.format(ang))

                    # run dti_tracker here
                    CMD = 'dti_tracker {} {} -at {} -v3 -m {} 0.1 1.1 -sm {} 0.1 1.1 -l {} -vorder {}'.format(fp_dtk_tensor, fp_track, ang, fp_bmask_crop, fp_smask_crop, step_length, vox_order)
                    print('Running the following command: \n{}'.format(CMD))
                    subprocess.call( CMD, shell=True )


# ---------------------------------
# set parameters and filenames
# ---------------------------------

def main(args):
    parser = parsefn()
    filename, bmask, smask, angles, dog_sigma, gauss_sigma, output_dir, step_lengths = parse_inputs(parser, args)

    # run sta tract generation
    print('Running Structure Tensor Analysis\n')
    sta_track(filename, dog_sigma, gauss_sigma, bmask, smask, angles, output_dir, step_lengths)


if __name__ == "__main__":
    main(sys.argv)