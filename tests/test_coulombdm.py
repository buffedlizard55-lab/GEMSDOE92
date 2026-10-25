"""Unit tests for the COULOMBDM physics & Canny 1D NMS module (gems/coulombdm.py)."""
from __future__ import annotations

import inspect
import numpy as np
import pytest

from gems.coulombdm import (
    claycap_alteration_conduit,
    coulomb_criticality_2d,
    coulombdm_surface,
    fft_upward_continue,
    oriented_nms_1d,
    upward_rtp_conduit,
)


def test_coulombdm_zero_catalogue_argument_leakage():
    """No function in gems.coulombdm may accept catalogue/truth/label parameters."""
    forbidden = {"catalogue", "existing_faults", "labels", "truth", "visible"}
    for fn in (
        fft_upward_continue,
        upward_rtp_conduit,
        coulomb_criticality_2d,
        claycap_alteration_conduit,
        oriented_nms_1d,
        coulombdm_surface,
    ):
        params = set(inspect.signature(fn).parameters)
        assert params.isdisjoint(forbidden), f"{fn.__name__} accepts {params & forbidden}"


def test_fft_upward_continue_matches_analytical_exponential_decay():
    """Harmonic wave cos(k x) decays by exact exp(-|k| z) in interior under upward continuation."""
    h, w = 128, 256
    pixel_m = 100.0
    wavelength_m = 3200.0  # 32 px period -> fits integer cycles in 256 px
    k = 2.0 * np.pi / wavelength_m
    xx = np.arange(w, dtype=np.float32)[None, :] * pixel_m
    wave = np.broadcast_to(np.cos(k * xx), (h, w)).astype(np.float32)
    valid = np.ones((h, w), dtype=bool)

    up = fft_upward_continue(wave, valid, heights_m=(0.0, 200.0, 500.0), pixel_m=pixel_m, pad_px=64)
    np.testing.assert_allclose(up[0.0], wave, atol=1e-4)
    for z in (200.0, 500.0):
        expected = np.exp(-k * z) * wave[32:-32, 64:-64]
        np.testing.assert_allclose(up[z][32:-32, 64:-64], expected, atol=1.5e-2)


def test_coulomb_criticality_peaks_on_transtensional_triad_and_suppresses_105deg_washes():
    """Mohr-Coulomb criticality rewards N18E, N60E, and N30W (150 deg) over N105E washes."""
    rng = np.random.default_rng(42)
    shape = (40, 40)
    valid = np.ones(shape, dtype=bool)
    b4 = rng.uniform(5.0, 45.0, size=shape).astype(np.float32)
    b7 = rng.uniform(2.0, 30.0, size=shape).astype(np.float32)
    b8 = rng.uniform(1.0, 25.0, size=shape).astype(np.float32)

    means = {}
    for az in (18.0, 60.0, 150.0, 105.0):
        strike = np.full(shape, az, dtype=np.float32)
        res = coulomb_criticality_2d(strike, b4, b7, b8, valid)
        assert np.isfinite(res["c_coulomb"]).all()
        assert float(res["c_coulomb"].min()) >= 0.0 and float(res["c_coulomb"].max()) <= 1.0
        means[az] = float(res["c_coulomb"].mean())

    assert means[18.0] > means[105.0] + 0.30
    assert means[60.0] > means[105.0] + 0.25
    assert means[150.0] > means[105.0] + 0.25


@pytest.mark.parametrize(
    ("az_deg", "coord_fn"),
    [
        (0.0, lambda yy, xx: xx - 32.0),
        (90.0, lambda yy, xx: yy - 32.0),
        (45.0, lambda yy, xx: (yy + xx - 64.0) / np.sqrt(2.0)),
        (135.0, lambda yy, xx: (yy - xx) / np.sqrt(2.0)),
    ],
)
def test_oriented_nms_1d_extracts_thin_centreline_across_all_orientations(az_deg, coord_fn):
    yy, xx = np.mgrid[0:65, 0:65].astype(np.float32)
    dist = coord_fn(yy, xx)
    ridge = np.exp(-0.5 * (dist / 2.5) ** 2).astype(np.float32)
    valid = np.ones_like(ridge, dtype=bool)
    strike = np.full_like(ridge, az_deg)

    crest = oriented_nms_1d(ridge, strike, valid, step_px=1.0)
    # Centre pixel (32, 32) has dist == 0 and must be extracted
    assert bool(crest[32, 32]) is True
    # Total crest density must be thin (~1-2 px wide, < 6% of grid)
    assert float(crest.mean()) < 0.06


