"""

This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca & Maged Goubran, maged.goubran@utoronto.ca
This function reads voxelized warped images & performs cluster based permutation tests

"""
import argparse
import os
import pickle
import nibabel as nib
import sys
import multiprocessing            
from nilearn.input_data import NiftiMasker
from nilearn.image import concat_imgs, smooth_img
from sklearn.feature_selection import VarianceThreshold
import fnmatch
import numpy as np
from mne.stats import spatio_temporal_cluster_test,ttest_ind_no_p
from sklearn.feature_extraction.image import grid_to_graph
from joblib import Parallel, delayed
from datetime import datetime
import mne
import scipy.ndimage as scp
from scipy.stats import mannwhitneyu, ttest_ind, kruskal, f_oneway
from miracl_workflow_ace_parser import ACEWorkflowParser

# # Create the parser
# my_parser = argparse.ArgumentParser(description='Working directory')
#
# # Add the arguments
# my_parser.add_argument('-wild','--wild_type', help='wild type group directory (should contain warped voxelized nifti files)', required=True)
# my_parser.add_argument('-dis','--disease', help='disease group directory (should contain warped voxelized nifti files)', required=True)
# my_parser.add_argument('-out','--output', help='path of output directory', required=True)
# my_parser.add_argument('-atl_dir','--atlas_dir', help='path of atlas directory', default='miracl_home')
# my_parser.add_argument('-n', '--num_perm', type=int, help="number of permutations", default=100)
# my_parser.add_argument('-res', '--img_resolution', type=int, help="resolution of images in um", default=25)
# my_parser.add_argument('-fwhm', '--smoothing_fwhm', type=int, help="fwhm of Gaussian kernel in pixel", default=3)
# my_parser.add_argument('-tfce_start', '--tfce_start', type=float, help="tfce threshold start", default=0.01)
# my_parser.add_argument('-tfce_step', '--tfce_step', type=float, help="tfce threshold step", default=10)
# my_parser.add_argument('-cpus', '--cpu_load', type=float, help="Percent of cpus used for parallelization", default=0.9)
# my_parser.add_argument('-tfce_h', '--tfce_h', type=float, help="tfce H power", default=2)
# my_parser.add_argument('-tfce_e', '--tfce_e', type=float, help="tfce E power", default=0.5)
# my_parser.add_argument('-stp', '--step_down_p', type=float, help="step_down_p value", default=0.3)
# my_parser.add_argument('-mask_thr', '--mask_thr', type=int, help="percentile to be used for binarizing difference of the mean", default=95)

my_parser = ACEWorkflowParser()
# Execute the parse_args() method
args = vars(my_parser.parse_args())

# Get the arguments
wild_dir = args['_pcs_wild_type']
dis_dir = args['_pcs_disease']
out_dir = args['_pcs_output']
num_perm = args['_pcs_num_perm']
atl_dir = args['_pcs_atlas_dir']
img_res = args['_pcs_img_resolution']
smoothing_fwhm = args['_pcs_smoothing_fwhm']
tfce_start = args['_pcs_tfce_start']
tfce_step = args['_pcs_tfce_step']
tfce_h = args['_pcs_tfce_h']
tfce_e = args['_pcs_tfce_e']
cpuload = args['_pcs_cpu_load']
stp = args['_pcs_step_down_p']
mask_thr = args['_pcs_mask_thr']

sys.exit()

cpus = multiprocessing.cpu_count()
ncpus = int(cpuload * cpus)  # 90% default of cores used

# create out dir
isExist = os.path.exists(out_dir)
if not isExist: os.mkdir(out_dir)

# function for preprocessing the images
def pre_processing_func(img_filename, input_dir, output_dir, grp, mask):
    
    img = nib.load(os.path.join(input_dir, img_filename))
    # smoothing the input image
    img = smooth_img(img, (smoothing_fwhm*img_res/1000.0))

    # change data to ndarray       
    img_ndarray = img.get_fdata().astype(np.float32)
    #img_ndarray = img.get_fdata()
    
    # print("image max: ", img_ndarray.max())
    # print("image min: ", img_ndarray.min())
    # print("image std: ", img_ndarray.std())

    # get the masked mean value 
    masked_mean = np.mean(img_ndarray, where = mask.astype('bool'))
    #masked_std = np.std(img_ndarray, where = mask.astype(np.bool))
    #print("image masked mean: ", masked_mean)
    #print("image masked std: ", masked_std)

    img_ndarray = img_ndarray / masked_mean
    #img_ndarray = img_ndarray - masked_mean / masked_std
    #print("image max: ", img_ndarray.max())
    #print("image min: ", img_ndarray.min())

    nib.save(nib.Nifti1Image(img_ndarray, img.affine, img.header), os.path.join(output_dir, grp + '_processed_' + img_filename))
    
    
