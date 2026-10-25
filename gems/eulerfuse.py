"""EULERFUSE: catalogue-free joint RTP/gravity contact-source localization.

The lane is pre-registered in ``docs/HYPOTHESES_20261024_EULERFUSE.md``.
This module never reads the mapped-fault catalogue.  It solves the structural-
index N=0 Euler equation in local windows and rasterizes stable inferred source
subcrops.  Catalogue masks are used only by the shared caller for cross-fitting,
holdout construction, and final exclusion.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import (
    distance_transform_edt,
    gaussian_filter,
    maximum_filter,
)

from .hydroconduit import _clean_valid

__all__ = [
    "EulerResult",
    "potential_derivatives",
    "euler_contact_sources",
    "joint_euler_features",
]


@dataclass
class EulerResult:
    """Rasterized stable N=0 source solutions for one potential field."""

    surface: np.ndarray
    depth_px: np.ndarray
    solution_mask: np.ndarray
    n_centres_tested: int
    n_solutions: int
    diagnostics: dict[str, float | int]


def potential_derivatives(
    field: np.ndarray,
    valid: np.ndarray,
    *,
    sigma_px: float = 1.5,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return ``(Fx, Fy, Fz, analytic_strength)`` in pixel-coordinate units.

    ``Fz`` is the upward vertical derivative of a harmonic potential field,
    computed in Fourier space with multiplier ``|k|``.  A smooth validity taper
    suppresses the otherwise unavoidable FFT ringing at the irregular footprint
    edge; callers also exclude a full Euler window around that edge.
    """
    if sigma_px <= 0:
        raise ValueError("sigma_px must be positive")
    f = np.asarray(field, dtype=np.float32)
    raw_valid = np.asarray(valid, dtype=bool)
    if f.ndim != 2 or raw_valid.shape != f.shape:
        raise ValueError("field/valid must be matching nonempty 2-D arrays")
    v = raw_valid & np.isfinite(f) & (f > -1e30)
    if not v.any():
        raise ValueError("field/valid must be matching nonempty 2-D arrays")

    clean = _clean_valid(f, v)
    smooth = gaussian_filter(clean, float(sigma_px), mode="nearest").astype(np.float32)
    fy, fx = np.gradient(smooth)
    fx = fx.astype(np.float32)
    fy = fy.astype(np.float32)

    # Taper to zero only near invalid cells. The interior remains exactly one.
    edge_dist = distance_transform_edt(v).astype(np.float32)
    taper = np.clip(edge_dist / np.float32(max(4.0, 3.0 * sigma_px)), 0.0, 1.0)
    tapered = ((smooth - np.float32(np.median(smooth[v]))) * taper).astype(np.float32)
    h, w = tapered.shape
    ky = (2.0 * np.pi * np.fft.fftfreq(h)).astype(np.float32)[:, None]
    kx = (2.0 * np.pi * np.fft.rfftfreq(w)).astype(np.float32)[None, :]
    k = np.hypot(ky, kx).astype(np.float32)
    spec = np.fft.rfft2(tapered)
    fz = np.fft.irfft2(spec * k, s=tapered.shape).real.astype(np.float32)
    del spec, tapered, smooth, k, kx, ky

    fx[~v] = 0.0
    fy[~v] = 0.0
    fz[~v] = 0.0
    strength = np.sqrt(fx * fx + fy * fy + fz * fz).astype(np.float32)
    strength[~v] = 0.0
    return fx, fy, fz, strength


def _stable_top_centres(
    strength: np.ndarray,
    valid_interior: np.ndarray,
    *,
    quantile: float,
    max_centres: int,
) -> tuple[np.ndarray, np.ndarray, float]:
    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must lie in (0,1)")
    vals = strength[valid_interior]
    if vals.size == 0:
        raise ValueError("no valid interior pixels")
    threshold = float(np.quantile(vals, quantile))
    # Test local analytic-strength maxima, not every high-gradient pixel. This
    # avoids counting the same broad anomaly hundreds of times.
    local_max = strength >= maximum_filter(strength, size=3, mode="nearest")
    idx = np.flatnonzero(valid_interior & local_max & (strength >= threshold))
    if idx.size > max_centres:
        # Stable mergesort plus flat-index tie break gives deterministic output.
        order = np.argsort(-strength.ravel()[idx], kind="mergesort")[:max_centres]
        idx = idx[order]
    y, x = np.unravel_index(idx, strength.shape)
    return y.astype(np.int32), x.astype(np.int32), threshold


