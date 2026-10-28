#!/usr/bin/env python3
"""Finalise TIPCOMP candidate: estimates+bootstrap, static holdout, PI-1
uniqueness, writer (shared grid.write_submission, zeros mode), 11 gates,
run card + readiness. Usage: finalise_tipcomp.py DOTS.npy RHO.npy TAG"""
from __future__ import annotations
import hashlib, json, sys, time, zipfile
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]
from gems import lbmodel as M, uniqueness_v3 as U  # noqa
from gems.gates import run_gates, summarise  # noqa
from gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod  # noqa

H, W = 3730, 3292; CACHE = ROOT / ".cache" / "tipcomp"; F9 = ROOT / ".cache" / "focus9_20261028b"
def read01(p):
    with rasterio.open(p) as ds: a = ds.read(1).astype(np.float32)
    return np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
def edt(m): return ndi.distance_transform_edt(~m).astype(np.float32)
def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def main():
    dots_path, rho_path, tag = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
    dots = np.load(dots_path); rho_surf = np.load(rho_path).astype(np.float32)
    grid = grid_mod.load_grid(ROOT / "data" / "bridge"); foot, cat = grid.footprint, grid.catalogue
    cand = np.zeros(H * W, np.float32); cand[dots] = 1.0; cand = cand.reshape(H, W)
    cand[~foot] = 0.0
    assert (cand[cat] == 0).all() and np.isfinite(cand).all() and cand.min() >= 0 and cand.max() <= 1
    # classes + estimates
    h19 = read01(ROOT/"data/bridge/h19_5.tif") > 0; dcat, dh19 = edt(cat), edt(h19)
    GSET = ["GSET_G10_h28_01839.tif","GSET_G27_h29_0219.tif","GEMSDOE27_h31_0225.tif","GSET_G49_gate_02376.tif",
            "GSET_G48_h59_02296.tif","GSET_G70_p5_02478.tif","GSET_G73_h73_01917.tif","GSET_G76_ptcf_02343.tif",
            "GSET_G82_h82_01886.tif","GSET_G91_lftg_01823.tif"]
    cons = np.zeros((H, W), np.int16)
    for fn in GSET: cons += (edt(read01(F9/fn) > 0) <= 2.0)
    cls = ((np.digitize(dcat, [2.01, 15.01]) * 6 + np.digitize(dh19, [0.5, 1.01, 2.01, 3.01, 5.01])) * 5
           + np.digitize(cons, [0.5, 1.5, 2.5, 4.5])).astype(np.int32)
    cls_sc = np.where(foot & ~cat, cls, -1); K = 90
    z = np.load(CACHE/"design.npz"); A, m, n, y, Ncls = z["A"], z["m"], z["n"], z["y"], z["Ncls"]
    Xd = M.factor_design((3, 6, 5))
    targets = {"candidate": cand,
               "R0_G32": (read01(ROOT/"data/parent_R0_zeros.tif") > 0).astype(np.float32),
               "lbmc1": (read01(ROOT/"docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif") > 0).astype(np.float32),
               "rieszlbm2": (read01(ROOT/"docs/downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788-zeros.tif") > 0).astype(np.float32)}
    drows = {nm: M.design_row(a, cls_sc, K) for nm, a in targets.items()}
    est = {nm: dict(n_dots=int((targets[nm] > 0).sum()),
                    published128=float(M.predict(z["rho_pub"], r["A"], r["m"], r["n"], Ncls)[0]),
                    refit26=float(M.predict(z["rho_refit"], r["A"], r["m"], r["n"], Ncls)[0])) for nm, r in drows.items()}
    ev = json.loads((ROOT/"evidence/tipcomp_20261028.json").read_text())
    paths = list(ev["estimator"]["reproduction"].keys())
    import re
    def site_of(p):
        fixed = {"data/parent_R0_zeros.tif": "GEMSDOE32", "data/bridge/h27_4_solo.tif": "GEMSDOE28",
                 "data/bridge/d28.tif": "GEMSDOE25", "data/bridge/h19_5.tif": "GEMSDOE19"}
        if p in fixed: return fixed[p]
        if "listricdip" in p: return "GEMSDOE92"
        mm = re.search(r"GEMSDOE(\d+)|GSET_G(\d+)|LOW_G(\d+)|MID_G(\d+)", p)
        num = next(g for g in mm.groups() if g) if mm else "?"
        return f"GEMSDOE{num}"
    groups = np.array([site_of(p) for p in paths]); uniq = np.unique(groups)
    rng = np.random.default_rng(7); boots = {nm: [] for nm in targets}
    for _ in range(200):
        pick = rng.choice(uniq, size=uniq.size, replace=True)
        idx = np.concatenate([np.flatnonzero(groups == g) for g in pick])
        try: f = M.fit_loglinear(A[idx], m[idx], n[idx], y[idx], Ncls, Xd, lam=1e-3)
        except Exception: continue
        rb = np.minimum(np.exp(Xd @ f["beta"]), 0.5)
        for nm, r in drows.items(): boots[nm].append(float(M.predict(rb, r["A"], r["m"], r["n"], Ncls)[0]))
    for nm in targets:
        v = np.array(boots[nm])
        est[nm]["bootstrap_refit26"] = dict(n=int(v.size), q05=float(np.quantile(v, .05)),
                                            median=float(np.median(v)), q95=float(np.quantile(v, .95)))
    dc = np.array(boots["candidate"]) - np.array(boots["R0_G32"])
    est["candidate_minus_R0_boot"] = dict(median=float(np.median(dc)), q05=float(np.quantile(dc, .05)), p_gt0=float((dc > 0).mean()))
    log("EST", json.dumps(est, indent=1))
    # static holdout
    terms = {}
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        for fold in folds:
            sc, tm = evaluate_holdout.evaluate(cand, fold, foot)
            terms["candidate"] = tm if "candidate" not in terms else terms["candidate"] + tm
    # need a comparator for pooled_summary: reuse E2 terms? use static R0 quickly
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        for fold in folds:
            sc, tm = evaluate_holdout.evaluate(targets["rieszlbm2"], fold, foot)
            terms["rieszlbm2_static"] = tm if "rieszlbm2_static" not in terms else terms["rieszlbm2_static"] + tm
    summ = evaluate_holdout.pooled_summary(terms, draws=1000, seed=520810, candidate="candidate")
    log("STATIC HOLDOUT", {k: round(v["dti"], 6) for k, v in summ["scores"].items()})
    # uniqueness
    reg_files = [p for p in sorted((ROOT/"docs/downloads").glob("*.tif")) + sorted(F9.glob("*.tif")) + sorted((ROOT/"data").rglob("*.tif")) if "gemsdoe92-tipcomp-" not in p.name]  # own interim artifacts excluded (disclosed)
    cand_lin = np.flatnonzero((cand > 0).ravel()); fp_lin = np.flatnonzero(foot.ravel())
    samp = np.sort(np.random.default_rng(42).choice(fp_lin, size=200_000, replace=False))
    cand_s = (cand.ravel()[samp] > 0).astype(np.float32); surf_s = rho_surf.ravel()[samp]
    rows, seen = [], set()
    for p in reg_files:
        s = hashlib.sha256(p.read_bytes()).hexdigest()
        if s in seen: continue
        seen.add(s); a = read01(p); pos = a > 0; npos = int(pos.sum())
        if npos == 0: continue
        if npos / float(foot.sum()) <= 0.20:
            their = np.flatnonzero(pos.ravel()); rep = "dot_field"
            if float((edt(pos) <= 3.0)[foot].mean()) > 0.70:
                v = a.ravel()[fp_lin]; k = min(cand_lin.size, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]; rep = "surface_topN(halo>0.70)"
        else:
            v = a.ravel()[fp_lin]; k = min(cand_lin.size, fp_lin.size); their = fp_lin[np.argpartition(-v, k)[:k]]; rep = "surface_topN"
        rows.append(dict(file=str(p.relative_to(ROOT)), sha256=s, representation=rep, n_positive=npos,
                         overlap_pi1=float(U.near_fraction(cand_lin, np.sort(their), (H, W))),
                         rho_final_sampled=float(spearmanr(cand_s, a.ravel()[samp]).statistic),
                         rho_surface_sampled=float(spearmanr(surf_s, a.ravel()[samp]).statistic)))
    wo = max(rows, key=lambda r: r["overlap_pi1"]); wr = max(rows, key=lambda r: abs(r["rho_final_sampled"]))
    ws = max(rows, key=lambda r: abs(r["rho_surface_sampled"]))
    uniq_out = dict(registry_unique_rasters=len(rows), worst_overlap=dict(value=wo["overlap_pi1"], file=wo["file"]),
                    worst_abs_rho_final=dict(value=abs(wr["rho_final_sampled"]), file=wr["file"]),
                    worst_abs_rho_surface=dict(value=abs(ws["rho_surface_sampled"]), file=ws["file"]),
                    pi1_pass=bool(wo["overlap_pi1"] <= 0.70 and abs(wr["rho_final_sampled"]) <= 0.90 and abs(ws["rho_surface_sampled"]) <= 0.90),
                    rows=rows)
    log("UNIQ", uniq_out["worst_overlap"], uniq_out["worst_abs_rho_final"], uniq_out["worst_abs_rho_surface"], "pass", uniq_out["pi1_pass"])
    # write TIF (temp name -> hash -> final name)
    tmp = ROOT / f"docs/downloads/_tmp_{tag}.tif"
    grid_mod.write_submission(tmp, cand, mode="zeros")
    sha256 = hashlib.sha256(tmp.read_bytes()).hexdigest()
    fname = f"gemsdoe92-tipcomp-{int(dots.size)}dots-20261028-{sha256[:8]}-zeros.tif"
    final = ROOT / "docs/downloads" / fname; tmp.replace(final)
    with zipfile.ZipFile(str(final)[:-4] + ".zip", "w", zipfile.ZIP_DEFLATED) as zf: zf.write(final, fname)
    gates = run_gates(str(final), str(ROOT/"data/bridge/sample_submission.tif"),
                      str(ROOT/"data/bridge/labels.tif"), prune_radius=2, require_submission_encoding=True)
    ok, report = summarise(gates); log(report)
    q05 = est["candidate"]["bootstrap_refit26"]["q05"]
    verdict = "promote" if (ok and uniq_out["pi1_pass"] and q05 > 0.2778) else "negative"
    note = f"TIPCOMP H-92F1: {int(dots.size)} dots; LBM ens x tip-cont x complement; caps vs focus9+priors; MODEL pub128 {est['candidate']['published128']:.3f}."
    card = dict(schema="gemsdoe92-run-card-v3", created_utc="2026-10-28", lane=f"TIPCOMP H-92F1 ({tag})",
        hypothesis="Unmapped faults concentrate in catalogue tip-continuation fans and in 300m-kernel coverage gaps left by fixed-spacing dotting of the H19-5 ridge; modulating a claim-fitted truth density by a visible-catalogue tip field and a focus-9 coverage-complement boost beats R0 (0.2778 CLAIM) while staying PI-1-unique.",
        mechanism="Ensemble LBM density sqrt(rho_published128*rho_refit26) x (1+0.35*tip) x (1+0.25*complement); exact lazy-greedy expected-DTI placement (gems/lbm_place) with 3px caps vs priors/focus-9 peaks/offenders; binary {0,1} dots, d_cat>2px.",
        named_non_fault_mimic="Map-sheet/compilation edge truncations and road/stream line-ends mis-digitised as fault tips; canyon-rim skeleton spurs on the H19-5 ridge.",
        raster=dict(file=f"docs/downloads/{fname}", zip=f"docs/downloads/{fname[:-4]}.zip", sha256=sha256,
                    bytes=final.stat().st_size, n_dots=int(dots.size)),
        raster_sha256=sha256, submission_name=f"gemsdoe92-tipcomp-{int(dots.size)}d-{sha256[:8]}",
        note=note[:140], note_chars=len(note[:140]),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version="gems57-pooled-hide-v2",
                         withheld_positive_pixels=22663, static_candidate=summ["scores"]["candidate"],
                         foldproper_e2=ev["holdout"]["summary_candidate_e2"]["scores"]["e2_tipcomp_foldproper"],
                         r0_recipe_control=ev["holdout"]["summary_candidate_e2"]["scores"]["r0_recipe"],
                         paired_e2_vs_r0_recipe=ev["holdout"]["summary_candidate_e2"]["paired_differences"]["r0_recipe"]),
        canaries=ev["E1_canaries"], model_estimate=dict(evidence_class="MODEL (not an organizer score)", **est),
        correlation_overlap_vs_registry=uniq_out,
        validator_output=dict(gates_ok=bool(ok), report=report),
        verdict=verdict, submission_eligible=bool(verdict == "promote"))
    (ROOT/f"docs/downloads/gemsdoe92-tipcomp-{int(dots.size)}dots-20261028-{sha256[:8]}_run_card.json").write_text(json.dumps(card, indent=2, default=float))
    (ROOT/f"evidence/tipcomp_{tag}_final.json").write_text(json.dumps(dict(est=est, static_holdout=summ, uniq={k: v for k, v in uniq_out.items() if k != "rows"}), indent=2, default=float))
    log("VERDICT", verdict, fname, sha256)

if __name__ == "__main__":
    main()
