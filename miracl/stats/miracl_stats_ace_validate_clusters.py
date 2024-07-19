import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import nibabel as nib
import numpy as np
import pandas as pd
import scipy.ndimage as scp
from scipy.stats import mannwhitneyu
from skimage import measure

from ..seg.miracl_seg_count_neurons_json import main as count_neurons_with_json
from .miracl_stats_ace_cluster_neuron_count import main as count_neurons_without_json

ATLAS_DIR = Path(os.environ.get("aradir"))
PROG_NAME = "ace_validate_clusters"
FULL_PROG_NAME = f"miracl stats {PROG_NAME}"


def parsefn():
    parser = argparse.ArgumentParser(
        prog=FULL_PROG_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""This function performs:
            1. Preprocess (binarize, dilate, and connected component analysis) the p value obtained by ACE cluster wise analysis
            2. warps the pvalue to the native space of each subject using transformation matrix;
            3. summarizes the information of each cluster at atlas space
            4. counts the neurons inside each cluster at native space and saves it in the .csv file
            5. run mann withney statistical test for each cluster using the neuronal count at native space to validate cluster
            """,
        add_help=False,
    )
    required_args = parser.add_argument_group("required arguments")
    optional_args = parser.add_argument_group("optional arguments")
    # Add the arguments
    required_args.add_argument(
        "-p",
        "--p_value",
        help="p_value nii image coming from `miracl stats ace` (clust_final/p_values.nii.gz)",
        required=True,
    )
    required_args.add_argument(
        "--path-to-ace-output",
        help="""relative path to get from subject folders (supplied by 
    --control and --treated) to the ace output folder 
    (e.g. some_path/final_ctn_down_10_rca_voxel_size_25/)""",
        required=True,
    )
    required_args.add_argument(
        "--path-to-raw-slices",
        help="""relative path to get from subject folders (supplied by
    --control and --treated) to the raw slices folder
    (e.g. some_path/raw_slices_tif/)""",
        required=True,
    )
    optional_args.add_argument(
        "--pvalue_thr",
        type=float,
        help="threshold for binarizing p value map (default: %(default)s)",
        default=0.01,
    )
    required_args.add_argument(
        "-f",
        "--f_stat",
        help="cluster wise TFCE F-statistic nifti image from `miracl stats ace (clust_final/f_obs.nii.gz)",
        required=True,
    )
    required_args.add_argument(
        "-d",
        "--mean_diff",
        help="mean diff of two groups nii image from `miracl stats ace` (clust_final/diff_mean.nii.gz)",
        required=True,
    )
    optional_args.add_argument(
        "--atlas_dir",
        help="path of atlas directory (default: %(default)s)",
        default=ATLAS_DIR,
    )
    required_args.add_argument(
        "-c",
        "--control",
        help="""path to control group; should have directories for each subject;
    each directory contains output from ACE""",
        required=True,
    )
    required_args.add_argument(
        "-t",
        "--treated",
        help="""path to treated group; should have directories for each subject;
    each directory contains output from ACE""",
        required=True,
    )
    required_args.add_argument(
        "--neuron-info-dir",
        help="""path to directory containing neuron information json files (if available)
    names of the json files should be the same as the subject names""",
        default=None,
    )
    required_args.add_argument(
        "--orient-code",
        help="orientation code of the image (same as used in registration)",
        required=True,
    )
    optional_args.add_argument(
        "-v",
        "--vox_size",
        type=int,
        choices=[10, 25, 50],
        help="voxel size of the atlas used in warping (default: %(default)s)",
        default=25,
    )
    optional_args.add_argument(
        "--hemi",
        help="hemisphere of the brain (default: %(default)s)",
        default="combined",
        choices=["split", "combined"],
    )
    optional_args.add_argument(
        "--side",
        help="side of the brain (default: %(default)s)",
        default=None,
        choices=["lh", "rh"],
    )
    optional_args.add_argument(
        "-o",
        "--output_dir",
        help="path of output directory (default: %(default)s)",
        default="validate_final",
    )
    optional_args.add_argument(
        "--min-area",
        type=int,
        help="minimum area of neuron to be considered in counting (default: %(default)s)",
        default=0,
    )
    optional_args.add_argument(
        "--skip",
        type=int,
        help="""number of slices to skip in the z direction from the front and
    back (default: %(default)s)""",
        default=50,
    )
    optional_args.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )

    return parser


class AtlasLoader:
    """Class for loading atlas template and annotation"""

    @staticmethod
    def load_atlas(
        atlas_dir: Path, out_dir: Path, hemi: str, side: str, img_res: int = 25
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        ann_dir = atlas_dir / "annotation"
        mask_dir = atlas_dir / "template"

        mask_filename = f"average_template_{img_res}um_brainmask.nii.gz"
        ann_filename = f"annotation_hemi_{hemi}_{img_res}um.nii.gz"

        # load the atlas
        if img_res == 10:
            ann_img = nib.load(ann_dir / ann_filename)
            ann_img_array = ann_img.get_fdata()
            # mask_img = np.ones_like(ann_img_array) # TODO: remove all mask img
            # mask_img[ann_img_array == 0] = 0
            # nib.save(
            #     nib.Nifti1Image(mask_img, ann_img.affine, ann_img.header),
            #     out_dir / f"brain_mask_{img_res}um.nii.gz",
            # )

            # mask_filename = out_dir / f"brain_mask_{img_res}um.nii.gz"
            # mask_img = nib.load(mask_filename)
            # mask_img_array = mask_img.get_fdata()

        else:
            ann_img = nib.load(ann_dir / ann_filename)
            ann_img_array = ann_img.get_fdata()
            # mask_filename = mask_dir / mask_filename
            # mask_img = nib.load(mask_filename)
            # mask_img_array = mask_img.get_fdata()

        annotation_lbls = pd.read_csv(
            atlas_dir / f"ara_mouse_structure_graph_hemi_{hemi}.csv",
        )
        selected_columns = ["id", "name"]
        annotation_lbls = annotation_lbls[selected_columns]

        ann_img_array = ann_img_array.astype(np.int_)
        return ann_img_array, annotation_lbls


class PreProcessClusters:
    """Class for pre=processing clusters"""

    @staticmethod
    def binarize_dialte_clusters(
        p_value_path: Path,
        thr: float,
        out_dir: Path,
        niter: int = 3,
        size_threshold: int = 0,
    ) -> Tuple[np.ndarray, np.ndarray, Path]:
        # set up output files
        bin_pval_path = out_dir / "p_values_bin.nii.gz"
        dil_bin_pval_path = out_dir / "p_values_binary_dilated.nii.gz"
        dil_bin_pval_conn_comp_path = (
            out_dir / "p_values_binary_dilated_conn_comp.nii.gz"
        )
        dil_bin_pval_conn_comp_filtered_path = (
            out_dir / "p_values_binary_dilated_conn_comp_filtered.nii.gz"
        )

        pvals_img_nii = nib.load(p_value_path)
        pvals_img_arr = pvals_img_nii.get_fdata()

        # binarize pval
        thr = -np.log10(thr)
        pvals_img_arr_bin = pvals_img_arr > thr
        nib.save(
            nib.Nifti1Image(
                pvals_img_arr_bin, pvals_img_nii.affine, pvals_img_nii.header
            ),
            bin_pval_path,
        )

        # dilate binarized pval
        pvals_img_arr_bin_d = scp.binary_dilation(
            pvals_img_arr_bin, iterations=niter
        ).astype(np.uint8)
        nib.save(
            nib.Nifti1Image(
                pvals_img_arr_bin_d.astype(np.bool_),
                pvals_img_nii.affine,
                pvals_img_nii.header,
            ),
            dil_bin_pval_path,
        )

        s = np.ones((3, 3, 3))
        labeled_pvals, _ = scp.label(pvals_img_arr_bin_d, structure=s)

        nib.save(
            nib.Nifti1Image(labeled_pvals, pvals_img_nii.affine, pvals_img_nii.header),
            dil_bin_pval_conn_comp_path,
        )

        # Calculate the size of each label
        label_sizes = np.bincount(labeled_pvals.ravel())

        # Filter labels based on size
        labels_to_keep = np.where(label_sizes >= size_threshold)[0]

        # Create a mask to select only the labeled components we want to keep
        mask = np.isin(labeled_pvals, labels_to_keep)  # TODO: make sure this works

        # Apply the mask to the labeled array
        filtered_labeled_pvals = np.where(mask, labeled_pvals, 0)

        nib.save(
            nib.Nifti1Image(
                filtered_labeled_pvals, pvals_img_nii.affine, pvals_img_nii.header
            ),
            dil_bin_pval_conn_comp_filtered_path,
        )

        pvals_img_arr[filtered_labeled_pvals == 0] = 0

        return (
            pvals_img_arr,
            filtered_labeled_pvals,
            dil_bin_pval_conn_comp_filtered_path,
        )


class ClusterWarperToClar:
    """Class for warping clusters to clar space"""

    @staticmethod
    def warp_sig_clusters(
        reg_dir: Path,
        dil_bin_pval_comp_fil: Path,
        ort_file: Path,
        org_clar: Path,
        out_dir: Path,
        out_lbl: Path,
        interpolation: str = "NearestNeighbor",
        lbl_type: str = "ushort",
    ):
        warp_cmd = f"miracl lbls warp_clar \
            -r {reg_dir} \
            -l {dil_bin_pval_comp_fil} \
            -o {ort_file} \
            -c {org_clar} \
            -d {out_dir} \
            -f {out_lbl} \
            -i {interpolation} \
            -t {lbl_type}"

        subprocess.Popen(warp_cmd, shell=True).wait()


class NeuronCounter:
    """Class for working with neuron counts
    This includes counting neurons and summarizing them"""

    def __init__(self, json=False):
        self._json = json

    def set_json(self, value):
        self._json = value

    def init_neuron_count_args(
        self,
        treated_subj_list_paths: Optional[List[Path]] = None,
        control_subj_list_paths: Optional[List[Path]] = None,
        treated_subj_list_seg_file_paths: Optional[List[Path]] = None,
        control_subj_list_seg_file_paths: Optional[List[Path]] = None,
        treated_subj_list_warped_clusters_dirs: Optional[List[Path]] = None,
        control_subj_list_warped_clusters_dirs: Optional[List[Path]] = None,
        treated_subj_list_json_paths: Optional[List[Path]] = None,
        control_subj_list_json_paths: Optional[List[Path]] = None,
        out_dir: Optional[Path] = None,
        min_area: Optional[int] = 0,
        skip: Optional[int] = 50,
        hemi: Optional[str] = "combined",
    ):
        self.treated_subj_list_paths = treated_subj_list_paths
        self.control_subj_list_paths = control_subj_list_paths
        self.treated_subj_list_seg_file_paths = treated_subj_list_seg_file_paths
        self.control_subj_list_seg_file_paths = control_subj_list_seg_file_paths
        self.treated_subj_list_warped_clusters_dirs = (
            treated_subj_list_warped_clusters_dirs
        )
        self.control_subj_list_warped_clusters_dirs = (
            control_subj_list_warped_clusters_dirs
        )
        self.treated_subj_list_json_paths = treated_subj_list_json_paths
        self.control_subj_list_json_paths = control_subj_list_json_paths
        self.out_dir = out_dir
        self.min_area = min_area
        self.skip = skip
        self.hemi = hemi

    def run_neuron_count(self):
        if self._json:
            return self._neuron_count_with_json(
                treated_subj_list_paths=self.treated_subj_list_paths,
                control_subj_list_paths=self.control_subj_list_paths,
                treated_subj_list_warped_clusters_dirs=self.treated_subj_list_warped_clusters_dirs,
                control_subj_list_warped_clusters_dirs=self.control_subj_list_warped_clusters_dirs,
                treated_subj_list_json_paths=self.treated_subj_list_json_paths,
                control_subj_list_json_paths=self.control_subj_list_json_paths,
                out_dir=self.out_dir,
                min_area=self.min_area,
                skip=self.skip,
                hemi=self.hemi,
            )
        else:
            return self._neuron_count_without_json(
                treated_subj_list_paths=self.treated_subj_list_paths,
                control_subj_list_paths=self.control_subj_list_paths,
                treated_subj_list_seg_file_paths=self.treated_subj_list_seg_file_paths,
                control_subj_list_seg_file_paths=self.control_subj_list_seg_file_paths,
                treated_subj_list_warped_clusters_dirs=self.treated_subj_list_warped_clusters_dirs,
                control_subj_list_warped_clusters_dirs=self.control_subj_list_warped_clusters_dirs,
                out_dir=self.out_dir,
                min_area=self.min_area,
                skip=self.skip,
            )

    def _neuron_count_with_json(
        self,
        treated_subj_list_paths: List[Path],
        control_subj_list_paths: List[Path],
        treated_subj_list_warped_clusters_dirs: List[Path],
        control_subj_list_warped_clusters_dirs: List[Path],
        treated_subj_list_json_paths: List[Path],
        control_subj_list_json_paths: List[Path],
        out_dir: Path,
        min_area: Optional[int] = 0,
        skip: Optional[int] = 50,
        hemi: Optional[str] = "combined",
    ):
        treated_subj_list_json_paths = []
        for idx, subj in enumerate(treated_subj_list_paths):
            # create namespace for neuron counting
            count_neurons_json_namespace = argparse.Namespace(
                lbl=treated_subj_list_warped_clusters_dirs[idx],
                min_area=min_area,
                max_area=1000000,
                neuron_info_dict=treated_subj_list_json_paths[idx],
                output=out_dir / subj.name,
                hemi=hemi,
                skip=skip,
                verbose=True,
                cpu_load=0.3,
            )
            count_neurons_with_json(count_neurons_json_namespace)

            treated_subj_list_json_paths.append(
                out_dir / subj.name / "neuron_info_final_with_label.json"
            )

        control_subj_list_json_paths = []
        for idx, subj in enumerate(control_subj_list_paths):
            # create namespace for neuron counting
            count_neurons_json_namespace = argparse.Namespace(
                lbl=control_subj_list_warped_clusters_dirs[idx],
                min_area=min_area,
                neuron_info_dict=control_subj_list_json_paths[idx],
                output=out_dir / subj.name,
                hemi=hemi,
                skip=skip,
                verbose=True,
            )
            count_neurons_with_json(count_neurons_json_namespace)

            control_subj_list_json_paths.append(
                out_dir / subj.name / "neuron_info_final_with_label.json"
            )

        return treated_subj_list_json_paths, control_subj_list_json_paths

    def _neuron_count_without_json(
        self,
        treated_subj_list_paths: List[Path],
        control_subj_list_paths: List[Path],
        treated_subj_list_seg_file_paths: List[Path],
        control_subj_list_seg_file_paths: List[Path],
        treated_subj_list_warped_clusters_dirs: List[Path],
        control_subj_list_warped_clusters_dirs: List[Path],
        out_dir: Path,
        min_area: Optional[int] = 0,
        skip: Optional[int] = 50,
    ):
        treated_subj_list_json_paths = []
        for idx, subj in enumerate(treated_subj_list_paths):
            count_cmd = f"miracl stats ace_neuron_count \
                -s {treated_subj_list_seg_file_paths[idx]} \
                -l {treated_subj_list_warped_clusters_dirs[idx]} \
                -o {out_dir / subj.name} \
                --min-area {min_area} \
                --skip {skip}"

            treated_subj_list_json_paths.append(
                out_dir / subj.name / "neuron_info_with_label.json"
            )

            # subprocess.Popen(count_cmd, shell=True).wait()

            count_neurons_json_namespace = argparse.Namespace(
                seg=treated_subj_list_seg_file_paths[idx],
                lbl=treated_subj_list_warped_clusters_dirs[idx],
                min_area=min_area,
                output=out_dir / subj.name,
                skip=skip,
                cpu_load=0.3,
                mask=None,
            )

            count_neurons_without_json(count_neurons_json_namespace)

        control_subj_list_json_paths = []
        for idx, subj in enumerate(control_subj_list_paths):
            count_cmd = f"miracl stats ace_neuron_count \
                -s {control_subj_list_seg_file_paths[idx]} \
                -l {control_subj_list_warped_clusters_dirs[idx]} \
                -o {out_dir / subj.name} \
                --min-area {min_area} \
                --skip {skip}"

            control_subj_list_json_paths.append(
                out_dir / subj.name / "neuron_info_with_label.json"
            )

            # subprocess.Popen(count_cmd, shell=True).wait()

            count_neurons_json_namespace = argparse.Namespace(
                seg=control_subj_list_seg_file_paths[idx],
                lbl=control_subj_list_warped_clusters_dirs[idx],
                min_area=min_area,
                output=out_dir / subj.name,
                skip=skip,
                cpu_load=0.3,
                mask=None,
            )

            count_neurons_without_json(count_neurons_json_namespace)

        return treated_subj_list_json_paths, control_subj_list_json_paths

    @staticmethod
    def compute_region_props(
        filtered_pval_array: np.ndarray,
        out_dir: Path,
        mean_diff_array: Optional[np.ndarray] = None,
        labeled_pval: Optional[np.ndarray] = None,
        stats: Optional[np.ndarray] = None,
        atlas_annotation_array: Optional[np.ndarray] = None,
        atlas_annotation_lbls_df: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        prop_list_diff = (
            "label",
            "coords",
            "centroid",
            "area",
            "intensity_mean",
            "intensity_max",
            "intensity_min",
        )

        cluster_props_difference = measure.regionprops_table(
            label_image=labeled_pval,
            intensity_image=mean_diff_array,
            properties=prop_list_diff,
        )
        data = pd.DataFrame(cluster_props_difference)

        # get pvalue assosciated to each cluster
        prop_list_pval = ("intensity_mean", "intensity_max", "intensity_min")
        cluster_props_pval = measure.regionprops_table(
            label_image=labeled_pval,
            intensity_image=filtered_pval_array,
            properties=prop_list_pval,
        )

        data["pval_mean"] = cluster_props_pval["intensity_mean"]
        data["pval_max"] = cluster_props_pval["intensity_max"]
        data["pval_min"] = cluster_props_pval["intensity_min"]

        # get statistic assosciated to each cluster
        prop_list_f_stat = ("intensity_mean", "intensity_max", "intensity_min")
        cluster_props_f_stat = measure.regionprops_table(
            label_image=labeled_pval, intensity_image=stats, properties=prop_list_f_stat
        )

        data["effect_size_mean"] = cluster_props_f_stat["intensity_mean"]
        data["effect_size_max"] = cluster_props_f_stat["intensity_max"]
        data["effect_size_min"] = cluster_props_f_stat["intensity_min"]

        # find the labels of each cluster
        data["cluster_lbl_values"] = None
        data["cluster_lbl_names"] = None
        data["cluster_lbl_areas_percent"] = None

        for i in range(len(data["coords"])):
            cluster_coords = data["coords"][i]
            cluster_lbls = [
                atlas_annotation_array[tuple(coord)] for coord in cluster_coords
            ]
            cluster_lbls.sort()
            cluster_lbl_values, counts = np.unique(cluster_lbls, return_counts=True)
            cluster_lbl_areas_percent = counts / data["area"][i]
            cluster_lbl_names = []
            for value in cluster_lbl_values:
                try:
                    cluster_name = list(atlas_annotation_lbls_df["id"]).index(value)
                    cluster_lbl_names.append(
                        atlas_annotation_lbls_df["name"][cluster_name]
                    )
                except ValueError:
                    cluster_lbl_names.append("unknown")

            data.iloc[
                i, data.columns.get_loc("cluster_lbl_values")
            ] = cluster_lbl_values
            data.iloc[i, data.columns.get_loc("cluster_lbl_names")] = cluster_lbl_names
            data.iloc[
                i, data.columns.get_loc("cluster_lbl_areas_percent")
            ] = cluster_lbl_areas_percent

        data = data.sort_values(by="intensity_max", ascending=False)
        data = data.drop(columns=["coords"])

        out_filename = out_dir / "sig_clusters_summary.csv"
        data.to_csv(out_filename)

        return data, out_filename

    @staticmethod
    def summarize_neuron_count_to_csv(
        neuron_json: Path,
        subj: str,
        sig_clusters_summary_csv_path: Path,
    ):
        sig_clusters_summary_csv = pd.read_csv(
            sig_clusters_summary_csv_path, index_col=0
        )
        clusters = sig_clusters_summary_csv["label"]
        sig_clusters_summary_csv[f"neuron_count_{subj}"] = 0

        with open(neuron_json, "r") as f:
            neuron_json_dict = json.load(f)

        for i, cluster in enumerate(clusters):
            neurons = []
            for neuron_id, stats in neuron_json_dict.items():
                if stats["label_val"] == cluster:
                    neurons.append(neuron_id)

            sig_clusters_summary_csv.iloc[
                i, sig_clusters_summary_csv.columns.get_loc(f"neuron_count_{subj}")
            ] = len(neurons)
        try:
            with open(Path(neuron_json).parent / "label_bboxes.json", "r") as f:
                bbox_dict = json.load(f)

            sig_clusters_summary_csv[f"{subj}_bbox_area_native"] = 0
            for i, cluster in enumerate(clusters):
                idxs = bbox_dict.get(str(cluster), [0, 0, 0, 0, 0, 0])
                sig_clusters_summary_csv.iloc[
                    i,
                    sig_clusters_summary_csv.columns.get_loc(
                        f"{subj}_bbox_area_native"
                    ),
                ] = (
                    (idxs[3] - idxs[0]) * (idxs[4] - idxs[1]) * (idxs[5] - idxs[2])
                )

        except FileNotFoundError:
            print(f"bbox file not found for {subj}")

        sig_clusters_summary_csv.to_csv(sig_clusters_summary_csv_path)

    @staticmethod
    def neuron_count_stats(
        sig_clusters_summary_csv_path: Path,
        treated_group_subj_name: List[str],
        control_group_subj_name: List[str],
    ):
        sig_clusters_summary_csv = pd.read_csv(
            sig_clusters_summary_csv_path, index_col=0
        )
        clusters = sig_clusters_summary_csv["label"]
        sig_clusters_summary_csv["mannwhitneyu_stats"] = 0
        sig_clusters_summary_csv["mannwhitneyu_pvalue"] = 0

        for i, cluster in enumerate(clusters):
            neurons_treated = []
            neurons_control = []
            for subj in treated_group_subj_name:
                neurons_treated.append(
                    sig_clusters_summary_csv[f"neuron_count_{subj}"].iloc[i]
                )
            for subj in control_group_subj_name:
                neurons_control.append(
                    sig_clusters_summary_csv[f"neuron_count_{subj}"].iloc[i]
                )

            try:
                stats, p = mannwhitneyu(neurons_treated, neurons_control)
            except:
                stats, p = pd.NA, pd.NA
            sig_clusters_summary_csv.iloc[
                i, sig_clusters_summary_csv.columns.get_loc("mannwhitneyu_stats")
            ] = stats
            sig_clusters_summary_csv.iloc[
                i, sig_clusters_summary_csv.columns.get_loc("mannwhitneyu_pvalue")
            ] = p

        sig_clusters_summary_csv.to_csv(sig_clusters_summary_csv)


class ValidateClustersInterface:
    """Main logic for cluster validation of ACE"""

    def __init__(self, args: argparse.Namespace):
        self.arg_dict: Dict = vars(args)
        self.treated_dir: str = self.arg_dict.get("treated", None)
        self.control_dir: str = self.arg_dict.get("ctrl", None)
        self.relative_path_to_ace_output: str = self.arg_dict.get(
            "path-to-ace-output", None
        )
        self.relative_path_to_raw_slices: str = self.arg_dict.get(
            "path-to-raw-slices", None
        )
        self.p_value_path: str = self.arg_dict.get("p_value", None)
        self.pvalue_thr: float = self.arg_dict.get("pvalue_thr", None)
        self.f_stat_path: str = self.arg_dict.get("stats", None)
        self.out_dir: str = self.arg_dict.get("out_dir", None)
        self.atlas_dir: str = self.arg_dict.get("atlas_dir", None)
        self.mean_diff_path: str = self.arg_dict.get("mean_diff", None)
        self.vox_size: int = self.arg_dict.get("vox_size", None)
        self.hemi: str = self.arg_dict.get("hemi", None)
        self.side: str = self.arg_dict.get("side", None)
        self.neuron_info_dir: Optional[str] = self.arg_dict.get("neuron-info-dir", None)
        self.min_area: int = self.arg_dict.get("min_area", None)
        self.skip: int = self.arg_dict.get("skip", None)
        self.orientation_code = self.arg_dict.get("orient_code", None)

        # convert all to Path
        self.treated_dir: Path = Path(self.treated_dir)
        self.control_dir: Path = Path(self.control_dir)
        self.p_value_path: Path = Path(self.p_value_path)
        self.f_stat_path: Path = Path(self.f_stat_path)
        self.out_dir: Path = Path(self.out_dir)
        self.atlas_dir: Path = Path(self.atlas_dir)
        self.mean_diff_path: Path = Path(self.mean_diff_path)
        self.neuron_info_dir: Optional[Path] = (
            Path(self.neuron_info_dir) if self.neuron_info_dir else None
        )

        # assert all paths exist
        assert self.treated_dir.exists(), f"{self.treated_dir} does not exist"
        assert self.control_dir.exists(), f"{self.control_dir} does not exist"
        assert self.p_value_path.exists(), f"{self.p_value_path} does not exist"
        assert self.f_stat_path.exists(), f"{self.f_stat_path} does not exist"
        assert self.atlas_dir.exists(), f"{self.atlas_dir} does not exist"
        assert self.mean_diff_path.exists(), f"{self.mean_diff_path} does not exist"

        if not self.out_dir.exists():
            print(f"Creating output directory: {self.out_dir}")
            self.out_dir.mkdir(parents=True)

        self._get_paths()
        self._create_orientation_files()
        self._load_atlas()

        self.neuron_counter = NeuronCounter()

    def _create_orientation_files(self):
        for idx, subj in enumerate(self.treated_subj_list_reg_orientation_paths):
            with open(subj, "w") as f:
                f.write(self.orientation_code)

        for idx, subj in enumerate(self.control_subj_list_reg_orientation_paths):
            with open(subj, "w") as f:
                f.write(self.orientation_code)

    def _get_paths(self):
        self.treated_subj_list_paths = [
            subj for subj in self.treated_dir.iterdir() if subj.is_dir()
        ]
        self.control_subj_list_paths = [
            subj for subj in self.control_dir.iterdir() if subj.is_dir()
        ]

        n_subj_treated = len(self.treated_subj_list_paths)
        n_subj_ctrl = len(self.control_subj_list_paths)
        print(f"{n_subj_treated} treated and {n_subj_ctrl} ctrl subjects found ...")

        # make absolute path to ace output
        treated_absolute_path_to_ace = [
            subj / self.relative_path_to_ace_output
            for subj in self.treated_subj_list_paths
        ]
        assert all(
            [subj.exists() for subj in treated_absolute_path_to_ace]
        ), f"some treated subjects do not have ace output folder from {self.relative_path_to_ace_output}"

        control_absolute_path_to_ace = [
            subj / self.relative_path_to_ace_output
            for subj in self.control_subj_list_paths
        ]
        assert all(
            [subj.exists() for subj in control_absolute_path_to_ace]
        ), f"some control subjects do not have ace output folder from {self.relative_path_to_ace_output}"

        # make absolute path to raw slices
        self.treated_absolute_path_to_raw_slices = [
            subj / self.relative_path_to_raw_slices
            for subj in self.treated_subj_list_paths
        ]
        assert all(
            [subj.exists() for subj in self.treated_absolute_path_to_raw_slices]
        ), f"some treated subjects do not have raw slices folder from {self.relative_path_to_raw_slices}"

        self.control_absolute_path_to_raw_slices = [
            subj / self.relative_path_to_raw_slices
            for subj in self.control_subj_list_paths
        ]
        assert all(
            [subj.exists() for subj in self.control_absolute_path_to_raw_slices]
        ), f"some control subjects do not have raw slices folder from {self.relative_path_to_raw_slices}"

        self.treated_subj_list_reg_paths = [
            subj / "clar_allen_reg" for subj in treated_absolute_path_to_ace
        ]

        self.control_subj_list_reg_paths = [
            subj / "clar_allen_reg" for subj in control_absolute_path_to_ace
        ]

        self.treated_subj_list_reg_orientation_paths = [
            subj / "orientation.txt" for subj in self.treated_subj_list_paths
        ]

        self.control_subj_list_reg_orientation_paths = [
            subj / "orientation.txt" for subj in self.control_subj_list_paths
        ]

        self.treated_subj_list_seg_file_paths = [
            list((subj / "vox_final").glob("stacked*.tif"))[0]
            for subj in treated_absolute_path_to_ace
        ]

        self.control_subj_list_seg_file_paths = [
            list((subj / "vox_final").glob("stacked*.tif"))[0]
            for subj in control_absolute_path_to_ace
        ]

        self.treated_subj_list_json_paths = [
            self.neuron_info_dir / f"{subj.name}.json"
            for subj in self.treated_subj_list_paths
        ]

        self.control_subj_list_json_paths = [
            self.neuron_info_dir / f"{subj.name}.json"
            for subj in self.control_subj_list_paths
        ]

    def _load_atlas(self):
        self.ann_img_array, self.annotation_lbls_df = AtlasLoader.load_atlas(
            atlas_dir=self.atlas_dir,
            out_dir=self.out_dir,
            img_res=self.vox_size,
            hemi=self.hemi,
            side=self.side,
        )

    def run(self):
        (
            filtered_pvals_img_arr,
            labeled_pvals_array,
            dil_bin_pval_conn_comp_filtered_path,
        ) = PreProcessClusters.binarize_dialte_clusters(
            self.p_value_path,
            self.pvalue_thr,
            self.out_dir,
        )

        mean_diff_array = nib.load(self.mean_diff_path).get_fdata()
        f_stat_array = nib.load(self.f_stat_path).get_fdata()

        data, cluster_csv_path = NeuronCounter.compute_region_props(
            filtered_pval_array=filtered_pvals_img_arr,
            mean_diff_array=mean_diff_array,
            labeled_pval_array=labeled_pvals_array,
            stats=f_stat_array,
            out_dir=self.out_dir,
            atlas_annotation_array=self.ann_img_array,
            atlas_annotation_lbls_df=self.annotation_lbls_df,
        )

        # warp clusters to original space treated
        treated_subj_warped_clusters_dirs = []
        for idx, subj in enumerate(self.treated_subj_list_paths):
            current_dir = f"p_values_bin_dilated_conncomp_filtered_warped_treated_{subj.name}_clar"
            treated_subj_warped_clusters_dirs.append(self.out_dir / current_dir)
            ClusterWarperToClar.warp_sig_clusters(
                reg_dir=self.treated_subj_list_reg_paths[idx],
                dil_bin_pval_comp_fil=dil_bin_pval_conn_comp_filtered_path,
                ort_file=self.treated_subj_list_reg_orientation_paths[idx],
                org_clar=self.treated_absolute_path_to_raw_slices[idx],
                out_dir=self.out_dir,
                out_lbl=current_dir,
            )

        # warp clusters to original space
        control_subj_warped_clusters_dirs = []
        for idx, subj in enumerate(self.control_subj_list_paths):
            current_dir = f"p_values_bin_dilated_conncomp_filtered_warped_control_{subj.name}_clar"
            control_subj_warped_clusters_dirs.append(self.out_dir / current_dir)
            ClusterWarperToClar.warp_sig_clusters(
                reg_dir=self.control_subj_list_reg_paths[idx],
                dil_bin_pval_comp_fil=dil_bin_pval_conn_comp_filtered_path,
                ort_file=self.control_subj_list_reg_orientation_paths[idx],
                org_clar=self.control_absolute_path_to_raw_slices[idx],
                out_dir=self.out_dir,
                out_lbl=current_dir,
            )

        # use neuron info files if they exist
        if self.neuron_info_dir:
            assert (
                self.neuron_info_dir.exists()
            ), f"{self.neuron_info_dir} does not exist"
            self.neuron_counter.set_json(True)
            self.neuron_counter.init_neuron_count_args(
                treated_subj_list_paths=self.treated_subj_list_paths,
                control_subj_list_paths=self.control_subj_list_paths,
                treated_subj_list_warped_clusters_dirs=treated_subj_warped_clusters_dirs,
                control_subj_list_warped_clusters_dirs=control_subj_warped_clusters_dirs,
                treated_subj_list_json_paths=self.treated_subj_list_json_paths,
                control_subj_list_json_paths=self.control_subj_list_json_paths,
                out_dir=self.out_dir,
                min_area=self.min_area,
                skip=self.skip,
                hemi=self.hemi,
            )
            self.neuron_counter.init_neuron_count_args()
        else:
            self.neuron_counter.set_json(False)
            self.neuron_counter.init_neuron_count_args(
                treated_subj_list_paths=self.treated_subj_list_paths,
                control_subj_list_paths=self.control_subj_list_paths,
                treated_subj_list_seg_file_paths=self.treated_subj_list_seg_file_paths,
                control_subj_list_seg_file_paths=self.control_subj_list_seg_file_paths,
                treated_subj_list_warped_clusters_dirs=treated_subj_warped_clusters_dirs,
                control_subj_list_warped_clusters_dirs=control_subj_warped_clusters_dirs,
                out_dir=self.out_dir,
                min_area=self.min_area,
                skip=self.skip,
            )

        (
            treated_subj_list_json_paths,
            control_subj_list_json_paths,
        ) = self.neuron_counter.run_neuron_count()

        # for idx, subj in enumerate(self.treated_subj_list_paths):
        #     # get the size of the raw image from segmentation file
        #     seg_file = self.treated_subj_list_seg_file_paths[idx]

        #     warped_cluster_dir = treated_subj_warped_clusters_paths[idx]
        #     command = f'python /code/miracl/stats/miracl_stats_ace_cluster_neuron_count.py \
        #             -s {seg_file} \
        #             -l {warped_cluster_dir} \
        #             -o {self.out_dir + "/" + os.path.basename(subj)}'
        #     subprocess.Popen(command, shell=True).wait()

        # print("\n counting neurons inside each cluster in the ctrl group")

        # for idx, subj in enumerate(self.control_subj_list_paths):
        #     # get the size of the raw image from segmentation file
        #     seg_file = self.control_subj_list_seg_file_paths[idx]

        #     warped_cluster_dir = os.path.join(
        #         self.out_dir,
        #         f"p_values_bin_dilated_conncomp_filtered_warped_ctrl_{os.path.basename(subj)}_tiff_clar",
        #     )

        #     command = f'python /data2/projects/Ahmadreza/ACE_reviewer_response_experiments/stats/validate_clusters/test_memmap.py \
        #             -s {seg_file} \
        #             -l {warped_cluster_dir} \
        #             -o {self.out_dir + "/" + os.path.basename(subj)}'
        #     subprocess.Popen(command, shell=True).wait()

        for idx, subj in enumerate(self.treated_subj_list_paths):
            NeuronCounter.summarize_neuron_count_to_csv(
                neuron_json=treated_subj_list_json_paths[idx],
                subj=subj.name,
                sig_clusters_summary_csv_path=cluster_csv_path,
            )

        for idx, subj in enumerate(self.control_subj_list_paths):
            NeuronCounter.summarize_neuron_count_to_csv(
                neuron_json=control_subj_list_json_paths[idx],
                subj=subj.name,
                sig_clusters_summary_csv_path=cluster_csv_path,
            )

        NeuronCounter.neuron_count_stats(
            sig_clusters_summary_csv_path=cluster_csv_path,
            treated_group_subj_name=[
                subj.name for subj in self.treated_subj_list_paths
            ],
            control_group_subj_name=[
                subj.name for subj in self.control_subj_list_paths
            ],
        )


def main(args: argparse.Namespace):
    interface = ValidateClustersInterface(args)
    interface.run()


if __name__ == "__main__":
    parser = parsefn()
    args = parser.parse_args()
    main(args)
