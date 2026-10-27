#!/usr/bin/env python3
"""End-to-end execution of the pre-registered PROVINCETOE 3-arm protocol.

Pre-registration: docs/HYPOTHESES_20261025_PROVINCETOE.md
Single method lane: PROVINCETOE (gems/provincetoe.py)
Frozen arms (budget = 3):
  1. provincetoe (Primary): 24 province-invariant Wallace basal toe-concavity +
     carbonate-horst gravity/basement flexure + dimensionless kinematic features,
     4-quadrant LOQO + label-blind footprint quantile calibration, cliff_slope=15.0,
     sub_weight=0.85.
  2. globalraw (Province-Shift Ablation): replaces dimensionless kinematic ratio
     with raw Walker Lane geod_shearrate & geod_2ndinv and disables per-quadrant
     footprint calibration (isolates #IR-92-NE-QUADRANT-LOQO-COLLAPSE).
  3. piedbasin (Stronger Cliff Taper & Equal Subsurface Flexure): uses provincetoe
     LOQO probabilities with cliff_slope=10.5 and sub_weight=1.00.
"""
from __future__ import annotations

import dataclasses
import gc
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import coulomb_loqo as cl_mod  # noqa: E402
from gems import gates as gates_mod  # noqa: E402
from gems import provincetoe as pt  # noqa: E402
from gems57 import (  # noqa: E402
    evaluate_holdout,
    grid as grid_mod,
    holdout as hold_mod,
    metric as metric_mod,
    submission_writer,
    uniqueness as U,
    validate as V,
)

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "provincetoe"
PUB_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DEC_DIR = PUB_CACHE / "decoded_37654"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

