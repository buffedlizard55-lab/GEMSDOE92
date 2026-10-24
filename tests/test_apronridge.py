"""Unit and policy-integration tests for the APRONRIDGE lane (session 2026-10-24).

1. Synthetic physics & algorithmic tests (self-contained; no .cache/ inputs required in CI).
2. On-disk GeoTIFF, single-TIFF ZIP, 10/10 format gate, holdout receipt, canary,
   uniqueness, and fail-closed public-witness invariants.
"""
from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from gems.apronridge import apron_habitat, directional_ridge_1d, lane_surface, rtp_curvature_ridge
from gems.gates import run_gates

ROOT = Path(__file__).resolve().parents[1]
PRIMARY_TIF = ROOT / "docs/downloads" / "h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif"
PRIMARY_ZIP = ROOT / "docs/downloads" / "h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.zip"
PRIMARY_AUDIT = ROOT / "docs/downloads" / "h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-audit.json"
SAMPLE_SUB = ROOT / "data/bridge/sample_submission.tif"
EXISTING_FAULTS = ROOT / "data/bridge/existing_faults.tif"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# 1. Synthetic physics & algorithmic tests
# --------------------------------------------------------------------------
def test_apron_habitat_selects_thin_cover_piedmont_over_playa_and_peak():
    yy, xx = np.mgrid[0:60, 0:60]
    valid = np.ones((60, 60), dtype=bool)
    # Left third: deep central playa (z=-400 m, depth=2500 m)
    # Middle third: thin-cover piedmont apron (z=-50 m, depth=180 m)
    # Right third: high granite range core (z=+600 m, depth=1.5 m)
    det_elev = np.where(xx < 20, -400.0, np.where(xx < 40, -50.0, 600.0)).astype(np.float32)
    depth = np.where(xx < 20, 2500.0, np.where(xx < 40, 180.0, 1.5)).astype(np.float32)
    grav_slope = np.linspace(0.05, 0.25, 3600, dtype=np.float32).reshape(60, 60)

    out = apron_habitat(det_elev, depth, grav_slope, valid)
    h = out["H_apron"]
    assert h.dtype == np.float32
    assert np.all((h >= 0.0) & (h <= 1.0))
    playa_mean = float(h[:, :20].mean())
    piedmont_mean = float(h[:, 20:40].mean())
    peak_mean = float(h[:, 40:].mean())
    assert piedmont_mean > 5.0 * playa_mean
    assert piedmont_mean > 5.0 * peak_mean


def test_rtp_curvature_ridge_detects_buried_magnetic_step_with_flat_dem():
    yy, xx = np.mgrid[0:64, 0:64]
    valid = np.ones((64, 64), dtype=bool)
    # Completely flat alluvial surface (zero DEM relief/slope) over a buried vertical RTP step
    det_elev = np.full((64, 64), -50.0, dtype=np.float32)
    det_slope = np.zeros((64, 64), dtype=np.float32)
    depth = np.full((64, 64), 180.0, dtype=np.float32)
    grav_slope = np.exp(-0.5 * ((xx - 32.0) / 4.0) ** 2).astype(np.float32)
    rtp = (100.0 / (1.0 + np.exp(-(xx - 32.0) / 1.5))).astype(np.float32)
    # Negative total curvature trough along the buried contact
    tc = (-2.0 * np.exp(-0.5 * ((xx - 32.0) / 2.0) ** 2)).astype(np.float32)

    r_rtp_out = rtp_curvature_ridge(rtp, tc, valid)
    assert r_rtp_out["R_rtp"][:, 30:35].mean() > 3.0 * r_rtp_out["R_rtp"][:, :15].mean()

    full = lane_surface(det_elev, det_slope, depth, grav_slope, rtp, tc, valid)
    assert full["S_raw"].dtype == np.float32
    assert full["S_raw"][:, 30:35].mean() > 3.0 * full["S_raw"][:, :15].mean()
    # Confirm directional 1D crest activates along x=32
    assert int(full["ridge_1d"][:, 31:34].sum()) > 30


def test_directional_ridge_1d_suppresses_interior_of_smooth_2d_dome():
    yy, xx = np.mgrid[0:41, 0:41]
    # A flat plateau has zero strict/tie-free 1D directional crests except at 1 point;
    # a narrow N-S ridge at x=20 produces a 1-px crest spine along all 41 rows.
    ridge = np.exp(-0.5 * ((xx - 20.0) / 2.0) ** 2).astype(np.float32)
    valid = np.ones_like(ridge, dtype=bool)
    mask = directional_ridge_1d(ridge, valid)
    assert np.all(mask[5:36, 20])
    assert not np.any(mask[5:36, 17])
    assert not np.any(mask[5:36, 23])


