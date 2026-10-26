#!/usr/bin/env python3
"""Transparent, cross-validated DTI estimator (MODEL, never a score).

Purpose
-------
Answer the standing question "what would this file plausibly score?" WITHOUT
claiming a leaderboard result. The estimator is fitted only on owner-reported
CLAIM values already recorded in this repository, using four *measurable*
structural statistics of each scored raster:

  x1  share of positive pixels within 3 px of the H19-5 multiline skeleton
  x2  share of positive pixels within 2 px of the mapped catalogue (dead mass)
  x3  log10 of the positive-pixel budget
  x4  quadrant allocation imbalance (max quadrant share - 0.25)

Model: logit(E[DTI]) = b0 + b1*x1 + b2*x2 + b3*x3 + b4*x4, ridge-penalised,
fitted by least squares in logit space. Honesty checks reported alongside every
prediction: in-sample RMSE, leave-one-out RMSE, and leave-one-out Spearman
rank correlation between prediction and the CLAIM values.

Evidence classes
----------------
  y (training target)     CLAIM            owner-reported, no organizer receipt
  prediction              MODEL            fitted latent-intensity expectation
  measured statistics     REGISTRY-MEASUREMENT

A MODEL number is never written as a score. Its uncertainty is the LOO RMSE.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

INPUTS = ROOT / ".cache" / "gems_inputs"
PUB_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "site_scores_claimed_20261025.csv"
OUT = ROOT / "evidence" / "score_estimator_20261026.json"


def logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def inv_logit(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def stats_for(path: Path, foot, h19_near3, d_cat, quad) -> dict:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    pos = (a > 0) & foot
    n = int(pos.sum())
    if n == 0:
        return dict(n_dots=0, ok=False)
    q_shares = [float((pos & (quad == q)).sum()) / n for q in range(4)]
    return dict(
        n_dots=n,
        ok=True,
        sum_mass=round(float(a[pos].sum()), 2),
        frac_h19_near3=round(float(h19_near3[pos].mean()), 6),
        frac_dcat_le2=round(float((d_cat[pos] <= 2.0).mean()), 6),
        quadrant_imbalance=round(max(q_shares) - 0.25, 6),
        mean_dcat=round(float(d_cat[pos].mean()), 4),
    )


def fit_ridge(Z: np.ndarray, y: np.ndarray, lam: float = 0.06) -> np.ndarray:
    """Ridge on standardised columns with an unpenalised intercept."""
    mu = Z.mean(axis=0)
    sd = Z.std(axis=0)
    sd[sd == 0] = 1.0
    Zs = (Z - mu) / sd
    Zs = np.column_stack([np.ones(len(Zs)), Zs])
    pen = np.eye(Zs.shape[1]) * lam
    pen[0, 0] = 0.0
    return np.linalg.solve(Zs.T @ Zs + pen, Zs.T @ y), mu, sd


def predict(Z: np.ndarray, coef, mu, sd) -> np.ndarray:
    Zs = (Z - mu) / sd
    Zs = np.column_stack([np.ones(len(Zs)), Zs])
    return inv_logit(Zs @ coef)


H19_SATURATION = 0.65
"""Skeleton-proximity saturation cap.

