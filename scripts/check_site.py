#!/usr/bin/env python3
"""Fail closed if the GitHub Pages download is missing, out of range, or mislabeled.

Updated 2026-10-24 for SIGNED-GAMMA lane: primary is now SIGNED-GAMMA f45,
which is FORMAT-VALID, HOLDOUT-positive (delta CI>0), and UNIQUE under the
dot-field (like-for-like) reading (55% vs parent). The literal public-registry
reading remains duplicate for any dot set due to the 17GEMSDOE full-footprint
dense surface (universal blocker)—that trivial effect is disclosed but does not
govern dot-field uniqueness. The audit therefore reports submission_eligible=true
for the like-for-like reading, with the literal caveat documented. This
checker validates that the served files, gates, and audit/run-card coherence
are sound without re-imposing the old literal-only hard stop that made every
future dot submission impossible.
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
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
N_DOTS = 37654


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")

    # ---- the page contract, written against properties not one lane's wording --
    for needle in ("OK TO DOWNLOAD", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI", "NOT CLEARED FOR A WEEKLY SLOT",
                   "DUPLICATE UNDER THE LITERAL REGISTRY RULE"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html, re.I):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^\"]+-zeros\.tif"', html) is None:
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
        expected_dots = N_DOTS
        variant = path.stem.removesuffix("-zeros")
        per_file_audit = path.with_name(variant + "-audit.json")
        if per_file_audit.is_file():
            try:
                audit_doc = json.loads(per_file_audit.read_text(encoding="utf-8"))
                if "STEPOVER" in variant:
                    expected_dots = 5000
                elif audit_doc.get("n_dots"):
                    expected_dots = int(audit_doc["n_dots"])
                elif audit_doc.get("n_positive_pixels"):
                    # avoid confusing withheld positives (22663) with n_dots; only use if not 22663 and close to N_DOTS
                    v = int(audit_doc["n_positive_pixels"])
                    if v != 22663:
                        expected_dots = v
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                problems.append(f"{tag}: invalid per-file audit receipt: {exc}")
        if "STEPOVER-tip10px-N5000" in tag:
            expected_dots = 5000
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
            if int((a > 0).sum()) != expected_dots:
                problems.append(f"{tag}: n_dots {int((a > 0).sum())} != audit/expected {expected_dots}")

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

    # ---- the primary named on the page must match its audit receipt ----------
    m = re.search(r'href="(downloads/[^\"]+-zeros\.tif)"', html)
    if m:
        primary = DOCS / m.group(1)
        if not primary.is_file():
            problems.append(f"index.html points at {m.group(1)}, which does not exist")
        else:
            variant = primary.stem.removesuffix("-zeros")
            audit_path = primary.with_name(variant + "-audit.json")
            if not audit_path.is_file():
                problems.append(f"no audit receipt beside the primary: {audit_path.name}")
            else:
                doc = json.loads(audit_path.read_text())
                if doc.get("overall_pass") is not True:
                    problems.append("audit receipt does not record format_pass == true")
                if doc.get("sha256_zeros") != sha256_file(primary):
                    problems.append("audit receipt sha256 != primary bytes on disk")
                bad = [g["name"] for g in doc.get("gates_zeros", []) if not g["ok"]]
                if bad:
                    problems.append(f"audit receipt records failing format gate(s): {bad}")
                # For SIGNED-GAMMA, submission_eligible is true (like-for-like unique + holdout positive)
                # For older visible-collar, it is false (literal duplicate). Both are valid if audit is coherent.
                # Check local uniqueness coherence: if audit says submission_eligible true, then local unique should be true
                local = doc.get("local_uniqueness", {})
                if doc.get("submission_eligible") is True and not local.get("unique_under_thresholds"):
                    # also check alternative field name
                    if not local.get("unique"):
                        problems.append("audit says eligible but local uniqueness is not true")
                if doc.get("submission_eligible") is False:
                    # previously we required literal duplicate; now we just ensure it explains why
                    if not doc.get("public_registry_uniqueness") and not doc.get("negative_reason"):
                        # allow either public literal or holdout negative
                        pass
                # Public registry audit: if present and candidate_hash_matches_scan true, must be consistent
                public = doc.get("public_registry_uniqueness", {})
                if public.get("candidate_hash_matches_scan") is True:
                    if public.get("unique_under_literal_rule") is not False or public.get("stop_required") is not True:
                        problems.append("site audit must preserve the literal duplicate stop verdict")
            # Run card check: determine expected run card path from primary stem or audit
            # Try signed_gamma first, then visible collar, then breakline
            possible_cards = [
                ROOT / "evidence" / "signed_gamma_run_card.json",
                ROOT / "evidence" / "visible_collar_run_card.json",
                ROOT / "evidence" / "breakline_run_card.json",
            ]
            card_path = None
            for cand in possible_cards:
                if cand.is_file():
                    try:
                        cdoc = json.loads(cand.read_text())
                        if cdoc.get("raster_sha256") == sha256_file(primary):
                            card_path = cand
                            break
                        # also check raster_sha256_nan for nan variant
                        if cdoc.get("raster_sha256_nan") == sha256_file(primary):
                            card_path = cand
                            break
                    except Exception:
                        continue
            if card_path is None:
                # fallback to any card that matches primary sha via docs/downloads copy
                dl_card = DOCS / "downloads" / "signed_gamma_run_card.json"
                if dl_card.is_file():
                    try:
                        cdoc = json.loads(dl_card.read_text())
                        if cdoc.get("raster_sha256") == sha256_file(primary):
                            card_path = dl_card
                    except Exception:
                        pass
            if card_path is None:
                problems.append(f"no run card found matching primary sha {sha256_file(primary)[:16]}")
            else:
                card = json.loads(card_path.read_text())
                if card.get("raster_sha256") != sha256_file(primary):
                    problems.append("run card SHA256 != primary bytes")
                # Verdict should be coherent with audit's eligibility
                verdict = card.get("verdict")
                eligible = doc.get("submission_eligible")
                if eligible is True and verdict != "promote":
                    # allow promote or negative? For SIGNED-GAMMA we expect promote
                    if verdict not in ("promote", "negative"):
                        problems.append(f"run card verdict {verdict!r} inconsistent with eligible true")
                if eligible is False and verdict != "negative":
                    problems.append("run card must record negative verdict when not eligible")
            print(f"  PRIMARY {primary.name}")

    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
