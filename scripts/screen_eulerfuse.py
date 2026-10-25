#!/usr/bin/env python3
"""Build and pre-placement-screen the pre-registered EULERFUSE surfaces.

This is the only feature/model implementation for the lane. It reuses the
pinned stack and shared LOQO helper, tests every new feature alone for leakage,
fits strict draw-blind surfaces for holdout use, and checks actual continuous
surfaces plus deterministic preview dots against the local cross-lane registry
before any submission GeoTIFF is written.
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

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.coulomb_loqo import (  # noqa: E402
    FEATURE_NAMES,
    compute_feature_stack,
    directional_ridge_1d,
    fit_predict_loqo,
    gdr_blind_thermal_features,
)
from gems.eulerfuse import joint_euler_features  # noqa: E402
from gems.hydroconduit import percentile_rank  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, holdout  # noqa: E402
from screen_coulomb_loqo import collect_unique_local_rasters  # noqa: E402

CACHE_DIR = ROOT / ".cache" / "gems_inputs"
CACHE_NPZ = CACHE_DIR / "eulerfuse_cache.npz"
SURFACE_DIR = ROOT / ".cache" / "eulerfuse_surfaces"
OUT_JSON = ROOT / "evidence" / "eulerfuse_screen.json"
DATE = "20261024"
BASE_N = len(FEATURE_NAMES)
EULER_NAMES = (
    "e01_mag_euler",
    "e02_grav_euler",
    "e03_joint_colocation",
    "e04_depth_agreement",
    "e05_base_consistency",
    "e06_joint_euler",
)


def sym_auc(y: np.ndarray, x: np.ndarray) -> tuple[float, float]:
    auc = float(roc_auc_score(y, x))
    return auc, max(auc, 1.0 - auc)


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return (np.nan_to_num(a, nan=0.0) > 0) & foot


def euler_crest(
    probability: np.ndarray,
    base_line: np.ndarray,
    euler_line: np.ndarray,
    valid: np.ndarray,
) -> dict[str, np.ndarray]:
    v = np.asarray(valid, bool)
    p = np.where(v, np.clip(probability, 0.0, 1.0), 0.0).astype(np.float32)
    line = np.maximum(
        np.float32(0.55) * np.asarray(base_line, np.float32),
        np.asarray(euler_line, np.float32),
    ).astype(np.float32)
    surface = np.where(v, p * (np.float32(0.12) + np.float32(0.88) * line), 0.0).astype(np.float32)
    return {"surface": surface, "ridge": directional_ridge_1d(surface, v), "line": line}


def make_preview(
    arm: str,
    surface: np.ndarray,
    ridge: np.ndarray,
    valid: np.ndarray,
    d_cat: np.ndarray,
    h19: np.ndarray,
    d_h19: np.ndarray,
) -> np.ndarray:
    pool = valid & ridge & (d_cat > 2.0)
    if arm == "joint45":
        skel = spaced_top_mask(surface, pool & h19, 16_944, min_dist_px=2.5)
        far = spaced_top_mask(
            surface,
            pool & (d_h19 > 3.0) & (~skel),
            20_710,
            min_dist_px=2.8,
            cand_cap=900_000,
        )
        out = skel | far
    else:
        out = spaced_top_mask(surface, pool, 37_654, min_dist_px=2.8, cand_cap=900_000)
    if int(out.sum()) != 37_654:
        raise RuntimeError(f"{arm}: preview dot count {int(out.sum())} != 37654")
    return out


def save_surface(path: Path, arr: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    grid_mod.write_geotiff(path, np.asarray(arr, np.float32), nodata=None)
    return sha256_file(path)


def main() -> int:
    started = time.time()
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(CACHE_DIR / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = holdout.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    print("[1/8] Loading SHA-verified stack and external inputs...", flush=True)
    wanted = (2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
    bands: dict[int, np.ndarray] = {}
    with rasterio.open(paths["training_features"]) as ds:
        for b in wanted:
            bands[b] = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k, rad_th, rad_u = (ds.read(i) for i in (1, 2, 3))

    valid_seed = (
        foot & np.isfinite(bands[2]) & (bands[2] > -1e30)
        & np.isfinite(bands[12]) & (bands[12] > -1e30)
        & np.isfinite(bands[19]) & (bands[19] > -1e30)
    )
    gdr = gdr_blind_thermal_features(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_seed, sigma_px=14.0
    )

    print("[2/8] Computing catalogue-free base and Euler features...", flush=True)
    base = compute_feature_stack(
        rtp=bands[2], geod_2ndinv=bands[4], grav_slope=bands[5],
        geod_shearrate=bands[7], geod_dilaterate=bands[8], grav_vg=bands[11],
        det_elev=bands[12], grav_anom=bands[13], depth_to_base=bands[15],
        cond_surf=bands[17], grav_hg=bands[18], det_elev_slope=bands[19],
        rad_k=rad_k, rad_th=rad_th, rad_u=rad_u,
        gdr_plume_feat=gdr["plume_feat"], footprint=foot,
    )
    eul = joint_euler_features(
        bands[2], bands[13], bands[15], foot,
        sigma_px=1.5, window_radius_px=4, strength_quantile=0.70,
        max_centres=300_000,
    )
    valid = np.asarray(base["valid"], bool) & np.asarray(eul["valid"], bool)
    euler_arrays = [np.asarray(eul[k], np.float32) for k in (
        "mag_euler", "grav_euler", "joint_colocation", "depth_agreement",
        "base_consistency", "joint_euler",
    )]
    # Stage the ~620 MB augmented design matrix as an ignored memory map rather
    # than retaining base + Euler + concatenated copies simultaneously.
    x_path = CACHE_DIR / "eulerfuse_X_foot.npy"
    x_mm = np.lib.format.open_memmap(
        x_path, mode="w+", dtype=np.float32,
        shape=(int(foot.sum()), BASE_N + len(EULER_NAMES)),
    )
    x_mm[:, :BASE_N] = np.asarray(base["X_foot"], np.float32)
    for j, arr in enumerate(euler_arrays):
        x_mm[:, BASE_N + j] = arr[foot]
    x_mm.flush()

    # Retain only compact model inputs and plain diagnostics before fitting. The
    # raw 12-band arrays and Euler derivative/result rasters otherwise add more
    # than a gigabyte to the HistGradientBoosting fit peak.
    base_line = np.maximum(
        np.asarray(base["L_topo"], np.float32),
        np.float32(0.80) * np.asarray(base["L_sub"], np.float32),
    ).copy()
    joint_line = percentile_rank(
        np.maximum(
            np.asarray(eul["joint_euler"], np.float32),
            np.float32(0.70) * np.asarray(eul["joint_colocation"], np.float32),
        ),
        valid,
    )
    grav_line = percentile_rank(np.asarray(eul["grav_euler"], np.float32), valid)
    euler_diagnostics = {
        **dict(eul["diagnostics"]),
        "mag": dict(eul["mag_result"].diagnostics),
        "gravity": dict(eul["grav_result"].diagnostics),
    }
    del x_mm, euler_arrays, rad_k, rad_th, rad_u, bands, base, eul
    import gc
    gc.collect()
    x_all = np.load(x_path, mmap_mode="r")

    print("[3/8] Building whole-component buffered folds and leakage canaries...", flush=True)
    draws: dict[int, list[dict]] = {}
    folds: list[dict] = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        draws[seed] = draw
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [f["receipt"] for f in draw]})
    rng = np.random.default_rng(92024)
    y_parts, i_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & valid)
        neg = np.flatnonzero(fold["region"] & valid & (~cat))
        nneg = min(neg.size, max(1, 2 * pos.size))
        sel = rng.choice(neg, nneg, replace=False) if neg.size > nneg else neg
        i_parts.extend((pos, sel))
        y_parts.extend((np.ones(pos.size, np.uint8), np.zeros(sel.size, np.uint8)))
    can_idx = np.concatenate(i_parts)
    can_y = np.concatenate(y_parts)
    row_map = np.full(foot.shape, -1, np.int32)
    row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    can_rows = row_map.ravel()[can_idx]
    canaries: dict[str, dict[str, float]] = {}
    for j, name in enumerate((*FEATURE_NAMES, *EULER_NAMES)):
        auc, symmetric = sym_auc(can_y, x_all[can_rows, j])
        canaries[name] = {"auc": round(auc, 6), "symmetric_auc": round(symmetric, 6)}

    print("[4/8] Fitting deployment LOQO models (control, joint, gravity)...", flush=True)
    base_cols = tuple(range(BASE_N))
    joint_cols = tuple(range(BASE_N + len(EULER_NAMES)))
    gravity_cols = (*base_cols, BASE_N + 1, BASE_N + 4)
    label_sets: dict[str, np.ndarray] = {"full": cat}
    excluded: dict[str, np.ndarray | None] = {"full": None}
    for seed in (20, 30):
        first = draws[seed][0]
        label_sets[f"draw{seed}"] = first["visible"]
        excluded[f"draw{seed}"] = distance_transform_edt(~first["hidden_all"]) <= 3.0

    surfaces: dict[str, np.ndarray] = {}
    ridges: dict[str, np.ndarray] = {}
    for split, labels in label_sets.items():
        print(f"      LOQO split={split}", flush=True)
        for model, cols in (("base", base_cols), ("joint", joint_cols), ("gravity", gravity_cols)):
            p = fit_predict_loqo(
                x_all, foot, valid, quad, labels, feature_cols=cols,
                excluded_mask=excluded[split], guard_px=12, neg_buffer_px=5.0,
                seed=20261024,
            )
            line = base_line if model == "base" else (joint_line if model == "joint" else grav_line)
            crest = euler_crest(p, base_line, line, valid)
            surfaces[f"S_{model}_{split}"] = crest["surface"]
            # Only deployment previews need cached ridges. Draw-specific ridges
            # are cheap to reconstruct in the evaluator and expensive to retain.
            if split == "full":
                ridges[f"R_{model}_{split}"] = crest["ridge"]
            del p, crest
            gc.collect()

    # Composite surfaces are canaries too. Draw-blind values are evaluated only
    # against the matching draw's truth/background.
    for model in ("base", "joint", "gravity"):
        auc, symmetric = sym_auc(can_y, surfaces[f"S_{model}_full"].ravel()[can_idx])
        canaries[f"LOQO_{model}_full_surface"] = {
            "auc": round(auc, 6), "symmetric_auc": round(symmetric, 6)
        }
        yd, vd = [], []
        for seed in (20, 30):
            s = surfaces[f"S_{model}_draw{seed}"]
            for fold in draws[seed]:
                pos = np.flatnonzero(fold["truth"] & valid)
                neg = np.flatnonzero(fold["region"] & valid & (~cat))
                yd.extend((np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)))
                vd.extend((s.ravel()[pos], s.ravel()[neg]))
        auc, symmetric = sym_auc(np.concatenate(yd), np.concatenate(vd))
        canaries[f"LOQO_{model}_drawblind_surface"] = {
            "auc": round(auc, 6), "symmetric_auc": round(symmetric, 6)
        }
    max_name = max(canaries, key=lambda k: canaries[k]["symmetric_auc"])
    max_auc = canaries[max_name]["symmetric_auc"]
    if max_auc > 0.90:
        raise SystemExit(f"LEAKAGE CANARY STOP: {max_name} symmetric AUC={max_auc:.6f}")

    print("[5/8] Building deterministic pre-placement previews...", flush=True)
    arm_model = {"joint": "joint", "gravity": "gravity", "joint45": "joint"}
    previews: dict[str, np.ndarray] = {}
    for arm, model in arm_model.items():
        previews[arm] = make_preview(
            arm, surfaces[f"S_{model}_full"], ridges[f"R_{model}_full"],
            valid, d_cat, h19, d_h19,
        )

    print("[6/8] Comparing actual surfaces and previews to local registry...", flush=True)
    registries = collect_unique_local_rasters(foot, exclude_substrings=("eulerfuse", "EULERFUSE"))
    sample_idx = np.linspace(0, int(foot.sum()) - 1, 250_000, dtype=np.int64)
    rows: dict[str, list[dict]] = {a: [] for a in arm_model}
    for label, path in registries:
        with rasterio.open(path) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)
        support = (raw > 0) & foot
        dreg = distance_transform_edt(~support)
        regsub = raw[foot][sample_idx]
        for arm, model in arm_model.items():
            ssub = surfaces[f"S_{model}_full"][foot][sample_idx]
            rho = float(spearmanr(ssub, regsub).statistic) if np.ptp(regsub) > 0 and np.ptp(ssub) > 0 else 0.0
            ov = float(np.mean(dreg[previews[arm]] <= 3.0))
            rows[arm].append({
                "registry_raster": label,
                "positive_pixels": int(support.sum()),
                "surface_spearman_rho_250k": round(rho, 6),
                "preview_forward_overlap_3px": round(ov, 6),
            })
        del raw, support, dreg, regsub

    uniqueness: dict[str, dict] = {}
    for arm, rr in rows.items():
        wr = max(rr, key=lambda x: abs(x["surface_spearman_rho_250k"]))
        wo = max(rr, key=lambda x: x["preview_forward_overlap_3px"])
        duplicate = abs(wr["surface_spearman_rho_250k"]) > 0.90 or wo["preview_forward_overlap_3px"] > 0.70
        uniqueness[arm] = {
            "registry_rasters_checked": len(rr),
            "worst_abs_surface_spearman_250k": round(abs(wr["surface_spearman_rho_250k"]), 6),
            "worst_surface_raster": wr["registry_raster"],
            "worst_preview_forward_overlap_3px": wo["preview_forward_overlap_3px"],
            "worst_overlap_raster": wo["registry_raster"],
            "duplicate": duplicate,
            "top5_overlap": sorted(rr, key=lambda x: -x["preview_forward_overlap_3px"])[:5],
        }
        print(f"      {arm}: |rho|max={uniqueness[arm]['worst_abs_surface_spearman_250k']:.4f}; overlap={uniqueness[arm]['worst_preview_forward_overlap_3px']:.4f}; duplicate={duplicate}", flush=True)

    viable = [a for a in arm_model if not uniqueness[a]["duplicate"]]
    if not viable:
        raise SystemExit("PRE-PLACEMENT DUPLICATE STOP: all EULERFUSE arms drifted into registry lanes")

    print("[7/8] Saving ignored reusable surfaces/cache...", flush=True)
    surface_hashes = {}
    for model in ("base", "joint", "gravity"):
        surface_hashes[model] = save_surface(
            SURFACE_DIR / f"EULERFUSE-{model}-surface-{DATE}.tif",
            surfaces[f"S_{model}_full"],
        )
    np.savez(
        CACHE_NPZ,
        valid=valid,
        base_line=base_line,
        joint_line=joint_line,
        grav_line=grav_line,
        **surfaces,
        **ridges,
    )

    print("[8/8] Writing machine-readable pre-placement evidence...", flush=True)
    out = {
        "schema": "gemsdoe92.eulerfuse-screen.v1",
        "lane": "EULERFUSE",
        "session_date_utc": DATE,
        "elapsed_seconds": round(time.time() - started, 2),
        "inputs": {
            "training_features_sha256": sha256_file(paths["training_features"]),
            "external_radiometrics_sha256": sha256_file(paths["ext_geodawn_rad_u8"]),
            "gdr_csv_sha256": sha256_file(paths["gdr_wellspring_in_footprint"]),
        },
        "euler_diagnostics": euler_diagnostics,
        "split_receipts": split_receipts,
        "leakage_canaries": {
            "evidence_class": "HOLDOUT-CANARY",
            "threshold_symmetric_auc": 0.90,
            "all_pass": True,
            "max_symmetric_auc": max_auc,
            "max_symmetric_feature": max_name,
            "features": canaries,
        },
        "preplacement_local_registry": uniqueness,
        "surface_sha256": surface_hashes,
        "viable_arms_after_local_screen": viable,
        "experiments_registered": ["joint", "gravity", "joint45"],
        "experiments_run_so_far": 0,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"SCREEN PASS -> {OUT_JSON}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
