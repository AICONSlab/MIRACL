#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os
import sys
import numpy as np
import pandas as pd

from miracl import ATLAS_DIR


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


def parsefn():
    parser = argparse.ArgumentParser(description='Get lbl info', usage=helpmsg())
    parser.add_argument('-l', '--lbl', help="input label", required=True)

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    lbl = args.lbl

    return lbl


def main(args):
    parser = parsefn()
    lbl = parse_inputs(parser, args)

    # read graph
    arastrctcsv = "%s/ara/ara_mouse_structure_graph_hemi_combined.csv" % ATLAS_DIR
    aragraph = pd.read_csv(arastrctcsv)

    try:  # get the data from the atlas, exit if the label doesnt match
        if isinstance(lbl, int) and int(lbl) in aragraph.id.values:
            lblinfo = aragraph[aragraph.id == int(lbl)]
        elif lbl in aragraph.name.values:
            lblinfo = aragraph[aragraph.name == lbl]
        elif lbl in aragraph.acronym.values:
            lblinfo = aragraph[aragraph.acronym == lbl]
        else:
            raise ValueError('Error: {} is not a label id, label name, OR label acronym. Please consult {} to see possible values\n'.format(lbl, arastrctcsv))
    except Exception as e:
        exit(e)
        #exit('Could not complete request.')

    # print
    # print(lblinfo.to_string(index=False))
    print(lblinfo.T)


if __name__ == "__main__":
    main(sys.argv)
