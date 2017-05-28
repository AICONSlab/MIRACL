#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import os
import subprocess
import sys

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

Example: miracl_lbls_stats.py -i clarity_downsample_05x_virus_chan.nii.gz -l registered_labels.nii.gz

    Arguments (required):

        -i Input volume

        -l Registered Allen labels

    Optional arguments:

        -o Output file name

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
        parser.add_argument('-o', '--outfile', type=str, help="Output file")

        args = parser.parse_args()

        print("\n running in script mode \n")

        # check if pars given

        assert isinstance(args.invol, str)
        invol = args.invol

        if not os.path.exists(invol):
            sys.exit('%s does not exist ... please check path and rerun script' % invol)

        assert isinstance(args.lbls, str)
        lbls = args.lbls

        if not args.outfile:
            outfile = 'labels_statistics.txt'
        else:
            assert isinstance(args.outfile, str)
            outfile = args.outfile

    return invol, lbls, outfile


# ---------

def main():
    # parse in args
    [invol, lbls, outfile] = parseinputs()

    # extract stats
    print("\n Extracting stats from input volume using registered labels ...\n")

    subprocess.check_call('ImageMaths %s %s > %s' % (invol, lbls, outfile), shell=True,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)

    # read fwf
    outtxt = pd.read_fwf('%s' % outfile)

    # read Allen ontology
    miracl_home = os.environ['MIRACL_HOME']

    annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    # Add label Name, Abrv, PathID

    # make dic
    name_dic = annot_csv.set_index('id')['name'].to_dict()
    acronym_dic = annot_csv.set_index('id')['acronym'].to_dict()
    pathid_dic = annot_csv.set_index('id')['pathid'].to_dict()

    outtxt['name'] = outtxt.LabelID
    outtxt['name'] = outtxt['name'].replace(name_dic)


if __name__ == "__main__":
    main()
