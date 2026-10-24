"""LCS lane: leaderboard-calibrated lane consensus (session 2026-10-24).

Hypothesis
----------
Independent detector lanes in the public GEMSDOE registry fire on faults for
*different physical reasons* (potential-field edges, gravity/magnetic worms,
topographic slope breaks, radon, strain, ...), so their false positives are
largely different non-fault mimics.  Where several lanes agree, the posterior
that a dot lands within the 300 m kernel of a new-fault pixel rises.  The
organizer-claimed leaderboard score of each lane gives an *empirical* weight
for its vote: its credit per dot, inverted from the official DTI algebra.

Evidence this is not a story (all in evidence/lb_concordance_*.json and
evidence/lcs_loo_calibration.json, reproducible with scripts/):

* Across 11 independent lanes, a lane's agreement with the OTHER lanes rank-
  correlates with its leaderboard-implied credit per dot (Spearman +0.75,
  permutation p = 0.005; +0.60 / p = 0.09 without the two SGMC lanes).
* Leave-one-lane-out prediction of credit per dot from consensus votes (final pool, d_cat > 3 px):
  Spearman +0.83 at gamma = 0.30 (null gamma = 0: -0.24); MAE 0.034 credit/dot at gamma = 0.30
  (0.017 at gamma = 0.75, 0.049 for the null).  The first prototype (d_cat > 2 px) had MAE 0.021 at 0.30;
  the shift is recorded in evidence/lcs_loo_calibration.json and IRREGULARITIES.md.

Mimic that consensus does NOT remove (stated, not hidden)
----------------------------------------------------------
* The geophysical expression of already-mapped faults.  Every lane's detector
  also fires on mapped faults' signatures, offset by 1-5 px; the scorer masks
  the catalogue pixels themselves (DrivenData forum thread 11516, staff reply
  2026-09-16), so a dot in that halo is penalised in full.  The live ladder
  confirms it: the 3,891 dots at exactly 1 px (+0.0108) and the 2,545 dots at
  1.41-2 px (+0.0070) behaved as zero-credit dots.  The model therefore
  multiplies the vote term by a halo-survival factor measured from the
  distance-to-catalogue enrichment of the H19-5 skeleton, and computes the vote
  excess *within* distance strata so catalogue proximity cannot masquerade as
  consensus.
* Range-front lithologic contacts and erosional escarpments that all
  potential-field lanes share.  Consensus cannot separate these from faults.

Everything here is pure array math; builders own file I/O and provenance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# ---- constants fixed BEFORE the build (no tuning on the candidate) ---------
G_EST = 12_500.0                 # |G|: truth pixels implied by the R0/SOLO/D2.8 removal ladder (MODEL, +-300)
KERNEL_INTEGRAL_PX2 = math.pi * 9.0 / 3.0   # integral of the 3 px triangular kernel over the plane
RADIUS_PX = 3.0
MIN_SPACING_SQ = 8               # R0 lineage floor: no pair closer than sqrt(8)=2.83 px
MIN_CATALOGUE_DISTANCE_PX = 3.0  # brief constraint 4 (= kernel radius): a NEW lane keeps every dot > 3 px from every mapped fault
STRATA_EDGES = (3.0, 4.0, 7.0, 12.0, 25.0, 1e9)
GAMMA = 0.30                     # minimiser of leave-one-lane-out MAE over {0,.15,.3,.5,.75,1}
CAP_FRACTION = 0.67              # per-raster forward-overlap cap (gate is 0.70; 3 pt margin)
N_TARGET = 37_654                # matched budget with parent R0
BREAK_EVEN_CREDIT = 0.056        # 0.2*DTI/(1-0.2*DTI): marginal credit per dot below which a dot lowers DTI
CREDIT_CAP = 1.0                 # no dot is credited more than one truth-pixel's worth in projections


def credit_per_dot(score: float, n_dots: int, g: float = G_EST) -> float:
    """Credit (weighted TP) per emitted dot implied by an organizer-claimed DTI.

    DTI = T / (0.2 T + 0.2 FP + 0.8 |G|) with FP = N - M, M ~ T/3  (each hit dot
    carries ~3 units of kernel-weighted truth for a line truth).  Inverting:
        T = (0.2 N + 0.8 |G|) / (1/DTI - 0.2 + 0.2/3).
    A MODEL quantity: the score is a CLAIM and |G| is inferred.
    """
    if not (0.0 < score < 1.0) or n_dots <= 0:
        raise ValueError("score must be in (0,1) and n_dots positive")
    t = (0.2 * n_dots + 0.8 * g) / (1.0 / score - 0.2 + 0.2 / 3.0)
    return t / n_dots


def random_dot_credit(footprint_px: int, g: float = G_EST) -> float:
    """Expected credit of one dot dropped uniformly at random in the footprint."""
    return (g / footprint_px) * KERNEL_INTEGRAL_PX2


def project_dti(t_credit: float, n_dots: int, g: float = G_EST) -> float:
    """MODEL projection of DTI from total credit T (never a score)."""
    m = t_credit / 3.0
    fp = max(n_dots - m, 0.0)
    return float(t_credit / (0.2 * t_credit + 0.2 * fp + 0.8 * g))


def dti_band_from_credit_error(mae_credit: float, n_dots: int = N_TARGET, g: float = G_EST,
                               base_score: float = 0.2778, base_n: int = 37654) -> float:
    """DTI change produced by one typical credit-per-dot model error, around the R0 operating point (MODEL)."""
    c0 = credit_per_dot(base_score, base_n, g)
    return float(project_dti((c0 + mae_credit) * n_dots, n_dots, g) - project_dti(c0 * n_dots, n_dots, g))


def halo_survival_profile(d_cat: np.ndarray, footprint: np.ndarray, skeleton: np.ndarray,
                          max_d: int = 40, background_from: float = 20.0):
    """Fraction of skeleton mass at distance d that is NOT a re-detection of a mapped fault.

    enrichment(d) = share of skeleton pixels at distance d / share of footprint
    pixels at distance d.  Far from the catalogue (d >= ``background_from``)
    enrichment settles at a background level b; the excess above b near the
    catalogue is the geophysical re-detection halo (zero credit: masked / not new).
    survival(d) = min(1, b / enrichment(d)).  Returns (edges, survival, b).
    """
    edges = np.arange(1, max_d + 1, 1.0)
    bins = np.r_[edges, 1e9]
    fpd = d_cat[footprint]
    skd = d_cat[skeleton & footprint]
    hf = np.histogram(fpd, bins=bins)[0].astype(float)
    hs = np.histogram(skd, bins=bins)[0].astype(float)
    enr = (hs / hs.sum()) / np.maximum(hf / hf.sum(), 1e-12)
    far = edges >= background_from
    b = float(np.mean(enr[:-1][far[:-1]]))
    padded = np.r_[enr[0], enr, enr[-1]]
    enr_s = np.convolve(padded, np.ones(3) / 3.0, "valid")
    surv = np.minimum(1.0, b / np.maximum(enr_s, 1e-9))
    return edges, surv, b


def lane_weights(credits: dict[str, float], c_random: float) -> dict[str, float]:
    """Vote weight = log enrichment of the lane's credit per dot over random placement (>= 0)."""
    return {k: float(max(math.log(max(c / c_random, 1.0)), 0.0)) for k, c in credits.items()}


