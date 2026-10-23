from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gems57 import metric

ROOT = Path(__file__).resolve().parents[1]


def test_exact_metric_matches_literal_bruteforce_with_overlapping_dots() -> None:
    truth = np.zeros((11, 13), dtype=bool)
    truth[4, 4] = True
    truth[4, 5] = True
    truth[8, 10] = True
    pred = np.zeros(truth.shape, dtype=np.float64)
    pred[4, 3] = 1.0
    pred[4, 6] = 0.7
    pred[8, 9] = 0.4
    pred[1, 1] = 0.25

    exact = metric.dti_exact(pred, truth)
    brute = metric.dti_bruteforce(pred, truth)
    assert np.isclose(exact["tp"], brute["tp"], atol=1e-12)
    assert np.isclose(exact["fp"], brute["fp"], atol=1e-12)
    assert np.isclose(exact["fn"], brute["fn"], atol=1e-12)
    assert np.isclose(exact["dti"], brute["dti"], atol=1e-12)


def test_manifest_is_sha256_pinned_and_candidate_tiffs_are_not_gitwhitelisted() -> None:
    doc = json.loads((ROOT / "registry" / "session_manifest.json").read_text())
    assert len(doc["files"]) == 12
    assert all(len(item["sha256"]) == 64 and item["bytes"] > 0 for item in doc["files"])
    ignore = (ROOT / ".gitignore").read_text()
    assert "*.tif" in ignore
    assert "!releases/" not in ignore


def test_only_three_prune_values_reserved_and_claims_are_not_receipts() -> None:
    rows = (ROOT / "ledger" / "submissions.csv").read_text().splitlines()
    assert any(",PRUNE,p2.5px-refill," in row for row in rows)
    assert any(",PRUNE,p3.5px-refill," in row for row in rows)
    assert any(",PRUNE,p4.5px-refill," in row for row in rows)
    assert all(",BUILT," in row or ",HISTORICAL_CLAIM," in row or row.startswith("id,") for row in rows)
    receipt = json.loads((ROOT / "evidence" / "prune_rungs.json").read_text())
    assert receipt["parent_claim"]["evidence_label"] == "CLAIM"
    assert receipt["parent_claim"]["receipt"] is False