Empirically, shares above ~0.65 are only reached by H19-5 descendants, and the
score there stops tracking proximity (0.2778 deep in the family). Clipping the
feature keeps the rank information among independent lanes while preventing the
logit model from extrapolating to implausible values on those files. Chosen from a
{0.45, 0.55, 0.65, 0.80, 1.00} sweep: leave-one-out RMSE/ρ are flat from 0.65 up
(0.0535/0.652 vs 0.0531/0.650), and only the cap removes the extrapolation.
"""


def features(rows: list[dict]) -> np.ndarray:
    return np.array(
        [
            [
                min(r["frac_h19_near3"], H19_SATURATION),
                r["frac_dcat_le2"],
                np.log10(max(r["n_dots"], 1)),
                r["quadrant_imbalance"],
            ]
            for r in rows
        ],
        dtype=np.float64,
    )


def main() -> int:
    inv = json.loads((PUB_CACHE / "repo_inventory.json").read_text(encoding="utf-8"))
    by_name: dict[str, list[tuple[str, Path]]] = {}
    for r in inv:
        for t in r["tifs"]:
            p = PUB_CACHE / f"{t['sha']}.tif"
            if p.is_file():
                by_name.setdefault(Path(t["path"]).stem, []).append((r["repo"], p))

    def resolve(name: str) -> list[tuple[str, Path]]:
        """Exact stem first; otherwise stems that *end with* the claimed name.

        Older ledgers record bare submission names (e.g. ``h25-1-dotted-h19-5-d1-5-...``)
        while the file is stored as ``gems24-h25-1-dotted-h19-5-d1-5-...``. A suffix
        match is accepted only if every matching stem resolves to the same blob set,
        so an ambiguous name is never guessed.
        """
        hits = by_name.get(name)
        if hits:
            return hits
        suffixed = [v for k, v in by_name.items() if k.endswith(name)]
        if not suffixed:
            return []
        shas = {p.name for group in suffixed for _repo, p in group}
        if len(shas) != 1:
            return []
        seen_paths: dict[str, tuple[str, Path]] = {}
        for group in suffixed:
            for repo, p in group:
                seen_paths.setdefault(p.name, (repo, p))
        return list(seen_paths.values())

    for r in inv:  # local served rasters (GEMSDOE92) are addressed by repo root
        if r["repo"] != "GEMSDOE92":
            continue
        for t in r["tifs"]:
            local = ROOT / t["path"]
            if local.is_file():
                by_name.setdefault(Path(t["path"]).stem, []).append(("GEMSDOE92", local))

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(INPUTS / "bridge" / "existing_faults.tif") as ds:
        cat = ds.read(1) > 0.5
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0) > 0.5
    d_cat = distance_transform_edt(~cat)
    h19_near3 = distance_transform_edt(~h19) <= 3.0
    H, W = foot.shape
    yy, xx = np.mgrid[0:H, 0:W]
    quad = ((yy >= H // 2).astype(np.int8) * 2 + (xx >= W // 2).astype(np.int8))

    # ---- training rows: owner-reported CLAIMs that resolve to one unique raster ----
    with LEDGER.open(encoding="utf-8") as fh:
        claims = [r for r in csv.DictReader(fh) if r.get("submission_name") and r.get("score")]
    train: list[dict] = []
    unresolved: list[dict] = []
    seen: set[str] = set()
    for c in claims:
        name = c["submission_name"].strip()
        if name in seen:
            continue
        hits = resolve(name)
        if not hits:
            unresolved.append(dict(site=c["site"].strip(), name=name, score=float(c["score"]), candidates=0))
            continue
        # Twin encodings (-zeros / -nan / -allfinite) of the same run are one scored
        # raster only if their positive support is pixel-identical; otherwise skip.
        chosen = None
        masks = []
        for repo, path in hits:
            try:
                with rasterio.open(path) as ds:
                    masks.append((np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0) > 0))
            except Exception:
                masks.append(None)
        good = [(h, m) for h, m in zip(hits, masks) if m is not None]
        if not good:
            unresolved.append(dict(site=c["site"].strip(), name=name, score=float(c["score"]), error="unreadable"))
            continue
        base = good[0][1]
        if any(not np.array_equal(m, base) for _, m in good[1:]):
            unresolved.append(dict(site=c["site"].strip(), name=name, score=float(c["score"]),
                                  candidates=len(hits), reason="twin encodings disagree on positive support"))
            continue
        chosen = good[0][0]
        seen.add(name)
        repo, path = chosen
        try:
            st = stats_for(path, foot, h19_near3, d_cat, quad)
        except Exception as exc:  # pragma: no cover - unreadable blob
            unresolved.append(dict(site=c["site"].strip(), name=name, score=float(c["score"]), error=str(exc)[:120]))
            continue
        if not st["ok"]:
            continue
        train.append(dict(site=c["site"].strip(), name=name, repo=repo, score=float(c["score"]), **st))

    y = np.array([r["score"] for r in train], dtype=np.float64)
    Z = features(train)
    coef, mu, sd = fit_ridge(Z, logit(y))

    fit_pred = predict(Z, coef, mu, sd)
    fit_rmse = float(np.sqrt(np.mean((fit_pred - y) ** 2)))

    loo = np.empty_like(y)
    for i in range(len(y)):
        mask = np.ones(len(y), dtype=bool)
        mask[i] = False
        c_i, m_i, s_i = fit_ridge(Z[mask], logit(y[mask]))
        loo[i] = predict(Z[i : i + 1], c_i, m_i, s_i)[0]
    loo_rmse = float(np.sqrt(np.mean((loo - y) ** 2)))
    loo_rho = float(spearmanr(loo, y).statistic)

    feature_names = ["frac_h19_near3_clipped_0.65", "frac_dcat_le2", "log10_n_dots", "quadrant_imbalance"]
    coef_raw = [float(c) for c in coef]
    coef_std = [float(c / s) for c, s in zip(coef[1:], sd)]

    # ---- predict for the focus-9 / fleet audit records + this session's arms ----
    audited = json.loads((ROOT / "evidence" / "focus9_executive_audit_20261026.json").read_text(encoding="utf-8"))
    targets: list[dict] = []
    for rec in audited["records"]:
        path = DOWNLOADS / Path(rec["rel_path"]).name
        if not path.is_file():
            hits = by_name.get(Path(rec["rel_path"]).stem, [])
            if not hits:
                continue
            # twin encodings of one run are interchangeable only if their positive
            # support is pixel-identical; otherwise this record is skipped.
            masks = []
            for _repo, p in hits:
                try:
                    with rasterio.open(p) as ds:
                        masks.append(np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0) > 0)
                except Exception:
                    masks.append(None)
            good = [(h, m) for h, m in zip(hits, masks) if m is not None]
            if not good or any(not np.array_equal(m, good[0][1]) for _, m in good[1:]):
                continue
            path = good[0][0][1]
        st = stats_for(path, foot, h19_near3, d_cat, quad)
        if not st["ok"]:
            continue
        targets.append(
            dict(
                key=rec["key"], site=rec["site"], role=rec["role"], sha256=rec["sha256"],
                rel_path=rec["rel_path"], claim_score=rec["claim_score"], **st,
            )
        )
    for arm in ("point37k", "celf37k", "celftail52k"):
        p = sorted(DOWNLOADS.glob(f"*SALEMSEISMO{arm}-*-zeros.tif"))
        if not p:
            continue
        st = stats_for(p[0], foot, h19_near3, d_cat, quad)
        targets.append(
            dict(
                key=f"SALEMSEISMO__{arm}", site="GEMSDOE92", role="new_20261026",
                sha256=None, rel_path=f"docs/downloads/{p[0].name}",
                claim_score=None, **st,
            )
        )

    Zt = features(targets)
    preds = predict(Zt, coef, mu, sd)
    for t, pr in zip(targets, preds):
        t["estimated_dti_MODEL"] = round(float(pr), 6)
        t["estimated_dti_MODEL_pm"] = round(loo_rmse, 6)
        base = t["claim_score"]
        if base is not None:
            t["claim_minus_model"] = round(float(base) - float(pr), 6)
        t["claim_label"] = (
            f"CLAIM {base:.4f}" if base is not None else "UNSCORED"
        )

    doc = dict(
        schema="gemsdoe92-score-estimator.v1",
        estimator="ridge logit(E[DTI]) ~ 1 + frac_h19_near3 + frac_dcat_le2 + log10(n_dots) + quadrant_imbalance",
        evidence_class="MODEL (fitted to owner-reported CLAIMs; NOT an organizer score)",
        trained_utc="2026-10-26",
        training_rows=len(train),
        unresolved_claims=len(unresolved),
        feature_names=feature_names,
        standardised_coefficients=dict(zip(feature_names, coef_std)),
        intercept_logit=coef_raw[0],
        in_sample_rmse=round(fit_rmse, 6),
        loo_rmse=round(loo_rmse, 6),
        loo_spearman=round(loo_rho, 6),
        interpretation=(
            "loo_rmse is the honest one-number uncertainty of any MODEL estimate below. "
            "loo_spearman measures rank fidelity against owner-reported CLAIMs only. "
            "Neither value is an organizer-confirmed accuracy."
        ),
        training=dict(
            rows=[
                dict(
                    site=r["site"], name=r["name"], repo=r["repo"], claim=round(r["score"], 6),
                    loo_model=round(float(l), 6),
                    frac_h19_near3=r["frac_h19_near3"], frac_dcat_le2=r["frac_dcat_le2"],
                    log10_n_dots=round(float(np.log10(max(r["n_dots"], 1))), 6),
                    quadrant_imbalance=r["quadrant_imbalance"], n_dots=r["n_dots"],
                )
                for r, l in zip(train, loo)
            ]
        ),
        unresolved=unresolved,
        predictions=sorted(targets, key=lambda t: -t["estimated_dti_MODEL"]),
    )
    OUT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    print(f"training rows {len(train)}  unresolved {len(unresolved)}")
    print(f"in-sample RMSE {fit_rmse:.4f} | LOO RMSE {loo_rmse:.4f} | LOO Spearman {loo_rho:.3f}")
    print("standardised coefficients:", {k: round(v, 3) for k, v in doc["standardised_coefficients"].items()})
    print()
    print(f"{'key':40s} {'claim':>7s} {'MODEL':>8s} {'delta':>8s} {'dots':>7s} {'h19':>6s} {'dc2':>6s}")
    for t in doc["predictions"]:
        cl = f"{t['claim_score']:.4f}" if t["claim_score"] is not None else "   -   "
        dl = f"{t['claim_minus_model']:+.4f}" if "claim_minus_model" in t else "   -   "
        print(
            f"{t['key']:40s} {cl:>7s} {t['estimated_dti_MODEL']:8.4f} {dl:>8s} "
            f"{t['n_dots']:7d} {t['frac_h19_near3']:6.3f} {t['frac_dcat_le2']:6.3f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
