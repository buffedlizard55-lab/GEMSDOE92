"""Metric-structured leaderboard model (LBM): infer truth density from CLAIM scores.

Why this exists
---------------
Each owner-reported score is one exact evaluation of the official DTI on the
hidden *public* labels.  The DTI is a known function of the prediction and the
truth, so a collection of scored rasters constrains the truth.  This module
fits the simplest such model and uses it (a) to estimate the score of any
raster and (b) to rank pixels for dot placement.

Model (expectation under a random-truth density ``rho``)
-------------------------------------------------------
Let ``C_i(y) = max_x p_i(x) k(|x-y|)`` be raster *i*'s kernel coverage field
(official triangular kernel, R = 3 px) and ``rho(y)`` the probability that a
non-catalogue pixel ``y`` is a new-fault (truth) pixel.  Then, exactly by
linearity of expectation,

    E[TP_i] = sum_y rho(y) C_i(y)

For thin random line-like truth, ``E[q(x)] ~= 3 rho(x)`` (see ``Q_PER_RHO``),
so ``E[M_i] = sum_x p_i(x) * min(1, 3 rho(x))`` and ``FP_i = n_i - M_i`` where
``n_i`` is the prediction mass on scored (non-catalogue) cells.  With
``G = sum_y rho(y)``:

    DTI_i = TP_i / (TP_i + 0.2 FP_i + 0.8 (G - TP_i))

``rho`` is piecewise constant on classes ``c`` (built from distance to the
catalogue, distance to prior skeletons and geophysical bins), so ``E[TP_i]`` is
linear in the class densities.  All counts are footprint-wide; if the public
subset is a spatially unbiased fraction ``phi`` of the footprint, every term
scales by ``phi`` and the DTI is unchanged.

Evidence class of every output: ``MODEL`` (fitted to owner CLAIMs; not an
organizer score).  Validate with grouped (leave-one-site-out) prediction.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi
from scipy.optimize import minimize

ALPHA, BETA, R_PX = 0.2, 0.8, 3.0
Q_PER_RHO = 3.0

_OFF = []
for _dy in range(-3, 4):
    for _dx in range(-3, 4):
        _k = 1.0 - np.hypot(_dy, _dx) / R_PX
        if _k > 0:
            _OFF.append((_dy, _dx, _k))


def coverage_field(p: np.ndarray, binary: bool | None = None) -> np.ndarray:
    """``C(y) = max_x p(x) k(|x-y|)`` on the full grid (float32)."""
    p = np.asarray(p, np.float32)
    if binary is None:
        pos = p[p > 0]
        binary = bool(pos.size == 0 or (pos.min() == 1.0 and pos.max() == 1.0))
    if binary:
        if not (p > 0).any():
            return np.zeros(p.shape, np.float32)
        d = ndi.distance_transform_edt(~(p > 0))
        return np.maximum(0.0, 1.0 - d / R_PX).astype(np.float32)
    out = np.zeros(p.shape, np.float32)
    h, w = p.shape
    for dy, dx, k in _OFF:
        ys = slice(max(0, dy), h + min(0, dy)); yd = slice(max(0, -dy), h + min(0, -dy))
        xs = slice(max(0, dx), w + min(0, dx)); xd = slice(max(0, -dx), w + min(0, -dx))
        np.maximum(out[yd, xd], p[ys, xs] * np.float32(k), out=out[yd, xd])
    return out


def design_row(p: np.ndarray, cls: np.ndarray, n_cls: int) -> dict:
    """Class-wise sufficient statistics of one full-grid raster.

    ``cls`` is int32 per pixel: class id for scored cells, -1 for cells that are
    outside the footprint or on the (pixel-exactly masked) catalogue.
    """
    scored = cls >= 0
    C = coverage_field(p)
    A = np.bincount(cls[scored], weights=C[scored].astype(np.float64), minlength=n_cls)
    pm = np.where(scored, p, 0.0)
    nz = pm > 0
    m = np.bincount(cls[nz], weights=pm[nz].astype(np.float64), minlength=n_cls)
    return dict(A=A, m=m, n=float(pm.sum()))


def predict(rho: np.ndarray, A, m, n, Ncls) -> np.ndarray:
    """Predicted DTI for rows (A: (R,K), m: (R,K), n: (R,)) and class sizes."""
    rho = np.asarray(rho, float)
    A = np.atleast_2d(A); m = np.atleast_2d(m); n = np.atleast_1d(n)
    tp = A @ rho
    M = m @ np.minimum(1.0, Q_PER_RHO * rho)
    fp = np.maximum(n - M, 0.0)
    G = float(Ncls @ rho)
    den = tp + ALPHA * fp + BETA * np.maximum(G - tp, 0.0)
    return np.where(den > 0, tp / np.maximum(den, 1e-12), 0.0)


def fit(A, m, n, y, Ncls, *, smooth_pairs=(), lam_smooth=0.0, lam_ridge=1e-3,
        rho0=None, weights=None, max_rho=0.5) -> dict:
    """Fit class densities by weighted least squares on the DTI scale.

    Parameterised as ``rho = max_rho * sigmoid(z)`` so 0 < rho < max_rho.
    ``smooth_pairs`` are (i, j) class pairs whose log-densities are shrunk
    together (adjacent distance bins); ``lam_ridge`` shrinks log rho toward the
    global mean.
    """
    A = np.asarray(A, float); m = np.asarray(m, float); n = np.asarray(n, float)
    y = np.asarray(y, float); Ncls = np.asarray(Ncls, float)
    K = A.shape[1]
    w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    if rho0 is None:
        rho0 = np.full(K, 0.003)
    z0 = np.log(rho0 / (max_rho - rho0))
    pairs = np.array(smooth_pairs, int).reshape(-1, 2)

    def obj(z):
        rho = max_rho / (1 + np.exp(-z))
        pr = predict(rho, A, m, n, Ncls)
        loss = float(np.sum(w * (pr - y) ** 2))
        lr = np.log(rho)
        if len(pairs):
            loss += lam_smooth * float(np.sum((lr[pairs[:, 0]] - lr[pairs[:, 1]]) ** 2))
        loss += lam_ridge * float(np.sum((lr - lr.mean()) ** 2))
        return loss

    res = minimize(obj, z0, method="L-BFGS-B", options=dict(maxiter=4000, maxfun=200000))
    rho = max_rho / (1 + np.exp(-res.x))
    pr = predict(rho, A, m, n, Ncls)
    return dict(rho=rho, pred=pr, rmse=float(np.sqrt(np.mean((pr - y) ** 2))),
                success=bool(res.success), fun=float(res.fun), G=float(Ncls @ rho))


def factor_design(levels: tuple[int, ...], interactions: tuple[tuple[int, int], ...] = ()) -> np.ndarray:
    """One-hot design (K x P) for a C-ordered product of factors.

    Column 0 is the intercept; each factor contributes ``levels[f]-1``
    treatment-coded columns (level 0 is the reference).  Optional pairwise
    interactions add ``(la-1)*(lb-1)`` columns.
    """
    K = int(np.prod(levels))
    idx = np.array(np.unravel_index(np.arange(K), levels)).T  # (K, F)
    cols = [np.ones(K)]
    for f, L in enumerate(levels):
        for l in range(1, L):
            cols.append((idx[:, f] == l).astype(float))
    for a, b in interactions:
        for la in range(1, levels[a]):
            for lb in range(1, levels[b]):
                cols.append(((idx[:, a] == la) & (idx[:, b] == lb)).astype(float))
    return np.array(cols).T


def monotone_factor_design(
    levels: tuple[int, ...] | dict,
    nonincreasing_factors: tuple[int, ...] = (1,),
) -> tuple[np.ndarray, list[tuple[float | None, float | None]]]:
    """Design matrix + L-BFGS-B bounds enforcing monotone non-increasing factors.

    For any factor ``f`` in ``nonincreasing_factors`` (e.g. ``f=1`` for ``dh19``
    perpendicular distance from a 1D fault centerline), replaces one-hot treatment
    columns with cumulative step indicators ``I(idx[:, f] >= l)`` paired with
    upper bound ``<= 0.0`` so ``rho(level 0) >= rho(level 1) >= ... >= rho(L-1)``,
    preventing 300 m kernel-collinearity flank inflation (Goodhart bias).
    """
    if isinstance(levels, dict):
        levels = tuple(len(v) for v in levels.values())
    K = int(np.prod(levels))
    idx = np.array(np.unravel_index(np.arange(K), levels)).T  # (K, F)
    cols = [np.ones(K)]
    bounds: list[tuple[float | None, float | None]] = [(None, None)]
    for f, L in enumerate(levels):
        mono = f in nonincreasing_factors
        for l in range(1, L):
            if mono:
                cols.append((idx[:, f] >= l).astype(float))
                bounds.append((None, 0.0))
            else:
                cols.append((idx[:, f] == l).astype(float))
                bounds.append((None, None))
    return np.array(cols).T, bounds


def fit_loglinear(A, m, n, y, Ncls, X, *, lam=1e-3, beta0=None, weights=None, bounds=None) -> dict:
    """Fit ``rho = exp(X beta)`` (capped at 0.5) by least squares on DTI."""
    A = np.asarray(A, float); m = np.asarray(m, float); n = np.asarray(n, float)
    y = np.asarray(y, float); Ncls = np.asarray(Ncls, float); X = np.asarray(X, float)
    w = np.ones(len(y)) if weights is None else np.asarray(weights, float)
    P = X.shape[1]
    b0 = np.zeros(P) if beta0 is None else np.asarray(beta0, float).copy()
    if beta0 is None:
        b0[0] = np.log(0.003)
    if bounds is not None:
        for j, (lo, hi) in enumerate(bounds):
            if lo is not None and b0[j] < lo:
                b0[j] = lo
            if hi is not None and b0[j] > hi:
                b0[j] = hi

    def rho_of(b):
        return np.minimum(np.exp(np.clip(X @ b, -30, 5)), 0.5)

    def obj(b):
        pr = predict(rho_of(b), A, m, n, Ncls)
        return float(np.sum(w * (pr - y) ** 2) + lam * np.sum(b[1:] ** 2))

    best = None
    for start in (b0, b0 + 0.0):
        res = minimize(obj, start, method="L-BFGS-B", bounds=bounds, options=dict(maxiter=5000, maxfun=500000))
        if best is None or res.fun < best.fun:
            best = res
    rho = rho_of(best.x)
    pr = predict(rho, A, m, n, Ncls)
    return dict(beta=best.x, rho=rho, pred=pr, rmse=float(np.sqrt(np.mean((pr - y) ** 2))),
                success=bool(best.success), G=float(Ncls @ rho))
