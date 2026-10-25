"""Synthetic physics tests for the XPHASE lane (no competition cache required)."""
from __future__ import annotations

import numpy as np

from gems.xphase import lane_surface, transverse_phase, xphase_components


def _stripe_scene(lag_px: int = 2, rotate90: bool = False):
    """Vertical MT contact at x=32; gravity contact offset by ``lag_px`` (or perpendicular)."""
    yy, xx = np.mgrid[0:64, 0:64]
    valid = np.ones((64, 64), dtype=bool)
    cond = (2.0 / (1.0 + np.exp(-(xx - 32.0) / 1.2))).astype(np.float32)
    if rotate90:
        grav = (30.0 / (1.0 + np.exp(-(yy - 32.0) / 1.2))).astype(np.float32)
    else:
        grav = (30.0 / (1.0 + np.exp(-(xx - (32.0 + lag_px)) / 1.2))).astype(np.float32)
    depth = np.full((64, 64), 250.0, dtype=np.float32)
    slope = np.full((64, 64), 1.5, dtype=np.float32)
    return cond, grav, depth, slope, valid


def test_orientation_agreement_is_high_for_parallel_and_low_for_perpendicular():
    cond, grav, depth, slope, valid = _stripe_scene(lag_px=2, rotate90=False)
    par = xphase_components(cond, grav, depth, slope, valid, apply_lag=False)
    cond_p, grav_p, depth_p, slope_p, valid_p = _stripe_scene(lag_px=2, rotate90=True)
    perp = xphase_components(cond_p, grav_p, depth_p, slope_p, valid_p, apply_lag=False)
    assert float(par["orient"][20:44, 28:36].mean()) > 0.75
    assert float(perp["orient"][20:44, 28:36].mean()) < 0.45


def test_transverse_lag_prefers_offset_gravity_peak_over_coincident():
    cond, grav_off, depth, slope, valid = _stripe_scene(lag_px=2, rotate90=False)
    _, grav_coin, *_ = _stripe_scene(lag_px=0, rotate90=False)
    off = lane_surface(cond, grav_off, depth, slope, valid, apply_lag=True)
    coin = lane_surface(cond, grav_coin, depth, slope, valid, apply_lag=True)
    # Offset contact should outrank a coincident (lithologic) contact near x=32.
    assert float(off["S_raw"][16:48, 30:35].mean()) > float(coin["S_raw"][16:48, 30:35].mean())
    assert off["lag"].dtype == np.float32
    assert np.all((off["lag"] >= 0.0) & (off["lag"] <= 1.0))


def test_cover_gate_prefers_intermediate_basement_depth():
    yy, xx = np.mgrid[0:48, 0:48]
    valid = np.ones((48, 48), dtype=bool)
    cond = (2.0 / (1.0 + np.exp(-(xx - 24.0) / 1.5))).astype(np.float32)
    grav = (20.0 / (1.0 + np.exp(-(xx - 26.0) / 1.5))).astype(np.float32)
    slope = np.full((48, 48), 1.0, dtype=np.float32)
    depth = np.where(xx < 16, 8.0, np.where(xx < 32, 250.0, 2500.0)).astype(np.float32)
    c = xphase_components(cond, grav, depth, slope, valid)
    mid = float(c["cover"][:, 16:32].mean())
    shallow = float(c["cover"][:, :16].mean())
    deep = float(c["cover"][:, 32:].mean())
    assert mid > 3.0 * shallow
    assert mid > 3.0 * deep


def test_nophase_ablation_sets_lag_to_one():
    cond, grav, depth, slope, valid = _stripe_scene(lag_px=2)
    with_lag = lane_surface(cond, grav, depth, slope, valid, apply_lag=True)
    no_lag = lane_surface(cond, grav, depth, slope, valid, apply_lag=False)
    assert float(no_lag["lag"][valid].min()) == 1.0
    assert float(with_lag["lag"][valid].mean()) < 1.0
    assert with_lag["ridge_1d"].dtype == bool
    assert int(with_lag["ridge_1d"].sum()) > 10


def test_on_disk_primary_is_format_valid_and_not_slot_cleared():
    import hashlib
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    tif = root / "docs/downloads/h33-h33-2-b2-XPHASEdual40-20261024-643553cf-zeros.tif"
    audit = root / "docs/downloads/h33-h33-2-b2-XPHASEdual40-20261024-643553cf-audit.json"
    card = json.loads((root / "evidence/xphase_run_card.json").read_text(encoding="utf-8"))
    assert tif.is_file() and audit.is_file()
    sha = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert sha == "080018382de33758c78e1b11f80098a1f736ac7de5f4c55641bd84b52b0f7200"
    assert card["raster_sha256"] == sha
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["holdout_dti"]["dti"] == 0.004653
    assert card["leakage_canary_max_symmetric_auc"] <= 0.90
    assert len(card["note"]) <= 140
    doc = json.loads(audit.read_text(encoding="utf-8"))
    assert doc["overall_pass"] is True
    assert doc["submission_eligible"] is False
    assert doc["public_registry_uniqueness"]["stop_required"] is True
    assert doc["sha256_zeros"] == sha


def test_transverse_phase_helper_range():
    mag = np.ones((8, 8), dtype=np.float32)
    ny = np.zeros((8, 8), dtype=np.float32)
    nx = np.ones((8, 8), dtype=np.float32)
    lag = transverse_phase(mag, mag, ny, nx, lag_px=1.0)
    assert lag.shape == (8, 8)
    assert np.all((lag >= 0.0) & (lag <= 1.0))
