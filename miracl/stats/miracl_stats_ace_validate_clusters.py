
"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca) & Maged Goubran
This function 

1. Preprocess (binarize, dilate, and connected component analysis) the p value obtained by ACE cluster wise analysis
2. warps the pvalue to the native space of each subject using transformation matrix;
3. summarizes the information of each cluster at atlas space
4. counts the neurons inside each cluster at native space and saves it in the .csv file
5. run mann withney statistical test for each cluster using the neuronal count at native space to validate cluster

"""
import argparse
import os
import pickle
import nibabel as nib
import numpy as np
import scipy.ndimage as scp
from skimage import measure
import pandas as pd
import fnmatch
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample
import subprocess
import tifffile
import json
from pathlib import Path
from scipy.stats import mannwhitneyu, ttest_ind
# -------------------------------------------------------
# create parser
# -------------------------------------------------------
my_parser = argparse.ArgumentParser(description='Working directory')

# Add the arguments
my_parser.add_argument('-p','--p_value', help='p_value nii image should be -log(p)', required=True)
my_parser.add_argument('-thr', '--pvalue_thr', type=float, help="threshold for binarizing p value", default=0.01)
my_parser.add_argument('-s','--stats', help='cluster wise TFCE statistics nii image', required=True)
my_parser.add_argument('-atl_dir','--atlas_dir', help='path of atlas directory', default='miracl_home')
my_parser.add_argument('-diff','--mean_diff', help='mean diff of two groups nii image', required=True)
my_parser.add_argument('-ctrl','--ctrl', help='path to control group; should have directories for each subject;each directory contains registration folder and 3D seg file from ACE', required=True)
my_parser.add_argument('-treated','--treated', help='path to treated group; specs should be similar to control group', required=True)
my_parser.add_argument('-o','--out_dir', help='path of output directory', required=True)

def ifdsntexistrun(outfile, outstr, command_str):
    command_list = command_str.split()
    if not os.path.exists(outfile):
        print(f"\n {outstr}")
        print(f"\n running command: {command_str}")
        subprocess.run(command_list)
    else:
        print(f"\n {outfile} already exists ... skipping")
# -------------------------------------------------------
# load and prepare atl
# -------------------------------------------------------

def get_atls(atl_dir, img_res=25):
      # find the atl directory
      if atl_dir == 'miracl_home':
            atl_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen/template'
            ann_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen/annotation'
            lbl_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen'
            #atl_dir = '/data3/projects/Ahmadreza/deepneuronseg/dataset/dataset3/walking_exp/cluster_test/atlas_sliced'
            #ann_dir = '/data3/projects/Ahmadreza/deepneuronseg/dataset/dataset3/walking_exp/cluster_test/atlas_sliced'
      
      mask_filename = f'average_template_{img_res}um_brainmask.nii.gz'
      ann_filename = f'annotation_hemi_combined_{img_res}um.nii.gz'

      # load the atlas
      if img_res == 10:

            ann_img = nib.load(os.path.join(ann_dir, ann_filename))
            ann_img_array = ann_img.get_fdata()
            mask_img = np.ones_like(ann_img_array)
            mask_img[ann_img_array == 0] = 0
            nib.save(nib.Nifti1Image(mask_img, ann_img.affine, ann_img.header), os.path.join(out_dir, "brain_mask_10um.nii.gz"))

            mask_filename = os.path.join(out_dir, "brain_mask_10um.nii.gz")
            mask_img = nib.load(mask_filename)
            mask_img_array = mask_img.get_fdata()

      else:

            ann_img = nib.load(os.path.join(ann_dir, ann_filename))
            ann_img_array = ann_img.get_fdata()
            mask_filename = os.path.join(atl_dir, mask_filename)
            mask_img = nib.load(mask_filename)
            mask_img_array = mask_img.get_fdata()

      # load atlas label names

      lbl_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen'

      annotation_lbls = pd.read_csv(
            os.path.join(lbl_dir, 'ara_mouse_structure_graph_hemi_combined.csv'),
            )
      selected_columns = ['id', 'name']
      annotation_lbls = annotation_lbls[selected_columns]

      # Display the DataFrame
      # print(annotation_lbls['lbl_name'])
      print('\n annotation_lbls: ', annotation_lbls)
      print('\n mask shape: ', mask_img_array.shape)
      ann_img_array = ann_img_array.astype("int")
      return ann_img_array, annotation_lbls

# -------------------------------------------------------
# function to preprocess pvalue image
# -------------------------------------------------------
def binarize_dialte_clusters(p_value, thr, out_dir, dil_bin_pval, dil_bin_pval_comp, dil_bin_pval_comp_fil, niter=3, size_thr=0): 

      
      pval_bin = os.path.join(out_dir, 'p_values_bin.nii.gz')

      print("\n reading p-values")
      pvals_img_nii = nib.load(p_value)
      pvals_img_arr = pvals_img_nii.get_fdata()

      print("\n shape p-value file: ", pvals_img_arr.shape,
            " p-value min: ", pvals_img_arr.min(),
            " p-value max: ", pvals_img_arr.max())

      # binarize pval
      print("\n extracting significant p-values")
      thr = -np.log10(thr)
      pvals_img_arr_bin = np.zeros_like(pvals_img_arr, dtype='bool')
      pvals_img_arr_bin[pvals_img_arr > thr] = True
      nib.save(nib.Nifti1Image(pvals_img_arr_bin, pvals_img_nii.affine, pvals_img_nii.header),
            pval_bin)

      # dilate binarized pval
      print("\n dilating significant p-values")
      pvals_img_arr_bin_d = scp.binary_dilation(pvals_img_arr_bin, iterations=niter).astype(np.uint8)
      nib.save(nib.Nifti1Image(pvals_img_arr_bin_d.astype(np.bool_), pvals_img_nii.affine, pvals_img_nii.header),
            dil_bin_pval)


      # run connected components 
  
      print("\n generating connected components")
      # Generate a structuring element that will consider features connected even if they touch diagonally
      s = np.ones((3,3,3))
      #print("structure for turning pvals to label: ", s)

      labeled_pvals, num_clusters_sig = scp.label(pvals_img_arr_bin_d, structure=s)

      nib.save(nib.Nifti1Image(labeled_pvals, pvals_img_nii.affine, pvals_img_nii.header), dil_bin_pval_comp)

      # filter by size (# of voxels)
      if os.path.isfile(dil_bin_pval_comp_fil):
            print("\n %s exists ... skipping" % dil_bin_pval_comp_fil)
      else:
            print("\n filtering p-values")
            # Calculate the size of each label
            label_sizes = np.bincount(labeled_pvals.ravel())

            # Filter labels based on size
            labels_to_keep = np.where(label_sizes >= size_thr)[0]

            # Create a mask to select only the labeled components we want to keep
            mask = np.in1d(labeled_pvals, labels_to_keep).reshape(labeled_pvals.shape)

            # Apply the mask to the labeled array
            filtered_labeled_pvals = np.where(mask, labeled_pvals, 0)

            nib.save(nib.Nifti1Image(filtered_labeled_pvals, pvals_img_nii.affine, pvals_img_nii.header), dil_bin_pval_comp_fil)

      # mask original p value with the filtered one

      pvals_img_arr[filtered_labeled_pvals == 0] = 0

      return pvals_img_arr, filtered_labeled_pvals


# -------------------------------------------------------
# warp sig clusters to original space 
# -------------------------------------------------------


def warp_sig_clusters(reg_dir, dil_bin_pval_comp_fil, ort_file, org_clar, out_dir, out_lbl, interpolation="NearestNeighbor", lbl_type="ushort"):


      warp_cmd = "/data2/projects/Ahmadreza/ACE_reviewer_response_experiments/stats/validate_clusters/miracl_lbls_warp_to_clar_space_v4.sh -r %s -l %s -o %s -c %s -d %s -f %s -i %s -t %s" \
            % (reg_dir, dil_bin_pval_comp_fil, ort_file, org_clar, out_dir, out_lbl, interpolation, lbl_type)

      ####
      # until MIRACL func is updated / fixed 

      # warp_cmd = "miracl lbls warp_clar -r %s -l %s -o %s -c %s -d %s -f %s -i %s -t %s" \
            # % ( reg_dir, dil_bin_pval_comp_fil, ort_file, org_clar, out_dir, out_lbl, interpolation, lbl_type )

      out_tiff_dir = os.path.join(out_dir, out_lbl)
      prt_str = "warping filtered clusters to clarity space"
      # ifdsntexistrun( out_tiff_dir, prt_str, warp_cmd )
      subprocess.Popen(warp_cmd, shell=True).wait()


# -------------------------------------------------------
# regionprop dataframes
# -------------------------------------------------------
def compute_region_props(mode,
                         pval,
                         out_dir,
                         mean_diff=None, 
                         labeled_pval=None, 
                         stats=None, 
                         atl_ann=None, 
                         atl_ann_lbls=None, 
                         ace_seg=None):


      if mode == "atlas":

             # get props assosciated to each cluster
            prop_list = ('label',
                        'coords',
                        'centroid',
                        'area',
                        'intensity_mean',
                        'intensity_max',
                        'intensity_min')

            cluster_props = measure.regionprops_table(label_image=labeled_pval,
                                                      intensity_image=mean_diff,
                                                      properties=prop_list)

            # get pvalue assosciated to each cluster
            prop_list = ('intensity_mean',
                        'intensity_max',
                        'intensity_min')
            cluster_props_temp = measure.regionprops_table(label_image=labeled_pval,
                                                      intensity_image=pval,
                                                      properties=prop_list)  

            data = pd.DataFrame(cluster_props)
            data["pval_mean"] = cluster_props_temp["intensity_mean"]
            data["pval_max"] = cluster_props_temp["intensity_max"]
            data["pval_min"] = cluster_props_temp["intensity_min"]

            # get statistic assosciated to each cluster
            prop_list = ('intensity_mean',
                        'intensity_max',
                        'intensity_min')
            cluster_props_temp = measure.regionprops_table(label_image=labeled_pval,
                                                      intensity_image=stats,
                                                      properties=prop_list)

            data["effect_size_mean"] = cluster_props_temp["intensity_mean"]
            data["effect_size_max"] = cluster_props_temp["intensity_max"]
            data["effect_size_min"] = cluster_props_temp["intensity_min"]


            # find the labels of each cluster
            data['cluster_lbl_values'] = np.zeros_like(data['area']).astype(object)
            data['cluster_lbl_names'] = np.zeros_like(data['area']).astype(object)
            data['cluster_lbl_areas_percent'] = np.zeros_like(data['area']).astype(object)

            for i in range(len(data['coords'])):
                  # get the regions of the brain each cluster takes 

                  cluster_coords = data['coords'][i]
                  cluster_lbls = [atl_ann[tuple(coord)] for coord in cluster_coords]
                  cluster_lbls.sort()
                  cluster_lbl_values, counts = np.unique(cluster_lbls, return_counts=True)
                  cluster_lbl_areas_percent = counts / data['area'][i]
                  cluster_lbl_names = []
                  for value in cluster_lbl_values:
                        try:
                              cluster_name = list(atl_ann_lbls["id"]).index(value)
                              cluster_lbl_names.append(atl_ann_lbls['name'][cluster_name])
                        except ValueError:
                              cluster_lbl_names.append('unknown')   
             
                  data['cluster_lbl_values'][i] = cluster_lbl_values
                  data['cluster_lbl_names'][i] = cluster_lbl_names
                  data['cluster_lbl_areas_percent'][i] = cluster_lbl_areas_percent

            # sort data based on area
            data = data.sort_values(by = 'intensity_max', ascending=False)
            data = data.drop(columns=['coords'])
            

            # Save the DataFrame to a CSV file
            data.to_csv(os.path.join(out_dir, 'sig_clusters_summary.csv'))

            print("\n sig_clusters_summary.csv has been created:")
            print(data)

            return data

# -------------------------------------------------------
# function to filter clusters
# -------------------------------------------------------
# def filter_clusters(sig_clusters_summary_csv, p_values_bin_dilated_conncomp, pvals_img_nii, out_dir):

#       # delete clusters with intensity_min of zero (edge regions)
#       column_name = 'intensity_min'
#       # Filter rows where the value in the specified column is less than 100
#       rows_to_delete = sig_clusters_summary_csv[sig_clusters_summary_csv[column_name] == 0].index
#       delete_labels = [sig_clusters_summary_csv['label'][i] for i in rows_to_delete]
#       print(delete_labels)

#       for label in delete_labels:
#             p_values_bin_dilated_conncomp[p_values_bin_dilated_conncomp == label] = 0

#       dil_bin_pval_comp_fil = os.path.join(out_dir, 'p_values_bin_dilated_conncomp_filtered.nii.gz')
#       print(dil_bin_pval_comp_fil)
#       nib.save(nib.Nifti1Image(p_values_bin_dilated_conncomp, pvals_img_nii.affine, pvals_img_nii.header), dil_bin_pval_comp_fil)
      
#       # filter .csv file
#       sig_clusters_summary_csv = sig_clusters_summary_csv.drop(rows_to_delete)
#       # Save the DataFrame to a CSV file
#       sig_clusters_summary_csv.to_csv(os.path.join(out_dir, 'sig_clusters_summary.csv'))

# -------------------------------------------------------
# function to summarize neuronal count into the .csv
# -------------------------------------------------------
def summarize_neuron_count_to_csv(neuron_json, subj, out_dir, sig_clusters_summary_csv_path):
      sig_clusters_summary_csv = pd.read_csv(sig_clusters_summary_csv_path, index_col=0)
      clusters = sig_clusters_summary_csv["label"]
      sig_clusters_summary_csv[f"neuron_count_{subj}"] = 0
      with open(neuron_json, "r") as f:
            neuron_json_dict = json.load(f)
      for i, cluster in enumerate(clusters):
            neurons = []
            for neuron_id, stats in neuron_json_dict.items():
                  if stats['label_val'] == cluster:
                        neurons.append(neuron_id)

            sig_clusters_summary_csv.iloc[
                  i,
                  sig_clusters_summary_csv.columns.get_loc(f'neuron_count_{subj}')
            ] = len(neurons)

      with open(Path(neuron_json).parent / "label_bboxes.json", "r") as f:
            bbox_dict = json.load(f)
      sig_clusters_summary_csv[f"{subj}_bbox_area_native"] = 0
      for i, cluster in enumerate(clusters):
            idxs = bbox_dict.get(str(cluster), [0, 0, 0, 0, 0, 0])
            # idxs = bbox_dict[str(cluster)] # TODO
            sig_clusters_summary_csv.iloc[
                  i,
                  sig_clusters_summary_csv.columns.get_loc(f'{subj}_bbox_area_native')
            ] = (idxs[3] - idxs[0]) * (idxs[4] - idxs[1]) * (idxs[5] - idxs[2])

      sig_clusters_summary_csv.to_csv(os.path.join(out_dir, 'sig_clusters_summary.csv'))

# -------------------------------------------------------
# function to perform statistical test for comparing neuronal count for each cluster
# -------------------------------------------------------
def neuron_count_stats(sig_clusters_summary_csv_path, treated_group_subj_name, ctrl_group_subj_name, out_dir):
      sig_clusters_summary_csv = pd.read_csv(sig_clusters_summary_csv_path, index_col=0)
      clusters = sig_clusters_summary_csv["label"]    
      sig_clusters_summary_csv["mannwhitneyu_stats"] = 0
      sig_clusters_summary_csv["mannwhitneyu_pvalue"] = 0

      for i, cluster in enumerate(clusters):
            neurons_treated = []
            neurons_ctrl = []
            for subj in treated_group_subj_name:
                  neurons_treated.append(sig_clusters_summary_csv[f'neuron_count_{subj}'].iloc[i])
            for subj in ctrl_group_subj_name:
                  neurons_ctrl.append(sig_clusters_summary_csv[f'neuron_count_{subj}'].iloc[i])
            

            print(cluster, neurons_treated, neurons_ctrl)

            try:
                  stats, p = mannwhitneyu(neurons_treated, neurons_ctrl)      
            except:
                  stats, p = pd.NA, pd.NA
            sig_clusters_summary_csv.iloc[
                  i,
                  sig_clusters_summary_csv.columns.get_loc("mannwhitneyu_stats")
            ] = stats
            sig_clusters_summary_csv.iloc[
                  i,
                  sig_clusters_summary_csv.columns.get_loc("mannwhitneyu_pvalue")
            ] = p

      sig_clusters_summary_csv.to_csv(os.path.join(out_dir, 'sig_clusters_summary_with_stats.csv'))

# -------------------------------------------------------
# main function
# -------------------------------------------------------

def main():
      # -------------------------------------------------------
      # create paths
      # -------------------------------------------------------
      # Execute the parse_args() method
      args = vars(my_parser.parse_args())
      treated_dir = args['treated']
      ctrl_dir = args['ctrl']
      p_value = args['p_value']
      pvalue_thr = args['pvalue_thr']
      stats = args['stats']
      out_dir = args['out_dir']
      atl_dir = args['atlas_dir']
      mean_diff = args["mean_diff"]
      # create out dir
      isExist = os.path.exists(out_dir)
      if not isExist: os.mkdir(out_dir)

      grp_treated_subj_list_paths = [os.path.join(treated_dir, subj) for subj in os.listdir(treated_dir)]
      grp_ctrl_subj_list_paths = [os.path.join(ctrl_dir, subj) for subj in os.listdir(ctrl_dir)]      

      n_subj_treated = len(os.listdir(treated_dir))
      n_subj_ctrl = len(os.listdir(ctrl_dir))
      print(f"\n {n_subj_treated} treated and {n_subj_ctrl} ctrl subjects found ...")
      print(f"\n treated subjs: {os.listdir(treated_dir)} ctrl subjs: {os.listdir(ctrl_dir)}")

      #grp_treated_subj_list_reg_paths = [os.path.join(subj, "registration", os.path.basename(subj).lower() + "_downsample_10x_nii", "clar_allen_reg") for subj in grp_treated_subj_list_paths]
      grp_treated_subj_list_reg_paths = [os.path.join(subj, "registration", "clar_allen_reg") for subj in grp_treated_subj_list_paths]
    
      #grp_ctrl_subj_list_reg_paths = [os.path.join(subj, "registration", os.path.basename(subj).lower() + "_downsample_10x_nii", "clar_allen_reg") for subj in grp_ctrl_subj_list_paths]
      grp_ctrl_subj_list_reg_paths = [os.path.join(subj, "registration", "clar_allen_reg") for subj in grp_ctrl_subj_list_paths]

      print(f"\n clar_allen_reg paths have been created for all subjects")

      #grp_treated_subj_list_reg_orientation_paths = [os.path.join(subj,"orientation.txt") for subj in grp_treated_subj_list_paths]
      grp_treated_subj_list_reg_orientation_paths = [os.path.join(subj, "registration", "orientation.txt") for subj in grp_treated_subj_list_paths]
 
      #grp_ctrl_subj_list_reg_orientation_paths = [os.path.join(subj,"orientation.txt") for subj in grp_ctrl_subj_list_paths]
      grp_ctrl_subj_list_reg_orientation_paths = [os.path.join(subj,"registration", "orientation.txt") for subj in grp_ctrl_subj_list_paths]

      print(f"\n orientation paths have been created for all subjects")

      #grp_treated_subj_list_seg_file_paths = [os.path.join(subj, "ace_out.tif") for subj in grp_treated_subj_list_paths]
      grp_treated_subj_list_seg_file_paths = [os.path.join(subj, "ace_unetr_mc_out.tif") for subj in grp_treated_subj_list_paths]

      #grp_ctrl_subj_list_seg_file_paths = [os.path.join(subj, "ace_out.tif") for subj in grp_ctrl_subj_list_paths]
      grp_ctrl_subj_list_seg_file_paths = [os.path.join(subj, "ace_unetr_mc_out.tif") for subj in grp_ctrl_subj_list_paths]
     
      print(f"\n ACE seg paths have been created for all subjects")

      # -------------------------------------------------------
      # call warp_clusters_regionprops for each subject & loop
      # -------------------------------------------------------

      print('\n preprocessing pval')
      print("\n get atlas annotation file and label")
      ann_img_array, annotation_lbls = get_atls(atl_dir)

      # binarize_dialte_connected component_clusters
      dil_bin_pval = os.path.join(out_dir, 'p_values_bin_dilated.nii.gz')
      dil_bin_pval_comp = os.path.join(out_dir, 'p_values_bin_dilated_conncomp.nii.gz')
      dil_bin_pval_comp_fil = os.path.join(out_dir, 'p_values_bin_dilated_conncomp_filtered.nii.gz')
      
      pvals_img_arr, labeled_pvals = binarize_dialte_clusters(p_value, pvalue_thr, out_dir, dil_bin_pval, dil_bin_pval_comp, dil_bin_pval_comp_fil)    

      # create .csv at atlas space
      print("\n create a .csv summarizing signficant clusters at atlas space")
      data=compute_region_props(mode="atlas",
                          pval=pvals_img_arr,
                          mean_diff=nib.load(mean_diff).get_fdata(),
                          labeled_pval=labeled_pvals,
                          stats=nib.load(stats).get_fdata(),
                          out_dir=out_dir,
                          atl_ann=ann_img_array,
                          atl_ann_lbls=annotation_lbls)

      print('\n filtering p value and .csv to remove edge regions')


      ## add dilation
      #filter_clusters(data, labeled_pvals, nib.load(p_value), out_dir)

      print('\n warping p value to treated subjects native space')

      # for idx, subj in enumerate(grp_treated_subj_list_paths):

      #       # get the size of the raw image from segmentation file
      #       memmap_seg_file_shape = tifffile.memmap(grp_treated_subj_list_seg_file_paths[idx]).shape
      #       org_clar = f"{memmap_seg_file_shape[0]}x{memmap_seg_file_shape[1]}x{memmap_seg_file_shape[2]}"

      #       warped_cluster = f"p_values_bin_dilated_conncomp_filtered_warped_treated_{os.path.basename(subj)}"
      #       warp_sig_clusters(grp_treated_subj_list_reg_paths[idx],
      #                         dil_bin_pval_comp_fil,
      #                         grp_treated_subj_list_reg_orientation_paths[idx],
      #                         org_clar, 
      #                         out_dir,
      #                         warped_cluster)

      print('\n warping p value to control subjects native space')

      for idx, subj in enumerate(grp_ctrl_subj_list_paths):

            # get the size of the raw image from segmentation file
            memmap_seg_file_shape = tifffile.memmap(grp_ctrl_subj_list_seg_file_paths[idx]).shape
            org_clar = f"{memmap_seg_file_shape[0]}x{memmap_seg_file_shape[1]}x{memmap_seg_file_shape[2]}"

            warped_cluster = f"p_values_bin_dilated_conncomp_filtered_warped_ctrl_{os.path.basename(subj)}"
            warp_sig_clusters(grp_ctrl_subj_list_reg_paths[idx],
                              dil_bin_pval_comp_fil,
                              grp_ctrl_subj_list_reg_orientation_paths[idx],
                              org_clar, 
                              out_dir,
                              warped_cluster)


      print('\n counting neurons inside each cluster in the treated group')

      for idx, subj in enumerate(grp_treated_subj_list_paths):

            # get the size of the raw image from segmentation file
            seg_file = grp_treated_subj_list_seg_file_paths[idx]

            warped_cluster_dir = os.path.join(out_dir, f"p_values_bin_dilated_conncomp_filtered_warped_treated_{os.path.basename(subj)}_tiff_clar")
            command = f'python /data2/projects/Ahmadreza/ACE_reviewer_response_experiments/stats/validate_clusters/test_memmap.py \
                  -s {seg_file} \
                  -l {warped_cluster_dir} \
                  -o {out_dir + "/" + os.path.basename(subj)}'
            subprocess.Popen(command, shell=True).wait()

      print('\n counting neurons inside each cluster in the ctrl group')

      for idx, subj in enumerate(grp_ctrl_subj_list_paths):

            # get the size of the raw image from segmentation file
            seg_file = grp_ctrl_subj_list_seg_file_paths[idx]

            warped_cluster_dir = os.path.join(out_dir, f"p_values_bin_dilated_conncomp_filtered_warped_ctrl_{os.path.basename(subj)}_tiff_clar")

            command = f'python /data2/projects/Ahmadreza/ACE_reviewer_response_experiments/stats/validate_clusters/test_memmap.py \
                  -s {seg_file} \
                  -l {warped_cluster_dir} \
                  -o {out_dir + "/" + os.path.basename(subj)}'
            subprocess.Popen(command, shell=True).wait()

      print('\n summarizing neuron count per subjects in the .csv file')
      for idx, subj in enumerate(grp_treated_subj_list_paths):
            summarize_neuron_count_to_csv(os.path.join(out_dir + "/" + os.path.basename(subj), "neuron_info_with_label.json"),
                                          os.path.basename(subj),
                                          out_dir,
                                          os.path.join(out_dir, 'sig_clusters_summary.csv'))
      
      for idx, subj in enumerate(grp_ctrl_subj_list_paths):
            summarize_neuron_count_to_csv(os.path.join(out_dir + "/" + os.path.basename(subj), "neuron_info_with_label.json"),
                                          os.path.basename(subj),
                                          out_dir,
                                          os.path.join(out_dir, 'sig_clusters_summary.csv'))

      print('\n running statistc between two group for each cluster')
      neuron_count_stats(os.path.join(out_dir, 'sig_clusters_summary.csv'),
                        os.listdir(treated_dir), 
                        os.listdir(ctrl_dir),
                        out_dir)


if __name__ == '__main__':
    main()

