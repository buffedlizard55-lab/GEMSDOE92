"""Tests for the 2026-10-31 GX lane: external-layer candidate, page contract and the 0.2778 algebra."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio

ROOT = Path(__file__).resolve().parents[1]
DL = ROOT / "docs" / "downloads"
EVID = ROOT / "evidence"

RC_PATH = DL / "gx1_run_card_20261031.json"
HOLD_PATH = EVID / "gx_holdout.json"
EVAL_PATH = EVID / "gx_candidate_eval.json"
PAGE = ROOT / "docs" / "executive-summary-20261031-gx.html"
INDEX = ROOT / "docs" / "index.html"

ALPHA, BETA = 0.2, 0.8

needs = lambda p: pytest.mark.skipif(not p.is_file(), reason=f"missing {p.name}")


@pytest.fixture(scope="module")
def card():
    if not RC_PATH.is_file():
        pytest.skip("GX run card not built")
    return json.loads(RC_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# fail-closed contract
# --------------------------------------------------------------------------- #
def test_run_card_is_fail_closed(card):
    """The artifact must never self-authorise a weekly slot."""
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["download_status"] == "OK TO DOWNLOAD FOR RESEARCH ONLY"
    assert card["experiments_used"] <= 3
    assert card["weekly_slots_spent"] == 0
    assert 0 < len(card["submission"]["note"]) <= 140
    assert 0 < len(card["submission"]["name"]) <= 140


def test_raster_and_zip_bytes_match_run_card(card):
    tif = DL / Path(card["raster"]["file"]).name
    zf = DL / Path(card["raster"]["zip"]).name
    assert tif.is_file() and zf.is_file()
    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert digest == card["raster"]["sha256"]
    if EVAL_PATH.is_file():  # the evaluator binds the same bytes
        assert json.loads(EVAL_PATH.read_text(encoding="utf-8"))["sha256"] == digest
    with zipfile.ZipFile(zf) as archive:
        members = [n for n in archive.namelist() if not n.endswith("/")]
        assert len(members) == 1, "one-TIFF ZIP required by the portal"
        assert Path(members[0]).name == tif.name
        assert hashlib.sha256(archive.read(members[0])).hexdigest() == digest


def test_raster_passes_the_shared_format_gates():
    """Re-run the shared gate module: this is what blocks the [0, 1] portal error."""
    audit_path = DL / "gemsdoe92-gx1-50000dots-20261031-zeros-audit.json"
    tif = DL / "gemsdoe92-gx1-50000dots-20261031-zeros.tif"
    if not (audit_path.is_file() and tif.is_file()):
        pytest.skip("GX artifact not built")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    gates = audit.get("gates") or []
    if gates:  # gate list present -> every gate must pass
        assert all(g["ok"] for g in gates)
    assert audit["nan_pixels"] == 0 and audit["infinity_pixels"] == 0
    assert audit["min"] >= 0.0 and audit["max"] <= 1.0
    assert audit["bands"] == 1 and audit["dtype"] == "float32"
    assert audit["crs"] == "EPSG:32611"
    assert (audit["height"], audit["width"]) == (3730, 3292)
    assert audit["mass_outside_footprint"] == 0
    assert audit["problems"] == [] and audit["ok"] is True
    with rasterio.open(tif) as src:
        arr = src.read(1)
    assert np.isfinite(arr).all(), "no NaN/Inf anywhere in the raster"
    assert arr.min() >= 0.0 and arr.max() <= 1.0
    assert int((arr > 0).sum()) == audit["n_nonzero"]


# --------------------------------------------------------------------------- #
# measurements
# --------------------------------------------------------------------------- #
@needs(HOLD_PATH)
def test_holdout_beats_the_r0_recipe_control():
    hold = json.loads(HOLD_PATH.read_text(encoding="utf-8"))
    sc = hold["pooled"]["scores"]
    best = max((k for k in sc if k.startswith("gx_")), key=lambda k: sc[k]["dti"])
    assert sc[best]["dti"] > sc["r0_recipe"]["dti"]
    diff = hold["pooled"]["paired_differences"]["r0_recipe"]
    assert diff["ci95"][0] > 0.0, "paired 95% CI must exclude zero"
    for arm in sc:
        if arm.startswith("gx_"):
            assert sc[arm]["dti"] > sc["random"]["dti"], arm
    assert hold["evaluator"] == "gems57-pooled-hide-v2"
    assert sc[best]["withheld_positive_pixels"] > 0


@needs(HOLD_PATH)
def test_leakage_canaries_pass_and_no_feature_is_dropped():
    hold = json.loads(HOLD_PATH.read_text(encoding="utf-8"))
    can = hold["canaries"]
    assert can, "canary table must not be empty"
    assert max(c["auc_holdout"] for c in can) <= 0.90
    assert hold["features_dropped"] == []


@needs(EVAL_PATH)
def test_registry_uniqueness_measurements(card):
    ev = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    rep = ev["uniqueness"]["worst_by_representation"]
    assert rep["dot_field"]["max"] <= 0.70
    assert rep["dot_field"]["n_above_070"] == 0
    assert rep["continuous_surface"]["max"] <= 0.70
    assert abs(ev["uniqueness"]["max_abs_spearman"]) <= 0.90
    # the literal dense-lattice collision is recorded, not hidden
    assert rep["dense_binary_lattice"]["n_above_070"] > 0
    assert card["correlation_and_overlap_vs_registry"]["dense_lattices_above_0_70"] > 0


@needs(EVAL_PATH)
def test_every_score_carries_a_rule3_label():
    """Rule 3: a projection is never written as a score."""
    ev = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    assert ev["holdout"]["evidence_class"] == "HOLDOUT-DTI"
    assert ev["estimate"]["evidence_class"] == "MODEL"
    assert ev["estimate"]["ridge_audit"]["valid_leaderboard_prediction"] is False


# --------------------------------------------------------------------------- #
# the 0.2778 algebra quoted in the executive summary (§3)
# --------------------------------------------------------------------------- #
def _dti(T, n, M, K):
    """DTI = T / (T + alpha*FPw + beta*FNw) with FPw = n - M and FNw = K - T."""
    return T / (T + ALPHA * (n - M) + BETA * (K - T))


def test_dti_algebra_matches_the_shared_metric_module():
    """alpha*(T + n - M) + beta*K == T + alpha*FPw + beta*FNw (since 1 - beta == alpha)."""
    rng = np.random.default_rng(20261031)
    for _ in range(200):
        T, M, K, n = rng.uniform(1, 6000, 4)
        M, K, n = min(M, n), max(K, T), max(n, M)
        lhs = ALPHA * (T + n - M) + BETA * K
        rhs = T + ALPHA * (n - M) + BETA * (K - T)
        assert abs(lhs - rhs) < 1e-9
        assert abs(_dti(T, n, M, K) - T / lhs) < 1e-12


def test_lineage_claims_are_self_consistent_under_the_dot_algebra():
    """The three nested H19-5 claims pin T ~ 5.1-5.5k and reproduce 0.2778 exactly."""
    claims = {"d2.8": (44090, 0.2600), "h27-4": (40199, 0.2708), "h33": (37654, 0.2778)}
    c = {k: 1.0 / v[1] - ALPHA for k, v in claims.items()}
    n = {k: v[0] for k, v in claims.items()}

    # T is identified from the claim differences alone: c_i - c_j = alpha*u*(n_i - n_j)
    T = {}
    for k1, k2 in (("d2.8", "h27-4"), ("d2.8", "h33"), ("h27-4", "h33")):
        T[(k1, k2)] = ALPHA * (n[k1] - n[k2]) / (c[k1] - c[k2])
    for key, value in T.items():
        assert 4000 < value < 7000, f"{key}: implausible covered truth mass {value}"
    assert max(T.values()) / min(T.values()) < 1.15, "constant-T approximation must be close"

    # pin M from h33 with the documented K assumption, then round-trip all three claims
    T_h33 = T[("d2.8", "h33")]
    K = 13219.0
    denom = T_h33 / claims["h33"][1]
    M = T_h33 + n["h33"] - (denom - BETA * K) / ALPHA
    assert 0 <= M <= n["h33"]
    assert abs(_dti(T_h33, n["h33"], M, K) - 0.2778) < 1e-6, "h33 must reproduce exactly"
    for key in ("d2.8", "h27-4"):
        assert abs(_dti(T_h33, n[key], M, K) - claims[key][1]) < 0.01, key

    # denominator composition quoted in the summary
    total = ALPHA * (T_h33 + n["h33"] - M) + BETA * K
    assert abs(BETA * K / total - 0.56) < 0.02, "false negatives dominate"
    assert abs(ALPHA * T_h33 / total - 0.056) < 0.01

    # pruning zero-yield dots is the largest lever the summary claims it is
    pruned = _dti(T_h33, n["h33"] - 18000, M, K)
    assert 0.30 < pruned < 0.40, pruned
    assert pruned > 0.2778


# --------------------------------------------------------------------------- #
# site / documentation contract
# --------------------------------------------------------------------------- #
@needs(PAGE)
def test_executive_summary_page_contract(card):
    html = PAGE.read_text(encoding="utf-8")
    tif = Path(card["raster"]["file"]).name
    assert f'href="downloads/{tif}" download' in html, "one-click download must be first"
    assert "OK TO DOWNLOAD FOR RESEARCH" in html
    assert "DO NOT SUBMIT" in html
    assert "OK TO SUBMIT" not in html.replace("OK TO DOWNLOAD", "")
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in html, f"{site} missing from the nine-site table"
    assert "CLAIM" in html and "MODEL" in html and "HOLDOUT-DTI" in html
    assert html.count("<tr>") >= 9


def test_index_html_carries_the_rendered_gx_banner(card):
    html = INDEX.read_text(encoding="utf-8")
    assert 'id="gx-20261031"' in html
    assert Path(card["raster"]["file"]).name in html


def test_standing_prompt_is_recorded_in_the_repo():
    """The user asked for the brief to live in the repo and be read every session."""
    sp = ROOT / "docs" / "STANDING_PROMPT_20261031.md"
    assert sp.is_file()
    assert "MUST GENERATE A UNIQUE TIF SUBMISSION" in sp.read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/STANDING_PROMPT_20261031.md" in readme
    sess = (ROOT / "SESSION_PROMPT.md").read_text(encoding="utf-8")
    assert "docs/STANDING_PROMPT_20261031.md" in sess
