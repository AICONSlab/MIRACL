#!/bin/bash
#SBATCH --job-name=upsample_labels
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00                   # guess - tune after a test run
#SBATCH --output=upsample_labels_%j.log
#SBATCH --error=upsample_labels_%j.log

set -euo pipefail

# =========================================================================
# Required - fill these in
# =========================================================================
BASE_FOLDER="/mgproject/aiconsgrp/projects/rat_brain_segmentation"
LABELS_NII="${BASE_FOLDER}/level4/sub-CAF_sample-rightHemi_acq-imaris_seg-all_level-4_from-WHSv4_dseg.nii.gz"        # downsampled/registered labels nifti (input)
TIFF_STACK_DIR="${BASE_FOLDER}/level4/tiff_stack_dir"    # where step 1's upsampled label tiff stack goes
OUT_NAME="labels_native"     # base name for the final nifti (exact filename gets a _01x_down_labels_chan suffix)
UX=16
UY=16
UZ=4

MIRACL_REPO="${BASE_FOLDER}/MIRACL"

mkdir -p "$TIFF_STACK_DIR"

echo "upsample ratio (x y z): $UX $UY $UZ"
# Note: scipy.ndimage.zoom rounds its output shape, so this can land off by a
# voxel or two from RAW_NATIVE_NII's exact shape - fine for a visual ITK-SNAP
# comparison, not guaranteed pixel-perfect.

# --- step 1: labels nifti -> upsampled tiff stack (nearest-neighbor, label-safe) ---
apptainer exec -B "${MIRACL_REPO}/miracl:/code/miracl" miracl_container.sif \
    python /code/miracl/conv/miracl_conv_convertNIItoTIFF.py \
        -i "$LABELS_NII" \
        -o "$TIFF_STACK_DIR" \
        -u "$UX" "$UY" "$UZ" \
        -s 0 \
        -st
        # add "-tp" above if your numeric verification check says the axes need swapping

echo "Done. Output in ${TIFF_STACK_DIR}"