# -------------------------------------------------------
# load and prepare atl
# -------------------------------------------------------

# find the atl directory
if atl_dir == 'miracl_home':
    atl_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen/template'
    ann_dir = '/data/projects/Ahmadreza/stats/scripts/Atl/Allen/annotation'
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

print('mask shape: ', mask_img_array.shape)

# -------------------------------------------------------
# load / prepare data
# -------------------------------------------------------

startTime = datetime.now()

# load wild images
wild_imgs = fnmatch.filter(os.listdir(wild_dir), '*.nii.gz')
wild_imgs.sort()

# only keep a quarter of an image for testing
print("pre processing group 1 ...")
for img in wild_imgs:
    pre_processing_func(img, wild_dir, out_dir, 'wild', mask_img_array)

# update the wild_images list after cropping
wild_imgs = fnmatch.filter(os.listdir(out_dir), 'wild_processed*.nii.gz')
wild_imgs.sort()
print('found #', len(wild_imgs), 'pre-preocessed wild type images!')

# load dis images
dis_imgs = fnmatch.filter(os.listdir(dis_dir), '*.nii.gz')
dis_imgs.sort()

# only keep a quarter of an image for testing
print("pre processing group 2 ...")
for img in dis_imgs:
    pre_processing_func(img, dis_dir, out_dir, 'dis', mask_img_array)
    
# update the dis_images list after cropping
dis_imgs = fnmatch.filter(os.listdir(out_dir), 'dis_processed*.nii.gz')
dis_imgs.sort()
print('found #', len(dis_imgs), 'pre-processed disease type images!')



# -------------------------------------------------------
# compute mean of disease and wild type images + differences of the mean
# -------------------------------------------------------

# compute the mean of wild type images
print('compute the mean of wild type images')

# load the wild images into an array
wild_img_list = []

for img_name in wild_imgs:
    img = nib.load(os.path.join(out_dir, img_name))
    wild_imgs_header = img.header
    wild_imgs_affine = img.affine
    img = img.get_fdata()
    #print(img.dtype)
    # multiply with atlas
    img = np.multiply(img, mask_img_array)  
    wild_img_list.append(img)
    
wild_imgs_array = np.stack(wild_img_list, axis = 3)
print('wild_imgs_array shape: ', wild_imgs_array.shape)

del wild_img_list # to reduce memory usage

wild_imgs_mean = np.mean(wild_imgs_array, axis = 3)
wild_imgs_std = np.std(wild_imgs_array, axis = 3)

print('wild_imgs_mean shape: ', wild_imgs_mean.shape)

# save the wild_imgs_mean and std
nib.save(nib.Nifti1Image(wild_imgs_mean, wild_imgs_affine, wild_imgs_header),
         os.path.join(out_dir, 'wild_imgs_mean.nii.gz'))
nib.save(nib.Nifti1Image(wild_imgs_std, wild_imgs_affine, wild_imgs_header),
         os.path.join(out_dir, 'wild_imgs_std.nii.gz'))

# compute the mean of disease type images
print('compute the mean of disease type images')

# load the wild images into an array
dis_img_list = []

for img_name in dis_imgs:
    img = nib.load(os.path.join(out_dir, img_name))
    dis_imgs_header = img.header
    dis_imgs_affine = img.affine
    img = img.get_fdata()
    # multiply with atlas
    img = np.multiply(img, mask_img_array)  
    dis_img_list.append(img)
    
    
    
dis_imgs_array = np.stack(dis_img_list, axis = 3)
print('dis_imgs_array shape: ', dis_imgs_array.shape)
del dis_img_list # to reduce memory usage

dis_imgs_mean = np.mean(dis_imgs_array, axis = 3)
dis_imgs_std = np.std(dis_imgs_array, axis = 3)
print('dis_imgs_mean shape: ', dis_imgs_mean.shape)

