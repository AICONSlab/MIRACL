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

# ---------
# help fn

def helpmsg():
    return '''miracl_get_connectivity_graph.py -r [input Region Of Interest] -n [number of labels]

    Finds the largest N Allen labels in the Region of Interest and extracts its N closely connected regions
    (targets sorted by normalized projection volume) from the Allen Connectivity atlas.
    Outputs a connectivity matrix of the primary injected sites (labels) & their most common targets.
    Labels and targets are mutually exclusive (a primary injections is not chosen a target & vice versa).
    If a label has no injection experiments, the connectivity atlas is searched for experiments for its parent label.
    Quering from the Allen API requires an internet connection.

    example: miracl_get_connectivity_graph.py -r my_roi_mask -n 21
    '''

# ---------
# Get input arguments

def getinpars():
    parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
    parser.add_argument('-r', '--roi', type=str, help="Input ROI", required=True)
    parser.add_argument('-n', '--numlbl', type=int, help="Number of primary labels", required=True)

    args = parser.parse_args()

    # check if pars given

    assert isinstance(args.roi, str)
    inmask = args.roi

    # number of select labels inside mask by pixels
    assert isinstance(args.numlbl, int)
    num_out_lbl = args.numlbl

    return inmask, num_out_lbl


# TODOhp: make input either mask or labelid?!

def initialize():
    # type: () -> object
    # input parameters

    # projection density threshold
    cutoff = 0.0025

    # max label value
    maxannot = 13000  # ignore labels in millions (too small)!

    # read ontology annotation csv

    miracl_home = '/Users/mgoubran/workspace/clarity_Project'

    annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # read atlas annotations
    atlas_lbls = np.loadtxt('%s/ara/annotation/annotation_hemi_combined_10um_labels.txt' % miracl_home)

    # major labels to exclude (ie root,grey,etc) @ depth < 3 or grap order < 6
    exclude = np.array(annot_csv[(annot_csv['depth'] < 3) | (annot_csv['graph_order'] < 6)].id)

    return cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude


# ---------------
# Get 'histogram' of masked labels

def gethist(miracl_home, inmask):
    """ Gets all labels inside input mask
    """

    # read annot labels
    lbls_file = '%s/ara/annotation/annotation_hemi_combined_25um.nii.gz' % miracl_home
    annot_lbls = nib.load(lbls_file)
    annot_lbls = annot_lbls.get_data()

    # read input mask
    maskimg = nib.load(inmask)
    maskimg = maskimg.get_data()
    # binarize
    mask = maskimg > 0

    masked_lbls = np.unique(annot_lbls[mask])
    masked_lbls = masked_lbls[masked_lbls > 0]

    print('Included Allen label ids in the input ROI are:')
    print(masked_lbls)

    return masked_lbls


# ---------------
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


# ---------------
# Exclude major lablels

def exlude_maj_lbls(in_lbls, exclude):
    """ excludes major labels at shallow depths (in the Allen 
    structure ontology graph) from the connectivity analysis
    """

    indx = np.in1d(in_lbls, exclude)
    out_lbls = np.delete(in_lbls, np.where(indx == True))

    return out_lbls


# ---------------
# get parent labels for ones w/out inj exp

def get_parentlbl(inj_exps, masked_lbls, annot_csv, exclude):
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

    uniq_lbls = exlude_maj_lbls(uniq_lbls, exclude)

    return uniq_lbls


# ---------------
# Query Allen API

