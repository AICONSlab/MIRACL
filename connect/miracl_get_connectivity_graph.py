#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import numpy as np
import pandas as pd
import seaborn as sns
import nibabel as nib
import os
import matplotlib.pyplot as plt
from lightning import Lightning
from numpy import random
import argparse

from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache


# TODOhp: multiple exps per label .. what to do?! look through and average?!!

# TODOhp: what if parent has no inj expriment

# ---------
# help fn

def helpmsg():
    return '''miracl_get_connectivity_graph.py -r [input Region Of Interest] -n [number of labels]

    Finds the largest N Allen labels in the Region of Interest and extracts its N closely connected regions
    (targets sorted by normalized projection volume) from the Allen Connectivity atlas.
    Outputs a connectivity matrix of the primary injected sites (labels) & their most common targets.
    Labels and targets are mutually exclusive (a primary injections is not chosen a target & vice versa).
    If a label has no injection experiments, the connectivity atlas is searched for experiments for its parent label.

    example: miracl_get_connectivity_graph.py -r my_roi_mask -n 25
    '''


# ---------
# Get input arguments

def getinpars():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
    parser.add_argument('-r', '--roi', type=str, help="Input ROI", required=True)

    args = parser.parse_args()

    # check if pars given

    if args.pl is None:
        pl = 3
        print("parent level not specified ... choosing default value of %d" % pl)
    else:
        assert isinstance(args.pl, int)
        pl = args.pl

    return pl


# TODOhp: make input either mask or labelid?!

def initialize():
    # type: () -> object
    # input parameters

    # number of select labels inside mask by pixels
    num_out_lbl = 25

    # projection density threshold
    cutoff = 0.0025

    # max label value
    maxannot = 13000  # ignore labels in millions (too small)!

    # read ontology annotation csv

    miracl_home = os.environ['MIRACL_HOME']

    annot_csv = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # read atlas annotations
    atlas_lbls = pd.read_fwf('%s/atlases/ara/annotation/annotation_hemi_combined_10um_labels.txt')

    ## major labels to exclude (ie root,grey,etc) @ depth 0 or 1
    exclude = np.array(annot_csv[(annot_csv['depth'] == 0) | (annot_csv['depth'] == 1)].id)

    return (num_out_lbl, cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude)


# ---------------

# Get 'histogram' of masked labels

