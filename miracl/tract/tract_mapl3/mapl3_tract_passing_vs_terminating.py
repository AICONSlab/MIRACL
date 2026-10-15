"""
Written by Ahmadreza Attarpour (a.attarpour@mail.utoronto.ca)

Differentiates passing vs. terminating axonal fibers at the atlas-region level.

Background
----------
At 25 µm voxel resolution (Allen CCF space), individual axons (~0.5 µm) are not
resolvable. What we observe is the aggregate fluorescent DENSITY from many co-aligned
axons. The key insight is that:

  • Passing fiber bundles  → elongated, anisotropic signal (tube/sheet in the volume)
  • Terminating fields     → diffuse, isotropic signal (fan-out arborization)

Three complementary signals capture this distinction per atlas region:

  Signal 1 | Structure Tensor Fractional Anisotropy (3D)
               Computed directly on the voxelized segmentation volume.
               FA ≈ 1  → elongated bundle  → PASSING
               FA ≈ 0  → isotropic cloud   → TERMINATING

  Signal 2 | Depth Variance (primary: MIP-based; fallback: 3D voxel-based)
               Measures how much the axonal signal is spread across depth layers
               along the projection axis inside each atlas region.

               Primary method (MIP-based, ~70% of regions):
                 For regions visible in the 2D MIP, uses MIP_depth = argmax
                 along the projection axis per pixel.
                 Low std(MIP_depth) within a region → signal at one depth  → PASSING
                 High std(MIP_depth) within a region → signal spread 3-D   → TERMINATING

               Fallback method (3D voxel-based, ~30% of regions):
                 Some regions have enough 3D signal to compute FA but project
                 to fewer than min_pixels pixels in the MIP — typically small
                 subcortical nuclei that are "hidden" underneath a brighter
                 region along the projection axis. For these, depth variance is
                 computed directly from the spread of signal voxel coordinates
                 along the projection axis in 3D. Same concept, more complete.

  Signal 3 | Distance from Injection Site (3D prior)
               Computes a Euclidean distance transform from the injection-site
               voxels in 3D. For each atlas region, takes the mean distance of
               its signal voxels from the injection site.
               Low mean distance  → still close to source   → PASSING (en route)
               High mean distance → far from source          → TERMINATING
               Biological rationale: in anterograde tracing the injection site
               is the soma. Signal immediately adjacent to it is from local
               collaterals/dendrites (not terminals). The further the signal
               travels, the more likely it represents a projection terminal.

Inputs
------
  --seg      : voxelized segmentation NIfTI in Allen CCF space
  --raw      : raw fluorescence NIfTI in Allen CCF space (optional, used for viz)
  --ann      : atlas annotation NIfTI (e.g. annotation_hemi_split_25um.nii.gz)
  --graph    : Allen structure graph CSV (e.g. ara_mouse_structure_graph_hemi_split.csv)
  --inj      : injection site name or acronym (e.g. "RORB")
  --exclude  : comma-separated region names/IDs to exclude (e.g. "olfactory bulb")
  --out      : output directory
  --axis     : projection axis for MIP (default 1 = anterior-posterior)
  --sigma    : Gaussian sigma for structure tensor smoothing (default 1.5 voxels)
  --w_fa     : weight for FA signal when combining scores (default 0.4)
  --w_dv     : weight for depth-variance signal (default 0.3)
  --w_di     : weight for injection-distance signal (default 0.3)
  --min_sig  : minimum signal threshold for voxel inclusion (default 0.1)
  --min_vox  : minimum signal voxels required to score a region (default 20)
  --save_nii          : save termination-score volume as NIfTI (bool)
  --save_intermediates: save tractography input volumes as NIfTI (bool)

Outputs
-------
  <out>/region_scores.csv             – per-region scores and final classification
  <out>/mip_termination_overlay.png   – MIP colored by termination score per region
  <out>/top_regions_barplot.png       – ranked bar chart of termination scores
  <out>/termination_score_vol.nii.gz  – 3D score volume (if --save_nii)

  If --save_intermediates, all in the same Allen CCF 25 µm space as --seg
  (same affine/header, safe to overlay on atlas in ITK-SNAP or Fiji):
  <out>/FA.nii.gz                     – 3D FA map (float32, NaN outside signal)
  <out>/fiber_directions.nii.gz       – 4D principal fiber direction field (Z×Y×X×3),
                                        eigenvector of smallest structure tensor eigenvalue
                                        ≡ DTI principal diffusion direction; zero outside signal
  <out>/injection_mask.nii.gz         – 3D binary mask of injection site (uint8)
  <out>/signal_mask.nii.gz            – 3D binary mask of segmentation signal (uint8)

Usage example
-------------
  python aa_passing_vs_terminating.py \\
    --seg  /data4/.../voxelized_seg_postprocessed_mapl3_channel_allen_space.nii.gz \\
    --ann  /data4/.../annotation_hemi_split_25um.nii.gz \\
    --graph /data4/.../ara_mouse_structure_graph_hemi_split.csv \\
    --inj  RORB \\
    --exclude "olfactory bulb" \\
    --out  /data4/.../passing_vs_terminating \\
    --save_nii true
"""

# ==============================================================================
# Section 1: Imports
# ==============================================================================

import argparse
import os
import warnings

import numpy as np
import nibabel as nib
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm

from scipy.ndimage import distance_transform_edt, binary_dilation

# from skimage.feature import structure_tensor, structure_tensor_eigenvalues
from skimage.feature import structure_tensor

from miracl.system.datamodels.miraclobj_utils import parser_true_or_false

warnings.filterwarnings("ignore")


def structure_tensor_eigenvalues_3d(A):
    """
    Calculate eigenvalues locally.

    I removed skimage.feature.structure_tensor_eigenvalues for current skimage
    version compatibility. scikit-image 0.14.2, which is the version installed
    in this version of MIRACL, does not provide structure_tensor_eigenvalues.

    Parameters
    ----------
    A : list of 6 ndarray
        Upper-triangular structure tensor elements [A00, A01, A02, A11, A12, A22],
        as returned by skimage.feature.structure_tensor.

    Returns
    -------
    ndarray, shape (3, Z, Y, X)
        Eigenvalues in DECREASING order. Index 0 is the largest.
    """
    m = np.empty(A[0].shape + (3, 3), dtype=A[0].dtype)
    m[..., 0, 0] = A[0]
    m[..., 0, 1] = m[..., 1, 0] = A[1]
    m[..., 0, 2] = m[..., 2, 0] = A[2]
    m[..., 1, 1] = A[3]
    m[..., 1, 2] = m[..., 2, 1] = A[4]
    m[..., 2, 2] = A[5]

    # eigvalsh returns ascending; [..., ::-1] makes it descending,
    # then moveaxis puts the eigenvalue index first -> (3, Z, Y, X).
    return np.moveaxis(np.linalg.eigvalsh(m)[..., ::-1], -1, 0)


# ==============================================================================
# Section 2: Atlas utilities
#   Reused/adapted from visualization/aa_max_tree_reconstruction.ipynb
# ==============================================================================


def region_masker(image, image_ann, graph, regions):
    """
    Exclude specified brain regions from the image by zeroing them out.

    Adapted from aa_max_tree_reconstruction.ipynb. Regions can be specified
    by name (str, case-insensitive substring match) or by integer atlas ID.

    Parameters
    ----------
    image     : ndarray  – 3D segmentation or signal volume
    image_ann : ndarray  – 3D atlas annotation volume (Allen CCF)
    graph     : DataFrame – Allen structure graph with columns 'id','name','acronym'
    regions   : list     – region names (str) or IDs (int) to exclude

    Returns
    -------
    masked_image : ndarray – image zeroed out in excluded regions and outside brain
    """
    region_ids = []

    for region in regions:
        if isinstance(region, str):
            region_lower = region.lower()
            matches = graph[
                (graph["name"].str.lower() == region_lower)
                | (graph["acronym"].str.lower() == region_lower)
            ]
            if matches.empty:
                # Fall back to substring search
                matches = graph[
                    (graph["name"].str.lower().str.contains(region_lower))
                    | (graph["acronym"].str.lower().str.contains(region_lower))
                ]
            if matches.empty:
                print(f"[region_masker] Warning: no region found for '{region}'")
            else:
                region_ids.extend(matches["id"].tolist())
        else:
            # Assume numeric atlas ID
            if region in graph["id"].values:
                region_ids.append(region)
            else:
                print(f"[region_masker] Warning: region ID {region} not in atlas")

    if not region_ids:
        print(
            "[region_masker] No valid regions to exclude, returning unmodified image."
        )
        brain_mask = image_ann > 0
        return image * brain_mask

    print(
        f"[region_masker] Excluding {len(region_ids)} region IDs: {region_ids[:10]}..."
    )
    exclusion_mask = np.isin(image_ann, region_ids)  # True where excluded
    inclusion_mask = ~exclusion_mask  # True where kept
    brain_mask = image_ann > 0  # True inside brain
    return image * inclusion_mask * brain_mask


