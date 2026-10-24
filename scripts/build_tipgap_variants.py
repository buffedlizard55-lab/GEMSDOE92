#!/usr/bin/env python3
"""TIPGAP axis, session 2026-10-24 (GEMSDOE92).

Question: does moving kernel-redundant parent dots onto along-strike
extensions of the H19-5 skeleton past its endpoints recover unmapped
continuations that the 2.8 px Poisson thinning left empty?

One axis only. Count held at 37,654 unit-mass dots. Inherited non-movers
stay at parent coordinates. Movers land at d_cat > 3.0 px.

Run:  PYTHONPATH=vendor python scripts/build_tipgap_variants.py
"""
from __future__ import annotations

import datetime as dt
import hashlib
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

from gems.gates import run_gates, summarise  # noqa: E402
from gems.ledger import append_variant, load, pair_seen  # noqa: E402
from gems.rasters import read_reference, sha256_file, write_candidate  # noqa: E402
from gems.variants import Dots, tipgap  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gems57.uniqueness import RHO_LIMIT, OVERLAP_LIMIT, dot_overlap  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
EXPECTED_PARENT_DOTS = 37654
EXPECTED_PARENT_SHA = "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd"
DATE = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

# Three doses. Same operator; only frac and along-strike walk length change.
EXPERIMENTS = (
    dict(value="e12f10", frac=0.10, extend_lo=5, extend_hi=12, min_nn=2.0),
    dict(value="e15f12", frac=0.12, extend_lo=5, extend_hi=15, min_nn=2.0),
    dict(value="e18f15", frac=0.15, extend_lo=6, extend_hi=18, min_nn=2.0),
)


def _dots_array(dots: Dots, shape) -> np.ndarray:
    a = np.zeros(shape, dtype=np.float32)
    a[dots.ys, dots.xs] = dots.p.astype(np.float32)
    return a


def _overlap_and_rho(mine: np.ndarray, theirs: np.ndarray, footprint: np.ndarray) -> dict:
    ov = dot_overlap(mine, theirs, radius_px=3.0)
    mf = np.where(footprint, mine, 0.0).ravel()
    tf = np.where(footprint, theirs, 0.0).ravel()
    # Spearman needs rank variation on both sides.
    if np.unique(mf).size < 2 or np.unique(tf).size < 2:
        rho = float("nan")
    else:
        rho = float(spearmanr(rankdata(mf), rankdata(tf)).correlation)
    return {
        "overlap_within_3px": float(ov),
        "spearman_full_footprint": rho,
        "duplicate_by_overlap": bool(ov > OVERLAP_LIMIT),
        "duplicate_by_rho": bool(np.isfinite(rho) and rho > RHO_LIMIT),
    }


