#!/usr/bin/env python
# Maged Goubran @ 2022, maged.goubran@utoronto.ca 

# coding: utf-8

import argparse
import glob
import os
from subprocess import call
import sys
import nibabel as nib
import numpy as np
import pandas as pd
import scipy.stats as stats
from miracl.utilfn.depends_manager import add_paths

### Inputs #########


def helpmsg(name=None):
    return '''miracl_stats_paired_ttest_ipsi_contra.py -d [ folder with feature extraction csv files]

    Computes paired_ttest test between both hemispheres for all labels across mice
    
    Looks for feature exraction csv files within input directory
    
    Outputs csv,xlsx files with stats results & a nifti image with label values corresponding to p-values of the t-test
    
    example: miracl_stats_paired_ttest_ipsi_contra.py -d feat_extract_csv

        '''


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())
    parser.add_argument('-d', '--dir', type=str, help="dir with csv files", required=True)

    return parser


def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    dir = args.dir

    return dir


# -----------------
# read csvs

def readcsvs(indir, splitval=20000):
    file_list = glob.glob('%s/*.csv' % indir)

    # Prep df per mouse
    alldfs = {}

    for c, csv in enumerate(file_list):
        df = pd.read_csv(csv)
        df = df.ix[:, 1::]
        # set sides
        df.loc[:, 'Side'] = np.where(df['LabelID'] < splitval, 'ipsi', 'contra')
        #     add mouse num
        #     df.loc[:,'Mouse'] = pd.Series(np.repeat(m,len(df)), index=df.index)

        alldfs[c] = df

    # get pars & feats vals from dict
    vals = alldfs.values()

    return vals, df


# -----------------
# clean up fn

def cleanuplbls(vals, splitval=20000):
    # get lbl intersec
    inter = set(vals[0].LabelAbrv)
    for vallist in vals[0:]:
        inter.intersection_update(vallist.LabelAbrv)

    # use intersec only
    for i in range(len(vals)):
        vals[i] = vals[i][vals[i].LabelAbrv.isin(inter)]

    ids = vals[0].LabelID

    # drop ipsi labels with no contra
    ipsi = ids[ids < splitval]
    contra = np.asarray(ids[ids > splitval])
    cp = ipsi + splitval
    cp = list(set(cp) & set(contra))
    ipsi = np.sort(pd.Series(cp) - splitval)

    return ipsi


# -----------------

def computepairttest(vals, ipsi, pars, splitval=20000):
    # compute paired-ttest test on ipsi vs. contra
    ttsss = {}
    ttpss = {}

    for par in pars:

        ttss = []
        ttps = []

        for ip in ipsi:
            ipstr = 'vals[i].%s[vals[i].LabelID==ip]' % par
            contstr = 'vals[i].%s[vals[i].LabelID==(ip+splitval)]' % par

            met_ipsi = [eval(ipstr) for i in range(len(vals))]
            met_ipsi = np.asarray([map(np.float, x) for x in met_ipsi])[:, 0]

            met_cont = [eval(contstr) for i in range(len(vals))]
            met_cont = np.asarray([map(np.float, x) for x in met_cont])[:, 0]

            [tts, ttp] = stats.ttest_rel(met_ipsi, met_cont)
            ttss.append(tts)
            ttps.append(ttp)

        ttsss[par] = ttss
        ttpss[par] = ttps

    tt_stat = [ttsss[key] for key in sorted(ttsss.iterkeys())]
    tt_pval = [ttpss[key] for key in sorted(ttpss.iterkeys())]

    return tt_stat, tt_pval


# -----------------

def savecsv(df, ipsi, tt_stat, tt_pval, outdir, pars):
    # save output
    # get lbl demos
    orgdf = df.ix[df.LabelID.isin(ipsi), 1:6]
    orgdf = orgdf.reset_index()

    # get stats
    stats = pd.DataFrame(tt_stat).T
    statstr = '_stat'
    parstat = [s + statstr for s in pars]
    stats.columns = parstat

    # get pvals
    pstr = '_pval'
    parspvl = [s + pstr for s in pars]
    pvals = pd.DataFrame(tt_pval).T
    pvals.columns = parspvl

    # combine stats & pvals
    comb = [stats, pvals]
    comb = pd.concat(comb, axis=1)
    comb = comb.sort_index(ascending=True, axis=1)

    # combine with demos
    frames = [orgdf, comb]
    savedf = pd.concat(frames, axis=1)

    # save df as csv
    outcsv = '%s/paired_ttest_test.csv' % outdir
    savedf.ix[:, 1:].to_csv(outcsv, index=False)

    return savedf


