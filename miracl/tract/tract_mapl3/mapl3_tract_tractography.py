"""
aa_tractography.py
Written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)

Step 2 of the axonal tractography pipeline.

This script loads the intermediate NIfTI files produced by
aa_passing_vs_terminating.py (--save_intermediates) and runs
deterministic streamline tractography on the precomputed
principal fiber direction field.

Algorithm
---------
Deterministic bidirectional tracking per seed:

  1. Seed from every voxel in the injection mask (subsampled if needed).
  2. From each seed, propagate in BOTH directions along the fiber direction
     field (eigenvector of the smallest structure tensor eigenvalue —
     equivalent to DTI's principal diffusion direction).
  3. At every step (nearest-neighbour voxel lookup):
       • Flip direction if the dot product with the previous direction < 0
         (handles the eigenvector sign ambiguity).
       • Stop if: outside the signal mask, FA below threshold,
         turning angle exceeds --max_angle, or streamline reaches
         --max_length_mm.
  4. Merge both halves into one streamline; filter by --min_length_mm.

Parallelism
-----------
Seeds are split into n_jobs batches; each batch is tracked in a
separate process (fork on Linux → copy-on-write for the read-only
direction field and masks).

Coordinate space
----------------
Tracking runs in voxel index space. At the end, the affine from the
reference NIfTI is applied to convert each point to RASMM mm. All
output .trk files are in RASMM space so they open directly in
ITK-SNAP, TrackVis, or DSI Studio alongside the atlas annotation.

Inputs
------
  --fa         : FA.nii.gz          (from --save_intermediates)
  --dirs       : fiber_directions.nii.gz  (from --save_intermediates)
  --seeds      : injection_mask.nii.gz    (from --save_intermediates)
  --mask       : signal_mask.nii.gz       (from --save_intermediates)
  --scores     : termination_score_vol.nii.gz   (optional, for splitting)
  --out        : output directory

Algorithm parameters
--------------------
  --step_vox   : step size in voxels (default: 0.5)
  --max_angle  : maximum turning angle per step in degrees (default: 30)
  --min_length_mm : minimum streamline length in mm (default: 2.0)
  --max_length_mm : maximum streamline length in mm (default: 30.0)
  --fa_thr     : FA below this → stop tracking (default: 0.05)
  --max_seeds  : cap on seeds; random subset drawn if exceeded (default: 20000)
  --score_thr  : termination score threshold for splitting output (default: 0.5)
  --n_jobs     : parallel worker processes (default: 70% of CPU count)
  --rng_seed   : random seed for reproducible seed subsampling (default: 42)

Outputs
-------
  <out>/streamlines.trk              – all accepted streamlines (RASMM)
  <out>/streamlines_passing.trk      – passing streamlines    (if --scores)
  <out>/streamlines_terminating.trk  – terminating streamlines (if --scores)
  <out>/tractography_stats.json      – summary statistics
"""

# ==============================================================================
# Section 1: Imports
# ==============================================================================

import argparse
import json
import multiprocessing
import os
import time
import warnings

import numpy as np
import nibabel as nib
from joblib import Parallel, delayed, parallel_config

from dipy.io.stateful_tractogram import StatefulTractogram, Space
from dipy.io.streamline import save_tractogram
from dipy.tracking.streamline import Streamlines

warnings.filterwarnings("ignore")

from scipy.ndimage import gaussian_filter

from miracl.system.datamodels.miraclobj_utils import parser_true_or_false

# ==============================================================================
# Section 2: Deterministic tracking functions
#
#   We implement a simple nearest-neighbour deterministic tracker rather than
#   using dipy's LocalTracking, because dipy's direction getters require a
#   probability-mass-function on a sphere — for a full brain volume at 25 µm
#   that would need ~100 GB of RAM. Our approach reads the precomputed
#   direction field directly, which is already in memory as a (Z,Y,X,3) array.
# ==============================================================================


def _propagate(
    start, init_dir, dirs, mask, fa_vol, step_vox, cos_thr, fa_thr, max_steps, gap_tol=3
):
    """
    Propagate a streamline in one direction from `start`.

    Uses nearest-neighbour lookup of the direction field at each step.
    The direction sign is kept consistent by flipping when the dot product
    with the previous direction is negative (eigenvector sign ambiguity).

    Gap tolerance
    -------------
    At 25 µm resolution, the voxelized segmentation has holes from missed
    detections and registration artifacts. A strict signal-mask check would
    kill most streamlines at the first gap. Instead, we allow up to `gap_tol`
    consecutive steps outside the signal mask (continuing in the same direction)
    before stopping. If the streamline re-enters the mask within that window,
    the gap counter resets and tracking continues normally.

    Parameters
    ----------
    start    : ndarray (3,) float  – starting voxel coordinates
    init_dir : ndarray (3,) float  – initial unit direction vector
    dirs     : ndarray (Z,Y,X,3)  – fiber direction field in voxel space
    mask     : ndarray (Z,Y,X) bool – signal mask (True = valid region)
    fa_vol   : ndarray (Z,Y,X) float or None – FA map; None = ignore FA check
    step_vox : float – step size in voxels
    cos_thr  : float – cos(max_angle); dot product below this → stop
    fa_thr   : float – minimum FA value to continue
    max_steps: int   – hard limit on steps per direction
    gap_tol  : int   – consecutive out-of-mask steps allowed before stopping

    Returns
    -------
    list of ndarray (3,) – tracked points in voxel coordinates (includes start)
    """
    pts = [start.copy()]
    pos = start.copy()
    direction = init_dir.copy()
    Zmax, Ymax, Xmax = mask.shape
    gap_count = 0  # consecutive steps currently outside signal mask

    for _ in range(max_steps):
        # Move one step
        pos = pos + step_vox * direction

        # Nearest-neighbour voxel index
        z = int(round(pos[0]))
        y = int(round(pos[1]))
        x = int(round(pos[2]))

        # Out-of-bounds → hard stop (no tolerance for leaving the brain volume)
        if not (0 <= z < Zmax and 0 <= y < Ymax and 0 <= x < Xmax):
            break

        # Signal mask check with gap tolerance
        if not mask[z, y, x]:
            gap_count += 1
            if gap_count > gap_tol:
                break
            # Still within tolerance: keep stepping in the same direction.
            # Don't update `direction` here (no valid dir field in the gap).
            pts.append(pos.copy())
            continue
        else:
            gap_count = 0  # back in signal → reset gap counter

        # FA threshold: stop in persistently low-anisotropy regions
        if fa_vol is not None:
            fa = fa_vol[z, y, x]
            if np.isnan(fa) or fa < fa_thr:
                break

        # Direction at new position (only looked up when inside signal mask)
        new_dir = dirs[z, y, x].copy()
        norm = np.linalg.norm(new_dir)
        if norm < 0.5:  # no meaningful direction → end of signal
            break
        new_dir /= norm

        # Handle sign ambiguity: flip to maintain directional continuity
        dot = np.dot(direction, new_dir)
        if dot < 0:
            new_dir = -new_dir
            dot = -dot

        # Turning angle check: stop if curvature exceeds threshold
        if dot < cos_thr:
            break

        direction = new_dir
        pts.append(pos.copy())

    return pts


