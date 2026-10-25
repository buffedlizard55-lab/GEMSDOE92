#!/usr/bin/env python3
"""BLINDFAULT lane driver: features -> canaries -> strict draw-blind LOQO holdout ->
full fit -> emission -> submission_writer -> local uniqueness -> run card.

Reuses, unmodified: gems57.holdout (buffered whole-component draws), gems57.evaluate_holdout
(pooled DTI, alpha 0.2 / beta 0.8 / 300 m triangular kernel), gems57.submission_writer,
gems.breakline.spaced_top_mask.  Pre-registration: docs/HYPOTHESES_20261025_BLINDFAULT.md.

Stages are cached in .cache/blindfault/ so a 3 GB sandbox can resume.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.ndimage import distance_transform_edt
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import blindfault as bf  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, submission_writer  # noqa: E402

CACHE = ROOT / ".cache" / "blindfault"
INPUTS = ROOT / ".cache" / "gems_inputs"
STACK = INPUTS / "training_features.tif"
EVIDENCE = ROOT / "evidence"
DOWNLOADS = ROOT / "docs" / "downloads"
DATE = "20261025"
N_DOTS = 37_654
SEEDS = (20, 30)
HOLDOUT_BEST = dict(lane="COULOMBLOQO standalone", dti=0.113316, ci=[0.100614, 0.127163],
                    source="evidence/coulomb_loqo_proxy_audit.json (same evaluator, seeds 20+30)")

ARMS = {
    "blind": dict(cols=tuple(range(12)), weighted=True),
    "blindflat": dict(cols=tuple(range(12)), weighted=False),
    "blindtopo": dict(cols=tuple(range(13)), weighted=True),
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_features(foot):
    f = CACHE / "features.npz"
    if f.is_file():
        z = np.load(f)
        return dict(valid=z["valid"], X_foot=z["X_foot"], names=list(z["names"]), conspicuity=z["conspicuity"])
    log("computing features (12 subsurface + 1 topo-ablation) ...")
    feats = bf.compute_features(STACK, foot)
    np.savez(f, valid=feats["valid"], X_foot=feats["X_foot"], names=np.array(feats["names"]),
             conspicuity=feats["conspicuity"])
    return feats


def canaries(feats, grid, draw20, foot):
    hidden = draw20[0]["hidden_all"]
    valid = feats["valid"]
    d_cat = distance_transform_edt(~grid.catalogue)
    far = foot & valid & (d_cat > 5.0)
    rng = np.random.default_rng(20261025)
    row = np.full(foot.shape, -1, np.int32); row[foot] = np.arange(int(foot.sum()))
    pos = row[hidden & valid]
    neg_all = row[far]
    neg = rng.choice(neg_all, size=min(200_000, neg_all.size), replace=False)
    y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
    out = []
    for j, name in enumerate(feats["names"]):
        x = np.concatenate([feats["X_foot"][pos, j], feats["X_foot"][neg, j]])
        auc = float(roc_auc_score(y, x))
        out.append(dict(feature=name, auc=round(auc, 6), symmetric_auc=round(max(auc, 1 - auc), 6),
                        pass_le_0p90=bool(max(auc, 1 - auc) <= 0.90)))
    # conspicuity itself, as the shift diagnostic (NOT a model feature)
    c = feats["conspicuity"]
    xc = np.concatenate([c[foot][pos], c[foot][neg]])
    auc = float(roc_auc_score(y, xc))
    out.append(dict(feature="conspicuity_weight_field(not_a_feature)", auc=round(auc, 6),
                    symmetric_auc=round(max(auc, 1 - auc), 6), pass_le_0p90=bool(max(auc, 1 - auc) <= 0.90)))
    return dict(n_pos=int(pos.size), n_neg=int(neg.size), withheld_seed=20, rows=out,
                max_symmetric_auc=max(r["symmetric_auc"] for r in out),
                all_pass=all(r["pass_le_0p90"] for r in out))


def low_conspicuity_fold(fold, c_field, keep_components):
    """Fold copy scoring only withheld components in `keep_components`; others masked out."""
    comp, _ = ndi.label(fold["hidden_all"], holdout.STRUCT3)
    keep = np.isin(comp, keep_components) & fold["hidden_all"]
    f = dict(fold)
    f["truth"] = fold["truth"] & keep
    f["masked_known"] = fold["masked_known"] | (fold["hidden_all"] & ~keep)
    return f


def low_tercile_components(draw, c_field):
    hidden = draw[0]["hidden_all"]
    comp, n = ndi.label(hidden, holdout.STRUCT3)
    idx = np.arange(1, n + 1)
    mean_c = ndi.mean(c_field, labels=comp, index=idx)
    cut = float(np.quantile(mean_c, 1.0 / 3.0))
    return idx[mean_c <= cut], cut


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="blind,blindflat,blindtopo")
    ap.add_argument("--skip-holdout", action="store_true")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    CACHE.mkdir(parents=True, exist_ok=True)

    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    quad = holdout.quadrant_ids(foot)
    feats = load_features(foot)
    valid = feats["valid"]
    X = feats["X_foot"]
    c_field = feats["conspicuity"]
    w_field = np.zeros(foot.shape, np.float32)
    w_field[valid] = bf.positive_weights(c_field[valid])
    d_cat = distance_transform_edt(~cat)
    log(f"features ready: X {X.shape}, valid={int(valid.sum())}, footprint={int(foot.sum())}")

    draws = {s: holdout.buffered_component_draw(grid, seed=s)[0] for s in SEEDS}
    receipts = {s: [f["receipt"] for f in draws[s]] for s in SEEDS}
    n_withheld = sum(r["withheld_positive_pixels"] for s in SEEDS for r in receipts[s])
    log(f"holdout draws: seeds {SEEDS}, withheld positives = {n_withheld}")

    can_path = CACHE / "canaries.json"
    if can_path.is_file():
        can = json.loads(can_path.read_text())
    else:
        can = canaries(feats, grid, draws[20], foot)
        can_path.write_text(json.dumps(can, indent=2))
    log(f"canaries: max symmetric AUC = {can['max_symmetric_auc']:.4f}, all_pass={can['all_pass']}")

    # H19-5 supervised reference under the same fold-visible emission rule
    with rasterio.open(ROOT / "data/bridge/h19_5.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)

    terms = {}          # arm -> pooled terms (primary instrument, d_visible > 2)
    terms_low = {}      # arm -> pooled terms on low-conspicuity withheld components
    static_terms = {}   # arm -> pooled terms, deployment raster (d_cat > 2) on all 8 folds
    low_cuts = {}

    if not args.skip_holdout:
        for s in SEEDS:
            draw = draws[s]
            vis = draw[0]["visible"]
            hidden = draw[0]["hidden_all"]
            collar = distance_transform_edt(~hidden) <= 3.0
            d_vis = distance_transform_edt(~vis)
            allowed_vis = foot & valid & (d_vis > 2.0)
            keep_comp, cut = low_tercile_components(draw, c_field)
            low_cuts[s] = dict(cut=cut, n_low_components=int(keep_comp.size))
            folds_low = [low_conspicuity_fold(f, c_field, keep_comp) for f in draw]

            # reference arm
            p_h19 = bf.spaced_top_mask(scan_rank, foot & valid & h19 & (d_vis > 2.0), N_DOTS, min_dist_px=2.4).astype(np.float32)
            p_h19[vis] = 0.0
            for f, fl in zip(draw, folds_low):
                _, t = evaluate_holdout.evaluate(p_h19, f, foot)
                terms["H19_5_dvis2"] = t if "H19_5_dvis2" not in terms else terms["H19_5_dvis2"] + t
                _, tl = evaluate_holdout.evaluate(p_h19, fl, foot)
                terms_low["H19_5_dvis2"] = tl if "H19_5_dvis2" not in terms_low else terms_low["H19_5_dvis2"] + tl

            for arm in arms:
                spec = ARMS[arm]
                sp = CACHE / f"S_{arm}_draw{s}.npy"
                if sp.is_file():
                    S = np.load(sp)
                else:
                    t0 = time.time()
                    S = bf.fit_predict_loqo_weighted(
                        X, foot, valid, quad, vis, feature_cols=spec["cols"],
                        pos_weight_field=w_field if spec["weighted"] else None,
                        excluded_mask=collar)
                    np.save(sp, S)
                    log(f"  {arm} draw-blind seed {s} fit in {time.time() - t0:.0f}s")
                pred = bf.emit_dots(S, allowed_vis, N_DOTS).astype(np.float32)
                pred[vis] = 0.0
                for f, fl in zip(draw, folds_low):
                    sc, t = evaluate_holdout.evaluate(pred, f, foot)
                    terms[arm] = t if arm not in terms else terms[arm] + t
                    _, tl = evaluate_holdout.evaluate(pred, fl, foot)
                    terms_low[arm] = tl if arm not in terms_low else terms_low[arm] + tl
                    log(f"  {arm} seed {s} fold {f['name']}: DTI {sc['dti']:.6f} (n_truth {sc['n_truth']})")
                del S, pred

    # Full fits -> deployment rasters
    results = {}
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    for arm in arms:
        spec = ARMS[arm]
        sp = CACHE / f"S_{arm}_full.npy"
        if sp.is_file():
            S = np.load(sp)
        else:
            t0 = time.time()
            S = bf.fit_predict_loqo_weighted(
                X, foot, valid, quad, cat, feature_cols=spec["cols"],
                pos_weight_field=w_field if spec["weighted"] else None)
            np.save(sp, S)
            log(f"  {arm} full LOQO fit in {time.time() - t0:.0f}s")
        dots = bf.emit_dots(S, foot & valid & (d_cat > 2.0), N_DOTS)
        assert not (dots & cat).any()
        pred = np.where(dots, 1.0, 0.0).astype(np.float32)
        # static reading, all 8 folds, same deployment raster (comparable to repo's static table)
        st = None
        for s in SEEDS:
            for f in draws[s]:
                _, t = evaluate_holdout.evaluate(pred, f, foot)
                st = t if st is None else st + t
        static_terms[arm] = st
        if "R0" not in static_terms:
            st0 = None
            for s in SEEDS:
                for f in draws[s]:
                    _, t = evaluate_holdout.evaluate(r0.astype(np.float32), f, foot)
                    st0 = t if st0 is None else st0 + t
            static_terms["R0"] = st0
        sha8 = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-blindfault-{arm}-{N_DOTS}-{DATE}-{sha8}-zeros"
        results[arm] = dict(stem=stem, dots=dots, pred=pred, S=S, sha8=sha8,
                            overlap_r0_3px=float((distance_transform_edt(~r0)[dots] <= 3.0).mean()),
                            frac_dots_low_conspicuity=float((c_field[dots] <= 1.0 / 3.0).mean()),
                            mean_conspicuity_dots=float(c_field[dots].mean()))
        log(f"  {arm}: dots={int(dots.sum())} sha8={sha8} overlap_R0={results[arm]['overlap_r0_3px']:.4f} "
            f"low-c frac={results[arm]['frac_dots_low_conspicuity']:.3f}")

    # Pooled summaries
    summary = {}
    if terms:
        cand = arms[0]
        pooled = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=cand)
        pooled_low = evaluate_holdout.pooled_summary(terms_low, draws=1000, seed=520810, candidate=cand)
        summary["primary_dvis2"] = pooled
        summary["low_conspicuity_tercile"] = pooled_low
        summary["low_conspicuity_cuts"] = low_cuts
        log("=== PRIMARY HOLDOUT-DTI (strict draw-blind LOQO, d_visible > 2.0) ===")
        for k, v in sorted(pooled["scores"].items(), key=lambda kv: -kv[1]["dti"]):
            log(f"   {k:14s} DTI {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")
        log("=== LOW-CONSPICUITY TERCILE HOLDOUT-DTI (mechanism instrument) ===")
        for k, v in sorted(pooled_low["scores"].items(), key=lambda kv: -kv[1]["dti"]):
            log(f"   {k:14s} DTI {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")
    pooled_static = evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=520810, candidate=arms[0])
    summary["static_dcat2_deployment"] = pooled_static
    log("=== STATIC HOLDOUT-DTI (deployment raster, d_cat > 2.0, 8 folds) ===")
    for k, v in sorted(pooled_static["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   {k:14s} DTI {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")

    out = dict(
        schema="gemsdoe92-blindfault-holdout.v1", lane="BLINDFAULT", date=DATE,
        evaluator_version=evaluate_holdout.VERSION,
        evaluator_hashes=evaluate_holdout.implementation_hashes(),
        split_receipts=receipts, withheld_positive_pixels=n_withheld,
        feature_names=feats["names"], arms={a: dict(cols=list(ARMS[a]["cols"]), weighted=ARMS[a]["weighted"]) for a in arms},
        leakage_canaries=can, holdout=summary, holdout_best_reference=HOLDOUT_BEST,
        deployment={a: {k: v for k, v in r.items() if k in ("stem", "sha8", "overlap_r0_3px",
                                                              "frac_dots_low_conspicuity", "mean_conspicuity_dots")}
                    for a, r in results.items()},
    )
    (EVIDENCE / "blindfault_holdout.json").write_text(json.dumps(out, indent=2) + "\n")
    for arm, r in results.items():
        np.save(CACHE / f"dots_{arm}.npy", r["dots"])
    log("WROTE evidence/blindfault_holdout.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