def gethist(miracl_home, inmask):
    """ Gets all labels inside input mask
    """

    # read annot labels
    annot_lbls = pd.read_csv('%s/atlases/ara/annotation/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # read input mask
    maskimg = nib.load(inmask)
    maskimg = maskimg.get_data()
    mask = maskimg > 0

    masked_lbls = annot_lbls == mask

    return masked_lbls


# Check if labels have injection exps

def check_inj_exp(masked_lbls, projexps):
    """ Checks if certain label has
    an injection experiment in Allen connect atlas
    """
    inj_exps = np.zeros([masked_lbls.shape[0]])

    for l, lbl in enumerate(masked_lbls):
        # get exp num by searching injection struct
        inj_exps[l] = (projexps['structure-id'] == lbl).any()

    inj_exps = np.asarray(inj_exps).astype(int)

    return inj_exps


# Exclude major lablels

def exlude_maj_lbls(in_lbls, exclude):
    indx = np.in1d(in_lbls, exclude)
    out_lbls = np.delete(in_lbls, np.where(indx == True))

    return out_lbls


# get parent labels for ones w/out inj exp

def get_parentlbl(inj_exps, masked_lbls, annot_csv):
    """ gets parent labels for labels
    without injection experiements in Allen atlas
    """
    masked_lbls_prt = masked_lbls

    for i in range(inj_exps.shape[0]):
        if inj_exps[i] == 0:
            l = masked_lbls[i]
            # get parent label
            pid = annot_csv.parent_structure_id[annot_csv.id == l].values[0]
            masked_lbls_prt[i] = pid

    unq, ind = np.unique(masked_lbls_prt, return_index=True)
    indsort = np.sort(ind)
    uniq_lbls = masked_lbls_prt[indsort]

    uniq_lbls = exlude_maj_lbls(uniq_lbls)

    return uniq_lbls


def query_connect(uniq_lbls, projexps, cutoff, num_out_lbl, exclude, mcc):
    """ Queries the structural connectivity of
    labels inside mask & sorts found labels by projection volume
    """

    all_connect_ids = np.zeros([num_out_lbl, (num_out_lbl * 2 + len(exclude)) + 3])
    all_connect_ids[:, 0] = uniq_lbls.T

    all_norm_proj = np.zeros([num_out_lbl, (num_out_lbl * 2 + len(exclude)) + 3])
    all_norm_proj[:, 0] = uniq_lbls.T

    for l, lbl in enumerate(uniq_lbls):
        # get exp num by searching injection struct
        exp_id = projexps[projexps['structure-id'] == lbl].id.index[0]

        # get exp regions stats
        projection_df = mcc.get_structure_unionizes([exp_id], is_injection=False)

        # TODOhp: check if need to use hemi 3 instead
        # get connected regions
        filter_exp = projection_df.loc[
            (projection_df['normalized_projection_volume'] > cutoff) & (projection_df['hemisphere_id'] != 3)]

        # sort exp values by norm proj volume
        norm_proj = filter_exp.sort_values(['normalized_projection_volume'],
                                           ascending=False).ix[:,
                    ['hemisphere_id', 'structure_id', 'normalized_projection_volume']]
        norm_proj_vol = norm_proj['normalized_projection_volume']

        # distinguish label hemisphere
        orgid = np.array(norm_proj['structure_id'])
        hem = np.array(norm_proj['hemisphere_id'])
        connect_ids = [orgid[i] + 2000 if hem[i] == 1 else orgid[i] for i in range(len(hem))]

        # extract n ids
        all_connect_ids[l, 1:] = connect_ids[0:(num_out_lbl * 2) + len(exclude) + 2]
        all_norm_proj[l, 1:] = norm_proj_vol[0:(num_out_lbl * 2) + len(exclude) + 2]

    return all_connect_ids, all_norm_proj


def saveconncsv(conn_ids, num_out_lbl, annot_csv):
    # save as csv
    export_connect = pd.DataFrame(conn_ids)

    connect_cols = ['connect_lbl_%02d' % (i + 1) for i in range(num_out_lbl)]
    all_cols = ['injection_lbl'] + connect_cols

    export_connect.columns = all_cols
    export_connect.to_csv('connected_ids.csv', index=False)

    # export acronynms
    dic = annot_csv.set_index('id')['acronym'].to_dict()

    export_connect_abv = export_connect.replace(dic)
    export_connect_abv.to_csv('connected_abrvs.csv', index=False)

    return (export_connect_abv, dic)


def exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv):
    # setup projection map
    out_norm_proj = all_norm_proj[:, 1:num_out_lbl + 1]
    names = np.array(export_connect_abv)[:, 0]

    # export projection map (lbls w norm proj volumes along tree)

    sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 1.5})
    plt.figure(figsize=((15, 15)))
    sns.heatmap(out_norm_proj, yticklabels=names,
                cbar_kws={"label": "Normalized projection volume", "orientation": "horizontal"},
                annot=True, fmt=".1f")
    plt.ylabel('Primary injection structures in stroke region')
    plt.xlabel('Target structure order along connection tree')
    plt.savefig('projection_map_along_tree.png', dpi=90)

    # export proj volumes
    norm_proj_df = pd.DataFrame(out_norm_proj)
    norm_proj_df.to_csv('norm_proj_volumes.csv', index=False)

    return out_norm_proj, names


