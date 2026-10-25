"""Unit tests for the ALI lane helpers (no competition rasters needed)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ali_design import OFFS, coverage  # noqa: E402
from ali_features import safe_load, safe_save  # noqa: E402
from ali_place import nms_dots  # noqa: E402


def _brute_cover(p):
    """C(g) = max_x p(x) k(|x-g|), k = (1 - d/3)+ : direct O(n^2) reference."""
    ys, xs = np.nonzero(p)
    H, W = p.shape
    gy, gx = np.mgrid[0:H, 0:W]
    out = np.zeros_like(p, dtype=np.float64)
    for y, x in zip(ys, xs):
        d = np.hypot(gy - y, gx - x)
        out = np.maximum(out, p[y, x] * np.clip(1 - d / 3.0, 0, None))
    return out


def test_kernel_offsets_match_official_support():
    # 300 m triangular kernel on 100 m pixels: k = 1 - d/3 > 0 only for d < 3 px.
    # That is the 5x5 block (max d = 2*sqrt(2) < 3); the four axis offsets at d = 3 carry k = 0.
    assert len(OFFS) == 25
    assert {(dy, dx) for dy, dx, _ in OFFS} == {(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)}
    for dy, dx, k in OFFS:
        assert np.isclose(k, 1 - np.hypot(dy, dx) / 3.0)


def test_coverage_equals_bruteforce():
    rng = np.random.default_rng(0)
    p = np.zeros((40, 50), np.float32)
    idx = rng.choice(p.size, 25, replace=False)
    p.ravel()[idx] = rng.uniform(0.2, 1.0, 25).astype(np.float32)
    assert np.allclose(coverage(p), _brute_cover(p), atol=1e-6)


def test_nms_respects_separation_and_budget():
    rng = np.random.default_rng(1)
    score = rng.random((60, 60)).astype(np.float32)
    cand = np.ones_like(score, bool)
    dots = nms_dots(score, cand, 2.5, 200)
    ys, xs = np.nonzero(dots)
    assert 0 < len(ys) <= 200
    d = np.hypot(ys[:, None] - ys[None, :], xs[:, None] - xs[None, :])
    d[np.diag_indices_from(d)] = np.inf
    assert d.min() >= 2.5


def test_nms_never_leaves_candidate_mask():
    score = np.ones((30, 30), np.float32)
    cand = np.zeros_like(score, bool)
    cand[5:10, 5:25] = True
    dots = nms_dots(score, cand, 2.5, 10_000)
    assert dots.any() and not (dots & ~cand).any()


def test_safe_save_roundtrip_and_tamper_detection(tmp_path):
    a = np.arange(20_000, dtype=np.float32).reshape(-1, 4)
    a[3, 2] = np.nan  # NaN must not break the byte-level comparison
    p = tmp_path / "x.npy"
    h = safe_save(p, a)
    b = safe_load(p, h)
    assert np.array_equal(np.isnan(a), np.isnan(b))
    raw = bytearray(p.read_bytes())
    raw[200:4096] = b"\0" * (4096 - 200)  # the zeroed-first-page failure seen in this sandbox
    p.write_bytes(bytes(raw))
    with pytest.raises(IOError):
        safe_load(p, h)


def test_ali_run_card_is_rejection_only_and_byte_bound():
    card_path = ROOT / "evidence" / "ali_run_card.json"
    if not card_path.is_file():
        pytest.skip("ALI run card not generated in this checkout")
    card = json.loads(card_path.read_text())
    assert card["verdict"] == "negative" and card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0 and card["organizer_confirmed_score"] is None
    assert 0 < len(card["note"]) <= 140 and len(card["submission_name"]) <= 140
    import hashlib
    tif = ROOT / card["raster"]["path"]
    assert hashlib.sha256(tif.read_bytes()).hexdigest() == card["raster_sha256"]
    h = card["holdout_dti"]
    assert h["evidence_class"] == "HOLDOUT-DTI" and h["withheld_positive_pixels"] > 0 and len(h["ci95"]) == 2
    assert card["leakage_canaries"]["max_auc"] <= 0.90
    reg = card["correlation_overlap_vs_registry"]["final_dots"]
    # the stop must be carried by real dot fields, not only by space-filling surfaces
    assert reg["discriminating_dot_fields"]["duplicate"] is True
    assert reg["discriminating_dot_fields"]["worst_forward_overlap"] > 0.70
