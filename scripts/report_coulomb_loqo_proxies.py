#!/usr/bin/env python3
"""Evaluate the 3 pre-registered COULOMB-LOQO variants across all holdout, proxy,
and local uniqueness instruments.

Outputs:
- ``evidence/coulomb_loqo_proxy_audit.json``
- ``docs/downloads/<stem>-audit.json`` sidecars for each served ``COULOMBLOQO`` TIF
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import verify_all_manifests  # noqa: E402
from gems.coulomb_loqo import build_crest_surface, spaced_top_mask  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric as gems57_metric  # noqa: E402
from screen_coulomb_loqo import collect_unique_local_rasters  # noqa: E402

CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "coulomb_loqo_cache.npz"
SCREEN_JSON = ROOT / "evidence" / "coulomb_loqo_screen.json"
VARIANTS_JSON = ROOT / "evidence" / "coulomb_loqo_variants.json"
OUT_JSON = ROOT / "evidence" / "coulomb_loqo_proxy_audit.json"


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    return (np.nan_to_num(arr, nan=0.0) > 0) & foot


def evaluate_local_uniqueness(
    cand_masks: dict[str, np.ndarray],
    foot: np.ndarray,
    local_rasters: list[tuple[str, Path]],
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    cand_f = {k: m[foot].astype(np.float32) for k, m in cand_masks.items()}
    rows_by_cand: dict[str, list[dict]] = {k: [] for k in cand_masks}

    for label, rpath in local_rasters:
        with rasterio.open(rpath) as ds:
            raw = np.nan_to_num(ds.read(1), nan=0.0)
        theirs = (raw > 0) & foot
        d_theirs = distance_transform_edt(~theirs)
        t_foot = theirs[foot].astype(np.float32)
        t_std = float(np.std(t_foot))
        for k, m in cand_masks.items():
            fwd = float((d_theirs[m] <= 3.0).mean())
            phi = float(np.corrcoef(cand_f[k], t_foot)[0, 1]) if t_std > 0 else 0.0
            rows_by_cand[k].append(
                {
                    "registry_raster": label,
                    "their_positive_pixels": int(theirs.sum()),
                    "forward_overlap_3px": round(fwd, 6),
                    "spearman_phi_footprint": round(phi, 6),
                }
            )
        del raw, theirs, d_theirs, t_foot

    for k, rows in rows_by_cand.items():
        w_ov = max(rows, key=lambda r: r["forward_overlap_3px"])
        w_rh = max(rows, key=lambda r: abs(r["spearman_phi_footprint"]))
        dup = bool(w_ov["forward_overlap_3px"] > 0.70 or abs(w_rh["spearman_phi_footprint"]) > 0.90)
        out[k] = {
            "n_rasters_checked": len(rows),
            "worst_forward_overlap": w_ov["forward_overlap_3px"],
            "worst_forward_file": w_ov["registry_raster"],
            "worst_abs_spearman_phi": round(abs(w_rh["spearman_phi_footprint"]), 6),
            "worst_spearman_file": w_rh["registry_raster"],
            "local_duplicate": dup,
            "top5_by_overlap": sorted(rows, key=lambda r: -r["forward_overlap_3px"])[:5],
        }
    return out


def main() -> int:
    paths = verify_all_manifests()
    sdoc = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    variants = vdoc["variants"]

    grid = grid_mod.load_grid(CACHE_DIR / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)
    h19 = load_mask(ROOT / "data/bridge/h19_5.tif", foot)
    d_h19 = distance_transform_edt(~h19)

    arms: dict[str, np.ndarray] = {
        "R0": load_mask(ROOT / "data/parent_R0_zeros.tif", foot),
    }
    baseline_candidates = {
        "HYDROCONDUIT_f45hydro": ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
        "HYDROCONDUIT_f50hydro": ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf50hydro-20261024-5d50e9e3-zeros.tif",
        "HYDROCONDUIT_f45pied": ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45pied-20261024-3c236840-zeros.tif",
        "APRONRIDGE_free1d": ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif",
        "APRONRIDGE_s50f50": ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEs50f50-20261024-2f0431ea-zeros.tif",
        "PIEDFRONT_f45Ptop": ROOT / "docs/downloads/h33-h33-2-b2-PIEDFRONTf45Ptop-20261024-aad86ac9-zeros.tif",
        "RELIEF_p10piedmont": ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif",
        "STRAINBREAK_f60s2i": ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
        "ANASIG_f45Atop": ROOT / "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
        "SPRINGALIGN_f33Ctop": ROOT / "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif",
        "BREAKLINE_f45Ltop": ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
        "STEPEDGE_f45Sraw": ROOT / "releases/h33-h33-2-b2-STEPEDGEf45Sraw-20261024-0854307f-zeros.tif",
    }
    for bname, bpath in baseline_candidates.items():
        if bpath.is_file():
            arms[bname] = load_mask(bpath, foot)

    cand_names: list[str] = []
    for v in variants:
        arm = v["value"]
        cand_names.append(arm)
        arms[arm] = load_mask(ROOT / v["file_zeros"], foot)

    print("1. Evaluating static-raster HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld px)...", flush=True)
    folds = []
    draws_by_seed = {}
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        draws_by_seed[seed] = draw
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        arr_f = mask.astype(np.float32)
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(arr_f, fold, foot)
            per_arm_fold_scores[arm_name].append(round(float(score["dti"]), 6))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms  # type: ignore[assignment]

    # Also evaluate strict draw-blind OOF LOQO under BOTH d_full_cat > 2.0 and d_visible > 2.0
    print("2. Evaluating strict draw-blind OOF LOQO (P_draw20 / P_draw30)...", flush=True)
    cache = np.load(NPZ_CACHE)
    valid = cache["valid"].astype(bool)
    l_topo = cache["L_topo"].astype(np.float32)
    l_sub = cache["L_sub"].astype(np.float32)
    p_draws = {
        20: cache["P_draw20"].astype(np.float32),
        30: cache["P_draw30"].astype(np.float32),
    }

    drawblind_dcat2_terms = None
    drawblind_dcat2_fold_scores: list[float] = []
    dvis_terms: dict[str, np.ndarray | None] = {
        "COULOMBLOQO_standalone_dvis2": None,
        "COULOMBLOQO_dual45_dvis2": None,
        "H19_skeleton_dvis2": None,
    }
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    for seed in (20, 30):
        crest_d = build_crest_surface(p_draws[seed], l_topo, l_sub, valid, sub_weight=0.80)
        s_d = crest_d["S_crest"]
        r_d = crest_d["ridge_1d"]

        # (a) Draw-blind LOQO evaluated with deployment d_full_cat > 2.0 mask
        mask_dcat2 = spaced_top_mask(
            s_d, foot & valid & r_d & (d_cat > 2.0), 37654, min_dist_px=2.8, cand_cap=900_000
        ).astype(np.float32)
        for fold in draws_by_seed[seed]:
            sc, tm = evaluate_holdout.evaluate(mask_dcat2, fold, foot)
            drawblind_dcat2_fold_scores.append(round(float(sc["dti"]), 6))
            drawblind_dcat2_terms = tm if drawblind_dcat2_terms is None else drawblind_dcat2_terms + tm

        # (b) Strict Rule-2 fold-visible d_visible > 2.0 evaluation (zero self-masking)
        vis = draws_by_seed[seed][0]["visible"]
        d_vis = distance_transform_edt(~vis)

        pred_stand_vis = spaced_top_mask(
            s_d, foot & valid & r_d & (d_vis > 2.0), 37654, min_dist_px=2.8, cand_cap=900_000
        ).astype(np.float32)
        pred_stand_vis[vis] = 0.0

        skel_vis = spaced_top_mask(s_d, foot & valid & h19 & (d_vis > 2.0), 16944, min_dist_px=2.5)
        far_vis = spaced_top_mask(
            s_d, foot & valid & r_d & (d_vis > 2.0) & (d_h19 > 3.0) & (~skel_vis), 20710, min_dist_px=2.8
        )
        pred_dual_vis = (skel_vis | far_vis).astype(np.float32)
        pred_dual_vis[vis] = 0.0

        pred_h19_vis = spaced_top_mask(
            scan_rank, foot & valid & h19 & (d_vis > 2.0), 37654, min_dist_px=2.4
        ).astype(np.float32)
        pred_h19_vis[vis] = 0.0

        for fold in draws_by_seed[seed]:
            for k_vis, arr_vis in (
                ("COULOMBLOQO_standalone_dvis2", pred_stand_vis),
                ("COULOMBLOQO_dual45_dvis2", pred_dual_vis),
                ("H19_skeleton_dvis2", pred_h19_vis),
            ):
                _, tm_v = evaluate_holdout.evaluate(arr_vis, fold, foot)
                dvis_terms[k_vis] = tm_v if dvis_terms[k_vis] is None else dvis_terms[k_vis] + tm_v

    terms_by_arm["COULOMBLOQO_drawblind_dcat2"] = drawblind_dcat2_terms  # type: ignore[assignment]
    per_arm_fold_scores["COULOMBLOQO_drawblind_dcat2"] = drawblind_dcat2_fold_scores

    pooled_by_cand = {
        c: evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=c)
        for c in cand_names + ["COULOMBLOQO_drawblind_dcat2"]
    }
    scores_all = pooled_by_cand[cand_names[0]]["scores"]
    print("\n=== POOLED STATIC HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld px) ===", flush=True)
    for k, s in sorted(scores_all.items(), key=lambda kv: -kv[1]["dti"]):
        print(f"   {k:28s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    dvis_summary = evaluate_holdout.pooled_summary(
        dvis_terms, draws=1000, seed=520810, candidate="COULOMBLOQO_standalone_dvis2"  # type: ignore[arg-type]
    )
    print("\n=== STRICT DRAW-BLIND FOLD-VISIBLE (d_visible > 2.0) HOLDOUT-DTI ===", flush=True)
    for k, s in dvis_summary["scores"].items():
        print(f"   {k:28s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]", flush=True)

    print("\n3. Evaluating off-catalogue USGS SGMC PROXY DTI (62,703 pixels >3 px off cat)...", flush=True)
    with rasterio.open(paths["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_scores = {
        k: round(float(gems57_metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }
    for k in cand_names + ["HYDROCONDUIT_f45hydro", "APRONRIDGE_free1d", "STRAINBREAK_f60s2i", "R0"]:
        if k in sgmc_scores:
            print(f"   SGMC PROXY {k:24s}: DTI = {sgmc_scores[k]:.6f}", flush=True)

    print("\n4. Checking final-dot local registry uniqueness...", flush=True)
    local_rasters = collect_unique_local_rasters(foot)
    uniq_final = evaluate_local_uniqueness({c: arms[c] for c in cand_names}, foot, local_rasters)
    for c in cand_names:
        u = uniq_final[c]
        print(
            f"   {c:12s}: worst_ov={u['worst_forward_overlap']:.6f} ({u['worst_forward_file']}), "
            f"worst_|phi|={u['worst_abs_spearman_phi']:.6f}, local_dup={u['local_duplicate']}",
            flush=True,
        )

    best_arm = max(cand_names, key=lambda c: scores_all[c]["dti"])
    print(f"\nWINNING COULOMB-LOQO ARM ON HOLDOUT-DTI: {best_arm} ({scores_all[best_arm]['dti']:.6f})", flush=True)

    # Keep ONLY the winning COULOMB-LOQO arm's .zip in docs/downloads/ (per repo convention)
    for v in variants:
        arm = v["value"]
        zpath = ROOT / v["file_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        if arm != best_arm:
            non_primary_zip = zpath.parent / f"{stem}-zeros.zip"
            if non_primary_zip.is_file():
                non_primary_zip.unlink()

    out_doc = {
        "schema": "gemsdoe92-coulomb-loqo-proxy-audit.v1",
        "lane": "COULOMB-LOQO",
        "evaluator_version": evaluate_holdout.VERSION,
        "winning_arm": best_arm,
        "split_receipts": split_receipts,
        "leakage_canaries": sdoc["leakage_canaries"],
        "uniqueness_preplacement_surface": sdoc["preplacement_surface_uniqueness"],
        "hide_and_recover_pooled_by_candidate": pooled_by_cand,
        "hide_and_recover_per_fold_dti": per_arm_fold_scores,
        "hide_and_recover_drawblind_fold_visible_dti": {
            "evidence_class": "HOLDOUT-DTI (strict draw-blind LOQO + d_visible > 2.0, zero self-masking)",
            "evaluator_version": evaluate_holdout.VERSION,
            "pooled_summary": dvis_summary,
        },
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "variant_dti": sgmc_scores,
        },
        "uniqueness_final_dots": uniq_final,
    }
    OUT_JSON.write_text(json.dumps(out_doc, indent=2) + "\n", encoding="utf-8")
    print(f"WROTE {OUT_JSON}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
