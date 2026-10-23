#!/usr/bin/env python3
"""Fail-closed startup gate: verify manifest pins and byte-exactly rebuild R0."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

from gems92 import core  # noqa: E402

OUT = ROOT / "registry" / "r0_verification.json"


def main() -> int:
    verified = core.verify_manifest()
    lin = core.rebuild_r0_from_lineage(verified)
    foot, catalogue, r0, d_cat = lin["foot"], lin["catalogue"], lin["r0"], lin["d_cat"]
    dvals = d_cat[r0]
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text(encoding="utf-8"))
    pins = []
    for entry in manifest["files"]:
        p = verified[entry["id"]]
        pins.append({
            "id": entry["id"], "path": entry["local_path"],
            "sha256": core.sha256_file(p), "expected_sha256": entry["sha256"],
            "bytes": p.stat().st_size, "expected_bytes": entry["bytes"],
            "ok": core.sha256_file(p) == entry["sha256"] and p.stat().st_size == entry["bytes"],
        })
    report = {
        "schema": "gems92.r0-exact-rebuild.v1",
        "parent": core.PARENT_ID,
        "manifest": {"path": "registry/data_manifest.json",
                     "schema_version": manifest["schema_version"],
                     "verified_count": len(pins),
                     "all_sha256_and_byte_lengths_match": all(i["ok"] for i in pins),
                     "files": pins},
        "lineage_rebuild": {
            "method": "full recorded H19-5 -> D1.5 -> D2.8 -> SOLO-D2.8 -> R0 recipe",
            "pixel_identical_to_pinned_r0": True,
            "intermediate_pixel_checks": ["D1.5", "D2.8", "SOLO-D2.8"],
            "n_dots": int(r0.sum()),
            "zeros_sha256": lin["rebuilt_zeros_sha256"],
            "expected_zeros_sha256": core.PARENT_SHA_ZEROS,
            "zeros_sha256_exact": lin["rebuilt_zeros_sha256"] == core.PARENT_SHA_ZEROS,
            "nan_sha256": lin["rebuilt_nan_sha256"],
            "expected_nan_sha256": core.PARENT_SHA_NAN,
            "nan_sha256_exact": lin["rebuilt_nan_sha256"] == core.PARENT_SHA_NAN,
        },
        "parent_geometry": {
            "footprint_px": int(foot.sum()), "catalogue_px": int(catalogue.sum()),
            "zero_catalogue_mass": int((r0 & catalogue).sum()) == 0,
            "min_catalogue_distance_px": float(dvals.min()),
            "n_within_2px": int((dvals <= 2.0).sum()),
            "n_within_3px": int((dvals <= 3.0).sum()),
            "dots": int(r0.sum()),
        },
        "note": "R0 SHA-256 equality is mandatory, not approximated; R0 0.2778 remains CLAIM without a submission receipt.",
    }
    report["ok"] = bool(
        report["manifest"]["all_sha256_and_byte_lengths_match"]
        and report["lineage_rebuild"]["n_dots"] == 37_654
        and report["lineage_rebuild"]["zeros_sha256_exact"]
        and report["lineage_rebuild"]["nan_sha256_exact"]
        and report["parent_geometry"]["zero_catalogue_mass"]
        and report["parent_geometry"]["n_within_2px"] == 0
    )
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "verified_inputs": len(pins),
                      "parent_dots": int(r0.sum()),
                      "zeros_sha256": lin["rebuilt_zeros_sha256"],
                      "nan_sha256": lin["rebuilt_nan_sha256"],
                      "report": str(OUT.relative_to(ROOT))}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
