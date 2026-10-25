#!/usr/bin/env python3
"""ALI lane, step 0: match owner-reported scores (ledger/site_scores_claimed_20261025.csv, CLAIMs)
to exact blobs of the synced public registry (filename stem == submission name; same-site preferred).
Ambiguous matches (candidates disagreeing on scored pixels) and grid mismatches are excluded, never guessed.
Output: .cache/work/scored_table.json
"""
import json, csv, numpy as np, rasterio, hashlib
from scipy import ndimage
from scipy.spatial import cKDTree
REG = ".cache/gemsdoe_public_registry/"
inv = json.load(open(REG+'repo_inventory.json'))
paths = [(r['repo'], t['path'], t['sha'], t['size']) for r in inv for t in r['tifs']]
rows = list(csv.DictReader(open('ledger/site_scores_claimed_20261025.csv', encoding='utf-8')))
extra = []  # the three 2026-10-25 claims are now rows of the ledger CSV
claims = [(r['site'].strip(), r['submission_name'].strip(), r['score'].strip()) for r in rows if r['submission_name'].strip()]
claims += extra
with rasterio.open("data/bridge/sample_submission.tif") as ds:
    foot = np.isfinite(ds.read(1)); T = ds.transform; crs = ds.crs
with rasterio.open("data/bridge/existing_faults.tif") as ds:
    cat = ds.read(1) == 1
dcat = ndimage.distance_transform_edt(~cat).astype(np.float32)
scored = foot & ~cat
def load(sha):
    with rasterio.open(REG+sha+".tif") as ds:
        if ds.count != 1 or ds.shape != foot.shape or ds.transform != T: return None, "grid_mismatch"
        a = ds.read(1).astype(np.float32)
    return a, None
r0 = load_r0 = None
def dots_of(a):
    v = np.where(np.isfinite(a), a, 0.0)
    v = np.where(scored, v, 0.0)
    return v
out = []
for site, name, score in claims:
    cands = [p for p in paths if p[1].split('/')[-1].rsplit('.',1)[0] == name]
    if not cands: cands = [p for p in paths if name in p[1].split('/')[-1]]
    same = [p for p in cands if p[0].lower()==site.lower()]
    sel = same or cands
    shas = sorted({p[2] for p in sel})
    rec = {"site": site, "name": name, "score_claim": float(score), "candidates": [ {"repo":p[0],"path":p[1],"sha1":p[2]} for p in sel]}
    if not shas:
        rec["status"] = "no_registry_match"; out.append(rec); continue
    vals = []
    for s in shas:
        a, err = load(s)
        if a is None: continue
        vals.append((s, a))
    if not vals:
        rec["status"] = "grid_mismatch"; out.append(rec); continue
    # check candidates agree on scored pixels
    base = dots_of(vals[0][1])
    agree = all(np.array_equal(dots_of(a), base) for _, a in vals[1:])
    rec["candidates_agree_on_scored_pixels"] = bool(agree)
    if not agree:
        rec["status"] = "ambiguous_candidates"; out.append(rec); continue
    a = vals[0][1]
    rec["sha1"] = vals[0][0]
    fin = np.isfinite(a)
    rec["nan_inside_footprint"] = int((~fin & foot).sum())
    rec["min"] = float(np.nanmin(a)); rec["max"] = float(np.nanmax(a))
    v = base
    pos = v > 0
    rec["n_pos_scored"] = int(pos.sum()); rec["sum_p_scored"] = float(v.sum())
    u = np.unique(v[pos]) if pos.any() else np.array([])
    rec["n_unique_pos_values"] = int(len(u))
    rec["binary"] = bool(len(u) <= 1)
    rec["status"] = "ok"
    out.append(rec)
json.dump(out, open(".cache/work/scored_table.json","w"), indent=1)
ok = [r for r in out if r.get("status")=="ok"]
print("ok", len(ok), "of", len(out))
from collections import Counter
print(Counter(r["status"] for r in out))
for r in sorted(ok, key=lambda r: -r["score_claim"])[:200]:
    print(f'{r["score_claim"]:.4f} {r["site"]:10s} n={r["n_pos_scored"]:7d} S={r["sum_p_scored"]:10.1f} bin={r["binary"]} nanin={r["nan_inside_footprint"]} {r["name"][:60]}')
