from __future__ import annotations

import hashlib

import pytest

from scripts.audit_focus9_registry_v3 import EXPECTED_SITES, build_report


def sample_sources():
    return {
        site: {
            "best": f"peak-{site}",
            "claim": 0.25,
            "repo": site,
            "path": f"docs/downloads/{site}.tif",
            "sha256": hashlib.sha256(site.encode()).hexdigest(),
            "bytes": 100,
            "commit": "a" * 40,
            "blob_inventory": "b" * 40,
        }
        for site in EXPECTED_SITES
    }


def sample_inventory(sources):
    repos = []
    for site, row in sources.items():
        repos.append({
            "owner": "buffedlizard55-lab",
            "repo": site,
            "files": [{"path": row["path"], "sha256": row["sha256"], "bytes": row["bytes"]}],
        })
    # One exact byte clone in a second repository; do not mistake an owner claim
    # or filename for the identity test.
    first = next(iter(sources.items()))
    site, row = first
    repos.append({
        "owner": "another-owner",
        "repo": "GEMSDOE-copy",
        "files": [{"path": "archive/renamed.tif", "sha256": row["sha256"], "bytes": row["bytes"]}],
    })
    return {"schema": "gemsdoe92-registry-v3", "built_utc": "2026-10-30T00:00:00Z",
            "owners": ["buffedlizard55-lab", "another-owner"], "repositories": repos, "errors": []}


def test_focus9_crosscheck_binds_paths_hashes_and_exact_copies():
    sources = sample_sources()
    report = build_report(sources, sample_inventory(sources), "c" * 64)
    assert report["summary"]["sites_checked"] == 9
    assert report["summary"]["source_path_sha_size_matches"] == 9
    assert report["summary"]["sites_with_exact_copies_elsewhere"] == 1
    cloned = next(row for row in report["rows"] if row["exact_copies_elsewhere"])
    assert cloned["has_exact_copy_in_another_repository"] is True
    assert cloned["unique_by_exact_sha_in_this_snapshot"] is False
    assert cloned["exact_copies_elsewhere"][0]["repo"] == "GEMSDOE-copy"


def test_focus9_crosscheck_fails_if_source_bytes_do_not_match_inventory():
    sources = sample_sources()
    inventory = sample_inventory(sources)
    inventory["repositories"][0]["files"][0]["sha256"] = "d" * 64
    with pytest.raises(ValueError, match="pinned path/bytes/SHA"):
        build_report(sources, inventory, "c" * 64)


def test_focus9_crosscheck_requires_exact_nine_site_set():
    sources = sample_sources()
    sources.pop(next(iter(sources)))
    with pytest.raises(ValueError, match="exactly the Focus-9 sites"):
        build_report(sources, sample_inventory(sources), "c" * 64)