def stratum_index(d_cat: np.ndarray, edges=STRATA_EDGES) -> np.ndarray:
    """Stratum id per pixel: 0..len(edges)-2 for d in (edges[k], edges[k+1]]; -1 below the first edge."""
    out = np.full(d_cat.shape, -1, dtype=np.int8)
    for k, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        out[(d_cat > lo) & (d_cat <= hi)] = k
    return out


def stratified_excess(votes: np.ndarray, strata: np.ndarray, pool: np.ndarray) -> np.ndarray:
    """votes - mean(votes over the pool within the same distance stratum), evaluated on ``pool``."""
    z = np.zeros(votes.shape, dtype=np.float32)
    for k in range(int(strata.max()) + 1):
        sel = pool & (strata == k)
        if sel.any():
            z[sel] = votes[sel] - votes[sel].mean()
    return z


def credit_score(z: np.ndarray, d_cat: np.ndarray, edges: np.ndarray, survival: np.ndarray,
                 gamma: float = GAMMA) -> np.ndarray:
    """Un-normalised expected-credit score: halo survival x exp(gamma * stratified vote excess)."""
    return np.interp(d_cat, edges, survival) * np.exp(gamma * z)


@dataclass
class Selection:
    index: np.ndarray            # indices into the candidate arrays, in acceptance order
    n_selected: int
    rejected_spacing: int
    rejected_cap: int
    cap_counts: np.ndarray       # final per-capped-raster counts
    caps: np.ndarray


