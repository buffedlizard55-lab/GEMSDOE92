"""TIPCOMP lane (2026-10-28, H-92F1): catalogue tip-continuation field.

Computable from a binary fault-catalogue mask alone, so it is strictly
fold-proper when fed ``fold["visible"]`` (Protocol Rule 2).  For every
catalogue endpoint (exactly one 8-neighbour) the local strike is the
principal axis of catalogue pixels in a square window; an axial Gaussian
ridge is stamped along that axis, suppressed within ``suppress_px`` of the
catalogue so the field never refills the 200 m collar that the fitted
dcat law says is empty (WHY_0_2778.md §2).
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

_STRUCT8 = np.ones((3, 3), dtype=int)


def endpoints(mask: np.ndarray) -> np.ndarray:
    """Boolean mask of degree-1 pixels of a 1px-wide binary trace mask."""
    m = np.asarray(mask, dtype=bool)
    deg = ndi.convolve(m.astype(np.int16), _STRUCT8, mode="constant", cval=0) - m
    return m & (deg == 1)


def tip_continuation_field(
    mask: np.ndarray,
    *,
    window: int = 15,
    length_px: float = 20.0,
    sigma_along: float = 8.0,
    sigma_across: float = 1.5,
    suppress_px: float = 2.2,
) -> np.ndarray:
    """Axial tip-propagation prospectivity in [0, ~1] (float32, full grid).

    Both directions along the endpoint strike are stamped (axial data: a
    buried continuation may extend either way from a compilation break).
    """
    m = np.asarray(mask, dtype=bool)
    H, W = m.shape
    out = np.zeros((H, W), dtype=np.float32)
    rad = int(np.ceil(length_px))
    yy, xx = np.mgrid[-rad : rad + 1, -rad : rad + 1].astype(np.float64)
    rr2 = yy * yy + xx * xx
    half = window // 2
    ep_y, ep_x = np.nonzero(endpoints(m))
    for y0, x0 in zip(ep_y, ep_x):
        ys = slice(max(0, y0 - half), min(H, y0 + half + 1))
        xs = slice(max(0, x0 - half), min(W, x0 + half + 1))
        wy, wx = np.nonzero(m[ys, xs])
        if wy.size < 4:
            continue
        cy = wy - (y0 - ys.start)
        cx = wx - (x0 - xs.start)
        # principal axis (largest eigenvector of the 2x2 covariance)
        syy = float((cy * cy).sum()); sxx = float((cx * cx).sum()); sxy = float((cx * cy).sum())
        theta = 0.5 * np.arctan2(2.0 * sxy, sxx - syy)  # axis angle in (x, y)
        ux, uy = np.cos(theta), np.sin(theta)
        along = xx * ux + yy * uy
        across = -xx * uy + yy * ux
        stamp = np.exp(-0.5 * (along / sigma_along) ** 2 - 0.5 * (across / sigma_across) ** 2)
        stamp[rr2 > length_px ** 2] = 0.0
        tys = slice(max(0, y0 - rad), min(H, y0 + rad + 1))
        txs = slice(max(0, x0 - rad), min(W, x0 + rad + 1))
        sy = slice(tys.start - (y0 - rad), tys.stop - (y0 - rad))
        sx = slice(txs.start - (x0 - rad), txs.stop - (x0 - rad))
        np.maximum(out[tys, txs], stamp[sy, sx].astype(np.float32), out=out[tys, txs])
    if suppress_px > 0:
        d = ndi.distance_transform_edt(~m)
        out[d <= suppress_px] = 0.0
    return out


def coverage_complement(
    ridge_dist: np.ndarray,
    peak_dot_masks: list[np.ndarray],
    *,
    ridge_max_px: float = 2.0,
    gap_min_px: float = 3.0,
) -> np.ndarray:
    """1.0 where a ridge cell is > ``gap_min_px`` from every peak dot.

    ``ridge_dist`` is EDT distance to the H19-5 skeleton.  These are the
    300 m-kernel coverage gaps left by fixed-spacing dotting at bends.
    """
    union = np.zeros(ridge_dist.shape, dtype=bool)
    for pm in peak_dot_masks:
        union |= np.asarray(pm, dtype=bool)
    d_peak = ndi.distance_transform_edt(~union)
    return ((ridge_dist <= ridge_max_px) & (d_peak > gap_min_px)).astype(np.float32)