def MIP_compute(img, axis=1):
    """
    Compute the Maximum Intensity Projection (MIP) and its depth map.

    Adapted from aa_max_tree_reconstruction.ipynb.

    Parameters
    ----------
    img  : ndarray – 3D volume
    axis : int     – axis along which to project (default 1 = A-P axis)

    Returns
    -------
    MIP       : ndarray (2D) – maximum value along the projection axis
    MIP_depth : ndarray (2D) – index (depth) at which the maximum occurred
    """
    return np.max(img, axis=axis), np.argmax(img, axis=axis)


def get_region_info(region_id, id_to_row):
    """
    Look up the name and acronym for a given atlas region ID.

    Adapted from aa_max_tree_reconstruction.ipynb.

    Parameters
    ----------
    region_id : int or float
    id_to_row : DataFrame   – indexed by 'id', columns 'name' and 'acronym'

    Returns
    -------
    (r_id, name, acronym)
    """
    try:
        r_id = int(region_id)
        row = id_to_row.loc[r_id]
        return r_id, row["name"], row["acronym"]
    except Exception:
        return region_id, "Unknown", "Unknown"


def get_injection_site_ids(injection_site_name, graph):
    """
    Return all atlas region IDs matching the injection site name or acronym.

    Parameters
    ----------
    injection_site_name : str   – e.g. "RORB" or "retrohippocampal region"
    graph               : DataFrame

    Returns
    -------
    ids   : list of int  – matched region IDs
    names : list of str  – corresponding region names
    """
    name_lower = injection_site_name.lower()
    matches = graph[
        (graph["name"].str.lower().str.contains(name_lower, na=False))
        | (graph["acronym"].str.lower().str.contains(name_lower, na=False))
    ]
    if matches.empty:
        raise ValueError(
            f"Injection site '{injection_site_name}' not found in atlas graph."
        )
    print(
        f"[injection site] Found {len(matches)} region(s) matching '{injection_site_name}':"
    )
    for _, row in matches.iterrows():
        print(f"  ID {row['id']:>6}  {row['acronym']:<12}  {row['name']}")
    return matches["id"].tolist(), matches["name"].tolist()


# ==============================================================================
# Section 3: Structure Tensor Fractional Anisotropy (Signal 1)
#
#   The structure tensor at each voxel captures local gradient covariance, giving
#   the principal directions and magnitudes of intensity variation.
#   Its eigenvalues λ1 ≥ λ2 ≥ λ3 describe local geometry:
#
#     λ1 >> λ2 ≈ λ3  →  elongated tube  →  PASSING fiber bundle
#     λ1 ≈ λ2 >> λ3  →  flat sheet      →  laminar / cortical fiber
#     λ1 ≈ λ2 ≈ λ3  →  isotropic blob  →  TERMINATING field
#
#   Fractional Anisotropy (FA):
#     FA = sqrt(3/2) * norm(λ - mean(λ)) / norm(λ)
#   FA ∈ [0, 1], 0 = isotropic, 1 = perfectly anisotropic.
# ==============================================================================


def compute_FA_volume(image, sigma=1.5, min_signal=0.1, compute_directions=False):
    """
    Compute a 3D Fractional Anisotropy map from the structure tensor of `image`.
    Optionally also computes the principal fiber direction field.

    A larger sigma smooths over more voxels before gradient estimation, which
    reduces noise but blurs fine spatial variation. At 25 µm resolution, sigma=1.5
    (≈37.5 µm effective window) is a reasonable starting point.

    Structure tensor eigenvalues (ascending: lam1 ≤ lam2 ≤ lam3):
      lam3 >> lam2 ≈ lam1  →  elongated tube / fiber bundle
      The eigenvector of lam1 (SMALLEST eigenvalue) points *along* the fiber,
      because gradient energy is minimal in the direction the intensity varies
      least — i.e., along the fiber axis. This is the analog of the DTI
      principal diffusion direction.

    Parameters
    ----------
    image               : ndarray (3D) – voxelized segmentation volume
    sigma               : float        – Gaussian smoothing sigma for structure tensor
    min_signal          : float        – voxels below this value are masked out (FA=NaN)
    compute_directions  : bool         – if True, also compute and return the 4D
                                         principal fiber direction field (Z×Y×X×3)

    Returns
    -------
    FA               : ndarray (3D, float32) – FA per voxel; NaN where signal absent
    fiber_directions : ndarray (4D, float32) or None
                       Shape (Z, Y, X, 3). Principal fiber direction (unit vector)
                       at each signal voxel; zero vector where no signal.
                       Only computed and returned when compute_directions=True.
    """
    print(
        f"[FA] Computing structure tensor (sigma={sigma}) on volume {image.shape} ..."
    )

    # skimage expects float; normalize to [0,1] first
    img_f = image.astype(np.float32)
    vmax = img_f.max()
    if vmax > 0:
        img_f = img_f / vmax

    # Compute 3D structure tensor.
    # Returns upper-triangular elements: [A00, A01, A02, A11, A12, A22]
    # where axis 0=Z, 1=Y, 2=X following image axes.
    A = structure_tensor(img_f, sigma=sigma, order="rc")

    # # Compute eigenvalues (ascending: lam[0] ≤ lam[1] ≤ lam[2])
    # eigenvalues = structure_tensor_eigenvalues(A)  # shape (3, Z, Y, X)
    # Now descending: lam[0] >= lam[1] >= lam[2]
    eigenvalues = structure_tensor_eigenvalues_3d(A)  # preserves shape (3, Z, Y, X)

    lam3 = eigenvalues[2].astype(np.float32)  # largest
    lam2 = eigenvalues[1].astype(np.float32)
    lam1 = eigenvalues[0].astype(np.float32)  # smallest

    # Fractional Anisotropy
    mean_lam = (lam1 + lam2 + lam3) / 3.0
    numerator = np.sqrt(
        (lam3 - mean_lam) ** 2 + (lam2 - mean_lam) ** 2 + (lam1 - mean_lam) ** 2
    )
    denominator = np.sqrt(lam3**2 + lam2**2 + lam1**2) + 1e-10
    FA = np.sqrt(1.5) * numerator / denominator

    # Mask out background voxels
    signal_mask = image > min_signal
    FA[~signal_mask] = np.nan

    print(f"[FA] Done. FA range: {np.nanmin(FA):.3f} – {np.nanmax(FA):.3f}")

    # ── Principal fiber direction (optional) ─────────────────────────────────
    fiber_directions = None
    if compute_directions:
        print(f"[FA] Computing fiber direction field at signal voxels ...")

        # Work only at signal voxels to avoid allocating a 77M × 3 × 3 matrix.
        # signal_mask already computed above; get flat indices.
        sidx = np.where(signal_mask)  # tuple of (Z-indices, Y-indices, X-indices)
        n = len(sidx[0])
        print(f"[FA] Decomposing tensors at {n:,} signal voxels ...")

        # Gather the 6 upper-triangular elements at signal voxels: shape (N, 6)
        # A = [A00, A01, A02, A11, A12, A22] where Aij = A[i*(i+1)//2 + j ... ]
        # Reconstructed symmetric 3×3:
        #   [[A[0], A[1], A[2]],
        #    [A[1], A[3], A[4]],
        #    [A[2], A[4], A[5]]]
        T = np.stack(
            [
                A[0][sidx].astype(np.float64),
                A[1][sidx].astype(np.float64),
                A[2][sidx].astype(np.float64),
                A[3][sidx].astype(np.float64),
                A[4][sidx].astype(np.float64),
                A[5][sidx].astype(np.float64),
            ],
            axis=1,
        )  # (N, 6)

        # Build (N, 3, 3) symmetric matrices
        mats = np.zeros((n, 3, 3), dtype=np.float64)
        mats[:, 0, 0] = T[:, 0]
        mats[:, 0, 1] = mats[:, 1, 0] = T[:, 1]
        mats[:, 0, 2] = mats[:, 2, 0] = T[:, 2]
        mats[:, 1, 1] = T[:, 3]
        mats[:, 1, 2] = mats[:, 2, 1] = T[:, 4]
        mats[:, 2, 2] = T[:, 5]

        # eigh returns eigenvalues in ASCENDING order; each column of evecs is
        # an eigenvector. Column 0 → smallest eigenvalue → along-fiber direction.
        _, evecs = np.linalg.eigh(mats)  # evecs: (N, 3, 3)
        fiber_dirs = evecs[:, :, 0].astype(np.float32)  # (N, 3)

        # Enforce consistent sign convention based on the DOMINANT axis component
        # (largest absolute value), not the fixed Z component (index 0).
        #
        # Using the Z component only works for fibers that run primarily in Z
        # (e.g. corticospinal tract). For corpus callosum fibers where Z ≈ 0,
        # the Z component is near-zero and numerically unstable — adjacent voxels
        # may flip randomly, producing an incoherent direction field that disrupts
        # interhemispheric tracking. Using the dominant component ensures locally
        # consistent sign regardless of fiber orientation.
        dominant_axis = np.argmax(np.abs(fiber_dirs), axis=1)  # (N,) ∈ {0,1,2}
        dominant_vals = fiber_dirs[np.arange(len(fiber_dirs)), dominant_axis]
        flip = dominant_vals < 0
        fiber_dirs[flip] *= -1

        # Scatter back into the full 4D volume (zero outside signal)
        fiber_directions = np.zeros((*image.shape, 3), dtype=np.float32)
        fiber_directions[sidx[0], sidx[1], sidx[2]] = fiber_dirs
        print(f"[FA] Fiber direction field computed. Shape: {fiber_directions.shape}")

    return FA.astype(np.float32), fiber_directions


