#!/usr/bin/env python
# Maged Goubran @ 2016, mgoubran@stanford.edu

# coding: utf-8

import numpy as np
import pandas as pd
from subprocess import call
import seaborn as sns
import os
import matplotlib.pyplot as plt

from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache


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
atlas_lbls = pd.read_fwf(
    '/Users/mgoubran/workspace/clarity_Project/allen_atlas/annotations/res0.025/included_lbls/atlas_lbl_ids.txt')


## major labels to exclude (ie root,grey,etc) @ depth 0 or 1
exclude = np.array(annot_csv[(annot_csv['depth']==0) | (annot_csv['depth']==1)].id)


##---------------

# Get 'histogram' of masked labels

def gethist():
    """ Gets all labels inside input mask
    """  
    call(["c3d", "f3d_stroke_mask_allen_masked_ero.nii.gz","annotation.nii.gz","-lstat",">","c3d_lbls.txt"])

    c3d = pd.read_fwf('c3d_lstat.txt')
    c3d = c3d[c3d.Mean!=0]
    c3d = c3d.sort_values(['Count','LabelID'],ascending=False)
    mask_lbls = np.asarray(c3d.LabelID)
    
    return mask_lbls


# In[7]:

# Check if labels have injection exps

def check_inj_exp(mask_lbls,projexps):
    """ Checks if certain label has
    an injection experiment in Allen connect atlas
    """    
    inj_exps=np.zeros([mask_lbls.shape[0]])
        
    for l,lbl in enumerate(mask_lbls):

        # get exp num by searching injection struct
        inj_exps[l] = (projexps['structure-id']==lbl).any()
    
    inj_exps = np.asarray(inj_exps).astype(int)
    
    return inj_exps


# In[8]:

# Exclude major lablels

def exlude_maj_lbls(in_lbls):
    
    indx = np.in1d(in_lbls,exclude)
    out_lbls = np.delete(in_lbls,np.where(indx==True)) 
    
    return out_lbls


# In[9]:

# get parent labels for ones w/out inj exp

def get_parentlbl(inj_exps,mask_lbls,annot_csv):
    """ gets parent labels for labels
    without injection experiements in Allen atlas
    """ 
    mask_lbls_prt = mask_lbls
    
    for i in range(inj_exps.shape[0]):
        if inj_exps[i]==0:
            
            l = mask_lbls[i]
            # get parent label
            pid = annot_csv.parent_structure_id[annot_csv.id==l].values[0]
            mask_lbls_prt[i] = pid

    unq,ind = np.unique(mask_lbls_prt,return_index=True)  
    indsort = np.sort(ind)
    uniq_lbls = mask_lbls_prt[indsort]
    
    uniq_lbls = exlude_maj_lbls(uniq_lbls)
    
    return uniq_lbls


# In[10]:

def query_connect(uniq_lbls,projexps,cutoff):
    """ Queries the structural connectivity of
    labels inside mask & sorts found labels by projection volume
    """
    
    all_connect_ids = np.zeros([num_out_lbl,(num_out_lbl*2+len(exclude))+3])
    all_connect_ids[:,0] = uniq_lbls.T

    all_norm_proj = np.zeros([num_out_lbl,(num_out_lbl*2+len(exclude))+3])
    all_norm_proj[:,0] = uniq_lbls.T

    for l,lbl in enumerate(uniq_lbls):

        # get exp num by searching injection struct
        exp_id = projexps[projexps['structure-id']==lbl].id.index[0]

        # get exp regions stats
        projection_df = mcc.get_structure_unionizes([exp_id], is_injection=False)

        # TODOhp: check if need to use hemi 3 instead
        # get connected regions
        filter_exp = projection_df.loc[(projection_df['normalized_projection_volume'] > cutoff) & (projection_df['hemisphere_id'] != 3)]

        # sort exp values by norm proj volume
        norm_proj = filter_exp.sort_values(['normalized_projection_volume'],
                                           ascending=False).ix[:,['hemisphere_id','structure_id','normalized_projection_volume']]
        norm_proj_vol = norm_proj['normalized_projection_volume']

        # distinguish label hemisphere
        orgid = np.array(norm_proj['structure_id'])
        hem = np.array(norm_proj['hemisphere_id'])        
        connect_ids = [ orgid[i]+2000 if hem[i]==1 else orgid[i] for i in range(len(hem))  ]

        # extract n ids
        all_connect_ids[l,1:] = connect_ids[0:(num_out_lbl*2)+len(exclude)+2] 
        all_norm_proj[l,1:] = norm_proj_vol[0:(num_out_lbl*2)+len(exclude)+2] 

    return all_connect_ids,all_norm_proj


