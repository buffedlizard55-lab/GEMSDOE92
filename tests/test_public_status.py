"""Publication cannot bury the decision below contradictory historical lanes."""
import copy
import json
from pathlib import Path

import pytest

from gems.public_status import (
    BEGIN, END, PAGES, check_panels, install_panel, render_status, validate_status,
)
from gems.rasters import sha256_file

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def publication(tmp_path):
    card = json.loads((ROOT / 'evidence/review797e_run_card.json').read_text())
    # No scientific data needed for publication-contract unit tests.
    files = [card['primary_download'], *card['publication_input_sha256']]
    for rel in files:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'test byte pin ' + rel.encode())
    card['raster_sha256'] = sha256_file(tmp_path / card['primary_download'])
    card['publication_input_sha256'] = {
        rel: sha256_file(tmp_path / rel) for rel in card['publication_input_sha256']}
    primary = card['primary_download'].removeprefix('docs/')
    panel = render_status(card)
    for name in PAGES:
        (tmp_path / 'docs' / name).write_text(install_panel('<body>old lanes</body>', panel))
    return tmp_path, card, primary


def test_actual_status_is_byte_bound_and_first_on_every_page():
    from scripts.check_site import primary_download
    problems = []
    primary = primary_download((ROOT / 'docs/index.html').read_text(), problems)
    assert not problems
    card = json.loads((ROOT / 'docs/downloads/review797e_run_card.json').read_text())
    assert not check_panels(card, ROOT, primary)
    assert (ROOT / 'evidence/review797e_run_card.json').read_bytes() == (
        ROOT / 'docs/downloads/review797e_run_card.json').read_bytes()


def test_readme_first_screen_cannot_promote_historical_lane_or_score():
    readme = (ROOT / 'README.md').read_text()
    first_screen = readme.split('### Persisted user brief', 1)[0]
    assert first_screen.index('Authoritative decision') < first_screen.index('DO NOT SUBMIT')
    assert 'OK TO DOWNLOAD FOR RESEARCH' in first_screen
    assert 'DO NOT SPEND A WEEKLY SLOT' in first_screen
    assert 'New unique-byte GeoTIFFs' in first_screen
    assert 'submission_eligible: false' in first_screen
    assert 'HOLDOUT-DTI `0.010909' in first_screen
    assert 'ORGANIZER-CONFIRMED score is available' in first_screen
    assert 'docs/REVIEW_20261025_ARENA_8A5595A3.md' in first_screen


def test_session_prompt_points_to_latest_audit_before_history():
    prompt = (ROOT / 'SESSION_PROMPT.md').read_text()
    first_addendum = prompt.split('---', 1)[0]
    assert 'docs/REVIEW_20261025_FRESH_AUDIT.md' in first_addendum
    assert 'No new TIFF' in first_addendum


def test_panel_update_is_idempotent_and_moves_stale_banner_below(publication):
    _, card, _ = publication
    panel = render_status(card)
    page = install_panel('<body>historical</body>', panel)
    assert install_panel(page, panel) == page
    page = page.replace('<body>', '<body><aside>NEWEST UNIQUE</aside>')
    fixed = install_panel(page, panel)
    assert fixed.index(panel) < fixed.index('NEWEST UNIQUE')
    assert fixed.count(BEGIN) == fixed.count(END) == 1


@pytest.mark.parametrize('field,value', [
    ('submission_eligible', True), ('submission_eligible', 'false'),
    ('new_raster_generated', 'true'), ('verdict', 'promote'),
    ('raster_sha256', '0' * 64), ('note', ''), ('note', 'x' * 141),
    ('validator_output', []), ('validator_output', [None]),
    ('validator_output', [{'name': [], 'ok': True}]),
    ('publication_input_sha256', {}), ('correlation_overlap_vs_registry', None),
])
def test_invalid_or_authorizing_status_fails_closed(publication, field, value):
    root, card, primary = publication
    card[field] = value
    assert check_panels(card, root, primary)


def test_primary_and_all_input_pins_are_required(publication):
    root, card, primary = publication
    for rel in (card['primary_download'], *card['publication_input_sha256']):
        path = root / rel
        saved = path.read_bytes()
        path.write_bytes(b'changed')
        assert check_panels(card, root, primary)
        path.write_bytes(saved)
    with pytest.raises(ValueError):
        validate_status(card, root, 'downloads/../unsafe-zeros.tif')
    card['primary_download'] = 'docs/downloads/sibling-zeros.tif'
    assert check_panels(card, root, primary)


@pytest.mark.parametrize('mutation', ['bury', 'missing', 'duplicate', 'edit'])
def test_each_page_is_checked_not_just_the_homepage(publication, mutation):
    root, card, primary = publication
    path = root / 'docs/executive-summary.html'
    text = path.read_text()
    if mutation == 'bury':
        text = text.replace('<body>', '<body><aside>contradiction</aside>')
    elif mutation == 'missing':
        text = '<body>no status</body>'
    elif mutation == 'duplicate':
        text += render_status(card)
    else:
        text = text.replace('DO NOT SUBMIT.', 'SUBMIT NOW.')
    path.write_text(text)
    assert check_panels(card, root, primary)


@pytest.mark.parametrize('html', [
    '<body>' + BEGIN, '<body>' + END,
    '<body>' + BEGIN + END + BEGIN + END, '<main>no body</main>',
    '<body><body>',
])
def test_ambiguous_template_does_not_get_partially_rewritten(html):
    with pytest.raises(ValueError):
        install_panel(html, 'new panel')


def test_receipt_strings_cannot_inject_markup(publication):
    _, original, _ = publication
    card = copy.deepcopy(original)
    card['primary_download'] = 'docs/downloads/" onclick="alert(1)-zeros.tif'
    card['raster_sha256'] = '<script>evil</script>'
    rendered = render_status(card)
    assert '<script>' not in rendered
    assert 'href="downloads/" onclick=' not in rendered
    assert '&lt;script&gt;' in rendered
