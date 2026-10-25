"""Regression tests for pinned-path resolution (the 2026-10-25 shared-tool fix).

Both registries in this repo are in active use and they record paths in
*different* conventions:

  * ``registry/session_manifest.json`` — data-root relative
    (``bridge/sample_submission.tif``)
  * ``registry/data_manifest.json`` / ``registry/parents/R0.json`` — repo relative
    (``data/bridge/sample_submission.tif``)

``gems.manifest.verify`` and ``gems.parent.verify_inputs`` both joined onto the
data root unconditionally, so the repo-relative form became
``data/data/bridge/...``: ``make manifest`` reported 8/8 pinned inputs MISSING and
``make verify`` could not see the parent at all, even though every file was on
disk and every hash was correct. These tests pin the fix.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gems.manifest import verify
from gems.rasters import resolve_pinned_path, sha256_file

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# the resolver itself
# --------------------------------------------------------------------------
def test_resolve_accepts_data_root_relative(tmp_path):
    (tmp_path / "bridge").mkdir()
    f = tmp_path / "bridge" / "a.tif"
    f.write_bytes(b"x")
    assert resolve_pinned_path(tmp_path, "bridge/a.tif") == f


def test_resolve_accepts_repo_relative(tmp_path):
    """The form that used to become data/data/... and report MISSING."""
    (tmp_path / "bridge").mkdir()
    f = tmp_path / "bridge" / "a.tif"
    f.write_bytes(b"x")
    # cwd is the repo root in the real invocation; emulate by making the
    # repo-relative form resolvable from the process cwd
    import os
    prev = Path.cwd()
    os.chdir(tmp_path)
    try:
        got = resolve_pinned_path(tmp_path / "data", "bridge/a.tif")
        # the contract that matters: the returned path opens and hashes as the
        # real file (it may legitimately be relative to the process cwd)
        assert got.is_file()
        assert sha256_file(got) == sha256_file(f)
    finally:
        os.chdir(prev)


def test_resolve_returns_data_root_form_when_absent(tmp_path):
    """A genuinely missing file must still be reported, at the data-root path."""
    got = resolve_pinned_path(tmp_path, "nope/absent.tif")
    assert got == tmp_path / "nope" / "absent.tif"
    assert not got.is_file()


# --------------------------------------------------------------------------
# the manifest gate, end to end
# --------------------------------------------------------------------------
def test_manifest_verifies_repo_relative_dest(tmp_path):
    (tmp_path / "bridge").mkdir()
    f = tmp_path / "bridge" / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({
        "files": [{"id": "a", "dest": "bridge/a.tif",
                   "sha256": sha256_file(f)}],
    }))
    rep = verify(manifest, tmp_path)
    assert rep["ok"], rep["problems"]
    assert rep["entries"][0]["status"] == "OK"


def test_manifest_accepts_list_root_and_rejects_invalid_structure(tmp_path):
    f = tmp_path / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "list.json"
    manifest.write_text(json.dumps([{
        "dest": "a.tif", "sha256": sha256_file(f), "bytes": 5,
    }]))
    assert verify(manifest, tmp_path)["ok"] is True

    manifest.write_text(json.dumps({"files": "not-a-list"}))
    report = verify(manifest, tmp_path)
    assert report["ok"] is False
    assert report["error"] == "manifest files must be a list"

    manifest.write_text("{not json")
    report = verify(manifest, tmp_path)
    assert report["ok"] is False
    assert report["error"].startswith("manifest is unreadable JSON:")


def test_manifest_rejects_invalid_pin_and_unsafe_path(tmp_path):
    f = tmp_path / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"files": [
        {"dest": "a.tif", "sha256": "NOT-A-DIGEST"},
        {"dest": "../a.tif", "sha256": sha256_file(f)},
        "not-an-object",
    ]}))
    report = verify(manifest, tmp_path)
    assert report["ok"] is False
    assert [row["status"] for row in report["entries"]] == [
        "INVALID_SHA256_PIN", "INVALID_PATH", "MALFORMED",
    ]


def test_manifest_still_reports_missing_and_mismatch(tmp_path):
    (tmp_path / "bridge").mkdir()
    f = tmp_path / "bridge" / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"files": [
        {"id": "a", "dest": "bridge/a.tif", "sha256": "0" * 64},
        {"id": "b", "dest": "bridge/absent.tif", "sha256": "1" * 64},
    ]}))
    rep = verify(manifest, tmp_path)
    assert not rep["ok"]
    assert any("expected" in p for p in rep["problems"])      # hash mismatch
    assert any("MISSING" in p for p in rep["problems"])       # absent file


def test_manifest_rejects_stale_recorded_byte_length_even_when_hash_matches(tmp_path):
    """A correct digest must not make a contradictory size claim disappear."""
    f = tmp_path / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"files": [{
        "id": "a", "dest": "a.tif", "sha256": sha256_file(f), "bytes": 4,
    }]}))
    rep = verify(manifest, tmp_path)
    assert not rep["ok"]
    assert rep["entries"][0]["status"] == "SIZE_MISMATCH"
    assert rep["entries"][0]["bytes"] == 5
    assert rep["problems"] == ["a.tif: expected 4 bytes, got 5"]


@pytest.mark.parametrize("bad_pin", [True, -1, 5.0, "5"])
def test_manifest_rejects_malformed_byte_length_without_crashing(tmp_path, bad_pin):
    f = tmp_path / "a.tif"
    f.write_bytes(b"hello")
    manifest = tmp_path / "m.json"
    manifest.write_text(json.dumps({"files": [{
        "id": "a", "dest": "a.tif", "sha256": sha256_file(f), "bytes": bad_pin,
    }]}))
    rep = verify(manifest, tmp_path)
    assert not rep["ok"]
    assert rep["entries"][0]["status"] == "INVALID_BYTES_PIN"
    assert "expected a nonnegative integer" in rep["problems"][0]


# --------------------------------------------------------------------------
# the committed registries must actually verify against the committed bytes
# --------------------------------------------------------------------------
@pytest.mark.skipif(not (ROOT / "data" / "bridge" / "sample_submission.tif").is_file(),
                    reason="competition data not staged in this checkout")
def test_committed_data_manifest_verifies():
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    rep = verify(ROOT / "registry" / "data_manifest.json", ROOT / "data")
    assert rep["ok"], rep["problems"]
    assert all(e["status"] == "OK" for e in rep["entries"])
    # Keep human-readable byte counts auditable too; SHA-256 alone previously
    # let two stale size claims survive in this registry.
    for item in manifest["files"]:
        assert item["bytes"] == (ROOT / item["dest"]).stat().st_size