def euler_contact_sources(
    field: np.ndarray,
    valid: np.ndarray,
    *,
    sigma_px: float = 1.5,
    window_radius_px: int = 4,
    strength_quantile: float = 0.70,
    max_centres: int = 300_000,
    min_depth_px: float = 0.5,
    max_depth_px: float = 12.0,
    max_offset_px: float = 5.0,
    residual_scale: float = 0.35,
    batch_size: int = 12_000,
) -> EulerResult:
    """Solve and rasterize moving-window N=0 Euler contact solutions.

    Coordinates are centered in each window before solving, greatly improving
    conditioning. A small trace-scaled ridge stabilizes the 3x3 normal system.
    Solutions must remain near their observation window, have plausible shallow
    depth magnitude, and explain the local Euler equations.  The sign of ``Fz``
    depends on the potential-field convention, so reported depth is ``abs(z0)``.
    """
    if window_radius_px < 2:
        raise ValueError("window_radius_px must be >= 2")
    if not (0 < min_depth_px < max_depth_px) or max_offset_px <= 0:
        raise ValueError("invalid depth/offset gates")
    if max_centres < 1 or batch_size < 1:
        raise ValueError("max_centres and batch_size must be positive")
    if not np.isfinite(residual_scale) or residual_scale <= 0:
        raise ValueError("residual_scale must be positive and finite")

    f = np.asarray(field, dtype=np.float32)
    raw_valid = np.asarray(valid, dtype=bool)
    if f.ndim != 2 or raw_valid.shape != f.shape:
        raise ValueError("field/valid must be matching 2-D arrays")
    v = raw_valid & np.isfinite(f) & (f > -1e30)
    fx, fy, fz, strength = potential_derivatives(f, v, sigma_px=sigma_px)
    interior = v & (distance_transform_edt(v) > float(window_radius_px + 2))
    cy, cx, threshold = _stable_top_centres(
        strength, interior, quantile=strength_quantile, max_centres=max_centres
    )

    r = int(window_radius_px)
    dy, dx = np.mgrid[-r : r + 1, -r : r + 1]
    dyf = dy.ravel().astype(np.float32)
    dxf = dx.ravel().astype(np.float32)
    nwin = int(dxf.size)

    out_surface = np.zeros(v.shape, dtype=np.float32)
    out_depth = np.zeros(v.shape, dtype=np.float32)
    out_solution = np.zeros(v.shape, dtype=bool)
    accepted_residuals: list[np.ndarray] = []
    accepted_conditions: list[np.ndarray] = []
    accepted_depths: list[np.ndarray] = []

    for start in range(0, cy.size, int(batch_size)):
        stop = min(start + int(batch_size), cy.size)
        yy = cy[start:stop, None] + dyf.astype(np.int32)[None, :]
        xx = cx[start:stop, None] + dxf.astype(np.int32)[None, :]
        ax = fx[yy, xx].astype(np.float64)
        ay = fy[yy, xx].astype(np.float64)
        az = fz[yy, xx].astype(np.float64)
        rhs = ax * dxf[None, :] + ay * dyf[None, :]

        m11 = np.einsum("ij,ij->i", ax, ax)
        m22 = np.einsum("ij,ij->i", ay, ay)
        m33 = np.einsum("ij,ij->i", az, az)
        m12 = np.einsum("ij,ij->i", ax, ay)
        m13 = np.einsum("ij,ij->i", ax, az)
        m23 = np.einsum("ij,ij->i", ay, az)
        b1 = np.einsum("ij,ij->i", ax, rhs)
        b2 = np.einsum("ij,ij->i", ay, rhs)
        b3 = np.einsum("ij,ij->i", az, rhs)

        n = stop - start
        normal = np.empty((n, 3, 3), dtype=np.float64)
        normal[:, 0, 0], normal[:, 1, 1], normal[:, 2, 2] = m11, m22, m33
        normal[:, 0, 1] = normal[:, 1, 0] = m12
        normal[:, 0, 2] = normal[:, 2, 0] = m13
        normal[:, 1, 2] = normal[:, 2, 1] = m23
        trace = m11 + m22 + m33
        ridge = np.maximum(trace * 1e-6 / 3.0, 1e-12)
        normal[:, 0, 0] += ridge
        normal[:, 1, 1] += ridge
        normal[:, 2, 2] += ridge
        rhs_n = np.column_stack((b1, b2, b3))

        eig = np.linalg.eigvalsh(normal)
        cond_ratio = np.clip(eig[:, 0] / np.maximum(eig[:, -1], 1e-20), 0.0, 1.0)
        sol = np.linalg.solve(normal, rhs_n[..., None])[..., 0]
        pred = ax * sol[:, 0, None] + ay * sol[:, 1, None] + az * sol[:, 2, None]
        mse = np.mean((pred - rhs) ** 2, axis=1)
        scale = np.mean(rhs * rhs, axis=1) + 1e-12
        rel_resid = mse / scale
        depth = np.abs(sol[:, 2])
        offset = np.hypot(sol[:, 0], sol[:, 1])

        keep = (
            np.isfinite(sol).all(axis=1)
            & (depth >= float(min_depth_px))
            & (depth <= float(max_depth_px))
            & (offset <= float(max_offset_px))
            & (rel_resid <= 2.0)
            & (cond_ratio >= 1e-5)
        )
        if not np.any(keep):
            continue

        target_y = np.rint(cy[start:stop][keep] + sol[keep, 1]).astype(np.int32)
        target_x = np.rint(cx[start:stop][keep] + sol[keep, 0]).astype(np.int32)
        in_bounds = (
            (target_y >= 0) & (target_y < v.shape[0])
            & (target_x >= 0) & (target_x < v.shape[1])
        )
        target_y, target_x = target_y[in_bounds], target_x[in_bounds]
        if target_y.size == 0:
            continue
        rr = rel_resid[keep][in_bounds]
        cc = cond_ratio[keep][in_bounds]
        dd = depth[keep][in_bounds]
        src_strength = strength[cy[start:stop][keep][in_bounds], cx[start:stop][keep][in_bounds]]
        local_scale = max(threshold, 1e-12)
        amp = np.tanh(src_strength / local_scale)
        depth_gate = np.exp(-0.5 * ((dd - 4.0) / 4.0) ** 2)
        score = (
            amp
            * np.exp(-rr / float(residual_scale))
            * np.sqrt(np.clip(cc / 0.02, 0.0, 1.0))
            * depth_gate
        ).astype(np.float32)

        flat = np.ravel_multi_index((target_y, target_x), v.shape)
        # Keep the depth associated with the strongest vote at each target.
        order = np.argsort(score, kind="mergesort")
        for j in order:
            iy, ix = int(target_y[j]), int(target_x[j])
            if score[j] >= out_surface[iy, ix]:
                out_surface[iy, ix] = score[j]
                out_depth[iy, ix] = np.float32(dd[j])
                out_solution[iy, ix] = True
        accepted_residuals.append(rr.astype(np.float32))
        accepted_conditions.append(cc.astype(np.float32))
        accepted_depths.append(dd.astype(np.float32))
        del ax, ay, az, rhs, normal, rhs_n, eig, sol, pred, flat

    # Turn point solutions into a narrow, continuous source-stability field.
    out_surface = maximum_filter(out_surface, size=3, mode="nearest")
    out_surface = gaussian_filter(out_surface, 0.8, mode="nearest").astype(np.float32)
    maxv = float(out_surface[v].max()) if v.any() else 0.0
    if maxv > 0:
        out_surface /= np.float32(maxv)
    out_surface[~v] = 0.0
    out_depth[~v] = 0.0

    if accepted_depths:
        all_d = np.concatenate(accepted_depths)
        all_r = np.concatenate(accepted_residuals)
        all_c = np.concatenate(accepted_conditions)
        diag: dict[str, float | int] = {
            "strength_threshold": threshold,
            "median_depth_px": float(np.median(all_d)),
            "median_relative_residual": float(np.median(all_r)),
            "median_condition_ratio": float(np.median(all_c)),
            "window_pixels": nwin,
        }
    else:
        diag = {
            "strength_threshold": threshold,
            "median_depth_px": 0.0,
            "median_relative_residual": 0.0,
            "median_condition_ratio": 0.0,
            "window_pixels": nwin,
        }
    return EulerResult(
        surface=out_surface,
        depth_px=out_depth,
        solution_mask=out_solution,
        n_centres_tested=int(cy.size),
        n_solutions=int(out_solution.sum()),
        diagnostics=diag,
    )


