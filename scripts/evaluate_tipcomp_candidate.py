#!/usr/bin/env python3
"""Pass-2 evaluation of the TIPCOMP E3 candidate: MODEL estimates (+ grouped
bootstrap), static holdout re-score, PI-1 uniqueness vs local registry."""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbmodel as M, uniqueness_v3 as U  # noqa
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa

H, W = 3730, 3292
CACHE = ROOT / ".cache" / "tipcomp"
def read01(p):
    with rasterio.open(p) as ds: a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
def edt(m): return ndi.distance_transform_edt(~m).astype(np.float32)
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def main():
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    h19 = read01(ROOT/"data/bridge/h19_5.tif") > 0
    dcat, dh19 = edt(cat), edt(h19)
    F9 = ROOT / ".cache" / "focus9_20261028b"
    GSET = ["GSET_G10_h28_01839.tif","GSET_G27_h29_0219.tif","GEMSDOE27_h31_0225.tif","GSET_G49_gate_02376.tif",
            "GSET_G48_h59_02296.tif","GSET_G70_p5_02478.tif","GSET_G73_h73_01917.tif","GSET_G76_ptcf_02343.tif",
            "GSET_G82_h82_01886.tif","GSET_G91_lftg_01823.tif"]
    cons = np.zeros((H, W), np.int16)
    for fn in GSET: cons += (edt(read01(F9/fn) > 0) <= 2.0)
    cls = ((np.digitize(dcat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
           + np.digitize(cons, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    cls_sc = np.where(foot & ~cat, cls, -1); K = 90
    z = np.load(CACHE/"design.npz"); A, m, n, y, Ncls = z["A"], z["m"], z["n"], z["y"], z["Ncls"]
    rho_pub, rho_refit = z["rho_pub"], z["rho_refit"]
    Xd = M.factor_design((3, 6, 5))
    dots = np.load(CACHE/"candidate_dots.npy")
    cand = np.zeros(H * W, np.float32); cand[dots] = 1.0; cand = cand.reshape(H, W)
    out = {"n_dots": int(dots.size)}
    targets = {"candidate_tipcomp": cand,
               "R0_G32": (read01(ROOT/"data/parent_R0_zeros.tif") > 0).astype(np.float32),
               "lbmc1": (read01(ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif") > 0).astype(np.float32),
               "rieszlbm2": (read01(ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif") > 0).astype(np.float32)}
    est = {}
    drows = {}
    for nm, arr in targets.items():
        r = M.design_row(arr, cls_sc, K); drows[nm] = r
        est[nm] = dict(n_dots=int((arr > 0).sum()),
                       lbm_v1_published_beta=float(M.predict(rho_pub, r["A"], r["m"], r["n"], Ncls)[0]),
                       lbm_refit_26rows=float(M.predict(rho_refit, r["A"], r["m"], r["n"], Ncls)[0]))
    log("estimates:", json.dumps(est, indent=1))
    # grouped (site) bootstrap of the 26-row refit
    ev = json.loads((ROOT/"evidence/tipcomp_20261028.json").read_text())
    # site groups aligned with design rows: rebuild order from SCORE list in runner (same order, dedup by sha)
    sys.path.insert(0, str(ROOT/"scripts"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("rt", ROOT/"scripts/run_tipcomp_20261028.py")
    # avoid executing main: just parse SCORED via exec of the top part is overkill -> use reproduction keys order
    sites_by_path = {}
    for rel, site in [
        ("data/parent_R0_zeros.tif","GEMSDOE32"),("data/bridge/h27_4_solo.tif","GEMSDOE28"),("data/bridge/d28.tif","GEMSDOE25"),
        ("data/bridge/h19_5.tif","GEMSDOE19")]:
        sites_by_path[rel] = site
    # design row order == reproduction dict order (insertion order preserved)
    paths = list(ev["estimator"]["reproduction"].keys())
    def site_of(p):
        import re
        mm = re.search(r"(GEMSDOE\d+|GSET_G(\d+)|LOW_G(\d+)|MID_G(\d+))", p)
        if p in sites_by_path: return sites_by_path[p]
        if "listricdip" in p: return "GEMSDOE92"
        if mm:
            g = mm.group(0)
            if g.startswith("GSET_G"): return "GEMSDOE" + g.split("_G")[1]
            if g.startswith("LOW_G") or g.startswith("MID_G"): return "GEMSDOE" + g.split("_G")[1]
            return g
        return p
    groups = np.array([site_of(p) for p in paths])
    log("groups:", list(zip(paths, groups))[:5], "n=", len(groups), "y=", len(y))
    rng = np.random.default_rng(7); uniq = np.unique(groups)
    boots = {nm: [] for nm in targets}
    for b in range(200):
        pick = rng.choice(uniq, size=uniq.size, replace=True)
        idx = np.concatenate([np.flatnonzero(groups == g) for g in pick])
        try:
            f = M.fit_loglinear(A[idx], m[idx], n[idx], y[idx], Ncls, Xd, lam=1e-3)
        except Exception:
            continue
        rho_b = np.minimum(np.exp(Xd @ f["beta"]), 0.5)
        for nm, r in drows.items():
            boots[nm].append(float(M.predict(rho_b, r["A"], r["m"], r["n"], Ncls)[0]))
    for nm in targets:
        v = np.array(boots[nm])
        est[nm]["bootstrap_refit"] = dict(n=int(v.size), q05=float(np.quantile(v, 0.05)),
            median=float(np.median(v)), q95=float(np.quantile(v, 0.95)))
    dc = np.array(boots["candidate_tipcomp"]) - np.array(boots["R0_G32"])
    est["candidate_minus_R0"] = dict(median=float(np.median(dc)), q05=float(np.quantile(dc, 0.05)),
                                     p_gt0=float((dc > 0).mean()))
    out["MODEL_estimates"] = est
    log("bootstrap candidate:", est["candidate_tipcomp"]["bootstrap_refit"], "delta:", out["MODEL_estimates"]["candidate_minus_R0"])

    # --- static holdout of candidate + riesz zero check ---
    terms = {}
    for nm in ("candidate_tipcomp", "rieszlbm2"):
        for seed in (20, 30):
            folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
            for fold in folds:
                sc, tm = evaluate_holdout.evaluate(targets[nm], fold, foot)
                terms[nm] = tm if nm not in terms else terms[nm] + tm
    summ = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="candidate_tipcomp")
    out["static_holdout"] = summ
    log("static holdout:", {k: round(v["dti"], 6) for k, v in summ["scores"].items()})
    # direct check: riesz dots within 3px of pooled withheld truth
    truth = np.zeros((H, W), bool)
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        for fold in folds: truth |= np.asarray(fold["truth"], bool)
    rz = targets["rieszlbm2"] > 0
    out["riesz_zero_check"] = dict(pooled_truth_px=int(truth.sum()),
        riesz_dots_within_3px_of_truth=int((rz & (edt(truth) <= 3.0)).sum()),
        candidate_dots_within_3px_of_truth=int(((cand > 0) & (edt(truth) <= 3.0)).sum()))
    log("zero check:", out["riesz_zero_check"])

    # --- PI-1 uniqueness vs local registry ---
    reg_files = sorted((ROOT/"docs/downloads").glob("*.tif")) + sorted(F9.glob("*.tif")) + \
                sorted((ROOT/"data").rglob("*.tif"))
    cand_lin = np.flatnonzero((cand > 0).ravel())
    rho_surf = np.load(CACHE/"rho_final.npy").astype(np.float32)
    fp_lin = np.flatnonzero(foot.ravel())
    rng2 = np.random.default_rng(42)
    samp = np.sort(rng2.choice(fp_lin, size=200_000, replace=False))
    cand_samp = (cand.ravel()[samp] > 0).astype(np.float32)
    surf_samp = rho_surf.ravel()[samp]
    rows, worst_o, worst_r, worst_s = [], (0, ""), (0, ""), (0, "")
    seen_sha = {}
    for p in reg_files:
        s = hashlib.sha256(p.read_bytes()).hexdigest()
        if s in seen_sha: continue
        seen_sha[s] = str(p)
        a = read01(p); pos = a > 0
        npos = int(pos.sum())
        if npos == 0: continue
        support = npos / float(foot.sum())
        if support <= 0.20:
            their = np.flatnonzero(pos.ravel()); rep = "dot_field"
            halo_frac = float((edt(pos) <= 3.0)[foot].mean())
            if halo_frac > 0.70:
                v = a.ravel()[fp_lin]; k = min(cand_lin.size, fp_lin.size)
                their = fp_lin[np.argpartition(-v, k)[:k]]; rep = "surface_topN(halo>0.70)"
        else:
            v = a.ravel()[fp_lin]; k = min(cand_lin.size, fp_lin.size)
            their = fp_lin[np.argpartition(-v, k)[:k]]; rep = "surface_topN"; halo_frac = None
        ov = float(U.near_fraction(cand_lin, np.sort(their), (H, W)))
        rho_c = float(spearmanr(cand_samp, a.ravel()[samp]).statistic)
        rho_s = float(spearmanr(surf_samp, a.ravel()[samp]).statistic)
        r = dict(file=str(p.relative_to(ROOT)), sha256=s, representation=rep, n_positive=npos,
                 overlap_pi1=ov, rho_final_sampled=rho_c, rho_surface_sampled=rho_s)
        rows.append(r)
        if ov > worst_o[0]: worst_o = (ov, r["file"])
        if abs(rho_c) > worst_r[0]: worst_r = (abs(rho_c), r["file"])
        if abs(rho_s) > worst_s[0]: worst_s = (abs(rho_s), r["file"])
    out["uniqueness"] = dict(registry_unique_rasters=len(rows), worst_overlap=dict(value=worst_o[0], file=worst_o[1]),
        worst_abs_rho_final=dict(value=worst_r[0], file=worst_r[1]),
        worst_abs_rho_surface=dict(value=worst_s[0], file=worst_s[1]),
        pi1_pass=bool(worst_o[0] <= 0.70 and worst_r[0] <= 0.90 and worst_s[0] <= 0.90), rows=rows)
    log("uniqueness worst:", worst_o, worst_r, worst_s, "n=", len(rows))
    ev.update({k: out[k] for k in ("MODEL_estimates", "static_holdout", "riesz_zero_check", "uniqueness")})
    ev["candidate_n_dots"] = out["n_dots"]
    (ROOT/"evidence/tipcomp_20261028.json").write_text(json.dumps(ev, indent=2, default=float))
    log("written evidence/tipcomp_20261028.json")

if __name__ == "__main__":
    main()