def exportheatmap(num_out_lbl, conn_ids, out_norm_proj, dic, names):
    # setup heat map
    heatmap = np.zeros((num_out_lbl + 1, num_out_lbl + 1))
    heatmap[:-1, 0] = conn_ids[:, 0]

    # get target regions
    # median across structures
    med = np.unique(np.median(conn_ids[:, 1:], axis=0))
    indexes = np.unique(conn_ids[:, 1], return_index=True)[1]
    # 1st connected structures
    first = [conn_ids[:, 1][ix] for ix in sorted(indexes)]
    # combine boths
    inter = np.intersect1d(med, first)
    diff = num_out_lbl - len(med) + len(inter)
    res = first[:diff]
    targ = np.unique(np.hstack([res, med]))

    if len(targ) < num_out_lbl:
        # 1st connected structures
        secindexes = np.unique(conn_ids[:, 2], return_index=True)[1]
        sec = [conn_ids[:, 2][ix] for ix in sorted(secindexes)]
        # combine boths
        sec = np.delete(sec, np.intersect1d(targ, sec))
        targ = np.unique(np.hstack([targ, sec]))

    targ = targ[0:num_out_lbl]
    heatmap[-1, 1:] = targ

    # propagate heat map

    for i in range(len(heatmap) - 1):

        for l, lbl in enumerate(targ):
            heatmap[i, l + 1] = out_norm_proj[i, np.where(conn_ids[i, 1:] == lbl)] if np.sum(
                conn_ids[i, 1:] == lbl) > 0 else 0

    targ = pd.DataFrame(targ)
    targ_abrv = targ.replace(dic)
    targ_abrv = np.array(targ_abrv[0])

    plt.figure(figsize=((15, 15)))
    sns.set_context("poster", font_scale=1.5, rc={"lines.linewidth": 1.5})
    sns.heatmap(heatmap[:-1, 1:], yticklabels=names, xticklabels=targ_abrv,
                cbar_kws={"label": "Normalized projection volume"}, vmax=15, cmap="GnBu", linewidths=.2)
    plt.ylabel('Primary injection structures in stroke region')
    plt.xlabel('Target structures')
    plt.savefig('stroke_region_connectivity_(heat_map)_poster.png', dpi=90)

    return heatmap, targ


def createconnectgraph(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic):
    lgn = Lightning(ipython=True, local=True)

    # create circle connectome
    connections = np.zeros((51, 51))

    connections[1:(num_out_lbl + 1), 0] = uniq_lbls.T
    connections[num_out_lbl + 1:, 0] = targ.T

    connections[0, 1:(num_out_lbl + 1)] = uniq_lbls.T
    connections[0, (num_out_lbl + 1):] = targ.T

    # propagate connections

    alllbls = connections[1:, 0]

    for l, lbl in enumerate(alllbls):

        for t, tart in enumerate(alllbls):
            iind = heatmap[:-1, 0] == lbl
            jind = heatmap[25, :] == tart
            val = heatmap[np.where(iind == True), np.where(jind == True)]

            connections[l + 1, t + 1] = val if val > 0 else 0

    # threshold connections

    thr = 10

    connections[connections < thr] = 0

    # lbls abrv
    alllbls_abrv = pd.DataFrame(alllbls)
    alllbls_abrv = alllbls_abrv.replace(dic)
    alllbls_abrv = np.array(alllbls_abrv[0])

    # get grand parents ids for groups

    ggp_parents = np.array(
        [annot_csv['parent_structure_id'][annot_csv['id'] == lbl].item() for l, lbl in enumerate(alllbls)])

    for i in range(4):
        ggp_parents = [annot_csv['parent_structure_id'][annot_csv['id'] == lbl].item() if (lbl != 997) else 997 for
                       l, lbl
                       in enumerate(ggp_parents)]

    # make dic
    repl = np.unique(ggp_parents)
    np.place(repl, repl > 0, range(len(repl)))
    uniq_parents = np.unique(ggp_parents)
    parents_dic = dict(zip(uniq_parents, repl))

    # replace

    ggp_parents = pd.DataFrame(ggp_parents)
    groups = ggp_parents.replace(parents_dic)

    # connections = random.rand(50,50)
    # connections[connections<0.98] = 0

    group = (random.rand(num_out_lbl * 2) * 3).astype('int')
    # lgn.circle(connections, labels=['group ' + str(x) for x in group], group=group)
    lgn.circle(connections, labels=alllbls_abrv, group=np.array(groups[0]), width=1000, height=1000)


