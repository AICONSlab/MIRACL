#!/usr/bin/env python
# Maged Goubran @ 2017, mgoubran@stanford.edu

# coding: utf-8

import argparse
import glob
import logging
import multiprocessing
import os
import re
import sys
import warnings
from argparse import RawTextHelpFormatter
from datetime import datetime

import cv2
import nibabel as nib
import numpy as np
import scipy.ndimage
from PyQt4.QtGui import *
from joblib import Parallel, delayed

from miracl.conv import miracl_conv_gui_options as gui_opts

warnings.simplefilter("ignore", UserWarning)


def helpmsg(name=None):
    return ''' Converts Tiff images to Nifti 

    A GUI will open to choose your:

        - < Input CLARITY TIFF dir >

    ----------

    For command-line / scripting

    Usage: miracl_conv_convertTIFFtoNII.py -f [Tiff folder]

    Example: miracl_conv_convertTIFFtoNII.py -f my_tifs -o stroke2 -cn 1 -cp C00 -ch Thy1YFP -vx 2.5 -vz 5

    required arguments:
      -f dir, --folder dir  Input CLARITY TIFF folder/dir

    optional arguments:
      -d , --down           Down-sample ratio (default: 5)
      -cn , --channum       Chan # for extracting single channel from multiple channel data (default: 0)
      -cp , --chanprefix    Chan prefix (string before channel number in file name). ex: C00
      -ch , --channame      Output chan name (default: eyfp)
      -o , --outnii         Output nii name (script will append downsample ratio & channel info to given name)
      -vx , --resx          Original resolution in x-y plane in um (default: 5)
      -vz , --resz          Original thickness (z-axis resolution / spacing between slices) in um (default: 5)
      -c  [ ...], --center  [ ...]
                            Nii center (default: 0,0,0 ) corresponding to Allen atlas nii template
      -dz , --downzdim      Down-sample in z dimension, binary argument, (default: 1) => yes
      -pd , --prevdown      Previous down-sample ratio, if already downs-sampled
      -h, --help            Show this help message and exit

    '''


def folder_dialog(self, msg):
    """
    Get file / folder with gui with QFileDialog
    """
    folder = str(QFileDialog.getExistingDirectory(self, "%s" % msg, "."))

    if len(folder) > 0:
        print("\n Folder chosen for reading is: %s" % folder)
    else:
        print("No folder was chosen")

    return folder


