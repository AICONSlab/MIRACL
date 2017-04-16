#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import glob
import logging
import multiprocessing
import os
import warnings
from Tkinter import *
from argparse import RawTextHelpFormatter
from datetime import datetime

import cv2
import nibabel as nib
import numpy as np
from PyQt4.QtGui import *
from joblib import Parallel, delayed

warnings.simplefilter("ignore", UserWarning)
import scipy.ndimage


def helpmsg():
    return '''

Converts Tiff images to Nifti 

    A GUI will open to choose your:

        - < Input CLARITY TIFF dir >

    ----------

    For command-line / scripting

    Usage: miracl_io_convertTIFFtoNII.py -f [Tiff folder]

    Example: miracl_io_convertTIFFtoNII.py -f my_tifs -o stroke2 -cn 1 -cp C00 -ch Thy1YFP -vx 2.5 -vz 5

        '''


# Dependencies:
#
#     Python 2.7
#     used modules:
#         argparse, numpy, cv2, nibabel, Tkinter, tkFileDialog,
#         glob, re, os, sys, datetime, joblib, multiprocessing


def folder_dialog(self, msg):
    """
    Get file / folder with gui with QFileDialog
    """

    folder = str(QFileDialog.getExistingDirectory(self, "%s" % msg, "."))

    if len(folder) > 0:
        print "\n Folder chosen for reading is: %s" % folder
    else:
        print "No folder was chosen"

    return folder


def parsefn(args):
    # parser = argparse.ArgumentParser(description='', usage=helpmsg(), formatter_class=RawTextHelpFormatter,
    # add_help=False)
    parser = argparse.ArgumentParser(description=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False,
                                     usage='%(prog)s -f [folder] -d [down-sample ratio] -cn [chann #]'
                                           ' -cp [chann prefix] -ch [out chann name] -o [out nii name] -vx [x-y res]'
                                           ' -vz [z res] -c [center]')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-f', '--folder', type=str, required=True, metavar='dir',
                          help="Input CLARITY TIFF folder/dir")

    optional = parser.add_argument_group('optional arguments')

    optional.add_argument('-d', '--down', type=int, metavar='', help="Downsample ratio (default: 5)")
    optional.add_argument('-cn', '--channum', type=int, metavar='',
                          help="Chan # for extracting single channel from multiple channel data (default: 1)")
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

    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    if len(args) == 1:

        print("Running in GUI mode")

        a = QApplication(sys.argv)
        w = QWidget()

        msg = "Open clarity dir (with .tif files)"

        indir = folder_dialog(w, msg)

        if not indir:
            sys.exit('input folder/directory not specified ... exiting')

        if not os.path.exists(indir):
            sys.exit('%s does not exist ... please check path and rerun script' % indir)

        fields = 'Out nii name (def = clarity)', 'Downsample ratio (def = 5)', 'chan # (def = 1)', 'chan prefix', \
                 'Out chan name (def = eyfp)', 'Resolution (x,y) (def = 5 "um")', 'Thickness (z) (def = 5 "um")', \
                 'center (def = 0,0,0)'

        def fetch(entries):
            for entry in entries:
                field = entry[0]
                text = entry[1].get()
                print('%s: "%s"' % (field, text))

        def makeform(root, fields):
            entries = []
            values = []

            strlen = len(max(fields, key=len))
            strw = int(strlen * 1.2)

            for field in fields:
                row = Frame(root)
                lab = Label(row, width=strw, text=field, anchor='w')
                ent = Entry(row)
                row.pack(side=TOP, fill=X, padx=5, pady=5)
                lab.pack(side=LEFT)
                ent.pack(side=RIGHT, expand=YES, fill=X)
                entries.append((field, ent))
                values.append(ent)

            return entries, values, strw

        def helpwindown(root, helpfun):
            window = Toplevel(root)
            window.title("Help func")
            t = Text(window, height=50, width=150)
            t.pack()
            t.insert(END, "%s" % helpfun)

        # def main():
        root = Tk()
        root.title("Nii conversion options")

        [ents, vals, strw] = makeform(root, fields)

        n = len(fields)
        w = strw * 10
        h = (n * 40) + 50
        root.geometry("%dx%d" % (w, h))

        root.bind('<Return>', (lambda event, e=ents: fetch(e)))

        b1 = Button(root, text='Enter',
                    command=(lambda e=ents: fetch(e)))
        b1.pack(side=LEFT, padx=5, pady=5)

        b2 = Button(root, text='Done', command=root.quit)
        b2.pack(side=RIGHT, padx=5, pady=5)

        b3 = Button(root, text="Help func", command=lambda: helpwindown(root, helpmsg()))
        b3.pack(side=LEFT, padx=5, pady=5)

        root.mainloop()

        outnii = 'clarity' if not vals[0].get() else vals[0].get()

        d = 5 if not vals[1].get() else int(vals[1].get())

        chann = 1 if not vals[2].get() else int(vals[2].get())

        chanp = None if not vals[3].get() else vals[3].get()

        chan = 'eyfp' if not vals[4].get() else vals[4].get()

        vx = 5 if not vals[5].get() else float(vals[5].get())

        vz = 5 if not vals[6].get() else float(vals[6].get())

        cent = [0, 0, 0] if not vals[7].get() else np.array(vals[7].get())

    else:

        args = parser.parse_args()

        print("\n running in script mode")

        # check if pars given

        assert isinstance(args.folder, str)
        indir = args.folder

        if not os.path.exists(indir):
            sys.exit('%s does not exist ... please check path and rerun script' % indir)

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
            chann = 1
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

    # make res in um
    vx /= float(1000)  # in um
    vz /= float(1000)

    return indir, outnii, d, chann, chanp, chan, vx, vz, cent


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


def savenii(newdata, d, outnii, vx=None, vz=None, cent=None):
    # array type
    # data_array = np.array(mres, dtype='int16')

    outvox = vx * d
    outz = vz * d
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

    print("\n down-sampling in the z dimension")

    sp_inter = 1 if data_array.shape[0] < 5000 else 0
    down = (1.0 / int(d))
    zoom = [1, 1, down]
    data_array = scipy.ndimage.interpolation.zoom(data_array, zoom, order=sp_inter)

    nii = nib.Nifti1Image(data_array, mat)

    # nifti header info
    nii.header.set_data_dtype(np.int16)
    nii.header.set_zooms([vs[0], vs[1], vs[2]])

    # Save nifti
    nib.save(nii, outnii)


# ---------

def main():
    """
    :rtype: nifti file
    """
    # scriptlog('tif2nii.log')

    starttime = datetime.now()

    args = sys.argv

    [indir, outnii, d, chann, chanp, chan, vx, vz, cent] = parsefn(args)

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

    Parallel(n_jobs=ncpus)(
        delayed(converttiff2nii)(d, i, x, newdata, tifx) for i, x in enumerate(file_list))

    # stack slices

    # subprocess.Popen('c3d %s/*.nii.gz -tile z -o %s' % (outdir, stackname), shell=True,
    #                  stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)

    # save nii
    print("\n\n saving nifti stack")

    stackname = '%s/%s_%02dx_down_%s_chan.nii.gz' % (outdir, outnii, d, chan)

    savenii(newdata, d, stackname, vx, vz, cent)

    # clear tmp memmap
    os.remove(memap)

    print("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - starttime))


if __name__ == "__main__":
    main()