def query_connect(uniq_lbls, projexps, cutoff, num_out_lbl, exclude, mcc):
    """ Queries the structural connectivity of
    labels inside mask & sorts found labels by normalized projection volume
    """

    all_connect_ids = np.zeros([num_out_lbl, (num_out_lbl * 3) + 1])
    all_connect_ids[:, 0] = uniq_lbls.T

    all_norm_proj = np.zeros([num_out_lbl, (num_out_lbl * 3) + 1])
    all_norm_proj[:, 0] = uniq_lbls.T

    for l, lbl in enumerate(uniq_lbls):
        # get exp num by searching injection struct
        exp_id = projexps[projexps['structure-id'] == lbl].id.index[0]

        # get exp regions stats
        projection_df = mcc.get_structure_unionizes([exp_id], is_injection=False)

        # get connected regions
        filter_exp = projection_df.loc[
            (projection_df['normalized_projection_volume'] > cutoff) & (projection_df['hemisphere_id'] == 3)]

        # sort exp values by norm proj volume
        norm_proj = filter_exp.sort_values(['normalized_projection_volume'],
                                           ascending=False).ix[:,
                    ['hemisphere_id', 'structure_id', 'normalized_projection_volume']]
        norm_proj_vol = norm_proj['normalized_projection_volume']

        # TODOhp: How to figure out which hemi 
        # distinguish label hemisphere
        orgid = np.array(norm_proj['structure_id'])
        hem = np.array(norm_proj['hemisphere_id'])
        connect_ids = [orgid[i] + 20000 if hem[i] == 1 else orgid[i] for i in range(len(hem))]

        # filter out labels to exclude
        excl_ids = np.in1d(connect_ids, exclude)
        connect_ids_excl = np.delete(connect_ids, np.where(excl_ids == True))

        # extract n ids
        all_connect_ids[l, 1:] = connect_ids_excl[0:(num_out_lbl * 3)]
        all_norm_proj[l, 1:] = norm_proj_vol[0:(num_out_lbl * 3)]

    return all_connect_ids, all_norm_proj


# ---------------
# save connected ids & abreviations as csv 

def saveconncsv(conn_ids, num_out_lbl, annot_csv):
    """ Saves connectivity ids (primary structures & targets)
    as a csv file with their ontology atlas ID number
    """

    print('Computing & saving connected ids as a csv file')    

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

    return export_connect_abv, dic


# ---------------
# compute & save projection map 

def exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv):
    """ Generates & saves the projection map of primary structures as png, and
    the projection data as a csv file
    """

    print('Computing & saving projection map')    

    # setup projection map
    out_norm_proj = all_norm_proj[:, 1:num_out_lbl + 1]
    names = np.array(export_connect_abv)[:, 0]

    # export projection map (lbls w norm proj volumes along tree)

    plt.figure(figsize=(15, 15))
    sns.set_context("talk", font_scale=1.1, rc={"lines.linewidth": 1.1})    
    sns.heatmap(out_norm_proj, yticklabels=names,
                cbar_kws={"label": "Normalized projection volume", "orientation": "horizontal"},
                annot=True, fmt=".1f")
    plt.ylabel('Primary injection structures in stroke region')
    plt.xlabel('Target structure order along connection graph')
    plt.savefig('projection_map_along_graph.png', dpi=90)

    # export proj volumes
    norm_proj_df = pd.DataFrame(out_norm_proj)
    norm_proj_df.to_csv('normalized_projection_volumes.csv', index=False)

    return out_norm_proj, names


# ---------------
# compute & save connectivity matrix

def exportheatmap(num_out_lbl, conn_ids, out_norm_proj, dic, names):
    """ Generates & saves the heatmap (connectivity matrix) of primary structures 
    & their common target structures as png
    """

    print('Computing & saving the connectivity matrix')    

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

    plt.figure(figsize=(15, 15))
    # sns.set_context("talk", font_scale=1.1, rc={"lines.linewidth": 1.1})
    sns.set_context("talk", font_scale=1.1)
    sns.heatmap(heatmap[:-1, 1:], yticklabels=names, xticklabels=targ_abrv,
                cbar_kws={"label": "Normalized projection volume"}, vmax=15, cmap="GnBu", linewidths=.1)
    plt.ylabel('Primary injection structures in stroke region')
    plt.xlabel('Target structures')
    plt.savefig('connectivity_matrix_heat_map.png', dpi=90)

    return heatmap, targ


# ---------------
# compute & save connectivity graph

