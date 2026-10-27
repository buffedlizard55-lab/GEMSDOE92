"""Freshness means GitHub ref comparison, never submission/score clearance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
import pytest

from scripts import audit_focus_freshness as freshness
from scripts.inspect_witness_support import describe_support

ROOT = Path(__file__).resolve().parents[1]


def test_freshness_receipt_fails_closed_and_binds_original_inventory():
    inventory = json.loads(freshness.INVENTORY.read_text())
    pins = {row['site']: row['repository_commit'] for row in inventory['selected_site_artifacts']}
    def mock_fetch(site):
        if site == 'GEMSDOE24':
            return {'sha': pins[site], 'commit_date': '2026-10-27T00:00:00Z'}
        if site == 'GEMSDOE25':
            return {'sha': 'f' * 40}
        if site == 'GEMSDOE27':
            raise OSError('sensitive subprocess output must not enter receipt')
        return {'sha': 'not-a-git-sha'}
    result = freshness.make_receipt(fetch=mock_fetch, observed_utc='2026-10-27T00:00:00Z')
    assert [x['status'] for x in result['sites'][:3]] == ['unchanged', 'changed', 'unknown']
    assert result['changed_count'] == 1 and result['unknown_count'] == 7
    assert result['complete'] is False and result['submission_eligible'] is False
    assert result['organizer_confirmed_score'] is None
    assert result['inventory_sha256'] == hashlib.sha256(freshness.INVENTORY.read_bytes()).hexdigest()
    assert 'sensitive' not in json.dumps(result)


def test_freshness_rejects_wrong_source_or_repeated_inventory(tmp_path):
    source = json.loads(freshness.INVENTORY.read_text())
    source['selected_site_artifacts'][0]['repository_commit'] = 'not-a-sha'
    broken = tmp_path / 'wrong.json'
    broken.write_text(json.dumps(source))
    with pytest.raises(ValueError, match='invalid pinned repository or commit'):
        freshness.make_receipt(broken, fetch=lambda _: {'sha': 'f' * 40})


def test_published_snapshot_is_bound_to_history_not_clearance():
    path = ROOT / 'docs/downloads/session_b97812a3_focus_freshness.json'
    receipt = json.loads(path.read_text())
    assert receipt['inventory_sha256'] == hashlib.sha256(freshness.INVENTORY.read_bytes()).hexdigest()
    assert len(receipt['sites']) == 9
    assert receipt['changed_count'] == sum(r['status'] == 'changed' for r in receipt['sites'])
    assert receipt['unknown_count'] == sum(r['status'] == 'unknown' for r in receipt['sites'])
    assert receipt['submission_eligible'] is False and receipt['organizer_confirmed_score'] is None


def test_witness_characterization_distinguishes_continuous_support():
    fp = np.array([[True, True], [False, True]])
    a = np.array([[.1, .2], [float('nan'), .8]], dtype='float32')
    got = describe_support(fp, a)
    assert got['positive_footprint_pixels'] == 3
    assert got['distinct_values'] == 3
    assert got['binary_zero_or_one_pixels'] == 0
    with pytest.raises(ValueError):
        describe_support(np.zeros((2, 2), dtype=bool), a)
    with pytest.raises(ValueError):
        describe_support(np.ones((2, 2), dtype=bool), a)


@pytest.mark.skipif(not shutil.which('node'), reason='Node is optional for browser script test')
def test_browser_freshness_only_hits_github_and_handles_failures():
    # Simulated DOM and fetch; no network. A malformed repo must not be queried.
    js = r'''
const labels = [
  {dataset:{focusRepo:'GEMSDOE24', pinnedSha:'a'.repeat(40)}},
  {dataset:{focusRepo:'GEMSDOE25', pinnedSha:'a'.repeat(40)}},
  {dataset:{focusRepo:'GEMSDOE27', pinnedSha:'a'.repeat(40)}},
  {dataset:{focusRepo:'../evil', pinnedSha:'a'.repeat(40)}}
];
const when = {};
global.document = {querySelectorAll: () => labels, querySelector: () => when};
const urls = [];
global.fetch = async url => {
  urls.push(url);
  if (url.includes('GEMSDOE27')) throw new Error('offline');
  return {ok:true, json:async () => ({sha: url.includes('GEMSDOE24') ? 'a'.repeat(40) : 'b'.repeat(40)})};
};
require(process.argv[1]);
setImmediate(() => console.log(JSON.stringify({labels, urls, when})));
'''
    result = subprocess.run([shutil.which('node'), '-e', js, str(ROOT / 'docs/focus-freshness.js')],
                            capture_output=True, text=True, check=True, timeout=10)
    data = json.loads(result.stdout)
    labels = data['labels']
    assert labels[0]['dataset']['freshness'] == 'unchanged'
    assert labels[1]['dataset']['freshness'] == 'changed'
    assert labels[2]['dataset']['freshness'] == 'unknown'
    assert 'unavailable' in labels[3]['textContent']
    assert labels[3]['dataset']['freshness'] == 'unknown'
    assert len(data['urls']) == 3
    assert all(url.startswith('https://api.github.com/repos/buffedlizard55-lab/GEMSDOE') for url in data['urls'])
    assert 'completed' in data['when']['textContent']
