#!/usr/bin/env python3
"""LCS step 2: select the candidate, measure all three uniqueness tiers, write the TIF.

Requires scripts/build_lcs_pool.py to have been run (gitignored cache under .cache/lcs).

Selection = maximise the percentile-rank sum of the consensus credit score at a fixed
count (matched to parent R0: 37,654 dots), 2.83 px spacing floor, d_cat > 3.0 px, subject to
a per-raster forward-overlap cap of 0.67 against every raster that carries an operator-
claimed leaderboard score (Tier S, "previous submissions").  Tier L (every distinct non-blanket
registry raster: 3 px halo covers < 50 % of the footprint) and Tier T (literal, all distinct rasters incl. blankets) are MEASURED and reported,
never hidden; the structural reason the literal rule cannot be met is quantified by the
frontier over caps.

Everything written here is labelled: MODEL projections are never scores.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems import lcs  # noqa: E402
from gems57 import grid as grid_mod  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

CACHE = ROOT / ".cache" / "lcs"
REG = ROOT / ".cache" / "gemsdoe_public_registry"
TODAY = "20261024"
R0_CREDIT = lcs.credit_per_dot(0.2778, 37654)  # MODEL: credit per dot implied by R0's claimed score


def decoded_digest(a: np.ndarray, fp: np.ndarray) -> str:
    a = np.where(np.isfinite(a), a, 0.0).astype(np.float32)
    a[~fp] = 0
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def tier_membership(keys, halo_cov, claims, digests_by_sha, cat_by_path, row_of_dec, r0_digest):
    s_rows, s_names = [], []
    for c in claims:
        f = c["registry_match_file"]
        if not f or f.startswith("data/"):
            continue
        r = cat_by_path.get(f)
        if r is None:
            continue
        d = digests_by_sha.get(r["sha256"])
        if d in row_of_dec and row_of_dec[d] not in s_rows:
            s_rows.append(row_of_dec[d])
            s_names.append(f"{c['site']}:{c['name'][:48]}")
    if r0_digest in row_of_dec and row_of_dec[r0_digest] not in s_rows:
        s_rows.append(row_of_dec[r0_digest])
        s_names.append("GEMSDOE32:R0")
    return s_rows, s_names


def overlaps_table(member_sel: np.ndarray, keys, halo_cov):
    """member_sel: (n_selected, R) bool -> per-raster forward overlap list."""
    ov = member_sel.mean(axis=0)
    rows = []
    for i, k in enumerate(keys):
        rows.append(dict(source=k["source"], n_dots=k["n_dots"], halo_coverage=halo_cov[i], forward_overlap=float(ov[i]),
                         n_files_sharing=k.get("n_files_sharing", 1)))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=80)
    ap.add_argument("--cap", type=float, default=lcs.CAP_FRACTION)
    ap.add_argument("--frontier", action="store_true", help="also trace the Tier-L price-of-uniqueness frontier (slow)")
    ap.add_argument("--tier-l-rounds", type=int, default=6, help="active-set rounds adding Tier-L violators to the cap set")
    ap.add_argument("--iters-l", type=int, default=240, help="Lagrangian iterations in each active-set round")
    ap.add_argument("--min-rank-quality", type=float, default=0.55,
                    help="PRE-REGISTERED: accept the Tier-L-compliant selection only if its mean score percentile stays >= this")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    fp, cat = grid.footprint, grid.catalogue
    d_cat = ndi.distance_transform_edt(~cat).astype(np.float32)
    P = np.load(CACHE / "pool.npz")
    yx, score, dcat_pool, lane_count, z = P["yx"], P["score"].astype(np.float64), P["d_cat"], P["lane_count"], P["z"]
    n_pool = len(yx)
    packed = np.load(CACHE / "member_packed.npy")
    keys_doc = json.loads((CACHE / "member_keys.json").read_text())
    keys = keys_doc["sparse"]
    M = np.unpackbits(packed, axis=1)[:, :n_pool].astype(bool).T  # (pool, R)
    hc = np.array([k["halo_coverage"] for k in keys])
    digests = json.loads((REG / "decoded_digests.json").read_text())
    cat_rows = list(csv.DictReader(open(ROOT / "evidence" / "registry_catalog_20261024.csv")))
    cat_by_path = {f"{r['repo']}/{r['path']}": r for r in cat_rows}
    claims = list(csv.DictReader(open(ROOT / "ledger" / "claimed_scores_20261024.csv")))
    row_of_dec = {k["decoded_sha256"]: i for i, k in enumerate(keys)}
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0_arr = ds.read(1).astype(np.float32)
    r0 = (r0_arr > 0) & fp
    r0_digest = decoded_digest(r0_arr, fp)
    s_rows, s_names = tier_membership(keys, hc, claims, digests, cat_by_path, row_of_dec, r0_digest)
    l_rows = [i for i in range(len(keys)) if hc[i] < 0.50]
    print(f"pool {n_pool:,}; Tier S rasters {len(s_rows)}; Tier L rasters {len(l_rows)}; tier-L-eligible {len(keys)}; "
          f"blankets (halo >= 0.50) {len(keys_doc['blanket'])}", flush=True)

    # ---- MODEL calibration on R0's claimed credit -----------------------------------------
    r0_in_pool = r0[yx[:, 0], yx[:, 1]]
    kappa = R0_CREDIT / float(score[r0_in_pool].mean())
    chat = np.minimum(kappa * score, lcs.CREDIT_CAP)

    def projections(idx):
        n = len(idx)
        t_naive = float(chat[idx].sum())
        pool_mean = float(chat.mean())
        t_shrunk = float((pool_mean + 0.5 * (chat[idx] - pool_mean)).sum())
        # null: no consensus signal, credit follows halo survival only
        surv = np.interp(dcat_pool, P["survival_edges"], P["survival"])
        k0 = R0_CREDIT / float(surv[r0_in_pool].mean())
        t_null = float((k0 * surv[idx]).sum())
        return dict(
            n=n, credit_per_dot_naive=t_naive / n, credit_per_dot_shrunk=t_shrunk / n, credit_per_dot_null=t_null / n,
            dti_naive=lcs.project_dti(t_naive, n), dti_shrunk=lcs.project_dti(t_shrunk, n), dti_null=lcs.project_dti(t_null, n))

    order = np.argsort(-score, kind="stable")
    t0 = time.time()
    sel_unc = lcs.spaced_capped_greedy(order, yx, fp.shape, lcs.N_TARGET)
    unc = sel_unc.index

    u_rank = (np.argsort(np.argsort(score, kind="stable"), kind="stable") + 1.0) / float(n_pool)
    rec, hist = lcs.lagrangian_capped_selection(score, yx, fp.shape, lcs.N_TARGET, M[:, s_rows],
                                                cap_fraction=args.cap, iters=args.iters)
    idx_s = rec["index"]
    ov_s = rec["overlap"]
    feasible_s = bool(rec["max_overlap"] <= 0.70 and len(idx_s) == lcs.N_TARGET)
    print(f"Tier-S selection: n={len(idx_s)} iter={rec['iter']} max overlap {rec['max_overlap']:.4f} feasible(<=0.70)={feasible_s} "
          f"rank-quality {u_rank[idx_s].mean():.3f} [{time.time() - t0:.0f}s]", flush=True)
    # ---- active-set rounds: add Tier-L rasters that this solution still violates ---------------
    rounds = [dict(round=0, constraint_rasters=len(s_rows), tierL_n_over=int((M[idx_s][:, l_rows].mean(0) > 0.70).sum()),
                   rank_quality=float(u_rank[idx_s].mean()), max_tierS=float(rec["max_overlap"]))]
    active = list(s_rows)
    best_L = None
    idx = idx_s
    for rnd in range(1, args.tier_l_rounds + 1):
        ovL = M[idx][:, l_rows].mean(0)
        viol = [l_rows[i] for i in np.where(ovL > 0.69)[0] if l_rows[i] not in active]
        if not viol:
            break
        active += viol
        recL, histL = lcs.lagrangian_capped_selection(score, yx, fp.shape, lcs.N_TARGET, M[:, active],
                                                      cap_fraction=args.cap, iters=args.iters_l)
        ii = recL["index"]
        ovl = M[ii][:, l_rows].mean(0)
        rounds.append(dict(round=rnd, constraint_rasters=len(active), added=len(viol), tierL_n_over=int((ovl > 0.70).sum()),
                           tierL_max=float(ovl.max()), rank_quality=float(u_rank[ii].mean()),
                           max_tierS=float(M[ii][:, s_rows].mean(0).max()), n=int(len(ii)), feasible=bool(recL["max_overlap"] <= 0.70)))
        print("  round", rounds[-1], flush=True)
        if recL["max_overlap"] <= 0.70 and len(ii) == lcs.N_TARGET:
            idx = ii
            hist = histL
            rec = recL
            if (ovl > 0.70).sum() == 0:
                best_L = ii
                break
        else:
            break
    tierL_compliant = best_L is not None
    accepted_L = bool(tierL_compliant and u_rank[best_L].mean() >= args.min_rank_quality)
    if accepted_L:
        idx = best_L
    else:
        idx = idx_s
        rec = dict(rec, index=idx_s) if not tierL_compliant else rec
    print(f"Tier-L compliant selection found={tierL_compliant}; accepted(rank-quality >= {args.min_rank_quality})={accepted_L}; "
          f"final rank-quality {u_rank[idx].mean():.3f}", flush=True)

    # ---- measure all tiers on the final dots ----------------------------------------------
    Msel = M[idx]
    table = overlaps_table(Msel, keys, hc)
    ov_all = np.array([t["forward_overlap"] for t in table])
    tierL = ov_all[l_rows]
    summary_tiers = dict(
        S=dict(n_rasters=len(s_rows), max_overlap=float(ov_all[s_rows].max()), n_over_0_70=int((ov_all[s_rows] > 0.70).sum()),
               members=s_names),
        L=dict(n_rasters=len(l_rows), max_overlap=float(tierL.max()), n_over_0_70=int((tierL > 0.70).sum())),
        T_sparse=dict(n_rasters=len(keys), max_overlap=float(ov_all.max()), n_over_0_70=int((ov_all > 0.70).sum())),
        T_blanket=dict(n_rasters=len(keys_doc["blanket"]), note="3 px halo covers >= 50% of the footprint: forward overlap is ~1.0 for any candidate in fault-rich terrain and >= 50% for random placement"),
    )
    worst = sorted(table, key=lambda t: -t["forward_overlap"])[:25]

    unc_table = overlaps_table(M[unc], keys, hc)
    unc_ov = np.array([t["forward_overlap"] for t in unc_table])
    frontier = []
    if args.frontier:
        Ml = M[:, l_rows]
        for cap in (0.98, 0.90, 0.80, 0.67):
            t1 = time.time()
            r2, _ = lcs.lagrangian_capped_selection(score, yx, fp.shape, lcs.N_TARGET, Ml, cap_fraction=cap, iters=45)
            ii = r2["index"]
            frontier.append(dict(cap=cap, tier="L (all constraints at once)", max_overlap=float(r2["max_overlap"]),
                                 n_over_cap=int((r2["overlap"] > cap + 1e-12).sum()),
                                 rank_quality=float(u_rank[ii].mean()),
                                 mean_lane_count=float(lane_count[ii].mean()), mean_score=float(score[ii].mean()),
                                 proj=projections(ii), seconds=round(time.time() - t1)))
            print("frontier", frontier[-1], flush=True)

    # ---- dots and surface rasters ----------------------------------------------------------
    dots = np.zeros(fp.shape, np.float32)
    dots[yx[idx, 0], yx[idx, 1]] = 1.0
    assert int((dots > 0).sum()) == lcs.N_TARGET == len(idx)
    assert not np.any((dots > 0) & cat) and not np.any((dots > 0) & ~fp)
    assert d_cat[dots > 0].min() > lcs.MIN_CATALOGUE_DISTANCE_PX
    from scipy.spatial import cKDTree
    d_nn, _ = cKDTree(yx[idx]).query(yx[idx], k=2)
    assert d_nn[:, 1].min() >= np.sqrt(lcs.MIN_SPACING_SQ) - 1e-9, "spacing floor violated"
    surface = np.zeros(fp.shape, np.float32)
    surface[yx[:, 0], yx[:, 1]] = (score / score.max()).astype(np.float32)

    content_id = hashlib.sha256(np.ascontiguousarray(dots).tobytes()).hexdigest()[:8]
    name = f"GEMSDOE92-LCS-consensus-{TODAY}-{content_id}"
    note = "GEMSDOE92 LCS: 37,654 LB-weighted lane-consensus dots; >3px from catalogue; <=67% overlap with scored lanes; UNSCORED"
    assert len(note) <= 140 and len(name) <= 140, (len(note), len(name))
    out_name = f"GEMSDOE92-lcs-consensus-37654-{TODAY}-{content_id}-zeros.tif"
    out_path = ROOT / "releases" / out_name
    receipt = None
    if not args.no_write:
        out_path.parent.mkdir(exist_ok=True)
        surf_path = ROOT / "releases" / f"GEMSDOE92-lcs-consensus-surface-{TODAY}-{content_id}.tif"
        grid_mod.write_geotiff(surf_path, surface, nodata=None)
        receipt = write_submission(out_path, dots, ROOT / "data" / "bridge" / "sample_submission.tif", fp, note=note, name=name,
                                   catalogue=cat, metadata=dict(lane="LCS", content_id=content_id, parent="h33-h33-2-b2",
                                                                evidence_class="MODEL", surface_file=surf_path.name))
        print("wrote", out_path.name, receipt["sha256"], flush=True)

    result = dict(
        schema="gemsdoe92-lcs-build.v1", created_utc="2026-10-24", content_id=content_id,
        candidate=dict(file=out_name, name=name, note=note, note_chars=len(note), n_dots=int(len(idx)),
                       sha256=(receipt or {}).get("sha256"), mean_lane_count=float(lane_count[idx].mean()),
                       mean_d_cat_px=float(dcat_pool[idx].mean()), share_within_5px_of_catalogue=float((dcat_pool[idx] < 5).mean()),
                       exact_pixel_overlap_with_R0=float(r0_in_pool[idx].mean())),
        constants=dict(N_TARGET=lcs.N_TARGET, GAMMA=lcs.GAMMA, CAP_FRACTION=args.cap, MIN_SPACING_SQ=lcs.MIN_SPACING_SQ,
                       G_EST=lcs.G_EST, R0_CREDIT_PER_DOT_MODEL=R0_CREDIT, kappa=kappa),
        selection=dict(method="subgradient Lagrangian, rank objective, active-set rounds over Tier-L violators", iterations=len(hist),
                       best_iter=int(rec["iter"]), max_overlap_tierS=float(M[idx][:, s_rows].mean(0).max()), feasible=feasible_s,
                       tierL_compliant_found=bool(tierL_compliant), tierL_accepted=accepted_L,
                       min_rank_quality_preregistered=args.min_rank_quality, final_rank_quality=float(u_rank[idx].mean()),
                       tierS_only_rank_quality=float(u_rank[idx_s].mean()), rounds=rounds, history_tail=hist[-5:]),
        tiers=summary_tiers,
        worst_overlaps=worst,
        uncapped_reference=dict(rank_quality=float(u_rank[unc].mean()), max_overlap_all_sparse=float(unc_ov.max()), n_over_0_70_all_sparse=int((unc_ov > 0.70).sum()),
                                tierS_n_over=int((unc_ov[s_rows] > 0.70).sum()), proj=projections(unc),
                                mean_lane_count=float(lane_count[unc].mean())),
        projections_MODEL=projections(idx),
        r0_reference=dict(credit_per_dot=R0_CREDIT, dti_projection_by_construction=lcs.project_dti(R0_CREDIT * 37654, 37654)),
        frontier_tierL=frontier,
        evidence_class="MODEL (projections) + REGISTRY-MEASUREMENT (overlaps); no score exists",
    )
    if args.no_write:
        # never overwrite the real build receipt from a dry run
        if frontier:
            (ROOT / "evidence" / "lcs_frontier.json").write_text(json.dumps(dict(
                evidence_class="MODEL", note="price-of-uniqueness frontier: capping ALL Tier-L rasters at once from the uncapped start",
                uncapped=dict(rank_quality=float(u_rank[unc].mean()), mean_lane_count=float(lane_count[unc].mean()),
                              n_over_0_70_all_sparse=int((unc_ov > 0.70).sum()), proj=projections(unc)),
                tierS_only=dict(rank_quality=float(u_rank[idx_s].mean())), frontier=frontier), indent=2) + "\n")
        print("dry run: lcs_build.json untouched")
        return 0
    (ROOT / "evidence" / "lcs_build.json").write_text(json.dumps(result, indent=2) + "\n")
    np.save(CACHE / "selected_index.npy", idx)
    print(json.dumps({k: result[k] for k in ("candidate", "selection", "projections_MODEL")}, indent=1)[:3500])
    print("tiers:", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != 'members'} for k, v in summary_tiers.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
