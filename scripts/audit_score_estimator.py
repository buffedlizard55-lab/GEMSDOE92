#!/usr/bin/env python3
"""Reproduce a conservative grouped-CV diagnostic of the historical CLAIM model.

This does not validate a prediction interval or establish a leaderboard model.
Grouping merges same-site rows and rows with identical recorded feature vectors;
related lineages with different vectors may still leak across groups. The model's
feature cap was selected using the entire dataset, so this is not nested CV.
Only the already committed, rounded feature records and unverified claims are used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.estimate_scores import features, fit_ridge, logit, predict  # noqa: E402

SOURCE = ROOT / "evidence/score_estimator_20261026.json"
OUTPUT = ROOT / "docs/downloads/score_estimator_audit_14f85876.json"


def groups_for(rows: list[dict]) -> list[int]:
    """Connected components: same site OR identical recorded feature vector."""
    parent = list(range(len(rows)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def merge(i: int, j: int) -> None:
        a, b = find(i), find(j)
        if a != b:
            parent[b] = a

    seen_sites: dict[str, int] = {}
    seen_features: dict[tuple, int] = {}
    for i, row in enumerate(rows):
        site = row["site"]
        key = tuple(row[k] for k in (
            "frac_h19_near3", "frac_dcat_le2", "n_dots", "quadrant_imbalance"
        ))
        if site in seen_sites:
            merge(i, seen_sites[site])
        else:
            seen_sites[site] = i
        if key in seen_features:
            merge(i, seen_features[key])
        else:
            seen_features[key] = i
    return [find(i) for i in range(len(rows))]


def cv_predictions(rows: list[dict], groups: list[int]) -> np.ndarray:
    if len(rows) != len(groups) or len(set(groups)) < 2:
        raise ValueError("need at least two nonempty disjoint groups")
    X = features(rows)
    y = np.array([r["claim"] for r in rows], dtype=float)
    g = np.asarray(groups)
    out = np.empty(len(rows), dtype=float)
    for group in sorted(set(groups)):
        test = g == group
        train = ~test
        if train.sum() < 2:
            raise ValueError("too few training rows")
        coef, mu, sd = fit_ridge(X[train], logit(y[train]))
        out[test] = predict(X[test], coef, mu, sd)
    return out


def audit(source: Path = SOURCE) -> dict:
    raw = source.read_bytes()
    data = json.loads(raw)
    rows = data["training"]["rows"]
    if len(rows) != data["training_rows"] or not rows:
        raise ValueError("training record count mismatch")
    y = np.array([r["claim"] for r in rows], dtype=float)
    if not np.isfinite(y).all() or np.any((y < 0) | (y > 1)):
        raise ValueError("invalid claim target")
    groups = groups_for(rows)
    rowwise = cv_predictions(rows, list(range(len(rows))))
    grouped = cv_predictions(rows, groups)
    sizes = [groups.count(g) for g in sorted(set(groups))]
    return {
        "schema": "gemsdoe92-exploratory-claim-model-audit-v1",
        "source": "evidence/score_estimator_20261026.json",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "training_rows": len(rows),
        "target_provenance": "owner-reported CLAIMs; organizer receipts not verified",
        "grouping": "connected components of same site or identical recorded feature vectors",
        "groups": len(sizes),
        "largest_group": max(sizes),
        "rows_in_multimember_groups": sum(s for s in sizes if s > 1),
        "row_loo_rmse_recomputed": round(float(np.sqrt(np.mean((rowwise - y) ** 2))), 6),
        "leave_group_out_rmse": round(float(np.sqrt(np.mean((grouped - y) ** 2))), 6),
        "limitations": [
            "Recorded descriptors are rounded; identical descriptors do not prove identical rasters.",
            "Different-vector related descendants can still cross groups; grouping is incomplete.",
            "The H19 saturation cap was chosen using full-data sweeps; this is not nested CV.",
            "Both diagnostics use unverified claim labels, not organizer receipts.",
            "Neither RMSE is a calibrated individual prediction interval or a leaderboard score.",
        ],
        "valid_leaderboard_prediction": False,
        "individual_prediction_interval_available": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(audit(), indent=2, allow_nan=False) + "\n"
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != text:
            print(f"stale audit: {OUTPUT}", file=sys.stderr)
            return 1
        print("score-estimator grouped diagnostic: OK")
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(text, encoding="utf-8")
        print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