def per_region_FA(FA_volume, image_ann, signal_mask, min_voxels=20):
    """
    Compute the mean FA score for each atlas region, averaged only over
    signal-positive voxels. Regions with fewer than min_voxels are skipped.

    Parameters
    ----------
    FA_volume   : ndarray (3D) – FA map (NaN where no signal)
    image_ann   : ndarray (3D) – atlas annotation volume
    signal_mask : ndarray (3D, bool) – True where signal is present
    min_voxels  : int           – minimum signal voxels to compute a valid score

    Returns
    -------
    dict  region_id → mean_FA (float)
    """
    print("[FA] Aggregating FA per atlas region ...")

    # Only consider voxels that have signal AND a valid FA value
    valid = signal_mask & (~np.isnan(FA_volume))
    region_ids = np.unique(image_ann[valid])
    region_ids = region_ids[region_ids > 0]  # skip background (id=0)

    result = {}
    for rid in region_ids:
        mask = valid & (image_ann == rid)
        n = mask.sum()
        if n < min_voxels:
            continue
        result[int(rid)] = float(np.nanmean(FA_volume[mask]))

    print(f"[FA] Scored {len(result)} regions.")
    return result


# ==============================================================================
# Section 4: Depth Variance (Signal 2)
#
#   Core intuition
#   ──────────────
#   A passing fiber bundle runs coherently through a region in a dominant
#   direction. When projected along the A-P axis, its signal concentrates at
#   a consistent depth → low spread across depth layers.
#
#   A terminal arborization fans out in all 3D directions inside the region.
#   Branches at different A-P depths contribute to different parts of the
#   projection → high spread across depth layers.
#
#   Metric: std(depth_coords of signal voxels) / region_depth_extent
#   → normalised by region size so small and large regions are comparable.
#   → low value = PASSING, high value = TERMINATING
#
#   Two-tier computation
#   ────────────────────
#   Primary (MIP-based):
#     For regions visible in the 2D MIP with ≥ min_pixels signal pixels,
#     "depth" = MIP_depth (the A-P index of the brightest voxel per column).
#     This is fast and captures the dominant signal layer.
#
#   Fallback (3D voxel-based):
#     ~30% of regions are "hidden" in the MIP: they have enough 3D signal
#     (≥ min_voxels) but project to fewer than min_pixels pixels, because a
#     brighter region occupies the same projection column in front of them.
#     Typical examples: small subcortical nuclei (cuneate, gracile, ambiguus,
#     solitary tract). For these, depth variance is computed directly from the
#     spread of all signal voxel coordinates along the projection axis.
#     This is actually the more principled measurement: it uses every signal
#     voxel, not just the brightest one per column.
#     Previously these regions received a constant median fill (0.426) which
#     added no information. The 3D fallback gives them a real score.
# ==============================================================================


def per_region_depth_variance(
    MIP_depth,
    MIP_signal_mask,
    image_ann_2d,
    ann_depth_extent,
    image_ann,
    signal_mask_3d,
    axis=1,
    min_pixels=10,
    min_voxels=20,
):
    """
    Compute normalised depth variance per atlas region.

    Primary method (MIP-based):
      For each region visible in the 2D MIP, compute std(MIP_depth) across its
      signal pixels, normalised by the region's depth extent.

    Fallback method (3D voxel-based):
      ~30% of regions have enough 3D signal to compute FA but project to fewer
      than min_pixels pixels in the MIP (hidden under a brighter region or
      simply too small in the projection plane). For these, depth variance is
      computed directly from the spread of signal voxel coordinates along the
      projection axis. This is the more principled measurement and avoids
      filling these regions with a meaningless constant median.

      Low spread  → signal concentrated in one depth layer → PASSING
      High spread → signal distributed across many layers  → TERMINATING

    Parameters
    ----------
    MIP_depth       : ndarray (2D)      – depth index of max intensity per pixel
    MIP_signal_mask : ndarray (2D,bool) – True where MIP > 0
    image_ann_2d    : ndarray (2D)      – atlas region at each MIP pixel
    ann_depth_extent: dict  rid → int   – region span along projection axis
    image_ann       : ndarray (3D)      – full atlas annotation volume (for fallback)
    signal_mask_3d  : ndarray (3D,bool) – True where 3D signal is present (for fallback)
    axis            : int               – projection axis (default 1 = A-P)
    min_pixels      : int               – minimum MIP pixels for primary method
    min_voxels      : int               – minimum 3D voxels for fallback method

    Returns
    -------
    dict  region_id → normalised_depth_variance (float)
         Source of each score recorded in returned metadata dict.
    """
    print("[DepthVar] Computing depth variance per atlas region ...")

    result = {}
    source = {}  # track whether each score came from MIP or 3D fallback

    # ── Primary: MIP-based depth variance ────────────────────────────────────
    mip_region_ids = np.unique(image_ann_2d[MIP_signal_mask])
    mip_region_ids = mip_region_ids[mip_region_ids > 0]

    for rid in mip_region_ids:
        pixel_mask = MIP_signal_mask & (image_ann_2d == rid)
        if pixel_mask.sum() < min_pixels:
            continue
        depths = MIP_depth[pixel_mask].astype(float)
        extent = ann_depth_extent.get(int(rid), 1)
        result[int(rid)] = float(np.std(depths)) / (extent + 1e-6)
        source[int(rid)] = "mip"

    mip_scored = len(result)

    # ── Fallback: 3D voxel coordinate variance for regions missed by MIP ─────
    # Get all region IDs that have 3D signal but weren't scored above
    all_3d_ids = np.unique(image_ann[signal_mask_3d])
    all_3d_ids = all_3d_ids[all_3d_ids > 0]
    fallback_ids = [r for r in all_3d_ids if int(r) not in result]

    for rid in fallback_ids:
        vox_mask = signal_mask_3d & (image_ann == rid)
        if vox_mask.sum() < min_voxels:
            continue
        # Extract voxel coordinates along the projection axis
        coords_along_axis = np.where(vox_mask)[axis].astype(float)
        extent = ann_depth_extent.get(int(rid), 1)
        result[int(rid)] = float(np.std(coords_along_axis)) / (extent + 1e-6)
        source[int(rid)] = "3d_fallback"

    fallback_scored = len(result) - mip_scored
    print(
        f"[DepthVar] Scored {len(result)} regions  "
        f"({mip_scored} via MIP, {fallback_scored} via 3D fallback)."
    )
    return result


def compute_annotation_depth_extent(image_ann, axis=1):
    """
    For each atlas region, compute how many layers it spans along `axis`.
    Used to normalise depth variance scores.

    Parameters
    ----------
    image_ann : ndarray (3D)
    axis      : int – projection axis

    Returns
    -------
    dict  region_id → int (number of layers occupied along axis)
    """
    unique_ids = np.unique(image_ann)
    unique_ids = unique_ids[unique_ids > 0]
    result = {}
    for rid in unique_ids:
        coords_along_axis = np.where(image_ann == rid)[axis]
        result[int(rid)] = int(coords_along_axis.max() - coords_along_axis.min() + 1)
    return result


