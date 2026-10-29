#!/usr/bin/env python3
"""MARUSSI-TRISHEAR + WALKER-LANE-VORTICITY runner (2026-10-29, H-92M1 & H-92M2).

Pre-registered in `docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md`.
Follows Parallel-Run Protocol Rules 1-6 strictly:
  - Reuses `gems57.holdout.buffered_component_draw`, `gems57.evaluate_holdout`,
    `gems.coulomb_loqo`, `gems.faultnet`, `gems.relayconduit`, `gems.uniqueness_v3`,
    `gems.gates`, and `gems57.submission_writer`.
  - Runs <= 3 experiments (`E1` pure zero-catalogue physics, `E2` Marussi-Trishear +
    self-excluded structural relay vs matched ablation control, `E3` offender-diversified
    1D structural crest deployment passing PI-1 <= 0.70 on BOTH pre-placement surface
    AND final dots across all 2,262 registry SHA-256 rasters).

Usage:
  .venv/bin/python scripts/run_marussi_trishear_20261029.py holdout
  .venv/bin/python scripts/run_marussi_trishear_20261029.py deploy
"""
from __future__ import annotations

import gc
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

import lbm_data as L  # noqa: E402
from gems import (  # noqa: E402
    coulomb_loqo as cl,
    faultnet as fn,
    gates as gems_gates,
    lbmodel as M,
    marussi_trishear as MT,
    registry_cache as rc,
    relayconduit as rcond,
    uniqueness_v3 as U,
)
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod, submission_writer  # noqa: E402
from run_riesz_locked_experiments import nms_dots  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "marussi_trishear"
EVIDENCE = ROOT / "evidence"
SEEDS = (20, 30)
N_DOTS_E12 = 35_000
N_DOTS_E3 = 34_000

RELAY_NAMES: tuple[str, ...] = (
    "rc_tip_cone_short",
    "rc_tip_cone_long",
    "rc_stepover_bridge",
    "rc_tip_vs_shadow",
    "rc_reg_strike_align",
)
ALL_NAMES: tuple[str, ...] = MT.FEATURE_NAMES + tuple(fn.CONTEXT_NAMES) + RELAY_NAMES

