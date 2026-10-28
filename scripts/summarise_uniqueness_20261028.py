#!/usr/bin/env python3
"""Summarise the 2026-10-28 full-registry PI-1 audits and the nine-site pairwise matrix.

Reads evidence/uniq_full_registry/*.json (written by audit_candidate_registry.py),
adds a NULL-LIFT column (worst overlap minus that raster's halo fraction, i.e. the
overlap expected from random placement at its density), and computes the 9x9
pairwise 3-px overlap among the nine focus-site peaks.  Output:
evidence/full_registry_summary_20261028.json.  Every number is a local computation
on bytes; none is an organizer score.
"""
from __future__ import annotations
import json, sys, glob
from pathlib import Path
import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
HALO = {r["sha"]: r["halo_frac"] for r in json.loads((ROOT / ".cache/registry_v3/halo_stats.json").read_text())}
SRC = json.loads((ROOT / "evidence/focus9_sources_20261028.json").read_text())

def dots(path: Path) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = ds.read(1)
    return np.nan_to_num(a, nan=0.0) > 0

rows = []
for f in sorted(glob.glob(str(ROOT / "evidence/uniq_full_registry/*.json"))):
    d = json.loads(Path(f).read_text())
    w = d["worst_overlap"]
    h = HALO.get(w["sha256"])
    rows.append(dict(
        name=Path(f).stem, candidate=d["candidate"], candidate_sha256=d["candidate_sha256"],
        n_dots=d["n_dots"], registry_unique_sha256=d["registry_unique_sha256"],
        pi1_pass=d["pi1_pass"], worst_overlap=w["value"], worst_raster_repos=w["repos"],
        worst_raster_halo_frac=h,
        # null-lift is undefined when the worst match is a byte-identical copy (overlap 1.0)
        null_lift=(None if (h is None or w["value"] >= 0.9999) else round(w["value"] - h, 6)),
        worst_abs_rho=d["worst_abs_rho"]["value"], n_rasters_overlap_over_0_5=d["n_rasters_overlap_over_0_5"],
        candidate_identical_copies_in_registry=d["candidate_identical_copies_in_registry"],
    ))

# nine-site pairwise 3-px overlap: fraction of row-site dots within 3 px of column-site dots.
sites = sorted(SRC.keys())
D = {s: dots(ROOT / ".cache/focus9_verify" / f"{s}.tif") for s in sites}
near = {s: ndi.distance_transform_edt(~D[s]) <= 3.0 for s in sites}
pair = {}
for a in sites:
    for b in sites:
        n_a = int(D[a].sum())
        pair[f"{a}->{b}"] = round(float((D[a] & near[b]).sum() / n_a), 6)
        # null: fraction of footprint covered by b's halo (uniform placement of a's dots)
# competition footprint = non-NaN cells of the official-format sample (NaN outside, per sample_submission.tif)
footprint = ~np.isnan(rasterio.open(ROOT / ".cache/gems_inputs/bridge/sample_submission.tif").read(1))
halo_frac_site = {s: round(float((near[s] & footprint).sum() / footprint.sum()), 6) for s in sites}
null_lift_pairwise = {f"{a}->{b}": round(pair[f"{a}->{b}"] - halo_frac_site[b], 6) for a in sites for b in sites}
out = dict(schema="gemsdoe92-full-registry-summary-20261028-v1",
           evidence_class="LOCAL-COMPUTATION on bytes (not an organizer score)",
           pi1_limit=0.70, candidates=rows,
           nine_site_pairwise_overlap=pair, nine_site_halo_frac=halo_frac_site, nine_site_pairwise_null_lift=null_lift_pairwise,
           nine_site_dots={s: int(D[s].sum()) for s in sites})
(ROOT / "evidence/full_registry_summary_20261028.json").write_text(json.dumps(out, indent=2))
for r in rows:
    print(f"{r['name']:38s} n={r['n_dots']:6d} pass={str(r['pi1_pass']):5s} worst={r['worst_overlap']:.4f} halo={r['worst_raster_halo_frac']} lift={r['null_lift']} rho={r['worst_abs_rho']:.3f}")
print("nine-site halo_frac:", halo_frac_site)
for a in sites:
    print(a, " ".join(f"{pair[f'{a}->{b}']:.3f}" for b in sites))
