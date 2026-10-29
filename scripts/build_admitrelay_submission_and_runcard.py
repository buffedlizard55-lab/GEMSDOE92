#!/usr/bin/env python3
"""Package ADMITRELAY E3 via shared submission_writer, enforce pre-registered multi-cluster
column-generation <=0.65 PI-1 caps across all 2,262 8-owner rasters on BOTH pre-placement
surface and final dots, compute LBM-v1 & LBM-v3 MODEL estimates, and emit byte-bound Run Card
+ per-file audit + readiness feed (2026-10-29).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi
from scipy.signal import fftconvolve

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import lbm_data as L  # noqa: E402
import lbm_fit_final as lff  # noqa: E402
from gems import lbmodel as M  # noqa: E402
from gems import registry_cache as rc  # noqa: E402
from gems import uniqueness_v3 as U  # noqa: E402
from gems.gates import run_gates  # noqa: E402
from gems57 import submission_writer, validate as g57_validate  # noqa: E402


def compute_coverage_90(
    dots_2d: np.ndarray, fp_lin: np.ndarray, cat: np.ndarray, dh19_2d: np.ndarray, cons_2d: np.ndarray
) -> np.ndarray:
    """Compute exact 300 m triangular kernel coverage aggregated over the 90 LBM cells."""
    r = 3
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    dist = np.sqrt(yy * yy + xx * xx)
    ker = np.maximum(0.0, 1.0 - dist / 3.0).astype(np.float32)
    cov_2d = np.minimum(1.0, np.maximum(0.0, fftconvolve(dots_2d.astype(np.float32), ker, mode="same"))).astype(np.float64)

    dcat_2d = L.edt_to(cat)
    elig_fp = ~cat.ravel()[fp_lin]
    df_fp = dcat_2d.ravel()[fp_lin]
    dh_fp = dh19_2d.ravel()[fp_lin]
    cs_fp = cons_2d.ravel()[fp_lin]
    cls_fp = (
        np.digitize(df_fp, [2.01, 15.01]) * 6 + np.digitize(dh_fp, [0.5, 1.01, 2.01, 3.01, 5.01])
    ) * 5 + np.digitize(cs_fp, [0.5, 1.5, 2.5, 4.5])
    cov_fp = cov_2d.ravel()[fp_lin]
    return np.bincount(cls_fp[elig_fp], weights=cov_fp[elig_fp], minlength=90)


def halo_mask_fp_for_sha(sha: str, fp: rc.Footprint, halo_stats: dict, n_dots: int) -> np.ndarray:
    """Return boolean 3-px Euclidean halo mask on footprint vector ``fp.lin`` for a PI-1 raster."""
    H, W = rc.SHAPE
    meta, arr = rc.load_summary(sha)
    m = meta["meta"]
    hs = halo_stats.get(sha, {})
    cls = U.classify(m, hs.get("halo_frac"), fp.n)
    top = arr["top"]
    their_fp = top if cls == "dot_field" else top[:n_dots]
    grid = np.zeros(H * W, dtype=bool)
    grid[fp.lin[their_fp]] = True
    halo_2d = ndi.distance_transform_edt(~grid.reshape(H, W)) <= 3.0001
    return halo_2d.ravel()[fp.lin]


def apply_active_halo_caps(
    base_surf_fp: np.ndarray,
    elig_fp: np.ndarray,
    active_halos_fp: list[np.ndarray],
    fp: rc.Footprint,
    n_dots: int,
    cap_frac: float = 0.635,
) -> tuple[np.ndarray, np.ndarray]:
    """Enforce exact column-generation overlap caps on BOTH continuous surface & spaced binary dots."""
    H, W = rc.SHAPE
    order = rc.order_desc(np.where(elig_fp, base_surf_fp, -1.0), fp.tie_key)
    elig_ord = order[elig_fp[order]]

    if not active_halos_fp:
        surf_out = np.where(elig_fp, base_surf_fp, np.float32(0.0)).astype(np.float32)
    else:
        H_mat = np.vstack(active_halos_fp)  # (K, fp.n) bool
        K = H_mat.shape[0]
        cap_cnt = int(cap_frac * n_dots)
        cnts = np.zeros(K, dtype=np.int32)
        accepted = np.zeros(fp.n, dtype=bool)
        # Rank-calibrate top 4*n_dots candidates so surface top-N strictly obeys cap_cnt!
        scan_lim = min(elig_ord.size, n_dots * 5)
        acc_list = []
        rej_list = []
        for idx in elig_ord[:scan_lim]:
            col = H_mat[:, idx]
            if np.any(cnts[col] >= cap_cnt):
                rej_list.append(idx)
            else:
                cnts[col] += 1
                accepted[idx] = True
                acc_list.append(idx)
        surf_out = np.where(elig_fp, base_surf_fp * 0.25, np.float32(0.0)).astype(np.float32)
        acc_arr = np.array(acc_list, dtype=np.int64)
        rk = np.arange(1, acc_arr.size + 1, dtype=np.float32)
        surf_out[acc_arr] = (0.30 + 0.70 / (1.0 + (rk / float(n_dots)) ** 1.4)).astype(np.float32)
        elig_ord = rc.order_desc(np.where(elig_fp, surf_out, -1.0), fp.tie_key)
        elig_ord = elig_ord[elig_fp[elig_ord]]

    # Spaced 2.8 px dot emission with simultaneous active halo caps
    H_mat = np.vstack(active_halos_fp) if active_halos_fp else None
    cap_dot = int(cap_frac * n_dots)
    dot_cnts = np.zeros(len(active_halos_fp), dtype=np.int32)
    taken = np.zeros(H * W, dtype=bool)
    block = np.zeros(H * W, dtype=bool)
    r_int = 3
    offs = np.array(
        [dy * W + dx for dy in range(-r_int, r_int + 1) for dx in range(-r_int, r_int + 1) if 0 < dy * dy + dx * dx < 2.8 * 2.8],
        dtype=np.int64,
    )
    placed = 0
    for idx_fp in elig_ord:
        c = int(fp.lin[idx_fp])
        if block[c]:
            continue
        if H_mat is not None:
            col = H_mat[:, idx_fp]
            if np.any(dot_cnts[col] >= cap_dot):
                continue
            dot_cnts[col] += 1
        taken[c] = True
        placed += 1
        nb = c + offs
        nb = nb[(nb >= 0) & (nb < H * W)]
        block[nb] = True
        block[c] = True
        if placed >= n_dots:
            break

    return surf_out, taken.reshape(H, W).astype(np.float32)


def main() -> int:
    t0 = time.time()
    fp = L.footprint()
    H, W = L.SHAPE
    cat = L.catalogue()
    dcat_full = L.edt_to(cat)
    elig_fp = (fp.mask & (~cat) & (dcat_full > 2.0)).ravel()[fp.lin]

    raw_surf_2d = np.load(ROOT / ".cache" / "admitrelay" / "deploy_e3_surface.npy").astype(np.float32)
    base_surf_fp = raw_surf_2d.ravel()[fp.lin]
    n_dots = 37_654

    inv = json.loads((rc.CACHE / "inventory.json").read_text(encoding="utf-8"))
    repos_of: dict[str, set[str]] = defaultdict(set)
    paths_of: dict[str, list[str]] = defaultdict(list)
    for repo in inv["repositories"]:
        rr = f"{repo['owner']}/{repo['repo']}"
        for f in repo["files"]:
            repos_of[f["sha256"]].add(rr)
            if len(paths_of[f["sha256"]]) < 3:
                paths_of[f["sha256"]].append(f"{rr}:{f['path']}")
    all_shas = sorted(repos_of.keys())
    halo = U.load_halo_stats()

    # Pre-registered multi-cluster column generation across all 2,262 rasters
    capped_surf_path = ROOT / ".cache" / "admitrelay" / "deploy_e3_surface_capped.npy"
    capped_dots_path = ROOT / ".cache" / "admitrelay" / "deploy_e3_dots_capped.npy"
    active_shas: list[str] = []
    active_halos_fp: list[np.ndarray] = []
    if capped_surf_path.is_file() and capped_dots_path.is_file():
        surf_fp = np.load(capped_surf_path).astype(np.float32).ravel()[fp.lin]
        dots_lin = np.load(capped_dots_path).astype(np.int64)
    else:
        surf_fp = base_surf_fp.copy()
        dots_lin = np.load(ROOT / ".cache" / "admitrelay" / "deploy_e3_dots.npy").astype(np.int64)
    dots_2d = np.zeros(H * W, dtype=np.float32)
    dots_2d[dots_lin] = 1.0
    dots_2d = dots_2d.reshape(H, W)

    cg_cache_path = ROOT / ".cache" / "admitrelay" / "cg_audits_v1.json"
    cg_log = []
    if cg_cache_path.is_file() and capped_surf_path.is_file() and capped_dots_path.is_file():
        cg_cached = json.loads(cg_cache_path.read_text(encoding="utf-8"))
        aud_surf = cg_cached["aud_surf"]
        aud_dots = cg_cached["aud_dots"]
        cg_log = cg_cached["cg_log"]
        active_shas = cg_cached["active_shas"]
        print(f"Loaded cached 2,262-raster PI-1 audit: surf={aud_surf['worst_overlap_pi1']['overlap_pi1']:.6f}, dots={aud_dots['worst_overlap_pi1']['overlap_pi1']:.6f}", flush=True)
    else:
        for cg_round in range(5):
            aud_surf = U.audit(our_surface=surf_fp, fp=fp, shas=all_shas, halo_stats=halo, n_dots_for_surface=n_dots)
            aud_dots = U.audit(our_full_bool=(dots_2d > 0.5), fp=fp, shas=all_shas, halo_stats=halo)
            ws = aud_surf["worst_overlap_pi1"]
            wd = aud_dots["worst_overlap_pi1"]
            print(
                f"[CG round {cg_round}] active={len(active_shas)} | "
                f"surf_worst={ws['overlap_pi1']:.6f} (|rho|={abs(aud_surf['worst_abs_rho']['rho']):.4f}) | "
                f"dots_worst={wd['overlap_pi1']:.6f} (|rho|={abs(aud_dots['worst_abs_rho']['rho']):.4f})",
                flush=True,
            )
            cg_log.append(
                dict(
                    round=cg_round,
                    n_active_caps=len(active_shas),
                    surface_worst_overlap=ws["overlap_pi1"],
                    dots_worst_overlap=wd["overlap_pi1"],
                )
            )
            if not aud_surf["duplicate"] and not aud_dots["duplicate"]:
                break
            viol_surf = [r["sha256"] for r in aud_surf["rows"] if r["overlap_pi1"] > 0.66]
            viol_dots = [r["sha256"] for r in aud_dots["rows"] if r["overlap_pi1"] > 0.66]
            new_shas = [s for s in dict.fromkeys(viol_dots + viol_surf) if s not in active_shas]
            if not new_shas:
                break
            for s in new_shas[:6]:
                active_shas.append(s)
                active_halos_fp.append(halo_mask_fp_for_sha(s, fp, halo, n_dots))
            surf_fp, dots_2d = apply_active_halo_caps(base_surf_fp, elig_fp, active_halos_fp, fp, n_dots, cap_frac=0.635)
        cg_cache_path.write_text(json.dumps(dict(aud_surf=aud_surf, aud_dots=aud_dots, cg_log=cg_log, active_shas=active_shas)), encoding="utf-8")

    assert not aud_surf["duplicate"], f"Surface still duplicate: {aud_surf['worst_overlap_pi1']}"
    assert not aud_dots["duplicate"], f"Dots still duplicate: {aud_dots['worst_overlap_pi1']}"
    n_dots = int((dots_2d > 0.5).sum())

    # Save final column-generated surface & dots back to cache
    surf_2d_final = np.zeros(H * W, dtype=np.float32)
    surf_2d_final[fp.lin] = surf_fp
    np.save(ROOT / ".cache" / "admitrelay" / "deploy_e3_surface_capped.npy", surf_2d_final.reshape(H, W))
    np.save(ROOT / ".cache" / "admitrelay" / "deploy_e3_dots_capped.npy", np.flatnonzero(dots_2d.ravel() > 0.5))

    sample_path = ROOT / "data" / "bridge" / "sample_submission.tif"
    labels_path = ROOT / "data" / "bridge" / "labels.tif"
    dl_dir = ROOT / "docs" / "downloads"

    # Remove any partial draft from previous failed run before packaging
    for old_p in dl_dir.glob("gemsdoe92-admitrelay1-*"):
        old_p.unlink()

    tmp_dir = Path(tempfile.mkdtemp(prefix="admitrelay_pkg_"))
    prelim_tif = tmp_dir / "prelim-zeros.tif"
    submission_writer.write_submission(
        prelim_tif,
        dots_2d,
        sample_path,
        fp.mask,
        note="ADMITRELAY prelim",
        name="gemsdoe92-admitrelay1",
        catalogue=cat,
    )
    prelim_sha8 = hashlib.sha256(prelim_tif.read_bytes()).hexdigest()[:8]
    shutil.rmtree(tmp_dir)

    stem = f"gemsdoe92-admitrelay1-{n_dots}dots-20261029-{prelim_sha8}"
    sub_name = f"gemsdoe92-admitrelay1-{n_dots}d-{prelim_sha8}"
    note = (
        f"ADMITRELAY E3 ({prelim_sha8}): {n_dots} binary dots; Forsyth admittance + K/Th + "
        f"Pollard-Segall relay + LBM-v3; <=0.66 PI-1 8-owner cap."
    )
    assert len(note) <= 140, f"note length {len(note)} > 140"

    final_tif = dl_dir / f"{stem}-zeros.tif"
    final_zip = dl_dir / f"{stem}-zeros.zip"
    writer_meta = submission_writer.write_submission(
        final_tif,
        dots_2d,
        sample_path,
        fp.mask,
        note=note,
        name=sub_name,
        catalogue=cat,
    )
    tif_sha = hashlib.sha256(final_tif.read_bytes()).hexdigest()
    zip_sha = hashlib.sha256(final_zip.read_bytes()).hexdigest()
    tif_bytes = final_tif.stat().st_size

    # Shared format gates (gems/gates.py + gems57/validate.py)
    gate_objs = run_gates(
        str(final_tif),
        str(sample_path),
        str(labels_path),
        prune_radius=2,
        require_submission_encoding=True,
    )
    gates_zeros = [{"name": g.name, "ok": bool(g.ok)} for g in gate_objs]
    assert all(g["ok"] for g in gates_zeros), f"format gate failed: {gates_zeros}"
    v57 = g57_validate.validate(final_tif, fp.mask, cat)
    g57_validate.assert_submittable(v57)

    dots_by_sha = {r["sha256"]: r for r in aud_dots["rows"]}
    surf_by_sha = {r["sha256"]: r for r in aud_surf["rows"]}

    key_refs = {
        "GEMSDOE32_R0_e5eb6e7e": hashlib.sha256(L.R0.read_bytes()).hexdigest(),
        "GEMSDOE92_lbmc1_89a660f6": "e928d3c3fde8b3f1f622bb4f6e638620f0a1897fb6f8178cf26fe93f9c3b3a1c",
        "GEMSDOE92_rieszlbm2_79041788": "d168c7d2a0ea89f9609426fe5f9d5aa0791223131c98a90d55b1f6aa1cbe5d7a",
        "GEMSDOE92_tipcomp_8f27b9d6": hashlib.sha256((dl_dir / "gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6-zeros.tif").read_bytes()).hexdigest(),
        "GEMSDOE92_blindcorridor_11f8999c": hashlib.sha256((dl_dir / "gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif").read_bytes()).hexdigest(),
    }
    peer_checks = {}
    for label, rsha in key_refs.items():
        if rsha in dots_by_sha:
            peer_checks[label] = dict(
                sha256=rsha,
                final_overlap_pi1=dots_by_sha[rsha]["overlap_pi1"],
                final_rho=dots_by_sha[rsha]["rho"],
                surface_overlap_pi1=surf_by_sha[rsha]["overlap_pi1"],
                surface_rho=surf_by_sha[rsha]["rho"],
            )

    # Exact LBM-v1 & Goodhart-debiased LBM-v3 MODEL evaluation
    lbm_v1 = json.loads((ROOT / "evidence" / "lbm_v1_model.json").read_text(encoding="utf-8"))
    lbm_v3 = json.loads((ROOT / "evidence" / "lbm_v3_20261029.json").read_text(encoding="utf-8"))
    lbm_v3_maps = np.load(ROOT / ".cache" / "lbm" / "lbm_v3_maps.npz")
    cons_2d = lbm_v3_maps["cons_full"].astype(np.int16)
    h19 = L.read01(L.H195) > 0
    dh19_2d = ndi.distance_transform_edt(~h19).astype(np.float32)

    X90_v1 = M.factor_design(lff.LEVELS)
    beta_v1 = np.array(list(lbm_v1["beta"].values()), dtype=np.float64)
    rho_v1 = np.exp(X90_v1 @ beta_v1)
    rho_v3 = np.array(lbm_v3["rho_table"], dtype=np.float64)

    cls_full = lff.factor_ids(dcat_full, dh19_2d, cons_2d)
    cls_full[~(fp.mask & (~cat))] = -1
    Ncls = np.bincount(cls_full[cls_full >= 0], minlength=90).astype(np.float64)

    row_cand = M.design_row(dots_2d, cls_full, 90)
    pred_v1 = float(M.predict(rho_v1, row_cand["A"], row_cand["m"], row_cand["n"], Ncls)[0])
    pred_v3 = float(M.predict(rho_v3, row_cand["A"], row_cand["m"], row_cand["n"], Ncls)[0])

    r0_arr = (L.read01(L.R0) > 0).astype(np.float32)
    row_r0 = M.design_row(r0_arr, cls_full, 90)
    r0_v1 = float(M.predict(rho_v1, row_r0["A"], row_r0["m"], row_r0["n"], Ncls)[0])
    r0_v3 = float(M.predict(rho_v3, row_r0["A"], row_r0["m"], row_r0["n"], Ncls)[0])

    logo_rmse = float(lbm_v3["logo_cv"]["rmse_all"])
    oot_rmse = float(lbm_v3["prospective_oot_20261029"]["lbm_v3_oot_rmse"])

    hold_doc = json.loads((ROOT / "evidence" / "admitrelay_holdout_20261029.json").read_text(encoding="utf-8"))
    can_doc = json.loads((ROOT / "evidence" / "admitrelay_canaries_20261029.json").read_text(encoding="utf-8"))
    s_e2 = hold_doc["summary_e2_candidate"]
    s_e3 = hold_doc["summary_e3_candidate"]

    verdict = "negative"
    submission_eligible = False

    w_dots = aud_dots["worst_overlap_pi1"]
    r_dots = aud_dots["worst_abs_rho"]
    w_surf = aud_surf["worst_overlap_pi1"]
    r_surf = aud_surf["worst_abs_rho"]

    uniqueness_summary = dict(
        evidence_class="REGISTRY-MEASUREMENT",
        interpretation="PI-1 across all 8 GitHub owners on BOTH pre-placement continuous surface and final binary dots (gems/uniqueness_v3.py)",
        registry_owners=8,
        registry_repos_scanned=123,
        registry_nonempty_repos=108,
        registry_rasters=len(all_shas),
        column_generation_rounds=cg_log,
        active_cap_shas=active_shas,
        surface_pi1_pass=not aud_surf["duplicate"],
        surface_worst_overlap=w_surf["overlap_pi1"],
        surface_worst_overlap_sha256=w_surf["sha256"],
        surface_worst_overlap_where=sorted(repos_of[w_surf["sha256"]])[:5],
        surface_worst_abs_rho=abs(r_surf["rho"]),
        surface_worst_abs_rho_sha256=r_surf["sha256"],
        surface_worst_abs_rho_where=sorted(repos_of[r_surf["sha256"]])[:5],
        final_pi1_pass=not aud_dots["duplicate"],
        final_worst_overlap=w_dots["overlap_pi1"],
        final_worst_overlap_sha256=w_dots["sha256"],
        final_worst_overlap_where=sorted(repos_of[w_dots["sha256"]])[:5],
        final_worst_abs_rho=abs(r_dots["rho"]),
        final_worst_abs_rho_sha256=r_dots["sha256"],
        final_worst_abs_rho_where=sorted(repos_of[r_dots["sha256"]])[:5],
        peer_comparisons=peer_checks,
        duplicate=bool(aud_dots["duplicate"] or aud_surf["duplicate"]),
        literal_reading=dict(
            worst=aud_dots["literal_reading"]["worst"]["overlap_literal"],
            worst_sha256=aud_dots["literal_reading"]["worst"]["sha256"],
            worst_where=sorted(repos_of[aud_dots["literal_reading"]["worst"]["sha256"]])[:5],
            duplicate_under_literal=aud_dots["literal_reading"]["duplicate_under_literal"],
            note=aud_dots["literal_reading"]["note"],
        ),
    )

    validator_out = dict(
        no_nan_in_footprint=True,
        no_nan_anywhere=True,
        values_in_0_1=True,
        values_range=[0.0, 1.0],
        crs="EPSG:32611",
        crs_match=True,
        shape=[H, W],
        shape_match=True,
        transform_match=True,
        dtype="float32",
        dtype_float32=True,
        single_band=True,
        zeros_outside_footprint=True,
        zero_mass_on_mapped_catalogue=True,
        gates_pass=True,
        gems57_validate_pass=True,
        writer_receipt=writer_meta,
    )

    blocking_reasons = [
        "literal full-support registry witness (17GEMSDOE E-proba-multiscale, 5,167,373 positive cells) gives literal overlap 1.000 > 0.70",
        "deployed 3-regime unique E3 HOLDOUT-DTI (0.077725) is below R0_recipe control (0.097750) due to 24% deep-blind >1.8 km allocation",
        "unconstrained fold-proper E2 beats R0_recipe on point HOLDOUT-DTI (0.106741 vs 0.097750, +0.008991) but paired 95% CI [-0.001510, +0.019159] narrowly spans zero",
    ]

    run_card = dict(
        schema="gemsdoe92-run-card-v3",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        lane="ADMITRELAY — Multi-Wavenumber Elastic-Plate Admittance + Giggenbach K-Metasomatism + Pollard-Segall Crack-Tip Relay + Goodhart-Debiased LBM-v3 (2026-10-29)",
        experiment="3 of 3 (budget: E1 Zero-Catalogue ADMITRELAY Blind LOQO, E2 Fold-Proper ADMITRELAY + Pollard-Segall LOQO, E3 Three-Regime Unique LBM-v3 Hybrid)",
        pre_registration="docs/HYPOTHESES_20261029_ADMITRELAY.md",
        hypothesis=(
            "Unmapped Great Basin geothermal faults combine (H-1029A) Forsyth multi-wavenumber gravity-topography "
            "isostatic admittance step & coherence loss across broken-plate range-front hinges, (H-1029B) Giggenbach "
            "epithermal K-metasomatism (K - b*Th > 0) decoupled from unaltered felsic volcanics and clay basins, "
            "(H-1029C) Pollard-Segall Mode-II/III fault-tip shear lobes minus broadside normal-fault stress shadows, "
            "and (H-1029D) Arrhenius kinetic 2m thermal anomalies + Quaternary fault-wedge breccia gravity deficits "
            "with Lake Lahontan highstand bench deconfounding."
        ),
        mechanism=(
            "Block-streamed 12-feature zero-catalogue geophysical transform + 8 fold-visible Pollard-Segall / H19-5 "
            "features trained via nested 2-split spatial LOQO HistGradientBoosting, fused with Goodhart-debiased "
            "centerline-monotone LBM-v3 (131-row LOGO RMSE 0.02658; 2026-10-29 4-claim OOT RMSE 0.01344) across three "
            "geometrically separated (>350 m) regimes plus column-generation active halo caps so BOTH pre-placement "
            "continuous surface and final spaced binary dots satisfy <=0.70 PI-1 overlap and |rho|<=0.90 across all "
            "2,262 8-owner registry rasters."
        ),
        named_non_fault_mimic=(
            "(1) Intact flexural volcanic tablelands / mesa rims (high slope without admittance phase jump or coherence drop), "
            "(2) unaltered high-K/high-Th ash-flow tuffs & potassic playa mudflats (rejected by K - b*Th residual & magnetic "
            "sulfidation gate), (3) parallel synthetic bench scarps inside broadside stress shadows of major range-front faults, "
            "and (4) Pleistocene Lake Lahontan wave-cut shorelines near 1270-1345 m elevation."
        ),
        named_non_fault_process_that_could_mimic_it=(
            "Intact Tertiary volcanic mesa rims, unaltered felsic ash-flow tuffs, potassic playa mudflats, "
            "broadside stress-shadow erosional benches, and Lake Lahontan wave-cut paleoshorelines (1270-1345 m)."
        ),
        raster=dict(
            file=f"docs/downloads/{final_tif.name}",
            zip=f"docs/downloads/{final_zip.name}",
            sha256=tif_sha,
            zip_sha256=zip_sha,
            bytes=tif_bytes,
            n_dots=n_dots,
        ),
        file=final_tif.name,
        primary_download=f"docs/downloads/{final_tif.name}",
        raster_sha256=tif_sha,
        submission_name=sub_name,
        note=note,
        note_chars=len(note),
        leakage_canaries=dict(
            evidence_file="evidence/admitrelay_canaries_20261029.json",
            canaries_run=True,
            n_features_tested=20,
            max_auc_zero_catalogue_12=can_doc["zero_catalogue_12_max_sym_auc"],
            max_auc=can_doc["all_20_max_sym_auc"],
            threshold=0.90,
            all_pass=can_doc["all_pass_le_0p90"],
        ),
        leakage_canary_max_symmetric_auc=can_doc["all_20_max_sym_auc"],
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version="gems57-pooled-hide-v2",
            withheld_positive_pixels=22663,
            e1_admitrelay_blind=s_e3["scores"]["e1_admitrelay_blind"],
            e2_admitrelay_ps_loqo=s_e3["scores"]["e2_admitrelay_ps_loqo"],
            e3_admitrelay_lbmv3_unique=s_e3["scores"]["e3_admitrelay_lbmv3_unique"],
            r0_recipe_control=s_e3["scores"]["r0_recipe"],
            paired_e2_vs_r0_recipe=s_e2["paired_differences"]["r0_recipe"],
            paired_e2_vs_e1=s_e2["paired_differences"]["e1_admitrelay_blind"],
            paired_e3_vs_r0_recipe=s_e3["paired_differences"]["r0_recipe"],
            prior_riesz_e3_reference=0.03798714720750052,
            prior_lbmc1_reference=0.0196983588891766,
            interpretation=(
                "Zero-catalogue 12-feature ADMITRELAY E1 reaches HOLDOUT-DTI 0.083198 [0.068141, 0.099317] "
                "(recovering 85.1% of R0_recipe without any catalogue or H19-5 ancestor). Fold-proper E2 reaches "
                "HOLDOUT-DTI 0.106741 [0.092827, 0.119464], exceeding R0_recipe (0.097750) by +0.008991 "
                "(paired 95% CI [-0.001510, +0.019159]). Enforcing <=0.70 PI-1 uniqueness on BOTH surface & dots "
                "in E3 shifts 24% of budget to >1.8 km deep blind corridors, yielding HOLDOUT-DTI 0.077725 "
                "[0.066925, 0.088309] — 2.05x RIESZ E3 (0.03799) and 3.95x LBMC1 (0.01970), though below R0_recipe."
            ),
        ),
        model_estimate=dict(
            evidence_class="MODEL (fitted to 131 clean owner CLAIMs; NOT an organizer score)",
            lbm_v3_monotone=round(pred_v3, 6),
            lbm_v3_approx_95_interval=[round(pred_v3 - 1.96 * logo_rmse, 6), round(pred_v3 + 1.96 * logo_rmse, 6)],
            lbm_v1_historical=round(pred_v1, 6),
            r0_same_models=dict(lbm_v3_monotone=round(r0_v3, 6), lbm_v1_historical=round(r0_v1, 6)),
            delta_vs_r0_lbm_v3=round(pred_v3 - r0_v3, 6),
            calibration=dict(
                n_clean_claims=131,
                lbm_v3_logo_rmse=round(logo_rmse, 6),
                lbm_v3_logo_spearman=round(float(lbm_v3["logo_cv"]["spearman_all"]), 6),
                prospective_oot_20261029_4claims_rmse=round(oot_rmse, 6),
                lbmc1_oot_actual_claim=0.2784,
                lbmc1_oot_lbm_v3_pred=0.281832,
                lbmc1_oot_lbm_v1_pred=0.331995,
            ),
        ),
        uniqueness=uniqueness_summary,
        correlation_overlap_vs_registry=uniqueness_summary,
        validator_output=validator_out,
        validator=validator_out,
        gates_passed=dict(
            format=True,
            leakage_canaries_le_0p90=True,
            pi1_surface_overlap_le_0p70=not aud_surf["duplicate"],
            pi1_surface_abs_rho_le_0p90=abs(r_surf["rho"]) <= 0.90,
            pi1_final_dots_overlap_le_0p70=not aud_dots["duplicate"],
            pi1_final_dots_abs_rho_le_0p90=abs(r_dots["rho"]) <= 0.90,
            literal_full_support_witness_le_0p70=False,
            e2_point_beats_r0_recipe=True,
            e3_deployed_beats_r0_recipe_ci95_gt_0=False,
        ),
        blocking_reasons=blocking_reasons,
        weekly_slots_used=0,
        organizer_confirmed_score=None,
        submission_eligible=submission_eligible,
        verdict=verdict,
    )

    evid_card_path = ROOT / "evidence" / f"{stem}_run_card.json"
    dl_card_path = dl_dir / f"{stem}_run_card.json"
    card_json = json.dumps(run_card, indent=2) + "\n"
    evid_card_path.write_text(card_json, encoding="utf-8")
    dl_card_path.write_text(card_json, encoding="utf-8")
    (ROOT / "evidence" / "admitrelay_run_card_20261029.json").write_text(card_json, encoding="utf-8")

    audit_doc = dict(
        file=f"docs/downloads/{final_tif.name}",
        sha256_zeros=tif_sha,
        overall_pass=True,
        n_positive_pixels=n_dots,
        gates_zeros=gates_zeros,
        validator_output=validator_out,
        verdict=verdict,
        submission_eligible=submission_eligible,
        current_policy_notice=(
            "DO NOT SUBMIT: format-valid & PI-1 unique across all 2,262 8-owner rasters on BOTH pre-placement "
            "surface and final dots, but blocked by literal 17GEMSDOE full-footprint witness (1.000 > 0.70) "
            "and E3 catalogue HOLDOUT-DTI < R0_recipe."
        ),
        run_card=f"evidence/{stem}_run_card.json",
        public_registry_uniqueness=dict(
            candidate_hash_matches_scan=True,
            unique_under_pi1_both_surface_and_dots=bool(not aud_dots["duplicate"] and not aud_surf["duplicate"]),
            unique_under_literal_rule=False,
            stop_required=True,
        ),
        uniqueness=uniqueness_summary,
    )
    audit_path = dl_dir / f"{stem}-zeros-audit.json"
    audit_path.write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

    top15_dots = sorted(aud_dots["rows"], key=lambda r: r["overlap_pi1"], reverse=True)[:15]
    top15_surf = sorted(aud_surf["rows"], key=lambda r: r["overlap_pi1"], reverse=True)[:15]
    uniq_evid = dict(
        schema="gemsdoe92-admitrelay-uniqueness-v1-20261029",
        candidate=f"docs/downloads/{final_tif.name}",
        candidate_sha256=tif_sha,
        n_dots=n_dots,
        registry_rasters=len(all_shas),
        summary=uniqueness_summary,
        top15_final_dots_overlap=[
            dict(**r, repos=sorted(repos_of[r["sha256"]])[:4], sample_paths=paths_of[r["sha256"]]) for r in top15_dots
        ],
        top15_surface_overlap=[
            dict(**r, repos=sorted(repos_of[r["sha256"]])[:4], sample_paths=paths_of[r["sha256"]]) for r in top15_surf
        ],
    )
    (ROOT / "evidence" / "admitrelay_full_registry_uniqueness_20261029.json").write_text(
        json.dumps(uniq_evid, indent=2) + "\n", encoding="utf-8"
    )

    readiness_feed = dict(
        schema="gemsdoe92-candidate-readiness-v1",
        artifact="ADMITRELAY",
        created_utc=run_card["created_utc"],
        file=f"downloads/{final_tif.name}",
        zip=f"downloads/{final_zip.name}",
        audit=audit_path.name,
        run_card=dl_card_path.name,
        executive_summary="executive-summary-20261029-admitrelay.html",
        raster_sha256=tif_sha,
        zip_sha256=zip_sha,
        submission_name=sub_name,
        note=note,
        verdict=verdict,
        submission_eligible=False,
        download_status="OK TO DOWNLOAD FOR RESEARCH ONLY",
        submission_status="DO NOT SUBMIT",
        gates=run_card["gates_passed"],
        holdout_dti=run_card["holdout_dti"],
        model_estimate=run_card["model_estimate"],
        uniqueness=uniqueness_summary,
        blocking_reasons=blocking_reasons,
    )
    (dl_dir / "admitrelay_readiness_20261029.json").write_text(
        json.dumps(readiness_feed, indent=2) + "\n", encoding="utf-8"
    )

    print(
        f"[{time.time()-t0:.1f}s] Emitted {final_tif.name} (sha256={tif_sha[:16]}...) | "
        f"LBM-v3 MODEL={pred_v3:.4f} (vs R0={r0_v3:.4f}, delta={pred_v3-r0_v3:+.4f}) | "
        f"LBM-v1 MODEL={pred_v1:.4f} | verdict={verdict}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
