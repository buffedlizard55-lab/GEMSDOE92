#!/usr/bin/env python3
"""Uniqueness-corrected TIPGAP far landing (lane drift repair).

The three on-skeleton TIPGAP doses kept >=85% of R0 pixels, so >70% of dots
fell within 3 px of parent/MASS registry rasters. This file moves 33% of
kernel-redundant dots onto along-strike extensions that are strictly >3 px
from every parent dot (off the D2.8 skeleton), which is the unique lane.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.gates import run_gates, summarise
from gems.ledger import append_variant, pair_seen, load
from gems.rasters import read_reference, sha256_file, write_candidate
from gems.variants import Dots, tipgap
from gems57 import evaluate_holdout, grid as grid_mod, holdout
from gems57.submission_writer import write_submission
from gems57.uniqueness import OVERLAP_LIMIT, RHO_LIMIT, dot_overlap
from gems57.validate import assert_submittable, validate

PARENT_ID = "h33-h33-2-b2"
EXPECTED_PARENT_SHA = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
DATE = json.loads((ROOT / "evidence" / "tipgap_session.json").read_text())["date_utc"]
# Keep a new timestamp for the unique file.
import datetime as dt
DATE = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

SPEC = dict(value="far18f33", frac=0.33, extend_lo=6, extend_hi=18, min_nn=2.0, min_parent_dist=3.0)


def _overlap_and_rho(mine, theirs, footprint):
    ov = float(dot_overlap(mine, theirs, radius_px=3.0))
    mf = np.where(footprint, mine, 0.0).ravel()
    tf = np.where(footprint, theirs, 0.0).ravel()
    if np.unique(mf).size < 2 or np.unique(tf).size < 2:
        rho = float("nan")
    else:
        rho = float(spearmanr(rankdata(mf), rankdata(tf)).correlation)
    return ov, rho


def main() -> int:
    ref = read_reference(ROOT / "data" / "bridge" / "sample_submission.tif")
    footprint = ref["footprint"]
    sample_path = ROOT / "data" / "bridge" / "sample_submission.tif"
    with rasterio.open(ROOT / "data" / "bridge" / "labels.tif") as ds:
        labels = ds.read(1) > 0.5
    with rasterio.open(ROOT / "data" / "parent_R0_nan.tif") as ds:
        parent_arr = ds.read(1)
    with rasterio.open(ROOT / "data" / "bridge" / "h19_5.tif") as ds:
        h19 = ds.read(1) > 0.5
    assert sha256_file(ROOT / "data" / "parent_R0_nan.tif") == EXPECTED_PARENT_SHA
    pys, pxs = np.nonzero((parent_arr > 0) & footprint)
    parent = Dots(pys, pxs, np.ones(len(pys)))
    d_cat = distance_transform_edt(~labels)
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    parent_mask = np.zeros(grid.shape, np.float32)
    parent_mask[pys, pxs] = 1.0

    variant = tipgap(
        parent, h19, footprint, labels, d_cat,
        frac=SPEC["frac"], extend_lo=SPEC["extend_lo"], extend_hi=SPEC["extend_hi"],
        min_dcat=3.0, min_nn=SPEC["min_nn"], min_parent_dist=SPEC["min_parent_dist"],
        value=SPEC["value"],
    )
    print("changed", variant.n_changed, variant.pct_changed, variant.stats)
    zeros = np.zeros(grid.shape, np.float32)
    zeros[variant.dots.ys, variant.dots.xs] = 1.0
    assert not np.any((zeros > 0) & ~footprint)
    assert not np.any((zeros > 0) & labels)

    staging = ROOT / "releases" / ".tmp-tipfar-zeros.tif"
    if staging.exists():
        staging.unlink()
    write_candidate(staging, zeros, ref, outside="zero")
    sha = sha256_file(staging)
    sha8 = sha[:8]
    name = f"h33-h33-2-b2-TIPGAPfar18f33-{DATE}-{sha8}"
    note = f"h33-h33-2-b2; TIPGAP FAR 33% along-strike >3px off parent skeleton e6-18; unique lane"
    if len(note) > 140:
        note = note[:140]
    zeros_path = ROOT / "releases" / f"{name}-zeros.tif"
    nan_path = ROOT / "releases" / f"{name}.tif"
    staging.replace(zeros_path)
    write_candidate(nan_path, zeros, ref, outside="nan")

    dl_dir = ROOT / "docs" / "downloads"
    dl_dir.mkdir(parents=True, exist_ok=True)
    dl = dl_dir / f"{name}-zeros.tif"
    if dl.exists():
        dl.unlink()
    receipt = write_submission(dl, zeros.astype(np.float32), sample_path, footprint,
                               note=note, name=name, catalogue=labels,
                               metadata={"axis": "TIPGAP", "value": SPEC["value"], "lane": "far"})
    local_val = validate(dl, footprint, labels)
    assert_submittable(local_val)
    ok, report = summarise(run_gates(str(zeros_path), str(sample_path),
                                     catalogue_path=str(ROOT / "data/bridge/labels.tif"),
                                     prune_radius=2))
    print(report)
    if not ok:
        return 2

    registry = [("parent_R0", parent_mask)]
    for p in sorted((ROOT / "releases").glob("*.tif")):
        if p.name.startswith(name):
            continue
        with rasterio.open(p) as ds:
            a = ds.read(1)
        registry.append((p.name, np.where(np.isfinite(a), a, 0.0).astype(np.float32)))
    uniq = []
    flags = []
    for rname, rarr in registry:
        ov, rho = _overlap_and_rho(zeros, rarr, footprint)
        row = dict(submission=rname, overlap_within_3px=ov, spearman_full_footprint=rho,
                   duplicate_by_overlap=ov > OVERLAP_LIMIT,
                   duplicate_by_rho=bool(np.isfinite(rho) and rho > RHO_LIMIT))
        uniq.append(row)
        print(f"  vs {rname}: ov={ov:.4f} rho={rho}")
        if rname != "parent_R0" and (row["duplicate_by_overlap"] or row["duplicate_by_rho"]):
            flags.append(rname)
    parent_ov = next(r for r in uniq if r["submission"] == "parent_R0")
    parent_dup = parent_ov["duplicate_by_overlap"] or parent_ov["duplicate_by_rho"]
    print("parent duplicate?", parent_dup, "nonparent flags", flags)

    folds = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    arms = {"R0": parent_mask, SPEC["value"]: zeros}
    terms_by_arm = {}
    per_arm = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, grid.footprint)
            per_arm[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
        print("holdout mean", arm_name, float(np.mean(per_arm[arm_name])))
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=SPEC["value"])
    dti = pooled["scores"][SPEC["value"]]["dti"]
    r0 = pooled["scores"]["R0"]["dti"]
    ci = pooled["scores"][SPEC["value"]]["ci95"]
    npos = pooled["scores"][SPEC["value"]]["withheld_positive_pixels"]
    print("HOLDOUT-DTI", dti, "CI", ci, "R0", r0, "npos", npos)

    from gems.variants import skeleton_endpoints
    ey, ex, _, _ = skeleton_endpoints(h19 & footprint)
    feat = np.full(grid.shape, np.nan)
    yy, xx = np.nonzero(footprint)
    d, _ = cKDTree(np.c_[ey, ex]).query(np.c_[yy, xx], k=1)
    feat[yy, xx] = d
    rng = np.random.default_rng(520810)
    aucs = []
    for fold in folds:
        py, px = np.nonzero(fold["truth"] & grid.footprint)
        ny, nx = np.nonzero(fold["region"] & grid.footprint & ~grid.catalogue)
        n = min(len(ny), max(1, 2 * len(py)))
        if len(ny) > n:
            pick = rng.choice(len(ny), size=n, replace=False)
            ny, nx = ny[pick], nx[pick]
        fpos, fneg = feat[py, px], feat[ny, nx]
        fpos, fneg = fpos[np.isfinite(fpos)], fneg[np.isfinite(fneg)]
        allv = np.concatenate([fpos, fneg])
        ranks = rankdata(allv)
        auc = (ranks[: fpos.size].sum() - fpos.size * (fpos.size + 1) / 2.0) / (fpos.size * fneg.size)
        aucs.append(float(auc))
    mean_auc = float(np.mean(aucs))
    sym = max(mean_auc, 1.0 - mean_auc)
    canary = dict(feature="distance_to_H19_5_endpoint", mean_auc=round(mean_auc, 6),
                  symmetric_auc=round(sym, 6),
                  status="INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS")
    print("canary", canary)

    promote = (dti > r0) and (canary["status"] == "REPORT_ONLY_PASS") and (not parent_dup) and (not flags)
    card = {
        "hypothesis": "Unmapped fault continuations sit 0.5–1.8 km along-strike of H19-5 tips, off the D2.8 skeleton (the pixels the Poisson thinning never occupied).",
        "mechanism": "Move 33% kernel-redundant parent dots onto along-strike walks >3 px from every R0 dot; S fixed, new T only if withheld continuations exist off-skeleton.",
        "named_non_fault_process_that_could_mimic_it": "Alluvial-fan channel nickpoints and lithologic pinch-outs that terminate magnetic lineaments without slip.",
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "n_withheld_positives": int(npos),
            "dti": dti,
            "ci95": ci,
            "delta_vs_R0": dti - r0,
            "R0_dti": r0,
            "R0_ci95": pooled["scores"]["R0"]["ci95"],
        },
        "correlation_overlap_vs_registry": {
            "parent": parent_ov,
            "nonparent_flags": flags,
            "rho_limit": RHO_LIMIT,
            "overlap_limit": OVERLAP_LIMIT,
            "complete_accessible_scan": False,
            "rows_head": uniq[:12],
        },
        "raster_sha256": sha256_file(zeros_path),
        "download_sha256": receipt["sha256"],
        "validator": local_val,
        "gates_report": report,
        "submission_name": name,
        "note": note,
        "verdict": "promote" if promote else "negative",
        "format_ok_to_upload": True,
        "slot_recommendation": "NOT a weekly slot unless a human overrides; holdout did not beat R0" if not promote else "holdout beat R0; still requires human quota check",
    }
    (ROOT / "evidence" / "tipgap_far_run_card.json").write_text(json.dumps(card, indent=2, default=str) + "\n")
    payload = {
        "spec": SPEC, "name": name, "note": note, "date_utc": DATE,
        "stats": variant.stats, "pct_changed": variant.pct_changed,
        "file_zeros": str(zeros_path.relative_to(ROOT)),
        "file_nan": str(nan_path.relative_to(ROOT)),
        "file_download": str(dl.relative_to(ROOT)),
        "file_zip": str(dl.with_suffix(".zip").relative_to(ROOT)),
        "sha256_zeros": sha256_file(zeros_path),
        "sha256_download": receipt["sha256"],
        "n_dots": int((zeros > 0).sum()),
        "pooled": pooled,
        "canary": canary,
        "card": card,
        "writer_receipt": receipt,
    }
    (ROOT / "evidence" / "tipgap_far.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")
    if not pair_seen(PARENT_ID, "TIPGAP", SPEC["value"], load()):
        append_variant({
            "id": name, "parent": PARENT_ID, "axis": "TIPGAP", "value": SPEC["value"],
            "n_dots": int((zeros > 0).sum()), "pct_changed": f"{variant.pct_changed:.6f}",
            "sha256": sha256_file(zeros_path), "status": "BUILT",
            "predicted_change": f"HOLDOUT-DTI {dti:.6f} vs R0 {r0:.6f}",
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha8, "change_desc": "33% far along-strike >3px from all parent dots",
            "receipt_score": "", "receipt_date": "", "notes": note,
        })
    print("VERDICT", card["verdict"], name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
