"""Unit tests for the CHILISTRIC geological feature & surface module."""
from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest
from scipy.ndimage import distance_transform_edt

from gems import chilistric as cl


def test_feature_index_sets_valid_and_disjoint_from_out_of_bounds():
    n = len(cl.FEATURE_NAMES)
    assert n == 44
    assert len(set(cl.FEATURE_NAMES)) == 44
    for idx_set in (
        cl.BASE_ONLY_INDICES,
        cl.DEBIASED_INDICES,
        cl.ADAPT_SUB_INDICES,
        cl.SCARP10M_HYDRO_INDICES,
    ):
        assert len(idx_set) > 0
        assert all(0 <= i < n for i in idx_set)
    # BASE_ONLY_INDICES strictly excludes all 8 new CHILISTRIC channels 36..43
    assert max(cl.BASE_ONLY_INDICES) == 35


def test_adaptive_dip_offset_bounds_and_depth_monotonicity():
    h, w = 48, 48
    valid = np.ones((h, w), dtype=bool)
    valid[:4, :] = False

    # Left half: shallow 120 m pediment; Right half: deep 950 m graben
    depth = np.full((h, w), 120.0, dtype=np.float32)
    depth[:, w // 2 :] = 950.0
    grav_hg = np.full((h, w), 1.5, dtype=np.float32)
    grav_vg = np.full((h, w), 1.0, dtype=np.float32)

    s = cl.compute_adaptive_dip_offset_px(depth, grav_hg, grav_vg, valid)
    assert s.dtype == np.float32
    assert np.all(s[~valid] == 0.0)
    assert np.all((s[valid] >= 1.80 - 1e-5) & (s[valid] <= 6.20 + 1e-5))
    shallow_mean = float(s[12:36, 6:16].mean())
    deep_mean = float(s[12:36, 32:42].mean())
    assert shallow_mean < 2.60
    assert deep_mean > 4.60
    assert deep_mean - shallow_mean > 2.0


def test_second_best_corroboration_suppresses_single_modality_mimics():
    valid = np.ones((3, 3), dtype=bool)
    valid[0, 0] = False

    # Pure single-modality mimic (high scarp, zero listric, zero hydro) -> 0.0!
    a = np.array([[0.9, 0.95, 0.80], [0.0, 0.70, 0.65], [0.1, 0.5, 0.9]], dtype=np.float32)
    b = np.array([[0.8, 0.00, 0.75], [0.9, 0.00, 0.60], [0.2, 0.5, 0.4]], dtype=np.float32)
    c = np.array([[0.7, 0.00, 0.05], [0.0, 0.68, 0.55], [0.9, 0.1, 0.8]], dtype=np.float32)

    sec = cl.compute_second_best_corroboration(a, b, c, valid)
    assert sec[0, 0] == 0.0  # outside valid
    assert sec[0, 1] == pytest.approx(0.0)  # pure shoreline mimic suppressed
    assert sec[1, 0] == pytest.approx(0.0)  # pure paleovalley mimic suppressed
    assert sec[0, 2] == pytest.approx(0.75)  # scarp + listric corroborated
    assert sec[1, 1] == pytest.approx(0.68)  # scarp + hydro corroborated
    assert sec[2, 2] == pytest.approx(0.80)  # all 3 corroborated


def test_mt_depth_deconfounded_edge_removes_pure_cover_trend():
    h, w = 64, 64
    valid = np.ones((h, w), dtype=bool)
    xx = np.linspace(0.0, 1200.0, w, dtype=np.float32)[None, :]
    depth = np.broadcast_to(xx, (h, w)).copy()
    # Pure basin-fill conductivity trend: log1p(cond) = 0.4 + 0.35 * log1p(depth)
    b_log = np.log1p(depth)
    cond_pure = np.expm1(0.4 + 0.35 * b_log).astype(np.float32)
    vg = np.zeros((h, w), dtype=np.float32)

    # Inject a sharp cross-contour fault conduit at row=32 (orthogonal to depth gradient)
    cond_fault = cond_pure.copy()
    cond_fault[32:, :] *= 4.5

    edge_pure = cl._mt_depth_deconfounded_edge(cond_pure, depth, vg, valid)
    edge_fault = cl._mt_depth_deconfounded_edge(cond_fault, depth, vg, valid)
    assert float(edge_pure[10:54, 10:54].max()) < 0.01
    assert float(edge_fault[31:34, 10:54].mean()) > 0.70
    assert float(edge_fault[10:20, 10:54].mean()) < 0.02
    assert np.all((edge_fault >= 0.0) & (edge_fault <= 1.0))
    assert np.isfinite(edge_pure).all()


def test_additive_tail_allocation_preserves_unit_peaks_and_spacing():
    rng = np.random.default_rng(42)
    h, w = 80, 80
    valid = np.ones((h, w), dtype=bool)
    valid[:3, :] = False
    score = rng.uniform(0.05, 1.0, size=(h, w)).astype(np.float32)
    score[~valid] = 0.0

    prim = cl.spaced_top_mask(score, valid, 30, min_dist_px=4.5)
    assert int(prim.sum()) == 30

    alloc = cl.build_additive_tail_allocation(
        prim,
        score,
        valid,
        n_tail_dots=20,
        min_dist_from_primary_px=4.2,
        tail_min_dist_px=4.2,
        tail_weight=0.65,
    )
    assert alloc.dtype == np.float32
    assert np.isfinite(alloc).all()
    assert np.all((alloc >= 0.0) & (alloc <= 1.0))
    assert np.all(alloc[~valid] == 0.0)
    # Every primary dot preserves exact 1.0 peak (zero fixed-L1 dilution!)
    assert np.all(alloc[prim] == 1.0)
    tail_mask = (alloc > 0.0) & (~prim)
    assert int(tail_mask.sum()) == 20
    assert np.allclose(alloc[tail_mask], 0.65)
    d_prim = distance_transform_edt(~prim)
    assert float(d_prim[tail_mask].min()) >= 4.2 - 1e-5

    with pytest.raises(ValueError):
        cl.build_additive_tail_allocation(prim, score, valid, tail_weight=0.0)
    with pytest.raises(ValueError):
        cl.build_additive_tail_allocation(prim, score, valid, tail_weight=1.1)


def test_zero_catalogue_imports_in_chilistric_module():
    src = Path(cl.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden = {"existing_faults", "d_cat", "dist_known_fault", "catalogue"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            assert node.id not in forbidden, f"Forbidden identifier {node.id} in gems/chilistric.py"


def test_chilistric_run_card_and_rasters_pass_all_gates():
    import hashlib
    import json
    from gems.gates import run_gates

    root = Path(__file__).resolve().parents[1]
    ev_card = root / "evidence" / "chilistric_run_card.json"
    dl_card = root / "docs" / "downloads" / "chilistric_run_card.json"
    ho_path = root / "evidence" / "chilistric_holdout.json"
    assert ev_card.is_file() and dl_card.is_file() and ho_path.is_file()
    assert ev_card.read_bytes() == dl_card.read_bytes()

    rc = json.loads(ev_card.read_text(encoding="utf-8"))
    ho = json.loads(ho_path.read_text(encoding="utf-8"))

    # Protocol Rule 5 & Rule 6 checks
    assert rc["lane"] == "CHILISTRIC"
    assert rc["verdict"] == "negative"
    assert rc["submission_eligible"] is False
    assert rc["experiments_run"] == 3
    assert rc["weekly_slots_spent"] == 0
    assert 0 < len(rc["submission_note"]) <= 140
    assert rc["note"] == rc["submission_note"]
    assert rc["organizer_confirmed"] is None or rc["organizer_confirmed"].get("score") is None

    # Protocol Rule 4: all 44 single-feature leakage canaries <= 0.90
    can = ho["leakage_canaries"]
    assert can["n_features"] == 44
    assert can["all_pass"] is True
    assert float(can["max_symmetric_auc"]) <= 0.90
    for f_row in can["features"]:
        assert float(f_row["symmetric_auc"]) <= 0.90

    # Verify all 3 generated GeoTIFFs match SHA-256 and pass 11/11 automated gates
    sample = root / "data" / "bridge" / "sample_submission.tif"
    labels = root / "data" / "bridge" / "labels.tif"
    for arm, rel_tif in rc["all_experiment_files"].items():
        tif_path = root / rel_tif
        assert tif_path.is_file(), f"Missing GeoTIFF for {arm}: {rel_tif}"
        sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
        assert sha == rc["all_experiment_sha256"][arm]
        gates = run_gates(
            tif_path,
            sample,
            labels,
            prune_radius=2,
            require_submission_encoding=True,
        )
        assert len(gates) == 11
        assert all(g.ok for g in gates), [g for g in gates if not g.ok]

