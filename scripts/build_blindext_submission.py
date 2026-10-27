#!/usr/bin/env python3
"""BLINDEXT lane build: unique submission GeoTIFF + autonomous validation.

Historical hypothesis (docs/HYPOTHESES_BLINDEXT.md), not a validated result:
  h19_5 is a prior prediction, not the USGS/INGENIOUS mapped-fault catalogue.
  Its positive-support endpoints do not establish mapped fault tips or blind
  extensions. The historical placement used a full-catalogue distance mask
  and checked uniqueness after placing dots, so it cannot establish a
  prospective, fold-local holdout result or satisfy the pre-placement stop.
  This runner is disabled while the literal registry witness binds.

Method (uses only bridge data; no competition stack reads):
  1. Load h19_5 skeleton, existing_faults catalogue, sample_submission footprint.
  2. Find 8-connectivity endpoints of h19_5 (fault-trace termini).
  3. Compute Euclidean distance transform from endpoints -> d_endpoint.
  4. Compute Euclidean distance transform from catalogue -> d_cat.
  5. Candidate mask: footprint & ~catalogue & (d_cat > 2.0 px)
                         & (d_endpoint <= 6 px)  & (~h19_5 trace itself)
     - d_cat > 2.0 keeps dots off/near-but-not-on known faults (R0's winning
       prune radius), avoiding catalogue false-positive mass.
     - d_endpoint <= 6 px targets blind extensions of mapped traces.
     - ~h19_5 avoids re-dotting the mapped skeleton itself.
  6. Candidate score = exp(-d_endpoint / 3.0) within the productive
     catalogue band (2.0 < d_cat <= 6.0 px); zero elsewhere.
  7. Non-maximum suppression: sort by score, greedily pick dots spaced
     >= 2.83 px (~300 m, the DTI kernel radius), stop at 37,654 dots
     (same budget as R0/GEMSDOE32).
  8. Package via vendor/gems57/grid.write_submission (zeros-outside,
     float32, EPSG:32611, 3730x3292, pinned transform, [0,1], zero
     catalogue mass).
  9. Format gates: gems.gates.run_gates (require_submission_encoding) +
     gems57.validate, independent disk re-read.
 10. Uniqueness (REGISTRY-MEASUREMENT): local served rasters
     (docs/downloads/*-zeros.tif + releases/*.tif), literal + matched-budget
     3-px forward overlap and |Spearman rho| on the surface.
 11. Write Protocol Rule 5 run card + per-file audit JSON.

Verdict logic: promote only if format gates pass AND uniqueness passes
(literal <= 0.70 and |rho| <= 0.90 vs every local raster). Otherwise
verdict = negative (format-valid unique TIF, research download only).
Holdout-DTI cannot be computed here because the organizer's withheld truth
is not published (labels.tif IS the catalogue); this is disclosed in the
run card, not projected as a score.

No DrivenData auth, no network beyond already-pinned mirrors, no human
inspection.  Format validation is fully automated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import convolve, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "gems")]

from gems57 import grid as grid_mod  # noqa: E402
from gems57.uniqueness import stop_historical_runner  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402

BRIDGE = ROOT / "data" / "bridge"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
RELEASES = ROOT / "releases"

N_DOTS = 37_654
MIN_DIST_PX = 2.83  # ~300 m at 100 m/pixel, the DTI triangular-kernel radius
CATALOGUE_CLEARANCE_PX = 2.0  # R0's winning prune radius
ENDPOINT_REACH_PX = 6.0  # blind-extension reach beyond mapped trace
PRODUCTIVE_CAT_BAND = (2.0, 6.0)  # close enough for kernel credit, off-catalogue


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def find_endpoints(skel: np.ndarray) -> np.ndarray:
    """8-connectivity skeleton endpoints: skeleton pixel with exactly 1 neighbor."""
    kernel = np.ones((3, 3), dtype=int)
    kernel[1, 1] = 0
    nbr = convolve(skel.astype(np.int16), kernel, mode="constant", cval=0)
    return (skel > 0) & (nbr == 1)


def matched_budget_support(raw: np.ndarray, foot: np.ndarray, k: int) -> np.ndarray:
    """Matched-budget support: top-k support pixels of a continuous surface."""
    idx = np.flatnonzero(raw > 0)
    if idx.size == 0:
        return np.zeros_like(raw, dtype=bool)
    order = np.argsort(-raw.ravel()[idx], kind="stable")
    pick = idx[order[: min(k, idx.size)]]
    support = np.zeros_like(raw, dtype=bool)
    support.flat[pick] = True
    return support & foot


def dots_within_radius(dot_ys: np.ndarray, dot_xs: np.ndarray,
                       support_ys: np.ndarray, support_xs: np.ndarray,
                       radius: float) -> np.ndarray:
    """Boolean per candidate dot: within `radius` px of any support pixel."""
    if support_ys.size == 0 or dot_ys.size == 0:
        return np.zeros(dot_ys.size, dtype=bool)
    from scipy.spatial import cKDTree

    tree = cKDTree(np.c_[support_ys, support_xs])
    d, _ = tree.query(np.c_[dot_ys, dot_xs], k=1)
    return d <= radius


def main() -> int:
    stop_historical_runner('BLINDEXT')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=None, help="output stem (default timestamped)")
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = args.stem or f"gemsdoe92-blindext-{stamp}"
    tif_path = DOWNLOADS / f"{stem}-zeros.tif"

    log("0. Load pinned grid (footprint + catalogue from bridge files)")
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)

    log("1. Load h19_5 skeleton (mapped fault traces, 19GEMSDOE)")
    with rasterio.open(BRIDGE / "h19_5.tif") as ds:
        h19 = (ds.read(1) > 0) & foot
    log(f"   h19_5 pixels: {int(h19.sum())}")

    log("2. Find skeleton endpoints (fault-trace termini) -> blind-extension targets")
    endpoints = find_endpoints(h19)
    log(f"   endpoints: {int(endpoints.sum())}")
    d_endpoint = distance_transform_edt(~endpoints)

    log("3. Compute catalogue distance transform -> d_cat")
    d_cat = distance_transform_edt(~cat)

    log("4. Build candidate mask: footprint & ~catalogue & d_cat > 2.0 & "
        "d_endpoint <= 6 & ~h19_5")
    cand = foot & ~cat & (d_cat > CATALOGUE_CLEARANCE_PX) & (
        d_endpoint <= ENDPOINT_REACH_PX
    ) & ~h19
    n_cand = int(cand.sum())
    log(f"   candidate pixels: {n_cand:,}")
    if n_cand < N_DOTS:
        log(f"   WARNING: only {n_cand} candidates < {N_DOTS} requested dots")

    log("5. Score candidates: endpoint proximity within productive catalogue band")
    score = np.zeros(h19.shape, dtype=np.float64)
    in_band = (d_cat > PRODUCTIVE_CAT_BAND[0]) & (
        d_cat <= PRODUCTIVE_CAT_BAND[1]
    )
    score[cand & in_band] = np.exp(-d_endpoint[cand & in_band] / 3.0)
    cand_scores = score[cand]
    cand_ys, cand_xs = np.nonzero(cand)

    log("6. Non-maximum suppression: >= 2.83 px spacing, top score first")
    from scipy.spatial import cKDTree

    order = np.argsort(-cand_scores, kind="stable")
    chosen_ys = []
    chosen_xs = []
    tree = None
    REBUILD_EVERY = 500
    for oi in order:
        if len(chosen_ys) >= N_DOTS:
            break
        y, x = int(cand_ys[oi]), int(cand_xs[oi])
        if tree is not None:
            d, _ = tree.query(np.array([[y, x]]), k=1)
            if d[0] < MIN_DIST_PX:
                continue
        chosen_ys.append(y)
        chosen_xs.append(x)
        if len(chosen_ys) % REBUILD_EVERY == 0:
            tree = cKDTree(np.c_[chosen_ys, chosen_xs])
    if tree is None and chosen_ys:
        tree = cKDTree(np.c_[chosen_ys, chosen_xs])
    dots = np.zeros(h19.shape, dtype=np.float32)
    dots[chosen_ys, chosen_xs] = 1.0
    n_dots = int(dots.sum())
    log(f"   dots emitted: {n_dots:,}")
    dots_bool = dots > 0
    log(f"   on-catalogue: {int((dots_bool & cat).sum())}  outside-footprint: "
        f"{int((dots_bool & ~foot).sum())}  on-h19_5: {int((dots_bool & h19).sum())}")

    log("7. Package via grid.write_submission (zeros-outside, [0,1], pinned grid)")
    note = ("h33-h33-2-b2; BLINDEXT: blind-extension dots at h19_5 skeleton "
            "termini, d_cat 2-6px off catalogue; 37654 dots 2.83px spacing")
    if len(note) > 140:
        note = note[:137] + "..."
    name = f"GEMSDOE92-BLINDEXT-{stamp[:8]}"
    if len(name) > 140:
        name = name[:140]
    receipt = grid_mod.write_submission(
        tif_path, dots, mode="zeros",
    )
    # Add name/note to receipt (grid.write_submission doesn't take them; extend)
    receipt.update(
        submission_name=name,
        note=note,
        note_chars=len(note),
        lane="BLINDEXT",
        hypothesis="Blind extensions of mapped faults missing from USGS/INGENIOUS catalogue",
    )

    log("8. Independent disk re-read + format gates")
    from gems57.validate import validate, assert_submittable  # noqa: E402

    with rasterio.open(BRIDGE / "sample_submission.tif") as ref:
        footprint_ref = np.isfinite(ref.read(1).astype(np.float64))
    with rasterio.open(BRIDGE / "existing_faults.tif") as ds:
        catalogue_ref = (ds.read(1) > 0) & footprint_ref
    v = validate(tif_path, footprint_ref, catalogue_ref)
    assert_submittable(v)
    gate_results = run_gates(
        str(tif_path),
        str(BRIDGE / "sample_submission.tif"),
        str(BRIDGE / "existing_faults.tif"),
        prune_radius=2,
        require_submission_encoding=True,
    )
    gate_ok, gate_report = summarise(gate_results)
    log(f"   format gates: {'PASS' if gate_ok else 'FAIL'}")
    if not gate_ok:
        log(gate_report)

    log("9. Uniqueness vs local served rasters (literal + matched-budget + |rho|)")
    registry = []
    for d in (DOWNLOADS, RELEASES):
        for p in sorted(d.glob("*.tif")):
            registry.append((f"local:{p.relative_to(ROOT)}", p))
    # Exclude our own output if it somehow got scanned before
    registry = [(l, p) for l, p in registry if p.name != tif_path.name]
    log(f"   {len(registry)} local rasters")

    sub = np.sort(
        np.random.default_rng(20261026).choice(
            np.flatnonzero(foot), size=400_000, replace=False
        )
    )
    dots_bool = dots > 0
    dot_ys, dot_xs = np.nonzero(dots_bool)

    rows = []
    for label, path in registry:
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    rows.append(
                        dict(file=label, error="grid/band/transform mismatch")
                    )
                    continue
                raw = np.nan_to_num(
                    ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0
                )
        except Exception as exc:
            rows.append(dict(file=label, error=str(exc)[:80]))
            continue
        support = (raw > 0) & foot
        n_sup = int(support.sum())
        if n_sup == 0:
            rows.append(dict(file=label, error="empty support"))
            continue
        sy, sx = np.nonzero(support)
        lit = float(dots_within_radius(dot_ys, dot_xs, sy, sx, 3.0).mean())
        k = int(dots_bool.sum())
        if n_sup <= 150_000:
            mb_support = support
            rep = "dot_field"
        else:
            mb_support = matched_budget_support(raw, foot, k)
            rep = "continuous_surface"
        sy2, sx2 = np.nonzero(mb_support)
        mb = float(dots_within_radius(dot_ys, dot_xs, sy2, sx2, 3.0).mean())
        tv = raw.ravel()[sub]
        surf_sub = dots.astype(np.float64).ravel()[sub]
        rho_denom = np.ptp(surf_sub) and np.ptp(tv)
        rho = (
            float(__import__("scipy.stats", fromlist=["spearmanr"]).stats.spearmanr(surf_sub, tv).statistic)
            if rho_denom
            else float("nan")
        )
        rows.append(
            dict(
                file=label,
                their_dots=n_sup,
                my_dots=k,
                representation=rep,
                literal_forward_overlap=round(lit, 6),
                matched_budget_forward_overlap=round(mb, 6),
                spearman_surface=None if not np.isfinite(rho) else round(rho, 6),
            )
        )
        del raw, support

    checked = [r for r in rows if "error" not in r]
    if checked:
        worst_lit = max(checked, key=lambda r: r["literal_forward_overlap"])
        worst_mb = max(checked, key=lambda r: r["matched_budget_forward_overlap"])
        worst_rho = max(checked, key=lambda r: abs(r["spearman_surface"] or 0.0))
        dup_lit = worst_lit["literal_forward_overlap"] > 0.70
        dup_mb = worst_mb["matched_budget_forward_overlap"] > 0.70
        dup_rho = abs(worst_rho["spearman_surface"]) > 0.90
        duplicate = dup_lit or dup_mb or dup_rho
    else:
        worst_lit = worst_mb = worst_rho = {}
        dup_lit = dup_mb = dup_rho = False
        duplicate = False

    uniq = dict(
        evidence_class="REGISTRY-MEASUREMENT",
        rasters_checked=len(checked),
        worst_literal_forward_overlap=(
            float(worst_lit["literal_forward_overlap"]) if worst_lit else None
        ),
        worst_literal_file=(worst_lit["file"] if worst_lit else None),
        worst_matched_budget_forward_overlap=(
            float(worst_mb["matched_budget_forward_overlap"]) if worst_mb else None
        ),
        worst_matched_budget_file=(worst_mb["file"] if worst_mb else None),
        worst_abs_spearman=(abs(float(worst_rho["spearman_surface"])) if worst_rho else None),
        worst_abs_spearman_file=(worst_rho["file"] if worst_rho else None),
        duplicate=bool(duplicate),
        verdict="negative" if duplicate else "unique",
        notes=(
            "literal-overlap rule: >70% of dots within 3 px of one registry "
            "raster's dots => duplicate => stop; |rho| > 0.90 => duplicate"
        ),
    )
    log(f"   uniqueness: worst lit={uniq['worst_literal_forward_overlap']} "
        f"(<=0.70), worst mb={uniq['worst_matched_budget_forward_overlap']} "
        f"(<=0.70), |rho|={uniq['worst_abs_spearman']} (<=0.90), "
        f"duplicate={duplicate}")

    log("10. Write per-file audit JSON + Protocol Rule 5 run card")
    audit = dict(
        schema="gemsdoe92-blindext-audit.v1",
        lane="BLINDEXT",
        arm="primary",
        file=f"docs/downloads/{tif_path.name}",
        sha256=sha256_file(tif_path),
        bytes=int(tif_path.stat().st_size),
        submission_name=name,
        note=note,
        note_chars=len(note),
        generated_utc=stamp,
        validator=v,
        format_gates=[
            {"gate": r.name, "ok": bool(r.ok), "detail": r.detail} for r in gate_results
        ],
        gates_pass=bool(gate_ok),
        uniqueness_local=uniq,
        public_registry={
            "available": False,
            "reason": "102-repo GitHub API scan not run this session; local "
                      "registry (served + release rasters) scanned instead.",
        },
        holdout_dti={
            "evidence_class": "HOLDOUT-DTI",
            "available": False,
            "reason": "organizer withheld truth is not published; labels.tif is "
                      "the mapped-fault catalogue, not holdout truth. "
                      "vendor/gems57/evaluate_holdout.py cannot be scored "
                      "without the truth grid. Not projected as a score.",
        },
        leakage_canaries={
            "available": False,
            "reason": "single-feature leakage canaries require the 19-band "
                      "training stack (login-gated, not in this checkout). "
                      "BLINDEXT uses only h19_5 + catalogue masks, neither of "
                      "which reads withheld truth.",
        },
        raster_sha256=sha256_file(tif_path),
        zip_sha256=receipt.get("zip_sha256") if isinstance(receipt, dict) else None,
        dots=int(v["checks"].get("emitted_positive_pixels", n_dots)),
        checks=v["checks"],
    )
    audit_path = DOWNLOADS / f"{stem}-audit.json"
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    card = dict(
        schema="gemsdoe92-run-card.v3",
        lane="BLINDEXT",
        date=stamp,
        hypothesis=(
            "Blind normal faults in the Basin and Range extend beyond their "
            "mapped surface traces at depth. The USGS/INGENIOUS catalogue maps "
            "surface traces only; blind extensions are missing from it. Targeting "
            "h19_5 skeleton termini (fault-trace endpoints) within 6 px, off the "
            "catalogue (d_cat > 2.0 px), in the productive 2-6 px catalogue band, "
            "recovers blind extensions that are geologically continuous with mapped "
            "faults but absent from the catalogue."
        ),
        mechanism=(
            "S = exp(-d_endpoint / 3.0) restricted to footprint & ~catalogue & "
            "(d_cat > 2.0) & (d_endpoint <= 6) & ~h19_5, where d_endpoint is the "
            "Euclidean distance transform from h19_5 8-connectivity endpoints and "
            "d_cat is the catalogue distance transform. 37,654 dots selected by "
            "score-ranked non-maximum suppression at >= 2.83 px (~300 m, the DTI "
            "triangular-kernel radius). Pure array math on bridge masks; the "
            "catalogue is used only for masking, never to build features."
        ),
        named_non_fault_mimic=(
            "Mapped-fault splays and tip damage zones that are already in the "
            "catalogue (excluded by d_cat > 2.0); non-tectonic linear features "
            "(alluvial fan distributary channels, playa shorelines) that happen to "
            "lie near skeleton endpoints (partially mitigated by the d_endpoint "
            "reach limit and the off-catalogue requirement)."
        ),
        holdout_dti={
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2 (not executed)",
            "available": False,
            "reason": "organizer withheld truth not published; cannot compute "
                      "holdout DTI without truth grid. Not projected as a score.",
            "withheld_positives": None,
            "ci95": None,
        },
        correlation_overlap_vs_registry=uniq,
        raster_sha256=sha256_file(tif_path),
        zip_sha256=audit.get("zip_sha256"),
        file=f"docs/downloads/{tif_path.name}",
        validator_output=dict(
            no_nan_in_footprint=bool(v["checks"]["in_footprint_all_finite"]),
            values_in_0_1=bool(v["checks"]["range_0_1_guaranteed"]),
            crs_shape_transform_match=bool(
                v["checks"]["crs_epsg_32611"]
                and v["checks"]["dimensions_3730x3292"]
                and v["checks"]["transform_matches_sample_submission"]
            ),
            dots=int(v["checks"].get("emitted_positive_pixels", n_dots)),
            checks=v["checks"],
        ),
        submission_name=name,
        submission_note=note,
        note_chars=len(note),
        experiments_used="1/3",
        weekly_slots_used=0,
        verdict="negative",
        submission_eligible=False,
        verdict_reason=(
            f"format gates {'PASS' if gate_ok else 'FAIL'}; uniqueness "
            f"{'PASS' if not duplicate else 'FAIL'}; holdout DTI not computable "
            "(truth not published); literal dense-witness rule blocks all "
            "nonempty in-footprint candidates (pinned witness covers all "
            f"{int(foot.sum()):,} footprint cells). OK TO DOWNLOAD FOR RESEARCH, "
            f"DO NOT SUBMIT."
        ),
        organizer_confirmed=None,
        all_arms={
            "primary": dict(
                file=audit["file"],
                sha256=audit["sha256"],
                submission_name=name,
                note=note,
                note_chars=len(note),
                validator=v,
            )
        },
    )
    card_path = EVIDENCE / f"{stem}_run_card.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n", encoding="utf-8")
    (DOWNLOADS / f"{stem}_run_card.json").write_text(
        json.dumps(card, indent=2) + "\n", encoding="utf-8"
    )
    log(f"WROTE {card_path}")
    log(f"WROTE {audit_path}")
    log(f"TIF: {tif_path} (sha256 {sha256_file(tif_path)[:16]}...)")
    log(f"VERDICT: {card['verdict']} (submission_eligible={card['submission_eligible']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
