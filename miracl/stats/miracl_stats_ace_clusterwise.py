"""
This code is written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca),
Maged Goubran (maged.goubran@utoronto.ca) and Jonas Osmann
(j.osmann@mail.utoronto.ca). This function reads voxelized warped images and
performs cluster based permutation tests
"""

from pathlib import Path
import os
import pickle
import nibabel as nib
import sys
import multiprocessing
from nilearn.maskers import NiftiMasker
from nilearn.image import concat_imgs, smooth_img
from sklearn.feature_selection import VarianceThreshold
import fnmatch
import numpy as np
from mne.stats import spatio_temporal_cluster_test, ttest_ind_no_p
from sklearn.feature_extraction.image import grid_to_graph
from joblib import Parallel, delayed
from datetime import datetime
import mne
import scipy.ndimage as scp
from scipy.stats import mannwhitneyu, ttest_ind, kruskal, f_oneway
from miracl.flow.miracl_workflow_ace_parser import ACEWorkflowParser
from collections import defaultdict

# my_parser = ACEWorkflowParser()
# args = my_parser.parse_args()


# -------------------------------------------------------
# function for preprocessing the images
# -------------------------------------------------------
def pre_processing_func(
    img_filename, input_dir, output_dir, grp, mask, smoothing_fwhm, img_res
):
    img = nib.load(os.path.join(input_dir, img_filename))
    # smoothing the input image
    img = smooth_img(img, (smoothing_fwhm * img_res / 1000.0))

    # change data to ndarray
    img_ndarray = img.get_fdata().astype(np.float32)
    # img_ndarray = img.get_fdata()

    # print("image max: ", img_ndarray.max())
    # print("image min: ", img_ndarray.min())
    # print("image std: ", img_ndarray.std())

    # get the masked mean value
    masked_mean = np.mean(img_ndarray, where=mask.astype("bool"))
    # masked_std = np.std(img_ndarray, where = mask.astype(np.bool))
    # print("image masked mean: ", masked_mean)
    # print("image masked std: ", masked_std)

    img_ndarray = img_ndarray / masked_mean
    # img_ndarray = img_ndarray - masked_mean / masked_std
    # print("image max: ", img_ndarray.max())
    # print("image min: ", img_ndarray.min())
    img_filename = str(img_filename).replace("/", "_")
    nib.save(
        nib.Nifti1Image(img_ndarray, img.affine, img.header),
        os.path.join(output_dir, grp + "_processed_" + img_filename),
    )


# -------------------------------------------------------
# stat functions
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
    return mannwhitneyu(args1, args2, alternative="two-sided")[0]


def stat_fun_ttest_ind(args1, args2):
    # get t-values only.
    return ttest_ind(
        args1,
        args2,
        # alternative='greater',
        equal_var=False,
    )[0]


def stat_fun_kruskal(args1, args2):
    # get t-values only.
    return kruskal(args1, args2)[0]


