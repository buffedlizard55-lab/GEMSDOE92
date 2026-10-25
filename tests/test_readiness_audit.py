"""The one-command audit must reject duplicates, never manufacture clearance."""
import base64
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import audit_readiness as mod


@pytest.fixture
def tiny_blob(monkeypatch):
    data = b'example pinned bytes'
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    monkeypatch.setattr(mod, 'WITNESS_BYTES', len(data))
    monkeypatch.setattr(mod, 'WITNESS_BLOB', blob)
    monkeypatch.setattr(mod, 'WITNESS_SHA256', hashlib.sha256(data).hexdigest())
    return data, {'sha': blob, 'size': len(data), 'encoding': 'base64',
                  'content': base64.b64encode(data).decode() + '\n'}


def test_decode_validates_full_identity(tiny_blob):
    data, doc = tiny_blob
    assert mod.decode_witness(doc) == data
    doc['content'] = base64.b64encode(b'changed pinned bytes').decode()
    with pytest.raises(ValueError, match='pinned'):
        mod.decode_witness(doc)


@pytest.mark.parametrize('key,value', [('encoding', 'raw'), ('sha', 'wrong'),
                                      ('size', True), ('content', None)])
def test_decode_rejects_bad_metadata(tiny_blob, key, value):
    _, doc = tiny_blob
    doc[key] = value
    with pytest.raises(ValueError, match='metadata'):
        mod.decode_witness(doc)


def test_decode_rejects_invalid_base64(tiny_blob):
    _, doc = tiny_blob
    doc['content'] = '!!!!'
    with pytest.raises(ValueError):
        mod.decode_witness(doc)


def test_fetch_is_verified_atomic_and_idempotent(tiny_blob, tmp_path, monkeypatch):
    data, doc = tiny_blob
    calls = []
    def run(*args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout=json.dumps(doc))
    monkeypatch.setattr(mod.subprocess, 'run', run)
    target = tmp_path / 'cache' / 'witness.tif'
    mod.fetch_witness(target)
    mod.fetch_witness(target)
    assert target.read_bytes() == data
    assert len(calls) == 1
    assert list(target.parent.iterdir()) == [target]


def test_corrupt_cache_is_not_overwritten(tiny_blob, tmp_path, monkeypatch):
    target = tmp_path / 'witness.tif'
    target.write_bytes(b'bad')
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a, **k: pytest.fail('network called'))
    with pytest.raises(ValueError, match='corrupt'):
        mod.fetch_witness(target)
    assert target.read_bytes() == b'bad'


def test_bad_response_is_not_cached(tiny_blob, tmp_path, monkeypatch):
    _, doc = tiny_blob
    doc['content'] = base64.b64encode(b'changed pinned bytes').decode()
    monkeypatch.setattr(mod.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout=json.dumps(doc)))
    target = tmp_path / 'cache' / 'witness.tif'
    with pytest.raises(ValueError):
        mod.fetch_witness(target)
    assert not target.exists()


def test_cli_preserves_previous_receipt(tmp_path, monkeypatch):
    target = tmp_path / 'receipt.json'
    target.write_text('prior')
    monkeypatch.setattr(mod, 'audit', lambda *a: pytest.fail('audit called'))
    assert mod.main(['--output', str(target)]) == 2
    assert target.read_text() == 'prior'


def test_cli_does_not_fetch_into_public_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, 'fetch_witness', lambda *a: pytest.fail('fetch called'))
    assert mod.main(['--output', str(tmp_path / 'r.json'), '--fetch-witness',
                     '--witness', str(tmp_path / 'public.tif')]) == 2


def test_cli_duplicate_exit_is_not_success(tmp_path, monkeypatch):
    monkeypatch.setattr(mod, 'audit', lambda *a: {'verdict': 'negative', 'submission_eligible': False})
    target = tmp_path / 'receipt.json'
    assert mod.main(['--output', str(target)]) == 1
    assert json.loads(target.read_text())['submission_eligible'] is False


def test_cli_missing_witness_is_inconclusive(tmp_path):
    target = tmp_path / 'receipt.json'
    assert mod.main(['--output', str(target), '--witness', str(tmp_path / 'missing.tif')]) == 2
    assert not target.exists()


def test_no_universal_stop_cannot_produce_receipt(monkeypatch):
    monkeypatch.setattr(mod, 'preflight', lambda *a: {'universal_nonempty_in_footprint_overlap_stop': False})
    with pytest.raises(ValueError, match='cannot grant clearance'):
        mod.audit(Path('.'), Path('witness.tif'))


@pytest.fixture
def published(tmp_path, monkeypatch):
    root = Path(__file__).resolve().parents[1]
    for rel in ('docs/downloads/review48_run_card.json', 'scripts/audit_readiness.py',
                'scripts/preflight_dense_witness.py', 'docs/review48.html'):
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((root / rel).read_bytes())
    status = json.loads((root / 'docs/downloads/readiness.json').read_text())
    monkeypatch.setattr(mod, 'build_status', lambda root: status)
    return tmp_path


def test_published_audit_is_byte_bound(published):
    assert mod.check_published_audit(published) == []


@pytest.mark.parametrize('key,value', [('submission_eligible', True), ('experiments', False),
                                      ('raster_sha256', 'bad'), ('format_pass', 'true'),
                                      ('validator_output', []), ('organizer_confirmed_score', 0.3)])
def test_publication_rejects_drift(published, key, value):
    path = published / 'docs/downloads/review48_run_card.json'
    card = json.loads(path.read_text())
    card[key] = value
    path.write_text(json.dumps(card))
    assert mod.check_published_audit(published)


@pytest.mark.parametrize('change', ['code', 'proof', 'holdout', 'missing', 'malformed'])
def test_publication_fails_closed_on_stale_or_invented_evidence(published, change):
    path = published / 'docs/downloads/review48_run_card.json'
    card = json.loads(path.read_text())
    if change == 'code':
        (published / 'scripts/audit_readiness.py').write_text('changed')
    elif change == 'proof':
        card['correlation_overlap_vs_registry']['preplacement_proof']['implementation_sha256'] = 'bad'
    elif change == 'holdout':
        card['holdout_dti']['value'] = 0.3
    elif change == 'missing':
        (published / 'docs/review48.html').unlink()
    else:
        card = []
    path.write_text(json.dumps(card))
    assert mod.check_published_audit(published)


def test_clean_review_links_and_download_match_current_primary():
    from html.parser import HTMLParser
    from urllib.parse import urlsplit, unquote
    from scripts.check_site import primary_download
    root = Path(__file__).resolve().parents[1]
    docs = root / 'docs'
    text = (docs / 'review48.html').read_text()
    class Links(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
        def handle_starttag(self, tag, attrs):
            if tag in ('a', 'link'):
                self.links.extend(v for k, v in attrs if k == 'href')
    parser = Links()
    parser.feed(text)
    for link in parser.links:
        url = urlsplit(link)
        if not url.scheme and not url.netloc and url.path:
            path = (docs / unquote(url.path)).resolve()
            assert path.is_relative_to(root)
            assert path.is_file(), link
    problems = []
    primary = primary_download((docs / 'index.html').read_text(), problems)
    assert not problems and primary in parser.links
    assert 'No new unique TIFF was generated' in text
    assert 'DO NOT SUBMIT' in text
    assert 'UNSCORED' in text