def track_one_seed(
    seed_vox, dirs, mask, fa_vol, step_vox, cos_thr, fa_thr, max_steps, gap_tol=3
):
    """
    Bidirectional deterministic tracking from a single seed voxel.

    Propagates in both directions along the initial fiber direction, then
    merges the two halves into one streamline (reversed-backward + forward).

    Parameters
    ----------
    seed_vox : ndarray (3,) – seed voxel coordinate (float)
    gap_tol  : int – consecutive out-of-mask steps tolerated (bridging gaps)
    (other params same as _propagate)

    Returns
    -------
    ndarray (N, 3) float32 – streamline in voxel coordinates, or None
    """
    z = int(round(seed_vox[0]))
    y = int(round(seed_vox[1]))
    x = int(round(seed_vox[2]))

    # Bounds guard
    if not (
        0 <= z < mask.shape[0] and 0 <= y < mask.shape[1] and 0 <= x < mask.shape[2]
    ):
        return None

    # Lookup initial direction at seed
    init_dir = dirs[z, y, x].copy()
    norm = np.linalg.norm(init_dir)
    if norm < 0.5:
        return None  # no signal at seed
    init_dir /= norm

    # Forward and backward propagation
    fwd = _propagate(
        seed_vox,
        init_dir,
        dirs,
        mask,
        fa_vol,
        step_vox,
        cos_thr,
        fa_thr,
        max_steps,
        gap_tol,
    )
    bwd = _propagate(
        seed_vox,
        -init_dir,
        dirs,
        mask,
        fa_vol,
        step_vox,
        cos_thr,
        fa_thr,
        max_steps,
        gap_tol,
    )

    # Merge: reverse backward (skip duplicate seed point), then forward
    if len(bwd) > 1:
        combined = list(reversed(bwd[1:])) + fwd
    else:
        combined = fwd

    if len(combined) < 2:
        return None

    return np.array(combined, dtype=np.float32)


def track_batch(
    seeds_batch, dirs, mask, fa_vol, step_vox, cos_thr, fa_thr, max_steps, gap_tol=3
):
    """
    Track a batch of seeds sequentially, returning all valid streamlines.

    Called by joblib workers — each worker gets a batch of seeds plus
    read-only references to the shared direction/mask arrays (copy-on-write
    via fork on Linux).

    Returns
    -------
    list of ndarray (N, 3) float32
    """
    result = []
    for seed in seeds_batch:
        sl = track_one_seed(
            seed, dirs, mask, fa_vol, step_vox, cos_thr, fa_thr, max_steps, gap_tol
        )
        if sl is not None:
            result.append(sl)
    return result


# ==============================================================================
# Section 3: Utility functions
# ==============================================================================


def generate_seeds(injection_mask, max_seeds, rng_seed=42):
    """
    Extract voxel coordinates from the injection mask.

    If the number of mask voxels exceeds max_seeds, randomly sample
    max_seeds of them (reproducible via rng_seed).

    Parameters
    ----------
    injection_mask : ndarray (3D, bool)
    max_seeds      : int – maximum number of seeds to return
    rng_seed       : int – numpy random seed for reproducibility

    Returns
    -------
    seeds : ndarray (N, 3) float32 – voxel coordinates of seeds
    """
    zs, ys, xs = np.where(injection_mask)
    all_seeds = np.stack([zs, ys, xs], axis=1).astype(np.float32)
    n_total = len(all_seeds)

    if n_total == 0:
        raise ValueError("Injection mask is empty — no seeds found.")

    if n_total > max_seeds:
        rng = np.random.default_rng(rng_seed)
        idx = rng.choice(n_total, size=max_seeds, replace=False)
        all_seeds = all_seeds[idx]
        print(f"[Seeds] Sampled {max_seeds:,} / {n_total:,} injection voxels")
    else:
        print(f"[Seeds] Using all {n_total:,} injection voxels as seeds")

    return all_seeds


