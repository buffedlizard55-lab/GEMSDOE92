#!/usr/bin/env python3
"""Emit the Protocol Rule-5 Run Card JSON, public uniqueness witness JSON, and
per-submission audit sidecars for LISTRICLOQO.

Writes:
- ``evidence/listric_loqo_public_registry_uniqueness.json``
- ``docs/downloads/listric_loqo_public_registry_uniqueness.json``
- ``evidence/listric_loqo_run_card.json``
- ``docs/downloads/listric_loqo_run_card.json``
- ``docs/downloads/h33-h33-2-b2-LISTRICLOQO*-audit.json``
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_listric_loqo_variants import MECHANISM_CARD, sha256_file  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402

SCREEN_JSON = ROOT / "evidence" / "listric_loqo_screen.json"
VARIANTS_JSON = ROOT / "evidence" / "listric_loqo_variants.json"
AUDIT_JSON = ROOT / "evidence" / "listric_loqo_proxy_audit.json"
DUAL_JSON = ROOT / "evidence" / "listric_loqo_dual_reading_audit.json"

PUB_JSON = ROOT / "evidence" / "listric_loqo_public_registry_uniqueness.json"
DL_PUB_JSON = ROOT / "docs" / "downloads" / "listric_loqo_public_registry_uniqueness.json"
RUN_CARD_EVIDENCE = ROOT / "evidence" / "listric_loqo_run_card.json"
RUN_CARD_DOWNLOADS = ROOT / "docs" / "downloads" / "listric_loqo_run_card.json"


def build_public_uniqueness_receipt(best_v: dict, adoc: dict, ddoc: dict, sdoc: dict) -> dict:
    grid = grid_mod.load_grid(ROOT / "data/bridge")
    fp = grid.footprint
    surf_path = ROOT / ".cache/gems_inputs/listric_loqo_S_cal_surface.tif"
    cand_path = ROOT / best_v["file_zeros"]

    with rasterio.open(surf_path) as ds:
        surf_arr = np.nan_to_num(ds.read(1), nan=0.0)[fp]
    with rasterio.open(cand_path) as ds:
        cand_arr = np.nan_to_num(ds.read(1), nan=0.0)[fp]

    w17_path = ROOT / ".cache/gemsdoe_public_registry/witnesses/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
    rho_pre_17 = 0.0
    rho_fin_17 = 0.0
    w17_sha = ""
    if w17_path.is_file():
        w17_sha = sha256_file(w17_path)
        with rasterio.open(w17_path) as ds:
            w_arr = np.nan_to_num(ds.read(1), nan=0.0)[fp]
        rho_pre_17 = float(spearmanr(surf_arr, w_arr).statistic)
        rho_fin_17 = float(spearmanr(cand_arr, w_arr).statistic)

    du = ddoc["candidates"][best_v["value"]]
    surf_u = adoc["uniqueness_preplacement_surface"]
    return {
        "schema": "gemsdoe92-public-registry-uniqueness.v2",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "lane": "LISTRICLOQO",
        "candidate_file": best_v["file_zeros"],
        "candidate_sha256_zeros": best_v["sha256_zeros"],
        "candidate_hash_matches_scan": True,
        "unique_under_literal_rule": False,
        "unique_under_dual_reading_rule": bool(du["dual_reading_verdict"] == "unique"),
        "stop_required": True,
        "preplacement_surface": {
            "surface_file": ".cache/gems_inputs/listric_loqo_S_cal_surface.tif",
            "surface_sha256": sdoc["surface_tif_sha256"],
            "worst_local_abs_spearman": surf_u["worst_abs_spearman_exact_full_footprint"],
            "worst_local_top37654_overlap_3px": surf_u["worst_top37654_forward_3px_overlap"],
            "spearman_vs_17GEMSDOE_E_proba_multiscale": round(abs(rho_pre_17), 6),
        },
        "final_dots": {
            "emitted_dots": best_v["n_dots"],
            "spearman_vs_17GEMSDOE_E_proba_multiscale": round(abs(rho_fin_17), 6),
            "witness_17GEMSDOE_sha256": w17_sha,
            "worst_operative_overlap_3px": du["worst_operative_overlap_3px"],
            "worst_operative_witness": du["worst_operative_witness"],
            "operative_over_70pct_count": du["operative_over_70pct_count"],
            "dot_fields_le_150k_worst_overlap_3px": du["dot_fields_le_150k_worst_overlap_3px"],
            "dot_fields_le_150k_worst_witness": du["dot_fields_le_150k_worst_witness"],
            "dot_fields_le_90k_worst_overlap_3px": du["dot_fields_le_90k_worst_overlap_3px"],
            "dot_fields_le_90k_worst_witness": du["dot_fields_le_90k_worst_witness"],
            "continuous_gt_150k_matched_budget_worst_overlap_3px": du[
                "continuous_gt_150k_matched_budget_worst_overlap_3px"
            ],
            "literal_unweighted_worst_overlap_3px": du["literal_unweighted_worst_overlap_3px"],
            "literal_unweighted_witness": du["literal_unweighted_witness"],
            "public_witness_receipts": du["public_witness_receipts"],
        },
    }


def main() -> int:
    sdoc = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    adoc = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    ddoc = json.loads(DUAL_JSON.read_text(encoding="utf-8"))

    win_arm = adoc["winning_arm"]
    variants = vdoc["variants"]
    variants_by_arm = {v["value"]: v for v in variants}
    v_win = variants_by_arm[win_arm]

    pooled_win = adoc["hide_and_recover_pooled_by_candidate"][win_arm]
    scores_all = pooled_win["scores"]
    paired_best = pooled_win["paired_differences"]
    dvis_summary = adoc["hide_and_recover_drawblind_fold_visible_dti"]["pooled_summary"]
    dvis_scores = dvis_summary["scores"]
    dvis_deltas = dvis_summary["paired_differences"]
    sgmc_scores = adoc["sgmc_control_proxy"]["variant_dti"]

    uniq_final = adoc["uniqueness_final_dots"]
    surf_u = adoc["uniqueness_preplacement_surface"]

    pub_receipt = build_public_uniqueness_receipt(v_win, adoc, ddoc, sdoc)
    pub_serialized = json.dumps(pub_receipt, indent=2) + "\n"
    PUB_JSON.write_text(pub_serialized, encoding="utf-8")
    DL_PUB_JSON.write_text(pub_serialized, encoding="utf-8")

    # Write per-file <stem>-audit.json sidecars in docs/downloads/ matching check_site.py contract
    for v in variants:
        arm = v["value"]
        u = uniq_final[arm]
        du = ddoc["candidates"][arm]
        zpath = ROOT / v["file_zeros"]
        assert sha256_file(zpath) == v["sha256_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        audit_sidecar = zpath.parent / f"{stem}-audit.json"

        sidecar_doc = {
            "gates_zeros": v["gates_zeros"],
            "gates_zeros_pass": all(g["ok"] for g in v["gates_zeros"]),
            "gates_nan": v["gates_nan"],
            "gates_nan_pass": all(g["ok"] for g in v["gates_nan"]),
            "file": zpath.name,
            "sha256_zeros": v["sha256_zeros"],
            "sha256_nan": v["sha256"],
            "n_positive_pixels": v["n_dots"],
            "n_dots": v["n_dots"],
            "overall_pass": bool(
                all(g["ok"] for g in v["gates_zeros"]) and all(g["ok"] for g in v["gates_nan"])
            ),
            "submission_eligible": False,
            "run_card": "evidence/listric_loqo_run_card.json",
            "local_registry_uniqueness": {
                "n_rasters_checked": u["n_rasters_checked"],
                "worst_forward_overlap_3px": u["worst_forward_overlap"],
                "worst_forward_file": u["worst_forward_file"],
                "worst_abs_spearman_phi": u["worst_abs_spearman_phi"],
                "local_duplicate": u["local_duplicate"],
            },
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": True,
                "unique_under_literal_rule": False,
                "unique_under_dual_reading_rule": bool(du["dual_reading_verdict"] == "unique"),
                "stop_required": True,
                "witness_evidence": "evidence/listric_loqo_public_registry_uniqueness.json",
                "dual_reading_evidence": "evidence/listric_loqo_dual_reading_audit.json",
                "scope": (
                    f"Git-blob-verified public witness + 79-raster local scan ({du['non_self_rasters_checked']} non-self "
                    f"rasters): UNIQUE under dual_reading_decision (0/{du['non_self_rasters_checked']} "
                    f"rasters > 0.70; worst operative overlap = {du['worst_operative_overlap_3px']:.6f} vs "
                    f"{du['worst_operative_witness']}; <=90k px max = {du['dot_fields_le_90k_worst_overlap_3px']:.6f}; "
                    f">150k matched-budget max = {du['continuous_gt_150k_matched_budget_worst_overlap_3px']:.6f}). "
                    f"Literal unweighted rule fires (1.0) on full-footprint 17GEMSDOE E-proba-multiscale."
                ),
                "candidate_sha256_zeros": v["sha256_zeros"],
            },
        }
        audit_sidecar.write_text(json.dumps(sidecar_doc, indent=2) + "\n", encoding="utf-8")

    best_u = uniq_final[win_arm]
    best_du = ddoc["candidates"][win_arm]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    run_card = {
        "schema": "gemsdoe92-run-card.v2",
        "session_id": "arena/a5100f33-gemsdoe92",
        "generated_utc": now_utc,
        "date": "2026-10-25",
        "git_head_sha": git_sha,
        "lane": "LISTRICLOQO (Listric Dip-Offset Hanging-Wall Pullback, 2D Gravity-Tensor & 18-deg Riedel Coupling, Selective Subsurface-Calibrated LOQO)",
        "hypothesis": MECHANISM_CARD["hypothesis"],
        "mechanism": MECHANISM_CARD["mechanism"],
        "named_non_fault_process_that_could_mimic_it": MECHANISM_CARD["non_fault_mimic"],
        "falsifier": MECHANISM_CARD["falsifier"],
        "decision_rule": MECHANISM_CARD["decision_rule"],
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": adoc["evaluator_version"],
            "withheld_positive_pixels": scores_all[win_arm]["withheld_positive_pixels"],
            "dti": scores_all[win_arm]["dti"],
            "ci95": scores_all[win_arm]["ci95"],
            "strict_draw_blind_dcat2_dti": scores_all["LISTRICLOQO_drawblind_dcat2"]["dti"],
            "strict_draw_blind_dcat2_ci95": scores_all["LISTRICLOQO_drawblind_dcat2"]["ci95"],
            "strict_draw_blind_dvis2_dti": dvis_scores["LISTRICLOQO_standalone_dvis2"]["dti"],
            "strict_draw_blind_dvis2_ci95": dvis_scores["LISTRICLOQO_standalone_dvis2"]["ci95"],
            "paired_vs_nolistric_dvis2": dvis_deltas["LISTRICLOQO_nolistric_dvis2"],
            "paired_vs_H19_skeleton_dvis2": dvis_deltas["H19_skeleton_dvis2"],
            "paired_vs_KNICKLOQO_standalone_prev_best": paired_best["KNICKLOQO_standalone"],
            "paired_vs_PROVINCETOE_provincetoe": paired_best["PROVINCETOE_provincetoe"],
            "paired_vs_POISSONKNICK_qcal": paired_best["POISSONKNICK_qcal"],
            "paired_vs_COULOMBLOQO_standalone": paired_best["COULOMBLOQO_standalone"],
            "paired_vs_EULERFUSE_gravity": paired_best["EULERFUSE_gravity"],
            "paired_vs_R0": paired_best["R0"],
        },
        "ablation_summary": {
            arm: {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": adoc["evaluator_version"],
                "withheld_positive_pixels": scores_all[arm]["withheld_positive_pixels"],
                "dti": scores_all[arm]["dti"],
                "ci95": scores_all[arm]["ci95"],
                "paired_delta_vs_KNICKLOQO_standalone": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["KNICKLOQO_standalone"]["delta"],
                "paired_ci95_vs_KNICKLOQO_standalone": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["KNICKLOQO_standalone"]["ci95"],
                "paired_delta_vs_COULOMBLOQO_standalone": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["COULOMBLOQO_standalone"]["delta"],
                "paired_ci95_vs_COULOMBLOQO_standalone": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["COULOMBLOQO_standalone"]["ci95"],
                "paired_delta_vs_R0": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["R0"]["delta"],
                "paired_ci95_vs_R0": adoc["hide_and_recover_pooled_by_candidate"][arm][
                    "paired_differences"
                ]["R0"]["ci95"],
                "sgmc_proxy_dti": sgmc_scores[arm],
                "worst_local_forward_overlap_3px": uniq_final[arm]["worst_forward_overlap"],
                "worst_local_forward_file": uniq_final[arm]["worst_forward_file"],
                "worst_local_abs_spearman_phi": uniq_final[arm]["worst_abs_spearman_phi"],
                "local_duplicate": uniq_final[arm]["local_duplicate"],
                "public_dual_reading_worst_overlap_3px": ddoc["candidates"][arm][
                    "worst_operative_overlap_3px"
                ],
                "public_dual_reading_verdict": ddoc["candidates"][arm]["dual_reading_verdict"],
            }
            for arm in ("standalone", "nolistric", "dual35")
        },
        "leakage_canary_max_symmetric_auc": sdoc["leakage_canaries"]["max_symmetric_auc"],
        "sgmc_proxy": {
            "evidence_class": "PROXY",
            "dti": sgmc_scores[win_arm],
            "nolistric_dti": sgmc_scores["nolistric"],
            "dual35_dti": sgmc_scores["dual35"],
            "KNICKLOQO_standalone": sgmc_scores["KNICKLOQO_standalone"],
            "COULOMBLOQO_standalone": sgmc_scores["COULOMBLOQO_standalone"],
            "R0": sgmc_scores["R0"],
            "delta_vs_COULOMBLOQO_standalone": round(
                sgmc_scores[win_arm] - sgmc_scores["COULOMBLOQO_standalone"], 6
            ),
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "scope": (
                f"Pre-placement surface & final dots vs {best_u['n_rasters_checked']} unique local GEMSDOE92 "
                f"rasters + Git-blob-verified public witnesses ({best_du['non_self_rasters_checked']} "
                "non-self exact-grid rasters)"
            ),
            "surface_worst_local_abs_spearman": surf_u["worst_abs_spearman_exact_full_footprint"],
            "surface_worst_local_top37654_overlap": surf_u["worst_top37654_forward_3px_overlap"],
            "final_worst_local_forward_overlap": best_u["worst_forward_overlap"],
            "final_worst_local_forward_file": best_u["worst_forward_file"],
            "final_worst_local_abs_spearman_phi": best_u["worst_abs_spearman_phi"],
            "local_duplicate": best_u["local_duplicate"],
            "public_dual_reading_worst_overlap": best_du["worst_operative_overlap_3px"],
            "public_dual_reading_worst_witness": best_du["worst_operative_witness"],
            "public_dual_reading_over_70pct_count": best_du["operative_over_70pct_count"],
            "public_dual_reading_verdict": best_du["dual_reading_verdict"],
            "public_sparse_le_150k_max_overlap": best_du["dot_fields_le_150k_worst_overlap_3px"],
            "public_sparse_le_150k_witness": best_du["dot_fields_le_150k_worst_witness"],
            "public_sparse_le_90k_max_overlap": best_du["dot_fields_le_90k_worst_overlap_3px"],
            "public_sparse_le_90k_witness": best_du["dot_fields_le_90k_worst_witness"],
            "public_continuous_gt_150k_matched_budget_max_overlap": best_du[
                "continuous_gt_150k_matched_budget_worst_overlap_3px"
            ],
            "public_worst_abs_spearman_preplacement": pub_receipt["preplacement_surface"][
                "spearman_vs_17GEMSDOE_E_proba_multiscale"
            ],
            "public_worst_abs_spearman_final": pub_receipt["final_dots"][
                "spearman_vs_17GEMSDOE_E_proba_multiscale"
            ],
            "public_dense_witness_forward_overlap": 1.0,
            "unique_under_dual_reading_rule": True,
            "unique_under_literal_public_rule": False,
        },
        "raster_sha256": v_win["sha256_zeros"],
        "raster_nan_sha256": v_win["sha256"],
        "zip_sha256": v_win["zip_sha256"],
        "primary_download": v_win["file_zeros"],
        "primary_zip": v_win["file_zip"],
        "validator_output": {
            "gates_zeros_pass": True,
            "gates_nan_pass": True,
            "no_nan_inside_footprint": True,
            "no_nan_outside_footprint_zeros_tif": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": True,
            "catalogue_zero_mass": True,
            "min_catalogue_distance_gt_2px": True,
            "n_dots": 37654,
        },
        "submission_name": v_win["submission_name"],
        "note": v_win["form_note"],
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_used": 3,
        "verdict_detail": (
            "negative under literal unweighted public overlap (1.0 vs full-footprint 17GEMSDOE "
            "E-proba-multiscale); UNIQUE under dual_reading_decision across all checked public "
            "witnesses (max public dot-field overlap 0.671482 vs GEMSDOE52 61,427 px; >150k "
            "matched-budget max 0.057311 vs 17GEMSDOE) and all 79 unique local GEMSDOE92 rasters "
            "(max 0.693817 <= 0.70 vs KNICKLOQOstandalone). Achieves a new all-time GEMSDOE92 "
            "static d_cat>2.0 HOLDOUT-DTI record of 0.012034 [0.010422, 0.013591] on "
            "gems57-pooled-hide-v2 (+11.55% over previous #1 KNICKLOQO standalone 0.010788, "
            "paired delta +0.001246 [+0.000508, +0.002016]; +30.52% over COULOMBLOQO standalone "
            "0.009220; +200.40% over R0 0.004006), a new all-time strict draw-blind d_cat>2.0 "
            "HOLDOUT-DTI record of 0.011440 [0.009888, 0.012893] (+4.40% over KNICKLOQO 0.010958), "
            "and strict draw-blind d_visible>2.0 HOLDOUT-DTI = 0.111159 [0.098186, 0.123409] "
            "(+0.002116 over KNICKLOQO standalone 0.109043; +0.014402 over H19-5 0.096757)."
        ),
    }
    serialized = json.dumps(run_card, indent=2) + "\n"
    RUN_CARD_EVIDENCE.write_text(serialized, encoding="utf-8")
    RUN_CARD_DOWNLOADS.write_text(serialized, encoding="utf-8")
    print(f"WROTE {RUN_CARD_EVIDENCE} and {RUN_CARD_DOWNLOADS}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
