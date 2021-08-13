import os
import sys
from glob import glob
import nibabel as nib
import dipy
from dipy.io.streamline import load_tractogram, save_tractogram
import argparse


def parsefn():
    p = argparse.ArgumentParser(description="Convert tractograms from TRK to either TCK or VTK.")
    p.add_argument('-t', '--tractogram', required=True, help='input tractogram file')
    p.add_argument('-f', '--force', action="store_true", help='overwrite existing output files')
    p.add_argument('-ot', '--outtype', default='tck', choices=['tck', 'vtk'], help='filetype for output')
    p.add_argument('-o', '--output', help='file name for output')
    return p

def parse_inputs(parser, args):
    tractogram = args.tractogram
    force = args.force
    outtype = args.outtype
    output = args.output if args.output else None

    return tractogram, force, outtype, output


def convert_trk(tractogram, outtype='tck', output=None, force=False):
    ''' Convert presumed trk file to either a tck file, or a vtk file
    '''
    # figure out input type, load file

    if nib.streamlines.detect_format(tractogram) is not nib.streamlines.TrkFile:
        print("Skipping non TRK file: '{}'".format(tractogram))
        return

    if output:
        output_filename = output
    else:
        output_filename = tractogram[:-4] + '.{}'.format(outtype)
        if os.path.isfile(output_filename) and not force:
            print("Skipping existing file: '{}'. Use -f to overwrite.".format(output_filename))
            return

    print("Converting file: {}\n".format(output_filename))
    # load tractogram, set origin to the corner
    trk = load_tractogram(tractogram, reference='same')
    trk.to_corner()  # set origin to the corner
    if  outtype == 'tck':
        save_tractogram(trk, output_filename)
    else:
        dipy.io.vtk.save_vtk_streamlines(trk, output_filename)

def main(args):
    parser = parsefn()
    tractogram, force, outtype, output = parse_inputs(parser, args)
    convert_trk(tractogram, outtype, output, force)

if __name__ == '__main__':
    main(sys.argv)