def main():
    # initial pars & read inputs

    [num_out_lbl, cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude] = initialize()

    # Get 'histogram' of masked labels
    print('Getting histogram of included labels in stroke mask & sorting by volume')

    masked_lbls = gethist(miracl_home, )

    # Setup Allen connect jason cache file
    mcc = MouseConnectivityCache(manifest_file='connectivity/manifest.json')
    # Load all injection experiments from Allen api
    all_experiments = mcc.get_experiments(dataframe=True)
    # Filter to only wild-type strain
    projexps = all_experiments[all_experiments['strain'] == "C57BL/6J"]

    # excluding background/negatives
    masked_lbls = exlude_maj_lbls(masked_lbls, exclude)
    masked_lbls = masked_lbls[(masked_lbls > 0) & (masked_lbls < maxannot)]

    # Check if labels have injection exps
    print('Checking if labels have injection experiments in the connectivity search')

    inj_exps = check_inj_exp(masked_lbls, projexps)

    # get parent labels for ones w/out inj exp
    print('Getting parent labels for labels without injection experiments')

    uniq_lbls = get_parentlbl(inj_exps, masked_lbls, annot_csv)

    # check all labels have inj exps
    print('Checking that all parent labels have injection exps')

    inj_exps = check_inj_exp(uniq_lbls, projexps)

    while (len(inj_exps) != sum(inj_exps)):
        uniq_lbls = get_parentlbl(inj_exps, uniq_lbls, annot_csv)
        inj_exps = check_inj_exp(uniq_lbls, projexps)

    # Restrict to n labels
    uniq_lbls = uniq_lbls[0:num_out_lbl]

    # query structure connectivity from Allen API
    print(
    'Quering structural connectivity of injection labels in the Allen connectivity api & sorting by projection volume')

    [all_connect_ids, all_norm_proj] = query_connect(uniq_lbls, projexps, cutoff)

    # excluding major labels @ depth 0 or 1
    all_connect_ids_excl = np.zeros((num_out_lbl, (num_out_lbl * 2) + 3))
    all_connect_ids_excl[:, 0] = uniq_lbls.T

    for i in range(all_connect_ids.shape[0]):
        indx_excl = np.in1d(all_connect_ids[i, 1:], exclude)
        connect_ids_excl = np.delete(all_connect_ids[i, 1:], np.where(indx_excl == True))
        connect_ids_excl = connect_ids_excl[0:(num_out_lbl * 2) + 2]
        all_connect_ids_excl[i, 1:] = connect_ids_excl

    # exclude same lbl if found in its connected regions
    conn = all_connect_ids_excl
    filconn = [np.delete(conn[t, :], np.where(conn[t] == conn[t][0])) for t in range(len(conn))]
    filconn = np.array([filconn[i][0:(num_out_lbl * 2)] for i in range(len(filconn))])

    # exclude labels not included in atlas annotations
    conn_ids = np.zeros((num_out_lbl, num_out_lbl + 1))
    conn_ids[:, 0] = uniq_lbls.T

    for i in range(filconn.shape[0]):
        indx_excl2 = np.in1d(filconn[i, 1:], np.array(atlas_lbls))
        connect_ids_fin = np.delete(filconn[i, 1:], np.where(indx_excl2 == True))
        connect_ids_fin = connect_ids_fin[0:num_out_lbl]
        conn_ids[i, 1:] = connect_ids_fin

    [export_connect_abv, dic] = saveconncsv(conn_ids, num_out_lbl, annot_csv)

    [out_norm_proj, names] = exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv)

    [heatmap, targ] = exportheatmap(num_out_lbl, conn_ids, out_norm_proj, dic, names)

    createconnectgraph(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic)

# TODOlp: view by  nested groups
