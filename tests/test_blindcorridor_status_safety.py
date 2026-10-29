"""Fail-closed presentation and byte binding for the main-side BLINDCORRIDOR artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from scripts import check_site

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DOWNLOADS = DOCS / "downloads"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_blindcorridor_feed_and_artifacts_are_bound_and_not_eligible() -> None:
    status = _json(DOWNLOADS / "blindcorridor_readiness_20261028.json")
    card = _json(DOWNLOADS / status["run_card"])
    audit = _json(DOWNLOADS / status["audit"])
    tif = DOWNLOADS / Path(status["file"]).name
    zip_path = DOWNLOADS / Path(status["zip"]).name
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    with zipfile.ZipFile(zip_path) as archive:
        members = [name for name in archive.namelist() if not name.endswith("/")]
        assert len(members) == 1 and Path(members[0]).name == tif.name
        assert hashlib.sha256(archive.read(members[0])).hexdigest() == digest

    assert status["raster_sha256"] == card["raster_sha256"] == audit["sha256_zeros"] == digest
    assert status["zip_sha256"] == zip_digest
    assert status["verdict"] == card["verdict"] == audit["verdict"] == "format_pass"
    assert status["submission_eligible"] is False
    assert card["submission_eligible"] is False
    assert audit["submission_eligible"] is False
    assert status["download_status"] == "OK TO DOWNLOAD FOR RESEARCH ONLY"
    assert status["submission_status"] == "DO NOT SUBMIT"
    assert status["submission_name"] == card["submission_name"]
    assert status["note"] == card["note"]
    assert 0 < len(status["note"]) <= 140

    assert status["holdout_dti"]["status"] == "not independently computed"
    assert status["leakage_canaries"]["canaries_run"] is False
    assert status["uniqueness"]["scope"] == "available bridge rasters only"
    assert status["uniqueness"]["checked_reference_count"] == 3
    assert status["uniqueness"]["full_registry_audit"] == "not performed"
    assert status["uniqueness"]["literal_dense_witness"] == "unresolved"


def test_blindcorridor_site_copy_is_downloadable_for_research_but_not_upload() -> None:
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    section = index.split('id="blindcorridor"', 1)[1].split("</section>", 1)[0]
    for phrase in (
        "FORMAT PASS ONLY",
        "DO NOT SUBMIT",
        "research only",
        "HOLDOUT-DTI",
        "not a submission basis",
        "available bridge references only",
        "not globally unique",
        "submission_eligible=false",
    ):
        assert phrase.lower() in section.lower()
    assert "OK TO SUBMIT" not in section
    assert "gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif" in section
    assert "blindcorridor_readiness_20261028.json" in section


def test_site_gate_rejects_blindcorridor_promotion_and_global_uniqueness(tmp_path, monkeypatch) -> None:
    docs = tmp_path / "docs"
    downloads = docs / "downloads"
    downloads.mkdir(parents=True)
    monkeypatch.setattr(check_site, "DOCS", docs)
    monkeypatch.setattr(check_site, "DOWNLOADS", downloads)
    monkeypatch.setattr(check_site, "INDEX", docs / "index.html")

    tif_name = "gemsdoe92-blindcorridor-fixture-zeros.tif"
    zip_name = "gemsdoe92-blindcorridor-fixture-zeros.zip"
    card_name = "gemsdoe92-blindcorridor-fixture_run_card.json"
    audit_name = "gemsdoe92-blindcorridor-fixture-zeros-audit.json"
    tif = downloads / tif_name
    tif.write_bytes(b"fixture raster bytes")
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    zip_path = downloads / zip_name
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr(tif_name, tif.read_bytes())
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    card = {
        "raster_sha256": digest,
        "verdict": "format_pass",
        "submission_eligible": False,
        "submission_name": "blindcorridor-fixture",
        "note": "research-only fixture",
        "holdout_dti": {},
        "leakage_canaries": {"canaries_run": False},
        "uniqueness": {"references": [{"reference": "one"}]},
    }
    audit = {"sha256_zeros": digest, "verdict": "format_pass", "submission_eligible": False}
    status = {
        "file": f"downloads/{tif_name}",
        "zip": f"downloads/{zip_name}",
        "raster_sha256": digest,
        "zip_sha256": zip_digest,
        "run_card": card_name,
        "audit": audit_name,
        "verdict": "format_pass",
        "submission_eligible": False,
        "download_status": "OK TO DOWNLOAD FOR RESEARCH ONLY",
        "submission_status": "DO NOT SUBMIT",
        "submission_name": card["submission_name"],
        "note": card["note"],
        "uniqueness": {
            "status": "partial local check only",
            "scope": "available bridge rasters only",
            "checked_reference_count": 1,
            "full_registry_audit": "not performed",
            "literal_dense_witness": "unresolved",
        },
    }
    (downloads / card_name).write_text(json.dumps(card))
    (downloads / audit_name).write_text(json.dumps(audit))
    (downloads / "blindcorridor_readiness_20261028.json").write_text(json.dumps(status))
    (docs / "index.html").write_text(
        '<section id="blindcorridor">FORMAT PASS ONLY DO NOT SUBMIT HOLDOUT-DTI '
        'not a submission basis available bridge references only not globally unique '
        f'<a href="downloads/{tif_name}">research raster</a></section>'
    )

    problems: list[str] = []
    check_site.check_blindcorridor_history(problems)
    assert problems == []

    status["submission_eligible"] = True
    status["submission_status"] = "CONDITIONAL"
    status["uniqueness"]["scope"] = "complete registry"
    (downloads / "blindcorridor_readiness_20261028.json").write_text(json.dumps(status))
    problems = []
    check_site.check_blindcorridor_history(problems)
    assert any("readiness feed must remain format_pass and not eligible" in p for p in problems)
    assert any("explicitly say DO NOT SUBMIT" in p for p in problems)
    assert any("uniqueness status must remain limited and unresolved" in p for p in problems)


def test_historical_registry_failure_is_bound_and_visible() -> None:
    status = _json(DOWNLOADS / "blindcorridor_readiness_20261028.json")
    evidence = _json(ROOT / "evidence/uniq_full_registry/blindcorridor-37654dots-11f8999c.json")
    historical = status["uniqueness"]["historical_registry_audit"]
    assert historical["candidate_sha256"] == evidence["candidate_sha256"] == status["raster_sha256"]
    assert historical["worst_overlap_3px"] == evidence["worst_overlap"]["value"] > 0.70
    assert historical["worst_repositories"] == evidence["worst_overlap"]["repos"]
    assert historical["pi1_pass"] is evidence["pi1_pass"] is False
    assert historical["current"] is False
    for page in ("index.html", "nine-sites.html", "executive-summary.html", "how-to-submit.html"):
        text = (DOCS / page).read_text(encoding="utf-8")
        assert "0.769108" in text and "13GEMSDOE" in text
        assert "DO NOT SUBMIT" in text
