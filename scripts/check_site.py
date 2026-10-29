#!/usr/bin/env python3
"""Fail closed if the published site (v3, 2026-10-27) is stale, inconsistent or unsafe.

Contract
--------
* docs/index.html, docs/nine-sites.html, index.html and generated status JSON feeds
  are byte-identical to ``scripts/render_site_v3.render()`` (generated from evidence).
* The manually maintained docs/how-to-submit.html and docs/executive-summary.html
  retain the historical audit record but must explicitly show the current negative
  BLINDCORRIDOR decision; they are checked for contradictory upload copy.
* docs/index.html declares exactly one ``data-primary="true"`` local
  ``downloads/*-zeros.tif``; the file exists and passes the shared format gates
  (submission encoding: all finite, [0,1], zeros outside the footprint, CRS/shape/
  transform equal to the sample, zero mass on mapped faults) and gems57 validate.
* Its per-file audit and run card are bound to the exact bytes (SHA-256), agree
  on the verdict, and the page says OK TO SUBMIT iff the verdict is ``promote``.
* Every served ``docs/downloads/*-zeros.tif`` passes the format gates and is
  linked from docs/index.html or docs/archive.html.
* The historical TIPCOMP status feed, run card, research TIFF, summary and
  archive copy remain hash-bound and explicitly negative / DO NOT SUBMIT.
* The BLINDCORRIDOR format-pass-only feed is hash-bound to its run card and audit,
  remains not submission-eligible, and states that holdout, canaries and the full
  registry audit are absent or unresolved.
The legacy (literal-stop) checker is preserved as scripts/check_site_legacy_20261026.py.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

import numpy as np  # noqa: E402
import rasterio  # noqa: E402

from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402

DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"
INDEX = DOCS / "index.html"
ARCHIVE = DOCS / "archive.html"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"


class _Anchors(HTMLParser):
    def __init__(self):
        super().__init__()
        self.primaries = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and ("data-primary", "true") in attrs:
            self.primaries.append(dict(attrs))


def primary_download(html: str, problems: list[str]) -> str | None:
    p = _Anchors(); p.feed(html)
    if len(p.primaries) != 1:
        problems.append("index.html must declare exactly one data-primary=true download")
        return None
    href = p.primaries[0].get("href", "")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.tif", href):
        problems.append("primary must be a local downloads/*-zeros.tif file")
        return None
    return href


def _audit_path(tif: Path) -> Path:
    for name in (tif.stem + "-audit.json", tif.name[: -len("-zeros.tif")] + "-audit.json"):
        p = tif.with_name(name)
        if p.is_file():
            return p
    return tif.with_name(tif.stem + "-audit.json")


def check_rendered(problems: list[str]) -> None:
    try:
        import render_site_v3
        for path, text in render_site_v3.render().items():
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                problems.append(f"stale generated page: {path.relative_to(ROOT)} (run scripts/render_site_v3.py)")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"site evidence invalid: {exc}")


def check_primary(html: str, problems: list[str]) -> None:
    rel = primary_download(html, problems)
    if not rel:
        return
    tif = DOCS / rel
    if not tif.is_file():
        problems.append(f"primary {rel} does not exist")
        return
    digest = sha256_file(tif)
    audit = json.loads(_audit_path(tif).read_text(encoding="utf-8")) if _audit_path(tif).is_file() else {}
    if not audit:
        problems.append("primary per-file audit missing")
        return
    if audit.get("sha256_zeros") != digest:
        problems.append("primary audit sha256 != primary bytes")
    if audit.get("overall_pass") is not True:
        problems.append("primary audit does not record overall_pass == true")
    rows = audit.get("gates_zeros")
    if not isinstance(rows, list) or not rows or any(r.get("ok") is not True for r in rows):
        problems.append("primary audit gates missing or failing")
    card_path = ROOT / str(audit.get("run_card", ""))
    if not card_path.is_file():
        problems.append("primary run card missing")
        return
    card = json.loads(card_path.read_text(encoding="utf-8"))
    if card.get("raster_sha256") != digest:
        problems.append("run card sha256 != primary bytes")
    verdict = card.get("verdict")
    # Never let a self-declared promotion override mandatory scientific gates.
    if verdict == "promote" or card.get("submission_eligible") is True:
        gates = card.get("gates_passed", {})
        literal = card.get("uniqueness", {}).get("literal_reading", {})
        if gates.get("catalogue_holdout_beats_r0_recipe") is not True:
            problems.append("promotion blocked: required R0 holdout gate is not true")
        if literal.get("duplicate_under_literal") is not False:
            problems.append("promotion blocked: literal registry duplicate or missing evidence")
        overlap = card.get("uniqueness", {}).get("surface_worst_overlap")
        if not isinstance(overlap, (float, int)) or isinstance(overlap, bool) or not 0 <= overlap <= .70:
            problems.append("promotion blocked: pre-placement overlap missing or above limit")
    if verdict not in ("promote", "negative"):
        problems.append("run card verdict must be promote or negative")
    if audit.get("verdict") != verdict or audit.get("submission_eligible") is not card.get("submission_eligible"):
        problems.append("audit and run card disagree on verdict/eligibility")
    for key in ("hypothesis", "mechanism", "named_non_fault_mimic", "holdout_dti", "uniqueness",
                "validator_output", "submission_name", "note"):
        if key not in card:
            problems.append(f"run card missing required field: {key}")
    if not 0 < len(card.get("note", "")) <= 140:
        problems.append("run card note must be 1..140 characters")
    box = html.split('id="submit-now"', 1)[-1].split("</section>", 1)[0]
    if verdict == "promote" and card.get("submission_eligible") is True:
        if "OK TO SUBMIT" not in box or "DO NOT SUBMIT" in box:
            problems.append("eligible primary is not clearly marked OK TO SUBMIT")
    elif "DO NOT SUBMIT" not in box or "OK TO SUBMIT" in box:
        problems.append("non-eligible primary is not clearly marked DO NOT SUBMIT")
    cur = json.loads((DOWNLOADS / "current_submission.json").read_text(encoding="utf-8"))
    rdy = json.loads((DOWNLOADS / "readiness.json").read_text(encoding="utf-8"))
    if cur.get("file") != f"docs/{rel}" or rdy.get("file") != rel:
        problems.append("status JSON files do not point at the primary")
    if cur.get("sha256") != digest or rdy.get("raster_sha256") != digest:
        problems.append("status JSON SHA-256 != primary bytes")
    if cur.get("ok_to_submit") is not rdy.get("submission_eligible") or cur.get("ok_to_submit") is not card.get("submission_eligible"):
        problems.append("status JSON eligibility disagrees with run card")
    if cur.get("submission_name") != card.get("submission_name") or rdy.get("note") != card.get("note"):
        problems.append("status JSON name/note disagree with run card")
    print(f"  PRIMARY {tif.name} sha256 {digest[:16]}… verdict={verdict}")


def check_tipcomp_history(problems: list[str]) -> None:
    """Keep the historical TIPCOMP download/status copy fail-closed.

    This is not a candidate promotion path: its stored verdict must remain
    negative, and its historical page/archive must never invite a selector
    decision or imply global uniqueness.
    """
    status_path = DOWNLOADS / "tipcomp_readiness_20261028.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"TIPCOMP readiness feed missing or invalid: {exc}")
        return

    rel = status.get("file", "")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.tif", rel):
        problems.append("TIPCOMP status file must be a local downloads/*-zeros.tif")
        return
    tif = DOCS / rel
    if not tif.is_file():
        problems.append(f"TIPCOMP research TIFF missing: {rel}")
        return
    digest = sha256_file(tif)
    if status.get("raster_sha256") != digest:
        problems.append("TIPCOMP readiness SHA-256 != research TIFF bytes")

    card_name = status.get("run_card", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+_run_card\.json", card_name):
        problems.append("TIPCOMP status must point to a local run card")
        return
    card_path = DOWNLOADS / card_name
    try:
        card = json.loads(card_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"TIPCOMP run card missing or invalid: {exc}")
        return
    if card.get("raster_sha256") != digest:
        problems.append("TIPCOMP run-card SHA-256 != research TIFF bytes")
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        problems.append("TIPCOMP must remain negative and not submission-eligible")
    if status.get("verdict") != "negative" or status.get("submission_eligible") is not False:
        problems.append("TIPCOMP readiness must remain negative and not submission-eligible")
    if status.get("download_status") != "OK TO DOWNLOAD FOR RESEARCH ONLY":
        problems.append("TIPCOMP download status must explicitly say research only")
    if not str(status.get("submission_status", "")).startswith("DO NOT SUBMIT"):
        problems.append("TIPCOMP status must explicitly say DO NOT SUBMIT")
    if status.get("submission_name") != card.get("submission_name") or status.get("note") != card.get("note"):
        problems.append("TIPCOMP status name/note disagree with run card")
    if not 0 < len(str(status.get("note", ""))) <= 140:
        problems.append("TIPCOMP metadata note must be 1..140 characters")

    summary_name = status.get("executive_summary", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.html", summary_name):
        problems.append("TIPCOMP executive summary path must be local")
        return
    summary_path = DOCS / summary_name
    try:
        summary = summary_path.read_text(encoding="utf-8")
    except OSError as exc:
        problems.append(f"TIPCOMP executive summary missing: {exc}")
        return
    for phrase in ("DO NOT SUBMIT", "OK TO DOWNLOAD FOR RESEARCH ONLY", "HOLDOUT-DTI", "MODEL"):
        if phrase not in summary:
            problems.append(f"TIPCOMP executive summary missing {phrase!r}")
    stale = ("SELECTOR DECISION REQUIRED", "Download; selector decides slot", "PI-1 unique", "Unique (PI-1")
    for phrase in stale:
        if phrase.lower() in summary.lower():
            problems.append(f"TIPCOMP executive summary contains stale promotion copy {phrase!r}")

    if not ARCHIVE.is_file():
        problems.append("historical archive missing while TIPCOMP TIFF is served")
        return
    archive = ARCHIVE.read_text(encoding="utf-8")
    needle = f'href="{rel}"'
    idx = archive.find(needle)
    if idx < 0:
        problems.append("TIPCOMP TIFF is not linked from the historical archive")
        return
    begin = archive.rfind("<section", 0, idx)
    finish = archive.find("</section>", idx)
    section = archive[begin:finish + len("</section>")] if begin >= 0 and finish >= 0 else ""
    for phrase in ("DO NOT SUBMIT", "submission_eligible: false", "HOLDOUT-DTI", "MODEL"):
        if phrase.lower() not in section.lower():
            problems.append(f"TIPCOMP archive status missing {phrase!r}")
    for phrase in stale:
        if phrase.lower() in section.lower():
            problems.append(f"TIPCOMP archive contains stale promotion copy {phrase!r}")
    print(f"  HISTORICAL {tif.name} sha256 {digest[:16]}… verdict=negative (research only)")


def check_blindcorridor_history(problems: list[str]) -> None:
    """Keep BLINDCORRIDOR visibly format-only and tied to its exact bytes."""
    status_path = DOWNLOADS / "blindcorridor_readiness_20261028.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"BLINDCORRIDOR readiness feed missing or invalid: {exc}")
        return

    rel = status.get("file", "")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.tif", rel):
        problems.append("BLINDCORRIDOR status file must be a local downloads/*-zeros.tif")
        return
    tif = DOCS / rel
    if not tif.is_file():
        problems.append(f"BLINDCORRIDOR research TIFF missing: {rel}")
        return
    digest = sha256_file(tif)
    if status.get("raster_sha256") != digest:
        problems.append("BLINDCORRIDOR readiness SHA-256 != research TIFF bytes")
    zip_rel = status.get("zip", "")
    if not re.fullmatch(r"downloads/[A-Za-z0-9_.-]+-zeros\.zip", zip_rel):
        problems.append("BLINDCORRIDOR ZIP path must be a local downloads/*-zeros.zip")
        return
    zip_path = DOCS / zip_rel
    if not zip_path.is_file():
        problems.append(f"BLINDCORRIDOR research ZIP missing: {zip_rel}")
        return
    if status.get("zip_sha256") != sha256_file(zip_path):
        problems.append("BLINDCORRIDOR readiness ZIP SHA-256 != ZIP bytes")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if not name.endswith("/")]
            if len(members) != 1 or Path(members[0]).name != tif.name:
                problems.append("BLINDCORRIDOR ZIP must contain exactly its single bound TIFF")
            elif hashlib.sha256(archive.read(members[0])).hexdigest() != digest:
                problems.append("BLINDCORRIDOR ZIP payload SHA-256 != research TIFF bytes")
    except (OSError, zipfile.BadZipFile) as exc:
        problems.append(f"BLINDCORRIDOR ZIP is invalid: {exc}")

    card_name = status.get("run_card", "")
    audit_name = status.get("audit", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+_run_card\.json", card_name):
        problems.append("BLINDCORRIDOR status must point to a local run card")
        return
    if not re.fullmatch(r"[A-Za-z0-9_.-]+-audit\.json", audit_name):
        problems.append("BLINDCORRIDOR status must point to a local format audit")
        return
    try:
        card = json.loads((DOWNLOADS / card_name).read_text(encoding="utf-8"))
        audit = json.loads((DOWNLOADS / audit_name).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"BLINDCORRIDOR run card or audit missing/invalid: {exc}")
        return
    if card.get("raster_sha256") != digest or audit.get("sha256_zeros") != digest:
        problems.append("BLINDCORRIDOR run-card/audit SHA-256 != research TIFF bytes")
    if card.get("verdict") != "format_pass" or card.get("submission_eligible") is not False:
        problems.append("BLINDCORRIDOR run card must remain format_pass and not eligible")
    if audit.get("verdict") != "format_pass" or audit.get("submission_eligible") is not False:
        problems.append("BLINDCORRIDOR format audit must remain format_pass and not eligible")
    if status.get("verdict") != "format_pass" or status.get("submission_eligible") is not False:
        problems.append("BLINDCORRIDOR readiness feed must remain format_pass and not eligible")
    if status.get("download_status") != "OK TO DOWNLOAD FOR RESEARCH ONLY":
        problems.append("BLINDCORRIDOR download status must explicitly say research only")
    if status.get("submission_status") != "DO NOT SUBMIT":
        problems.append("BLINDCORRIDOR status must explicitly say DO NOT SUBMIT")
    if status.get("submission_name") != card.get("submission_name") or status.get("note") != card.get("note"):
        problems.append("BLINDCORRIDOR status name/note disagree with run card")
    if not 0 < len(str(status.get("note", ""))) <= 140:
        problems.append("BLINDCORRIDOR metadata note must be 1..140 characters")

    holdout = card.get("holdout_dti", {})
    if (not isinstance(holdout, dict) or "dti" in holdout or "ci95" in holdout
            or "evaluator_version" in holdout or "withheld_positive_pixels" in holdout):
        problems.append("BLINDCORRIDOR must not present an uncomputed HOLDOUT-DTI as a result")
    if card.get("leakage_canaries", {}).get("canaries_run") is not False:
        problems.append("BLINDCORRIDOR leakage-canary status changed; review required")
    refs = card.get("uniqueness", {}).get("references", [])
    unique = status.get("uniqueness", {})
    if (unique.get("status") != "partial local check only"
            or unique.get("scope") != "available bridge rasters only"
            or unique.get("checked_reference_count") != len(refs)
            or unique.get("full_registry_audit") != "not performed"
            or unique.get("literal_dense_witness") != "unresolved"):
        problems.append("BLINDCORRIDOR uniqueness status must remain limited and unresolved")

    page = INDEX.read_text(encoding="utf-8") if INDEX.is_file() else ""
    section = page.split('id="blindcorridor"', 1)[-1].split("</section>", 1)[0]
    for phrase in ("FORMAT PASS ONLY", "DO NOT SUBMIT", "HOLDOUT-DTI", "not a submission basis", "available bridge references only", "not globally unique"):
        if phrase.lower() not in section.lower():
            problems.append(f"BLINDCORRIDOR landing-page status missing {phrase!r}")
    if "OK TO SUBMIT" in section:
        problems.append("BLINDCORRIDOR section contains contradictory OK TO SUBMIT copy")
    if f"downloads/{Path(rel).name}" not in section:
        problems.append("BLINDCORRIDOR research TIFF is not linked from its status section")
    print(f"  HISTORICAL {tif.name} sha256 {digest[:16]}… verdict=format_pass (DO NOT SUBMIT)")


def check_dexpkostrov_history(problems: list[str]) -> None:
    """Cryptographically bind the 2026-10-29 DEXP-KOSTROV-KOENDERINK artifact and its fail-closed status."""
    status_path = DOWNLOADS / "dexpkostrov_readiness_20261029.json"
    if not status_path.is_file():
        if DOCS == ROOT / "docs":
            problems.append("DEXP-KOSTROV readiness feed missing: dexpkostrov_readiness_20261029.json")
        return
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        tif = DOCS / status["file"]
        zip_path = DOCS / status["zip"]
        card = json.loads((DOWNLOADS / status["run_card"]).read_text(encoding="utf-8"))
        audit = json.loads((DOWNLOADS / status["audit"]).read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError) as exc:
        problems.append(f"DEXP-KOSTROV evidence invalid: {exc}")
        return
    if not tif.is_file() or not zip_path.is_file():
        problems.append("DEXP-KOSTROV TIFF or ZIP missing")
        return
    digest = sha256_file(tif)
    if status.get("raster_sha256") != digest or card.get("raster_sha256") != digest or audit.get("sha256_zeros") != digest:
        problems.append("DEXP-KOSTROV SHA-256 mismatch across readiness/run_card/audit")
    if status.get("zip_sha256") != sha256_file(zip_path):
        problems.append("DEXP-KOSTROV ZIP SHA-256 mismatch")
    if (status.get("verdict") != "negative" or card.get("verdict") != "negative" or audit.get("verdict") != "negative"
            or status.get("submission_eligible") is not False or card.get("submission_eligible") is not False
            or audit.get("submission_eligible") is not False):
        problems.append("DEXP-KOSTROV must remain verdict=negative and submission_eligible=false")
    if status.get("submission_status") != "DO NOT SUBMIT":
        problems.append("DEXP-KOSTROV submission_status must be DO NOT SUBMIT")
    summary_path = DOCS / str(status.get("executive_summary", ""))
    if not summary_path.is_file():
        problems.append("DEXP-KOSTROV executive summary HTML missing")
    else:
        stxt = summary_path.read_text(encoding="utf-8")
        if "DO NOT SUBMIT" not in stxt or "OK TO SUBMIT" in stxt:
            problems.append("DEXP-KOSTROV executive summary HTML violates fail-closed DO NOT SUBMIT wording")
    print(f"  CANDIDATE-20261029 {tif.name} sha256 {digest[:16]}… verdict=negative (DO NOT SUBMIT)")


def check_marussi_20261029(problems: list[str]) -> None:
    """Keep the 2026-10-29 MARUSSI-TRISHEAR artifact byte-bound and fail-closed."""
    status_path = DOWNLOADS / "marussi_trishear_readiness_20261029.json"
    if not status_path.is_file():
        if DOCS == ROOT / "docs":
            problems.append("MARUSSI-TRISHEAR readiness feed missing")
        return
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        card = json.loads((DOWNLOADS / status["run_card"]).read_text(encoding="utf-8"))
        audit = json.loads((DOWNLOADS / status["audit"]).read_text(encoding="utf-8"))
        tif = DOCS / status["file"]
        summary = (DOCS / status["executive_summary"]).read_text(encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"MARUSSI-TRISHEAR evidence invalid: {exc}")
        return
    if not tif.is_file():
        problems.append(f"MARUSSI-TRISHEAR TIFF missing: {status.get('file')}")
        return
    digest = sha256_file(tif)
    if digest != status.get("raster_sha256") or digest != card.get("raster_sha256") or digest != audit.get("sha256_zeros"):
        problems.append("MARUSSI-TRISHEAR SHA-256 mismatch across TIFF, readiness, run card, or audit")
    if (card.get("verdict") != "negative" or card.get("submission_eligible") is not False
            or status.get("verdict") != "negative" or status.get("submission_eligible") is not False):
        problems.append("MARUSSI-TRISHEAR must remain fail-closed negative")
    if not 0 < len(str(card.get("note", ""))) <= 140:
        problems.append("MARUSSI-TRISHEAR note must be 1..140 characters")
    if "DO NOT SUBMIT" not in summary or "OK TO SUBMIT" in summary:
        problems.append("MARUSSI-TRISHEAR executive summary must state DO NOT SUBMIT without OK TO SUBMIT")
    print(f"  CANDIDATE-20261029 {tif.name} sha256 {digest[:16]}… verdict=negative (DO NOT SUBMIT)")


def check_admitrelay_history(problems: list[str]) -> None:
    """Keep the 2026-10-29 ADMITRELAY + LBM-v3 artifact byte-bound and fail-closed."""
    status_path = DOWNLOADS / "admitrelay_readiness_20261029.json"
    if not status_path.is_file():
        return
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
        tif = DOCS / status["file"]
        zip_path = DOCS / status["zip"]
        card = json.loads((DOWNLOADS / status["run_card"]).read_text(encoding="utf-8"))
        audit = json.loads((DOWNLOADS / status["audit"]).read_text(encoding="utf-8"))
        summary = (DOCS / status["executive_summary"]).read_text(encoding="utf-8")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"ADMITRELAY readiness/evidence missing or invalid: {exc}")
        return

    if not tif.is_file() or not zip_path.is_file():
        problems.append("ADMITRELAY research TIFF or ZIP missing")
        return
    digest = sha256_file(tif)
    if status.get("raster_sha256") != digest or card.get("raster_sha256") != digest or audit.get("sha256_zeros") != digest:
        problems.append("ADMITRELAY SHA-256 mismatch across readiness / run card / audit")
    if status.get("zip_sha256") != sha256_file(zip_path):
        problems.append("ADMITRELAY ZIP SHA-256 mismatch")
    if status.get("verdict") != "negative" or card.get("verdict") != "negative" or audit.get("verdict") != "negative":
        problems.append("ADMITRELAY must remain verdict=negative")
    if status.get("submission_eligible") is not False or card.get("submission_eligible") is not False or audit.get("submission_eligible") is not False:
        problems.append("ADMITRELAY must remain submission_eligible=false")
    if status.get("download_status") != "OK TO DOWNLOAD FOR RESEARCH ONLY" or status.get("submission_status") != "DO NOT SUBMIT":
        problems.append("ADMITRELAY download/submission status strings invalid")
    for phrase in ("DO NOT SUBMIT", "OK TO DOWNLOAD FOR RESEARCH ONLY", "HOLDOUT-DTI", "MODEL", "CLAIM"):
        if phrase not in summary:
            problems.append(f"ADMITRELAY executive summary missing {phrase!r}")
    if "OK TO SUBMIT" in summary:
        problems.append("ADMITRELAY executive summary contains contradictory OK TO SUBMIT copy")
    print(f"  CANDIDATE-20261029 {tif.name} sha256 {digest[:16]}… verdict=negative (DO NOT SUBMIT)")


def check_served(html: str, problems: list[str]) -> int:
    archive = ARCHIVE.read_text(encoding="utf-8") if ARCHIVE.is_file() else ""
    served = sorted(DOWNLOADS.glob("*-zeros.tif"))
    if not served:
        problems.append("no zeros-outside rasters in docs/downloads")
    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5
    for path in served:
        if f"downloads/{path.name}" not in html and f"downloads/{path.name}" not in archive:
            problems.append(f"{path.name} is served but linked from neither index.html nor archive.html")
        ok, report = summarise(run_gates(str(path), str(SAMPLE), str(LABELS), prune_radius=2,
                                         require_submission_encoding=True))
        if not ok:
            problems.append(f"{path.name}: gates failed\n{report}")
            continue
        with rasterio.open(path) as ds:
            a = ds.read(1)
        if not np.isfinite(a).all() or a.min() < 0 or a.max() > 1:
            problems.append(f"{path.name}: values outside [0,1] or non-finite")
        if np.any((a > 0) & ~footprint):
            problems.append(f"{path.name}: mass outside footprint")
        if np.any(a[cat] > 0):
            problems.append(f"{path.name}: mass on catalogue")
        try:
            assert_submittable(validate(path, footprint, cat))
        except AssertionError as exc:
            problems.append(f"{path.name}: {exc}")
    return len(served)


def check_focus_nine_summary(problems: list[str]) -> None:
    """Keep the linked, evidence-derived focus-nine page fail-closed and current."""
    try:
        import render_nine_sites_20261028
        path = render_nine_sites_20261028.OUT
        if not path.is_file() or path.read_text(encoding="utf-8") != render_nine_sites_20261028.render():
            problems.append("stale focus-nine executive summary (run scripts/render_nine_sites_20261028.py)")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        problems.append(f"focus-nine executive summary evidence invalid: {exc}")


def check_lidarsintervalve_20261029(problems: list[str]) -> None:
    """Verify 2026-10-29 LIDAR-SINTERVALVE byte-binding, gates, and fail-closed status."""
    status_path = DOWNLOADS / "lidarsintervalve_readiness_20261029.json"
    try:
        status = json.loads(status_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        problems.append(f"LIDAR-SINTERVALVE readiness feed missing or invalid: {exc}")
        return
    rel = status.get("file", "")
    tif = DOCS / rel
    if not tif.is_file():
        problems.append(f"LIDAR-SINTERVALVE research TIFF missing: {rel}")
        return
    digest = sha256_file(tif)
    if status.get("raster_sha256") != digest:
        problems.append("LIDAR-SINTERVALVE readiness SHA-256 != research TIFF bytes")
    zip_path = DOCS / status.get("zip", "")
    if not zip_path.is_file() or status.get("zip_sha256") != sha256_file(zip_path):
        problems.append("LIDAR-SINTERVALVE ZIP missing or SHA-256 mismatch")
    else:
        with zipfile.ZipFile(zip_path) as zf:
            members = [n for n in zf.namelist() if not n.endswith("/")]
            if members != [tif.name] or hashlib.sha256(zf.read(tif.name)).hexdigest() != digest:
                problems.append("LIDAR-SINTERVALVE ZIP payload != research TIFF bytes")
    card = json.loads((DOWNLOADS / status.get("run_card", "")).read_text(encoding="utf-8"))
    audit = json.loads((DOWNLOADS / status.get("audit", "")).read_text(encoding="utf-8"))
    if card.get("raster_sha256") != digest or audit.get("sha256_zeros") != digest:
        problems.append("LIDAR-SINTERVALVE run-card/audit SHA-256 != research TIFF bytes")
    if card.get("verdict") != "negative" or card.get("submission_eligible") is not False:
        problems.append("LIDAR-SINTERVALVE run card must remain negative and not submission-eligible")
    if status.get("verdict") != "negative" or status.get("submission_eligible") is not False:
        problems.append("LIDAR-SINTERVALVE readiness must remain negative and not submission-eligible")
    exec_path = DOCS / status.get("executive_summary", "")
    if not exec_path.is_file():
        problems.append("LIDAR-SINTERVALVE executive summary HTML missing")
    else:
        exec_html = exec_path.read_text(encoding="utf-8")
        check_conflict_markers("executive-summary-20261029-lidarsintervalve.html", exec_html, problems)
        if "DO NOT SUBMIT" not in exec_html or "OK TO SUBMIT" in exec_html:
            problems.append("LIDAR-SINTERVALVE executive summary status copy invalid")
    print(f"  CURRENT-20261029 {tif.name} sha256 {digest[:16]}… verdict=negative (DO NOT SUBMIT)")


def check_conflict_markers(label: str, page: str, problems: list[str]) -> None:
    """Reject unresolved Git markers in served text, including diff3 ancestors."""
    if re.search(r"^(?:<{7}|={7}|>{7}|\|{7})(?: |$)", page, re.MULTILINE):
        problems.append(f"{label} contains unresolved merge conflict markers")


def main() -> int:
    problems: list[str] = []
    if not INDEX.is_file():
        print("FAIL: docs/index.html missing")
        return 2
    check_rendered(problems)
    check_focus_nine_summary(problems)
    html = INDEX.read_text(encoding="utf-8")
    howto = (DOCS / "how-to-submit.html").read_text(encoding="utf-8") if (DOCS / "how-to-submit.html").is_file() else ""
    summary = (DOCS / "executive-summary.html").read_text(encoding="utf-8") if (DOCS / "executive-summary.html").is_file() else ""
    for label, page in (("index.html", html), ("how-to-submit.html", howto), ("executive-summary.html", summary)):
        check_conflict_markers(label, page, problems)
    for label, page in (("how-to-submit.html", howto), ("executive-summary.html", summary)):
        if "BLINDCORRIDOR" not in page or "DO NOT SUBMIT" not in page:
            problems.append(f"{label} must show the current BLINDCORRIDOR DO NOT SUBMIT status")
        if "OK TO SUBMIT" in page:
            problems.append(f"{label} contains contradictory OK TO SUBMIT copy")
    for needle in ("How to submit", "user-reported", "HOLDOUT-DTI", "Download"):
        if needle not in html:
            problems.append(f"index.html missing {needle!r}")
    if "Predicted values must be in range [0, 1]" not in howto:
        problems.append("how-to-submit.html must explain the portal range error")
    if not re.search(r"(3 per week|weekly limit)", html + howto, re.I):
        problems.append("no weekly-slot caution")
    ids = re.findall(r'\bid="([^"]+)"', html)
    if len(ids) != len(set(ids)):
        problems.append("index.html contains duplicate element ids")
    check_primary(html, problems)
    check_tipcomp_history(problems)
    check_blindcorridor_history(problems)
    check_dexpkostrov_history(problems)
    check_marussi_20261029(problems)
    check_admitrelay_history(problems)
    check_lidarsintervalve_20261029(problems)
    n = check_served(html, problems)
    if problems:
        print("SITE CHECK FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"SITE CHECK PASS ({n} served raster(s) gated)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
