"""Tests for the CONCENTRATION axis machinery. No competition data required.

The removal and placement routines claim to be *exact* marginal-DTI routines.
These tests hold them to that claim by recomputing DTI from scratch, and pin the
two structural guarantees the axis depends on: the dot count never changes and
per-block quotas are never exceeded.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor"), str(ROOT / "scripts")]

from concentration_axis import (  # noqa: E402
    DotState, allocate_quotas, block_index, block_mean, greedy_add_blocked,
    greedy_remove,
)
from gems57 import metric  # noqa: E402


def brute_dti(mask: np.ndarray, w: np.ndarray) -> float:
    """Independent recomputation of DTI for a binary dot mask under weights w."""
    ys, xs = np.nonzero(mask)
    cov = np.zeros(mask.shape)
    m_dot = 0.0
    for y, x in zip(ys, xs):
        best = 0.0
        for dy, dx, kw in zip(metric.OFF_DY, metric.OFF_DX, metric.OFF_K):
            yy, xx = int(y) + int(dy), int(x) + int(dx)
            if 0 <= yy < mask.shape[0] and 0 <= xx < mask.shape[1]:
                cov[yy, xx] = max(cov[yy, xx], kw)
                best = max(best, w[yy, xx] * kw)
        m_dot += best
    t = float((w * cov).sum())
    n = float(len(ys))
    den = metric.ALPHA * (t + n - m_dot) + metric.BETA * float(w.sum())
    return t / den if den > 0 else 0.0


def make_case(seed: int = 7, shape=(40, 45), n: int = 60):
    rng = np.random.default_rng(seed)
    w = rng.random(shape)
    mask = np.zeros(shape, dtype=bool)
    ys = rng.integers(0, shape[0], size=n)
    xs = rng.integers(0, shape[1], size=n)
    mask[ys, xs] = True
    return mask, w


# --------------------------------------------------------------------------
def test_dot_state_matches_brute_force():
    mask, w = make_case()
    st = DotState(mask, w)
    assert st.dti() == pytest.approx(brute_dti(mask, w), rel=1e-12)


def test_removal_loss_is_exact():
    """Deleting dot j must move T by exactly the reported dT_rm(j)."""
    mask, w = make_case()
    st = DotState(mask, w)
    t_before = float((w * st.cov1).sum())
    dT = st.removal_loss()
    for j in range(len(st.ys)):
        m2 = mask.copy()
        m2[st.ys[j], st.xs[j]] = False
        st2 = DotState(m2, w)
        t_after = float((w * st2.cov1).sum())
        assert t_before - t_after == pytest.approx(dT[j], abs=1e-12)


def test_delta_remove_matches_brute_force():
    mask, w = make_case()
    st = DotState(mask, w)
    dT = st.removal_loss()
    worst = int(np.argmin(st.delta_remove(np.arange(len(st.ys)), dT)))
    m2 = mask.copy()
    m2[st.ys[worst], st.xs[worst]] = False
    predicted = st.dti() + st.delta_remove(np.array([worst]), dT[[worst]])[0]
    assert brute_dti(m2, w) == pytest.approx(predicted, rel=1e-10)


def test_greedy_remove_honours_count_and_allowed():
    mask, w = make_case(n=80)
    st = DotState(mask, w)
    allowed = np.zeros(int(mask.sum()), dtype=bool)
    allowed[::2] = True  # only every other dot may be taken
    removed = greedy_remove(st, 10, allowed=allowed, batch=3)
    assert len(removed) == 10
    assert allowed[removed].all()
    assert int(st.mask.sum()) == int(mask.sum()) - 10


def test_greedy_remove_prefers_least_costly_dots():
    """The first dots taken should be the ones with the smallest removal loss."""
    mask, w = make_case(n=60)
    st = DotState(mask, w)
    loss = st.delta_remove(np.arange(len(st.ys)), st.removal_loss())
    taken = greedy_remove(DotState(mask, w), 5, batch=5)
    kept = np.setdiff1d(np.arange(len(st.ys)), taken)
    assert loss[taken].min() >= loss[kept].max() - 1e-12


# --------------------------------------------------------------------------
def test_allocate_quotas_sums_to_total_and_respects_caps():
    weights = np.array([4.0, 3.0, 2.0, 1.0])
    avail = np.array([100, 5, 50, 0])
    q = allocate_quotas(weights, avail, 60)
    assert q.sum() == 60
    assert (q <= avail).all()
    assert q[3] == 0
    assert q[1] <= 5


def test_allocate_quotas_is_deterministic():
    w = np.array([1.0, 2.0, 3.0, 4.0])
    a = np.array([7, 3, 9, 2])
    assert np.array_equal(allocate_quotas(w, a, 15), allocate_quotas(w, a, 15))


def test_allocate_quotas_raises_when_blocks_cannot_absorb():
    with pytest.raises(ValueError):
        allocate_quotas(np.array([1.0, 1.0]), np.array([1, 1]), 10)


def test_greedy_add_blocked_respects_capacity_and_count():
    mask, w = make_case(n=40)
    st = DotState(mask, w)
    block_px = 8
    bi, nby, nbx = block_index(mask.shape, block_px)
    nblk = nby * nbx
    total_before = int(st.mask.sum())

    legal = np.ones(mask.shape, dtype=bool)
    cand_mask = legal & ~mask
    # two destination blocks with hard caps
    dest_ids = np.array([bi[0, 0], bi[10, 10]])
    dest_index = np.full(nblk, -1, dtype=np.int32)
    dest_index[dest_ids] = np.arange(len(dest_ids), dtype=np.int32)
    cand_block = dest_index[bi].astype(np.int32)
    cap = np.array([4, 2], dtype=np.int64)

    greedy_add_blocked(st, cand_mask, 6, cand_block, cap)
    assert int(st.mask.sum()) == total_before + 6
    added = st.mask & ~mask
    counts = np.bincount(cand_block[added], minlength=2)
    assert counts[0] == 4 and counts[1] == 2


def test_greedy_add_blocked_raises_when_pool_too_small():
    mask, w = make_case(n=40)
    st = DotState(mask, w)
    bi, nby, nbx = block_index(mask.shape, 8)
    nblk = nby * nbx
    cand_mask = np.zeros(mask.shape, dtype=bool)
    cand_mask[0, 0] = True
    dest_index = np.full(nblk, -1, dtype=np.int32)
    dest_index[bi[0, 0]] = 0
    with pytest.raises(ValueError):
        greedy_add_blocked(st, cand_mask, 3, dest_index[bi].astype(np.int32),
                           np.array([9], dtype=np.int64))


# --------------------------------------------------------------------------
def test_block_mean_and_index():
    shape = (20, 30)
    field = np.arange(600, dtype=float).reshape(shape)
    bi, nby, nbx = block_index(shape, 10)
    assert (nby, nbx) == (3, 4)   # one extra partial block per axis
    m, cnt = block_mean(field, bi, nby * nbx)
    assert cnt.sum() == 600
    # block (0,0) is the mean of rows 0-9, cols 0-9
    assert m[0] == pytest.approx(field[:10, :10].mean())


def test_block_mean_respects_weight_mask():
    shape = (10, 10)
    field = np.ones(shape)
    field[:5] = 3.0
    bi, nby, nbx = block_index(shape, 5)
    weight = np.zeros(shape, dtype=bool)
    weight[:5] = True
    m, cnt = block_mean(field, bi, nby * nbx, weight=weight)
    assert cnt[0] == 25      # top-left block fully weighted
    assert cnt[2] == 0       # bottom-left block excluded
    assert m[0] == pytest.approx(3.0)
    assert np.isnan(m[2])
