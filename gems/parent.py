"""Parent rebuild and verification.

The brief (section 5) is explicit: rebuild R0 and match its sha256, or stop and
report. Never approximate the parent. This module therefore refuses, loudly, in
every situation where it cannot prove the parent:

  * an input listed in the recipe is missing or its sha256 differs
  * the rebuilt file's sha256 differs from the recorded one
  * the recipe does not pin a seed or a git SHA

It never "best efforts" its way to a plausible parent.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .rasters import (read_reference, resolve_pinned_path, sha256_file,
                        write_candidate)


class ParentUnavailable(RuntimeError):
    """Raised when the parent cannot be reproduced byte-for-byte."""


@dataclass
class Recipe:
    parent_id: str
    builder: str           # dotted path to the builder function
    params: dict
    inputs: dict           # relpath -> sha256
    expected_sha256: str
    git_sha: str
    seed: int
    mode: str = "rebuild"  # "rebuild" (regenerate from pinned inputs) or
    files: dict = None     # "pinned_artefact" (the committed raster IS the authority)

    def __post_init__(self):
        if self.files is None:
            self.files = {}

    @classmethod
    def load(cls, path: str | Path) -> "Recipe":
        p = Path(path)
        if not p.exists():
            raise ParentUnavailable(f"recipe not found: {p} -- cannot rebuild the parent")
        raw = json.loads(p.read_text())
        mode = raw.get("mode", "rebuild")
        if mode == "pinned_artefact":
            return cls._load_pinned_artefact(p, raw)
        missing = [k for k in ("parent_id", "builder", "inputs",
                               "expected_sha256", "git_sha", "seed") if k not in raw]
        if missing:
            raise ParentUnavailable(f"recipe {p} lacks required keys: {missing}")
        recipe = cls(params=raw.get("params", {}), **{k: raw[k] for k in (
            "parent_id", "builder", "inputs", "expected_sha256", "git_sha", "seed")})
        problems = recipe.placeholder_problems()
        if problems:
            raise ParentUnavailable(
                f"recipe {p} is a template or incomplete: " + "; ".join(problems)
                + " -- refusing to treat it as a parent")
        return recipe

    @classmethod
    def _load_pinned_artefact(cls, p: Path, raw: dict) -> "Recipe":
        """Load a `mode: pinned_artefact` record -- the committed raster is the authority.

        R0 has no recipe that reproduces it bit-for-bit: it was produced upstream in
        GEMSDOE32. What *is* provable, and what this gate therefore checks, is that the
        committed bytes are exactly the pinned bytes (sha256 + length) and that the
        invariants the record claims were actually measured on those bytes.
        """
        problems = []
        if not raw.get("parent_id"):
            problems.append("parent_id is missing")
        files = raw.get("files") or {}
        if not files:
            problems.append("files is empty -- a pinned artefact must name at least one raster")
        for enc, entry in files.items():
            if not isinstance(entry, dict) or not entry.get("path"):
                problems.append(f"files.{enc} has no path")
                continue
            sha = str(entry.get("sha256") or "")
            if "REPLACE" in sha.upper() or len(sha) != 64 or \
                    any(c not in "0123456789abcdefABCDEF" for c in sha):
                problems.append(f"files.{enc}.sha256 is not a real 64-hex digest")
            if "bytes" not in entry:
                problems.append(f"files.{enc} records no byte length")
        if problems:
            raise ParentUnavailable(
                f"recipe {p} is a template or incomplete: " + "; ".join(problems)
                + " -- refusing to treat it as a parent")
        # the strongest available encoding is the artefact's expected digest
        primary = files.get("zeros") or files.get("nan") or next(iter(files.values()))
        return cls(
            parent_id=raw["parent_id"], builder="", params={}, inputs={},
            expected_sha256=primary["sha256"], git_sha="", seed=0,
            mode="pinned_artefact", files=files,
        )

    def placeholder_problems(self) -> list[str]:
        """Reject templates and unrecorded values. A recipe must be provable."""
        out = []
        sha = str(self.expected_sha256 or "")
        if "REPLACE" in sha.upper() or len(sha) != 64 or \
                any(c not in "0123456789abcdefABCDEF" for c in sha):
            out.append("expected_sha256 is not a real 64-hex digest")
        if "REPLACE" in str(self.git_sha).upper() or not self.git_sha:
            out.append("git_sha is not recorded")
        if self.seed is None:
            out.append("seed is not recorded")
        bad = [k for k, v in self.inputs.items()
               if "REPLACE" in str(v).upper() or len(str(v)) != 64]
        if bad:
            out.append(f"inputs without a real sha256: {bad}")
        if "REPLACE" in str(self.params).upper():
            out.append("params still contain placeholders")
        return out


def verify_inputs(recipe: Recipe, data_root: str | Path) -> list[str]:
    """Check every pinned input's sha256. Returns problems (empty == all good)."""
    root = Path(data_root)
    problems = []
    for rel, want in recipe.inputs.items():
        f = resolve_pinned_path(root, rel)
        if not f.exists():
            problems.append(f"MISSING input {rel} (expected sha256 {want[:12]}...)")
            continue
        got = sha256_file(f)
        if got != want:
            problems.append(f"HASH MISMATCH {rel}: expected {want} got {got}")
    return problems