# In[11]:

# Get 'histogram' of masked labels
print('Getting histogram of included labels in stroke mask & sorting by volume')

mask_lbls = gethist()

# Setup Allen connect jason cache file
mcc = MouseConnectivityCache(manifest_file='connectivity/manifest.json')
# Load all injection experiments from Allen api
all_experiments = mcc.get_experiments(dataframe=True)
# Filter to only wild-type strain
projexps = all_experiments[all_experiments['strain']=="C57BL/6J"]

# excluding background/negatives
mask_lbls = exlude_maj_lbls(mask_lbls) 
mask_lbls = mask_lbls[ (mask_lbls > 0) & (mask_lbls < maxannot) ]

# Check if labels have injection exps
print('Checking if labels have injection experiments in the connectivity search')

inj_exps = check_inj_exp(mask_lbls,projexps)

# get parent labels for ones w/out inj exp
print('Getting parent labels for labels without injection experiments')


uniq_lbls = get_parentlbl(inj_exps,mask_lbls,annot_csv)

# check all labels have inj exps
print('Checking that all parent labels have injection exps')

inj_exps = check_inj_exp(uniq_lbls,projexps)

while (len(inj_exps) != sum(inj_exps)):

    uniq_lbls = get_parentlbl(inj_exps,uniq_lbls,annot_csv)
    inj_exps = check_inj_exp(uniq_lbls,projexps)

# Restrict to n labels    
uniq_lbls = uniq_lbls[0:num_out_lbl]    


# In[12]:

# query structure connectivity from Allen API    
print('Quering structural connectivity of injection labels in the Allen connectivity api & sorting by projection volume')

[all_connect_ids,all_norm_proj] = query_connect(uniq_lbls,projexps,cutoff)


# In[13]:

# excluding major labels @ depth 0 or 1 
all_connect_ids_excl = np.zeros((num_out_lbl,(num_out_lbl*2)+3))
all_connect_ids_excl[:,0] = uniq_lbls.T

for i in range(all_connect_ids.shape[0]):
    indx_excl = np.in1d(all_connect_ids[i,1:],exclude)
    connect_ids_excl = np.delete(all_connect_ids[i,1:],np.where(indx_excl==True))        
    connect_ids_excl = connect_ids_excl[0:(num_out_lbl*2)+2]
    all_connect_ids_excl[i,1:] = connect_ids_excl
    


# In[14]:

# exclude same lbl if found in its connected regions 
conn = all_connect_ids_excl
filconn = [ np.delete(conn[t,:],np.where(conn[t]==conn[t][0])) for t in range(len(conn)) ]
filconn = np.array([ filconn[i][0:(num_out_lbl*2)] for i in range(len(filconn))])


# In[15]:

# exclude labels not included in atlas annotations

conn_ids = np.zeros((num_out_lbl,num_out_lbl+1))
conn_ids[:,0] = uniq_lbls.T

for i in range(filconn.shape[0]):
    indx_excl2 = np.in1d(filconn[i,1:],np.array(atlas_lbls))
    connect_ids_fin = np.delete(filconn[i,1:],np.where(indx_excl2==True))        
    connect_ids_fin = connect_ids_fin[0:num_out_lbl]
    conn_ids[i,1:] = connect_ids_fin
    


# In[16]:

# save as csv
export_connect = pd.DataFrame(conn_ids)

connect_cols = ['connect_lbl_%02d' % (i+1) for i in range(num_out_lbl) ]
all_cols = ['injection_lbl'] + connect_cols

export_connect.columns = all_cols
export_connect.to_csv('connected_ids.csv', index=False)


# In[17]:

# export acronynms

dic = annot_csv.set_index('id')['acronym'].to_dict()

export_connect_abv = export_connect.replace(dic)
export_connect_abv.to_csv('connected_abrvs.csv', index=False)


# In[18]:

# setup projection map
out_norm_proj = all_norm_proj[:,1:num_out_lbl+1]
names = np.array(export_connect_abv)[:,0]


# In[19]:

# export projection map (lbls w norm proj volumes along tree)

sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 1.5})
plt.figure(figsize=((15,15)))
sns.heatmap(out_norm_proj, yticklabels=names,cbar_kws={"label": "Normalized projection volume","orientation": "horizontal"}, 
            annot=True,fmt=".1f")
plt.ylabel('Primary injection structures in stroke region')
plt.xlabel('Target structure order along connection tree')
plt.savefig('projection_map_along_tree.png',dpi=90)


