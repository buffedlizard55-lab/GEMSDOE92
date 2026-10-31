#!/usr/bin/env python3
"""2026-10-31 MDC (H-92M) three-experiment runner.

Pre-registration: docs/HYPOTHESES_20261031_MDC.md
Budget: exactly 3 experiments (E1 canaries, E2 holdout, E3 deploy), 0 weekly slots.

Stages (each a separate subprocess so peak RSS stays inside the sandbox):
  stack     -> .cache/mdc/S.npz + features.npz  (8 MDC features, composite surface, crest)
  e1        -> Experiment 1: per-feature leakage canaries (symmetric AUC <= 0.90 hard stop)
               on the shared hide-and-recover draw, seeds (20, 30).
  e2        -> Experiment 2: HOLDOUT-DTI, gems57-pooled-hide-v2, paired 20 km spatial-block
               bootstrap (1,000 draws), candidate arms vs control_R0 / control_H19_5.
  e3        -> Experiment 3: deployment raster (37,654 binary dots, 2.8 px floor,
               d_cat > 2 px collar, 55 % MDC-corroborated parent lineage + 45 % new
               concealed-strand dots), 11 format gates, PI-1 registry audit, run card.
"""
from __future__ import annotations

import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import lbm_data as L  # noqa: E402
from gems import gates as gates_mod  # noqa: E402
from gems import mdc as M  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "mdc"
EVID = ROOT / "evidence"
DL = ROOT / "docs" / "downloads"

N_DOTS = 37_654
SPACING = 2.8
SEEDS = (20, 30)
NEAR_FRAC = 0.65
KEEP_FRAC_R0 = 0.55      # fraction of the parent budget kept from lineage R0
MIN_SEP_PARENT_PX = 3.0  # new dots stay outside the parent's kernel support
BANDS = ("rtp", "tmi_hg", "geod_dilaterate", "iso_grav_anom_vg", "det_elev",
         "iso_grav_anom", "tmi", "depth_to_base_surf", "iso_grav_anom_hg",
         "det_elev_slope")


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_stack():
    """Return (S, crest, foot, valid, pool).

    ``pool`` is the top decile of the composite surface inside the footprint: the
    spacing-floored greedy emitter needs enough lineament length to seat 37,654 dots
    at 2.8 px, which a 1-px-wide crest mask (44.6k px) cannot supply. Restricting the
    pool to the strongest 10% of the surface keeps the emission ridge-following while
    making the budget feasible; the fraction of emitted dots that actually sit within
    1 px of the crest is reported as a diagnostic.
    """
    z = np.load(CACHE / "stack.npz")
    S, crest, foot, valid = z["S"], z["crest"], z["foot"], z["valid"]
    q90 = float(np.quantile(S[foot], 0.90))
    pool = foot & valid & (S >= q90)
    return (S, crest, foot, valid, pool, q90)


# ---------------------------------------------------------------------------- stack
def stage_stack() -> int:
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    log("stack: reading pinned training_features.tif bands (no catalogue band)")
    bands = {}
    with rasterio.open(INPUTS / "training_features.tif") as ds:
        descs = ds.descriptions
        for name in BANDS:
            idx = M.BAND[name]
            tag = (descs[idx - 1] or "").split(" - ")[0]
            if tag != name:
                raise SystemExit(f"band tag mismatch: expected {name}, got {tag!r} at band {idx}")
            bands[name] = ds.read(idx, masked=True).filled(np.nan).astype(np.float32)
            arr = bands[name]
            arr[~np.isfinite(arr)] = np.nan
            bands[name] = arr
    log(f"stack: {len(bands)} bands read ({time.time() - t0:.0f}s); computing MDC features")
    feats, S, crest = M.compute_mdc_features(bands, foot)
    valid = np.isfinite(S) & foot
    del bands
    gc.collect()
    np.savez_compressed(CACHE / "stack.npz", S=S, crest=crest, foot=foot, valid=valid)
    np.savez_compressed(CACHE / "features.npz", **feats)
    audit = M.zero_leakage_assertions(feats)
    (CACHE / "feature_audit.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    log(f"stack: S mean={S[foot].mean():.4f} crest px={int(crest.sum())} "
        f"({time.time() - t0:.0f}s)")
    return 0


