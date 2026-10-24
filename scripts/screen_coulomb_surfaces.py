#!/usr/bin/env python3
"""Pre-registered screen for the COULOMB-session surfaces (2026-10-24).

Identical instruments to the preserved STEPEDGE screen
(scripts/screen_stepedge_surfaces.py) and to report_breakline_proxies.py:
(a) single-feature symmetric-AUC leakage canary vs withheld catalogue
positives (buffered-component folds, seeds 20/30, rng 520810);
(b) a 16,944-dot spaced top-set (2.8 px floor, >3 px off H19-5, d_cat>2 px)
scored alone as PROXY on off-catalogue USGS SGMC bedrock faults and on the
fixed-catalogue diagnostic; (c) far-set forward overlap vs prior lanes' far
dots, plus -- for the Rank-1 COULOMB-free surface only -- full local-registry
uniqueness of its top-37,654 spaced set (forward overlap + sampled Spearman).

Gate zero: the BREAKLINE-L control must reproduce sym AUC 0.621604 and
far-only SGMC 0.072325 before any new number is trusted.

Every number written is PROXY-SCREEN. Nothing here is a competition score.
Pre-registration: docs/HYPOTHESES_20261024_COULOMB.md (screen -> build rule).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests
from gems.breakline import lane_surface as breakline_surface, percentile_rank
from gems.coulomb import (
    coulomb_surface,
    magtilt_contact,
    mtedge_dilat,
)
from gems57 import grid as grid_mod, holdout, metric
from report_breakline_proxies import load_mask, uniqueness

N_FAR = 16944
N_FULL = 37654
BASELINE_EXPECTED = {"sym_auc": 0.621604, "far_only_sgmc_dti": 0.072325}

PRIOR_FARS = {
    "breakline_f45": "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
    "anasig_f45": "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
    "strainbreak_f60": "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
    "stepedge_f60": "docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif",
    "springalign_f33": "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif",
    "piedfront_f35": "docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif",
    "apronridge_free1d_whole": "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif",
    "hydroconduit_f45hydro": "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
}


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, bundle = build_and_verify_parent(inputs)
    r0 = bundle["r0"]
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    assert np.array_equal(grid.footprint, foot) and np.array_equal(grid.catalogue, cat)

    print("Loading bands 2/4/5/7/8/10/12/15/16/19 ...", flush=True)
    with rasterio.open(inputs["training_features"]) as ds:
        b2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4 = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7 = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8 = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b10 = ds.read(10, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b16 = ds.read(16, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid_topo = foot & np.isfinite(b12) & (b12 > -1e30) & np.isfinite(b19) & (b19 > -1e30)

    print("Building BREAKLINE baseline + COULOMB surfaces ...", flush=True)
    bl = breakline_surface(b12, b19, valid_topo)
    cs = coulomb_surface(
        det_elev=b12, det_elev_slope=b19, depth_to_base=b15, grav_slope=b5,
        rtp=b2, dilaterate=b8, shearrate=b7, second_inv=b4,
        deq=b10, ieq=b16, footprint=foot,
    )
    valid_c = cs["valid"]
    surfaces: dict[str, tuple[np.ndarray, np.ndarray]] = {
        "breakline_L_baseline": (bl["L_pct"], valid_topo),
        "coulomb_free": (cs["S_free_pct"], valid_c),
        "coulomb_open": (cs["S_open_pct"], valid_c),
        "coulomb_seismo": (cs["S_seismo_pct"], valid_c),
        "coulomb_O_only": (cs["O_pct"], valid_c),
        "seismo_prior_only": (cs["seismo_pct"], valid_c),
        "rtp_tilt_only": (cs["R_rtp_tilt"], valid_c),
        "rel_scarp_only": (percentile_rank(cs["R_scarp_rel"], valid_c), valid_c),
    }
    # Keep raw free/open/seismo for the top-37654 uniqueness sets; free bands.
    s_free_raw = cs["S_free_raw"].copy()
    del bl, cs, b2, b4, b5, b7, b8, b10, b12, b15, b16, b19

    print("Building Rank-3 MAGTILT + Rank-4 MTEDGE surfaces ...", flush=True)
    with rasterio.open(inputs["training_features"]) as ds:
        t3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        t9 = ds.read(9, masked=True).filled(np.nan).astype(np.float32)
        t2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        t17 = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        t8 = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
    valid_mag = foot & np.isfinite(t3) & (t3 > -1e30) & np.isfinite(t9) & (t9 > -1e30)
    valid_mt = foot & np.isfinite(t17) & (t17 > -1e30) & np.isfinite(t8) & (t8 > -1e30)
    mt = magtilt_contact(t3, t9, t2, valid_mag)
    me = mtedge_dilat(t17, t8, valid_mt)
    surfaces["magtilt_contact"] = (mt["magtilt_pct"], valid_mag)
    surfaces["mtedge_dilat"] = (me["mtedge_pct"], valid_mt)
    del t3, t9, t2, t17, t8, mt, me

    # ---- canary sampling (identical construction to report_breakline_proxies)
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    rng = np.random.default_rng(520810)
    y_parts, sample_idx = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_idx.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(sample_idx)

    # ---- truths and far pool
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    d_h19 = distance_transform_edt(~h19)

    prior_fars: dict[str, np.ndarray] = {}
    for name, rel in PRIOR_FARS.items():
        m = load_mask(ROOT / rel, foot)
        if name == "apronridge_free1d_whole":
            prior_fars[name] = m  # standalone: whole file is off-skeleton by design
        else:
            prior_fars[name] = m & (d_h19 > 3.0)
    prior_far_edt = {k: distance_transform_edt(~v) for k, v in prior_fars.items()}

    from gems.breakline import spaced_top_mask

    results: dict[str, dict] = {}
    for name, (surf, valid) in surfaces.items():
        vals = np.nan_to_num(surf, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
        far = spaced_top_mask(surf, far_cand, N_FAR)
        row = {
            "sym_auc": round(max(auc, 1 - auc), 6),
            "auc": round(auc, 6),
            "far_only_sgmc_dti": round(float(metric.dti_binary(
                far, sgmc_truth, valid=foot, known=cat)["dti"]), 6),
            "far_only_fixedcat_dti": round(float(metric.dti_binary(
                far, cat, valid=foot, known=None)["dti"]), 6),
            "far_pool": int(far_cand.sum()),
            "far_overlap_vs_prior_lanes": {
                k: round(float(np.mean(edt[far] <= 3.0)), 6)
                for k, edt in prior_far_edt.items()},
        }
        results[name] = row
        print(name, row, flush=True)

    base = results["breakline_L_baseline"]
    reproduced = (abs(base["sym_auc"] - BASELINE_EXPECTED["sym_auc"]) < 5e-4
                  and abs(base["far_only_sgmc_dti"] - BASELINE_EXPECTED["far_only_sgmc_dti"]) < 5e-4)

    # ---- Rank-1 full local-registry uniqueness on the top-37,654 spaced set
    free_top = None
    free_uni = None
    free_rho = None
    if reproduced:
        from gems.coulomb import directional_ridge_1d
        ridge = directional_ridge_1d(s_free_raw, valid_c)
        cand = foot & valid_c & ridge & (d_cat > 2.0)
        free_top = spaced_top_mask(s_free_raw, cand, N_FULL, min_dist_px=2.8,
                                   cand_cap=800_000)
        print(f"coulomb_free top-37654 pool={int(cand.sum())} placed={int(free_top.sum())}",
              flush=True)
        free_uni = uniqueness({"COULOMBfree_top37654": free_top}, foot, set())
        # Sampled Spearman of S_free_pct vs each registry mask.
        rng2 = np.random.default_rng(520811)
        foot_idx = np.flatnonzero(foot)
        samp = rng2.choice(foot_idx, size=min(100_000, len(foot_idx)), replace=False)
        s_vals = (surfaces["coulomb_free"][0].ravel()[samp]).astype(np.float64)
        reg_paths = ([ROOT / "data/parent_R0_zeros.tif", ROOT / "data/bridge/h19_5.tif",
                      ROOT / "data/bridge/d28.tif", ROOT / "data/bridge/h27_4_solo.tif"]
                     + sorted((ROOT / "docs/downloads").glob("*-zeros.tif"))
                     + sorted((ROOT / "releases").glob("*-zeros.tif")))
        worst_rho = 0.0
        worst_rho_file = ""
        for p in reg_paths:
            if not p.is_file():
                continue
            m = load_mask(p, foot)
            if not m.any():
                continue
            rho = float(spearmanr(s_vals, m.ravel()[samp].astype(np.float64)).statistic)
            if abs(rho) > abs(worst_rho):
                worst_rho, worst_rho_file = rho, p.name
        free_rho = {"worst_spearman_rho": round(worst_rho, 6),
                    "worst_rho_file": worst_rho_file,
                    "n_rasters": len(reg_paths)}
        print("coulomb_free surface uniqueness:", free_uni["COULOMBfree_top37654"], flush=True)
        print("coulomb_free sampled rho:", free_rho, flush=True)
    del s_free_raw

    fwd = (free_uni["COULOMBfree_top37654"]["worst_forward_overlap"]
           if free_uni else None)
    rho = abs(free_rho["worst_spearman_rho"]) if free_rho else None
    canary = results.get("coulomb_free", {}).get("sym_auc")
    build_free = bool(reproduced and canary is not None and canary <= 0.90
                       and fwd is not None and fwd <= 0.70
                       and rho is not None and rho <= 0.90)
    report = {
        "evidence_class": "PROXY-SCREEN",
        "n_far": N_FAR,
        "n_full": N_FULL,
        "sgmc_truth_px": int(sgmc_truth.sum()),
        "baseline_expected": BASELINE_EXPECTED,
        "baseline_reproduced_within_5e-4": bool(reproduced),
        "surfaces": results,
        "coulomb_free_top37654_uniqueness": free_uni["COULOMBfree_top37654"] if free_uni else None,
        "coulomb_free_sampled_spearman": free_rho,
        "preregistered_rule": (
            "Build Rank-1 COULOMB family iff baseline reproduces AND coulomb_free "
            "sym_auc<=0.90 AND top-37654 forward overlap<=0.70 AND |rho|<=0.90 vs "
            "every pre-session local raster; else screen Rank 2 (SEISMO-SWARM)."),
        "screen_decision": {
            "coulomb_free_sym_auc": canary,
            "coulomb_free_worst_forward_overlap": fwd,
            "coulomb_free_worst_abs_rho": rho,
            "build_rank1_coulomb": build_free,
        },
    }
    out = ROOT / "evidence/coulomb_preplacement_screen.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"baseline_reproduced": reproduced, "build_rank1": build_free,
                      "written": str(out)}, indent=2))
    return 0 if reproduced else 2


if __name__ == "__main__":
    raise SystemExit(main())