# --------------------------------------------------------------------------
# 2. On-disk deliverables, gates, receipts, and protocol invariants
# --------------------------------------------------------------------------
def test_apronridge_primary_deliverables_and_10_of_10_gates():
    assert PRIMARY_TIF.is_file()
    assert PRIMARY_ZIP.is_file()
    assert PRIMARY_AUDIT.is_file()

    audit = json.loads(PRIMARY_AUDIT.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    assert audit["gates_zeros_pass"] is True
    assert audit["gates_nan_pass"] is True
    assert audit["n_dots"] == 37654
    assert audit["sha256_zeros"] == _sha256(PRIMARY_TIF)

    # Fail-closed public dense witness enforcement
    assert audit["submission_eligible"] is False
    assert audit["public_registry_uniqueness"]["unique_under_literal_rule"] is False
    assert audit["public_registry_uniqueness"]["stop_required"] is True

    # Re-run live 10/10 format gates on disk
    gates = run_gates(str(PRIMARY_TIF), str(SAMPLE_SUB), str(EXISTING_FAULTS), prune_radius=2)
    assert len(gates) == 10
    assert all(g.ok for g in gates), [g for g in gates if not g.ok]

    # Single-TIFF ZIP archive check
    with zipfile.ZipFile(PRIMARY_ZIP) as zf:
        names = zf.namelist()
        assert names == [PRIMARY_TIF.name]
        assert hashlib.sha256(zf.read(PRIMARY_TIF.name)).hexdigest() == audit["sha256_zeros"]

    with rasterio.open(PRIMARY_TIF) as ds:
        arr = ds.read(1)
        assert ds.dtypes == ("float32",)
        assert ds.count == 1
        assert ds.nodata is None
        assert int((arr > 0).sum()) == 37654
        assert float(np.nanmin(arr)) >= 0.0 and float(np.nanmax(arr)) <= 1.0


def test_apronridge_ablation_holdout_uniqueness_and_ledger_policy():
    vdoc = json.loads((ROOT / "evidence/apronridge_variants.json").read_text(encoding="utf-8"))
    adoc = json.loads((ROOT / "evidence/apronridge_proxy_audit.json").read_text(encoding="utf-8"))
    rcard = json.loads((ROOT / "evidence/apronridge_run_card.json").read_text(encoding="utf-8"))
    wdoc = json.loads((ROOT / "evidence/public_witness_apronridge.json").read_text(encoding="utf-8"))

    # Hard 3-experiment budget
    assert len(vdoc["variants"]) == 3
    assert rcard["experiments_used"] == 3
    assert [v["value"] for v in vdoc["variants"]] == ["s60f40", "s50f50", "free1d"]
    for v in vdoc["variants"]:
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert len(v["form_note"]) <= 140
        p = ROOT / v["file_zeros"]
        assert p.is_file()
        assert _sha256(p) == v["sha256_zeros"]

    # Leakage canaries all <= 0.90
    assert adoc["leakage_canaries"]["stop_and_investigate_if_any_gt_0_90"] is False
    assert adoc["leakage_canaries"]["max_symmetric_auc"] <= 0.90

    # Local registry uniqueness on both pre-placement surface and all 3 final dot rasters
    assert adoc["pre_placement_surface_registry"]["duplicate"] is False
    assert adoc["pre_placement_surface_registry"]["worst_abs_spearman"] <= 0.90
    assert adoc["pre_placement_surface_registry"]["worst_top37654_forward_overlap"] <= 0.70
    for arm in ("s60f40", "s50f50", "free1d"):
        u = adoc["local_registry_uniqueness"][arm]
        assert u["local_duplicate"] is False
        assert u["worst_forward_overlap"] <= 0.70
        assert u["worst_abs_spearman_phi"] <= 0.90

    # Holdout result: free1d beats R0, STRAINBREAK f60s2i, and RELIEF p10piedmont
    scores = adoc["hide_and_recover_pooled_summary"]["scores"]
    assert adoc["selected_arm"] == "free1d"
    assert scores["free1d"]["evidence_class"] == "HOLDOUT-DTI"
    assert scores["free1d"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert scores["free1d"]["withheld_positive_pixels"] == 22663
    assert scores["free1d"]["dti"] > scores["RELIEF_p10piedmont"]["dti"] > scores["STRAINBREAK_f60s2i"]["dti"] > scores["R0"]["dti"]
    assert rcard["holdout_dti"]["paired_vs_R0"]["ci95"][0] > 0.0

    # Honest fail-closed verdict under binding public witness
    assert wdoc["candidate"]["sha256"] == rcard["raster_sha256"]
    assert wdoc["stop_required_vs_this_witness"] is True
    assert rcard["verdict"] == "negative"
    assert rcard["submission_eligible"] is False
    assert len(rcard["note"]) <= 140

    # Ledger & mechanism cards synchronized
    with (ROOT / "ledger/submissions.csv").open(encoding="utf-8") as f:
        rows = {r["id"]: r for r in csv.DictReader(f)}
    cards = json.loads((ROOT / "ledger/mechanism_cards.json").read_text(encoding="utf-8"))
    for v in vdoc["variants"]:
        assert v["id"] in rows
        assert rows[v["id"]]["status"] == "BUILT"
        assert v["id"] in cards


def test_validate_submission_cli_honors_candidate_and_fails_closed():
    import subprocess
    import sys

    script = str(ROOT / "scripts/validate_submission.py")
    ok_proc = subprocess.run(
        [sys.executable, script, "--candidate", str(PRIMARY_TIF)],
        capture_output=True,
        text=True,
    )
    assert ok_proc.returncode == 0
    assert PRIMARY_TIF.name in ok_proc.stdout

    bad_proc = subprocess.run(
        [sys.executable, script, "--candidate", str(ROOT / "docs/downloads/does_not_exist.tif")],
        capture_output=True,
        text=True,
    )
    assert bad_proc.returncode != 0

