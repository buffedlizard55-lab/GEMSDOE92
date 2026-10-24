#!/usr/bin/env python3
"""Build two deterministic STEPEDGE variants from parent R0 (2026-10-24).

Lane as built (screen selection is the story, recorded honestly):
the pre-registered screen (scripts/screen_stepedge_surfaces.py,
evidence/stepedge_screen.json) reproduced the BREAKLINE-L baseline to the
digit (sym AUC 0.621604, far SGMC 0.072325) and then measured:

* coherence-gated STEPEDGE S (pct(step) x coherence): far SGMC 0.065885 but
  far-set forward overlap 0.755 vs BREAKLINE f45's far dots -> DUPLICATE
  under the pre-registered rule, duplicate-stopped, never built.
* STEPRAW (aperture-persistent sustained step WITHOUT the coherence gate,
  S = pct_rank(min(step_{2,3px}, step_{4,6px})) on Band 12 det_elev):
  far SGMC 0.071257 (98.5% of baseline), sym AUC 0.57972, far-set overlap
  0.427 vs BREAKLINE f45 / 0.099 vs ANASIG f45 / 0.158 vs STRAINBREAK f60.

Per the pre-registered rule (best non-baseline far SGMC passing canary +
disjointness), STEPRAW is the built surface.  Removing the gate is also a
physical statement: the shared coherence gate was forcing every terrain
lane onto the same lineaments; the sustained-offset statistic carries the
signal on its own (its named risk -- isotropic rugged range interiors with
large cross-line offsets but no lineament -- is priced by the holdout).

Structure mirrors build_breakline_variants.py exactly (shared tools reused,
not forked): keep-set by exact expected-DTI greedy restricted to R0 pixels
under w = 0.30+0.70*S on H19-5 support; far dots by descending S under the
2.8 px spacing floor, >3 px off every H19-5 pixel, >2 px off the catalogue.
Doses: f33 (12,426 far / 25,228 keep), f45 (16,944 far / 20,710 keep) and
f60 (22,592 far / 15,062 keep, far dots also >3 px off BREAKLINE-f45 and
SCARPPOL-f45 far dots -- the literal-uniqueness repair pre-registered in
the amendment to docs/HYPOTHESES_20261024_STEPEDGE.md after f33/f45
measured 0.76/0.71 forward overlap vs same-dose siblings).
37,654 unit-mass dots total at every dose.  Budget: 3 of 3 experiments.

The pre-placement surface is written to .cache/stepedge_surface_pct.tif
(gitignored) with its SHA-256 in the evidence doc, so the report stage can
run the surface-level uniqueness check on the actual surface, not a rebuild.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_snap_scarp_variants import (build_and_verify_parent, validate_reopened,
                                       verify_all_manifests, write_tif)
from exact_dti_refill import select_exact_marginal_dti_add
from gems.stepedge import lane_surface, spaced_top_mask

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "stepedge_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"
SURFACE_CACHE = ROOT / ".cache" / "stepedge_surface_pct.tif"

MECHANISM_CARD = {
    "hypothesis": (
        "A Quaternary fault offsetting alluvium (or one lithology against itself) leaves a "
        "SUSTAINED topographic step: detrended elevation stays offset across the trace at both "
        "200-300 m and 400-600 m apertures. Such a fault has no magnetic/gravity contrast, so "
        "the H19-5 potential-field worm skeleton behind R0 misses it, and a low scarp is easily "
        "missed by photo-era Qfaults mapping, while DEM-based expert mapping (the competition "
        "label source, DrivenData #306 p.967) traces exactly such steps. The min over apertures "
        "rejects channel walls/ridges, whose cross-line offset decays once the aperture exceeds "
        "their width (synthetic: 6 m step 5.4 m persistent vs channel 1.3 m)."
    ),
    "mechanism": (
        "At fixed S=37,654, DTI rises when expected T gains outweigh denominator growth. Kept "
        "skeleton dots are chosen by exact marginal expected-DTI greedy (alpha 0.2, beta 0.8, "
        "R=3px) under w=0.30+0.70*S on H19-5 support, so coverage-redundant parent dots are the "
        "donors. Far dots take the strongest aperture-persistent steps first (descending S, "
        "2.8px spacing): the pre-build screen's identical 16,944-dot far set hit off-catalogue "
        "USGS SGMC bedrock faults at 0.071257 vs BREAKLINE-L 0.072325 while being 57% disjoint "
        "from BREAKLINE's far dots -- an independent evidence channel, not a reweighting."
    ),
    "non_fault_mimic": (
        "Lake Lahontan wave-cut shoreline benches are sustained steps at all apertures; so are "
        "alluvial-fan segment boundaries, fluvial terrace edges, bedding-controlled cuestas and "
        "(without a coherence gate) rugged range-interior relief. Any of these concentrated in "
        "the far set would be pure false positives."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI at/below R0, or a live receipt delta <= -0.010 vs R0 if ever "
        "submitted, rejects aperture-persistent ungated steps as new-fault locations at these "
        "doses. The coherence-gated form was already falsified as a lane (duplicate of "
        "BREAKLINE, screen overlap 0.755) and is not built."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats the best locally-unique arm (STRAINBREAK f60, "
        "0.005487) with paired delta vs R0 CI excluding 0, full-file SGMC exceeds R0 (0.09606), "
        "leakage canary <= 0.90, literal local uniqueness passes on the pre-placement surface "
        "AND final dots (dot-like registry scope; dense-witness literal number disclosed), and "
        "all format MUST gates pass on disk re-read. Otherwise verdict negative: format-valid "
        "download, DO NOT SUBMIT."
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    assert not np.any(r0 & ~h19), "R0 not subset of H19-5; far uniqueness argument breaks"

    print("Loading Band 12 det_elev ...")
    with rasterio.open(inputs["training_features"]) as ds:
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
    valid = foot & np.isfinite(det_elev) & (det_elev > -1e30)
    print(f"Footprint {int(foot.sum())}, valid det_elev {int(valid.sum())}")

    surf = lane_surface(det_elev, valid)
    s_pct = surf["step_pct"]          # STEPRAW: persistent-step rank, NO coherence gate
    s_raw = surf["step_pct"]
    del det_elev

    # Persist the ACTUAL pre-placement surface for the uniqueness audit.
    SURFACE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    prof = profile.copy()
    prof.update(driver="GTiff", dtype="float32", count=1, compress="deflate",
                nodata=None, tiled=True, blockxsize=256, blockysize=256)
    surf_out = np.where(foot, s_pct, np.float32(0.0)).astype(np.float32)
    with rasterio.open(SURFACE_CACHE, "w", **prof) as ds:
        ds.write(surf_out, 1)
    surface_sha = sha256_file(SURFACE_CACHE)
    del surf_out
    print(f"Pre-placement surface -> {SURFACE_CACHE} sha256={surface_sha[:12]}")

    d_h19 = distance_transform_edt(~h19)
    far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
    n_far_cand = int(far_cand.sum())
    print(f"Far candidates (>3px off H19-5, d_cat>2): {n_far_cand}")
    if n_far_cand < 400000:
        raise RuntimeError(f"Far pool too small: {n_far_cand}")

    # f60-only repulsion pool: also >3 px off the two same-dose sibling far
    # sets that blocked f45's literal uniqueness (STRAINBREAK-proven repair).
    def _far_of(rel: str) -> np.ndarray:
        with rasterio.open(ROOT / rel) as ds:
            m = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
        return m & (d_h19 > 3.0)
    repel = np.ones(foot.shape, bool)
    for rel in ("docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
                "releases/h33-h33-2-b2-SCARPPOLf45Stop-20261024-cf4e45c0-zeros.tif"):
        repel &= distance_transform_edt(~_far_of(rel)) > 3.0
    far_cand_f60 = far_cand & repel
    print(f"Far candidates f60 (also repelled): {int(far_cand_f60.sum())}")
    del repel

    w_keep = np.where(h19 & valid, 0.30 + 0.70 * s_pct, 0.08 * s_pct).astype(np.float32)
    w_keep[~foot] = 0.0
    w_keep[~valid] = 0.0

    n_parent = int(r0.sum())
    assert n_parent == 37654
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))
    doses = [("f33Sraw", 0.33, int(round(0.33 * n_parent))),
             ("f45Sraw", 0.45, int(round(0.45 * n_parent))),
             ("f60Sraw", 0.60, int(round(0.60 * n_parent)))]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, frac, n_far in doses:
        n_keep = n_parent - n_far
        print(f"\nBuilding STEPEDGE {val_name}: keep {n_keep} + far {n_far} ...")
        keep_mask = select_exact_marginal_dti_add(
            base_mask=np.zeros_like(r0), cand_mask=r0.copy(), w=w_keep, n_add=n_keep)
        assert int(keep_mask.sum()) == n_keep and not np.any(keep_mask & ~r0)
        pool = far_cand_f60 if val_name == "f60Sraw" else far_cand
        far_added = spaced_top_mask(s_raw, pool, n_far)
        final_mask = keep_mask | far_added
        assert int(final_mask.sum()) == n_parent
        assert np.array_equal(final_mask & r0, keep_mask)
        far_mask = final_mask & (~r0)
        assert int(far_mask.sum()) == n_far
        assert np.all(d_h19[far_mask] > 3.0)
        assert np.all(d_cat[final_mask] > 2.0)
        assert np.sum(final_mask & cat) == 0

        stem_base = f"{PARENT_ID}-STEPEDGE{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()
        stem = f"{stem_base}-{sha8}"
        nan_file, zeros_file = f"{stem}.tif", f"{stem}-zeros.tif"
        nan_path, zeros_path = OUT_DIR / nan_file, OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)
        sha_nan_disk, sha_zeros_disk = sha256_file(nan_path), sha256_file(zeros_path)
        assert sha_nan_disk == sha_nan
        nan_checks = validate_reopened(nan_path, inputs["sample_submission"],
                                        inputs["existing_faults"], final_mask, foot, cat,
                                        d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_path, inputs["sample_submission"],
                                          inputs["existing_faults"], final_mask, foot, cat,
                                          d_cat, expect_nan_outside=False)
        pct_changed = float(n_far / n_parent * 100.0)
        dropped = r0 & (~final_mask)
        form_note = (f"{PARENT_ID}; STEPEDGE {val_name} {n_far} far dots on "
                     f"aperture-persistent DEM steps >3px off H19-5")
        assert len(form_note) <= 140, form_note
        variants.append({
            "id": stem, "site": "GEMSDOE92", "name": nan_file,
            "file_zeros": f"releases/{zeros_file}", "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (f"STEPEDGE Sraw re-emission: greedy-keep {n_keep} of R0, add {n_far} "
                            f"far dots ({frac*100:.1f}%) spaced-top-S on aperture-persistent DEM "
                            f"steps >3px off H19-5; fixed 37654 dots"),
            "notes": (f"frac_far={frac:.2f}; n_far={n_far}; n_keep={n_keep}; far_pool={int(pool.sum())}; "
                      f"whole_file_within3px_of_R0_by_construction={n_keep/n_parent:.4f}; git={git_sha[:12]}"),
            "parent": PARENT_ID, "axis": "STEPEDGE", "value": val_name,
            "n_dots": n_parent, "pct_changed": pct_changed,
            "removed": n_far, "added": n_far,
            "sha256": sha_nan_disk, "sha256_zeros": sha_zeros_disk,
            "primary_file": nan_file, "fallback_file": zeros_file,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/stepedge_proxy_audit.json",
            "predicted_range": "not projected (a projection is never written as a score)",
            "prediction_scope": "MODEL scope note only; organizer score requires a submission receipt.",
            "parent_diff": {
                "removed": int(dropped.sum()), "added": n_far, "shared": n_keep,
                "moved_pct": pct_changed,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_mask].min()),
                "collar_dots_final_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "collar_dots_parent_dcat_le_3": collar_r0,
                "mean_S_pct_far": float(s_pct[far_mask].mean()),
                "mean_S_pct_dropped": float(s_pct[dropped].mean()),
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates; EPSG:32611, 3730x3292, float32, binary unit-mass, d_cat>2.0)",
            "seed": 0,
        })
        print(f"PASS {stem} sha256={sha_nan_disk[:12]} far={n_far} keep={n_keep}")

    evidence_doc = {
        "schema": "gemsdoe92.stepedge-variants.v1",
        "session_date_utc": DATE,
        "axis": "STEPEDGE",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "screen": "evidence/stepedge_screen.json (baseline reproduced to the digit; coherence-gated form duplicate-stopped at overlap 0.755)",
        "lane_surface": {
            "definition": "S = pct_rank( min(step_{2,3px}, step_{4,6px}) ) on det_elev along the structure-tensor dominant-gradient direction; NO coherence gate (screen selection)",
            "bands": "training_features Band 12 det_elev only",
            "implementation": "gems/stepedge.py (deriv sigma 1px, tensor sigma 2px, 1001-knot ranks)",
            "catalogue_use": "none in S, keep ranking or refill weight; inherited d_cat>2.0px exclusion only",
            "preplacement_surface_cache": str(SURFACE_CACHE.relative_to(ROOT)),
            "preplacement_surface_sha256": surface_sha,
            "far_candidate_pool": {"rule": "footprint AND valid det_elev AND d_cat>2 AND d_H19>3 AND not R0", "n_candidates": n_far_cand},
            "keep_rule": "exact expected-DTI greedy over R0 pixels only, w=0.30+0.70*S on H19-5 support",
            "refill_rule": "spaced top-S: descending S, 2.8px strict floor (gems.breakline.spaced_top_mask via gems.stepedge re-export)",
        },
        "variants": variants,
        "scope_note": "No submission, leaderboard, or hidden labels accessed.",
    }
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2), encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k, "") for k in fieldnames}
        row.update({"id": v["id"], "parent": v["parent"], "axis": v["axis"], "value": v["value"],
                    "n_dots": str(v["n_dots"]), "pct_changed": f"{v['pct_changed']:.6f}",
                    "sha256": v["sha256"], "status": "BUILT",
                    "predicted_change": v["predicted_change"], "file_zeros": v["file_zeros"],
                    "file_nan": v["file_nan"], "sha8": v["sha8"],
                    "change_desc": v["change_desc"], "receipt_score": "", "receipt_date": "",
                    "notes": v["notes"]})
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {"parent": PARENT_ID, "axis": "STEPEDGE", "value": v["value"],
                          **MECHANISM_CARD, "predicted_sign_and_size": v["predicted_change"]}
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