def cluster_fn(
    slice,
    all_vols_imgs,
    mask_img_array,
    mask_img,
    num_perm,
    f_obs_slices,
    cluster_pv_slices,
    mask_diff_mean_arr,
    mask_diff_mean,
    tfce_start,
    tfce_step,
    tfce_h,
    tfce_e,
    ncpus,
    stp,
    control_imgs,
    out_dir,
):
    # sys.stdout.write("\r statistcal test on slice #%d ..." % slice)
    sys.stdout.flush()

    # print("statistcal test on slice #", slice, "...")
    # print("------------------------------------")

    all_vols_slices = []
    for img in all_vols_imgs:
        # img = nib.load(file)
        img_slice = img.slicer[slice : slice + 1, :, :]
        # print("image slice shape: ", img_slice.shape)
        all_vols_slices.append(img_slice)

    # create an adj where each pixel is connected to its neighbors and also mask the image to only work on where brain is
    # adj = grid_to_graph(mask_img_array.shape[1], mask_img_array.shape[2], mask=mask_img_array[slice, :, :])

    adj = grid_to_graph(
        mask_diff_mean_arr.shape[1],
        mask_diff_mean_arr.shape[2],
        mask=mask_diff_mean_arr[slice, :, :],
    )
    print("adj shape: ", adj.shape)

    # check if the data contains at least thr voxel inside the brain
    thr = 50
    if adj.shape[0] > thr:
        # create nifti masker
        print("Applying NiftiMasker")
        # nifti_masker = NiftiMasker(mask_img=mask_img.slicer[slice:slice+1, :, :], standardize=False, memory='nilearn_cache')
        nilearn_cache_dir = str(Path(out_dir) / "nilearn_cache")
        nifti_masker = NiftiMasker(
            mask_img=mask_diff_mean.slicer[slice : slice + 1, :, :],
            standardize=True,
            memory=nilearn_cache_dir,
        )

        # apply nifit masker
        data = nifti_masker.fit_transform(concat_imgs(all_vols_slices))
        print("data shape: ", data.shape)

        eps = 0.001

        if data.max() > eps:
            # variance threshold
            # print('Applying VarianceThreshold')

            # print('min var', np.var(data, axis=1).min())
            # print('mean var', np.var(data, axis=1).mean())
            # print('max var', np.var(data, axis=1).max())

            # var = np.var(data, axis=1).mean()

            # variance_threshold = VarianceThreshold(threshold=var)
            # thresh_data = variance_threshold.fit_transform(data)

            thresh_data = data
            # print('thresh_data shape: ', thresh_data.shape)

            # preparing the data for cluster test; data should be subject x time x spatial info
            thresh_data = np.expand_dims(thresh_data, axis=1)
            print("thresh_data shape: ", thresh_data.shape)

            # raise ValueError
            # Permutation Cluster Test
            mne.set_cache_dir(nilearn_cache_dir)

            ############ applying simple stats tests voxel-wise for debugging
            # t_stats_temp, p_value_temp = ttest_ind(thresh_data[0:len(control_imgs),], thresh_data[len(control_imgs):,], equal_var=False)
            # print("applying voxelwise ttest: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp),
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))

            # t_stats_temp, p_value_temp = mannwhitneyu(thresh_data[0:len(control_imgs),], thresh_data[len(control_imgs):,],
            #                             alternative='two-sided')
            # print("applying voxelwise mannwhitneyu: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp),
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))
            # t_stats_temp, p_value_temp = kruskal(thresh_data[0:len(control_imgs),], thresh_data[len(control_imgs):,])
            # print("applying voxelwise kruskal: min: ",
            #        np.min(t_stats_temp),
            #        " max: ", np.max(t_stats_temp),
            #        " min p value: ", np.min(p_value_temp),
            #        " N voxels sig: ", np.sum(p_value_temp < 0.05))
            # t_stats_temp, p_value_temp = f_oneway(thresh_data[0:len(control_imgs),], thresh_data[len(control_imgs):,])
            # print("applying voxelwise f_oneway: min: ",
            #       np.min(t_stats_temp),
            #       " max: ", np.max(t_stats_temp),
            #       " min p value: ", np.min(p_value_temp),
            #       " N voxels sig: ", np.sum(p_value_temp < 0.05))
            ######################

            threshold_tfce = dict(
                start=float(tfce_start),
                step=float(tfce_step),
                h_power=tfce_h,
                e_power=tfce_e,
            )  # h=1 ans e = 1 to find more
            f_obs, clusters, cluster_pv, H0 = spatio_temporal_cluster_test(
                [thresh_data[0 : len(control_imgs),], thresh_data[len(control_imgs) :,]],
                # thresh_data[len(control_imgs):,],
                threshold=threshold_tfce,
                adjacency=adj,
                out_type="mask",
                n_permutations=num_perm,
                buffer_size=100000,
                tail=0,
                n_jobs=ncpus,
                # stat_fun=stat_fun_kruskal,
                step_down_p=stp,
                # max_step = 50,
                # t_power = 0
            )

            cluster_pv = -1 * np.log10(cluster_pv)  # 0.05 woll be -1.3
            if cluster_pv.max() > 1.3:
                print("H0 is rejected!")
            print("Max p value on slice #", slice, ": ", cluster_pv.max())

            # print('Applying niftimasker inverse transform')
            print("------------------------------------")
            p_values = np.expand_dims(cluster_pv, axis=0)
            f_obs = np.nan_to_num(f_obs)

            # pvals_unmasked = nifti_masker.inverse_transform(variance_threshold.inverse_transform(p_values))
            pvals_unmasked = nifti_masker.inverse_transform(p_values)
            # pvals_unmasked has the shape of (1, height, width, 1)
            pvals_unmasked = pvals_unmasked.get_fdata()[0, :, :, 0]
            # f_obs_unmasked = nifti_masker.inverse_transform(variance_threshold.inverse_transform(f_obs))
            f_obs_unmasked = nifti_masker.inverse_transform(f_obs)
            f_obs_unmasked = f_obs_unmasked.get_fdata()[0, :, :, 0]

            # f_obs_slices.append(f_obs_unmasked)
            # cluster_pv_slices.append(pvals_unmasked)
            # clusters_slices.append(clusters)
            # H0_slices.append(H0)

        else:
            print("this slice contains values less than %f ... skipping stats" % eps)
            print("------------------------------------")
            f_obs_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
            pvals_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))

            # f_obs_slices.append(f_obs_unmasked)
            # cluster_pv_slices.append(pvals_unmasked)
            # clusters_slices.append([])
            # H0_slices.append([])

    else:
        print(
            "this slice contains less than %d voxels inside the brain ... skipping stats"
            % thr
        )
        print("------------------------------------")
        f_obs_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))
        pvals_unmasked = np.zeros((img_slice.shape[1], img_slice.shape[2]))

        # f_obs_slices.append(f_obs_unmasked)
        # cluster_pv_slices.append(pvals_unmasked)
        # clusters_slices.append([])
        # H0_slices.append([])

    f_obs_slices[slice, :, :] = f_obs_unmasked
    cluster_pv_slices[slice, :, :] = pvals_unmasked


