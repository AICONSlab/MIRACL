#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import subprocess
import sys

import numpy as np
import pandas as pd


# import commands

def helpmsg():
    return '''Usage: miracl_lbls_stats.py 

Computes Allen label stats of input volume 

    A GUI will open to choose your:

        - < input volume > 

        - < registered Allen labels >

    ----------

    For command-line / scripting

    Usage: miracl_lbls_stats.py -i [input volume] -l [reg Allen labels]

Example: miracl_lbls_stats.py -i clarity_downsample_05x_virus_chan.nii.gz -l registered_labels.nii.gz -o label_stats.csv -s Count

    Arguments (required):

        -i Input volume

        -l Registered Allen labels

    Optional arguments:

        -o Output file name

        -s Sort values by, options are:

            Mean or StdD or Max or Min or Count or Vol(mm^3)

            Mean -> mean intensity values
            Count -> number of voxels

        '''

    # Dependencies:

    #     ImageMaths (ANTs)
    #     Python 2.7


def parseinputs():
    if len(sys.argv) == 1:

        print("Running in GUI mode")

    else:

        parser = argparse.ArgumentParser(description='', usage=helpmsg())

        parser.add_argument('-i', '--invol', type=str, help="In volume", required=True)
        parser.add_argument('-l', '--lbls', type=str, help="Reg lbls", required=True)
        parser.add_argument('-s', '--sort', type=str, help="Sort by", default='Mean')
        parser.add_argument('-o', '--outfile', type=str, help="Output file",
                            default='virus_signal_label_statistics.csv')

        args = parser.parse_args()

    return args


# ---------

def main():
    # parse in args

    args = parseinputs()

    print("\n running in script mode \n")

    # check if pars given
    assert isinstance(args.invol, str)
    invol = args.invol
    assert os.path.exists(invol), '%s does not exist ... please check path and rerun script' % invol

    assert isinstance(args.lbls, str)
    lbls = args.lbls
    assert os.path.exists(lbls), '%s does not exist ... please check path and rerun script' % lbls

    assert isinstance(args.outfile, str)
    assert isinstance(args.sort, str)

    # extract stats
    print(" Extracting stats from input volume using registered labels ...\n")

    # subprocess.check_call('ImageIntensityStatistics 3 %s %s > %s' % (invol, lbls, outfile), shell=True,
    #                       stdout=subprocess.PIPE,
    #                       stderr=subprocess.PIPE)

    subprocess.check_call('c3d %s %s -lstat > %s' % (invol, lbls, args.outfile), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    # read fwf
    outtxt = pd.read_fwf('%s' % args.outfile)

    # read Allen ontology
    miracl_home = os.environ['MIRACL_HOME']

    annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    # Add label Name, Abrv, PathID

    # make dic
    name_dict = annot_csv.set_index('id')['name'].to_dict()
    acronym_dict = annot_csv.set_index('id')['acronym'].to_dict()
    pathid_dict = annot_csv.set_index('id')['structure_id_path'].to_dict()
    parent_dict = annot_csv.set_index('id')['parent_structure_id'].to_dict()

    # replace label info
    outtxt['name'] = outtxt.LabelID.replace(name_dict)
    outtxt['acronym'] = outtxt.LabelID.replace(acronym_dict)
    outtxt['parent'] = outtxt.LabelID.replace(parent_dict)
    outtxt['pathid'] = outtxt.LabelID.replace(pathid_dict)

    # sort data-frame
    outtxt = outtxt.sort_values([args.sort], ascending=False)
    # remove background
    outtxt = outtxt[outtxt['LabelID'] != 0]

    # re-oder columns with info then sorted column of choice
    cols = ['LabelID', 'acronym', 'name', 'parent', args.sort]
    dfcols = outtxt.columns.values
    allcols = np.hstack([cols, dfcols])
    _, idx = np.unique(allcols, return_index=True)
    columns = allcols[np.sort(idx)]

    outtxt = outtxt[columns]

    # save to csv
    outtxt.to_csv('%s' % args.outfile, index=False)


if __name__ == "__main__":
    main()
