#! /usr/bin/env python
# Maged Goubran @ 2017, mgoubran@stanford.edu

# coding: utf-8

import argparse
import glob
import multiprocessing
import os
import re
import subprocess
import sys
from argparse import RawTextHelpFormatter
from datetime import datetime

import nibabel as nib
import numpy as np
import scipy.ndimage
import tifffile as tiff
from joblib import Parallel, delayed

import miracl_utils_endstatement as statement


def helpmsg():
    return '''

    Performs intensity correction on CLARITY tiff data in parallel using N4

    Creates a downsampled nifti from the tiff data
    Runs N4 'bias field' / intensity correction on the nifti
    Upsamples the output bias field and applies it to the tiff data

    Example: miracl_utils_int_corr_tiffs.py -f tiff_folder -o bias_corr_folder
        '''


def parseargs():
    parser = argparse.ArgumentParser(description=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False,
                                     usage='%(prog)s -f [input tiff folder] -o [ output folder ] -s [ shrink factor]'
                                           '-cn [ channel num ] -cp [ channel prefix ] -p [ power ]')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', '--folder', type=str, required=True, metavar='dir',
                          help="Input CLARITY TIFF folder/dir")

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-od', '--outdir', type=str, metavar='', default='int_corr_tiffs',
                          help="Output folder name (default: %(default)s)")
    optional.add_argument('-cn', '--channum', type=int, metavar='', default=1,
                          help="Chan # for extracting single channel from multiple channel data (default: %(default)s)")
    optional.add_argument('-cp', '--chanprefix', type=str, metavar='', default=None,
                          help="Chan prefix (string before channel number in file name). ex: C00. (default: %("
                               "default)s) ")
    optional.add_argument('-ch', '--channame', type=str, metavar='', default='AAV',
                          help="Output chan name (default: %(default)s) ")
    optional.add_argument('-on', '--outnii', type=str, metavar='', default='clarity',
                          help="Output nii name (script will append downsample ratio & channel info to given name)")
    optional.add_argument('-vx', '--resx', type=float, metavar='', default=5,
                          help="Original resolution in x-y plane in um (default: %(default)s)")
    optional.add_argument('-vz', '--resz', type=float, metavar='', default=5,
                          help="Original thickness (z-axis resolution / spacing between slices) in um (default: %("
                               "default)s) ")
    optional.add_argument('-m', '--maskimg', type=int, metavar='', default=1,
                          help="Mask images before correction (default: %(default)s)")
    optional.add_argument('-d', '--down', type=int, metavar='', default=5,
                          help="Downsample / shrink factor to run boias corr on downsampled data"
                               "(default: %(default)s)")
    optional.add_argument('-n', '--noise', type=float, metavar='', default=0.005,
                          help="Noise parameter for histogram sharpening - deconvolution (default: %(default)s)")
    optional.add_argument('-b', '--bins', type=int, metavar='', default=200,
                          help="Histogram bins (default: %(default)s)")
    optional.add_argument('-k', '--fwhm', type=float, metavar='', default=0.5,
                          help="FWHM for histogram sharpening - deconvolution (default: %(default)s)")
    optional.add_argument('-l', '--levels', type=int, metavar='', default=4,
                          help="Number of levels for convergence (default: %(default)s)")
    optional.add_argument('-it', '--iters', type=int, metavar='', default=50,
                          help="Number of iterations per level for convergence (default: %(default)s)")
    optional.add_argument('-t', '--thresh', type=int, metavar='', default=0,
                          help="Threshold per iteration for convergence (default: %(default)s)")
    optional.add_argument('-p', '--mulpower', type=int, metavar='', default=1,
                          help="Use the bias field raised to a power of 'p' to enhance its effects"
                               "(default: %(default)s)")
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    args = parser.parse_args()

    indir = args.folder
    assert os.path.exists(indir), 'Input dir: %s does not exist!' % indir

    outdir = args.outdir
    assert isinstance(outdir, str)
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    maskimg = args.maskimg
    assert isinstance(maskimg, int)

    chann = args.channum
    assert isinstance(chann, int)

    chanp = args.chanprefix
    assert isinstance(chanp, str)

    chan = args.channame
    assert isinstance(chan, str)

    down = args.down
    assert isinstance(down, int)

    outnii = args.outnii
    assert isinstance(outnii, str)

    fwhm = args.fwhm
    assert isinstance(fwhm, float)

    vx = args.resx
    vz = args.resz

    noise = args.noise
    assert isinstance(noise, float)

    bins = args.bins
    assert isinstance(bins, int)

    levels = args.levels
    assert isinstance(levels, int)

    iters = args.iters
    assert isinstance(iters, int)

    thresh = args.thresh
    assert isinstance(thresh, int)

    mulpower = args.mulpower
    assert isinstance(mulpower, int)

    return indir, outdir, maskimg, chann, chanp, down, fwhm, noise, bins, levels, iters, thresh, mulpower, outnii, \
           vx, vz, chan


