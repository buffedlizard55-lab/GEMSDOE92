"""SCARPDIPOLE lane surface: Hanks-Bucknam-Wallace scarp-diffusion profile-curvature dipole.

Geological & Geomorphic Mechanism
---------------------------------
Under linear topographic hillslope diffusion ``dz/dt = kappa * laplacian(z)``
(Wallace, 1977, GSA Bull. 88:1267-1281; Bucknam & Anderson, 1979, Geology 7:11-14;
Hanks, Bucknam, Lajoie & Wallace, 1984, JGR 89:5771-5790), a normal-fault scarp
offsetting unconsolidated Basin-and-Range alluvium, piedmont bajada gravels, or
homogeneous volcanic sheets evolves toward an antisymmetric error-function step
``z(s) ~ -erf(s / sqrt(4 * kappa * t))`` along the local downslope coordinate
``s`` (unit vector ``s_hat = -grad(z) / ||grad(z)||``):

1. Upslope of the fault trace (``s < 0``, scarp crest), profile curvature along
   downslope ``z_ss = s_hat^T H(z) s_hat`` is **negative** (convex).
2. Downslope of the fault trace (``s > 0``, colluvial wedge / scarp toe),
   ``z_ss`` is **positive** (concave).
3. Directly on the **fault trace midpoint (``s = 0``)**, ``z_ss`` passes through
   **zero** with a strictly **positive downslope third derivative**
   ``dz_ss/ds = s_hat . grad(z_ss) > 0``, while along-strike curvature
   ``|z_tt| = |t_hat^T H(z) t_hat|`` (``t_hat`` perpendicular to ``s_hat``)
   remains small on laterally continuous fault strands.

How this differs from BREAKLINE and prior lanes in GEMSDOE92
------------------------------------------------------------
- Every H19-5 skeleton lane (R0, MASS, PRUNE, SNAP, CONCENTRATION, RELIEF,
  DILATATION) restricts emission to the potential-field worm skeleton, missing
  faults that juxtapose identical volcanic or alluvial lithologies (zero
  magnetic/gravity contrast) and violating the 70% 3-px uniqueness gate when
  kept > 70% on R0.
- ``BREAKLINE`` (``gems/breakline.py``) used unsigned ``||grad(det_elev_slope)||``
  across the entire elevation range. ``||grad(slope)||`` peaks TWICE on a fault
  scarp (at crest and toe, offset from the fault trace), fires equally on
  single-sided erosional/lacustrine cliffs without a paired convex-concave
  scarp dipole, and places large fractions of off-skeleton mass on high alpine
  bedrock ridgelines (>p85 of detrended elevation).
- ``SCARPDIPOLE`` detects the directional **convex-crest -> concave-toe zero-crossing**
  right on the scarp midpoint across ``sigma in {1.0, 2.0}`` px (100 m and 200 m),
  penalizes along-strike planform bending ``|z_tt|``, conditions on structure-tensor
  orientation coherence and ``sqrt(pct_rank(det_elev_slope))``, and applies a
  Basin-and-Range piedmont-to-range-front morphometric habitat envelope
  (``[p15, p85]`` of ``Band 12 det_elev``) that suppresses flat playa mudflats
  (``< p15``) and extreme alpine ridgelines (``> p85``).
- Furthermore, ``SCARPDIPOLE`` re-ranks **both** the on-skeleton ``H19-5`` share
  (recovering piedmont scarp-corroborated ``H19-5`` strands dropped by R0's
  arbitrary scan-order thinning) **and** the off-skeleton ``d_H19 > 3.0 px``
  share under one single label-free surface ``S``.

Zero catalogue pixels or labels ever enter ``scarpdipole_surface``.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from gems.breakline import percentile_rank, structure_tensor_coherence

DIPOLE_SIGMAS_PX: tuple[float, ...] = (1.0, 2.0)
PIEDMONT_Q_LOW: float = 15.0
PIEDMONT_Q_HIGH: float = 85.0
OUTSIDE_HABITAT_WEIGHT: float = 0.45


def grad32(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Second-order central differences in float32 (half the memory of np.gradient)."""
    a = np.asarray(a, dtype=np.float32)
    gy = np.empty_like(a, dtype=np.float32)
    gx = np.empty_like(a, dtype=np.float32)
    gy[1:-1] = 0.5 * (a[2:] - a[:-2])
    gy[0] = a[1] - a[0]
    gy[-1] = a[-1] - a[-2]
    gx[:, 1:-1] = 0.5 * (a[:, 2:] - a[:, :-2])
    gx[:, 0] = a[:, 1] - a[:, 0]
    gx[:, -1] = a[:, -1] - a[:, -2]
    return gy, gx


