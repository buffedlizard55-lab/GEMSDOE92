#!/usr/bin/env bash
# Reproduce EXP1 (session ee2370c1) end to end. Network: github.com / codeload.github.com only.
# Wall time ~1.5 h on 2 CPUs / 4 GB RAM.  Every output number is MODEL or HOLDOUT-DTI, never a score.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python}
$PY scripts/restore_inputs.py                       # 12 SHA-256-pinned inputs -> .cache/gems_inputs
$PY scripts/build_registry_cache.py --workers 2     # all public GEMSDOE rasters -> .cache/registry_v3
$PY /dev/stdin <<'PYEOF'                            # halo statistics for PI-1 (registry_v3/halo_stats.json)
import json, sys, numpy as np
sys.path[:0] = ['.', 'scripts']
import lbm_data as L
from gems import registry_cache as rc
from scipy import ndimage as ndi
fp = L.footprint(); H, W = L.SHAPE
inv = json.loads((rc.CACHE / 'inventory.json').read_text())
out = []
for s in sorted({f['sha256'] for r in inv['repositories'] for f in r['files']}):
    meta, arr = rc.load_summary(s); m = meta['meta']
    halo = None
    if m['top_complete'] and m['n_fp_pos'] > 0:
        g = np.zeros(H * W, bool); g[fp.lin[arr['top']]] = True
        halo = float((ndi.distance_transform_edt(~g.reshape(H, W)).ravel()[fp.lin] <= 3).mean())
    out.append(dict(sha=s, n_pos=m['n_fp_pos'], support_frac=m['n_fp_pos'] / fp.n, halo_frac=halo,
                    binary=m['binary'], complete=m['top_complete']))
(rc.CACHE / 'halo_stats.json').write_text(json.dumps(out))
PYEOF
$PY scripts/match_claims.py                         # CLAIM scores -> registry rasters
$PY scripts/lbm_cache.py                            # coverage fields of scored rasters
$PY scripts/lbm_fit_final.py                        # LBM-v1 + grouped CV
$PY scripts/lbm_ensemble_map.py                     # ensemble density (G>=0.18, G>=0.15)
$PY scripts/exp1_twopool.py --round0-only           # round-0 placement + full audit rows
$PY scripts/exp1_hybrid.py --rounds 1 --out hybrid_ens
$PY scripts/exp1_repair.py --start .cache/exp1/hybrid_ens/round0_sel.npy --out final_ens
$PY scripts/exp1_holdout.py                         # shared gems57 spatial holdout (reported)
$PY scripts/exp1_canaries.py                        # leakage canaries
$PY scripts/holdout_validity.py                     # does the holdout predict CLAIMs?
$PY scripts/focus9_sources.py                       # pin nine-site best files to commits
$PY scripts/focus9_uniqueness.py                    # nine-site uniqueness
$PY scripts/build_exp1_submission.py .cache/exp1/final_ens/final_sel.npy
$PY scripts/render_site_v3.py && $PY scripts/check_site.py