def apply_affine_batch(affine, streamlines_vox):
    """
    Apply a 4×4 affine to a list of streamlines in voxel coordinates.

    Parameters
    ----------
    affine          : ndarray (4, 4) – voxel-to-mm affine from NIfTI header
    streamlines_vox : list of ndarray (N, 3) – streamlines in voxel space

    Returns
    -------
    list of ndarray (N, 3) float32 – streamlines in RASMM mm
    """
    R = affine[:3, :3]
    t = affine[:3, 3]
    result = []
    for sl in streamlines_vox:
        result.append((sl @ R.T + t).astype(np.float32))
    return result


def streamline_length_mm(sl_mm):
    """
    Compute the Euclidean length of a streamline in mm.

    Parameters
    ----------
    sl_mm : ndarray (N, 3) – streamline in RASMM mm

    Returns
    -------
    float – total arc length in mm
    """
    diffs = np.diff(sl_mm, axis=0)
    return float(np.sum(np.linalg.norm(diffs, axis=1)))


def score_streamlines(streamlines_vox, score_vol, score_thr=0.5):
    """
    Classify each streamline as passing or terminating using the
    termination score volume.

    Strategy: sample the termination score at both endpoints of each
    streamline and take the MAXIMUM. The distal (non-injection) end
    of the streamline carries the most relevant classification signal.
    Score ≥ score_thr → TERMINATING; else → PASSING.

    Parameters
    ----------
    streamlines_vox : list of ndarray (N, 3) – streamlines in voxel coords
    score_vol       : ndarray (3D, float32)  – termination score per voxel
    score_thr       : float – classification threshold (default 0.5)

    Returns
    -------
    labels         : ndarray (M,) str  – 'terminating' or 'passing' per streamline
    endpoint_scores: ndarray (M,) float – max endpoint termination score
    """
    Z, Y, X = score_vol.shape
    labels = []
    scores = []

    for sl in streamlines_vox:
        # Clamp both endpoints to valid voxel range
        def clamp_lookup(pt):
            z = int(np.clip(round(pt[0]), 0, Z - 1))
            y = int(np.clip(round(pt[1]), 0, Y - 1))
            x = int(np.clip(round(pt[2]), 0, X - 1))
            v = score_vol[z, y, x]
            return float(v) if not np.isnan(v) else 0.0

        s0 = clamp_lookup(sl[0])  # one endpoint
        s1 = clamp_lookup(sl[-1])  # other endpoint
        s = max(s0, s1)

        labels.append("terminating" if s >= score_thr else "passing")
        scores.append(s)

    return np.array(labels), np.array(scores, dtype=np.float32)


def save_streamlines(streamlines_mm, ref_nii, stem):
    """
    Save streamlines in RASMM space as both .tck (mrview) and .trk (TrackVis).

    Parameters
    ----------
    streamlines_mm : list of ndarray (N, 3) – in RASMM mm
    ref_nii        : nibabel image  – reference for affine / space metadata
    stem           : str – output path without extension (e.g. './tractography/streamlines')
    """
    sft = StatefulTractogram(
        streamlines=Streamlines(streamlines_mm), reference=ref_nii, space=Space.RASMM
    )
    for ext in (".tck", ".trk"):
        path = stem + ext
        save_tractogram(sft, path, bbox_valid_check=False)
        print(f"[Save] {len(streamlines_mm):>7,} streamlines → {path}")


# ==============================================================================
# Section 4: Direction field smoothing, atlas lookup, CSV export, endpoint filter
# ==============================================================================


def smooth_direction_field(dirs, sigma):
    """
    Apply Gaussian smoothing to each component of a fiber direction field
    and renormalize to unit length.

    Smoothing reduces abrupt directional transitions at tract boundaries
    (e.g. cortex→corpus callosum ~90° turn). Each of the 3 components is
    smoothed independently with the same sigma, then renormalized voxel-by-voxel.
    Voxels with near-zero magnitude (originally zero = outside signal) are left
    as zero to preserve the signal mask boundary.

    Parameters
    ----------
    dirs  : ndarray (Z, Y, X, 3) float32 – raw direction field
    sigma : float – Gaussian sigma in voxels

    Returns
    -------
    ndarray (Z, Y, X, 3) float32 – smoothed, renormalized direction field
    """
    smoothed = np.empty_like(dirs)
    for c in range(3):
        smoothed[..., c] = gaussian_filter(
            dirs[..., c].astype(np.float64), sigma=sigma
        ).astype(np.float32)

    norms = np.linalg.norm(smoothed, axis=-1, keepdims=True)  # (Z, Y, X, 1)
    nonzero = norms[..., 0] > 1e-6
    smoothed[nonzero] = smoothed[nonzero] / norms[nonzero]
    smoothed[~nonzero] = 0.0
    print(
        f"[DirSmooth] Gaussian smoothing applied (sigma={sigma} vox) to direction field."
    )
    return smoothed


def load_atlas_for_tractography(ann_path, graph_path):
    """
    Load atlas annotation volume and structure graph for region lookups.

    Parameters
    ----------
    ann_path   : str – path to atlas annotation NIfTI (uint32, Allen CCF space)
    graph_path : str – path to structure graph CSV with columns id, name, acronym

    Returns
    -------
    image_ann : ndarray (Z, Y, X) uint32
    id_to_row : DataFrame indexed by 'id', columns ['name', 'acronym']
    """
    import pandas as pd

    ann_nii = nib.load(ann_path)
    image_ann = ann_nii.get_fdata().astype(np.uint32)
    graph = pd.read_csv(graph_path)
    id_to_row = graph.set_index("id")[["name", "acronym"]]
    print(
        f"[Atlas] Loaded annotation {image_ann.shape}, {len(id_to_row)} regions in graph."
    )
    return image_ann, id_to_row


