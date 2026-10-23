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

from .rasters import read_reference, sha256_file, write_candidate


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

    @classmethod
    def load(cls, path: str | Path) -> "Recipe":
        p = Path(path)
        if not p.exists():
            raise ParentUnavailable(f"recipe not found: {p} -- cannot rebuild the parent")
        raw = json.loads(p.read_text())
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
        f = root / rel
        if not f.exists():
            problems.append(f"MISSING input {rel} (expected sha256 {want[:12]}...)")
            continue
        got = sha256_file(f)
        if got != want:
            problems.append(f"HASH MISMATCH {rel}: expected {want} got {got}")
    return problems


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
