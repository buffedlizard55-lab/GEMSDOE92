"""Unit tests for the POISSONFLEX lane (gems/poissonflex.py)."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr

from gems.poissonflex import (
    FEATURE_NAMES,
    basement_rollover_flexure,
    bolstad_equalize_quadrants,
    build_poissonflex_crest_surface,
    compute_poissonflex_stack,
    fit_predict_loqo_poissonflex,
    knickpoint_saddle_and_integral,
    moving_window_poisson,
    within_quadrant_rank,
)


def _make_quad(h: int, w: int) -> np.ndarray:
    q = np.zeros((h, w), dtype=np.int8)
    q[: h // 2, w // 2 :] = 1
    q[h // 2 :, : w // 2] = 2
    q[h // 2 :, w // 2 :] = 3
    return q


def test_within_quadrant_rank_zero_cross_quadrant_leakage():
    rng = np.random.default_rng(7)
    h, w = 40, 44
    quad = _make_quad(h, w)
    valid = np.ones((h, w), dtype=bool)
    valid[0, :] = False
    f1 = rng.normal(size=(h, w)).astype(np.float64)
    f2 = f1.copy()
    # Massively shift & scale NE (quad == 1), mimicking #IR-92-NE-QUADRANT-LOQO-COLLAPSE
    f2[quad == 1] = 0.01 * f2[quad == 1] - 500.0

    r1 = within_quadrant_rank(f1, valid, quad)
    r2 = within_quadrant_rank(f2, valid, quad)
    # Zero cross-quadrant contamination & exact affine rank invariance
    assert np.array_equal(r1[quad != 1], r2[quad != 1])
    assert np.allclose(r1[quad == 1], r2[quad == 1], atol=1e-6)
    assert np.all(r1[~valid] == 0.0)
    for q in range(4):
        vq = r1[valid & (quad == q)]
        assert vq.min() == pytest.approx(0.0, abs=1e-6)
        assert vq.max() == pytest.approx(1.0, abs=1e-6)


def test_bolstad_equalize_cures_ne_starvation_preserving_monotonicity():
    rng = np.random.default_rng(19)
    h, w = 80, 80
    quad = _make_quad(h, w)
    valid = np.ones((h, w), dtype=bool)
    base = rng.beta(0.5, 8.0, size=(h, w)).astype(np.float32)
    depressed = base.copy()
    depressed[quad == 1] *= 0.15  # NE severely uncalibrated downward
    depressed[quad == 2] = np.clip(depressed[quad == 2] * 1.4, 0.0, 1.0)

    # Raw top-200 starves NE completely
    raw_top = depressed >= np.quantile(depressed, 1.0 - 200.0 / depressed.size)
    assert int((raw_top & (quad == 1)).sum()) == 0

    eq = bolstad_equalize_quadrants(depressed, valid, quad)
    assert eq.dtype == np.float32
    assert float(eq.min()) >= 0.0 and float(eq.max()) <= 1.0
    for q in range(4):
        m = quad == q
        rho = float(spearmanr(depressed[m], eq[m]).statistic)
        assert rho > 0.9999
    eq_top = eq >= np.quantile(eq, 1.0 - 200.0 / eq.size)
    ne_share = float((eq_top & (quad == 1)).sum()) / float(eq_top.sum())
    assert 0.20 <= ne_share <= 0.30


def test_moving_window_poisson_detects_coupling_and_demagnetization():
    h, w = 64, 64
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    quad = _make_quad(h, w)

    # Vertical gravity gradient step + wave
    grav_vg = np.tanh((xx - 24.0) / 3.0) + 0.25 * np.sin(yy / 4.0)
    grav_slope = np.exp(-0.5 * ((xx - 24.0) / 3.0) ** 2) + np.exp(-0.5 * ((xx - 46.0) / 2.5) ** 2)
    # Left fault (x=24): coupled positive Poisson step; Right fault (x=46): hydrothermally demagnetized trough!
    rtp = 40.0 * grav_vg - 35.0 * np.exp(-0.5 * ((xx - 46.0) / 1.8) ** 2)

    out = moving_window_poisson(rtp, grav_vg, grav_slope, valid, quad, window_sigma_px=3.0)
    assert float(out["r_pg"][:, 18:30].mean()) > 0.65
    # Demagnetized trough at x=46 exceeds background
    assert float(out["demag_conduit"][:, 45:48].mean()) > float(out["demag_conduit"][:, 5:12].mean()) * 2.5


def test_basement_rollover_flexure_peaks_updip_on_footwall_shoulder():
    h, w = 48, 80
    _, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    # Listric half-graben thickening eastward across ramp centered at x = 40
    depth_to_base = 30.0 + 900.0 / (1.0 + np.exp(-(xx - 40.0) / 4.0))
    # Subtle compaction monocline above footwall shoulder (x ~ 33)
    det_elev = 120.0 - 4.0 / (1.0 + np.exp(-(xx - 33.0) / 3.0))

    flex = basement_rollover_flexure(depth_to_base, det_elev, valid, curv_sigma_px=2.0)
    prof_grad = flex["base_step_grad"][h // 2, 15:65]
    prof_shld = flex["shoulder_curv"][h // 2, 15:65]
    x_grad_peak = 15 + int(np.argmax(prof_grad))
    x_shld_peak = 15 + int(np.argmax(prof_shld))
    # Buried footwall shoulder curvature peaks strictly updip (west) of the mid-ramp inflection!
    assert x_shld_peak < x_grad_peak
    assert float(flex["compaction_lock"][h // 2, x_shld_peak]) > 0.25


def test_knickpoint_saddle_bridges_collinear_canyon_mouths():
    h, w = 64, 64
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    valid = np.ones((h, w), dtype=bool)
    # Range dipping east across x=32 with periodic incised E-W canyons along y -> saddles at x=32
    scarp = 80.0 / (1.0 + np.exp((xx - 32.0) / 2.2))
    canyons = -12.0 * np.cos(2.0 * np.pi * yy / 10.0) * np.exp(-0.5 * ((xx - 30.0) / 8.0) ** 2)
    det_elev = (scarp + canyons).astype(np.float32)
    strike_ns = np.zeros((h, w), dtype=np.float32)  # 0 deg = N-S strike

    kn = knickpoint_saddle_and_integral(det_elev, strike_ns, valid, hess_sigma_px=1.5, along_sigma_px=5.0)
    # Integral along N-S strike at x=31..33 exceeds off-fault background
    on_fault = float(kn["knick_strike_integral"][10:54, 30:34].mean())
    off_fault = float(kn["knick_strike_integral"][10:54, 8:16].mean())
    assert on_fault > off_fault * 3.0


def test_full_stack_and_loqo_end_to_end():
    rng = np.random.default_rng(101)
    h, w = 56, 56
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False
    quad = _make_quad(h, w)
    quad[~foot] = -1

    def rf(scale=1.0):
        return (scale * rng.normal(size=(h, w))).astype(np.float32)

    st = compute_poissonflex_stack(
        rtp=rf(50.0),
        geod_2ndinv=np.abs(rf(15.0)),
        grav_slope=np.abs(rf(2.0)),
        geod_shearrate=np.abs(rf(10.0)),
        geod_dilaterate=rf(8.0),
        grav_vg=rf(1.5),
        det_elev=rf(100.0),
        grav_anom=rf(8.0),
        depth_to_base=np.abs(rf(400.0)),
        cond_surf=np.abs(rf(3.0)) + 0.5,
        grav_hg=rf(2.0),
        det_elev_slope=np.abs(rf(6.0)),
        rad_k=np.abs(rf(20.0)) + 2.0,
        rad_th=np.abs(rf(20.0)) + 2.0,
        rad_u=np.abs(rf(15.0)) + 1.0,
        gdr_plume_feat=np.abs(rf(0.2)),
        footprint=foot,
        quad=quad,
    )
    assert st["X_foot"].shape == (int(foot.sum()), len(FEATURE_NAMES))
    assert len(FEATURE_NAMES) == 30
    assert np.isfinite(st["X_foot"]).all()

    lbl = np.zeros((h, w), dtype=bool)
    lbl[8:20, 12] = True
    lbl[8:20, 42] = True
    lbl[36:48, 14] = True
    lbl[36:48, 44] = True

    fit = fit_predict_loqo_poissonflex(
        st["X_foot"], foot, st["valid"], quad, lbl, guard_px=3, neg_buffer_px=2.0, max_iter=25
    )
    for k in ("proba_raw", "proba_eq"):
        p = fit[k]
        assert p.shape == (h, w) and p.dtype == np.float32
        assert np.isfinite(p).all()
        assert float(p.min()) >= 0.0 and float(p.max()) <= 1.0
        assert np.all(p[~foot] == 0.0)

    crest = build_poissonflex_crest_surface(
        fit["proba_eq"], st["L_scarp_knick"], st["L_poisson_flex"], st["valid"]
    )
    assert crest["S_crest"].shape == (h, w)
    assert crest["ridge_1d"].dtype == bool


def test_streaming_from_files_matches_in_memory_stack(tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    from gems.coulomb_loqo import gdr_blind_thermal_features
    from gems.poissonflex import compute_poissonflex_from_files

    rng = np.random.default_rng(77)
    h, w = 36, 40
    foot = np.ones((h, w), dtype=bool)
    foot[0, :] = False
    quad = _make_quad(h, w)
    quad[~foot] = -1

    stack_p = tmp_path / "stack.tif"
    rad_p = tmp_path / "rad.tif"
    csv_p = tmp_path / "gdr.csv"

    bands = {i: rng.normal(loc=15.0, scale=5.0, size=(h, w)).astype(np.float32) for i in range(1, 20)}
    with rasterio.open(
        stack_p, "w", driver="GTiff", height=h, width=w, count=19,
        dtype="float32", crs="EPSG:32611", transform=from_origin(0, h * 100, 100, 100)
    ) as ds:
        for i in range(1, 20):
            ds.write(bands[i], i)

    rad_arr = rng.integers(5, 180, size=(3, h, w), dtype=np.uint8)
    with rasterio.open(
        rad_p, "w", driver="GTiff", height=h, width=w, count=3,
        dtype="uint8", crs="EPSG:32611", transform=from_origin(0, h * 100, 100, 100)
    ) as rds:
        for i in range(1, 4):
            rds.write(rad_arr[i - 1], i)

    csv_p.write_text(
        "row,col,temp_c,thermalclass,geothermquartz_c,dist_known_fault_px\n"
        "12,15,65.0,Hot ,115.0,0.0\n"
        "24,28,22.0,Cold,95.0,1.0\n"
    )
    valid = foot & np.isfinite(bands[12]) & np.isfinite(bands[19]) & np.isfinite(bands[2])
    gdr_f = gdr_blind_thermal_features(csv_p, (h, w), valid, sigma_px=14.0)["plume_feat"]

    ref = compute_poissonflex_stack(
        rtp=bands[2], geod_2ndinv=bands[4], grav_slope=bands[5], geod_shearrate=bands[7],
        geod_dilaterate=bands[8], grav_vg=bands[11], det_elev=bands[12], grav_anom=bands[13],
        depth_to_base=bands[15], cond_surf=bands[17], grav_hg=bands[18], det_elev_slope=bands[19],
        rad_k=rad_arr[0], rad_th=rad_arr[1], rad_u=rad_arr[2], gdr_plume_feat=gdr_f,
        footprint=foot, quad=quad,
    )
    streamed = compute_poissonflex_from_files(stack_p, rad_p, csv_p, foot, quad)
    assert np.array_equal(ref["valid"], streamed["valid"])
    assert np.allclose(ref["X_foot"], streamed["X_foot"], atol=1e-5)
    assert np.allclose(ref["L_scarp_knick"], streamed["L_scarp_knick"], atol=1e-5)
    assert np.allclose(ref["L_poisson_flex"], streamed["L_poisson_flex"], atol=1e-5)


def test_poissonflex_run_card_and_artifacts_contract():
    import hashlib
    import json
    from pathlib import Path
    import rasterio

    root = Path(__file__).resolve().parents[1]
    src_card = root / "evidence" / "poissonflex_run_card.json"
    dl_card = root / "docs" / "downloads" / "poissonflex_run_card.json"
    assert src_card.is_file() and dl_card.is_file()
    assert src_card.read_bytes() == dl_card.read_bytes()

    card = json.loads(src_card.read_text(encoding="utf-8"))
    for key in (
        "hypothesis",
        "mechanism",
        "named_non_fault_process_that_could_mimic_it",
        "holdout_dti",
        "correlation_overlap_vs_registry",
        "raster_sha256",
        "validator_output",
        "submission_name",
        "note",
        "verdict",
    ):
        assert key in card, f"missing Protocol Rule 5 key: {key}"

    assert card["primary_arm"] == "poissonflex_opt"
    assert card["verdict"] == "negative"
    assert card["submission_eligible"] is False
    assert card["weekly_slots_used"] == 0
    assert card["experiments_used"] == "3/3"
    assert len(card["note"]) <= 140
    assert len(card["submission_name"]) <= 140
    assert card["leakage_canary_max_symmetric_auc"] <= 0.90
    assert card["validator_output"]["no_nan_in_footprint"] is True
    assert card["validator_output"]["values_in_0_1"] is True
    assert card["validator_output"]["crs_shape_transform_match"] is True
    assert card["validator_output"]["dots"] == 45000

    # Verify holdout ordering and SGMC discovery
    sc = card["holdout_dti"]["scores"]
    assert sc["poissonflex_opt"]["dti"] > sc["H19_5_dvis2"]["dti"]
    assert sc["poissonflex_opt"]["dti"] < sc["COULOMBLOQO_standalone_dvis2"]["dti"]
    sgmc = card["holdout_dti"]["sgmc_off_catalogue_proxy_gt3px"]["dti_by_arm"]
    assert sgmc["poissonflex_opt"] > sgmc["R0"] > sgmc["COULOMBLOQO_standalone"]

    # Verify all 3 GeoTIFFs on disk match exact hashes, [0, 1] finite bounds, and dot counts
    with rasterio.open(root / "data" / "bridge" / "sample_submission.tif") as ref_ds:
        foot = np.isfinite(ref_ds.read(1))
        ref_crs = ref_ds.crs
        ref_transform = ref_ds.transform
    with rasterio.open(root / "data" / "bridge" / "labels.tif") as lds:
        cat = lds.read(1) > 0.5

    expected_dots = {"poissonflex_opt": 45000, "poissonflex_eq": 37654, "poissonflex_raw": 37654}
    for arm, meta in card["all_arms"].items():
        tif_p = root / meta["file"]
        assert tif_p.is_file()
        assert hashlib.sha256(tif_p.read_bytes()).hexdigest() == meta["sha256"]
        with rasterio.open(tif_p) as ds:
            assert ds.count == 1 and ds.dtypes[0] == "float32"
            assert ds.crs == ref_crs and ds.transform == ref_transform
            arr = ds.read(1)
        assert arr.shape == (3730, 3292)
        assert np.isfinite(arr).all()
        assert float(arr.min()) == 0.0 and float(arr.max()) == 1.0
        assert int((arr > 0).sum()) == expected_dots[arm]
        assert not np.any((arr > 0) & ~foot)
        assert not np.any((arr > 0) & cat)


def test_poissonflex_audit_sidecars_and_zip_integrity():
    import hashlib
    import json
    import zipfile
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    card = json.loads((root / "evidence" / "poissonflex_run_card.json").read_text(encoding="utf-8"))
    best_meta = card["all_arms"]["poissonflex_opt"]
    zip_p = root / best_meta["zip"]
    assert zip_p.is_file()
    assert hashlib.sha256(zip_p.read_bytes()).hexdigest() == best_meta["zip_sha256"]
    with zipfile.ZipFile(zip_p) as zf:
        names = zf.namelist()
        assert len(names) == 1 and names[0].endswith("-zeros.tif")
        assert hashlib.sha256(zf.read(names[0])).hexdigest() == best_meta["sha256"]

    for arm, meta in card["all_arms"].items():
        tif_p = root / meta["file"]
        audit_p = tif_p.with_name(tif_p.stem.removesuffix("-zeros") + "-audit.json")
        assert audit_p.is_file()
        adoc = json.loads(audit_p.read_text(encoding="utf-8"))
        assert adoc["overall_pass"] is True
        assert adoc["submission_eligible"] is False
        assert adoc["sha256_zeros"] == meta["sha256"]
        assert adoc["n_dots"] == meta["n_dots"]
        assert all(g["ok"] is True for g in adoc["gates_zeros"])


def test_prior_next_steps_evidence_receipts_complete():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    cl_sel = json.loads((root / "evidence" / "coulomb_loqo_dual_reading_selector.json").read_text(encoding="utf-8"))
    assert cl_sel["public_inventory"]["missing_blobs"] == 0
    assert cl_sel["candidates"]["COULOMBLOQO_standalone"]["decision"]["verdict"] == "negative"
    assert cl_sel["candidates"]["COULOMBLOQO_dual45"]["decision"]["verdict"] == "negative"

    ne_diag = json.loads((root / "evidence" / "ne_quadrant_loqo_collapse_diagnostic.json").read_text(encoding="utf-8"))
    assert ne_diag["covariate_shift_by_quadrant"]["geod_shearrate"]["NE"]["median"] == 0.0


def test_poissonflex_synchronized_across_readme_site_and_ledger():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    card = json.loads((root / "evidence" / "poissonflex_run_card.json").read_text(encoding="utf-8"))
    sha = card["raster_sha256"]
    fname = Path(card["file"]).name

    pre_reg = (root / "docs/HYPOTHESES_20261025_POISSONFLEX.md").read_text(encoding="utf-8")
    assert "poissonflex_opt" in pre_reg and "POISSONFLEX" in pre_reg

    for rel in (
        "README.md",
        "SESSION_PROMPT.md",
        "SLOT_PLAN.md",
        "docs/REVIEW_CURRENT.md",
        "docs/NEXT_STEPS.md",
        "docs/ANALYSIS_20261025_POISSONFLEX.md",
        "docs/index.html",
        "docs/executive-summary.html",
        "docs/SUBMIT.html",
        "docs/HYPOTHESES.html",
        "ledger/submissions.csv",
    ):
        txt = (root / rel).read_text(encoding="utf-8")
        assert fname in txt or fname.removesuffix("-zeros.tif") in txt, f"missing {fname} in {rel}"
        if rel != "docs/HYPOTHESES.html":
            assert sha in txt, f"missing {sha} in {rel}"

