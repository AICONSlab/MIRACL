import argparse
import subprocess
import io
import pandas as pd
import nibabel as nib
import numpy as np
import os
import sys

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
    lbls_arr = np.round(lbls_arr_raw).astype(np.int32)

    # vectorized version: count positive-intensity voxels per label in a single pass,
    # instead of rescanning the full volume once per label
    positive_mask = (invol_arr > 0).astype(np.int64)
    counts = np.bincount(lbls_arr.ravel(), weights=positive_mask.ravel())
    ids_arr = np.unique(lbls_arr)
    res_df = pd.DataFrame({
        "LabelID": ids_arr,
        "intensity_count": counts[ids_arr].astype(np.int64),
    })

    print("Done getting intensity counts.")
    return res_df

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
    annot_tsv = pd.read_csv("/code/atlases/waxholm/WHS_SD_rat_atlas_v4.label", sep="\t")
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

def parse_inputs(parser, args):
    if isinstance(args, list):
        args, unknown = parser.parse_known_args()

    invol = args.invol
    lbls = args.lbls
    outfile = args.outfile
    sort = args.sort

    # check if pars given

    assert isinstance(invol, str)
    assert os.path.exists(invol), (
        "%s does not exist ... please check path and rerun script" % invol
    )
    assert isinstance(lbls, str)
    assert os.path.exists(lbls), (
        "%s does not exist ... please check path and rerun script" % lbls
    )
    assert isinstance(outfile, str)
    assert isinstance(sort, str)

    return invol, lbls, outfile, sort

def main(args):
    """Compute label statistics and intensity counts for a volume, merge in Waxholm atlas
    label names, and save the result to a CSV.

    args: parsed arguments from parsefn(), with invol, lbls, and outfile attributes
    """
    # parse in args
    parser = parsefn()
    invol, lbls, outfile, sort = parse_inputs(parser, args)

    # Get the dataframe from c3d -lstat
    stats_df = get_lstat_df(
            invol=invol,
            lbls=lbls
    )

    # Generate additional stats and merge into output file
    count_stats = get_count_stats(invol, lbls)
    print("Done getting label statistics.")
    stats_df = merge_stats_df(stats_df, count_stats)

    # Sort dataframe
    stats_df = stats_df.sort_values([sort], ascending=False)

    # Save to csv
    stats_df.to_csv(outfile, index=False)
    print(f"Saved stats to {outfile}")

def parsefn():
    parser = argparse.ArgumentParser(
        description="""miracl lbls_stats -i INVOL -l LBLS [-s SORT] [-o OUTFILE] [-h]

Examples:
    miracl_lbls_stats.py -i input_volume.nii.gz -l registered_labels.nii.gz -o output_stats.csv -s Count

Notes:
    - Input volumes must be registered to the Waxholm atlas space.
    - Output CSV contains label statistics merged with Waxholm ontology info.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "-i",
        "--invol",
        required=True,
        type=str,
        help="Input volume",
    )
    required.add_argument(
        "-l",
        "--lbls",
        required=True,
        type=str,
        help="Registered Waxholm labels",
    )

    optional = parser.add_argument_group("additional arguments")
    optional.add_argument(
        "-s",
        "--sort",
        type=str,
        help="Sort by Mean, StdD, Max, Min, Count or Vol(mm^3) (default: 'Mean')",
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
        "-h",
        "--help",
        action="help",
        help="show this help message and exit",
    )

    return parser

if __name__ == "__main__":
    main(sys.argv)
    