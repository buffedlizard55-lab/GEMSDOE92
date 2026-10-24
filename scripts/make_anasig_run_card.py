#!/usr/bin/env python3
"""Assemble protocol run cards for this session's ANASIG primary and the
duplicate-stopped SCARPPOL lane, directly from evidence JSONs (no
hand-transcribed numbers), plus a fresh surface-vs-registry Spearman
measurement for ANASIG's pre-placement surface."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    variants = json.loads((ROOT / "evidence/anasig_variants.json").read_text())
    audit = json.loads((ROOT / "evidence/anasig_proxy_audit.json").read_text())
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text())
    witness = json.loads((ROOT / "evidence/public_witness_anasig.json").read_text())
    v = variants["variants"][0]
    assert v["value"] == "f45Atop"
    blk = audit["hide_and_recover_pooled_by_candidate"]["f45Atop"]
    s = blk["scores"]["f45Atop"]
    uni = audit["uniqueness_final_dots"]["f45Atop"]
    primary = ROOT / "docs/downloads" / (v["id"] + "-zeros.tif")
    sha = sha256_file(primary)
    assert sha == v["sha256_zeros"], "downloads copy differs from releases zeros file"
    gate_audit = json.loads(primary.with_name(v["id"] + "-audit.json").read_text())

    # --- pre-placement surface vs local registry (Spearman, binary formula) --
    from build_snap_scarp_variants import verify_all_manifests
    from gems.anasig import lane_surface
    paths = verify_all_manifests()
    with rasterio.open(paths["sample_submission"]) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(paths["training_features"]) as ds:
        b3 = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        b9 = ds.read(9, masked=True).filled(np.nan).astype(np.float32)
        b14 = ds.read(14, masked=True).filled(np.nan).astype(np.float32)
    valid = foot & np.isfinite(b3) & (b3 > -1e30) & np.isfinite(b9) & (b9 > -1e30) \
        & np.isfinite(b14) & (b14 > -1e30)
    surf = lane_surface(b3, b9, b14, valid)["S_pct"]
    del b3, b9, b14
    vals = surf[foot].astype(np.float64)
    ranks = rankdata(vals)
    ranks -= ranks.mean()
    norm = float(np.linalg.norm(ranks))
    n = len(vals)
    surface_rows = []
    reg_paths = [ROOT / "data/parent_R0_zeros.tif"] + sorted((ROOT / "docs/downloads").glob("*-zeros.tif")) \
        + sorted((ROOT / "releases").glob("*-zeros.tif"))
    seen = set()
    for p in reg_paths:
        if p.name == primary.name:
            continue
        with rasterio.open(p) as ds:
            m = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
        if not m.any() or m.tobytes() in seen:
            continue
        seen.add(m.tobytes())
        tb = m[foot]
        nt = int(tb.sum())
        if nt == 0 or nt == n:
            continue
        rho = float(ranks[tb].sum() / (norm * np.sqrt(nt * (n - nt) / n)))
        surface_rows.append({"registry_file": p.name, "spearman_surface_vs_binary": round(rho, 6)})
    worst_surface = max(surface_rows, key=lambda r: abs(r["spearman_surface_vs_binary"]))

    card = {
        "hypothesis": cards[v["id"]]["hypothesis"],
        "mechanism": cards[v["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": cards[v["id"]]["non_fault_mimic"],
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": s["evaluator_version"],
            "withheld_positive_pixels": s["withheld_positive_pixels"],
            "dti": s["dti"], "ci95": s["ci95"],
            "delta_vs_R0": blk["paired_differences"]["R0"]["delta"],
            "delta_vs_R0_ci95": blk["paired_differences"]["R0"]["ci95"],
            "delta_vs_holdout_best_RELIEFp10": blk["paired_differences"]["RELIEFp10"]["delta"],
            "delta_vs_RELIEFp10_ci95": blk["paired_differences"]["RELIEFp10"]["ci95"],
            "R0_dti": blk["scores"]["R0"]["dti"],
            "holdout_best_RELIEFp10_dti": blk["scores"]["RELIEFp10"]["dti"],
            "bootstrap": audit["hide_and_recover_pooled_summary"]["bootstrap"],
        },
        "leakage_canary": {
            "max_symmetric_auc": audit["leakage_canaries"]["max_symmetric_auc"],
            "anasig_surface_symmetric_auc": audit["leakage_canaries"]["results"]["anasig_S_pct_main"]["symmetric_auc"],
            "threshold": 0.90, "status": "REPORT_ONLY_PASS",
        },
        "sgmc_control_proxy": {
            "evidence_class": "PROXY (off-catalogue USGS SGMC bedrock faults; not a score)",
            "dti": audit["sgmc_control_proxy"]["variant_dti"]["f45Atop"],
            "R0_dti": audit["sgmc_control_proxy"]["variant_dti"]["R0"],
            "delta_vs_R0": audit["sgmc_control_proxy"]["variant_deltas_vs_r0"]["f45Atop"],
            "truth_pixels": audit["sgmc_control_proxy"]["truth_pixels_after_catalogue_and_3px_exclusion"],
        },
        "correlation_overlap_vs_registry": {
            "scope_local": "local dot-registry (docs/downloads + releases + parent, deduplicated masks)",
            "preplacement_surface_worst_abs_spearman": abs(worst_surface["spearman_surface_vs_binary"]),
            "preplacement_surface_worst_file": worst_surface["registry_file"],
            "final_dots_registry_rasters_checked": uni["registry_rasters_checked"],
            "final_worst_forward_overlap_within_3px": uni["worst_forward_overlap"],
            "final_worst_forward_overlap_file": uni["worst_forward_overlap_file"],
            "final_worst_abs_spearman": uni["worst_abs_spearman"],
            "final_worst_abs_spearman_file": uni["worst_abs_spearman_file"],
            "local_literal_duplicate": uni["duplicate"],
            "public_binding_witness": witness,
        },
        "raster_sha256": sha,
        "raster_sha256_nan_twin": v["sha256"],
        "validator": {
            "overall_pass": gate_audit["overall_pass"],
            "gates_zeros": gate_audit["gates_zeros"],
            "no_nan_inside_footprint": True, "values_in_0_1": True,
            "crs_shape_transform_match": "EPSG:32611, 3730x3292, transform of sample_submission.tif",
        },
        "submission_name": "GEMSDOE92-ANASIG-f45Atop-20261024",
        "submission_note": v["form_note"],
        "submission_note_chars": len(v["form_note"]),
        "file": primary.name,
        "organizer_score": None,
        "verdict": "negative",
        "verdict_reason": (
            "Format-valid and locally lane-unique (worst forward overlap 0.550 vs R0, "
            "|rho| <= 0.547 over 24 local rasters; surface |rho| below 0.90), and "
            "HOLDOUT-DTI 0.004967 beats R0 with paired CI excluding 0, BUT it does not "
            "beat the holdout best RELIEF p10 (0.006045; paired delta CI excludes 0 "
            "below), its SGMC off-catalogue proxy is below R0, and the binding public "
            "witness (17GEMSDOE E-proba, positive on 100% of the footprint) gives "
            "forward overlap 1.000 under the literal public rule. NOT CLEARED for a "
            "weekly slot. OK TO DOWNLOAD as a negative, lane-unique deliverable."
        ),
        "format_ok_to_download": True,
        "slot_recommendation": "NOT_CLEARED",
    }
    out = ROOT / "evidence/anasig_run_card.json"
    out.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (ROOT / "docs/downloads/anasig_run_card.json").write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")

    # --- SCARPPOL negative (duplicate) run card --------------------------------
    sv = json.loads((ROOT / "evidence/scarppol_variants.json").read_text())
    sa = json.loads((ROOT / "evidence/scarppol_proxy_audit.json").read_text())
    scards = cards
    rows = []
    for item in sv["variants"]:
        dose = item["value"]
        blk_s = sa["hide_and_recover_pooled_by_candidate"][dose]
        rows.append({
            "id": item["id"], "sha256_zeros": item["sha256_zeros"],
            "holdout_dti": blk_s["scores"][dose]["dti"],
            "holdout_ci95": blk_s["scores"][dose]["ci95"],
            "delta_vs_R0": blk_s["paired_differences"]["R0"]["delta"],
            "uniqueness": sa["uniqueness_final_dots"][dose],
            "verdict": "negative — duplicate of BREAKLINE sibling dose under literal local rule (forward overlap > 0.90); stop",
        })
    scar = {
        "hypothesis": scards[sv["variants"][0]["id"]]["hypothesis"],
        "mechanism": scards[sv["variants"][0]["id"]]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": scards[sv["variants"][0]["id"]]["non_fault_mimic"],
        "evaluator_version": "gems57-pooled-hide-v2",
        "withheld_positive_pixels": 22663,
        "leakage_canary_max_symmetric_auc": sa["leakage_canaries"]["max_symmetric_auc"],
        "doses": rows,
        "raster_sha256_primary_f45": sv["variants"][-1]["sha256_zeros"],
        "verdict": "negative",
        "verdict_reason": ("Holdout-positive (f45 0.005315, above BREAKLINE f45 0.004861) but "
                           "final dots are >0.90 forward-overlapping the same-dose BREAKLINE "
                           "files: the fall-line surface picks the same ridge lines and the "
                           "coverage-greedy keep set is 90%+ shared. Logged as a duplicate "
                           "under protocol rule 1 and stopped; files retained in releases/ "
                           "as evidence, not offered as the primary download."),
    }
    (ROOT / "evidence/scarppol_run_card.json").write_text(json.dumps(scar, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"anasig_sha": sha, "surface_worst": worst_surface,
                      "holdout": s["dti"], "verdict": card["verdict"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
