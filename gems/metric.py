"""DTI metric algebra for GEMS (DrivenData #306) -- official equations.

CORRECTED 2026-10-24 (shared-tool fix; see IRREGULARITIES.md). The previous
revision transcribed a session-brief algebra that does NOT match the official
metric: it defined T as a sum over dot->truth kernel weights (double-counting
truth pixels covered by several dots) and G as *uncovered* truth mass, which
can yield DTI > 1 (its old unit test asserted DTI = 5.0). Measured against the
official implementation (vendor/gems57/metric.dti_exact, itself verified
against a literal brute-force transcription) on 30 random small cases, the old
code differed by up to 0.88 (evidence/r0_forensics_20261024.json). No live
decision in this repo was gated on this module -- the holdout instrument has
always been vendor/gems57 -- but the fix is made here, once, so no future lane
inherits the wrong algebra.

Official definitions (problem description p.967, fetched and transcribed
2026-10-24; alpha = 0.2, beta = 0.8, triangular kernel R = 300 m = 3 px):

    TPw = sum_g max_x p(x) k(d(x,g))          (= T below, a max per truth px)
    FPw = sum_x p(x) [1 - max_g k(d(x,g))]    (= S - M below)
    FNw = |G| - TPw
    DTI = TPw / (TPw + alpha*FPw + beta*FNw)
        = T / (0.2*T + 0.2*(S - M) + 0.8*|G|)

    T   = sum over truth pixels g of max_j p_j k(d(j,g))   (saturates per g)
    S   = sum over dots j of p_j                           (total emitted mass)
    M   = sum over dots j of p_j * max over g of k(d)      (saturates per dot)
    |G| = total number of truth pixels (Totals.G; NOT the uncovered mass)

Marginal bar (vendor/gems57/metric.py derives the same result): adding one
non-redundant dot whose marginal truth credit dT equals its self-credit k
raises DTI iff k > alpha * DTI (k > 0.056 at DTI = 0.28).

Everything here is a PROXY evaluator for local decisions. It scores dots against
whatever truth set it is handed (normally the known-fault catalogue, used only as
a holdout). It is NOT the organizers' scoring code and never produces a "score".
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

ALPHA = 0.2
BETA = 0.8
R_PX = 3.0  # 300 m at 100 m pixels, per brief section 2

_EPS = 1e-12


def kernel(d: np.ndarray | float) -> np.ndarray | float:
    """Triangular kernel, zero at and beyond R_PX."""
    return np.maximum(0.0, 1.0 - np.asarray(d, dtype=float) / R_PX)


@dataclass(frozen=True)
class Totals:
    T: float
    S: float
    M: float
    G: float

    @property
    def dti(self) -> float:
        den = ALPHA * self.T + ALPHA * (self.S - self.M) + BETA * self.G
        if den <= 0:
            return 0.0
        return self.T / den

    def as_dict(self) -> dict:
        return {
            "T": round(self.T, 6),
            "S": round(self.S, 6),
            "M": round(self.M, 6),
            "G": round(self.G, 6),
            "dti": round(self.dti, 8),
        }


class Truth:
    """A labelled pixel set (proxy truth). Holds a KD-tree for ball queries."""

    def __init__(self, ys, xs, tree=None):
        self.ys = np.asarray(ys, dtype=np.int64)
        self.xs = np.asarray(xs, dtype=np.int64)
        self.tree = tree if tree is not None else cKDTree(np.c_[self.ys, self.xs])

    def __len__(self) -> int:
        return len(self.ys)


class DotSet:
    """Sparse dots with exact incremental DTI totals.

    dots are (y, x) integer pixel indices with float mass p. Out-of-bounds or
    duplicates are the caller's problem; build_variant guarantees uniqueness.
    """

    def __init__(self, ys, xs, p, truth: Truth):
        self.ys = np.asarray(ys, dtype=np.int64).copy()
        self.xs = np.asarray(xs, dtype=np.int64).copy()
        self.p = np.asarray(p, dtype=float).copy()
        self.truth = truth
        self._rebuild()

    # -- construction -----------------------------------------------------
    @classmethod
    def from_raster(cls, raster: np.ndarray, truth: Truth) -> "DotSet":
        ys, xs = np.nonzero(raster)
        return cls(ys, xs, raster[ys, xs].astype(float), truth)

    def _rebuild(self) -> None:
        """Recompute dot->truth links, truth->dots index and per-truth best."""
        n_t = len(self.truth)
        self.best = np.zeros(n_t, dtype=float)
        self.dot_truth: list[np.ndarray] = []
        self._cover: list[set[int]] = [set() for _ in range(n_t)]
        self.dot_credit = np.zeros(len(self.p), dtype=float)
        self.dot_max = np.zeros(len(self.p), dtype=float)
        for j, (y, x) in enumerate(zip(self.ys, self.xs)):
            idx, d = self._ball(y, x)
            self.dot_truth.append(idx)
            if len(idx) == 0:
                continue
            k = kernel(d)
            self.dot_credit[j] = k.sum()
            self.dot_max[j] = k.max()
            for g, kg in zip(idx, k):
                self._cover[g].add(j)
                cov = min(1.0, self.p[j] * kg)
                if cov > self.best[g]:
                    self.best[g] = cov

    @property
    def keys(self) -> set[tuple[int, int]]:
        return set(zip(self.ys.tolist(), self.xs.tolist()))

    def _kg(self, j: int, g: int) -> float:
        return float(kernel(np.hypot(self.truth.ys[g] - self.ys[j],
                                     self.truth.xs[g] - self.xs[j])))

    def _ball(self, y, x):
        idx = self.truth.tree.query_ball_point([y, x], R_PX)
        if not idx:
            return np.empty(0, np.int64), np.empty(0, float)
        idx = np.asarray(idx, dtype=np.int64)
        d = np.hypot(self.truth.ys[idx] - y, self.truth.xs[idx] - x)
        keep = d <= R_PX
        return idx[keep], d[keep]

    # -- totals -----------------------------------------------------------
    @property
    def S(self) -> float:
        return float(self.p.sum())

    def totals(self) -> Totals:
        # Official TPw: per-truth-pixel max credit (self.best), summed over
        # truth pixels -- NOT sum_j p_j * sum_g k, which double-counts truth
        # covered by several dots (pre-2026-10-24 bug; dot_credit is kept
        # only as a diagnostic). G is the total truth count |G|.
        T = float(np.minimum(1.0, self.best).sum())
        M = float((self.p * self.dot_max).sum())
        G = float(len(self.truth))
        return Totals(T=T, S=self.S, M=M, G=G)

    # -- exact marginal gains --------------------------------------------
    @staticmethod
    def _apply(T, S, M, G, dT, dS, dM, dG) -> float:
        """Exact dDTI for (T,S,M,G) -> (T+dT, S+dS, M+dM, G+dG)."""
        den0 = ALPHA * T + ALPHA * (S - M) + BETA * G
        den1 = ALPHA * (T + dT) + ALPHA * (S + dS - M - dM) + BETA * (G + dG)
        d0 = T / den0 if den0 > 0 else 0.0
        d1 = (T + dT) / den1 if den1 > 0 else 0.0
        return d1 - d0

    def gain_add(self, y: int, x: int, p: float = 1.0) -> float:
        """Exact dDTI of adding mass p at an empty pixel.

        With no truth in reach the dot still adds p to S, so the gain is
        negative (denominator grows, numerator does not). That negative
        signal is what makes MASS-drop ranking meaningful.
        """
        t = self.totals()
        idx, d = self._ball(y, x)
        if len(idx) == 0:
            return self._apply(t.T, t.S, t.M, t.G, 0.0, p, 0.0, 0.0)
        k = kernel(d)
        # Marginal TPw: only the improvement over each truth pixel's current
        # best coverage counts (official max-per-truth rule). |G| is fixed.
        newcov = np.minimum(1.0, p * k)
        dT = float(np.sum(np.maximum(0.0, newcov - self.best[idx])))
        c_max = float(p * k.max())
        return self._apply(t.T, t.S, t.M, t.G, dT, p, c_max, 0.0)

    def gain_move(self, j: int, y: int, x: int) -> float:
        """Exact dDTI of moving dot j to (y, x). Mass, count and S preserved."""
        t = self.totals()
        pj = self.p[j]
        new_idx, nd = self._ball(y, x)
        affected = set(np.asarray(self.dot_truth[j]).tolist()) | set(new_idx.tolist())

        dM = -pj * self.dot_max[j]
        if len(new_idx):
            k = kernel(nd)
            dM += pj * float(k.max())
            newmap = {int(g): float(kk) for g, kk in zip(new_idx, k)}
        else:
            newmap = {}

        # Marginal TPw: recompute each affected truth pixel's best coverage
        # without dot j, then with dot j at its new location. |G| is fixed.
        dT = 0.0
        for g in affected:
            others = self._cover[g] - {j}
            cov_other = max((min(1.0, self.p[m] * self._kg(m, g)) for m in others), default=0.0)
            cov_new = min(1.0, pj * newmap[g]) if g in newmap else 0.0
            dT += float(min(1.0, max(cov_other, cov_new)) - min(1.0, self.best[g]))
        return self._apply(t.T, t.S, t.M, t.G, dT, 0.0, dM, 0.0)

    def rank_candidates(self, candidates, p: float = 1.0) -> list[tuple[tuple[int, int], float]]:
        """Rank empty candidate pixels by exact marginal gain, best first."""
        seen = set(zip(self.ys.tolist(), self.xs.tolist()))
        out = []
        for y, x in candidates:
            if (int(y), int(x)) in seen:
                continue
            out.append(((int(y), int(x)), self.gain_add(int(y), int(x), p)))
        out.sort(key=lambda c: (-c[1], c[0]))
        return out
