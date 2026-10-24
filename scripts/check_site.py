#!/usr/bin/env python3
"""Fail closed if a served research download is missing, out of range, or mislabeled.

Derives the primary from its explicit ``data-primary`` section and gates every
served zeros-outside raster. It also requires the homepage to distinguish
format-valid research downloads from submission eligibility. Format validity
never overrides a negative scientific or registry verdict.
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

    # ---- page contract: download status, no-submit status, and explicit primary --
    for needle in ("OK TO DOWNLOAD", "FOR RESEARCH ONLY", "DO NOT SUBMIT",
                   "Predicted values must be in range [0, 1]", "HOLDOUT-DTI",
                   "NOT CLEARED FOR A WEEKLY SLOT",
                   "DUPLICATE UNDER THE LITERAL REGISTRY RULE"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    hero = html.split("</header>", 1)[0]
    if "No GeoTIFF is cleared for competition submission" not in hero:
        problems.append("homepage hero must state that no file is cleared to submit")
    if "SUBMISSION STATUS: NO" not in hero:
        problems.append("homepage hero must distinguish research download from submission status")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|human step)", html, re.I):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^"]+-zeros\.tif"', html) is None:
        problems.append("index.html offers no zeros-outside download")
    primary_sections = re.findall(
        r'<section\b(?=[^>]*\bdata-primary="true")[^>]*>(.*?)</section>',
        html, flags=re.S)
    if len(primary_sections) != 1:
        problems.append(f"index.html must declare exactly one data-primary section; found {len(primary_sections)}")
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
                expected_dots = int(audit_doc.get("n_positive_pixels",
                                      audit_doc.get("raster", {}).get("positive_pixels",
                                      audit_doc.get("n_dots", N_DOTS))))
            except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
                problems.append(f"{tag}: invalid per-file audit receipt: {exc}")
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

    # ---- the explicitly declared primary must match its audit and run card ---
    primary = None
    if len(primary_sections) == 1:
        links = re.findall(r'href="(downloads/[^"]+-zeros\.tif)"', primary_sections[0])
        if len(links) != 1:
            problems.append(f"data-primary section must contain exactly one zeros-outside TIFF link; found {len(links)}")
        else:
            primary = DOCS / links[0]
            if not primary.is_file():
                problems.append(f"index.html points at {links[0]}, which does not exist")
                primary = None

    if primary is not None:
        variant = primary.stem.removesuffix("-zeros")
        audit_path = primary.with_name(variant + "-audit.json")
        audit_doc = None
        if not audit_path.is_file():
            problems.append(f"no audit receipt beside the primary: {audit_path.name}")
        else:
            try:
                parsed = json.loads(audit_path.read_text(encoding="utf-8"))
                if not isinstance(parsed, dict):
                    raise ValueError("audit root must be a JSON object")
                audit_doc = parsed
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                problems.append(f"invalid primary audit receipt {audit_path.name}: {exc}")

        if audit_doc is not None:
            if audit_doc.get("overall_pass") is not True:
                problems.append("audit receipt does not record format validation pass")
            if audit_doc.get("sha256_zeros") != sha256_file(primary):
                problems.append("audit receipt sha256 != primary bytes on disk")
            gates = audit_doc.get("gates_zeros", [])
            if not isinstance(gates, list):
                problems.append("audit receipt gates_zeros must be a list")
            else:
                bad = []
                for gate in gates:
                    if not isinstance(gate, dict):
                        bad.append("<invalid gate record>")
                    elif gate.get("ok") is not True:
                        bad.append(gate.get("name", "<unnamed>"))
                if bad:
                    problems.append(f"audit receipt records failing format gate(s): {bad}")
            if audit_doc.get("submission_eligible") is not False:
                problems.append("audit must say submission_eligible=false when the binding uniqueness gate fails")
            public = audit_doc.get("public_registry_uniqueness", {})
            if not isinstance(public, dict):
                problems.append("public registry uniqueness audit must be an object")
                public = {}
            if public.get("candidate_hash_matches_scan") is not True:
                problems.append("public registry audit is absent or not for these exact candidate bytes")
            if public.get("unique_under_literal_rule") is not False or public.get("stop_required") is not True:
                problems.append("site audit must preserve the literal duplicate stop verdict (binding public witness or full-scan duplicate)")

            card_rel = audit_doc.get("run_card")
            card_path = ROOT / card_rel if isinstance(card_rel, str) else ROOT / "evidence" / "visible_collar_run_card.json"
            if not card_path.is_file():
                problems.append(f"primary run card missing: {card_path}")
            else:
                try:
                    card = json.loads(card_path.read_text(encoding="utf-8"))
                    if not isinstance(card, dict):
                        raise ValueError("run card root must be a JSON object")
                    if card.get("raster_sha256") != sha256_file(primary):
                        problems.append("run card SHA256 != primary bytes")
                    if card.get("verdict") != "negative":
                        problems.append("run card must record negative verdict after registry duplicate stop")
                except (OSError, ValueError, json.JSONDecodeError) as exc:
                    problems.append(f"invalid primary run card {card_path}: {exc}")
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
