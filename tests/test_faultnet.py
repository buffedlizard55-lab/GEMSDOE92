"""FAULTNET lane: self-exclusion exactness (the leakage guard), endpoints, uniqueness helpers,
and receipt consistency between the run card, the served TIFF and the site block."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

from gems import faultnet as fn  # noqa: E402


def _toy():
    m = np.zeros((160, 170), bool)
    m[40, 10:70] = True
    m[50:110, 90] = True
    m[130, 120:165] = True
    m[20:30, 20] = True
    lab, n = ndi.label(m, fn.STRUCT8)
    return m, lab, n


@pytest.mark.parametrize("sigma", [3.0, 10.0])
def test_own_gaussian_sum_equals_deleting_the_component(sigma):
    m, lab, n = _toy()
    full = fn.gaussian_density(m, sigma)
    own = fn.own_gaussian_sum(lab, sigma)
    for k in range(1, n + 1):
        on = lab == k
        ref = fn.gaussian_density(m & ~on, sigma)
        np.testing.assert_allclose((full - own)[on], ref[on], atol=1e-5)
    assert np.all(own[~m] == 0)


def test_self_excluded_distance_exact_and_unchanged_off_catalogue():
    m, lab, n = _toy()
    d = fn.self_excluded_distance(m, lab)
    for k in range(1, n + 1):
        on = lab == k
        ref = np.minimum(ndi.distance_transform_edt(~(m & ~on)), fn.CAP_PX)
        np.testing.assert_allclose(d[on], ref[on])
    np.testing.assert_allclose(d[~m], np.minimum(ndi.distance_transform_edt(~m), fn.CAP_PX)[~m])
    assert d[m].min() > 0  # a positive never sees itself (feature != label)


def test_endpoints_of_a_line_and_a_dot():
    m = np.zeros((10, 10), bool)
    m[2, 2:7] = True
    m[8, 8] = True
    ep = fn.endpoints(m)
    assert set(zip(*np.nonzero(ep))) == {(2, 2), (2, 6), (8, 8)}


def test_context_fields_never_reveal_label_on_positives():
    m, lab, n = _toy()
    de = np.add.outer(np.arange(m.shape[0]), np.zeros(m.shape[1])).astype(np.float32)
    F = fn.context_fields(m, de, np.ones_like(m))
    assert set(F) == set(fn.CONTEXT_NAMES)
    assert all(v.dtype == np.float32 and np.isfinite(v).all() for v in F.values())
    assert F["cx_logdist"][m].min() > 0


def test_uniqueness_overlap_helper_matches_bruteforce():
    import faultnet_uniqueness as U
    rng = np.random.default_rng(0)
    a = np.zeros((60, 70), bool)
    a.ravel()[rng.choice(a.size, 80, replace=False)] = True
    b = np.zeros_like(a)
    b.ravel()[rng.choice(b.size, 120, replace=False)] = True
    got = U.overlap(U.neighbours(a), np.flatnonzero(b), a.size)
    dist = ndi.distance_transform_edt(~b)
    assert got == pytest.approx(float((dist[a] <= 3.0).mean()))


CARD = ROOT / "evidence" / "faultnet_run_card.json"


@pytest.mark.skipif(not CARD.is_file(), reason="run card not generated")
def test_run_card_matches_served_files_and_decision_rule():
    card = json.loads(CARD.read_text())
    assert card["weekly_slots_used"] == 0 and card["experiments_used"] <= 3
    assert card["leakage_canary"]["max_symmetric_auc"] <= 0.90
    n_ok = 0
    for arm, a in card["arms"].items():
        tif = ROOT / a["file"]
        assert hashlib.sha256(tif.read_bytes()).hexdigest() == a["sha256"]
        assert len(a["note"]) <= 140 and len(a["submission_name"]) <= 140
        assert a["validator"]["all_checks_passed"] and a["validator"]["gates_ok"]
        h = a["holdout_dti"]
        assert h["evidence_class"] == "HOLDOUT-DTI" and h["withheld_positives"] > 0
        beats = all(h["dti"] > v["control_dti"] and v["ci95"][0] > 0 for v in h["paired_vs_required_controls"].values())
        eligible = beats and a["uniqueness"]["unique_operative"]
        assert a["ok_to_submit"] == (a["verdict"] == "promote")
        if a["ok_to_submit"]:
            assert eligible
            n_ok += 1
    assert n_ok <= 1


@pytest.mark.skipif(not CARD.is_file(), reason="run card not generated")
def test_faultnet_lane_is_explicitly_negative_while_site_status_remains_authoritative():
    cur = json.loads((ROOT / "docs" / "downloads" / "current_submission.json").read_text())
    readme = (ROOT / "README.md").read_text()
    index = (ROOT / "docs" / "index.html").read_text()
    assert cur["verdict"] == "negative" and cur["ok_to_submit"] is False
    assert cur["uniqueness"]["unique_operative"] is False
    assert (ROOT / cur["file"]).is_file() and (ROOT / cur["zip"]).is_file()

    # README carries the active Arena review first; integrated main-branch
    # current-status snapshots remain historical and cannot supersede it.
    readme_status = readme.split("### Starting point for every session", 1)[0]
    assert "Current verified decision" in readme_status
    assert "OK TO DOWNLOAD FOR RESEARCH" in readme_status and "DO NOT SUBMIT" in readme_status
    assert "REVIEW_20261025_ARENA.md" in readme_status
    assert "CURRENT-READINESS:BEGIN" in index
    site_status = index.split("<!-- CURRENT-READINESS:BEGIN -->", 1)[1].split("<!-- CURRENT-READINESS:END -->", 1)[0]
    assert "OK TO DOWNLOAD FOR RESEARCH" in site_status and "DO NOT SUBMIT" in site_status

    # The lane-specific receipt remains visible as a negative research result,
    # not as a second current submission authorization.
    faultnet = index.split("<!-- CURRENT:BEGIN -->", 1)[1].split("<!-- CURRENT:END -->", 1)[0]
    assert cur["sha256"] in faultnet
    assert "DO NOT SUBMIT" in faultnet
    assert "0.7586" in faultnet
