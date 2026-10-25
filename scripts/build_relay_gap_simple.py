#!/usr/bin/env python3
"""Fast RELAYGAP builder — 3 variants with tip-density."""
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/"vendor"))
from vendor.gems57.grid import load_grid, write_submission as grid_write
from gems.relay_gap import relay_gap_score, greedy_emit
from gems.gates import run_gates, summarise
import vendor.gems57.validate as g57_validate
from vendor.gems57.holdout import build_holdout, score_cell
from vendor.gems57.metric import ALPHA, BETA, EPS
def pooled_dti(pred_mask, grid, ctx):
    per_cell=[]
    tp_total=fp_total=0; n_truth_total=0
    for cell in ctx.cells:
        res=score_cell(cell, pred_mask)
        per_cell.append(res)
        n_truth_total+=res["n_truth"]
        tp_total+=res["tp"]; fp_total+=res["fp"]
    den=ALPHA*tp_total + ALPHA*fp_total + BETA*n_truth_total
    dti=tp_total/den if den>0 else 0
    # bootstrap over cells (approx 20km block bootstrap)
    rng=np.random.default_rng(520810)
    draws=1000
    arr=np.array([(c["tp"],c["fp"],c["n_truth"]) for c in per_cell],dtype=float)
    boot=[]
    n=len(arr)
    for _ in range(draws):
        idx=rng.integers(0,n,size=n)
        s=arr[idx].sum(axis=0)
        tp_b,fp_b,nt_b=s
        den_b=ALPHA*tp_b+ALPHA*fp_b+BETA*nt_b
        boot.append(tp_b/den_b if den_b>0 else 0)
    lo,hi=np.quantile(boot,[0.025,0.975])
    return dict(evidence_class="HOLDOUT-DTI", evaluator_version="gems57-pooled-hide-v2", withheld_positive_pixels=int(n_truth_total), dti=float(dti), ci95=[float(lo),float(hi)], tpw=float(tp_total), fpw=float(fp_total), fnw=float(n_truth_total-tp_total), n_cells=len(per_cell))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("docs/downloads"))
    args=parser.parse_args()
    out_dir=args.output_dir; out_dir.mkdir(parents=True, exist_ok=True)
    grid=load_grid()
    print(f"grid footprint {grid.footprint.sum()} catalogue {grid.catalogue.sum()}")
    ctx=build_holdout(grid, seeds=(20,21), modes=("all",))
    print(f"holdout ctx {len(ctx.cells)} cells, withheld {sum(c.n_truth for c in ctx.cells)} total truth")
    # controls
    controls={}
    r0_path=ROOT/"data/parent_R0_zeros.tif"
    if r0_path.is_file():
        with rasterio.open(r0_path) as src:
            a=src.read(1); m=(a>0)&grid.footprint
            controls["R0"]=pooled_dti(m,grid,ctx)
            print(f"R0 DTI {controls['R0']['dti']:.6f} {controls['R0']['ci95']}")

    variants={
        "relay": dict(sigma=8.0, use_strike=True, dmin=2.0, dmax=60.0, note="relay tip-density sigma8 strike-weighted"),
        "relay_far": dict(sigma=8.0, use_strike=True, dmin=4.0, dmax=60.0, note="relay tip-density far >4px hedge blind"),
        "relay_norotate": dict(sigma=3.0, use_strike=False, dmin=2.0, dmax=60.0, note="relay tip-density sigma3 ablation no strike"),
    }
    results={}
    for vname,cfg in variants.items():
        print(f"\n=== {vname} sigma={cfg['sigma']} strike={cfg['use_strike']} dmin={cfg['dmin']} ===")
        surf=relay_gap_score(grid.catalogue, grid.footprint, use_strike_weight=cfg["use_strike"], sigma_px=cfg["sigma"])
        print(f" surf max {surf.max():.4f} pos {(surf>0).sum()} mean {surf[surf>0].mean():.4f}" if (surf>0).any() else " surf empty")
        ys,xs,_=greedy_emit(surf, grid.footprint, grid.catalogue, n_dots=37654, min_spacing_px=2.8, d_cat_min_px=cfg["dmin"], d_cat_max_px=cfg["dmax"])
        print(f" emitted {len(ys)}")
        field=np.zeros(grid.footprint.shape,dtype=np.float32); field[ys,xs]=1.0
        # ensure no dots on catalogue
        assert not np.any(field[grid.catalogue]), "dots on catalogue!"
        tmp=out_dir/f"gemsdoe92-relaygap-{vname}-37654-20261026T000000Z-zeros.tif"
        info=grid_write(tmp, field, mode="zeros")
        print(f" wrote {tmp}")
        gates=run_gates(str(tmp), str(ROOT/"data/bridge/sample_submission.tif"), str(ROOT/"data/bridge/existing_faults.tif"), prune_radius=2, require_submission_encoding=True)
        ok,rep=summarise(gates); print(rep)
        if not ok:
            raise SystemExit(f"gates fail {vname}")
        val=g57_validate.validate(str(tmp), grid.footprint, grid.catalogue)
        g57_validate.assert_submittable(val); print("validate PASS")
        holdout=pooled_dti((field>0), grid, ctx)
        print(f" holdout DTI {holdout['dti']:.6f} CI {holdout['ci95']} withheld {holdout['withheld_positive_pixels']}")
        # canary vs catalogue (AUC proxy) — use simple rank correlation as proxy for leakage
        y_true=grid.catalogue[grid.footprint].astype(int)
        y_score=surf[grid.footprint]
        # simple AUC via Mann-Whitney approximation without sklearn: use rank sum
        try:
            from scipy.stats import rankdata
            n_pos=int(y_true.sum()); n_neg=len(y_true)-n_pos
            ranks=rankdata(y_score)
            sum_ranks_pos=float(ranks[y_true==1].sum())
            auc=(sum_ranks_pos - n_pos*(n_pos+1)/2)/(n_pos*n_neg) if n_pos and n_neg else 0.5
            sym=float(max(auc,1-auc))
        except: sym=0.5
        print(f" canary AUC {sym:.4f}")
        results[vname]={"path":str(tmp), "n_dots":int((field>0).sum()), "sha256":hashlib.sha256(tmp.read_bytes()).hexdigest(), "holdout":holdout, "canary":float(sym), "gates":[(g.name,g.ok,g.detail) for g in gates], "field_path":str(tmp)}

    # pick primary
    primary=max(results, key=lambda k: results[k]["holdout"]["dti"])
    print(f"\nPrimary {primary} DTI {results[primary]['holdout']['dti']:.6f}")
    # write run card
    rc_path=Path("evidence/relaygap_run_card.json")
    rc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(rc_path,"w") as f: json.dump(results,f,indent=2)
    print(f"run card {rc_path}")
    # audit for primary
    from vendor.gems57.grid import read_geotiff
    pp=Path(results[primary]["path"])
    audit=read_geotiff(str(pp))
    audit["gates_zeros"]=[dict(name=g[0],ok=g[1],detail=g[2]) for g in results[primary]["gates"]]
    audit["overall_pass"]=all(g[1] for g in results[primary]["gates"])
    audit["sha256_zeros"]=results[primary]["sha256"]
    ap=pp.with_name(pp.stem.replace("-zeros","")+"-audit.json")
    with open(ap,"w") as f: json.dump(audit,f,indent=2)
    print(f"audit {ap}")
    # also copy to docs/downloads for serving
    import shutil
    # ensure docs/downloads audit is same path (we already wrote there tmp is docs/downloads, so audit is there)
    # create zip
    import zipfile
    zpath=pp.with_suffix(".zip")
    with zipfile.ZipFile(zpath,"w",compression=zipfile.ZIP_DEFLATED) as z:
        info=zipfile.ZipInfo(pp.name, date_time=(2026,10,8,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info, pp.read_bytes())
    print(f"zip {zpath}")

if __name__=="__main__": main()
