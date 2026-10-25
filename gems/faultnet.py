"""FAULTNET -- fault-network *context* features from the visible catalogue.

Lane hypothesis (pre-registered in docs/HYPOTHESES_20261025_FAULTNET.md)
-----------------------------------------------------------------------
Every supervised LOQO lane in this repository (COULOMBLOQO, KNICKLOQO,
PROVINCETOE, POISSONFLEX, BLINDFAULT) learns *what a fault pixel looks like*
from geophysics/topography alone; none of them uses *where the other mapped
faults are*.  Fault populations are spatially clustered and self-similar:
secondary splays, synthetic/antithetic faults, step-over and accommodation-zone
faults concentrate within ~0.3-5 km of mapped master faults and share the
local strike (Kim, Peacock & Sanderson 2004, J. Struct. Geol. 26:503-517,
https://doi.org/10.1016/j.jsg.2003.08.002; Faulds & Hinz 2015, World
Geothermal Congress, favourable structural settings, step-overs/terminations).
FAULTNET adds five catalogue-network context fields computed **only from the
visible catalogue** to the COULOMBLOQO physical feature stack.

Self-exclusion (the leakage guard that makes this legal)
--------------------------------------------------------
Training positives *are* visible-catalogue pixels, so a naive "distance to
the catalogue" would equal 0 on every positive (feature == label).  Every field
below is therefore evaluated **with the pixel's own 8-connected catalogue
component removed** for pixels lying on the catalogue.  Off-catalogue pixels
(training negatives, holdout truth, deployment candidates) see the whole
visible catalogue -- exactly the situation of an unmapped fault, whose own
trace is by definition absent from the catalogue.

Fields (all float32, full grid):
  cx_logdist    log1p(min(distance to nearest *other* catalogue component, CAP))
  cx_dens10     catalogue density, Gaussian sigma = 10 px (1 km), own removed
  cx_dens40     catalogue density, Gaussian sigma = 40 px (4 km), own removed
  cx_strike     cos^2(topographic-edge normal - regional catalogue normal) x
                regional coherence (sigma = 40 px tensor, own removed)
  cx_logtip     log1p(min(distance to nearest *other* component endpoint, CAP))

The named non-fault process that can mimic these fields: **lithological
contacts and range-front geomorphology that parallel mapped faults** (e.g.
bedding, lava-flow margins, Lake Lahontan shorelines).  The topographic crest
gate and the physical features are what separate them.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

CAP_PX = 60.0
SIG_SMALL = 10.0
SIG_LARGE = 40.0
TRUNCATE = 4.0
STRUCT8 = np.ones((3, 3), bool)

CONTEXT_NAMES: tuple[str, ...] = ("cx_logdist", "cx_dens10", "cx_dens40", "cx_strike", "cx_logtip")

__all__ = ["CONTEXT_NAMES", "context_fields", "endpoints", "own_gaussian_sum",
           "gaussian_density", "self_excluded_distance"]


def _z(sigma: float, truncate: float = TRUNCATE) -> float:
    """1D normaliser used by scipy.ndimage.gaussian_filter (radius = int(truncate*sigma+0.5))."""
    r = int(truncate * float(sigma) + 0.5)
    x = np.arange(-r, r + 1, dtype=np.float64)
    return float(np.exp(-0.5 * (x / sigma) ** 2).sum())


def gaussian_density(mask_or_weights: np.ndarray, sigma: float) -> np.ndarray:
    a = np.asarray(mask_or_weights)
    if a.dtype != np.float32:
        a = a.astype(np.float32)
    return ndi.gaussian_filter(a, sigma, output=np.float32, mode="constant", truncate=TRUNCATE)


def own_gaussian_sum(labels: np.ndarray, sigma: float, weights: np.ndarray | None = None) -> np.ndarray:
    """Exact contribution of each pixel's *own* component to the gaussian_filter sum.

    Reproduces scipy's separable discrete kernel ``w(dy) w(dx) / Z^2`` with the
    same truncation radius, so ``gaussian_density(all) - own`` equals the
    density of the catalogue with the pixel's own component deleted.
    Returns an array (same shape) that is non-zero only on labelled pixels.
    """
    out = np.zeros(labels.shape, np.float32)
    r = int(TRUNCATE * float(sigma) + 0.5)
    z2 = _z(sigma) ** 2
    objs = ndi.find_objects(labels)
    w_full = None if weights is None else np.asarray(weights)
    for lab, sl in enumerate(objs, start=1):
        if sl is None:
            continue
        sub = labels[sl] == lab
        yy, xx = np.nonzero(sub)
        yy = yy + sl[0].start
        xx = xx + sl[1].start
        dy = np.abs(yy[:, None] - yy[None, :])
        dx = np.abs(xx[:, None] - xx[None, :])
        k = np.exp(-0.5 * ((dy / sigma) ** 2 + (dx / sigma) ** 2))
        k[(dy > r) | (dx > r)] = 0.0
        v = np.ones(len(yy)) if w_full is None else w_full[yy, xx].astype(np.float64)
        out[yy, xx] = (k @ v) / z2
    return out


def endpoints(mask: np.ndarray) -> np.ndarray:
    """Skeleton endpoints (exactly one 8-neighbour) of a thin catalogue mask."""
    m = np.asarray(mask, bool)
    nb = ndi.convolve(m.astype(np.uint8), STRUCT8.astype(np.uint8), mode="constant") - m
    ep = m & (nb == 1)
    # isolated single pixels count as endpoints too
    ep |= m & (nb == 0)
    return ep


def self_excluded_distance(targets: np.ndarray, labels: np.ndarray, cap: float = CAP_PX) -> np.ndarray:
    """min(distance to target pixels, cap); on labelled pixels, own-component targets excluded.

    ``targets`` is a boolean mask whose True pixels each belong to a component
    in ``labels`` (e.g. the catalogue itself or its endpoints).
    """
    t = np.asarray(targets, bool)
    d = np.minimum(ndi.distance_transform_edt(~t), cap)
    pad = int(np.ceil(cap)) + 1
    h, w = labels.shape
    for lab, sl in enumerate(ndi.find_objects(labels), start=1):
        if sl is None:
            continue
        y0, y1 = max(0, sl[0].start - pad), min(h, sl[0].stop + pad)
        x0, x1 = max(0, sl[1].start - pad), min(w, sl[1].stop + pad)
        win_lab = labels[y0:y1, x0:x1]
        own = win_lab == lab
        other_t = t[y0:y1, x0:x1] & (win_lab != lab)
        if other_t.any():
            dw = np.minimum(ndi.distance_transform_edt(~other_t), cap)
        else:
            dw = np.full(own.shape, cap)
        d[y0:y1, x0:x1][own] = dw[own]
    return d


def _orient_coh(a, b, c):
    theta = (0.5 * np.arctan2(2.0 * b, a - c)).astype(np.float32)
    tr = a + c
    coh = np.sqrt((a - c) ** 2 + 4.0 * b * b) / np.maximum(tr, 1e-12)
    return theta, np.clip(coh, 0.0, 1.0).astype(np.float32)


def context_fields(catalogue_visible: np.ndarray, det_elev: np.ndarray, valid: np.ndarray) -> dict[str, np.ndarray]:
    """Five self-excluded catalogue-network context fields (see module docstring).

    Memory-lean (float32, temporaries freed) so it fits beside the 24-band
    COULOMBLOQO stack inside the 3 GB sandbox.
    """
    vis = np.asarray(catalogue_visible, bool)
    v = np.asarray(valid, bool)
    labels, _ = ndi.label(vis, STRUCT8)
    out: dict[str, np.ndarray] = {}
    # (1) distance to nearest other component
    out["cx_logdist"] = np.log1p(self_excluded_distance(vis, labels)).astype(np.float32)
    # (2,3) self-excluded densities
    for name, sig in (("cx_dens10", SIG_SMALL), ("cx_dens40", SIG_LARGE)):
        full = gaussian_density(vis, sig)
        full -= own_gaussian_sum(labels, sig)
        np.maximum(full, 0.0, out=full)
        full *= np.float32(1e3)
        out[name] = full
    # (4) regional catalogue strike field (own removed) vs local topographic edges
    vs = ndi.gaussian_filter(vis.astype(np.float32), 1.5)
    gy, gx = np.gradient(vs)
    del vs
    gy[~vis] = 0.0
    gx[~vis] = 0.0
    comps = []
    for wgt in (gx * gx, gx * gy, gy * gy):
        full = gaussian_density(wgt, SIG_LARGE)
        full -= own_gaussian_sum(labels, SIG_LARGE, weights=wgt)
        comps.append(full)
        del wgt
    del gx, gy
    th_reg, coh_reg = _orient_coh(*comps)
    del comps
    de = np.where(np.isfinite(det_elev), det_elev, 0.0).astype(np.float32)
    tgy, tgx = np.gradient(ndi.gaussian_filter(de, 1.5))
    del de
    a = ndi.gaussian_filter(tgx * tgx, 4.0)
    b = ndi.gaussian_filter(tgx * tgy, 4.0)
    c = ndi.gaussian_filter(tgy * tgy, 4.0)
    del tgx, tgy
    th_top, coh_top = _orient_coh(a, b, c)
    del a, b, c
    dth = th_top - th_reg
    del th_top, th_reg
    out["cx_strike"] = (np.cos(dth) ** 2 * coh_reg * np.sqrt(coh_top)).astype(np.float32)
    del dth, coh_reg, coh_top
    # (5) distance to nearest endpoint of another component
    out["cx_logtip"] = np.log1p(self_excluded_distance(endpoints(vis), labels)).astype(np.float32)
    for k in out:
        out[k][~v] = 0.0
    return out
