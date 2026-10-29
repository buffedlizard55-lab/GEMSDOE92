"""Automated regression & byte-binding tests for the 2026-10-29 ADMITRELAY + LBM-v3 session."""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np

from gems import lbmodel as M

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DL = DOCS / "downloads"
EVID = ROOT / "evidence"

CAND_STEM = "gemsdoe92-admitrelay1-37654dots-20261029-b8051a75"
CAND_SHA256 = "b8051a75da299099fb7b43aed18c06aeefa8291d78b523e3083f9620a5527214"


def test_monotone_factor_design_enforces_nonincreasing_flanks():
    levels = {"dcat": ["0", "1", "2"], "dh19": ["0", "1", "2", "3", "4", "5"], "cons": ["0", "1", "2", "3", "4"]}
    X, bounds = M.monotone_factor_design(levels, nonincreasing_factors=(1,))
    assert X.shape == (90, 1 + 2 + 5 + 4)
    # Any feasible parameter vector satisfying `bounds` must yield non-increasing rho along dh19
    beta = np.array([-6.5, -0.4, 1.2, -0.05, -0.20, -0.15, -0.30, -0.50, -0.2, 0.0, 0.3, 1.8])
    for val, (lo, hi) in zip(beta, bounds):
        assert (lo is None or val >= lo) and (hi is None or val <= hi)
    rho = np.exp(X @ beta).reshape(3, 6, 5)
    diffs = np.diff(rho, axis=1)
    assert np.all(diffs <= 1e-12), f"dh19 monotonicity violated: max diff={diffs.max()}"


def test_lbm_v3_prospective_oot_and_monotone_table():
    doc = json.loads((EVID / "lbm_v3_20261029.json").read_text(encoding="utf-8"))
    assert doc["n_clean_claims"] == 131
    assert doc["logo_cv"]["rmse_all"] < 0.030
    assert doc["logo_cv"]["spearman_all"] > 0.95

    oot = doc["prospective_oot_20261029"]
    assert oot["trained_on_n_claims"] == 127
    assert oot["tested_on_n_unseen_20261029_claims"] == 4
    assert oot["lbm_v3_oot_rmse"] < 0.015
    assert oot["lbm_v3_oot_rmse"] < oot["lbm_v1_oot_rmse"]
    assert oot["lbmc1_goodhart_error_reduction_factor"] > 10.0

    by_site = {r["site"]: r for r in oot["rows"]}
    assert by_site["GEMSDOE92"]["claim"] == 0.2784
    assert abs(by_site["GEMSDOE92"]["lbm_v3_prospective_oot"] - 0.2784) < 0.005

    rho_3d = np.array(doc["rho_table"], dtype=float).reshape(3, 6, 5)
    assert np.all(np.diff(rho_3d, axis=1) <= 1e-10)


def test_admitrelay_canaries_and_holdout_receipts():
    can = json.loads((EVID / "admitrelay_canaries_20261029.json").read_text(encoding="utf-8"))
    assert can["leakage_flag"] is False
    assert can["all_pass_le_0p90"] is True
    assert len(can["features"]) == 20
    assert can["zero_catalogue_12_max_sym_auc"] <= 0.90
    assert can["all_20_max_sym_auc"] <= 0.90
    assert all(f["symmetric_auc"] <= 0.90 for f in can["features"])

    hold = json.loads((EVID / "admitrelay_holdout_20261029.json").read_text(encoding="utf-8"))
    assert hold["experiments_executed"] == 3
    sc = hold["summary_e3_candidate"]["scores"]
    assert sc["e1_admitrelay_blind"]["dti"] > 0.080
    assert sc["e2_admitrelay_ps_loqo"]["dti"] > sc["r0_recipe"]["dti"]
    assert sc["e3_admitrelay_lbmv3_unique"]["dti"] > 2.0 * 0.037987


def test_admitrelay_artifacts_byte_bound_and_fail_closed():
    tif = DL / f"{CAND_STEM}-zeros.tif"
    zf = DL / f"{CAND_STEM}-zeros.zip"
    audit_p = DL / f"{CAND_STEM}-zeros-audit.json"
    dl_card_p = DL / f"{CAND_STEM}_run_card.json"
    ev_card_p = EVID / f"{CAND_STEM}_run_card.json"
    alias_card_p = EVID / "admitrelay_run_card_20261029.json"
    feed_p = DL / "admitrelay_readiness_20261029.json"
    exec_p = DOCS / "executive-summary-20261029-admitrelay.html"

    for p in (tif, zf, audit_p, dl_card_p, ev_card_p, alias_card_p, feed_p, exec_p):
        assert p.is_file(), f"missing artifact: {p}"

    digest = hashlib.sha256(tif.read_bytes()).hexdigest()
    assert digest == CAND_SHA256
    assert dl_card_p.read_bytes() == ev_card_p.read_bytes() == alias_card_p.read_bytes()

    with zipfile.ZipFile(zf) as archive:
        members = [m for m in archive.namelist() if not m.endswith("/")]
        assert len(members) == 1 and Path(members[0]).name == tif.name
        assert hashlib.sha256(archive.read(members[0])).hexdigest() == digest

    card = json.loads(dl_card_p.read_text(encoding="utf-8"))
    audit = json.loads(audit_p.read_text(encoding="utf-8"))
    feed = json.loads(feed_p.read_text(encoding="utf-8"))

    for key in (
        "hypothesis",
        "mechanism",
        "named_non_fault_mimic",
        "holdout_dti",
        "correlation_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "note",
        "verdict",
    ):
        assert key in card, f"missing protocol run-card key: {key}"

    assert card["raster_sha256"] == audit["sha256_zeros"] == feed["raster_sha256"] == digest
    assert 0 < len(card["note"]) <= 140
    assert card["verdict"] == audit["verdict"] == feed["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert audit["submission_eligible"] is False
    assert feed["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0

    u = card["uniqueness"]
    assert u["registry_rasters"] >= 2260
    assert u["surface_pi1_pass"] is True and u["surface_worst_overlap"] <= 0.70 and u["surface_worst_abs_rho"] <= 0.90
    assert u["final_pi1_pass"] is True and u["final_worst_overlap"] <= 0.70 and u["final_worst_abs_rho"] <= 0.90
    assert u["literal_reading"]["duplicate_under_literal"] is True and u["literal_reading"]["worst"] == 1.0

    summary_html = exec_p.read_text(encoding="utf-8")
    assert "DO NOT SUBMIT" in summary_html
    assert "OK TO DOWNLOAD FOR RESEARCH ONLY" in summary_html
    assert "OK TO SUBMIT" not in summary_html
    assert summary_html.count("</main>") == 1
    ids = re.findall(r'\bid="([^"]+)"', summary_html)
    assert len(ids) == len(set(ids))


def test_no_git_conflict_markers_in_tracked_text_or_html():
    marker_re = re.compile(r"^(<<<<<<<|=======|>>>>>>>)(\s|$)", re.MULTILINE)
    exts = {".py", ".md", ".json", ".html", ".txt"}
    skip_dirs = {".git", ".venv", ".cache", "__pycache__", ".pytest_cache", "node_modules"}
    bad = []
    for p in ROOT.rglob("*"):
        if any(part in skip_dirs for part in p.parts):
            continue
        if p.is_file() and p.suffix in exts:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if marker_re.search(txt):
                bad.append(str(p.relative_to(ROOT)))
    assert not bad, f"Git merge-conflict markers found in: {bad}"
