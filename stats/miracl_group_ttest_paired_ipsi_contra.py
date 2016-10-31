#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu 

# coding: utf-8

import numpy as np
import scipy as sp
import scipy.stats as stats
import pandas as pd
from subprocess import call
import nibabel as nib
import os
import argparse

### Inputs #########

def helpmsg(name=None): 

    return '''miracl_group_wilcoxon_gp-lbls.py -g [group] -m [mice list] -p [parameter list]

Computes non-parametric wilcoxon test for all grand-parent labels across mice for all given parameters (& features)
    
example: miracl_group_wilcoxon_gp-lbls.py  -g stroke  -m 01 02 04 07 08 10 11 12  -p fa md t2 Areas Density Counts
        '''

parser = argparse.ArgumentParser(description='Sample argparse py', usage=helpmsg())
parser.add_argument('-g','--group', type=str, help="group (stroke or control)", required=True)

parser.add_argument('-m','--mouse', type=int, nargs='+', help="mice ids", required=True)
parser.add_argument('-p','--pars', type=str, nargs='+', help="parameters & features", required=True)

args = parser.parse_args()

mice = args.mouse
grp = g = args.group
pars = args.pars

## if control given then control else contra side

###################

# mkdir 
outres = '/data/clarity_project/mouse/stroke_study/results/wilcoxon'
outdir = outres + '/ipsi_vs_contra' 

if not os.path.exists(outdir):
    os.makedirs(outdir)
else:
    print 'Experiment folder exists.. overwriting old experiment!'

# Init dirs
projdir='/data/clarity_project/mouse/stroke_study'

# sort pars
pars = sorted(pars)

# Prep df per mouse 
alldfs ={}

for m in mice:
    
    m = "%02d" % m

    subjdir = '%s/%s/%s/stats' % (projdir,grp,m)    

    df = pd.read_csv ('%s/%s_gp-lbls_stats_comb.csv' % (subjdir,m)) 
    alldfs[m] = df


# get pars & feats vals from dict
vals = alldfs.values()


# get lbl intersec 
inter = set(vals[0].LabelAbrv)
for vallist in vals[0:]:
    inter.intersection_update(vallist.LabelAbrv)


# use intersec only
for i in range(len(vals)):
    vals[i] = vals[i][vals[i].LabelAbrv.isin(inter)]

ids=vals[1].LabelID


# drop ipsi labels with no contra
ipsi = ids[ids < 2000]
contra = np.asarray(ids[ids > 2000])
cp = ipsi + 2000
cp = list(set(cp) & set(contra))
ipsi = np.sort(pd.Series(cp) - 2000)


###################

# compute mann-whitney test on ipsi vs. contra
wlsss = {}
wlpss = {}

for par in pars: 
    
    wlss = []
    wlps = []

    for ip in ipsi:
        
        ipstr = 'vals[i].%s[vals[i].LabelID==ip]' % par
        contstr = 'vals[i].%s[vals[i].LabelID==(ip+2000)]' % par
        
        met_ipsi = [ eval(ipstr) for i in range(len(vals)) ]
        met_ipsi = np.asarray([ map(np.float, x) for x in met_ipsi ])[:,0]
        
        met_cont = [ eval(contstr) for i in range(len(vals)) ]
        met_cont = np.asarray([ map(np.float, x) for x in met_cont ])[:,0]

        [wls,wlp] = stats.wilcoxon(met_ipsi,met_cont)
        wlss.append(wls)
        wlps.append(wlp)
                
    wlsss[par] = wlss
    wlpss[par] = wlps


wl_stat = [ wlsss[key] for key in sorted(wlsss.iterkeys()) ]
wl_pval = [ wlpss[key] for key in sorted(wlpss.iterkeys()) ]


###################

# save output
# get lbl demos
orgdf = df.ix[df.LabelID.isin(ipsi),1:6]
orgdf = orgdf.reset_index()


# get stats
stats = pd.DataFrame(wl_stat).T
statstr = '_stat'
parstat = [s + statstr for s in pars]
stats.columns = parstat


# get pvals
pstr = '_pval'
parspvl = [s + pstr for s in pars]
pvals = pd.DataFrame(wl_pval).T 
pvals.columns = parspvl


# combine stats & pvals
comb = [stats, pvals]
comb = pd.concat(comb,axis=1)
comb = comb.sort_index(ascending=True,axis=1)


# combine with demos
frames = [orgdf, comb]
newdf = pd.concat(frames,axis=1)


# save df as csv
outcsv = '%s/wilcoxon_test.csv' % outdir
newdf.ix[:,1:].to_csv(outcsv,index=False)

###################

# save as excel
outexcel = '%s/wilcoxon_text.xlsx' % outdir

writer = pd.ExcelWriter(outexcel, engine='xlsxwriter')
newdf.ix[:,1:].to_excel(writer, index=False, sheet_name='wilcoxon')

workbook = writer.book
worksheet = writer.sheets['wilcoxon']

number_rows = len(newdf.index)

# Add a format. Green fill with dark green text.
format1 = workbook.add_format({'bg_color': '#C6EFCE',
                               'font_color': '#006100'})

color_range = "F2:Q{}".format(number_rows+1)

# green cells less than alpha (0.05)
worksheet.conditional_format(color_range, {'type': 'cell',
                                           'criteria': '<',
                                           'value': '0.05',
                                           'format': format1})
writer.save()


###################

# project onto labels

atlasdir = '/data/clarity_project/atlases/allen/annotations'

nii = nib.load('%s/grand-parent_lbls.nii.gz' % atlasdir)
img = nii.get_data()


# replace intensities with p-values
for p,par in enumerate(pars):

    newimg = np.ones(img.shape)
    
    for w,wlx in enumerate(wl_pval[p]):
        
        orgipsi = ipsi[w]
        idxip = (img == orgipsi)
        newimg[idxip] = wl_pval[p][w]
        # if want both sides
        orgcont = contra[w]
        idxcont = (img == orgcont)
        newimg[idxcont] = wl_pval[p][w]
    
    #save new nifti
    mat = np.eye(4)
    mat[0,0] = 0.025
    mat[1,1] = 0.025
    mat[2,2] = 0.025
    newnii = nib.Nifti1Image(newimg,mat)
    niiname = '%s/%s_wilcoxon_pval_gp-lbls.nii.gz' % (outdir,pars[p])
    nib.save(newnii,niiname)

# ort out niftis
for par in pars:
    call(["c3d", "%s/%s_wilcoxon_pval_gp-lbls.nii.gz" % (outdir, par), "-orient", "ASR", "-o",
          "%s/%s_wilcoxon_pval_gp-lbls.nii.gz" % (outdir, par)])