# save the dis_imgs_mean and std
nib.save(nib.Nifti1Image(dis_imgs_mean, dis_imgs_affine, dis_imgs_header),
                         os.path.join(out_dir, 'dis_imgs_mean.nii.gz'))
nib.save(nib.Nifti1Image(dis_imgs_std, dis_imgs_affine, dis_imgs_header),
                         os.path.join(out_dir, 'dis_imgs_std.nii.gz'))

# compute the mean of disease type images
print('compute the difference of means')
diff_mean = np.subtract(dis_imgs_mean, wild_imgs_mean)

# save the diff_mean
nib.save(nib.Nifti1Image(diff_mean, dis_imgs_affine, dis_imgs_header),
                         os.path.join(out_dir, 'diff_mean.nii.gz'))
print('diff_mean shape: ', diff_mean.shape)

# # smooth the diff_mean
# diff_mean_smooth = nib.load(os.path.join(out_dir, 'diff_mean.nii'))
# diff_mean_smooth = smooth_img(diff_mean_smooth, (smoothing_fwhm*img_res/1000.0))

# # save the diff_mean smooth version
# nib.save(diff_mean_smooth, os.path.join(out_dir, 'diff_mean_smooth.nii'))


del wild_imgs_mean # to reduce memory usage
del dis_imgs_mean # to reduce memory usage
del wild_imgs_std # to reduce memory usage
del dis_imgs_std # to reduce memory usage
# del diff_mean # to reduce memory usage
del wild_imgs_array # to reduce memory usage
del dis_imgs_array # to reduce memory usage


# -------------------------------------------------------
# create a mask based on diff_mean
# -------------------------------------------------------

mask_diff_mean_arr = np.zeros_like(diff_mean).astype(np.uint8)
print('diff_mean max and min: ', diff_mean.max(), diff_mean.min())

thr = np.percentile(diff_mean[diff_mean > 0.001], mask_thr)
print('diff_mean 95 percentile + values: ', thr)

mask_diff_mean_arr[diff_mean > thr] = 1

thr = np.percentile(diff_mean[diff_mean < -0.001], 100-mask_thr)
print('diff_mean 5 percentile - values: ', thr)
mask_diff_mean_arr[diff_mean < thr] = 1

# removing small objects
#mask_diff_mean_arr = scp.binary_opening(mask_diff_mean_arr, iterations=1).astype(np.uint8)

# dilating the objects
#mask_diff_mean_arr = scp.binary_dilation(mask_diff_mean_arr, iterations=1).astype(np.uint8)

# save the mask_diff_mean
nib.save(nib.Nifti1Image(mask_diff_mean_arr, dis_imgs_affine, dis_imgs_header),
                         os.path.join(out_dir, 'mask_diff_mean.nii.gz'))
print('mask_diff_mean shape: ', mask_diff_mean_arr.shape)
mask_diff_mean = nib.load(os.path.join(out_dir, 'mask_diff_mean.nii.gz'))

# -------------------------------------------------------
# start statistics 
# -------------------------------------------------------
# concatenate two groups images
all_vols = wild_imgs + dis_imgs
# print(all_vols)
all_vols = [os.path.join(out_dir, file) for file in all_vols]
all_vols_imgs = [nib.load(file) for file in all_vols]
#all_vols = concat_imgs(all_vols)

temp_img = nib.load(os.path.join(out_dir, wild_imgs[0]))

# -------------------------------------------------------
# stat function 
# -------------------------------------------------------
def stat_fun_ttest(args1, args2):
    # get t-values only.
    return ttest_ind_no_p(
        args1,
        args2,
        equal_var=False,
    )
def stat_fun_f_oneway(args1, args2):
    # get t-values only.
    return f_oneway(
        args1,
        args2,
    )[0]
def stat_fun_mann(args1, args2):
    # get t-values only.
    return mannwhitneyu(
        args1,
        args2,
        alternative='two-sided'
    )[0]
def stat_fun_ttest_ind(args1, args2):
    # get t-values only.
    return ttest_ind(
        args1,
        args2,
        #alternative='greater',
        equal_var=False
    )[0]
def stat_fun_kruskal(args1, args2):
    # get t-values only.
    return kruskal(
        args1, args2
    )[0]

