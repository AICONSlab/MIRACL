#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os
import sys

import numpy as np
import pandas as pd


# from IPython.display import HTML, display

def helpmsg():
    return '''miracl_lbls_get_graph_info.py -l [ label id OR label name OR label acronym ]

    Get label info from Allen atlas ontology graph

    example: miracl_lbls_get_graph_info.py -l 672
        OR
            miracl_lbls_get_graph_info.py -l Caudoputamen
        OR
            miracl_lbls_get_graph_info.py -l CP
    '''

def parseargs():
    parser = argparse.ArgumentParser(description='Get lbl info', usage=helpmsg())
    parser.add_argument('-l', '--lbl', help="input label", required=True)

    args = parser.parse_args()

    lbl = args.lbl

    return lbl


def main():
    lbl = parseargs()

    # read graph
    miracl_home = os.environ['MIRACL_HOME']
    arastrctcsv = "%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv" % miracl_home
    aragraph = pd.read_csv(arastrctcsv)

    if np.in1d(lbl, aragraph.id.values):

        lblinfo = aragraph[aragraph.id == int(lbl)]

    else:
        if np.in1d(lbl, aragraph.name.values):
            lblinfo = aragraph[aragraph.name == lbl]
        else:
            lblinfo = aragraph[aragraph.acronym == lbl]

    # print
    # print(lblinfo.to_string(index=False))
    print(lblinfo.T)


if __name__ == "__main__":
    sys.exit(main())