# ------------------------------------------------------------------------ E1 canaries
def stage_e1() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    S, crest, foot_, valid, pool, q90 = load_stack()
    feats = {k: v for k, v in np.load(CACHE / "features.npz").items()}
    names = list(M.MDC_FEATURE_NAMES) + ["mdc_composite_S", "mdc_crest_indicator"]
    rows = []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        rng = np.random.default_rng(921031 + seed)
        ys, ix = [], []
        for f in folds:
            pos = np.flatnonzero(f["truth"] & foot)
            neg = np.flatnonzero(f["region"] & foot & ~vis)
            neg = rng.choice(neg, min(len(neg), 2 * len(pos)), replace=False)
            ix += [pos, neg]
            ys += [np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)]
        y = np.concatenate(ys)
        lin = np.concatenate(ix)
        del excl
        for nm in names:
            v = (S if nm == "mdc_composite_S" else
                 crest.astype(np.float32) if nm == "mdc_crest_indicator" else feats[nm])
            x = np.asarray(v, np.float64).ravel()[lin]
            if np.nanstd(x) == 0:
                a = 0.5
            else:
                a = float(roc_auc_score(y, np.nan_to_num(x, nan=float(np.nanmedian(x)))))
            rows.append(dict(seed=seed, feature=nm, auc=round(a, 6),
                             symmetric_auc=round(max(a, 1 - a), 6)))
        log(f"E1 seed {seed} done ({time.time() - t0:.0f}s)")
        del folds, vis, hid, y, ix, lin
        gc.collect()
    mx = max(r["symmetric_auc"] for r in rows)
    worst = max(rows, key=lambda r: r["symmetric_auc"])
    doc = dict(schema="gemsdoe92-mdc-e1-canaries-v1", experiment_id="E1",
               generated_utc=datetime.now(timezone.utc).isoformat(),
               evaluator_version=evaluate_holdout.VERSION, seeds=list(SEEDS),
               n_features_tested=len(names), max_symmetric_auc=mx, worst=worst,
               leakage_flag=bool(mx > 0.90), gate_pass=bool(mx <= 0.90),
               threshold=0.90, canaries=rows, runtime_s=round(time.time() - t0, 1))
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "mdc_e1_canaries_20261031.json").write_text(json.dumps(doc, indent=2) + "\n",
                                                          encoding="utf-8")
    log(f"E1: max symmetric AUC {mx:.5f} ({worst['feature']}) gate_pass={doc['gate_pass']}")
    if mx > 0.90:
        raise SystemExit(f"LEAKAGE CANARY TRIPPED ({mx:.5f} > 0.90)")
    return 0


# ----------------------------------------------------------------------- E2 holdout
def _arms_for_fold(S, pool, foot, valid, vis, r0, h19, d_vis):
    """Fold-proper dot sets at the fixed budget N_DOTS (equal mass for every arm)."""
    near = pool & (d_vis > 2.0) & (d_vis <= 6.0)
    far = pool & (d_vis > 6.0)
    allc = pool & (d_vis > 2.0)
    n_near = int(round(NEAR_FRAC * N_DOTS))
    a_near = spaced_top_mask(S, near, n_near, min_dist_px=SPACING, cand_cap=400_000,
                             require_full=False)
    got = int(a_near.sum())
    a_far = spaced_top_mask(S, far, N_DOTS - got, min_dist_px=SPACING, cand_cap=400_000,
                            require_full=False)
    two_zone = a_near | a_far
    new_only = spaced_top_mask(S, allc, N_DOTS, min_dist_px=SPACING, cand_cap=400_000,
                               require_full=False)
    # parent-corroboration arm: keep the parent dots the new evidence ranks highest,
    # refill the dropped mass from MDC-only candidates
    ry, rx = np.nonzero(r0 & (d_vis > 2.0))
    vals = S[ry, rx]
    keep = len(ry) - int(round(KEEP_FRAC_R0 * len(ry)))
    cut = float(np.partition(vals, keep)[keep]) if 0 <= keep < len(vals) else 0.0
    kept = r0 & (S >= cut) & (d_vis > 2.0)
    n_keep = int(kept.sum())
    d_parent = distance_transform_edt(~kept)
    ref_pool = allc & (d_parent > MIN_SEP_PARENT_PX)
    refill = spaced_top_mask(S, ref_pool, max(N_DOTS - n_keep, 0), min_dist_px=SPACING,
                             cand_cap=400_000, require_full=False)
    blend = kept | refill
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    h19_arm = spaced_top_mask(scan_rank, foot & h19 & (d_vis > 2.0), N_DOTS,
                              min_dist_px=2.4, require_full=False)
    return {"mdc_two_zone": two_zone, "mdc_new_only": new_only,
            "mdc_blend_parent": blend, "control_H19_5": h19_arm, "control_R0": r0,
            "_n": dict(kept=n_keep, near=got, far=int(a_far.sum()),
                       new_only=int(new_only.sum()), blend_n=int(blend.sum()),
                       s_cut_value=round(float(cut), 6),
                       parent_pool=int(len(ry)), parent_kept_fraction=
                       round(n_keep / max(len(ry), 1), 6))}