def cluster_fn(slice, all_vols_imgs, mask_img_array, mask_img, num_perm, f_obs_slices, cluster_pv_slices):
    

    #sys.stdout.write("\r statistcal test on slice #%d ..." % slice)
    sys.stdout.flush()
    
    # print("statistcal test on slice #", slice, "...")
    #print("------------------------------------")

    all_vols_slices = []
    for img in all_vols_imgs:

        #img = nib.load(file)
        img_slice = img.slicer[slice:slice+1, :, :]
        #print("image slice shape: ", img_slice.shape)
        all_vols_slices.append(img_slice)


    # create an adj where each pixel is connected to its neighbors and also mask the image to only work on where brain is
    #adj = grid_to_graph(mask_img_array.shape[1], mask_img_array.shape[2], mask=mask_img_array[slice, :, :])

    adj = grid_to_graph(mask_diff_mean_arr.shape[1], mask_diff_mean_arr.shape[2], mask=mask_diff_mean_arr[slice, :, :])
    print('adj shape: ', adj.shape)



    # check if the data contains at least thr voxel inside the brain
    thr = 50
    if adj.shape[0] > thr: 


        # create nifti masker
        print('Applying NiftiMasker')
        #nifti_masker = NiftiMasker(mask_img=mask_img.slicer[slice:slice+1, :, :], standardize=False, memory='nilearn_cache')
        nifti_masker = NiftiMasker(mask_img=mask_diff_mean.slicer[slice:slice+1, :, :], standardize=True, memory='nilearn_cache')

        # apply nifit masker
        data = nifti_masker.fit_transform(concat_imgs(all_vols_slices))
        print('data shape: ', data.shape)

        eps = 0.001
        
        if data.max() > eps:


            # variance threshold
            # print('Applying VarianceThreshold')
           
            #print('min var', np.var(data, axis=1).min())
            #print('mean var', np.var(data, axis=1).mean())
            #print('max var', np.var(data, axis=1).max())

            #var = np.var(data, axis=1).mean()

            #variance_threshold = VarianceThreshold(threshold=var)
            #thresh_data = variance_threshold.fit_transform(data)
            
            thresh_data = data
            #print('thresh_data shape: ', thresh_data.shape)

                
            # preparing the data for cluster test; data should be subject x time x spatial info
            thresh_data = np.expand_dims(thresh_data, axis = 1)
            print('thresh_data shape: ', thresh_data.shape)

            #raise ValueError
            # Permutation Cluster Test
            mne.set_cache_dir('nilearn_cache')


            ############ applying simple stats tests voxel-wise for debugging
            # t_stats_temp, p_value_temp = ttest_ind(thresh_data[0:len(wild_imgs),], thresh_data[len(wild_imgs):,], equal_var=False)
            # print("applying voxelwise ttest: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp), 
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))

            # t_stats_temp, p_value_temp = mannwhitneyu(thresh_data[0:len(wild_imgs),], thresh_data[len(wild_imgs):,],
            #                             alternative='two-sided')
            # print("applying voxelwise mannwhitneyu: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp), 
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))
            # t_stats_temp, p_value_temp = kruskal(thresh_data[0:len(wild_imgs),], thresh_data[len(wild_imgs):,])
            # print("applying voxelwise kruskal: min: ",
            #        np.min(t_stats_temp),
            #        " max: ", np.max(t_stats_temp), 
            #        " min p value: ", np.min(p_value_temp),
            #        " N voxels sig: ", np.sum(p_value_temp < 0.05))
            # t_stats_temp, p_value_temp = f_oneway(thresh_data[0:len(wild_imgs),], thresh_data[len(wild_imgs):,])
            # print("applying voxelwise f_oneway: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp), 
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))                  
            ######################
            
            threshold_tfce = dict(start=float(tfce_start), step=float(tfce_step), h_power=tfce_h, e_power=tfce_e) # h=1 ans e = 1 to find more
            f_obs, clusters, cluster_pv, H0 = spatio_temporal_cluster_test(
                                                    [thresh_data[0:len(wild_imgs),], thresh_data[len(wild_imgs):,]],
                                                    #thresh_data[len(wild_imgs):,],
                                                    threshold=threshold_tfce,
                                                    adjacency=adj,
                                                    out_type='mask',
                                                    n_permutations=num_perm,
                                                    buffer_size=100000,
                                                    tail=0,
                                                    n_jobs=ncpus, 
                                                    #stat_fun=stat_fun_kruskal,
                                                    step_down_p=stp,
                                                    #max_step = 50,
                                                    #t_power = 0
                                                    )


            cluster_pv = -1 * np.log10(cluster_pv) # 0.05 woll be -1.3
            if cluster_pv.max() > 1.3: print("H0 is rejected!")
            print("Max p value on slice #", slice, ": ", cluster_pv.max())

            #print('Applying niftimasker inverse transform')
            print("------------------------------------")
            p_values = np.expand_dims(cluster_pv, axis=0)
            f_obs = np.nan_to_num(f_obs)

            #pvals_unmasked = nifti_masker.inverse_transform(variance_threshold.inverse_transform(p_values))
            pvals_unmasked = nifti_masker.inverse_transform(p_values)
            # pvals_unmasked has the shape of (1, height, width, 1)
            pvals_unmasked = pvals_unmasked.get_fdata()[0,:,:,0]
            #f_obs_unmasked = nifti_masker.inverse_transform(variance_threshold.inverse_transform(f_obs))
            f_obs_unmasked = nifti_masker.inverse_transform(f_obs)
            f_obs_unmasked = f_obs_unmasked.get_fdata()[0,:,:,0]

            # f_obs_slices.append(f_obs_unmasked)
            # cluster_pv_slices.append(pvals_unmasked)
            # clusters_slices.append(clusters)
            # H0_slices.append(H0)

        else:

            print("this slice contains values less than %f ... skipping stats" %eps)
            print("------------------------------------")
            f_obs_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
            pvals_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
            
            # f_obs_slices.append(f_obs_unmasked)
            # cluster_pv_slices.append(pvals_unmasked)
            # clusters_slices.append([])
            # H0_slices.append([])

    else:

        print("this slice contains less than %d voxels inside the brain ... skipping stats" %thr)
        print("------------------------------------")
        f_obs_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
        pvals_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
        
        # f_obs_slices.append(f_obs_unmasked)
        # cluster_pv_slices.append(pvals_unmasked)
        # clusters_slices.append([])
        # H0_slices.append([])


    f_obs_slices[slice, :, :] =  f_obs_unmasked
    cluster_pv_slices[slice, :, :] =  pvals_unmasked
       

