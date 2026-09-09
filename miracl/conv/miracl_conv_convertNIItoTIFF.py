#!/usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@utoronto.ca

# coding: utf-8

import argparse
# from PyQt5.QtWidgets import *
import logging
import os
import sys
import warnings
from argparse import RawTextHelpFormatter
from datetime import datetime

import nibabel as nib
import numpy as np
import scipy.ndimage
import tifffile as tiff
from pathlib import Path
from tqdm import tqdm
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from miracl.conv import miracl_conv_gui_options as gui_opts

import pdb

warnings.simplefilter("ignore", UserWarning)


def helpmsg():
    return '''

Converts Nifti images to Tiff

    A GUI will open to choose your:

        - < Input CLARITY Nii >

    ----------

    For command-line / scripting

    Usage: miracl_conv_convertNIItoTIFF.py -i [Nii file]

    Example: miracl_conv_convertNIItoTIFF.py -i stroke2.nii.gz -o stroke2.tiff -u 5

    required arguments:
      -i, --input          Input CLARITY Nii

    optional arguments:
      -u, --up   [ ...]    Up-sample ratio. Either one value applied to all axes, or three
                            values "X Y Z" for per-axis ratios (order must match the input
                            nii's array axes), e.g. -u 2 2 4 for xy=2, z=4 (default: 1)
      -o, --outnii         Output nii name (script will append downsample ratio & channel info to given name)
      -s, --spline         Spline order
      -st, --tiffstack     Write output as a directory of per-slice TIFFs instead of one multi-page
                            TIFF (default: off). Required if the output will be read back in by
                            miracl_conv_convertTIFFtoNII.py, which expects one file per slice.
      -tp, --transpose     Transpose each XY slice before writing (default: off). Nibabel doesn't
                            guarantee a width/height axis order, so whether this is needed depends on
                            the source of your input nii - verify on one slice before running the
                            full stack (compare against the same slice in a nifti viewer, e.g. it
                            shouldn't look rotated 90 degrees or mirrored).

      -h, --help           Show this help message and exit


        '''


# Dependencies:
#
#     Python 2.7
#     used modules:
#         argparse, numpy, cv2, nibabel, pyqt4,
#         glob, re, os, sys, datetime, joblib, multiprocessing


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
    if len(sys.argv) >= 3 and sys.argv[-2] == 'conv' and sys.argv[-1] == 'nii_tiff':
        parser = argparse.ArgumentParser(description='', usage=helpmsg(), formatter_class=RawTextHelpFormatter,
                                         add_help=False)
    else:
        parser = argparse.ArgumentParser(description='', usage=helpmsg(), formatter_class=RawTextHelpFormatter, add_help=False)
                                         #usage='%(prog)s  -i [In nii] -o [Out tiff] -u [Up-sample ratio] -s [Spline order]')

        required = parser.add_argument_group('required arguments')
        required.add_argument('-i', '--input', type=str, required=True, metavar='dir',
                              help="Input NII")

        optional = parser.add_argument_group('optional arguments')

        optional.add_argument('-u', '--up', type=float, nargs='+', metavar='',
                              help="Up-sample ratio: one value for all axes, or three values "
                                   "'X Y Z' for per-axis ratios (default: 1)")
        optional.add_argument('-o', '--outtiff', type=str, metavar='', help="Output tiff name")
        optional.add_argument('-s', '--spline', type=int, metavar='', help="Spline order")
        optional.add_argument('-st', '--tiffstack', action='store_true',
                              help="Write output as a directory of per-slice TIFFs instead of a single "
                                   "multi-page TIFF (default: off)")
        optional.add_argument('-tp', '--transpose', action='store_true',
                              help="Transpose each XY slice before writing (default: off). Verify on "
                                   "one slice first - axis order isn't guaranteed by nibabel.")

    # optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    if sys.argv[-2] == 'conv' and sys.argv[-1] == 'nii_tiff':

        print("Running in GUI mode")

        # from PyQt5.QtGui import *
        from PyQt5.QtWidgets import QApplication
        from miracl.conv import miracl_conv_gui_options as gui_opts

        title = 'Nii to Tiff conversion'
        dirs = ['Input Nii file']
        fields = ['Out nii name (def = clarity)', 'Up-sample ratio (def = 1)', 'Spline order (def = 3)']

        app = QApplication(sys.argv)
        menu, linedits, labels = gui_opts.OptsMenu(title=title, dirs=dirs, fields=fields, helpfun=helpmsg())
        menu.show()
        app.exec_()
        app.processEvents()

        indirstr = labels[dirs[0]].text()
        input = str(indirstr.split(":")[1]).lstrip()
        assert os.path.exists(input), '%s does not exist ... please check path and rerun script' % input

        # Initialize default params

        outtiff = 'clarity.tif' if not linedits[fields[0]].text() else str(linedits[fields[0]].text())

        u = 1 if not linedits[fields[1]].text() else int(linedits[fields[1]].text())

        s = 3 if not linedits[fields[2]].text() else int(linedits[fields[1]].text())

        tiffstack = False  # not exposed in the GUI form yet; script mode has the -st flag
        transpose = False  # not exposed in the GUI form yet; script mode has the -tp flag

    else:

        print("\n running in script mode")

        # check if pars given

        assert isinstance(args.input, str)
        input = args.input

        assert os.path.exists(input), '%s does not exist ... please check path and rerun script' % input

        if args.outtiff is None:
            outtiff = 'clarity.tif'
        else:
            assert isinstance(args.outtiff, str)
            outtiff = args.outtiff

        if args.up is None:
            u = 1
            print("\n Up-sample ratio not specified ... choosing default value of %d" % u)
        elif len(args.up) == 1:
            u = args.up[0]
        elif len(args.up) == 3:
            u = tuple(args.up)
        else:
            parser.error("-u/--up expects either 1 value (uniform) or 3 values (X Y Z)")

        if args.spline is None:
            s = 3
            print("\n Spline order not specified ... choosing default value of %d" % s)
        else:
            assert isinstance(args.spline, int)
            s = args.spline

        tiffstack = bool(args.tiffstack)
        transpose = bool(args.transpose)

    return input, outtiff, u, s, tiffstack, transpose


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


