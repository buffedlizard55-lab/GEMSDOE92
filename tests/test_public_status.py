"""Public status is byte-bound to the VARIO run card and fails closed."""
from copy import deepcopy
import json
import re
import shutil
from pathlib import Path

import pytest

from gems.public_status import PAGES, check_panels, install_panel, render_status, validate_status

ROOT = Path(__file__).resolve().parents[1]
CARD_PATH = ROOT / "docs/downloads/vario_run_card.json"


def _card():
    return json.loads(CARD_PATH.read_text())


def _primary():
    card = _card()
    return card["submission_file"].removeprefix("docs/")


def test_actual_status_is_byte_bound_and_first_on_every_page():
    card = _card()
    validate_status(card, ROOT, _primary())
    assert check_panels(card, ROOT, _primary()) == []
    panel = render_status(card)
    for name in PAGES:
        text = (ROOT / "docs" / name).read_text()
        body_end = text.index(">", text.index("<body")) + 1
        assert text[body_end:].lstrip().startswith("<!-- VARIO-STATUS:BEGIN -->")
        assert panel in text
    assert "DO NOT SUBMIT" in panel and "OK TO DOWNLOAD" in panel
    assert "no ORGANIZER-CONFIRMED score exists" in panel


def test_panel_update_is_idempotent_and_moves_stale_banner_below():
    panel = render_status(_card())
    text = '<html><body><aside>OLD LANE BANNER</aside><main>x</main></body></html>'
    once = install_panel(text, panel)
    assert install_panel(once, panel) == once
    assert once.index("VARIO-STATUS:BEGIN") < once.index("OLD LANE BANNER")


@pytest.mark.parametrize("key,value", [
    ("submission_eligible", True),
    ("submission_eligible", "false"),
    ("verdict", "promote"),
    ("verdict", "positive"),
    ("raster_sha256", "0" * 64),
    ("note", ""),
    ("note", "x" * 141),
    ("note", None),
    ("validator_output", []),
    ("validator_output", [{"name": "crs", "ok": True, "detail": ""}]),
    ("validator_output", "pass"),
    ("organizer_confirmed_score", 0.4413),
    ("weekly_slots_used", 2),
])
def test_invalid_or_authorizing_status_fails_closed(key, value):
    bad = deepcopy(_card())
    bad[key] = value
    with pytest.raises(ValueError):
        validate_status(bad, ROOT, _primary())


@pytest.mark.parametrize("degrade", ["missing", "duplicate", "edit"])
def test_each_page_is_checked_not_just_the_homepage(tmp_path, degrade):
    docs = tmp_path / "docs"
    (docs / "downloads").mkdir(parents=True)
    card = _card()
    source = ROOT / card["submission_file"]
    target = tmp_path / card["submission_file"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    panel = render_status(card)
    for name in PAGES:
        (docs / name).write_text(f"<html><body>\n{panel}\n</body></html>")
    page = docs / PAGES[-1]
    text = page.read_text()
    if degrade == "missing":
        text = "<html><body>nothing here</body></html>"
    elif degrade == "duplicate":
        text = text.replace("</body>", panel + "</body>")
    else:
        text = text.replace("DO NOT SUBMIT", "GO AHEAD")
    page.write_text(text)
    assert check_panels(card, tmp_path, _primary())


def test_ambiguous_template_does_not_get_partially_rewritten():
    panel = render_status(_card())
    with pytest.raises(ValueError):
        install_panel("<body><body>", panel)
    with pytest.raises(ValueError):
        install_panel(f"<html><body>{panel}{panel}</body></html>", panel)


def test_receipt_strings_cannot_inject_markup():
    card = _card()
    card["note"] = '<script>alert(1)</script>'
    card["validator_output"][0]["detail"] = '<b onclick="x()">hi</b>'
    rendered = render_status(card)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
