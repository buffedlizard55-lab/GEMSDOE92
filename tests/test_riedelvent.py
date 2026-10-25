"""Unit and artifact-contract tests for the RIEDELVENT lane (2026-10-25)."""
from __future__ import annotations

import json
from pathlib import Path
import zipfile

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

from gems.gates import run_gates, summarise
from gems.rasters import sha256_file
from gems.riedelvent import (
    COLLINEAR_NOVENT_INDICES,
    EXPECTED_TRAINING_BAND_TAGS,
    GROUP_B_RIEDEL_INDICES,
    GROUP_C_VENT_INDICES,
    RIEDELVENT_FEATURE_NAMES,
    assert_training_band_tags,
    build_additive_mobius_tail_allocation,
    gravity_gradient_tensor_invariants,
    riedel_obliquity_couplings,
)
from gems57.validate import assert_submittable, validate

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"

PRIMARY_STEM = "gemsdoe92-riedelvent-tail85k-85000-20261025-1cc99d0f"
BIN37K_STEM = "gemsdoe92-riedelvent-bin37k-37654-20261025-6797160f"
ABLATION_STEM = "gemsdoe92-riedelvent-collinear_novent-37654-20261025-37221889"


def test_assert_training_band_tags_catches_misattribution(tmp_path: Path) -> None:
    """Guard against #IR-92-VENTSCARP-BAND-INDEX-MISATTRIBUTION."""
    tif = tmp_path / "synthetic_19band.tif"
    profile = {
        "driver": "GTiff",
        "height": 4,
        "width": 4,
        "count": 19,
        "dtype": "float32",
        "crs": "EPSG:32611",
        "transform": Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
    }
    with rasterio.open(tif, "w", **profile) as dst:
        dst.write(np.zeros((19, 4, 4), dtype=np.float32))
        for bidx, expected_name in EXPECTED_TRAINING_BAND_TAGS.items():
            dst.update_tags(bidx, band_name=expected_name)

    with rasterio.open(tif) as src:
        assert_training_band_tags(src)

    # Corrupt Band 3 -> "heatflow" and verify fail-closed ValueError/AssertionError
    with rasterio.open(tif, "r+") as dst:
        dst.update_tags(3, band_name="heatflow")
    with rasterio.open(tif) as src:
        with pytest.raises((AssertionError, ValueError)):
            assert_training_band_tags(src)


def test_gravity_tensor_distinguishes_2d_step_from_3d_stepover() -> None:
    """A pure 1D step along x has near-zero 3D step-over ratio compared to a 3D corner."""
    yy, xx = np.mgrid[0:64, 0:64].astype(np.float32)
    valid = np.ones((64, 64), dtype=bool)
    # 1D sigmoid step varying only along x -> 2D sheet (lambda_2 ~ 0)
    g_1d = np.tanh((xx - 32.0) / 4.0).astype(np.float32)
    gz_1d = (0.25 / np.cosh((xx - 32.0) / 4.0) ** 2).astype(np.float32)
    step_1d, as_1d, gy_1d, gx_1d = gravity_gradient_tensor_invariants(
        g_1d, gz_1d, valid, sigma_px=1.5
    )

    # 3D accommodation step-over corner varying along both x and y
    g_3d = (np.tanh((xx - 32.0) / 4.0) * np.tanh((yy - 32.0) / 4.0)).astype(np.float32)
    gz_3d = (
        0.25
        / (np.cosh((xx - 32.0) / 4.0) ** 2 * np.cosh((yy - 32.0) / 4.0) ** 2)
    ).astype(np.float32)
    step_3d, as_3d, gy_3d, gx_3d = gravity_gradient_tensor_invariants(
        g_3d, gz_3d, valid, sigma_px=1.5
    )

    assert float(step_1d[32, 32]) < 0.05
    assert float(step_3d[28:37, 28:37].max()) > 0.35
    for arr in (step_1d, as_1d, gy_1d, gx_1d, step_3d, as_3d, gy_3d, gx_3d):
        assert arr.dtype == np.float32
        assert np.isfinite(arr).all()


def test_riedel_obliquity_peaks_at_20_and_72_deg_not_collinear() -> None:
    """Synthetic R (~20 deg) and antithetic R' (~72 deg) exceed collinear (0 deg) response."""
    yy, xx = np.mgrid[0:16, 0:16].astype(np.float32)
    valid = np.ones((16, 16), dtype=bool)
    # Non-constant edge magnitudes so percentile_rank spans (0, 1]
    mag = (1.0 + 0.1 * xx + 0.1 * yy).astype(np.float32)
    base_gy = np.zeros_like(mag)
    base_gx = mag.copy()
    step3d = np.ones_like(mag)
    shear_z = np.ones_like(mag)
    dilat_z = np.ones_like(mag)

    def eval_angle(deg: float) -> tuple[float, float, float]:
        rad = np.deg2rad(deg)
        s_gy = (np.sin(rad) * mag).astype(np.float32)
        s_gx = (np.cos(rad) * mag).astype(np.float32)
        r_syn, r_conj, r_exc, _ = riedel_obliquity_couplings(
            s_gy, s_gx, base_gy, base_gx, step3d, shear_z, dilat_z, valid
        )
        return float(r_syn[-1, -1]), float(r_conj[-1, -1]), float(r_exc[-1, -1])

    r0, rp0, exc0 = eval_angle(0.0)
    r20, rp20, exc20 = eval_angle(20.0)
    r72, rp72, exc72 = eval_angle(72.0)

    assert r20 > 5.0 * r0
    assert rp72 > 5.0 * rp0
    assert exc20 > exc0
    assert exc72 > exc0


