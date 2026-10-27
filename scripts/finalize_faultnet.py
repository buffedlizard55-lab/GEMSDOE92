#!/usr/bin/env python3
"""Write, validate, gate and decide the FAULTNET GeoTIFFs; emit the run card.

Inputs (all produced by this lane, nothing hand-typed):
  evidence/faultnet_holdout.json      (scripts/run_faultnet.py holdout)
  .cache/faultnet/dots_<arm>.npy      (scripts/run_faultnet.py deploy)
  evidence/faultnet_uniqueness.json   (scripts/faultnet_uniqueness.py)
Outputs:
  docs/downloads/gemsdoe92-faultnet-<arm>-...-zeros.{tif,zip,json}
  evidence/faultnet_run_card.json (+ docs/downloads copy)
  docs/downloads/current_submission.json  (single source of truth for the site banner)

Decision rule (pre-registered, docs/HYPOTHESES_20261025_FAULTNET.md):
  promote <=> canaries <= 0.90  AND  format gates pass  AND  operative uniqueness
              AND HOLDOUT-DTI(arm) > HOLDOUT-DTI(COULOMBLOQO control on identical folds)
              AND paired 95% CI lower bound of the difference > 0.
At most ONE file (the best promoted arm) is marked OK TO SUBMIT.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import gates as G  # noqa: E402
from gems57 import grid as grid_mod, submission_writer  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
C = ROOT / ".cache" / "faultnet"
DL = ROOT / "docs" / "downloads"
EV = ROOT / "evidence"
ARMS = ("netctx", "netdens", "netfar")
DATE = "20261025"
CONTROL = "control_COULOMBLOQO"
HIST_BEST = dict(name="COULOMBLOQO standalone (historical run, evidence/coulomb_loqo_run_card.json lineage)",
                 dti=0.113316, evidence_class="HOLDOUT-DTI", evaluator_version="gems57-pooled-hide-v2")
NOTES = {
    "netctx": "FAULTNET netctx: physics+self-excluded catalogue-network context LOQO crest; 37654 dots 2.8px >2px off catalogue",
    "netdens": "FAULTNET netdens: physics+catalogue density/strike context LOQO crest; 37654 dots 2.8px >2px off catalogue",
    "netfar": "FAULTNET netfar: netctx surface, dots >4px off catalogue; 37654 dots 2.8px",
}


def write_audits(card: dict) -> None:
    """Per-arm *-audit.json in the schema scripts/check_site.py reads for the data-primary download.

    The uniqueness scan ran on dots_<arm>.npy; candidate_hash_matches_scan is True only when the served
    TIFF's positive pixels are pixel-identical to that array (checked here, not assumed)."""
    import rasterio
    for arm, a in card["arms"].items():
        tif = ROOT / a["file"]
        with rasterio.open(tif) as ds:
            pos = ds.read(1) > 0
        same = bool(np.array_equal(pos, np.load(C / f"dots_{arm}.npy")))
        u = a["uniqueness"]
        audit = dict(
            file=a["file"], sha256_zeros=a["sha256"], sha256_nan=None,
            gates_zeros=a["validator"]["gates"], gates_nan=[], overall_pass=bool(a["ok_to_download"]),
            generated_utc=card["generated_utc"], note=a["note"], n_positive_pixels=int(pos.sum()), n_dots=a["dots"],
            gates_zeros_pass=bool(a["validator"]["gates_ok"]), gates_nan_pass=None,
            submission_eligible=bool(a["ok_to_submit"]), verdict=a["verdict"], run_card="evidence/faultnet_run_card.json",
            public_registry_uniqueness=dict(
                evidence_file="evidence/faultnet_uniqueness.json", candidate_hash_matches_scan=same,
                candidate_sha256_zeros=a["sha256"], registries_checked=u["registry_rasters_checked"],
                unique_under_literal_rule=bool(u["unique_operative"]), stop_required=not u["unique_operative"],
                worst_forward_overlap=u["worst_overlap_final"]["value"], worst_overlap_raster=u["worst_overlap_final"]["raster"],
                worst_abs_spearman=u["worst_abs_rho_final"]["value"],
                scope="Public buffedlizard55-lab *GEMSDOE* default branches, unique Git blobs on the competition grid "
                      "(scripts/build_public_registry_index.py) plus local lineage rasters; rule per #IR-92-FAULTNET-DOT-DEFINITION."))
        (DL / a["file"].split("/")[-1].replace("-zeros.tif", "-audit.json")).write_text(json.dumps(audit, indent=1))


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("finalize_faultnet:main")

    if "--audit-only" in sys.argv:
        write_audits(json.loads((EV / "faultnet_run_card.json").read_text()))
        return 0
    hold = json.loads((EV / "faultnet_holdout.json").read_text())
    uniq = json.loads((EV / "faultnet_uniqueness.json").read_text())
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    sample = INPUTS / "bridge" / "sample_submission.tif"
    catalogue_path = INPUTS / "bridge" / "existing_faults.tif"
    canary_max = max(c["symmetric_auc"] for c in hold["canaries"])
    scores = hold["scores"]
    ctrl = scores[CONTROL]
    arms = {}
    for arm in ARMS:
        dots = np.load(C / f"dots_{arm}.npy")
        pred = np.where(dots & foot, 1.0, 0.0).astype(np.float32)
        tag = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-faultnet-{arm}-{int(dots.sum())}-{DATE}-{tag}-zeros"
        tif = DL / f"{stem}.tif"
        for ext in (".tif", ".zip", ".json"):
            tif.with_suffix(ext).unlink(missing_ok=True)
        receipt = submission_writer.write_submission(
            tif, pred, sample, foot, note=NOTES[arm], name=f"gemsdoe92-faultnet-{arm}-{DATE}-{tag}",
            catalogue=cat, metadata=dict(lane="FAULTNET", arm=arm))
        gr = G.run_gates(tif, sample, catalogue_path, prune_radius=2 if arm != "netfar" else None,
                         require_submission_encoding=True)
        gates_ok = all(g.ok for g in gr)
        d = hold["paired_by_candidate"][arm][CONTROL]
        s = scores[arm]
        u = uniq["results"][arm]
        # stricter: netfar must also beat the emission-matched control (added post-holdout, see addendum)
        controls = [CONTROL] + (["control_COULOMBLOQO_far"] if arm == "netfar" and "control_COULOMBLOQO_far" in scores else [])
        vs = {c: hold["paired_by_candidate"][arm][c] for c in controls}
        beats = bool(all(s["dti"] > scores[c]["dti"] and vs[c]["ci95"][0] > 0 for c in controls))
        promote = bool(canary_max <= 0.90 and gates_ok and receipt["validator"]["all_checks_passed"]
                       and u["unique_operative"] and beats)
        arms[arm] = dict(
            file=f"docs/downloads/{tif.name}", zip=f"docs/downloads/{tif.with_suffix('.zip').name}",
            receipt=f"docs/downloads/{tif.with_suffix('.json').name}",
            sha256=receipt["sha256"], zip_sha256=receipt["zip_sha256"], bytes=receipt["bytes"],
            submission_name=receipt["submission_name"], note=receipt["note"], note_chars=receipt["note_chars"],
            dots=int(dots.sum()), on_catalogue=int((dots & cat).sum()),
            holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
                             dti=round(s["dti"], 6), ci95=[round(x, 6) for x in s["ci95"]],
                             withheld_positives=s["withheld_positive_pixels"],
                             paired_vs_COULOMBLOQO_control=dict(delta=round(d["delta"], 6), ci95=[round(x, 6) for x in d["ci95"]]),
                             paired_vs_required_controls={c: dict(control_dti=round(scores[c]["dti"], 6), delta=round(v["delta"], 6),
                                                                  ci95=[round(x, 6) for x in v["ci95"]]) for c, v in vs.items()}),
            beats_holdout_best=beats,
            validator=dict(all_checks_passed=receipt["validator"]["all_checks_passed"],
                           checks=receipt["validator"]["checks"], min=receipt["validator"]["min"],
                           max=receipt["validator"]["max"], n_nan=receipt["validator"]["n_nan"],
                           gates=[dict(name=g.name, ok=g.ok, detail=g.detail) for g in gr], gates_ok=gates_ok),
            uniqueness=dict(unique_operative=u["unique_operative"], duplicates_operative=u["duplicates_operative"],
                            worst_overlap_final=u["worst_overlap_final"], worst_overlap_surface_topn=u["worst_overlap_surface_topn"],
                            worst_abs_rho_final=u["worst_abs_rho_final"], worst_abs_rho_surface=u["worst_abs_rho_surface"],
                            registry_rasters_checked=u["registry_rasters_checked"], literal_reading=u["literal_reading"]),
            promote_candidate=promote)
    promoted = [a for a in ARMS if arms[a]["promote_candidate"]]
    best = max(promoted, key=lambda a: arms[a]["holdout_dti"]["dti"]) if promoted else None
    best_any = max(ARMS, key=lambda a: arms[a]["holdout_dti"]["dti"])
    for a in ARMS:
        arms[a]["verdict"] = "promote" if a == best else "negative"
        arms[a]["ok_to_download"] = arms[a]["validator"]["all_checks_passed"] and arms[a]["validator"]["gates_ok"]
        arms[a]["ok_to_submit"] = a == best
    primary = best or best_any
    P = arms[primary]
    card = dict(
        schema="gemsdoe92-faultnet-run-card-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        lane="FAULTNET",
        hypothesis="Unmapped faults cluster around mapped ones (splays, antithetic, step-over/relay faults sharing the local strike); "
                   "self-excluded catalogue-network context added to the COULOMBLOQO physics stack ranks hidden faults better.",
        mechanism="Fault-population clustering and damage-zone self-similarity: 1 km/4 km fault density, distance to other faults and "
                  "their tips, regional-strike alignment of topographic edges; each field excludes the pixel's own catalogue component.",
        named_non_fault_mimic="Lithological contacts and range-front geomorphology running parallel to mapped faults (bedding, lava-flow margins, Lahontan shorelines).",
        holdout=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"], instrument=hold["instrument"],
                     seeds=hold["seeds"], scores={k: dict(dti=round(v["dti"], 6), ci95=[round(x, 6) for x in v["ci95"]],
                                                          withheld_positives=v["withheld_positive_pixels"]) for k, v in scores.items()},
                     historical_holdout_best=HIST_BEST),
        leakage_canary=dict(max_symmetric_auc=canary_max, threshold=0.90, pass_=canary_max <= 0.90, n=len(hold["canaries"])),
        arms=arms,
        primary_arm=primary,
        raster_sha256=P["sha256"],
        correlation_overlap_vs_registry=P["uniqueness"],
        validator_output=dict(no_nan_inside_footprint=P["validator"]["checks"].get("in_footprint_all_finite"),
                              values_in_0_1=P["validator"]["checks"].get("range_0_1_guaranteed"),
                              crs_shape_transform_match=all(P["validator"]["checks"].get(k) for k in
                                                            ("crs_epsg_32611", "dimensions_3730x3292", "transform_matches_sample_submission"))),
        submission_name=P["submission_name"], note=P["note"],
        verdict=P["verdict"], ok_to_download=P["ok_to_download"], ok_to_submit=P["ok_to_submit"],
        experiments_used=3, weekly_slots_used=0, organizer_confirmed_score=None,
        uniqueness_reading="#IR-92-FAULTNET-DOT-DEFINITION (dot fields literal; continuous surfaces matched-budget top-n + rank-correlation; literal reading published alongside)",
    )
    (EV / "faultnet_run_card.json").write_text(json.dumps(card, indent=1))
    shutil.copy2(EV / "faultnet_run_card.json", DL / "faultnet_run_card.json")
    shutil.copy2(EV / "faultnet_uniqueness.json", DL / "faultnet_uniqueness.json")
    shutil.copy2(EV / "faultnet_holdout.json", DL / "faultnet_holdout.json")
    current = dict(schema="gemsdoe92-current-submission-v1", generated_utc=card["generated_utc"], lane="FAULTNET",
                   arm=primary, ok_to_download=P["ok_to_download"], ok_to_submit=P["ok_to_submit"], verdict=P["verdict"],
                   file=P["file"], zip=P["zip"], sha256=P["sha256"], zip_sha256=P["zip_sha256"],
                   submission_name=P["submission_name"], note=P["note"], holdout_dti=P["holdout_dti"],
                   control=dict(name=CONTROL, dti=round(ctrl["dti"], 6), ci95=[round(x, 6) for x in ctrl["ci95"]]),
                   uniqueness=P["uniqueness"], run_card="docs/downloads/faultnet_run_card.json",
                   siblings={a: dict(file=arms[a]["file"], verdict=arms[a]["verdict"], dti=arms[a]["holdout_dti"]["dti"])
                             for a in ARMS if a != primary})
    (DL / "current_submission.json").write_text(json.dumps(current, indent=1))
    write_audits(card)
    for a in ARMS:
        x = arms[a]
        print(a, x["verdict"], "DTI", x["holdout_dti"]["dti"], x["holdout_dti"]["ci95"], "Δctrl", x["holdout_dti"]["paired_vs_COULOMBLOQO_control"],
              "unique", x["uniqueness"]["unique_operative"], "gates", x["validator"]["gates_ok"], x["file"])
    print("PRIMARY", primary, "OK_TO_SUBMIT", P["ok_to_submit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
