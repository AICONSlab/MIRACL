#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import glob
import logging
import multiprocessing
import os
import tkFileDialog
from Tkinter import *
from datetime import datetime

import cv2
import nibabel as nib
import numpy as np
from joblib import Parallel, delayed


def helpmsg(name=None):
    return '''Usage: miracl_io_convertTIFFtoNII.py

Converts Tiff images to Nifti 

    A GUI will open to choose your:

        - < Input clarity tif dir > : images of only one channel

    ----------

    For command-line / scripting

    Usage: miracl_io_convertTIFFtoNII.py -f [Tiff folder]  -o [out nii name]

    Example: miracl_io_convertTIFFtoNII.py -f my_tifs -o stroke2 -cn 1 -cp C00 -ch Thy1YFP -vx 2.5 -vz 5


        '''


# Dependencies:
#
#     Python 2.7
#     used modules:
#         argparse, numpy, scipy, cv2, pandas, tifffile, Tkinter, tkFileDialog,
#         glob, re, os, sys, datetime, joblib, multiprocessing


def parsefn(args):
    if len(args) == 1:

        print("Running in GUI mode")

        Tk().withdraw()
        indir = tkFileDialog.askdirectory(title='Open clarity dir (with .tif files) by double clicking then "OK"')

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
            for field in fields:
                row = Frame(root)
                lab = Label(row, width=25, text=field, anchor='w')
                ent = Entry(row)
                row.pack(side=TOP, fill=X, padx=5, pady=5)
                lab.pack(side=LEFT)
                ent.pack(side=RIGHT, expand=YES, fill=X)
                entries.append((field, ent))
                values.append(ent)
            return entries, values

        root = Tk()
        root.title("Nii conversion options")
        root.geometry("300x350")
        [ents, vals] = makeform(root, fields)
        root.bind('<Return>', (lambda event, e=ents: fetch(e)))
        b1 = Button(root, text='Show',
                    command=(lambda e=ents: fetch(e)))
        b1.pack(side=LEFT, padx=5, pady=5)
        b2 = Button(root, text='Done', command=root.quit)
        b2.pack(side=RIGHT, padx=5, pady=5)
        root.mainloop()

        outnii = 'clarity' if not vals[0].get() else vals[0].get()

        d = 5 if not vals[1].get() else int(vals[1].get())

        chann = 1 if not vals[2].get() else int(vals[2].get())

        chanp = None if not vals[3].get() else vals[3].get()

        chan = 'eyfp' if not vals[4].get() else vals[4].get()

        vx = 0.005 if not vals[5].get() else int(vals[5].get()) / float(1000)

        vz = 0.005 if not vals[6].get() else int(vals[6].get()) / float(1000)

        cent = [0, 0, 0] if not vals[7].get() else np.array(vals[7].get())


    else:

        parser = argparse.ArgumentParser(description='', usage=helpmsg())

        parser.add_argument('-f', '--folder', type=str, required=True, metavar='', help="Input Clarity tif folder/dir")
        parser.add_argument('-d', '--down', type=int, metavar='', help="Downsample ratio (default: 5)")
        parser.add_argument('-cn', '--channum', type=int, metavar='',
                            help="Chan # for extracting single channel from multiple channel data (default: 1)")
        parser.add_argument('-cp', '--chanprefix', type=str, metavar='',
                            help="Chan prefix (string before channel number in file name). ex: C00")
        parser.add_argument('-ch', '--channame', type=str, metavar='', help="Output chan name (default: eyfp) ")
        parser.add_argument('-o', '--outnii', type=str, metavar='',
                            help="Output nii name (script will append downsample ratio and channel info to given name)")
        parser.add_argument('-vx', '--resx', type=float, metavar='',
                            help="Original resolution in x-y plane in um (default: 5)")
        parser.add_argument('-vz', '--resz', type=float, metavar='',
                            help="Original thickness (z-axis resolution / spacing between slices) in um (default: 5) ")
        parser.add_argument('-c', '--center', type=int, nargs='+', metavar='',
                            help="Nii center (default: 0,0,0 ) corresponding to Allen atlas nii template")

        args = parser.parse_args()

        print("\n running in script mode \n")

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
            print("\n down sample ratio not specified ... choosing default value of %d" % d)
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
            vx = 0.005  # 5 um
        else:
            vx = args.resx
            vx /= float(1000)

        if args.resz is None:
            vz = 0.005  # 5 um
        else:
            vz = args.resz
            vz /= float(1000)

        if args.center is None:
            cent = [0, 0, 0]
        else:
            cent = args.center

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


def numericalSort(value):
    numbers = re.compile(r'(\d+)')
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


# ---------

def converttiff2nii(d, i, x, newdata):
    """
    """

    # down ratio
    down = (1.0 / int(d))

    sys.stdout.write("\r processing slice %d ... " % i)
    sys.stdout.flush()

    m = cv2.imread(x, -1)
    newdata[i, :, :] = cv2.resize(m, (0, 0), fx=down, fy=down, interpolation=cv2.INTER_CUBIC)
    # data.append(mres)


def savenii(newdata, d, outnii, vx=None, vz=None, cent=None):

    # array type
    # data_array = np.array(mres, dtype='int16')

    outvox = vx * d
    vs = [outvox, outvox, vz]

    # Create nifti
    mat = np.eye(4) * outvox
    mat[0, 3] = cent[0]
    mat[1, 3] = cent[1]
    mat[2, 3] = cent[2]
    mat[2, 2] = vz
    mat[3, 3] = 1

    # roll dimensions
    data_array = np.rollaxis(newdata, 0, 3)

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

    scriptlog('tif2nii.log')

    startTime = datetime.now()

    args = sys.argv

    [indir, outnii, d, chann, chanp, chan, vx, vz, cent] = parsefn(args)

    cpuload = 0.95
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)

    # Get file list

    # sort files
    if chanp is None:
        file_list = sorted(glob.glob("%s/*.tif" % indir), key=numericalSort)
    else:
        file_list = sorted(glob.glob("%s/*%s%01d*.tif" % (indir, chanp, chann)), key=numericalSort)

    # make out dir
    outdir = 'niftis'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    # convert tiff files in //
    print("\n converting TIFF images to NII in parallel using %02d cpus \n" % ncpus)

    memap = '%s/tmp_array_memmap.map' % outdir

    m = cv2.imread(file_list[0], -1)

    newdata = np.memmap(memap, dtype=float, shape=(len(file_list), m.shape[0] / d, m.shape[1] / d), mode='w+')

    Parallel(n_jobs=ncpus)(
        delayed(converttiff2nii)(d, i, x, newdata) for i, x in enumerate(file_list))

    # stack slices

    # subprocess.Popen('c3d %s/*.nii.gz -tile z -o %s' % (outdir, stackname), shell=True,
    #                  stdout=subprocess.PIPE,
    #                  stderr=subprocess.PIPE)

    # save nii
    print("\n saving nifti stack \n")

    stackname = '%s/%s_%02dx_down_%s_chan.nii.gz' % (outdir, outnii, d, chan)

    savenii(newdata, d, stackname, vx, vz, cent)

    # clear tmp memmap
    os.remove(memap)

    print("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - startTime))


if __name__ == "__main__":
    main()