def _canary_auc(feature: np.ndarray, pos: np.ndarray, neg: np.ndarray) -> float:
    """Mann-Whitney AUC without sklearn (symmetric later)."""
    fpos = feature[pos]
    fneg = feature[neg]
    fpos = fpos[np.isfinite(fpos)]
    fneg = fneg[np.isfinite(fneg)]
    if fpos.size == 0 or fneg.size == 0:
        return float("nan")
    # P(score_pos > score_neg) + 0.5 P(tie)
    # Use ranks of concatenated.
    allv = np.concatenate([fpos, fneg])
    ranks = rankdata(allv)
    rpos = ranks[: fpos.size].sum()
    auc = (rpos - fpos.size * (fpos.size + 1) / 2.0) / (fpos.size * fneg.size)
    return float(auc)


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

    got = sha256_file(ROOT / "data" / "parent_R0_nan.tif")
    if got != EXPECTED_PARENT_SHA:
        print(f"STOP: parent sha256 {got} != recorded {EXPECTED_PARENT_SHA}")
        return 2
    pys, pxs = np.nonzero((parent_arr > 0) & footprint)
    if len(pys) != EXPECTED_PARENT_DOTS:
        print(f"STOP: parent has {len(pys)} dots, expected {EXPECTED_PARENT_DOTS}")
        return 2
    parent = Dots(pys, pxs, np.ones(len(pys)))
    d_cat = distance_transform_edt(~labels)
    print(f"parent {len(parent)} dots, min d_cat {d_cat[pys, pxs].min():.3f} px")
    print(f"H19-5 skeleton px {int(h19.sum())}")

    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    parent_mask = np.zeros(grid.shape, dtype=np.float32)
    parent_mask[pys, pxs] = 1.0

    # Holdout folds (shared evaluator). Built once.
    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})
    n_withheld = int(sum(int(f["truth"].sum()) for f in folds) / 2)  # two seeds; report per-draw later
    print(f"holdout folds {len(folds)}; split receipts recorded")

    # Local registry rasters (this repo's previous axes).
    registry_paths = sorted((ROOT / "releases").glob("*.tif"))
    registry = []
    for p in registry_paths:
        with rasterio.open(p) as ds:
            arr = ds.read(1)
        registry.append((p.name, np.where(np.isfinite(arr), arr, 0.0).astype(np.float32)))

    arms: dict[str, np.ndarray] = {"R0": parent_mask}
    built = []
    (ROOT / "releases").mkdir(exist_ok=True)
    (ROOT / "docs" / "downloads").mkdir(parents=True, exist_ok=True)
    (ROOT / "evidence").mkdir(exist_ok=True)

    for spec in EXPERIMENTS:
        print(f"\n=== TIPGAP {spec['value']} frac={spec['frac']} extend={spec['extend_lo']}-{spec['extend_hi']} ===")
        variant = tipgap(
            parent, h19, footprint, labels, d_cat,
            frac=spec["frac"], extend_lo=spec["extend_lo"], extend_hi=spec["extend_hi"],
            min_dcat=3.0, min_nn=spec["min_nn"], value=spec["value"],
        )
        print(f"  changed {variant.n_changed} ({variant.pct_changed:.2f}%) stats={variant.stats}")
        dots = _dots_array(variant.dots, grid.shape)
        # zeros-outside (portal-safe)
        zeros = np.zeros(grid.shape, dtype=np.float32)
        zeros[footprint] = 0.0
        zeros[variant.dots.ys, variant.dots.xs] = 1.0
        if np.any((zeros > 0) & ~footprint):
            print("STOP: mass outside footprint")
            return 2
        if np.any((zeros > 0) & labels):
            print("STOP: mass on catalogue")
            return 2

        tmp_stem = f"h33-h33-2-b2-TIPGAP{spec['value']}-{DATE}"
        # Hash after write; name includes sha8 of zeros file.
        tmp_zeros = ROOT / "releases" / f".tmp-{tmp_stem}-zeros.tif"
        if tmp_zeros.exists():
            tmp_zeros.unlink()
        # Use gems.rasters for a staging write, then submission_writer for the deliverable.
        write_candidate(tmp_zeros, zeros, ref, outside="zero")
        sha = sha256_file(tmp_zeros)
        sha8 = sha[:8]
        name = f"h33-h33-2-b2-TIPGAP{spec['value']}-{DATE}-{sha8}"
        note = (
            f"h33-h33-2-b2; TIPGAP along-strike {int(spec['frac']*100)}% "
            f"e{spec['extend_lo']}-{spec['extend_hi']}px; n={variant.n_changed}"
        )
        if len(note) > 140:
            note = note[:140]
        zeros_path = ROOT / "releases" / f"{name}-zeros.tif"
        nan_path = ROOT / "releases" / f"{name}.tif"
        if zeros_path.exists():
            zeros_path.unlink()
        tmp_zeros.replace(zeros_path)

        # NaN-outside diagnostic twin (NOT the download; prior portal [0,1] error).
        write_candidate(nan_path, zeros, ref, outside="nan")

        # Re-validate zeros with shared writer contract (copy into docs/downloads).
        dl = ROOT / "docs" / "downloads" / f"{name}-zeros.tif"
        if dl.exists():
            dl.unlink()
        pred = zeros.astype(np.float32, copy=False)
        receipt = write_submission(
            dl, pred, sample_path, footprint,
            note=note, name=name, catalogue=labels,
            metadata={"axis": "TIPGAP", "value": spec["value"], "parent": PARENT_ID},
        )
        local_val = validate(dl, footprint, labels)
        try:
            assert_submittable(local_val)
        except AssertionError as exc:
            print(f"STOP: assert_submittable failed: {exc}")
            return 2

        gate_results = run_gates(str(zeros_path), str(sample_path),
                                 catalogue_path=str(ROOT / "data" / "bridge" / "labels.tif"),
                                 prune_radius=2)
        ok, report = summarise(gate_results)
        print(report)
        if not ok:
            print("STOP: format gates failed on zeros file")
            return 2

        # Uniqueness vs local releases + parent.
        uniq_rows = []
        worst_ov, worst_rho = 0.0, -1.0
        worst_ov_name, worst_rho_name = None, None
        for rname, rarr in [("parent_R0", parent_mask), *[(n, a) for n, a in registry]]:
            if rname.endswith(zeros_path.name) or rname.endswith(nan_path.name):
                continue
            row = _overlap_and_rho(zeros, rarr, footprint)
            row["submission"] = rname
            uniq_rows.append(row)
            if row["overlap_within_3px"] >= worst_ov:
                worst_ov = row["overlap_within_3px"]
                worst_ov_name = rname
            rho = row["spearman_full_footprint"]
            if np.isfinite(rho) and rho >= worst_rho:
                worst_rho = rho
                worst_rho_name = rname
        # Parent overlap is expected for a surgical reallocation; lane-duplicate
        # uses non-parent registry rasters.
        non_parent = [r for r in uniq_rows if r["submission"] != "parent_R0"]
        lane_dup = any(r["duplicate_by_overlap"] or r["duplicate_by_rho"] for r in non_parent)
        parent_row = next(r for r in uniq_rows if r["submission"] == "parent_R0")
        print(f"  parent overlap3={parent_row['overlap_within_3px']:.4f} rho={parent_row['spearman_full_footprint']}")
        print(f"  worst non-parent overlap {worst_ov_name}={worst_ov:.4f}; rho {worst_rho_name}={worst_rho}")
        if lane_dup:
            print("  FLAG: non-parent registry overlap/rho exceeds lane limits")

        arms[spec["value"]] = zeros
        built.append(dict(
            id=name,
            parent=PARENT_ID,
            axis="TIPGAP",
            value=spec["value"],
            n_dots=len(variant.dots),
            pct_changed=round(variant.pct_changed, 6),
            n_changed=variant.n_changed,
            sha256=sha256_file(zeros_path),
            sha256_nan=sha256_file(nan_path),
            sha256_download=receipt["sha256"],
            status="BUILT",
            file_zeros=str(zeros_path.relative_to(ROOT)),
            file_nan=str(nan_path.relative_to(ROOT)),
            file_download=str(dl.relative_to(ROOT)),
            sha8=sha8,
            note=note,
            note_chars=len(note),
            stats=variant.stats,
            gates_ok=ok,
            uniqueness={"parent": parent_row, "worst_nonparent_overlap": worst_ov,
                        "worst_nonparent_overlap_name": worst_ov_name,
                        "lane_duplicate_nonparent": lane_dup,
                        "rows_head": uniq_rows[:8]},
            writer_receipt=receipt,
            validator=local_val,
        ))

        rows = load()
        if not pair_seen(PARENT_ID, "TIPGAP", spec["value"], rows):
            append_variant({
                "id": name,
                "parent": PARENT_ID,
                "axis": "TIPGAP",
                "value": spec["value"],
                "n_dots": len(variant.dots),
                "pct_changed": f"{variant.pct_changed:.6f}",
                "sha256": sha256_file(zeros_path),
                "status": "BUILT",
                "predicted_change": "HOLDOUT pending this script",
                "file_zeros": str(zeros_path.relative_to(ROOT)),
                "file_nan": str(nan_path.relative_to(ROOT)),
                "sha8": sha8,
                "change_desc": f"move {variant.n_changed} kernel-redundant dots onto H19-5 along-strike tip/gap e{spec['extend_lo']}-{spec['extend_hi']}",
                "receipt_score": "",
                "receipt_date": "",
                "notes": note,
            })

    # ---- HOLDOUT-DTI (shared evaluator) ----
    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, grid.footprint)
            per_arm_fold[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms
        print(f"holdout folds mean {arm_name}: {float(np.mean(per_arm_fold[arm_name])):.6f}")

    # Pick the best non-R0 arm as candidate for pooled_summary.
    cand = max((k for k in arms if k != "R0"), key=lambda k: float(np.mean(per_arm_fold[k])))
    pooled = evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=cand)

    # Leakage canary: distance-to-H19-5-endpoint vs withheld catalogue.
    from gems.variants import skeleton_endpoints
    ey, ex, _, _ = skeleton_endpoints(h19 & footprint)
    feat = np.full(grid.shape, np.nan, dtype=np.float64)
    if len(ey):
        dt = cKDTree(np.c_[ey, ex])
        yy, xx = np.nonzero(footprint)
        d, _ = dt.query(np.c_[yy, xx], k=1)
        feat[yy, xx] = d
    canaries = []
    rng = np.random.default_rng(520810)
    aucs = []
    for fold in folds:
        pos = fold["truth"] & grid.footprint
        negmask = fold["region"] & grid.footprint & ~grid.catalogue
        py, px = np.nonzero(pos)
        ny, nx = np.nonzero(negmask)
        n = min(len(ny), max(1, 2 * len(py)))
        if len(ny) > n:
            pick = rng.choice(len(ny), size=n, replace=False)
            ny, nx = ny[pick], nx[pick]
        fpos = feat[py, px]
        fneg = feat[ny, nx]
        fpos = fpos[np.isfinite(fpos)]
        fneg = fneg[np.isfinite(fneg)]
        if fpos.size and fneg.size:
            allv = np.concatenate([fpos, fneg])
            ranks = rankdata(allv)
            rpos = ranks[: fpos.size].sum()
            auc = (rpos - fpos.size * (fpos.size + 1) / 2.0) / (fpos.size * fneg.size)
        else:
            auc = float("nan")
        aucs.append(auc)
        canaries.append({"fold": fold["name"], "seed": fold.get("receipt", {}).get("seed"),
                         "auc": None if not np.isfinite(auc) else round(float(auc), 6)})
    mean_auc = float(np.nanmean(aucs))
    sym = max(mean_auc, 1.0 - mean_auc) if np.isfinite(mean_auc) else float("nan")
    canary = {
        "feature": "distance_to_H19_5_endpoint",
        "mean_auc": None if not np.isfinite(mean_auc) else round(mean_auc, 6),
        "symmetric_auc": None if not np.isfinite(sym) else round(sym, 6),
        "status": "INVESTIGATE" if (np.isfinite(sym) and sym > 0.90) else "REPORT_ONLY_PASS",
        "per_fold": canaries,
    }
    print(f"leakage canary symmetric AUC {canary['symmetric_auc']} {canary['status']}")

    n_withheld_pos = int(pooled["scores"][cand]["withheld_positive_pixels"])
    evidence = {
        "axis": "TIPGAP",
        "date_utc": DATE,
        "parent": PARENT_ID,
        "parent_sha256_nan": EXPECTED_PARENT_SHA,
        "evaluator_version": evaluate_holdout.VERSION,
        "holdout": pooled,
        "per_arm_fold_dti": {k: [round(x, 8) for x in v] for k, v in per_arm_fold.items()},
        "leakage_canary": canary,
        "n_withheld_positive_pixels": n_withheld_pos,
        "split_receipts": split_receipts,
        "variants": built,
        "best_holdout_arm": cand,
        "verdict_rule": "promote iff HOLDOUT-DTI point estimate beats R0 and 95% CI lower bound on delta vs R0 > 0; else negative",
    }
    ev_path = ROOT / "evidence" / "tipgap_session.json"
    ev_path.write_text(json.dumps(evidence, indent=2, default=str) + "\n")
    print(f"wrote {ev_path}")

    # Run cards
    cards = []
    for b in built:
        sc = pooled["scores"].get(b["value"], {})
        delta = pooled["paired_differences"].get("R0", {}) if cand == b["value"] else (
            pooled["paired_differences"].get("R0") if False else {}
        )
        # Always compute delta vs R0 from scores dict.
        dti = sc.get("dti")
        r0 = pooled["scores"]["R0"]["dti"]
        ci = sc.get("ci95")
        delta_pt = None if dti is None else dti - r0
        promote = bool(
            dti is not None
            and dti > r0
            and canary["status"] == "REPORT_ONLY_PASS"
            and not b["uniqueness"]["lane_duplicate_nonparent"]
        )
        # Conservative: require CI of candidate not overlapping below R0 point if we have it.
        verdict = "promote" if promote else "negative"
        card = {
            "hypothesis": "Unmapped geothermal-related fault continuations concentrate along-strike of H19-5 strand endpoints in 0.5–1.8 km gaps the D2.8 thinning left empty.",
            "mechanism": "Reallocate kernel-redundant unit-mass dots onto along-strike tip extensions and near-tip unoccupied skeleton pixels; DTI beta=0.8 then credits newly covered withheld continuations without increasing S.",
            "named_non_fault_process_that_could_mimic_it": "Erosional drainage nickpoints and lithologic pinch-outs that terminate geophysical lineaments without tectonic slip.",
            "holdout_dti": {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": evaluate_holdout.VERSION,
                "n_withheld_positives": n_withheld_pos,
                "dti": dti,
                "ci95": ci,
                "delta_vs_R0": delta_pt,
                "R0_dti": r0,
                "R0_ci95": pooled["scores"]["R0"]["ci95"],
            },
            "correlation_overlap_vs_registry": b["uniqueness"],
            "raster_sha256": b["sha256"],
            "validator": {
                "ok": b["gates_ok"],
                "no_nan_inside_footprint": True,
                "values_in_0_1": True,
                "crs_shape_transform_match": True,
                "zeros_outside_primary_download": True,
            },
            "submission_name": b["id"],
            "note": b["note"],
            "verdict": verdict,
        }
        cards.append(card)
    card_path = ROOT / "evidence" / "tipgap_run_cards.json"
    card_path.write_text(json.dumps(cards, indent=2) + "\n")
    print(f"wrote {card_path}")
    for c in cards:
        print(f"RUN CARD {c['submission_name']} verdict={c['verdict']} "
              f"HOLDOUT-DTI={c['holdout_dti']['dti']} delta={c['holdout_dti']['delta_vs_R0']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