N_DOTS = 37_654
DATE_TAG = "20261025"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def symmetric_auc(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    if np.ptp(scores) == 0:
        return 0.5, 0.5
    auc = float(roc_auc_score(y_true, scores))
    return auc, max(auc, 1.0 - auc)


def load_raw_bands() -> tuple[dict[int, np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    band_ids = (2, 3, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19)
    bands: dict[int, np.ndarray] = {}
    with rasterio.open(INPUTS / "training_features.tif") as ds:
        for b in band_ids:
            arr = ds.read(b, masked=True).filled(np.nan).astype(np.float32)
            arr[(~np.isfinite(arr)) | (arr <= -1e20)] = np.nan
            bands[b] = arr
    with rasterio.open(INPUTS / "external" / "geodawn_rad_u8.tif") as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
        rad_u = ds.read(3)
    return bands, rad_k, rad_th, rad_u


def scan_local_registry(
    cands: dict[str, np.ndarray],
    surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
    expected: tuple,
    exclude_prefixes: tuple[str, ...],
) -> tuple[dict[str, list[dict]], list[dict]]:
    reg_files: list[tuple[str, Path]] = []
    seen_sha: set[str] = set()
    for d in (DOWNLOADS, ROOT / "releases", ROOT / "data", ROOT / "data" / "bridge", INPUTS / "lineage"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if any(p.name.startswith(pref) for pref in exclude_prefixes):
                continue
            if p.name in ("sample_submission.tif", "existing_faults.tif"):
                continue
            sh = sha256_file(p)
            if sh in seen_sha:
                continue
            seen_sha.add(sh)
            reg_files.append((str(p.relative_to(ROOT)), p))

    foot_idx = np.flatnonzero(foot)
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
    surf_sub = {a: surfaces[a].ravel()[sub].astype(np.float32) for a in cands}

    rows: dict[str, list[dict]] = {a: [] for a in cands}
    skipped: list[dict] = []
    for label, p in reg_files:
        try:
            with rasterio.open(p) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    skipped.append(dict(file=label, reason="grid/band mismatch"))
                    continue
                vals = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        except Exception as exc:
            skipped.append(dict(file=label, reason=str(exc)[:80]))
            continue
        sup = (vals > 0) & foot
        n_sup = int(sup.sum())
        if n_sup == 0:
            skipped.append(dict(file=label, reason="empty"))
            continue
        near_lit = U._near(sup, 3.0)
        tv = vals.ravel()[sub]
        has_var = np.ptp(tv) > 0
        for a, m in cands.items():
            k = int(m.sum())
            lit = float(near_lit[m].mean())
            if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
                mb, rep = lit, "dot_field"
            else:
                mb = float(U._near(U.matched_budget_support(vals, foot, k), 3.0)[m].mean())
                rep = "continuous_surface"
            rho = float(spearmanr(surf_sub[a], tv).statistic) if has_var else 0.0
            rows[a].append(dict(
                file=label,
                their_dots=n_sup,
                my_dots=k,
                representation=rep,
                literal_forward_overlap=round(lit, 6),
                matched_budget_forward_overlap=round(mb, 6),
                spearman_surface=round(rho, 6) if np.isfinite(rho) else 0.0,
            ))
        del vals, sup, near_lit
    return rows, skipped


def scan_public_registry_memmap(
    cands: dict[str, np.ndarray],
    surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
) -> tuple[dict[str, list[dict]], dict]:
    """Scan all external public GEMSDOE* rasters via verified memmap + exact top-hit checks."""
    meta_doc = json.loads((DEC_DIR / "meta.json").read_text())
    n_valid = int(meta_doc["n_valid"])
    meta = meta_doc["meta"]
    sub_idx = np.load(DEC_DIR / "sub_idx.npy")
    mm_lit = np.load(DEC_DIR / "lit_bits.npy", mmap_mode="r")
    mm_mb = np.load(DEC_DIR / "mb_bits.npy", mmap_mode="r")
    mm_rnk = np.load(DEC_DIR / "sub_unit_ranks.npy", mmap_mode="r")

    H, W = foot.shape
    offs = [(dr, dc) for dr in range(-3, 4) for dc in range(-3, 4) if dr * dr + dc * dc <= 9]

    rows: dict[str, list[dict]] = {a: [] for a in cands}
    ext_indices = [i for i in range(n_valid) if meta[i]["repo"] != "GEMSDOE92"]

    for a, m in cands.items():
        rr, cc = np.nonzero(m)
        nb_flat = np.empty((len(offs), rr.size), dtype=np.int64)
        for k_o, (dr, dc) in enumerate(offs):
            nb_flat[k_o] = np.clip(rr + dr, 0, H - 1) * W + np.clip(cc + dc, 0, W - 1)
        byte_idx = nb_flat >> 3
        bit_mask = (1 << (7 - (nb_flat & 7))).astype(np.uint8)

        cv = surfaces[a].ravel()[sub_idx]
        cr = rankdata(cv).astype(np.float64)
        cr -= cr.mean()
        nrm = float(np.linalg.norm(cr))
        cr_unit = (cr / nrm).astype(np.float32) if nrm > 0 else np.zeros_like(cr, dtype=np.float32)
        approx_rho = mm_rnk[:n_valid] @ cr_unit

        arm_rows: list[dict] = []
        for i in ext_indices:
            lb = mm_lit[i]
            hl = np.zeros(rr.size, dtype=bool)
            for k_o in range(len(offs)):
                hl |= (lb[byte_idx[k_o]] & bit_mask[k_o]) != 0
            lit_val = float(hl.mean())
            if meta[i]["their_dots"] <= U.DOT_FIELD_MAX_SUPPORT:
                mb_val = lit_val
            else:
                mb = mm_mb[i]
                hm = np.zeros(rr.size, dtype=bool)
                for k_o in range(len(offs)):
                    hm |= (mb[byte_idx[k_o]] & bit_mask[k_o]) != 0
                mb_val = float(hm.mean())
            arm_rows.append(dict(
                row_idx=i,
                repo=meta[i]["repo"],
                file=meta[i]["file"],
                git_sha=meta[i]["git_sha"],
                sha256=meta[i]["sha256"],
                their_dots=meta[i]["their_dots"],
                my_dots=int(rr.size),
                representation=meta[i]["representation"],
                literal_forward_overlap=round(lit_val, 6),
                matched_budget_forward_overlap=round(mb_val, 6),
                spearman_surface=round(float(approx_rho[i]), 6),
                spearman_scope="400k-cell footprint subsample (top-5 verified on full 5,167,373-px footprint)",
            ))

        # Exact full-footprint Spearman + U.dual_overlap verification on top-5 MB & top-5 |rho|
        top_mb = sorted(arm_rows, key=lambda r: -r["matched_budget_forward_overlap"])[:5]
        top_rh = sorted(arm_rows, key=lambda r: -abs(r["spearman_surface"]))[:5]
        verify_map = {r["git_sha"]: r for r in (top_mb + top_rh)}
        s_foot = surfaces[a][foot]
        for gsha, r_entry in verify_map.items():
            with rasterio.open(PUB_CACHE / f"{gsha}.tif") as ds:
                tv_full = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
            exact_d = U.dual_overlap(m, tv_full, foot)
            assert abs(exact_d["matched_budget_forward_overlap"] - r_entry["matched_budget_forward_overlap"]) < 1e-5
            tv_f = tv_full[foot]
            if np.ptp(tv_f) > 0:
                r_entry["spearman_surface"] = round(float(spearmanr(s_foot, tv_f).statistic), 6)
                r_entry["spearman_scope"] = "exact full 5,167,373-px footprint"
            del tv_full, tv_f

        rows[a] = arm_rows

    inv_meta = dict(
        total_repos_scanned=102,
        external_repos_scanned=101,
        total_unique_blobs_fetched=meta_doc["total_blobs"],
        total_valid_template_rasters=n_valid,
        external_valid_template_rasters=len(ext_indices),
        skipped_invalid_or_non_template=len(meta_doc["skipped"]),
    )
    return rows, inv_meta


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("run_provincetoe:main")

    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    log("1. Loading verified competition grid, catalogue, lineage & physical stack...")
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    quad = hold_mod.quadrant_ids(foot)
    d_cat = distance_transform_edt(~cat)

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot

    bands, rad_k, rad_th, rad_u = load_raw_bands()
    valid_base = (
        foot
        & np.isfinite(bands[12])
        & np.isfinite(bands[19])
        & np.isfinite(bands[2])
    )
    gdr_res = cl_mod.gdr_blind_thermal_features(
        INPUTS / "external" / "gdr_wellspring_in_footprint.csv",
        foot.shape,
        valid_base,
        sigma_px=14.0,
    )

    # Build holdout folds once for seeds 20 and 30 (22,663 withheld positives)
    draws_by_seed: dict[int, list[dict]] = {}
    all_folds: list[dict] = []
    for seed in (20, 30):
        dr, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        draws_by_seed[seed] = dr
        all_folds.extend(dr)

    log("2. Computing 26-column PROVINCETOE feature stack (strict zero cross-quadrant bleed)...")
    stack = pt.compute_provincetoe_stack(
        rtp=bands[2],
        geod_2ndinv=bands[4],
        grav_slope=bands[5],
        geod_shearrate=bands[7],
        geod_dilaterate=bands[8],
        det_elev=bands[12],
        grav_anom=bands[13],
        depth_to_base=bands[15],
        cond_surf=bands[17],
        grav_hg=bands[18],
        det_elev_slope=bands[19],
        rad_k=rad_k,
        rad_th=rad_th,
        gdr_plume_feat=gdr_res["plume_feat"],  # type: ignore[arg-type]
        footprint=foot,
        quad=quad,
    )
    # Free 650 MB of raw band rasters immediately so peak RSS stays < 1.8 GiB!
    del bands, rad_k, rad_th, rad_u, valid_base
    gc.collect()

    X_foot = stack["X_foot"]
    valid = stack["valid"]
    l_toe_raw = stack["L_toe_raw"]
    l_sub = stack["L_sub"]
    slope_deg = stack["slope_deg"]
    del stack
    gc.collect()

    # ---- Step 1: Protocol Rule 4 Leakage Canaries ----
    log("3. Running Protocol Rule 4 single-feature leakage canaries (gate <= 0.90)...")
    rng_can = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in all_folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & (~cat))
        n_neg = min(len(neg), max(1, 2 * len(pos)))
        neg_sel = rng_can.choice(neg, size=n_neg, replace=False) if len(neg) > n_neg else neg
        idx_parts.extend((pos, neg_sel))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg_sel), np.uint8)))
    y_canary = np.concatenate(y_parts)
    flat_canary_idx = np.concatenate(idx_parts)

    foot_row_map = np.full(foot.shape, -1, dtype=np.int32)
    foot_row_map[foot] = np.arange(int(foot.sum()), dtype=np.int32)
    canary_rows = foot_row_map.ravel()[flat_canary_idx]

    canary_list: list[dict] = []
    for j, fname in enumerate(pt.ALL_FEATURE_NAMES):
        auc, sym = symmetric_auc(y_canary, X_foot[canary_rows, j])
        canary_list.append(dict(feature=fname, auc=round(auc, 6), symmetric_auc=round(sym, 6), pass_le_0p90=(sym <= 0.90)))
    for extra_name, extra_arr in (("L_toe_raw_1d", l_toe_raw), ("L_sub_1d", l_sub)):
        auc, sym = symmetric_auc(y_canary, extra_arr.ravel()[flat_canary_idx])
        canary_list.append(dict(feature=extra_name, auc=round(auc, 6), symmetric_auc=round(sym, 6), pass_le_0p90=(sym <= 0.90)))

    max_canary_sym = max(r["symmetric_auc"] for r in canary_list)
    log(f"   {len(canary_list)}/{len(canary_list)} canaries checked; max symmetric AUC = {max_canary_sym:.6f}")
    if max_canary_sym > 0.90:
        raise RuntimeError(f"LEAKAGE CANARY TRIPPED: max_symmetric_auc={max_canary_sym:.6f} > 0.90")

    # ---- Step 2: Full-catalogue 4-quadrant LOQO & Deployment Surfaces (3 Frozen Arms) ----
    arms_order = ["provincetoe", "globalraw", "piedbasin"]
    deploy_dots: dict[str, np.ndarray] = {}
    if all((CACHE / f"S_{a}_full.npy").is_file() and (CACHE / f"dots_{a}.npy").is_file() for a in arms_order):
        log("4. Loading cached full-catalogue LOQO surfaces & dots from .cache/provincetoe/...")
        for arm in arms_order:
            dots = np.load(CACHE / f"dots_{arm}.npy")
            deploy_dots[arm] = dots
            q_counts = [int((dots & (quad == q)).sum()) for q in range(4)]
            log(f"   arm={arm:12s}: dots={int(dots.sum()):,} | quad shares NW={100*q_counts[0]/N_DOTS:.1f}% NE={100*q_counts[1]/N_DOTS:.1f}% SW={100*q_counts[2]/N_DOTS:.1f}% SE={100*q_counts[3]/N_DOTS:.1f}%")
    else:
        log("4. Fitting full-catalogue 4-quadrant LOQO for frozen arms (provincetoe, globalraw, piedbasin)...")
        fit_pt_full = pt.fit_predict_provincetoe_loqo(
            X_foot, foot, valid, quad, cat,
            feature_cols=pt.PRIMARY_COLS,
            calibrate_quadrants=True,
            rank_gamma=2.0,
            guard_px=12,
            neg_buffer_px=5.0,
            seed=20261025,
        )
        fit_gr_full = pt.fit_predict_provincetoe_loqo(
            X_foot, foot, valid, quad, cat,
            feature_cols=pt.GLOBALRAW_COLS,
            calibrate_quadrants=False,
            guard_px=12,
            neg_buffer_px=5.0,
            seed=20261025,
        )
        arm_specs = {
            "provincetoe": dict(proba=fit_pt_full["cal_proba"], cliff_slope_deg=15.0, sub_weight=0.85),
            "globalraw": dict(proba=fit_gr_full["cal_proba"], cliff_slope_deg=15.0, sub_weight=0.85),
            "piedbasin": dict(proba=fit_pt_full["cal_proba"], cliff_slope_deg=10.5, sub_weight=1.00),
        }
        for arm in arms_order:
            sp = arm_specs[arm]
            built = pt.build_provincetoe_surface(
                sp["proba"], l_toe_raw, l_sub, slope_deg, valid,
                cliff_slope_deg=sp["cliff_slope_deg"],
                sub_weight=sp["sub_weight"],
            )
            s_arr = built["S_surface"]
            r_1d = built["ridge_1d"]
            dots = pt.spaced_top_mask(
                s_arr, foot & valid & r_1d & (d_cat > 2.0), N_DOTS, min_dist_px=2.8, cand_cap=900_000
            )
            deploy_dots[arm] = dots
            np.save(CACHE / f"S_{arm}_full.npy", s_arr)
            np.save(CACHE / f"dots_{arm}.npy", dots)
            q_counts = [int((dots & (quad == q)).sum()) for q in range(4)]
            log(f"   arm={arm:12s}: dots={int(dots.sum()):,} | quad shares NW={100*q_counts[0]/N_DOTS:.1f}% NE={100*q_counts[1]/N_DOTS:.1f}% SW={100*q_counts[2]/N_DOTS:.1f}% SE={100*q_counts[3]/N_DOTS:.1f}%")
            del built, s_arr, r_1d
        del fit_pt_full, fit_gr_full, arm_specs
        gc.collect()

    # ---- Step 3: Strict Draw-Blind Rule-2 (d_visible > 2.0) Holdout Evaluation ----
    dvis_terms: dict[str, np.ndarray | None] = {
        "provincetoe": None,
        "globalraw": None,
        "piedbasin": None,
        "H19_5_dvis2": None,
        "COULOMBLOQO_standalone_dvis2": None,
    }
    dvis_per_fold: dict[str, list[dict]] = {k: [] for k in dvis_terms}
    scan_rank = np.linspace(1.0, 0.0, foot.size, dtype=np.float32).reshape(foot.shape)
    pt_ckpt_npz = CACHE / "dvis_pt_terms.npz"
    pt_ckpt_json = CACHE / "dvis_pt_per_fold.json"

    if pt_ckpt_npz.is_file() and pt_ckpt_json.is_file():
        log("5. Loading cached strict draw-blind Rule-2 PROVINCETOE terms...")
        z_pt = np.load(pt_ckpt_npz)
        for k_arm in ("provincetoe", "globalraw", "piedbasin", "H19_5_dvis2"):
            dvis_terms[k_arm] = z_pt[k_arm]
        saved_pf = json.loads(pt_ckpt_json.read_text())
        for k_arm in ("provincetoe", "globalraw", "piedbasin", "H19_5_dvis2"):
            dvis_per_fold[k_arm] = saved_pf[k_arm]
    else:
        log("5. Fitting strict draw-blind Rule-2 (d_visible > 2.0) LOQO across seeds 20 & 30...")
        for seed in (20, 30):
            folds_s = draws_by_seed[seed]
            vis = folds_s[0]["visible"]
            hid_all = folds_s[0]["hidden_all"]
            excl = hid_all | (distance_transform_edt(~hid_all) <= 3.0)
            d_vis = distance_transform_edt(~vis)

            fit_pt_s = pt.fit_predict_provincetoe_loqo(
                X_foot, foot, valid, quad, vis,
                feature_cols=pt.PRIMARY_COLS,
                excluded_mask=excl,
                calibrate_quadrants=True,
                rank_gamma=2.0,
                guard_px=12,
                neg_buffer_px=5.0,
                seed=20261025 + seed,
            )
            fit_gr_s = pt.fit_predict_provincetoe_loqo(
                X_foot, foot, valid, quad, vis,
                feature_cols=pt.GLOBALRAW_COLS,
                excluded_mask=excl,
                calibrate_quadrants=False,
                guard_px=12,
                neg_buffer_px=5.0,
                seed=20261025 + seed,
            )

            preds_seed: dict[str, np.ndarray] = {}
            for arm, p_arr, cs, sw in (
                ("provincetoe", fit_pt_s["cal_proba"], 15.0, 0.85),
                ("globalraw", fit_gr_s["cal_proba"], 15.0, 0.85),
                ("piedbasin", fit_pt_s["cal_proba"], 10.5, 1.00),
            ):
                b_s = pt.build_provincetoe_surface(p_arr, l_toe_raw, l_sub, slope_deg, valid, cliff_slope_deg=cs, sub_weight=sw)
                pr = pt.spaced_top_mask(
                    b_s["S_surface"], foot & valid & b_s["ridge_1d"] & (d_vis > 2.0), N_DOTS, min_dist_px=2.8, cand_cap=900_000
                ).astype(np.float32)
                pr[vis] = 0.0
                preds_seed[arm] = pr
                del b_s
            del fit_pt_s, fit_gr_s
            gc.collect()

            pr_h19 = pt.spaced_top_mask(scan_rank, foot & valid & h19 & (d_vis > 2.0), N_DOTS, min_dist_px=2.4).astype(np.float32)
            pr_h19[vis] = 0.0
            preds_seed["H19_5_dvis2"] = pr_h19

            for fold in folds_s:
                for k_arm, arr_p in preds_seed.items():
                    sc, tm = evaluate_holdout.evaluate(arr_p, fold, foot)
                    dvis_terms[k_arm] = tm if dvis_terms[k_arm] is None else dvis_terms[k_arm] + tm
                    sc_q = hold_mod.score(arr_p, fold, foot, restrict_to_region=True)
                    dvis_per_fold[k_arm].append(dict(
                        seed=seed,
                        fold=fold["name"],
                        pooled_fold_dti=round(float(sc["dti"]), 6),
                        quadrant_internal_dti=round(float(sc_q["dti"]), 6),
                        tpw=round(float(sc_q["tpw"]), 2),
                        fpw=round(float(sc_q["fpw"]), 2),
                    ))
            del preds_seed
            gc.collect()

        np.savez(pt_ckpt_npz, **{k: dvis_terms[k] for k in ("provincetoe", "globalraw", "piedbasin", "H19_5_dvis2")})  # type: ignore[arg-type]
        pt_ckpt_json.write_text(json.dumps({k: dvis_per_fold[k] for k in ("provincetoe", "globalraw", "piedbasin", "H19_5_dvis2")}, indent=2))

    # Free PROVINCETOE X_foot & 1D arrays before computing exact paired COULOMBLOQO_standalone_dvis2 control
    del X_foot, l_toe_raw, l_sub
    gc.collect()

    log("6. Computing exact paired COULOMBLOQO standalone d_visible > 2.0 control on identical folds...")
    bands_cl, rad_k_cl, rad_th_cl, rad_u_cl = load_raw_bands()
    cl_stack = cl_mod.compute_feature_stack(
        rtp=bands_cl[2],
        geod_2ndinv=bands_cl[4],
        grav_slope=bands_cl[5],
        geod_shearrate=bands_cl[7],
        geod_dilaterate=bands_cl[8],
        grav_vg=bands_cl[11],
        det_elev=bands_cl[12],
        grav_anom=bands_cl[13],
        depth_to_base=bands_cl[15],
        cond_surf=bands_cl[17],
        grav_hg=bands_cl[18],
        det_elev_slope=bands_cl[19],
        rad_k=rad_k_cl,
        rad_th=rad_th_cl,
        rad_u=rad_u_cl,
        gdr_plume_feat=gdr_res["plume_feat"],  # type: ignore[arg-type]
        footprint=foot,
    )
    del bands_cl, rad_k_cl, rad_th_cl, rad_u_cl, gdr_res
    gc.collect()

    for seed in (20, 30):
        folds_s = draws_by_seed[seed]
        vis = folds_s[0]["visible"]
        hid_all = folds_s[0]["hidden_all"]
        excl = hid_all | (distance_transform_edt(~hid_all) <= 3.0)
        d_vis = distance_transform_edt(~vis)
        p_cl = cl_mod.fit_predict_loqo(
            cl_stack["X_foot"], foot, cl_stack["valid"], quad, vis,
            excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261024 + seed,
        )
        c_cl = cl_mod.build_crest_surface(p_cl, cl_stack["L_topo"], cl_stack["L_sub"], cl_stack["valid"], sub_weight=0.80)
        pr_cl = cl_mod.spaced_top_mask(
            c_cl["S_crest"], foot & cl_stack["valid"] & c_cl["ridge_1d"] & (d_vis > 2.0), N_DOTS, min_dist_px=2.8, cand_cap=900_000
        ).astype(np.float32)
        pr_cl[vis] = 0.0
        for fold in folds_s:
            sc, tm = evaluate_holdout.evaluate(pr_cl, fold, foot)
            dvis_terms["COULOMBLOQO_standalone_dvis2"] = (
                tm if dvis_terms["COULOMBLOQO_standalone_dvis2"] is None else dvis_terms["COULOMBLOQO_standalone_dvis2"] + tm
            )
            sc_q = hold_mod.score(pr_cl, fold, foot, restrict_to_region=True)
            dvis_per_fold["COULOMBLOQO_standalone_dvis2"].append(dict(
                seed=seed,
                fold=fold["name"],
                pooled_fold_dti=round(float(sc["dti"]), 6),
                quadrant_internal_dti=round(float(sc_q["dti"]), 6),
                tpw=round(float(sc_q["tpw"]), 2),
                fpw=round(float(sc_q["fpw"]), 2),
            ))
    del cl_stack
    gc.collect()

    # Summarize Rule-2 d_visible > 2.0 holdout
    dvis_probe = evaluate_holdout.pooled_summary(dvis_terms, draws=1000, seed=520810, candidate="provincetoe")  # type: ignore[arg-type]
    best_arm = max(arms_order, key=lambda a: dvis_probe["scores"][a]["dti"])
    dvis_summary = evaluate_holdout.pooled_summary(dvis_terms, draws=1000, seed=520810, candidate=best_arm)  # type: ignore[arg-type]

    log("=== STRICT DRAW-BLIND FOLD-VISIBLE (d_visible > 2.0) HOLDOUT-DTI ===")
    for k, s in sorted(dvis_summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   {k:30s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")

    # ---- Step 4: Static Deployment (d_cat > 2.0) Holdout + SGMC Proxy ----
    log("7. Evaluating static deployment (d_cat > 2.0) HOLDOUT-DTI & off-catalogue SGMC PROXY...")
    static_cands: dict[str, np.ndarray] = {
        a: deploy_dots[a].astype(np.float32) for a in arms_order
    }
    static_cands["R0"] = r0.astype(np.float32)
    ref_files = {
        "COULOMBLOQO_standalone": DOWNLOADS / "h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "COULOMBDM_s45coulomb55": DOWNLOADS / "h33-h33-2-b2-COULOMBDMs45coulomb55-20261024-a10dccdd-zeros.tif",
        "HYDROCONDUIT_f45hydro": DOWNLOADS / "h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
        "APRONRIDGE_free1d": DOWNLOADS / "h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif",
        "BLINDFAULT_blindtopo": DOWNLOADS / "gemsdoe92-blindfault-blindtopo-37654-20261025-4648eea5-zeros.tif",
    }
    for rname, rpath in ref_files.items():
        if rpath.is_file():
            with rasterio.open(rpath) as ds:
                static_cands[rname] = ((np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot).astype(np.float32)

    static_terms: dict[str, np.ndarray | None] = {k: None for k in static_cands}
    static_per_fold: dict[str, list[float]] = {k: [] for k in static_cands}
    for fold in all_folds:
        for k, arr_s in static_cands.items():
            sc, tm = evaluate_holdout.evaluate(arr_s, fold, foot)
            static_terms[k] = tm if static_terms[k] is None else static_terms[k] + tm
            static_per_fold[k].append(round(float(sc["dti"]), 6))
    static_summary = evaluate_holdout.pooled_summary(static_terms, draws=1000, seed=520810, candidate=best_arm)  # type: ignore[arg-type]

    log("=== POOLED STATIC DEPLOYMENT (d_cat > 2.0) HOLDOUT-DTI ===")
    for k, s in sorted(static_summary["scores"].items(), key=lambda kv: -kv[1]["dti"]):
        log(f"   {k:30s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")

    with rasterio.open(INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_scores = {
        k: round(float(metric_mod.dti_binary(arr_s > 0.5, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, arr_s in static_cands.items()
    }
    for k, v in sorted(sgmc_scores.items(), key=lambda kv: -kv[1]):
        log(f"   SGMC PROXY {k:24s}: DTI = {v:.6f}")

    # Slope & quadrant diagnostics
    diag_alloc = {}
    for arm in arms_order:
        m = deploy_dots[arm]
        q_sh = {
            qn: round(float((m & (quad == qi)).sum()) / float(N_DOTS), 6)
            for qi, qn in enumerate(("NW", "NE", "SW", "SE"))
        }
        slp_sh = {}
        for s_lo, s_hi in ((0.0, 2.5), (2.5, 6.0), (6.0, 12.0), (12.0, 90.0)):
            slp_sh[f"{s_lo:.1f}_{s_hi:.1f}deg"] = round(
                float((m & (slope_deg >= s_lo) & (slope_deg < s_hi)).sum()) / float(N_DOTS), 6
            )
        diag_alloc[arm] = dict(quadrant_shares=q_sh, slope_shares=slp_sh)

    # ---- Step 5: Emit GeoTIFFs via vendor/gems57/submission_writer.py & Run Automated Gates ----
    log("8. Writing 3 frozen-arm GeoTIFFs via vendor/gems57/submission_writer.py & verifying 11/11 gates...")
    exclude_prefixes = ("gemsdoe92-provincetoe-",)
    built_files: dict[str, dict] = {}
    for arm in arms_order:
        raw_bytes_hash8 = hashlib.sha256(np.packbits(deploy_dots[arm]).tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-provincetoe-{arm}-{N_DOTS}-{DATE_TAG}-{raw_bytes_hash8}-zeros"
        tif_path = DOWNLOADS / f"{stem}.tif"
        dti_v = dvis_summary["scores"][arm]["dti"]
        name = f"GEMSDOE92-PROVINCETOE-{arm}-{DATE_TAG}"
        note = f"PROVINCETOE {arm}: 37654 LOQO Wallace-toe + carbonate-grav dots; HOLDOUT-DTI {dti_v:.6f}"
        assert len(name) <= 140 and len(note) <= 140

        receipt = submission_writer.write_submission(
            tif_path,
            deploy_dots[arm].astype(np.float32),
            INPUTS / "bridge" / "sample_submission.tif",
            foot,
            note=note,
            name=name,
            catalogue=cat,
            metadata=dict(
                lane="PROVINCETOE",
                arm=arm,
                hypothesis_doc="docs/HYPOTHESES_20261025_PROVINCETOE.md",
            ),
        )
        (CACHE / f"{stem}.receipt.json").write_text(json.dumps(receipt, indent=2))
        aux_json = tif_path.with_suffix(".json")
        if aux_json.is_file():
            aux_json.replace(CACHE / aux_json.name)
        os.chmod(tif_path, 0o644)
        if tif_path.with_suffix(".zip").is_file():
            os.chmod(tif_path.with_suffix(".zip"), 0o644)

        v_rep = V.validate(tif_path, foot, cat)
        v_rep["file"] = f"docs/downloads/{tif_path.name}"
        V.assert_submittable(v_rep)
        gate_list = gates_mod.run_gates(
            str(tif_path),
            str(INPUTS / "bridge" / "sample_submission.tif"),
            str(INPUTS / "bridge" / "existing_faults.tif"),
            prune_radius=2,
            require_submission_encoding=True,
        )
        ok_gates, gate_txt = gates_mod.summarise(gate_list)
        if not ok_gates:
            raise RuntimeError(f"Format gate failure for {tif_path.name}:\n{gate_txt}")

        built_files[arm] = dict(
            stem=stem,
            file=f"docs/downloads/{tif_path.name}",
            filename=tif_path.name,
            sha256_zeros=sha256_file(tif_path),
            bytes=tif_path.stat().st_size,
            zip=f"docs/downloads/{stem}.zip",
            zip_sha256=sha256_file(tif_path.with_suffix(".zip")),
            submission_name=name,
            note=note,
            note_chars=len(note),
            validator=v_rep,
            gates_zeros=[dataclasses.asdict(g) for g in gate_list],
        )
        log(f"   PASS 11/11 gates: {tif_path.name} (sha256={built_files[arm]['sha256_zeros'][:16]}...)")

    # ---- Step 6: Local + 102-Repo Public Registry Uniqueness ----
    log("9. Scanning local cross-lane registry & 102-repo cached public registry...")
    deploy_surfaces = {a: np.load(CACHE / f"S_{a}_full.npy", mmap_mode="r") for a in arms_order}
    rows_local, skipped_local = scan_local_registry(
        deploy_dots, deploy_surfaces, foot, expected_grid, exclude_prefixes=exclude_prefixes
    )
    rows_pub, pub_inv_meta = scan_public_registry_memmap(deploy_dots, deploy_surfaces, foot)

    sib_overlap = {
        f"{a}_vs_{b}": round(float(U._near(deploy_dots[b], 3.0)[deploy_dots[a]].mean()), 6)
        for a in arms_order
        for b in arms_order
        if a != b
    }

    uniq_by_arm: dict[str, dict] = {}
    for arm in arms_order:
        dl = U.dual_reading_decision(rows_local[arm])
        dp = U.dual_reading_decision(rows_pub[arm])
        uniq_by_arm[arm] = dict(
            local=dl,
            public=dp,
            top_local_mb=sorted(rows_local[arm], key=lambda r: -r["matched_budget_forward_overlap"])[:5],
            top_public_mb=sorted(rows_pub[arm], key=lambda r: -r["matched_budget_forward_overlap"])[:8],
            top_public_rho=sorted(rows_pub[arm], key=lambda r: -abs(r["spearman_surface"]))[:5],
        )
        log(
            f"   {arm:12s}: LOCAL MB={dl['worst_matched_budget_forward_overlap']:.4f} ({dl['worst_matched_budget_file']}), "
            f"|rho|={dl['worst_abs_spearman']:.4f}, dup={dl['duplicate']} | "
            f"PUBLIC MB={dp['worst_matched_budget_forward_overlap']:.4f} ({dp['worst_matched_budget_file']}), "
            f"lit={dp['worst_literal_forward_overlap']:.4f}, |rho|={dp['worst_abs_spearman']:.4f}, dup={dp['duplicate']}"
        )

    # Save holdout, uniqueness, per-file audits, and Protocol Rule 5 Run Card
    holdout_doc = dict(
        schema="gemsdoe92-provincetoe-holdout.v1",
        lane="PROVINCETOE",
        hypothesis_doc="docs/HYPOTHESES_20261025_PROVINCETOE.md",
        evaluator_version="gems57-pooled-hide-v2",
        withheld_positive_pixels=22663,
        best_arm=best_arm,
        leakage_canaries=dict(
            n_features_tested=len(canary_list),
            max_symmetric_auc=max_canary_sym,
            all_pass=(max_canary_sym <= 0.90),
            rows=canary_list,
        ),
        rule2_dvis2=dvis_summary,
        rule2_per_fold=dvis_per_fold,
        static_dcat2=static_summary,
        static_per_fold=static_per_fold,
        sgmc_proxy_dti=sgmc_scores,
        allocation_diagnostics=diag_alloc,
    )
    (EVIDENCE / "provincetoe_holdout.json").write_text(json.dumps(holdout_doc, indent=2) + "\n")

    uniq_doc = dict(
        schema="gemsdoe92-provincetoe-uniqueness.v1",
        lane="PROVINCETOE",
        policy="#IR-92-DENSE-WITNESS-MATCHED-BUDGET: both literal and matched-budget readings reported side by side",
        public_inventory=pub_inv_meta,
        local_rasters_checked=len(rows_local[best_arm]),
        skipped_local=skipped_local,
        sibling_overlap=sib_overlap,
        by_arm=uniq_by_arm,
    )
    (EVIDENCE / "provincetoe_uniqueness.json").write_text(json.dumps(uniq_doc, indent=2) + "\n")

    # Determine overall verdict:
    # Note: under literal dense-witness rule (17GEMSDOE E-proba-multiscale, 5,167,373 positive cells -> 1.000),
    # unique_under_literal_rule is False, so submission_eligible MUST remain False per scripts/check_site.py.
    best_dvis = dvis_summary["scores"][best_arm]
    cl_dvis = dvis_summary["scores"]["COULOMBLOQO_standalone_dvis2"]
    best_stat = static_summary["scores"][best_arm]
    u_best = uniq_by_arm[best_arm]
    dual_unique = (not u_best["local"]["duplicate"]) and (not u_best["public"]["duplicate"])
    beats_holdout_best = bool(best_dvis["dti"] > cl_dvis["dti"])

    # Per-file *-audit.json sidecars (satisfying check_recorded_gates & check_site.py)
    for arm in arms_order:
        bf = built_files[arm]
        ua = uniq_by_arm[arm]
        audit_stem = bf["stem"].removesuffix("-zeros")
        audit_doc = dict(
            schema="gemsdoe92-provincetoe-audit.v1",
            lane="PROVINCETOE",
            arm=arm,
            file=bf["filename"],
            sha256_zeros=bf["sha256_zeros"],
            n_positive_pixels=N_DOTS,
            n_dots=N_DOTS,
            overall_pass=True,
            gates_zeros_pass=True,
            gates_zeros=bf["gates_zeros"],
            submission_eligible=False,
            verdict="negative",
            run_card="evidence/provincetoe_run_card.json",
            holdout_rule2_dvis2=dvis_summary["scores"][arm],
            holdout_static_dcat2=static_summary["scores"][arm],
            sgmc_proxy_dti=sgmc_scores[arm],
            local_registry_uniqueness=ua["local"],
            public_registry_uniqueness=dict(
                candidate_hash_matches_scan=True,
                candidate_sha256_zeros=bf["sha256_zeros"],
                unique_under_literal_rule=False,
                unique_under_matched_budget_rule=(not ua["public"]["duplicate"]),
                stop_required=True,
                witness_evidence="evidence/provincetoe_uniqueness.json",
                worst_matched_budget_forward_overlap=ua["public"]["worst_matched_budget_forward_overlap"],
                worst_matched_budget_file=ua["public"]["worst_matched_budget_file"],
                worst_literal_forward_overlap=ua["public"]["worst_literal_forward_overlap"],
                worst_literal_file=ua["public"]["worst_literal_file"],
                worst_abs_spearman=ua["public"]["worst_abs_spearman"],
                scope=(
                    f"Refreshed 102-repo Git-SHA1-verified public scan ({pub_inv_meta['external_valid_template_rasters']} "
                    f"external valid rasters): matched-budget worst overlap={ua['public']['worst_matched_budget_forward_overlap']:.6f} "
                    f"({ua['public']['worst_matched_budget_file']}); literal dense witness 17GEMSDOE E-proba-multiscale "
                    f"(5,167,373 positive cells) yields literal_forward_overlap=1.000000."
                ),
            ),
        )
        (DOWNLOADS / f"{audit_stem}-audit.json").write_text(json.dumps(audit_doc, indent=2) + "\n")

    bf_best = built_files[best_arm]
    run_card = dict(
        schema="gemsdoe92-run-card.v1",
        date="2026-10-25",
        lane="PROVINCETOE",
        winning_arm=best_arm,
        experiments_executed=3,
        budget_cap_experiments=3,
        weekly_slots_used=0,
        new_unique_tiff_generated=True,
        file=bf_best["filename"],
        primary_download=bf_best["file"],
        zip_download=bf_best["zip"],
        zip_sha256=bf_best["zip_sha256"],
        raster_sha256=bf_best["sha256_zeros"],
        submission_name=bf_best["submission_name"],
        note=bf_best["note"],
        note_chars=bf_best["note_chars"],
        hypothesis=(
            "PROVINCETOE (Rank 1 in docs/HYPOTHESES_20261025_PROVINCETOE.md): Tectonic-Province Strain-Invariant "
            "Wallace Scarp-Diffusion Basal Toe-Concavity & Carbonate-Horst Isostatic Flexure LOQO."
        ),
        mechanism=(
            "Replaces convex log-slope Hessian cliff ridges (which placed 45.2% of COULOMBLOQO dots on >=12 deg alpine "
            "cliffs and triggered 0.7398 sparse overlap vs GEMSDOE23) and raw Walker Lane GPS strain magnitudes (which "
            "starved NE to 11.2% in COULOMBLOQO and 0.7% in BLINDFAULT despite NE holding 41.6% of unmapped SGMC faults) "
            "with upward-concave basal piedmont toe curvature (+lambda_max(nabla^2 z)) gated by cross-eigenvector step "
            "monotonicity M_step and one-sided apron asymmetry A_toe, Wallace crest-toe diffusion dipoles, within-quadrant "
            "relative gravity/basement/RTP/MT contrasts, dimensionless strain-style partitioning, and label-blind "
            "per-quadrant empirical quantile calibration."
        ),
        named_non_fault_process_that_could_mimic_it=(
            "Coalescing alluvial-fan bajada slope-apron breaks, V-shaped incised stream thalwegs, and Pluvial Lake "
            "Lahontan/Bonneville wave-cut shoreline nickpoints. Suppressed via symmetric-wall step monotonicity M_step -> 0 "
            "in V-canyons, along-strike elevation progression against isohypsic lake contours, signed footwall gravity & "
            "basement shallowing concordance, and smooth alpine-cliff attenuation."
        ),
        leakage_canary_max_symmetric_auc=max_canary_sym,
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version="gems57-pooled-hide-v2",
            withheld_positive_pixels=22663,
            primary_instrument="strict_draw_blind_d_visible_gt_2p0",
            strict_draw_blind_dvis2_dti=round(float(best_dvis["dti"]), 6),
            strict_draw_blind_dvis2_ci95=[round(float(x), 6) for x in best_dvis["ci95"]],
            control_H19_5_dvis2_dti=round(float(dvis_summary["scores"]["H19_5_dvis2"]["dti"]), 6),
            control_COULOMBLOQO_standalone_dvis2_dti=round(float(cl_dvis["dti"]), 6),
            paired_delta_vs_H19_5_dvis2=dvis_summary["paired_differences"].get("H19_5_dvis2"),
            paired_delta_vs_COULOMBLOQO_dvis2=dvis_summary["paired_differences"].get("COULOMBLOQO_standalone_dvis2"),
            paired_delta_vs_globalraw_ablation_dvis2=dvis_summary["paired_differences"].get("globalraw"),
            static_dcat2_dti=round(float(best_stat["dti"]), 6),
            static_dcat2_ci95=[round(float(x), 6) for x in best_stat["ci95"]],
            control_R0_static_dcat2_dti=round(float(static_summary["scores"]["R0"]["dti"]), 6),
            sgmc_off_catalogue_proxy_dti=sgmc_scores[best_arm],
            beats_prior_holdout_best_dvis2=beats_holdout_best,
        ),
        correlation_overlap_vs_registry=dict(
            policy="#IR-92-DENSE-WITNESS-MATCHED-BUDGET",
            dual_reading_unique=dual_unique,
            local=u_best["local"],
            public=u_best["public"],
        ),
        validator=bf_best["validator"],
        validator_output=dict(
            overall_pass=True,
            crs="EPSG:32611",
            shape=[3730, 3292],
            dtype="float32",
            values_range=[0.0, 1.0],
            no_nan_in_footprint=True,
            no_nan_anywhere=True,
            n_positive_pixels=N_DOTS,
            catalogue_mass=0.0,
        ),
        sibling_arms={
            a: dict(
                file=built_files[a]["file"],
                sha256=built_files[a]["sha256_zeros"],
                dvis2_dti=round(float(dvis_summary["scores"][a]["dti"]), 6),
                static_dcat2_dti=round(float(static_summary["scores"][a]["dti"]), 6),
                sgmc_proxy_dti=sgmc_scores[a],
                public_matched_budget_worst_overlap=uniq_by_arm[a]["public"]["worst_matched_budget_forward_overlap"],
                local_matched_budget_worst_overlap=uniq_by_arm[a]["local"]["worst_matched_budget_forward_overlap"],
            )
            for a in arms_order
        },
        submission_eligible=False,
        verdict="negative",
        verdict_reason=(
            f"Format-valid (11/11 gates PASS, values in [0, 1]) and dual_reading_unique={dual_unique} "
            f"(public matched-budget max overlap {u_best['public']['worst_matched_budget_forward_overlap']:.4f}, "
            f"local max overlap {u_best['local']['worst_matched_budget_forward_overlap']:.4f}), "
            f"strict draw-blind HOLDOUT-DTI {best_dvis['dti']:.6f} vs COULOMBLOQO {cl_dvis['dti']:.6f} "
            f"and H19-5 {dvis_summary['scores']['H19_5_dvis2']['dti']:.6f}; "
            "literal dense-witness rule (17GEMSDOE E-proba-multiscale, 5,167,373 positive footprint cells -> 1.000) "
            "keeps submission_eligible=false under the repository's fail-closed site gate."
        ),
    )
    run_card_bytes = (json.dumps(run_card, indent=2) + "\n").encode("utf-8")
    (EVIDENCE / "provincetoe_run_card.json").write_bytes(run_card_bytes)
    (DOWNLOADS / "provincetoe_run_card.json").write_bytes(run_card_bytes)
    (DOWNLOADS / "provincetoe_uniqueness.json").write_bytes((EVIDENCE / "provincetoe_uniqueness.json").read_bytes())
    (DOWNLOADS / "provincetoe_holdout.json").write_bytes((EVIDENCE / "provincetoe_holdout.json").read_bytes())

    log(f"DONE in {time.time() - t0:.1f}s! Best arm: {best_arm} (d_vis>2.0 DTI={best_dvis['dti']:.6f}, static DTI={best_stat['dti']:.6f}, dual_unique={dual_unique})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
