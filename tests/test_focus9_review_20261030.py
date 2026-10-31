from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def test_focus9_page_is_reproducible_and_cautiously_labeled():
    from render_focus9_review_20261030 import render_page

    page = DOCS / "focus9-review-20261030.html"
    assert page.read_text(encoding="utf-8") == render_page()
    text = page.read_text(encoding="utf-8")
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert f"<strong>{site}</strong>" in text
    assert "NOT UNIQUE BY EXACT SHA" in text
    assert "not a score" in text
    assert "none is a current verified score" in text
    assert "not live-verified here" in text
    assert "NO FOCUS-SITE FILE IS CLEARED TO SUBMIT" in text
    assert "0.2778" in text and "0.3195" in text and "0.4413" in text


def test_current_status_is_bound_to_existing_lidar_and_fresh_receipts():
    current = json.loads((DOCS / "downloads/current_submission.json").read_text(encoding="utf-8"))
    readiness = json.loads((DOCS / "downloads/readiness.json").read_text(encoding="utf-8"))
    registry = json.loads((DOCS / "downloads/lidarsintervalve_registry_20261030.json").read_text(encoding="utf-8"))
    focus9 = json.loads((DOCS / "downloads/focus9_registry_20261030.json").read_text(encoding="utf-8"))
    assert current["new_tiff_created_this_review"] is False
    assert current["experiments_run_this_review"] == 0
    assert current["holdout_run_this_review"] is False
    assert current["weekly_slots_used_this_review"] == 0
    assert current["file"].endswith("gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif")
    assert current["ok_to_download"] is True and current["ok_to_submit"] is False
    assert readiness["submission_eligible"] is False
    assert readiness["uniqueness"]["current_final_dot_pi1_pass"] is True
    assert readiness["uniqueness"]["current_pre_placement_surface_reaudited"] is False
    assert readiness["uniqueness"]["literal_full_support_witness_duplicate"] is True
    assert registry["registry_snapshot"]["inventory_sha256"] == focus9["registry_snapshot"]["inventory_sha256"]
    assert current["registry_audit_sha256"] == hashlib.sha256((DOCS / "downloads/lidarsintervalve_registry_20261030.json").read_bytes()).hexdigest()
    assert registry["pi1_pass"] is True
    assert abs(registry["worst_overlap"]["value"] - 0.690949) < 1e-9


def test_primary_download_is_lidar_and_focus9_page_is_prominent():
    index = (DOCS / "index.html").read_text(encoding="utf-8")
    nine = (DOCS / "nine-sites.html").read_text(encoding="utf-8")
    assert index.count('data-primary="true"') == 1
    assert 'data-primary="true" href="downloads/gemsdoe92-lidarsintervalve-37654dots-20261029-65c6cb0e-zeros.tif"' in index
    assert "focus9-review-20261030.html" in index
    assert "focus9-review-20261030.html" in nine
    assert 'data-primary="true"' not in nine
    assert "DO NOT SUBMIT" in index and "OK TO SUBMIT" not in index
