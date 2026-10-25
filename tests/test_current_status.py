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
    primary = card['primary_download']
    audit = str(Path(primary).with_name(Path(primary).stem.removesuffix('-zeros') + '-audit.json'))
    paths = ['docs/index.html', *status.PAGES, status.CARD, primary, audit,
             'evidence/review_f23_preflight.json',
             'docs/REVIEW_20261025_SESSION_FOLLOWUP.md',
             'docs/downloads/session_followup_20261025_run_card.json',
             'docs/ANALYSIS_20261025_LEADERBOARD.md']
    for name in paths:
        dest = tmp_path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, dest)
    return tmp_path


def test_readme_preserves_session_start_brief_and_ordered_inputs():
    text = (ROOT / 'README.md').read_text()
    assert '### Persisted user brief — starting point for every session' in text
    assert 'Read this README and [SESSION_PROMPT.md](SESSION_PROMPT.md) before work.' in text
    assert '### Start every session here' in text
    assert '[current review](docs/REVIEW_CURRENT.md)' in text
    assert '[ordered next steps](docs/NEXT_STEPS.md)' in text
    assert '[full supplied site-score inventory](ledger/site_scores_claimed_20261025.csv)' in text
    assert 'This expandable prompt block is a **normalized, condensed operating brief**' in text
    assert 'preserved verbatim as historical input' not in text


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
        assert 'REVIEW_20261025_SESSION_FOLLOWUP.md' in block
        assert 'session_followup_20261025_run_card.json' in block
        assert 'ANALYSIS_20261025_LEADERBOARD.md' in block
        assert 'DO NOT SUBMIT' in block
        assert 'HOLDOUT-DTI' in block
        assert 'unique' in block.lower() and 'DO NOT SUBMIT' in block
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
        public_dense_witness_forward_overlap=value))
    with pytest.raises(ValueError, match='registry rejection'):
        status.load_card(site)


def test_rejects_changed_bytes(site):
    card = status.load_card(site)
    (site / card['primary_download']).write_bytes(b'changed')
    with pytest.raises(ValueError, match='SHA-256'):
        status.load_card(site)


@pytest.mark.parametrize('value', [False, 'true', 1, None])
def test_format_flag_requires_boolean_true(site, value):
    card = json.loads((site / status.CARD).read_text())
    primary = card['primary_download']
    path = (site / primary).with_name(Path(primary).stem.removesuffix('-zeros') + '-audit.json')
    audit = json.loads(path.read_text())
    audit['gates_zeros_pass'] = value
    path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match='validator'):
        status.load_card(site)


@pytest.mark.parametrize('rows', [[], [{'name': 'crs', 'ok': True}],
                                  [{'name': 'crs', 'ok': 'true'}]])
def test_incomplete_format_evidence_cannot_be_published(site, rows):
    card = json.loads((site / status.CARD).read_text())
    primary = card['primary_download']
    path = (site / primary).with_name(Path(primary).stem.removesuffix('-zeros') + '-audit.json')
    audit = json.loads(path.read_text())
    audit['gates_zeros'] = rows
    path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match='format gates'):
        status.load_card(site)


@pytest.mark.parametrize('field', ['correlation_overlap_vs_registry'])
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


def test_preflight_pin_must_match(site):
    path = site / 'evidence/review_f23_preflight.json'
    proof = json.loads(path.read_text())
    proof['sha256'] = 'bad'
    path.write_text(json.dumps(proof))
    with pytest.raises(ValueError, match='preflight'):
        status.load_card(site)


def test_stale_panel_fails_check_and_is_repairable(site):
    path = site / 'index.html'
    path.write_text(path.read_text().replace('Current decision: research-only TIFF; submission blocked', 'stale decision'))
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
