#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import argparse
import os

import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import scipy as sp
import seaborn as sns
from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from lightning import Lightning
from scipy import ndimage


# ---------
# help fn

def helpmsg():
    return '''miracl_connect_ROI_matrix_connectogram.py -r [input Region Of Interest] -n [number of labels]

    Finds the largest N Allen labels in the Region of Interest and extracts its N closely connected regions
    (targets sorted by normalized projection volume) from the Allen Connectivity atlas.
    Outputs a connectivity matrix of the primary injected sites (labels) & their most common targets.
    Labels and targets are mutually exclusive (a primary injections is not chosen a target & vice versa).
    If a label has no injection experiments, the connectivity atlas is searched for experiments for its parent label.
    Quering from the Allen API requires an internet connection.

    example: miracl_connect_ROI_matrix_connectogram.py -r my_roi_mask -n 25
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


def initialize():
    # type: () -> object
    # input parameters

    # projection density threshold
    cutoff = 0.001

    # max label value
    maxannot = 13000  # ignore labels in millions (too small)!

    # read ontology annotation csv

    miracl_home = os.environ['MIRACL_HOME']

    annot_csv = pd.read_csv('%s/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    # read atlas annotations
    atlas_lbls = np.loadtxt('%s/ara/annotation/annotation_hemi_split_10um_labels.txt' % miracl_home)

    # major labels to exclude (ie root,grey,etc) @ depth < 5 or grap order < 6
    exclude = np.array(annot_csv[(annot_csv["depth"] < 5) | (annot_csv["graph_order"] < 6)].id)

    return cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude


# ---------------
# Get 'histogram' of masked labels

def gethist(miracl_home, inmask):
    """ Gets all labels inside input mask
    """

    # read annot labels
    print("\n Reading Allen Reference Atlas annoations")
    lbls_file = '%s/ara/annotation/annotation_hemi_combined_25um.nii.gz' % miracl_home
    annot_lbls = nib.load(lbls_file)
    annot_lbls = annot_lbls.get_data()

    # read input mask
    maskimg = nib.load(inmask)
    maskimg = maskimg.get_data()

    # upsample if needed
    if annot_lbls.shape != maskimg.shape:
        anotx = annot_lbls.shape[0]
        maskx = maskimg.shape[0]
        rat = anotx / maskx

        print("\n Upsampling mask to annotation resolution")
        maskimg = sp.ndimage.zoom(maskimg, rat, order=0)

    # binarize
    mask = maskimg > 0

    # get max
    maxlbl = np.max(np.unique(annot_lbls[mask]))

    # get hist
    hist = ndimage.measurements.histogram(annot_lbls, 0, maxlbl, maxlbl, mask)

    # sort by lbl     
    sorthist = np.argsort(hist)

    # flip (larger to smaller)
    masked_lbls = sorthist[::-1]

    # drop empty labels
    fullhist = np.delete(hist, np.where(hist == 0))
    numfull = len(fullhist) - 2

    masked_lbls = masked_lbls[1:numfull]  # & drop 0-background

    # flip again (smaller to larger)
    # masked_lbls = masked_lbls[::-1]

    # print('Included Allen label ids in the input ROI are:')
    # print(masked_lbls)

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

def query_connect(uniq_lbls, projexps, cutoff, exclude, mcc):
    """ Queries the structural connectivity of
    labels inside mask & sorts found labels by normalized projection volume
    """

    all_connect_ids = []
    all_norm_proj = []

    for l, lbl in enumerate(uniq_lbls):
        # get exp num by searching injection struct
        exp_id = projexps[projexps['structure-id'] == lbl].id.index[0]

        # get exp regions stats
        projection_df = mcc.get_structure_unionizes([exp_id], is_injection=False)

        # Should probably do ipsi/contra

        # get connected regions
        filter_exp = projection_df.loc[
            (projection_df['normalized_projection_volume'] > cutoff) & (projection_df['hemisphere_id'] != 3)]

        # sort exp values by norm proj volume
        norm_proj = filter_exp.sort_values(['normalized_projection_volume'], ascending=False).ix[:,
                    ['hemisphere_id', 'structure_id', 'normalized_projection_volume']]
        norm_proj_vol = norm_proj["normalized_projection_volume"]
        all_norm_proj.append(norm_proj_vol)

        # distinguish label hemisphere
        orgid = np.array(norm_proj['structure_id'])
        hem = np.array(norm_proj['hemisphere_id'])
        connect_ids = [orgid[i] + 20000 if hem[i] == 2 else orgid[i] for i in range(len(hem))]

        # filter out labels to exclude
        excl_ids = np.in1d(connect_ids, exclude)
        connect_ids_excl = np.delete(connect_ids, np.where(excl_ids == True))
        all_connect_ids.append(connect_ids_excl)

        # extract n ids

    all_connect_ids = np.array(all_connect_ids)
    all_norm_proj = np.array(all_norm_proj)

    return all_connect_ids, all_norm_proj


# ---------------
# save connected ids & abreviations as csv 

def saveconncsv(conn_ids, annot_csv, num_out_lbl):
    """ Saves connectivity ids (primary structures & targets)
    as a csv file with their ontology atlas ID number
    """

    print("\n Computing & saving connected ids as a csv file")

    # save as csv
    export_connect = pd.DataFrame(conn_ids)

    connect_cols = ['connect_lbl_%02d' % (i + 1) for i in range(export_connect.shape[1] - 1)]
    all_cols = ['injection_lbl'] + connect_cols

    export_connect.columns = all_cols
    export_connect.to_csv('connected_ids_%d_labels.csv' % num_out_lbl, index=False)

    # export acronynms
    dic = annot_csv.set_index('id')['acronym'].to_dict()

    export_connect_abv = export_connect.replace(dic)
    export_connect_abv.to_csv('connected_abrvs_%d_labels.csv' % num_out_lbl, index=False)

    return export_connect_abv, dic


# ---------------
# compute & save projection map 

def exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv):
    """ Generates & saves the projection map of primary structures as png, and
    the projection data as a csv file
    """

    print("\n Computing & saving projection map")

    # setup projection map
    out_norm_proj = [all_norm_proj[i][1:num_out_lbl + 1] for i in range(num_out_lbl)]
    names = np.array(export_connect_abv)[:, 0]

    # export projection map (lbls w norm proj volumes along tree)

    abrv_annot = np.array(export_connect_abv.ix[:, 1:num_out_lbl + 1])
    abrv_annot = pd.DataFrame(abrv_annot).replace(np.nan, ' ', regex=True)

    plt.figure(figsize=(num_out_lbl, num_out_lbl))
    sns.set_context("talk", font_scale=0.5)
    sns.heatmap(out_norm_proj, yticklabels=names, xticklabels=range(1, num_out_lbl + 1),
                cbar_kws={"label": "Normalized projection volume", "orientation": "horizontal"},
                annot=abrv_annot, fmt="s", linewidths=5)

    plt.yticks(rotation=0)

    plt.ylabel('Primary injection structures in region of interest')
    plt.xlabel('Target structure order along connection graph')
    plt.savefig('projection_map_along_graph_%d_labels.png' % num_out_lbl, dpi=300)

    # export proj volumes
    norm_proj_df = pd.DataFrame(out_norm_proj)
    norm_proj_df.to_csv('normalized_projection_volumes_%d_labels.csv' % num_out_lbl, index=False)

    return names


# ---------------
# compute & save connectivity matrix

def exportheatmap(num_out_lbl, conn_ids, all_norm_proj, uniq_lbls, export_connect_abv, dic, names):
    """ Generates & saves the heatmap (connectivity matrix) of primary structures 
    & their common target structures as png
    """

    print("\n Computing & saving the connectivity matrix")

    # make square map
    eps = export_connect_abv.shape[1]

    # conv to array
    conn_ids = [np.array(conn_ids[i][0:eps], dtype=np.float) for i in range(num_out_lbl)]
    # pad conn ids
    conn_ids = [np.pad(conn_ids[i], (0, max(0, eps - len(conn_ids[i]))), 'constant', constant_values=(np.nan,)) for i
                in range(num_out_lbl)]
    conn_ids = np.array(conn_ids, dtype=np.float)

    out_norm_proj = [all_norm_proj[i][:num_out_lbl + 1] for i in range(num_out_lbl)]
    out_norm_proj = np.array(out_norm_proj)

    # setup heat map
    heatmap = np.zeros((num_out_lbl + 1, num_out_lbl + 1))
    heatmap[:-1, 0] = uniq_lbls

    # get target regions

    # get mode across structures (most common)
    temp = np.zeros((num_out_lbl, eps - 1))
    temp[:, :] = conn_ids[:, 1:]
    targ = []
    for i in range(num_out_lbl):
        # mode in 2D
        med = sp.stats.mode(temp, axis=None, nan_policy='omit')[0]
        temp[temp == med] = np.nan
        targ.append(med)

    targ = [targ[i][0] for i in range(num_out_lbl)]

    heatmap[-1, 1:] = targ

    # propagate heat map

    for i in range(len(heatmap) - 1):

        for l, lbl in enumerate(targ):
            heatmap[i, l + 1] = out_norm_proj[i, np.where(conn_ids[i, 1:num_out_lbl] == lbl)] if np.sum(
                conn_ids[i, 1:num_out_lbl] == lbl) > 0 else 0

    targ = pd.DataFrame(targ)
    targ_abrv = targ.replace(dic)
    targ_abrv = np.array(targ_abrv[0])

    plt.figure(figsize=(num_out_lbl / 1.5, num_out_lbl / 1.5))
    sns.set_context("talk", font_scale=0.9)
    sns.heatmap(heatmap[:-1, 1:], yticklabels=names, xticklabels=targ_abrv,
                cbar_kws={"label": "Normalized projection volume"}, vmax=1, cmap="GnBu", linewidths=2)

    plt.xticks(rotation=45)
    plt.yticks(rotation=0)

    plt.ylabel('Primary injection structures in region of interest')
    plt.xlabel('Target structures')
    plt.savefig('connectivity_matrix_heat_map_%d_labels.png' % num_out_lbl, dpi=300)

    return heatmap, targ


# ---------------
# compute & save connectivity graph

def createconnectogram(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic):
    """ Generates & saves the connectome graph of the connectiviy matrix
    """

    print("\n Computing & saving the interactive connectivity graph (connectogram) ")

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
    thr = 0.1
    connections[connections < thr] = 0

    # lbls abrv
    alllbls_abrv = pd.DataFrame(alllbls)
    alllbls_abrv = alllbls_abrv.replace(dic)
    alllbls_abrv = np.array(alllbls_abrv[0])

    # get grand parents ids for groups
    ggp_parents = np.array(
        [annot_csv['parent_structure_id'][annot_csv['id'] == lbl].item() for l, lbl in enumerate(alllbls)])

    parent_grps = ggp_parents

    for i in range(2):
        parent_grps = np.array(
            [annot_csv['parent_structure_id'][annot_csv['id'] == lbl].item() if (lbl != 997) else 997 for
             l, lbl in enumerate(parent_grps)])

    # make dic
    repl = np.unique(ggp_parents)
    np.place(repl, repl > 0, range(len(repl)))
    uniq_parents = np.unique(ggp_parents)
    parents_dic = dict(zip(uniq_parents, repl))

    # replace
    ggp_parents = pd.DataFrame(ggp_parents)
    groups = ggp_parents.replace(parents_dic)
    groups = np.array(groups[0])

    # make dic
    repl2 = np.unique(parent_grps)
    np.place(repl2, repl2 > 0, range(len(repl2)))
    uniq_parents2 = np.unique(parent_grps)
    parents_dic2 = dict(zip(uniq_parents2, repl2))

    parent_grps = pd.DataFrame(parent_grps)
    parent_groups = parent_grps.replace(parents_dic2)
    parent_groups = np.array(parent_groups[0])

    justconn = connections[1:, 1:]

    c = lgn.circle(justconn, labels=alllbls_abrv, group=[parent_groups, groups], width=1000, height=1000)

    c.save_html('connectogram_grouped_by_parent_id_%d_labels.html' % num_out_lbl, overwrite=True)

# ---------------

def main():
    # initial pars & read inputs
    [inmask, num_out_lbl] = getinpars()

    print("\n Reading input mask (ROI) and Allen annotations")

    [cutoff, maxannot, miracl_home, annot_csv, atlas_lbls, exclude] = initialize()

    # Get 'histogram' of masked labels
    print("\n Getting histogram of included labels in mask & sorting by volume")

    masked_lbls = gethist(miracl_home, inmask)

    # Setup Allen connect jason cache file
    mcc = MouseConnectivityCache(
        manifest_file='%s/connect/connectivity_exps/mouse_connectivity_manifest.json' % miracl_home)
    # Load all injection experiments from Allen api
    all_experiments = mcc.get_experiments(dataframe=True)
    # Filter to only wild-type strain
    projexps = all_experiments[all_experiments['strain'] == "C57BL/6J"]
    # no transgenic mice
    projexps = projexps[projexps['transgenic-line'] == ""]

    # excluding background/negatives
    masked_lbls = exlude_maj_lbls(masked_lbls, exclude)
    masked_lbls = masked_lbls[(masked_lbls > 0) & (masked_lbls < maxannot)]

    # Check if labels have injection exps
    print("\n Checking if labels have injection experiments in the connectivity search")

    inj_exps = check_inj_exp(masked_lbls, projexps)

    # get parent labels for ones w/out inj exp
    print("\n Getting parent labels for labels without injection experiments")

    uniq_lbls = get_parentlbl(inj_exps, masked_lbls, annot_csv, exclude)

    # check all labels have inj exps
    print("\n Checking that all parent labels have injection exps")

    inj_exps = check_inj_exp(uniq_lbls, projexps)

    while len(inj_exps) != sum(inj_exps):
        uniq_lbls = get_parentlbl(inj_exps, uniq_lbls, annot_csv, exclude)
        inj_exps = check_inj_exp(uniq_lbls, projexps)

    # Restrict to n labels
    uniq_lbls = uniq_lbls[0:num_out_lbl]

    # query structure connectivity from Allen API
    print("\n Quering structural connectivity of injection labels in the Allen API & sorting by projection volume")

    [all_connect_ids, all_norm_proj] = query_connect(uniq_lbls, projexps, cutoff, exclude, mcc)

    # ---------------

    print("\n Excluding larger 'parent' labels (with graph depth < 5 and graph order < 6)")

    # right injection sites
    uniq_lbls += 20000

    # exclude primary injection if found as a target regions (mutually exclusive)
    filconn = [np.delete(all_connect_ids[t], np.where(np.in1d(all_connect_ids[t], uniq_lbls))) for t in
               range(len(all_connect_ids))]

    # exclude labels not included in atlas annotations
    lblinatl = [np.in1d(filconn[i], atlas_lbls) for i in range(len(filconn))]
    atlfilconn = [np.delete(filconn[i], np.where(lblinatl[i] == False)) for i in range(len(filconn))]

    conn_ids = [np.hstack((uniq_lbls[i], atlfilconn[i])) for i in range(num_out_lbl)]

    # ---------------        

    # save csv     
    [export_connect_abv, dic] = saveconncsv(conn_ids, annot_csv, num_out_lbl)

    # compute & save proj map
    names = exportprojmap(all_norm_proj, num_out_lbl, export_connect_abv)

    # compute & save connectivity matrix
    [heatmap, targ] = exportheatmap(num_out_lbl, conn_ids, all_norm_proj, uniq_lbls, export_connect_abv, dic, names)

    # compute & save connectivity graph
    createconnectogram(num_out_lbl, heatmap, annot_csv, uniq_lbls, targ, dic)

# Call main function
if __name__ == "__main__":
    main()

    # TODOs:
    # TODOhp: make input either mask or labelid?!

    # TODOlp: multiple exps per label .. what to do?! look through and average?!!
    # TODOlp : interactive heatmap with cursor (bookeh or lightning)
    # TODOlp : add weighting for connectogram & maybe interactive numbers/groups & force (another conn) graph
