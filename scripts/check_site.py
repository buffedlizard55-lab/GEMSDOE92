#!/usr/bin/env python3
"""Run local site preflight and disclose promotion status without conflating them.

This checker gates every served zeros-outside raster for local range/geometry
properties, verifies the primary audit hash, and screens the primary against
parent R0. A pass is not official submission acceptance: the official problem
page specifies null/NaN outside the bounds, while these diagnostic files use
zeros there. It never claims global uniqueness from the parent-only screen.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.uniqueness import dot_overlap, surface_rho  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
N_DOTS = 37654
PARENT_R0 = ROOT / "data" / "parent_R0_zeros.tif"
RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70


def measure_primary_uniqueness(primary: Path, footprint: np.ndarray) -> dict:
    """Screen the site's primary against parent R0; never claim global uniqueness.

    Parent R0 is a known registry raster, so a single threshold breach is enough
    to block promotion. Passing this one comparison is NOT global clearance: a
    separate complete, hash-pinned registry audit is required for promotion.
    """
    if not PARENT_R0.is_file():
        return {"status": "INDETERMINATE_BLOCK", "reason": "parent R0 is unavailable"}
    with rasterio.open(primary) as ds:
        candidate = ds.read(1).astype(np.float32, copy=False)
    with rasterio.open(PARENT_R0) as ds:
        parent = ds.read(1).astype(np.float32, copy=False)
    if candidate.shape != footprint.shape or parent.shape != footprint.shape:
        return {"status": "INDETERMINATE_BLOCK", "reason": "candidate/parent grid mismatch"}
    rho = surface_rho(candidate, parent, footprint)["spearman_full_footprint"]
    overlap = dot_overlap(candidate, parent)
    reasons = []
    if rho is None or not np.isfinite(rho):
        reasons.append("rank correlation unavailable")
    elif rho > RHO_LIMIT:
        reasons.append(f"Spearman {rho:.6f} > {RHO_LIMIT:.2f}")
    if overlap > OVERLAP_LIMIT:
        reasons.append(f"within-3px dot overlap {overlap:.6%} > {OVERLAP_LIMIT:.0%}")
    return {
        "status": "DUPLICATE_STOP" if reasons else "NOT_GLOBALLY_CLEARED",
        "spearman_full_footprint": rho,
        "candidate_dots_within_3px_of_R0": overlap,
        "reasons": reasons,
        "scope": "parent R0 only; a pass is not global uniqueness clearance",
    }


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")
    print("OFFICIAL FORMAT ACCEPTANCE UNRESOLVED — local zeros-outside diagnostics differ from the problem page's null/NaN outside-bounds requirement")

    # ---- the page contract, written against properties not one lane's wording --
    for needle in ("OK TO DOWNLOAD FOR REVIEW", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI", "null/NaN",
                   "NOT CLEARED / NOT RECOMMENDED FOR COMPETITION SUBMISSION"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^"]+-zeros\.tif"', html) is None:
        problems.append("index.html offers no zeros-outside download")
    # a HOLDOUT number must never be dressed as an organizer receipt
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.00\d{4}", html):
        problems.append("holdout number labeled ORGANIZER-CONFIRMED")

    # ---- every served zeros-outside raster must be linked AND pass the gates ---
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    for path in served:
        if f"downloads/{path.name}" not in html:
            problems.append(f"{path.name} is served but not linked from index.html")

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5

    for path in served:
        tag = path.name
        with rasterio.open(path) as ds:
            a = ds.read(1)
            if ds.dtypes[0] != "float32" or ds.count != 1:
                problems.append(f"{tag}: dtype/band")
            if not np.isfinite(a).all():
                problems.append(f"{tag}: NaN/inf present (portal [0,1] risk)")
            if a.min() < 0 or a.max() > 1:
                problems.append(f"{tag}: values [{a.min()}, {a.max()}]")
            if np.any((a > 0) & ~footprint):
                problems.append(f"{tag}: mass outside footprint")
            if np.any(a[cat] > 0):
                problems.append(f"{tag}: mass on catalogue")
            if int((a > 0).sum()) != N_DOTS:
                problems.append(f"{tag}: n_dots {int((a > 0).sum())} != {N_DOTS}")

        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{tag}: {exc}")

        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS),
                                         prune_radius=2))
        if not ok:
            problems.append(f"{tag}: gates failed\n{report}")
        else:
            print(f"  PASS {tag}  sha256 {sha256_file(path)[:16]}…")

    # ---- the primary named on the page must match its local format audit ----
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    if m:
        primary = DOCS / m.group(1)
        if not primary.is_file():
            problems.append(f"index.html points at {m.group(1)}, which does not exist")
        else:
            variant = primary.stem.removesuffix("-zeros")
            audit_path = primary.with_name(variant + "-audit.json")
            if not audit_path.is_file():
                problems.append(f"no local format-audit JSON beside the primary: {audit_path.name}")
            else:
                doc = json.loads(audit_path.read_text())
                if doc.get("overall_pass") is not True:
                    problems.append("format-audit JSON does not record overall_pass == true")
                if doc.get("sha256_zeros") != sha256_file(primary):
                    problems.append("format-audit SHA-256 != primary bytes on disk")
                bad = [g["name"] for g in doc.get("gates_zeros", []) if not g["ok"]]
                if bad:
                    problems.append(f"format-audit JSON records failing gates: {bad}")
            uniqueness = measure_primary_uniqueness(primary, footprint)
            if uniqueness["status"] == "DUPLICATE_STOP":
                print("  PROMOTION BLOCKED — DUPLICATE STOP against registry parent R0")
                print(f"    Spearman={uniqueness.get('spearman_full_footprint')}; "
                      f"candidate dots within 3 px={uniqueness.get('candidate_dots_within_3px_of_R0'):.6%}")
                for reason in uniqueness["reasons"]:
                    print(f"    {reason}")
            else:
                print("  PROMOTION NOT CLEARED — parent comparison did not establish global uniqueness")
                print(f"    {uniqueness}")
            print(f"  PRIMARY {primary.name}")

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE FORMAT CHECK PASS ({len(served)} served raster(s) gated); promotion status reported separately above)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
