#!/usr/bin/env python3
"""Assemble the served files, audit receipt and protocol run card for the LCS candidate.

Everything public is DERIVED from evidence JSON (build, registry gates for both phases, proxy audit,
policy) through gems.uniqueness_policy.decide and gems.verdict.derive.  Nothing is typed in.

Writes:
  docs/downloads/<variant>-zeros.tif, .zip, <variant>-audit.json
  evidence/lcs_run_card.json  and  docs/downloads/lcs_run_card.json
  docs/downloads/lcs_{build,registry_final,registry_surface,proxy_audit}.json   (evidence copies)
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import lcs, uniqueness_policy, verdict  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

EV = ROOT / "evidence"
DL = ROOT / "docs" / "downloads"
R0_CLAIM = 0.2778


def load(name):
    return json.loads((EV / name).read_text(encoding="utf-8"))


def main() -> int:
    build = load("lcs_build.json")
    final = load("lcs_registry_final.json")
    surface = load("lcs_registry_surface.json")
    proxy = load("lcs_proxy_audit.json")
    policy_doc = uniqueness_policy.load_policy()
    cand = build["candidate"]
    rel = ROOT / "releases" / cand["file"]
    variant = rel.stem.removesuffix("-zeros")
    sha = sha256_file(rel)
    if not (sha == cand["sha256"] == final["candidate_sha256"]):
        raise SystemExit("candidate bytes differ between build receipt, registry gate and disk: re-run the gate")

    DL.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rel, DL / rel.name)
    shutil.copy2(rel.with_suffix(".zip"), DL / rel.with_suffix(".zip").name)
    served = DL / rel.name

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp, cat = grid.footprint, grid.catalogue
    sample, labels = ROOT / "data" / "bridge" / "sample_submission.tif", ROOT / "data" / "bridge" / "labels.tif"
    gates = run_gates(str(served), str(sample), str(labels), prune_radius=None)       # strict 3 px (brief constraint 4)
    gates_ok, gates_text = summarise(gates)
    val = validate(served, fp, cat)
    assert_submittable(val)
    with rasterio.open(served) as ds:
        a = ds.read(1)
    nn_ok = bool(np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1)
    format_pass = bool(gates_ok and val["all_checks_passed"] and nn_ok and sha256_file(served) == sha)

    policy = uniqueness_policy.decide(surface, final, policy_doc)
    pooled = proxy["holdout"]["scores"]
    s = pooled["scores"]
    paired = pooled["paired_differences"]
    vs_best = paired.get("RELIEF_p10_holdout_best")
    canary_ok = bool(proxy["leakage_canary"]["symmetric_auc"] <= 0.90)
    proj = build["projections_MODEL"]
    r0_proj = build["r0_reference"]["dti_projection_by_construction"]
    loo = load("lcs_loo_calibration.json")
    mae = loo["grid"][str(lcs.GAMMA)]["mae"]
    loo_band = lcs.dti_band_from_credit_error(mae)
    worst_scenario = min(proj["dti_null"], proj["dti_shrunk"])
    model_ok = bool(worst_scenario >= r0_proj - loo_band)
    v = verdict.derive(format_pass, policy, canary_ok, model_ok, vs_best)

    tier_summary = {t: dict(passed=policy["tiers"][t]["passed"],
                            surface=dict(max_forward_overlap=policy["tiers"][t]["surface"].get("max_forward_overlap"),
                                         n_over_0_70=policy["tiers"][t]["surface"].get("n_over_overlap"),
                                         max_abs_spearman=policy["tiers"][t]["surface"].get("max_abs_spearman"),
                                         n_rasters=policy["tiers"][t]["surface"].get("n_distinct")),
                            final=dict(max_forward_overlap=policy["tiers"][t]["final"].get("max_forward_overlap"),
                                       n_over_0_70=policy["tiers"][t]["final"].get("n_over_overlap"),
                                       max_abs_spearman=policy["tiers"][t]["final"].get("max_abs_spearman"),
                                       n_rasters=policy["tiers"][t]["final"].get("n_distinct"),
                                       n_files=policy["tiers"][t]["final"].get("n_files"),
                                       worst=policy["tiers"][t]["final"].get("worst")))
                    for t in "SLT"}

    run_card = dict(
        schema="gemsdoe92-run-card.v2", lane="LCS", created_utc="2026-10-24", evidence_class="MODEL+REGISTRY-MEASUREMENT+HOLDOUT-DTI",
        hypothesis=("Dots chosen where several INDEPENDENT detector lanes agree, with each lane's vote weighted by its "
                    "leaderboard-implied credit per dot, are more likely to land within 300 m of a new-fault pixel than the "
                    "single skeleton lane alone, and can be made unique by construction (<= 67 % overlap with every scored "
                    "lane and with every non-blanket registry raster)."),
        mechanism=("Multi-modality agreement (potential-field edges, slope breaks, radon, strain, geologic) suppresses modality-specific "
                   "mimics; a halo-survival factor and vote excess measured inside distance-to-catalogue strata prevent "
                   "re-detections of mapped faults (masked by the scorer, DrivenData thread 11516) from posing as consensus; "
                   "selection is a Lagrangian-capped greedy at a matched 37,654-dot budget, 2.83 px spacing, > 3 px from the catalogue."),
        named_non_fault_mimics=["range-front lithologic contacts and erosional escarpments shared by all potential-field lanes",
                                "geophysical re-detection of already-mapped faults (halo, handled by stratification)",
                                "survey levelling / block-seam artefacts common to several magnetic lanes"],
        leaderboard_calibration=dict(
            evidence_class="CLAIM+MODEL", concordance=load("lb_concordance_20261024.json")["concordance"],
            loo_calibration=loo),
        holdout=dict(
            evidence_class="HOLDOUT-DTI", evaluator=proxy["evaluator"], withheld_positive_pixels=proxy["holdout"]["withheld_positive_pixels"],
            scores={k: dict(dti=v_["dti"], ci95=v_["ci95"]) for k, v_ in s.items()},
            paired_vs_LCS=paired, not_fold_pure=proxy["holdout"]["not_fold_pure"],
            holdout_best_bar="RELIEF_p10_holdout_best", lcs_minus_best=vs_best,
            canary=proxy["leakage_canary"], sgmc_control=proxy["sgmc_control"]),
        registry=dict(evidence_class="REGISTRY-MEASUREMENT", scope=final["scope"], policy=dict(decisive_tier=policy_doc["decisive_tier"],
                      thresholds=policy_doc["thresholds"], rationale=policy_doc["rationale"]), tiers=tier_summary,
                      blanket_rasters=final["blankets"], complete_accessible_scan=final["complete_accessible_scan"],
                      surface_support_pixels=int(surface["candidate_dots"]),
                      random_control=json.loads((EV / "lcs_random_control_registry.json").read_text())["tier_T_all"] if (EV / "lcs_random_control_registry.json").exists() else None,
                      literal_registry_rule_passed=policy["literal_passed"]),
        projection_MODEL=dict(note="projection, never a score; one typical leave-one-lane-out model error is the band below", **proj,
                              r0_by_construction=r0_proj, loo_mae_credit_per_dot=mae, loo_band=loo_band, model_ok=model_ok),
        raster_sha256=sha, validator=dict(local_checks=val["checks"], all_checks_passed=val["all_checks_passed"], gates=[str(g) for g in gates]),
        name=cand["name"], note=cand["note"], note_chars=len(cand["note"]),
        status=dict(ok_to_download=v["ok_to_download"], ok_to_submit=v["ok_to_submit"], blocking_reasons=v["blocking_reasons"],
                    slot_recommended=v["slot_recommended"], literal_registry_rule_passed=v["literal_registry_rule_passed"]),
        verdict=v["verdict"],
        verdict_basis=("promote iff ok_to_submit AND paired HOLDOUT-DTI CI vs the recorded holdout best is entirely > 0; "
                       f"beats_holdout_best={v['beats_holdout_best']}"),
        slot_note=("No weekly slot is selected, used or implied by this repository. The selector is a separate human step within "
                   "3 submissions per week; no organizer receipt exists for this file."),
    )
    (EV / "lcs_run_card.json").write_text(json.dumps(run_card, indent=2, default=float) + "\n")
    shutil.copy2(EV / "lcs_run_card.json", DL / "lcs_run_card.json")
    for name in ("lcs_build", "lcs_registry_final", "lcs_registry_surface", "lcs_proxy_audit"):
        shutil.copy2(EV / f"{name}.json", DL / f"{name}.json")

    audit = dict(
        gates_zeros=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates], gates_zeros_pass=bool(gates_ok),
        file=served.name, sha256_zeros=sha, n_positive_pixels=int((a > 0).sum()), n_dots=int((a > 0).sum()),
        overall_pass=format_pass, submission_eligible=v["ok_to_submit"], verdict=v["verdict"],
        run_card="evidence/lcs_run_card.json",
        distance_gate_radius_px=3, note="distance_from_catalogue gate run at the strict 3 px radius, not the R0-lineage 2 px override",
        public_registry_uniqueness=dict(
            candidate_hash_matches_scan=bool(final["candidate_sha256"] == sha),
            unique_under_literal_rule=bool(policy["literal_passed"]), stop_required=bool(not policy["literal_passed"]),
            decisive_tier=policy_doc["decisive_tier"], decisive_tier_passed=bool(policy["decisive_passed"]),
            tiers={t: dict(passed=policy["tiers"][t]["passed"]) for t in "SLT"},
            scope=final["scope"]),
        status=run_card["status"])
    (DL / f"{variant}-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(dict(file=served.name, format_pass=format_pass, status=run_card["status"], verdict=v["verdict"],
                          tiers={t: policy["tiers"][t]["passed"] for t in "SLT"},
                          lcs_minus_holdout_best=vs_best, canary=proxy["leakage_canary"]["symmetric_auc"],
                          projection=dict(null=proj["dti_null"], shrunk=proj["dti_shrunk"], naive=proj["dti_naive"])), indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
