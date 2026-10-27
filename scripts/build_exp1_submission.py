#!/usr/bin/env python3
"""Write, validate and document the EXP1 candidate (shared writer + gates + run card).

Usage: python scripts/build_exp1_submission.py .cache/exp1/hybrid/final_sel.npy

Steps (all automatic, fail-closed):
 1. build a float32 0/1 grid (zeros outside the footprint, zero on mapped faults);
 2. write TIFF + one-TIFF ZIP + receipt with vendor/gems57/submission_writer.py;
 3. re-read from disk: gems.gates (submission encoding) + gems57.validate;
 4. PI-1 registry audit of the written bytes (all 2,060 public rasters) and of
    the placement surface (pre-placement check);
 5. collect MODEL estimate, spatial holdout, canaries and instrument-validity
    evidence; write the protocol run card (rule 5) and a per-file audit.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
from gems import lbm_place as P  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import submission_writer  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOWNLOADS = ROOT / "docs" / "downloads"
EVID = ROOT / "evidence"
DATE = "20261027"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    sel_path = Path(sys.argv[1])
    fp = L.footprint(); cat = L.catalogue(); H, W = L.SHAPE
    sel = np.load(sel_path)
    pred = np.zeros(H * W, np.float32); pred[sel] = 1.0; pred = pred.reshape(H, W)
    if (pred[cat] > 0).any() or (pred[~fp.mask] > 0).any():
        raise SystemExit("candidate has dots on the catalogue or outside the footprint")
    n = int(pred.sum())
    tag = hashlib.sha1(np.sort(sel).astype(np.int64).tobytes()).hexdigest()[:8]
    stem = f"gemsdoe92-lbmc1-{n}dots-{DATE}-{tag}"
    tif = DOWNLOADS / f"{stem}-zeros.tif"
    name = f"gemsdoe92-lbmc1-{n}d-{tag}"
    note = (f"LBM-consensus v1: {n} dots by exact expected-DTI greedy on a truth density fit to 123 scored "
            f"rasters; 70%/3px registry caps.")
    if len(note) > 140:
        note = f"LBM-consensus v1: {n} dots, expected-DTI greedy on 123-score-fit density; 70%/3px registry caps."
    assert len(note) <= 140, len(note)
    receipt = None
    if not tif.exists():
        receipt = submission_writer.write_submission(
            tif, pred, L.SAMPLE, fp.mask, note=note, name=name, catalogue=cat,
            metadata=dict(lane="EXP1-LBM-consensus", session="ee2370c1", selection=str(sel_path)))
    file_sha = sha256(tif)
    # 3. re-read gates
    gates = run_gates(str(tif), str(L.SAMPLE), str(L.CATALOGUE), prune_radius=2, require_submission_encoding=True)
    ok, report = summarise(gates)
    v = validate(tif, fp.mask, cat)
    assert_submittable(v)
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        grid_ok = dict(crs=str(ds.crs), shape=list(ds.shape), transform=list(tuple(ds.transform)[:6]),
                       dtype=ds.dtypes[0], count=ds.count)
    with rasterio.open(L.SAMPLE) as ds:
        ref = dict(crs=str(ds.crs), shape=list(ds.shape), transform=list(tuple(ds.transform)[:6]))
    validator_output = dict(
        no_nan_in_footprint=bool(np.isfinite(a[fp.mask]).all()),
        no_nan_anywhere=bool(np.isfinite(a).all()),
        values_in_0_1=bool(a.min() >= 0 and a.max() <= 1),
        crs_match=grid_ok["crs"] == ref["crs"], shape_match=grid_ok["shape"] == ref["shape"],
        transform_match=grid_ok["transform"] == ref["transform"],
        dtype_float32=grid_ok["dtype"] == "float32", single_band=grid_ok["count"] == 1,
        zeros_outside_footprint=bool((a[~fp.mask] == 0).all()),
        zero_mass_on_mapped_catalogue=bool((a[cat] == 0).all()),
        n_positive=int((a > 0).sum()), gates_pass=bool(ok), gems57_validate_pass=True,
        gates=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates])
    # 4. uniqueness: final dots (from disk) + surface
    hs = U.load_halo_stats(); shas = sorted(hs)
    aud_final = U.audit(a > 0, fp=fp, shas=shas, halo_stats=hs)
    maps = np.load(ROOT / ".cache" / "lbm" / "lbm_ens_maps.npz")
    surface = P.isolated_value(maps["rho_full"].astype(np.float64))[fp.lin]
    aud_surf = U.audit(None, our_surface=surface, fp=fp, shas=shas, halo_stats=hs, n_dots_for_surface=n)
    slim = lambda d: {k: v for k, v in d.items() if k != "rows"}
    (EVID / f"{stem}_uniqueness.json").write_text(json.dumps(dict(final=aud_final, surface=slim(aud_surf)), indent=1))
    # 5. MODEL estimate
    est_path = EVID / f"{stem}_lbm_estimate.json"
    if not est_path.exists():
        subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "scripts" / "lbm_estimate.py"), str(sel_path),
                        "--boot", "200", "--out", str(est_path)], check=True)
    est = json.loads(est_path.read_text())
    cand_key = [k for k in est["candidates"] if k != "R0_reference"][0]
    ce = est["candidates"][cand_key]; r0e = est["candidates"]["R0_reference"]
    hold = json.loads((EVID / "exp1_holdout.json").read_text())
    can = json.loads((EVID / "exp1_canaries.json").read_text())
    val = json.loads((EVID / "holdout_validity_20261027.json").read_text())
    model = json.loads((EVID / "lbm_v1_model.json").read_text())
    place = json.loads((EVID / "exp1_placement.json").read_text())
    hs_ = hold["summary"]["scores"]
    # PI-1b: a surface has no dots, so the binding pre-placement check is rank correlation;
    # the surface's top-N overlap is reported as a diagnostic.
    surface_rho_ok = abs(aud_surf["worst_abs_rho"]["rho"]) <= U.RHO_LIMIT
    unique = (not aud_final["duplicate"]) and surface_rho_ok
    beats = ce["bootstrap"]["q05"] > 0.2778 and ce["bootstrap"]["delta_vs_R0"]["q05"] > 0
    robust = all(ce["estimates"][k] >= r0e["estimates"][k] - 1e-4 for k in ce["estimates"])
    fmt = all(v2 for k2, v2 in validator_output.items() if isinstance(v2, bool))
    promote = bool(unique and beats and robust and fmt and not can["leakage_flag"])
    card = dict(
        schema="gemsdoe92-run-card-v3", created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        lane="EXP1 — LB-calibrated multi-detector convergence (H1)", experiment="1 of 3 (budget)",
        density_model="ensemble: mean of rho(G-set CLAIM>=0.18) and rho(G-set CLAIM>=0.15) (evidence/lbm_ensemble_model.json)",
        hypothesis=("Independent fault detectors converge on real new faults; the organizer's new faults lie mostly "
                    ">1.5 km from mapped traces and ~1 px off the H19-5 skeleton (fitted from 123 CLAIM scores)."),
        mechanism=("Exact lazy-greedy maximisation of expected DTI under a truth density rho fitted to the official "
                   "metric (E[TP]=sum rho*C), with the 70%/3px registry rule enforced as caps during placement."),
        named_non_fault_mimic="Lake Lahontan paleoshorelines (topographic) and lithologic contacts (magnetic/gravity edges)",
        raster=dict(file=f"docs/downloads/{tif.name}", zip=f"docs/downloads/{tif.with_suffix('.zip').name}",
                    sha256=file_sha, bytes=tif.stat().st_size, n_dots=n),
        raster_sha256=file_sha,
        submission_name=name, note=note, note_chars=len(note),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["summary"]["evaluator_version"],
                         withheld_positive_pixels=hs_["exp1_lbm"]["withheld_positive_pixels"],
                         exp1=dict(dti=hs_["exp1_lbm"]["dti"], ci95=hs_["exp1_lbm"]["ci95"]),
                         r0_recipe_control=dict(dti=hs_["r0_recipe"]["dti"], ci95=hs_["r0_recipe"]["ci95"]),
                         paired_delta_vs_r0_recipe=hold["summary"]["paired_differences"]["r0_recipe"],
                         instrument_validity=dict(spearman_holdout_vs_claim=val["spearman_holdout_vs_claim"],
                                                  spearman_lbm_vs_claim=val["spearman_lbm_logo_vs_claim"], n=val["n"]),
                         interpretation=("Catalogue hide-and-recover does not predict leaderboard CLAIMs "
                                         f"(Spearman {val['spearman_holdout_vs_claim']:.2f} over {val['n']} rasters; "
                                         "R0 itself scores 0.004 on it). It is reported, not used as the promotion gate.")),
        model_estimate=dict(evidence_class="MODEL (not an organizer score)", point=ce["estimates"],
                            bootstrap=ce["bootstrap"], r0_same_model=dict(point=r0e["estimates"], bootstrap=r0e["bootstrap"]),
                            validation=model["validation"]),
        leakage_canaries=dict(threshold=0.90, pooled_auc=can["pooled_auc"], max_auc=can["max_auc"],
                              leakage_flag=can["leakage_flag"]),
        uniqueness=dict(interpretation="PI-1 (see gems/uniqueness_v3.py)", registry_rasters=aud_final["registry_rasters"],
                        final_worst_overlap=aud_final["worst_overlap_pi1"]["overlap_pi1"],
                        final_worst_overlap_sha256=aud_final["worst_overlap_pi1"]["sha256"],
                        final_worst_abs_rho=abs(aud_final["worst_abs_rho"]["rho"]),
                        surface_worst_overlap=aud_surf["worst_overlap_pi1"]["overlap_pi1"],
                        surface_worst_abs_rho=abs(aud_surf["worst_abs_rho"]["rho"]),
                        surface_rule=("PI-1b: binding surface check = |rank correlation| <= 0.90 (a surface has no dots); "
                                      "top-N overlap of the unconstrained surface is a diagnostic only"),
                        duplicate=bool(not unique),
                        literal_reading=dict(worst=aud_final["literal_reading"]["worst"]["overlap_literal"],
                                             duplicate_under_literal=aud_final["literal_reading"]["duplicate_under_literal"],
                                             note=aud_final["literal_reading"]["note"])),
        validator_output=validator_output,
        placement=dict(rounds=place.get("rounds"), method=place.get("method")),
        gates_passed=dict(format=fmt, uniqueness_pi1=unique, model_beats_0_2778_at_q05=beats,
                          model_robust_all_specs_ge_R0=robust,
                          no_leakage=not can["leakage_flag"], catalogue_holdout_beats_r0_recipe=bool(
                              hold["summary"]["paired_differences"]["r0_recipe"]["ci95"][0] > 0)),
        verdict="promote" if promote else "negative",
        submission_eligible=promote,
        slot_note="Weekly cap is 3 submissions/week (competition website prevails). Selection of the final pick is a separate human step.",
    )
    card_path = EVID / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=1, default=float), encoding="utf-8")
    (DOWNLOADS / f"{stem}_run_card.json").write_text(json.dumps(card, indent=1, default=float), encoding="utf-8")
    audit = dict(file=f"docs/downloads/{tif.name}", sha256_zeros=file_sha, overall_pass=fmt,
                 n_positive_pixels=n, gates_zeros=[dict(name=g.name, ok=bool(g.ok)) for g in gates],
                 validator_output={k: v2 for k, v2 in validator_output.items() if isinstance(v2, bool)},
                 verdict=card["verdict"], submission_eligible=promote,
                 run_card=f"evidence/{card_path.name}", uniqueness=card["uniqueness"])
    (DOWNLOADS / f"{stem}-zeros-audit.json").write_text(json.dumps(audit, indent=1), encoding="utf-8")
    print(json.dumps(dict(file=str(tif), sha256=file_sha, n=n, name=name, note=note, verdict=card["verdict"],
                          gates=card["gates_passed"], model=ce["estimates"], boot=ce["bootstrap"]), indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