def lookup_region(image_ann, pt, id_to_row, shape):
    """
    Look up the atlas region at a single voxel coordinate point.

    Parameters
    ----------
    image_ann : ndarray (Z, Y, X) uint32
    pt        : ndarray (3,) or sequence – voxel coordinate (z, y, x)
    id_to_row : DataFrame indexed by id, columns name, acronym
    shape     : tuple (Z, Y, X) – volume shape for clamping

    Returns
    -------
    (region_id, acronym, name) — all str-safe; 'outside_brain' when atlas_id == 0
    """
    Z, Y, X = shape
    z = int(np.clip(round(float(pt[0])), 0, Z - 1))
    y = int(np.clip(round(float(pt[1])), 0, Y - 1))
    x = int(np.clip(round(float(pt[2])), 0, X - 1))
    rid = int(image_ann[z, y, x])
    if rid == 0:
        return 0, "outside_brain", "outside_brain"
    try:
        row = id_to_row.loc[rid]
        return rid, str(row["acronym"]), str(row["name"])
    except KeyError:
        return rid, f"id_{rid}", f"id_{rid}"


def resolve_region_ids(region_specs, id_to_row):
    """
    Resolve a list of region name strings, acronyms, or integer ID strings to atlas IDs.

    Parameters
    ----------
    region_specs : list of str
    id_to_row    : DataFrame indexed by id, columns name, acronym

    Returns
    -------
    set of int – matched atlas region IDs
    """
    matched_ids = set()
    graph_reset = id_to_row.reset_index()  # columns: id, name, acronym

    for spec in region_specs:
        spec = spec.strip()
        if not spec:
            continue
        # Try integer ID first
        try:
            rid = int(spec)
            if rid in id_to_row.index:
                matched_ids.add(rid)
                print(f"[EndpointFilter] Resolved region ID {rid} from '{spec}'")
            else:
                print(
                    f"[EndpointFilter] Warning: ID {rid} not in atlas graph, skipping."
                )
            continue
        except ValueError:
            pass
        # Case-insensitive exact match, then substring
        sl = spec.lower()
        exact = graph_reset[
            (graph_reset["name"].str.lower() == sl)
            | (graph_reset["acronym"].str.lower() == sl)
        ]
        if exact.empty:
            exact = graph_reset[
                (graph_reset["name"].str.lower().str.contains(sl, na=False))
                | (graph_reset["acronym"].str.lower().str.contains(sl, na=False))
            ]
        if exact.empty:
            print(f"[EndpointFilter] Warning: no region matched '{spec}', skipping.")
        else:
            ids = exact["id"].tolist()
            matched_ids.update(ids)
            print(
                f"[EndpointFilter] '{spec}' matched {len(ids)} region ID(s): {ids[:5]}"
            )

    return matched_ids


def filter_by_endpoint_region(
    streamlines_vox,
    streamlines_mm,
    lengths,
    image_ann,
    id_to_row,
    exclude_outside_brain=False,
    exclude_end_ids=None,
):
    """
    Filter streamlines based on the atlas region at their endpoints.

    Both endpoints (pt[0] and pt[-1]) are checked. A streamline is removed if
    either endpoint falls in an excluded category.

    Parameters
    ----------
    streamlines_vox       : list of ndarray (N, 3) – voxel coordinates
    streamlines_mm        : list of ndarray (N, 3) – RASMM mm coordinates
    lengths               : list of float – arc length per streamline (mm)
    image_ann             : ndarray (Z, Y, X) uint32
    id_to_row             : DataFrame indexed by id
    exclude_outside_brain : bool – remove streamlines with any endpoint atlas_id == 0
    exclude_end_ids       : set of int or None – atlas IDs to exclude at either endpoint

    Returns
    -------
    kept_vox  : list of ndarray
    kept_mm   : list of ndarray
    kept_len  : list of float
    kept_mask : list of bool – True = kept (for downstream label re-indexing)
    """
    if exclude_end_ids is None:
        exclude_end_ids = set()

    ann_shape = image_ann.shape
    kept_vox, kept_mm, kept_len, kept_mask = [], [], [], []
    n_outside = 0
    n_region = 0

    for vox, mm, L in zip(streamlines_vox, streamlines_mm, lengths):
        rid0, _, _ = lookup_region(image_ann, vox[0], id_to_row, ann_shape)
        rid1, _, _ = lookup_region(image_ann, vox[-1], id_to_row, ann_shape)

        if exclude_outside_brain and (rid0 == 0 or rid1 == 0):
            n_outside += 1
            kept_mask.append(False)
            continue

        if rid0 in exclude_end_ids or rid1 in exclude_end_ids:
            n_region += 1
            kept_mask.append(False)
            continue

        kept_vox.append(vox)
        kept_mm.append(mm)
        kept_len.append(L)
        kept_mask.append(True)

    n_removed = n_outside + n_region
    print(
        f"[EndpointFilter] Removed {n_removed:,} streamlines "
        f"({n_outside:,} outside brain, {n_region:,} in excluded regions). "
        f"Kept {len(kept_vox):,}."
    )
    return kept_vox, kept_mm, kept_len, kept_mask


