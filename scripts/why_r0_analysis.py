#!/usr/bin/env python3
"""Recompute every number behind docs/WHY_R0_0_2778.md (MEASURED / CLAIM / MODEL kept distinct).

MEASURED  : set relations, distances to the catalogue, spacing - read from rasters.
CLAIM     : operator-reported leaderboard scores (ledger/claimed_scores_20261024.csv).
MODEL     : algebra of the official DTI:  DTI = T / (0.2 T + 0.2 FP + 0.8 FN'),  FN' = |G| - T.
            With FP = N - M (M ~ kernel-credit of the dots themselves, small) a removal of n dots that
            carry credit delta changes 1/DTI by  -0.2 n (1 - kbar) / T  (+ credit terms).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import lcs  # noqa: E402

REG = ROOT / ".cache" / "gemsdoe_public_registry"


def registry_file(substr):
    idx = json.loads((REG / "registry_index.json").read_text())
    hits = [r for r in idx["rasters"] if substr in r["sources"][0]]
    if not hits:
        raise FileNotFoundError(substr)
    return hits[0]["cache_file"]


def rd(p):
    with rasterio.open(p) as ds:
        return np.nan_to_num(ds.read(1), nan=0.0)


def main() -> int:
    cat = rd(ROOT / "data/bridge/existing_faults.tif") > 0
    d_cat = ndi.distance_transform_edt(~cat)
    R0 = rd(ROOT / "data/parent_R0_zeros.tif") > 0
    SOLO = rd(ROOT / "data/bridge/h27_4_solo.tif") > 0
    D28 = rd(ROOT / "data/bridge/d28.tif") > 0
    H195 = rd(ROOT / "data/bridge/h19_5.tif") > 0
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    out = dict(evidence_classes=dict(sets="MEASURED", scores="CLAIM", credit="MODEL"))

    chain = dict(R0=int(R0.sum()), SOLO=int(SOLO.sum()), D2_8=int(D28.sum()), H19_5=int(H195.sum()),
                 catalogue_px=int(cat.sum()), footprint_px=int(fp.sum()), grid_cells=int(fp.size),
                 R0_subset_SOLO=bool((R0 & ~SOLO).sum() == 0), SOLO_subset_D28=bool((SOLO & ~D28).sum() == 0),
                 D28_subset_H195=bool((D28 & ~H195).sum() == 0))
    g1, g2 = D28 & ~SOLO, SOLO & ~R0
    chain["group_D28_to_SOLO"] = dict(n=int(g1.sum()), d_cat_min=float(d_cat[g1].min()), d_cat_max=float(d_cat[g1].max()))
    chain["group_SOLO_to_R0"] = dict(n=int(g2.sum()), d_cat_min=float(d_cat[g2].min()), d_cat_max=float(d_cat[g2].max()),
                                     n_at_sqrt2=int(np.isclose(d_cat[g2], np.sqrt(2)).sum()), n_at_2=int(np.isclose(d_cat[g2], 2.0).sum()))
    yx = np.argwhere(R0)
    d, _ = cKDTree(yx).query(yx, k=2)
    chain["R0_min_nn_px"] = float(d[:, 1].min())
    chain["R0_median_nn_px"] = float(np.median(d[:, 1]))
    chain["R0_median_d_cat_px"] = float(np.median(d_cat[R0]))
    for r in (3, 4, 5):
        chain[f"R0_dots_within_{r}px_of_catalogue"] = int((d_cat[R0] <= r).sum())
    out["measured"] = chain

    # ---- ladder (CLAIM) and its algebra (MODEL) -------------------------------------------
    s = dict(H19_5=0.1922, D1_5=0.2477, D2_8=0.2600, SOLO=0.2708, R0=0.2778)
    n = dict(H19_5=121131, D1_5=60069, D2_8=44090, SOLO=40199, R0=37654)
    ladder = [dict(step=f"{a}->{b}", dots_removed=n[a] - n[b], delta=round(s[b] - s[a], 4)) for a, b in
              (("H19_5", "D1_5"), ("D1_5", "D2_8"), ("D2_8", "SOLO"), ("SOLO", "R0"))]
    out["ladder_CLAIM"] = ladder
    n1, n2 = chain["group_D28_to_SOLO"]["n"], chain["group_SOLO_to_R0"]["n"]
    t1 = 0.2 * n1 / (1 / s["D2_8"] - 1 / s["SOLO"])
    t2 = 0.2 * n2 / (1 / s["SOLO"] - 1 / s["R0"])
    # +-0.00005 rounding on each score -> propagate on the zero-credit T estimate
    def t_pair(n_, a, b, da=0.0, db=0.0):
        return 0.2 * n_ / (1 / (a + da) - 1 / (b + db))
    t1_rng = [t_pair(n1, s["D2_8"], s["SOLO"], da, db) for da in (-5e-5, 5e-5) for db in (-5e-5, 5e-5)]
    t2_rng = [t_pair(n2, s["SOLO"], s["R0"], da, db) for da in (-5e-5, 5e-5) for db in (-5e-5, 5e-5)]
    d_solo = t1 / s["SOLO"]
    ceiling = lambda T, D, dti: dti * 0.2 / D          # per-dot gain of removing a zero-credit FP=1 dot
    kbar = 0.03
    # credit delta2 that reconciles pair 2 with T from pair 1:  s_R0 = (T-d)/(D - 0.2 d - 0.2 n2 (1-kbar))
    delta2 = (t1 - s["R0"] * (d_solo - 0.2 * n2 * (1 - kbar))) / (1 - 0.2 * s["R0"])
    out["algebra_MODEL"] = dict(
        T_from_pair1_zero_credit=t1, T_from_pair2_zero_credit=t2, T_pair1_rounding_range=[min(t1_rng), max(t1_rng)],
        T_pair2_rounding_range=[min(t2_rng), max(t2_rng)], D_at_SOLO=d_solo,
        per_dot_gain_group1_observed=(s["SOLO"] - s["D2_8"]) / n1, per_dot_gain_group2_observed=(s["R0"] - s["SOLO"]) / n2,
        per_dot_gain_zero_credit_ceiling=ceiling(t1, d_solo, s["SOLO"]),
        group2_credit_units_implied=delta2, group2_credit_per_dot=delta2 / n2,
        interpretation="both flank groups behave as pure false positives (ceiling 2.9e-6/dot vs observed 2.78e-6 and 2.75e-6)")
    # ---- implied truth size / recall / precision (MODEL; |G| sensitivity) -------------------
    rows = []
    for g in (11000.0, 12500.0, 14000.0):
        c = lcs.credit_per_dot(s["R0"], n["R0"], g)
        rows.append(dict(G=g, T=c * n["R0"], credit_per_dot=c, recall=c * n["R0"] / g,
                         dti_check=lcs.project_dti(c * n["R0"], n["R0"], g)))
    out["R0_credit_vs_G_MODEL"] = rows
    out["random_dot_credit_MODEL"] = lcs.random_dot_credit(int(fp.sum()))
    out["break_even_credit_MODEL"] = lcs.BREAK_EVEN_CREDIT
    # ---- additive groups measured against R0 (CLAIM scores, MEASURED sets) ----------------------
    anderson = rd(registry_file("gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros")) > 0
    added = anderson & ~R0
    T_r0 = lcs.credit_per_dot(s["R0"], n["R0"]) * n["R0"]
    D_r0 = T_r0 / s["R0"]
    na = int(added.sum())
    k = 0.03
    # (T+delta)/(D+0.2 delta + 0.2 na (1-k)) = 0.2750
    sa = 0.2750
    delta = (sa * (D_r0 + 0.2 * na * (1 - k)) - T_r0) / (1 - 0.2 * sa)
    out["anderson_group_CLAIM_MEASURED_MODEL"] = dict(
        subset_relation_R0_in_anderson=bool((R0 & ~anderson).sum() == 0), n_added=na,
        score_change_CLAIM=sa - s["R0"], credit_units_implied=delta, credit_per_added_dot=delta / na,
        mean_d_cat_of_added_dots=float(d_cat[added].mean()),
        reading="added non-skeleton dots earned less than random placement (0.023/dot) - about half of random placement and ~5x below break-even")
    # ---- distance enrichment of the skeleton ------------------------------------------------------
    edges = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50, 100, 1e9]
    hf = np.histogram(d_cat[fp], bins=edges)[0].astype(float)
    hh = np.histogram(d_cat[H195 & fp], bins=edges)[0].astype(float)
    hr = np.histogram(d_cat[R0], bins=edges)[0].astype(float)
    out["enrichment_vs_footprint_MEASURED"] = [
        dict(d_lo=edges[i], d_hi=(edges[i + 1] if edges[i + 1] < 1e8 else None),
             H19_5=float((hh[i] / hh.sum()) / (hf[i] / hf.sum())), R0=float((hr[i] / hr.sum()) / (hf[i] / hf.sum())),
             footprint_share=float(hf[i] / hf.sum())) for i in range(len(edges) - 1)]
    # ---- leaderboard snapshot (fetched 2026-10-24 with fetch_page; not receipts) -----------------------
    out["leaderboard_snapshot_2026_10_24"] = dict(
        source="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/ (public page, top 50 only)",
        top=[0.4413, 0.3916, 0.3904, 0.3724, 0.3539, 0.3418, 0.3416, 0.3375, 0.3358, 0.3330],
        rank_20=0.3273, rank_30=0.3004, rank_40=0.2900, rank_47=0.2833, rank_50=0.2818,
        r0_claim=0.2778, r0_rank="outside the visible top 50 (below 0.2818)",
        note="the page lists 50 rows; R0's 0.2778 is a CLAIM and cannot be located on this page")
    outp = ROOT / "evidence" / "why_r0_20261024.json"
    outp.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("measured", "algebra_MODEL", "R0_credit_vs_G_MODEL", "anderson_group_CLAIM_MEASURED_MODEL")}, indent=1)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
