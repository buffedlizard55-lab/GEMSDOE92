"""RADSCARP lane surface: fused DEM scarp-break + radiometric alteration coherence (2026-10-25).

Geology
-------
Geothermal faults in the Great Basin are both mechanical and hydrogeochemical
structures. Mechanically they produce a linear break-in-slope on detrended
topography (detectable as ||grad det_elev_slope|| with coherent orientation).
Geochemically, sustained fluid flow precipitates or leaches radioelement-bearing
minerals along the damage zone, creating a linear radiometric edge in the
GeoDAWN airborne gamma-ray survey (K, Th, U, total count). A shoreline terrace
has a topographic break but no radiometric edge; a lithologic contact has a
radiometric edge but no coherent topographic break; an agricultural playa
boundary may have both but is not fault-bounded at depth. Requiring the
co-location of the two independent lineaments therefore suppresses the dominant
false positives of either detector alone while retaining fault-controlled
geothermal conduits.

The lane surface is

    L(x) = pct_rank(||grad det_elev_slope||) * coherence(det_elev)
    R(x) = pct_rank(||grad (K/Th)||) * coherence(K/Th)
    S(x) = L(x) * R(x)          S_pct = pct_rank(S)

All percentile ranks are taken inside the valid footprint (1001-knot
interpolation, the project-standard construction). Inputs:

  - L uses the pinned 19-band stack: Band 12 det_elev, Band 19 det_elev_slope
  - R uses the pinned external GeoDAWN radiometrics: geodawn_rad_u8.tif
    Bands 1 K and 2 Th (uint8 0-255), K/Th ratio (float32). Nothing here reads
    the fault catalogue, so catalogue withholding cannot leak.

Why it should find faults the catalogue and parent both miss
-------------------------------------------------------------
Parent R0 sits on the H19-5 potential-field worm skeleton: lines that needed a
magnetic/gravity expression to be drawn. A geothermal fault that offsets thin
alluvium (<50 m throw) and is sealed by silica sinter may have a subtle but
linear DEM scarp and a coincident radiometric alteration halo, yet carry no
usable potential-field contrast (density/susceptibility change below detection
of 400 m line-spacing aeromag). Expert mappers trace the scarp on 1 m LiDAR;
geochemists map the alteration halo; neither is represented in the worm skeleton
or the USGS/INGENIOUS Quaternary catalogue, which is dominated by range-bounding
scarps mapped on older 10 m DEMs/aerial photos.

Candidate pixels are R-pixels on the fused ridges lying >3 px from every H19-5
pixel, i.e. alteration-coated scarp-breaks the worm geometry never represented.

Named non-fault mimics: silicified lithologic ridges with radiometric contrast
(rhyolitic tuff vs basalt), playa evaporite margins where K/Th changes sharply
across a topographic step, and road/berm construction corridors that disturb
both topography and surface radioelements. All produce co-located linear breaks
without Quaternary fault displacement.

Pure array math; builder owns I/O, sentinel masking, provenance.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

DERIV_SIGMA_PX = 1.0
TENSOR_SIGMA_PX = 2.0


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank in [0,1] over valid finite cells, 1001 knots."""
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
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(np.isfinite(a), a, np.float32(fill)).astype(np.float32)


def slope_break_magnitude(field: np.ndarray, valid: np.ndarray) -> np.ndarray:
    s = _clean(field, valid)
    gy, gx = np.gradient(s)
    return np.hypot(gy, gx).astype(np.float32)


def structure_tensor_coherence(field: np.ndarray, valid: np.ndarray,
                               deriv_sigma: float = DERIV_SIGMA_PX,
                               tensor_sigma: float = TENSOR_SIGMA_PX) -> np.ndarray:
    a = gaussian_filter(_clean(field, valid), float(deriv_sigma))
    gy, gx = np.gradient(a)
    jxx = gaussian_filter(gx * gx, float(tensor_sigma))
    jyy = gaussian_filter(gy * gy, float(tensor_sigma))
    jxy = gaussian_filter(gx * gy, float(tensor_sigma))
    coh = np.sqrt((jxx - jyy) ** 2 + 4.0 * jxy * jxy) / np.maximum(jxx + jyy, 1e-12)
    return np.clip(coh, 0.0, 1.0).astype(np.float32)


def radiometric_ratio(k: np.ndarray, th: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """K/Th ratio, float32, sentinel-cleaned via _clean on output."""
    k_f = _clean(k.astype(np.float32), valid)
    th_f = _clean(th.astype(np.float32), valid)
    # Th in footprint never 0; use eps for safety outside
    ratio = k_f / np.maximum(th_f, 1.0)
    # Clip extreme tails (playa spikes) to 99.5th percentile for stability
    # but keep original outside valid; will be masked by percentile_rank
    m = np.asarray(valid, bool)
    if m.any():
        v = ratio[m]
        lo, hi = np.quantile(v, [0.005, 0.995])
        ratio = np.clip(ratio, lo, hi).astype(np.float32)
    return ratio.astype(np.float32)


def lane_surface(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                 k_band: np.ndarray, th_band: np.ndarray,
                 valid: np.ndarray) -> dict[str, np.ndarray]:
    """Build RADSCARP fused surface.

    Returns dict with:
      break_pct, coherence_L, L_raw, L_pct,
      R_ratio, R_grad_mag, R_break_pct, R_coherence, R_raw,
      S_raw, S_pct
    """
    valid = np.asarray(valid, bool)

    # L branch (topographic)
    break_pct = percentile_rank(slope_break_magnitude(det_elev_slope, valid), valid)
    coh_l = structure_tensor_coherence(det_elev, valid)
    l_raw = (break_pct * coh_l).astype(np.float32)

    # R branch (radiometric)
    r_ratio = radiometric_ratio(k_band, th_band, valid)
    r_grad_mag = slope_break_magnitude(r_ratio, valid)
    r_break_pct = percentile_rank(r_grad_mag, valid)
    r_coh = structure_tensor_coherence(r_ratio, valid)
    r_raw = (r_break_pct * r_coh).astype(np.float32)

    # Fusion
    s_raw = (l_raw * r_raw).astype(np.float32)
    return {
        "break_pct": break_pct,
        "coherence_L": coh_l,
        "L_raw": l_raw,
        "L_pct": percentile_rank(l_raw, valid),
        "R_ratio": r_ratio,
        "R_grad_mag": r_grad_mag,
        "R_break_pct": r_break_pct,
        "R_coherence": r_coh,
        "R_raw": r_raw,
        "S_raw": s_raw,
        "S_pct": percentile_rank(s_raw, valid),
    }


def spaced_top_mask(surface: np.ndarray, cand_mask: np.ndarray, n: int,
                    min_dist_px: float = 2.8, cand_cap: int = 400_000) -> np.ndarray:
    """Top-n candidate pixels by surface value under a spacing floor.

    Deterministic greedy scan in descending surface order (stable, so ties
    break row-major): take a pixel unless an already-taken pixel lies
    within min_dist_px (strictly), which reproduces the R0 lineage's
    2.828 px nearest-neighbour floor -- adjacent diagonals at sqrt(8) px
    are allowed, everything closer is blocked.  The scan is restricted to
    the cand_cap highest-valued candidates for runtime; callers that need
    n dots must pass a pool whose high-value region is dense enough that
    the floor does not exhaust it (asserted by the builder).
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
