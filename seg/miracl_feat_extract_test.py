#!/usr/bin/env python
# Maged Goubran @ 2015, mgoubran@stanford.edu 

print "\n Extracting features from Clarity segmentations \n"

import pandas as pd
import numpy as np
import nibabel as nib
from skimage.measure import regionprops
import scipy as sp
import sys
import glob
from joblib import Parallel, delayed
import multiprocessing
import warnings 
import os
from datetime import datetime
import tifffile as tiff

startTime = datetime.now()

# load segmentation 
seg = tiff.imread("seg.tif") 
# convert seg to uint8
seg=np.uint16(seg)

print '\n seg shape is', seg.shape

#load label image
regdir='%s/reg/clar_allen' % subjdir

print "\n Reading Allen atlas labels \n"

lblnii=nib.load('%s/allen_gp-lbls_clar_ants_ort_cras.nii.gz' % regdir) 
orglbl=lblnii.get_data()

# why again (orient issue?)
print " Upsampling labels to Clarity resolution \n"

# upsample label
reslbl=sp.ndimage.zoom(orglbl, 10, order=0)

# swap dims
lbl=np.swapaxes(reslbl,0,1)
lbl=np.uint16(lbl)

## ----------------------
#  Feats per label Fn

def ComputeLabel(segslice,lblslice,l,labels,areas,perims,orients,eccents):

    # skip zero label
    l=l+1

    idx=lblslice==l
    allints=segslice[idx]
    ints=np.unique(allints)
    ints=ints[1:]

    nareas = areas[np.where(np.in1d(labels,ints))]
    nareas = nareas.astype(np.int16)

    avgarea=np.mean(nareas) if len(nareas) > 0 else 0

    count=len(nareas)
        
    return (avgarea,count,avgperim,avgorient,avgeccent)

## ----------------------
#  Feats per Slice Fn

# expect to see RuntimeWarnings 
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)


def ComputeSlice(seg,lbl,i):

    sys.stdout.write("\r Computing features for slice %d ..." % i)
    sys.stdout.flush()

    segslice=seg[:,:,i]
    lblslice=lbl[:,:,i]
    
    proper = []
    proper = regionprops(segslice)  

    properties = []
    properties.append(proper)

    areas=np.zeros(len(proper),dtype=np.int16)

    a = 0

    for prop in properties[0]:
        
        a=a+1
        
        areas[a-1]=prop.area

    res = Parallel(n_jobs=38, max_nbytes='500M', pre_dispatch='4 * n_jobs', backend='threading')(delayed(ComputeLabel)(segslice,lblslice,l,labels,areas,perims,orients,eccents) for l in range(nlbls))
        
    return res

## ----------------------
# Run region prop Fn in Parallel over cpu cores

from joblib import Parallel, delayed

nslices=seg.shape[2]

nlbls=3143


res = Parallel(n_jobs=38, max_nbytes='500M', pre_dispatch='4 * n_jobs', backend='threading')(delayed(ComputeSlice)(seg,lbl,i) for i in range(nslices))

print '\n Done Region Prop calculation'

allarray = np.array(res)

allareas = allarray[:,:,0]
allcounts = allarray[:,:,1]

allareas[np.where(allareas == 0)] = np.nan

mareas=np.nanmean(allareas,axis=0)
mcounts=np.sum(allcounts,axis=0)

mareas=np.nan_to_num(mareas)

## ----------------------

# output feats as df

print "\n Exporting features to csv file \n"

outdf = pd.DataFrame({ 'LabelName': pd.Series(np.nan,index=range(nlbls)),                         
                       'LabelAbrv' : pd.Series(np.nan,index=range(nlbls)), 
                       'LabelID' : np.zeros(nlbls),
                       'ParentID' : np.zeros(nlbls), 
                       'IDPath' : pd.Series(np.nan,index=range(nlbls)), 
                       'Counts' : np.zeros(nlbls), 
                       'Areas' : np.zeros(nlbls),
                       'Perims' : np.zeros(nlbls),  
                       'Orients' : np.zeros(nlbls),
                       'Eccents': np.zeros(nlbls) })

cols = ['LabelName','LabelAbrv','ParentID','IDPath','LabelID','Counts','Areas','Perims','Orients','Eccents']
outdf=outdf[cols]


# Export values with label names and abreviations

lookup=pd.read_csv('/data/clarity_project/atlases/allen/annotations/allen_annot_lbls.csv')


pd.options.mode.chained_assignment = None

for n in range(nlbls):

    n=n+1
    
    lenname=len(lookup.name[lookup.id==n])
    
    # skip empty rows -- labels don't increase sequentially
    if (lenname==0):
        continue

    outdf.LabelName[n] = lookup.name[lookup.id==n].values[0]  #if lenname > 0 else []       
    outdf.LabelAbrv[n] = lookup.acronym[lookup.id==n].values[0] #if lenname > 0 else []        
    outdf.ParentID[n] = lookup.parent_structure_id[lookup.id==n] #if lenname > 0 else 0    
    outdf.IDPath[n] = lookup.structure_id_path[lookup.id==n].values[0] #if lenname > 0 else []
    outdf.LabelID[n] = n #if lenname > 0 else 0 
    
    outdf.Counts[n] = mcounts[n-1]
    outdf.Areas[n] = mareas[n-1]
   
# drop first row
outdf = outdf.ix[1:]

# drop Nan rows
outdf = outdf[outdf.LabelID != 0 ]

# save df to csv
outdir = '%s/stats' % subjdir

if not os.path.exists(outdir):
    os.makedirs(outdir)

outcsv = '%s/%s_clar_feats_allen_gp-lbls.csv' % (outdir,sys.argv[2])
outdf.to_csv(outcsv)   

print ("\n Features Computation done in %s ... Have a good day!\n" % (datetime.now() - startTime)) 
