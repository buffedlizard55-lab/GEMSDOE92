"""Independent regression check of the shared DTI evaluator (2026-10-25).

The naive implementation below is written directly from the official
DrivenData problem-description equations (competition 306, page 967) and
shares no code with ``vendor/gems57/metric.py``. The shared evaluator must
agree with it on random grids. Any drift in the shared metric fails here.

Official sources:
  https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
  (TP_w = sum_g max_x p(x)k(d); FP_w = sum_{p>0} p(x)[1-max_g k]; FN_w = sum_g[1-max_x p k];
   DTI = TP_w / (TP_w + 0.2 FP_w + 0.8 FN_w); k(d) = max(1 - d/R, 0), R = 3 px.)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import metric  # noqa: E402

R = 3.0
ALPHA, BETA = 0.2, 0.8


def _kernel(d: float) -> float:
    return max(1.0 - d / R, 0.0)


def naive_dti(p: np.ndarray, g: np.ndarray) -> float:
    """Direct transcription of the official equations; O(N*G), tiny grids only."""
    gt = [tuple(x) for x in np.argwhere(g)]
    pred = [tuple(x) for x in np.argwhere(p > 0)]
    tp = 0.0
    for gi in gt:
        best = 0.0
        for xi in pred:
            d = float(np.hypot(xi[0] - gi[0], xi[1] - gi[1]))
            if d <= R:
                best = max(best, float(p[xi]) * _kernel(d))
        tp += best
    fp = 0.0
    for xi in pred:
        dmin = min(float(np.hypot(xi[0] - gi[0], xi[1] - gi[1])) for gi in gt)
        fp += float(p[xi]) * (1.0 - _kernel(dmin))
    fn = float(len(gt)) - tp
    return tp / (tp + ALPHA * fp + BETA * fn + 1e-12)


def _random_case(seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    shape = (30, 30)
    g = np.zeros(shape, bool)
    g[rng.integers(0, 30), :] = True
    g[:, rng.integers(0, 30)] = True
    g &= rng.random(shape) < 0.9
    p = np.where(rng.random(shape) < 0.08, rng.random(shape), 0.0).astype(float)
    return p, g


def test_shared_dti_matches_naive_official_formula():
    worst = 0.0
    for seed in range(12):
        p, g = _random_case(seed)
        shared = metric.dti_exact(p, g)
        shared = shared["dti"] if isinstance(shared, dict) else float(shared)
        worst = max(worst, abs(naive_dti(p, g) - shared))
    assert worst < 1e-9, f"shared DTI drifted from the official formula: {worst}"


def test_official_worked_example_arithmetic():
    # Official worked example (page 967): TP_w = 3.00, FP_w = 1.89, FN_w = 2.00 -> 0.60
    value = 3.0 / (3.0 + ALPHA * 1.89 + BETA * 2.0)
    assert round(value, 2) == 0.60
