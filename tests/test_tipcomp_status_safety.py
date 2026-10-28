"""Regression tests for TIPCOMP's fail-closed historical status copy."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_tipcomp_status_is_hash_bound_and_negative() -> None:
    status = _json(DOWNLOADS / "tipcomp_readiness_20261028.json")
    card = _json(DOWNLOADS / status["run_card"])
    tif = DOCS / status["file"]
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()

    assert status["raster_sha256"] == digest
    assert card["raster_sha256"] == digest
    assert status["verdict"] == card["verdict"] == "negative"
    assert status["submission_eligible"] is False
    assert card["submission_eligible"] is False
    assert status["download_status"] == "OK TO DOWNLOAD FOR RESEARCH ONLY"
    assert status["submission_status"].startswith("DO NOT SUBMIT")
    assert status["submission_name"] == card["submission_name"]
    assert status["note"] == card["note"]
    assert 0 < len(status["note"]) <= 140


def test_tipcomp_summary_and_archive_do_not_promote_candidate() -> None:
    status = _json(DOWNLOADS / "tipcomp_readiness_20261028.json")
    summary = (DOCS / status["executive_summary"]).read_text(encoding="utf-8")
    archive = (DOCS / "archive.html").read_text(encoding="utf-8")
    href = f'href="{status["file"]}"'
    idx = archive.index(href)
    start = archive.rfind("<section", 0, idx)
    end = archive.index("</section>", idx) + len("</section>")
    historical_section = archive[start:end]

    for page in (summary, historical_section):
        assert "DO NOT SUBMIT" in page
        assert "OK TO DOWNLOAD FOR RESEARCH ONLY" in page
        assert "HOLDOUT-DTI" in page
        assert "MODEL" in page
        for stale in (
            "SELECTOR DECISION REQUIRED",
            "Download; selector decides slot",
            "PI-1 unique",
            "Unique (PI-1",
        ):
            assert stale.lower() not in page.lower()


def test_why_02778_separates_claim_model_and_historical_lineage() -> None:
    why = (DOCS / "WHY_0_2778.md").read_text(encoding="utf-8")
    lower = why.lower()

    assert "`0.2778` is a `claim`" in lower
    assert "`model (logo)`" in lower
    assert "historical receipt" in lower
    assert "not reproducible in this review" in lower
    assert "**not “globally optimal.”**" in lower
    assert "local marginal argument cannot establish a global optimum" in lower
    assert "that proves:" not in lower
    assert "organizer-confirmed" in lower


def test_current_input_audit_records_missing_pins_and_no_run() -> None:
    audit = _json(ROOT / "evidence" / "input_cache_audit_9649dfc1.json")
    assert audit["files_expected"] == 12
    assert audit["files_verified"] == 0
    assert audit["all_pins_verified"] is False
    assert audit["official_origin_authenticated"] is False
    assert audit["redistribution_rights_verified"] is False
    assert audit["training_run"] is False
    assert audit["holdout_run"] is False
    assert audit["submission_eligible"] is False
