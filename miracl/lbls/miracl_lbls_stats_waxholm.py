import argparse
import subprocess
import io
import time
import pandas as pd
import nibabel as nib
import numpy as np
from tqdm import tqdm

def get_count_stats(invol, lbls):
    """Given an input volume and a label mask, generate a table of statistics for each label in the label mask.
    Unlike c3d's "lstat", this method extracts the following statistics:

    "intensity count": within a label, the number of voxels in the input with an intensity greater than 0

    invol (str): path to a medical image
    lbls (str): path to a label image
    """
    print("Getting intensity counts...")

    # load images
    invol_img = nib.load(invol)
    invol_arr = invol_img.get_fdata()

    lbls_img = nib.load(lbls)
    lbls_arr_raw = lbls_img.get_fdata()
    # if np.any(lbls_arr_raw != np.round(lbls_arr_raw)):
    #     print("  WARNING: labels image contains non-integer values (likely from interpolated "
    #           "resampling) - rounding to the nearest label")
    lbls_arr = np.round(lbls_arr_raw).astype(np.int32)

    # create list to store results
    # res = []

    # # for each intensity value in lbl array
    # start_loop = time.time()
    # ids = list(np.unique(lbls_arr))
    # for label_id in tqdm(ids):
    #     masked_arr = invol_arr[lbls_arr == label_id]

    #     intensity_count = masked_arr > 0
    #     intensity_count = intensity_count.sum()

    #     # create dict that stores {intensity_value, count, total}
    #     res.append({"LabelID": label_id, "intensity_count": intensity_count})

    # # convert list to pandas dataframe, return
    # res_df = pd.DataFrame(res)
    # loop_time = time.time() - start_loop
    # print(f"Loop method took {loop_time:.2f}s")

    # vectorized version: count positive-intensity voxels per label in a single pass,
    # instead of rescanning the full volume once per label
    start_fast = time.time()
    positive_mask = (invol_arr > 0).astype(np.int64)
    counts = np.bincount(lbls_arr.ravel(), weights=positive_mask.ravel())
    ids_arr = np.unique(lbls_arr)
    res_df_fast = pd.DataFrame({
        "LabelID": ids_arr,
        "intensity_count": counts[ids_arr].astype(np.int64),
    })
    fast_time = time.time() - start_fast
    print(f"Vectorized method took {fast_time:.2f}s")

    # combine both results into one dataframe to verify they match
    # compare_df = res_df.merge(res_df_fast, on="LabelID", suffixes=("_loop", "_fast"))
    # compare_df["match"] = compare_df["intensity_count_loop"] == compare_df["intensity_count_fast"]
    # print(f"All {len(compare_df)} labels match: {compare_df['match'].all()}")

    print("Done getting intensity counts.")
    return res_df_fast

def get_lstat_df(invol, lbls):
    """Run c3d's -lstat on an input volume and label mask, and return the result as a DataFrame.

    invol (str): path to a medical image
    lbls (str): path to a label image
    """
    print("Getting label statistics...")
    result = subprocess.run(
        ["c3d", invol, lbls, "-lstat"],
        capture_output=True,
        text=True,
        check=True,
    )
    columns = ["LabelID", "Mean", "StdD", "Max", "Min", "Count", "Vol_mm3",
               "ExtentX", "ExtentY", "ExtentZ"]
    result_df = pd.read_csv(io.StringIO(result.stdout), sep=r"\s+", skiprows=1, names=columns)
    return result_df

def merge_stats_df(stats_df, count_stats):
    """Merge intensity counts and Waxholm atlas label names into stats_df, and reorder
    columns so name and intensity_count sit right after LabelID.

    stats_df (pd.DataFrame): output of get_lstat_df
    count_stats (pd.DataFrame): output of get_count_stats
    """
    # Merge intensity counts into stats_df
    stats_df = stats_df.merge(count_stats, on="LabelID", how="left")
    # Read in tsv from atlas
    annot_tsv = pd.read_csv("/workspaces/data/tpl-WHSv4/tpl-WHSv4_seg-all_dseg.tsv", sep="\t")
    # Merge label names into stats_df
    stats_df = stats_df.merge(
        annot_tsv[["index", "name"]], left_on="LabelID", right_on="index", how="left"
    ).drop(columns=["index"])
    # Move name column to right after LabelID, and intensity_count right after name
    cols = stats_df.columns.tolist()
    cols.remove("name")
    cols.insert(cols.index("LabelID") + 1, "name")
    cols.remove("intensity_count")
    cols.insert(cols.index("name") + 1, "intensity_count")
    return stats_df[cols]

