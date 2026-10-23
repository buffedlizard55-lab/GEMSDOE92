"""DTI metric algebra for GEMS (DrivenData #306).

The algebra is taken from the session brief v2, section 2, which records it as
derived and checked on 2026-10-22 against
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/
That page is NOT fetched here: its terms of use ban automated access.

    DTI = T / (0.2*T + 0.2*(S - M) + 0.8*|G|)

    T   = kernel credit
        = sum over dots j of p_j * sum over truth pixels g with d(j,g) <= R of k(d)
    S   = sum over dots j of p_j                       (total emitted mass)
    M   = sum over dots j of p_j * max over g of k(d)  (mass already credited)
    |G| = uncovered truth mass                        (ASSUMED, see below)

Kernel: triangular, R = 300 m = 3 px at 100 m pixels, k(d) = max(0, 1 - d/R).

ASSUMPTION ABOUT |G|
--------------------
The brief gives |G| no closed form. We take |G| = sum over truth pixels g of
(1 - min(1, best coverage of g by any dot)), i.e. truth mass no dot reaches.
This is flagged in IRREGULARITIES.md item 3 because the choice can reorder
dots under marginal-gain ranking.

The assumption is not arbitrary: it is the only reading under which the brief's
own stated shortcut holds. Adding one dot with credit c next to a currently
uncovered isolated truth pixel changes T by c, S by 1, M by c, |G| by -c, so

    dDTI = c - DTI*(0.2c + 0.2(1-c) + 0.8(-c)) = c - 0.2*DTI

which pays iff c > 0.2*DTI, i.e. c > 0.056 at DTI = 0.28 -- the brief's numbers.
tests/test_metric.py asserts this identity.

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
        T = float((self.p * self.dot_credit).sum())
        M = float((self.p * self.dot_max).sum())
        G = float((1.0 - np.minimum(1.0, self.best)).sum())
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
        c_credit = float(p * k.sum())
        c_max = float(p * k.max())
        newcov = np.minimum(1.0, p * k)
        dG = float(-np.sum(np.maximum(0.0, newcov - self.best[idx])))
        return self._apply(t.T, t.S, t.M, t.G, c_credit, p, c_max, dG)

    def gain_move(self, j: int, y: int, x: int) -> float:
        """Exact dDTI of moving dot j to (y, x). Mass, count and S preserved."""
        t = self.totals()
        pj = self.p[j]
        new_idx, nd = self._ball(y, x)
        affected = set(np.asarray(self.dot_truth[j]).tolist()) | set(new_idx.tolist())

        dT = -pj * self.dot_credit[j]
        dM = -pj * self.dot_max[j]
        if len(new_idx):
            k = kernel(nd)
            dT += pj * float(k.sum())
            dM += pj * float(k.max())
            newmap = {int(g): float(kk) for g, kk in zip(new_idx, k)}
        else:
            newmap = {}

        dG = 0.0
        for g in affected:
            others = self._cover[g] - {j}
            cov_other = max((min(1.0, self.p[m] * self._kg(m, g)) for m in others), default=0.0)
            cov_new = min(1.0, pj * newmap[g]) if g in newmap else 0.0
            dG += float(min(1.0, self.best[g]) - min(1.0, max(cov_other, cov_new)))
        return self._apply(t.T, t.S, t.M, t.G, dT, 0.0, dM, dG)

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
