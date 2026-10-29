"""The linked focus-nine executive page must not silently promote old artifacts."""
import json
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_site
import render_nine_sites_20261028 as renderer


def test_published_page_is_generated_and_fail_closed():
    problems = []
    check_site.check_focus_nine_summary(problems)
    assert not problems
    page = renderer.render()
    assert "DO NOT SUBMIT — no cleared new TIFF" in page
    assert "older sparse-only overlap is not clearance" in page
    assert "Not available" in page
    assert "only file that passes uniqueness" not in page
    assert all(site in page for site in renderer.SITES)
    assert page.count("FAIL (overlap &gt; 0.70)") == 0  # controlled static label uses literal >
    assert page.count("FAIL (overlap > 0.70)") == 9


def test_site_check_rejects_altered_summary(monkeypatch, tmp_path):
    page = tmp_path / "summary.html"
    page.write_text(renderer.render().replace("DO NOT SUBMIT — no cleared new TIFF", "OK TO SUBMIT"))
    monkeypatch.setattr(renderer, "OUT", page)
    problems = []
    check_site.check_focus_nine_summary(problems)
    assert any("stale focus-nine" in p for p in problems)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "invalid"])
def test_invalid_receipt_fails_closed(monkeypatch, tmp_path, mutation):
    for name in ("evidence/focus9_sources_20261028.json", "docs/downloads/focus9_pairwise_recheck_14f85876.json"):
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, dest)
    path = tmp_path / "docs/downloads/focus9_pairwise_recheck_14f85876.json"
    data = json.loads(path.read_text())
    if mutation == "missing":
        data["comparisons"].pop()
    elif mutation == "duplicate":
        data["comparisons"][-1] = data["comparisons"][0]
    else:
        data["comparisons"][0]["forward_3px_overlap_a_to_b"] = float("nan")
    path.write_text(json.dumps(data))
    monkeypatch.setattr(renderer, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        renderer.render()
    problems = []
    check_site.check_focus_nine_summary(problems)
    assert any("evidence invalid" in p for p in problems)


@pytest.mark.parametrize("field", ["claim", "link"])
def test_invalid_inventory_fails_closed(monkeypatch, tmp_path, field):
    for name in ("evidence/focus9_sources_20261028.json", "docs/downloads/focus9_pairwise_recheck_14f85876.json"):
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / name, dest)
    path = tmp_path / "evidence/focus9_sources_20261028.json"
    data = json.loads(path.read_text())
    if field == "claim":
        data["GEMSDOE32"]["claim"] = 0.0
    else:
        data["GEMSDOE32"]["blob_url"] = "javascript:alert(1)"
    path.write_text(json.dumps(data))
    monkeypatch.setattr(renderer, "ROOT", tmp_path)
    with pytest.raises(ValueError):
        renderer.render()
