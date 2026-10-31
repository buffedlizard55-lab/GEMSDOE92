"""MDC lane (H-92M): non-local Morpho-Disequilibrium & Concealed-strand prior.

Pre-registration: ``docs/HYPOTHESES_20261031_MDC.md``.

Physical idea
-------------
Every topographic lane in this repository (BREAKLINE, SCARPPOL, KNICK, VENTSCARP,
LIDAR-SINTERVALVE, ...) queries the DEM at, or a few pixels around, the candidate
cell: a slope break, a curvature sign change, a scarp-polarity step, a knickpoint.
Those detectors are pixel-local. A fault strand buried under 10-500 m of
Plio-Quaternary fan or playa fill (``Band 15 depth_to_base_surf`` > ~100 m) has no
100 m-pixel expression at all, so a local detector cannot find it, which is exactly
the recall deficit recorded for the R0 family in ``docs/WHY_0_2778.md``.

Drainage networks integrate tectonic forcing over kilometres and over 10^4-10^5 yr,
so a concealed strand can still show up as a *catchment-scale* disequilibrium even
when no single pixel breaks. The four classical morphotectonic indices used here
are non-local functionals of the elevation field:

* local relative height / relief inefficiency (hypsometric-analogue; Bull 1978),
* mountain-front sinuosity ``Smf`` (Bull & McFadden 1977; DeMartino et al. 2021),
* catchment/asymmetry coherence of slope-facing (aspect-vector coherence; Chen et
  al. 2003),
* buried-basement step measured *across* the front, from the gravity field
  (``Band 18`` horizontal gradient projected on the front normal; Zeldrich-type
  range-front geometry).

A cell is promoted when the *geophysical* cross-front step is large while the
*topographic* scarp energy is small -- the "topo-blind ratio". That inverse
contrast is the signature of a covered strand and cannot be produced by a sharp
lithologic contact at the surface (which makes both terms large).

Novelty vs this repository
--------------------------
``grep -riE "catchment|accumulation|sinuosity|hypsometr|steepness" gems/*.py`` returns
nothing: no module computes an integrated (window/catchment-scale) morphotectonic
functional, and no module projects the basement gradient on the range-front normal.
Polarity-lock lanes (BLINDFAULT, COULOMB_LOQO, FLEXURE_KNICK_PROVINCE, LISTRICDIP,
POISSONFLEX, RADIOCONTACT) use the sign of the E-W gravity derivative only; they do
not form the topo-blind inverse contrast nor the drainage-coherence terms.

Strict zero-leakage invariant
-----------------------------
No fault-catalogue array enters ``compute_mdc_features``. The catalogue is used only
later, by the caller, as the exclusion collar (``d_cat``) exactly as the competition
masks mapped faults out of scoring.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

SENTINEL = -3.4028235e38

#: band indices (1-based GDAL bands of the pinned ``training_features.tif``)
BAND = {
    "rtp": 2, "tmi_hg": 3, "geod_dilaterate": 8, "iso_grav_anom_vg": 11,
    "det_elev": 12, "iso_grav_anom": 13, "tmi": 14, "depth_to_base_surf": 15,
    "cond_surf": 17, "iso_grav_anom_hg": 18, "det_elev_slope": 19,
}

MDC_FEATURE_NAMES: tuple[str, ...] = (
    "mdc_relief_inefficiency",       # local relative height, 3.1 km window
    "mdc_relief_alongstrike_grad",   # along-front gradient of the above (uplift-cell edge)
    "mdc_front_sinuosity_deficit",   # 1 - Smf_local  (low = linear mature front)
    "mdc_aspect_coherence",          # |mean unit-aspect| / mean |unit-aspect| at 1 km
    "mdc_basement_step_across_front",# |grad depth_to_base . front normal| at 1 km
    "mdc_potential_edge_energy",     # hyps. of (B18 grav hg, B03 tmi hg) concordant edge
    "mdc_topo_blind_ratio",          # rank(basement step) - rank(scarp energy)
    "mdc_extension_dilatation",      # relu(-B08) extension only (fluid-pathway modulator)
)

#: pre-registered window sizes in pixels (100 m grid)
W_RELIEF = 31   # 3.1 km  -> catchment-scale relative height
W_FRONT = 21    # 2.1 km  -> bedrock/alluvium contact perimeter-area (Smf analogue)
W_COH = 11      # 1.1 km  -> slope-facing coherence
SMOOTH = 1.2    # px, light gaussian on the composite before crest extraction


# ----------------------------------------------------------------------------- I/O
def read_band(path: str | Path, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(band).astype(np.float32)


def clean(a: np.ndarray, footprint: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Replace nodata / sentinels / non-finite with the finite-valid median.

    Returns (filled float32 field, ok mask). Same contract as the shared
    ``gems.drainage_knick.clean`` so a fold-crop stays contiguous.
    """
    a = np.asarray(a, dtype=np.float32)
    ok = footprint & np.isfinite(a) & (a > SENTINEL + 1e6)
    fill = float(np.median(a[ok])) if ok.any() else 0.0
    return np.where(ok, a, fill).astype(np.float32), ok


