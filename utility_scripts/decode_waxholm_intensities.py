#!/usr/bin/env python3
"""
Recovers true Waxholm label IDs from atlas volumes whose intensities were
rescaled to the full int16 range (max label 502 -> 32767), as happened to the
split-hemisphere files and everything derived from them.

The rescale is linear, so the original ID is recovered with
    label_id = round(intensity * 502 / 32767)

Handles .nii/.nii.gz, a multi-page .tif, or a directory of per-slice tifs.
Output is always an integer dtype - label volumes must never be float, or
downstream int() truncation silently shifts voxels into a neighbouring region.

Usage:
  python3 decode_waxholm_intensities.py <input> <.label file> [output]

Without an output path it only reports the intensity -> id -> name mapping.
"""
import re
import sys
from pathlib import Path

import nibabel as nib
import numpy as np
import tifffile

# Highest IDX in WHS_SD_rat_atlas_v4.label; it maps to int16 max after rescaling.
# This is atlas-version specific - check the .label file before reusing.
MAX_LABEL = 502
INT16_MAX = 32767
OUT_DTYPE = np.int16  # 502 fits comfortably; keeps files half the size of int32

ITKSNAP_LINE_RE = re.compile(
    r'^\s*(-?\d+)\s+\d+\s+\d+\s+\d+\s+[\d.]+\s+[01]\s+[01]\s+"(.*)"\s*$'
)


def read_lut(path):
    lut = {}
    with open(path) as f:
        for line in f:
            m = ITKSNAP_LINE_RE.match(line)
            if m:
                lut[int(m.group(1))] = m.group(2)
    if not lut:
        sys.exit(f"no ITK-SNAP label lines parsed from {path}")
    return lut


def decode(values):
    """Map rescaled intensities back to label IDs."""
    scaled = np.asarray(values, dtype=np.float64) * MAX_LABEL / INT16_MAX
    return np.round(scaled).astype(OUT_DTYPE)


def decode_volume(data):
    """Decode a whole array slice-by-slice so peak memory stays bounded."""
    out = np.empty(data.shape, dtype=OUT_DTYPE)
    for z in range(data.shape[-1]):
        out[..., z] = decode(data[..., z])
    return out


def check(intensities, lut):
    """Refuse to touch anything that isn't a cleanly rescaled label volume."""
    ids = decode(intensities)
    residual = np.abs(
        np.asarray(intensities, dtype=np.float64) * MAX_LABEL / INT16_MAX - ids
    ).max()
    if residual > 0.1:
        sys.exit(f"intensities do not look linearly rescaled (max residual {residual:.3f})")

    unknown = sorted({int(i) for i in ids if int(i) not in lut})
    if unknown:
        sys.exit(f"recovered IDs missing from the .label file: {unknown}")
    return ids, residual


def load(path):
    """Return (data, nifti_image_or_None). TIFF stacks come back as (X, Y, Z)."""
    p = Path(path)
    if p.is_dir():
        files = sorted(p.glob("*.tif*"))
        if not files:
            sys.exit(f"no *.tif files in {p}")
        return np.stack([tifffile.imread(f) for f in files], axis=-1), None
    if p.suffix.lower() in (".tif", ".tiff"):
        # tifffile gives (pages, Y, X); move pages last to match the nifti layout
        return np.moveaxis(tifffile.imread(p), 0, -1), None
    img = nib.load(str(p))
    return np.asanyarray(img.dataobj), img


def save(out_path, decoded, img):
    p = Path(out_path)
    if img is not None:
        # Copy the header for affine/zooms, but force an integer dtype and drop
        # any scaling - inheriting a float32 header is what we are fixing.
        hdr = img.header.copy()
        hdr.set_data_dtype(OUT_DTYPE)
        hdr.set_slope_inter(1, 0)
        nib.save(nib.Nifti1Image(decoded, img.affine, hdr), str(p))
    elif p.suffix.lower() in (".tif", ".tiff"):
        tifffile.imwrite(p, np.moveaxis(decoded, -1, 0))
    else:
        p.mkdir(parents=True, exist_ok=True)
        for z in range(decoded.shape[-1]):
            tifffile.imwrite(p / f"lbls_clar_slice_{z:05d}.tif", decoded[..., z])


def main(in_path, label_path, out_path=None):
    lut = read_lut(label_path)
    data, img = load(in_path)

    intensities = np.unique(data)
    ids, residual = check(intensities, lut)

    for value, label_id in zip(intensities, ids):
        print(f"{float(value):>10.1f}\t{int(label_id):>4}\t{lut[int(label_id)]}")
    print(
        f"\n{len(intensities)} intensities -> {len(set(ids.tolist()))} labels "
        f"(max residual {residual:.4f})",
        file=sys.stderr,
    )

    if out_path:
        decoded = decode_volume(data)
        save(out_path, decoded, img)
        print(f"wrote {out_path} as {np.dtype(OUT_DTYPE).name}", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        sys.exit(f"Usage: {sys.argv[0]} <input> <.label file> [output]")
    main(*sys.argv[1:])
