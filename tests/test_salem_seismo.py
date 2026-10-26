"""Unit tests for the SALEMSEISMO zero-catalogue multi-physics + CELF module."""
from __future__ import annotations

import numpy as np
import pytest

from gems import salem_seismo as ss


def _bruteforce_submodular_greedy(
    surface: np.ndarray,
    cand_mask: np.ndarray,
    n: int,
    *,
    min_dist_px: float = 2.8,
    power_eta: float = 1.35,
    initial_coverage: np.ndarray | None = None,
    dot_amplitude: float = 1.0,
) -> np.ndarray:
    """Direct O(n * |cand| * 25) reference greedy solver to prove CELF bit-exactness."""
    surf = np.maximum(np.nan_to_num(surface.astype(np.float32), nan=0.0), 0.0)
    s_max = float(surf[cand_mask].max())
    w_grid = np.where(surf > 0.0, (surf / np.float32(s_max)) ** np.float32(power_eta), 0.0).astype(np.float32)
    h, w = surf.shape
    cov = (
        np.clip(initial_coverage.astype(np.float32), 0.0, 1.0).copy()
        if initial_coverage is not None
        else np.zeros((h, w), dtype=np.float32)
    )
    ys, xs = np.nonzero(cand_mask)
    chosen = np.zeros((h, w), dtype=bool)
    blocked = np.zeros((h, w), dtype=bool)

    # Compute initial tie_rank order identical to celf_submodular_place
    from scipy.ndimage import convolve
    g0 = (np.float32(dot_amplitude) * convolve(w_grid, ss.KERNEL_300M_7X7, mode="constant")).astype(np.float32)
    init_order = np.argsort(-g0[ys, xs], kind="stable")
    ys = ys[init_order]
    xs = xs[init_order]

    for _ in range(n):
        best_gain = -1.0
        best_idx = -1
        for i in range(ys.size):
            y, x = int(ys[i]), int(xs[i])
            if blocked[y, x]:
                continue
            g = 0.0
            for dy, dx, kw in ss.KERNEL_300M_OFFSETS:
                yy, xx = y + dy, x + dx
                if 0 <= yy < h and 0 <= xx < w:
                    nc = dot_amplitude * kw
                    oc = float(cov[yy, xx])
                    if nc > oc:
                        g += float(w_grid[yy, xx]) * (nc - oc)
            if g > best_gain + 1e-12:
                best_gain = g
                best_idx = i
        assert best_idx >= 0
        by, bx = int(ys[best_idx]), int(xs[best_idx])
        chosen[by, bx] = True
        for y2 in range(h):
            for x2 in range(w):
                if (y2 - by) ** 2 + (x2 - bx) ** 2 < min_dist_px ** 2:
                    blocked[y2, x2] = True
        for dy, dx, kw in ss.KERNEL_300M_OFFSETS:
            yy, xx = by + dy, bx + dx
            if 0 <= yy < h and 0 <= xx < w:
                nc = np.float32(dot_amplitude * kw)
                if nc > cov[yy, xx]:
                    cov[yy, xx] = nc
    return chosen


def _kernel_weighted_recall(w_grid: np.ndarray, alloc: np.ndarray) -> float:
    h, w = w_grid.shape
    cov = np.zeros((h, w), dtype=np.float32)
    for dy, dx, kw in ss.KERNEL_300M_OFFSETS:
        ys = slice(max(dy, 0), h + min(dy, 0))
        yd = slice(max(-dy, 0), h + min(-dy, 0))
        xs = slice(max(dx, 0), w + min(dx, 0))
        xd = slice(max(-dx, 0), w + min(-dx, 0))
        np.maximum(cov[yd, xd], np.float32(kw) * alloc[ys, xs], out=cov[yd, xd])
    return float((w_grid * cov).sum())


def test_kernel_300m_offsets_exact():
    assert len(ss.KERNEL_300M_OFFSETS) == 25
    for dy, dx, kw in ss.KERNEL_300M_OFFSETS:
        assert abs(dy) <= 2 and abs(dx) <= 2
        assert np.isclose(kw, 1.0 - np.hypot(dy, dx) / 3.0)


def test_celf_matches_bruteforce_with_and_without_initial_coverage():
    rng = np.random.default_rng(42)
    surf = (rng.random((28, 32)).astype(np.float32) ** 2) + 0.01
    cand = np.ones((28, 32), dtype=bool)
    cand[:2, :] = False

    got = ss.celf_submodular_place(surf, cand, 18, min_dist_px=2.8, power_eta=1.35)
    ref = _bruteforce_submodular_greedy(surf, cand, 18, min_dist_px=2.8, power_eta=1.35)
    assert np.array_equal(got, ref)

    # Also verify exact match when initial_coverage is present
    init_cov = np.zeros((28, 32), dtype=np.float32)
    init_cov[8:13, 10:15] = 0.75
    got2 = ss.celf_submodular_place(
        surf, cand, 14, min_dist_px=3.2, power_eta=1.35, initial_coverage=init_cov, dot_amplitude=0.65
    )
    ref2 = _bruteforce_submodular_greedy(
        surf, cand, 14, min_dist_px=3.2, power_eta=1.35, initial_coverage=init_cov, dot_amplitude=0.65
    )
    assert np.array_equal(got2, ref2)


