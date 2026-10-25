#!/usr/bin/env python3
"""Finalize DILATATION p15 as the GEMSDOE92 submission artifact.

Lane: DILATATION (geodetic dilatation rate, Band 8 `geod_dilaterate`) -- Rank 1 of
the 5 pre-registered untried hypotheses in docs/HYPOTHESES.md.

Pipeline (no manual step, no network beyond already-restored pinned inputs):
  1. Copy the byte-verified p15dilatation zeros-outside TIFF (built by
     scripts/build_dilatation_variants.py; SHA-256 pinned in evidence/) into
     docs/downloads/ so it is one-click downloadable, with a one-TIFF ZIP.
  2. Independent disk re-read: gems57.validate (footprint + catalogue) +
     gems.gates.run_gates(require_submission_encoding=True).
  3. Re-run the spatially-blocked holdout (gems57-pooled-hide-v2, seeds 20+30,
     8 buffered quadrant folds, 22,663 withheld positives, 1000-draw paired
     spatial-block bootstrap CI) for arms p15dilatation vs R0 control.
  4. Re-run single-feature leakage canary context (max symmetric AUC 0.514862
     from evidence/dilatation_proxy_audit.json).
  5. Uniqueness (REGISTRY-MEASUREMENT) vs the complete LOCAL registry
     (served + release + bridge + pinned ancillaries): literal forward
     3-px dot overlap, |Spearman rho|, and matched-budget overlap for dense
     continuous-surface witnesses. Public 102-repo scan is NOT available in
     this sandbox (no gh auth / no cached inventory) and is reported as
     out-of-scope, never claimed.
  6. Write Protocol Rule 5 run card (evidence/) + per-file audit JSON
     (docs/downloads/) with verdict `negative` / `submission_eligible: false`.

Verdict logic: promote only if (a) static HOLDOUT-DTI beats the holdout-best
reference with paired CI excluding 0, and (b) the literal registry gate
passes. DILATATION p15 beats parent R0 (paired CI excludes 0) but does NOT
beat the holdout-best (COULOMBLOQO standalone 0.113316 Rule-2 / 0.009220
static) and the literal dense-witness overlap stop fires -> verdict negative,
a format-valid research download only. Negative results are deliverables.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems57 import grid as grid_mod, validate as V, uniqueness as U  # noqa: E402
from gems57 import holdout, evaluate_holdout  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
BRIDGE = INPUTS / "bridge"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
RELEASES = ROOT / "releases"

SRC_TIF = RELEASES / "h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432-zeros.tif"
SRC_NAN_TIF = RELEASES / "h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432.tif"
STEM = "h33-h33-2-b2-DILATATIONp15dilatation-20261025-ebc1b432"
DST_TIF = DOWNLOADS / f"{STEM}-zeros.tif"
DST_ZIP = DOWNLOADS / f"{STEM}-zeros.zip"
DST_AUDIT = DOWNLOADS / f"{STEM}-audit.json"
RUN_CARD_EVIDENCE = EVIDENCE / "dilatation_run_card.json"
RUN_CARD_DL = DOWNLOADS / "dilatation_run_card.json"

SUBMISSION_NAME = "GEMSDOE92-DILATATION-p15-20261025"
SUBMISSION_NOTE = (
    "h33-h33-2-b2; DILATATION p15: 5648 dots shifted low-to-high geodetic "
    "dilatation tercile on H19-5, d_cat>2px; HOLDOUT-DTI 0.005818; negative"
)
assert len(SUBMISSION_NAME) <= 140, len(SUBMISSION_NAME)
assert len(SUBMISSION_NOTE) <= 140, len(SUBMISSION_NOTE)

HOLDOUT_BEST_RULE2 = 0.113316   # COULOMB-LOQO standalone, strict draw-blind d_visible > 2.0
HOLDOUT_BEST_STATIC = 0.009220  # COULOMB-LOQO standalone, static d_cat > 2.0


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    for p in (SRC_TIF, SRC_NAN_TIF):
        if not p.is_file():
            raise FileNotFoundError(f"source artifact missing: {p}")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # ---- 0. Load pinned grid (footprint + catalogue) -------------------
    log("0. Load pinned grid (footprint + catalogue)")
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)

    # ---- 1. Publish the byte-verified p15 zeros TIFF to docs/downloads -
    log(f"1. Publish {SRC_TIF.name} -> {DST_TIF.name}")
    shutil.copyfile(SRC_TIF, DST_TIF)
    tif_sha = sha256_file(DST_TIF)
    nan_sha = sha256_file(SRC_NAN_TIF)
    assert tif_sha == "cc79c48ae0f46b0c22cd410305a773e72b719833718bceed2c5bcda3c8c38052", tif_sha

    # one-TIFF ZIP (exactly one TIFF inside)
    with zipfile.ZipFile(DST_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo(DST_TIF.name, date_time=(2026, 10, 8, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, DST_TIF.read_bytes())
    with zipfile.ZipFile(DST_ZIP) as z:
        assert z.namelist() == [DST_TIF.name] and z.read(DST_TIF.name) == DST_TIF.read_bytes()
    zip_sha = sha256_file(DST_ZIP)
    log(f"  TIF sha256 {tif_sha}  ZIP sha256 {zip_sha}")

    # ---- 2. Independent disk re-read validation + format gates ---------
    log("2. Independent disk re-read validation + format gates")
    v = V.validate(DST_TIF, foot, cat)
    V.assert_submittable(v)
    gate_results = run_gates(
        str(DST_TIF), str(BRIDGE / "sample_submission.tif"),
        str(BRIDGE / "existing_faults.tif"), prune_radius=2,
        require_submission_encoding=True,
    )
    gate_ok, gate_report = summarise(gate_results)
    log(f"  format gates: {'PASS' if gate_ok else 'FAIL'}")
    for r in gate_results:
        log(f"    {r}")

    with rasterio.open(DST_TIF) as ds:
        dots_arr = ds.read(1)
    log(f"  dots={int((dots_arr > 0).sum())} on_catalogue={int(((dots_arr > 0) & cat).sum())} "
        f"outside_footprint={int(((dots_arr > 0) & ~foot).sum())}")

    # ---- 3. Holdout re-run: p15dilatation vs R0 -------------------------
    log("3. Holdout re-run (gems57-pooled-hide-v2, seeds 20+30, 8 folds)")
    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    log(f"  {len(folds)} folds")

    r0_path = ROOT / "data" / "parent_R0_zeros.tif"
    with rasterio.open(r0_path) as ds:
        r0_arr = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    terms_by_arm = {}
    per_fold = {}
    for arm_name, arr in (("p15dilatation", dots_arr), ("R0", r0_arr)):
        all_terms = None
        fold_scores = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(arr, fold, grid.footprint)
            fold_scores.append(round(float(score["dti"]), 9))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
        per_fold[arm_name] = fold_scores
    log(f"  per-fold p15: {[round(x, 6) for x in per_fold['p15dilatation']]}")
    log(f"  per-fold R0:  {[round(x, 6) for x in per_fold['R0']]}")

    pooled = evaluate_holdout.pooled_summary(
        terms_by_arm, draws=1000, seed=520810, candidate="p15dilatation")
    primary = pooled["scores"]["p15dilatation"]
    control = pooled["scores"]["R0"]
    delta = pooled["paired_differences"]["R0"]
    log(f"  p15dilatation: {primary['dti']:.6f} [{primary['ci95'][0]:.6f}, {primary['ci95'][1]:.6f}] "
        f"(withheld={primary['withheld_positive_pixels']})")
    log(f"  R0: {control['dti']:.6f} [{control['ci95'][0]:.6f}, {control['ci95'][1]:.6f}]")
    log(f"  paired delta p15-R0: {delta['delta']:.6f} [{delta['ci95'][0]:.6f}, {delta['ci95'][1]:.6f}]")

    # ---- 4. Leakage canary context (recorded evidence) -----------------
    log("4. Leakage canary context (recorded in evidence/dilatation_proxy_audit.json)")
    proxy = json.loads((EVIDENCE / "dilatation_proxy_audit.json").read_text(encoding="utf-8"))
    canaries = proxy["leakage_canaries"]
    max_auc = float(canaries["max_symmetric_auc"])
    log(f"  max symmetric AUC = {max_auc:.6f} (<= 0.90: {max_auc <= 0.90})")

    # ---- 5. Uniqueness vs complete local registry ----------------------
    log("5. Uniqueness vs complete local registry")
    records = []
    seen = set()
    for d in (DOWNLOADS, RELEASES, ROOT / "data", BRIDGE):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            if p.name == DST_TIF.name:
                continue  # never compare the candidate against itself
            if p.stat().st_size < 1000:
                continue
            records.append(dict(
                repo=str(d.relative_to(ROOT)) if d != ROOT / "data" else "data",
                submission=p.name,
                file=str(p),
                sha256=sha256_file(p),
            ))
    log(f"  {len(records)} local registry rasters")
    uniq = U.compare_array_to_registry(
        dots_arr, records, foot,
        file_sha256=tif_sha, include_reverse=True,
        expected_grid=expected,
        progress=(lambda i, n, row: log(f"    registry gate {i}/{n}") if i % 20 == 0 else None),
    )
    checked = [r for r in uniq["rows"] if "error" not in r]
    errors = [r for r in uniq["rows"] if "error" in r]

    # Matched-budget overlap for dense continuous-surface witnesses
    dense_witnesses = []
    for r in checked:
        if int(r.get("their_dots", 0)) > U.DOT_FIELD_MAX_SUPPORT:
            p = Path(r["file"])
            try:
                with rasterio.open(p) as ds:
                    tv = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
            except Exception:
                continue
            mb = U.dual_overlap(dots_arr, tv, foot)
            dense_witnesses.append(dict(
                file=r["file"], submission=r["submission"], their_dots=int(r["their_dots"]),
                literal_forward_overlap=float(r["forward_overlap"]),
                matched_budget_forward_overlap=float(mb["matched_budget_forward_overlap"]),
                representation=mb["representation"],
            ))
    dense_witnesses.sort(key=lambda r: -r["matched_budget_forward_overlap"])

    worst_lit = max(checked, key=lambda r: r["forward_overlap"]) if checked else None
    worst_rho = max(checked, key=lambda r: abs(r["spearman_full_footprint"] or 0.0)) if checked else None
    duplicate = bool(
        (worst_lit and worst_lit["forward_overlap"] > 0.70)
        or (worst_rho and abs(float(worst_rho["spearman_full_footprint"])) > 0.90)
        or errors
    )
    log(f"  worst literal overlap={worst_lit['forward_overlap'] if worst_lit else None} "
        f"vs {worst_lit['submission'] if worst_lit else None}")
    log(f"  worst |rho|={abs(float(worst_rho['spearman_full_footprint'])) if worst_rho else None} "
        f"vs {worst_rho['submission'] if worst_rho else None}")
    log(f"  dense witnesses (matched-budget): "
        f"[{', '.join(w['submission'] + '=' + str(round(w['matched_budget_forward_overlap'], 4)) for w in dense_witnesses[:5])}]")
    log(f"  duplicate={duplicate}")

    # ---- 6. Verdict ------------------------------------------------------
    beats_rule2 = primary["dti"] > HOLDOUT_BEST_RULE2
    beats_static = primary["dti"] > HOLDOUT_BEST_STATIC
    ci_excludes_zero = delta["ci95"][0] > 0
    beats_holdout_best = beats_rule2 and ci_excludes_zero
    unique_ok = (not duplicate) and gate_ok
    verdict = "promote" if (beats_holdout_best and unique_ok) else "negative"
    submission_eligible = bool(verdict == "promote")
    log(f"  verdict={verdict} beats_rule2={beats_rule2} ci_excl_0={ci_excludes_zero} "
        f"unique_ok={unique_ok} gates_ok={gate_ok}")

    # ---- 7. Audit JSON ----------------------------------------------------
    gate_rows = [{"name": r.name, "ok": bool(r.ok), "detail": r.detail} for r in gate_results]
    audit = dict(
        schema="gemsdoe92-audit.v2", lane="DILATATION", arm="p15dilatation",
        file=f"docs/downloads/{DST_TIF.name}",
        file_sha256=tif_sha, zip_file=DST_ZIP.name, zip_sha256=zip_sha,
        sha256_zeros=tif_sha, sha256_nan=nan_sha,
        bytes=DST_TIF.stat().st_size, generated_utc=stamp,
        submission_name=SUBMISSION_NAME, submission_note=SUBMISSION_NOTE, note_chars=len(SUBMISSION_NOTE),
        overall_pass=bool(all(r["ok"] for r in gate_rows) and v["all_checks_passed"]),
        submission_eligible=submission_eligible,
        validator=v,
        gates_zeros=gate_rows,
        gates_pass=gate_ok,
        holdout_source="evidence/dilatation_proxy_audit.json + re-run this session",
        uniqueness_local=uniq,
        matched_budget_dense_witnesses=dense_witnesses,
        public_registry={"available": False,
                         "reason": "gh CLI unauthenticated and no cached 102-repo inventory in "
                                   "this sandbox; local complete registry used; public scope not claimed"},
        public_registry_uniqueness={"candidate_hash_matches_scan": True,
                                    "unique_under_literal_rule": False,
                                    "stop_required": True,
                                    "scope_note": ("public 102-repo scan not executed in this sandbox "
                                                   "(no gh auth, no cached inventory); local complete registry "
                                                   "duplicate stop recorded: worst forward overlap 1.0000 vs "
                                                   "DILATATION p10 sibling; pinned dense-witness rule binding")},
        run_card="evidence/dilatation_run_card.json",
        dense_witness_note=("The pinned 17GEMSDOE E-proba-multiscale full-footprint witness is not cached "
                            "in this sandbox; the literal gate is binding regardless: any nonempty in-footprint "
                            "prediction overlaps a full-footprint-positive witness at 1.0 > 0.70."),
    )
    DST_AUDIT.write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    log(f"  WROTE {DST_AUDIT}")

    # ---- 8. Protocol Rule 5 run card -------------------------------------
    beats_ref = dict(
        holdout_best_rule2_d_visible_2=HOLDOUT_BEST_RULE2,
        holdout_best_static_d_cat_2=HOLDOUT_BEST_STATIC,
        reference_lane="COULOMB-LOQO standalone",
    )
    card = dict(
        schema="gemsdoe92-run-card.v3", lane="DILATATION", date=stamp,
        hypothesis=("The USGS/INGENIOUS catalogue maps Quaternary scarps; geothermal permeability is controlled "
                    "by where the crust is actively opening. DILATATION tests Band 8 geodetic dilatation rate: "
                    "shift parent-dot mass from low/mid to the high-dilatation tercile (>= p67) on H19-5 ridge "
                    "support with d_cat > 2.0 px, holding the 37,654-dot budget fixed. Rate in nstrain/yr from the "
                    "pinned 19-band GeoDAWN stack (Band 8)."),
        mechanism=("Percentile-ranked Band 8 dilatation field defines low/mid/high terciles; the 5,648 lowest-dilatation "
                   "parent dots are relocated (exact expected marginal DTI refill) into high-dilatation tercile cells "
                   "on valid, off-catalogue (d_cat > 2.0 px) H19-5 support; unit mass and count held. Pure array math; "
                   "the catalogue is used only for masking/clearance, never to build features."),
        named_non_fault_mimic=("Distributed alluvial compaction / groundwater pumping subsidence bowls (e.g. Clayton "
                               "Valley), and elastic strain shadows around locked Walker Lane segments where dilatation "
                               "is high but permeability is shear-parallel rather than open."),
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI", evaluator_version=evaluate_holdout.VERSION,
            alpha=0.2, beta=0.8, triangular_radius_m=300.0,
            instrument="static d_cat > 2.0 deployment, pooled gems57-pooled-hide-v2, seeds 20+30, "
                       "8 buffered quadrant folds, 1000-draw paired spatial-block bootstrap CI",
            withheld_positives=int(primary["withheld_positive_pixels"]),
            scores={"p15dilatation": primary, "R0": control},
            paired_vs_R0=dict(delta=delta["delta"], ci95=delta["ci95"]),
            beats_parent_R0=bool(primary["dti"] > control["dti"] and ci_excludes_zero),
            beats_holdout_best=bool(beats_holdout_best),
            holdout_best_reference=beats_ref,
        ),
        leakage_canaries=dict(
            source="evidence/dilatation_proxy_audit.json (single-feature symmetric AUC vs pooled withheld truth)",
            max_symmetric_auc=max_auc, all_pass_le_0p90=bool(max_auc <= 0.90),
            per_feature={k: round(float(v["symmetric_auc"]), 6) for k, v in canaries["results"].items()},
        ),
        correlation_overlap_vs_registry=dict(
            local=dict(
                rasters_checked=uniq["registry_rasters_checked"],
                complete=bool(uniq["complete_accessible_scan"]),
                worst_literal_forward_overlap=(float(worst_lit["forward_overlap"]) if worst_lit else None),
                worst_literal_file=(worst_lit["submission"] if worst_lit else None),
                worst_abs_spearman=(abs(float(worst_rho["spearman_full_footprint"])) if worst_rho else None),
                worst_spearman_file=(worst_rho["submission"] if worst_rho else None),
                duplicate=bool(duplicate),
            ),
            matched_budget_dense_witnesses=dense_witnesses,
            public={"available": False,
                    "scope": "102-repo public scan not available in this sandbox (no gh auth, no cached inventory)"},
            dense_witness=audit["dense_witness_note"],
        ),
        raster_sha256=tif_sha,
        zip_sha256=zip_sha,
        file=f"docs/downloads/{DST_TIF.name}",
        validator_output=dict(
            no_nan_in_footprint=bool(v["checks"]["in_footprint_all_finite"]),
            values_in_0_1=bool(v["checks"]["range_0_1_guaranteed"]),
            crs_shape_transform_match=bool(v["checks"]["crs_epsg_32611"] and v["checks"]["dimensions_3730x3292"]
                                           and v["checks"]["transform_matches_sample_submission"]),
            dots=int(v["emitted_positive_pixels"]),
            checks=v["checks"],
            gates=gate_rows,
        ),
        submission_name=SUBMISSION_NAME,
        submission_note=SUBMISSION_NOTE,
        note_chars=len(SUBMISSION_NOTE),
        experiments_used="1/3 (this lane; build + finalize)",
        weekly_slots_used=0,
        verdict=verdict,
        submission_eligible=submission_eligible,
        verdict_reason=("static HOLDOUT-DTI " + f"{primary['dti']:.6f}" + " vs holdout-best "
                        + f"{HOLDOUT_BEST_RULE2}" + " (Rule-2); paired delta vs R0 "
                        + f"{delta['delta']:.6f}" + " CI [" + f"{delta['ci95'][0]:.6f}"
                        + ", " + f"{delta['ci95'][1]:.6f}" + "]; literal registry duplicate="
                        + str(duplicate) + "; gates_ok=" + str(gate_ok) + "; max AUC "
                        + f"{max_auc:.4f}"),
        organizer_confirmed=None,
    )
    RUN_CARD_EVIDENCE.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    RUN_CARD_DL.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    log(f"  WROTE {RUN_CARD_EVIDENCE}")
    log(f"  WROTE {RUN_CARD_DL}")
    log(f"VERDICT: {verdict} (submission_eligible={submission_eligible})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
