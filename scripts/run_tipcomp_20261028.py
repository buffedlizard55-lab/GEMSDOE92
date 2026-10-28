#!/usr/bin/env python3
"""TIPCOMP session 2026-10-28 (H-92F1): E1 canaries/controls, E2 fold-proper
tip-continuation holdout, E3 full-data candidate with registry caps.

Reuses (no forks): vendor/gems57 evaluate_holdout + holdout + grid writer,
gems/lbmodel, gems/lbm_place, gems/uniqueness_v3.near_fraction,
scripts/run_riesz_locked_experiments.nms_dots.
Outputs: evidence/tipcomp_20261028.json, .cache/tipcomp/candidate_dots.npy
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbmodel as M, lbm_place as P, tipcomp as TC, uniqueness_v3 as U  # noqa
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa
from run_riesz_locked_experiments import nms_dots  # noqa

CACHE = ROOT / ".cache" / "tipcomp"; CACHE.mkdir(parents=True, exist_ok=True)
F9 = ROOT / ".cache" / "focus9_20261028b"
H, W = 3730, 3292

def read01(p: Path) -> np.ndarray:
    with rasterio.open(p) as ds: a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)

def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def edt(mask): return ndi.distance_transform_edt(~mask).astype(np.float32)
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

# ---------- scored set (CLAIMs; deduped by sha at load) ----------
SCORED = [
    ("data/parent_R0_zeros.tif", 0.2778, "GEMSDOE32"),
    ("data/bridge/h27_4_solo.tif", 0.2708, "GEMSDOE28"),
    ("data/bridge/d28.tif", 0.2600, "GEMSDOE25"),
    ("data/bridge/h19_5.tif", 0.1922, "GEMSDOE19"),
    (".cache/focus9_20261028b/GEMSDOE24_peak_d15.tif", 0.2477, "GEMSDOE24"),
    (".cache/focus9_20261028b/GEMSDOE27_peak_gap.tif", 0.2449, "GEMSDOE27"),
    (".cache/focus9_20261028b/GEMSDOE28_peak_h36.tif", 0.2710, "GEMSDOE28"),
    (".cache/focus9_20261028b/GEMSDOE30_peak_d28p.tif", 0.2600, "GEMSDOE30"),
    (".cache/focus9_20261028b/GEMSDOE31_peak_solo.tif", 0.2708, "GEMSDOE31"),
    (".cache/focus9_20261028b/GEMSDOE33_peak_h33d.tif", 0.2632, "GEMSDOE33"),
    (".cache/focus9_20261028b/GEMSDOE36_peak_pinn.tif", 0.2750, "GEMSDOE36"),
    (".cache/focus9_20261028b/GEMSDOE27_h31_0225.tif", 0.2250, "GEMSDOE27"),
    (".cache/focus9_20261028b/GEMSDOE24_gvc1_00859.tif", 0.0859, "GEMSDOE24"),
    (".cache/focus9_20261028b/GSET_G10_h28_01839.tif", 0.1839, "GEMSDOE10"),
    (".cache/focus9_20261028b/GSET_G27_h29_0219.tif", 0.2190, "GEMSDOE27"),
    (".cache/focus9_20261028b/GSET_G48_h59_02296.tif", 0.2296, "GEMSDOE48"),
    (".cache/focus9_20261028b/GSET_G49_gate_02376.tif", 0.2376, "GEMSDOE49"),
    (".cache/focus9_20261028b/GSET_G70_p5_02478.tif", 0.2478, "GEMSDOE70"),
    (".cache/focus9_20261028b/GSET_G73_h73_01917.tif", 0.1917, "GEMSDOE73"),
    (".cache/focus9_20261028b/GSET_G76_ptcf_02343.tif", 0.2343, "GEMSDOE76"),
    (".cache/focus9_20261028b/GSET_G82_h82_01886.tif", 0.1886, "GEMSDOE82"),
    (".cache/focus9_20261028b/GSET_G91_lftg_01823.tif", 0.1823, "GEMSDOE91"),
    (".cache/focus9_20261028b/LOW_G25_h66_00742.tif", 0.0742, "GEMSDOE25"),
    (".cache/focus9_20261028b/LOW_G28_s18_00217.tif", 0.0217, "GEMSDOE28"),
    (".cache/focus9_20261028b/MID_G30_msdb_01462.tif", 0.1462, "GEMSDOE30"),
    ("docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif", 0.0255, "GEMSDOE92"),
]
GSET_FILES = ["GSET_G10_h28_01839.tif","GSET_G27_h29_0219.tif","GEMSDOE27_h31_0225.tif",
    "GSET_G49_gate_02376.tif","GSET_G48_h59_02296.tif","GSET_G70_p5_02478.tif",
    "GSET_G73_h73_01917.tif","GSET_G76_ptcf_02343.tif","GSET_G82_h82_01886.tif","GSET_G91_lftg_01823.tif"]
PEAKS = {  # focus-9 peaks (site -> path, claim)
    "GEMSDOE24": (F9/"GEMSDOE24_peak_d15.tif", 0.2477),
    "GEMSDOE25": (ROOT/"data/bridge/d28.tif", 0.2600),
    "GEMSDOE27": (F9/"GEMSDOE27_peak_gap.tif", 0.2449),
    "GEMSDOE28": (F9/"GEMSDOE28_peak_h36.tif", 0.2710),
    "GEMSDOE30": (F9/"GEMSDOE30_peak_d28p.tif", 0.2600),
    "GEMSDOE31": (F9/"GEMSDOE31_peak_solo.tif", 0.2708),
    "GEMSDOE32": (ROOT/"data/parent_R0_zeros.tif", 0.2778),
    "GEMSDOE33": (F9/"GEMSDOE33_peak_h33d.tif", 0.2632),
    "GEMSDOE36": (F9/"GEMSDOE36_peak_pinn.tif", 0.2750),
}

def main():
    t0 = time.time(); out = {"schema": "gemsdoe92-tipcomp-20261028-v1"}
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    log("footprint", int(foot.sum()), "catalogue", int(cat.sum()))
    h19 = read01(ROOT/"data/bridge/h19_5.tif") > 0
    dcat, dh19 = edt(cat), edt(h19)
    # --- rebuild LBM-v1 cons (<=2px halo count over the 10 G-set dot fields) ---
    cons = np.zeros((H, W), np.int16)
    for fn in GSET_FILES:
        cons += (edt(read01(F9/fn) > 0) <= 2.0)
    log("cons max", int(cons.max()), "frac>=5", float((cons[foot] >= 5).mean()))
    cls = ((np.digitize(dcat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
           + np.digitize(cons, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    scored_mask = foot & ~cat
    cls_sc = np.where(scored_mask, cls, -1)
    K = 90; Ncls = np.bincount(cls_sc[cls_sc >= 0], minlength=K).astype(float)
    # --- design rows for scored set ---
    rows, seen = [], set()
    for rel, claim, site in SCORED:
        p = ROOT / rel; s = sha(p)
        if s in seen: continue
        seen.add(s)
        rows.append(dict(path=rel, claim=claim, site=site, sha256=s, **M.design_row(read01(p), cls_sc, K)))
    y = np.array([r["claim"] for r in rows]); groups = np.array([r["site"] for r in rows])
    A = np.array([r["A"] for r in rows]); m = np.array([r["m"] for r in rows]); n = np.array([r["n"] for r in rows])
    log(f"scored rows={len(rows)} sites={len(set(groups))}")
    # published LBM-v1 beta (128 CLAIMs) reproduction check
    ens = json.loads((ROOT/"evidence/lbm_ensemble_model.json").read_text())
    Xd = M.factor_design((3, 6, 5))
    rho_pub = np.minimum(np.exp(Xd @ np.array(ens["members"]["gset_0.18"]["beta"])), 0.5)
    pred_pub = M.predict(rho_pub, A, m, n, Ncls)
    repro = {rows[i]["path"]: dict(claim=float(y[i]), lbm_v1_published=float(pred_pub[i])) for i in range(len(rows))}
    rmse_pub = float(np.sqrt(np.mean((pred_pub - y) ** 2)))
    log("published-beta RMSE on in-session scored set:", round(rmse_pub, 5),
        " R0 pred:", [round(v["lbm_v1_published"], 4) for k, v in repro.items() if "parent_R0" in k])
    # in-session refit + LOGO
    fit = M.fit_loglinear(A, m, n, y, Ncls, Xd, lam=1e-3)
    logo = np.zeros(len(y))
    for g in np.unique(groups):
        te = groups == g; tr = ~te
        f = M.fit_loglinear(A[tr], m[tr], n[tr], y[tr], Ncls, Xd, lam=1e-3)
        logo[te] = M.predict(np.minimum(np.exp(Xd @ f["beta"]), 0.5), A[te], m[te], n[te], Ncls)
    out["estimator"] = dict(n_rows=len(rows), n_sites=int(len(set(groups))),
        published_beta_rmse_insession=rmse_pub, refit_in_sample_rmse=float(fit["rmse"]),
        refit_logo_rmse=float(np.sqrt(np.mean((logo - y) ** 2))),
        refit_logo_spearman=float(spearmanr(logo, y).statistic), reproduction=repro)
    rho_refit = np.minimum(np.exp(Xd @ fit["beta"]), 0.5)
    np.savez(CACHE/"design.npz", A=A, m=m, n=n, y=y, Ncls=Ncls, rho_pub=rho_pub, rho_refit=rho_refit)

    # --- full-data tip + complement fields ---
    tip_full = TC.tip_continuation_field(cat)
    peak_masks = [read01(p) > 0 for p, _ in PEAKS.values()]
    comp_full = TC.coverage_complement(dh19, peak_masks)
    cons9 = np.zeros((H, W), np.int16)
    for pm in peak_masks: cons9 += (edt(pm) <= 2.0)
    log("tip>0 cells", int((tip_full > 0).sum()), "complement cells", int(comp_full.sum()))

    # ============ E1 + E2: holdout (seeds 20,30) ============
    terms, per_fold, canary_X, canary_y = {}, {}, [], []
    statics = {
        "static_R0_G32peak": (read01(ROOT/"data/parent_R0_zeros.tif") > 0).astype(np.float32),
        "static_D28_G25peak": (read01(ROOT/"data/bridge/d28.tif") > 0).astype(np.float32),
        "static_lbmc1_1027": (read01(ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif") > 0).astype(np.float32),
        "static_rieszlbm2_1028": (read01(ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif") > 0).astype(np.float32),
    }
    rng = np.random.default_rng(20261028)
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        vis = folds[0]["visible"]; known = folds[0]["masked_known"]
        dvis = edt(vis)
        tip_vis = TC.tip_continuation_field(vis)
        g18 = ndi.gaussian_filter(vis.astype(np.float32), 18.0)
        elig = foot & ~known & (dvis > 2.0)
        # R0-recipe control (H19-5 dotted 2.8) + budget
        r0r = nms_dots(np.flatnonzero((h19 & elig).ravel()), (H, W), 2.8, 10**9).astype(np.float32)
        n_r0 = int(r0r.sum())
        # E2 fold-proper surface: tip + continuation corridor, dcat-band law from published beta only
        band = np.where(dvis > 15.0, 1.0, np.where(dvis > 2.0, 0.35, 0.0)).astype(np.float32)
        e2_surf = band * (0.15 + tip_vis + 2.0 * g18 / max(float(g18.max()), 1e-9))
        e2_surf[~elig] = 0.0
        elin = np.flatnonzero(elig.ravel())
        ord2 = elin[np.argsort(e2_surf.ravel()[elin])[::-1]]
        pred_e2 = nms_dots(ord2, (H, W), 2.8, n_r0).astype(np.float32)
        arms = dict(r0_recipe=r0r, e2_tipcomp_foldproper=pred_e2, **statics)
        for nm, arr in arms.items():
            for fold in folds:
                sc, tm = evaluate_holdout.evaluate(arr, fold, foot)
                terms[nm] = tm if nm not in terms else terms[nm] + tm
                per_fold.setdefault(nm, []).append(round(float(sc["dti"]), 6))
        log(f"seed {seed}: n_r0={n_r0} e2 dots={int(pred_e2.sum())}")
        # canary samples: withheld positives vs random scored negatives (per seed, pooled later)
        truth = np.zeros((H, W), bool)
        for fold in folds:
            truth |= (np.asarray(fold["truth"], bool) & np.asarray(fold["region"], bool)
                      & ~np.asarray(fold.get("masked_known", fold["visible"]), bool))
        pos = np.flatnonzero((truth & foot).ravel())
        neg_pool = np.flatnonzero((scored_mask & ~truth & elig).ravel())
        neg = rng.choice(neg_pool, size=min(pos.size * 4, neg_pool.size), replace=False)
        idx = np.concatenate([pos, neg]); yy = np.r_[np.ones(pos.size), np.zeros(neg.size)]
        rho_map = rho_pub[cls]
        feats = np.column_stack([tip_vis.ravel()[idx], dvis.ravel()[idx], g18.ravel()[idx],
                                 rho_map.ravel()[idx], cons9.ravel()[idx].astype(float), e2_surf.ravel()[idx]])
        canary_X.append(feats); canary_y.append(yy)
    CX = np.vstack(canary_X); CY = np.concatenate(canary_y)
    names = ["tip_field_visible", "d_visible", "gauss18_visible", "lbm_v1_rho", "cons9_focus_peaks", "e2_surface"]
    canaries = {}
    for j, nm in enumerate(names):
        a = float(roc_auc_score(CY, CX[:, j])); canaries[nm] = dict(auc=a, sym_auc=max(a, 1 - a))
    out["E1_canaries"] = dict(n_pos=int(CY.sum()), n_neg=int((1 - CY).sum()), features=canaries,
                              pass_le_0p90=bool(all(v["sym_auc"] <= 0.90 for v in canaries.values())))
    summ = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="e2_tipcomp_foldproper")
    out["holdout"] = dict(evaluator="gems57-pooled-hide-v2 (seeds 20,30; 20km block bootstrap 1000)",
                          summary_candidate_e2=summ, per_fold=per_fold)
    log("canaries:", {k: round(v["sym_auc"], 4) for k, v in canaries.items()})
    try:
        log("holdout scores:", {k: round(v["dti"], 5) for k, v in summ["scores"].items()})
    except Exception as e: log("summary keys", list(summ)[:6], e)

    (ROOT/"evidence/tipcomp_20261028.json").write_text(json.dumps(out, indent=2, default=float))  # E1/E2 checkpoint
    # ============ E3: full-data candidate ============
    rho_map_pub = rho_pub[cls].astype(np.float64); rho_map_pub[~scored_mask] = 0.0
    tip_c = tip_full - float(tip_full[scored_mask].mean())
    rho_final = rho_map_pub * np.clip(1.0 + 0.35 * tip_c, 0.65, 1.40) * (1.0 + 0.25 * comp_full)
    eligible = foot & ~cat & (dcat > 2.0)
    rho_final[~eligible] = 0.0
    np.save(CACHE/"rho_final.npy", rho_final.astype(np.float32))
    iso = P.isolated_value(rho_final)
    elin = np.flatnonzero(eligible.ravel())
    cand = np.sort(elin[np.argpartition(-iso[elin], 350_000)[:350_000]])
    # caps: R0, lbmc1, rieszlbm2, focus-9 peaks (dedup vs R0 handled by same mask)
    cap_src = [("R0_G32", ROOT/"data/parent_R0_zeros.tif", 0.62),
               ("lbmc1", ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif", 0.58),
               ("rieszlbm2", ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif", 0.58)]
    for site, (p, _) in PEAKS.items():
        if site not in ("GEMSDOE32",): cap_src.append((site, p, 0.62))
    cols, caps, cap_names = [], [], []
    yy_c, xx_c = np.divmod(cand, W)
    OFF3 = [(dy, dx) for dy in range(-3, 4) for dx in range(-3, 4) if dy*dy + dx*dx <= 9]
    for nm, p, cp in cap_src:
        dots = np.flatnonzero((read01(p) > 0).ravel())
        halo = np.zeros(H * W, bool); dy_, dx_ = np.divmod(dots, W)
        for ddy, ddx in OFF3:
            ry, rx = dy_ + ddy, dx_ + ddx; ok = (ry >= 0) & (ry < H) & (rx >= 0) & (rx < W)
            halo[ry[ok] * W + rx[ok]] = True
        cols.append(halo[cand]); caps.append(cp); cap_names.append(nm)
    member = np.stack(cols, axis=1)
    log("placing… cand", cand.size, "caps", cap_names)
    res = P.place(rho_final, eligible, n_max=60_000, cand=cand, member=member, caps=np.array(caps))
    order = np.asarray(res["order"]); best_n = int(res["best_n"])
    dots_final = np.sort(order[:best_n])
    np.save(CACHE/"candidate_dots.npy", dots_final)
    out["E3_placement"] = dict(best_n=best_n, model_dti_at_best=float(res.get("best_dti", float("nan"))) if "best_dti" in res else None,
                               res_keys=[k for k in res if k != "order"], caps=dict(zip(cap_names, caps)))
    log("best_n", best_n, "res keys", [k for k in res if k != "order"])
    # realised overlaps of final dots vs cap sources
    real = {}
    for nm, p, cp in cap_src:
        real[nm] = float(U.near_fraction(dots_final, np.flatnonzero((read01(p) > 0).ravel()), (H, W)))
    out["E3_realised_cap_overlaps"] = real; log("realised overlaps", {k: round(v, 4) for k, v in real.items()})
    (ROOT/"evidence/tipcomp_20261028.json").write_text(json.dumps(out, indent=2, default=float))
    log(f"done {time.time()-t0:.0f}s -> evidence/tipcomp_20261028.json")

if __name__ == "__main__":
    main()
