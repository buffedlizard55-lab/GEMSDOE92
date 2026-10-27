"""GAPBRIDGE lane: dual-physics coincidence surface + anti-registry dotted emission.
Surface S = geometric mean of rank-normalised gradients: RTP tilt edge (b2), MT cond gradient (b17),
basement-depth gradient (b15), det-elev slope-break (b19 local contrast). No catalogue feature in S.
Holdout: quadrant hide-and-recover via vendor gems57 (buffered component draw), pooled DTI.
Emission: greedy Poisson-disc >=2.8px, >2px off catalogue, budget 37654. Two arms:
 plain (top S) and anti (also >3px from R0+d28+solo dots). Controls: R0 dots, random-in-footprint."""
import sys, json, hashlib
from pathlib import Path

# This historical script previously built a surface, wrote arrays and placed
# dots at import time, before any registry check. Stop before those side effects
# under the binding literal witness; importing it is not a safe library API.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
from gems57.uniqueness import stop_historical_runner
stop_historical_runner('GAPBRIDGE')

import numpy as np, rasterio
from scipy.ndimage import distance_transform_edt, binary_dilation, uniform_filter
from gems57 import evaluate_holdout, holdout as H
from gems57.grid import Grid

def load(p,b=1):
    with rasterio.open(p) as ds: return ds.read(b)
lab=load('data/bridge/labels.tif'); foot=lab>=0; known=lab==1
tf='.cache/gems_inputs/training_features.tif'
def band(i):
    a=load(tf,i).astype(np.float32); a[~foot]=np.nan; return a
def gradmag(a):
    gy,gx=np.gradient(np.nan_to_num(a,nan=np.nanmedian(a))); return np.hypot(gx,gy).astype(np.float32)
def rank01(a):
    v=a[foot & np.isfinite(a)]; order=np.argsort(np.argsort(v)); out=np.zeros(a.shape,np.float32)
    out[foot & np.isfinite(a)]=order/max(len(order)-1,1); return out
print('building surface...')
rtp=band(2); f_rtp=rank01(gradmag(rtp))
f_mt=rank01(gradmag(band(17))); f_base=rank01(gradmag(band(15)))
slope=band(19); loc=np.log1p(np.maximum(slope,0)); f_topo=rank01(np.abs(loc-uniform_filter(np.nan_to_num(loc,nan=0.),size=9)))
S=((f_rtp+0.01)*(f_mt+0.01)*(f_base+0.01)*(f_topo+0.01))**0.25
np.save('/tmp/work/S.npy',S)
# leakage canary: AUC of each feature vs known faults (must be <=0.90)
from sklearn.metrics import roc_auc_score
rng=np.random.default_rng(0); idx=np.argwhere(foot); sel=idx[rng.choice(len(idx),400000,replace=False)]
y=known[sel[:,0],sel[:,1]].astype(int)
can={}
for nm,f in [('rtp_grad',f_rtp),('mt_grad',f_mt),('base_grad',f_base),('topo_break',f_topo),('S_geomean',S)]:
    can[nm]=round(float(roc_auc_score(y,f[sel[:,0],sel[:,1]])),4)
print('CANARIES',can)
dist_cat=distance_transform_edt(~known)
r0=load('data/parent_R0_zeros.tif')>0; d28=load('data/bridge/d28.tif')>0; solo=load('data/bridge/h27_4_solo.tif')>0
reg=r0|d28|solo; dist_reg=distance_transform_edt(~reg)
def emit(pool_mask, score, n=37654, minsep=2.8):
    ys,xs=np.nonzero(pool_mask); sc=score[ys,xs]; o=np.argsort(-sc); ys,xs=ys[o],xs[o]
    # greedy separation via blocked grid
    keep=np.zeros(score.shape,bool); blocked=np.zeros(score.shape,bool); cnt=0
    r=int(np.ceil(minsep))
    for y,x in zip(ys,xs):
        if blocked[y,x]: continue
        keep[y,x]=True; cnt+=1
        blocked[max(0,y-r):y+r+1, max(0,x-r):x+r+1]=True; blocked[y,x]=True
        if cnt>=n: break
    return keep
base_pool=foot & (dist_cat>2)
plain=emit(base_pool,S); anti=emit(base_pool & (dist_reg>3),S)
print('plain',int(plain.sum()),'anti',int(anti.sum()))
np.save('/tmp/work/plain.npy',plain); np.save('/tmp/work/anti.npy',anti)
# uniqueness vs dotted registry (operative: dot fields)
def fwd(a,b): return float((binary_dilation(b,iterations=3)&a).sum()/max(a.sum(),1))
for nm,a in [('plain',plain),('anti',anti)]:
    print(nm,'overlap R0/d28/solo/h19:',[round(fwd(a,x),4) for x in [r0,d28,solo,load('data/bridge/h19_5.tif')>0]])
# Holdout: buffered component draw folds
grid=Grid(footprint=foot, known=known)
ctx=H.buffered_component_draw(grid,seed=20,hide_frac=0.20,buffer_px=3) if hasattr(H,'buffered_component_draw') else None
print('ctx type',type(ctx))
json.dump({'canaries':can},open('/tmp/work/canaries.json','w'))
