#!/usr/bin/env python
# Maged Goubran @ Stanford 2018, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd
from lightning import Lightning
from IPython import embed

def helpmsg():
    return '''

    Creates force graph for CLARITY STA analysis

    Usage: miracl_sta_create_force_graph.py -l [ label stats ] -s [ side ] -o [ out graph ]

    Example: miracl_sta_create_force_graph.py -l  -s

    Arguments (required):

        -l label stats

        -s side (combined or split)

    Optional arguments:

        -o out graph (html format)

        '''


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())

    parser.add_argument('-l', '--label_stats', type=str, help="Label stats", required=True)
    parser.add_argument('-s', '--side', type=str, help="Side", required=True)
    parser.add_argument('-o', '--graph', type=str, help="Out graph")

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    # check pars
    if not os.path.exists(args.label_stats):
        sys.exit('%s does not exist ... please check path and rerun script' % args.label_stats)
    else:
        assert isinstance(args.label_stats, str)
        label_stats = args.label_stats

    assert isinstance(args.side, str)
    side = args.side

    if not args.graph:
        out_graph = 'clarity_brain_mask.html'
    else:
        assert isinstance(args.graph, str)
        out_graph = args.graph

    return label_stats, side, out_graph


# ---------

def force(indf, dic, allengraph, lblid, thr, k, name):
    # force graph
    lgn = Lightning(ipython=True, local=True)

    means = indf.Mean.values
    #means = indf.Sum.values
    zeros = np.zeros((means.shape[0] + 1, means.shape[0] + 1))
    zeros[:-1, -1] = means
    zeros[-1, :-1] = means
    df = pd.DataFrame(zeros)
    lbls = np.append(indf.LabelID.values, lblid)

    lblsdf = pd.DataFrame(lbls)
    lblsdf.columns = ['lbls']
    lblsdf = lblsdf.replace(dic)

    df.columns = lblsdf.lbls.values
    df.index = lblsdf.lbls.values

    # threshold for force graph
    dfthr = df.copy()
    #thrval = indf.Sum.mean() * thr
    thrval = indf.Mean.mean() * thr
    dfthr[dfthr < thrval] = 0

    # drop zeros
    dfthr = dfthr[(dfthr.T != 0).any()]
    dfthr = dfthr.loc[:, (dfthr != 0).any(axis=0)]

    parents = []

    lbls = dfthr.index.values

    # get parent ids
    for l, lbl in enumerate(lbls):

        # path id
        path = allengraph.structure_id_path[allengraph.acronym == lbls[l]]

        # remove /
        numpath = re.sub("[/]", ' ', str(path))

        # get digits
        digpath = [int(s) for s in numpath.split() if s.isdigit()]
        digpath = digpath[1:]  # drop 1st index

        # get great grand parent
        if len(path) == 0:
            parent = allengraph.id[allengraph.acronym == lbls[l]]
            if len(parent) == 0:
                parent = 688
        elif len(digpath) < 3:
            parent = digpath[0]
        else:
            parent = digpath[2]

        parents.append(parent)

    sizes = (dfthr.PL.values + 1) * k
    sizes[-1] = np.max(sizes)

    #     return lgn.force(dfthr,group=parents,labels=dfthr.index.values,values=dfthr.max(),size=sizes,width=2000,height=1500,colormap=cmap)

    #f = lgn.force(dfthr, labels=dfthr.index.values, size=sizes, width=2500, height=1500)
    print(dfthr.index.values)
    f = lgn.force(dfthr, labels=dfthr.index.values, values=dfthr.max(), size=sizes, width=2500, height=1500)
    f.save_html('%s_conn_force.html' % name, overwrite=True)


# ---------

def main(args):
    # parse in args
    parser = parsefn()
    label_stats, side, out_graph = parse_inputs(parser, args)

    miracl_home = os.environ['MIRACL_HOME']

    # allen graph
    allengraph = pd.read_csv('%s/../atlases/ara/ara_mouse_structure_graph_hemi_%s.csv' % (miracl_home, side))
    # export acronynms
    dic = allengraph.set_index('id')['acronym'].to_dict()

    label_df = pd.read_csv(label_stats)
    lblid = label_df.LabelID[0]
    thr = 0.001
    k = 0.5

    # create graph
    force(label_df, dic, allengraph, lblid, thr, k, out_graph)

if __name__ == "__main__":
    main(sys.argv)
