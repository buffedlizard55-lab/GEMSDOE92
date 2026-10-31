#!/usr/bin/env python3
"""Cross-check the pinned Focus-9 source files against a fresh registry-v3 snapshot.

This is a hash-identity audit only. It does not recalculate scores or spatial
3-pixel overlap, and a current owner-maintained GitHub mirror snapshot does not
establish organizer provenance. Exact SHA-256 matches elsewhere are sufficient
to reject a site file as a unique new artifact under the project protocol.

Example::

    .venv/bin/python scripts/audit_focus9_registry_v3.py \
        --inventory .cache/registry_v3/inventory.json \
        --output evidence/focus9_registry_20261030.json
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCES = ROOT / "evidence" / "focus9_sources_20261028.json"
DEFAULT_INVENTORY = ROOT / ".cache" / "registry_v3" / "inventory.json"
EXPECTED_SITES = {
    "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
    "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
}


def build_report(sources: dict, inventory: dict, inventory_sha256: str) -> dict:
    """Validate each pinned source row and list all same-byte registry copies."""
    if set(sources) != EXPECTED_SITES:
        raise ValueError(f"expected exactly the Focus-9 sites, got {sorted(sources)}")
    repositories = inventory.get("repositories")
    if not isinstance(repositories, list) or not repositories:
        raise ValueError("registry inventory has no repository rows")

    by_repo_path: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    by_sha: dict[str, list[dict]] = defaultdict(list)
    n_grid_rasters = 0
    for repo in repositories:
        owner, name = repo.get("owner"), repo.get("repo")
        if not isinstance(owner, str) or not isinstance(name, str):
            raise ValueError("registry repository row lacks owner/repo identity")
        for item in repo.get("files", []):
            row = dict(item, owner=owner, repo=name)
            by_repo_path[(owner, name, item.get("path", ""))].append(row)
            by_sha[item.get("sha256", "")].append(row)
            n_grid_rasters += 1

    rows = []
    for site in sorted(EXPECTED_SITES):
        source = sources[site]
        owner = "buffedlizard55-lab"
        repo = source.get("repo")
        path = source.get("path")
        digest = source.get("sha256")
        size = source.get("bytes")
        if (not isinstance(repo, str) or not isinstance(path, str)
                or not isinstance(digest, str) or len(digest) != 64
                or type(size) is not int or size <= 0):
            raise ValueError(f"{site}: malformed pinned source identity")
        source_key = (owner, repo, path)
        matches = by_repo_path.get(source_key, [])
        if not any(r.get("sha256") == digest and r.get("bytes") == size for r in matches):
            raise ValueError(f"{site}: pinned path/bytes/SHA is absent from fresh inventory")

        copies = []
        for item in by_sha[digest]:
            if (item["owner"], item["repo"], item.get("path")) == source_key:
                continue
            copies.append({
                "owner": item["owner"],
                "repo": item["repo"],
                "path": item.get("path"),
                "bytes": item.get("bytes"),
            })
        copies.sort(key=lambda x: (x["owner"], x["repo"], x["path"] or ""))
        rows.append({
            "site": site,
            "best_name": source.get("best"),
            "claim": source.get("claim"),
            "claim_evidence_class": "CLAIM (owner-reported; no organizer receipt verified)",
            "source_repository": f"{owner}/{repo}",
            "source_path": path,
            "source_commit": source.get("commit"),
            "source_git_blob_sha1": source.get("blob_inventory"),
            "sha256": digest,
            "bytes": size,
            "pinned_source_found_at_exact_path": True,
            "exact_copies_elsewhere": copies,
            "exact_copy_count_elsewhere": len(copies),
            "has_exact_copy_in_another_repository": any(
                (c["owner"], c["repo"]) != (owner, repo) for c in copies
            ),
            "unique_by_exact_sha_in_this_snapshot": not copies,
        })

    return {
        "schema": "gemsdoe92-focus9-registry-v3-hash-audit-v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evidence_class": "REGISTRY-MEASUREMENT (exact-byte identity only)",
        "source_manifest": "evidence/focus9_sources_20261028.json",
        "registry_snapshot": {
            "schema": inventory.get("schema"),
            "built_utc": inventory.get("built_utc"),
            "owners": inventory.get("owners", []),
            "owner_count": len(inventory.get("owners", [])),
            "repository_count": len(repositories),
            "grid_compatible_raster_records": n_grid_rasters,
            "unique_sha256_count": len(by_sha),
            "error_count": len(inventory.get("errors", [])),
            "inventory_sha256": inventory_sha256,
            "snapshot_method": "current default-branch GitHub owner-mirror tarballs; not organizer-authenticated or commit-pinned as a single fleet snapshot",
        },
        "summary": {
            "sites_checked": len(rows),
            "source_path_sha_size_matches": sum(r["pinned_source_found_at_exact_path"] for r in rows),
            "sites_with_exact_copies_elsewhere": sum(r["has_exact_copy_in_another_repository"] for r in rows),
            "sites_with_no_other_same_sha_path": sum(not r["exact_copies_elsewhere"] for r in rows),
        },
        "limitations": [
            "This audit verifies exact byte hashes against the current registry-v3 inventory only; it does not verify or recalculate owner-reported scores.",
            "The registry is a dated snapshot of owner-maintained public GitHub mirrors, not a live or organizer-authenticated submission registry.",
            "A byte match is a uniqueness rejection signal; absence of a byte match is not proof of spatial uniqueness under the 3-pixel overlap and rank-correlation rules.",
        ],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    sources_path = args.sources if args.sources.is_absolute() else ROOT / args.sources
    inventory_path = args.inventory if args.inventory.is_absolute() else ROOT / args.inventory
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    source_data = json.loads(sources_path.read_text(encoding="utf-8"))
    raw_inventory = inventory_path.read_bytes()
    inventory = json.loads(raw_inventory)
    report = build_report(source_data, inventory, hashlib.sha256(raw_inventory).hexdigest())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(
        f"Focus-9 exact-hash audit: {report['summary']['source_path_sha_size_matches']}/9 pinned files found; "
        f"{report['summary']['sites_with_exact_copies_elsewhere']}/9 have exact copies in another repo; "
        f"registry={report['registry_snapshot']['unique_sha256_count']} SHA-256"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