def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Percentile rank in [0,1] over finite valid cells (1001 knots)."""
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    out = np.zeros(a.shape, np.float32)
    vals = a[m]
    if vals.size == 0:
        return out
    knots = np.quantile(vals, np.linspace(0.0, 1.0, 1001))
    out[m] = np.interp(vals, knots, np.linspace(0.0, 1.0, 1001)).astype(np.float32)
    return out


# ------------------------------------------------------------------- morphometrics
def relief_field(det_elev: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Local relative height ``(z - zmin_W) / (zmax_W - zmin_W)`` in [0,1].

    Hypsometric-analogue: a bedrock block still standing high relative to its own
    local valley floor over a 3.1 km window has not yet degraded to base level,
    which is the classical signature of recent differential uplift across a range
    front (Bull 1978). Separable min/max filters keep this O(N*W) instead of O(N*W^2).
    """
    z = np.where(footprint, det_elev, np.nan).astype(np.float32)
    zf = np.where(footprint, z, np.nanmax(z) if np.isfinite(z).any() else 0.0)
    zmin = ndi.minimum_filter(zf, size=W_RELIEF, mode="nearest")
    zmax = ndi.maximum_filter(zf, size=W_RELIEF, mode="nearest")
    rng = np.maximum(zmax - zmin, 1e-3)
    return np.clip((zf - zmin) / rng, 0.0, 1.0).astype(np.float32)


def front_normal(det_elev: np.ndarray, bedrock: np.ndarray, footprint: np.ndarray):
    """Unit normal of the smoothed bedrock/alluvium contact + a contact-confidence map.

    ``bedrock`` is a bool map of the >0 detrended-elevation (positive-relief) block.
    The contact is the gradient of the 2.1 km-smoothed block fraction; its unit
    normal points basin-ward. Returned as (front_energy, n_y, n_x).
    """
    frac = ndi.uniform_filter(bedrock.astype(np.float32), size=W_FRONT)
    gy, gx = np.gradient(frac, axis=0), np.gradient(frac, axis=1)
    e = np.hypot(gy, gx).astype(np.float32)
    e = np.where(footprint, e, 0.0)
    denom = np.maximum(e, 1e-6)
    return e, (gy / denom).astype(np.float32), (gx / denom).astype(np.float32)


