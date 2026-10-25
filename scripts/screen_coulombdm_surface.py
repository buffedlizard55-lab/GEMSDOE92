#!/usr/bin/env python3
"""Pre-placement leakage canaries (Protocol Rule 4) and surface uniqueness screen (Rule 1)
for the COULOMBDM lane (Two-Regime Oriented 2D Mohr-Coulomb + Multi-Altitude RTP/Clay-Cap).

Must execute and PASS BEFORE building any COULOMBDM candidate GeoTIFF:
1. Tests all 32 raw & derived features (plus Rank-4 SEISMIC-ANISOTROPY screen) alone on
   buffered holdout folds (seeds 20 & 30); enforces symmetric ROC AUC <= 0.90.
2. Tests pre-placement continuous surface S_pct (|Spearman rho| <= 0.90) and spaced-top-37,654
   1D-crest masks (standalone & off-skeleton, 3-px forward overlap <= 0.70) against all
   local registry rasters in data/, releases/, and docs/downloads/.
3. Saves .cache/gems_inputs/coulombdm_S_surface.tif for public-registry auditing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.coulombdm import (  # noqa: E402
    coulombdm_surface,
    gdr_blind_thermal_plume,
    percentile_rank,
    spaced_top_mask,
)
from gems.hydroconduit import _clean_valid  # noqa: E402
from gems57 import grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402
from report_breakline_proxies import load_mask, uniqueness  # noqa: E402


def main() -> int:
    paths = verify_all_manifests()
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot, cat = grid.footprint, grid.catalogue

    with rasterio.open(paths["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5_gsl = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7_shr = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b10_deq = ds.read(10, masked=True).filled(np.nan).astype(np.float32)
        b11_gvg = ds.read(11, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b16_ieq = ds.read(16, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    with rasterio.open(paths["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
        rad_u = ds.read(3)

    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        paths["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = coulombdm_surface(
        det_elev=b12_el,
        det_elev_slope=b19_sl,
        depth_to_base=b15_db,
        grav_slope=b5_gsl,
        grav_vg=b11_gvg,
        geod_2ndinv=b4_s2i,
        geod_shearrate=b7_shr,
        geod_dilaterate=b8_dil,
        rtp=b2_rtp,
        cond_surf=b17_cd,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )

    # Also compute Rank-4 SEISMIC-ANISOTROPY screen surface (Bands 10, 16, 7)
    valid_arr = np.asarray(surf["valid"], bool)
    log_deq = gaussian_filter(
        np.log(np.maximum(_clean_valid(b10_deq, valid_arr), 0.0) + 50.0).astype(np.float32),
        2.0,
    )
    dy_q, dx_q = np.gradient(log_deq)
    dyy_q, _ = np.gradient(dy_q)
    _, dxx_q = np.gradient(dx_q)
    seis_ridge = np.maximum(-(dxx_q + dyy_q), 0.0).astype(np.float32)
    seis_aniso_pct = percentile_rank(
        percentile_rank(seis_ridge, valid_arr)
        * percentile_rank(_clean_valid(b16_ieq, valid_arr), valid_arr)
        * percentile_rank(_clean_valid(b7_shr, valid_arr), valid_arr),
        valid_arr,
    )

    # Persist pre-placement surface for public registry audit
    surf_tif = ROOT / ".cache" / "gems_inputs" / "coulombdm_S_surface.tif"
    with rasterio.open(paths["sample_submission"]) as ref:
        prof = ref.profile.copy()
    prof.update(driver="GTiff", count=1, dtype="float32", nodata=None, compress="deflate")
    with rasterio.open(surf_tif, "w", **prof) as dst:
        dst.write(np.where(foot, np.asarray(surf["S_pct"], dtype=np.float32), 0.0), 1)

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
        "band05_iso_grav_slope": b5_gsl,
        "band07_geod_shearrate": b7_shr,
        "band08_geod_dilaterate": b8_dil,
        "band10_deq_n100a15": b10_deq,
        "band11_iso_grav_vg": b11_gvg,
        "band12_det_elev": b12_el,
        "band15_depth_to_base": b15_db,
        "band16_ieq_n100a15": b16_ieq,
        "band17_cond_surf": b17_cd,
        "band19_det_elev_slope": b19_sl,
        "rad_k_raw": rad_k.astype(np.float32),
        "rad_th_raw": rad_th.astype(np.float32),
        "rad_u_raw": rad_u.astype(np.float32),
        "rel_break_pct": surf["rel_break_pct"],
        "mu_step": surf["mu_step"],
        "coh_elev": surf["coh_elev"],
        "scarp_edge_pct": surf["scarp_edge_pct"],
        "rtp_persist_pct": surf["rtp_persist_pct"],
        "rtp_demag_pct": surf["rtp_demag_pct"],
        "rtp_conduit_pct": surf["rtp_conduit_pct"],
        "grav_contact_pct": surf["grav_contact_pct"],
        "mt_edge_pct": surf["mt_edge_pct"],
        "rad_alt_pct": surf["rad_alt_pct"],
        "hydro_boost_pct": surf["hydro_boost_pct"],
        "kappa_mc": surf["kappa_mc"],
        "c_coulomb_elev": surf["c_coulomb_elev"],
        "c_coulomb_rtp": surf["c_coulomb_rtp"],
        "r_pied": surf["r_pied"],
        "r_sub": surf["r_sub"],
        "r_bed": surf["r_bed"],
        "S_pct": surf["S_pct"],
        "hab_coulomb_pct": surf["hab_coulomb_pct"],
        "seismic_anisotropy_rank4_screen": seis_aniso_pct,
    }
    canaries = {}
    for name, arr in canary_inputs.items():
        vals = np.nan_to_num(np.asarray(arr), nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        canaries[name] = {
            "auc": round(auc, 6),
            "symmetric_auc": round(sym, 6),
            "status": "INVESTIGATE" if sym > 0.90 else "PASS",
        }

    max_canary = max(c["symmetric_auc"] for c in canaries.values())
    if max_canary > 0.90:
        raise RuntimeError(f"Leakage canary > 0.90 triggered: {max_canary}")

    # ---- Channel attribution & candidate pool capacity ----
    crest = np.asarray(surf["crest_1d"], bool)
    r_pied = np.asarray(surf["r_pied"], dtype=np.float32)
    r_sub = np.asarray(surf["r_sub"], dtype=np.float32)
    r_bed = np.asarray(surf["r_bed"], dtype=np.float32)
    s_raw = np.asarray(surf["S_raw"], dtype=np.float32)

    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    free_pool = foot & valid_arr & crest & (d_cat > 2.0)
    far_pool = foot & valid_arr & crest & (d_cat > 2.0) & (d_h19 > 3.0)

    surf_free_37k = spaced_top_mask(s_raw, free_pool, 37654, min_dist_px=2.8)
    surf_far_37k = spaced_top_mask(s_raw, far_pool, 37654, min_dist_px=2.8)
    surf_seis_far_37k = spaced_top_mask(seis_aniso_pct, foot & valid_arr & (d_cat > 2.0) & (d_h19 > 3.0), 37654, min_dist_px=2.8)

    # Off-catalogue SGMC sanity check (pre-build screen, including Rank-4 SEISMIC-ANISOTROPY)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_free = round(float(gems57_metric.dti_binary(surf_free_37k, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
    sgmc_far = round(float(gems57_metric.dti_binary(surf_far_37k, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
    sgmc_seis_far = round(float(gems57_metric.dti_binary(surf_seis_far_37k, sgmc_truth, valid=foot, known=cat)["dti"]), 6)

    win_sub = int(np.sum(surf_free_37k & (r_sub >= r_pied) & (r_sub >= r_bed)))
    win_bed = int(np.sum(surf_free_37k & (r_bed > r_pied) & (r_bed > r_sub)))
    win_pied = int(surf_free_37k.sum()) - win_sub - win_bed

    # ---- Protocol Rule 1: Pre-placement surface uniqueness vs all local rasters ----
    uniq = uniqueness(
        {
            "SURF_COULOMB1D_TOP37654": surf_free_37k,
            "SURF_COULOMBFAR_TOP37654": surf_far_37k,
        },
        foot,
        set(),
    )

    fp_idx = np.flatnonzero(foot)
    sample = np.random.default_rng(20261024).choice(fp_idx, size=300_000, replace=False)
    s_vals = np.asarray(surf["S_pct"], dtype=np.float32).ravel()[sample]
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
    for row in uniq["SURF_COULOMB1D_TOP37654"]["rows"]:
        p = by_name.get(row["registry_file"])
        if p is None:
            continue
        m = load_mask(p, foot).ravel()[sample].astype(float)
        rho = float(spearmanr(s_vals, m).statistic)
        spear_rows.append({"registry_file": row["registry_file"], "spearman_S_pct": round(rho, 6)})
    worst_spear = max(spear_rows, key=lambda r: abs(r["spearman_S_pct"]))

    del (
        b2_rtp, b4_s2i, b5_gsl, b7_shr, b8_dil, b10_deq,
        b11_gvg, b12_el, b15_db, b16_ieq, b17_cd, b19_sl,
        rad_k, rad_th, rad_u,
    )

    out_doc = {
        "schema": "gemsdoe92-preplacement-screen.v1",
        "lane": "COULOMBDM",
        "gdr_summary": {
            "n_thermal_pixels": int(gdr_info["n_thermal_pixels"]),
            "n_blind_geotherm_pixels": int(gdr_info["n_blind_geotherm_pixels"]),
        },
        "pool_and_channel_diagnostics": {
            "crest_1d_total_px": int(crest.sum()),
            "free_pool_dcat_gt_2_px": int(free_pool.sum()),
            "far_pool_dh19_gt_3_px": int(far_pool.sum()),
            "free_spaced_37654_emitted": int(surf_free_37k.sum()),
            "far_spaced_37654_emitted": int(surf_far_37k.sum()),
            "channel_winners_on_free_37654": {
                "piedmont_monoclinal_scarp": win_pied,
                "concealed_subsurface_rtp_grav_mt": win_sub,
                "corroborated_bedrock_relay": win_bed,
            },
            "sgmc_off_catalogue_screen": {
                "coulomb1d_top37654_sgmc_dti": sgmc_free,
                "coulombfar_top37654_sgmc_dti": sgmc_far,
                "rank4_seismic_anisotropy_far_sgmc_dti": sgmc_seis_far,
            },
        },
        "leakage_canaries": {
            "max_symmetric_auc": max_canary,
            "all_pass_le_0_90": max_canary <= 0.90,
            "features": canaries,
        },
        "preplacement_surface_uniqueness": {
            "SURF_COULOMB1D_TOP37654": {
                k: uniq["SURF_COULOMB1D_TOP37654"][k]
                for k in (
                    "registry_rasters_checked",
                    "worst_forward_overlap",
                    "worst_forward_overlap_file",
                    "worst_abs_spearman",
                    "worst_abs_spearman_file",
                    "duplicate",
                )
            },
            "SURF_COULOMBFAR_TOP37654": {
                k: uniq["SURF_COULOMBFAR_TOP37654"][k]
                for k in (
                    "registry_rasters_checked",
                    "worst_forward_overlap",
                    "worst_forward_overlap_file",
                    "worst_abs_spearman",
                    "worst_abs_spearman_file",
                    "duplicate",
                )
            },
            "continuous_sampled_spearman_300k": worst_spear,
        },
    }
    out_path = ROOT / "evidence" / "coulombdm_preplacement_screen.json"
    out_path.write_text(json.dumps(out_doc, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "max_canary_symmetric_auc": max_canary,
        "pool_and_channel_diagnostics": out_doc["pool_and_channel_diagnostics"],
        "SURF_COULOMB1D_TOP37654": out_doc["preplacement_surface_uniqueness"]["SURF_COULOMB1D_TOP37654"],
        "SURF_COULOMBFAR_TOP37654": out_doc["preplacement_surface_uniqueness"]["SURF_COULOMBFAR_TOP37654"],
        "continuous_spearman": worst_spear,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