def test_mobius_additive_tail_allocator_invariants() -> None:
    """Core receives exact 1.0; tail receives [tail_lo, tail_hi]; zero outside legal."""
    rng = np.random.default_rng(92)
    surface = rng.uniform(0.0, 1.0, size=(80, 80)).astype(np.float32)
    legal = np.ones((80, 80), dtype=bool)
    legal[:8, :] = False

    out = build_additive_mobius_tail_allocation(
        surface,
        legal,
        n_primary=50,
        n_total=120,
        min_dist_px=2.5,
        tail_lo=0.30,
        tail_hi=0.60,
    )
    assert out.dtype == np.float32
    assert np.isfinite(out).all()
    assert float(out.min()) >= 0.0
    assert float(out.max()) <= 1.0
    assert not np.any(out[~legal] > 0)
    pos = out[out > 0]
    assert pos.size == 120
    assert int((out == 1.0).sum()) == 50
    tail_vals = out[(out > 0) & (out < 1.0)]
    assert tail_vals.size == 70
    assert float(tail_vals.min()) >= 0.30 - 1e-6
    assert float(tail_vals.max()) <= 0.60 + 1e-6


def test_feature_ablation_excludes_riedel_and_vent_indices() -> None:
    """Ablation branch must exclude all Group-B Riedel and Group-C Vent features."""
    assert len(RIEDELVENT_FEATURE_NAMES) == 32
    assert set(COLLINEAR_NOVENT_INDICES).isdisjoint(GROUP_B_RIEDEL_INDICES)
    assert set(COLLINEAR_NOVENT_INDICES).isdisjoint(GROUP_C_VENT_INDICES)


@pytest.mark.parametrize(
    ("stem", "expected_pos", "expected_sha256"),
    [
        (
            PRIMARY_STEM,
            85000,
            "709fc6cd643d92cd9fa7f77623007bb9da3763aa4ba0871f41f06e4b96541a40",
        ),
        (
            BIN37K_STEM,
            37654,
            "da96c3af27994f6c8726758b9b59a8f8dc4be7894a7c0ae110039409cd41ba09",
        ),
        (
            ABLATION_STEM,
            37654,
            "2e220bb549e65c5992ed1d068269da170e1bc5140e169ad32dba1c1a01033553",
        ),
    ],
)
def test_riedelvent_rasters_zips_and_audits_pass_all_gates(
    stem: str, expected_pos: int, expected_sha256: str
) -> None:
    tif_path = DOWNLOADS / f"{stem}-zeros.tif"
    zip_path = DOWNLOADS / f"{stem}-zeros.zip"
    audit_path = DOWNLOADS / f"{stem}-audit.json"

    assert tif_path.is_file()
    assert zip_path.is_file()
    assert audit_path.is_file()
    assert sha256_file(tif_path) == expected_sha256

    with rasterio.open(SAMPLE) as ds:
        footprint = np.isfinite(ds.read(1))
    with rasterio.open(LABELS) as ds:
        cat = ds.read(1) > 0.5

    ok, report = summarise(
        run_gates(
            str(tif_path),
            str(SAMPLE),
            str(LABELS),
            prune_radius=2,
            require_submission_encoding=True,
        )
    )
    assert ok, report

    res = validate(tif_path, footprint, cat)
    assert_submittable(res)
    assert len(res["checks"]) == 15 and all(res["checks"].values())
    with rasterio.open(tif_path) as ds:
        arr = ds.read(1)
    assert int((arr > 0).sum()) == expected_pos

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert names == [tif_path.name]

    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["n_positive_pixels"] == expected_pos
    assert audit["verdict"] == "negative"
    assert audit["submission_eligible"] is False
    assert audit["overall_pass"] is True


def test_riedelvent_run_card_and_docs_contract() -> None:
    rc_ev = EVIDENCE / "riedelvent_run_card.json"
    rc_dl = DOWNLOADS / "riedelvent_run_card.json"
    assert rc_ev.is_file() and rc_dl.is_file()
    assert rc_ev.read_bytes() == rc_dl.read_bytes()

    card = json.loads(rc_ev.read_text(encoding="utf-8"))
    required_keys = {
        "hypothesis",
        "mechanism",
        "mimic",
        "holdout_dti",
        "registry_uniqueness",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "submission_note",
        "verdict",
    }
    assert required_keys.issubset(card.keys())
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["live_weekly_slots_spent"] == 0
    assert card["experiments_used"] == 3
    assert len(card["submission_note"]) <= 140
    assert card["leakage_canary"]["pass"] is True
    assert card["leakage_canary"]["max_single_feature_symmetric_auc"] <= 0.90
    assert card["registry_uniqueness"]["local_unique"] is True
    assert card["registry_uniqueness"]["public_dual_reading_unique"] is True
    assert card["registry_uniqueness"]["public_worst_operative_overlap_3px"] <= 0.70
    assert card["validator_output"]["values_in_0_1"] is True
    assert card["validator_output"]["no_nan_inside_footprint"] is True
    assert card["validator_output"]["crs_shape_transform_match"] is True

    for doc_rel in (
        "docs/riedelvent.html",
        "docs/ANALYSIS_20261025_RIEDELVENT.md",
        "docs/HYPOTHESES_20261025_RIEDELVENT.md",
    ):
        assert (ROOT / doc_rel).is_file(), f"Missing {doc_rel}"
