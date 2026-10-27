"""Upstream pins and local shared-template overrides stay honest and verifiable."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_vendor_files_match_source_or_explicit_local_override():
    pins = json.loads((ROOT / 'registry/vendor_pins.json').read_text())
    upstream = pins['sha256']
    local = pins['local_overrides_sha256']
    assert set(local) == {'gates.py', 'submission_writer.py', 'uniqueness.py', 'validate.py'}
    assert set(local) <= set(upstream)
    for name, source_digest in upstream.items():
        path = ROOT / 'vendor/gems57' / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == local.get(name, source_digest), name
        if name in local:
            assert actual != source_digest, f'{name}: remove obsolete override'
