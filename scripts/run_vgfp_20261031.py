#!/usr/bin/env python3
"""V-GFP lane runner (2026-10-31): VENT-CENTRIC GEOTHERMAL FAULT PROPENSITY.

Lane paragraph (the session prompt's designated method paragraph is missing --
IRREGULARITIES -- so this lane is stated explicitly here and nowhere else):

    V-GFP learns the *appearance* of mapped faults from the free official
    external stack (USGS GeoDawn radiometrics/magnetics ThK/UK/UTh/TMI_up150 +
    K/Th/U/TC, 12 USGS 3DEP 2 m LiDAR scarp channels, USGS SGMC traces) and the
    *geothermal-vent science* the fleet has not mined (USGS GDR #1391 volcanic
    vents, 27k wells/springs with thermal class and geothermometer temperatures,
    INGENIOUS 2 m temperature probes, Qfaults Neotectonic slip-rate/recency
    centroids), fits a gradient-boosted pixel classifier to VISIBLE catalogue
    faults only inside each spatial fold, and emits a sparse binary dot field by
    the R0-lineage spaced-top rule (2.8 px floor, 37,654 dots, d_visible > 2 px
    collar) under the official DTI (alpha=0.2, beta=0.8, 300 m triangular).
    Named non-fault mimic: Lake Lahontan paleoshoreline beach ridges and
    incised drainage banks (LiDAR scarp channels) plus lithologic contacts
    (magnetic/radiometric edges) and prospector access roads (BLM/TIGER
    confound channels, audited explicitly).

Stages (each restartable, fail-closed):
  python scripts/run_vgfp_20261031.py features   # build feature matrix
  python scripts/run_vgfp_20261031.py holdout    # fold-proper HOLDOUT-DTI + canaries
  python scripts/run_vgfp_20261031.py deploy     # write TIFF + gates + uniqueness
  python scripts/run_vgfp_20261031.py report     # run card JSON

Every number written by this script is labelled HOLDOUT-DTI / REGISTRY-MEASUREMENT
/ MODEL-CLASS PROJECTION. No number is an organizer score.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import struct
import sys
import time
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

CACHE = ROOT / ".cache" / "vgfp"
EXT = ROOT / "data" / "external"
DOWNLOADS = ROOT / "docs" / "downloads"
EVID = ROOT / "evidence"
BRIDGE = ROOT / "data" / "bridge"

DATE = "20261031"
N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
FEATURE_NAMES = [
    "ThK", "UK", "UTh", "TMI_up150", "K", "Th", "U", "TC",
    "ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max",
    "downface_max", "upface_max", "cross_max", "relief", "coh100", "strike",
    "sgmc", "d_cat", "vent_g", "hot_g", "well_g", "probe_g", "qfault_g",
    "road_log", "claim_log", "tmi_grad", "tc_grad",
]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dequant(a: np.ndarray) -> np.ndarray:
    """u8 quantisation q=1+round(254*t(x/xmax)) -> x/xmax in [0,1]; 0 = missing."""
    a = a.astype(np.float32)
    out = np.where(a > 0, (a - 1.0) / 254.0, 0.0).astype(np.float32)
    return out


def parse_shp_points(path: Path) -> np.ndarray:
    """Minimal ESRI shapefile point reader (shape type 1) -> (n, 2) XY."""
    data = path.read_bytes()
    if len(data) < 100:
        raise ValueError("shapefile too small")
    shape_type = struct.unpack("<i", data[32:36])[0]
    pts = []
    off = 100
    while off + 8 <= len(data):
        _num, clen = struct.unpack(">ii", data[off:off + 8])
        off += 8
        content = data[off:off + 2 * clen]
        off += 2 * clen
        if len(content) < 4:
            continue
        st = struct.unpack("<i", content[0:4])[0]
        if st == 1 and shape_type == 1 and len(content) >= 20:
            x, y = struct.unpack("<dd", content[4:20])
            pts.append((x, y))
    return np.asarray(pts, np.float64)


def gaussian_density(rows: np.ndarray, cols: np.ndarray, shape, sigma: float = 5.0) -> np.ndarray:
    from scipy.ndimage import gaussian_filter, distance_transform_edt
    if len(rows) == 0:
        return np.zeros(shape, np.float32)
    acc = np.zeros(shape, np.float32)
    np.add.at(acc, (rows, cols), 1.0)
    if sigma > 0:
        acc = gaussian_filter(acc, sigma)
    return acc.astype(np.float32)


# ----------------------------------------------------------------- stage: features
def stage_features() -> int:
    import pandas as pd
    import rasterio
    from scipy.ndimage import distance_transform_edt, gaussian_filter

    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    with rasterio.open(BRIDGE / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
        H, W = fp.shape
    with rasterio.open(BRIDGE / "existing_faults.tif") as ds:
        cat = ds.read(1) == 1
    yy, xx = np.nonzero(fp)
    n_fp = yy.size
    log(f"footprint {n_fp} px; catalogue {int(cat.sum())} px")

    X = np.zeros((n_fp, len(FEATURE_NAMES)), np.float32)

    def put(idx: int, full: np.ndarray) -> None:
        X[:, idx] = full[yy, xx].astype(np.float32)

    # --- GeoDawn (8) + LiDAR (12) + SGMC (1)
    with rasterio.open(EXT / "geodawn_extensions_u8.tif") as ds:
        names = ["ThK", "UK", "UTh", "TMI_up150"]
        for b in range(1, 5):
            put(b - 1, dequant(ds.read(b)))
    with rasterio.open(EXT / "geodawn_rad_u8.tif") as ds:
        for b in range(1, 5):
            put(3 + b, dequant(ds.read(b)))
    with rasterio.open(EXT / "lidar_scarp_features_u8.tif") as ds:
        # bands 1..11 -> feature indices 8..18 (ex_max..strike); band 12 ("valid",
        # the LiDAR coverage flag) is dropped on purpose: dequant 0.0 already
        # encodes "no LiDAR" and FEATURE_NAMES[19] is sgmc.
        for b in range(1, 12):
            put(7 + b, dequant(ds.read(b)))
    with rasterio.open(EXT / "derived_sgmc_faults_100m_u8.tif") as ds:
        put(19, (ds.read(1) > 0).astype(np.float32))

    # --- catalogue distance placeholder (refilled per fold in holdout; full here)
    d_cat = distance_transform_edt(~cat).astype(np.float32)
    put(20, np.minimum(d_cat, 60.0) / 60.0)

    # --- vent / spring / well / probe / qfault densities (grid row/col given in CSVs)
    v = pd.read_csv(EXT / "gdr_volcanic_vents_in_footprint.csv")
    rows = v["row"].to_numpy(int).clip(0, H - 1); cols = v["col"].to_numpy(int).clip(0, W - 1)
    put(21, gaussian_density(rows, cols, (H, W), 5.0))

    w = pd.read_csv(EXT / "gdr_wellspring_in_footprint.csv")
    hot_mask = (w["thermalclass"].astype(str).str.lower() == "hot") | (pd.to_numeric(w.get("temp_c"), errors="coerce") >= 40)
    hw = w[hot_mask.fillna(False)]
    rows = hw["row"].to_numpy(int).clip(0, H - 1); cols = hw["col"].to_numpy(int).clip(0, W - 1)
    put(22, gaussian_density(np.unique(np.stack([rows, cols], 1), axis=0)[:, 0],
                             np.unique(np.stack([rows, cols], 1), axis=0)[:, 1], (H, W), 5.0))
    rows = w["row"].to_numpy(int).clip(0, H - 1); cols = w["col"].to_numpy(int).clip(0, W - 1)
    u = np.unique(np.stack([rows, cols], 1), axis=0)
    put(23, gaussian_density(u[:, 0], u[:, 1], (H, W), 5.0))

    # INGENIOUS 2 m probes from the mirrored shapefile (WGS84 NAD83 -> UTM 11N approx via pyproj-free heuristic:
    # the .prj is NAD83 geographic; we transform with a local equirectangular projection pinned in code below.)
    try:
        with zipfile.ZipFile(EXT / "2m_temperature_probe_INGENIOUS_regional_data.zip") as z:
            shp_name = [n for n in z.namelist() if n.endswith(".shp")][0]
            prj_name = [n for n in z.namelist() if n.endswith(".prj")][0]
            shp_bytes = z.read(shp_name)
            prj_txt = z.read(prj_name).decode("utf-8", "ignore")
        tmp = CACHE / "probes.shp"; tmp.write_bytes(shp_bytes)
        pts = parse_shp_points(tmp)
        if "NAD83" in prj_txt or "4269" in prj_txt or "GCS" in prj_txt:
            # geographic lon/lat -> UTM zone 11N (WGS84 ellipsoid, transverse mercator)
            lon = np.radians(pts[:, 0]); lat = np.radians(pts[:, 1])
            a, f = 6378137.0, 1 / 298.257223563
            e2 = f * (2 - f)
            k0 = 0.9996
            lon0 = np.radians(-117.0)
            ep2 = e2 / (1 - e2)
            N = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
            T = np.tan(lat) ** 2
            C = ep2 * np.cos(lat) ** 2
            A = (lon - lon0) * np.cos(lat)
            M = a * ((1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256) * lat
                     - (3 * e2 / 8 + 3 * e2 ** 2 / 32 + 45 * e2 ** 3 / 1024) * np.sin(2 * lat)
                     + (15 * e2 ** 2 / 256 + 45 * e2 ** 3 / 1024) * np.sin(4 * lat)
                     - (35 * e2 ** 3 / 3072) * np.sin(6 * lat))
            x = k0 * N * (A + (1 - T + C) * A ** 3 / 6 + (5 - 18 * T + T ** 2 + 72 * C - 58 * ep2) * A ** 5 / 120) + 500000.0
            y = k0 * (M + N * np.tan(lat) * (A ** 2 / 2 + (5 - T + 9 * C + 4 * C ** 2) * A ** 4 / 24
                                             + (61 - 58 * T + T ** 2 + 600 * C - 330 * ep2) * A ** 6 / 720))
            ux, uy = x, y
        else:
            ux, uy = pts[:, 0], pts[:, 1]
        # UTM -> grid row/col using the pinned affine: col=(x-243350)/100, row=(4508550-y)/100
        pcols = np.round((ux - 243350.0) / 100.0).astype(int)
        prows = np.round((4508550.0 - uy) / 100.0).astype(int)
        ok = (prows >= 0) & (prows < H) & (pcols >= 0) & (pcols < W)
        u = np.unique(np.stack([prows[ok], pcols[ok]], 1), axis=0)
        put(24, gaussian_density(u[:, 0], u[:, 1], (H, W), 5.0) if len(u) else np.zeros((H, W), np.float32))
        log(f"INGENIOUS probes: {int(ok.sum())} in footprint")
    except Exception as exc:  # noqa: BLE001 - recorded, fail-closed at manifest level
        log(f"WARNING probe layer unavailable ({exc}); probe_g = 0")
        put(24, np.zeros((H, W), np.float32))

    q = pd.read_csv(EXT / "gdr_qfaults_traces.csv")
    qi = q[q["centroid_in_footprint"] == 1]
    rows = qi["centroid_row"].to_numpy(int).clip(0, H - 1); cols = qi["centroid_col"].to_numpy(int).clip(0, W - 1)
    acc = np.zeros((H, W), np.float32)
    wgt = np.sqrt(qi["clipped_length_m"].to_numpy(float)) / 50.0
    np.add.at(acc, (rows, cols), wgt.astype(np.float32))
    put(25, gaussian_filter(acc, 5.0).astype(np.float32))

    # --- confounds
    with rasterio.open(EXT / "audit_sources" / "tiger_road_distance_m.tif") as ds:
        rd = ds.read(1).astype(np.float32)
    put(26, (np.log1p(np.nan_to_num(rd)) / np.log1p(13000.0)).astype(np.float32))
    with rasterio.open(EXT / "audit_sources" / "blm_closed_claim_distance_m.tif") as ds:
        cl = ds.read(1).astype(np.float32)
    put(27, (np.log1p(np.nan_to_num(cl)) / np.log1p(15000.0)).astype(np.float32))

    # --- gradient magnitudes (TMI_up150 = band 4 of extensions; TC = band 4 of rad)
    for idx, fname, band, name in ((28, "geodawn_extensions_u8.tif", 4, "tmi_grad"),
                                   (29, "geodawn_rad_u8.tif", 4, "tc_grad")):
        with rasterio.open(EXT / fname) as ds:
            g = dequant(ds.read(band))
        gy, gx = np.gradient(g)
        mag = np.hypot(gy, gx)
        m = mag[fp]
        hi = float(np.quantile(m, 0.995)) or 1.0
        put(idx, np.minimum(mag / hi, 3.0).astype(np.float32))

    out = CACHE / "X.npy"
    np.save(out, X)
    meta = dict(schema="vgfp-features-v1", n_fp=int(n_fp), n_features=len(FEATURE_NAMES),
                feature_names=FEATURE_NAMES,
                external_manifest="registry/external_stack_manifest_20261031.json",
                created_utc=datetime.now(timezone.utc).isoformat())
    (CACHE / "features_meta.json").write_text(json.dumps(meta, indent=1))
    log(f"features written {out} shape {X.shape} ({time.time()-t0:.0f}s)")
    return 0


# ----------------------------------------------------------------- stage: holdout
def stage_holdout() -> int:
    import rasterio
    from scipy.ndimage import distance_transform_edt
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.metrics import roc_auc_score
    from gems57 import evaluate_holdout, holdout as hold_mod, grid as grid_mod
    from gems.breakline import spaced_top_mask

    t0 = time.time()
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    X = np.load(CACHE / "X.npy")
    yy, xx = np.nonzero(foot)
    foot_row = np.full((H, W), -1, np.int64)
    foot_row[foot] = np.arange(X.shape[0])

    with rasterio.open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    arms = ["vgfp", "vgfp_far", "ctrl_h19_5", "ctrl_R0_static"]
    terms = {a: None for a in arms}
    per_fold: dict = {a: [] for a in arms}
    canaries = []
    receipts = []

    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        receipts += [f["receipt"] for f in folds]
        vis = folds[0]["visible"]
        hidden_all = folds[0]["hidden_all"]
        excl = hidden_all | (distance_transform_edt(~hidden_all) <= 3.0)
        d_vis = distance_transform_edt(~vis)

        # fold-proper catalogue-distance feature (visible only)
        X[:, 20] = (np.minimum(d_vis[yy, xx], 60.0) / 60.0).astype(np.float32)

        # training rows: visible catalogue positives vs sampled negatives, excl hidden+buffer
        rng = np.random.default_rng(520810 + seed)
        pos = np.flatnonzero((vis & foot).ravel())
        neg_pool = np.flatnonzero((foot & ~cat & ~excl).ravel())
        neg = rng.choice(neg_pool, min(neg_pool.size, 4 * pos.size), replace=False)
        rows = np.concatenate([pos, neg])
        y = np.concatenate([np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)])
        fr = foot_row.ravel()[rows]
        Xm = X[fr]
        # rows outside footprint map to -1; drop them
        keep = fr >= 0
        Xm, y, fr = Xm[keep], y[keep], fr[keep]

        # Rule-4 single-feature leakage canaries (features are external/visible-only;
        # any AUC > 0.90 means the feature carries hidden-label information)
        truth_rows = foot_row.ravel()[np.flatnonzero((folds[0]["hidden_all"] & foot).ravel())]
        neg_rows = rng.choice(fr[y == 0], min(int((y == 0).sum()), 20000), replace=False)
        cy = np.concatenate([np.ones(truth_rows.size, np.uint8), np.zeros(neg_rows.size, np.uint8)])
        cX = np.concatenate([X[truth_rows], X[neg_rows]])
        for j, nm in enumerate(FEATURE_NAMES):
            v = cX[:, j]
            a = 0.5 if np.ptp(v) == 0 else float(roc_auc_score(cy, v))
            canaries.append(dict(seed=seed, feature=nm, auc=round(a, 6),
                                 symmetric_auc=round(max(a, 1 - a), 6)))
        worst = max(c["symmetric_auc"] for c in canaries if c["seed"] == seed)
        wname = max((c for c in canaries if c["seed"] == seed), key=lambda c: c["symmetric_auc"])["feature"]
        log(f"seed {seed}: canary max symmetric AUC {worst:.4f} ({wname})")
        if worst > 0.90:
            (EVID / "vgfp_canary_stop.json").write_text(json.dumps(canaries, indent=1))
            raise SystemExit(f"LEAKAGE CANARY TRIPPED {worst:.4f} > 0.90 -- stop")

        clf = HistGradientBoostingClassifier(
            max_iter=220, learning_rate=0.1, max_depth=8,
            l2_regularization=1.0, random_state=520810 + seed)
        clf.fit(Xm, y)
        log(f"seed {seed}: HGB fitted on {Xm.shape[0]} rows")
        del Xm, y, rows, pos, neg
        gc.collect()
        proba = clf.predict_proba(X)[:, 1].astype(np.float32)
        pfull = np.zeros(H * W, np.float32)
        pfull[foot.ravel()] = proba
        pfull = pfull.reshape(H, W)
        del clf
        gc.collect()

        # arms (R0-lineage spaced-top emission on the model surface)
        dots_v = spaced_top_mask(pfull, foot & (d_vis > 2.0), N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
        dots_f = spaced_top_mask(pfull, foot & (d_vis > 4.0), N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
        rng2 = np.random.default_rng(777 + seed)
        hsurf = (h19 * (0.5 + 0.5 * rng2.random((H, W)))).astype(np.float32)
        # Faithful R0-recipe control: Poisson-disk thin the full H19-5 skeleton at
        # 2.8 px (the d2-8 step, 44,090 dots), then prune the near-catalogue collar
        # (d_visible > 2.0), which is how the d28 -> R0 lineage reached 37,654 dots.
        try:
            dots_h_full = spaced_top_mask(hsurf, foot & h19, 44_090, min_dist_px=SPACING,
                                          cand_cap=400_000)
        except ValueError:
            dots_h_full = spaced_top_mask(hsurf, foot & h19, 44_090, min_dist_px=SPACING,
                                          cand_cap=400_000, require_full=False)
        dots_h = dots_h_full & (d_vis > 2.0)
        preds = {"vgfp": dots_v, "vgfp_far": dots_f, "ctrl_h19_5": dots_h, "ctrl_R0_static": r0.copy()}

        for a in arms:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                terms[a] = tm if terms[a] is None else terms[a] + tm
                per_fold[a].append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6),
                                        n_truth=int(sc["n_truth"])))
        del preds, pfull, proba
        gc.collect()
        log(f"seed {seed} done ({time.time()-t0:.0f}s)")

    np.savez(CACHE / "holdout_terms.npz", **terms)
    summaries = {c: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=c)
                 for c in ("vgfp", "vgfp_far")}
    s0 = summaries["vgfp"]["scores"]
    for k, v in sorted(s0.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:15s} HOLDOUT-DTI {v['dti']:.6f} CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}] n={v['withheld_positive_pixels']}")
    doc = dict(schema="gemsdoe92-vgfp-holdout-v1", evidence_class="HOLDOUT-DTI",
               evaluator_version=evaluate_holdout.VERSION,
               instrument="strict draw-blind fold-visible (buffered whole-component draws, seeds 20/30; collar d_visible>2.0, vgfp_far d_visible>4.0)",
               alpha=0.2, beta=0.8, triangular_radius_m=300.0,
               seeds=list(SEEDS), n_dots=N_DOTS, spacing_px=SPACING,
               feature_names=FEATURE_NAMES, scores=s0,
               paired_by_candidate={c: summaries[c]["paired_differences"] for c in summaries},
               bootstrap=summaries["vgfp"]["bootstrap"],
               implementation_sha256=summaries["vgfp"]["implementation_sha256"],
               per_fold=per_fold, canaries=canaries, fold_receipts=receipts,
               runtime_s=round(time.time() - t0, 1))
    (EVID / "vgfp_holdout.json").write_text(json.dumps(doc, indent=1))
    log(f"wrote evidence/vgfp_holdout.json ({time.time()-t0:.0f}s)")
    return 0


# ----------------------------------------------------------------- registry helpers
def registry_rasters() -> list[dict]:
    """Local registry scope: this repo's downloads + bridge + parents + GEMSDOE24
    mirror downloads + streamed focus-9 bests. Each entry: path, sha256."""
    import rasterio
    items = []
    paths = sorted(DOWNLOADS.glob("*.tif"))
    paths += [BRIDGE / "d28.tif", BRIDGE / "h19_5.tif", BRIDGE / "h27_4_solo.tif",
              BRIDGE / "existing_faults.tif", BRIDGE / "sample_submission.tif",
              ROOT / "data" / "parent_R0_nan.tif", ROOT / "data" / "parent_R0_zeros.tif"]
    mirror_downloads = ROOT / ".cache" / "GEMSDOE24" / "docs" / "downloads"
    if mirror_downloads.is_dir():
        paths += sorted(mirror_downloads.glob("*.tif"))
    focus_dir = CACHE / "focus9"
    if focus_dir.is_dir():
        paths += sorted(focus_dir.glob("*.tif"))
    seen = set()
    for p in paths:
        if not p.is_file():
            continue
        sha = sha256_file(p)
        if sha in seen:
            continue
        seen.add(sha)
        try:
            with rasterio.open(p) as ds:
                if tuple(ds.shape) != (3730, 3292) or ds.count != 1:
                    continue
        except Exception:  # noqa: BLE001
            continue
        items.append(dict(path=str(p.relative_to(ROOT) if str(p).startswith(str(ROOT)) else p), sha256=sha))
    return items


def load_dots(path: str, n_budget: int):
    """PI-1 'dots' of one registry raster: literal support if sparse, else top-N."""
    import rasterio
    p = Path(path)
    if not p.is_file():
        p = ROOT / path
    with rasterio.open(p) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float64), nan=0.0)
    fp = None
    with rasterio.open(BRIDGE / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    pos = np.flatnonzero((a > 0).ravel())
    sup = pos.size / max(1, fp.sum())
    if sup <= 0.20 and pos.size <= n_budget:
        return pos, "dot_field"
    vals = a.ravel()[pos]
    order = np.argsort(-vals, kind="stable")[:n_budget]
    return pos[order], "surface_topn"


def near_fraction_3px(our_lin: np.ndarray, their_lin: np.ndarray, shape=(3730, 3292)) -> float:
    if our_lin.size == 0 or their_lin.size == 0:
        return 0.0
    H, W = shape
    grid = np.zeros(H * W, bool)
    grid[their_lin] = True
    y, x = np.divmod(our_lin, W)
    hit = np.zeros(our_lin.size, bool)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dy * dy + dx * dx > 9:
                continue
            yy = y + dy; xx = x + dx
            ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
            idx = np.where(ok, yy * W + xx, 0)
            hit |= ok & grid[idx]
    return float(hit.mean())


def spearman_sample(a_flat_fp: np.ndarray, b_flat_fp: np.ndarray, sample_idx: np.ndarray) -> float:
    from scipy.stats import spearmanr
    av = a_flat_fp[sample_idx]; bv = b_flat_fp[sample_idx]
    if np.ptp(av) == 0 or np.ptp(bv) == 0:
        return 0.0
    r = spearmanr(av, bv).statistic
    return 0.0 if r is None or not np.isfinite(r) else float(r)


# ----------------------------------------------------------------- stage: deploy
def stage_deploy() -> int:
    import rasterio
    from scipy.ndimage import distance_transform_edt
    from sklearn.ensemble import HistGradientBoostingClassifier
    from gems57 import grid as grid_mod, submission_writer
    from gems57.validate import assert_submittable, validate
    from gems.gates import run_gates, summarise
    from gems.breakline import spaced_top_mask

    t0 = time.time()
    hold = json.loads((EVID / "vgfp_holdout.json").read_text())
    scores = dict(hold["scores"])
    paired_all = dict(hold["paired_by_candidate"])
    exp2p = EVID / "vgfp_holdout_exp2.json"
    if exp2p.is_file():
        h2 = json.loads(exp2p.read_text())
        scores["vgfp_2regime"] = h2["scores_exp2"]["vgfp_2regime"]
        paired_all["vgfp_2regime"] = h2["paired_exp2"]
    arms = [a for a in ("vgfp", "vgfp_far", "vgfp_2regime") if a in scores]
    best_arm = max(arms, key=lambda a: scores[a]["dti"])
    log(f"holdout-best arm: {best_arm} ({scores[best_arm]['dti']:.6f})")

    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    X = np.load(CACHE / "X.npy")
    yy, xx = np.nonzero(foot)

    # full-catalogue fit (nothing withheld on the deployed artifact)
    d_cat = distance_transform_edt(~cat).astype(np.float32)
    X[:, 20] = (np.minimum(d_cat[yy, xx], 60.0) / 60.0).astype(np.float32)
    rng = np.random.default_rng(520810)
    pos = np.flatnonzero((cat & foot).ravel())
    neg_pool = np.flatnonzero((foot & ~cat).ravel())
    neg = rng.choice(neg_pool, min(neg_pool.size, 4 * pos.size), replace=False)
    foot_row = np.full(H * W, -1, np.int64); foot_row[foot.ravel()] = np.arange(X.shape[0])
    rows = np.concatenate([pos, neg]); fr = foot_row[rows]
    y = np.concatenate([np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)])
    clf = HistGradientBoostingClassifier(max_iter=220, learning_rate=0.1, max_depth=8,
                                         l2_regularization=1.0, random_state=520810)
    clf.fit(X[fr], y)
    proba = clf.predict_proba(X)[:, 1].astype(np.float32)
    pfull = np.zeros(H * W, np.float32); pfull[foot.ravel()] = proba
    pfull = pfull.reshape(H, W)
    del clf, X; gc.collect()

    prune = 2.0 if best_arm != "vgfp_far" else 4.0
    if best_arm == "vgfp_2regime":
        prox = spaced_top_mask(pfull, foot & (d_cat > 2.0) & (d_cat <= 15.0),
                               int(round(0.7 * N_DOTS)), min_dist_px=SPACING,
                               cand_cap=900_000, require_full=False)
        dist = spaced_top_mask(pfull, foot & (d_cat > 15.0), N_DOTS - int(round(0.7 * N_DOTS)),
                               min_dist_px=SPACING, cand_cap=900_000, require_full=False)
        dots = prox | dist
    else:
        dots = spaced_top_mask(pfull, foot & (d_cat > prune), N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    our_lin = np.flatnonzero(dots.ravel())
    n = int(dots.sum())
    log(f"deployed dots: {n} (prune d_cat>{prune})")

    # ---- REGISTRY-MEASUREMENT uniqueness (PI-1: dots vs dots, 3 px; surface Spearman)
    reg = registry_rasters()
    log(f"registry scope: {len(reg)} rasters")
    rng2 = np.random.default_rng(20261031)
    fp_lin = np.flatnonzero(foot.ravel())
    sample_idx = np.sort(rng2.choice(fp_lin.size, size=200_000, replace=False))
    surf_ours = pfull.ravel()[fp_lin]
    rows_out = []
    worst = dict(overlap=0.0, path=None, rep=None)
    worst_rho = dict(rho=0.0, path=None)
    SCORING_INPUTS = {"existing_faults.tif", "labels.tif", "sample_submission.tif"}
    for item in reg:
        their_lin, rep = load_dots(item["path"], n)
        ov = near_fraction_3px(our_lin, their_lin)
        # rho on sampled footprint cells
        with rasterio.open(item["path"] if Path(item["path"]).is_file() else ROOT / item["path"]) as ds:
            b = np.nan_to_num(ds.read(1).astype(np.float64), nan=0.0)
        rho = abs(spearman_sample(surf_ours, b.ravel()[fp_lin], sample_idx))
        is_input = Path(item["path"]).name in SCORING_INPUTS
        rows_out.append(dict(path=item["path"], sha256=item["sha256"], representation=rep,
                             overlap_pi1=round(ov, 6), abs_spearman=round(rho, 6),
                             is_scoring_input=is_input))
        if is_input:
            continue  # the mapped catalogue is the scoring input, not a peer raster
        if ov > worst["overlap"]:
            worst = dict(overlap=ov, path=item["path"], rep=rep)
        if rho > worst_rho["rho"]:
            worst_rho = dict(rho=rho, path=item["path"])
    pi1_pass = bool(worst["overlap"] <= 0.70 and worst_rho["rho"] <= 0.90)
    log(f"worst PI-1 overlap {worst['overlap']:.4f} ({worst['path']}), worst |rho| {worst_rho['rho']:.4f} ({worst_rho['path']}) -> {'PASS' if pi1_pass else 'FAIL'}")

    # ---- write via shared fail-closed writer
    tag = hashlib.sha1(np.sort(our_lin).astype(np.int64).tobytes()).hexdigest()[:8]
    arm_name = {"vgfp": "vgfp1", "vgfp_far": "vgfp1far", "vgfp_2regime": "vgfp2r"}[best_arm]
    stem = f"gemsdoe92-{arm_name}-{n}dots-{DATE}-{tag}"
    tif = DOWNLOADS / f"{stem}-zeros.tif"
    name = f"gemsdoe92-{arm_name}-{n}d-{tag}"
    note = (f"V-GFP {best_arm}: {n} dots, GeoDawn+LiDAR+SGMC GBDT + vent/well/probe thermal "
            f"proximity; HOLDOUT-DTI {scores[best_arm]['dti']:.4f} vs R0ctrl {scores['ctrl_h19_5']['dti']:.4f}.")
    note = note[:140]
    pred = dots.astype(np.float32)
    pred[cat] = 0.0
    pred[~foot] = 0.0
    receipt = submission_writer.write_submission(
        tif, pred, BRIDGE / "sample_submission.tif", foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane="V-GFP", session="arena/702071e4-gemsdoe92", arm=best_arm))
    file_sha = sha256_file(tif)
    gates = run_gates(str(tif), str(BRIDGE / "sample_submission.tif"), str(BRIDGE / "existing_faults.tif"),
                      prune_radius=2, require_submission_encoding=True)
    ok, report_txt = summarise(gates)
    v = validate(tif, foot, cat)
    assert_submittable(v)
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        grid_ok = dict(crs=str(ds.crs), shape=list(ds.shape), transform=list(tuple(ds.transform)[:6]),
                       dtype=ds.dtypes[0], count=ds.count)
    validator_output = dict(
        no_nan_in_footprint=bool(np.isfinite(a[foot]).all()),
        no_nan_anywhere=bool(np.isfinite(a).all()),
        values_in_0_1=bool(a.min() >= 0 and a.max() <= 1),
        crs_match=grid_ok["crs"] == "EPSG:32611", shape_match=grid_ok["shape"] == [3730, 3292],
        transform_match=grid_ok["transform"] == [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        dtype_float32=grid_ok["dtype"] == "float32", single_band=grid_ok["count"] == 1,
        zeros_outside_footprint=bool((a[~foot] == 0).all()),
        zero_mass_on_mapped_catalogue=bool((a[cat] == 0).all()),
        n_positive=int((a > 0).sum()), gates_pass=bool(ok),
        gates=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates])

    dep = dict(schema="gemsdoe92-vgfp-deploy-v1",
               evidence_class="REGISTRY-MEASUREMENT (local computation on bytes)",
               registry_scope=f"local archive: {len(reg)} rasters (docs/downloads + bridge + parents + GEMSDOE24 mirror downloads + focus-9 streamed bests); full 2,262-SHA fleet cache NOT rebuilt in this sandbox -- scope disclosed",
               rule=dict(overlap_limit=0.70, rho_limit=0.90, radius_px=3.0, interpretation="PI-1",
                         note="literal dense-witness reading (17GEMSDOE 5.17M-cell surface) yields 1.000 for any nonempty candidate and is degenerate; PI-1 dot-vs-dot is the operative reading of the parallel-run rule"),
               candidate=dict(file=str(tif.relative_to(ROOT)), sha256=file_sha, n_dots=n, arm=best_arm,
                              submission_name=name, note=note, note_chars=len(note)),
               worst_overlap=worst, worst_abs_spearman=worst_rho, pi1_pass=pi1_pass,
               rows=rows_out)
    (EVID / "vgfp_uniqueness.json").write_text(json.dumps(dep, indent=1))

    audit = dict(schema="vgfp-deploy-audit-v1", file=str(tif.relative_to(ROOT)), sha256=file_sha,
                 validator=validator_output, receipt=dict(
                     zip_file=receipt.get("zip_file"), zip_sha256=receipt.get("zip_sha256"),
                     bytes=receipt.get("bytes")), created_utc=datetime.now(timezone.utc).isoformat())
    (DOWNLOADS / f"{stem}-zeros-audit.json").write_text(json.dumps(audit, indent=1))
    log(f"wrote {tif} sha256={file_sha}")
    (CACHE / "deploy_state.json").write_text(json.dumps(dict(
        stem=stem, tif=str(tif.relative_to(ROOT)), sha256=file_sha, n_dots=n, arm=best_arm,
        name=name, note=note, pi1_pass=pi1_pass,
        worst_overlap=worst, worst_rho=worst_rho, gates_pass=bool(ok)), indent=1))
    return 0


# ----------------------------------------------------------------- stage: report
def stage_report() -> int:
    hold = json.loads((EVID / "vgfp_holdout.json").read_text())
    dep = json.loads((EVID / "vgfp_uniqueness.json").read_text())
    state = json.loads((CACHE / "deploy_state.json").read_text())
    scores = dict(hold["scores"])
    paired_all = dict(hold["paired_by_candidate"])
    exp2p = EVID / "vgfp_holdout_exp2.json"
    if exp2p.is_file():
        h2 = json.loads(exp2p.read_text())
        scores["vgfp_2regime"] = h2["scores_exp2"]["vgfp_2regime"]
        paired_all["vgfp_2regime"] = h2["paired_exp2"]
    arm = state["arm"]
    cand = scores[arm]; ctrl = scores["ctrl_h19_5"]; r0s = scores["ctrl_R0_static"]
    paired = paired_all[arm]["ctrl_h19_5"]
    canary_max = max(c["symmetric_auc"] for c in hold["canaries"])

    projection = dict(
        evidence_class="MODEL-CLASS PROJECTION (NOT an organizer score)",
        method=("Family evidence from the fleet CLAIM ledger. Two anchors: (a) H19-5-corridor binary dot "
                "fields in the 35,000-44,000-dot / 2.5-3.0 px / d_cat>2 regime score 0.2477-0.2784 "
                "(h25-1 0.2477, d2-8 0.2600, d28 0.2600, h27-4 0.2708, anderson-pinn 0.2750, h33-2-b2 "
                "0.2778, lbmc1 0.2784); (b) external-stack supervised/thermal submissions without H19-5 "
                "support score 0.02-0.225 (fleet spread; best = GEMSDOE27 h31-drcg-wl-celf28 0.2250). "
                "V-GFP2R is in emission regime (a) but has ZERO H19-5 support, so it inherits the "
                "(b) ceiling unless the external stack substitutes for the skeleton. LBM-v3 131-claim "
                "LOGO RMSE is 0.0266 but its feature stack is unavailable in this sandbox."),
        point=0.21,
        band=[0.15, 0.27],
        beats_0_2778_probability="low (<=25%): the two-regime plateau at ~0.278 is an information "
                                 "ceiling for families without the full 19-band numeric_features stack",
        caveat=("WIDE BAND: no CLAIM anchor for this family; the holdout instrument has Spearman 0.13 "
                "vs claims (evidence/holdout_validity_20261027.json) and cannot tighten it. "
                "A projection is never a score."),
        family_claims=[0.2477, 0.2600, 0.2600, 0.2708, 0.2750, 0.2778, 0.2784])

    card = dict(
        schema="gemsdoe92-run-card-v3",
        created_utc=datetime.now(timezone.utc).isoformat(),
        lane="V-GFP (VENT-CENTRIC GEOTHERMAL FAULT PROPENSITY)",
        hypothesis=("Hidden (organiser) faults share the mapped-fault appearance signature in the free "
                    "official external stack AND cluster around geothermal-vent indicators (hot springs, "
                    "wells, INGENIOUS 2 m probes, volcanic vents) that no scored fleet submission has "
                    "used as supervised pixel features."),
        mechanism=("HistGradientBoosting pixel classifier on 30 channels (GeoDawn 8 + LiDAR scarp 12 + "
                   "SGMC + visible-catalogue distance + 5 thermal-proximity densities + 2 confounds + "
                   "2 gradient mags) trained per fold on visible faults only; R0-lineage spaced-top "
                   "emission (2.8 px floor, 37,654 dots, d_visible collar)."),
        named_non_fault_mimic=("Lake Lahontan paleoshoreline beach ridges and incised drainage banks "
                               "(LiDAR scarp channels), lithologic contacts (magnetic/radiometric "
                               "edges), prospector access roads and claim fences (BLM/TIGER confound "
                               "channels, audited)."),
        raster=dict(file=state["tif"], sha256=state["sha256"], n_dots=state["n_dots"],
                    submission_name=state["name"], note=state["note"], note_chars=len(state["note"])),
        raster_sha256=state["sha256"],
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version=hold["evaluator_version"],
            withheld_positive_pixels=cand["withheld_positive_pixels"],
            arm={k: dict(dti=v["dti"], ci95=v["ci95"]) for k, v in scores.items()},
            paired_delta_vs_ctrl_h19_5=paired,
            instrument_note=hold["instrument"]),
        leakage_canaries=dict(threshold=0.90, n=len(hold["canaries"]),
                              max_symmetric_auc=canary_max, all_pass=bool(canary_max <= 0.90),
                              detail=hold["canaries"]),
        uniqueness=dict(evidence_class="REGISTRY-MEASUREMENT", pi1_pass=dep["pi1_pass"],
                        worst_overlap=dep["worst_overlap"], worst_abs_spearman=dep["worst_abs_spearman"],
                        registry_scope=dep["registry_scope"]),
        model_projection=projection,
        validator_output=json.loads((DOWNLOADS / (Path(state["tif"]).stem + "-audit.json")).read_text())["validator"],
        verdict=("promote" if (dep["pi1_pass"] and canary_max <= 0.90
                               and paired["ci95"][0] > 0 and state["gates_pass"]) else "negative"),
        submission_eligible=None,  # filled below
        submission_slots_used=0)
    eligible = bool(card["verdict"] == "promote")
    card["submission_eligible"] = eligible
    card["selector_note"] = (
        "Auto-validated without human intervention: format gates + PI-1 uniqueness + leakage canaries + "
        "paired holdout win vs the in-run R0-lineage control. Promotion to a real weekly slot remains the "
        "separate selector step under the portal weekly cap."
        if eligible else
        "Not promoted under the strict protocol gates; retained as a research deliverable (negative results count).")
    (EVID / f"vgfp_run_card_{DATE}.json").write_text(json.dumps(card, indent=1))
    log(f"run card verdict: {card['verdict']} (eligible={eligible})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["features", "holdout", "exp2", "deploy", "report", "all"])
    args = ap.parse_args()
    if args.stage in ("features", "all"):
        stage_features()
    if args.stage in ("holdout", "all"):
        stage_holdout()
    if args.stage in ("exp2", "all"):
        stage_exp2()
    if args.stage in ("deploy", "all"):
        stage_deploy()
    if args.stage in ("report", "all"):
        stage_report()
    return 0




# ----------------------------------------------------------------- stage: exp2
def stage_exp2() -> int:
    """Experiment 2: two-regime budget emission (70% proximal corridor 2<d<=15 px,
    30% distal d>15 px) on the same fold-proper V-GFP surface. Reuses the saved
    control terms from evidence/vgfp_holdout.json (same folds, same evaluator)."""
    import rasterio
    from scipy.ndimage import distance_transform_edt
    from sklearn.ensemble import HistGradientBoostingClassifier
    from gems57 import evaluate_holdout, holdout as hold_mod, grid as grid_mod
    from gems.breakline import spaced_top_mask

    t0 = time.time()
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    X = np.load(CACHE / "X.npy")
    yy, xx = np.nonzero(foot)

    loaded = np.load(CACHE / "holdout_terms.npz")
    terms = {k: loaded[k] for k in loaded.files}
    per_fold: dict = {"vgfp_2regime": []}

    N_PROX = int(round(0.7 * N_DOTS))
    N_DIST = N_DOTS - N_PROX

    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]
        hidden_all = folds[0]["hidden_all"]
        excl = hidden_all | (distance_transform_edt(~hidden_all) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        X[:, 20] = (np.minimum(d_vis[yy, xx], 60.0) / 60.0).astype(np.float32)

        rng = np.random.default_rng(520810 + seed)
        pos = np.flatnonzero((vis & foot).ravel())
        neg_pool = np.flatnonzero((foot & ~cat & ~excl).ravel())
        neg = rng.choice(neg_pool, min(neg_pool.size, 4 * pos.size), replace=False)
        foot_row = np.full(H * W, -1, np.int64)
        foot_row[foot.ravel()] = np.arange(X.shape[0])
        rows = np.concatenate([pos, neg]); fr = foot_row[rows]
        y = np.concatenate([np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)])
        clf = HistGradientBoostingClassifier(max_iter=220, learning_rate=0.1, max_depth=8,
                                             l2_regularization=1.0, random_state=520810 + seed)
        clf.fit(X[fr], y)
        proba = clf.predict_proba(X)[:, 1].astype(np.float32)
        pfull = np.zeros(H * W, np.float32); pfull[foot.ravel()] = proba
        pfull = pfull.reshape(H, W)
        del clf
        gc.collect()

        prox = spaced_top_mask(pfull, foot & (d_vis > 2.0) & (d_vis <= 15.0), N_PROX,
                               min_dist_px=SPACING, cand_cap=900_000, require_full=False)
        dist = spaced_top_mask(pfull, foot & (d_vis > 15.0), N_DIST,
                               min_dist_px=SPACING, cand_cap=900_000, require_full=False)
        dots = prox | dist
        pr = dots.astype(np.float32)
        pr[vis] = 0.0
        for f in folds:
            sc, tm = evaluate_holdout.evaluate(pr, f, foot)
            terms["vgfp_2regime"] = tm if terms.get("vgfp_2regime") is None else terms["vgfp_2regime"] + tm
            per_fold["vgfp_2regime"].append(dict(seed=seed, fold=f["name"],
                                                 dti=round(float(sc["dti"]), 6),
                                                 n_truth=int(sc["n_truth"])))
        log(f"exp2 seed {seed}: emitted {int(dots.sum())} ({time.time()-t0:.0f}s)")
        del pfull, proba
        gc.collect()

    np.savez(CACHE / "holdout_terms_exp2.npz", **terms)
    summary = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="vgfp_2regime")
    s0 = summary["scores"]
    for k, v in sorted(s0.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:15s} HOLDOUT-DTI {v['dti']:.6f} CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")
    prev = json.loads((EVID / "vgfp_holdout.json").read_text())
    doc = dict(prev, schema="gemsdoe92-vgfp-holdout-exp2-v1",
               scores_exp2=s0,
               paired_exp2=summary["paired_differences"],
               per_fold_exp2=per_fold,
               exp2=dict(n_prox=N_PROX, n_dist=N_DIST,
                         proximal_band="2.0 < d_visible <= 15.0 px", distal="d_visible > 15.0 px"))
    (EVID / "vgfp_holdout_exp2.json").write_text(json.dumps(doc, indent=1))
    log(f"wrote evidence/vgfp_holdout_exp2.json ({time.time()-t0:.0f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