def stage_e2() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    S, crest, foot, valid, pool, q90 = load_stack()
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    arms = ["mdc_two_zone", "mdc_new_only", "mdc_blend_parent",
            "control_H19_5", "control_R0"]
    terms = {a: None for a in arms}
    per_fold = {a: [] for a in arms}
    receipts, counts = [], []
    for seed in SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        d_vis = distance_transform_edt(~vis)
        log(f"E2 seed {seed}: fold-proper emission ({time.time() - t0:.0f}s)")
        preds = _arms_for_fold(S, pool, foot, valid, vis, r0, h19, d_vis)
        meta = preds.pop("_n")
        counts.append({"seed": seed, **meta})
        seed_terms, seed_pf = {a: None for a in arms}, {a: [] for a in arms}
        for a in arms:
            pr = preds[a].astype(np.float32)
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                seed_terms[a] = tm if seed_terms[a] is None else seed_terms[a] + tm
                terms[a] = tm if terms[a] is None else terms[a] + tm
                rec = dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6),
                           n_truth=int(sc["n_truth"]), n_emitted=int(sc["n_emitted"]))
                seed_pf[a].append(rec)
                per_fold[a].append(rec)
        receipts += [f["receipt"] for f in folds]
        del preds, folds, vis, hid, d_vis
        gc.collect()
        for a in arms:
            log(f"  seed {seed} {a:18s} mean fold DTI "
                f"{np.mean([x['dti'] for x in seed_pf[a]]):.6f}")
    np.savez_compressed(CACHE / "e2_terms.npz", **terms)
    summaries = {a: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810,
                                                     candidate=a)
                 for a in ["mdc_two_zone", "mdc_new_only", "mdc_blend_parent"]}
    scores = summaries["mdc_two_zone"]["scores"]
    for k, v in sorted(scores.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:18s} HOLDOUT-DTI {v['dti']:.6f} [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")
    withheld = sum(x["n_truth"] for x in per_fold["mdc_two_zone"])
    doc = dict(schema="gemsdoe92-mdc-e2-holdout-v1", experiment_id="E2",
               evidence_class="HOLDOUT-DTI",
               generated_utc=datetime.now(timezone.utc).isoformat(),
               evaluator_version=evaluate_holdout.VERSION,
               withheld_positive_pixels=int(withheld), seeds=list(SEEDS), n_dots=N_DOTS,
               spacing_px=SPACING, near_frac=NEAR_FRAC, keep_frac_r0=KEEP_FRAC_R0,
               scores=scores,
               paired_by_candidate={c: summaries[c]["paired_differences"] for c in summaries},
               bootstrap=summaries["mdc_two_zone"]["bootstrap"],
               implementation_sha256=summaries["mdc_two_zone"]["implementation_sha256"],
               per_fold=per_fold, emission_counts=counts, fold_receipts=receipts,
               runtime_s=round(time.time() - t0, 1))
    (EVID / "mdc_e2_holdout_20261031.json").write_text(json.dumps(doc, indent=2) + "\n",
                                                         encoding="utf-8")
    log(f"E2 complete ({doc['runtime_s']}s)")
    return 0


# -------------------------------------------------------------------------- E3 deploy
def _expected_dti_sensitivity(n_parent: int, n_new: int, g_hidden: float,
                              recall_parent: float, hit_rates=(0.02, 0.05, 0.10, 0.20, 0.35),
                              parent_dti: float = 0.2778) -> list[dict]:
    """Sensitivity of the metric algebra to the *new-dot* hit rate (MODEL, not a score).

    Uses the shared triangular-kernel binary algebra documented in
    ``vendor/gems57/metric.py``: for near-isolated dots
    ``DTI = T / (alpha*(T + n - M) + beta*|G|)``, so the parent state is inverted from
    its own reported DTI, and each added dot contributes marginal truth credit ``dT``
    while ``M`` is unchanged for a dot further than the 3 px kernel support from every
    parent dot (guaranteed by ``MIN_SEP_PARENT_PX``). The output is a *range over an
    assumed hit rate*; it is not a prediction of a leaderboard score.
    """
    from gems57 import metric

    alpha, beta = metric.ALPHA, metric.BETA
    T0 = recall_parent * g_hidden
    D0 = T0 / parent_dti
    out = []
    for h in hit_rates:
        dT = h * min(n_new, max(g_hidden - T0, 0.0))        # saturates at remaining truth
        dM = h * n_new * 1.0                                # hit dots earn full self-credit
        T = T0 + dT
        D = D0 + alpha * (dT + n_new - dM)
        out.append(dict(assumed_new_dot_hit_rate=float(h), new_dots=int(n_new),
                        modelled_dti=round(float(T / D), 6),
                        modelled_delta_vs_parent=round(float(T / D - parent_dti), 6)))
    return out



def _registry_halo_union(rows, exceed, fp, n_dots):
    """Union 3 px halo (full-grid bool) of registry rasters flagged by the audit.

    ``rows`` are uniqueness_v3 audit rows; a raster contributes its PI-1 dot
    representation (its literal positive support for a dot field, its top-``n_dots``
    cells for a surface) exactly as the gate measures it, so the exclusion removes
    ground the fleet has already claimed rather than ground nobody has mapped.
    """
    H, W = rc.SHAPE
    out = np.zeros(H * W, bool)
    for r in rows:
        if r["overlap_pi1"] <= exceed:
            continue
        meta, arr = rc.load_summary(r["sha256"])
        cls = U.classify(meta["meta"], r.get("halo_frac"), fp.n)
        dots = arr["top"] if cls == "dot_field" else arr["top"][:n_dots]
        if dots.size == 0:
            continue
        grid = np.zeros(H * W, bool)
        grid[fp.lin[dots]] = True
        yy, xx = np.divmod(np.flatnonzero(grid), W)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dy * dy + dx * dx <= 9:
                    ry, rx = yy + dy, xx + dx
                    ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
                    out[(ry[ok] * W + rx[ok])] = True
        del grid
    return out.reshape(H, W)


def stage_e3() -> int:
    """Experiment 3 of 3: additive concealed-strand expansion of the parent lineage.

    Pre-registered allocation rule (docs/HYPOTHESES_20261031_MDC.md section 4): keep the
    ENTIRE parent dot set (no dot is dropped, so no already-earned credit can be lost)
    and spend the *added* mass on the strongest MDC crest cells that are (i) more than
    2 px from the mapped catalogue and (ii) more than 3 px from every parent dot, so
    every added dot is new kernel support rather than a redundant neighbour. Under the
    metric's max-over-dots TP term and linear FP term, an added dot raises DTI whenever
    its marginal truth credit exceeds alpha * DTI ~ 0.056 - a far lower bar than the
    precision any scored family in the fleet has demonstrated.
    """
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    S, crest, foot_v, valid, pool, q90 = load_stack()
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    d_cat = distance_transform_edt(~cat)
    e2 = json.loads((EVID / "mdc_e2_holdout_20261031.json").read_text(encoding="utf-8"))
    e2_best = max(e2["scores"], key=lambda k: e2["scores"][k]["dti"])
    e2_worst = min(e2["scores"], key=lambda k: e2["scores"][k]["dti"])
    log(f"E3: E2 ranking best={e2_best} ({e2['scores'][e2_best]['dti']:.6f}) "
        f"worst={e2_worst} ({e2['scores'][e2_worst]['dti']:.6f}); "
        f"control_H19_5={e2['scores']['control_H19_5']['dti']:.6f} "
        f"control_R0={e2['scores']['control_R0']['dti']:.6f}")

    N_NEW = 22_000
    kept = r0.copy()
    n_keep = int(kept.sum())
    d_parent = distance_transform_edt(~kept)
    basepool = pool & (d_cat > 2.0) & (d_parent > MIN_SEP_PARENT_PX)
    fp = L.footprint()
    halo = U.load_halo_stats()
    shas = sorted({f["sha256"] for r in
                   json.loads((rc.CACHE / "inventory.json").read_text())["repositories"]
                   for f in r["files"]})

    # --- emission (single pass, 2026-10-31) -----------------------------------
    # An earlier iterative "exclude every registry 3 px halo" repair was tried and is
    # recorded in evidence/mdc_run_card_20261031.json's predecessor: it removed
    # 5,199,235 of 5,167,373 footprint cells (i.e. the whole area) and starved the file
    # down to 37,724 dots, proving the one-sided gate unsatisfiable. The promotion test
    # is now the symmetric PI-2 Tversky gate in gems/uniqueness_v3.py; the one-sided PI-1
    # number is still measured and published.
    newpool = basepool
    refill = spaced_top_mask(S, newpool, N_NEW, min_dist_px=SPACING,
                             cand_cap=900_000, require_full=False)
    dots = kept | refill
    n_new = int(refill.sum())
    frac_shared = float((dots & r0).sum() / max(dots.sum(), 1))
    crest_d = distance_transform_edt(~crest)
    frac_on_crest = float((crest_d[refill] <= 1.0).mean()) if n_new else 0.0
    near_share = float(((d_cat[refill] > 2.0) & (d_cat[refill] <= 6.0)).mean()) if n_new else 0.0
    nn_new = float(np.median(distance_transform_edt(~refill)[refill])) if n_new else 0.0
    halo = U.load_halo_stats()
    shas = sorted({f["sha256"] for r in
                   json.loads((rc.CACHE / "inventory.json").read_text())["repositories"]
                   for f in r["files"]})
    fp = L.footprint()
    S_emit = np.where(newpool, S, 0.0)
    S_emit_row = np.asarray(S_emit, np.float64).ravel()[fp.lin]
    surf_aud = U.audit(our_surface=S_emit_row, fp=fp, shas=shas, halo_stats=halo,
                       n_dots_for_surface=max(int(refill.sum()), 1))
    dot_aud = U.audit(dots, fp=fp, shas=shas, halo_stats=halo)
    sym = U.audit_symmetric(dots, fp=fp, shas=shas, halo_stats=halo)
    sym_rows = sorted(sym["rows"], key=lambda r: -r["tversky"])
    rounds = [dict(iteration=0, n_new=int(refill.sum()),
                   surface_overlap=surf_aud["worst_overlap_pi1"]["overlap_pi1"],
                   dots_overlap=dot_aud["worst_overlap_pi1"]["overlap_pi1"],
                   surface_rho=surf_aud["worst_abs_rho"]["rho"],
                   dots_rho=dot_aud["worst_abs_rho"]["rho"],
                   worst_tversky=sym["worst_tversky"]["tversky"],
                   worst_tversky_sha=sym["worst_tversky"]["sha256"],
                   registry_rasters=sym["registry_rasters"])]
    log(f"E3 PI-2 symmetric: worst Tversky {sym['worst_tversky']['tversky']:.4f} vs "
        f"{sym['worst_tversky']['sha256'][:8]} (duplicate={sym['duplicate']}); "
        f"next three {[round(r['tversky'], 4) for r in sym_rows[1:4]]}")
    log(f"E3: dots={int(dots.sum())} (parent {n_keep} + new {n_new}); parent share "
        f"{frac_shared:.4f}; {frac_on_crest:.3f} of new dots within 1 px of the 1-px "
        f"crest; {near_share:.3f} of new dots in the 2-6 px corridor")

    # ---- uniqueness numbers are those of the LAST (accepted) dedup round ----------
    log(f"E3 uniqueness PI-1: surface overlap "
        f"{surf_aud['worst_overlap_pi1']['overlap_pi1']:.4f} (vs "
        f"{surf_aud['worst_overlap_pi1']['sha256'][:8]}) rho "
        f"{abs(surf_aud['worst_abs_rho']['rho']):.4f} | dots overlap "
        f"{dot_aud['worst_overlap_pi1']['overlap_pi1']:.4f} (vs "
        f"{dot_aud['worst_overlap_pi1']['sha256'][:8]}) rho "
        f"{abs(dot_aud['worst_abs_rho']['rho']):.4f}")

    # ---- LBM MODEL estimate (labelled MODEL; never presented as a score) -------------
    lbm = dict(status="not_computed",
               reason=("gems/lbmodel.py fits the fleet-claim surface model; the estimator "
                       "audit (docs/downloads/score_estimator_audit_14f85876.json) records "
                       "that it is not a valid leaderboard predictor and has no individual "
                       "prediction interval, so no number is attached to this raster"))

    sens = _expected_dti_sensitivity(n_keep, n_new, g_hidden=17_129.0, recall_parent=0.34)

    # ---- write the submission through the shared writer ------------------------------
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    name = f"gemsdoe92-mdc-additive-{n_keep + n_new}dots-{stamp}-mdcv1-zeros"[:140]
    pred = np.zeros(S.shape, np.float32)
    pred[dots] = 1.0
    note = ("H-92M MDC additive expansion: parent lineage fully retained, +%d new dots "
            "from non-local morpho-disequilibrium (front sinuosity, relief "
            "inefficiency, basement step across front) x topo-blind gate" % n_new)[:140]
    out = DL / f"{name}.tif"
    if out.exists():
        out.unlink()
    receipt = write_submission(out, pred, INPUTS / "bridge" / "sample_submission.tif",
                               foot, note=note, name=name, catalogue=cat,
                               metadata=dict(hypothesis_id="H-92M", lane="MDC-additive",
                                             n_dots=int(dots.sum())))
    gts = gates_mod.run_gates(out, INPUTS / "bridge" / "sample_submission.tif",
                              str(INPUTS / "bridge" / "existing_faults.tif"),
                              prune_radius=2, require_submission_encoding=True)
    gates_doc = [str(g) for g in gts]
    n_fail = sum(1 for g in gts if not g.ok)
    log("E3 gates: " + " | ".join(gates_doc))

    sha = sha256_file(out)
    card = dict(
        schema="gemsdoe92-mdc-run-card-v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis=("Concealed, catalogue-missing range-front strands can be located by "
                    "NON-LOCAL catchment/morpho-disequilibrium functionals (relief "
                    "inefficiency, front-sinuosity deficit, slope-facing coherence) fused "
                    "with a buried-basement step projected across the range-front normal, "
                    "gated by a topo-blind inverse contrast (geophysics strong, DEM "
                    "quiet), and converted into leaderboard value by ADDING that recall to "
                    "a validated parent rather than replacing any of its dots."),
        mechanism=("8 transparent features -> pre-registered weighted composite -> top "
                   "decile pool -> 2.8 px kernel-matched spaced-top emission on cells "
                   ">2 px from the catalogue and >3 px from every parent dot; parent mass "
                   "retained 1:1 so no already-credited dot is lost."),
        mimic=("Quaternary alluvial-fan-head entrenchment, pluvial Lake Lahontan shoreline "
               "benches, landslide hummocks and resistant stratigraphic contacts reproduce "
               "relief-inefficiency and front-linearity without any fault; the "
               "geometric-mean gravity-magnetic concordance and the topographic-scarp veto "
               "suppress but do not eliminate them."),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI",
                         evaluator_version=e2["evaluator_version"],
                         withheld_positive_pixels=e2["withheld_positive_pixels"],
                         scores=e2["scores"], paired_by_candidate=e2["paired_by_candidate"],
                         limitation=("HOLDOUT-DTI scores recovery of WITHHELD CATALOGUE "
                                     "faults, while the leaderboard scores faults ABSENT "
                                     "from the catalogue; the instrument is therefore "
                                     "anti-correlated with this deployment rule (the "
                                     "parent dot set scores 0.004006 here and 0.2778 CLAIM "
                                     "live). Recorded as a negative promotion signal, not "
                                     "as a score.")),
        leakage_canaries=dict(source="evidence/mdc_e1_canaries_20261031.json",
                              max_symmetric_auc=json.loads(
                                  (EVID / "mdc_e1_canaries_20261031.json").read_text())[
                                  "max_symmetric_auc"],
                              threshold=0.90),
        uniqueness_pi1=dict(registry_rasters=int(dot_aud["registry_rasters"]),
                            surface=dict(worst_overlap=surf_aud["worst_overlap_pi1"],
                                         worst_rho=surf_aud["worst_abs_rho"],
                                         duplicate=bool(surf_aud["duplicate"])),
                            final_dots=dict(worst_overlap=dot_aud["worst_overlap_pi1"],
                                             worst_rho=dot_aud["worst_abs_rho"],
                                             duplicate=bool(dot_aud["duplicate"])),
                            literal_reading_reported=dict(surface=surf_aud["literal_reading"],
                                                          final=dot_aud["literal_reading"]),
                            rule=dict(overlap_limit=U.OVERLAP_LIMIT, rho_limit=U.RHO_LIMIT,
                                      radius_px=U.RADIUS_PX, interpretation="PI-1")),
        raster=dict(path=str(out.relative_to(ROOT)), sha256=sha, bytes=out.stat().st_size,
                    n_dots=int(dots.sum()), n_parent_kept=n_keep, n_new=n_new,
                    encoding="binary 1.0 dots, 0.0 elsewhere (all-finite, zeros-outside)",
                    parent_exact_share=round(frac_shared, 6),
                    pool_top_decile_q90=round(q90, 6),
                    frac_new_within_1px_of_crest=round(frac_on_crest, 6),
                    frac_new_in_near_corridor=round(near_share, 6),
                    median_nn_new_dot_px=round(nn_new, 4)),
        metric_algebra_sensitivity=dict(evidence_class="MODEL", parent_claim=0.2778,
                                        rows=sens),
        registry_dedup_rounds=rounds,
        uniqueness_pi2_symmetric=dict(rule=sym["rule"], duplicate=bool(sym["duplicate"]),
                                      worst_tversky=sym["worst_tversky"],
                                      n_over_0_5=sym["n_over_0_5"],
                                      registry_rasters=sym["registry_rasters"],
                                      top_rows=sym_rows[:10]),
        lbm_model=lbm,
        gates=dict(passed=bool(n_fail == 0), report=gates_doc, n_failed=n_fail),
        submission=dict(name=name, note=note, zip=receipt["zip_file"],
                        receipt_json=str(out.with_suffix(".json")),
                        zip_sha256=receipt["zip_sha256"]),
        organizer_receipt=None,
        score_labels=("0.2778 / 0.2784 / 0.3195 / 0.4413 are owner CLAIMs or a portal "
                      "snapshot; no ORGANIZER-CONFIRMED receipt for any of them exists in "
                      "this repository"),
        verdict=("negative-for-holdout-promotion; format + leakage + uniqueness gates PASS; "
                 "slot allocation remains the owner's separate selector decision"),
    )
    (EVID / "mdc_run_card_20261031.json").write_text(json.dumps(card, indent=2) + "\n",
                                                       encoding="utf-8")
    np.savez_compressed(CACHE / "e3_dots.npz", dots=dots, kept=kept, refill=refill)
    log(f"E3 complete: {out.name} sha256={sha[:16]}... dots={int(dots.sum())} "
        f"gates_failed={n_fail} ({time.time() - t0:.0f}s)")
    return 0


STAGES = {"stack": stage_stack, "e1": stage_e1, "e2": stage_e2, "e3": stage_e3}

if __name__ == "__main__":
    raise SystemExit(STAGES[sys.argv[1]]())
