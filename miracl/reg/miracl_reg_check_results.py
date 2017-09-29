#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import commands
import os
import subprocess
import sys


def helpmsg():
    return '''Usage: miracl_reg_check_results.py 

checks registration results

    A GUI will open to choose your:

        - < reg final dir > : directory with final registration volumes and labels

    ----------

    For command-line / scripting

    Usage: miracl_reg_check_results.py -f [reg final folder] -v [visualization software] -s [reg space (clarity or
    allen)]

Example: miracl_convertTifftoNii.py -f reg_final -v itk -s clarity

    Arguments (required):

        -f Input final registration folder

    Optional arguments:

        -v Visualization software: itkSNAP 'itk' (default) or freeview 'free'
        -s Registration Space of results: clarity (default) or allen

        '''


# Dependencies:
#
#    Python 2.7, itksnap or freeview

def parseinputs():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    if len(sys.argv) == 1:

        print("Running in GUI mode")

        miracl_home = os.environ['MIRACL_HOME']

        indirstr = subprocess.check_output(
            '%s/io/miracl_io_file_folder_gui.py -f %s -s %s' % (miracl_home, 'folder', '"Please open reg final dir"'),
            shell=True,
            stderr=subprocess.PIPE)
        indir = indirstr.split(":")[1].lstrip().rstrip()

        # args = parser.parse_args()
        viz = 'itk'
        space = 'clarity'

    else:

        print("\n running in script mode \n")

        # check if pars given
        parser.add_argument('-f', '--folder', type=str, help="reg final folder", required=True)
        parser.add_argument('-v', '--viz', type=str, help="Visualization software")
        parser.add_argument('-s', '--space', type=str, help="Registration Space")

        args = parser.parse_args()

        assert isinstance(args.folder, str)
        indir = args.folder

        if not os.path.exists(indir):
            sys.exit('%s does not exist ... please check path and rerun script' % indir)

        if args.viz is None:
            viz = 'itk'
            print("\n software not specified ... choosing itkSNAP")
        else:
            assert isinstance(args.viz, str)
            viz = args.viz

        if args.space is None:
            space = 'clarity'
            print("\n registration space not specified ... choosing clarity space")
        else:
            assert isinstance(args.space, str)
            space = args.space

    return indir, viz, space


# ---------

def main():
    [indir, viz, space] = parseinputs()

    if viz == "itk":

        # check for itk
        status, result = commands.getstatusoutput("which itksnap")

        if status == 256:
            print('\n itkSNAP is not installed or not in your path! \n')
            sys.exit()

        if space == "clarity":

            print("\n Viewing downsampled CLARITY volume with registered Allen labels using itkSNAP ...\n")

            subprocess.check_call(
                'itksnap -g %s/clar_downsample_res??um.nii.gz -s %s/annotation_hemi_combined_??um_clar_downsample.nii.gz -l $snaplut' % (
                indir, indir), shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        else:

            # get res
            # name = str(glob.glob("%s/clar_downsample_res??um.nii.gz" % indir))
            # res = int(filter(str.isdigit, name))
            res = 10

            print("\n Viewing registered CLARITY volume in Allen space with labels using itkSNAP ...\n")

            subprocess.check_call(
                'itksnap -g %s/clar_allen_space.nii.gz -o $allen%d -s $lbls%d -l $snaplut' % (indir, res, res),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

    else:

        status, result = commands.getstatusoutput("which freeview")

        if status == 256:
            print('\n Freeview (from FREESURFER) is not installed or not in your path! \n')
            sys.exit()

        if space == "clarity":

            print("\n Viewing downsampled CLARITY volume with registered Allen labels using Freeview ...\n")

            # w lut not working
            # 'freeview -v %s/clar_downsample_res??um.nii.gz -v %s/annotation_hemi_combined_??um_clar_downsample.nii.gz:lut=$freelut'

            subprocess.check_call(
                'freeview -v %s/clar_downsample_res??um.nii.gz -v %s/annotation_hemi_combined_??um_clar_downsample.nii.gz'
                % (indir, indir), shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        else:

            print("\n Viewing registered CLARITY volume in Allen space with labels using Freeview ...\n")

            subprocess.check_call(
                'freeview -v %s/clar_allen_space.nii.gz -v $allen25 -v $lbls25' % indir,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)


if __name__ == "__main__":
    main()
