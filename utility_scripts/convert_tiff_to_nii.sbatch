#!/bin/bash
#SBATCH --job-name=tiff2nii
#SBATCH --partition=CHANGEME              # TODO: fill in - your cluster's partition/QOS
#SBATCH --account=CHANGEME                # TODO: fill in - your billing account
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32                # matches the joblib thread pool (~95% of cores)
#SBATCH --mem=768G                        # intermediate memmap + z-downsample copy can spike this high
#SBATCH --time=24:00:00                   # guess - tune after a test run
#SBATCH --tmp=1200G                       # scratch/local disk for the intermediate memmap + output
#SBATCH --output=tiff2nii_%j.log
#SBATCH --error=tiff2nii_%j.log

set -euo pipefail

# =========================================================================
# Required - fill these in
# =========================================================================
TIFF_DIR="CHANGEME"                       # TODO: fill in - input tiff folder (-f)
RES_XY="CHANGEME"                         # TODO: fill in - native x-y resolution in um (-vx)
RES_Z="CHANGEME"                          # TODO: fill in - native z spacing in um (-vz)

# =========================================================================
# Defaults - override if you're not happy with these
# =========================================================================
WORK_DIR="${SLURM_TMPDIR:-/path/to/scratch/tiff2nii_${SLURM_JOB_ID}}"  # TODO if no SLURM_TMPDIR on your cluster
OUT_NAME="clarity"                        # (-o) output nifti base name
DOWN=2                                    # (-d) downsample ratio
DOWN_Z=1                                  # (-dz) 1 = also downsample z by DOWN (or DOWN scaled by vx/vz), 0 = keep native z
CHAN_NAME="eyfp"                          # (-ch) output channel name

# =========================================================================
# Optional - only needed for multi-channel tiff filenames (e.g. "...C00...", "...C01...")
# Leave blank ("") to convert all files in TIFF_DIR as a single channel.
# =========================================================================
CHAN_NUM=""                               # (-cn) channel number, e.g. 0
CHAN_PREFIX=""                            # (-cp) prefix before the channel number, e.g. C00

mkdir -p "$WORK_DIR"

# --- environment ---
source /opt/miniconda/etc/profile.d/conda.sh
conda activate base

CHAN_ARGS=()
if [[ -n "$CHAN_NUM" ]]; then
    CHAN_ARGS+=(-cn "$CHAN_NUM")
fi
if [[ -n "$CHAN_PREFIX" ]]; then
    CHAN_ARGS+=(-cp "$CHAN_PREFIX")
fi

python /workspaces/MIRACL/miracl/conv/miracl_conv_convertTIFFtoNII.py \
    -f "$TIFF_DIR" \
    -w "$WORK_DIR" \
    -o "$OUT_NAME" \
    -d "$DOWN" \
    -dz "$DOWN_Z" \
    -ch "$CHAN_NAME" \
    -vx "$RES_XY" \
    -vz "$RES_Z" \
    "${CHAN_ARGS[@]}"

echo "Done. Output in $WORK_DIR/conv_final/"
