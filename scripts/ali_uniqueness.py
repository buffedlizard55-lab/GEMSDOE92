#!/usr/bin/env python3
"""ALI lane: registry uniqueness for one or more candidate dot sets.

Against EVERY TIFF blob in the synced public registry
(.cache/gemsdoe_public_registry, 102 buffedlizard55-lab/*GEMSDOE* repos) plus
this repo's own docs/downloads, compute with the shared vendor helpers:
  * literal forward overlap  = share of my dots within 3 px of their positive pixels
    (vendor/gems57/uniqueness.py::_near, exact disk);
  * matched-budget forward overlap (vendor dual_overlap) for rasters with more than
    150,000 positive pixels (top-K by value, K = my dot count);
  * Spearman rank correlation over the footprint (uniform 1,000,000-pixel
    subsample, exact recomputation for any |rho| > 0.75);
  * halo coverage of their support (share of the scored domain inside their 3 px halo;
    the expected overlap of a uniformly random candidate).
The binding decision is written by scripts/ali_verdict.py, not here.
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path
import numpy as np, rasterio
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.uniqueness import _near, matched_budget_support, DOT_FIELD_MAX_SUPPORT  # noqa: E402

REG = ROOT / ".cache" / "gemsdoe_public_registry"


def spearman_fast(a_sub, b_sub):
    return float(spearmanr(a_sub, b_sub).statistic)


def main():
    cands = {}
    for arg in sys.argv[1:]:
        name, path = arg.split("=", 1)
        with rasterio.open(path) as ds:
            cands[name] = ds.read(1)
    with rasterio.open(ROOT / "data/bridge/sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    with rasterio.open(ROOT / "data/bridge/existing_faults.tif") as ds:
        cat = ds.read(1) == 1
    scored = foot & ~cat
    rng = np.random.default_rng(92)
    sub = rng.choice(np.flatnonzero(foot.ravel()), 1_000_000, replace=False)
    mine = {n: (np.nan_to_num(a) > 0) & foot for n, a in cands.items()}
    mine_sub = {n: np.where(foot, np.nan_to_num(a), 0).ravel()[sub] for n, a in cands.items()}
    inv = json.load(open(REG / "repo_inventory.json"))
    entries = {}
    for r in inv:
        for t in r["tifs"]:
            entries.setdefault(t["sha"], []).append(f"{r['repo']}:{t['path']}")
    for p in sorted((ROOT / "docs" / "downloads").glob("*.tif")):
        entries.setdefault("local:" + p.name, []).append(f"GEMSDOE92(local):{p.relative_to(ROOT)}")
    rows, t0 = [], time.time()
    for i, (sha, paths) in enumerate(sorted(entries.items())):
        f = (ROOT / "docs" / "downloads" / sha[6:]) if sha.startswith("local:") else REG / f"{sha}.tif"
        row = dict(blob=sha, paths=paths[:3], n_paths=len(paths))
        try:
            with rasterio.open(f) as ds:
                if ds.shape != foot.shape or ds.count < 1:
                    raise ValueError(f"grid {ds.shape} x{ds.count}")
                b = ds.read(1).astype(np.float32)
        except Exception as e:  # unreadable / other grid: logged, never silently dropped
            row["error"] = str(e)[:200]; rows.append(row); continue
        bv = np.where(foot & np.isfinite(b), b, 0.0)
        their = (bv > 0) & foot
        n_t = int(their.sum()); row["their_dots"] = n_t
        if n_t == 0:
            row["empty"] = True; rows.append(row); continue
        halo = _near(their, 3.0)
        row["halo_coverage"] = float(halo[scored].mean())
        uniq = np.unique(bv[their][:200000])
        row["binary"] = bool(uniq.size <= 1)
        bsub = bv.ravel()[sub]
        for n, m in mine.items():
            lit = float(halo[m].mean())
            rho = spearman_fast(mine_sub[n], bsub) if np.ptp(bsub) > 0 else 0.0
            if abs(rho) > 0.75:
                rho = float(spearmanr(np.where(foot, np.nan_to_num(cands[n]), 0)[foot], bv[foot]).statistic)
            mb = lit
            if n_t > DOT_FIELD_MAX_SUPPORT and not row["binary"]:
                mb = float(_near(matched_budget_support(bv, foot, int(m.sum())), 3.0)[m].mean())
            row[n] = dict(literal_forward_overlap=lit, matched_budget_forward_overlap=mb, spearman=rho)
        rows.append(row)
        if i % 100 == 0:
            print(f"{i}/{len(entries)} t={time.time()-t0:.0f}s", flush=True)
    out = dict(registry_dir=str(REG.relative_to(ROOT)), blobs=len(entries), rows=rows,
               candidates={n: dict(dots=int(m.sum()), sha256=hashlib.sha256(Path(p.split('=',1)[1]).read_bytes()).hexdigest())
                           for (n, m), p in zip(mine.items(), sys.argv[1:])},
               generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    (ROOT / ".cache" / "work").mkdir(exist_ok=True, parents=True)
    json.dump(out, open(ROOT / ".cache" / "work" / "ali_uniqueness.json", "w"), indent=1)
    print("done", len(rows), f"{time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