def _clean_median(a: np.ndarray, valid: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    m = np.asarray(valid, bool) & np.isfinite(a)
    fill = float(np.median(a[m])) if m.any() else 0.0
    return np.where(m, a, np.float32(fill)).astype(np.float32)


def scarp_profile_dipole(det_elev: np.ndarray, valid: np.ndarray,
                         sigmas: tuple[float, ...] = DIPOLE_SIGMAS_PX) -> np.ndarray:
    """Multi-scale convex-crest -> concave-toe profile-curvature dipole zero-crossing."""
    valid = np.asarray(valid, bool)
    if not sigmas:
        raise ValueError("sigmas must be non-empty")
    zc = _clean_median(det_elev, valid)
    acc = np.zeros(zc.shape, dtype=np.float32)
    w_scale = np.float32(1.0 / len(sigmas))
    for sig in sigmas:
        z = gaussian_filter(zc, float(sig))
        zy, zx = grad32(z)
        gnorm = np.hypot(zy, zx) + np.float32(1e-6)
        # Unit vector pointing downslope: s_hat = -grad(z) / ||grad(z)||
        dy_dn = (-zy / gnorm).astype(np.float32)
        dx_dn = (-zx / gnorm).astype(np.float32)
        # Unit vector along strike (perpendicular to s_hat)
        ty, tx = -dx_dn, dy_dn
        zyy, zyx = grad32(zy)
        zxy, zxx = grad32(zx)
        h_xy = np.float32(0.5) * (zyx + zxy)
        # Second directional derivative along downslope (convex < 0, concave > 0)
        z_ss = dy_dn * dy_dn * zyy + np.float32(2.0) * dy_dn * dx_dn * h_xy + dx_dn * dx_dn * zxx
        # Second directional derivative along strike (planform bending proxy)
        z_tt = ty * ty * zyy + np.float32(2.0) * ty * tx * h_xy + tx * tx * zxx
        zss_y, zss_x = grad32(z_ss)
        # Positive jump from upslope convex crest (z_ss < 0) to downslope concave toe (z_ss > 0)
        dipole_jump = np.maximum(np.float32(0.0), dy_dn * zss_y + dx_dn * zss_x)
        abs_zss = np.abs(z_ss[valid])
        zss_scale = np.float32((float(np.percentile(abs_zss, 75.0)) if abs_zss.size else 1.0) + 1e-6)
        zc_weight = np.exp(np.float32(-0.5) * (z_ss / zss_scale) ** 2).astype(np.float32)
        lin_weight = dipole_jump / (dipole_jump + np.abs(z_tt) + np.float32(1e-6))
        acc += w_scale * percentile_rank(dipole_jump * zc_weight * lin_weight, valid)
    return acc.astype(np.float32)


def piedmont_range_envelope(det_elev: np.ndarray, valid: np.ndarray,
                            q_low: float = PIEDMONT_Q_LOW,
                            q_high: float = PIEDMONT_Q_HIGH,
                            outside_weight: float = OUTSIDE_HABITAT_WEIGHT) -> tuple[np.ndarray, tuple[float, float]]:
    """Basin-and-Range morphometric habitat weight over detrended elevation.

    Active Quaternary and geothermal-controlling normal faults concentrate in the
    piedmont-to-range-front transition ``[p15, p85]`` of detrended elevation,
    whereas deep flat playa centers (``< p15``) and extreme alpine ridge crests
    (``> p85``) are dominated by desiccation/shoreline noise and non-fault cliffs.
    """
    valid = np.asarray(valid, bool) & np.isfinite(det_elev)
    if not valid.any():
        return np.zeros(det_elev.shape, dtype=np.float32), (0.0, 0.0)
    lo, hi = (float(x) for x in np.percentile(det_elev[valid], [q_low, q_high]))
    in_corridor = (det_elev >= lo) & (det_elev <= hi)
    env = np.where(in_corridor, np.float32(1.0), np.float32(outside_weight))
    env = np.where(valid, env, np.float32(0.0)).astype(np.float32)
    return env, (lo, hi)


def scarpdipole_surface(det_elev: np.ndarray, det_elev_slope: np.ndarray,
                        valid: np.ndarray) -> dict[str, np.ndarray | tuple[float, float]]:
    """Compute the label-free SCARPDIPOLE prospectivity surface and diagnostics."""
    elev_f = np.asarray(det_elev, dtype=np.float32)
    slope_f = np.asarray(det_elev_slope, dtype=np.float32)
    # Convert any unmasked GDAL float32 nodata sentinels (<= -1e30) to NaN before smoothing
    elev_safe = np.where(np.isfinite(elev_f) & (elev_f > -1e30), elev_f, np.float32(np.nan))
    slope_safe = np.where(np.isfinite(slope_f) & (slope_f > -1e30), slope_f, np.float32(np.nan))
    valid = np.asarray(valid, bool) & np.isfinite(elev_safe) & np.isfinite(slope_safe)
    dipole_pct = scarp_profile_dipole(elev_safe, valid)
    coherence = structure_tensor_coherence(elev_safe, valid, deriv_sigma=1.0, tensor_sigma=2.0)
    slope_pct = percentile_rank(slope_safe, valid)
    envelope, bounds = piedmont_range_envelope(elev_safe, valid)
    s_raw = (dipole_pct * coherence * np.sqrt(slope_pct) * envelope).astype(np.float32)
    s_pct = percentile_rank(s_raw, valid)
    return {
        "dipole_pct": dipole_pct,
        "coherence": coherence,
        "slope_pct": slope_pct,
        "envelope": envelope,
        "habitat_bounds_m": bounds,
        "S_raw": s_raw,
        "S_pct": s_pct,
    }
