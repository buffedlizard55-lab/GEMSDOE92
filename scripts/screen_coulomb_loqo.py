#!/usr/bin/env python3
"""Pre-placement leakage canary & local surface registry screen for COULOMB-LOQO.

Enforces Parallel-Run Protocol Rules 1, 2, and 4 BEFORE building any submission TIF:
1. Verifies SHA-256 checksums of all pinned stack inputs.
2. Computes the 24 catalogue-free physical features (Groups A-E) and caches compact
   footprint arrays inside gitignored ``.cache/gems_inputs/`` for exact reuse.
3. Fits 4-quadrant Leave-One-Quadrant-Out (LOQO, >= 1.2 km guard band) models:
   - ``P_full`` (all 24 features, Groups A-E)
   - ``P_topo`` (8 Group-A topographic/cover features only -- pre-registered ablation)
   - ``P_draw20`` / ``P_draw30`` (strict draw-blind models trained ONLY on ``fold['visible']``
     in ``quad != q``, completely excluding ``hidden_all`` everywhere).
4. Tests every raw band, derived feature, and LOQO surface individually on the buffered
   holdout folds (Rule 4 leakage canary: ``symmetric ROC AUC <= 0.90``).
5. Evaluates the continuous pre-placement surface ``S_full`` BEFORE placement against
   every unique local registry raster (Rule 1: ``|Spearman rho| <= 0.90`` AND spaced
   1D-crest top-37,654 3-px forward overlap ``<= 0.70``). Fails closed otherwise.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests, write_tif  # noqa: E402
from gems.coulomb_loqo import (  # noqa: E402
    FEATURE_NAMES,
    TOPO_ONLY_INDICES,
    build_crest_surface,
    compute_feature_stack,
    fit_predict_loqo,
    gdr_blind_thermal_features,
    spaced_top_mask,
)
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, holdout  # noqa: E402

CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "coulomb_loqo_cache.npz"
SURFACE_TIF = CACHE_DIR / "coulomb_loqo_S_full_surface.tif"
OUT_JSON = ROOT / "evidence" / "coulomb_loqo_screen.json"


def symmetric_auc(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    auc = float(roc_auc_score(y_true, scores))
    return auc, float(max(auc, 1.0 - auc))


def collect_unique_local_rasters(foot: np.ndarray) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = [
        ("parent_R0_zeros.tif", ROOT / "data/parent_R0_zeros.tif"),
        ("h19_5.tif", ROOT / "data/bridge/h19_5.tif"),
        ("d28.tif", ROOT / "data/bridge/d28.tif"),
        ("h27_4_solo.tif", ROOT / "data/bridge/h27_4_solo.tif"),
        ("d15_lineage.tif", CACHE_DIR / "lineage/calib_d15_02477.tif"),
    ]
    for folder in (ROOT / "docs/downloads", ROOT / "releases"):
        if not folder.is_dir():
            continue
        for p in sorted(folder.glob("*.tif")):
            if "COULOMBLOQO" in p.name:
                continue
            candidates.append((f"{folder.name}/{p.name}", p))

    seen_masks: set[bytes] = set()
    unique_list: list[tuple[str, Path]] = []
    for label, p in candidates:
        if not p.is_file():
            continue
        with rasterio.open(p) as ds:
            arr = ds.read(1)
        pos = (np.nan_to_num(arr, nan=0.0) > 0) & foot
        if not pos.any():
            continue
        key = np.packbits(pos).tobytes()
        if key in seen_masks:
            continue
        seen_masks.add(key)
        unique_list.append((label, p))
    return unique_list


def main() -> int:
    t0 = time.time()
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(CACHE_DIR / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    quad = holdout.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)

    print("1. Loading verified 19-band stack + GeoDAWN radiometrics + GDR #1391...", flush=True)
    raw_band_map = {
        2: "B02_rtp",
        4: "B04_geod_2ndinv",
        5: "B05_iso_grav_anom_slope",
        7: "B07_geod_shearrate",
        8: "B08_geod_dilaterate",
        11: "B11_iso_grav_anom_vg",
        12: "B12_det_elev",
        13: "B13_iso_grav_anom",
        15: "B15_depth_to_base_surf",
        17: "B17_cond_surf",
        18: "B18_iso_grav_anom_hg",
        19: "B19_det_elev_slope",
    }
    bands: dict[int, np.ndarray] = {}
    with rasterio.open(paths["training_features"]) as ds:
        profile = ds.profile.copy()
        for b in raw_band_map:
            bands[b] = ds.read(b, masked=True).filled(np.nan).astype(np.float32)

    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
        rad_u = ds.read(3)

    valid_base = (
        foot
        & np.isfinite(bands[12]) & (bands[12] > -1e30)
        & np.isfinite(bands[19]) & (bands[19] > -1e30)
        & np.isfinite(bands[2]) & (bands[2] > -1e30)
    )
    gdr_res = gdr_blind_thermal_features(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=14.0
    )

    # Build buffered holdout folds for canary sampling BEFORE deleting raw bands
    folds = []
    draws_by_seed = {}
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        draws_by_seed[seed] = draw

    rng = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & (~cat))
        n_neg = min(len(neg), max(1, 2 * len(pos)))
        neg_sel = rng.choice(neg, size=n_neg, replace=False) if len(neg) > n_neg else neg
        idx_parts.extend((pos, neg_sel))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg_sel), np.uint8)))
    y_canary = np.concatenate(y_parts)
    flat_canary_idx = np.concatenate(idx_parts)

    canaries: dict[str, dict[str, float]] = {}
    for b, bname in raw_band_map.items():
        vals = np.nan_to_num(bands[b].ravel()[flat_canary_idx], nan=0.0, posinf=0.0, neginf=0.0)
        vals = np.where(vals <= -1e30, 0.0, vals)
        auc, sym = symmetric_auc(y_canary, vals)
        canaries[bname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}

    for rname, rarr in (("RAD_K", rad_k), ("RAD_Th", rad_th), ("RAD_U", rad_u)):
        vals = rarr.ravel()[flat_canary_idx].astype(np.float32)
        auc, sym = symmetric_auc(y_canary, vals)
        canaries[rname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}

    print("2. Computing 24 catalogue-free physical features (Groups A-E)...", flush=True)
    stack = compute_feature_stack(
        rtp=bands[2],
        geod_2ndinv=bands[4],
        grav_slope=bands[5],
        geod_shearrate=bands[7],
        geod_dilaterate=bands[8],
        grav_vg=bands[11],
        det_elev=bands[12],
        grav_anom=bands[13],
        depth_to_base=bands[15],
        cond_surf=bands[17],
        grav_hg=bands[18],
        det_elev_slope=bands[19],
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_feat=gdr_res["plume_feat"],  # type: ignore[arg-type]
        footprint=foot,
    )
    del bands, rad_k, rad_th, rad_u

    X_foot = stack["X_foot"]
    valid = stack["valid"]
    l_topo = stack["L_topo"]
    l_sub = stack["L_sub"]

    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    canary_foot_rows = foot_row_map.ravel()[flat_canary_idx]

    for j, fname in enumerate(FEATURE_NAMES):
        vals = X_foot[canary_foot_rows, j]
        auc, sym = symmetric_auc(y_canary, vals)
        canaries[fname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}

    print("3. Fitting 4-quadrant Leave-One-Quadrant-Out (LOQO) models...", flush=True)
    p_full = fit_predict_loqo(X_foot, foot, valid, quad, cat, guard_px=12, neg_buffer_px=5.0)
    p_topo = fit_predict_loqo(
        X_foot, foot, valid, quad, cat,
        feature_cols=TOPO_ONLY_INDICES, guard_px=12, neg_buffer_px=5.0,
    )

    # Strict draw-blind LOQO models (trained strictly on fold['visible'] in quad != q,
    # excluding hidden_all + 3-px context buffer from both positives and negatives)
    p_draw: dict[int, np.ndarray] = {}
    for seed in (20, 30):
        f0 = draws_by_seed[seed][0]
        vis = f0["visible"]
        excl = distance_transform_edt(~f0["hidden_all"]) <= 3.0
        p_draw[seed] = fit_predict_loqo(
            X_foot, foot, valid, quad, vis,
            excluded_mask=excl, guard_px=12, neg_buffer_px=5.0,
        )

    crest_full = build_crest_surface(p_full, l_topo, l_sub, valid, sub_weight=0.80)
    crest_topo = build_crest_surface(p_topo, l_topo, None, valid)
    s_full = crest_full["S_crest"]
    s_topo = crest_topo["S_crest"]

    # Canary check on composite LOQO surfaces (including strict draw-blind OOF surface)
    draw_oof_vals_parts = []
    for seed in (20, 30):
        s_d = build_crest_surface(p_draw[seed], l_topo, l_sub, valid, sub_weight=0.80)["S_crest"]
        for fold in draws_by_seed[seed]:
            pos = np.flatnonzero(fold["truth"] & foot)
            neg = np.flatnonzero(fold["region"] & foot & (~cat))
            # Match exact deterministic canary evaluation on draw-blind predictions
            draw_oof_vals_parts.append((
                np.concatenate([np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)]),
                np.concatenate([s_d.ravel()[pos], s_d.ravel()[neg]]),
            ))
    y_all_d = np.concatenate([a for a, _ in draw_oof_vals_parts])
    v_all_d = np.concatenate([b for _, b in draw_oof_vals_parts])
    auc_d, sym_d = symmetric_auc(y_all_d, v_all_d)
    canaries["LOQO_draw_blind_S_full"] = {"auc": round(auc_d, 6), "symmetric_auc": round(sym_d, 6)}

    for sname, sarr in (("LOQO_P_full", p_full), ("LOQO_S_full", s_full), ("LOQO_S_topo", s_topo)):
        vals = sarr.ravel()[flat_canary_idx]
        auc, sym = symmetric_auc(y_canary, vals)
        canaries[sname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6)}

    max_sym_auc = max(v["symmetric_auc"] for v in canaries.values())
    max_sym_feat = max(canaries, key=lambda k: canaries[k]["symmetric_auc"])
    print(f"   Max canary symmetric AUC = {max_sym_auc:.6f} ({max_sym_feat})", flush=True)
    if max_sym_auc > 0.90:
        raise SystemExit(f"LEAKAGE CANARY STOP: {max_sym_feat} symmetric AUC = {max_sym_auc:.6f} > 0.90")

    # Save continuous pre-placement surface GeoTIFF (for audit_public_registry.py --surface)
    # and cached arrays for build/report scripts
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ref_ds:
        ref_prof = ref_ds.profile.copy()
    write_tif(SURFACE_TIF, ref_prof, foot, s_full, nan_outside=False)

    np.savez_compressed(
        NPZ_CACHE,
        valid=valid,
        L_topo=l_topo,
        L_sub=l_sub,
        P_full=p_full,
        P_topo=p_topo,
        P_draw20=p_draw[20],
        P_draw30=p_draw[30],
        S_full=s_full,
        S_topo=s_topo,
    )

    print("4. Checking pre-placement continuous surface uniqueness vs all local rasters...", flush=True)
    pool_1d = foot & valid & (d_cat > 2.0) & crest_full["ridge_1d"]
    top_preview = spaced_top_mask(s_full, pool_1d, 37654, min_dist_px=2.8)
    s_foot = s_full[foot]
    # Subsample 250k footprint cells deterministically for fast exact rank correlation check,
    # and full footprint on top candidates
    sub_idx = np.linspace(0, int(foot.sum()) - 1, 250_000, dtype=np.int64)
    s_sub = s_foot[sub_idx]

    local_rasters = collect_unique_local_rasters(foot)
    surf_rows = []
    for label, rpath in local_rasters:
        with rasterio.open(rpath) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0)
        r_sub = raw[foot][sub_idx]
        rho = float(spearmanr(s_sub, r_sub).statistic) if np.std(r_sub) > 0 else 0.0
        theirs = (raw > 0) & foot
        d_theirs = distance_transform_edt(~theirs)
        fwd = float((d_theirs[top_preview] <= 3.0).mean())
        surf_rows.append({
            "registry_raster": label,
            "their_positive_pixels": int(theirs.sum()),
            "spearman_rho_250k": round(rho, 6),
            "top37654_1d_forward_3px_overlap": round(fwd, 6),
        })
        del raw, theirs, d_theirs

    worst_rho_row = max(surf_rows, key=lambda r: abs(r["spearman_rho_250k"]))
    worst_ov_row = max(surf_rows, key=lambda r: r["top37654_1d_forward_3px_overlap"])
    # Compute exact full-footprint Spearman on the worst-rho raster
    worst_label = worst_rho_row["registry_raster"]
    worst_path = dict(local_rasters)[worst_label]
    with rasterio.open(worst_path) as ds:
        exact_worst_rho = float(spearmanr(s_foot, np.nan_to_num(ds.read(1), nan=0.0)[foot]).statistic)

    surf_dup = bool(
        abs(exact_worst_rho) > 0.90
        or worst_ov_row["top37654_1d_forward_3px_overlap"] > 0.70
    )
    print(
        f"   Checked {len(surf_rows)} unique local rasters: "
        f"worst |Spearman| = {abs(exact_worst_rho):.6f} ({worst_label}), "
        f"worst top-37,654 1D overlap = {worst_ov_row['top37654_1d_forward_3px_overlap']:.6f} "
        f"({worst_ov_row['registry_raster']})",
        flush=True,
    )
    if surf_dup:
        raise SystemExit("PRE-PLACEMENT SURFACE DUPLICATE STOP TRIGGERED")

    out = {
        "schema": "gemsdoe92-coulomb-loqo-screen.v1",
        "lane": "COULOMB-LOQO",
        "elapsed_seconds": round(time.time() - t0, 2),
        "gdr_summary": {
            "n_thermal_pixels": gdr_res["n_thermal_pixels"],
            "n_blind_geotherm_pixels": gdr_res["n_blind_geotherm_pixels"],
            "dist_known_fault_px_dropped": True,
        },
        "surface_tif_sha256": sha256_file(SURFACE_TIF),
        "n_1d_crest_candidates_off_cat2": int(pool_1d.sum()),
        "leakage_canaries": {
            "evidence_class": "HOLDOUT-CANARY (buffered_component_draw seeds 20+30, 22,663 positives)",
            "threshold_symmetric_auc": 0.90,
            "all_pass": bool(max_sym_auc <= 0.90),
            "max_symmetric_auc": round(max_sym_auc, 6),
            "max_symmetric_feature": max_sym_feat,
            "features": canaries,
        },
        "preplacement_surface_uniqueness": {
            "evidence_class": "REGISTRY-MEASUREMENT (local cross-lane rasters)",
            "unique_local_rasters_checked": len(surf_rows),
            "worst_abs_spearman_exact_full_footprint": round(abs(exact_worst_rho), 6),
            "worst_spearman_raster": worst_label,
            "worst_top37654_forward_3px_overlap": worst_ov_row["top37654_1d_forward_3px_overlap"],
            "worst_overlap_raster": worst_ov_row["registry_raster"],
            "duplicate": surf_dup,
            "top10_by_overlap": sorted(
                surf_rows, key=lambda r: -r["top37654_1d_forward_3px_overlap"]
            )[:10],
        },
    }
    OUT_JSON.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"SCREEN PASS -> {OUT_JSON}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
