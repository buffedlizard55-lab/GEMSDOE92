"""RELAYGAP — catalogue-tip relay-gap detector (catalogue-free except for geometry).

Hypothesis: relay breaching faults between en echelon normal fault tips host
a large fraction of Great Basin geothermal systems but are omitted from the
catalogue, which maps through-going masters. They sit 0.3–5 km from masters,
share regional strike, and lack a Quaternary scarp until they breach.

Fast implementation: tip-density via Gaussian smoothing (O(HW log HW)),
masked to the inter-fault halo (2 < d_cat <= 60 px). High tip density
marks relay/transfer zones where multiple strands terminate in <4 km.

Non-fault mimic: collinear lithologic contacts / Lahontan shoreline gaps
between range fronts that align by chance.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

STRUCT8 = np.ones((3, 3), bool)
CAP_PX = 60.0  # 6 km search radius for tip-gap context
SIG_GAP = 1.5  # smoothing for gap-score halo

def _endpoints_and_components(mask: np.ndarray):
    """Endpoints (degree 1) and 8-connected components of a thin fault mask."""
    m = np.asarray(mask, bool)
    nb = ndi.convolve(m.astype(np.uint8), np.ones((3,3),np.uint8), mode="constant") - m.astype(np.int32)
    ep = m & (nb == 1)
    ep |= m & (nb == 0)  # isolated pixels
    labels, n_comp = ndi.label(m, structure=STRUCT8)
    return ep, labels, n_comp

def relay_gap_score(catalogue_visible: np.ndarray, footprint: np.ndarray, *, use_strike_weight: bool = True, sigma_px: float = 8.0) -> np.ndarray:
    """Compute relay-gap score S from *visible* catalogue via tip density.

    Parameters
    ----------
    catalogue_visible : bool array (H, W)
    footprint : bool array (H, W)
    use_strike_weight : bool
        If True, modulate by local strike variance (low coherence = relay).
    sigma_px : float
        Gaussian sigma for tip density (8 px = 800 m captures relay width).

    Returns
    -------
    score : float32 (H, W), zero outside footprint, 0 on visible catalogue
    """
    vis = np.asarray(catalogue_visible, bool) & np.asarray(footprint, bool)
    fp = np.asarray(footprint, bool)
    h, w = vis.shape
    if not vis.any():
        return np.zeros((h, w), dtype=np.float32)

    ep, labels, n_comp = _endpoints_and_components(vis)
    if not ep.any():
        return np.zeros((h, w), dtype=np.float32)

    # Tip density: Gaussian halo around endpoints (relay zones have many tips/km)
    tip_density = ndi.gaussian_filter(ep.astype(np.float32), sigma=float(sigma_px), mode="constant", cval=0.0)

    # Mask to halo where a new relay can be placed: 2 < d_cat <= 60 px (0.2–6 km off master)
    from scipy.ndimage import distance_transform_edt
    d_cat = distance_transform_edt(~vis)
    halo = fp & (d_cat > 2.0) & (d_cat <= CAP_PX) & (tip_density > 0)
    if not halo.any():
        return np.zeros((h, w), dtype=np.float32)

    score = np.zeros((h, w), dtype=np.float32)
    score[halo] = tip_density[halo]

    # Strike-variance gate (optional): in relay zones, local fault strike variance is high
    if use_strike_weight:
        dens = ndi.gaussian_filter(vis.astype(np.float32), sigma=6.0, mode="constant", cval=0.0)
        gy, gx = np.gradient(dens)
        a = ndi.gaussian_filter(gy * gy, sigma=6.0, mode="constant", cval=0.0)
        b = ndi.gaussian_filter(gy * gx, sigma=6.0, mode="constant", cval=0.0)
        c_ = ndi.gaussian_filter(gx * gx, sigma=6.0, mode="constant", cval=0.0)
        tr = a + c_
        coh = np.sqrt(np.maximum((a - c_)**2 + 4*b*b, 0)) / np.maximum(tr, 1e-12)
        coh = np.clip(coh, 0, 1).astype(np.float32)
        w = (0.5 + 0.5 * (1.0 - coh)).astype(np.float32)
        score[halo] *= w[halo]

    vals = score[halo]
    lo, hi = np.percentile(vals, [2, 98])
    if hi > lo:
        score = np.clip((score - lo) / (hi - lo), 0, 1).astype(np.float32)
    else:
        score[halo] = 1.0
    score[~fp] = 0
    score[vis] = 0
    score = ndi.gaussian_filter(score, sigma=SIG_GAP, mode="constant", cval=0.0).astype(np.float32)
    score[~fp] = 0
    score[vis] = 0
    return score.astype(np.float32)

def greedy_emit(surface: np.ndarray, footprint: np.ndarray, catalogue_visible: np.ndarray, n_dots: int = 37654, min_spacing_px: float = 2.8, d_cat_min_px: float = 2.0, d_cat_max_px: float = 60.0):
    """Greedy emit on *surface* respecting spacing and catalogue distance."""
    fp = np.asarray(footprint, bool)
    vis = np.asarray(catalogue_visible, bool)
    surf = np.asarray(surface, dtype=np.float32)
    from scipy.ndimage import distance_transform_edt
    dist_cat = distance_transform_edt(~vis)
    allowed = fp & (dist_cat > d_cat_min_px) & (dist_cat <= d_cat_max_px) & np.isfinite(surf)
    allowed &= np.isfinite(surf)
    ys, xs = np.nonzero(allowed)
    if len(ys) == 0:
        raise ValueError("no allowed pixels for emission; check footprint/catalogue")
    scores = surf[ys, xs].astype(float)
    order = np.lexsort((xs, ys, -scores))
    ys, xs, scores = ys[order], xs[order], scores[order]
    selected_ys = []
    selected_xs = []
    # Use cKDTree for spacing check O(N log N) instead of O(N^2) brute force
    # We'll incrementally build tree but query efficiently via vectorized distance check
    # Simpler: maintain grid of occupied cells with inhibition radius via binary dilation mask
    # For 2.8 px, we can use a boolean inhibition mask dilated by 2 px kernel.
    # But to keep exact Euclidean, we use tree.
    from scipy.spatial import cKDTree
    # We'll use incremental but with periodic rebuild: maintain list, query via tree each time is O(N) if we rebuild each time.
    # Instead we can pre-select in order and use inhibition mask: faster.
    # Use inhibition mask approach: maintain a boolean mask 'blocked' where selected dots inhibit within 2.8 px.
    # This is equivalent to greedy with Euclidean spacing if we dilate exactly.
    # We'll implement fast grid inhibition via binary dilation with exact Euclidean kernel.
    h, w = fp.shape
    blocked = np.zeros((h, w), dtype=bool)
    # Precompute inhibition kernel for 2.8 px (ceil 3)
    # Create disk of radius 2.8 px
    r = 2.8
    rad = int(np.ceil(r))
    yy, xx = np.ogrid[-rad:rad+1, -rad:rad+1]
    disk = (yy*yy + xx*xx) <= r*r
    for y, x, s in zip(ys, xs, scores):
        if len(selected_ys) >= n_dots:
            break
        if blocked[y, x]:
            continue
        selected_ys.append(int(y))
        selected_xs.append(int(x))
        # mark inhibition
        y0 = max(0, y - rad); y1 = min(h, y + rad + 1)
        x0 = max(0, x - rad); x1 = min(w, x + rad + 1)
        dy0 = y0 - (y - rad); dy1 = dy0 + (y1 - y0)
        dx0 = x0 - (x - rad); dx1 = dx0 + (x1 - x0)
        blocked[y0:y1, x0:x1] |= disk[dy0:dy1, dx0:dx1]
    if len(selected_ys) < n_dots:
        print(f"WARNING: only {len(selected_ys)}/{n_dots} dots emitted; relaxing to 2.0 px")
        # relax to 2.0 px for remaining
        r2 = 2.0
        rad2 = int(np.ceil(r2))
        yy2, xx2 = np.ogrid[-rad2:rad2+1, -rad2:rad2+1]
        disk2 = (yy2*yy2 + xx2*xx2) <= r2*r2
        # rebuild blocked with 2.0 for remaining (keep existing selections)
        # For remaining, check 2.0 not 2.8
        blocked2 = np.zeros((h,w), dtype=bool)
        for y,x in zip(selected_ys, selected_xs):
            y0 = max(0, y - rad2); y1 = min(h, y + rad2 + 1)
            x0 = max(0, x - rad2); x1 = min(w, x + rad2 + 1)
            dy0 = y0 - (y - rad2); dy1 = dy0 + (y1 - y0)
            dx0 = x0 - (x - rad2); dx1 = dx0 + (x1 - x0)
            blocked2[y0:y1, x0:x1] |= disk2[dy0:dy1, dx0:dx1]
        for y, x, s in zip(ys, xs, scores):
            if len(selected_ys) >= n_dots:
                break
            if blocked2[y, x]:
                continue
            if (int(y), int(x)) in zip(selected_ys, selected_xs):
                continue
            selected_ys.append(int(y)); selected_xs.append(int(x))
            y0 = max(0, y - rad2); y1 = min(h, y + rad2 + 1)
            x0 = max(0, x - rad2); x1 = min(w, x + rad2 + 1)
            dy0 = y0 - (y - rad2); dy1 = dy0 + (y1 - y0)
            dx0 = x0 - (x - rad2); dx1 = dx0 + (x1 - x0)
            blocked2[y0:y1, x0:x1] |= disk2[dy0:dy1, dx0:dx1]
        blocked = blocked2
    if len(selected_ys) < n_dots:
        print(f"WARNING: still only {len(selected_ys)}/{n_dots} dots after relax")
    return np.array(selected_ys, dtype=int), np.array(selected_xs, dtype=int), np.array([surf[y,x] for y,x in zip(selected_ys, selected_xs)], dtype=float)