def test_coulombdm_surface_handles_sentinels_and_footprint_bounds():
    rng = np.random.default_rng(7)
    shape = (48, 56)
    foot = np.ones(shape, dtype=bool)
    foot[:4, :] = False
    yy, xx = np.mgrid[0:48, 0:56].astype(np.float32)

    det_elev = (-80.0 + 120.0 * np.tanh((xx - 28.0) / 4.0)).astype(np.float32)
    det_elev_slope = (np.abs(np.gradient(det_elev, axis=1)) * 5.0).astype(np.float32)
    det_elev[10, 10] = np.float32(-3.4028235e38)
    det_elev_slope[12, 12] = np.float32(np.inf)
    depth_to_base = np.where(xx > 28, 180.0, 25.0).astype(np.float32)
    rtp = (100.0 * np.tanh((xx - 36.0) / 3.0) + rng.normal(0, 2, shape)).astype(np.float32)

    out = coulombdm_surface(
        det_elev=det_elev,
        det_elev_slope=det_elev_slope,
        depth_to_base=depth_to_base,
        grav_slope=rng.uniform(0.03, 0.25, shape).astype(np.float32),
        grav_vg=rng.normal(0.0, 1.5, shape).astype(np.float32),
        geod_2ndinv=rng.uniform(5.0, 40.0, shape).astype(np.float32),
        geod_shearrate=rng.uniform(1.0, 25.0, shape).astype(np.float32),
        geod_dilaterate=rng.uniform(-2.0, 18.0, shape).astype(np.float32),
        rtp=rtp,
        cond_surf=rng.uniform(1.8, 3.8, shape).astype(np.float32),
        rad_k=rng.integers(0, 200, shape, dtype=np.uint8),
        rad_th=rng.integers(0, 200, shape, dtype=np.uint8),
        rad_u=rng.integers(0, 200, shape, dtype=np.uint8),
        gdr_plume_pct=rng.uniform(0.0, 1.0, shape).astype(np.float32),
        footprint=foot,
    )
    for k in ("S_raw", "S_pct", "hab_coulomb_pct"):
        arr = np.asarray(out[k])
        assert np.isfinite(arr).all(), f"non-finite values in {k}"
        assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0 + 1e-6
        assert np.all(arr[~foot] == 0.0)
    crest = np.asarray(out["crest_1d"])
    assert not np.any(crest & ~foot)
    assert int(crest.sum()) > 20


def test_disk_r3_binary_dilation_is_bit_identical_to_edt():
    """Shared-tool speedup in report_breakline_proxies.py must be 100% bit-identical to EDT <= 3.0."""
    from scipy.ndimage import binary_dilation, distance_transform_edt

    rng = np.random.default_rng(20261024)
    yy, xx = np.ogrid[-3:4, -3:4]
    disk_r3 = (yy * yy + xx * xx) <= 9  # 37 pixels with Euclidean dist <= 3.0

    for density in (0.001, 0.01, 0.15):
        mask = rng.random((120, 140)) < density
        via_edt = distance_transform_edt(~mask) <= 3.0
        via_dil = binary_dilation(mask, structure=disk_r3)
        assert np.array_equal(via_edt, via_dil)


def test_coulombdm_served_deliverables_gates_zip_and_run_card():
    """All 3 COULOMBDM deliverables, ZIPs, audits, and run card must validate cleanly from disk."""
    import hashlib
    import json
    import zipfile
    from pathlib import Path
    import rasterio

    root = Path(__file__).resolve().parents[1]
    downloads = root / "docs" / "downloads"
    evidence = root / "evidence"

    card_path = evidence / "coulombdm_run_card.json"
    served_card = downloads / "coulombdm_run_card.json"
    assert card_path.is_file() and served_card.is_file()
    assert card_path.read_bytes() == served_card.read_bytes()

    card = json.loads(card_path.read_text(encoding="utf-8"))
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["experiments_used"] == 3
    assert card["leakage_canary_max_symmetric_auc"] <= 0.90
    assert len(card["note"]) <= 140
    assert card["correlation_overlap_vs_registry"]["local"]["literal_duplicate"] is False
    assert (
        card["correlation_overlap_vs_registry"]["public"]["sparse_le_150k_over_70pct"]
        == 0
    )

    pub_scan = json.loads(
        (evidence / "coulombdm_public_registry_uniqueness.json").read_text(encoding="utf-8")
    )
    assert pub_scan["evidence_class"] == "REGISTRY-MEASUREMENT"
    assert pub_scan["final_dots"]["stop_required"] is True
    assert pub_scan["inventory"]["one_band_exact_template_grid_rasters_compared"] >= 1370

    variants = card["experiments_run_in_budget"]["arms"]
    assert set(variants) == {"coulomb1d", "s35coulomb65", "s45coulomb55"}
    # Standalone coulomb1d must achieve strong Rule-2 blind-fault holdout (> 0.090)
    assert variants["coulomb1d"]["fold_visible_rule2_holdout_dti"] > 0.090

    for arm, meta in variants.items():
        tif_path = root / meta["file_zeros"]
        zip_path = tif_path.with_suffix(".zip")
        audit_path = downloads / (tif_path.stem.removesuffix("-zeros") + "-audit.json")
        assert tif_path.is_file(), f"missing {tif_path}"
        assert zip_path.is_file(), f"missing {zip_path}"
        assert audit_path.is_file(), f"missing {audit_path}"

        sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
        assert sha == meta["sha256_zeros"]
        assert len(meta["submission_note"]) <= 140

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            assert names == [tif_path.name]
            assert hashlib.sha256(zf.read(names[0])).hexdigest() == sha

        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        assert audit["overall_pass"] is True
        assert audit["sha256_zeros"] == sha
        assert audit["verdict"] == "negative"
        assert audit["submission_eligible"] is False
        assert all(g["ok"] for g in audit["gates_zeros"])

        with rasterio.open(tif_path) as src:
            assert src.count == 1
            assert src.dtypes == ("float32",)
            assert (src.height, src.width) == (3730, 3292)
            assert src.crs is not None and src.crs.to_epsg() == 32611
            assert src.nodata is None
            arr = src.read(1)
            assert np.isfinite(arr).all()
            assert float(arr.min()) >= 0.0 and float(arr.max()) <= 1.0
            assert int((arr > 0).sum()) == 37654

