#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import pandas as pd
import numpy as np
import scipy as sp
from scipy import ndimage
from skimage.measure import regionprops
import tifffile as tiff 
from joblib import Parallel, delayed
import multiprocessing
from datetime import datetime
import sys
import os
import argparse


# TODOhp: make sure works on full version

# ---------
# help fn

def helpmsg(name=None): 

    return '''mouse_feat_extract.py -s [segmentation tif] -l [Labels]

    Computes features of segmented image and summarizes them per label

    example: mouse_feat_extract.py -s seg.tif -l allen_annotations.tif
    '''
# ---------
# Get input arguments

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-s','--seg', type=str, help="segmentation tif", required=True)
parser.add_argument('-l','--lbl', type=str, help="label annotations", required=True)

args = parser.parse_args()
inseg = args.seg
inlbls = args.lbl

# ---------

def upsampleswplbls(seg,lbls):

    segx = seg.shape[1]
    segy = seg.shape[2]
    segz = seg.shape[0]

    lblsx = lbls.shape[1]
    lblsy = lbls.shape[2]
    lblsz = lbls.shape[0]

    if segx != lblsx:

        if segx == lblsy:

            print ('Swapping x-y')
            reslbls = np.swapaxes(lbls, 1, 2)
        
        else:

            # rx = float(segx) / lblsy
            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            print('Upsampling labels to clarity resolution')

            # reslbls = sp.ndimage.zoom(lbls,(rz,rx,rx), order=0)
            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

            resx = reslbls.shape[1]

            if segx != resx:
                print ('Swapping x-y')
                reslbls = np.swapaxes(reslbls,1,2)

    else:

        reslbls = lbls

    return reslbls 

# ---------
# Get region prop fn

def computearea(seg,lbls,l):

    sys.stdout.write("\r processing label %d ... " % l)
    sys.stdout.flush()

    # print 'processing label ', l

    lbl = lbls == l
    numvox = np.sum(lbl)
    mask = np.zeros(seg.shape, dtype=np.uint16)
    mask[lbl] = seg[lbl]
    
    if np.max(mask) > 0:
        areas = ( prop.area for prop in regionprops(mask) )
        areas = np.array(list(areas))
        avgarea = np.nanmean(areas)
        stdarea = np.nanstd(areas)
        maxarea = np.nanmax(areas)
        cellnum = len(list(areas))
        celldens = (float(cellnum) / numvox) * 1e3 # assuming 1um res
    else:
        avgarea = 0
        stdarea = 0
        maxarea = 0
        cellnum = 0
        celldens = 0
    
    return avgarea,stdarea,maxarea,cellnum,celldens

# ---------
# Run feat extract for all lbls

def runalllblspar(seg,lbls,ncpus,alllbls):
                
    allprops = Parallel(n_jobs=ncpus, backend='threading')(delayed(computearea)(seg,lbls,l) for i,l in enumerate(alllbls))
    allprops = np.asarray(allprops)
    allareas = allprops[:,0]
    allstdareas = allprops[:,1]
    allmaxareas = allprops[:,2]
    allnums = allprops[:,3]
    alldens = allprops[:,4]
    
    return allareas,allstdareas,allmaxareas,allnums,alldens

# ---------

def getlblvals(lbls):

    flat = np.ndarray.flatten(lbls)
    posflat = flat[flat > 0]
    counts = np.bincount(posflat)

    return np.nonzero(counts)[0]

# ---------
# main fn

def main():

    startTime = datetime.now()

    cpuload = 0.95
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload*cpus) # 80% of cores used

    # open seg
    print ("Reading segmetation")
    seg  = tiff.imread(inseg)

    # open lbls
    print ("Reading labels")
    lbls = tiff.imread(inlbls)

    if (lbls.dtype == np.float64) or (lbls.dtype == np.float32) or (lbls.dtype == np.int32):
        lbls = lbls.astype(np.int16)

    # get all lbls
    alllbls = getlblvals(lbls)

    # upsample or swap if needed
    reslbls = upsampleswplbls(seg,lbls)

    print ("Computing Feature extraction...")
    [allareas,allstdareas,allmaxareas,allnums,alldens] = runalllblspar(seg,reslbls,ncpus,alllbls)
    
    print ('\n Exporting features to csv file')


    miracl_home = os.environ['MIRACL_HOME']

    if np.max(alllbls) > 20000:

        lookup = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    else:

        lookup = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # get attributes
    names = lookup.name[lookup.id.isin(alllbls)]
    abrvs = lookup.acronym[lookup.id.isin(alllbls)]
    parents = lookup.parent_structure_id[lookup.id.isin(alllbls)]
    paths = lookup.structure_id_path[lookup.id.isin(alllbls)]


    # nrows = allareas

    propsdf = pd.DataFrame(
        dict(LabelID=alllbls, LabelAbrv=abrvs, LabelName=names, ParentID=parents, IDPath=paths, Count=allnums,
             Density=alldens, VolumeAvg=allareas, VolumeStd=allstdareas, VolumeMax=allmaxareas))

    cols = ['LabelID','LabelAbrv','LabelName','ParentID','IDPath','Count','Density','VolumeAvg','VolumeStd','VolumeMax']
    propsdf = propsdf[cols]

    propscsv = "clarity_segmentation_features_ara_labels.csv"
    propsdf.to_csv(propscsv)

    print ("\n Features Computation done in %s ... Have a good day!\n" % (datetime.now() - startTime))


if __name__ == "__main__":    
    main()
