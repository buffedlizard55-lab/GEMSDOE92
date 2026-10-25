"""Unit and audit regression tests for the TILTANGLE lane and its 2026-10-25 leakage/uniqueness audit."""
from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from gems import tiltangle as ta

ROOT = Path(__file__).resolve().parents[1]


def test_tiltangle_surface_takes_no_catalogue_and_obeys_miller_singh_geometry(tmp_path):
    sig = set(inspect.signature(ta.lane_surface).parameters)
    assert sig == {"stack_path", "footprint"}

    h, w = 24, 24
    stack = tmp_path / "synthetic_stack.tif"
    foot = np.ones((h, w), dtype=bool)
    with rasterio.open(
        stack,
        "w",
        driver="GTiff",
        height=h,
        width=w,
        count=19,
        dtype="float32",
        crs="EPSG:32611",
        transform=from_origin(243350.0, 4508550.0, 100.0, 100.0),
    ) as ds:
        for b in range(1, 20):
            ds.write(np.zeros((h, w), dtype=np.float32), b)
        # Band 11 (grav_vg): zero on top half (vertical contact inflection), 10 on bottom half
        vg = np.zeros((h, w), dtype=np.float32)
        vg[h // 2 :, :] = 10.0
        ds.write(vg, ta.BAND["grav_vg"])
        # Band 13 (grav_anom): constant so N-S derivative is 0
        ds.write(np.zeros((h, w), dtype=np.float32), ta.BAND["grav_anom"])
        # Band 18 (grav_hg_ew): 5.0 on top half (strong E-W gradient), 0.0 on bottom half
        hg_ew = np.zeros((h, w), dtype=np.float32)
        hg_ew[: h // 2, :] = 5.0
        ds.write(hg_ew, ta.BAND["grav_hg_ew"])

    out = ta.lane_surface(str(stack), foot)
    # Top half: vg == 0, hgm == 5 -> tilt == 0 deg, cos(tilt)^2 == 1 -> s_raw == 5
    np.testing.assert_allclose(out["tilt"][: h // 2 - 1, :], 0.0, atol=1e-5)
    np.testing.assert_allclose(out["s_raw"][: h // 2 - 1, :], 5.0, atol=1e-5)
    # Bottom half: vg == 10, hgm == 0 -> tilt == 90 deg, cos(tilt)^2 == 0 -> s_raw == 0
    np.testing.assert_allclose(out["tilt"][h // 2 + 1 :, :], 90.0, atol=1e-4)
    np.testing.assert_allclose(out["s_raw"][h // 2 + 1 :, :], 0.0, atol=1e-5)


def test_tiltangle_audit_and_run_card_disclose_dpref_leakage_and_duplicate_stop():
    audit_path = ROOT / "evidence" / "tiltangle_audit_20261025.json"
    rc_path = (
        ROOT
        / "docs"
        / "downloads"
        / "gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros_run_card.json"
    )
    sidecar_path = (
        ROOT
        / "docs"
        / "downloads"
        / "gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros.json"
    )
    tif_path = (
        ROOT
        / "docs"
        / "downloads"
        / "gemsdoe92-tiltangle-tiltangle-37654-20261025T182301Z-zeros.tif"
    )

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    rc = json.loads(rc_path.read_text(encoding="utf-8"))
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    tif_sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()

    assert audit["raster_sha256"] == tif_sha
    assert rc["raster_sha256"] == tif_sha
    assert sidecar["sha256"] == tif_sha

    for doc in (audit, rc, sidecar):
        assert doc["verdict"] == "negative"
        assert doc["submission_eligible"] is False

    # Leakage canary: pure surface passes (<= 0.90), full-catalogue d_pref fails (> 0.90)
    can = rc["leakage_canaries"]
    assert can["surface_only_all_pass"] is True
    assert can["surface_only_max_symmetric_auc"] <= 0.90
    assert can["overall_all_pass"] is False
    assert can["features"]["d_pref_full_catalogue_LEAKED"]["symmetric_auc"] > 0.90
    assert can["withheld_fault_fraction_with_d_pref_eq_1"] == 1.0

    # Registry uniqueness: fails both local 3-px dot overlap (> 0.70) and literal dense witness (1.0)
    reg = rc["correlation_overlap_vs_registry"]
    assert reg["unique_under_literal_rule"] is False
    assert reg["local_dot_field_duplicate"] is True
    assert reg["stop_required"] is True
    assert reg["local_worst_forward_3px_overlap"] > 0.70
    assert reg["public_dense_witness_forward_overlap"] == 1.0

    # Holdout DTI: leak-free static and Rule-2 have 95% CIs on 22,663 withheld positives
    ho = rc["holdout_dti"]
    assert ho["evidence_class"] == "HOLDOUT-DTI"
    assert ho["evaluator_version"] == "gems57-pooled-hide-v2"
    assert ho["withheld_positive_pixels"] == 22663
    assert len(ho["ci95"]) == 2
    assert ho["dti"] < 0.01  # pure surface static is ~0.005272, not leaked 0.033466
    assert "invalidated_leaked_full_catalogue_dpref_static" in ho

    # Note and HTML page must not claim submission-readiness or unqualified uniqueness
    assert len(rc["note"]) <= 140
    assert "DO NOT SUBMIT" in rc["note"]
    assert not rc["note"].endswith("; unique")

    html = (ROOT / "docs" / "tiltangle.html").read_text(encoding="utf-8")
    assert "Download the submission-ready GeoTIFF" not in html
    assert "0.962399" in html
    assert "0.005272" in html
    assert "0.776332" in html
    assert "DO NOT SUBMIT" in html