def verify_stats(stats_df, invol, lbls):
    """Run internal consistency checks on stats_df to catch pipeline bugs (unit mismatches,
    off-by-one errors in masking, incorrect merges), without needing an external oracle.

    stats_df (pd.DataFrame): merged stats dataframe, output of merge_stats_df
    invol (str): path to input volume
    lbls (str): path to label image
    """
    print("Running verification checks...")
    lbls_img = nib.load(lbls)
    lbls_arr = np.round(lbls_img.get_fdata()).astype(np.int32)
    voxel_volume = np.prod(lbls_img.header.get_zooms())

    non_bg = stats_df[stats_df["LabelID"] != 0]

    # Check 1: Count should sum to the number of non-background voxels in the label image
    total_count = non_bg["Count"].sum()
    total_nonbg_voxels = int(np.sum(lbls_arr != 0))
    if total_count != total_nonbg_voxels:
        print(f"  WARNING: total Count ({total_count}) != non-background voxels in labels ({total_nonbg_voxels})")

    # Check 2: Vol_mm3 should equal Count * voxel volume
    expected_vol = non_bg["Count"] * voxel_volume
    mismatched = ~np.isclose(non_bg["Vol_mm3"], expected_vol, rtol=1e-1)
    if mismatched.any():
        print(f"  WARNING: Vol_mm3 does not match Count * voxel_volume for {mismatched.sum()} labels")
        print(non_bg.loc[mismatched, ["LabelID", "Vol_mm3", "Count"]].assign(expected_vol=expected_vol[mismatched]))

    # Check 3: intensity_count can never exceed Count
    bad_rows = stats_df[stats_df["intensity_count"] > stats_df["Count"]]
    if not bad_rows.empty:
        print(f"  WARNING: {len(bad_rows)} labels have intensity_count > Count")

    print("Done running verification checks.")

def main(args):
    """Compute label statistics and intensity counts for a volume, merge in Waxholm atlas
    label names, and save the result to a CSV.

    args: parsed arguments from parsefn(), with invol, lbls, and outfile attributes
    """
    # Extract the arguments
    invol = args.invol
    lbls = args.lbls
    # Get the dataframe from c3d -lstat
    stats_df = get_lstat_df(
            invol=invol,
            lbls=lbls
    )
    # Generate additional stats and merge into output file
    count_stats = get_count_stats(invol, lbls)
    print("Done getting label statistics.")
    stats_df = merge_stats_df(stats_df, count_stats)
    # Run verification checks if requested
    if args.verify:
        verify_stats(stats_df, invol, lbls)
    # Sort dataframe
    stats_df = stats_df.sort_values([args.sort], ascending=False)
    # Save to csv
    stats_df.to_csv(args.outfile, index=False)
    print(f"Saved stats to {args.outfile}")

def parsefn():
    """Build and return the argument parser for this script."""
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Compute label statistics (mean, std, volume, etc.) for a brain volume with the Waxholm atlas.",
        epilog="Example: python3 stats_script.py -i brain.nii.gz -l labels.nii.gz",
        add_help=False,
    )
    # Get arguments from user through command line
    required = parser.add_argument_group("required arguments")
    required.add_argument("-i", "--invol", required=True, type=str, help="Input volume")
    required.add_argument("-l", "--lbls", required=True, type=str, help="Registerd Allen labels")

    optional = parser.add_argument_group("additional arguments")
    optional.add_argument(
        "-s",
        "--sort",
        type=str,
        help="Sort by Mean, StdD, Max, Min, Count or Vol_mm3 (default: 'Mean')",
        default="Mean",
    )
    optional.add_argument(
        "-o",
        "--outfile",
        type=str,
        help="Output CSV filename (default: %(default)s)",
        default="label_statistics.csv",
    )
    optional.add_argument(
        "-v",
        "--verify",
        action="store_true",
        help="Run internal consistency checks on the output stats (default: False)",
    )
    optional.add_argument(
        "-h",
        "--help",
        action="help",
        help="show this help message and exit",
    )
    return parser

if __name__ == "__main__":
    parser = parsefn()
    args = parser.parse_args()
    # Call the main function to compute statistics
    main(args=args)
    