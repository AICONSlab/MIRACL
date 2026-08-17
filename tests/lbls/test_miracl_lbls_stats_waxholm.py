import pytest
import numpy as np
import pandas as pd
import subprocess
from unittest.mock import Mock, patch
import argparse

from miracl.lbls.miracl_lbls_stats_waxholm import \
    get_count_stats, \
    get_lstat_df, \
    merge_stats_df, \
    parse_inputs, \
    parsefn, \
    main

@pytest.mark.parametrize("invol_arr, lbls_arr, expected", [
    (
        np.array([[[1, -1], [2, 0]], [[3, -4], [5, -6]]]),
        np.array([[[0, 0], [1, 1]], [[0, 0], [1, 1]]]),
        {0: 2, 1: 2},
    ),
    (
        np.array([[[5, 5], [5, 5]], [[5, 5], [5, 5]]]),
        np.array([[[2, 2], [2, 2]], [[2, 2], [2, 2]]]),
        {2: 8},
    ),
    (
        np.array([
            [[1, -1, 2], [-3, 4, -5], [6, -7, 0]],   # z=0, label 0
            [[5, 5, 5], [5, 5, 5], [5, 5, 5]],        # z=1, label 1
            [[9, 9, 9], [-9, -9, -9], [0, 0, 0]],     # z=2, label 2
        ]),
        np.array([
            [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            [[1, 1, 1], [1, 1, 1], [1, 1, 1]],
            [[2, 2, 2], [2, 2, 2], [2, 2, 2]],
        ]),
        {0: 4, 1: 9, 2: 3},
    ),
])
def test_get_count_stats(monkeypatch, invol_arr, lbls_arr, expected):
    fake_arrays = {"invol": invol_arr, "lbls": lbls_arr}

    def fake_load(path):
        class FakeImg:
            def get_fdata(self):
                return fake_arrays[path]
        return FakeImg()

    monkeypatch.setattr("miracl.lbls.miracl_lbls_stats_waxholm.nib.load", fake_load)

    result = get_count_stats("invol", "lbls")
    actual = dict(zip(result["LabelID"], result["Intensity_Count"]))
    assert actual == expected

def make_fake_run(stdout):
    return Mock(return_value=subprocess.CompletedProcess(
        args=[], returncode=0, stdout=stdout, stderr="",
    ))


@pytest.mark.parametrize("stdout, expected", [
    (
        "LabelID Mean StdD Max Min Count Vol(mm^3) ExtentX ExtentY ExtentZ\n"
        "      0  12.5  3.5 20.0  5.0   100     100.0      10      10      10\n",
        [{"LabelID": 0, "Mean": 12.5, "Count": 100}],
    ),
    (
        "LabelID Mean StdD Max Min Count Vol(mm^3) ExtentX ExtentY ExtentZ\n"
        "      0  12.5  3.5 20.0  5.0   100     100.0      10      10      10\n"
        "      1  45.2  1.1 50.0 40.0    50      50.0       5       5       5\n"
        "      2   0.0  0.0  0.0  0.0     0       0.0       0       0       0\n",
        [
            {"LabelID": 0, "Mean": 12.5, "Count": 100},
            {"LabelID": 1, "Mean": 45.2, "Count": 50},
            {"LabelID": 2, "Mean": 0.0, "Count": 0},
        ],
    ),
])
def test_get_lstat_df(monkeypatch, stdout, expected):
    mock_run = make_fake_run(stdout)
    monkeypatch.setattr("miracl.lbls.miracl_lbls_stats_waxholm.subprocess.run", mock_run)

    df = get_lstat_df("invol.nii.gz", "lbls.nii.gz")

    assert list(df.columns) == [
        "LabelID", "Mean", "StdD", "Max", "Min", "Count",
        "Vol_mm3", "ExtentX", "ExtentY", "ExtentZ",
    ]
    assert len(df) == len(expected)
    for i, row in enumerate(expected):
        for col, val in row.items():
            assert df.loc[i, col] == val

    mock_run.assert_called_once_with(
        ["c3d", "invol.nii.gz", "lbls.nii.gz", "-lstat"],
        capture_output=True,
        text=True,
        check=True,
    )


def test_get_lstat_df_raises_on_c3d_failure(monkeypatch):
    mock_run = Mock(side_effect=subprocess.CalledProcessError(returncode=1, cmd=["c3d"]))
    monkeypatch.setattr("miracl.lbls.miracl_lbls_stats_waxholm.subprocess.run", mock_run)

    with pytest.raises(subprocess.CalledProcessError):
        get_lstat_df("bad.nii.gz", "lbls.nii.gz")

@pytest.fixture
def annot_labels():
    return pd.DataFrame({
        "index": [0, 1, 3, 4, 5, 444, 448, 500, 501, 502],
        "R":     [0, 255, 0, 255, 0, 0, 128, 1, 2, 230],
        "G":     [0, 52, 0, 255, 255, 128, 0, 10, 20, 184],
        "B":     [0, 39, 255, 1, 255, 0, 100, 100, 200, 67],
        "A":     [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "VIS":   [0, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        "MSH":   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "name": [
            "Clear Label",
            "corticofugal tract and corona radiata",
            "Subthalamic nucleus",
            "Molecular cell layer of the cerebellum",
            "Cerebellum, unspecified",
            "Temporal association cortex",
            "Secondary visual area, medial part",
            "Endopiriform nucleus",
            "Amygdaloid area, unspecified",
            "Nucleus of the lateral olfactory tract",
        ],
    })

@pytest.mark.parametrize("stats_df, count_stats, sort", [
    (
        pd.DataFrame({
            "LabelID": [0, 1, 2, 55],
            "Mean": [93.2, 1, 3.14, 10],
            "StdD": [6.7, 0.99, 3.1415, 0.23],
            "Max": [93.2, 1, 3.14, 10],
            "Min": [93.2, 1, 3.14, 10],
            "Count": [88, 77, 66, 55],
            "Vol_mm3": [100, 200, 50, 23]
        }),
        pd.DataFrame({
            "LabelID": [1, 0, 2, 55],
            "Intensity_Count": [81, 71, 51, 9]
        }),
        "Mean"
    ),
    (
        pd.DataFrame({
            "LabelID": [0, 1, 2, 55],
            "Mean": [93.2, 1, 3.14, 10],
            "StdD": [6.7, 0.99, 3.1415, 0.23],
            "Max": [93.2, 1, 3.14, 10],
            "Min": [93.2, 1, 3.14, 10],
            "Count": [88, 77, 66, 55],
            "Vol_mm3": [100, 200, 50, 23]
        }),
        pd.DataFrame({
            "LabelID": [1, 0, 2, 55],
            "Intensity_Count": [81, 71, 51, 9]
        }),
        "Min"
    ),
])
def test_merge_stats_df(monkeypatch, annot_labels, stats_df, count_stats, sort):
    # Patch the pd.read_csv function
    monkeypatch.setattr(
        "miracl.lbls.miracl_lbls_stats_waxholm.pd.read_csv",
        Mock(return_value=annot_labels),
    )
    # Call function
    stats_df = merge_stats_df(stats_df, count_stats, sort)
    # Assert that the first three columns are LabelID, name, and sort
    stats_df_cols = stats_df.columns
    assert stats_df_cols[0] == "LabelID"
    assert stats_df_cols[1] == "name"
    assert stats_df_cols[2] == sort
    # Assert that the correct intensity counts are merged
    for label in stats_df["LabelID"]:
        # Get location of this label in count stats
        label_iloc = count_stats.loc[count_stats["LabelID"] == label].index[0]
        expected_count = count_stats.loc[label_iloc, "Intensity_Count"]
        actual_count = stats_df.loc[stats_df["LabelID"] == label, "Intensity_Count"].iloc[0]
        assert actual_count == expected_count

@pytest.mark.parametrize("invol, lbls, outfile, sort, file_exists", [
    ("invol.nii.gz", "lbls.nii.gz", "out.csv", "Mean", True),
    ("invol.nii.gz", "lbls.nii.gz", "out.csv", "Mean", False),
    ("invol.nii.gz", "lbls.nii.gz", "out.csv", "Min", False),
    ("test_invol.nii.gz", "test_lbls.nii.gz", "test_out.csv", "StdD", True),
])
def test_parse_inputs(invol, lbls, outfile, sort, file_exists):
    namespace = argparse.Namespace(invol=invol, lbls=lbls, outfile=outfile, sort=sort)

    # Mock the parser
    mock_parser = Mock()
    mock_parser.parse_known_args.return_value = (namespace, [])

    # Call function and check result
    with patch("miracl.lbls.miracl_lbls_stats_waxholm.os.path.exists", return_value=file_exists):
        if not file_exists:
            with pytest.raises(AssertionError):
                parse_inputs(mock_parser, [])
        else:
            result = parse_inputs(mock_parser, [])
            assert result == (invol, lbls, outfile, sort)
        mock_parser.parse_known_args.assert_called_once_with()

@pytest.mark.parametrize("argv", [
    ["-i", "invol.nii.gz", "-l", "lbls.nii.gz"],
    ["--invol", "invol.nii.gz", "--lbls", "lbls.nii.gz"],
])
def test_parsefn_required_args_and_defaults(argv):
    parser = parsefn()
    args = parser.parse_args(argv)

    assert args.invol == "invol.nii.gz"
    assert args.lbls == "lbls.nii.gz"
    assert args.sort == "Mean"
    assert args.outfile == "label_statistics.csv"


@pytest.mark.parametrize("argv, expected_sort, expected_outfile", [
    (["-i", "invol.nii.gz", "-l", "lbls.nii.gz", "-s", "Count"], "Count", "label_statistics.csv"),
    (["-i", "invol.nii.gz", "-l", "lbls.nii.gz", "-o", "out.csv"], "Mean", "out.csv"),
    (["-i", "invol.nii.gz", "-l", "lbls.nii.gz", "-s", "Max", "-o", "stats.csv"], "Max", "stats.csv"),
])
def test_parsefn_optional_overrides(argv, expected_sort, expected_outfile):
    parser = parsefn()
    args = parser.parse_args(argv)

    assert args.sort == expected_sort
    assert args.outfile == expected_outfile


@pytest.mark.parametrize("argv", [
    ["-l", "lbls.nii.gz"],          # missing invol
    ["-i", "invol.nii.gz"],         # missing lbls
    [],                              # missing both
])
def test_parsefn_missing_required_args_exits(argv, capsys):
    parser = parsefn()

    with pytest.raises(SystemExit):
        parser.parse_args(argv)

    captured = capsys.readouterr()
    assert "required" in captured.err.lower()


def test_parsefn_help_flag_exits_zero(capsys):
    parser = parsefn()

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["-h"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()

FAKE_MERGED_DF = pd.DataFrame({
    "LabelID": [0, 1, 2],
    "name": ["a", "b", "c"],
    "Intensity_Count": [10, 30, 20],
    "Mean": [1.0, 3.0, 2.0],
})

FAKE_MERGED_DF_DIVERGING_SORT = pd.DataFrame({
    "LabelID": [0, 1, 2, 3],
    "name": ["a", "b", "c", "d"],
    "Intensity_Count": [40, 10, 30, 20],
    "Mean": [1.0, 2.0, 3.0, 4.0],
})


@pytest.mark.parametrize("merged_df, sort_col, expected_label_order", [
    (FAKE_MERGED_DF, "Mean", [1, 2, 0]),
    (FAKE_MERGED_DF, "Intensity_Count", [1, 2, 0]),
    (FAKE_MERGED_DF_DIVERGING_SORT, "Mean", [3, 2, 1, 0]),
    (FAKE_MERGED_DF_DIVERGING_SORT, "Intensity_Count", [0, 2, 3, 1]),
])
def test_main_sorts_descending_and_saves_csv(tmp_path, merged_df, sort_col, expected_label_order):
    outfile = tmp_path / "stats.csv"
    args = Mock()

    with patch("miracl.lbls.miracl_lbls_stats_waxholm.parsefn"), \
         patch("miracl.lbls.miracl_lbls_stats_waxholm.parse_inputs",
               return_value=("invol.nii.gz", "lbls.nii.gz", str(outfile), sort_col)), \
         patch("miracl.lbls.miracl_lbls_stats_waxholm.get_lstat_df"), \
         patch("miracl.lbls.miracl_lbls_stats_waxholm.get_count_stats"), \
         patch("miracl.lbls.miracl_lbls_stats_waxholm.merge_stats_df", return_value=merged_df):

        main(args)

    assert outfile.exists()
    saved_df = pd.read_csv(outfile)
    assert list(saved_df["LabelID"]) == expected_label_order
