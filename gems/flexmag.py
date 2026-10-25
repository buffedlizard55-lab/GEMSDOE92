"""FLEXMAG lane: blind-fault forced-fold hinge x magnetic analytic-signal concordance.

Pre-registered in docs/HYPOTHESES_20261025_FLEXMAG.md (rank 1 of 5).

Geology
-------
A normal fault whose tip has not breached the surface has no scarp for
photo/lidar mapping (the basis of the USGS/INGENIOUS catalogue) to record.
It still folds the cover above its tip: basement depth (B15
``depth_to_base_surf``) and detrended elevation (B12 ``det_elev``) carry a
monocline/forced-fold hinge at mesoscale wavelength, and the fault plane
juxtaposes magnetic basement or hosts a demagnetised damage zone, giving a
strike-blind edge in the total magnetic intensity gradient field.  FLEXMAG
requires both expressions to coincide:

    hinge  = geomean( pct|grad DoG(B15)|, pct|grad DoG(B12)| )
             DoG = G(sigma=6 px) - G(sigma=30 px) band-pass
    coh    = mesoscale structure-tensor coherence of DoG(B15)
    mag    = pct( sqrt(B3^2 + B9^2) )   TMI analytic-signal amplitude
    S      = pct( hinge * coh * (0.30 + 0.70 * mag) )

Named non-fault mimics: sedimentary onlap / paleo-valley margins and
regional basin-edge flexure produce a hinge with no magnetic edge; dike
margins produce a magnetic edge with no flexure.  The concordance gate
(0.30 floor so a pure hinge is down-weighted, not erased) targets exactly
that separation.

Strict zero-leakage invariant: no fault-catalogue array enters any function
in this module.  The caller owns catalogue masking, placement and scoring.
Band numbers are the 1-based GDAL bands of the pinned 19-band stack, read
from the file's own band descriptions (verified 2026-10-25).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

from .breakline import percentile_rank, structure_tensor_coherence
from .gravquad import clean

__all__ = [
    "BAND",
    "DOG_SIGMA_NEAR_PX",
    "DOG_SIGMA_FAR_PX",
    "EDGE_ERODE_PX",
    "MAG_FLOOR",
    "dog_bandpass",
    "gradient_magnitude",
    "magnetic_asa",
    "compute_flexmag_surfaces",
]

# 1-based bands in training_features.tif (GDAL descriptions verified on the
# restored pinned stack, SHA-256 4371c82e... in registry/session_manifest.json)
BAND = dict(
    rtp=2,            # rtp - Reduced to pole magnetic data
    tmi_hg=3,         # tmi_hg - TMI horizontal gradient
    tmi_vg=9,         # tmi_vg - TMI vertical gradient
    det_elev=12,      # det_elev - Detrended elevation
    depth_to_base=15,  # depth_to_base_surf - Depth to basement surface
)

DOG_SIGMA_NEAR_PX = 6.0    # 600 m: suppresses sub-km scarp/drainage noise
DOG_SIGMA_FAR_PX = 30.0    # 3 km: suppresses regional tilt / basin wavelength
EDGE_ERODE_PX = 32         # >= far sigma: kills median-fill footprint-edge steps
MAG_FLOOR = 0.30           # hinge-only evidence keeps 30% weight (pre-registered)
MAG_SMOOTH_PX = 2.0


def dog_bandpass(field: np.ndarray, valid: np.ndarray,
                 sigma_near: float = DOG_SIGMA_NEAR_PX,
                 sigma_far: float = DOG_SIGMA_FAR_PX) -> np.ndarray:
    """Difference-of-Gaussians band-pass of a cleaned field (float32)."""
    if not (0.0 < sigma_near < sigma_far):
        raise ValueError("require 0 < sigma_near < sigma_far")
    u = clean(field, valid)
    near = gaussian_filter(u, float(sigma_near))
    far = gaussian_filter(u, float(sigma_far))
    out = (near - far).astype(np.float32)
    out[~np.asarray(valid, bool)] = 0.0
    return out


def gradient_magnitude(field: np.ndarray) -> np.ndarray:
    """``||grad field||`` by central differences (float32, same shape)."""
    gy, gx = np.gradient(np.asarray(field, dtype=np.float32))
    return np.hypot(gy, gx).astype(np.float32)


def magnetic_asa(tmi_hg: np.ndarray, tmi_vg: np.ndarray,
                 valid: np.ndarray) -> np.ndarray:
    """TMI analytic-signal amplitude ``sqrt(hg^2 + vg^2)``, lightly smoothed.

    B3 is the horizontal-gradient magnitude and B9 the vertical gradient of
    total magnetic intensity, so this is the classic total-gradient /
    analytic-signal amplitude (strike-blind to first order).
    """
    hg = clean(tmi_hg, valid)
    vg = clean(tmi_vg, valid)
    asa = np.hypot(hg, vg).astype(np.float32)
    asa = gaussian_filter(asa, float(MAG_SMOOTH_PX)).astype(np.float32)
    asa[~np.asarray(valid, bool)] = 0.0
    return asa


def compute_flexmag_surfaces(
    *,
    depth_to_base: np.ndarray,
    det_elev: np.ndarray,
    tmi_hg: np.ndarray,
    tmi_vg: np.ndarray,
    rtp: np.ndarray,
    footprint: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return the FLEXMAG surface, its two ablation surfaces, and components.

    Keys (all float32 in [0, 1] except ``valid`` bool; 0 outside ``valid``):
    ``valid``, ``hinge``, ``coherence``, ``mag``, ``S_flexmag`` (experiment 1),
    ``S_flex`` (experiment 2, no magnetic gate), ``S_mag`` (experiment 3, no
    flexure).  Pure array math; no catalogue is read here.
    """
    foot = np.asarray(footprint, bool)
    raw_valid = foot.copy()
    for arr in (depth_to_base, det_elev, tmi_hg, tmi_vg, rtp):
        a = np.asarray(arr, dtype=np.float32)
        if a.shape != foot.shape:
            raise ValueError(f"band shape {a.shape} != footprint {foot.shape}")
        raw_valid &= np.isfinite(a) & (a > -1e30)
    if not raw_valid.any():
        raise ValueError("no valid footprint cells")

    # Median-filled outside-valid cells create a false step (hence a false
    # hinge) at the footprint boundary after the far-sigma blur; erode the
    # analysis validity by >= sigma_far so no placed dot can sit on it.
    dist_inside = distance_transform_edt(raw_valid)
    valid = raw_valid & (dist_inside >= float(EDGE_ERODE_PX))
    del dist_inside
    if not valid.any():
        raise ValueError("edge erosion removed every valid cell")

    bp_base = dog_bandpass(depth_to_base, raw_valid)
    bp_elev = dog_bandpass(det_elev, raw_valid)
    hinge_base = percentile_rank(gradient_magnitude(bp_base), valid)
    hinge_elev = percentile_rank(gradient_magnitude(bp_elev), valid)
    hinge = np.sqrt(np.maximum(hinge_base * hinge_elev, 0.0)).astype(np.float32)
    del bp_elev, hinge_base, hinge_elev

    # Mesoscale linearity of the basement band-pass (tensor window >> the
    # native-scale lanes' 2 px, matching the flexure wavelength).
    coh = structure_tensor_coherence(bp_base, valid, deriv_sigma=1.0,
                                     tensor_sigma=8.0)
    del bp_base

    mag = percentile_rank(magnetic_asa(tmi_hg, tmi_vg, raw_valid), valid)

    gate = (np.float32(MAG_FLOOR) + np.float32(1.0 - MAG_FLOOR) * mag).astype(np.float32)
    s_flexmag = percentile_rank((hinge * coh * gate).astype(np.float32), valid)
    s_flex = percentile_rank((hinge * coh).astype(np.float32), valid)

    coh_native = structure_tensor_coherence(rtp, valid, deriv_sigma=1.0,
                                            tensor_sigma=2.0)
    s_mag = percentile_rank((mag * coh_native).astype(np.float32), valid)
    del coh_native, gate

    out = dict(valid=valid, hinge=hinge, coherence=coh, mag=mag,
               S_flexmag=s_flexmag, S_flex=s_flex, S_mag=s_mag)
    for k, v in out.items():
        if k == "valid":
            continue
        v[~valid] = 0.0
        if not np.isfinite(v).all() or float(v.min()) < 0.0 or float(v.max()) > 1.0:
            raise AssertionError(f"surface {k} left [0,1] or went non-finite")
    return out