def export_tract_csv(
    streamlines_vox,
    streamlines_mm,
    lengths,
    labels,
    endpoint_scores,
    image_ann,
    id_to_row,
    out_path,
    inj_mask=None,
    sample_every_n=5,
):
    """
    Export per-streamline metadata to a CSV file.

    For each streamline records: origin/end atlas regions, length, number of
    points, pipe-separated unique regions traversed along the tract (sampled
    every sample_every_n points), classification, and endpoint termination score.

    Parameters
    ----------
    streamlines_vox  : list of ndarray (N, 3) – voxel coordinates (for atlas lookup)
    streamlines_mm   : list of ndarray (N, 3) – RASMM mm coordinates
    lengths          : list of float – arc length per streamline (mm)
    labels           : list of str or None – 'passing'/'terminating' / None
    endpoint_scores  : list of float or None
    image_ann        : ndarray (Z, Y, X) uint32
    id_to_row        : DataFrame indexed by id, columns name, acronym
    out_path         : str – output CSV path
    sample_every_n   : int – point sampling interval for region traversal (default 5)

    CSV columns
    -----------
    streamline_id, origin_id, origin_acronym, origin_name,
    end_id, end_acronym, end_name, length_mm, n_points,
    regions_traversed, classification, endpoint_score
    """
    import pandas as pd

    ann_shape = image_ann.shape
    rows = []

    def _acr(rid):
        try:
            return str(id_to_row.loc[rid, "acronym"])
        except KeyError:
            return f"id_{rid}"

    # Helper to check if a voxel coordinate is inside the injection mask
    if inj_mask is not None:
        _IZ, _IY, _IX = inj_mask.shape

        def _in_inj(pt):
            z = int(np.clip(round(float(pt[0])), 0, _IZ - 1))
            y = int(np.clip(round(float(pt[1])), 0, _IY - 1))
            x = int(np.clip(round(float(pt[2])), 0, _IX - 1))
            return bool(inj_mask[z, y, x])
    else:

        def _in_inj(pt):
            return False

    for i, (sl_vox, sl_mm) in enumerate(zip(streamlines_vox, streamlines_mm)):
        # Orient so pt[0] = injection-site end, pt[-1] = distal (target) end.
        # track_one_seed() produces reversed_bwd + fwd; which physical end lands
        # on the injection site is determined by eigenvector sign (random per voxel).
        # Check the injection mask at both endpoints and flip if needed.
        end0_inj = _in_inj(sl_vox[0])
        end1_inj = _in_inj(sl_vox[-1])
        if not end0_inj and end1_inj:
            # pt[-1] is the injection-site end → flip so injection side is pt[0]
            sl_vox = sl_vox[::-1]
            sl_mm = sl_mm[::-1]

        origin_id, origin_acr, origin_name = lookup_region(
            image_ann, sl_vox[0], id_to_row, ann_shape
        )
        end_id, end_acr, end_name = lookup_region(
            image_ann, sl_vox[-1], id_to_row, ann_shape
        )

        # Sample intermediate points for region traversal
        sampled_idx = list(range(0, len(sl_vox), sample_every_n))
        if (len(sl_vox) - 1) not in sampled_idx:
            sampled_idx.append(len(sl_vox) - 1)

        seen = {}
        for idx in sampled_idx:
            rid, _, _ = lookup_region(image_ann, sl_vox[idx], id_to_row, ann_shape)
            if rid not in seen:
                seen[rid] = True
        # Ordered by first appearance, skip outside_brain (id=0)
        regions_traversed_str = "|".join(_acr(rid) for rid in seen if rid != 0)

        classification = labels[i] if labels is not None else "unclassified"
        ep_score = (
            float(endpoint_scores[i]) if endpoint_scores is not None else float("nan")
        )

        rows.append(
            {
                "streamline_id": i,
                "origin_id": origin_id,
                "origin_acronym": origin_acr,
                "origin_name": origin_name,
                "end_id": end_id,
                "end_acronym": end_acr,
                "end_name": end_name,
                "length_mm": round(lengths[i], 4),
                "n_points": len(sl_vox),
                "regions_traversed": regions_traversed_str,
                "classification": classification,
                "endpoint_score": round(ep_score, 4)
                if not np.isnan(ep_score)
                else float("nan"),
            }
        )

    import pandas as pd

    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False)
    print(f"[CSV] Tract metadata saved → {out_path}  ({len(df):,} rows)")
    return df


# ==============================================================================
# Section 5: Argument parsing
# ==============================================================================


