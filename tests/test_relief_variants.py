"""Unit and policy tests for RELIEF variants (no competition TIFFs needed in CI)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pytest

from gems.variants import Dots, relief

ROOT = Path(__file__).resolve().parents[1]


def test_relief_tercile_shift_basic() -> None:
    # 20 dots: 5 in basin (0), 5 in piedmont (1), 10 in range (2)
    ys = np.arange(1, 21)
    xs = np.ones(20, dtype=int)
    parent = Dots(ys, xs, np.ones(20))

    det_elev = np.zeros((25, 25), dtype=np.float32)
    terciles = np.zeros((25, 25), dtype=int)
    terciles[1:6, :] = 0   # basin (5 dots)
    terciles[6:11, :] = 1  # piedmont (5 dots)
    terciles[11:21, :] = 2 # range (10 dots)

    # Move frac=0.10 of total mass into piedmont (allow_out_of_bounds since 20 dots total)
    v = relief(parent, det_elev, terciles, frac=0.10, direction="to_piedmont")
    assert len(v.dots) == 20
    assert np.isclose(v.dots.p.sum(), 20.0)
    # Piedmont mass should increase, basin + range should decrease
    assert v.dots.p[5:10].sum() > 5.0
    assert v.dots.p[0:5].sum() < 5.0
    assert v.dots.p[10:20].sum() < 10.0


def test_relief_receipts_ledger_and_policy_invariants() -> None:
    relief_doc = json.loads((ROOT / "evidence" / "relief_variants.json").read_text(encoding="utf-8"))
    assert relief_doc["axis"] == "RELIEF"
    assert relief_doc["parent"] == "h33-h33-2-b2"
    assert relief_doc["parent_claim"]["evidence_label"] == "CLAIM"
    assert relief_doc["parent_claim"]["receipt"] is False
    assert relief_doc["exact_parent_rebuild"]["matches_recorded_hashes"] is True

    variants = relief_doc["variants"]
    assert len(variants) == 3
    assert [v["value"] for v in variants] == ["p10piedmont", "p12piedmont", "p15piedmont"]

    for v in variants:
        assert v["n_dots"] == 37654
        assert v["status"] == "BUILT"
        assert v["predicted_change"].startswith("MODEL:")
        assert len(v["form_note"]) <= 140
        assert 1.0 <= v["pct_changed"] <= 50.0
        assert v["parent_diff"]["min_catalogue_distance_px"] > 2.0
        assert all(v["format_validation"]["nan"].values())
        assert all(v["format_validation"]["zeros"].values())

    # Check ledger uniqueness on sha256 and (parent, axis, value)
    with (ROOT / "ledger" / "submissions.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    shas = [r["sha256"] for r in rows]
    pairs = [(r["parent"], r["axis"], r["value"]) for r in rows]
    assert len(shas) == len(set(shas)), "Duplicate SHA256 in ledger"
    assert len(pairs) == len(set(pairs)), "Duplicate (parent, axis, value) in ledger"

    relief_rows = [r for r in rows if r["axis"] == "RELIEF"]
    assert len(relief_rows) == 3
    for r in relief_rows:
        assert r["n_dots"] == "37654"
        assert r["receipt_score"] == ""
        assert r["receipt_date"] == ""

    # Check mechanism cards & report-only proxy audit
    cards = json.loads((ROOT / "ledger" / "mechanism_cards.json").read_text(encoding="utf-8"))
    for v in variants:
        assert v["id"] in cards
        c = cards[v["id"]]
        for req_key in ("hypothesis", "mechanism", "non_fault_mimic", "predicted_sign_and_size", "falsifier"):
            assert c.get(req_key)

    proxy_doc = json.loads((ROOT / "evidence" / "relief_proxy_audit.json").read_text(encoding="utf-8"))
    assert proxy_doc["evidence_label"] == "PROXY"
    assert proxy_doc["leakage_canaries"]["stop_and_investigate_if_any_gt_0_90"] is False
    assert proxy_doc["leakage_canaries"]["max_symmetric_auc"] < 0.90