def createnii(tifdir, down, chann, chanp, chan, outnii, vx, vz):
    print("\n converting TIFF images to NII")

    subprocess.check_call(
        'miracl_io_convertTIFFtoNII.py -f %s -d %s -cn %s -cp %s -ch %s -vx %s -vz %s -o %s'
        % (tifdir, down, chann, chanp, chan, vx, vz, outnii),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def biascorrnii(nii, maskimg, hist, conv, niicorr, mask, field):
    print("\n Performing intensity correction on downsampled nifti")

    if maskimg == 1:

        subprocess.check_call(
            'ThresholdImage 3 %s %s Otsu 5' % (nii, mask),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.check_call(
            'c3d %s -binarize -type uchar -o %s' % (mask, mask),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.check_call(
            'N4BiasFieldCorrection -d 3 -i %s -t %s -c %s -x %s -o [%s, %s]'
            % (nii, hist, conv, mask, niicorr, field),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    else:

        subprocess.check_call(
            'N4BiasFieldCorrection -d 2 -i %s -s 1 -t %s -s %s -o [%s, %s]'
            % (nii, hist, conv, niicorr, field),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def numericalsort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def applycorr(i, tif, outdir, biasres, down, mulpower):
    sys.stdout.write("\r processing slice %d ..." % i)
    sys.stdout.flush()

    biasslice = biasres[:, :, i - 1]
    biassliceres = scipy.ndimage.interpolation.zoom(biasslice, down)

    tifimg = tiff.imread(tif)

    if tifimg.shape != biassliceres.shape:
        array = np.full(tifimg.shape, biassliceres.min(), np.float16)
        array[0:biassliceres.shape[0], 0:biassliceres.shape[1]] = biassliceres
    else:
        array = biassliceres

    corrtif = tifimg / np.power(array, mulpower)

    tifcorrfile = os.path.join(outdir, os.path.basename(tif))

    tiff.imsave(tifcorrfile, corrtif)


def main():

    starttime = datetime.now()

    indir, outdir, maskimg, chann, chanp, down, fwhm, noise, bins, levels, iters, thresh, mulpower, outnii, vx, vz, \
    chan = parseargs()

    # make downsampled nii
    createnii(indir, down, chann, chanp, chan, outnii, vx, vz)

    # bias corr
    totaliters = ('%dx' % iters) * levels
    totaliters = totaliters[:-1]

    hist = [fwhm, noise, bins]
    conv = [totaliters, thresh]

    niidir = 'niftis'

    niiname = '%s/%s_%02dx_down_%s_chan.nii.gz' % (niidir, outnii, down, chan)

    corname = os.path.basename(niiname).split('.nii')[0]
    niicorr = os.path.join(niidir, '%s_corr.nii.gz' % corname)
    field = os.path.join(niidir, '%s_biasfield.nii.gz' % corname)
    mask = os.path.join(niidir, '%s_mask.nii.gz' % corname)

    biascorrnii(niiname, maskimg, hist, conv, niicorr, mask, field)

    # up-sample bias field
    biasnii = nib.load(field)
    bias = biasnii.get_data()
    biasres = scipy.ndimage.interpolation.zoom(bias, [1, 1, down])

    # sort files
    if chanp is None:
        file_list = sorted(glob.glob("%s/*.tif" % indir), key=numericalsort)
    else:
        file_list = sorted(glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann)), key=numericalsort)

    cpuload = 0.95
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)

    print("\n Correcting TIFF images in parallel using %02d cpus" % ncpus)

    Parallel(n_jobs=ncpus)(
        delayed(applycorr)(i, tif, outdir, biasres, down, mulpower)
        for i, tif in enumerate(file_list))

    # print("\n Intensity correction done in %s ... Have a good day!\n" % (datetime.now() - starttime))

    statement.main('Test', '%s' % (datetime.now() - starttime))

if __name__ == "__main__":
    main()
