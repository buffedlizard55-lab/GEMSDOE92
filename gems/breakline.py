"""BREAKLINE lane surface: linear DEM slope-breaks (session 2026-10-24).

Geology
-------
A Quaternary normal-fault scarp is, in detrended topography, a *linear
break-in-slope*: slope itself is anomalous in a strip along the scarp face,
so the gradient of the slope field peaks along two lines (scarp crest and
base).  Most pixels with a large slope gradient are not faults, though --
incised drainages and rugged range interiors produce isotropic break
noise everywhere.  The structure-tensor coherence of the detrended
elevation field separates the two populations: it is near 1 where the
local gradient field has one dominant orientation (a lineament) and near
0 where orientations are mixed.

The lane surface is therefore

    L(x) = pct_rank( ||grad det_elev_slope(x)|| ) * coherence(det_elev)(x)

with percentile ranks taken inside the valid footprint (1001-knot
interpolation, the project-standard rank construction).  Both inputs come
from the pinned 19-band stack (Band 12 ``det_elev``, Band 19
``det_elev_slope``); nothing here reads the fault catalogue, so catalogue
withholding cannot leak through this surface.

Why this should find faults the catalogue and the parent both miss
------------------------------------------------------------------
Parent R0 sits on the H19-5 potential-field worm skeleton: lines that
needed a magnetic/gravity expression to be drawn.  A fault juxtaposing
the same lithology against itself (or offsetting only alluvium) can carry
a clear topographic scarp with no usable potential-field contrast -- it
is invisible to the worm skeleton but is exactly what expert mappers
trace on high-resolution DEMs, which is how the competition's new-fault
labels were produced (problem description, DrivenData #306 page 967).
Candidate pixels for this lane are ridge pixels of ``L`` lying more than
3 px from every H19-5 skeleton pixel, i.e. linear scarp-breaks the worm
geometry never represented.

Named non-fault mimics: pluvial-lake shoreline terraces (Lahontan),
alluvial-fan segment boundaries and terrace risers, bedding-plane breaks
on dipping strata, and glacial/periglacial trimlines.  All produce
linear, coherent slope breaks without Quaternary surface rupture.

Everything here is pure array math on caller-supplied float arrays; the
builder in ``scripts/build_breakline_variants.py`` owns file I/O,
sentinel masking and provenance.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

DERIV_SIGMA_PX = 1.0    # gradient smoothing for the structure tensor (~100 m)
TENSOR_SIGMA_PX = 2.0   # tensor integration scale (~200 m either side of a break)


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank in [0, 1] over ``valid`` finite cells, 1001 knots.

    Same construction the SNAP/RELIEF/DILATATION builders use (their local
    ``percentile_rank`` copies assume pre-cleaned input; this one also
    guards non-finite cells so it is safe on raw stack bands).
    """
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    out = np.zeros(a.shape, np.float32)
    vals = a[m]
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[m] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


def _clean(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Replace non-finite cells with the finite-valid median (float32)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a), a, np.float32(fill)).astype(np.float32)


def slope_break_magnitude(det_elev_slope: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """``||grad(det_elev_slope)||`` -- magnitude of the break-in-slope field."""
    s = _clean(det_elev_slope, valid)
    gy, gx = np.gradient(s)
    return np.hypot(gy, gx).astype(np.float32)


def structure_tensor_coherence(field: np.ndarray, valid: np.ndarray,
                               deriv_sigma: float = DERIV_SIGMA_PX,
                               tensor_sigma: float = TENSOR_SIGMA_PX) -> np.ndarray:
    """Local orientation coherence in [0, 1] of a scalar field's gradients.

    ``coh = sqrt((Jxx-Jyy)^2 + 4 Jxy^2) / (Jxx+Jyy)`` on the smoothed
    gradient outer product.  1 = single dominant orientation (lineament),
    0 = isotropic.  Flat areas (zero gradient energy) return 0.
    """
    a = gaussian_filter(_clean(field, valid), float(deriv_sigma))
    gy, gx = np.gradient(a)
    jxx = gaussian_filter(gx * gx, float(tensor_sigma))
    jyy = gaussian_filter(gy * gy, float(tensor_sigma))
    jxy = gaussian_filter(gx * gy, float(tensor_sigma))
    coh = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy * jxy) / np.maximum(jxx + jyy, 1e-12)
    return np.clip(coh, 0.0, 1.0).astype(np.float32)


