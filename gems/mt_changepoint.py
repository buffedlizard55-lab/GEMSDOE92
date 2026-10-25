"""MT-CHANGEPOINT lane: Magnetotelluric conductive conduit & basement changepoint detection.

Pre-registered in docs/HYPOTHESES_20261025_MT_CHANGEPOINT.md.

Geology & Physical Signature
----------------------------
In Basin and Range extensional and transtensional geothermal systems (e.g.,
Dixie Valley, Brady's, San Emidio, Steamboat), deep convective circulation of
saline hydrothermal fluids produces clay-alteration caps (smectite, illite,
chlorite) that exhibit high electrical conductivity in magnetotelluric (MT)
surveys (Band 17, cond_surf).

A fault zone cutting through the crust creates a sharp lateral boundary:
conductive hydrothermal fluid and altered gouge juxtapose resistive,
impermeable basement rock. This manifests as a steep spatial changepoint
(directional gradient magnitude normalized by local standard deviation) in MT
conductivity.

Crucially, non-fault evaporite playas (e.g. Humboldt and Carson Sinks) also
display high surface conductivity. True geothermal fault conduits are distinguished
from passive lacustrine playas by:
1. Directional alignment / concordance between the MT conductivity changepoint
   and the subsurface basement step-edge (Band 15, depth_to_base_surf gradient).
2. Proximity to basement fault scarps and gravity vertical gradient anomalies
   (Band 11, iso_grav_anom_vg) reflecting silica/calcite mineral self-sealing.
3. Topographic / basement slope suppression to downweight flat, deep playa floors.

Mathematical formulation:
- G_mt = ||grad(log(1 + cond))||_2
- Local std: sigma_mt = sqrt(E[(x - mu)^2]) over 7x7 px window
- Changepoint ratio: CP_mt = G_mt / (sigma_mt + eps)
- G_base = ||grad(DoG(depth_to_base, 4px, 20px))||_2
- Concordance: cos_theta = |g_mt . g_base| / (||g_mt|| * ||g_base|| + eps)
- Playa downweight: W_playa = 1.0 - clip(pct(cond) * (1 - pct(G_base)), 0, 1)^1.5
- Coincidence: S = pct( CP_mt * cos_theta * pct(G_base) * (0.35 + 0.65 * pct(|grav_vg|)) * W_playa )

Zero-leakage invariant: no fault-catalogue array is ever passed to this module.
All calculations are strictly physical transformations of geophysics bands.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter, uniform_filter

from .breakline import percentile_rank
from .gravquad import clean

__all__ = [
    "BAND",
    "compute_mt_changepoint_surfaces",
]

# 1-based bands in training_features.tif
BAND = dict(
    iso_grav_vg=11,     # iso_grav_anom_vg - Isostatic gravity anomaly vertical gradient
    depth_to_base=15,   # depth_to_base_surf - Depth to basement surface
    cond_surf=17,       # cond_surf - Conductivity surface (MT)
    det_elev_slope=19,  # det_elev_slope - Detrended elevation slope
)


def _grad(a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute spatial gradient components and Euclidean magnitude."""
    gy, gx = np.gradient(a)
    mag = np.hypot(gx, gy)
    return gx, gy, mag


def compute_mt_changepoint_surfaces(
    cond_surf: np.ndarray,
    depth_to_base: np.ndarray,
    iso_grav_vg: np.ndarray,
    det_elev_slope: np.ndarray,
    footprint: np.ndarray,
    edge_erode_px: int = 24,
) -> dict[str, np.ndarray]:
    """Build MT-Changepoint coincidence and ablation surfaces on the valid grid."""
    foot = np.asarray(footprint, bool)
    
    # Valid mask with edge erosion to prevent boundary gradient artifacts
    from scipy.ndimage import binary_erosion
    valid = binary_erosion(foot, iterations=edge_erode_px)
    
    # 1. MT log-conductivity and local changepoint
    log_cond = np.log1p(np.maximum(clean(cond_surf, foot), 0.0))
    gx_mt, gy_mt, g_mt = _grad(log_cond)
    
    # Local standard deviation of log-conductivity via uniform filter
    win_size = 7
    mean_cond = uniform_filter(log_cond, size=win_size)
    mean_cond_sq = uniform_filter(log_cond ** 2, size=win_size)
    var_cond = np.maximum(mean_cond_sq - mean_cond ** 2, 0.0)
    std_cond = np.sqrt(var_cond)
    
    cp_mt = g_mt / (std_cond + np.nanmedian(std_cond[valid]) * 0.1 + 1e-6)
    cp_mt_pct = percentile_rank(cp_mt, valid)
    
    # 2. Basement DoG gradient (band-pass filter 4 px to 20 px)
    base_clean = clean(depth_to_base, foot)
    dog_base = gaussian_filter(base_clean, 4.0) - gaussian_filter(base_clean, 20.0)
    gx_base, gy_base, g_base = _grad(dog_base)
    g_base_pct = percentile_rank(g_base, valid)
    
    # 3. Directional concordance between MT changepoint and basement step
    denom = (g_mt * g_base) + 1e-8
    cos_theta = np.abs(gx_mt * gx_base + gy_mt * gy_base) / denom
    cos_theta = np.clip(cos_theta, 0.0, 1.0)
    
    # 4. Playa deconfounding: high conductivity with flat/low basement gradient
    pct_cond = percentile_rank(log_cond, valid)
    playa_risk = np.clip(pct_cond * (1.0 - g_base_pct), 0.0, 1.0) ** 1.5
    w_playa = 1.0 - 0.70 * playa_risk
    
    # 5. Gravity vertical gradient coupling
    grav_vg_clean = np.abs(clean(iso_grav_vg, foot))
    grav_vg_pct = percentile_rank(grav_vg_clean, valid)
    
    # Surface 1: Full MTCP coincidence
    raw_mtcp = cp_mt_pct * cos_theta * g_base_pct * (0.35 + 0.65 * grav_vg_pct) * w_playa
    S_mtcp = percentile_rank(raw_mtcp, valid)
    
    # Surface 2: MT alone ablation (pure changepoint ratio, no basement/grav)
    S_mt = cp_mt_pct
    
    # Surface 3: Basement x Gravity ablation (no MT)
    raw_base_grav = g_base_pct * (0.35 + 0.65 * grav_vg_pct)
    S_base_grav = percentile_rank(raw_base_grav, valid)
    
    return {
        "valid": valid,
        "S_mtcp": S_mtcp,
        "S_mt": S_mt,
        "S_base_grav": S_base_grav,
        "cp_mt": cp_mt,
        "cp_mt_pct": cp_mt_pct,
        "g_base_pct": g_base_pct,
        "cos_theta": cos_theta,
        "w_playa": w_playa,
        "grav_vg_pct": grav_vg_pct,
    }
