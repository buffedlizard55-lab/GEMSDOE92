"""PIEDFRONT lane surface: piedmont range-front relative scarp-break & gravity concordance.

Session 2026-10-24 (GEMSDOE92).  Pre-registered rank-1 hypothesis in
``docs/HYPOTHESES_20261024_PIEDFRONT.md``.

Geology & Physics
-----------------
Prior off-skeleton terrain lanes (BREAKLINE, SCARPPOL, STRAINBREAK) used the
*unnormalized* gradient of detrended-elevation slope ``||grad(det_elev_slope)||``
(Band 19).  Because raw slope in rugged mountain-range cores reaches 20-45 deg
while alluvial fans slope at 1-6 deg, unnormalized ``||grad(det_elev_slope)||``
placed 74.8% of BREAKLINE's off-skeleton dots inside high-elevation mountain
range interiors (``det_elev >= p67``, median slope 19.3 deg, median basement
depth 78 m).  Those mountain-interior dots hit pre-Quaternary bedrock faults on
the USGS SGMC map, but missed the subtle 1-5 m Quaternary alluvial fault scarps
and blind range-front step-faults along the piedmont apron, and failed to clear
the ``RELIEF p10`` holdout bar (0.006045) on ``gems57-pooled-hide-v2``.

In Basin-and-Range extensional tectonics (Wallace 1977, GSA Bulletin; Bucknam &
Anderson 1979, Geology; Faulds & Hinz 2015), active Quaternary normal faults
and range-front geothermal conduits localize along the **piedmont-range-front
hinge**: where bedrock footwalls step down across a subsurface density boundary
into 50-800 m of alluvial basin fill, producing:

1. A sharp **relative break-in-slope** on a gentle background fan slope:

       rel_break(x) = ||grad det_elev_slope(x)|| / (max(det_elev_slope(x), 0) + s0)

   with ``s0 = 2.0 deg``, gated by the structure-tensor orientation coherence of
   detrended elevation (Band 12 ``det_elev``):

       R_scarp(x) = pct_rank(rel_break(x)) * coherence(det_elev)(x)

2. A **piedmont-basement gravity-gradient envelope** combining the horizontal
   gradient magnitude of the isostatic gravity anomaly (Band 5
   ``iso_grav_anom_slope``, sensing the buried basement density step), the
   piedmont elevation transition (Band 12 ``det_elev``), and the alluvial cover
   thickness wedge (Band 15 ``depth_to_base_surf``):

       W_pied(x) = exp(-0.5 * ((pct_rank(det_elev)(x) - 0.45) / 0.28)^2)
                 * exp(-0.5 * ((pct_rank(depth_to_base)(x) - 0.50) / 0.35)^2)
                 * (0.50 + 0.50 * pct_rank(iso_grav_anom_slope)(x))

3. The combined label-free, catalogue-free **PIEDFRONT** prospectivity surface:

       S_raw(x) = R_scarp(x) * W_pied(x),   S_pct(x) = pct_rank(S_raw(x))

Named non-fault mimics
----------------------
Pluvial Lake Lahontan wave-cut shoreline terraces and beach ridges at piedmont
elevations (~1,200-1,330 m AMSL) overlying regional basin-margin gravity
gradients, incised alluvial-fan terrace risers (fan-head trenches), and
pediment-alluvium lithologic contacts.

Nothing in this module reads the fault catalogue.  Pure deterministic array
math reusing ``gems.breakline`` primitives.
"""

from __future__ import annotations

import numpy as np

from .breakline import (
    _clean,
    percentile_rank,
    slope_break_magnitude,
    spaced_top_mask,
    structure_tensor_coherence,
)

SLOPE_SOFTENING_DEG = 2.0
ELEV_PIEDMONT_CENTER = 0.45
ELEV_PIEDMONT_WIDTH = 0.28
DEPTH_COVER_CENTER = 0.50
DEPTH_COVER_WIDTH = 0.35


def relative_slope_break(det_elev_slope: np.ndarray, valid: np.ndarray,
                         s0_deg: float = SLOPE_SOFTENING_DEG) -> np.ndarray:
    """Fractional break-in-slope ``||grad(slope)|| / (max(slope, 0) + s0_deg)``."""
    brk = slope_break_magnitude(det_elev_slope, valid)
    slope_pos = np.maximum(_clean(det_elev_slope, valid), np.float32(0.0))
    return (brk / (slope_pos + np.float32(s0_deg))).astype(np.float32)


def piedfront_surface(
    det_elev: np.ndarray,
    det_elev_slope: np.ndarray,
    iso_grav_slope: np.ndarray,
    depth_to_base: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute the label-free PIEDFRONT surface and its intermediate components.

    All percentile ranks are computed strictly inside ``valid`` using the
    project-standard 1001-knot interpolation (``gems.breakline.percentile_rank``).
    """
    valid = np.asarray(valid, bool)
    rel_brk = relative_slope_break(det_elev_slope, valid)
    rel_brk_pct = percentile_rank(rel_brk, valid)
    coh = structure_tensor_coherence(det_elev, valid)
    r_scarp = (rel_brk_pct * coh).astype(np.float32)

    elev_pct = percentile_rank(det_elev, valid)
    depth_pct = percentile_rank(depth_to_base, valid)
    grav_pct = percentile_rank(iso_grav_slope, valid)

    elev_gate = np.exp(
        -0.5 * ((elev_pct - ELEV_PIEDMONT_CENTER) / ELEV_PIEDMONT_WIDTH) ** 2
    ).astype(np.float32)
    cover_gate = np.exp(
        -0.5 * ((depth_pct - DEPTH_COVER_CENTER) / DEPTH_COVER_WIDTH) ** 2
    ).astype(np.float32)
    w_pied = (elev_gate * cover_gate * (0.50 + 0.50 * grav_pct)).astype(np.float32)
    w_pied[~valid] = 0.0

    s_raw = (r_scarp * w_pied).astype(np.float32)
    s_raw[~valid] = 0.0
    s_pct = percentile_rank(s_raw, valid)

    return {
        "rel_break_pct": rel_brk_pct,
        "coherence": coh,
        "R_scarp": r_scarp,
        "elev_pct": elev_pct,
        "depth_pct": depth_pct,
        "grav_pct": grav_pct,
        "W_pied": w_pied,
        "S_raw": s_raw,
        "S_pct": s_pct,
        "valid": valid,
    }


__all__ = [
    "SLOPE_SOFTENING_DEG",
    "piedfront_surface",
    "relative_slope_break",
    "spaced_top_mask",
]