def convert_nii_to_tiff(input_nii, out_tiff, upsample_ratio, spline_order, tiffstack=False, transpose=False, grid_mode=True, compression="zstd", dtype=None):
    print("new function!")

    nii_img = nib.load(input_nii)
    vol = np.asarray(nii_img.dataobj)
    out_dtype = if dtype else nii_img.get_data_dtype()

    if np.issubdtype(out_dtype, np.integer):
        if vol.dtype.kind == "f" and not np.array_equal(vol, np.rint(vol)):
            raise ValueError("input has non-integer values; refusing to cast to "
                            f"{out_dtype} (is this really a label volume?)")
        lim = np.iinfo(out_dtype)
        if vol.min() < lim.min or vol.max() > lim.max:
            raise ValueError(f"labels span [{vol.min()}, {vol.max()}], "
                            f"outside {out_dtype} range")

    ratios = ((float(upsample_ratio),) * vol.ndim if np.isscalar(upsample_ratio)
              else tuple(float(r) for r in upsample_ratio))
    if len(ratios) != vol.ndim:
        raise ValueError(f"upsample_ratio has {len(ratios)} entries, "
                         f"volume is {vol.ndim}D")

    # scipy's own output-shape rule, so we know what zoom will hand back
    target = tuple(int(round(n * f)) for n, f in zip(vol.shape, ratios))

    kw = dict(order=spline_order, grid_mode=grid_mode,
              mode="nearest" if grid_mode else "constant")

    if not tiffstack:
        hres = zoom(vol, ratios, **kw)
        tiff.imwrite(out_tiff, hres.T if transpose else hres,
                     compression=compression)
        return target

    if vol.ndim != 3:
        raise ValueError("tiffstack requires a 3D volume")

    # order 0 is exact in the native dtype; higher orders would re-quantise the
    # intermediate, so carry those in float and convert once at write time
    work = vol.astype(out_dtype) if spline_order == 0 else vol.astype(np.float32)

    # slice axis first, so each 2D slice is contiguous in the loop below
    work   = np.ascontiguousarray(work.transpose(2, 0, 1))
    z_only = scipy.ndimage.zoom(work, (ratios[2], 1.0, 1.0), **kw)
    assert z_only.shape == (target[2], vol.shape[0], vol.shape[1]), z_only.shape
    del work

    out_dir = Path(out_tiff)
    out_dir.mkdir(parents=True, exist_ok=True)
    info = np.iinfo(out_dtype) if np.issubdtype(out_dtype, np.integer) else None
    pad  = max(6, len(str(target[2] - 1)))

    for k in tqdm(range(target[2])):
        tif_path = out_dir / f"slice_{k:0{pad}d}.tif"
        if tif_path.exists():
            continue                                     # resumable
        tif_slice = scipy.ndimage.zoom(z_only[k], ratios[:2], **kw)
        assert tif_slice.shape == target[:2], tif_slice.shape
        if info is not None and tif_slice.dtype.kind == "f":
            tif_slice = np.clip(np.rint(tif_slice), info.min, info.max)   # splines overshoot
        tif_slice = tif_slice.astype(out_dtype, copy=False)
        tiff.imwrite(tif_path, tif_slice.T if transpose else tif_slice)

    return target

# ---------

# def converttiff2nii(d, i, x, newdata, tifx):
#     """
#     """
#
#     # down ratio
#     down = (1.0 / int(d))
#
#     sys.stdout.write("\r processing slice %d ..." % i)
#     sys.stdout.flush()
#
#     m = cv2.imread(x, -1)
#
#     # nearest neighbour for very large data sets
#     inter = cv2.INTER_CUBIC if tifx < 5000 else cv2.INTER_NEAREST
#
#     newdata[i, :, :] = cv2.resize(m, (0, 0), fx=down, fy=down, interpolation=inter)
#     # data.append(mres)

# ---------

def main(args):
    starttime = datetime.now()

    parser = parsefn()
    input, outtiff, u, s, tiffstack, transpose = parse_inputs(parser, args)

    # convert nii volume to tiff
    print("\n converting NII volume to TIFF")
    print(f"\n transpose = {transpose}")

    convert_nii_to_tiff(input, outtiff, u, s, tiffstack, transpose)

    print("\n conversion done in %s ... Have a good day!\n" % (datetime.now() - starttime))


if __name__ == "__main__":
    main(sys.argv[1:])


# Todos
