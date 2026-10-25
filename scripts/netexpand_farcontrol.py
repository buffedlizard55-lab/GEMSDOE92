#!/usr/bin/env python3
"""Emission-matched control for netexpand_far: control_knick with d_visible>4.

Not an experiment arm (FAULTNET farcontrol precedent): refits the identical
KNICK30 control per draw (same seeds/exclusions as run_netexpand holdout),
emits with the far rule, merges terms into holdout_terms.npz and refreshes
evidence/netexpand_holdout.json scores/paired differences.
"""
from __future__ import annotations

import gc
import importlib.util
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
spec = importlib.util.spec_from_file_location("rn", ROOT / "scripts/run_netexpand.py")
rn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rn)
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa: E402


def main() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(rn.INPUTS / "bridge")
    foot = grid.footprint
    quad = hold_mod.quadrant_ids(foot)
    X, arr = rn.load_arrays()
    valid, det_elev = arr["valid"], arr["det_elev"]
    z = dict(np.load(rn.CACHE / "holdout_terms.npz"))
    tm_far, per_fold = None, []
    for seed in rn.SEEDS:
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis, hid = folds[0]["visible"], folds[0]["hidden_all"]
        excl = hid | (distance_transform_edt(~hid) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        rn.log(f"seed {seed}: context (visible) + knick control refit")
        rn.fill_context(X, foot, vis, det_elev, valid)
        p = rn.fit_knick_control(np.asarray(X), foot, valid, quad, vis, excl, seed=20261225 + seed)
        _, dots = rn.orig_dots(p, arr, valid, foot, d_vis, 4.0)
        pr = dots.astype(np.float32)
        pr[vis] = 0.0
        for f in folds:
            sc, tm = evaluate_holdout.evaluate(pr, f, foot)
            tm_far = tm if tm_far is None else tm_far + tm
            per_fold.append(dict(seed=seed, fold=f["name"], dti=round(float(sc["dti"]), 6)))
        del p, dots, pr
        gc.collect()
        rn.log(f"seed {seed} done ({time.time()-t0:.0f}s)")
    z["control_knick_far"] = tm_far
    np.savez(rn.CACHE / "holdout_terms.npz", **z)
    doc = json.loads((rn.EVIDENCE / "netexpand_holdout.json").read_text())
    for cand in ("netexpand", "netexpand_far", "nocontext"):
        s = evaluate_holdout.pooled_summary(z, draws=1000, seed=520810, candidate=cand)
        doc["scores"] = s["scores"]
        doc["paired_by_candidate"][cand] = s["paired_differences"]
    doc["per_fold"]["control_knick_far"] = per_fold
    doc["emission_matched_control"] = dict(
        name="control_knick_far", emission="d_visible > 4.0 (same as netexpand_far)",
        note="Post-hoc control (not an experiment arm); makes the far-arm comparison stricter.")
    (rn.EVIDENCE / "netexpand_holdout.json").write_text(json.dumps(doc, indent=1))
    sc = doc["scores"]["control_knick_far"]
    d = doc["paired_by_candidate"]["netexpand_far"]["control_knick_far"]
    rn.log(f"control_knick_far HOLDOUT-DTI {sc['dti']:.6f} CI {sc['ci95']}; "
           f"netexpand_far delta {d['delta']:+.6f} CI {d['ci95']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
