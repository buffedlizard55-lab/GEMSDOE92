"""Regression guard for evidence/nine_site_byte_check_20261030.json.

The evidence was produced by scripts/nine_site_byte_check.py from the exact owner
files (see that script's docstring). These tests pin the measured values so an
edit cannot silently change the uniqueness picture shown to reviewers.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "nine_site_byte_check_20261030.json"

EXPECTED_SHA = {
    "24": "68d0e2e4fcc594f9a23f56c44b885fee733d026d39be55e18ad2a07289525310",
    "25": "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8",
    "27": "33003374335d84bf885f2d8f5e9dd4c57044c8ec58fa6a0d7fa581e8bc41c11d",
    "28": "5556aa1438fd67376b60d5ffc99228ec09dcc11a8408298a743ccb88d6163641",
    "30": "8cf893ead5667df21d3288a9968c35fd5385c425b029d82ee71d311715b129fd",
    "31": "07b6db440535404bb41ec8ddc797713e200d308e3da35937393efde5eb84bc40",
    "32": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
    "33": "87f857d505e23247e991ccfab2cbe9f49a04df4f9c8028dce7ea261554690757",
    "36": "e15891020b9c57056ac7fa874a5e506fbd6ed9314a4ea8e73af0753887a3708a",
}
EXPECTED_DOTS = {"24": 60069, "25": 44090, "27": 61328, "28": 37660, "30": 44090,
                 "31": 40199, "32": 37654, "33": 41865, "36": 38854}


@pytest.fixture(scope="module")
def ev():
    return json.loads(EVIDENCE.read_text())


def test_nine_files_are_pinned_by_sha(ev):
    assert set(ev["files"]) == set(EXPECTED_SHA)
    for s, sha in EXPECTED_SHA.items():
        assert ev["files"][s]["sha256"] == sha, s


def test_dot_counts_and_grid(ev):
    for s, n in EXPECTED_DOTS.items():
        f = ev["files"][s]
        assert f["n_dots"] == n, s
        assert f["crs"] == "EPSG:32611" and f["shape"] == [3730, 3292], s
        assert f["n_out_of_0_1"] == 0, s


def test_only_exact_duplicate_is_25_30(ev):
    # identical in-footprint dot sets; they differ only in outside-footprint encoding
    assert ev["exact_identical_dot_sets"] == [["25", "30"]]
    assert ev["files"]["25"]["n_nan"] == 7111787 and ev["files"]["30"]["n_nan"] == 0


def test_no_pair_passes_the_70pct_3px_rule(ev):
    # the internal literal rule: >70% of A's dots within 3 px of B's dots => duplicate
    for k, v in ev["pairwise_A_fraction_within_3px_of_B"].items():
        assert v > 0.70, k


def test_random_baseline_is_far_below_the_claimed_family(ev):
    base = ev["random_baseline_within_3px_of_GEMSDOE32"]["mean"]
    assert base < 0.20
    assert min(ev["min_over_others_per_site"].values()) > 0.85
