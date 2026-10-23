import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import metric  # noqa: E402
from gems92 import core  # noqa: E402


def test_dti_exact_matches_bruteforce():
    rng = np.random.default_rng(7)
    truth = np.zeros((12, 12), dtype=bool)
    truth[5, 3:9] = True
    pred = np.zeros((12, 12))
    pred[5, 4] = 1.0
    pred[4, 6] = 1.0
    pred[9, 9] = 1.0
    exact = metric.dti_exact(pred, truth)
    brute = metric.dti_bruteforce(pred, truth)
    assert abs(exact["dti"] - brute["dti"]) < 1e-10
    assert abs(exact["tp"] - brute["tp"]) < 1e-10


def test_dti_algebra_identity():
    # DTI = T / (0.2T + 0.2(S-M) + 0.8|G|) from the components of max_cover
    rng = np.random.default_rng(3)
    truth = rng.random((15, 15)) < 0.08
    pred = (rng.random((15, 15)) < 0.06).astype(np.float64)
    covers, k_max, _ = metric.max_cover(np.where(truth, 0.0, pred) * 0 + pred, truth)
    # recompute directly with dti_exact components
    res = metric.dti_exact(pred, truth)
    s_sum = float(pred.sum())
    yy, xx = np.nonzero(pred > 0)
    # M = sum over dots of max kernel to truth (via distance-based kernel)
    from scipy.ndimage import distance_transform_edt
    dg = distance_transform_edt(~truth)
    m_val = float(metric.kernel(dg[pred > 0]).sum() * 1.0) if (pred > 0).any() else 0.0
    # kernel at a dot position uses pred value (=1) times k(dg); max_cover returns that per dot location grid
    _, kgrid, _ = metric.max_cover(pred, truth)
    m_val = float((pred * kgrid).sum())
    denom = 0.2 * res["tp"] + 0.2 * (s_sum - m_val) + 0.8 * float(truth.sum())
    assert abs(res["tp"] / denom - res["dti"]) < 1e-9


def test_build_traces_keeps_line_drops_isolated():
    mask = np.zeros((60, 60), dtype=bool)
    # straight strand: dots every 3 px along row 30, cols 5..50 (16 dots, span 45 px)
    mask[30, 5:51:3] = True
    # isolated speckles far away
    mask[5, 5] = True
    mask[5, 50] = True
    mask[55, 30] = True
    kept, traces = core.build_traces(mask, min_span_px=10.0)
    assert kept[30, 5]
    assert int(kept.sum()) == 16
    assert len(traces) == 1
    assert traces[0]["span_km"] >= 1.0


def test_walked_paths_follow_strand_not_zigzag():
    rows = np.full(16, 30)
    cols = np.arange(5, 51, 3)
    paths = core.walked_paths(rows, cols)
    assert len(paths) == 1
    p = paths[0]
    pts = np.column_stack([rows[p], cols[p]]).astype(float)
    seg = np.diff(pts, axis=0)
    poly = float(np.hypot(seg[:, 0], seg[:, 1]).sum())
    # a sane strand path is ~45 px, not hundreds from zigzag ordering
    assert 40.0 <= poly <= 50.0


def test_ledger_rows_and_notes():
    ledger = ROOT / "ledger" / "submissions.csv"
    rows = list(csv.DictReader(ledger.open(newline="")))
    trackb = [r for r in rows if r["axis"] == "TRACKB"]
    assert len(trackb) == 3
    hashes = [r["sha256"] for r in trackb] + [r["sha256_zeros"] for r in trackb]
    assert len(set(hashes)) == 6
    for r in trackb:
        assert r["parent"] == "h33-h33-2-b2"
        assert int(r["n_dots"]) == 37654
        assert 1.0 <= float(r["pct_changed"]) <= 50.0
        assert r["status"] == "BUILT"
        assert r["receipt_score"] == ""
        receipt = json.loads((ROOT / "releases" / f"{r['id']}.json").read_text())
        assert len(receipt["note"]) <= 140
        gj = json.loads((ROOT / "releases" / f"{r['id']}-traces.geojson").read_text())
        assert gj["features"], r["id"]
        for feat in gj["features"][:5]:
            assert feat["properties"]["polyline_km"] >= 1.0
            assert len(feat["properties"]["evidence"]) > 100
