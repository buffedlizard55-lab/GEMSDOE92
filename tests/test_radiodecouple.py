"""Unit and integration tests for the RADIODECOUPLE lane."""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
BRIDGE = ROOT / "data" / "bridge"
INPUTS = ROOT / ".cache" / "gems_inputs"

from gems.gates import run_gates, summarise
from gems57.validate import validate, assert_submittable


def test_radiodecouple_artifacts_exist():
    """Verify all 3 pre-registered RADIODECOUPLE arms exist on disk."""
    for arm in ("standalone", "demag", "dual35"):
        tif = DOWNLOADS / f"gemsdoe92-radiodecouple-{arm}-37654-20261025-zeros.tif"
        audit = DOWNLOADS / f"gemsdoe92-radiodecouple-{arm}-37654-20261025-audit.json"
        assert tif.is_file(), f"Missing TIFF for {arm}: {tif}"
        assert audit.is_file(), f"Missing audit for {arm}: {audit}"


def test_radiodecouple_standalone_format_gates():
    """Test format and range gates on the primary standalone artifact."""
    tif = DOWNLOADS / "gemsdoe92-radiodecouple-standalone-37654-20261025-zeros.tif"
    ref = BRIDGE / "sample_submission.tif"
    cat = BRIDGE / "existing_faults.tif"

    with rasterio.open(ref) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(cat) as ds:
        cat_mask = ds.read(1) > 0

    with rasterio.open(tif) as ds:
        data = ds.read(1)
        assert ds.count == 1
        assert ds.dtypes[0] == "float32"
        assert ds.shape == (3730, 3292)
        assert np.isfinite(data).all()
        assert data.min() >= 0.0
        assert data.max() <= 1.0
        assert int((data > 0).sum()) == 37654
        assert not np.any((data > 0) & ~foot)
        assert not np.any(data[cat_mask] > 0)

    v = validate(tif, foot, cat_mask)
    assert_submittable(v)

    res = run_gates(str(tif), str(ref), str(cat), prune_radius=2, require_submission_encoding=True)
    ok, report = summarise(res)
    assert ok, f"Gates failed:\n{report}"


def test_radiodecouple_run_card():
    """Verify that the RADIODECOUPLE run card is complete, valid, and has negative verdict."""
    card_path = EVIDENCE / "gemsdoe92-radiodecouple-20261025T160000Z_run_card.json"
    assert card_path.is_file()

    doc = json.loads(card_path.read_text(encoding="utf-8"))
    assert doc["schema"] == "gemsdoe92-run-card.v3"
    assert doc["lane"] == "RADIODECOUPLE"
    assert doc["verdict"] == "negative"
    assert doc["submission_eligible"] is False
    assert doc["experiments_used"] == "3/3"
    assert doc["weekly_slots_used"] == 0

    holdout = doc["holdout_dti"]
    assert holdout["withheld_positives"] == 22663
    assert holdout["scores"]["standalone"]["dti"] > holdout["scores"]["R0"]["dti"]
    assert doc["leakage_canaries"]["all_pass_le_0p90"] is True

    audit_path = DOWNLOADS / "gemsdoe92-radiodecouple-standalone-37654-20261025-audit.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["overall_pass"] is True
    assert audit["submission_eligible"] is False
    assert audit["verdict"] == "negative"
