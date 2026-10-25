"""Gate receipts cannot pass by truthiness, missing rows, or vacuous all()."""
import json
from pathlib import Path

import pytest

from scripts.check_site import check_recorded_gates

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-audit.json'


def receipt():
    return json.loads(AUDIT.read_text())


def test_actual_primary_receipt_is_complete():
    problems = []
    check_recorded_gates(receipt(), problems)
    assert problems == []


@pytest.mark.parametrize('bad_rows', [None, {}, [], 'PASS', [None], [{}],
                                     [{'name': 'crs', 'ok': 'true'}],
                                     [{'name': 'crs', 'ok': 1}]])
def test_malformed_rows_fail_closed_without_crash(bad_rows):
    problems = []
    check_recorded_gates({'gates_zeros': bad_rows}, problems)
    assert problems


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'false', 'truthy'])
def test_complete_receipt_cannot_hide_a_bad_gate(mutation):
    doc = receipt()
    rows = doc['gates_zeros']
    if mutation == 'missing':
        rows.pop()
    elif mutation == 'duplicate':
        rows.append(rows[0].copy())
    elif mutation == 'false':
        rows[0]['ok'] = False
    else:
        rows[0]['ok'] = 'false'
    problems = []
    check_recorded_gates(doc, problems)
    assert problems


def test_ci_primary_receipt_gate_uses_explicit_primary_marker():
    workflow = (ROOT / '.github/workflows/ci.yml').read_text()
    assert 'data-primary="true"' in workflow
    assert 'must declare exactly one data-primary=true download' in workflow
    assert 'm = re.search' not in workflow


def test_pages_stages_public_files_without_breaking_existing_docs_urls():
    workflow = (ROOT / '.github/workflows/pages.yml').read_text()
    assert workflow.index('python scripts/check_site.py') < workflow.index('cp -R docs')
    assert 'cp index.html .nojekyll .cache/pages/' in workflow
    assert 'cp -R docs .cache/pages/docs' in workflow
    assert 'path: .cache/pages' in workflow
    assert 'path: .' not in workflow.replace('path: .cache/pages', '')
