"""Tests for the `mode: pinned_artefact` parent verification path.

`registry/parents/R0.json` is not a rebuild recipe: R0 was produced upstream in
GEMSDOE32 and no recipe reproduces it bit-for-bit. Before 2026-10-25 the
`gems.parent.Recipe` loader only understood the rebuild form, so `make verify` --
advertised in the Makefile as the gate that stops a session before it burns slots
on descendants of an unverified parent -- errored out unconditionally and proved
nothing. These tests pin the replacement behaviour: byte identity AND a
re-measurement of the invariants the record claims.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems.parent import (ParentUnavailable, Recipe, compare_claimed_invariants,
                         verify_pinned_artefact)

ROOT = Path(__file__).resolve().parents[1]


def _write(parent_dir: Path, name: str, arr: np.ndarray, nodata) -> Path:
    p = parent_dir / name
    with rasterio.open(p, "w", driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                       count=1, dtype="float32", crs="EPSG:32611",
                       transform=from_origin(500000, 4200000, 100, 100),
                       nodata=nodata) as ds:
        ds.write(arr.astype(np.float32), 1)
    return p


def _recipe(parent_dir: Path, root: Path, artefact: str, sha: str, size: int,
            verified: dict | None = None) -> Path:
    doc = {
        "parent_id": "T0",
        "mode": "pinned_artefact",
        "files": {"zeros": {"path": str(artefact), "sha256": sha, "bytes": size}},
    }
    if verified is not None:
        doc["verified"] = verified
    p = parent_dir / "T0.json"
    p.write_text(json.dumps(doc))
    return p


# --------------------------------------------------------------------------
# loader
# --------------------------------------------------------------------------
def test_pinned_artefact_recipe_loads_without_rebuild_keys(tmp_path):
    doc = {"parent_id": "T0", "mode": "pinned_artefact",
           "files": {"zeros": {"path": "data/t0.tif",
                               "sha256": "a" * 64, "bytes": 10}}}
    p = tmp_path / "T0.json"
    p.write_text(json.dumps(doc))
    r = Recipe.load(p)
    assert r.mode == "pinned_artefact"
    assert r.parent_id == "T0"
    assert r.expected_sha256 == "a" * 64   # primary encoding = zeros when present


def test_pinned_artefact_rejects_placeholder_sha(tmp_path):
    doc = {"parent_id": "T0", "mode": "pinned_artefact",
           "files": {"zeros": {"path": "data/t0.tif", "sha256": "REPLACE_ME"}}}
    p = tmp_path / "T0.json"
    p.write_text(json.dumps(doc))
    with pytest.raises(ParentUnavailable, match="template or incomplete"):
        Recipe.load(p)


def test_pinned_artefact_rejects_empty_files(tmp_path):
    p = tmp_path / "T0.json"
    p.write_text(json.dumps({"parent_id": "T0", "mode": "pinned_artefact", "files": {}}))
    with pytest.raises(ParentUnavailable, match="template or incomplete"):
        Recipe.load(p)


def test_pinned_artefact_rejects_missing_byte_length(tmp_path):
    p = tmp_path / "T0.json"
    p.write_text(json.dumps({"parent_id": "T0", "mode": "pinned_artefact",
                             "files": {"zeros": {"path": "data/t0.tif", "sha256": "b" * 64}}}))
    with pytest.raises(ParentUnavailable, match="records no byte length"):
        Recipe.load(p)


def test_rebuild_recipe_still_requires_its_keys(tmp_path):
    """The fix must not weaken the original rebuild contract."""
    p = tmp_path / "R.json"
    p.write_text(json.dumps({"parent_id": "R0", "builder": "gems.builders.x"}))
    with pytest.raises(ParentUnavailable, match="lacks required keys"):
        Recipe.load(p)


# --------------------------------------------------------------------------
# verification: byte identity, then re-measured invariants
# --------------------------------------------------------------------------
def test_verify_pinned_artefact_passes_and_remeasures(tmp_path):
    import hashlib
    from scipy.ndimage import distance_transform_edt

    data = tmp_path / "data"
    (data / "bridge").mkdir(parents=True)
    arr = np.zeros((40, 50), np.float32)
    arr[10, 10] = 1.0
    arr[10, 20] = 1.0
    art = _write(data, "t0.tif", arr, None)

    ref = np.full((40, 50), np.nan, np.float32)
    ref[5:35, 5:45] = 0.0
    _write(data / "bridge", "sample_submission.tif", ref, np.float32(np.nan))
    cat = np.zeros((40, 50), np.float32)
    cat[10, 30] = 1.0
    _write(data / "bridge", "existing_faults.tif", cat, None)

    sha = hashlib.sha256(art.read_bytes()).hexdigest()
    d_cat = distance_transform_edt(~((cat > 0) & np.isfinite(ref)))
    claimed = {"n_dots": 2, "total_mass": 2.0, "footprint_px": int(np.isfinite(ref).sum()),
               "min_catalogue_distance_px": float(d_cat[arr > 0].min())}
    rp = _recipe(tmp_path, data, "t0.tif", sha, art.stat().st_size, claimed)

    report = verify_pinned_artefact(Recipe.load(rp), data)
    assert report["ok"], report["problems"]
    assert report["measured"]["remeasured"]["n_dots"] == 2
    assert compare_claimed_invariants(rp, report["measured"]["remeasured"]) == []


def test_verify_pinned_artefact_catches_wrong_sha(tmp_path):
    import hashlib
    data = tmp_path / "data"
    data.mkdir()
    arr = np.zeros((20, 20), np.float32)
    arr[5, 5] = 1.0
    art = _write(data, "t0.tif", arr, None)
    rp = _recipe(tmp_path, data, "t0.tif", "c" * 64, art.stat().st_size)
    report = verify_pinned_artefact(Recipe.load(rp), data, measure=False)
    assert not report["ok"]
    assert any("HASH MISMATCH" in p for p in report["problems"])


def test_verify_pinned_artefact_catches_stale_byte_length(tmp_path):
    """Exactly the defect found in registry/parents/R0.json on 2026-10-25."""
    import hashlib
    data = tmp_path / "data"
    data.mkdir()
    arr = np.zeros((20, 20), np.float32)
    arr[5, 5] = 1.0
    art = _write(data, "t0.tif", arr, None)
    rp = _recipe(tmp_path, data, "t0.tif",
                 hashlib.sha256(art.read_bytes()).hexdigest(),
                 art.stat().st_size - 443)
    report = verify_pinned_artefact(Recipe.load(rp), data, measure=False)
    assert not report["ok"]
    assert any("LENGTH MISMATCH" in p for p in report["problems"])


def test_verify_pinned_artefact_catches_missing_file(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    rp = _recipe(tmp_path, data, "nope.tif", "d" * 64, 10)
    report = verify_pinned_artefact(Recipe.load(rp), data, measure=False)
    assert not report["ok"]
    assert any("MISSING" in p for p in report["problems"])


def test_compare_claimed_invariants_flags_drift(tmp_path):
    rp = tmp_path / "T0.json"
    rp.write_text(json.dumps({"parent_id": "T0", "mode": "pinned_artefact",
                              "files": {"zeros": {"path": "x", "sha256": "e" * 64, "bytes": 1}},
                              "verified": {"n_dots": 37654, "date": "2026-10-23"}}))
    drift = compare_claimed_invariants(rp, {"n_dots": 37653})
    assert len(drift) == 1 and "n_dots" in drift[0]
    # a matching number and a non-compared key produce no drift
    assert compare_claimed_invariants(rp, {"n_dots": 37654, "date": "1999-01-01"}) == []


@pytest.mark.skipif(not (ROOT / "data" / "parent_R0_zeros.tif").is_file(),
                    reason="parent artefact not staged in this checkout")
def test_repo_root_parent_verifies_against_committed_bytes():
    """The real gate: the committed R0 record must hold against the committed file."""
    rp = ROOT / "registry" / "parents" / "R0.json"
    recipe = Recipe.load(rp)
    assert recipe.mode == "pinned_artefact"
    report = verify_pinned_artefact(recipe, ROOT / "data")
    assert report["ok"], report["problems"]
    assert report["measured"]["remeasured"]["n_dots"] == 37654
    assert compare_claimed_invariants(rp, report["measured"]["remeasured"]) == []
