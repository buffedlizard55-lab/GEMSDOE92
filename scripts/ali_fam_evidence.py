#!/usr/bin/env python3
"""ALI lane: model-free check - share of each scored raster's far dots (d_cat>3) in top FAM strata vs its CLAIM score."""
import sys, json, numpy as np, rasterio
from scipy.stats import spearmanr
sys.path.insert(0,'scripts')
from ali_place import base_maps
foot, cat, fam, dcat = base_maps()
scored = foot & ~cat
thr = json.load(open('.cache/work/ali_design.json'))['meta']['fam_thresholds']   # 0.70,0.90,0.96,0.985,0.995 quantiles
print("FAM thresholds", [round(t,3) for t in thr])
REG='.cache/gemsdoe_public_registry/'
tab=[r for r in json.load(open('.cache/work/scored_table.json')) if r.get('status')=='ok']
seen=set(); rows=[]
for r in tab:
    if r['sha1'] in seen: continue
    seen.add(r['sha1'])
    with rasterio.open(REG+r['sha1']+'.tif') as ds: a=ds.read(1)
    m=(np.nan_to_num(a)>0)&scored
    far=m&(dcat>3)
    f=fam[far]
    n=far.sum()
    if n==0: continue
    rows.append(dict(name=r['name'], lb=r['score_claim'], n=int(m.sum()), nfar=int(n), top05=float((f>=thr[4]).mean()), top15=float((f>=thr[3]).mean()), top4=float((f>=thr[2]).mean()), top10=float((f>=thr[1]).mean()), medfam=float(np.median(f))))
lb=np.array([r['lb'] for r in rows])
for k in ['top05','top15','top4','top10','medfam']:
    v=np.array([r[k] for r in rows]); print(k, "spearman vs LB:", round(spearmanr(v,lb)[0],3))
rows.sort(key=lambda r:-r['lb'])
for r in rows[:30]: print(f"{r['lb']:.4f} nfar={r['nfar']:6d} top0.5%={r['top05']:.3f} top1.5%={r['top15']:.3f} top4%={r['top4']:.3f} top10%={r['top10']:.3f} {r['name'][:45]}")
print("... max top0.5% share among all scored:", max(r['top05'] for r in rows), " max top1.5%:", max(r['top15'] for r in rows), " max top4%:", max(r['top4'] for r in rows))
json.dump(rows, open('.cache/work/fam_evidence.json','w'))
