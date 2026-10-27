#!/usr/bin/env python3
"""Shared data loading for the leaderboard model (LBM) and the uniqueness gate.

Functions here only read pinned inputs from ``.cache/gems_inputs`` and the
registry cache in ``.cache/registry_v3``.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems import registry_cache as rc  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
SAMPLE = INPUTS / "bridge" / "sample_submission.tif"
CATALOGUE = INPUTS / "bridge" / "existing_faults.tif"
FEATURES = INPUTS / "training_features.tif"
R0 = INPUTS / "lineage" / "GEMSDOE32__h33-2-b2-zeros.tif"
H195 = INPUTS / "lineage" / "calib_h195_01922.tif"
D28 = INPUTS / "lineage" / "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
SHAPE = rc.SHAPE


@lru_cache(maxsize=1)
def footprint() -> rc.Footprint:
    return rc.load_footprint(SAMPLE)


@lru_cache(maxsize=1)
def catalogue() -> np.ndarray:
    with rasterio.open(CATALOGUE) as ds:
        return ds.read(1) == 1


def read01(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0)


def full_from_summary(sha256: str) -> tuple[np.ndarray, dict]:
    """Rebuild a full-grid float32 raster (zeros outside the footprint)."""
    meta, arr = rc.load_summary(sha256)
    fp = footprint()
    out = np.zeros(SHAPE[0] * SHAPE[1], np.float32)
    out[fp.lin[arr["top"]]] = arr["topv"]
    return out.reshape(SHAPE), meta["meta"]


def support_lin(sha256: str) -> tuple[np.ndarray, np.ndarray, dict]:
    """Footprint-linear positive indices (value-ordered) and values."""
    meta, arr = rc.load_summary(sha256)
    return arr["top"], arr["topv"], meta["meta"]


def load_claims_matched() -> list[dict]:
    d = json.loads((ROOT / "evidence" / "claims_matched_20261027.json").read_text(encoding="utf-8"))
    return d["rows"]


def inventory_records() -> list[dict]:
    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    return [dict(f, pushed_at=r.get("pushed_at")) for r in inv["repositories"] for f in r["files"]]


def edt_to(mask: np.ndarray) -> np.ndarray:
    return ndi.distance_transform_edt(~mask).astype(np.float32)
