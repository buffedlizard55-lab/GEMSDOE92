#!/usr/bin/env python3
"""Pre-placement leakage canaries (Protocol Rule 4) and surface uniqueness check (Rule 1).

Must pass BEFORE building any HYDROCONDUIT candidate raster:
1. Every individual band and derived component feature tested ALONE on buffered holdout
   folds (seeds 20 and 30) must have symmetric ROC AUC <= 0.90.
2. Pre-placement surfaces S_pied_pct and S_hydro_pct must have |Spearman rho| <= 0.90
   and spaced-top-37654 forward 3-px overlap <= 0.70 against every local registry raster.
3. Writes exact pre-placement surface GeoTIFF into gitignored .cache/gems_inputs/ so
   public-registry audits check the genuine continuous pre-placement surface.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.hydroconduit import (  # noqa: E402
    gdr_blind_thermal_plume,
    hydroconduit_surface,
    spaced_top_mask,
)
from gems57 import grid as grid_mod, holdout  # noqa: E402
from report_breakline_proxies import load_mask, uniqueness  # noqa: E402


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    with rasterio.open(paths["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)

    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = hydroconduit_surface(
        det_elev=b12_el,
        det_elev_slope=b19_sl,
        depth_to_base=b15_db,
        geod_2ndinv=b4_s2i,
        geod_dilaterate=b8_dil,
        rtp=b2_rtp,
        cond_surf=b17_cd,
        rad_k=rad_k,
        rad_th=rad_th,
        gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )

    # Save continuous pre-placement surface to gitignored .cache for public audit tool
    surf_tif = ROOT / ".cache" / "gems_inputs" / "hydroconduit_S_hydro_surface.tif"
    with rasterio.open(paths["sample_submission"]) as ref:
        prof = ref.profile.copy()
    prof.update(driver="GTiff", count=1, dtype="float32", nodata=None, compress="deflate")
    with rasterio.open(surf_tif, "w", **prof) as dst:
        dst.write(np.where(foot, surf["S_hydro_pct"], 0.0).astype(np.float32), 1)

    # ---- Protocol Rule 4: Single-feature leakage canaries ----
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)

    rng = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        idx_parts.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat = np.concatenate(idx_parts)

    canary_inputs = {
        "band02_rtp": b2_rtp,
        "band04_geod_2ndinv": b4_s2i,
        "band08_geod_dilaterate": b8_dil,
        "band12_det_elev": b12_el,
        "band15_depth_to_base_surf": b15_db,
        "band17_cond_surf": b17_cd,
        "band19_det_elev_slope": b19_sl,
        "rad_k_raw": rad_k.astype(np.float32),
        "rad_th_raw": rad_th.astype(np.float32),
        "rel_break_pct": surf["rel_break_pct"],
        "coh_elev": surf["coh_elev"],
        "mu_step": surf["mu_step"],
        "t_scarp": surf["t_scarp"],
        "p_elev": surf["p_elev"],
        "p_cover": surf["p_cover"],
        "kappa_strike": surf["kappa_strike"],
        "kappa_strain": surf["kappa_strain"],
        "m_rtp": surf["m_rtp"],
        "r_kth": surf["r_kth"],
        "c_mt": surf["c_mt"],
        "q_gdr": surf["q_gdr"],
        "g_hydro": surf["g_hydro"],
        "S_pied_pct": surf["S_pied_pct"],
        "S_hydro_pct": surf["S_hydro_pct"],
    }
    canaries = {}
    for name, arr in canary_inputs.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        canaries[name] = {
            "auc": round(auc, 6),
            "symmetric_auc": round(sym, 6),
            "status": "INVESTIGATE" if sym > 0.90 else "PASS",
        }
    del b2_rtp, b4_s2i, b8_dil, b12_el, b15_db, b17_cd, b19_sl, rad_k, rad_th

    max_canary = max(c["symmetric_auc"] for c in canaries.values())
    if max_canary > 0.90:
        raise RuntimeError(f"Leakage canary > 0.90 triggered: {max_canary}")

    # ---- Protocol Rule 1: Pre-placement surface uniqueness vs local registry ----
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)
    r0 = load_mask(ROOT / "data/parent_R0_zeros.tif", foot)
    far_pool = foot & surf["valid"] & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)

    surf_set_pied = spaced_top_mask(surf["S_pied_raw"], far_pool, 37654)
    surf_set_hydro = spaced_top_mask(surf["S_hydro_raw"], far_pool, 37654)
    uniq = uniqueness(
        {"SURF_PIED_TOP37654": surf_set_pied, "SURF_HYDRO_TOP37654": surf_set_hydro},
        foot,
        set(),
    )

    fp_idx = np.flatnonzero(foot)
    sample = np.random.default_rng(20261024).choice(fp_idx, size=300_000, replace=False)
    sh_vals = surf["S_hydro_pct"].ravel()[sample]
    sp_vals = surf["S_pied_pct"].ravel()[sample]
    by_name = {
        p.name: p
        for p in [
            ROOT / "data/parent_R0_zeros.tif",
            *sorted((ROOT / "data/bridge").glob("*.tif")),
            *sorted((ROOT / "docs/downloads").glob("*.tif")),
            *sorted((ROOT / "releases").glob("*.tif")),
        ]
    }
    spear_rows = []
    for row in uniq["SURF_HYDRO_TOP37654"]["rows"]:
        p = by_name.get(row["registry_file"])
        if p is None:
            continue
        m = load_mask(p, foot).ravel()[sample].astype(float)
        rho_h = float(spearmanr(sh_vals, m).statistic)
        rho_p = float(spearmanr(sp_vals, m).statistic)
        spear_rows.append({
            "registry_file": row["registry_file"],
            "spearman_S_hydro": round(rho_h, 6),
            "spearman_S_pied": round(rho_p, 6),
        })
    worst_spear_h = max(spear_rows, key=lambda r: abs(r["spearman_S_hydro"]))
    worst_spear_p = max(spear_rows, key=lambda r: abs(r["spearman_S_pied"]))

    out_doc = {
        "schema": "gemsdoe92-preplacement-screen.v1",
        "lane": "HYDROCONDUIT",
        "gdr_summary": {
            "n_thermal_pixels": gdr_info["n_thermal_pixels"],
            "n_blind_geotherm_pixels": gdr_info["n_blind_geotherm_pixels"],
        },
        "leakage_canaries": {
            "max_symmetric_auc": max_canary,
            "all_pass_le_0_90": max_canary <= 0.90,
            "features": canaries,
        },
        "preplacement_surface_uniqueness": {
            "S_pied_top37654": {
                k: uniq["SURF_PIED_TOP37654"][k]
                for k in (
                    "registry_rasters_checked",
                    "worst_forward_overlap",
                    "worst_forward_overlap_file",
                    "worst_abs_spearman",
                    "worst_abs_spearman_file",
                    "duplicate",
                )
            },
            "S_hydro_top37654": {
                k: uniq["SURF_HYDRO_TOP37654"][k]
                for k in (
                    "registry_rasters_checked",
                    "worst_forward_overlap",
                    "worst_forward_overlap_file",
                    "worst_abs_spearman",
                    "worst_abs_spearman_file",
                    "duplicate",
                )
            },
            "continuous_sampled_spearman_300k": {
                "worst_S_hydro": worst_spear_h,
                "worst_S_pied": worst_spear_p,
            },
        },
    }
    out_path = ROOT / "evidence" / "hydroconduit_preplacement_screen.json"
    out_path.write_text(json.dumps(out_doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "max_canary_symmetric_auc": max_canary,
        "S_pied_surface_uniq": out_doc["preplacement_surface_uniqueness"]["S_pied_top37654"],
        "S_hydro_surface_uniq": out_doc["preplacement_surface_uniqueness"]["S_hydro_top37654"],
        "continuous_spearman": out_doc["preplacement_surface_uniqueness"]["continuous_sampled_spearman_300k"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