# -------------------------------------------------------
# Parallelize clustering function 
# -------------------------------------------------------

# statistics results

clusters_slices, H0_slices = [], []

f_memap = os.path.join(out_dir,'tmp_f_array_memmap.map')
p_memap = os.path.join(out_dir,'tmp_p_array_memmap.map')

f_obs_slices = np.memmap(f_memap, dtype=np.float32, shape=(temp_img.shape[0], temp_img.shape[1], temp_img.shape[2]), mode='w+')
cluster_pv_slices = np.memmap(p_memap, dtype=np.float32, shape=(temp_img.shape[0], temp_img.shape[1], temp_img.shape[2]), mode='w+')

print('Running in parallel using %s cpus ...' % ncpus) 

#Parallel(n_jobs=ncpus, backend="threading")(delayed(cluster_fn)(
Parallel(n_jobs=ncpus)(delayed(cluster_fn)(
              s, all_vols_imgs, mask_img_array, mask_img, num_perm, f_obs_slices, cluster_pv_slices) for s in range(temp_img.shape[0]))
              #s, all_vols_imgs, mask_img_array, mask_img, num_perm, f_obs_slices, cluster_pv_slices) for s in range(221,225))

print("saving Nifti files")
nib.save(nib.Nifti1Image(f_obs_slices, temp_img.affine, temp_img.header), os.path.join(out_dir, 'f_obs.nii.gz'))
nib.save(nib.Nifti1Image(cluster_pv_slices, temp_img.affine, temp_img.header), os.path.join(out_dir, 'p_values.nii.gz'))
print("saving results into a pickle file")

with open(os.path.join(out_dir, "results.pickle"), 'wb') as f:
    pickle.dump([f_obs_slices, clusters_slices, cluster_pv_slices, H0_slices], f)

# remove tmp memmaps
os.remove(f_memap)
os.remove(p_memap)

end_str = "\n Parallel cluster permutation-based stats done in %s ... Have a good day!\n" % (datetime.now() - startTime)

print(end_str)

with open('log_thread.txt', 'a') as f:
    f.write(end_str)

