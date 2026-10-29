#!/bin/bash
#SBATCH --job-name=feat_extract_fixed
#SBATCH --account=def-YOURPI            # <-- set your Alliance allocation
#SBATCH --time=12:00:00                 # bump to 24:00:00 if it runs long (see NOTES)
#SBATCH --cpus-per-task=4               # parallel workers -- MEMORY SCALES WITH THIS
#SBATCH --mem=160G                      # ~25 GB baseline + ~28 GB per worker (see NOTES)
#SBATCH --output=feat_extract_fixed-%j.out

# Runs the corrected region-wise feature extraction (miracl seg feat_extract_fixed)
# inside the MIRACL Apptainer container on FIR, using your EDITED checkout so the
# fix (connected-component counting + int32 atlas IDs) is what actually executes.

set -euo pipefail

module load apptainer            # or a pinned version, e.g. apptainer/1.3.5

# ---- paths: EDIT THESE ----------------------------------------------------
SIF="$SCRATCH/miracl_latest.sif"                                 # MIRACL apptainer image (.sif)
REPO="$SCRATCH/MIRACL"                                           # your checkout w/ the feat_extract_fixed changes (branch compute-canada-fix)
DATA="$SCRATCH/data"                                             # directory holding the inputs
SEG="$DATA/voxelized_seg_seg.tiff"                               # voxelized segmentation
LBL="$DATA/annotation_hemi_combined_10um_clar_vox.tif"          # Allen labels
# ---------------------------------------------------------------------------

apptainer exec \
  --bind "$DATA":"$DATA" \
  --bind "$REPO":/opt/miracl_fixed \
  --env PYTHONPATH=/opt/miracl_fixed \
  --env MIRACL_HOME=/code/miracl \
  --env MIRACL_FEAT_NCPUS="${SLURM_CPUS_PER_TASK:-4}" \
  "$SIF" \
  python -m miracl.cli seg feat_extract_fixed \
    -s "$SEG" \
    -l "$LBL"

echo "Done. Output CSV -> $DATA/clarity_segmentation_features_ara_labels.csv"

# =============================== NOTES =====================================
# MEMORY: labels are upsampled to seg resolution (~975x1840x1850), and EACH
#   worker allocates full-volume arrays (mask uint16 ~6.6 GB + ndimage.label
#   int32 ~13.3 GB + bool masks ~6.6 GB) ~= ~28 GB/worker, on top of a ~25 GB
#   shared baseline. So:  --mem  >=  25 + (--cpus-per-task * 28)  GB.
#     cpus=2 -> ~96G   cpus=4 -> ~160G   cpus=8 -> ~256G (largemem node)
#   MIRACL_FEAT_NCPUS caps the workers to your SLURM cpu request (the script
#   would otherwise spawn 0.95 * ALL node cores and OOM instantly).
#
# TIME: cost is dominated by a full-volume connected-component labeling PER
#   region (~hundreds of regions). Budget generously; 12h is a starting point.
#
# CODE SOURCE: PYTHONPATH=/opt/miracl_fixed makes `import miracl` use your
#   bind-mounted checkout (the fix), while MIRACL_HOME=/code/miracl keeps the
#   atlases resolving to the container's /code/atlases.
# ===========================================================================