def createconnectogram(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic):
    """ Generates & saves the connectome graph of the connectiviy matrix
    """

    print('Computing & saving the connectivity graph')

    lgn = Lightning(ipython=True, local=True)

    # create circle connectome
    connections = np.zeros(((2 * num_out_lbl) + 1, (2 * num_out_lbl) + 1))

    connections[1:(num_out_lbl + 1), 0] = uniq_lbls.T
    connections[num_out_lbl + 1:, 0] = targ.T

    connections[0, 1:(num_out_lbl + 1)] = uniq_lbls.T
    connections[0, (num_out_lbl + 1):] = targ.T

    # propagate connections

    alllbls = connections[1:, 0]

    for l, lbl in enumerate(alllbls):

        for t, tart in enumerate(alllbls):
            iind = heatmap[:-1, 0] == lbl
            jind = heatmap[num_out_lbl, :] == tart
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
                       l, lbl in enumerate(ggp_parents)]

    # make dic
    repl = np.unique(ggp_parents)
    np.place(repl, repl > 0, range(len(repl)))
    uniq_parents = np.unique(ggp_parents)
    parents_dic = dict(zip(uniq_parents, repl))

    # replace
    ggp_parents = pd.DataFrame(ggp_parents)
    groups = ggp_parents.replace(parents_dic)

    c = lgn.circle(connections, labels=alllbls_abrv, group=np.array(groups[0]), width=1000, height=1000)

    c.save_html('connectogram_grouped_by_parent_id.html', overwrite=True)


# ---------------

def main():

    # initial pars & read inputs
    [inmask, num_out_lbl] = getinpars()

    print('Reading input mask (ROI) and Allen annotations')

    [cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude] = initialize()

    # Get 'histogram' of masked labels
    print('Getting histogram of included labels in mask & sorting by volume')

    masked_lbls = gethist(miracl_home, inmask)
    
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

    uniq_lbls = get_parentlbl(inj_exps, masked_lbls, annot_csv, exclude)

    # check all labels have inj exps
    print('Checking that all parent labels have injection exps')

    inj_exps = check_inj_exp(uniq_lbls, projexps)

    while (len(inj_exps) != sum(inj_exps)):
        uniq_lbls = get_parentlbl(inj_exps, uniq_lbls, annot_csv, exclude)
        inj_exps = check_inj_exp(uniq_lbls, projexps)

    # Restrict to n labels
    uniq_lbls = uniq_lbls[0:num_out_lbl]

    # query structure connectivity from Allen API
    print(
    'Quering structural connectivity of injection labels in the Allen connectivity api & sorting by projection volume')

    [all_connect_ids, all_norm_proj] = query_connect(uniq_lbls, projexps, cutoff, num_out_lbl, exclude, mcc)

    # ---------------

    # exclude primary injection if found as a target regions (mutually exclusive) 
    filconn = [np.delete(all_connect_ids[t, :], np.where(np.in1d(all_connect_ids[t, :], uniq_lbls))) for t in
               range(len(all_connect_ids))]

    # exclude labels not included in atlas annotations
    lblinatl = [np.in1d(filconn[i], atlas_lbls) for i in range(len(filconn))]
    atlfilconn = [np.delete(filconn[i], np.where(lblinatl == False)) for i in range(len(filconn))]
    atlfilconn = np.array([atlfilconn[a][0:num_out_lbl] for a in range(len(atlfilconn))])

    # combine with primary injections
    primar = np.reshape(uniq_lbls, [num_out_lbl, 1])
    conn_ids = np.hstack((primar, atlfilconn))

    # allfil = np.hstack((uniq_lbls, atlas_lbls))

    # print(allfil)

    # filconn = [np.delete(all_connect_ids[t, :], np.where(np.in1d(all_connect_ids[t,:], allfil))) for t in range(len(all_connect_ids))]

    # # exctract only num out lbls
    # numfilconn = np.array([filconn[a][0:num_out_lbl] for a in range(len(filconn))])

    # # combine with primary injections
    # primar = np.reshape(uniq_lbls,[num_out_lbl,1])

    # print (all_connect_ids.shape)
    # # print (filconn.shape)
    # print (numfilconn.shape)
    # print (primar.shape)

    # ---------------        

    # save csv     
    [export_connect_abv, dic] = saveconncsv(conn_ids, num_out_lbl, annot_csv)

    # compute & save proj map
    [out_norm_proj, names] = exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv)

    # compute & save connectivity matrix
    [heatmap, targ] = exportheatmap(num_out_lbl, conn_ids, out_norm_proj, dic, names)

    # compute & save connectivity graph
    createconnectogram(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic)

# TODOlp: view by  nested groups

# Call main function
if __name__ == "__main__":
    main()
