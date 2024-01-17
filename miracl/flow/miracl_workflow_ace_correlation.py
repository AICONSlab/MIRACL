"""
This code is written by Ahmadreza Attarpour, a.attarpour@mail.utoronto.ca
This function reads reads p value of clusters obtained by cluster-wise permutation test & summarize information of each cluster

"""
import argparse
import os
import sys
import pickle
import nibabel as nib
import numpy as np
import scipy.ndimage as scp
from skimage import measure
import pandas as pd
import fnmatch
# from scipy.stats import pearsonr, permutation_test
from scipy.stats import pearsonr
import scipy.stats as ss
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.utils import resample

# # -------------------------------------------------------
# # create parser
# # -------------------------------------------------------
# my_parser = argparse.ArgumentParser(description="Working directory")
#
# # Add the arguments
# my_parser.add_argument(
#     "-p", "--p_value", help="p_value nii image should be -log(p)", required=True
# )
# my_parser.add_argument(
#     "-s",
#     "--stats",
#     help="stats nii image should be e. g. f statistic map",
#     required=True,
# )
# my_parser.add_argument(
#     "-diff", "--mean_diff", help="mean diff of two groups nii image", required=True
# )
# my_parser.add_argument(
#     "-out", "--output", help="path of output directory", required=True
# )
# my_parser.add_argument(
#     "-atl_dir", "--atlas_dir", help="path of atlas directory", default="miracl_home"
# )
# my_parser.add_argument(
#     "-res", "--img_resolution", type=int, help="resolution of images in um", default=25
# )
# my_parser.add_argument(
#     "-thr",
#     "--pvalue_thr",
#     type=float,
#     help="threshold for binarizing p value",
#     default=0.05,
# )
# my_parser.add_argument(
#     "-exp",
#     "--experiment",
#     type=str,
#     help="experiment dir either cold or walking",
#     default="walking",
# )
#
#
# # Execute the parse_args() method
# args = vars(my_parser.parse_args())


