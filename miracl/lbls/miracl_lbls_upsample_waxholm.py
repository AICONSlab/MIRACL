# Upsamples a downsampled, registered Waxholm labels volume to native resolution
# and writes it as a single NIfTI sharing the raw scan's affine, so it loads in
# ITK-SNAP as an aligned segmentation overlay.

from pathlib import Path

import nibabel as nib
import numpy as np
import tifffile
from tqdm import tqdm

# --- config ---
LABELS_WARPED_DOWNSAMPLED = "/workspaces/level4/sub-CAF_sample-rightHemi_acq-imaris_seg-all_level-4_from-WHSv4_dseg.nii.gz"  #"labels_warped_downsampled.nii.gz"
RAW_NATIVE_NII = "/path/to/conv_final/clarity_02x_down_eyfp_chan.nii.gz"  # TODO: native-res raw nifti; its affine defines the overlay's target geometry
OUTPUT_DIR = Path("/workspaces/MIRACL/native_label_tiffs")
OUTPUT_NII = OUTPUT_DIR / "labels_native_res.nii"
FULL_X, FULL_Y, FULL_Z = 7092, 10297, 3129   # native mask stack dims (width, height, depth)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Low-res volume is small (a few hundred MB) - load it once, fully, into memory.
low_res_img = nib.load(LABELS_WARPED_DOWNSAMPLED)
low_res_vol = np.asarray(low_res_img.dataobj).astype(np.uint16)  # (low_x, low_y, low_z)
low_x, low_y, low_z = low_res_vol.shape

raw_img = nib.load(RAW_NATIVE_NII)
assert raw_img.shape[:3] == (FULL_X, FULL_Y, FULL_Z), (
    f"raw nifti shape {raw_img.shape[:3]} doesn't match configured "
    f"FULL_X/FULL_Y/FULL_Z ({FULL_X}, {FULL_Y}, {FULL_Z}) - "
    "the overlay won't align in ITK-SNAP unless these match"
)

# Precompute nearest-neighbor index maps once
x_idx = (np.arange(FULL_X) * low_x // FULL_X)
y_idx = (np.arange(FULL_Y) * low_y // FULL_Y)

# Native-res label volume is too big to hold in memory - memmap it to disk.
MEMMAP_PATH = OUTPUT_DIR / "labels_native_res.memmap"
out_vol = np.memmap(MEMMAP_PATH, dtype=np.uint16, mode="w+", shape=(FULL_X, FULL_Y, FULL_Z))


def upsample_slice(z: int) -> None:
    # nearest source z-slice for this output z
    src_z = z * low_z // FULL_Z
    low_res_slice = low_res_vol[:, :, src_z]          # (low_x, low_y)

    # nearest-neighbor upsample via pure index remapping
    upsampled = low_res_slice[np.ix_(x_idx, y_idx)]   # (FULL_X, FULL_Y)

    out_vol[:, :, z] = upsampled

    tifffile.imwrite(
        OUTPUT_DIR / f"label_slice_{z:06d}.tif",
        upsampled.T,  # tifffile treats dim0 as rows/height, so transpose to (FULL_Y, FULL_X)
        dtype=np.uint16,
    )


if __name__ == "__main__":
    for z in tqdm(range(FULL_Z)):
        upsample_slice(z)

    out_vol.flush()
    nii = nib.Nifti1Image(np.asarray(out_vol), raw_img.affine)
    nii.header.set_data_dtype(np.uint16)
    nib.save(nii, OUTPUT_NII)
    MEMMAP_PATH.unlink()

    print(f"\n wrote {OUTPUT_NII}")