# ==============================================================================
# Section 5: Distance from Injection Site (Signal 3)
#
#   Biological rationale for anterograde tracing
#   ─────────────────────────────────────────────
#   The injection site labels the SOMA. Axons grow outward from it. Therefore:
#
#     • Voxels immediately adjacent to the injection site contain the initial
#       axon segments (en route), or local collaterals/dendrites — NOT terminals.
#     • Voxels far from the injection site that still contain signal are likely
#       TERMINAL FIELDS: the axon travelled far and stopped there.
#
#   Implementation
#   ──────────────
#   1. Build a binary injection-site mask from the atlas annotation.
#   2. Run scipy.ndimage.distance_transform_edt on the *inverse* mask.
#      This gives, for every voxel outside the injection site, its Euclidean
#      distance (in voxels) to the nearest injection-site voxel.
#   3. For each atlas region, compute the mean distance of its signal-positive
#      voxels to the injection site. Scale by voxel size (µm) for interpretability.
#
#   Note: distance is a PRIOR, not a deterministic classifier. A region may be
#   far from the injection site but still just be a transit corridor (e.g. the
#   internal capsule). Signal 1 (FA) will correct for this: a far, anisotropic
#   region will still score low on termination.
# ==============================================================================


def compute_injection_distance_map(image_ann, injection_ids, voxel_size_um=25.0):
    """
    Compute a 3D Euclidean distance map (in µm) from the injection-site voxels.

    Uses scipy.ndimage.distance_transform_edt which operates on a binary
    background mask: distance is computed for every voxel NOT in the injection
    site to the nearest injection-site voxel.

    Parameters
    ----------
    image_ann      : ndarray (3D, int) – atlas annotation volume
    injection_ids  : list of int       – atlas region IDs of the injection site
    voxel_size_um  : float             – isotropic voxel size in µm (default 25)

    Returns
    -------
    dist_map : ndarray (3D, float32) – distance in µm from injection site;
               0 inside the injection site itself
    """
    print(
        f"[Distance] Computing 3D distance transform from injection site "
        f"(IDs: {injection_ids}) ..."
    )

    # Binary mask: True = injection site voxels, False = everything else
    inj_mask = np.isin(image_ann, injection_ids)

    # EDT expects a binary array where 0 = foreground (source).
    # We invert: 0 inside injection site, 1 outside.
    bg_mask = (~inj_mask).astype(np.uint8)

    # Compute Euclidean distance transform (in voxels)
    dist_voxels = distance_transform_edt(bg_mask).astype(np.float32)

    # Convert to µm
    dist_map = dist_voxels * voxel_size_um

    inj_voxels = inj_mask.sum()
    print(
        f"[Distance] Injection site: {inj_voxels:,} voxels  "
        f"| max distance: {dist_map.max():.0f} µm"
    )
    return dist_map


def per_region_injection_distance(
    dist_map, image_ann, signal_mask, injection_ids, min_voxels=20
):
    """
    Compute the mean distance from the injection site for each atlas region,
    averaged only over signal-positive voxels.

    The injection site region itself is excluded from the output (it is the
    source, not a target).

    Parameters
    ----------
    dist_map      : ndarray (3D) – output of compute_injection_distance_map()
    image_ann     : ndarray (3D) – atlas annotation volume
    signal_mask   : ndarray (3D, bool) – True where segmentation signal is present
    injection_ids : list of int  – injection site region IDs (excluded from output)
    min_voxels    : int          – minimum signal voxels to compute a valid score

    Returns
    -------
    dict  region_id → mean_distance_um (float)
    """
    print("[Distance] Aggregating injection distance per atlas region ...")

    # Only score voxels that have signal and are not in the injection site
    not_injection = ~np.isin(image_ann, injection_ids)
    valid = signal_mask & not_injection

    region_ids = np.unique(image_ann[valid])
    region_ids = region_ids[region_ids > 0]  # skip background

    result = {}
    for rid in region_ids:
        if int(rid) in injection_ids:
            continue  # skip injection site
        mask = valid & (image_ann == rid)
        n = mask.sum()
        if n < min_voxels:
            continue
        result[int(rid)] = float(np.mean(dist_map[mask]))

    print(
        f"[Distance] Scored {len(result)} regions  "
        f"| range: {min(result.values()):.0f} – {max(result.values()):.0f} µm"
    )
    return result


# ==============================================================================
# Section 6: Combine scores into a single termination score per region
#
#   Each signal is first min-max normalised to [0, 1] across all scored regions
#   so that the three weights are on a comparable scale.
#
#   Termination score (higher = more likely TERMINATING):
#
#     T = w_fa × (1 − FA_norm)    ← Signal 1: low FA  → isotropic → terminating
#       + w_dv × dv_norm           ← Signal 2: high depth spread   → terminating
#       + w_di × di_norm           ← Signal 3: far from injection   → terminating
#
#   T ∈ [0, 1].  T ≥ 0.5 → classified as TERMINATING, T < 0.5 → PASSING.
#
#   Signal roles and interactions
#   ──────────────────────────────
#   FA (w_fa = 0.4, highest weight):
#     The primary morphological signal. Directly measures whether the aggregate
#     signal in a region is shaped like a fiber bundle (anisotropic) or a
#     terminal cloud (isotropic). Works in full 3D, not projection-dependent.
#
#   Depth variance (w_dv = 0.3):
#     Measures how much the signal is spread across depth layers. Complements
#     FA by capturing 3D volumetric distribution rather than local orientation.
#     ~70% of regions use the MIP-based version; ~30% use the 3D voxel fallback.
#
#   Injection distance (w_di = 0.3, acts as a prior):
#     Biases distal regions toward terminating — the further an axon travels
#     from the soma, the more likely it is reaching a terminal. However, FA
#     can override this: a far-but-highly-anisotropic region (e.g. internal
#     capsule) will still score low on termination because its FA is high.
#     Conversely, a nearby region with low FA and high depth variance can
#     still be classified as terminating.
#
#   Missing values:
#     Any signal missing for a region is filled with the across-region median
#     before normalisation, giving it a neutral (middle-of-the-road) contribution
#     rather than unduly pushing it toward either class.
# ==============================================================================