def parsefn():
    if sys.argv[-2] == 'conv' and sys.argv[-1] == 'tiff_nii':
        parser = argparse.ArgumentParser(description='', usage=helpmsg(), formatter_class=RawTextHelpFormatter,
                                         add_help=False)
    else:
        parser = argparse.ArgumentParser(description='', usage=helpmsg(), formatter_class=RawTextHelpFormatter,
                                         add_help=False)
        # parser = argparse.ArgumentParser(description=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False,
        #                                  usage='%(prog)s -f [folder] -d [down-sample ratio] -cn [chann #]'
        #                                        ' -cp [chann prefix] -ch [out chann name] -o [out nii name] -vx [x-y res]'
        #                                        ' -vz [z res] -c [center] -dz [down-sample in z]')

        required = parser.add_argument_group('required arguments')
        required.add_argument('-f', '--folder', type=str, required=True, metavar='dir',
                              help="Input CLARITY TIFF folder/dir")

        optional = parser.add_argument_group('optional arguments')

        optional.add_argument('-d', '--down', type=int, metavar='', help="Down-sample ratio (default: 5)")
        optional.add_argument('-cn', '--channum', type=int, metavar='',
                              help="Chan # for extracting single channel from multiple channel data (default: 0)")
        optional.add_argument('-cp', '--chanprefix', type=str, metavar='',
                              help="Chan prefix (string before channel number in file name). ex: C00")
        optional.add_argument('-ch', '--channame', type=str, metavar='', help="Output chan name (default: eyfp) ")
        optional.add_argument('-o', '--outnii', type=str, metavar='',
                              help="Output nii name (script will append downsample ratio & channel info to given name)")
        optional.add_argument('-vx', '--resx', type=float, metavar='',
                              help="Original resolution in x-y plane in um (default: 5)")
        optional.add_argument('-vz', '--resz', type=float, metavar='',
                              help="Original thickness (z-axis resolution / spacing between slices) in um (default: 5) ")
        optional.add_argument('-c', '--center', type=int, nargs='+', metavar='',
                              help="Nii center (default: 0,0,0 ) corresponding to Allen atlas nii template")
        optional.add_argument('-dz', '--downzdim', type=int, metavar='',
                              help="Down-sample in z dimension, binary argument, (default: 1) => yes")
        optional.add_argument('-pd', '--prevdown', type=int, metavar='',
                              help="Previous down-sample ratio, if already downs-sampled")

        # optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    if sys.argv[-2] == 'conv' and sys.argv[-1] == 'tiff_nii':

        print("Running in GUI mode")

        title = 'Tiff to Nii conversion'
        dirs = ['Input tiff folder']
        fields = ['Out nii name (def = clarity)', 'Downsample ratio (def = 5)', 'chan # (def = 1)', 'chan prefix',
                  'Out chan name (def = eyfp)', 'Resolution (x,y) (def = 5 "um")', 'Thickness (z) (def = 5 "um")',
                  'center (def = 0,0,0)', 'Downsample in z (def = 1)', 'Prev Downsampling (def = 1 -> not downsampled)']
        # field_names = ['outnii', 'd', 'chann', 'chanp', 'chan', 'vx', 'vz', 'cent', 'downz', 'pd']

        app = QApplication(sys.argv)
        menu, linedits, labels = gui_opts.OptsMenu(title=title, dirs=dirs, fields=fields, helpfun=helpmsg())
        menu.show()
        app.exec_()
        app.processEvents()

        indirstr = labels[dirs[0]].text()
        indir = str(indirstr.split(":")[1]).lstrip()
        assert os.path.exists(indir), '%s does not exist ... please check path and rerun script' % indir

        # Initialize default params

        outnii = 'clarity' if not linedits[fields[0]].text() else str(linedits[fields[0]].text())
        # assert isinstance(outnii, str), '-outnii not a string'

        d = 5 if not linedits[fields[1]].text() else int(linedits[fields[1]].text())
        # assert isinstance(d, int), '-d not a integer'

        chann = 0 if not linedits[fields[2]].text() else int(linedits[fields[2]].text())
        # assert isinstance(chann, int), '-chann not a integer'

        chanp = None if not linedits[fields[3]].text() else str(linedits[fields[3]].text())

        chan = 'eyfp' if not linedits[fields[4]].text() else str(linedits[fields[4]].text())

        vx = 5 if not linedits[fields[5]].text() else float(linedits[fields[5]].text())

        vz = 5 if not linedits[fields[6]].text() else float(linedits[fields[6]].text())

        cent = [0, 0, 0] if not linedits[fields[7]].text() else linedits[fields[7]].text()

        downz = 1 if not linedits[fields[8]].text() else int(linedits[fields[8]].text())

        pd = 1 if not linedits[fields[9]].text() else int(linedits[fields[9]].text())

    else:

        print("\n running in script mode")

        # check if pars given
        assert isinstance(args.folder, str)
        indir = args.folder

        assert os.path.exists(indir), '%s does not exist ... please check path and rerun script' % indir

        if args.outnii is None:
            outnii = 'clarity'
        else:
            assert isinstance(args.outnii, str)
            outnii = args.outnii

        if args.down is None:
            d = 5
            print("\n down-sample ratio not specified ... choosing default value of %d" % d)
        else:
            assert isinstance(args.down, int)
            d = args.down

        if args.channum is None:
            chann = 0
            print("\n channel # not specified ... choosing default value of %d" % chann)
        else:
            assert isinstance(args.channum, int)
            chann = args.channum

            if args.chanprefix is None:
                sys.exit('-cp (channel prefix) not specified ')

        chanp = args.chanprefix if args.chanprefix is not None else None

        if args.channame is None:
            chan = 'eyfp'
            print("\n channel name not specified ... choosing default value of %s" % chan)
        else:
            assert isinstance(args.channame, str)
            chan = args.channame

        if args.resx is None:
            vx = 5
        else:
            vx = args.resx

        if args.resz is None:
            vz = 5
        else:
            vz = args.resz

        if args.center is None:
            cent = [0, 0, 0]
        else:
            cent = args.center

        if args.downzdim is None:
            downz = 1
        else:
            downz = args.downzdim

        if args.prevdown is None:
            pd = 1
        else:
            pd = args.prevdown

    # make res in um
    vx /= float(1000)  # in um
    vz /= float(1000)

    return indir, outnii, d, chann, chanp, chan, vx, vz, cent, downz, pd


