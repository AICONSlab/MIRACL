#!/usr/bin/env python3
import sys
from pathlib import Path
import nibabel as nib
import numpy as np


def percentile_threshold(data: np.ndarray, percentile_thr: float) -> np.ndarray:
    """
    Threshold extreme values using the given percentile.
    Clips values below percentile_thr and above (100 - percentile_thr).
    """
    p_low = np.percentile(data, percentile_thr)
    p_high = np.percentile(data, 100 - percentile_thr)
    return np.clip(data, p_low, p_high)


if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} <input_nii> <percentile_thr> <output_dir>")
    sys.exit(1)

input_file = Path(sys.argv[1])
pct_thr = float(sys.argv[2])
output_dir = Path(sys.argv[3])

if not input_file.exists():
    print(f"ERROR: Input file '{input_file}' does not exist.")
    sys.exit(1)

output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / input_file.name

img = nib.load(str(input_file))
data = img.get_fdata()

data = percentile_threshold(data, pct_thr)

out_img = nib.Nifti1Image(data, img.affine, img.header)
nib.save(out_img, str(output_file))

print(f"Percentile threshold applied. Output saved to: {output_file}")