def main(args, output_dir_arg, p_value_arg, stats_arg, mean_diff_arg):
    p_value = p_value_arg
    stats = stats_arg
    mean_diff = mean_diff_arg
    out_dir = output_dir_arg
    atl_dir = args.u_atlas_dir
    img_res = args.rca_voxel_size
    thr = args.cf_pvalue_thr
    # exp = args["experiment"]

    print(f"p_value: {p_value_arg}")
    print(f"stats: {stats_arg}")
    print(f"mean_diff: {mean_diff_arg}")
    print(f"out_dir: {output_dir_arg}")
    print(f"atl_dir: {args.u_atlas_dir}")
    print(f"img_res: {args.rca_voxel_size}")
    print(f"thr: {args.cf_pvalue_thr}")

    sys.exit()

    # -------------------------------------------------------
    # load and prepare atl
    # -------------------------------------------------------

    # find the atl directory
    if atl_dir == "miracl_home":
        atl_dir = "/data/projects/Ahmadreza/stats/scripts/Atl/Allen/template"
        ann_dir = "/data/projects/Ahmadreza/stats/scripts/Atl/Allen/annotation"
        lbl_dir = "/data/projects/Ahmadreza/stats/scripts/Atl/Allen"
        # atl_dir = '/data3/projects/Ahmadreza/deepneuronseg/dataset/dataset3/walking_exp/cluster_test/atlas_sliced'
        # ann_dir = '/data3/projects/Ahmadreza/deepneuronseg/dataset/dataset3/walking_exp/cluster_test/atlas_sliced'

    mask_filename = f"average_template_{img_res}um_brainmask.nii.gz"
    ann_filename = f"annotation_hemi_combined_{img_res}um.nii.gz"

    # load the atlas
    if img_res == 10:
        ann_img = nib.load(os.path.join(ann_dir, ann_filename))
        ann_img_array = ann_img.get_fdata()
        mask_img = np.ones_like(ann_img_array)
        mask_img[ann_img_array == 0] = 0
        nib.save(
            nib.Nifti1Image(mask_img, ann_img.affine, ann_img.header),
            os.path.join(out_dir, "brain_mask_10um.nii.gz"),
        )

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

    lbl_dir = "/data/projects/Ahmadreza/stats/scripts/Atl/Allen"

    annotation_lbls = pd.read_csv(
        os.path.join(lbl_dir, "ara_mouse_structure_graph_hemi_combined.csv"),
    )
    selected_columns = ["id", "name"]
    annotation_lbls = annotation_lbls[selected_columns]

    # Display the DataFrame
    # print(annotation_lbls['lbl_name'])
    print("annotation_lbls: ", annotation_lbls)
    print("mask shape: ", mask_img_array.shape)
    ann_img_array = ann_img_array.astype("int")
    # -------------------------------------------------------
    # load and prepare images
    # -------------------------------------------------------
    grp_treated = []
    grp_ctrl = []
    if exp == "walking":
        grp_treated_dir = "/data/projects/Ahmadreza/stats/walking_exp_warped_voxelized_imgs/seg_warp_25um_corrected/walking"
        grp_ctrl_dir = "/data/projects/Ahmadreza/stats/walking_exp_warped_voxelized_imgs/seg_warp_25um_corrected/non_walking"

        grp_treated_imgs_list = fnmatch.filter(os.listdir(grp_treated_dir), "*.nii.gz")
        grp_ctrl_imgs_list = fnmatch.filter(os.listdir(grp_ctrl_dir), "*.nii.gz")

        for img in grp_treated_imgs_list:
            # normalize data similar strategy used in cluster analysis
            img_ndarray = nib.load(os.path.join(grp_treated_dir, img)).get_fdata()
            # masked_mean = np.mean(img_ndarray, where = mask_img_array.astype('bool'))
            # img_ndarray = img_ndarray / masked_mean

            grp_treated.append(img_ndarray)
        for img in grp_ctrl_imgs_list:
            # normalize data similar strategy used in cluster analysis
            img_ndarray = nib.load(os.path.join(grp_ctrl_dir, img)).get_fdata()
            # masked_mean = np.mean(img_ndarray, where = mask_img_array.astype('bool'))
            # img_ndarray = img_ndarray / masked_mean

            grp_ctrl.append(img_ndarray)
    else:
        grp_treated_dir = "/data/projects/Ahmadreza/stats/cold_exp_warped_voxelized_imgs/seg_warp_25um_corrected/4c_25um_corrected"
        grp_ctrl_dir = "/data/projects/Ahmadreza/stats/cold_exp_warped_voxelized_imgs/seg_warp_25um_corrected/30c_25um_corrected"

        grp_treated_imgs_list = fnmatch.filter(os.listdir(grp_treated_dir), "*.nii.gz")
        grp_ctrl_imgs_list = fnmatch.filter(os.listdir(grp_ctrl_dir), "*.nii.gz")

        for img in grp_treated_imgs_list:
            # normalize data similar strategy used in cluster analysis
            img_ndarray = nib.load(os.path.join(grp_treated_dir, img)).get_fdata()
            # masked_mean = np.mean(img_ndarray, where = mask_img_array.astype('bool'))
            # img_ndarray = img_ndarray / masked_mean

            grp_treated.append(img_ndarray)

        for img in grp_ctrl_imgs_list:
            # normalize data similar strategy used in cluster analysis
            img_ndarray = nib.load(os.path.join(grp_ctrl_dir, img)).get_fdata()
            # masked_mean = np.mean(img_ndarray, where = mask_img_array.astype('bool'))
            # img_ndarray = img_ndarray / masked_mean

            grp_ctrl.append(img_ndarray)

    print("grp_treated_dir", grp_treated_dir)
    print("grp_ctrl_dir", grp_ctrl_dir)

    # -------------------------------------------------------
    # load and prepare stats images
    # -------------------------------------------------------
    mean_diff_img_nii = nib.load(mean_diff)
    mean_diff_img_arr = mean_diff_img_nii.get_fdata()

    pvals_img_nii = nib.load(p_value)
    pvals_img_arr = pvals_img_nii.get_fdata()

    stats_img_nii = nib.load(stats)
    stats_img_arr = stats_img_nii.get_fdata()
    print(
        "shape pvalue: ",
        pvals_img_arr.shape,
        "pvalue min: ",
        pvals_img_arr.min(),
        " pvalue max: ",
        pvals_img_arr.max(),
    )

    # binarize pval
    thr = -np.log10(thr)
    pvals_img_arr_bin = np.zeros_like(pvals_img_arr, dtype="bool")
    pvals_img_arr_bin[pvals_img_arr > thr] = True
    nib.save(
        nib.Nifti1Image(
            pvals_img_arr_bin.astype(np.uint8),
            pvals_img_nii.affine,
            pvals_img_nii.header,
        ),
        os.path.join(out_dir, "p_values_bin.nii.gz"),
    )

    # dilate binarized pval
    pvals_img_arr_bin_d = scp.binary_dilation(pvals_img_arr_bin, iterations=1).astype(
        np.uint8
    )
    nib.save(
        nib.Nifti1Image(
            pvals_img_arr_bin_d.astype(np.uint8),
            pvals_img_nii.affine,
            pvals_img_nii.header,
        ),
        os.path.join(out_dir, "p_values_bin_dilated.nii.gz"),
    )

    # dilate slice by slice
    # pvals_img_arr_bin_d = np.zeros_like(pvals_img_arr_bin, dtype = 'bool')
    # for i in range(pvals_img_arr_bin.shape[0]):
    #     temp = pvals_img_arr_bin[i, : , :]
    #     temp_dilated = scp.binary_dilation(temp, structure = scp.generate_binary_structure(2,2), iterations=1)
    #     pvals_img_arr_bin_d[i, :, :] = temp_dilated
    # nib.save(nib.Nifti1Image(pvals_img_arr_bin_d.astype(np.uint8), pvals_img_nii.affine, pvals_img_nii.header),
    #           os.path.join(out_dir, 'p_values_bin_dilated.nii.gz'))

    # remove small clusters
    # pvals_img_arr_bin_d_o = scp.binary_opening(pvals_img_arr_bin_d, iterations=1).astype(np.uint8)
    # nib.save(nib.Nifti1Image(pvals_img_arr_bin_d_o.astype(np.uint8), pvals_img_nii.affine, pvals_img_nii.header),
    #          os.path.join(out_dir, 'p_values_bin_dilated_open.nii.gz'))

    # Generate a structuring element that will consider features connected even if they touch diagonally
    s = np.ones((3, 3, 3))
    # print("structure for turning pvals to label: ", s)
    # Change the pval_sig map to label
    labeled_pvals, num_clusters_sig = scp.label(
        pvals_img_arr_bin_d.astype(np.uint8), structure=s
    )

    # get clusters info
    prop_list = (
        "coords",
        "centroid",
        "area",
        "intensity_mean",
        "intensity_max",
        "intensity_min",
    )

    cluster_props = measure.regionprops_table(
        label_image=labeled_pvals,
        intensity_image=mean_diff_img_arr,
        properties=prop_list,
    )

    # get pvalue assosciated to each cluster
    prop_list = ("intensity_mean", "intensity_max", "intensity_min")
    cluster_props_temp = measure.regionprops_table(
        label_image=labeled_pvals, intensity_image=pvals_img_arr, properties=prop_list
    )

    data = pd.DataFrame(cluster_props)
    data["pval_mean"] = cluster_props_temp["intensity_mean"]
    data["pval_max"] = cluster_props_temp["intensity_max"]
    data["pval_min"] = cluster_props_temp["intensity_min"]

    # get statistic assosciated to each cluster
    prop_list = ("intensity_mean", "intensity_max", "intensity_min")
    cluster_props_temp = measure.regionprops_table(
        label_image=labeled_pvals, intensity_image=stats_img_arr, properties=prop_list
    )

    data["effect_size_mean"] = cluster_props_temp["intensity_mean"]
    data["effect_size_max"] = cluster_props_temp["intensity_max"]
    data["effect_size_min"] = cluster_props_temp["intensity_min"]

    # find the labels of each cluster
    data["cluster_lbl_values"] = np.zeros_like(data["area"]).astype(object)
    data["cluster_lbl_names"] = np.zeros_like(data["area"]).astype(object)
    data["cluster_lbl_areas_percent"] = np.zeros_like(data["area"]).astype(object)
    data["grp_treated_mean_intensity"] = np.zeros_like(data["area"]).astype(object)
    data["grp_ctrl_mean_intensity"] = np.zeros_like(data["area"]).astype(object)

    for i in range(len(data["coords"])):
        # get the regions of the brain each cluster takes

        cluster_coords = data["coords"][i]
        cluster_lbls = [ann_img_array[tuple(coord)] for coord in cluster_coords]
        cluster_lbls.sort()
        cluster_lbl_values, counts = np.unique(cluster_lbls, return_counts=True)
        cluster_lbl_areas_percent = counts / data["area"][i]
        cluster_lbl_names = []
        for value in cluster_lbl_values:
            try:
                cluster_name = list(annotation_lbls["id"]).index(value)
                cluster_lbl_names.append(annotation_lbls["name"][cluster_name])
            except ValueError:
                cluster_lbl_names.append("unknown")
        data["cluster_lbl_values"][i] = cluster_lbl_values
        data["cluster_lbl_names"][i] = cluster_lbl_names
        data["cluster_lbl_areas_percent"][i] = cluster_lbl_areas_percent

        # get the values of image intensity per subject in each cluster
        intensity_mean_grp_treated = []
        for img_ndarray in grp_treated:
            intensity_mean_grp_treated.append(
                np.mean([img_ndarray[tuple(coord)] for coord in cluster_coords])
            )

        data["grp_treated_mean_intensity"][i] = intensity_mean_grp_treated

        intensity_mean_grp_ctrl = []
        for img_ndarray in grp_ctrl:
            intensity_mean_grp_ctrl.append(
                np.mean([img_ndarray[tuple(coord)] for coord in cluster_coords])
            )

        data["grp_ctrl_mean_intensity"][i] = intensity_mean_grp_ctrl

    # sort data based on area
    data = data.sort_values(by="intensity_max", ascending=False)
    print(data)

    # Save the DataFrame to a CSV file
    data.to_csv(os.path.join(out_dir, "clusters_summary.csv"))

    data = data.drop(columns=["coords"])
    # data.to_csv(os.path.join(out_dir, 'clusters_summary_readable.csv'))

    # -------------------------------------------------------
    # correlation analysis
    # -------------------------------------------------------
    # get the correlation between most important clusters
    # set a threshold to how many sig clusters be used for correlation analysis

    N_thr = 22
    # to_del = [3, 6, 13, 14, 15, 18, 25, 28, 33, 36]

    # data.iloc[80], data.iloc[16] = data.iloc[16], data.iloc[80]
    # data.iloc[56], data.iloc[5] = data.iloc[5], data.iloc[56]

    # data.to_csv(os.path.join(out_dir, 'clusters_summary_readable.csv'))

    # delete small clusters
    column_name = "area"
    thr = 100
    rows_to_delete = data[data[column_name] < thr].index
    data = data.drop(rows_to_delete)

    # delete clusters with intensity_min of zero (edge regions)
    column_name = "intensity_min"
    # Filter rows where the value in the specified column is less than 100
    rows_to_delete = data[data[column_name] == 0].index
    data = data.drop(rows_to_delete)

    # delete selected areas
    # for cold exp
    # to_del = [185, 187, 7, 166, 4, 169, 172, 168, 97]
    # for i in to_del:
    #     data = data.drop(i)

    # data.iloc[29], data.iloc[21] = data.iloc[21], data.iloc[29]

    data.to_csv(os.path.join(out_dir, "clusters_summary_readable.csv"))

    # start correlation
    treated_values = np.array(data["grp_treated_mean_intensity"].tolist())
    ctrl_values = np.array(data["grp_ctrl_mean_intensity"].tolist())

    # treated_values = np.array([treated_values[i] for i in range(len(treated_values)) if i not in to_del])
    # ctrl_values = np.array([ctrl_values[i] for i in range(len(ctrl_values)) if i not in to_del])

    if len(treated_values) > N_thr:
        treated_values = treated_values[:N_thr]
        ctrl_values = ctrl_values[:N_thr]

    corr_matrix = np.ones((len(treated_values), len(treated_values)))
    pvalue_matrix = np.zeros((len(treated_values), len(treated_values)))

    # # Calculate correlation coefficients and p-values
    # for i in range(len(treated_values)):
    #     for j in range(i):
    #         corr, pvalue = pearsonr(np.concatenate((treated_values[i], ctrl_values[i])), np.concatenate((treated_values[j], ctrl_values[j])))
    #         # corr, pvalue = pearsonr(treated_values[i], treated_values[j])
    #         # corr2 = np.corrcoef(treated_values[i], treated_values[j])[0, 1]
    #         print(i, j, corr, pvalue, treated_values[i], treated_values[j])
    #         corr_matrix[i, j] = corr
    #         pvalue_matrix[i, j] = pvalue
    #         corr_matrix[j, i] = corr
    #         pvalue_matrix[j, i] = pvalue

    # def my_corr(x, y):
    #     corr, pvalue = pearsonr(x, y)
    #     return corr

    # for i in range(len(treated_values)):
    #     for j in range(i):

    #         corr_bootstrap = permutation_test((np.concatenate((treated_values[i], ctrl_values[i])), np.concatenate((treated_values[j], ctrl_values[j]))),
    #                                             my_corr,
    #                                             permutation_type='pairings')

    #         # corr_bootstrap = permutation_test((treated_values[i], treated_values[j]),
    #         #                                     my_corr,
    #         #                                     permutation_type='pairings',
    #         #                                     n_resamples=100000)

    #         corr_matrix[i, j] = corr_bootstrap.statistic
    #         pvalue_matrix[i, j] = corr_bootstrap.pvalue
    #         corr_matrix[j, i] = corr_bootstrap.statistic
    #         pvalue_matrix[j, i] = corr_bootstrap.pvalue

    for i in range(len(treated_values)):
        for j in range(i):
            rng = np.random.default_rng()
            method = ss.PermutationMethod(n_resamples=np.inf, random_state=rng)
            res = pearsonr(
                np.concatenate((treated_values[i], ctrl_values[i])),
                np.concatenate((treated_values[j], ctrl_values[j])),
                method=method,
            )
            method = ss.BootstrapMethod(method="BCa", random_state=rng)
            low, high = res.confidence_interval(confidence_level=0.8, method=method)
            print(
                i,
                j,
                res.statistic,
                low,
                high,
                res.pvalue,
                treated_values[i],
                treated_values[j],
            )
            corr_matrix[i, j] = low
            pvalue_matrix[i, j] = res.pvalue
            corr_matrix[j, i] = low
            pvalue_matrix[j, i] = res.pvalue

    print("correaltion matrix size: ", corr_matrix.shape)
    print("pvalue matrix size: ", pvalue_matrix.shape)

    correlation_matrix_df = pd.DataFrame(
        corr_matrix, index=data.index[:N_thr], columns=data.index[:N_thr]
    )
    pvalue_matrix_df = pd.DataFrame(
        pvalue_matrix, index=data.index[:N_thr], columns=data.index[:N_thr]
    )

    # -------------------------------------------------------
    # distance analysis
    # -------------------------------------------------------
    # calculate Euclidean distance between clusters
    # Extract the relevant columns
    # N_thr_dis = N_thr + len(to_del)
    N_thr_dis = N_thr
    columns = ["centroid-0", "centroid-1", "centroid-2"]
    df = data.head(N_thr_dis)[columns].values

    # df = np.array([df[i] for i in range(len(df)) if i not in to_del])

    # Calculate the pairwise Euclidean distances
    distances = pdist(df, metric="euclidean")

    # Create a square distance matrix
    distance_matrix = squareform(distances)

    # Create a DataFrame from the distance matrix
    distance_matrix_df = pd.DataFrame(
        distance_matrix, index=data.index[:N_thr], columns=data.index[:N_thr]
    )
    # print(distance_df)
    print("distance matrix size: ", distance_matrix_df.shape)

    # -------------------------------------------------------
    # plot the results
    # -------------------------------------------------------

    # obtaining x- and y- label
    # ticklabels = []
    # for i in range(N_thr):
    #     label_idx = np.argmax(data['cluster_lbl_areas_percent'].tolist()[i])
    #     ticklabels.append(data['cluster_lbl_names'].tolist()[i][label_idx])

    # Filter data based on p-values
    index = data.index[:N_thr_dis]
    # index = [index[i] for i in range(len(index)) if i not in to_del]
    columns = data.index[:N_thr_dis]
    # columns = [columns[i] for i in range(len(columns)) if i not in to_del]

    significant_mask = pvalue_matrix < 0.05
    significant_correlation_matrix = np.where(
        significant_mask, correlation_matrix_df, np.nan
    )
    significant_correlation_matrix_df = pd.DataFrame(
        significant_correlation_matrix, index=index, columns=columns
    )

    significant_distance_matrix = np.where(significant_mask, distance_matrix_df, np.nan)
    significant_distance_matrix_df = pd.DataFrame(
        significant_distance_matrix, index=index, columns=columns
    )

    # Set up subplots
    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

    # Plot correlation matrix with heatmap
    sns.heatmap(
        significant_correlation_matrix_df,
        cmap="coolwarm",
        linewidth=0.5,
        annot=True,
        annot_kws={"fontsize": 4, "fontweight": "bold"},
        cbar=True,
        ax=axes[0],
        xticklabels=True,
        yticklabels=True,
    )
    axes[0].set_title("Correlation Coefficient")

    # Plot p-values with heatmap
    sns.heatmap(
        pvalue_matrix_df,
        cmap="RdBu_r",
        annot=True,
        linewidth=0.5,
        annot_kws={"fontsize": 4, "fontweight": "bold"},
        cbar=True,
        ax=axes[1],
        xticklabels=True,
        yticklabels=True,
    )

    axes[1].set_title("P-values")

    # Plot distance matrix with heatmap
    # sns.heatmap(significant_distance_matrix_df, cmap="Blues", annot=True, annot_kws={"fontsize":4}, cbar=True, ax=axes[2],  xticklabels = True, yticklabels= True)
    sns.heatmap(
        significant_distance_matrix_df,
        linewidth=0.5,
        cmap="Blues",
        cbar=True,
        ax=axes[2],
        xticklabels=True,
        yticklabels=True,
    )
    axes[2].set_title("Euclidean Distance")

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save or show the plot
    # plt.savefig(os.path.join(out_dir,'corr_analysis_sig.png'), dpi = 600)
    # plt.show()

    # combine correaltion and distance plots
    mask1 = np.triu(np.ones_like(significant_correlation_matrix, dtype=bool))
    mask2 = np.tril(np.ones_like(significant_distance_matrix, dtype=bool))

    # Set up subplots
    fig, ax = plt.subplots(figsize=(11, 9))
    # Plot correlation matrix with heatmap
    sns.heatmap(
        significant_correlation_matrix_df,
        mask=mask1,
        square=True,
        cmap="coolwarm",
        linecolor="gray",
        linewidth=0.5,
        annot=True,
        annot_kws={"fontsize": 5, "fontweight": "bold"},
        cbar=True,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
    )

    # Plot distance matrix with heatmap
    # sns.heatmap(significant_distance_matrix_df, cmap="Blues", annot=True, annot_kws={"fontsize":4}, cbar=True, ax=axes[2],  xticklabels = True, yticklabels= True)
    sns.heatmap(
        significant_distance_matrix_df,
        mask=mask2,
        square=True,
        linewidth=0.5,
        annot=True,
        annot_kws={"fontsize": 5, "fontweight": "bold"},
        linecolor="gray",
        cmap=sns.cubehelix_palette(as_cmap=True),
        cbar=True,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
        fmt=".1f",
    )

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save or show the plot
    plt.savefig(
        os.path.join(
            out_dir, "corr_analysis_sig_combined_effect_size_edited_alpha05.png"
        ),
        dpi=600,
    )
    # plt.show()

    significant_mask = pvalue_matrix < 0.01
    significant_correlation_matrix = np.where(
        significant_mask, correlation_matrix_df, np.nan
    )
    significant_correlation_matrix_df = pd.DataFrame(
        significant_correlation_matrix, index=index, columns=columns
    )

    significant_distance_matrix = np.where(significant_mask, distance_matrix_df, np.nan)
    significant_distance_matrix_df = pd.DataFrame(
        significant_distance_matrix, index=index, columns=columns
    )

    # combine correaltion and distance plots
    mask1 = np.triu(np.ones_like(significant_correlation_matrix, dtype=bool))
    mask2 = np.tril(np.ones_like(significant_distance_matrix, dtype=bool))

    # Set up subplots
    fig, ax = plt.subplots(figsize=(11, 9))
    # Plot correlation matrix with heatmap
    sns.heatmap(
        significant_correlation_matrix_df,
        mask=mask1,
        square=True,
        cmap="coolwarm",
        linecolor="gray",
        linewidth=0.5,
        annot=True,
        annot_kws={"fontsize": 5, "fontweight": "bold"},
        cbar=True,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
    )

    # Plot distance matrix with heatmap
    # sns.heatmap(significant_distance_matrix_df, cmap="Blues", annot=True, annot_kws={"fontsize":4}, cbar=True, ax=axes[2],  xticklabels = True, yticklabels= True)
    sns.heatmap(
        significant_distance_matrix_df,
        mask=mask2,
        square=True,
        linewidth=0.5,
        annot=True,
        annot_kws={"fontsize": 5, "fontweight": "bold"},
        linecolor="gray",
        cmap=sns.cubehelix_palette(as_cmap=True),
        cbar=True,
        ax=ax,
        xticklabels=True,
        yticklabels=True,
        fmt=".1f",
    )

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Save or show the plot
    plt.savefig(
        os.path.join(
            out_dir, "corr_analysis_sig_combined_effect_size_edited_alpha01.png"
        ),
        dpi=600,
    )
