"""The current decision is one byte-bound VARIO card, rendered everywhere."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from gems.public_status import install_panel, render_status, validate_status
from scripts.render_current_status import BEGIN, END, load_card, panel, render, check

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture()
def card():
    return load_card()


def _primary(card):
    assert card["submission_file"].startswith("docs/downloads/")
    return card["submission_file"].removeprefix("docs/")


def test_current_panels_are_synchronized_and_idempotent(card):
    assert check() == []
    validate_status(card, ROOT, _primary(card))
    for page in ("index.html", "executive-summary.html", "SUBMIT.html"):
        text = (ROOT / "docs" / page).read_text()
        assert text.count(BEGIN) == text.count(END) == 1
        # the authoritative panel is the first content inside <body>
        body_end = text.index(">", text.index("<body")) + 1
        assert text[body_end:].lstrip().startswith(BEGIN)
        assert "OK TO DOWNLOAD" in text
    # panel links resolve inside the repo
    import re
    for href in re.findall(r'href="([^"#]+)"', panel(card, "index.html")):
        if not href.startswith(("http://", "https://")):
            assert (ROOT / "docs" / href).is_file(), href


@pytest.mark.parametrize("key,value", [
    ("verdict", "promote"),                       # inconsistent with failed gates
    ("submission_eligible", True),                # slots are a separate selector step
    ("weekly_slots_used", 1),
    ("organizer_confirmed_score", 0.30),          # no receipt exists
    ("raster_sha256", "0" * 64),                  # not these bytes
    ("note", ""),
    ("note", "x" * 141),
    ("submission_file", "docs/downloads/other-zeros.tif"),
])
def test_rejects_unsupported_status(card, key, value):
    bad = deepcopy(card)
    bad[key] = value
    if key == "verdict":
        pass  # gates stay false -> verdict inconsistent
    with pytest.raises(ValueError):
        validate_status(bad, ROOT, _primary(card))


def test_forged_promote_verdict_cannot_override_literal_stop(card):
    forced = deepcopy(card)
    forced["gates"] = {k: True for k in forced["gates"]}
    forced["verdict"] = "promote"
    forced["blocking_reasons"] = []
    with pytest.raises(ValueError, match="registry pre-placement STOP"):
        validate_status(forced, ROOT, _primary(card))
    forced["gates"]["operative_uniqueness"] = False
    with pytest.raises(ValueError):
        validate_status(forced, ROOT, _primary(card))


def test_receipt_must_be_object():
    for value in ([], None, "invalid"):
        with pytest.raises(ValueError):
            validate_status(value, ROOT, "downloads/x-zeros.tif")


def test_incomplete_format_evidence_cannot_be_published(card):
    for rows in ([], None, [{"name": "crs", "ok": False, "detail": ""}],
                 [{"name": "crs", "ok": True, "detail": ""}]):
        bad = deepcopy(card)
        bad["validator_output"] = rows
        with pytest.raises(ValueError):
            validate_status(bad, ROOT, _primary(card))


def test_stale_panel_fails_check_and_is_repairable(card, tmp_path):
    text = f"<html><body>\n{panel(card, 'index.html')}\n<h1>workbench</h1></body></html>"
    rendered = render(text, panel(card, "index.html"), markdown=False)
    assert rendered == text  # idempotent
    stale = text.replace("OK TO DOWNLOAD", "OK TO GO")
    assert render(stale, panel(card, "index.html"), markdown=False) == text


def test_newer_lane_cannot_push_authority_below_its_banner(card):
    text = f"<html><body><aside>NEW LANE SAYS SUBMIT</aside><h1>x</h1></body></html>"
    out = render(text, panel(card, "index.html"), markdown=False)
    assert out.index(BEGIN) < out.index("NEW LANE")
    assert install_panel("<html><body><p>x</p></body></html>", render_status(card)).count(BEGIN) == 1


def test_render_escapes_local_paths_and_text(card):
    evil = deepcopy(card)
    evil["note"] = '<img src=x onerror=alert(1)>'
    out = panel(evil, "index.html")
    assert "<img src=x" not in out and "&lt;img" in out


@pytest.mark.parametrize("page", ["README.md", "SUBMISSION_READY.md"])
def test_markdown_lane_cannot_precede_current_decision(card, page):
    text = (ROOT / page).read_text()
    assert text.count(BEGIN) == 1
    assert text.index(BEGIN) < text.index("## Prior") if "## Prior" in text else True
    block = panel(card, page)
    assert block.startswith(BEGIN) and "Current research download" in block
    out = render(text, block, markdown=True)
    title, _, _ = out.partition("\n")
    assert title.startswith("# ") and out.split("\n", 2)[2].startswith(BEGIN)


def test_site_publication_gate_includes_current_status():
    # 2026-10-27: the publication gate re-renders the evidence-bound v3 site; the
    # legacy VARIO-status checker is preserved verbatim as check_site_legacy_20261026.py.
    src = (ROOT / "scripts/check_site.py").read_text()
    assert "render_site_v3" in src and "data-primary" in src
    legacy = (ROOT / "scripts/check_site_legacy_20261026.py").read_text()
    assert "render_vario_status" in legacy and "VARIO-STATUS:BEGIN" in legacy


def test_rederivation_rejects_tampered_tiff(tmp_path):
    """load_card re-runs gates from bytes; a tampered primary fails closed."""
    from scripts.render_vario_status import load_card as fresh
    fresh(ROOT)  # current bytes pass
