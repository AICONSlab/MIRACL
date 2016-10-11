#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import scipy as sp
import pandas as pd
import argparse

### Inputs #########

def helpmsg(name=None): 

    return '''mouse_combine_gp-lbls_stats.py -m [mouse id] 

Combines parameters & features stats into a single csv file

example: mouse_combine_gp-lbls_stats.py -m 01  
  		'''

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-m','--mouse', type=int, help="mouse id", required=True)
parser.add_argument('-g','--group', type=str, help="group (stroke or control)", required=True)

args = parser.parse_args()

mouse = m = args.mouse
m = "%02d" % m

group = g = args.group

# Init dirs
projdir = '/data/clarity_project/mouse/stroke_study/%s' % group

subjdir = '%s/%s/stats' % (projdir,m)

fa = pd.read_csv("%s/%s_inv_FA_allen_gp-lbls.csv" % (subjdir,m))  
md = pd.read_csv("%s/%s_inv_MD_allen_gp-lbls.csv" % (subjdir,m))  
t1 = pd.read_csv("%s/%s_inv_T1_allen_gp-lbls.csv" % (subjdir,m))  
t2 = pd.read_csv("%s/%s_inv_T2_allen_gp-lbls.csv" % (subjdir,m))  
ct = pd.read_csv("%s/%s_exv_CT_allen_gp-lbls.csv" % (subjdir,m))  
clar = pd.read_csv("%s/%s_clar_feats_allen_gp-lbls.csv" % (subjdir,m)) 

fa = fa.ix[:,:10]
md = md.ix[:,:10]
t1 = t1.ix[:,:10]
t2 = t2.ix[:,:10]
ct = ct.ix[:,:10]

fa = fa.rename(columns={"Mean":"fa"})
md = md.rename(columns={"Mean":"md"})
t1 = t1.rename(columns={"Mean":"t1"})
t2 = t2.rename(columns={"Mean":"t2"})
ct = ct.rename(columns={"Mean":"ct"})

# get same lbls
clar = clar.ix[:,1:]
clar2 = clar[clar.IDPath.isin(fa.IDPath)]

fa2 = fa[fa.IDPath.isin(clar2.IDPath)]
md2 = md[md.IDPath.isin(clar2.IDPath)]
t12 = t1[t1.IDPath.isin(clar2.IDPath)]
t22 = t2[t2.IDPath.isin(clar2.IDPath)]
ct2 = ct[ct.IDPath.isin(clar2.IDPath)]

clar3 = clar2.reset_index(drop=True)

fa3 = fa2.reset_index(drop=True)
md3 = md2.reset_index(drop=True)
t13 = t12.reset_index(drop=True)
t23 = t22.reset_index(drop=True)
ct3 = ct2.reset_index(drop=True)

dens = clar3.Counts / fa3.Count
dens = pd.DataFrame({'Density': pd.Series(dens)})

# combine dfs
frames = [fa3, md3.md, t13.t1, t23.t2, ct3.ct, dens, clar3.ix[:,5:] ]
allcomb = pd.concat(frames,axis=1,join='inner')

outcsv = '%s/%s_gp-lbls_stats_comb.csv' % (subjdir,m)

allcomb.to_csv(outcsv)   
