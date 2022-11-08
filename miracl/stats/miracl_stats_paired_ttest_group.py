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
from miracl import ATLAS_DIR

from miracl.lbls.miracl_lbls_get_graph_info import get_lbl_info
from miracl.utilfn.miracl_utilfn_extract_lbl import extract_label
from miracl.lbls.miracl_lbls_generate_parents_at_depth import get_parent_data

### Inputs #########


def helpmsg(name=None):
    return '''miracl_stats_paired_ttest_group.py -i [ input csv files]

    Computes paired_ttest test between two groups of mice across all labels
    
    Looks for feature exraction csv files within input directory
    
    Outputs csv,xlsx files with stats results & a nifti image with label values corresponding to p-values of the t-test
    
    example: miracl_stats_paired_ttest_ipsi_contra.py -d feat_extract_csv

        '''


def parsefn():
    parser = argparse.ArgumentParser(description='', usage=helpmsg())
    parser.add_argument('-i', '--input', type=str, help="Comma separate values (CSV) file with values", required=True)
    parser.add_argument('-p', '--pval', help="p-value to threshold final figure by; default: 0.05", default=0.05)

    return parser


def parse_inputs(parser, args):
    input = args.input
    pval = args.pval

    return input, pval


# -----------------
# read csvs

def readcsvs(file_name):
    ''' Returns dataframe from comma-separated values file
    '''
    df = pd.read_csv(file_name)

    return df


def create_groups(df):
    ''' Return dataframes representing the groups, as well as the regions of interest from the input
    '''
    df_groups = df.ix[:, 1::] # remove the column showing the regions
    df_regions = df.ix[:, 0] # remove the column showing the regions
    df_group1 = df_groups.filter(regex='^R', axis=1)
    df_group1_cols = list(df_group1.columns)
    df_group2 = df_groups[[col for col in df_groups.columns if col not in df_group1.columns]]  # anything not in group1 would be group 2

    return df_regions, df_group1, df_group2


def run_ttest(group1, group2):
    ''' Return the result of running a t-test between the two groups
    '''
    t, p = stats.ttest_ind(group1, group2, axis=1, nan_policy='omit')
    return t, p

def combine_results(df_regions, tt_stat, tt_pval):
    ''' Return dataframe combining ttest, pvalue results with associated regions 
    '''
    # combine score, pval into one dataframe
    t_val_df = pd.concat([df_regions, pd.Series(tt_stat)], axis=1)
    t_val_df = pd.concat([t_val_df, pd.Series(tt_pval)], axis=1)
    t_val_df.columns = ['region', 'stat', 'pvalue']
    return t_val_df


def store_csvs(df, outdir):
    ''' Store t-test scores, p-values
    '''
    # save df as csv
    outcsv = '%s/paired_ttest_test.csv' % outdir
    df.to_csv(outcsv, index=False)

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

def projpvalonatlas(atlas, atlas_legend, pval_csv, output, thresh=None):
    """ Project the pvalues from the analysis onto the labels of the Allen atlas"""
    # if no threshold is given, set pvalue to 1.1
    if not thresh:
        thresh = 1.01

    # load atlas
    nii = nib.load('%s' % atlas)
    atlas_img = nii.get_data()

    # load atlas lookup table, pval table
    atlas_df = pd.read_csv(atlas_legend)
    pval_df = pd.read_csv(pval_csv)

    # create dictionary that stores depth of each arrat
    depth_arr_dict = {}

    # generate blank image
    res = np.zeros(atlas_img.shape)
    # for each region in the csv result file
    for index, row in pval_df.iterrows():
        region = row['region'][1:]
        # get the corresponding atlas_id value in the split atlas
        # if the value isnt nan, extract and go
        if pd.notna(row['pvalue']) and row['pvalue'] < thresh:
            allen_id = atlas_df.loc[atlas_df['acronym'] == region, 'id'].iloc[0]

            name = atlas_df.loc[atlas_df['acronym'] == region, 'name'].iloc[0]

            # extract the depth, use the information to get the voxels with the ROI
            lbl_info = get_lbl_info(region)
            depth = lbl_info['depth'][0]

            # if allen atlas at depth doesnt exist, create it
            if depth not in depth_arr_dict:
                depth_arr_dict[depth] = get_parent_data(depth)
            depth_arr = depth_arr_dict[depth]

            # set all corresponding voxels to the p-value
            res[depth_arr == allen_id] = row['pvalue']

    # store nifti as result
    newnii = nib.Nifti1Image(res, nii.affine)
    #niiname = os.path.join(outdir, 'groupwise_ttest_pval_2_thresh.nii.gz')
    nib.save(newnii, output)


def main(args):
    parser = parsefn()
    input_file, pval = parse_inputs(parser, args)
    outdir = os.path.dirname(input_file)
    if not outdir:
        outdir = os.getcwd()

    # load dataframe
    df = readcsvs(input_file)

    # split groups
    regions, group1, group2 = create_groups(df)

    # run tests
    tstat, pvalue = run_ttest(group1, group2)

    tt_df = combine_results(regions, tstat, pvalue)

    # store into csvs, excel files
    store_csvs(tt_df, outdir)
    # savexlsx(tt_df, outdir)
    outcsv = os.path.join(outdir, 'paired_ttest_test.csv')
    
    # generate final nifti
    niiname = os.path.join(outdir, 'groupwise_ttest_pval.nii.gz')
    atlas = '%s/ara/annotation/annotation_hemi_combined_25um.nii.gz' % ATLAS_DIR
    atlas_legend = '%s/ara/ara_mouse_structure_graph_hemi_combined.csv' % ATLAS_DIR
    projpvalonatlas(atlas, atlas_legend, outcsv, niiname, 0.05)


if __name__ == "__main__":
    main(sys.argv)