def front_sinuosity_deficit(bedrock: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """``1 - Smf_local`` where ``Smf_local = L / sqrt(A)`` on a 2.1 km window.

    Classical Bull & McFadden (1977) front sinuosity: a low value marks a straight,
    mature, fault-controlled front; a high value marks a segmented, fan-confused
    front. Here the *perimeter-to-sqrt-area* ratio is estimated locally from the
    smoothed block-fraction field (its gradient magnitude is a perimeter density),
    so the index is a continuous map rather than a single number per front.
    """
    frac = ndi.uniform_filter(bedrock.astype(np.float32), size=W_FRONT)
    gy, gx = np.gradient(frac, axis=0), np.gradient(frac, axis=1)
    perim = np.hypot(gy, gx)
    area = np.clip(frac, 1e-4, 1.0)
    smf = perim / np.sqrt(area)
    smf = ndi.uniform_filter(np.where(footprint, smf, 0.0).astype(np.float32), size=W_FRONT)
    band = (frac > 0.02) & (frac < 0.98) & footprint
    r = percentile_rank(np.where(band, smf, np.nan), band)
    return (1.0 - r).astype(np.float32)


def aspect_coherence(gy: np.ndarray, gx: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Vector coherence ``|mean(grad)| / mean|grad|`` at 1.1 km, scaled by slope.

    1 where every cell faces the same way (a planar fault facet or a scarp), ~0 in
    dendritic dissection or hummocky landslide terrain. Multiplying by the local
    slope magnitude keeps a flat, coherent playa from scoring like a facet.
    """
    mag = np.hypot(gy, gx)
    vy = np.where(footprint, gy, 0.0).astype(np.float32)
    vx = np.where(footprint, gx, 0.0).astype(np.float32)
    my = ndi.uniform_filter(vy, size=W_COH)
    mx = ndi.uniform_filter(vx, size=W_COH)
    mm = ndi.uniform_filter(mag.astype(np.float32), size=W_COH)
    coh = np.hypot(my, mx) / np.maximum(mm, 1e-6)
    return (coh * np.tanh(mm / (mm.std() + 1e-6))).astype(np.float32)


def basement_step_across_front(depth: np.ndarray, n_y: np.ndarray, n_x: np.ndarray,
                               front_energy: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """``|grad depth_to_basement . front normal|`` smoothed at 1.1 km.

    A range-front normal fault offsets the basement surface; the offset direction is
    perpendicular to the front, so projecting the basement gradient onto the front
    normal isolates the *throw* and suppresses contacts that run parallel to the
    front. This is the term that survives sediment cover, and it is what makes the
    lane able to find a strand the DEM cannot see.
    """
    dy, dx = np.gradient(depth, axis=0), np.gradient(depth, axis=1)
    proj = dy * n_y + dx * n_x
    proj = np.where(footprint, proj, 0.0).astype(np.float32)
    amp = ndi.uniform_filter(np.abs(proj), size=W_COH)
    return (amp * (0.25 + 0.75 * np.clip(front_energy / (front_energy.max() + 1e-9), 0, 1))
            ).astype(np.float32)


def potential_edge_energy(grav_hg: np.ndarray, tmi_hg: np.ndarray, rtp: np.ndarray,
                          footprint: np.ndarray) -> np.ndarray:
    """Concordant gravity+magnetic edge energy (amplitude geometric mean).

    A basement-involved fault juxtaposes dense, magnetized footwall against light,
    non-magnetic fill, so BOTH horizontal gradients peak on the same pixel. A
    sedimentary or alteration contact usually moves only one field. The geometric
    mean rewards joint expression and is zero when either field is flat.
    """
    g = np.clip(percentile_rank(np.abs(grav_hg), footprint), 0, 1)
    m = np.clip(percentile_rank(np.abs(tmi_hg), footprint), 0, 1)
    r = np.clip(percentile_rank(np.abs(rtp), footprint), 0, 1)
    return np.sqrt(np.maximum(g, 0) * np.maximum(m, 0)) * (0.5 + 0.5 * r).astype(np.float32)


# ------------------------------------------------------------------------- the stack
def compute_mdc_features(bands: dict[str, np.ndarray], footprint: np.ndarray
                         ) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]:
    """Build the eight MDC features, the composite surface, and the crest mask.

    ``bands`` maps :data:`BAND` keys to full-grid float32 arrays (already read from
    the pinned stack; this function does not touch the catalogue).

    Returns ``(features, S, crest)`` where ``S`` is the composite [0,1] surface and
    ``crest`` is the 1-px-wide ridge mask of the lightly smoothed surface.
    """
    foot = np.asarray(footprint, bool)
    fields: dict[str, np.ndarray] = {}
    oks: list[np.ndarray] = []
    for k, a in bands.items():
        f, ok = clean(np.asarray(a, np.float32), foot)
        bands[k] = f
        oks.append(ok)
        del f, ok
    valid = np.ones(foot.shape, bool)
    for ok in oks:
        valid &= ok
    del oks

    det_elev = bands["det_elev"]
    slope = bands["det_elev_slope"]
    gy, gx = np.gradient(det_elev, axis=0), np.gradient(det_elev, axis=1)
    scarp_energy = np.hypot(gy, gx).astype(np.float32)

    relief = relief_field(det_elev, foot)
    bedrock = (det_elev > 0.0) & foot
    fe, n_y, n_x = front_normal(det_elev, bedrock, foot)
    smf_def = front_sinuosity_deficit(bedrock, foot)
    coh = aspect_coherence(gy, gx, foot)
    step = basement_step_across_front(bands["depth_to_base_surf"], n_y, n_x, fe, foot)
    edge = potential_edge_energy(bands["iso_grav_anom_hg"], bands["tmi_hg"], bands["rtp"], foot)

    # along-front gradient of relative height: the edge of an uplift cell
    rgy, rgx = np.gradient(relief, axis=0), np.gradient(relief, axis=1)
    rel_grad = np.hypot(rgy, rgx).astype(np.float32) * np.clip(fe / (fe.max() + 1e-9), 0, 1)

    r_step = percentile_rank(step, foot)
    r_scarp = percentile_rank(np.where(slope > 0, slope, 0.0), foot)
    blind = (r_step - r_scarp).astype(np.float32)          # >0 => geophysics-only expression
    ext = np.clip(-bands["geod_dilaterate"], 0.0, None).astype(np.float32)
    r_ext = percentile_rank(ext, foot)

    f = {
        "mdc_relief_inefficiency": percentile_rank(relief, foot),
        "mdc_relief_alongstrike_grad": percentile_rank(rel_grad, foot),
        "mdc_front_sinuosity_deficit": smf_def,
        "mdc_aspect_coherence": percentile_rank(coh, foot),
        "mdc_basement_step_across_front": r_step,
        "mdc_potential_edge_energy": percentile_rank(edge, foot),
        "mdc_topo_blind_ratio": percentile_rank(blind, foot),
        "mdc_extension_dilatation": r_ext,
    }
    features = {k: np.asarray(v, np.float32) for k, v in f.items()}

    # Pre-registered composite (weights fixed BEFORE any holdout number was seen).
    s = (0.30 * features["mdc_basement_step_across_front"]
         + 0.22 * features["mdc_potential_edge_energy"]
         + 0.14 * features["mdc_relief_alongstrike_grad"]
         + 0.12 * features["mdc_relief_inefficiency"]
         + 0.10 * features["mdc_aspect_coherence"]
         + 0.06 * features["mdc_front_sinuosity_deficit"]
         + 0.06 * features["mdc_extension_dilatation"])
    # Topo-blind amplifier, ADDITIVE so the composite keeps its dynamic range and
    # never saturates (a multiplicative gain followed by max-normalisation collapsed
    # the median crest value onto 1.0 and destroyed the ranking; caught 2026-10-31).
    blind_bonus = 0.30 * np.clip(features["mdc_topo_blind_ratio"] - 0.55, 0.0, None) / 0.45
    S = np.clip(s + blind_bonus, 0.0, 1.0).astype(np.float32)
    S = np.where(foot, S, 0.0).astype(np.float32)
    sm = ndi.gaussian_filter(S, sigma=SMOOTH)
    crest = (ndi.maximum_filter(sm, size=3) == sm) & foot & (sm > 0)
    return features, S, crest


# ------------------------------------------------------------------ emission policy
def two_zone_quota(S: np.ndarray, cand: np.ndarray, d_cat: np.ndarray, n_total: int,
                   near_frac: float = 0.65, min_dist_px: float = 2.8,
                   near_band: tuple[float, float] = (2.0, 6.0)) -> dict[str, np.ndarray]:
    """Kernel-matched emission split between the near-corridor and the far field.

    ``near_band`` reproduces the only allocation change the fleet's own receipts
    reward monotonically (the 2-6 px piedmont corridor that carried 0.2600 -> 0.2708
    -> 0.2778), and the far arm adds the concealed strands the near corridor cannot
    see. Both zones are emitted with the 2.8 px spacing floor so that consecutive
    dots stay inside one 300 m triangular-kernel support along strike.
    """
    from .breakline import spaced_top_mask  # local import: keeps module import-light

    near = cand & (d_cat > near_band[0]) & (d_cat <= near_band[1])
    far = cand & (d_cat > near_band[1])
    n_near = int(round(near_frac * n_total))
    out_near = spaced_top_mask(S, near, n_near, min_dist_px=min_dist_px, cand_cap=1_200_000)
    got = int(out_near.sum())
    out_far = spaced_top_mask(S, far, n_total - got, min_dist_px=min_dist_px, cand_cap=1_200_000)
    return dict(near=out_near, far=out_far, both=(out_near | out_far))


def zero_leakage_assertions(features: dict[str, np.ndarray]) -> dict:
    """Machine check that no feature is a re-badged catalogue distance field."""
    out = {}
    for k, v in features.items():
        out[k] = dict(min=float(np.nanmin(v)), max=float(np.nanmax(v)),
                      nan=int(np.count_nonzero(~np.isfinite(v))),
                      frac_zero=float(np.mean(np.asarray(v) == 0.0)))
    return out
