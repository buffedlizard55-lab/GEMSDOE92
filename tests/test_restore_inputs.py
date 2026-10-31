"""Manifest compatibility and safety tests for pinned input restoration."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import restore_inputs


COMMIT_A = "a" * 40
COMMIT_B = "b" * 40
SHA_A = hashlib.sha256(b"sample grid bytes").hexdigest()
SHA_B = hashlib.sha256(b"official-mirror bytes").hexdigest()


def base_entry(**overrides):
    row = {
        "id": "sample_submission",
        "repo": "buffedlizard55-lab/GEMSDOE92",
        "ref": COMMIT_A,
        "path": "data/sample_submission.tif",
        "local_path": ".cache/gems_inputs/bridge/sample_submission.tif",
        "sha256": SHA_A,
        "bytes": len(b"sample grid bytes"),
    }
    row.update(overrides)
    return row


def test_normalises_legacy_ref_path_manifest():
    got = restore_inputs.normalise_manifest_entry(base_entry())
    assert got["repo"] == "buffedlizard55-lab/GEMSDOE92"
    assert got["ref"] == COMMIT_A
    assert got["path"] == "data/sample_submission.tif"
    assert got["local_path"] == ".cache/gems_inputs/bridge/sample_submission.tif"


def test_normalises_lidar_commit_repo_path_github_url_manifest():
    row = {
        "id": "ext_lidar_scarp_features_u8",
        "repo": "https://github.com/buffedlizard55-lab/GEMSDOE24.git",
        "commit": COMMIT_B,
        "repo_path": "data/external/lidar_scarp_features_u8.tif",
        "local_path": ".cache/gems_inputs/external/lidar_scarp_features_u8.tif",
        "sha256": SHA_B,
        "bytes": len(b"official-mirror bytes"),
    }
    got = restore_inputs.normalise_manifest_entry(row)
    assert got["repo"] == "buffedlizard55-lab/GEMSDOE24"
    assert got["ref"] == COMMIT_B
    assert got["path"] == "data/external/lidar_scarp_features_u8.tif"


@pytest.mark.parametrize(
    "repo",
    [
        "http://github.com/owner/repo.git",
        "https://example.org/owner/repo.git",
        "https://user@github.com/owner/repo.git",
        "https://github.com/owner/repo.git?ref=main",
        "owner/repo/extra",
        "../owner/repo",
    ],
)
def test_repository_source_must_be_github_https_and_safe(repo):
    with pytest.raises(ValueError):
        restore_inputs.normalise_manifest_entry(base_entry(repo=repo))


@pytest.mark.parametrize(
    "field,value",
    [
        ("ref", "short"),
        ("path", "../outside.tif"),
        ("path", "/absolute/file.tif"),
        ("path", "data\\outside.tif"),
        ("local_path", ".cache/gems_inputs/../../outside.tif"),
        ("local_path", "data/outside.tif"),
        ("sha256", "not-a-digest"),
        ("bytes", True),
    ],
)
def test_manifest_pins_and_paths_fail_closed(field, value):
    with pytest.raises(ValueError):
        restore_inputs.normalise_manifest_entry(base_entry(**{field: value}))


def test_multipart_parts_are_validated_and_normalised():
    row = base_entry(
        id="training_features",
        multipart=True,
        parts=["data/stack.part-000", "data/stack.part-001"],
    )
    got = restore_inputs.normalise_manifest_entry(row)
    assert got["parts"] == ["data/stack.part-000", "data/stack.part-001"]
    with pytest.raises(ValueError, match="multipart part"):
        restore_inputs.normalise_manifest_entry({**row, "parts": ["../escape"]})


def test_restore_accepts_both_schema_versions_without_network(tmp_path, monkeypatch, capsys):
    sample_bytes = b"sample grid bytes"
    lidar_bytes = b"official-mirror bytes"
    source_bytes = {
        "data/sample_submission.tif": sample_bytes,
        "data/external/lidar.tif": lidar_bytes,
    }
    base_manifest = tmp_path / "base.json"
    base_manifest.write_text(json.dumps({"files": [base_entry()]}), encoding="utf-8")
    lidar_manifest = tmp_path / "lidar.json"
    lidar_manifest.write_text(
        json.dumps(
            {
                "files": [
                    {
                        "id": "lidar",
                        "repo": "https://github.com/owner/lidar.git",
                        "commit": COMMIT_B,
                        "repo_path": "data/external/lidar.tif",
                        "local_path": ".cache/gems_inputs/external/lidar.tif",
                        "sha256": SHA_B,
                        "bytes": len(lidar_bytes),
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(restore_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(restore_inputs, "MANIFEST_PATH", base_manifest)
    monkeypatch.setattr(restore_inputs, "LIDAR1M_EXT_MANIFEST_PATH", lidar_manifest)

    calls = []

    def fake_sparse_fetch(repo_slug, commit, paths, temp_dir):
        calls.append((repo_slug, commit, list(paths)))
        checkout = Path(temp_dir) / "checkout"
        checkout.mkdir()
        for relative in paths:
            source = checkout / relative
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_bytes(source_bytes[relative])
        return checkout

    monkeypatch.setattr(restore_inputs, "sparse_fetch", fake_sparse_fetch)
    assert restore_inputs.main(["--lidar-1m"]) == 0

    assert {call[0] for call in calls} == {"buffedlizard55-lab/GEMSDOE92", "owner/lidar"}
    assert (tmp_path / ".cache/gems_inputs/bridge/sample_submission.tif").read_bytes() == sample_bytes
    assert (tmp_path / ".cache/gems_inputs/external/lidar.tif").read_bytes() == lidar_bytes
    assert (tmp_path / ".cache/data/sample_submission.tif").read_bytes() == sample_bytes
    assert "RESTORED sample_submission" in capsys.readouterr().out


def test_restore_refuses_duplicate_cache_destinations(tmp_path, monkeypatch):
    same = base_entry(id="external_duplicate")
    manifest = tmp_path / "base.json"
    manifest.write_text(json.dumps({"files": [base_entry(), same]}), encoding="utf-8")
    monkeypatch.setattr(restore_inputs, "ROOT", tmp_path)
    monkeypatch.setattr(restore_inputs, "MANIFEST_PATH", manifest)
    with pytest.raises(SystemExit, match="duplicate cache destinations"):
        restore_inputs.main([])
    assert not (tmp_path / ".cache/gems_inputs").exists()
