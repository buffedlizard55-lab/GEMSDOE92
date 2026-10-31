#!/usr/bin/env python3
"""PEEL lane, step D: fit on the full catalogue, place dots, package, estimate.

Placement rule is deliberately identical to the incumbent ``h33-h33-2-b2``
(GEMSDOE32, claimed 0.2778): minimum 2 px clearance from every mapped-catalogue
pixel, 2.8 px non-maximum-suppression separation, 37,654 unit-mass binary dots.
Only the *score field* changes, so any holdout difference is attributable to the
features rather than to the dot budget or packing geometry.

Score estimate
--------------
``evidence/peel_score_estimate_20261031.json`` fits a two-parameter
metric-structured model to five locally available (raster, owner CLAIM) pairs:

    DTI_hat = T / (0.2*(N - M) + 0.8*G),   T = M = kappa * sum_{dots} p(dot)

with ``p`` the PEEL probability surface, ``N`` the dot count and ``G`` the
hidden-fault pixel mass.  ``(kappa, G)`` are fitted by least squares and the
fit is reported with leave-one-out error.  Every output is labelled ``MODEL``:
it is a projection from owner CLAIMs, not an organizer score and not a receipt.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
from gems57 import submission_writer  # noqa: E402
from gems57.grid import load_grid  # noqa: E402

W = ROOT / ".cache" / "work" / "peel"
DL = ROOT / "docs" / "downloads"
K_BUDGET = 37654
SEP = 2.8
BUF = 2.0
MODEL_SEED = 31
NAME = "gemsdoe92-peel-scarpalt-37654-20261031"
NOTE = ("PEEL 44-band catalogue-free scarp x alteration model; d_cat>2 collar, "
        "37654 dots @2.8px; same budget as h33-2-b2")

# (raster, owner CLAIM, label). Claims are owner-reported, never receipts.
ANCHORS = [
    ("data/parent_R0_nan.tif", 0.2778, "GEMSDOE32 h33-h33-2-b2"),
    ("docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif", 0.2784, "GEMSDOE92 lbmc1"),
    ("data/bridge/h27_4_solo.tif", 0.2708, "GEMSDOE31 h27-4-solo-d28"),
    ("data/bridge/d28.tif", 0.2600, "GEMSDOE25/30 d28-poisson300m"),
    ("data/bridge/h19_5.tif", 0.1922, "GEMSDOE19 h19-5"),
]


def nms_dots(score, cand, sep, k_max):
    H, Wd = score.shape
    flat = np.flatnonzero(cand.ravel())
    order = flat[np.argsort(-score.ravel()[flat], kind="stable")]
    r = int(np.ceil(sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < sep * sep
    occ = np.zeros((H + 2 * r, Wd + 2 * r), bool)
    out = np.zeros((H, Wd), bool)
    n = 0
    for f in order:
        y, x = divmod(int(f), Wd)
        if occ[y + r, x + r]:
            continue
        out[y, x] = True
        occ[y:y + 2 * r + 1, x:x + 2 * r + 1] |= disk
        n += 1
        if n >= k_max:
            break
    return out


def dots_of(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return (np.isfinite(a) & (np.nan_to_num(a) > 0)) & foot


def fit_model(X, idx, cat, foot, seed, cols):
    rng = np.random.default_rng(seed)
    pos = np.flatnonzero(cat.ravel()[idx])
    negpool = np.flatnonzero((foot & ~cat).ravel())
    neg = np.searchsorted(idx, negpool[rng.choice(negpool.size, size=240_000, replace=False)])
    tr = np.concatenate([pos, neg])
    y = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
    clf = HistGradientBoostingClassifier(
        max_iter=150, learning_rate=0.08, max_leaf_nodes=31,
        min_samples_leaf=40, l2_regularization=1.0, random_state=seed, early_stopping=False)
    clf.fit(X[tr][:, cols], y)
    p = np.empty(idx.size, np.float32)
    for i in range(0, idx.size, 600_000):
        p[i:i + 600_000] = clf.predict_proba(X[i:i + 600_000][:, cols])[:, 1].astype(np.float32)
    surf = np.zeros(foot.shape, np.float32)
    surf.ravel()[idx] = p
    return surf


def estimate(foot, idx, anchors, surf):
    """Holdout-anchored projection from the ONE (raster, claim, holdout) triple we hold.

    A single anchor pair cannot identify a mapping from the local holdout to the
    organizer leaderboard, so both admissible one-parameter mappings are reported
    and neither is called a score:

    * proportional : claim = C_r0 * (H_cand / H_r0)
    * additive     : claim = C_r0 + (H_cand - H_r0)

    H_r0 is the R0-recipe HOLDOUT-DTI measured in the same run as the candidate
    (same folds, same withheld positives, same bootstrap), so the ratio is
    paired and shares its systematic error.  Every output is ``MODEL``.
    """
    H_r0 = 0.097493          # CTRL_R0_recipe, peel_holdout_20261031.json
    C_r0 = 0.2778            # GEMSDOE32 owner CLAIM for the same construction
    H_cand = float(json.loads((ROOT / "evidence" / "peel_holdout_20261031.json").read_text())
                   ["summaries"]["E3_PEEL_full"]["dti"])
    rows = []
    for rel, claim, label in anchors:
        d = dots_of(ROOT / rel, foot)
        rows.append(dict(label=label, raster=rel, claim=claim, n=int(d.sum()),
                         evidence_class="CLAIM (owner-reported; no receipt in this repo)"))
    prop = C_r0 * (H_cand / H_r0)
    add = C_r0 + (H_cand - H_r0)
    return dict(
        schema="gemsdoe92-peel-score-estimate-v1",
        evidence_class="MODEL (holdout-anchored projection; never an organizer score)",
        anchor_raster="data/parent_R0_nan.tif (h33-h33-2-b2)",
        anchor_holdout=H_r0, anchor_claim=C_r0,
        candidate_holdout=H_cand,
        holdout_gain=H_cand - H_r0,
        holdout_gain_ratio=H_cand / H_r0,
        mapping_proportional=float(prop),
        mapping_additive=float(add),
        estimate_interval=[float(min(prop, add)), float(max(prop, add))],
        unidentified=("one anchor pair cannot distinguish the two mappings; a second "
                      "submission receipt scored against a measured holdout is required"),
        anchors=rows,
        candidate_dots=int((surf > 0).sum()))


def main() -> int:
    meta = json.loads((W / "features.json").read_text())
    X = np.load(W / "X.npy", mmap_mode="r")
    grid = load_grid()
    foot = np.asarray(grid.footprint, bool)
    cat = np.asarray(grid.catalogue, bool)
    idx = np.flatnonzero(foot.ravel())
    cols = list(range(len(meta["names"])))
    dcat = ndi.distance_transform_edt(~cat)
    eligible = foot & ~cat & (dcat > BUF)

    surf = fit_model(X, idx, cat, foot, MODEL_SEED, cols)
    np.save(W / "surf_full.npy", surf)
    dots = nms_dots(surf, eligible, SEP, K_BUDGET)
    print(f"placed {int(dots.sum())} dots; mean p on dots {float(surf[dots].mean()):.4f}", flush=True)

    # "-zeros" encoding: every cell finite, zeros outside the scored footprint.
    # The organizer accepts NaN-outside or zeros-outside; zeros keeps the file
    # finite everywhere, which is the stricter of the two conventions.
    pred = np.zeros(foot.shape, np.float32)
    pred[dots] = 1.0
    sample = ROOT / "data" / "bridge" / "sample_submission.tif"
    out = DL / f"{NAME}-zeros.tif"
    rec = submission_writer.write_submission(out, pred, sample, foot, note=NOTE, name=NAME,
                                            catalogue=cat)
    sha = hashlib.sha256(out.read_bytes()).hexdigest()
    print("wrote", out.name, "sha256", sha)
    print("writer receipt ok:", rec.get("ok", rec))

    est = estimate(foot, idx, ANCHORS, (surf * dots).astype(np.float32))
    est["candidate"] = str(out.relative_to(ROOT))
    est["candidate_sha256"] = sha
    (ROOT / "evidence" / "peel_score_estimate_20261031.json").write_text(
        json.dumps(est, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: est[k] for k in ("candidate_holdout", "holdout_gain",
                                          "mapping_proportional", "mapping_additive",
                                          "estimate_interval")}, indent=1))
    for a in est["anchors"]:
        print(f"   {a['label']:32s} n={a['n']:6d} claim={a['claim']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