# ---------
# Logging fn

def scriptlog(logname):
    class StreamToLogger(object):
        """
       Fake file-like stream object that redirects writes to a logger instance.
       """

        def __init__(self, logger, log_level=logging.INFO):
            self.logger = logger
            self.log_level = log_level
            self.linebuf = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s" % logname,
        format='%(asctime)s:%(message)s',
        filemode='w')

    stdout_logger = logging.getLogger('STDOUT')
    handler = logging.StreamHandler()
    stdout_logger.addHandler(handler)
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger('STDERR')
    stderr_logger.addHandler(handler)
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)


# ---------

# sort fn

def numericalsort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


# ---------

def converttiff2nii(d, i, x, newdata, tifx):
    """
    """

    # down ratio
    down = (1.0 / int(d))

    sys.stdout.write("\r processing slice %d ..." % i)
    sys.stdout.flush()

    m = cv2.imread(x, -1)

    # nearest neighbour for very large data sets
    inter = cv2.INTER_CUBIC if tifx < 5000 else cv2.INTER_NEAREST

    newdata[i, :, :] = cv2.resize(m, (0, 0), fx=down, fy=down, interpolation=inter)
    # data.append(mres)


def savenii(newdata, d, outnii, downz, vx=None, vz=None, cent=None):
    # array type
    # data_array = np.array(mres, dtype='int16')

    outvox = vx * d
    dz = d if vx <= vz else int(d * float(vx / vz))

    if downz == 1:
        outz = vz * dz
    else:
        outz = vz

    vs = [outvox, outvox, outz]

    # Create nifti
    mat = np.eye(4) * outvox
    mat[0, 3] = cent[0]
    mat[1, 3] = cent[1]
    mat[2, 3] = cent[2]
    mat[2, 2] = outz
    mat[3, 3] = 1

    # roll dimensions
    data_array = np.rollaxis(newdata, 0, 3)

    # downsample z dim

    if downz == 1:
        print("\n\n down-sampling in the z dimension")

        sp_inter = 1 if data_array.shape[0] < 5000 else 0
        down = (1.0 / int(dz))
        zoom = [1, 1, down]
        data_array = scipy.ndimage.interpolation.zoom(data_array, zoom, order=sp_inter)

    nii = nib.Nifti1Image(data_array, mat)

    # nifti header info
    nii.header.set_data_dtype(np.int16)
    nii.header.set_zooms([vs[0], vs[1], vs[2]])

    # save nii
    print("\n saving nifti stack")

    # Save nifti
    nib.save(nii, outnii)


# ---------

def main(args):
    starttime = datetime.now()

    parser = parsefn()
    indir, outnii, d, chann, chanp, chan, vx, vz, cent, downz, pd = parse_inputs(parser, args)

    cpuload = 0.95
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)

    # Get file list

    # sort files
    if chanp is None:
        file_list = sorted(glob.glob("%s/*.tif" % indir), key=numericalsort)
    else:
        file_list = sorted(glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann)), key=numericalsort)

    # make out dir
    outdir = 'niftis'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # convert tiff files in //
    print("\n converting TIFF images to NII in parallel using %02d cpus \n" % ncpus)

    memap = '%s/tmp_array_memmap.map' % outdir

    tif = cv2.imread(file_list[0], -1)

    tifx = tif.shape[0]
    tify = tif.shape[1]
    tifxd = int(round(float(tifx) / d))
    tifyd = int(round(float(tify) / d))

    newdata = np.memmap(memap, dtype=float, shape=(len(file_list), tifxd, tifyd), mode='w+')

    Parallel(n_jobs=ncpus, backend="threading")(
        delayed(converttiff2nii)(d, i, x, newdata, tifx) for i, x in enumerate(file_list))

    # stack slices

    # subprocess.Popen('c3d %s/*.nii.gz -tile z -o %s' % (outdir, stackname), shell=True,
    #                  stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)

    # for prev down-sampled
    nd = d * pd

    stackname = '%s/%s_%02dx_down_%s_chan.nii.gz' % (outdir, outnii, nd, chan)

    nvx = vx * pd
    nvz = vz * pd

    savenii(newdata, d, stackname, downz, nvx, nvz, cent)

    # clear tmp memmap
    os.remove(memap)

    print("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - starttime))


if __name__ == "__main__":
    main(sys.argv)
