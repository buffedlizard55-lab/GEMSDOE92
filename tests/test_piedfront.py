"""Unit and evidence-contract tests for the PIEDFRONT lane (2026-10-24)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

from gems.piedfront import piedfront_surface, relative_slope_break

ROOT = Path(__file__).resolve().parents[1]


def _synthetic_fields(shape=(64, 72), seed=19):
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:shape[0], 0:shape[1]]
    det_elev = (np.linspace(-60.0, 90.0, shape[1])[None, :] + rng.normal(0, 1.5, shape)).astype(np.float32)
    det_slope = (np.abs(np.sin(x / 7.0)) * 8.0 + 1.0).astype(np.float32)
    grav_slope = (np.cos(y / 9.0) * 0.5 + 1.0).astype(np.float32)
    depth_base = (np.linspace(50.0, 1200.0, shape[0])[:, None] + rng.normal(0, 5.0, shape)).astype(np.float32)
    return det_elev, det_slope, grav_slope, depth_base


def test_piedfront_surface_keys_shapes_and_ranges():
    det_elev, det_slope, grav_slope, depth_base = _synthetic_fields()
    valid = np.ones(det_elev.shape, dtype=bool)
    valid[:4, :] = False
    valid[:, -3:] = False

    out = piedfront_surface(det_elev, det_slope, grav_slope, depth_base, valid)
    expected_keys = {
        "rel_break_pct",
        "coherence",
        "R_scarp",
        "elev_pct",
        "depth_pct",
        "grav_pct",
        "W_pied",
        "S_raw",
        "S_pct",
        "valid",
    }
    assert set(out) == expected_keys
    assert np.array_equal(out["valid"], valid)
    for k in expected_keys - {"valid"}:
        arr = out[k]
        assert arr.shape == det_elev.shape and arr.dtype == np.float32, k
        assert np.isfinite(arr).all(), k
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0, k
    for k in ("rel_break_pct", "R_scarp", "elev_pct", "depth_pct", "grav_pct", "W_pied", "S_raw", "S_pct"):
        assert np.all(out[k][~valid] == 0.0), k

    assert np.allclose(out["S_raw"][valid], (out["R_scarp"] * out["W_pied"])[valid], atol=1e-6)


def test_relative_scarp_break_favors_piedmont_over_steep_range():
    # Identical slope-break magnitude ||grad(slope)|| = 2.0 deg/px on gentle piedmont (2 deg)
    # vs steep mountain crag (28 deg): relative break must be strictly larger on the piedmont.
    slope = np.zeros((20, 40), dtype=np.float32)
    # Left half: gentle piedmont with a 2-deg step at col 10
    slope[:, :10] = 1.0
    slope[:, 10:20] = 3.0
    # Right half: steep range interior with the same 2-deg step at col 30
    slope[:, 20:30] = 27.0
    slope[:, 30:] = 29.0
    rel = relative_slope_break(slope, valid=np.ones_like(slope, dtype=bool))
    assert float(rel[10, 10]) > float(rel[10, 30]) * 4.0


def test_piedfront_evidence_and_primary_artefact_contract():
    variants = json.loads((ROOT / "evidence/piedfront_variants.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "evidence/piedfront_proxy_audit.json").read_text(encoding="utf-8"))
    card = json.loads((ROOT / "evidence/piedfront_run_card.json").read_text(encoding="utf-8"))
    dl_audit = json.loads(
        (ROOT / "docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-audit.json").read_text(
            encoding="utf-8"
        )
    )

    assert len(variants["variants"]) == 3
    by_val = {v["value"]: v for v in variants["variants"]}
    assert set(by_val) == {"f35Ptop", "f40Ptop", "f45Ptop"}

    f35 = by_val["f35Ptop"]
    tif_path = ROOT / "docs/downloads" / f"{f35['id']}-zeros.tif"
    zip_path = ROOT / "docs/downloads" / f"{f35['id']}-zeros.zip"
    assert tif_path.is_file()
    assert zip_path.is_file()
    sha_disk = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    assert sha_disk == f35["sha256_zeros"] == card["raster_sha256"] == dl_audit["sha256_zeros"]
    import zipfile
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert zf.namelist() == [tif_path.name]
        assert hashlib.sha256(zf.read(tif_path.name)).hexdigest() == sha_disk

    # Holdout DTI beats both R0 and RELIEF p10 in point estimate
    dti_f35 = card["holdout_dti"]["dti"]
    dti_r0 = card["holdout_dti"]["R0_dti"]
    dti_relief = card["holdout_dti"]["RELIEFp10_dti"]
    assert dti_f35 > dti_relief > dti_r0
    assert card["holdout_dti"]["delta_vs_R0_ci95"][0] > 0.0
    assert card["holdout_dti"]["delta_vs_BREAKLINEf45_ci95"][0] > 0.0

    # Leakage canary and local uniqueness gates pass
    assert card["leakage_canary_max_symmetric_auc"] <= 0.90
    loc = card["correlation_overlap_vs_registry"]["local"]
    assert loc["worst_forward_overlap_within_3px"] <= 0.70
    assert loc["worst_abs_spearman"] <= 0.90
    assert loc["literal_duplicate"] is False
    assert loc["preplacement_surface"]["worst_forward_overlap"] <= 0.70
    assert loc["preplacement_surface"]["worst_abs_spearman"] <= 0.90
    assert loc["preplacement_surface"]["duplicate"] is False

    # Submission note and verdict contract
    assert 0 < card["note_chars"] <= 140
    assert len(card["note"]) == card["note_chars"]
    assert card["verdict"] == "negative"
    assert dl_audit["format_pass"] is True
    assert dl_audit["submission_eligible"] is False
    assert audit["best_candidate"] == "f35Ptop"
