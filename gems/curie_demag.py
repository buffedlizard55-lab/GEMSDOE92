"""CURIE-DEMAG lane: multi-scale RTP variance suppression inside MT clay-cap perimeters.

Geology
-------
Geothermal upflow alters titanomagnetite to pyrite/leucoxene above a
conductive smectite clay cap (180-250 °C), creating a narrow magnetic
quiet trough inside volcanic terrains. The trough is bounded laterally
by steep MT resistivity gradients (clay-cap flanks). Blind faults that
host the upflow have no preserved Quaternary scarp and no basalt offset,
but the quiet zone + clay-cap edge is directly visible to airborne
magnetics/MT. The USGS/INGENIOUS catalogue is a scarp catalogue, so
these faults were never mapped.

Surface (pure array math; catalogue is used only by caller for masking):

    var_short   = local variance of B2 RTP in 3x3 window  (300 m)
    var_regional= local variance of B2 RTP in 15x15 window (1500 m)
    R           = var_short / (var_regional + eps)         variance ratio
    suppression = 1 - R                                    quiet-zone score

    grad_log_cond = |grad(log(B17 cond_surf + 1))|         clay-cap flank
    lapl_RTP      = max(0, laplacian(B2 RTP))              demag bowl

    S = pct_rank(suppression) * pct_rank(grad_log_cond) * pct_rank(lapl_RTP)

All ranks are percentile ranks over valid footprint (1001 knots).
GDR wells >=80 C are used only for diagnostic distance weighting
(optional); they do not build the core surface, so catalogue withholding
cannot leak through the surface.

Layers
------
* B2  rtp                (reduced-to-pole magnetic anomaly)
* B14 tmi                (total magnetic intensity, for cross-check)
* B17 cond_surf          (subsurface MT electrical conductivity)
* B11 iso_grav_anom_vg   (isostatic gravity vertical gradient, for context)

Band numbers are 1-based in training_features.tif.
Sentinel for off-footprint is -3.4028235e+38 float32.
"""

from __future__ import annotations

import numpy as np
import rasterio
from scipy.ndimage import uniform_filter, laplace

SENTINEL = -3.4028235e+38

BAND = dict(
    rtp=2,          # reduced-to-pole magnetic
    tmi=14,         # total magnetic intensity
    cond=17,        # MT conductivity
    grav_vg=11,     # gravity vertical gradient (diagnostic)
    grav_iso=13,    # gravity anomaly (context)
)

def read_stack_band(path: str, band: int) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(band).astype(np.float32)
    return a

def clean(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    foot = np.asarray(foot, bool)
    out = a.astype(np.float32, copy=False)
    # off-footprint sentinel will be handled via valid mask
    out[~foot] = 0.0
    return out

def percentile_rank(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    v = np.asarray(valid, bool)
    out = np.zeros(a.shape, dtype=np.float32)
    if not v.any():
        return out
    vals = a[v].astype(np.float64)
    # 1001 knots
    qs = np.linspace(0, 100, 1001)
    knots = np.quantile(vals, qs/100.0)
    # digitize
    idx = np.searchsorted(knots, a, side='right') - 1
    idx = np.clip(idx, 0, 1000)
    pct = idx.astype(np.float32) / 1000.0
    out[v] = pct[v]
    out[~v] = 0.0
    return out

def local_variance(a: np.ndarray, size: int) -> np.ndarray:
    """Local variance via uniform_filter (mean of square - square of mean)."""
    a = a.astype(np.float64)
    # uniform_filter handles edges with reflect; we will mask invalid later
    m = uniform_filter(a, size=size, mode='reflect')
    m2 = uniform_filter(a*a, size=size, mode='reflect')
    var = m2 - m*m
    var = np.maximum(var, 0.0)
    return var.astype(np.float32)

def grad_mag(a: np.ndarray) -> np.ndarray:
    gy, gx = np.gradient(a.astype(np.float64))
    return np.hypot(gy, gx).astype(np.float32)

def lane_surface(stack_path: str, footprint: np.ndarray, gdr_path: str | None = None) -> dict:
    """Build CURIE-DEMAG surface and components.

    Returns dict with keys: valid, suppression, mt_grad, demag, S, plus
    intermediate variances for audit. Nothing reads the fault catalogue.
    """
    foot = np.asarray(footprint, bool)
    rtp = clean(read_stack_band(stack_path, BAND["rtp"]), foot)
    tmi = clean(read_stack_band(stack_path, BAND["tmi"]), foot)
    cond = clean(read_stack_band(stack_path, BAND["cond"]), foot)

    valid = (foot
             & np.isfinite(rtp) & (rtp > SENTINEL + 1e6)
             & np.isfinite(tmi) & (tmi > SENTINEL + 1e6)
             & np.isfinite(cond) & (cond > SENTINEL + 1e6))

    # small diagnostic: ensure foot valid fraction reasonable
    if valid.sum() < 1000:
        raise ValueError("valid footprint too small")

    # local variances of RTP (use float64 for accuracy then cast)
    rtp_valid = np.where(valid, rtp, 0.0).astype(np.float32)
    var3 = local_variance(rtp_valid, size=3)    # 300 m
    var15 = local_variance(rtp_valid, size=15)  # 1500 m

    eps = 1e-6
    # avoid division by zero
    ratio = var3 / (var15 + eps)
    # quiet zone: low short-scale variance vs regional -> ratio ~0 -> suppression ~1
    suppression_raw = 1.0 - np.clip(ratio, 0.0, 1.0)
    suppression_raw[~valid] = 0.0

    # MT clay-cap flank: gradient of log(conductivity+1)
    log_cond = np.log(np.maximum(cond, 0.0) + 1.0).astype(np.float32)
    # mask invalid before gradient to avoid edge bleed; set invalid to 0
    log_cond[~valid] = 0.0
    mt_grad_raw = grad_mag(log_cond)
    mt_grad_raw[~valid] = 0.0

    # demagnetization bowl: positive Laplacian of RTP (bowl = high laplacian)
    # laplace via scipy.ndimage (second derivative sum)
    lap = laplace(rtp_valid.astype(np.float64), mode='reflect').astype(np.float32)
    demag_raw = np.maximum(lap, 0.0)
    demag_raw[~valid] = 0.0

    # percentile ranks over valid
    sup_pct = percentile_rank(suppression_raw, valid)
    mt_pct = percentile_rank(mt_grad_raw, valid)
    demag_pct = percentile_rank(demag_raw, valid)

    # product of ranks (geometric mean)
    S = (sup_pct * mt_pct * demag_pct).astype(np.float32)
    S[~valid] = 0.0

    # optional: weight by proximity to hot wells (>=80C) if gdr_path provided
    # For now return core S; GDR weighting can be applied by caller as scalar

    return dict(
        valid=valid,
        suppression_raw=suppression_raw.astype(np.float32),
        mt_grad_raw=mt_grad_raw.astype(np.float32),
        demag_raw=demag_raw.astype(np.float32),
        suppression=sup_pct,
        mt_grad=mt_pct,
        demag=demag_pct,
        S=S,
        var3=var3,
        var15=var15,
        ratio=ratio.astype(np.float32),
    )