# -----------------

def savexlsx(savedf, outdir):
    # save as excel
    outexcel = '%s/paired_ttest_text.xlsx' % outdir

    writer = pd.ExcelWriter(outexcel, engine='xlsxwriter')
    savedf.ix[:, 1:].to_excel(writer, index=False, sheet_name='paired_ttest')

    workbook = writer.book
    worksheet = writer.sheets['paired_ttest']

    number_rows = len(savedf.index)

    # Add a format. Green fill with dark green text.
    format1 = workbook.add_format({'bg_color': '#C6EFCE',
                                   'font_color': '#006100'})

    color_range = "F2:Q{}".format(number_rows + 1)

    # green cells less than alpha (0.05)
    worksheet.conditional_format(color_range, {'type': 'cell',
                                               'criteria': '<',
                                               'value': '0.05',
                                               'format': format1})
    writer.save()


# -----------------

def projpvalonatlas(atlas, pars, ipsi, tt_pval, outdir):
    # project onto labels

    nii = nib.load('%s' % atlas)
    img = nii.get_data()

    # replace intensities with p-values
    for p, par in enumerate(pars):

        newimg = np.ones(img.shape)

        for t, ttx in enumerate(tt_pval[p]):
            orgipsi = ipsi[t]
            idxip = (img == orgipsi)
            newimg[idxip] = tt_pval[p][t]

            # # if want both sides
            # orgcont = contra[w]
            # idxcont = (img == orgcont)
            # newimg[idxcont] = tt_pval[p][w]

        # save new nifti
        mat = np.eye(4) * 0.025
        mat[3, 3] = 1

        newnii = nib.Nifti1Image(newimg, mat)
        niiname = '%s/%s_paired_ttest_pval.nii.gz' % (outdir, pars[p])
        nib.save(newnii, niiname)

    # ort out niftis
    for par in pars:
        call(["c3d", "%s/%s_paired_ttest_pval.nii.gz" % (outdir, par), "-orient", "ASR", "-o",
            "%s/%s_paired_ttest_pval.nii.gz" % (outdir, par)])


def main(args):
    parser = parsefn()
    dir = parse_inputs(parser, args)

    # mkdir
    outdir = '%s/paired_ttest_ipsi_vs_contra' % dir

    if not os.path.exists(outdir):
        os.makedirs(outdir)
    else:
        print('Experiment folder exists.. overwriting old experiment!')

    # read csv
    print("\n Reading feature extraction csv files")

    # splitval = 20000

    [vals, df] = readcsvs(dir)

    # clean-up labels (for intersections between mices & dropping ones w only one hemi)
    ipsi = cleanuplbls(vals)

    # get pars
    # pars = list(df.columns[5:-1])
    pars = list(df.columns[5:-3])  # ignore Vol max,min

    # compute paired t-test
    print("\n Computing paired t-test between ipsi & contra hemispheres across all mice")
    [tt_stat, tt_pval] = computepairttest(vals, ipsi, pars)

    # save csv
    print("\n Saving stats as csv file")
    savedf = savecsv(df, ipsi, tt_stat, tt_pval, outdir, pars)

    # save xlsx
    print("\n Saving stats as xlsx file with significant p-values as green cells")
    savexlsx(savedf, outdir)

    # project onto atlas labels
    print("\n Projecting stats onto atlas label and saving nifti file")

    miracl_home = os.environ['MIRACL_HOME']
    atlas = '%s/atlases/ara/annotation/annotation_hemi_combined_25um.nii.gz' % miracl_home

    projpvalonatlas(atlas, pars, ipsi, tt_pval, outdir)


if __name__ == "__main__":
    main(sys.argv)
