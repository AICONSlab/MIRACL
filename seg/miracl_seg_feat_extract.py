#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import argparse
import logging
import multiprocessing
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import scipy as sp
import tifffile as tiff
from joblib import Parallel, delayed
from scipy import ndimage
from skimage.measure import regionprops


# ---------
# help fn

def helpmsg(name=None):
    return '''Usage: mouse_feat_extract.py -s [segmentation tif] -l [Labels]

    Computes features of segmented image and summarizes them per label

    example: mouse_feat_extract.py -s segmentation/voxelized_seg.tif -l reg_final/annotation_hemi_combined_25um_clar_vox.tif

        arguments (required):

        s. Voxelized segmentation tif file

        l. Allen labels (registered to clarity) used to summarize features

                reg_final/annotation_hemi_(hemi)_(vox)um_clar_vox.tif

    ------

    Main Outputs




	Dependencies:

	    Python 2.7

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
# Logging fn

def scriptlog(logname):
    class StreamToLogger(object):
        """
	   Fake file-like stream object that redirects writes to a logger instance.
	   """

        def __init__(self, logger, log_level=logging.INFO):
            self.logger = logger
            self.log_level = log_level
            self.linebuf = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

        def flush(self):
            pass

    logging.basicConfig(
        level=logging.DEBUG,
        filename="%s" % logname,
        format='%(asctime)s:%(message)s',
        filemode='w')

    stdout_logger = logging.getLogger('STDOUT')
    handler = logging.StreamHandler()
    stdout_logger.addHandler(handler)
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)

    stderr_logger = logging.getLogger('STDERR')
    stderr_logger.addHandler(handler)
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)


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

        if segz != lblsz:

            rx = float(segx) / lblsx
            ry = float(segy) / lblsy
            rz = float(segz) / lblsz

            print('Upsampling labels to clarity resolution')

            # reslbls = sp.ndimage.zoom(lbls,(rz,rx,rx), order=0)
            reslbls = sp.ndimage.zoom(lbls, (rz, rx, ry), order=0)

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
    scriptlog('feat_extract.log')

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

        graph = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_split.csv' % miracl_home)

    else:

        graph = pd.read_csv('%s/atlases/ara/ara_mouse_structure_graph_hemi_combined.csv' % miracl_home)

    # get attributes
    # names = graph.name[graph.id.isin(alllbls)]
    # abrvs = graph.acronym[graph.id.isin(alllbls)]
    # parents = graph.parent_structure_id[graph.id.isin(alllbls)]
    # paths = graph.structure_id_path[graph.id.isin(alllbls)]

    # nrows = allareas

    # propsdf = pd.DataFrame(
    #     dict(LabelID=alllbls, LabelAbrv=abrvs, LabelName=names, ParentID=parents, IDPath=paths, Count=allnums,
    #          Density=alldens, VolumeAvg=allareas, VolumeStd=allstdareas, VolumeMax=allmaxareas))

    # Filter labels not included

    propsdf = pd.DataFrame(
        dict(LabelID=alllbls, Count=allnums, Density=alldens, VolumeAvg=allareas, VolumeStd=allstdareas,
             VolumeMax=allmaxareas))
    propsdf = propsdf[propsdf.LabelID.isin(graph.id)]

    # make dicts
    name_dic = dict(zip(graph.id, graph.name))
    abrv_dic = dict(zip(graph.id, graph.acronym))
    parents_dic = dict(zip(graph.id, graph.parent_structure_id))
    paths_dic = dict(zip(graph.id, graph.structure_id_path))

    propsdf['LabelName'] = propsdf.LabelID
    propsdf['LabelAbrv'] = propsdf.LabelID
    propsdf['ParentID'] = propsdf.LabelID
    propsdf['IDPath'] = propsdf.LabelID

    propsdf = propsdf.replace({'LabelName': name_dic})
    propsdf = propsdf.replace({'LabelAbrv': abrv_dic})
    propsdf = propsdf.replace({'IDPath': paths_dic})
    propsdf['ParentID'] = propsdf.ParentID.map(parents_dic)

    cols = ['LabelID','LabelAbrv','LabelName','ParentID','IDPath','Count','Density','VolumeAvg','VolumeStd','VolumeMax']
    propsdf = propsdf[cols]

    propscsv = "clarity_segmentation_features_ara_labels.csv"
    propsdf.to_csv(propscsv)

    print ("\n Features Computation done in %s ... Have a good day!\n" % (datetime.now() - startTime))


if __name__ == "__main__":    
    main()
