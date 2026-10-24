"""SCARPPOL lane surface: signed scarp polarity along the fall line (2026-10-24).

Geology
-------
A Quaternary normal-fault scarp is a *signed step* in the detrended
topographic profile.  Walking downhill across it, slope first grows
(the convex crest of the scarp face) and then collapses (the concave
base).  BREAKLINE (session 2026-10-24, ``gems/breakline.py``) used the
isotropic magnitude ``||grad det_elev_slope||``, which cannot separate
that signed crest/base pair from isotropic roughness of the same
magnitude.  This lane projects the slope gradient onto the local
fall-line direction (the unit gradient of ``det_elev``):

    dir2(x) = grad(det_elev_slope)(x) . unit_grad(det_elev)(x)

``|dir2|`` is large where slope changes *along* the direction the
surface actually falls -- the crest/base pair of a scarp -- and small
where slope varies across the fall line (drainage walls, contour-
parallel benches).  The lane surface is

    S(x) = pct_rank( |dir2(x)| ) * coherence(det_elev)(x)
    S_pct = pct_rank(S)

with percentile ranks inside the valid footprint (1001-knot
interpolation, the project-standard rank construction) and the same
structure-tensor coherence as BREAKLINE, so the two surfaces differ
only in the break statistic, not in the lineament gate.

Why this should find faults the catalogue and the parent both miss
------------------------------------------------------------------
Parent R0 sits on the H19-5 potential-field worm skeleton.  A fault
offsetting only alluvium (or the same lithology against itself) can
carry a clear signed scarp step with no magnetic/gravity contrast; it
is invisible to the worms but is exactly the expression expert mappers
trace on DEMs, which is how the competition's new-fault labels were
produced (DrivenData #306, problem description p. 967).  Candidate
pixels are ridge pixels of ``S`` more than 3 px from every H19-5
skeleton pixel.

Named non-fault mimics: pluvial Lake Lahontan shoreline benches and
wave-cut terraces, alluvial-fan segment boundaries, incised channel
banks, and bedding-plane breaks on dipping strata.  All can produce a
signed crest/base pair along the fall line without surface rupture.

Nothing here reads the fault catalogue, so catalogue withholding
cannot leak through this surface.  Pure array math on caller-supplied
float arrays; ``scripts/build_scarppol_variants.py`` owns file I/O.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from .breakline import percentile_rank, structure_tensor_coherence

__all__ = ["percentile_rank", "structure_tensor_coherence", "spaced_top_mask",
           "directional_slope_change", "lane_surface"]

# Re-exported so lane builders use one spacing implementation, not a fork.
from .breakline import spaced_top_mask  # noqa: E402

DERIV_SIGMA_PX = 1.0    # smoothing before gradients (~100 m)


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a), a, np.float32(fill)).astype(np.float32)


def directional_slope_change(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                             valid: np.ndarray,
                             deriv_sigma: float = DERIV_SIGMA_PX) -> np.ndarray:
    """``grad(det_elev_slope) . unit_grad(det_elev)`` -- signed, float32.

    Positive where slope grows along the fall line (scarp crest side),
    negative where it falls (base side).  Flat cells (no fall line)
    return 0.
    """
    valid = np.asarray(valid, bool)
    e = gaussian_filter(_clean(det_elev, valid), float(deriv_sigma))
    s = gaussian_filter(_clean(det_elev_slope, valid), float(deriv_sigma))
    gy, gx = np.gradient(e)
    norm = np.hypot(gy, gx)
    uy = np.divide(gy, norm, out=np.zeros_like(gy), where=norm > 1e-12)
    ux = np.divide(gx, norm, out=np.zeros_like(gx), where=norm > 1e-12)
    sgy, sgx = np.gradient(s)
    return (sgy * uy + sgx * ux).astype(np.float32)


def lane_surface(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                 valid: np.ndarray) -> dict[str, np.ndarray]:
    """SCARPPOL surface and components (float32 arrays).

    Returns ``dir2`` (signed directional slope change), ``dir2_pct``,
    ``coherence``, ``S_raw`` (``dir2_pct * coherence``) and ``S_pct``
    (percentile rank of ``S_raw``), ranks over ``valid``.
    """
    valid = np.asarray(valid, bool)
    dir2 = directional_slope_change(det_elev, det_elev_slope, valid)
    dir2_pct = percentile_rank(np.abs(dir2), valid)
    coh = structure_tensor_coherence(det_elev, valid)
    s_raw = (dir2_pct * coh).astype(np.float32)
    return {"dir2": dir2, "dir2_pct": dir2_pct, "coherence": coh,
            "S_raw": s_raw, "S_pct": percentile_rank(s_raw, valid)}
