"""Core primitives for the GEMSDOE92 AXIS=TRACKB session.

Everything here is label-free with respect to the hidden test faults:
the only fault geometry used is the pinned organizer catalogue
(``existing_faults.tif``), used solely for (a) the parent lineage prune
that defines R0 and (b) the >=2 px / refill >3 px exclusion geometry.
The ranking field is built exclusively from the organizer-provided
19-band stack in ``training_features.tif``.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter, label as ndi_label
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import metric  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
PARENT_SHA_ZEROS = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
PARENT_SHA_NAN = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
SEED = 20261023


def data_path(verified: dict[str, Path], fid: str) -> Path:
    return verified[fid]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest(manifest_path: Path | None = None) -> dict[str, Path]:
    manifest_path = manifest_path or (ROOT / "registry" / "data_manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    verified: dict[str, Path] = {}
    for entry in manifest["files"]:
        p = ROOT / entry["local_path"]
        if not p.is_file():
            raise FileNotFoundError(
                f"Missing pinned input {entry['id']}: {p} "
                "(run python scripts/restore_inputs.py)"
            )
        actual_sha = sha256_file(p)
        actual_bytes = p.stat().st_size
        if actual_sha != entry["sha256"]:
            raise ValueError(
                f"SHA-256 mismatch on {entry['id']} ({p}): got {actual_sha}, "
                f"expected {entry['sha256']}"
            )
        if actual_bytes != entry["bytes"]:
            raise ValueError(
                f"Byte-length mismatch on {entry['id']} ({p}): got {actual_bytes}, "
                f"expected {entry['bytes']}"
            )
        verified[entry["id"]] = p
    return verified


# ---------------------------------------------------------------------------
# Parent lineage (copied deterministically from the recorded H19-5 recipe;
# identical algorithm to GEMSDOE88 scripts/build_prune_variants.py)
# ---------------------------------------------------------------------------

def dot_thin(mask: np.ndarray, min_dist: float) -> np.ndarray:
    """Deterministic geodesic Poisson-disk thinning of a binary ridge mask."""
    mask = np.asarray(mask, dtype=bool)
    if min_dist <= 1.0 or not mask.any():
        return mask.copy()
    H, W = mask.shape
    pad = int(np.ceil(min_dist)) + 1
    Wp, Hp = W + 2 * pad, H + 2 * pad
    padded = np.zeros((Hp, Wp), dtype=bool)
    padded[pad: pad + H, pad: pad + W] = mask
    flat = bytearray(padded.tobytes())
    visited, blocked, kept = bytearray(Hp * Wp), bytearray(Hp * Wp), bytearray(Hp * Wp)
    r = int(np.ceil(min_dist))
    lim = min_dist * min_dist
    disc = [
        dy * Wp + dx
        for dy in range(-r, r + 1)
        for dx in range(-r, r + 1)
        if dy * dy + dx * dx < lim
    ]
    nbr = (-Wp - 1, -Wp, -Wp + 1, -1, 1, Wp - 1, Wp, Wp + 1)
    comp, _ = ndi_label(padded, structure=np.ones((3, 3), dtype=int))
    fc = comp.ravel()
    order = np.flatnonzero(fc)
    _, first = np.unique(fc[order], return_index=True)
    for seed in order[np.sort(first)].tolist():
        if visited[seed]:
            continue
        visited[seed] = 1
        queue = deque((seed,))
        while queue:
            q = queue.popleft()
            if not blocked[q]:
                kept[q] = 1
                for o in disc:
                    blocked[q + o] = 1
            for o in nbr:
                nb = q + o
                if flat[nb] and not visited[nb]:
                    visited[nb] = 1
                    queue.append(nb)
    out = np.frombuffer(bytes(kept), dtype=np.uint8).reshape(Hp, Wp).astype(bool)
    return out[pad: pad + H, pad: pad + W]


def rebuild_r0_from_lineage(verified: dict[str, Path]) -> dict:
    """Rebuild R0 from H19-5 through every recorded step; match SHA-256 exactly."""
    import tempfile

    with rasterio.open(verified["sample_submission"]) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(verified["existing_faults"]) as ds:
        ef_profile = ds.profile.copy()
        catalogue = (ds.read(1) > 0) & foot
    d_cat = distance_transform_edt(~catalogue)

    def _load(fid: str) -> np.ndarray:
        with rasterio.open(verified[fid]) as ds:
            return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    h19_5 = _load("anc_h19_5")
    d15_ref = _load("anc_d1_5")
    d28_ref = _load("anc_d2_8")
    solo_ref = _load("anc_solo_d2_8")
    r0_ref = _load("parent_r0_zeros")

    d15_rebuilt = dot_thin(h19_5, 1.5)
    d28_rebuilt = dot_thin(h19_5, 2.8)
    solo_rebuilt = d28_rebuilt & (d_cat > 1.0)
    r0_rebuilt = d28_rebuilt & (d_cat > 2.0)

    if not np.array_equal(d15_rebuilt, d15_ref):
        raise RuntimeError("Lineage rebuild failed at D1.5")
    if not np.array_equal(d28_rebuilt, d28_ref):
        raise RuntimeError("Lineage rebuild failed at D2.8")
    if not np.array_equal(solo_rebuilt, solo_ref):
        raise RuntimeError("Lineage rebuild failed at SOLO-D2.8")
    if not np.array_equal(r0_rebuilt, r0_ref):
        raise RuntimeError("Lineage rebuild failed at R0 pixel mask")

    prof_zeros = ef_profile.copy()
    prof_zeros.update(
        driver="GTiff", dtype="float32", count=1, compress="deflate",
        predictor=3, zlevel=9, tiled=True, blockxsize=256, blockysize=256,
        nodata=None,
    )
    prof_nan = prof_zeros.copy()
    prof_nan.update(nodata=np.nan)

    with tempfile.TemporaryDirectory() as td:
        p_z = Path(td) / "r0_zeros.tif"
        p_n = Path(td) / "r0_nan.tif"
        with rasterio.open(p_z, "w", **prof_zeros) as dst:
            dst.write(np.where(foot, r0_rebuilt.astype(np.float32), 0.0).astype(np.float32), 1)
        with rasterio.open(p_n, "w", **prof_nan) as dst:
            dst.write(np.where(foot, r0_rebuilt.astype(np.float32), np.nan).astype(np.float32), 1)
        sha_z = sha256_file(p_z)
        sha_n = sha256_file(p_n)

    if sha_z != PARENT_SHA_ZEROS:
        raise RuntimeError(f"Rebuilt R0 zeros SHA mismatch: {sha_z} != {PARENT_SHA_ZEROS}")
    if sha_n != PARENT_SHA_NAN:
        raise RuntimeError(f"Rebuilt R0 NaN SHA mismatch: {sha_n} != {PARENT_SHA_NAN}")

    return dict(
        foot=foot, catalogue=catalogue, d_cat=d_cat, h19_5=h19_5,
        d15=d15_rebuilt, d28=d28_rebuilt, solo=solo_rebuilt, r0=r0_rebuilt,
        rebuilt_zeros_sha256=sha_z, rebuilt_nan_sha256=sha_n,
        ef_profile=ef_profile,
    )


# ---------------------------------------------------------------------------
# Provided-band physics field (19 bands only) + leakage canaries
# ---------------------------------------------------------------------------

def percentile_rank(arr: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.zeros(arr.shape, dtype=np.float32)
    v = np.nan_to_num(arr[valid], nan=0.0, posinf=0.0, neginf=0.0)
    qs = np.linspace(0.0, 1.0, 1001)
    knots = np.quantile(v, qs)
    out[valid] = np.interp(v, knots, qs).astype(np.float32)
    return out


def hessian_ridge(a: np.ndarray, sigma: float = 2.0) -> np.ndarray:
    axx = gaussian_filter(a, sigma, order=(0, 2), mode="nearest")
    ayy = gaussian_filter(a, sigma, order=(2, 0), mode="nearest")
    axy = gaussian_filter(a, sigma, order=(1, 1), mode="nearest")
    tmp = np.sqrt(np.maximum(((axx - ayy) * 0.5) ** 2 + axy ** 2, 0.0))
    l1 = (axx + ayy) * 0.5 + tmp
    l2 = (axx + ayy) * 0.5 - tmp
    big = np.where(np.abs(l1) >= np.abs(l2), l1, l2)
    return np.maximum(-big, 0.0).astype(np.float32)


def build_physics_field(verified: dict[str, Path], foot: np.ndarray,
                        catalogue: np.ndarray) -> tuple[np.ndarray, dict, dict[str, float]]:
    """Label-free composite s_phys from the 19 provided bands only.

    Returns (s_phys_percentile, components_dict, canaries). Canary positives
    are whole-component withheld catalogue pixels (seeds 20+30, vendor
    gems57 holdout); every channel must have symmetric AUC <= 0.90 or this
    raises (leakage canary, brief section 6 REPORT-ONLY turned fail-closed
    here for field *construction*, exactly as in prior sessions).
    """
    from sklearn.metrics import roc_auc_score

    from gems57 import grid as grid_mod, holdout as holdout_mod

    gd = grid_mod.load_grid(verified["sample_submission"].parent)
    folds20, _ = holdout_mod.buffered_component_draw(gd, seed=20)
    folds30, _ = holdout_mod.buffered_component_draw(gd, seed=30)
    pos_mask = folds20[0]["hidden_all"] | folds30[0]["hidden_all"]
    del folds20, folds30, gd
    rng = np.random.default_rng(SEED)
    neg_pool = np.flatnonzero(foot & ~catalogue & ~pos_mask)
    neg_sample = rng.choice(neg_pool, size=min(100_000, len(neg_pool)), replace=False)
    pos_idx = np.flatnonzero(pos_mask)
    del pos_mask, neg_pool
    eval_idx = np.concatenate([pos_idx, neg_sample])
    y_true = np.concatenate(
        [np.ones(len(pos_idx), dtype=np.int8), np.zeros(len(neg_sample), dtype=np.int8)]
    )
    canaries: dict[str, float] = {}

    def consume(name: str, arr: np.ndarray) -> np.ndarray:
        auc = float(roc_auc_score(y_true, arr.ravel()[eval_idx]))
        sym = float(max(auc, 1.0 - auc))
        canaries[name] = round(sym, 5)
        if sym > 0.90:
            raise RuntimeError(f"LEAKAGE CANARY TRIPPED on {name}: symmetric AUC = {sym:.5f} > 0.90")
        return percentile_rank(arr, foot)

    def read_clean(ds, idx: int) -> np.ndarray:
        a = np.where(foot, np.nan_to_num(ds.read(idx), nan=0.0), 0.0).astype(np.float32)
        bad = (~np.isfinite(a)) | (np.abs(a) > 1e20)
        if np.any(bad & foot):
            a[bad] = float(np.median(a[foot & ~bad]))
        a[~foot] = 0.0
        return a

    with rasterio.open(verified["training_features"]) as ds:
        b12 = read_clean(ds, 12)
        scarp_h = hessian_ridge(b12, 1.8) + 0.5 * hessian_ridge(b12, 3.2)
        b19 = read_clean(ds, 19)
        b03 = read_clean(ds, 3)
        b18 = read_clean(ds, 18)
        b15 = read_clean(ds, 15)
        gy15, gx15 = np.gradient(gaussian_filter(b15, 1.5))
        b15g = np.hypot(gy15, gx15).astype(np.float32)
        del gy15, gx15
        b02 = read_clean(ds, 2)
        b02h = hessian_ridge(b02, 2.0)
        b04 = read_clean(ds, 4)
        b16 = read_clean(ds, 16)
        b06 = np.abs(read_clean(ds, 6))
        b17 = read_clean(ds, 17)
        gy17, gx17 = np.gradient(gaussian_filter(b17, 1.5))
        b17g = np.hypot(gy17, gx17).astype(np.float32)
        del gy17, gx17

    p_scarp_h = consume("det_elev_hessian_b12", scarp_h)
    p_b19 = consume("det_elev_slope_b19", b19)
    p_b18 = consume("grav_hg_b18", b18)
    p_b03 = consume("tmi_hg_b03", b03)
    p_b15g = consume("basement_grad_b15", b15g)
    p_b02h = consume("rtp_hessian_b02", b02h)
    p_b04 = consume("geod_strain_b04", b04)
    p_b16 = consume("seismic_ieq_b16", b16)
    p_b06 = consume("mag_tilt_curv_b06", b06)
    p_b17g = consume("mt_cond_grad_b17", b17g)

    line_scarp = 0.58 * p_scarp_h + 0.42 * p_b19
    line_geopot = 0.34 * p_b18 + 0.28 * p_b03 + 0.22 * p_b15g + 0.16 * p_b02h
    line_kinem = 0.45 * p_b04 + 0.35 * p_b16 + 0.20 * p_b06
    s_phys = (0.40 * line_scarp + 0.34 * line_geopot + 0.16 * line_kinem
              + 0.10 * p_b17g).astype(np.float32)
    s_phys[~foot] = 0.0
    auc_c = float(roc_auc_score(y_true, s_phys.ravel()[eval_idx]))
    canaries["composite_s_phys"] = round(float(max(auc_c, 1.0 - auc_c)), 5)
    if canaries["composite_s_phys"] > 0.90:
        raise RuntimeError("LEAKAGE CANARY TRIPPED on composite_s_phys")

    components = {
        "scarp_pct": p_scarp_h, "slope_pct": p_b19,
        "tmi_hg_pct": p_b03, "grav_hg_pct": p_b18,
    }
    return s_phys, components, canaries


def soft_weights(s_phys_pct: np.ndarray, h19_5: np.ndarray, foot: np.ndarray,
                 catalogue: np.ndarray) -> np.ndarray:
    """Soft expected-fault weight w(g) for exact-marginal refill ranking."""
    w = np.where(
        h19_5, 0.045 + 0.22 * s_phys_pct, 0.015 * s_phys_pct
    ).astype(np.float32)
    w[~(foot & ~catalogue)] = 0.0
    return w


# ---------------------------------------------------------------------------
# TRACKB traces: dot-graph components chained at <=4.5 px
# ---------------------------------------------------------------------------

def build_traces(r0: np.ndarray, min_span_px: float, gap_px: float = 4.5,
                 min_dots: int = 4) -> tuple[np.ndarray, list[dict]]:
    """Keep R0 dots whose <=gap chaining component spans >= min_span_px.

    Returns (kept_mask, traces). Each trace dict carries the dot indices
    (into the row-major R0 dot list), PCA strike/linearity and the
    PCA-ordered polyline length. Connectivity through neighbouring dots
    on the H19-5 ridge is the strike-consistency criterion: every step is
    <=4.5 px along the ridge the parent detector already traced.
    """
    ys, xs = np.nonzero(r0)
    pts = np.column_stack([ys, xs]).astype(np.float64)
    n = len(pts)
    tree = cKDTree(pts)
    pairs = tree.query_pairs(r=gap_px)
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    comps: dict[int, list[int]] = {}
    for i in range(n):
        comps.setdefault(find(i), []).append(i)

    kept = np.zeros(n, dtype=bool)
    traces: list[dict] = []
    for members in comps.values():
        if len(members) < min_dots:
            continue
        p = pts[members]
        span = float(np.hypot(p[:, 0].max() - p[:, 0].min(),
                              p[:, 1].max() - p[:, 1].min()))
        if span < min_span_px:
            continue
        kept[members] = True
        centre = p.mean(axis=0)
        c = p - centre
        _, _, vt = np.linalg.svd(c, full_matrices=False)
        axis = vt[0]  # (row, col) direction
        t = c @ axis
        order = np.argsort(t, kind="stable")
        sorted_p = p[order]
        seg = np.diff(sorted_p, axis=0)
        poly_px = float(np.hypot(seg[:, 0], seg[:, 1]).sum()) if len(seg) else 0.0
        # successive turn angles along the PCA-ordered chain
        turns: list[float] = []
        for i in range(1, len(seg)):
            a, b = seg[i - 1], seg[i]
            na, nb = float(np.hypot(*a)), float(np.hypot(*b))
            if na > 0 and nb > 0:
                cosang = float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
                turns.append(float(np.degrees(np.arccos(cosang))))
        cov = (c.T @ c) / len(members)
        evals = np.linalg.eigvalsh(cov)
        linearity = float(evals[1] / (evals.sum() + 1e-12)) if len(members) >= 2 else 1.0
        # strike azimuth (deg clockwise from north, undirected 0-180):
        # row increases south, so north component = -axis_row, east = axis_col
        strike = float(np.degrees(np.arctan2(axis[1], -axis[0])) % 180.0)
        traces.append({
            "dot_indices": [int(members[i]) for i in order],
            "n_dots": int(len(members)),
            "span_px": span,
            "span_km": span * 0.1,
            "polyline_km": poly_px * 0.1,
            "strike_deg": strike,
            "linearity": linearity,
            "mean_turn_deg": float(np.mean(turns)) if turns else 0.0,
            "centroid_row": float(centre[0]),
            "centroid_col": float(centre[1]),
        })
    kept_mask = np.zeros(r0.shape, dtype=bool)
    kept_mask[ys[kept], xs[kept]] = True
    # attach grid positions to traces for downstream stats / GeoJSON
    for tr in traces:
        idx = np.asarray(tr["dot_indices"], dtype=int)
        tr["rows"] = ys[idx]
        tr["cols"] = xs[idx]
    traces.sort(key=lambda t: (-t["polyline_km"], t["centroid_row"], t["centroid_col"]))
    for i, tr in enumerate(traces):
        tr["trace_id"] = f"T{i:04d}"
    return kept_mask, traces


def walked_paths(rows: np.ndarray, cols: np.ndarray, gap_px: float = 4.5) -> list[np.ndarray]:
    """Decompose a dot set into straightest-walk paths through its <=gap graph.

    Starts at lowest-degree dots (strand ends first), walks to the
    unvisited neighbour with the smallest turn angle (never >90 deg),
    then extends backwards from the start. Returns index arrays into
    (rows, cols). Every input dot appears in exactly one path; callers
    filter by polyline length. Ordering follows the actual strand, so
    polyline lengths and turn angles are geologically meaningful --
    unlike a PCA projection order through a branching network.
    """
    pts = np.column_stack([rows, cols]).astype(np.float64)
    n = len(pts)
    if n == 0:
        return []
    tree = cKDTree(pts)
    adj: list[list[int]] = [[] for _ in range(n)]
    for a, b in tree.query_pairs(r=gap_px):
        adj[a].append(b)
        adj[b].append(a)
    deg = np.array([len(a) for a in adj])

    def _walk(path: list[int], visited: np.ndarray, prev_vec) -> list[int]:
        while True:
            cur = path[-1]
            cand = [nb for nb in adj[cur] if not visited[nb]]
            if not cand:
                break
            if prev_vec is None:
                nxt = min(cand, key=lambda nb: (float(np.hypot(*(pts[nb] - pts[cur]))),
                                                float(pts[nb, 0]), float(pts[nb, 1])))
            else:
                def _score(nb):
                    v = pts[nb] - pts[cur]
                    nv = float(np.hypot(*v))
                    ang = float(np.degrees(np.arccos(np.clip(
                        np.dot(prev_vec, v) / (np.hypot(*prev_vec) * nv), -1.0, 1.0)))) if nv > 0 else 180.0
                    return (ang, nv, float(pts[nb, 0]), float(pts[nb, 1]))
                nxt = min(cand, key=_score)
                v = pts[nxt] - pts[cur]
                nv = float(np.hypot(*v))
                ang = float(np.degrees(np.arccos(np.clip(
                    np.dot(prev_vec, v) / (np.hypot(*prev_vec) * nv), -1.0, 1.0)))) if nv > 0 else 180.0
                if ang > 90.0:
                    break
            prev_vec = pts[nxt] - pts[cur]
            path.append(int(nxt))
            visited[nxt] = True
        return path

    visited = np.zeros(n, dtype=bool)
    start_order = sorted(range(n), key=lambda i: (int(deg[i]), float(pts[i, 0]), float(pts[i, 1])))
    paths: list[np.ndarray] = []
    for start in start_order:
        if visited[start]:
            continue
        visited[start] = True
        path = _walk([int(start)], visited, None)
        if len(path) >= 2:
            path = path[::-1]
            prev = pts[path[-1]] - pts[path[-2]]
            path = _walk(path, visited, prev)
        paths.append(np.asarray(path, dtype=int))
    return paths


# ---------------------------------------------------------------------------
# Chunked exact-marginal-DTI refill (vendor metric offsets, batch greedy)
# ---------------------------------------------------------------------------

def refill_chunked_exact(kept: np.ndarray, pool_mask: np.ndarray, w: np.ndarray,
                         n_add: int, chunk: int = 250) -> np.ndarray:
    """Add n_add dots from pool_mask maximising exact expected DTI in batches.

    Each batch recomputes the exact coverage C_A(g), and per-candidate
    (dT, m_cand) from vendor/gems57/metric.py offsets, ranks by the exact
    next-DTI (T+dT)/(D+alpha*(dT+1-m)), tie-broken by (row, col), and takes
    the top ``chunk``. This is the exact marginal criterion of brief
    section 2 evaluated iteratively in batches -- never the isolated-pixel
    shortcut k > alpha*DTI alone.
    """
    state = np.asarray(kept, dtype=bool).copy()
    if n_add <= 0:
        return state
    H, W = state.shape
    w64 = np.asarray(w, dtype=np.float64)
    w_tot = float(w64.sum())
    alpha, beta = metric.ALPHA, metric.BETA
    cy_all, cx_all = np.nonzero(pool_mask & ~state)
    if len(cy_all) < n_add:
        raise ValueError(f"Candidate pool ({len(cy_all)}) smaller than refill ({n_add})")
    remaining = np.ones(len(cy_all), dtype=bool)

    off_dy = metric.OFF_DY.astype(np.int64)
    off_dx = metric.OFF_DX.astype(np.int64)
    off_k = metric.OFF_K.astype(np.float64)

    added = 0
    while added < n_add:
        by, bx = np.nonzero(state)
        cov = np.zeros((H, W), dtype=np.float64)
        for dy, dx, kw in zip(off_dy, off_dx, off_k):
            ny, nx = by + int(dy), bx + int(dx)
            ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
            np.maximum.at(cov, (ny[ok], nx[ok]), float(kw))
        t_cur = float((w64 * cov).sum())
        m_base = np.zeros(len(by), dtype=np.float64)
        for dy, dx, kw in zip(off_dy, off_dx, off_k):
            ny, nx = by + int(dy), bx + int(dx)
            ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
            m_base[ok] = np.maximum(m_base[ok], w64[ny[ok], nx[ok]] * float(kw))
        m_cur = float(m_base.sum())
        s_cur = float(len(by))

        idx = np.flatnonzero(remaining)
        cy, cx = cy_all[idx], cx_all[idx]
        m_cand = np.zeros(len(cy), dtype=np.float64)
        dT = np.zeros(len(cy), dtype=np.float64)
        for dy, dx, kw in zip(off_dy, off_dx, off_k):
            ny, nx = cy + int(dy), cx + int(dx)
            ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
            wv = w64[ny[ok], nx[ok]]
            m_cand[ok] = np.maximum(m_cand[ok], wv * float(kw))
            dT[ok] += wv * np.maximum(0.0, float(kw) - cov[ny[ok], nx[ok]])
        d_cur = alpha * (t_cur + s_cur - m_cur) + beta * w_tot + metric.EPS
        next_dti = (t_cur + dT) / (d_cur + alpha * (dT + 1.0 - m_cand))
        order = np.lexsort((cx, cy, -next_dti))
        take_n = min(chunk, n_add - added, len(order))
        chosen_local = order[:take_n]
        chosen_global = idx[chosen_local]
        state[cy_all[chosen_global], cx_all[chosen_global]] = True
        remaining[chosen_global] = False
        added += int(take_n)
    return state


def weighted_expected_dti(mask: np.ndarray, w: np.ndarray) -> dict[str, float]:
    a = np.asarray(mask, dtype=bool)
    w64 = np.asarray(w, dtype=np.float64)
    H, W = a.shape
    cov = np.zeros((H, W), dtype=np.float64)
    ay, ax = np.nonzero(a)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = ay + int(dy), ax + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        np.maximum.at(cov, (ny[ok], nx[ok]), float(kw))
    t_val = float((w64 * cov).sum())
    m_self = np.zeros(len(ay), dtype=np.float64)
    for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
        ny, nx = ay + int(dy), ax + int(dx)
        ok = (ny >= 0) & (ny < H) & (nx >= 0) & (nx < W)
        m_self[ok] = np.maximum(m_self[ok], w64[ny[ok], nx[ok]] * float(kw))
    m_val = float(m_self.sum())
    s_val = float(len(ay))
    w_tot = float(w64.sum())
    denom = metric.ALPHA * (t_val + s_val - m_val) + metric.BETA * w_tot + metric.EPS
    return dict(T=t_val, S=s_val, M=m_val, W=w_tot, denom=denom,
                dti=float(t_val / denom))


def block_cv(mask: np.ndarray, foot: np.ndarray, block_px: int) -> float:
    H, W = foot.shape
    Hs, Ws = (H // block_px) * block_px, (W // block_px) * block_px
    fb = foot[:Hs, :Ws].reshape(Hs // block_px, block_px, Ws // block_px, block_px).sum(axis=(1, 3))
    interior = fb == (block_px * block_px)
    ab = mask[:Hs, :Ws].reshape(Hs // block_px, block_px, Ws // block_px, block_px).sum(axis=(1, 3))
    dens = ab[interior] / fb[interior]
    return float(dens.std() / dens.mean())
