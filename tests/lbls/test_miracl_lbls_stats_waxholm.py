import pytest
import numpy as np
from miracl.lbls.miracl_lbls_stats_waxholm import get_count_stats

@pytest.mark.parametrize("invol_arr, lbls_arr, expected", [
    (np.array([[1, -1], [2, 0]]), np.array([[0, 0], [1, 1]]), {0: 1, 1: 1}),
    (np.array([[5, 5], [5, 5]]), np.array([[2, 2], [2, 2]]), {2: 4}),
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
    print(result)
    # actual = dict(zip(result["LabelID"], result["Intensity_Count"]))
    # assert actual == expected
    assert 1 == 1