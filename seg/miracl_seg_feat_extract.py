#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import pandas as pd
import numpy as np
from skimage.measure import regionprops
import tifffile as tiff 
from joblib import Parallel, delayed
import multiprocessing
from datetime import datetime
import sys
import argparse

# ---------
# help fn

def helpmsg(name=None): 

    return '''mouse_feat_extract.py -s [segmentation tif] -l [Labels]

    Computes features of segmented image

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
# Get region prop fn

def computearea(seg,lbls,l):

    sys.stdout.write("\r processing label %d ... " % l)
    sys.stdout.flush()

    # print 'processing label ', l

    lbl = lbls == l
    numvox = np.sum(lbl)
    mask = np.zeros((seg.shape),dtype=np.uint16)
    mask[lbl] = seg[lbl]
    
    if np.max(mask) > 0:
        areas = ( prop.area for prop in regionprops(mask) )
        areas = np.array(list(areas))
        avgarea = np.nanmean(areas)
        stdarea = np.nanstd(areas)
        maxarea = np.nanmax(areas)
        cellnum = len(list(areas))
        celldens = (float(cellnum) / numvox) * 1e9 # assuming 1um res
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
                
    allprops = Parallel(n_jobs=ncpus,backend='threading')(delayed(computearea)(seg,lbls,l) for i,l in enumerate(alllbls))
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
    posflat = flat [flat > 0 ]
    counts = np.bincount(posflat)

    return np.nonzero(counts)[0]

# ---------
# main fn

def main():

    startTime = datetime.now()

    cpuload = 0.8
    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload*cpus) # 80% of cores used

    # open seg
    print ("Reading segmetation")
    seg  = tiff.imread(inseg)

    # open lbls
    print ("Reading labels")
    lbls = tiff.imread(inlbls)
    lbls = lbls.astype(np.uint16)

    # get all lbls
    alllbls = getlblvals(lbls)

    print ("Computing Feature extraction...")
    [allareas,allstdareas,allmaxareas,allnums,alldens] = runalllblspar(seg,lbls,ncpus,alllbls)
    
    print ('\n Exporting features to csv file')

    # lookup=pd.read_csv('/data/clarity_project/atlases/allen/annotations/allen_annot_lbls.csv')

    nrows = allareas 

    propsdf = pd.DataFrame({'LabelID' : alllbls,
                            'Count' : allnums,
                            'Density' : alldens,                            
                            'VolumeAvg' : allareas,
                            'VolumeStd': allstdareas,
                            'VolumeMax': allmaxareas})

    cols = ['LabelID','Count','Density','VolumeAvg','VolumeStd','VolumeMax']
    propsdf = propsdf[cols]

    propscsv = 'clarity_segmentation_features.csv'    
    propsdf.to_csv(propscsv)

    print ("\n Features Computation done in %s ... Have a good day!\n" % (datetime.now() - startTime)) 

if __name__ == "__main__":    
    main()