def test_celf_beats_point_greedy_on_parallel_double_ridge_and_spikes():
    """Demonstrate why CELF beats spaced_top_mask:
    - Fault A has two parallel twin ridges 3 px apart (e.g. scarp + updip ramp) of height 0.90.
    - Fault B is a separate continuous fault ridge of height 0.82.
    - Isolated 1-px noise spikes have height 0.95 surrounded by zeros.
    Point-greedy wastes its budget on 1-px spikes and twin ridges on Fault A;
    CELF ignores isolated spikes and places dots along BOTH Fault A and Fault B!
    """
    surf = np.zeros((40, 40), dtype=np.float32)
    # Fault A realistic 3-px scarp strip (y=8..10) where y=8 and y=10 are 2.83 px diagonal twin candidates
    surf[8, 5:35] = 0.90
    surf[9, 5:35] = 0.85
    surf[10, 5:35] = 0.89
    # Fault B single continuous ridge at y=28
    surf[27:30, 5:35] = 0.82
    # Isolated 1-px spikes
    for x_sp in (4, 10, 16, 22, 28, 34):
        surf[36, x_sp] = 0.96

    cand = np.zeros_like(surf, dtype=bool)
    cand[8, 5:35] = True
    cand[10, 5:35] = True
    cand[28, 5:35] = True
    cand[36, :] = surf[36, :] > 0

    n_dots = 14
    d_point = ss.spaced_top_mask(surf, cand, n_dots, min_dist_px=2.8)
    d_celf = ss.celf_submodular_place(surf, cand, n_dots, min_dist_px=2.8, power_eta=1.0)

    rec_point = _kernel_weighted_recall(surf, d_point.astype(np.float32))
    rec_celf = _kernel_weighted_recall(surf, d_celf.astype(np.float32))
    assert rec_celf > rec_point * 1.25
    # Point-greedy wastes all 6 spikes and misses Fault B; CELF skips all spikes and covers Fault B!
    assert int(d_celf[36, :].sum()) == 0
    assert int(d_point[36, :].sum()) == 6
    assert int(d_celf[28, :].sum()) >= 5
    assert int(d_point[28, :].sum()) == 0


def test_celf_additive_tail_allocation_invariants():
    rng = np.random.default_rng(7)
    surf = rng.random((45, 45)).astype(np.float32)
    elig = np.ones((45, 45), dtype=bool)
    prim = ss.celf_submodular_place(surf, elig, 12, min_dist_px=2.8)
    alloc = ss.celf_additive_tail_allocation(
        prim, surf, elig, n_tail_dots=8, min_dist_from_primary_px=4.0, tail_min_dist_px=3.8, tail_weight=0.65
    )
    assert alloc.dtype == np.float32
    assert float(alloc.min()) >= 0.0 and float(alloc.max()) <= 1.0
    assert int((alloc == 1.0).sum()) == 12
    assert int(np.isclose(alloc, 0.65).sum()) == 8
    assert int((alloc > 0).sum()) == 20


def test_diamond_wedge_ids_and_dual_oof_smoke():
    foot = np.ones((64, 64), dtype=bool)
    foot[:4, :] = False
    wedges = ss.diamond_wedge_ids(foot)
    assert set(np.unique(wedges[foot])).issubset({0, 1, 2, 3})
    assert len(np.unique(wedges[foot])) == 4

    quad = np.zeros((64, 64), dtype=np.int8)
    quad[32:, :] += 2
    quad[:, 32:] += 1

    rng = np.random.default_rng(99)
    n_foot = int(foot.sum())
    X_foot = rng.normal(size=(n_foot, len(ss.FEATURE_NAMES))).astype(np.float32)
    labels = np.zeros((64, 64), dtype=bool)
    labels[10:20, 14] = True
    labels[12:22, 48] = True
    labels[42:54, 16] = True
    labels[44:56, 50] = True

    res = ss.fit_predict_salem_seismo_dual_oof(
        X_foot, foot, foot, quad, wedges, labels,
        guard_px=3, neg_buffer_px=2.0, neg_pos_ratio=3, max_iter=20, seed=123,
    )
    p = res["dualcal_proba"]
    assert p.shape == (64, 64)
    assert np.isfinite(p).all()
    assert float(p.min()) >= 0.0 and float(p.max()) <= 1.0
    assert float(p[~foot].max()) == 0.0


def test_band_tag_guard_rejects_misattributed_band():
    class DummyDS:
        count = 19
        def tags(self, b: int) -> dict[str, str]:
            name = ss.EXPECTED_TRAINING_BANDS[b]
            if b == 3:
                name = "heatflow_wrong"
            return {"band_name": name}

    with pytest.raises(ValueError, match="Band 3 tag mismatch"):
        ss.assert_training_band_tags(DummyDS())  # type: ignore[arg-type]
