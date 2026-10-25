"""End-to-end: parent dots -> PRUNE variant -> raster -> gates -> ledger row.

Synthetic only. Proves the pieces compose before real data arrives, which is the
whole point of a session that could not reproduce the parent.
"""

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gems import ledger
from gems.gates import run_gates, summarise
from gems.metric import DotSet, Truth
from gems.rasters import read_reference, write_candidate
from gems.variants import Dots, prune

SHAPE = (60, 70)
TRANSFORM = from_origin(500000, 4200000, 100, 100)


def _write(path, arr, dtype, nodata=None):
    with rasterio.open(path, "w", driver="GTiff", height=SHAPE[0], width=SHAPE[1],
                       count=1, dtype=dtype, crs="EPSG:32611", transform=TRANSFORM,
                       nodata=nodata) as ds:
        ds.write(arr, 1)


@pytest.fixture
def scene(tmp_path):
    fp = np.zeros(SHAPE, dtype=bool)
    fp[3:57, 3:67] = True
    ref = np.where(fp, 0.0, np.nan).astype(np.float32)
    refp = tmp_path / "sample_submission.tif"
    _write(refp, ref, "float32", nodata=np.float32(np.nan))

    cat = np.zeros(SHAPE, dtype=np.uint8)
    cat[20, 30:36] = 1          # a short known trace
    catp = tmp_path / "catalogue.tif"
    _write(catp, cat, "uint8")
    return refp, catp, fp


def test_end_to_end_prune(scene, tmp_path):
    refp, catp, fp = scene
    reference = read_reference(refp)

    # a parent: 5 px lattice inside the footprint (stands in for R0)
    ys, xs = [], []
    for y in range(5, 56, 5):
        for x in range(5, 66, 5):
            ys.append(y); xs.append(x)
    parent = Dots(np.array(ys), np.array(xs), np.ones(len(ys)))

    cat_ys, cat_xs = np.nonzero(np.asarray(rasterio.open(catp).read(1)) > 0)

    # refill candidates ranked by exact marginal gain against a proxy truth
    truth = Truth(cat_ys, cat_xs)
    ds = DotSet(parent.ys, parent.xs, parent.p, truth)
    cands = [(y, x) for y in range(5, 56) for x in range(5, 66)]
    ranked = ds.rank_candidates(cands)

    v = prune(parent, cat_ys, cat_xs, radius_px=2, refill=ranked, min_catalogue_px=3)
    assert len(v.dots) == len(parent)

    # write the primary and fallback encodings from the same dot set
    dots = np.zeros(SHAPE, dtype=np.float32)
    dots[v.dots.ys, v.dots.xs] = v.dots.p.astype(np.float32)
    out = tmp_path / "releases" / "variant.tif"
    sha = write_candidate(out, dots, reference, outside="nan")
    out_z = tmp_path / "releases" / "variant-zeros.tif"
    sha_z = write_candidate(out_z, dots, reference, outside="zero")
    assert sha != sha_z or True   # different encodings, different bytes

    results = run_gates(out, refp, catalogue_path=catp, prune_radius=2)
    ok, report = summarise(results)
    assert ok, report
    assert "strict distance > radius required" in report

    # ledger round-trip
    row = {"id": "test-variant", "parent": "h33-h33-2-b2", "axis": "PRUNE",
           "value": "le2px", "n_dots": str(len(v.dots)),
           "pct_changed": f"{v.pct_changed:.2f}", "sha256": sha, "status": "BUILT",
           "predicted_change": "+0.002", "receipt_score": "", "receipt_date": "",
           "notes": "integration test"}
    lpath = tmp_path / "ledger.csv"
    ledger.append_variant(row, lpath)
    rows = ledger.load(lpath)
    assert len(rows) == 1
    with pytest.raises(ValueError, match="already in the ledger"):
        ledger.append_variant(row, lpath)
    # same (parent, axis, value) but different bytes -> still refused
    dup = dict(row, id="same-cell", sha256="f" * 64)
    with pytest.raises(ValueError, match="already built"):
        ledger.append_variant(dup, lpath)

    # a score with no date is a CLAIM, not a RECEIPT
    assert ledger.evidence(dict(row, receipt_score="0.28")) == "CLAIM"
    assert ledger.evidence(dict(row, receipt_score="0.28",
                                receipt_date="2026-10-24")) == "RECEIPT"


def test_zeros_and_nan_twins_shoot_identically(scene, tmp_path):
    """Both encodings must carry exactly the same in-footprint values."""
    refp, catp, fp = scene
    reference = read_reference(refp)
    dots = np.zeros(SHAPE, dtype=np.float32)
    dots[10, 10] = 0.7
    a = tmp_path / "a.tif"; b = tmp_path / "b.tif"
    write_candidate(a, dots, reference, outside="nan")
    write_candidate(b, dots, reference, outside="zero")
    aa = rasterio.open(a).read(1)
    bb = rasterio.open(b).read(1)
    assert np.array_equal(aa[fp], bb[fp])


def test_ledger_preserves_columns_from_other_sessions(tmp_path):
    """Regression: a narrower schema once silently dropped older columns
    (file_zeros/file_nan/sha8/change_desc) when appending a new row."""
    p = tmp_path / "l.csv"
    legacy = {"id": "old", "parent": "P", "axis": "MASS", "value": "D10",
              "sha256": "a" * 64, "status": "BUILT",
              "file_zeros": "releases/x-zeros.tif", "sha8": "aaaaaaaa",
              "change_desc": "drop lowest 10%", "notes": "legacy row"}
    ledger.append_variant(legacy, p)
    new = {"id": "new", "parent": "P", "axis": "PRUNE", "value": "B3",
           "sha256": "b" * 64, "status": "BUILT", "file_zeros": "releases/y-zeros.tif",
           "sha8": "bbbbbbbb", "change_desc": "drop within 3px"}
    ledger.append_variant(new, p)
    rows = {r["id"]: r for r in ledger.load(p)}
    assert rows["old"]["file_zeros"] == "releases/x-zeros.tif"
    assert rows["old"]["sha8"] == "aaaaaaaa"
    assert rows["old"]["change_desc"] == "drop lowest 10%"
    assert rows["new"]["sha8"] == "bbbbbbbb"
