#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import commands
import os
import subprocess
import sys


def helpmsg(name=None):
    return '''Usage: miracl_reg_check_results.py 

Converts Tiff images to Nifti 

    A GUI will open to choose your:

        - < reg final dir > : directory with final registration volumes and labels

    ----------

    For command-line / scripting

    Usage: miracl_reg_check_results.py -f [reg final folder] -v [visualization software] -s [reg space (clarity or allen)]

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

    if len(sys.argv) == 1:

        print("Running in GUI mode")



    else:

        parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())

        parser.add_argument('-f', '--folder', type=str, help="reg final folder", required=True)
        parser.add_argument('-v', '--viz', type=str, help="Visualization software")
        parser.add_argument('-s', '--space', type=str, help="Registration Space")

        args = parser.parse_args()

        print("\n running in script mode \n")

        # check if pars given

        assert isinstance(args.folder, str)
        indir = args.folder

        if not os.path.exists(indir):
            sys.exit('%s does not exist ... please check path and rerun script' % indir)

        if args.viz is None:
            viz = 'itk'
            print("\n software not specified ... choosing itkSNAP")
        else:
            assert isinstance(args.outnii, str)
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
                indir, indir),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)


        else:

            print("\n Viewing registered CLARITY volume in Allen space with labels using itkSNAP ...\n")

            subprocess.check_call(
                'itksnap -g %s/clar_downsample_res??um.nii.gz -s %s/annotation_hemi_combined_??um_clar_downsample.nii.gz -l $snaplut' % (
                indir, indir),
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

            subprocess.check_call(
                'itksnap -g %s/clar_downsample_res??um.nii.gz -s %s/annotation_hemi_combined_??um_clar_downsample.nii.gz -l $snaplut' % (
                indir, indir),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        else:

            print("\n Viewing registered CLARITY volume in Allen space with labels using Freeview ...\n")

            subprocess.check_call(
                'itksnap -g %s/clar_downsample_res??um.nii.gz -s %s/annotation_hemi_combined_??um_clar_downsample.nii.gz -l $snaplut' % (
                indir, indir),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)


if __name__ == "__main__":
    main()