def main(args, output_dir_arg):
    control_dir = args.pcs_control
    treated_dir = args.pcs_treated
    out_dir = output_dir_arg
    num_perm = args.sctp_num_perm
    atl_dir = args.u_atlas_dir
    img_res = args.rwc_voxel_size
    smoothing_fwhm = args.sctp_smoothing_fwhm
    tfce_start = args.sctp_tfce_start
    tfce_step = args.sctp_tfce_step
    tfce_h = args.sctp_tfce_h
    tfce_e = args.sctp_tfce_e
    cpuload = args.sctp_cpu_load
    stp = args.sctp_step_down_p
    mask_thr = args.sctp_mask_thr
    hemi = args.rca_hemi
    side = args.rca_side
    side = {"rh": "right", "lh": "left"}.get(side, None)

    cpus = multiprocessing.cpu_count()
    ncpus = int(cpuload * cpus)  # 90% default of cores used

    print("Running clusterwise stats with the following arguments:")
    print(f"  control_dir: {control_dir}")
    print(f"  treated_dir: {treated_dir}")
    print(f"  out_dir: {out_dir}")
    print(f"  num_perm: {num_perm}")
    print(f"  atl_dir: {atl_dir}")
    print(f"  img_res: {img_res}")
    print(f"  smoothing_fwhm: {smoothing_fwhm}")
    print(f"  tfce_start: {tfce_start}")
    print(f"  tfce_step: {tfce_step}")
    print(f"  tfce_h: {tfce_h}")
    print(f"  tfce_e: {tfce_e}")
    print(f"  cpuload: {cpuload}")
    print(f"  stp: {stp}")
    print(f"  mask_thr: {mask_thr}")
    print(f"  cpus: {cpus}")
    print(f"  ncpus: {ncpus}")
    print(f"  hemi: {hemi}")
    print(f"  side: {side}")

    # -------------------------------------------------------
    # load and prepare atl
    # -------------------------------------------------------

    # find the atl directory
    ann_dir = Path(atl_dir)
    atl_dir = Path(atl_dir)

    atl_dir = atl_dir / "template"
    ann_dir = ann_dir / "annotation"

    if hemi == "combined":
        mask_filename = f"average_template_{img_res}um_brainmask.nii.gz"
        ann_filename = f"annotation_hemi_combined_{img_res}um.nii.gz"
    elif hemi == "split":
        mask_filename = f"average_template_{img_res}um_brainmask_{side}.nii.gz"
        ann_filename = f"annotation_hemi_{side}_{img_res}um.nii.gz"

    # load the atlas
    # if img_res == 10:
    ann_img = nib.load(os.path.join(ann_dir, ann_filename))
    ann_img_array = ann_img.get_fdata()
    mask_img = np.ones_like(ann_img_array)
    mask_img[ann_img_array == 0] = 0
    nib.save(
        nib.Nifti1Image(mask_img, ann_img.affine, ann_img.header),
        os.path.join(out_dir, mask_filename),
    )

    mask_filename = os.path.join(out_dir, mask_filename)
    mask_img = nib.load(mask_filename)
    mask_img_array = mask_img.get_fdata()

    # else:
    #     ann_img = nib.load(os.path.join(ann_dir, ann_filename))
    #     ann_img_array = ann_img.get_fdata()
    #     mask_filename = os.path.join(atl_dir, mask_filename)
    #     mask_img = nib.load(mask_filename)
    #     mask_img_array = mask_img.get_fdata()

    print("mask shape: ", mask_img_array.shape)

    # -------------------------------------------------------
    # load / prepare data
    # -------------------------------------------------------

    startTime = datetime.now()

    # load control images
    if len(control_dir) > 1:
        control_warp_tiff_template = Path(control_dir[1])
        control_base_dir = Path(control_dir[0])
        control_warp_tiff_extension = Path(
            *control_warp_tiff_template.relative_to(control_base_dir).parts[1:]
        )
        control_imgs_regex = "*/" + control_warp_tiff_extension.as_posix()
        control_imgs = control_base_dir.glob(control_imgs_regex)
        control_imgs = [str(file.relative_to(control_base_dir)) for file in control_imgs]
        control_dir = control_base_dir
    else:
        control_dir = control_dir[0]
        control_imgs = fnmatch.filter(os.listdir(control_dir), "*.nii.gz")
        control_imgs.sort()

    # only keep a quarter of an image for testing
    print("pre processing group 1 ...")
    for img in control_imgs:
        pre_processing_func(
            img, control_dir, out_dir, "control", mask_img_array, smoothing_fwhm, img_res
        )

    # update the control_images list after cropping
    control_imgs = fnmatch.filter(os.listdir(out_dir), "control_processed*.nii.gz")
    control_imgs.sort()
    print("found #", len(control_imgs), "pre-processed control type images!")

    # load treated images
    if len(treated_dir) > 1:
        treated_warp_tiff_template = Path(treated_dir[1])
        treated_base_dir = Path(treated_dir[0])
        treated_warp_tiff_extension = Path(
            *treated_warp_tiff_template.relative_to(treated_base_dir).parts[1:]
        )
        trt_imgs_regex = "*/" + treated_warp_tiff_extension.as_posix()
        trt_imgs = treated_base_dir.glob(trt_imgs_regex)
        trt_imgs = [str(file.relative_to(treated_base_dir)) for file in trt_imgs]
        treated_dir = treated_base_dir
    else:
        treated_dir = treated_dir[0]
        trt_imgs = fnmatch.filter(os.listdir(treated_dir), "*.nii.gz")
        trt_imgs.sort()

    # only keep a quarter of an image for testing
    print("pre processing group 2 ...")
    for img in trt_imgs:
        pre_processing_func(
            img, treated_dir, out_dir, "trt", mask_img_array, smoothing_fwhm, img_res
        )

    # update the trt_images list after cropping
    trt_imgs = fnmatch.filter(os.listdir(out_dir), "trt_processed*.nii.gz")
    trt_imgs.sort()
    print("found #", len(trt_imgs), "pre-processed treatement type images!")

    # -------------------------------------------------------
    # compute mean of treatment and control type images + differences of the mean
    # -------------------------------------------------------

    # compute the mean of control type images
    print("compute the mean of control type images")

    # load the control images into an array
    control_img_list = []

    for img_name in control_imgs:
        img = nib.load(os.path.join(out_dir, img_name))
        control_imgs_header = img.header
        control_imgs_affine = img.affine
        img = img.get_fdata()
        # print(img.dtype)
        # multiply with atlas
        img = np.multiply(img, mask_img_array)
        control_img_list.append(img)

    control_imgs_array = np.stack(control_img_list, axis=3)
    print("control_imgs_array shape: ", control_imgs_array.shape)

    del control_img_list  # to reduce memory usage

    control_imgs_mean = np.mean(control_imgs_array, axis=3)
    control_imgs_std = np.std(control_imgs_array, axis=3)

    print("control_imgs_mean shape: ", control_imgs_mean.shape)

    # save the control_imgs_mean and std
    nib.save(
        nib.Nifti1Image(control_imgs_mean, control_imgs_affine, control_imgs_header),
        os.path.join(out_dir, "control_imgs_mean.nii.gz"),
    )
    nib.save(
        nib.Nifti1Image(control_imgs_std, control_imgs_affine, control_imgs_header),
        os.path.join(out_dir, "control_imgs_std.nii.gz"),
    )

    # compute the mean of treatment type images
    print("compute the mean of treatment type images")

    # load the control images into an array
    trt_img_list = []

    for img_name in trt_imgs:
        img = nib.load(os.path.join(out_dir, img_name))
        trt_imgs_header = img.header
        trt_imgs_affine = img.affine
        img = img.get_fdata()
        # multiply with atlas
        img = np.multiply(img, mask_img_array)
        trt_img_list.append(img)

    trt_imgs_array = np.stack(trt_img_list, axis=3)
    print("trt_imgs_array shape: ", trt_imgs_array.shape)
    del trt_img_list  # to reduce memory usage

    trt_imgs_mean = np.mean(trt_imgs_array, axis=3)
    trt_imgs_std = np.std(trt_imgs_array, axis=3)
    print("trt_imgs_mean shape: ", trt_imgs_mean.shape)

    # save the trt_imgs_mean and std
    nib.save(
        nib.Nifti1Image(trt_imgs_mean, trt_imgs_affine, trt_imgs_header),
        os.path.join(out_dir, "trt_imgs_mean.nii.gz"),
    )
    nib.save(
        nib.Nifti1Image(trt_imgs_std, trt_imgs_affine, trt_imgs_header),
        os.path.join(out_dir, "trt_imgs_std.nii.gz"),
    )

    # compute the mean of the differences
    print("compute the difference of means")
    diff_mean = np.subtract(trt_imgs_mean, control_imgs_mean)

    # save the diff_mean
    nib.save(
        nib.Nifti1Image(diff_mean, trt_imgs_affine, trt_imgs_header),
        os.path.join(out_dir, "diff_mean.nii.gz"),
    )
    print("diff_mean shape: ", diff_mean.shape)

    # # smooth the diff_mean
    # diff_mean_smooth = nib.load(os.path.join(out_dir, 'diff_mean.nii'))
    # diff_mean_smooth = smooth_img(diff_mean_smooth, (smoothing_fwhm*img_res/1000.0))

    # # save the diff_mean smooth version
    # nib.save(diff_mean_smooth, os.path.join(out_dir, 'diff_mean_smooth.nii'))

    del control_imgs_mean  # to reduce memory usage
    del trt_imgs_mean  # to reduce memory usage
    del control_imgs_std  # to reduce memory usage
    del trt_imgs_std  # to reduce memory usage
    # del diff_mean # to reduce memory usage
    del control_imgs_array  # to reduce memory usage
    del trt_imgs_array  # to reduce memory usage

    # -------------------------------------------------------
    # create a mask based on diff_mean
    # -------------------------------------------------------

    mask_diff_mean_arr = np.zeros_like(diff_mean).astype(np.uint8)
    print("diff_mean max and min: ", diff_mean.max(), diff_mean.min())

    thr = np.percentile(diff_mean[diff_mean > 0.001], mask_thr)
    print("diff_mean 95 percentile + values: ", thr)

    mask_diff_mean_arr[diff_mean > thr] = 1

    thr = np.percentile(diff_mean[diff_mean < -0.001], 100 - mask_thr)
    print("diff_mean 5 percentile - values: ", thr)
    mask_diff_mean_arr[diff_mean < thr] = 1

    # removing small objects
    # mask_diff_mean_arr = scp.binary_opening(mask_diff_mean_arr, iterations=1).astype(np.uint8)

    # dilating the objects
    # mask_diff_mean_arr = scp.binary_dilation(mask_diff_mean_arr, iterations=1).astype(np.uint8)

    # save the mask_diff_mean
    nib.save(
        nib.Nifti1Image(mask_diff_mean_arr, trt_imgs_affine, trt_imgs_header),
        os.path.join(out_dir, "mask_diff_mean.nii.gz"),
    )
    print("mask_diff_mean shape: ", mask_diff_mean_arr.shape)
    mask_diff_mean = nib.load(os.path.join(out_dir, "mask_diff_mean.nii.gz"))

    # -------------------------------------------------------
    # start statistics
    # -------------------------------------------------------
    # concatenate two groups images
    all_vols = control_imgs + trt_imgs
    # print(all_vols)
    all_vols = [os.path.join(out_dir, file) for file in all_vols]
    all_vols_imgs = [nib.load(file) for file in all_vols]
    # all_vols = concat_imgs(all_vols)

    temp_img = nib.load(os.path.join(out_dir, control_imgs[0]))

    # -------------------------------------------------------
    # Parallelize clustering function
    # -------------------------------------------------------

    # statistics results

    clusters_slices, H0_slices = [], []

    f_memap = os.path.join(out_dir, "tmp_f_array_memmap.map")
    p_memap = os.path.join(out_dir, "tmp_p_array_memmap.map")

    f_obs_slices = np.memmap(
        f_memap,
        dtype=np.float32,
        shape=(temp_img.shape[0], temp_img.shape[1], temp_img.shape[2]),
        mode="w+",
    )
    cluster_pv_slices = np.memmap(
        p_memap,
        dtype=np.float32,
        shape=(temp_img.shape[0], temp_img.shape[1], temp_img.shape[2]),
        mode="w+",
    )

    print("Running in parallel using %s cpus ..." % ncpus)

    # Parallel(n_jobs=ncpus, backend="threading")(delayed(cluster_fn)(
    Parallel(n_jobs=ncpus)(
        delayed(cluster_fn)(
            s,
            all_vols_imgs,
            mask_img_array,
            mask_img,
            num_perm,
            f_obs_slices,
            cluster_pv_slices,
            mask_diff_mean_arr,
            mask_diff_mean,
            tfce_start,
            tfce_step,
            tfce_h,
            tfce_e,
            ncpus,
            stp,
            control_imgs,
            out_dir,
        )
        for s in range(temp_img.shape[0])
    )
    # s, all_vols_imgs, mask_img_array, mask_img, num_perm, f_obs_slices, cluster_pv_slices) for s in range(221,225))

    print("saving Nifti files")
    nib.save(
        nib.Nifti1Image(f_obs_slices, temp_img.affine, temp_img.header),
        os.path.join(out_dir, "f_obs.nii.gz"),
    )
    nib.save(
        nib.Nifti1Image(cluster_pv_slices, temp_img.affine, temp_img.header),
        os.path.join(out_dir, "p_values.nii.gz"),
    )
    print("saving results into a pickle file")

    with open(os.path.join(out_dir, "results.pickle"), "wb") as f:
        pickle.dump([f_obs_slices, clusters_slices, cluster_pv_slices, H0_slices], f)

    # remove tmp memmaps
    os.remove(f_memap)
    os.remove(p_memap)

    end_str = f"\n  Parallel cluster permutation-based stats done in {datetime.now() - startTime} ... Have a good day!\n"

    print(end_str)

    log_thread_file_path = Path(out_dir) / "log_thread.txt"
    if log_thread_file_path.is_file():
        log_thread_file_path.unlink()

    with open(log_thread_file_path, "a") as f:
        f.write(end_str)