def joint_euler_features(
    rtp: np.ndarray,
    gravity: np.ndarray,
    depth_to_base: np.ndarray,
    footprint: np.ndarray,
    *,
    sigma_px: float = 1.5,
    window_radius_px: int = 4,
    strength_quantile: float = 0.70,
    max_centres: int = 300_000,
) -> dict[str, np.ndarray | EulerResult | dict[str, int | float]]:
    """Build six catalogue-free RTP/gravity Euler features in ``[0,1]``."""
    fp = np.asarray(footprint, dtype=bool)
    rtp_arr = np.asarray(rtp, dtype=np.float32)
    gravity_arr = np.asarray(gravity, dtype=np.float32)
    base = np.asarray(depth_to_base, dtype=np.float32)
    if fp.ndim != 2 or any(a.shape != fp.shape for a in (rtp_arr, gravity_arr, base)):
        raise ValueError("all feature arrays and footprint must share one 2-D shape")
    valid = (
        fp
        & np.isfinite(rtp_arr) & (rtp_arr > -1e30)
        & np.isfinite(gravity_arr) & (gravity_arr > -1e30)
    )
    mag = euler_contact_sources(
        rtp_arr, valid, sigma_px=sigma_px, window_radius_px=window_radius_px,
        strength_quantile=strength_quantile, max_centres=max_centres,
    )
    grav = euler_contact_sources(
        gravity_arr, valid, sigma_px=sigma_px, window_radius_px=window_radius_px,
        strength_quantile=strength_quantile, max_centres=max_centres,
    )

    m_near = maximum_filter(mag.surface, size=7, mode="nearest")
    g_near = maximum_filter(grav.surface, size=7, mode="nearest")
    coloc = np.sqrt(np.maximum(mag.surface * g_near, grav.surface * m_near)).astype(np.float32)

    md = maximum_filter(mag.depth_px, size=7, mode="nearest")
    gd = maximum_filter(grav.depth_px, size=7, mode="nearest")
    both = (md > 0) & (gd > 0)
    depth_agree = np.zeros(fp.shape, dtype=np.float32)
    depth_agree[both] = np.exp(-np.abs(md[both] - gd[both]) / 3.0).astype(np.float32)
    joint = (coloc * (0.35 + 0.65 * depth_agree)).astype(np.float32)

    base_depth_px = np.maximum(np.abs(base) / 100.0, 0.25)
    e_depth = np.where(gd > 0, gd, md)
    base_consistency = np.zeros(fp.shape, dtype=np.float32)
    has = valid & (e_depth > 0) & np.isfinite(base_depth_px)
    base_consistency[has] = np.exp(
        -np.abs(np.log1p(e_depth[has]) - np.log1p(base_depth_px[has])) / 1.25
    ).astype(np.float32)
    base_joint = (joint * (0.4 + 0.6 * base_consistency)).astype(np.float32)

    for arr in (m_near, g_near, coloc, depth_agree, joint, base_consistency, base_joint):
        arr[~valid] = 0.0
        np.clip(arr, 0.0, 1.0, out=arr)
    return {
        "valid": valid,
        "mag_euler": mag.surface,
        "grav_euler": grav.surface,
        "joint_colocation": coloc,
        "depth_agreement": depth_agree,
        "base_consistency": base_consistency,
        "joint_euler": base_joint,
        "mag_result": mag,
        "grav_result": grav,
        "diagnostics": {
            "mag_centres_tested": mag.n_centres_tested,
            "mag_solutions": mag.n_solutions,
            "grav_centres_tested": grav.n_centres_tested,
            "grav_solutions": grav.n_solutions,
        },
    }