def lane_surface(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                 valid: np.ndarray) -> dict[str, np.ndarray]:
    """Build the BREAKLINE surface and its two components.

    Returns float32 arrays: ``break_pct`` (percentile rank of the
    slope-break magnitude), ``coherence`` (0..1), ``L_raw``
    (``break_pct * coherence``) and ``L_pct`` (percentile rank of
    ``L_raw``).  All ranks are taken over ``valid``.
    """
    valid = np.asarray(valid, bool)
    break_pct = percentile_rank(slope_break_magnitude(det_elev_slope, valid), valid)
    coh = structure_tensor_coherence(det_elev, valid)
    l_raw = (break_pct * coh).astype(np.float32)
    l_pct = percentile_rank(l_raw, valid)
    return {"break_pct": break_pct, "coherence": coh, "L_raw": l_raw, "L_pct": l_pct}


def spaced_top_mask(surface: np.ndarray, cand_mask: np.ndarray, n: int,
                    min_dist_px: float = 2.8, cand_cap: int = 400_000) -> np.ndarray:
    """Top-``n`` candidate pixels by surface value under a spacing floor.

    Deterministic greedy scan in descending surface order (stable, so ties
    break row-major): take a pixel unless an already-taken pixel lies
    within ``min_dist_px`` (strictly), which reproduces the R0 lineage's
    2.828 px nearest-neighbour floor -- adjacent diagonals at sqrt(8) px
    are allowed, everything closer is blocked.  The scan is restricted to
    the ``cand_cap`` highest-valued candidates for runtime; callers that
    need ``n`` dots must pass a pool whose high-value region is dense
    enough that the floor does not exhaust it (asserted by the builder).

    This emission rule -- concentrate on the strongest lineaments first,
    spaced along them -- was the rule exercised by the pre-build surface
    screen.  It is intentionally *not* the exact expected-DTI greedy:
    under a rank-percentile weight field that greedy spreads dots to
    cover low-rank support mass, which measured worse on every local
    instrument in this lane (see IRREGULARITIES 2026-10-24 PASS-2 note
    and evidence/screen_vs_greedy_diagnostic.json).
    """
    surface = np.asarray(surface, dtype=np.float32)
    cand_mask = np.asarray(cand_mask, bool)
    ys, xs = np.nonzero(cand_mask)
    vals = surface[ys, xs]
    if len(ys) > cand_cap:
        idx = np.argpartition(-vals, cand_cap)[:cand_cap]
        ys, xs, vals = ys[idx], xs[idx], vals[idx]
    order = np.argsort(-vals, kind="stable")
    ys, xs = ys[order], xs[order]

    r = int(np.floor(min_dist_px))
    offs = [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1)
            if np.hypot(dy, dx) < min_dist_px]
    height, width = surface.shape
    blocked = np.zeros(surface.shape, bool)
    chosen = np.zeros(surface.shape, bool)
    count = 0
    for y, x in zip(ys.tolist(), xs.tolist()):
        if blocked[y, x]:
            continue
        chosen[y, x] = True
        count += 1
        if count == n:
            break
        for dy, dx in offs:
            yy, xx = y + dy, x + dx
            if 0 <= yy < height and 0 <= xx < width:
                blocked[yy, xx] = True
    if count != n:
        raise ValueError(f"spaced_top_mask: selected {count} of {n} requested dots "
                         f"(candidate cap {cand_cap}, spacing floor {min_dist_px} px)")
    return chosen