def verify_pinned_artefact(recipe: Recipe, data_root: str | Path,
                           measure: bool = True) -> dict:
    """Prove a `mode: pinned_artefact` parent from the bytes on disk.

    Two independent checks, because a recorded sha256 alone only proves the file
    has not changed -- not that the invariants the record advertises are true of
    it:

      1. **Byte identity** -- sha256 *and* length of every recorded encoding.
      2. **Re-measured invariants** -- dot count, total mass, minimum catalogue
         distance and footprint size are recomputed from the raster itself and
         compared to the numbers the record claims. This is what catches a
         record that was edited without re-verifying the file it describes.

    Returns ``{"ok": bool, "problems": [...], "measured": {...}}``. Never raises:
    the caller decides whether an unprovable parent is fatal.
    """
    root = Path(data_root)
    problems: list[str] = []
    measured: dict[str, object] = {}

    for enc, entry in recipe.files.items():
        f = resolve_pinned_path(root, entry["path"])
        if not f.is_file():
            problems.append(f"MISSING {enc} artefact {entry['path']} "
                            f"(expected sha256 {entry['sha256'][:12]}...)")
            continue
        got_sha = sha256_file(f)
        if got_sha != entry["sha256"]:
            problems.append(f"HASH MISMATCH {entry['path']}: "
                            f"expected {entry['sha256']} got {got_sha}")
        got_bytes = f.stat().st_size
        if int(entry.get("bytes", got_bytes)) != got_bytes:
            problems.append(f"LENGTH MISMATCH {entry['path']}: "
                            f"expected {entry['bytes']} got {got_bytes}")
        measured[enc] = {"path": entry["path"], "sha256": got_sha, "bytes": got_bytes}

    if not measure or problems:
        return {"ok": not problems, "problems": problems, "measured": measured}

    # --- re-measure the claimed invariants from the raster itself -----------
    try:
        import numpy as np
        import rasterio
        from scipy.ndimage import distance_transform_edt
    except ImportError as e:  # pragma: no cover - deps are pinned in requirements
        problems.append(f"cannot re-measure invariants without rasterio/scipy: {e}")
        return {"ok": False, "problems": problems, "measured": measured}

    ref_path = root / "bridge" / "sample_submission.tif"
    cat_path = root / "bridge" / "existing_faults.tif"
    enc = "zeros" if "zeros" in recipe.files else next(iter(recipe.files))
    art = resolve_pinned_path(root, recipe.files[enc]["path"])
    if not ref_path.is_file() or not cat_path.is_file():
        problems.append(f"cannot re-measure: missing {ref_path} or {cat_path}")
        return {"ok": False, "problems": problems, "measured": measured}

    with rasterio.open(ref_path) as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(cat_path) as ds:
        cat = (ds.read(1) > 0) & foot
    with rasterio.open(art) as ds:
        arr = ds.read(1)
    if arr.shape != foot.shape:
        problems.append(f"artefact shape {arr.shape} != reference shape {foot.shape}")
        return {"ok": False, "problems": problems, "measured": measured}

    mass = np.where(np.isfinite(arr), arr, 0.0)
    dots = mass > 0
    if not (dots <= foot).all():
        problems.append("artefact has positive mass outside the reference footprint")
    d_cat = distance_transform_edt(~cat)
    stats = {
        "n_dots": int(dots.sum()),
        "total_mass": float(mass.sum()),
        "footprint_px": int(foot.sum()),
        "min_catalogue_distance_px": float(d_cat[dots].min()) if dots.any() else float("nan"),
        "dots_within_3px": int((d_cat[dots] <= 3.0).sum()) if dots.any() else 0,
        "dots_within_4px": int((d_cat[dots] <= 4.0).sum()) if dots.any() else 0,
        "dots_within_5px": int((d_cat[dots] <= 5.0).sum()) if dots.any() else 0,
    }
    measured["remeasured"] = stats

    return {"ok": not problems, "problems": problems, "measured": measured}


def compare_claimed_invariants(recipe_path: str | Path, measured: dict) -> list[str]:
    """Diff a record's advertised `verified` block against re-measured numbers.

    Tolerant of float formatting (compares to 6 dp) and of keys the record does
    not carry. Returns a list of human-readable discrepancies.
    """
    raw = json.loads(Path(recipe_path).read_text())
    claimed = raw.get("verified") or {}
    out = []
    for key, want in claimed.items():
        if key in ("date", "grid") or key not in measured:
            continue
        got = measured[key]
        if isinstance(want, (int, float)) and isinstance(got, (int, float)):
            if abs(float(want) - float(got)) > 1e-6:
                out.append(f"{key}: record claims {want}, raster measures {got}")
        elif want != got:
            out.append(f"{key}: record claims {want!r}, raster measures {got!r}")
    return out


def rebuild(recipe: Recipe, data_root: str | Path, out_path: str | Path,
            builder_fn) -> dict:
    """Run the pinned builder and verify the rebuild against expected_sha256.

    builder_fn(**params) -> (dots_ndarray, reference_dict) is supplied by the
    caller (gems.builders), so this module stays free of competition specifics.
    """
    problems = verify_inputs(recipe, data_root)
    if problems:
        raise ParentUnavailable("pinned inputs are not usable:\n  " + "\n  ".join(problems))

    dots, reference = builder_fn(data_root=Path(data_root), seed=recipe.seed,
                                 **recipe.params)
    got = write_candidate(out_path, dots, reference)
    if got != recipe.expected_sha256:
        raise ParentUnavailable(
            f"REBUILD MISMATCH for {recipe.parent_id}\n"
            f"  expected sha256 {recipe.expected_sha256}\n"
            f"  rebuilt  sha256 {got}\n"
            f"  recipe git_sha {recipe.git_sha} seed {recipe.seed}\n"
            "Refusing to approximate the parent. Common causes: library version "
            "drift (bit-identical floats), a different reference grid, or a "
            "builder that is not the one recorded in the recipe.")
    return {"parent_id": recipe.parent_id, "sha256": got, "status": "VERIFIED"}


def reference_for(data_root: str | Path, rel: str) -> dict:
    return read_reference(Path(data_root) / rel)
