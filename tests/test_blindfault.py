"""BLINDFAULT lane + matched-budget uniqueness policy tests (2026-10-25)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from gems57 import uniqueness as U

ROOT = Path(__file__).resolve().parents[1]


def test_matched_budget_support_topk_and_small_support():
    fp = np.ones((6, 6), bool)
    v = np.arange(36, dtype=float).reshape(6, 6) + 1.0  # all positive, dense
    top = U.matched_budget_support(v, fp, 3)
    assert top.sum() == 3 and top[5, 5] and top[5, 4] and top[5, 3]
    sparse = np.zeros((6, 6)); sparse[0, 0] = 1; sparse[1, 1] = 1
    assert U.matched_budget_support(sparse, fp, 10).sum() == 2  # support smaller than k is kept whole
    assert U.matched_budget_support(v, fp, 0).sum() == 0


def test_dual_overlap_dense_surface_literal_fires_but_matched_budget_discriminates():
    fp = np.ones((40, 40), bool)
    mine = np.zeros((40, 40)); mine[5, 5] = mine[20, 20] = mine[35, 5] = 1
    dense = np.full((40, 40), 0.01); dense[0, 0] = 1.0; dense[0, 1] = 0.9; dense[0, 2] = 0.8
    r = U.dual_overlap(mine, dense, fp, dot_field_max_support=100)
    assert r["representation"] == "continuous_surface"
    assert r["literal_forward_overlap"] == 1.0            # degenerate reading
    assert r["matched_budget_forward_overlap"] == 0.0     # top-3 cells are far from my dots
    assert r["matched_budget_k"] == 3
    near = np.zeros((40, 40)); near[5, 6] = 1; near[20, 21] = 1
    r2 = U.dual_overlap(mine, near, fp)
    assert r2["representation"] == "dot_field" and abs(r2["literal_forward_overlap"] - 2 / 3) < 1e-9
    assert r2["matched_budget_forward_overlap"] == r2["literal_forward_overlap"]


def test_dual_reading_decision_reports_both_and_uses_matched_budget():
    rows = [
        dict(file="dense", representation="continuous_surface", literal_forward_overlap=1.0,
             matched_budget_forward_overlap=0.10, spearman_surface=0.2),
        dict(file="dots", representation="dot_field", literal_forward_overlap=0.65,
             matched_budget_forward_overlap=0.65, spearman_surface=0.1),
    ]
    d = U.dual_reading_decision(rows)
    assert d["literal_reading_fires"] is True
    assert d["worst_literal_forward_overlap"] == 1.0
    assert d["worst_matched_budget_forward_overlap"] == 0.65
    assert d["duplicate"] is False and d["verdict"] == "unique"
    rows[1]["matched_budget_forward_overlap"] = rows[1]["literal_forward_overlap"] = 0.71
    assert U.dual_reading_decision(rows)["duplicate"] is True
    rows[1]["matched_budget_forward_overlap"] = rows[1]["literal_forward_overlap"] = 0.5
    rows[0]["spearman_surface"] = -0.95
    assert U.dual_reading_decision(rows)["duplicate"] is True  # |rho| applies to dense rasters too


def test_positive_weights_monotone_and_bounded():
    from gems.blindfault import positive_weights
    c = np.array([0.0, 0.5, 1.0], np.float32)
    w = positive_weights(c)
    assert w[0] > w[1] > w[2] and abs(w[0] - 10.0) < 1e-5 and abs(w[2] - 1 / 1.1) < 1e-5


@pytest.mark.skipif(not (ROOT / "evidence/blindfault_run_card.json").is_file(), reason="run card not built")
def test_blindfault_run_card_is_labelled_and_consistent():
    card = json.loads((ROOT / "evidence/blindfault_run_card.json").read_text())
    hold = json.loads((ROOT / "evidence/blindfault_holdout.json").read_text())
    assert card["lane"] == "BLINDFAULT" and card["weekly_slots_used"] == 0
    assert card["holdout_dti"]["evidence_class"] == "HOLDOUT-DTI"
    assert card["holdout_dti"]["evaluator_version"] == "gems57-pooled-hide-v2"
    assert card["holdout_dti"]["withheld_positives"] == 22663 == hold["withheld_positive_pixels"]
    assert len(card["submission_note"]) <= 140 and len(card["submission_name"]) <= 140
    assert card["leakage_canaries"]["all_pass_le_0p90"] is True
    best = card["primary_arm"]
    best_dti = card["holdout_dti"]["scores"][best]["dti"]
    ref = card["holdout_dti"]["repository_holdout_best"]["dti"]
    # verdict must follow the pre-registered gate, never a projection
    if best_dti <= ref:
        assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert card["organizer_confirmed"] is None
    tif = ROOT / card["file"]
    assert tif.is_file()
    import hashlib
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster_sha256"]