def parse_args():
    p = argparse.ArgumentParser(
        description="Deterministic axonal tractography from structure tensor direction field.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required inputs
    p.add_argument(
        "--fa",
        required=True,
        help="FA.nii.gz (from aa_passing_vs_terminating.py --save_intermediates)",
    )
    p.add_argument("--dirs", required=True, help="fiber_directions.nii.gz (4D Z×Y×X×3)")
    p.add_argument("--seeds", required=True, help="injection_mask.nii.gz (seed mask)")
    p.add_argument(
        "--mask", required=True, help="signal_mask.nii.gz (tracking boundary)"
    )
    p.add_argument("--out", required=True, help="Output directory")

    # Optional input
    p.add_argument(
        "--scores",
        help="termination_score_vol.nii.gz (optional; enables passing/terminating split)",
    )

    # Atlas annotation for region-based features (CSV output and endpoint filtering)
    p.add_argument(
        "--ann",
        help=(
            "Atlas annotation NIfTI (uint32, Allen CCF space). "
            "Same file used by aa_passing_vs_terminating.py --ann. "
            "Required for --csv and --exclude_* options."
        ),
    )
    p.add_argument(
        "--graph",
        help=(
            "Allen structure graph CSV with columns id, name, acronym. "
            "Required when --ann is provided."
        ),
    )

    # Tracking parameters
    p.add_argument(
        "--step_vox",
        type=float,
        default=0.5,
        help=(
            "Step size in voxels (default 0.5 = 12.5 µm at 25 µm resolution). "
            "Direction field has 1-voxel resolution so steps < 0.5 add "
            "smoothness with no direction fidelity gain. Larger steps "
            "(1.0) are faster but miss tight turns. 0.5 recommended."
        ),
    )
    p.add_argument(
        "--max_angle",
        type=float,
        default=30.0,
        help="Maximum turning angle per step in degrees",
    )
    p.add_argument(
        "--min_length_mm",
        type=float,
        default=2.0,
        help="Minimum streamline length in mm (shorter streamlines discarded)",
    )
    p.add_argument(
        "--max_length_mm",
        type=float,
        default=30.0,
        help="Maximum streamline length in mm (longer streamlines truncated at stop)",
    )
    p.add_argument(
        "--fa_thr",
        type=float,
        default=0.05,
        help="Stop tracking if FA drops below this value (0 = disable FA check)",
    )
    p.add_argument(
        "--gap_tol",
        type=int,
        default=5,
        help=(
            "Consecutive out-of-mask steps tolerated before stopping. "
            "Bridges small holes in the binary segmentation caused by "
            "noise or missed detections. 5 voxels ≈ 125 µm at 25 µm resolution."
        ),
    )
    p.add_argument(
        "--smooth_dirs",
        type=float,
        default=0.0,
        help=(
            "Gaussian smoothing sigma (voxels) applied to the fiber direction "
            "field after loading, before tracking. 0 = disabled (default). "
            "Recommended 1.0–1.5 to improve corpus callosum and other "
            "interhemispheric tract tracking where cortex→CC direction "
            "transitions cause abrupt ~90° turns that exceed --max_angle."
        ),
    )

    # Seeding
    p.add_argument(
        "--max_seeds",
        type=int,
        default=20000,
        help="Maximum seeds; random subset drawn if injection mask is larger",
    )
    p.add_argument(
        "--rng_seed",
        type=int,
        default=42,
        help="Random seed for reproducible seed subsampling",
    )

    # Classification
    p.add_argument(
        "--score_thr",
        type=float,
        default=0.5,
        help="Termination score threshold for splitting streamlines (requires --scores)",
    )

    # CSV output
    p.add_argument(
        "--csv",
        required=False,
        default=True,
        type=parser_true_or_false,
        help=(
            "Export per-streamline metadata CSV (origin region, end region, "
            "length, traversed regions, classification, endpoint score). "
            "Requires --ann and --graph."
        ),
    )
    p.add_argument(
        "--csv_sample_n",
        type=int,
        default=5,
        help=(
            "Sample every N points along each streamline for region-traversal "
            "lookup in the CSV. Default 5 ≈ every 62.5 µm at 25 µm resolution."
        ),
    )

    # Endpoint filtering
    p.add_argument(
        "--exclude_outside_brain",
        required=False,
        default=True,
        type=parser_true_or_false,
        help=(
            "Remove streamlines where either endpoint is outside the brain "
            "(atlas_id == 0). Requires --ann."
        ),
    )
    p.add_argument(
        "--exclude_end_regions",
        default="",
        help=(
            "Comma-separated region names, acronyms, or integer IDs. "
            "Streamlines where either endpoint falls in any of these regions "
            "are removed. Example: 'fiber tracts,VS,1009'. "
            "Requires --ann and --graph."
        ),
    )

    # Compute
    p.add_argument(
        "--n_jobs",
        type=int,
        default=0,
        help="Parallel worker processes (0 = 70%% of CPU count)",
    )

    return p.parse_args()


# ==============================================================================
# Section 5: Main pipeline
# ==============================================================================


def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)
    total_t0 = time.time()

    # ── Resolve n_jobs ──────────────────────────────────────────────────────
    if args.n_jobs <= 0:
        cpus = multiprocessing.cpu_count()
        n_jobs = max(1, int(0.7 * cpus))
    else:
        n_jobs = args.n_jobs
    print(f"[Init] Using {n_jobs} worker processes")

    # ──────────────────────────────────────────────────────────────────────────
    # 5.1  Load inputs
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("LOADING INPUTS")
    print("=" * 60)

    # FA map (3D)
    fa_nii = nib.load(args.fa)
    fa_vol = fa_nii.get_fdata(dtype=np.float32)
    # NaN was already written by aa_passing_vs_terminating.py for non-signal voxels.
    # Do NOT convert 0→NaN here: 0 is a valid (isotropic) FA within signal voxels.
    print(
        f"  FA map         : {fa_vol.shape}  "
        f"range [{np.nanmin(fa_vol):.3f}, {np.nanmax(fa_vol):.3f}]"
    )

    # Fiber direction field (4D: Z×Y×X×3)
    dirs_nii = nib.load(args.dirs)
    dirs = dirs_nii.get_fdata(dtype=np.float32)
    print(f"  Directions     : {dirs.shape}")

    # Injection mask (seed mask)
    seeds_nii = nib.load(args.seeds)
    inj_mask = seeds_nii.get_fdata(dtype=np.float32).astype(bool)
    print(f"  Injection mask : {inj_mask.shape}  ({inj_mask.sum():,} voxels)")

    # Signal mask (tracking boundary)
    mask_nii = nib.load(args.mask)
    signal_mask = mask_nii.get_fdata(dtype=np.float32).astype(bool)
    print(f"  Signal mask    : {signal_mask.shape}  ({signal_mask.sum():,} voxels)")

    # Verify all volumes have the same spatial shape
    shapes = {fa_vol.shape, dirs.shape[:3], inj_mask.shape, signal_mask.shape}
    if len(shapes) > 1:
        raise ValueError(
            f"Input volumes have mismatched shapes: {shapes}. "
            "All must come from the same --save_intermediates run."
        )

    # Reference NIfTI (used for affine and .trk header)
    # Use FA as the reference — it has the correct 3D shape and affine
    ref_nii = fa_nii
    affine = ref_nii.affine

    # Infer voxel size for reporting (assumes isotropic)
    zoom_mm = float(np.abs(fa_nii.header.get_zooms()[0]))
    voxel_size_mm = zoom_mm if zoom_mm > 0 else 0.025
    print(
        f"\n  Voxel size     : {voxel_size_mm * 1000:.1f} µm  ({voxel_size_mm:.4f} mm)"
    )

    # Termination score volume (optional)
    score_vol = None
    if args.scores:
        score_nii = nib.load(args.scores)
        score_vol = score_nii.get_fdata(dtype=np.float32)
        print(
            f"  Score volume   : {score_vol.shape}  (loaded for streamline splitting)"
        )

    # Atlas annotation + structure graph (optional — for CSV export and endpoint filtering)
    image_ann = None
    id_to_row = None
    if args.ann:
        if not args.graph:
            raise ValueError("--ann requires --graph to be provided as well.")
        image_ann, id_to_row = load_atlas_for_tractography(args.ann, args.graph)
        if image_ann.shape != fa_vol.shape:
            raise ValueError(
                f"Atlas annotation shape {image_ann.shape} does not match "
                f"FA map shape {fa_vol.shape}. Both must be in Allen CCF space."
            )

    # ── Optional direction field smoothing ─────────────────────────────────────
    if args.smooth_dirs > 0:
        print(
            f"\n[DirSmooth] Smoothing direction field with sigma={args.smooth_dirs} vox ..."
        )
        dirs = smooth_direction_field(dirs, sigma=args.smooth_dirs)

    # ──────────────────────────────────────────────────────────────────────────
    # 5.2  Tracking parameters
    # ──────────────────────────────────────────────────────────────────────────
    step_vox = args.step_vox
    step_mm = step_vox * voxel_size_mm
    cos_thr = float(np.cos(np.deg2rad(args.max_angle)))
    fa_thr = args.fa_thr if args.fa_thr > 0 else None
    max_steps = int(np.ceil(args.max_length_mm / step_mm))

    print("\n" + "=" * 60)
    print("TRACKING PARAMETERS")
    print("=" * 60)
    print(
        f"  Step size      : {step_vox} voxels  ({step_mm * 1000:.1f} µm  /  {step_mm:.4f} mm)"
    )
    print(f"  Max angle      : {args.max_angle}°")
    print(f"  FA threshold   : {fa_thr if fa_thr is not None else 'disabled'}")
    print(
        f"  Gap tolerance  : {args.gap_tol} voxels  ({args.gap_tol * voxel_size_mm * 1000:.0f} µm)"
    )
    print(f"  Length range   : {args.min_length_mm} – {args.max_length_mm} mm")
    print(f"  Max steps/dir  : {max_steps:,}")
    print(f"  Workers        : {n_jobs}")

    # ──────────────────────────────────────────────────────────────────────────
    # 5.3  Generate seeds
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("GENERATING SEEDS")
    print("=" * 60)

    seeds = generate_seeds(inj_mask, max_seeds=args.max_seeds, rng_seed=args.rng_seed)
    n_seeds = len(seeds)

    # ──────────────────────────────────────────────────────────────────────────
    # 5.4  Parallel tracking
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"TRACKING {n_seeds:,} SEEDS  (parallel, {n_jobs} workers)")
    print("=" * 60)

    # Split seeds into n_jobs roughly equal batches.
    # Each worker gets a batch and tracks it sequentially.
    # On Linux (fork), the large read-only arrays (dirs, signal_mask, fa_vol)
    # are shared copy-on-write, so memory is not duplicated per worker.
    batches = np.array_split(seeds, n_jobs)

    t0 = time.time()
    fa_arg = fa_vol if (fa_thr is not None) else None

    with parallel_config(backend="loky", n_jobs=n_jobs):
        batch_results = Parallel()(
            delayed(track_batch)(
                batch,
                dirs,
                signal_mask,
                fa_arg,
                step_vox,
                cos_thr,
                fa_thr if fa_thr is not None else -1.0,
                max_steps,
                args.gap_tol,
            )
            for batch in batches
        )

    # Flatten batch results into one list
    streamlines_vox = []
    for batch_sls in batch_results:
        streamlines_vox.extend(batch_sls)

    n_tracked = len(streamlines_vox)
    elapsed = time.time() - t0
    print(
        f"[Track] {n_tracked:,} raw streamlines generated in {elapsed:.1f}s "
        f"({n_seeds / elapsed:.0f} seeds/s)"
    )

    # ──────────────────────────────────────────────────────────────────────────
    # 5.5  Convert to RASMM and filter by length
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FILTERING BY LENGTH")
    print("=" * 60)

    # Convert from voxel coordinates to RASMM mm using the NIfTI affine,
    # and filter by length in a single pass to keep vox/mm lists in sync.
    all_mm, all_vox, lengths = [], [], []
    for vox in streamlines_vox:
        mm = apply_affine_batch(affine, [vox])[0]
        L = streamline_length_mm(mm)
        if args.min_length_mm <= L <= args.max_length_mm:
            all_mm.append(mm)
            all_vox.append(vox)
            lengths.append(L)

    streamlines_mm = all_mm
    streamlines_vox = all_vox

    n_kept = len(streamlines_mm)
    mean_L = float(np.mean(lengths)) if lengths else 0.0

    print(
        f"  Kept   : {n_kept:,} / {n_tracked:,} streamlines "
        f"(mean length {mean_L:.1f} mm)"
    )
    print(f"  Removed: {n_tracked - n_kept:,} (too short or too long)")

    # ──────────────────────────────────────────────────────────────────────────
    # 5.5b  Endpoint region filtering (optional)
    # ──────────────────────────────────────────────────────────────────────────
    n_endpoint_filtered = 0
    do_ep_filter = image_ann is not None and (
        args.exclude_outside_brain or args.exclude_end_regions.strip()
    )

    if do_ep_filter:
        print("\n" + "=" * 60)
        print("FILTERING BY ENDPOINT REGION")
        print("=" * 60)

        exclude_end_ids = set()
        if args.exclude_end_regions.strip():
            specs = [s.strip() for s in args.exclude_end_regions.split(",")]
            exclude_end_ids = resolve_region_ids(specs, id_to_row)

        n_before_ep = n_kept
        streamlines_vox, streamlines_mm, lengths, kept_mask = filter_by_endpoint_region(
            streamlines_vox,
            streamlines_mm,
            lengths,
            image_ann,
            id_to_row,
            exclude_outside_brain=args.exclude_outside_brain,
            exclude_end_ids=exclude_end_ids,
        )

        n_kept = len(streamlines_mm)
        n_endpoint_filtered = n_before_ep - n_kept
        mean_L = float(np.mean(lengths)) if lengths else 0.0
        print(
            f"  After endpoint filter: {n_kept:,} streamlines remain "
            f"(mean length {mean_L:.1f} mm)"
        )

    elif (
        args.exclude_outside_brain or args.exclude_end_regions.strip()
    ) and image_ann is None:
        print(
            "[EndpointFilter] Warning: --exclude_outside_brain / --exclude_end_regions "
            "requested but --ann not provided. Skipping endpoint filtering."
        )

    # ──────────────────────────────────────────────────────────────────────────
    # 5.6  Save all streamlines
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("SAVING STREAMLINES")
    print("=" * 60)

    save_streamlines(streamlines_mm, ref_nii, os.path.join(args.out, "streamlines"))

    # ──────────────────────────────────────────────────────────────────────────
    # 5.7  Score-based splitting (optional)
    # ──────────────────────────────────────────────────────────────────────────
    n_term = n_pass = 0
    labels = None
    endpoint_scores_arr = None

    if score_vol is not None and n_kept > 0:
        print("\n" + "=" * 60)
        print("CLASSIFYING STREAMLINES BY TERMINATION SCORE")
        print("=" * 60)

        labels, endpoint_scores_arr = score_streamlines(
            streamlines_vox, score_vol, score_thr=args.score_thr
        )

        term_sls = [sl for sl, l in zip(streamlines_mm, labels) if l == "terminating"]
        pass_sls = [sl for sl, l in zip(streamlines_mm, labels) if l == "passing"]
        n_term = len(term_sls)
        n_pass = len(pass_sls)

        print(
            f"  Terminating : {n_term:,}  |  Passing : {n_pass:,}  "
            f"(threshold {args.score_thr})"
        )

        if n_term > 0:
            save_streamlines(
                term_sls, ref_nii, os.path.join(args.out, "streamlines_terminating")
            )
        if n_pass > 0:
            save_streamlines(
                pass_sls, ref_nii, os.path.join(args.out, "streamlines_passing")
            )

    # ──────────────────────────────────────────────────────────────────────────
    # 5.7b  Per-streamline CSV export (optional)
    # ──────────────────────────────────────────────────────────────────────────
    if args.csv:
        if image_ann is None:
            print("[CSV] Warning: --csv requires --ann and --graph. Skipping.")
        elif n_kept > 0:
            print("\n" + "=" * 60)
            print("EXPORTING TRACT METADATA CSV")
            print("=" * 60)
            export_tract_csv(
                streamlines_vox,
                streamlines_mm,
                lengths,
                list(labels) if labels is not None else None,
                list(endpoint_scores_arr) if endpoint_scores_arr is not None else None,
                image_ann,
                id_to_row,
                out_path=os.path.join(args.out, "tract_metadata.csv"),
                inj_mask=inj_mask,
                sample_every_n=args.csv_sample_n,
            )
        else:
            print("[CSV] No streamlines to export.")

    # ──────────────────────────────────────────────────────────────────────────
    # 5.8  Statistics JSON
    # ──────────────────────────────────────────────────────────────────────────
    stats = {
        "n_seeds": int(n_seeds),
        "n_raw_streamlines": int(n_tracked),
        "n_kept_streamlines": int(n_kept),
        "n_endpoint_filtered": int(n_endpoint_filtered),
        "mean_length_mm": round(mean_L, 2),
        "voxel_size_mm": round(voxel_size_mm, 6),
        "step_size_vox": args.step_vox,
        "step_size_mm": round(step_mm, 6),
        "max_angle_deg": args.max_angle,
        "smooth_dirs_sigma": args.smooth_dirs,
        "fa_threshold": args.fa_thr,
        "gap_tolerance_vox": args.gap_tol,
        "min_length_mm": args.min_length_mm,
        "max_length_mm": args.max_length_mm,
        "score_threshold": args.score_thr,
        "n_terminating": int(n_term),
        "n_passing": int(n_pass),
        "exclude_outside_brain": args.exclude_outside_brain,
        "exclude_end_regions": args.exclude_end_regions,
        "total_time_s": round(time.time() - total_t0, 1),
    }

    stats_path = os.path.join(args.out, "tractography_stats.json")
    with open(stats_path, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\n[Stats] Saved → {stats_path}")

    print("\n" + "=" * 60)
    print(f"DONE  ({stats['total_time_s']:.0f}s total)")
    print("=" * 60)


if __name__ == "__main__":
    main()
