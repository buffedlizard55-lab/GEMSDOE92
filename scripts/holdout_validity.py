#!/usr/bin/env python3
"""Does the shared catalogue hide-and-recover holdout predict leaderboard CLAIMs?

Scores every CLAIM-matched raster, as published, on the gems57 instrument
(buffered whole-component draws, seeds 20 and 30; visible faults masked
pixel-exactly; pooled DTI alpha 0.2 / beta 0.8, 300 m kernel), then reports
the rank correlation between HOLDOUT-DTI and the owner-reported CLAIM, next to
the LBM's grouped-CV predictions.  Output: evidence/holdout_validity_20261027.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr, pearsonr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
import lbm_data as L  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402


def main() -> int:
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")
    foot = grid.footprint
    folds = []
    for seed in (20, 30):
        f, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        folds.extend(f)
    model = json.loads((ROOT / "evidence" / "lbm_v1_model.json").read_text())
    rows = model["rows"]
    seen = {}
    out = []
    for r in rows:
        sha = r["sha256"]
        if sha not in seen:
            p, _ = L.full_from_summary(sha)
            p = np.clip(np.nan_to_num(p), 0, 1).astype(np.float64)
            terms = None
            for fold in folds:
                _, tm = evaluate_holdout.evaluate(p, fold, foot)
                terms = tm if terms is None else terms + tm
            t = terms.sum(axis=0)
            seen[sha] = float(t[0] / (t[0] + 0.2 * t[1] + 0.8 * t[2]))
        out.append(dict(site=r["site"], name=r["name"], claim=r["claim"], holdout_dti=seen[sha],
                        lbm_logo=r["logo"]))
        print(r["site"], r["claim"], round(seen[sha], 5), flush=True)
    c = np.array([o["claim"] for o in out]); h = np.array([o["holdout_dti"] for o in out])
    l = np.array([o["lbm_logo"] for o in out])
    res = dict(schema="gemsdoe92-holdout-validity-v1",
               instrument="gems57 buffered_component_draw seeds 20,30 (22,663 withheld positives); rasters scored as published",
               n=len(out),
               spearman_holdout_vs_claim=float(spearmanr(h, c)[0]),
               pearson_holdout_vs_claim=float(pearsonr(h, c)[0]),
               spearman_lbm_logo_vs_claim=float(spearmanr(l, c)[0]),
               top10_by_claim=[dict(o) for o in sorted(out, key=lambda o: -o["claim"])[:10]],
               top10_by_holdout=[dict(o) for o in sorted(out, key=lambda o: -o["holdout_dti"])[:10]],
               rows=out)
    (ROOT / "evidence" / "holdout_validity_20261027.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k.startswith(("spearman", "pearson", "n"))}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