def spaced_capped_greedy(order: np.ndarray, yx: np.ndarray, shape: tuple[int, int], n_target: int,
                         member: np.ndarray | None = None, cap: int | np.ndarray | None = None,
                         min_spacing_sq: int = MIN_SPACING_SQ) -> Selection:
    """Greedy acceptance in ``order`` with a hard spacing floor and per-raster halo caps.

    ``member`` is a boolean (n_candidates, n_rasters) matrix: candidate i lies within
    3 px of raster r's dots.  A candidate is accepted only if accepting it keeps
    every raster's halo count <= cap[r].  Deterministic; stops at ``n_target``.
    """
    h, w = shape
    pad = 3
    occ = np.zeros((h + 2 * pad, w + 2 * pad), dtype=bool)
    offs = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
            if dy * dy + dx * dx < min_spacing_sq and (dy, dx) != (0, 0)]
    oy = np.array([o[0] for o in offs]) + pad
    ox = np.array([o[1] for o in offs]) + pad
    if member is not None:
        n_r = member.shape[1]
        caps = np.full(n_r, int(cap), dtype=np.int64) if np.isscalar(cap) else np.asarray(cap, dtype=np.int64)
        counts = np.zeros(n_r, dtype=np.int64)
    else:
        caps = counts = np.zeros(0, dtype=np.int64)
    picked, rej_sp, rej_cap = [], 0, 0
    for i in order:
        y, x = int(yx[i, 0]), int(yx[i, 1])
        if occ[y + oy, x + ox].any() or occ[y + pad, x + pad]:
            rej_sp += 1
            continue
        if member is not None:
            row = member[i]
            if row.any() and np.any(counts[row] + 1 > caps[row]):
                rej_cap += 1
                continue
            counts[row] += 1
        occ[y + pad, x + pad] = True
        picked.append(int(i))
        if len(picked) >= n_target:
            break
    return Selection(index=np.asarray(picked, dtype=np.int64), n_selected=len(picked),
                     rejected_spacing=rej_sp, rejected_cap=rej_cap, cap_counts=counts, caps=caps)


def lagrangian_capped_selection(score: np.ndarray, yx: np.ndarray, shape: tuple[int, int], n_target: int,
                                member: np.ndarray, cap_fraction: float = CAP_FRACTION, iters: int = 60,
                                eta: float = 0.6, decay: float = 0.97):
    """Maximise rank-sum of ``score`` at fixed count under fractional per-raster overlap caps.

    Subgradient method on the Lagrangian
        L(S, mu) = sum_i u_i - sum_r mu_r * (|S ∩ H_r| - cap_fraction*|S|),   u = score percentile in [0,1].
    Every iteration solves the inner problem greedily (spacing floor, exact count) with adjusted values
    ``u_i - sum_r mu_r (M_ir - cap_fraction)`` and then moves mu_r by eta * (overlap_r - cap_fraction),
    clipped at 0.  Returns (best feasible else least-violating record, history).  Deterministic.
    """
    n_pool, n_r = member.shape
    u = (np.argsort(np.argsort(score, kind="stable"), kind="stable") + 1.0) / float(n_pool)
    mu = np.zeros(n_r, dtype=np.float64)
    mem_f = member.astype(np.float32)
    best_feasible, best_any, history = None, None, []
    for t in range(iters):
        adj = u - (mem_f - np.float32(cap_fraction)) @ mu.astype(np.float32) if mu.any() else u
        order = np.argsort(-adj, kind="stable")
        sel = spaced_capped_greedy(order, yx, shape, n_target)
        idx = sel.index
        ov = member[idx].mean(axis=0)
        worst = float(ov.max())
        feasible = worst <= cap_fraction + 1e-12 and sel.n_selected >= n_target
        total = float(u[idx].sum())
        history.append(dict(iter=t, n=int(sel.n_selected), max_overlap=worst, n_over=int((ov > cap_fraction + 1e-12).sum()),
                            n_active=int((mu > 0).sum()), rank_sum=total, feasible=bool(feasible)))
        rec = dict(index=idx, overlap=ov, rank_sum=total, max_overlap=worst, iter=t, mu=mu.copy())
        if feasible and (best_feasible is None or total > best_feasible["rank_sum"]):
            best_feasible = rec
        if best_any is None or (worst, -total) < (best_any["max_overlap"], -best_any["rank_sum"]):
            best_any = rec
        mu = np.maximum(0.0, mu + eta * (decay ** t) * (ov - cap_fraction))
    return (best_feasible or best_any), history