# In[20]:

# setup heat map

heatmap = np.zeros((num_out_lbl+1,num_out_lbl+1))
heatmap[:-1,0] = conn_ids[:,0]

# get target regions
# median across structures
med = np.unique(np.median(conn_ids[:,1:],axis=0))
indexes = np.unique(conn_ids[:,1],return_index=True)[1]
# 1st connected structures
first = [conn_ids[:,1][ix] for ix in sorted(indexes)]
# combine boths
inter = np.intersect1d(med,first)
diff = num_out_lbl-len(med)+len(inter)
res = first[:diff]
targ = np.unique(np.hstack([res,med]))

if len(targ) < num_out_lbl:

    # 1st connected structures
    secindexes = np.unique(conn_ids[:,2],return_index=True)[1]
    sec = [conn_ids[:,2][ix] for ix in sorted(secindexes)]
    # combine boths
    sec = np.delete(sec,np.intersect1d(targ,sec))
    targ = np.unique(np.hstack([targ,sec]))

targ = targ[0:num_out_lbl]    
heatmap[-1,1:] = targ


# In[21]:

# propagate heat map

for i in range(len(heatmap)-1):
    
    for l,lbl in enumerate(targ):
        
        heatmap[i,l+1] = out_norm_proj[i,np.where(conn_ids[i,1:]==lbl)] if np.sum(conn_ids[i,1:]==lbl) > 0 else 0


# In[22]:

targ = pd.DataFrame(targ)
targ_abrv = targ.replace(dic)
targ_abrv = np.array(targ_abrv[0])


# In[38]:

plt.figure(figsize=((15,15)))
sns.set_context("poster", font_scale=1.5, rc={"lines.linewidth": 1.5})
sns.heatmap(heatmap[:-1,1:],yticklabels=names,xticklabels=targ_abrv,
            cbar_kws={"label": "Normalized projection volume"},vmax=15,cmap="GnBu",linewidths=.2)
plt.ylabel('Primary injection structures in stroke region')
plt.xlabel('Target structures')
plt.savefig('stroke_region_connectivity_(heat_map)_poster.png',dpi=90)


# In[24]:

# export proj volumes
norm_proj_df = pd.DataFrame(out_norm_proj)
norm_proj_df.to_csv('norm_proj_volumes.csv', index=False)


# In[25]:

from lightning import Lightning
from numpy import random, asarray


# In[34]:

lgn = Lightning(ipython=True, local=True)


# In[27]:

# create circle connectome 
connections = np.zeros((51,51))

connections[1:26,0] = uniq_lbls.T
connections[26:,0] = targ.T

connections[0,1:26] = uniq_lbls.T
connections[0,26:] = targ.T

#propagate connections

alllbls = connections[1:,0]

for l,lbl in enumerate(alllbls):
    
    for t,tart in enumerate(alllbls):
        
        iind = heatmap[:-1,0]==lbl
        jind = heatmap[25,:]==tart
        val = heatmap[np.where(iind==True),np.where(jind==True)]
        
        connections[l+1,t+1] = val if val > 0 else 0


# In[28]:

# threshold connections

thr = 10

connections[connections < thr] =0


# In[29]:

# lbls abrv
alllbls_abrv = pd.DataFrame(alllbls)
alllbls_abrv = alllbls_abrv.replace(dic)
alllbls_abrv = np.array(alllbls_abrv[0])


# In[30]:

# get grand parents ids for groups

ggp_parents  = np.array([ annot_csv['parent_structure_id'][annot_csv['id']==lbl].item() for l,lbl in enumerate(alllbls) ])

for i in range(4):
    
    ggp_parents  = [ annot_csv['parent_structure_id'][annot_csv['id']==lbl].item() if (lbl!=997) else 997 for l,lbl in enumerate(ggp_parents)  ]
    


# In[31]:

# make dic
repl = np.unique(ggp_parents)
np.place(repl,repl>0,range(len(repl)))
uniq_parents = np.unique(ggp_parents)
parents_dic = dict(zip(uniq_parents, repl))

# replace

ggp_parents = pd.DataFrame(ggp_parents)
groups = ggp_parents.replace(parents_dic)


# In[32]:

# connections = random.rand(50,50)
# connections[connections<0.98] = 0

group = (random.rand(50) * 3).astype('int')
# lgn.circle(connections, labels=['group ' + str(x) for x in group], group=group)
lgn.circle(connections, labels=alllbls_abrv, group = np.array(groups[0]),width=1000,height=1000)

# TODOlp: view by  nested groups
