#!/usr/bin/env python3
"""Assemble the Protocol Rule 5 JSON run card for the COULOMB lane lead arm
(seismo, best point HOLDOUT-DTI of the 3 pre-registered experiments) and
enrich all 3 download-audit receipts with verdict + registry fields.

Lead arm: seismo (HOLDOUT-DTI 0.005808) over free (0.005689) and open (0.005184);
free-vs-seismo paired delta includes 0 (statistical tie), so the lead is by
point estimate only and all 3 ship as negative research deliverables.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEAD = "seismo"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    variants = json.loads((ROOT / "evidence/coulomb_variants.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "evidence/coulomb_proxy_audit.json").read_text(encoding="utf-8"))
    screen = json.loads((ROOT / "evidence/coulomb_preplacement_screen.json").read_text(encoding="utf-8"))
    spot = json.loads((ROOT / "evidence/coulomb_public_spotcheck.json").read_text(encoding="utf-8"))
    witness = json.loads((ROOT / "evidence/public_witness_coulomb.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text(encoding="utf-8"))

    by_val = {x["value"]: x for x in variants["variants"]}
    v = by_val[LEAD]
    blk = audit["hide_and_recover_pooled_by_candidate"][LEAD]
    s = blk["scores"][LEAD]
    pd = blk["paired_differences"]
    uni = audit["uniqueness_final_dots"][LEAD]
    surf_uni = screen["coulomb_free_top37654_uniqueness"]

    primary = ROOT / v["file_zeros"]
    sha = sha256_file(primary)
    assert sha == v["sha256_zeros"]
    assert witness["candidate"]["sha256"] == sha
    assert witness["stop_required_vs_this_witness"] is True

    arms = {}
    for k in ("free", "open", "seismo"):
        b = audit["hide_and_recover_pooled_by_candidate"][k]["scores"][k]
        u = audit["uniqueness_final_dots"][k]
        arms[k] = {
            "id": by_val[k]["id"],
            "sha256_zeros": by_val[k]["sha256_zeros"],
            "n_dots": by_val[k]["n_dots"],
            "repulsion_tier": by_val[k]["parent_diff"]["repulsion_tier"],
            "static_holdout_dti": b["dti"],
            "static_holdout_ci95": b["ci95"],
            "sgmc_proxy": audit["sgmc_proxy_dti"][k],
            "worst_local_forward_overlap": u["worst_forward_overlap"],
            "local_duplicate": u["duplicate"],
        }

    card = {
        "schema": "gemsdoe92-protocol-run-card.v1",
        "lane": "COULOMB",
        "primary_variant": LEAD,
        "hypothesis": cards[v["id"]]["hypothesis"],
        "mechanism": cards[v["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
        "experiments_run_in_budget": {"budget_cap": 3, "experiments_executed": 3, "arms": arms},
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "withheld_positive_pixels": 22663,
            "dti": s["dti"],
            "ci95": s["ci95"],
            "delta_vs_R0": pd["R0"]["delta"],
            "delta_vs_R0_ci95": pd["R0"]["ci95"],
            "delta_vs_RELIEFp10": pd["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": pd["RELIEFp10"]["ci95"],
            "delta_vs_BREAKLINEf45": pd["BREAKLINEf45"]["delta"],
            "delta_vs_BREAKLINEf45_ci95": pd["BREAKLINEf45"]["ci95"],
            "delta_vs_APRONRIDGEfree1d": pd["APRONRIDGEfree1d"]["delta"],
            "delta_vs_APRONRIDGEfree1d_ci95": pd["APRONRIDGEfree1d"]["ci95"],
            "delta_vs_HYDROCONDUITf45hydro": pd["HYDROCONDUITf45hydro"]["delta"],
            "delta_vs_HYDROCONDUITf45hydro_ci95": pd["HYDROCONDUITf45hydro"]["ci95"],
            "R0_dti": blk["scores"]["R0"]["dti"],
            "holdout_best_prior_HYDROCONDUITf45hydro_dti": blk["scores"]["HYDROCONDUITf45hydro"]["dti"],
            "promotion_bar_beaten": False,
        },
        "leakage_canary_max_symmetric_auc": audit["leakage_canary_max_symmetric_auc"],
        "leakage_canaries_all_pass_le_0_90": all(
            c["status"] == "REPORT_ONLY_PASS" for c in audit["leakage_canaries"].values()),
        "sgmc_control_proxy": {
            "evidence_class": "PROXY",
            "lead_arm_dti": audit["sgmc_proxy_dti"][LEAD],
            "R0_dti": audit["sgmc_proxy_dti"]["R0"],
            "truth_px": audit["sgmc_truth_px"],
        },
        "correlation_overlap_vs_registry": {
            "local": {
                "registry_rasters_checked": uni["registry_rasters_checked"],
                "worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
                "worst_forward_overlap_file": uni["worst_forward_overlap_file"],
                "worst_abs_spearman": uni["worst_abs_spearman"],
                "worst_abs_spearman_file": uni["worst_abs_spearman_file"],
                "literal_duplicate": uni["duplicate"],
                "preplacement_surface_top37654": {
                    "registry_rasters_checked": surf_uni["registry_rasters_checked"],
                    "worst_forward_overlap": surf_uni["worst_forward_overlap"],
                    "worst_forward_overlap_file": surf_uni["worst_forward_overlap_file"],
                    "worst_abs_spearman": surf_uni["worst_abs_spearman"],
                    "sampled_continuous_spearman": screen["coulomb_free_sampled_spearman"],
                    "duplicate": surf_uni["duplicate"],
                },
            },
            "public_spotcheck_diagnostic_not_clearance": {
                "evidence_file": "evidence/coulomb_public_spotcheck.json",
                "witnesses_checked": len(spot["results"]),
                "full_102_repo_scan_run_this_session": False,
                "dense_17GEMSDOE_forward_overlap": 1.0,
                "sparse_witness_max_forward_overlap": max(
                    max(a["forward_3px"] for a in r["arms"].values())
                    for r in spot["results"] if r["kind"] != "dense"),
            },
            "public_binding_witness": {
                "evidence_file": "evidence/public_witness_coulomb.json",
                "witness": witness["witness"]["raster"],
                "git_blob_sha": witness["witness"]["git_blob_sha"],
                "forward_overlap": witness["forward_overlap_candidate_dots_within_3px_of_witness"],
                "spearman_full_footprint": witness["spearman_full_footprint"],
                "stop_required": True,
            },
        },
        "raster_sha256": sha,
        "raster_sha256_nan_twin": v["sha256"],
        "validator": {
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": True,
            "grid": "EPSG:32611 3730x3292 100m float32 single-band nodata=None",
            "n_dots": v["n_dots"],
            "zero_outside_footprint": True,
            "zero_catalogue_mass": True,
            "gates": "10/10 gems.gates + gems57.validate PASS (see per-file -audit.json)",
        },
        "submission_name": v["submission_name"],
        "file": v["file_zeros"],
        "note": v["form_note"],
        "note_chars": len(v["form_note"]),
        "organizer_score": None,
        "download_status": "OK TO DOWNLOAD FOR RESEARCH (format-valid)",
        "submission_status": "DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT",
        "submission_eligible": False,
        "verdict": "negative",
        "verdict_reason": (
            "HOLDOUT-DTI 0.005808 [0.004846, 0.006809] beats R0 (paired +0.001802 "
            "[+0.000616, +0.002924]) but trails the 0.008549 promotion bar (paired "
            "-0.002741 [-0.004137, -0.001382] vs HYDROCONDUIT f45hydro, CI excludes 0); "
            "SGMC PROXY 0.035654 << R0 0.096060; binding 17GEMSDOE dense witness "
            "forward overlap 1.000 (literal duplicate stop). Locally unique "
            "(worst 0.2661 <= 0.70) and format-valid: negative research deliverable."
        ),
    }
    (ROOT / "evidence/coulomb_run_card.json").write_text(
        json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (ROOT / "docs/downloads/coulomb_run_card.json").write_text(
        json.dumps(card, indent=2) + "\n", encoding="utf-8")

    # Enrich per-file audit receipts (APRONRIDGE pattern) for all 3 arms.
    for k in ("free", "open", "seismo"):
        vv = by_val[k]
        ap = ROOT / "docs/downloads" / f"{vv['id']}-audit.json"
        doc = json.loads(ap.read_text(encoding="utf-8"))
        assert doc["overall_pass"] is True and doc["sha256_zeros"] == vv["sha256_zeros"]
        u = audit["uniqueness_final_dots"][k]
        doc["n_positive_pixels"] = vv["n_dots"]
        doc["n_dots"] = vv["n_dots"]
        doc["submission_eligible"] = False
        doc["verdict"] = "negative"
        doc["run_card"] = "evidence/coulomb_run_card.json"
        doc["local_registry_uniqueness"] = {
            "registry_rasters_checked": u["registry_rasters_checked"],
            "worst_forward_overlap": u["worst_forward_overlap"],
            "worst_forward_overlap_file": u["worst_forward_overlap_file"],
            "worst_abs_spearman": u["worst_abs_spearman"],
            "unique_under_literal_rule": not u["duplicate"],
        }
        doc["public_registry_uniqueness"] = {
            "candidate_hash_matches_scan": (k == LEAD),
            "unique_under_literal_rule": False,
            "stop_required": True,
            "witness_evidence": "evidence/public_witness_coulomb.json",
            "scope": ("Binding single-witness check on lead arm seismo bytes vs Git-blob-verified "
                      "17GEMSDOE E-proba-multiscale (100% footprint positive => forward_overlap=1.0); "
                      "universal halo covers every nonempty in-footprint raster including free/open. "
                      "5-witness sparse diagnostic max 0.4831 (not clearance); no full scan this session."),
        }
        ap.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        print(f"enriched {ap.name}", flush=True)

    (ROOT / "docs/downloads/public_witness_coulomb.json").write_text(
        (ROOT / "evidence/public_witness_coulomb.json").read_text(encoding="utf-8"))
    print("wrote evidence/coulomb_run_card.json + docs/downloads/coulomb_run_card.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