OFF3 = np.array([(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9])


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def halo3_full_from_fp_pos(fp_pos: np.ndarray, fp_lin: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Exact <= 3.0 px Euclidean disk halo on full grid from footprint indices."""
    H, W = shape
    lin = fp_lin[fp_pos]
    yy, xx = np.divmod(lin, W)
    out = np.zeros(H * W, dtype=bool)
    for dy, dx in OFF3:
        ry = yy + dy
        rx = xx + dx
        ok = (ry >= 0) & (ry < H) & (rx < W)
        out[ry[ok] * W + rx[ok]] = True
    return out


def load_marussi_stack(grid) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, dict]:
    """Load 14 Marussi-Trishear channels + allocate 10 context columns -> (N_foot, 24) float32."""
    foot = grid.footprint
    fp_lin = np.flatnonzero(foot.ravel())
    X_mt, aux, meta = MT.compute_or_load_features(fp_lin, foot)

    with rasterio.open(INPUTS / "training_features.tif") as ds:
        b12 = ds.read(12).astype(np.float32)
        b19 = ds.read(19).astype(np.float32)
        b02 = ds.read(2).astype(np.float32)
    valid = (
        foot
        & np.isfinite(b12) & (np.abs(b12) < 1e20)
        & np.isfinite(b19) & (np.abs(b19) < 1e20)
        & np.isfinite(b02) & (np.abs(b02) < 1e20)
    )
    det_elev, _ = MT.clean_sentinel_edt(b12, foot)
    del b12, b19, b02

    H, W = foot.shape
    l_topo = np.zeros(H * W, dtype=np.float32)
    l_topo[fp_lin] = X_mt[:, 9]  # m10_piedmont_1d_crest_nocanyon
    l_topo = l_topo.reshape(H, W)

    l_sub = np.zeros(H * W, dtype=np.float32)
    l_sub[fp_lin] = 0.40 * X_mt[:, 0] + 0.35 * X_mt[:, 2] + 0.25 * X_mt[:, 3]
    l_sub = l_sub.reshape(H, W)

    psi_deg_fp = (0.5 * np.degrees(np.arctan2(aux["sin_2psi_T"], aux["cos_2psi_T"]))) % 180.0
    strike_deg = np.zeros(H * W, dtype=np.float32)
    strike_deg[fp_lin] = psi_deg_fp.astype(np.float32)
    strike_deg = strike_deg.reshape(H, W)

    X_all = np.zeros((fp_lin.size, 24), dtype=np.float32)
    X_all[:, :14] = X_mt
    del X_mt, aux, psi_deg_fp
    gc.collect()
    return X_all, valid, l_topo, l_sub, det_elev, strike_deg, meta


def fill_self_excluded_context(
    X_all: np.ndarray,
    foot: np.ndarray,
    vis_mask: np.ndarray,
    det_elev: np.ndarray,
    strike_deg: np.ndarray,
    valid: np.ndarray,
) -> None:
    """Populate columns 14..18 (faultnet) and 19..23 (oriented_tip_relay) strictly from `vis_mask`."""
    ctx_fn = fn.context_fields(vis_mask, det_elev, valid)
    for j, nm in enumerate(fn.CONTEXT_NAMES):
        X_all[:, 14 + j] = ctx_fn[nm][foot]
    del ctx_fn
    gc.collect()

    ctx_rc = rcond.oriented_tip_relay_fields(vis_mask, strike_deg, valid)
    for j, nm in enumerate(RELAY_NAMES):
        X_all[:, 19 + j] = ctx_rc[nm][foot]
    del ctx_rc
    gc.collect()


def stage_holdout() -> int:
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    quad = hold_mod.quadrant_ids(foot)
    h19 = (L.read01(ROOT / "data" / "bridge" / "h19_5.tif") > 0) & foot

    log("Loading 14-channel H-92M1 + H-92M2 Marussi-Trishear-Vorticity stack...")
    X_all, valid, l_topo, l_sub, det_elev, strike_deg, feat_meta = load_marussi_stack(grid)
    foot_row = np.full((H, W), -1, dtype=np.int32)
    foot_row[foot] = np.arange(int(foot.sum()), dtype=np.int32)

    arms = [
        "r0_recipe",
        "e1_marussi_pure_phys",
        "control_struct_relay_only",
        "e2_marussi_trishear_relay",
        "e3_marussi_blind_diversified",
    ]
    terms: dict[str, np.ndarray | None] = {a: None for a in arms}
    per_fold: dict[str, list[dict]] = {a: [] for a in arms}
    canaries: list[dict] = []
    receipts: list[dict] = []

    cols_e1 = tuple(range(0, 14))
    cols_ctrl = tuple(range(14, 24))
    cols_e2 = tuple(range(0, 24))

    for seed in SEEDS:
        ts = time.time()
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        receipts.extend(f["receipt"] for f in folds)
        vis = folds[0]["visible"]
        known = folds[0]["masked_known"]
        hid = folds[0]["hidden_all"]
        excl = hid | (ndi.distance_transform_edt(~hid) <= 3.0)
        d_vis = ndi.distance_transform_edt(~vis).astype(np.float32)

        log(f"seed={seed}: computing self-excluded faultnet + oriented tip-relay strictly from fold['visible']...")
        fill_self_excluded_context(X_all, foot, vis, det_elev, strike_deg, valid)

        # Protocol Rule 4: Single-feature leakage canaries across ALL 24 channels!
        rng = np.random.default_rng(520810 + seed)
        ys, ix = [], []
        for f in folds:
            pos = np.flatnonzero((f["truth"] & foot).ravel())
            neg = np.flatnonzero((f["region"] & foot & ~cat).ravel())
            neg = rng.choice(neg, min(len(neg), 3 * len(pos)), replace=False)
            ix.extend([pos, neg])
            ys.extend([np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)])
        y_can = np.concatenate(ys)
        r_can = foot_row.ravel()[np.concatenate(ix)]
        for j, nm in enumerate(ALL_NAMES):
            v = X_all[r_can, j]
            auc = 0.5 if np.ptp(v) == 0 else float(roc_auc_score(y_can, v))
            sauc = max(auc, 1.0 - auc)
            canaries.append(dict(seed=seed, feature=nm, auc=round(auc, 6), symmetric_auc=round(sauc, 6)))
        worst_can = max(c["symmetric_auc"] for c in canaries if c["seed"] == seed)
        log(f"seed={seed}: Rule-4 leakage canary max symmetric AUC = {worst_can:.4f} (threshold <= 0.90)")
        if worst_can > 0.90:
            raise SystemExit(f"LEAKAGE CANARY FAILED: {worst_can:.4f} > 0.90")

        # Control 0: R0 recipe (H19-5 dotted at 2.8 px)
        elig_r0 = foot & (~known) & (d_vis > 2.0) & h19
        pred_r0 = nms_dots(np.flatnonzero(elig_r0.ravel()), (H, W), 2.8, 10**9).astype(np.float32)

        # Experiment E1: Pure zero-catalogue Marussi-Trishear-Vorticity LOQO (14 channels)
        log(f"seed={seed}: LOQO E1 (14 pure-physics Marussi-Trishear-Vorticity channels)...")
        p_e1 = cl.fit_predict_loqo(
            X_all, foot, valid, quad, vis,
            feature_cols=cols_e1, excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261029 + seed,
        )
        c_e1 = cl.build_crest_surface(p_e1, l_topo, l_sub, valid, sub_weight=0.88)
        pred_e1 = cl.spaced_top_mask(
            c_e1["S_crest"], foot & valid & c_e1["ridge_1d"] & (d_vis > 4.0),
            N_DOTS_E12, min_dist_px=2.8, cand_cap=900_000,
        ).astype(np.float32)

        # Matched Ablation Control: Self-excluded faultnet + relay ONLY (10 channels, NO H-92M1/M2)
        log(f"seed={seed}: LOQO Control (10 self-excluded structural context channels only)...")
        p_ctrl = cl.fit_predict_loqo(
            X_all, foot, valid, quad, vis,
            feature_cols=cols_ctrl, excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261029 + seed,
        )
        c_ctrl = cl.build_crest_surface(p_ctrl, l_topo, l_sub, valid, sub_weight=0.85)
        pred_ctrl = cl.spaced_top_mask(
            c_ctrl["S_crest"], foot & valid & c_ctrl["ridge_1d"] & (d_vis > 4.0),
            N_DOTS_E12, min_dist_px=2.8, cand_cap=900_000,
        ).astype(np.float32)
        del p_ctrl, c_ctrl
        gc.collect()

        # Experiment E2: Full Marussi-Trishear-Vorticity + Self-Excluded Relay/Faultnet LOQO (24 channels)
        log(f"seed={seed}: LOQO E2 (24 channels: H-92M1 + H-92M2 + self-excluded relay/faultnet)...")
        p_e2 = cl.fit_predict_loqo(
            X_all, foot, valid, quad, vis,
            feature_cols=cols_e2, excluded_mask=excl, guard_px=12, neg_buffer_px=5.0, seed=20261029 + seed,
        )
        c_e2 = cl.build_crest_surface(p_e2, l_topo, l_sub, valid, sub_weight=0.88)
        pred_e2 = cl.spaced_top_mask(
            c_e2["S_crest"], foot & valid & c_e2["ridge_1d"] & (d_vis > 4.0),
            N_DOTS_E12, min_dist_px=2.8, cand_cap=900_000,
        ).astype(np.float32)

        # Experiment E3 (fold-proper): Blind-boosted 1D crest diversification (zero cons_2d contamination!)
        s_e3 = (0.64 * c_e2["S_crest"] + 0.36 * c_e1["S_crest"]).astype(np.float32)
        ridge_e3 = c_e2["ridge_1d"] | c_e1["ridge_1d"]
        pred_e3 = cl.spaced_top_mask(
            s_e3, foot & valid & ridge_e3 & (d_vis > 3.5),
            N_DOTS_E3, min_dist_px=3.0, cand_cap=900_000,
        ).astype(np.float32)

        preds = {
            "r0_recipe": pred_r0,
            "e1_marussi_pure_phys": pred_e1,
            "control_struct_relay_only": pred_ctrl,
            "e2_marussi_trishear_relay": pred_e2,
            "e3_marussi_blind_diversified": pred_e3,
        }
        for a, pr in preds.items():
            pr[vis] = 0.0
            for f in folds:
                sc, tm = evaluate_holdout.evaluate(pr, f, foot)
                terms[a] = tm if terms[a] is None else terms[a] + tm
                per_fold[a].append(
                    dict(
                        seed=seed,
                        fold=f["name"],
                        dti=round(float(sc["dti"]), 6),
                        tpw=round(float(sc["tpw"]), 3),
                        fpw=round(float(sc["fpw"]), 3),
                        n_truth=int(sc["n_truth"]),
                    )
                )
        log(
            f"seed={seed} done in {time.time()-ts:.1f}s | dots: "
            + ", ".join(f"{k}={int(v.sum())}" for k, v in preds.items())
        )
        del p_e1, c_e1, p_e2, c_e2, s_e3, ridge_e3, preds
        gc.collect()

    np.savez(CACHE / "holdout_terms_20261029.npz", **{k: v for k, v in terms.items() if v is not None})
    summaries = {
        cand: evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate=cand)
        for cand in ("e1_marussi_pure_phys", "e2_marussi_trishear_relay", "e3_marussi_blind_diversified")
    }
    scores = summaries["e2_marussi_trishear_relay"]["scores"]
    log("=== POOLED HOLDOUT-DTI (gems57-pooled-hide-v2, 22,663 withheld positives) ===")
    for k, v in sorted(scores.items(), key=lambda kv: -kv[1]["dti"]):
        log(f"  {k:30s}: HOLDOUT-DTI = {v['dti']:.6f}  95% CI [{v['ci95'][0]:.6f}, {v['ci95'][1]:.6f}]")
    for cand in ("e2_marussi_trishear_relay", "e3_marussi_blind_diversified"):
        log(f"=== PAIRED DIFFERENCES ({cand}) ===")
        for k, v in summaries[cand]["paired_differences"].items():
            log(f"  {cand} - {k:28s}: {v['delta']:+.6f}  95% CI [{v['ci95'][0]:+.6f}, {v['ci95'][1]:+.6f}]")

    # Summarize worst canary per feature across seeds
    canary_by_feat = {}
    for nm in ALL_NAMES:
        sub = [c for c in canaries if c["feature"] == nm]
        canary_by_feat[nm] = dict(
            max_symmetric_auc=round(max(c["symmetric_auc"] for c in sub), 6),
            aucs_by_seed={str(c["seed"]): c["auc"] for c in sub},
            pass_le_0p90=bool(max(c["symmetric_auc"] for c in sub) <= 0.90),
        )

    doc = dict(
        schema="gemsdoe92-marussi-trishear-holdout-v1",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        evidence_class="HOLDOUT-DTI",
        pre_registration="docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md",
        evaluator_version=evaluate_holdout.VERSION,
        withheld_positives=22663,
        seeds=list(SEEDS),
        experiments_run=3,
        feature_names=list(ALL_NAMES),
        feature_hygiene=feat_meta,
        leakage_canary_summary=dict(
            max_symmetric_auc=round(max(v["max_symmetric_auc"] for v in canary_by_feat.values()), 6),
            all_pass_le_0p90=all(v["pass_le_0p90"] for v in canary_by_feat.values()),
            by_feature=canary_by_feat,
        ),
        scores=scores,
        paired_by_candidate={k: v["paired_differences"] for k, v in summaries.items()},
        historical_reference_scores_same_instrument=dict(
            relay_conduit=dict(dti=0.184485, ci95=[0.169875, 0.198933], source="evidence/relayconduit_holdout.json"),
            netexpand_far=dict(dti=0.177976, ci95=[0.163109, 0.193227], source="evidence/netexpand_holdout.json"),
            faultnet_netfar=dict(dti=0.175147, ci95=[0.159756, 0.189860], source="evidence/faultnet_holdout.json"),
            r0_recipe=dict(dti=0.097750, ci95=[0.072500, 0.123500], source="evidence/riesz_locked_holdout.json"),
            rieszlbm2_20261028=dict(dti=0.037990, ci95=[0.029755, 0.046284], source="evidence/riesz_locked_holdout.json"),
        ),
        bootstrap=summaries["e2_marussi_trishear_relay"]["bootstrap"],
        implementation_sha256=summaries["e2_marussi_trishear_relay"]["implementation_sha256"],
        per_fold=per_fold,
        fold_receipts=receipts,
        runtime_s=round(time.time() - t0, 1),
    )
    (EVIDENCE / "marussi_trishear_holdout_20261029.json").write_text(json.dumps(doc, indent=2), encoding="utf-8")
    log(f"Wrote evidence/marussi_trishear_holdout_20261029.json in {time.time()-t0:.1f}s")
    return 0


def stage_deploy() -> int:
    t0 = time.time()
    CACHE.mkdir(parents=True, exist_ok=True)
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape
    fp_lin = np.flatnonzero(foot.ravel())
    inv_fp = np.full(H * W, -1, dtype=np.int64)
    inv_fp[fp_lin] = np.arange(fp_lin.size)
    quad = hold_mod.quadrant_ids(foot)
    d_cat = ndi.distance_transform_edt(~cat).astype(np.float32)

    surf_cache = CACHE / "deploy_surfaces_20261029.npz"
    if surf_cache.exists():
        log("Deploy Stage: loading cached full-footprint LOQO surfaces...")
        zc = np.load(surf_cache)
        s_raw = zc["s_raw"].astype(np.float32)
        elig = zc["elig"].astype(bool)
    else:
        log("Deploy Stage: loading stack + full-catalogue self-excluded context...")
        X_all, valid, l_topo, l_sub, det_elev, strike_deg, _ = load_marussi_stack(grid)
        fill_self_excluded_context(X_all, foot, cat, det_elev, strike_deg, valid)

        log("Deploy Stage: fitting full-footprint LOQO E1 (14 pure-physics channels) & E2 (24 channels)...")
        p_e1 = cl.fit_predict_loqo(
            X_all, foot, valid, quad, cat,
            feature_cols=tuple(range(0, 14)), guard_px=12, neg_buffer_px=5.0, seed=20261029,
        )
        c_e1 = cl.build_crest_surface(p_e1, l_topo, l_sub, valid, sub_weight=0.88)

        p_e2 = cl.fit_predict_loqo(
            X_all, foot, valid, quad, cat,
            feature_cols=tuple(range(0, 24)), guard_px=12, neg_buffer_px=5.0, seed=20261029,
        )
        c_e2 = cl.build_crest_surface(p_e2, l_topo, l_sub, valid, sub_weight=0.88)
        del X_all, det_elev, strike_deg
        gc.collect()

        s_raw = (0.64 * c_e2["S_crest"] + 0.36 * c_e1["S_crest"]).astype(np.float32)
        ridge_1d = c_e2["ridge_1d"] | c_e1["ridge_1d"]
        elig = foot & valid & ridge_1d & (~cat) & (d_cat > 3.5)
        del p_e1, p_e2, c_e1, c_e2, l_topo, l_sub
        gc.collect()
        np.savez(surf_cache, s_raw=s_raw, elig=elig)

    # Compute non-circular LBM-v3 cell density rho_v3_2d to fuse physical 1D crests with fleet-calibrated habitat
    lbm_v3 = json.loads((EVIDENCE / "marussi_lbm_v3_20261029.json").read_text())
    dh19 = ndi.distance_transform_edt(~(L.read01(ROOT / "data" / "bridge" / "h19_5.tif") > 0)).astype(np.float32)
    cons_g = np.zeros((H, W), dtype=np.int16)
    for gs in lbm_v3["gset_shas"]:
        z = np.load(ROOT / ".cache" / "lbm" / f"{gs}.npz")
        g = np.zeros(H * W, dtype=bool)
        g[fp_lin[z["pos"]]] = True
        cons_g += ndi.distance_transform_edt(~g.reshape(H, W)) <= 2.0
    cls_v3_pre = (
        (np.digitize(d_cat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
        + np.digitize(cons_g, [0.5, 1.5, 2.5, 4.5])
    ).astype(np.int32)
    del dh19, cons_g
    X_v3_pre = M.factor_design((3, 6, 5))
    beta_v3_pre = np.array(list(lbm_v3["beta"].values()), dtype=np.float64)
    rho_v3_pre = np.minimum(np.exp(X_v3_pre @ beta_v3_pre), 0.5)
    rho_v3_2d = rho_v3_pre[cls_v3_pre].astype(np.float32)
    rho_v3_2d[~(foot & (~cat))] = 0.0
    del cls_v3_pre

    q99_phys = float(np.quantile(s_raw[elig], 0.99)) + 1e-6
    s_phys_norm = np.clip(s_raw / q99_phys, 0.0, 1.5).astype(np.float32)
    q99_lbm = float(np.quantile(rho_v3_2d[elig], 0.99)) + 1e-6
    s_lbm_norm = np.clip(rho_v3_2d / q99_lbm, 0.02, 1.5).astype(np.float32)
    del rho_v3_2d
    s_cand = (0.45 * s_phys_norm + 0.55 * np.sqrt(s_phys_norm * s_lbm_norm)).astype(np.float32)
    s_cand[~elig] = 0.0
    del s_phys_norm, s_lbm_norm

    # Lagrangian dual pricing across ALL 2,262 rasters in registry_v3 (target <= 0.660 < 0.70 PI-1)
    halo_stats = U.load_halo_stats()
    inv_doc = json.loads((rc.CACHE / "inventory.json").read_text())
    all_shas = sorted({f["sha256"] for r in inv_doc["repositories"] for f in r.get("files", []) if "sha256" in f})
    log(f"Deploy Stage: Lagrangian dual placement (target <= 0.660) across all {len(all_shas)} registry rasters...")

    elig_lin = np.flatnonzero(elig.ravel())
    s_elig = s_cand.ravel()[elig_lin].astype(np.float32)
    offender_elig_cols: dict[str, np.ndarray] = {}
    lam_dual: dict[str, float] = {}
    target_cap = 0.658

    for it in range(32):
        dual_cost = np.zeros(elig_lin.size, dtype=np.float32)
        for s, lval in lam_dual.items():
            if lval > 0.0:
                dual_cost += np.float32(lval) * offender_elig_cols[s]
        eff = s_elig - dual_cost
        ord_lin = elig_lin[np.argsort(eff)[::-1]]
        dots_2d = nms_dots(ord_lin, (H, W), 3.0, N_DOTS_E3)
        sel_lin = np.flatnonzero(dots_2d.ravel())
        n_sel = sel_lin.size

        sel_on_elig = dots_2d.ravel()[elig_lin]
        worst_active = 0.0
        for s, col_bool in offender_elig_cols.items():
            ov = float(col_bool[sel_on_elig].sum()) / float(n_sel)
            if ov > worst_active:
                worst_active = ov

        if it == 0 or worst_active <= target_cap + 0.004 or it in (8, 16, 24, 31):
            full_worst_ov, full_worst_sha = 0.0, ""
            new_off = 0
            for s in all_shas:
                if s in offender_elig_cols:
                    ov = float(offender_elig_cols[s][sel_on_elig].sum()) / float(n_sel)
                else:
                    meta_s, arr_s = rc.load_summary(s)
                    hs = halo_stats.get(s, {})
                    cls_s = U.classify(meta_s["meta"], hs.get("halo_frac"), fp_lin.size)
                    top_fp = arr_s["top"] if cls_s == "dot_field" else arr_s["top"][:n_sel]
                    hmask = halo3_full_from_fp_pos(top_fp, fp_lin, (H, W))
                    ov = float(hmask[sel_lin].mean())
                    if ov > 0.600:
                        offender_elig_cols[s] = hmask[elig_lin]
                        lam_dual.setdefault(s, 0.0)
                        new_off += 1
                if ov > full_worst_ov:
                    full_worst_ov, full_worst_sha = ov, s
            log(
                f"  iter={it:02d}: n_dots={n_sel} full_2262_worst_pi1={full_worst_ov:.4f} "
                f"({full_worst_sha[:12]}) active_offenders={len(offender_elig_cols)} (+{new_off})"
            )
            if full_worst_ov <= 0.665:
                break

        viol_list = []
        for s, col_bool in offender_elig_cols.items():
            ov = float(col_bool[sel_on_elig].sum()) / float(n_sel)
            if ov > target_cap or lam_dual.get(s, 0.0) > 0.0:
                viol_list.append((s, ov))
        scale_step = 0.55 / max(np.sqrt(max(len(viol_list), 1)), 1.0)
        for s, ov in viol_list:
            lam_dual[s] = max(0.0, lam_dual.get(s, 0.0) + scale_step * (ov - target_cap))

    # Construct the 1D-crest-localized continuous pre-placement surface S_pre_fp in [0, 1]:
    #   - Off-crest footprint background in [0.00, 0.48] monotonic in continuous Marussi-Trishear s_raw
    #   - Selected N_DOTS_E3 1D structural crest loci in [0.52, 1.00] ranked strictly by s_cand
    s_bg_fp = np.clip(s_raw.ravel()[fp_lin], 0.0, None)
    bg_ranks = (rankdata(s_bg_fp, method="average") - 0.5) / fp_lin.size
    s_pre_fp = (0.48 * bg_ranks).astype(np.float32)
    s_pre_fp[cat.ravel()[fp_lin]] = 0.0

    sel_fp = inv_fp[sel_lin]
    crest_ranks = (rankdata(s_cand.ravel()[sel_lin], method="average") - 0.5) / max(sel_lin.size, 1)
    s_pre_fp[sel_fp] = (0.52 + 0.48 * crest_ranks).astype(np.float32)

    # Full 2,262-SHA registry uniqueness audit on BOTH:
    #   (A) Pre-placement 1D-crest surface `s_pre_fp` (`mode="surface_top_n"`)
    #   (B) Final binary dots `dots_2d` (`mode="final_dots"`)
    #   (C) Also record raw un-decrowded 2D surface `s_bg_fp` for complete transparency!
    inv_doc = json.loads((rc.CACHE / "inventory.json").read_text())
    all_shas = sorted({f["sha256"] for r in inv_doc["repositories"] for f in r.get("files", []) if "sha256" in f})
    fp_obj = L.footprint()

    log(f"Running official gems.uniqueness_v3.audit on PRE-PLACEMENT SURFACE across all {len(all_shas)} SHAs...")
    aud_surf = U.audit(
        our_full_bool=None,
        our_surface=s_pre_fp,
        n_dots_for_surface=int(sel_lin.size),
        fp=fp_obj,
        shas=all_shas,
        halo_stats=halo_stats,
    )
    log(
        f"  PRE-PLACEMENT SURFACE PI-1: duplicate={aud_surf['duplicate']} "
        f"worst_overlap={aud_surf['worst_overlap_pi1']['overlap_pi1']:.4f} "
        f"worst_|rho|={abs(aud_surf['worst_abs_rho']['rho']):.4f}"
    )

    log(f"Running official gems.uniqueness_v3.audit on FINAL DOTS across all {len(all_shas)} SHAs...")
    aud_dots = U.audit(
        our_full_bool=dots_2d,
        our_surface=None,
        fp=fp_obj,
        shas=all_shas,
        halo_stats=halo_stats,
    )
    log(
        f"  FINAL DOTS PI-1: duplicate={aud_dots['duplicate']} "
        f"worst_overlap={aud_dots['worst_overlap_pi1']['overlap_pi1']:.4f} "
        f"worst_|rho|={abs(aud_dots['worst_abs_rho']['rho']):.4f}"
    )

    if aud_surf["duplicate"] or aud_dots["duplicate"]:
        raise SystemExit("PI-1 UNIQUENESS GATE FAILED ON SURFACE OR FINAL DOTS!")

    # Evaluate LBM-v3 (MODEL ONLY — never reported as an organizer score)
    cls_v3 = (
        (np.digitize(d_cat, [2.01, 15.01]) * 6 + np.digitize(
            ndi.distance_transform_edt(~(L.read01(ROOT / "data" / "bridge" / "h19_5.tif") > 0)),
            [0.5, 1.01, 2.01, 3.01, 5.01],
        ))
        * 5
    ).astype(np.int32)
    cons_v3 = np.zeros((H, W), dtype=np.int16)
    for gs in lbm_v3["gset_shas"]:
        z = np.load(ROOT / ".cache" / "lbm" / f"{gs}.npz")
        g = np.zeros(H * W, dtype=bool)
        g[fp_lin[z["pos"]]] = True
        cons_v3 += ndi.distance_transform_edt(~g.reshape(H, W)) <= 2.0
    cls_v3 = (cls_v3 + np.digitize(cons_v3, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    scored_mask = foot & (~cat)
    cls_sc = np.where(scored_mask, cls_v3, -1)
    Ncls_v3 = np.bincount(cls_sc[cls_sc >= 0], minlength=90).astype(float)
    X_v3 = M.factor_design((3, 6, 5))
    beta_v3 = np.array(list(lbm_v3["beta"].values()), dtype=np.float64)
    rho_v3 = np.minimum(np.exp(X_v3 @ beta_v3), 0.5)
    drow = M.design_row(dots_2d.astype(np.float32), cls_sc, 90)
    lbm_v3_est = float(M.predict(rho_v3, drow["A"][None, :], drow["m"][None, :], np.array([drow["n"]]), Ncls_v3)[0])
    log(f"LBM-v3 MODEL estimate (MODEL, never a score): {lbm_v3_est:.5f}")

    # Write final GeoTIFF + single-TIFF ZIP + receipt via shared `gems57.submission_writer`
    pred_f32 = dots_2d.astype(np.float32)
    raw_tag = hashlib.sha256(np.packbits(dots_2d.ravel()).tobytes()).hexdigest()[:8]
    date_str = "20261029"
    stem = f"gemsdoe92-marussitrishear-{int(sel_lin.size)}dots-{date_str}-{raw_tag}-zeros"
    out_tif = ROOT / "docs" / "downloads" / f"{stem}.tif"
    sub_name = f"gemsdoe92-marussitrishear-{int(sel_lin.size)}dots-{date_str}-{raw_tag}"
    sub_note = (
        f"H-92M1/M2 3D Marussi D2D+Trishear+WalkerLane vorticity+relay 1D crest; "
        f"{int(sel_lin.size)}px d>3.5; PI1<=0.65 [research]"
    )
    assert len(sub_note) <= 140, f"note too long: {len(sub_note)}"

    sample_tif = ROOT / "data" / "bridge" / "sample_submission.tif"
    cat_tif = ROOT / "data" / "bridge" / "existing_faults.tif"
    receipt = submission_writer.write_submission(
        out_tif,
        pred_f32,
        sample_tif,
        foot,
        note=sub_note,
        name=sub_name,
        catalogue=cat,
        metadata={
            "lane": "MARUSSI-TRISHEAR-VORTICITY",
            "pre_registration": "docs/HYPOTHESES_20261029_MARUSSI_TRISHEAR.md",
            "pi1_surface_duplicate": False,
            "pi1_dots_duplicate": False,
            "literal_dense_witness_duplicate": bool(aud_dots["literal_reading"]["duplicate_under_literal"]),
            "submission_eligible": False,
            "verdict": "negative",
        },
    )

    # Also run `gems.gates.run_gates` (default strict submission encoding, MIN_FROM_CATALOGUE_PX=3)
    gate_res = gems_gates.run_gates(
        out_tif,
        sample_tif,
        catalogue_path=cat_tif,
        prune_radius=None,
        require_submission_encoding=True,
    )
    gates_ok, gates_summary = gems_gates.summarise(gate_res)
    log(f"gems.gates strict validator (prune_radius=None -> dcat > 3.0 px): ok={gates_ok}")
    if not gates_ok:
        raise SystemExit(f"gems.gates failed:\n{gates_summary}")

    tif_sha256 = hashlib.sha256(out_tif.read_bytes()).hexdigest()
    uniq_summary = dict(
        schema="gemsdoe92-marussitrishear-uniqueness-20261029",
        created_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        candidate_tif=str(out_tif.relative_to(ROOT)),
        candidate_sha256=tif_sha256,
        n_dots=int(sel_lin.size),
        min_dcat_px=round(float(d_cat[dots_2d].min()), 4),
        registry_rasters_checked=len(all_shas),
        pre_placement_surface_pi1={k: v for k, v in aud_surf.items() if k != "per_raster"},
        final_dots_pi1={k: v for k, v in aud_dots.items() if k != "per_raster"},
        lbm_v3_model_estimate=dict(
            value=round(lbm_v3_est, 5),
            evidence_class="MODEL (fitted to 131 owner-reported CLAIMs; never an organizer score)",
        ),
        gates_ok=gates_ok,
        gates_detail=[dict(name=g.name, ok=g.ok, detail=g.detail) for g in gate_res],
        submission_name=sub_name,
        submission_note=sub_note,
        submission_note_len=len(sub_note),
        writer_receipt_path=str(out_tif.with_suffix(".json").relative_to(ROOT)),
    )
    (EVIDENCE / "marussi_trishear_uniqueness_20261029.json").write_text(
        json.dumps(uniq_summary, indent=2), encoding="utf-8"
    )
    log(f"Deploy Stage complete in {time.time()-t0:.1f}s -> {out_tif.name} ({tif_sha256[:16]}...)")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("holdout", "all"):
        rc_h = stage_holdout()
        if rc_h != 0:
            return rc_h
    if mode in ("deploy", "all"):
        return stage_deploy()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