def _minmax_norm(series):
    """Min-max normalise a pandas Series to [0, 1]. Returns 0.5 if constant."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return pd.Series(0.5, index=series.index)
    return (series - mn) / (mx - mn)


def combine_scores(
    fa_scores,
    dv_scores,
    di_scores,
    w_fa=0.4,
    w_dv=0.3,
    w_di=0.3,
    id_to_row=None,
    injection_ids=None,
):
    """
    Merge per-region signal scores into a ranked DataFrame.

    Parameters
    ----------
    fa_scores     : dict  rid → mean FA (high = passing)
    dv_scores     : dict  rid → normalised depth variance (high = terminating)
    di_scores     : dict  rid → mean distance from injection site in µm
                               (high = more distal = more likely terminating)
    w_fa / w_dv / w_di : float – blending weights (should sum to 1)
    id_to_row     : DataFrame (indexed by id, cols 'name','acronym') or None
    injection_ids : list of int – injection site region IDs (flagged in output)

    Returns
    -------
    df : DataFrame sorted by termination_score descending
    """
    all_ids = set(fa_scores) | set(dv_scores) | set(di_scores)
    rows = []
    for rid in all_ids:
        rows.append(
            {
                "region_id": rid,
                "FA": fa_scores.get(rid, np.nan),
                "depth_var": dv_scores.get(rid, np.nan),
                "mean_dist_inj_um": di_scores.get(rid, np.nan),
            }
        )

    df = pd.DataFrame(rows).set_index("region_id")

    # Annotate with region name/acronym
    if id_to_row is not None:
        df["name"] = df.index.map(
            lambda r: id_to_row.loc[r, "name"] if r in id_to_row.index else "Unknown"
        )
        df["acronym"] = df.index.map(
            lambda r: id_to_row.loc[r, "acronym"] if r in id_to_row.index else "UNK"
        )

    # Flag injection site regions
    if injection_ids:
        df["is_injection_site"] = df.index.isin(injection_ids)
    else:
        df["is_injection_site"] = False

    # Normalise each signal; fill missing values with neutral 0.5
    df["FA_norm"] = _minmax_norm(df["FA"].fillna(df["FA"].median()))
    df["dv_norm"] = _minmax_norm(df["depth_var"].fillna(df["depth_var"].median()))
    df["di_norm"] = _minmax_norm(
        df["mean_dist_inj_um"].fillna(df["mean_dist_inj_um"].median())
    )

    # Composite termination score (0 = passing, 1 = terminating)
    #   - FA contributes INVERSELY  (high FA → passing → lowers score)
    #   - depth variance contributes DIRECTLY (high var → terminating → raises score)
    #   - distance contributes DIRECTLY (far from inj → terminating → raises score)
    df["termination_score"] = (
        w_fa * (1.0 - df["FA_norm"]) + w_dv * df["dv_norm"] + w_di * df["di_norm"]
    )

    # Binary classification label
    df["classification"] = np.where(
        df["termination_score"] >= 0.5, "terminating", "passing"
    )

    df = df.sort_values("termination_score", ascending=False)
    return df


# ==============================================================================
# Section 7: Visualisation
#
#   Two figures:
#   Fig 1 – MIP overlay: the 2D MIP image with each region coloured by its
#            termination_score (cool-warm colormap: blue=passing, red=terminating).
#
#   Fig 2 – Bar chart: top N terminating and top N passing regions ranked by score.
# ==============================================================================


def visualize_mip_overlay(
    MIP_raw,
    image_ann_2d,
    df_scores,
    injection_ids,
    injection_acronym,
    output_path,
    top_n_labels=10,
):
    """
    Overlay the termination score on the MIP image.

    Left panel  : raw fluorescence MIP in greyscale (anatomical context).
    Right panel : same background with each atlas region coloured by its
                  termination_score (blue = passing, red = terminating).
                  Injection site is outlined in green.
                  Top-scoring terminating and passing regions are labelled
                  by their atlas acronym at their centroid.

    Parameters
    ----------
    MIP_raw           : ndarray (2D) – raw fluorescence MIP (greyscale background)
    image_ann_2d      : ndarray (2D) – atlas region ID at each MIP pixel
    df_scores         : DataFrame    – output of combine_scores()
    injection_ids     : list of int  – IDs of the injection site regions
    injection_acronym : str          – short label for the plot title
    output_path       : str          – where to save the PNG
    top_n_labels      : int          – how many top/bottom regions to annotate
    """
    # Build a 2D score map: each pixel gets its region's termination_score
    score_map = np.full(image_ann_2d.shape, np.nan, dtype=np.float32)
    for rid, row in df_scores.iterrows():
        if not np.isnan(row["termination_score"]):
            score_map[image_ann_2d == rid] = row["termination_score"]

    # Background: normalised raw MIP in greyscale
    raw_norm = MIP_raw.astype(np.float32)
    if raw_norm.max() > 0:
        raw_norm = (raw_norm - np.percentile(raw_norm, 1)) / (
            np.percentile(raw_norm, 99) - np.percentile(raw_norm, 1) + 1e-10
        )
        raw_norm = np.clip(raw_norm, 0, 1)

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))

    # --- Left panel: raw MIP ---
    axes[0].imshow(raw_norm, cmap="gray", aspect="equal", interpolation="none")
    axes[0].set_title("Raw Signal MIP", fontweight="bold")
    axes[0].axis("off")

    # --- Right panel: termination score overlay ---
    axes[1].imshow(
        raw_norm, cmap="gray", aspect="equal", interpolation="none", alpha=0.5
    )

    cmap_score = cm.RdBu_r  # red=terminating (high score), blue=passing (low score)
    score_rgba = cmap_score(score_map)
    score_rgba[..., 3] = np.where(
        np.isnan(score_map), 0.0, 0.6 + 0.4 * score_map.clip(0, 1)
    )

    axes[1].imshow(score_rgba, aspect="equal", interpolation="none")

    # Highlight injection site with a contour
    inj_mask = np.isin(image_ann_2d, injection_ids).astype(float)
    axes[1].contour(inj_mask, levels=[0.5], colors="lime", linewidths=1.5)

    # Annotate centroids of top/bottom regions (skip injection site)
    non_inj = df_scores[~df_scores["is_injection_site"]]
    top_term = non_inj.head(top_n_labels)
    top_pass = non_inj.tail(top_n_labels)
    for label_df, colour in [(top_term, "darkred"), (top_pass, "darkblue")]:
        for rid, row in label_df.iterrows():
            ys, xs = np.where(image_ann_2d == rid)
            if len(ys) == 0:
                continue
            cy, cx = int(ys.mean()), int(xs.mean())
            acronym = row.get("acronym", str(rid))
            axes[1].text(
                cx,
                cy,
                acronym,
                fontsize=5,
                color=colour,
                ha="center",
                va="center",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", alpha=0.4, ec="none"),
            )

    # Colorbar
    sm = cm.ScalarMappable(cmap=cmap_score, norm=mcolors.Normalize(vmin=0, vmax=1))
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=axes[1], fraction=0.03, pad=0.02)
    cbar.set_label("Termination Score  (0=passing, 1=terminating)", fontsize=9)

    axes[1].set_title(
        f"Axonal Fiber Classification (injection: {injection_acronym})",
        fontweight="bold",
    )
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] MIP overlay saved → {output_path}")


def visualize_barplot(df_scores, output_path, top_n=20, injection_acronym=""):
    """
    Horizontal bar chart of the top terminating and top passing regions.

    Parameters
    ----------
    df_scores        : DataFrame – output of combine_scores()
    output_path      : str
    top_n            : int       – number of regions shown per category
    injection_acronym: str       – shown in plot title
    """
    non_inj = df_scores[~df_scores["is_injection_site"]].copy()

    top_term = non_inj.head(top_n)
    top_pass = non_inj.tail(top_n).iloc[::-1]  # reverse so lowest score is at bottom

    fig, axes = plt.subplots(1, 2, figsize=(16, max(6, top_n * 0.4)))

    for ax, subset, title, colour in [
        (axes[0], top_term, f"Top {top_n} Terminating Regions", "#d73027"),
        (axes[1], top_pass, f"Top {top_n} Passing Regions", "#4575b4"),
    ]:
        labels = (
            subset["acronym"].fillna(
                pd.Series(subset.index.astype(str).values, index=subset.index)
            )
            if "acronym" in subset.columns
            else subset.index.astype(str)
        )
        scores = subset["termination_score"]
        ax.barh(
            range(len(scores)),
            scores,
            color=colour,
            alpha=0.75,
            edgecolor="k",
            linewidth=0.4,
        )

        # Annotate each bar with FA value as a secondary indicator
        for i, (_, row) in enumerate(subset.iterrows()):
            fa_val = row.get("FA", np.nan)
            if not np.isnan(fa_val):
                ax.text(
                    scores.iloc[i] + 0.01,
                    i,
                    f"FA={fa_val:.2f}",
                    va="center",
                    fontsize=6,
                    color="grey",
                )

        ax.set_yticks(range(len(scores)))
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlim(0, 1.15)
        ax.axvline(0.5, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_xlabel("Termination Score", fontsize=9)
        ax.set_title(title, fontweight="bold", fontsize=10)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle(
        f"Passing vs. Terminating — injection site: {injection_acronym}",
        fontweight="bold",
        fontsize=12,
        y=1.01,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Viz] Bar chart saved → {output_path}")


def save_score_nifti(df_scores, image_ann, ref_nii, output_path):
    """
    Save a 3D NIfTI volume where each atlas region is filled with its
    termination_score. Useful for viewing in Fiji/ITK-SNAP alongside the atlas.

    Parameters
    ----------
    df_scores   : DataFrame
    image_ann   : ndarray (3D)
    ref_nii     : nibabel image  – used for affine/header
    output_path : str
    """
    score_vol = np.zeros(image_ann.shape, dtype=np.float32)
    for rid, row in df_scores.iterrows():
        val = row["termination_score"]
        if not np.isnan(val):
            score_vol[image_ann == rid] = float(val)

    out_nii = nib.Nifti1Image(score_vol, affine=ref_nii.affine, header=ref_nii.header)
    out_nii.header.set_data_dtype(np.float32)
    nib.save(out_nii, output_path)
    print(f"[NIfTI] Termination score volume saved → {output_path}")


# ==============================================================================
# Section 8: Save tractography inputs (Step 1 of tractography pipeline)
#
#   Saves FA map, principal fiber direction field, injection mask, and signal
#   mask as NIfTI volumes in the exact same coordinate space as the input
#   segmentation (--seg). All outputs share the same affine matrix from
#   seg_nii, so they can be directly overlaid on the atlas annotation or the
#   warped signal in any viewer (ITK-SNAP, Fiji, ANTS).
#
#   These files serve as inputs for aa_tractography.py:
#     FA.nii.gz              → stopping criterion (FA < threshold → stop)
#     fiber_directions.nii.gz → direction field for deterministic tracking
#     injection_mask.nii.gz  → seed mask (tracking starts here)
#     signal_mask.nii.gz     → white-matter mask (tracking stays inside signal)
# ==============================================================================


def save_tractography_inputs(
    FA_volume,
    fiber_directions,
    image_ann,
    signal_mask,
    injection_ids,
    seg_nii,
    out_dir,
    inj_dilation=2,
    sig_dilation=0,
    hemi_clip=False,
):
    """
    Save NIfTI volumes needed as inputs for tractography (aa_tractography.py).

    All saved volumes use the same affine as seg_nii (the input segmentation),
    which is already in Allen CCF 25 µm space. They can be overlaid directly on
    the atlas annotation or the warped signal without any registration step.

    Parameters
    ----------
    FA_volume        : ndarray (3D, float32) – FA map from compute_FA_volume()
    fiber_directions : ndarray (4D, float32) – principal fiber directions (Z×Y×X×3)
    image_ann        : ndarray (3D, int)     – atlas annotation volume
    signal_mask      : ndarray (3D, bool)    – True where segmentation signal present
    injection_ids    : list of int           – atlas region IDs of the injection site
    seg_nii          : nibabel image         – reference for affine/header
    out_dir          : str                   – directory to write files into

    Files saved
    -----------
    FA.nii.gz              : 3D float32 FA map (NaN outside signal)
    fiber_directions.nii.gz: 4D float32 (Z,Y,X,3) principal fiber direction field
                             Zero vector outside signal. Eigenvector of the smallest
                             structure tensor eigenvalue = along-fiber direction.
    injection_mask.nii.gz  : 3D uint8 binary mask, 1 inside injection site regions
    signal_mask.nii.gz     : 3D uint8 binary mask, 1 where segmentation signal present
    """
    affine = seg_nii.affine
    header = seg_nii.header

    # ── FA map (3D) ───────────────────────────────────────────────────────────
    fa_path = os.path.join(out_dir, "FA.nii.gz")
    fa_nii = nib.Nifti1Image(FA_volume, affine=affine, header=header)
    fa_nii.header.set_data_dtype(np.float32)
    nib.save(fa_nii, fa_path)
    print(f"[Tract] FA map saved            → {fa_path}")

    # ── Principal fiber direction field (4D: Z×Y×X×3) ────────────────────────
    # Saved AFTER the signal mask dilation block below, because dilation may
    # propagate directions into new voxels (EDT nearest-neighbour fill).
    # Saving here would write the pre-propagation array to disk.
    dirs_path = os.path.join(out_dir, "fiber_directions.nii.gz")
    hdr4 = header.copy()
    hdr4.set_data_shape(fiber_directions.shape)
    if len(hdr4["pixdim"]) > 4:
        hdr4["pixdim"][4] = 1.0

    # ── Injection site mask (3D) ──────────────────────────────────────────────
    # Intersect atlas region with segmentation signal so seeds are placed only
    # where fluorescence is actually present (not the full anatomical atlas region).
    atlas_region = np.isin(image_ann, injection_ids)
    inj_signal = atlas_region & signal_mask.astype(bool)  # atlas ∩ signal

    if inj_signal.sum() == 0:
        # Fallback: injection site has no segmentation signal (e.g. cleared soma
        # region); use pure atlas to avoid an empty seed mask.
        print(
            "[Tract] Warning: atlas∩signal intersection is empty — "
            "falling back to pure atlas mask for injection site."
        )
        inj_mask_bool = atlas_region
    else:
        inj_mask_bool = inj_signal

    # Optional morphological dilation to capture signal just outside atlas boundary.
    # After dilation, clip back to original signal mask so seeds are always on
    # real detected axons — prevents seeding from empty white matter in dilated zone.
    if inj_dilation > 0:
        inj_mask_bool = binary_dilation(inj_mask_bool, iterations=inj_dilation)
        inj_mask_bool = inj_mask_bool & signal_mask.astype(
            bool
        )  # only real signal voxels
        inj_mask_bool = inj_mask_bool & (image_ann > 0)  # clip to brain

    # ── Optional hemisphere clip ──────────────────────────────────────────────
    # Restricts injection mask to the ipsilateral (right) hemisphere so that
    # contralateral axon terminals pulled in by dilation+clip-to-signal are
    # excluded as seeds. Streamlines can still travel to the left hemisphere
    # naturally via CC — only seeding is restricted.
    # Allen CCF hemi-split 25µm: X-axis size = 456, midline = X < 228 (right).
    # Comment out the if-block below to disable.
    if hemi_clip:
        midline_x = inj_mask_bool.shape[2] // 2  # 228 for 456-wide volume
        hemi_mask = np.zeros_like(inj_mask_bool)
        hemi_mask[:, :, :midline_x] = True  # keep right hemisphere (X < 228)
        before = inj_mask_bool.sum()
        inj_mask_bool = inj_mask_bool & hemi_mask
        removed = before - inj_mask_bool.sum()
        print(
            f"[Tract] Hemisphere clip: removed {removed:,} contralateral voxels "
            f"(X >= {midline_x})"
        )

    inj_mask_vol = inj_mask_bool.astype(np.uint8)
    inj_path = os.path.join(out_dir, "injection_mask.nii.gz")
    inj_nii = nib.Nifti1Image(inj_mask_vol, affine=affine, header=header)
    inj_nii.header.set_data_dtype(np.uint8)
    nib.save(inj_nii, inj_path)
    print(
        f"[Tract] Injection mask saved    → {inj_path}  "
        f"({inj_mask_vol.sum():,} voxels, dilation={inj_dilation}, "
        f"hemi_clip={hemi_clip})"
    )

    # ── Signal mask (3D) ──────────────────────────────────────────────────────
    # Optional dilation fills gaps in the binary segmentation between cortex and
    # white-matter tracts (e.g. corpus callosum), allowing tracking to bridge
    # unsegmented white matter that separates the injection site from distant targets.
    sig_bool = signal_mask.astype(bool)
    if sig_dilation > 0:
        print(
            f"[Tract] Dilating signal mask by {sig_dilation} voxels "
            f"({sig_dilation * 25:.0f} µm) to fill white-matter gaps ..."
        )

        # --- Old approach (commented out) ------------------------------------
        # Simply dilated the mask without updating fiber_directions. This
        # created a "dead zone": dilated voxels had mask=True but dirs=[0,0,0],
        # so the tracker entered them, found norm<0.5, and immediately stopped.
        # sig_bool = binary_dilation(sig_bool, iterations=sig_dilation)
        # sig_bool = sig_bool & (image_ann > 0)
        # ---------------------------------------------------------------------

        # New approach: dilate mask AND propagate directions into dilated zone.
        # For each newly added voxel, copy the direction from the nearest
        # original signal voxel using distance_transform_edt indices (one-shot,
        # fully vectorised — equivalent to iterative flood-fill but faster).
        sig_bool_dilated = binary_dilation(sig_bool, iterations=sig_dilation)
        sig_bool_dilated = sig_bool_dilated & (image_ann > 0)

        new_voxels = sig_bool_dilated & ~sig_bool  # dilated zone only
        if new_voxels.any():
            print(
                f"[Tract] Propagating directions into {new_voxels.sum():,} "
                f"dilated voxels via nearest-neighbour EDT ..."
            )
            # distance_transform_edt on ~sig_bool returns, for every voxel
            # outside the original signal, the (z,y,x) index of the nearest
            # signal voxel.
            _, nn_idx = distance_transform_edt(~sig_bool, return_indices=True)
            # nn_idx shape: (3, Z, Y, X)
            nz, ny, nx = np.where(new_voxels)
            src_z = nn_idx[0][nz, ny, nx]
            src_y = nn_idx[1][nz, ny, nx]
            src_x = nn_idx[2][nz, ny, nx]
            fiber_directions[nz, ny, nx] = fiber_directions[src_z, src_y, src_x]

        sig_bool = sig_bool_dilated

    sig_path = os.path.join(out_dir, "signal_mask.nii.gz")
    sig_nii = nib.Nifti1Image(sig_bool.astype(np.uint8), affine=affine, header=header)
    sig_nii.header.set_data_dtype(np.uint8)
    nib.save(sig_nii, sig_path)
    print(
        f"[Tract] Signal mask saved       → {sig_path}  "
        f"({sig_bool.sum():,} voxels, dilation={sig_dilation})"
    )

    # Save fiber directions here — after dilation so EDT-propagated directions
    # for the dilated zone are included in the file written to disk.
    dirs_nii = nib.Nifti1Image(fiber_directions, affine=affine, header=hdr4)
    dirs_nii.header.set_data_dtype(np.float32)
    nib.save(dirs_nii, dirs_path)
    print(f"[Tract] Fiber directions saved  → {dirs_path}")


# ==============================================================================
# Section 9: Argument parsing and main pipeline
# ==============================================================================


def parse_args():
    p = argparse.ArgumentParser(
        description="Classify atlas regions as passing vs. terminating axonal fields.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Required
    p.add_argument(
        "--seg", required=True, help="Voxelized segmentation NIfTI (Allen CCF space)"
    )
    p.add_argument(
        "--ann",
        required=True,
        help="Atlas annotation NIfTI (e.g. annotation_hemi_split_25um.nii.gz)",
    )
    p.add_argument("--graph", required=True, help="Allen structure graph CSV")
    p.add_argument(
        "--inj", required=True, help="Injection site name or acronym (e.g. RORB)"
    )
    p.add_argument("--out", required=True, help="Output directory")

    # Optional data
    p.add_argument(
        "--raw", help="Raw fluorescence NIfTI (optional, used for background in viz)"
    )
    p.add_argument(
        "--exclude",
        default="",
        help="Comma-separated region names/IDs to exclude (e.g. 'olfactory bulb')",
    )

    # Algorithm parameters
    p.add_argument(
        "--axis", type=int, default=1, help="MIP projection axis (0=Z, 1=Y, 2=X)"
    )
    p.add_argument(
        "--sigma", type=float, default=1.5, help="Gaussian sigma for structure tensor"
    )
    p.add_argument(
        "--min_sig",
        type=float,
        default=0.1,
        help="Minimum signal threshold for voxel inclusion",
    )
    p.add_argument(
        "--min_vox",
        type=int,
        default=20,
        help="Minimum signal voxels required to score a 3D region",
    )
    p.add_argument(
        "--min_pix",
        type=int,
        default=10,
        help="Minimum signal pixels required to score a 2D (MIP) region",
    )

    # Score blending weights
    p.add_argument("--w_fa", type=float, default=0.4, help="Weight for FA signal")
    p.add_argument(
        "--w_dv", type=float, default=0.3, help="Weight for depth-variance signal"
    )
    p.add_argument(
        "--w_di",
        type=float,
        default=0.3,
        help="Weight for injection-site distance signal",
    )

    # Outputs
    p.add_argument(
        "--save_nii",
        required=False,
        default=False,
        type=parser_true_or_false,
        help="Also save termination score as a NIfTI volume",
    )
    p.add_argument(
        "--save_intermediates",
        required=False,
        default=False,
        type=parser_true_or_false,
        help=(
            "Save tractography input NIfTI files: FA.nii.gz, "
            "fiber_directions.nii.gz (4D Z×Y×X×3), "
            "injection_mask.nii.gz, signal_mask.nii.gz. "
            "All in the same Allen CCF space as --seg."
        ),
    )
    p.add_argument(
        "--inj_dilation",
        type=int,
        default=2,
        help=(
            "Morphological dilation radius (voxels) applied to the "
            "injection mask after atlas∩signal intersection. "
            "0 = no dilation (pure intersection). "
            "Default 2 voxels ≈ 50 µm at 25 µm resolution."
        ),
    )
    p.add_argument(
        "--sig_dilation",
        type=int,
        default=0,
        help=(
            "Morphological dilation radius (voxels) applied to the "
            "signal mask before saving. Fills gaps in the binary "
            "segmentation between cortex and white-matter tracts "
            "(e.g. corpus callosum), enabling tractography to bridge "
            "unsegmented white matter. 0 = no dilation (default). "
            "Recommended 10 voxels ≈ 250 µm at 25 µm resolution."
        ),
    )
    p.add_argument(
        "--hemi_clip",
        required=False,
        default=False,
        type=parser_true_or_false,
        help=(
            "Restrict injection mask to the ipsilateral (right) hemisphere "
            "(X < 228 in Allen CCF hemi-split 25µm). Prevents contralateral "
            "axon terminals from being included as seeds after dilation. "
            "Streamlines can still travel to the left hemisphere via CC."
        ),
    )
    p.add_argument(
        "--top_n",
        type=int,
        default=20,
        help="Number of top/bottom regions shown in bar chart",
    )

    return p.parse_args()


def main():
    args = parse_args()
    os.makedirs(args.out, exist_ok=True)

    # ------------------------------------------------------------------
    # 8.0  Resume check: if CSV already exists, skip all computation and
    #      go straight to visualisation. This lets you re-run the script
    #      after a crash without repeating the expensive FA computation.
    # ------------------------------------------------------------------
    params_path = os.path.join(args.out, "step1_params.json")
    csv_path = os.path.join(args.out, "region_scores.csv")

    # Resume check: only skip if BOTH the CSV and the params file exist AND
    # the key parameters match.  A mismatch (e.g. different sig_dilation) means
    # we must recompute even if the CSV exists — silently reusing a stale CSV
    # with different parameters would give wrong tractography results.
    _resume = False
    if os.path.exists(csv_path) and os.path.exists(params_path):
        import json as _json

        _saved = _json.load(open(params_path))
        _match = (
            _saved.get("sigma") == args.sigma
            and _saved.get("inj_dilation") == args.inj_dilation
            and _saved.get("sig_dilation") == args.sig_dilation
            and _saved.get("min_sig") == args.min_sig
            and _saved.get("hemi_clip") == args.hemi_clip
            and _saved.get("inj") == args.inj
        )
        if _match:
            _resume = True
        else:
            print(f"\n[Resume] CSV exists but parameters changed — recomputing.")

    if _resume:
        print(f"\n[Resume] Found existing CSV with matching parameters: {csv_path}")
        print(
            "[Resume] Skipping computation — loading scores and regenerating visualisations."
        )

        df_scores = pd.read_csv(csv_path, index_col="region_id")

        # Still need atlas annotation + raw image for visualisation
        ann_nii = nib.load(args.ann)
        image_ann = ann_nii.get_fdata().astype(np.uint32)
        seg_nii = nib.load(args.seg)
        image = np.abs(seg_nii.get_fdata().astype(np.float32))
        image[image < args.min_sig] = 0

        graph = pd.read_csv(args.graph)

        # Apply the same exclusion mask as the normal path so that
        # signal_mask_3d and visualisations are consistent with the saved CSV.
        exclude_list = [r.strip() for r in args.exclude.split(",") if r.strip()]
        if exclude_list:
            image = region_masker(image, image_ann, graph, exclude_list)

        if args.raw:
            image_raw = nib.load(args.raw).get_fdata().astype(np.float32)
        else:
            image_raw = image.copy()

        injection_ids, _ = get_injection_site_ids(args.inj, graph)
        inj_acronym = (
            graph.loc[graph["id"] == injection_ids[0], "acronym"].values[0]
            if injection_ids
            else args.inj
        )

        MIP, MIP_depth = MIP_compute(image, axis=args.axis)
        MIP_raw, _ = MIP_compute(image_raw, axis=args.axis)
        idx_a, idx_b = np.indices(MIP_depth.shape)
        if args.axis == 0:
            image_ann_2d = image_ann[MIP_depth.astype(int), idx_a, idx_b]
        elif args.axis == 1:
            image_ann_2d = image_ann[idx_a, MIP_depth.astype(int), idx_b]
        else:
            image_ann_2d = image_ann[idx_a, idx_b, MIP_depth.astype(int)]

        # Jump directly to visualisation
        print("\n" + "=" * 60)
        print("SAVING VISUALISATIONS")
        print("=" * 60)
        visualize_mip_overlay(
            MIP_raw,
            image_ann_2d,
            df_scores,
            injection_ids,
            inj_acronym,
            output_path=os.path.join(args.out, "mip_termination_overlay.png"),
            top_n_labels=args.top_n // 2,
        )
        visualize_barplot(
            df_scores,
            output_path=os.path.join(args.out, "top_regions_barplot.png"),
            top_n=args.top_n,
            injection_acronym=inj_acronym,
        )
        if args.save_nii:
            save_score_nifti(
                df_scores,
                image_ann,
                seg_nii,
                output_path=os.path.join(args.out, "termination_score_vol.nii.gz"),
            )
        if args.save_intermediates:
            print("\n" + "=" * 60)
            print("SAVING TRACTOGRAPHY INPUTS (resume mode)")
            print("=" * 60)
            signal_mask_3d = image > args.min_sig
            # Recompute FA and directions — these were not saved in the CSV
            FA_volume, fiber_directions = compute_FA_volume(
                image,
                sigma=args.sigma,
                min_signal=args.min_sig,
                compute_directions=True,
            )
            save_tractography_inputs(
                FA_volume,
                fiber_directions,
                image_ann,
                signal_mask_3d,
                injection_ids,
                seg_nii,
                out_dir=args.out,
                inj_dilation=args.inj_dilation,
                sig_dilation=args.sig_dilation,
                hemi_clip=args.hemi_clip,
            )
        print("\n" + "=" * 60)
        print("DONE")
        print("=" * 60)
        return

    # ------------------------------------------------------------------
    # 8.1  Load data
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    seg_nii = nib.load(args.seg)
    image = seg_nii.get_fdata().astype(np.float32)
    image = np.abs(image)
    image[image < args.min_sig] = 0
    print(
        f"  Segmentation : {image.shape}  min={image.min():.3f}  max={image.max():.3f}"
    )

    ann_nii = nib.load(args.ann)
    image_ann = ann_nii.get_fdata().astype(np.uint32)
    print(f"  Annotation   : {image_ann.shape}")

    graph = pd.read_csv(args.graph)
    print(f"  Atlas graph  : {len(graph)} regions")

    # Raw image (optional; use segmentation as fallback for MIP background)
    if args.raw:
        raw_nii = nib.load(args.raw)
        image_raw = raw_nii.get_fdata().astype(np.float32)
        print(f"  Raw channel  : {image_raw.shape}")
    else:
        image_raw = image.copy()
        print("  Raw channel  : not provided, using segmentation as background")

    id_to_row = graph.set_index("id")[["name", "acronym"]]

    # ------------------------------------------------------------------
    # 8.2  Exclude user-specified regions and restrict to brain
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("PREPROCESSING")
    print("=" * 60)

    exclude_list = [r.strip() for r in args.exclude.split(",") if r.strip()]
    if exclude_list:
        image = region_masker(image, image_ann, graph, exclude_list)

    signal_mask_3d = image > args.min_sig
    print(f"  Signal voxels: {signal_mask_3d.sum():,}")

    # Identify injection site regions
    injection_ids, _ = get_injection_site_ids(args.inj, graph)
    # Get a short display name for the injection site
    inj_acronym = (
        graph.loc[graph["id"] == injection_ids[0], "acronym"].values[0]
        if injection_ids
        else args.inj
    )

    # ------------------------------------------------------------------
    # 8.3  Compute MIP and 2D atlas map
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("COMPUTING MIP AND 2D ATLAS MAP")
    print("=" * 60)

    MIP, MIP_depth = MIP_compute(image, axis=args.axis)
    MIP_raw, _ = MIP_compute(image_raw, axis=args.axis)
    MIP_signal_mask = MIP > 0

    # Project annotation to 2D using MIP depth
    # Each pixel in the MIP is assigned the atlas region at its maximum-intensity depth
    idx_a, idx_b = np.indices(MIP_depth.shape)
    if args.axis == 0:
        image_ann_2d = image_ann[MIP_depth.astype(int), idx_a, idx_b]
    elif args.axis == 1:
        image_ann_2d = image_ann[idx_a, MIP_depth.astype(int), idx_b]
    else:  # axis == 2
        image_ann_2d = image_ann[idx_a, idx_b, MIP_depth.astype(int)]

    print(f"  MIP shape    : {MIP.shape}")
    print(f"  Signal pixels: {MIP_signal_mask.sum():,}")

    # ------------------------------------------------------------------
    # 8.4  Signal 1: Structure Tensor FA
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SIGNAL 1: STRUCTURE TENSOR FA (3D)")
    print("=" * 60)

    FA_volume, fiber_directions = compute_FA_volume(
        image,
        sigma=args.sigma,
        min_signal=args.min_sig,
        compute_directions=args.save_intermediates,
    )
    fa_scores = per_region_FA(
        FA_volume, image_ann, signal_mask_3d, min_voxels=args.min_vox
    )

    # ------------------------------------------------------------------
    # 8.5  Signal 2: MIP Depth Variance
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SIGNAL 2: MIP DEPTH VARIANCE")
    print("=" * 60)

    ann_depth_extent = compute_annotation_depth_extent(image_ann, axis=args.axis)
    dv_scores = per_region_depth_variance(
        MIP_depth,
        MIP_signal_mask,
        image_ann_2d,
        ann_depth_extent,
        image_ann=image_ann,
        signal_mask_3d=signal_mask_3d,
        axis=args.axis,
        min_pixels=args.min_pix,
        min_voxels=args.min_vox,
    )

    # ------------------------------------------------------------------
    # 8.6  Signal 3: Distance from Injection Site
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SIGNAL 3: DISTANCE FROM INJECTION SITE (3D)")
    print("=" * 60)

    # Infer voxel size from the NIfTI header (assumes isotropic).
    # NIfTI zooms are stored in mm → multiply by 1000 to convert to µm.
    zoom_mm = float(np.abs(seg_nii.header.get_zooms()[0]))
    if zoom_mm == 0:
        voxel_size_um = 25.0
        print(
            f"  [Warning] Could not read voxel size from header, assuming {voxel_size_um} µm"
        )
    else:
        voxel_size_um = zoom_mm * 1000.0
        print(f"  Voxel size: {zoom_mm} mm  →  {voxel_size_um:.1f} µm")

    dist_map = compute_injection_distance_map(
        image_ann, injection_ids, voxel_size_um=voxel_size_um
    )
    di_scores = per_region_injection_distance(
        dist_map, image_ann, signal_mask_3d, injection_ids, min_voxels=args.min_vox
    )

    # ------------------------------------------------------------------
    # 8.7  Combine scores
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("COMBINING SCORES")
    print("=" * 60)

    w_sum = args.w_fa + args.w_dv + args.w_di
    if abs(w_sum - 1.0) > 1e-3:
        print(f"  Warning: weights sum to {w_sum:.3f} (not 1.0), normalising.")
        args.w_fa /= w_sum
        args.w_dv /= w_sum
        args.w_di /= w_sum

    df_scores = combine_scores(
        fa_scores,
        dv_scores,
        di_scores,
        w_fa=args.w_fa,
        w_dv=args.w_dv,
        w_di=args.w_di,
        id_to_row=id_to_row,
        injection_ids=injection_ids,
    )

    # ------------------------------------------------------------------
    # 8.8  Save CSV + params snapshot
    # ------------------------------------------------------------------
    csv_path = os.path.join(args.out, "region_scores.csv")
    df_scores.to_csv(csv_path)
    print(f"\n[Output] CSV saved → {csv_path}")

    import json as _json

    _params = {
        "inj": args.inj,
        "sigma": args.sigma,
        "min_sig": args.min_sig,
        "min_vox": args.min_vox,
        "w_fa": args.w_fa,
        "w_dv": args.w_dv,
        "w_di": args.w_di,
        "inj_dilation": args.inj_dilation,
        "sig_dilation": args.sig_dilation,
        "hemi_clip": args.hemi_clip,
        "exclude": args.exclude,
        "axis": args.axis,
    }
    with open(params_path, "w") as _f:
        _json.dump(_params, _f, indent=2)
    print(f"[Output] Step-1 params saved → {params_path}")

    # Print a summary table
    n_term = (df_scores["classification"] == "terminating").sum()
    n_pass = (df_scores["classification"] == "passing").sum()
    print(f"\n  Classified regions:  {n_term} terminating  |  {n_pass} passing")
    print("\n  Top 10 terminating regions:")
    top10 = df_scores[~df_scores["is_injection_site"]].head(10)
    if "acronym" in top10.columns and "name" in top10.columns:
        print(
            top10[
                [
                    "acronym",
                    "name",
                    "FA",
                    "depth_var",
                    "mean_dist_inj_um",
                    "termination_score",
                ]
            ].to_string()
        )
    else:
        print(
            top10[
                ["FA", "depth_var", "mean_dist_inj_um", "termination_score"]
            ].to_string()
        )

    # ------------------------------------------------------------------
    # 8.9  Visualisations
    # ------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("SAVING VISUALISATIONS")
    print("=" * 60)

    visualize_mip_overlay(
        MIP_raw,
        image_ann_2d,
        df_scores,
        injection_ids,
        inj_acronym,
        output_path=os.path.join(args.out, "mip_termination_overlay.png"),
        top_n_labels=args.top_n // 2,
    )

    visualize_barplot(
        df_scores,
        output_path=os.path.join(args.out, "top_regions_barplot.png"),
        top_n=args.top_n,
        injection_acronym=inj_acronym,
    )

    if args.save_nii:
        save_score_nifti(
            df_scores,
            image_ann,
            seg_nii,
            output_path=os.path.join(args.out, "termination_score_vol.nii.gz"),
        )

    # ------------------------------------------------------------------
    # 9.X  Tractography inputs (Step 1 — only when --save_intermediates)
    #
    #      All volumes saved in the same Allen CCF 25 µm space as --seg
    #      (they share seg_nii.affine) so they overlay on the atlas directly.
    #      These are the inputs for aa_tractography.py (Step 2).
    # ------------------------------------------------------------------
    if args.save_intermediates:
        print("\n" + "=" * 60)
        print("SAVING TRACTOGRAPHY INPUTS")
        print("=" * 60)
        if fiber_directions is None:
            # Should not happen because we pass compute_directions=args.save_intermediates,
            # but guard in case of resume path or future refactoring.
            print(
                "[Warning] fiber_directions not computed — re-running FA with directions ..."
            )
            _, fiber_directions = compute_FA_volume(
                image,
                sigma=args.sigma,
                min_signal=args.min_sig,
                compute_directions=True,
            )
        save_tractography_inputs(
            FA_volume,
            fiber_directions,
            image_ann,
            signal_mask_3d,
            injection_ids,
            seg_nii,
            out_dir=args.out,
            inj_dilation=args.inj_dilation,
            sig_dilation=args.sig_dilation,
            hemi_clip=args.hemi_clip,
        )

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
