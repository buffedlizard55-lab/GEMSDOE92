"""One current decision must survive parallel-lane historical banners."""
import json
from pathlib import Path
import shutil

import pytest

from scripts import render_current_status as status

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def site(tmp_path):
    card = json.loads((ROOT / status.CARD).read_text())
    paths = ['docs/index.html', *status.PAGES, status.CARD, card['primary_download'],
             card['preflight_receipt']]
    for name in paths:
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
    return tmp_path


def edit_card(root, fn):
    path = root / status.CARD
    card = json.loads(path.read_text())
    fn(card)
    path.write_text(json.dumps(card))


def test_current_panels_are_synchronized_and_idempotent(site):
    assert status.check(site) == []
    assert status.check(site, write=True) == []
    for name in status.PAGES:
        text = (site / name).read_text()
        block = text.split(status.BEGIN)[1].split(status.END)[0]
        assert 'DO NOT SUBMIT' in block
        assert 'HOLDOUT-DTI' in block
        assert 'not a new unique submission' in block or 'No new unique TIFF' in block
        if name.endswith('.html'):
            import re
            assert '<a href=' in block and ' download ' in block
            for href in re.findall(r'href="([^"]+)"', block):
                # The explanatory review isn't needed by this fixture, but every
                # destination must resolve in the actual checkout.
                assert (ROOT / Path(name).parent / href).is_file()
        if name in ('docs/index.html', 'docs/executive-summary.html', 'docs/SUBMIT.html'):
            assert text.count('<details data-status-archive="true">') == 1
            assert text.index(status.END) < text.index('data-status-archive') < text.index('<header')


@pytest.mark.parametrize('field,value', [('verdict', 'promote'), ('submission_eligible', True),
                                        ('new_unique_tiff_generated', True),
                                        ('note', 'x' * 141),
                                        ('primary_download', '../../outside-zeros.tif')])
def test_rejects_unsupported_status(site, field, value):
    edit_card(site, lambda c: c.update({field: value}))
    with pytest.raises(ValueError):
        status.load_card(site)


@pytest.mark.parametrize('value', [[], None, 'invalid'])
def test_receipt_must_be_object(site, value):
    (site / status.CARD).write_text(json.dumps(value))
    with pytest.raises(ValueError, match='JSON object'):
        status.load_card(site)


@pytest.mark.parametrize('value', [True, '1.0', float('nan')])
def test_overlap_requires_real_measurement(site, value):
    edit_card(site, lambda c: c['correlation_overlap_vs_registry'].update(
        existing_primary_forward_overlap_within_3px=value))
    with pytest.raises(ValueError, match='literal rejection'):
        status.load_card(site)


def test_rejects_changed_bytes(site):
    card = status.load_card(site)
    (site / card['primary_download']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='SHA-256'):
        status.load_card(site)


@pytest.mark.parametrize('value', [False, 'true', 1, None])
def test_format_flag_requires_boolean_true(site, value):
    edit_card(site, lambda c: c['validator_output'].update(all_finite=value))
    with pytest.raises(ValueError, match='unvalidated'):
        status.load_card(site)


@pytest.mark.parametrize('rows', [[], [{'name': 'crs', 'ok': True}],
                                  [{'name': 'crs', 'ok': 'true'}]])
def test_incomplete_format_evidence_cannot_be_published(site, rows):
    edit_card(site, lambda c: c['validator_output'].update(gates=rows))
    with pytest.raises(ValueError, match='format gates'):
        status.load_card(site)


@pytest.mark.parametrize('field', ['validator_output', 'correlation_overlap_vs_registry'])
@pytest.mark.parametrize('value', [None, [], 'true'])
def test_nested_receipts_must_be_objects(site, field, value):
    edit_card(site, lambda c: c.update({field: value}))
    with pytest.raises(ValueError, match='object'):
        status.load_card(site)


def test_invalid_later_target_does_not_partially_render(site):
    first = site / status.PAGES[0]
    first.write_text(first.read_text().replace('Current decision:', 'Old decision:'))
    before = first.read_bytes()
    last = site / status.PAGES[-1]
    last.write_text(last.read_text() + status.BEGIN)
    with pytest.raises(ValueError, match='markers'):
        status.check(site, write=True)
    assert first.read_bytes() == before


def test_preflight_and_card_must_agree(site):
    edit_card(site, lambda c: c['correlation_overlap_vs_registry'].update(witness_sha256='bad'))
    with pytest.raises(ValueError, match='preflight'):
        status.load_card(site)


def test_stale_panel_fails_check_and_is_repairable(site):
    path = site / 'index.html'
    path.write_text(path.read_text().replace('Current decision: research download only', 'stale decision'))
    assert status.check(site) == ['index.html']
    assert status.check(site, write=True) == ['index.html']
    assert status.check(site) == []


def test_newer_lane_cannot_push_authority_below_its_banner(site):
    path = site / 'index.html'
    path.write_text(path.read_text().replace('<body>', '<body><ASIDE>newest lane</ASIDE>', 1))
    with pytest.raises(ValueError, match='must precede'):
        status.check(site)


def test_marker_corruption_rejected():
    with pytest.raises(ValueError, match='markers'):
        status.render('<body>' + status.BEGIN, 'block', markdown=False)


def test_render_escapes_local_paths_and_text(site):
    card = status.load_card(site)
    # The HTML renderer must not interpolate arbitrary narrative text as markup.
    card['note'] = '<script>bad</script>'
    block = status.panel(card, 'index.html')
    assert '<script>' not in block
    assert 'href="docs/downloads/' in block


def test_site_publication_gate_includes_current_status():
    assert 'check_current_status(ROOT)' in (ROOT / 'scripts/check_site.py').read_text()


@pytest.mark.parametrize('name', [p for p in status.PAGES if p.endswith('.md')])
def test_markdown_lane_cannot_precede_current_decision(site, name):
    path = site / name
    first, rest = path.read_text().split('\n', 1)
    banner = '> Latest artifact — future date; unique and ready (stale claim)\n'
    path.write_text(first + '\n' + banner + rest)
    assert name in status.check(site)
    assert name in status.check(site, write=True)
    repaired = path.read_text()
    assert repaired.index(status.END) < repaired.index(banner)
    assert repaired.count(banner) == 1  # Preserve historical evidence.
    assert status.check(site) == []


@pytest.mark.parametrize('markdown', [True, False])
def test_reversed_markers_rejected(markdown):
    with pytest.raises(ValueError, match='end precedes begin'):
        status.render('# Heading\n' + status.END + status.BEGIN, 'block', markdown=markdown)


def test_markdown_requires_h1():
    with pytest.raises(ValueError, match='project H1'):
        status.render('stale claim\n', 'block', markdown=True)
