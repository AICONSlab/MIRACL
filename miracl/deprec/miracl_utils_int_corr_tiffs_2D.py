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

from joblib import Parallel, delayed


def helpmsg():
    return '''

    Performs intensity correction on CLARITY tiff data in parallel using N4

    Example: miracl_utilfn_int_corr_tiffs_2D.py -f tiff_folder -o bias_corr_folder
        '''


def parseargs():
    parser = argparse.ArgumentParser(description=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False,
                                     usage='%(prog)s -f [input tiff folder] -o [ output folder ] -s [ shrink factor]'
                                           '-cn [ channel num ] -cp [ channel prefix ]')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', '--folder', type=str, required=True, metavar='dir',
                          help="Input CLARITY TIFF folder/dir")

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-o', '--outdir', type=str, metavar='', default='int_corr_tiffs',
                          help="Output folder name (default: %(default)s)")
    optional.add_argument('-cn', '--channum', type=int, metavar='', default=1,
                          help="Chan # for extracting single channel from multiple channel data (default: %(default)s)")
    optional.add_argument('-cp', '--chanprefix', type=str, metavar='', default=None,
                          help="Chan prefix (string before channel number in file name). ex: C00. (default: %(default)s) ")
    optional.add_argument('-m', '--maskimg', type=int, metavar='', default=1,
                          help="Mask images before correction (default: %(default)s)")
    optional.add_argument('-s', '--shrink', type=int, metavar='', default=7,
                          help="Shrink factor to lessen computation time (default: %(default)s)")
    optional.add_argument('-n', '--noise', type=float, metavar='', default=0.001,
                          help="Noise parameter for histogram sharpening - deconvolution (default: %(default)s)")
    optional.add_argument('-b', '--bins', type=int, metavar='', default=200,
                          help="Histogram bins (default: %(default)s)")
    optional.add_argument('-k', '--fwhm', type=float, metavar='', default=0.5,
                          help="FWHM for histogram sharpening - deconvolution (default: %(default)s)")
    optional.add_argument('-l', '--levels', type=int, metavar='', default=3,
                          help="Number of levels for convergence (default: %(default)s)")
    optional.add_argument('-i', '--iters', type=int, metavar='', default=20,
                          help="Number of iterations per level for convergence (default: %(default)s)")
    optional.add_argument('-t', '--thresh', type=int, metavar='', default=0,
                          help="Threshold per iteration for convergence (default: %(default)s)")
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

    shrink = args.shrink
    assert isinstance(shrink, int)

    fwhm = args.fwhm
    assert isinstance(fwhm, float)

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

    return indir, outdir, maskimg, chann, chanp, shrink, fwhm, noise, bins, levels, iters, thresh


def numericalsort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def biascorr(i, tif, outdir, maskimg, shrink, hist, conv):
    sys.stdout.write("\r processing slice %d ..." % i)
    sys.stdout.flush()

    tifcorr = os.path.join(outdir, os.path.basename(tif))

    if maskimg == 1:

        maskdir = os.path.join(outdir, 'masks')

        tifname = os.path.basename(tif).split('.tif')[0]
        mask = os.path.join(maskdir, '%s_mask.tif' % tifname)

        subprocess.check_call(
            'ThresholdImage 2 %s %s Otsu 4' % (tif, mask),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.check_call(
            'c3d %s -binarize -type uchar -o %s' % (mask, mask),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.check_call(
            'N4BiasFieldCorrection -d 2 -i %s -s %s -t %s -c %s -x %s -o %s'
            % (tif, shrink, hist, conv, mask, tifcorr),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    else:

        subprocess.check_call(
            'N4BiasFieldCorrection -d 2 -i %s -s %s -t %s -s %s -o %s'
            % (tif, shrink, hist, conv, tifcorr),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    subprocess.check_call(
        'c3d %s -type ushort -o %s' % (tifcorr, tifcorr),
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main():
    starttime = datetime.now()

    indir, outdir, maskimg, chann, chanp, shrink, fwhm, noise, bins, levels, iters, thresh = parseargs()

    # sort files
    if chanp is None:
        file_list = sorted(glob.glob("%s/*.tif" % indir), key=numericalsort)
    else:
        file_list = sorted(glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann)), key=numericalsort)

    cpuload = 0.95
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)

    totaliters = ('%dx' % iters) * levels
    totaliters = totaliters[:-1]

    hist = [fwhm, noise, bins]
    conv = [totaliters, thresh]

    print("\n Correcting TIFF images in parallel using %02d cpus \n" % ncpus)

    if maskimg == 1:
        maskdir = os.path.join(outdir, 'masks')
        os.makedirs(maskdir)

    Parallel(n_jobs=ncpus)(
        delayed(biascorr)(i, tif, outdir, maskimg, shrink, hist, conv)
        for i, tif in enumerate(file_list))

    print("\n Intensity correction done in %s ... Have a good day!\n" % (datetime.now() - starttime))


if __name__ == "__main__":
    main()
