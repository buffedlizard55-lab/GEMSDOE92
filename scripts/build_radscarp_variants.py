#!/usr/bin/env python3
"""Build three deterministic RADSCARP variants from parent R0.

Axis: RADSCARP — fused DEM slope-break coherence × radiometric K/Th alteration edge
(session 2026-10-25; the geothermal-conduit lane ranked #1 in
docs/HYPOTHESES_20261025_RADSCARP.md).

Parent R0: h33-h33-2-b2 (37,654 unit-mass dots; d_cat > 2.0 px), a geometric
Poisson thinning of the binary H19-5 mask — no favourability ranking.

Surface S(x) = L(x) * R(x)

  L(x) = pct_rank(||grad det_elev_slope||) * coherence(det_elev)   [BREAKLINE L]
  R_rat(x) = K(x)/Th(x)   (K=Band1, Th=Band2 of geodawn_rad_u8.tif uint8 0-255)
  R(x) = pct_rank(||grad R_rat||) * coherence(R_rat)
  S(x) = L(x) * R(x) ;  S_pct = pct_rank(S)

All ranks over valid footprint (1001-knot). No catalogue read beyond inherited
d_cat>2 exclusion. Valid = footprint & finite topography & (K>0 & Th>0 outside nodata)
— but inside footprint radiometrics never zero (verified), so valid == topo-valid.

Two stages, both driven by S:

1. KEEP (donor selection). Exact expected-DTI greedy restricted to R0's own pixels
   under w = 0.30 + 0.70*S_pct on H19-5 support (coverage-aware ranking).
2. FAR (arrivals). Freed budget re-emitted onto pixels >3px from EVERY H19-5 pixel
   (hence >3px from every R0/D2.8/SOLO pixel — asserted), >2px from catalogue,
   inside footprint, on valid topography, selected by descending S_raw under 2.8px
   spacing floor (gems.radscarp.spaced_top_mask) — the screened concentration rule.

Dose ladder (far fraction of 37,654):
- f33 : 12,426 far (33%), 25,228 kept → 67.0% within 3px of R0 by construction
- f38 : 14,309 far (38%), 23,345 kept → 62.0%
- f45 : 16,944 far (45%), 20,710 kept → 55.0%

Count and unit mass held exact. Whole-file overlap vs R0 equals kept fraction by
construction; measured vs other registry rasters in report script.

Writes releases/<id>.tif (NaN outside) and releases/<id>-zeros.tif, re-reads both,
runs gates + validation, appends ledger/submissions.csv and ledger/mechanism_cards.json,
and records evidence/radscarp_variants.json. Mirrors build_breakline_variants.py.
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

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests, write_tif, validate_reopened
from exact_dti_refill import select_exact_marginal_dti_add
from gems.radscarp import lane_surface, spaced_top_mask

PARENT_ID = "h33-h33-2-b2"
DATE = "20261025"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "radscarp_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Geothermal faults in the Great Basin are both mechanical and hydrogeochemical structures. "
        "Mechanically they produce a linear break-in-slope on detrended topography (||grad det_elev_slope|| "
        "with coherent orientation). Geochemically, sustained fluid flow alters radioelement-bearing minerals, "
        "creating a linear radiometric K/Th edge in the GeoDAWN airborne gamma-ray survey. Requiring co-location "
        "of the two independent lineaments (S = L × R) suppresses the dominant false positives of either detector alone: "
        "Lahontan shoreline terraces (DEM-only) and lithologic contacts (radiometric-only). Parent R0 sits on the "
        "H19-5 potential-field worm skeleton — lines needing magnetic/gravity contrast. A geothermal fault offsetting "
        "thin alluvium with silica sinter may have a subtle DEM scarp and a coincident K/Th alteration halo yet no "
        "usable potential-field contrast, invisible to the worm skeleton but traceable on 1 m LiDAR and gamma radiometrics. "
        "Placing 33–45% of budget on fused scarp-alteration ridges >3px off the skeleton tests that geothermal conduit channel."
    ),
    "mechanism": (
        "At fixed S=37,654, DTI rises when expected T gains outweigh denominator growth. Kept skeleton dots are chosen "
        "by exact marginal expected-DTI greedy (α=0.2, β=0.8, R=3px) under w=0.30+0.70·S_pct on H19-5 support, so "
        "coverage-redundant parent dots are donors. Far dots take the strongest remaining fused scarp-alteration lineaments "
        "first (descending S_raw, 2.8px spacing floor): if per-pixel geothermal fault probability rises superlinearly "
        "with S rank — as alteration-coated scarps concentrate permeability — concentrating on top lineaments at kernel "
        "spacing earns more expected credit per dot than spreading to low-rank support mass."
    ),
    "non_fault_mimic": (
        "Silicified volcanic flow margins (rhyolitic tuff K-rich vs basalt K-poor) with coincident topographic steps, "
        "playa evaporite terraces where K/Th changes sharply across a compaction scarp, and road/berm construction corridors "
        "that disturb both fields all produce co-located linear breaks without Quaternary surface rupture. Fused dots on "
        "such mimics would be pure false positives; playa evaporites cover >10% of footprint basins."
    ),
    "falsifier": (
        "Live receipt delta ≤ -0.010 vs R0 rejects fused altered-scarp breaks as new-fault locations at these doses. "
        "Holdout delta at or below R0 with CI excluding 0 likewise rejects the lane on the catalogue instrument. The "
        "pre-build screen already showed pure radiometric coherence alone is weak (SGMC AUC ~0.52); only the fused product "
        "is tested here. |delta| <0.01 live is no evidence."
    ),
    "decision_rule": (
        "Promote only if literal uniqueness (≤70% dots within 3px of every measured registry raster, |Spearman| ≤0.90 on "
        "surface and final dots) AND pooled HOLDOUT-DTI beats current holdout best (RELIEF p10, 0.006045) with paired CI "
        "excluding 0 vs R0. Otherwise verdict negative: format-valid and downloadable, not cleared for weekly slot."
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
    assert not np.any(r0 & ~h19), "R0 not subset of H19-5; far uniqueness breaks"

    print("Loading topographic bands (12 det_elev, 19 det_elev_slope) and radiometrics (K,Th)...")
    with rasterio.open(inputs["training_features"]) as ds:
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds:
        k_band = ds.read(1).astype(np.float32)  # uint8 0-255, nodata 0 outside foot
        th_band = ds.read(2).astype(np.float32)
        # Verify geometry matches
        assert ds.height == foot.shape[0] and ds.width == foot.shape[1]
        assert str(ds.crs) == "EPSG:32611"

    # Valid mask: footprint & finite topography (radiometrics never zero inside footprint verified)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_slope) & (det_slope > -1e30)
    )
    # Radiometrics check: inside footprint, K and Th should be >0
    rad_valid_inside = (k_band[foot] > 0).all() and (th_band[foot] > 0).all()
    print(f"Footprint {int(foot.sum())}, valid topo {int(valid.sum())}, rad >0 inside foot: {rad_valid_inside}")
    if not rad_valid_inside:
        # Still proceed, but note; outside footprint zeros are okay (valid masks them)
        print("WARNING: some K/Th zero inside footprint (unexpected)")

    surf = lane_surface(det_elev, det_slope, k_band, th_band, valid)
    s_raw = surf["S_raw"]
    s_pct = surf["S_pct"]
    l_raw = surf["L_raw"]
    r_raw = surf["R_raw"]
    print(f"S_raw range [{float(np.nanmin(s_raw)):.4f}, {float(np.nanmax(s_raw)):.4f}] mean {float(s_raw[valid].mean()):.4f}")
    print(f"L_raw mean {float(l_raw[valid].mean()):.4f} R_raw mean {float(r_raw[valid].mean()):.4f}")
    del det_elev, det_slope, k_band, th_band

    d_h19 = distance_transform_edt(~h19)
    far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
    n_far_cand = int(far_cand.sum())
    print(f"Far candidates (>3px off H19-5, d_cat>2): {n_far_cand}")
    if n_far_cand < 400000:
        raise RuntimeError(f"Far candidate pool too small: {n_far_cand} < 400000")

    w_keep = np.where(h19 & valid, 0.30 + 0.70 * s_pct, 0.08 * s_pct).astype(np.float32)
    w_keep[~foot] = 0.0
    w_keep[~valid] = 0.0

    n_parent = int(r0.sum())
    assert n_parent == 37654
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))

    doses = [
        ("f33", 0.33, int(round(0.33 * n_parent))),
        ("f38", 0.38, int(round(0.38 * n_parent))),
        ("f45", 0.45, int(round(0.45 * n_parent))),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, frac, n_far in doses:
        n_keep = n_parent - n_far
        print(f"\nBuilding RADSCARP {val_name}: keep {n_keep} greedy-R0 + {n_far} far fused dots ({frac*100:.0f}% off-skeleton)...")
        keep_mask = select_exact_marginal_dti_add(base_mask=np.zeros_like(r0), cand_mask=r0.copy(), w=w_keep, n_add=n_keep)
        assert int(keep_mask.sum()) == n_keep and not np.any(keep_mask & ~r0)

        far_added = spaced_top_mask(s_raw, far_cand, n_far)
        final_mask = keep_mask | far_added
        assert int(final_mask.sum()) == n_parent
        assert np.array_equal(final_mask & r0, keep_mask)

        far_mask = final_mask & (~r0)
        assert int(far_mask.sum()) == n_far
        assert np.all(d_h19[far_mask] > 3.0)
        assert np.all(d_cat[final_mask] > 2.0)
        assert np.sum(final_mask & cat) == 0

        stem_base = f"{PARENT_ID}-RADSCARP{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()

        stem = f"{PARENT_ID}-RADSCARP{val_name}-{DATE}-{sha8}"
        nan_file = f"{stem}.tif"
        zeros_file = f"{stem}-zeros.tif"
        nan_path = OUT_DIR / nan_file
        zeros_path = OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)
        sha_nan_disk = sha256_file(nan_path)
        sha_zeros_disk = sha256_file(zeros_path)
        assert sha_nan_disk == sha_nan

        nan_checks = validate_reopened(nan_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=False)

        pct_changed = float(n_far / n_parent * 100.0)
        dropped = r0 & (~final_mask)
        form_note = f"{PARENT_ID}; RADSCARP {val_name} {n_far} far dots on fused scarp+K/Th ridges >3px off H19-5"
        assert len(form_note) <= 140, f"Form note {len(form_note)} >140: {form_note}"

        variant_meta = {
            "id": stem,
            "site": "GEMSDOE92",
            "name": nan_file,
            "file_zeros": f"releases/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": f"RADSCARP re-emission: greedy-keep {n_keep} of R0, add {n_far} far dots ({frac*100:.1f}%) spaced fused L×R on altered scarps >3px off H19-5; fixed 37654 dots",
            "notes": f"frac_far={frac:.2f}; n_far={n_far}; n_keep={n_keep}; far_pool={n_far_cand}; whole_file_within3px_of_R0_by_construction={n_keep/n_parent:.4f}; git={git_sha[:12]}",
            "parent": PARENT_ID,
            "axis": "RADSCARP",
            "value": val_name,
            "n_dots": n_parent,
            "pct_changed": pct_changed,
            "removed": n_far,
            "added": n_far,
            "sha256": sha_nan_disk,
            "sha256_zeros": sha_zeros_disk,
            "primary_file": nan_file,
            "fallback_file": zeros_file,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/radscarp_proxy_audit.json",
            "predicted_range": "not projected",
            "prediction_scope": "MODEL scope note only; organizer score requires receipt.",
            "parent_diff": {
                "removed": int(dropped.sum()),
                "added": n_far,
                "shared": n_keep,
                "moved_pct": pct_changed,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_mask].min()),
                "collar_dots_final_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "collar_dots_parent_dcat_le_3": collar_r0,
                "mean_S_pct_far": float(s_pct[far_mask].mean()),
                "mean_S_pct_dropped": float(s_pct[dropped].mean()),
                "mean_L_pct_far": float(surf["L_pct"][far_mask].mean()) if "L_pct" in surf else None,
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates; EPSG:32611, 3730x3292, float32, binary unit-mass, d_cat>2.0)",
            "seed": 0,
        }
        variants.append(variant_meta)
        print(f"PASS {stem} (sha256={sha_nan_disk[:12]}..., far={n_far}, keep={n_keep})")

    evidence_doc = {
        "schema": "gemsdoe92.radscarp-variants.v1",
        "session_date_utc": DATE,
        "axis": "RADSCARP",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n_parent,
            "zeros_sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
            "nan_sha256": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
            "matches_recorded_hashes": True,
        },
        "lane_surface": {
            "definition": "L = pct_rank(||grad det_elev_slope||) * coherence(det_elev); R_ratio=K/Th; R = pct_rank(||grad R_ratio||) * coherence(R_ratio); S = L * R; S_pct = pct_rank(S)",
            "bands": "training_features Band12 det_elev + Band19 det_elev_slope + geodawn_rad_u8 Bands1 K +2 Th (uint8)",
            "implementation": "gems/radscarp.py (deriv sigma 1px, tensor sigma 2px, 1001-knot ranks, K/Th clipped 0.5-99.5%)",
            "catalogue_use": "none in S, keep ranking or refill weight; inherited d_cat>2.0px exclusion only",
            "far_candidate_pool": {
                "rule": "footprint AND valid topography AND d_cat>2.0px AND d_H19>3.0px AND not in R0",
                "n_candidates": n_far_cand,
            },
            "keep_rule": "exact expected-DTI greedy (alpha 0.2 beta 0.8 R=3px) over R0 pixels only, w=0.30+0.70*S_pct on H19-5 support",
            "refill_rule": "spaced top-S: descending S_raw, 2.8px strict spacing floor (gems.radscarp.spaced_top_mask)",
            "uniqueness_by_construction": "R0 ⊂ H19-5 (asserted); far dots >3px from every H19-5 pixel, so whole-file fraction within 3px of any lineage raster equals kept fraction (0.67/0.62/0.55) vs R0.",
        },
        "variants": variants,
        "scope_note": "No submission, leaderboard, hidden labels accessed. Fused surface uses topography + radiometrics only.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2), encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys()) if existing_rows else ["id","parent","axis","value","n_dots","pct_changed","sha256","status","predicted_change","file_zeros","file_nan","sha8","change_desc","receipt_score","receipt_date","notes"]
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k,"") for k in fieldnames}
        row.update({"id": v["id"], "parent": v["parent"], "axis": v["axis"], "value": v["value"], "n_dots": str(v["n_dots"]), "pct_changed": f"{v['pct_changed']:.6f}", "sha256": v["sha256"], "status": "BUILT", "predicted_change": v["predicted_change"], "file_zeros": v["file_zeros"], "file_nan": v["file_nan"], "sha8": v["sha8"], "change_desc": v["change_desc"], "receipt_score": "", "receipt_date": "", "notes": v["notes"]})
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {"parent": PARENT_ID, "axis": "RADSCARP", "value": v["value"], **MECHANISM_CARD, "predicted_sign_and_size": v["predicted_change"]}
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
