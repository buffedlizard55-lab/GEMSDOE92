#!/usr/bin/env python3
"""Fail closed if the public download site is mislabeled or has invalid TIFFs.

This checks every served zeros-outside raster against the local format gates,
verifies the primary bytes against their audit, and requires every linked or
archived TIFF/ZIP to say DO NOT SUBMIT while the current eligibility state is
negative. It also checks the current single-witness provenance receipt. This is
not a full public-registry scanner and does not certify global uniqueness.
"""
from __future__ import annotations

import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
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


class _AnchorParser(HTMLParser):
    """Small stdlib-only parser for visible anchor text and hrefs."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            attrs = dict(attrs)
            self._href = attrs.get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_entityref(self, name):
        if self._href is not None:
            self._text.append(unescape(f"&{name};"))

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.links.append((self._href, " ".join(" ".join(self._text).split())))
            self._href = None
            self._text = []


def _anchors(path: Path) -> list[tuple[str, str]]:
    parser = _AnchorParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.links


def _download_href(href: str) -> str | None:
    clean = href.split("#", 1)[0].split("?", 1)[0]
    if clean.startswith("./"):
        clean = clean[2:]
    if clean.startswith("docs/downloads/"):
        clean = clean.removeprefix("docs/")
    if clean.startswith("downloads/") and Path(clean).suffix.lower() in {".tif", ".tiff", ".zip"}:
        return clean
    return None


def _check_download_label(page: Path, href: str, label: str, problems: list[str]) -> None:
    resource = _download_href(href)
    if not resource:
        return
    if "DO NOT SUBMIT" not in label.upper():
        problems.append(f"{page.relative_to(ROOT)} download link lacks DO NOT SUBMIT: {href!r} ({label!r})")
    if not any(term in label.upper() for term in ("RESEARCH", "DIAGNOSTIC")):
        problems.append(f"{page.relative_to(ROOT)} download link lacks a research/diagnostic label: {href!r} ({label!r})")


def main() -> int:
    problems: list[str] = []

    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    html = INDEX.read_text(encoding="utf-8")
    index_links = _anchors(INDEX)

    # ---- page contract: keep download, holdout, and eligibility distinct -----
    for needle in ("OK TO DOWNLOAD", "Predicted values must be in range [0, 1]",
                   "HOLDOUT-DTI", "NOT CLEARED FOR A WEEKLY SLOT",
                   "DUPLICATE UNDER THE LITERAL REGISTRY RULE", "DO NOT SUBMIT"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if not re.search(r"(weekly slot|3/week|weekly competition slot|weekly cap)", html, re.I):
        problems.append("index.html carries no weekly-slot caution")
    if re.search(r'href="downloads/[^"]+-zeros\.tif"', html) is None:
        problems.append("index.html offers no zeros-outside download")
    if re.search(r"ORGANIZER-CONFIRMED[^<]{0,40}0\.00\d{4}", html):
        problems.append("holdout number labeled ORGANIZER-CONFIRMED")

    # Every TIFF/ZIP exposed anywhere on the site must carry its negative status
    # in the anchor itself; surrounding prose is not enough for an action link.
    status_pages = [INDEX, DOCS / "executive-summary.html", DOCS / "SUBMIT.html", DOCS / "submit.html"]
    for page in status_pages:
        if not page.is_file():
            problems.append(f"status page missing: {page.relative_to(ROOT)}")
            continue
        for href, label in _anchors(page):
            _check_download_label(page, href, label, problems)

    # README and the Markdown submission alias also expose direct download links.
    markdown_link = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for page in (ROOT / "README.md", DOCS / "SUBMIT.md"):
        if not page.is_file():
            problems.append(f"download status page missing: {page.relative_to(ROOT)}")
            continue
        text = page.read_text(encoding="utf-8")
        for label, href in markdown_link.findall(text):
            _check_download_label(page, href, label, problems)

    # Every file stored in the public download directory is listed from the
    # landing page with an explicit negative label, including diagnostic twins.
    public_payloads = sorted([*DOWNLOADS.glob("*.tif"), *DOWNLOADS.glob("*.tiff"), *DOWNLOADS.glob("*.zip")])
    by_href = {_download_href(href): label for href, label in index_links if _download_href(href)}
    for path in public_payloads:
        href = f"downloads/{path.name}"
        label = by_href.get(href)
        if label is None:
            problems.append(f"{path.name} is in the public download directory but not listed on index.html")
        elif "DO NOT SUBMIT" not in label.upper():
            problems.append(f"{path.name} is linked without DO NOT SUBMIT status")

    # ---- every served zeros-outside raster must pass the local MUST gates ----
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")

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

        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS), prune_radius=2))
        if not ok:
            problems.append(f"{tag}: gates failed\n{report}")
        else:
            print(f"  PASS {tag}  sha256 {sha256_file(path)[:16]}…")

    # ---- the primary named on the page must match its exact audit and card --
    m = re.search(r'href="(downloads/[^"]+-zeros\.tif)"', html)
    primary: Path | None = None
    primary_sha: str | None = None
    if m:
        primary = DOCS / m.group(1)
        if not primary.is_file():
            problems.append(f"index.html points at {m.group(1)}, which does not exist")
        else:
            primary_sha = sha256_file(primary)
            variant = primary.stem.removesuffix("-zeros")
            audit_path = primary.with_name(variant + "-audit.json")
            if not audit_path.is_file():
                problems.append(f"no audit receipt beside the primary: {audit_path.name}")
            else:
                doc = json.loads(audit_path.read_text())
                if doc.get("overall_pass") is not True:
                    problems.append("audit receipt does not record format_pass == true")
                if doc.get("sha256_zeros") != primary_sha:
                    problems.append("audit receipt sha256 != primary bytes on disk")
                bad = [g["name"] for g in doc.get("gates_zeros", []) if not g["ok"]]
                if bad:
                    problems.append(f"audit receipt records failing format gate(s): {bad}")
                if doc.get("submission_eligible") is not False:
                    problems.append("audit must say submission_eligible=false when the binding uniqueness gate fails")
                public = doc.get("public_registry_uniqueness", {})
                if public.get("candidate_hash_matches_scan") is not True:
                    problems.append("public registry audit is absent or not for these exact candidate bytes")
                if public.get("unique_under_literal_rule") is not False or public.get("stop_required") is not True:
                    problems.append("site audit must preserve the literal duplicate stop verdict")
            card_rel = doc.get("run_card")
            card_path = (ROOT / card_rel) if card_rel else (ROOT / "evidence" / "visible_collar_run_card.json")
            if not card_path.is_file():
                problems.append(f"primary run card missing: {card_path}")
            else:
                card = json.loads(card_path.read_text())
                if card.get("raster_sha256") != primary_sha:
                    problems.append("run card SHA256 != primary bytes")
                if card.get("verdict") != "negative":
                    problems.append("run card must record negative verdict after registry duplicate stop")
            print(f"  PRIMARY {primary.name}")

    # The fresh current status receipt must agree with the exact primary bytes.
    witness_path = DOWNLOADS / "public_witness_anasig.json"
    current_card_path = DOWNLOADS / "current_registry_stop_run_card_20261024.json"
    if primary is None or primary_sha is None:
        problems.append("current primary was not resolved; cannot verify provenance receipts")
    else:
        try:
            witness_doc = json.loads(witness_path.read_text(encoding="utf-8"))
            candidate = witness_doc.get("candidate", {})
            witness = witness_doc.get("witness", {})
            comparison = witness_doc.get("postplacement_candidate_comparison", {})
            if candidate.get("sha256") != primary_sha:
                problems.append("fresh witness candidate SHA does not match primary bytes")
            if witness_doc.get("evidence_class", "").startswith("REGISTRY-MEASUREMENT") is False:
                problems.append("fresh witness receipt is not labeled REGISTRY-MEASUREMENT")
            if witness.get("positive_fraction_of_footprint") != 1.0:
                problems.append("fresh witness receipt no longer proves full-footprint positive support")
            if comparison.get("forward_overlap_candidate_dots_within_3px_of_witness", 0) <= 0.70:
                problems.append("fresh witness receipt does not record a binding >70% overlap")
            if comparison.get("stop_required_vs_this_witness") is not True:
                problems.append("fresh witness receipt does not record the literal stop")
            if witness.get("uncovered_allowed_pixels_in_3px_halo") != 0:
                problems.append("fresh witness receipt does not certify complete allowed-domain halo coverage")
            if witness_doc.get("scope", "").find("not a full public scan") < 0:
                problems.append("fresh witness receipt must state its single-witness/non-full-scan scope")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            problems.append(f"fresh public-witness receipt invalid or missing: {exc}")
        try:
            current = json.loads(current_card_path.read_text(encoding="utf-8"))
            if current.get("candidate", {}).get("raster_sha256") != primary_sha:
                problems.append("current run-card SHA does not match primary bytes")
            if current.get("candidate", {}).get("new_candidate_generated_this_review") is not False:
                problems.append("current run card must say no new candidate was generated")
            if current.get("candidate", {}).get("submission_status") != "NOT CLEARED; DO NOT SUBMIT":
                problems.append("current run card must preserve explicit do-not-submit status")
            if current.get("verdict") != "negative":
                problems.append("current run card must record a negative verdict")
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            problems.append(f"current status run card invalid or missing: {exc}")

    if problems:
        print("SITE CHECK FAIL")
        for problem in problems:
            print(" -", problem)
        return 1
    print(f"SITE CHECK PASS ({len(served)} served zeros-outside rasters gated; {len(public_payloads)} TIFF/ZIP downloads labeled DO NOT SUBMIT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
