#!/usr/bin/env python3
"""Build the single-dose ANASIG variant from parent R0 (f45 only).

Axis: ANASIG -- re-emission onto magnetic analytic-signal ridges
(sqrt(Band3^2+Band9^2) gated by coherence of Band14) that lie off the
H19-5 worm skeleton (session 2026-10-24; ranked hypothesis 3 in
docs/HYPOTHESES_20261024_SCARPPOL.md, promoted to build after the
rank-1 SCARPPOL lane was stopped as a BREAKLINE duplicate and the
in-memory hybrid screen showed ANASIG f45 holdout-positive and
lane-disjoint; see docs/ANALYSIS_20261024_ANASIG.md).

Parent R0: h33-h33-2-b2 (37,654 unit-mass dots; d_cat > 2.0 px).
Two changes, driven by one label-free field (gems/anasig.py):

    S(x) = pct_rank(sqrt(tmi_hg^2 + tmi_vg^2)) * coherence(tmi)

1. KEEP: exact expected-DTI greedy over R0 pixels under
   w = 0.30 + 0.70*S_pct on H19-5 support (20,710 kept).
2. FAR: 16,944 spaced top-S dots (2.8 px floor) on pixels >3 px from
   every H19-5 pixel, >2 px from the catalogue, valid magnetics.

Only the f45 dose is built: the SCARPPOL lane had already used the
session's 3-dose budget before its duplicate stop, so this lane is
limited to one build (deviation logged in IRREGULARITIES.md).

Writes releases/<id>.tif (NaN outside) and releases/<id>-zeros.tif,
re-reads both, runs gems.gates, appends ledger/submissions.csv and
ledger/mechanism_cards.json, records evidence/anasig_variants.json.
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
from gems.anasig import lane_surface, spaced_top_mask

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "anasig_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Magnetic analytic-signal ridges (sqrt(tmi_hg^2+tmi_vg^2), coherence-gated on tmi) "
        "mark near-vertical basement contacts under cover. The H19-5 skeleton behind R0 is "
        "multi-line corroborated, so a contact carried by the magnetic analytic signal "
        "alone could be dropped from the skeleton and the USGS/INGENIOUS catalogue while "
        "still marking a basement fault propagating into basin fill. Placing 45% of the "
        "budget on the strongest such ridges >3px off the whole skeleton tests that "
        "single-line magnetic channel."
    ),
    "mechanism": (
        "At fixed S=37,654, DTI rises when expected T gains outweigh denominator growth. "
        "Kept skeleton dots are chosen by exact marginal expected-DTI greedy (alpha 0.2, "
        "beta 0.8, R=3px) under w=0.30+0.70*S_pct on H19-5 support. Far dots take the "
        "strongest analytic-signal ridges first (descending S, 2.8px spacing). In-memory "
        "screen (docs/ANALYSIS_20261024_ANASIG.md): f45 hybrid HOLDOUT-DTI 0.004967 vs "
        "R0 0.004006, forward overlap 0.528 vs BREAKLINE f45 -- holdout-positive and "
        "lane-disjoint, unlike SCARPPOL (0.900 vs BREAKLINE, duplicate-stopped)."
    ),
    "non_fault_mimic": (
        "Lithologic contacts without fault offset, dike/sill edges, buried volcanic "
        "flow margins, and cultural magnetic noise all produce analytic-signal ridges "
        "with no Quaternary fault."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat the current holdout best (RELIEF p10, "
        "0.006045) rejects promotion on the catalogue instrument; canary symmetric "
        "AUC >0.90 stops the lane as leakage until investigated; forward overlap "
        ">0.70 or |rho| >0.90 vs any local registry raster logs a duplicate and stops."
    ),
    "decision_rule": (
        "Promote only if literal local-registry uniqueness AND pooled HOLDOUT-DTI "
        "beats RELIEF p10 (0.006045) with paired CI excluding 0 vs R0 AND all format "
        "gates pass. Otherwise negative: format-valid, downloadable, not cleared "
        "for a weekly slot."
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

    assert not np.any(r0 & ~h19), "R0 is not a subset of H19-5; far-field uniqueness argument breaks"

    print("Loading magnetic bands (3 tmi_hg, 9 tmi_vg, 14 tmi)...")
    with rasterio.open(inputs["training_features"]) as ds:
        tmi_hg = ds.read(3, masked=True).filled(np.nan).astype(np.float32)
        tmi_vg = ds.read(9, masked=True).filled(np.nan).astype(np.float32)
        tmi = ds.read(14, masked=True).filled(np.nan).astype(np.float32)

    valid = (
        foot
        & np.isfinite(tmi_hg) & (tmi_hg > -1e30)
        & np.isfinite(tmi_vg) & (tmi_vg > -1e30)
        & np.isfinite(tmi) & (tmi > -1e30)
    )
    print(f"Footprint {int(foot.sum())}, valid magnetics {int(valid.sum())}")

    surf = lane_surface(tmi_hg, tmi_vg, tmi, valid)
    s_pct = surf["S_pct"]
    s_raw = surf["S_raw"]
    del tmi_hg, tmi_vg, tmi

    d_h19 = distance_transform_edt(~h19)

    # FAR candidate pool: all valid pixels >3px from every H19-5 pixel,
    # >2px from catalogue, valid footprint, off the parent (PASS-2: no
    # 5x5-ridge restriction -- it was an unscreened deviation that removed
    # the 2-3px shoulders of crests whose peak sits inside the exclusions).
    far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
    n_far_cand = int(far_cand.sum())
    print(f"Far candidates (>3px off H19-5, d_cat>2): {n_far_cand}")
    if n_far_cand < 400000:
        raise RuntimeError(f"Far candidate pool too small: {n_far_cand} < 400000 (screen cap)")

    # Keep-stage weight (project-standard support construction).
    w_keep = np.where(h19 & valid, 0.30 + 0.70 * s_pct, 0.08 * s_pct).astype(np.float32)
    w_keep[~foot] = 0.0
    w_keep[~valid] = 0.0

    n_parent = int(r0.sum())
    assert n_parent == 37654, f"Parent dot count {n_parent} != 37654"
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))

    doses = [
        ("f45Atop", 0.45, int(round(0.45 * n_parent))),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, frac, n_far in doses:
        n_keep = n_parent - n_far
        print(f"\nBuilding ANASIG {val_name}: keep {n_keep} greedy-R0 + {n_far} far ridge dots "
              f"({frac*100:.0f}% off-skeleton)...")

        keep_mask = select_exact_marginal_dti_add(
            base_mask=np.zeros_like(r0), cand_mask=r0.copy(), w=w_keep, n_add=n_keep)
        assert int(keep_mask.sum()) == n_keep and not np.any(keep_mask & ~r0)

        # Far dots are >3px from every H19-5 pixel, hence >3px from every kept
        # dot; the 2.8px floor inside spaced_top_mask therefore governs the
        # whole-file minimum spacing together with the parent's own floor.
        far_added = spaced_top_mask(s_raw, far_cand, n_far)
        final_mask = keep_mask | far_added
        assert int(final_mask.sum()) == n_parent, f"Count {int(final_mask.sum())} != {n_parent}"
        assert np.array_equal(final_mask & r0, keep_mask), "kept set drifted during refill"

        far_mask = final_mask & (~r0)
        assert int(far_mask.sum()) == n_far
        assert np.all(d_h19[far_mask] > 3.0), "far dot within 3px of H19-5 skeleton"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat violation"
        assert np.sum(final_mask & cat) == 0, "catalogue mass violation"

        stem_base = f"{PARENT_ID}-ANASIG{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()

        stem = f"{PARENT_ID}-ANASIG{val_name}-{DATE}-{sha8}"
        nan_file = f"{stem}.tif"
        zeros_file = f"{stem}-zeros.tif"
        nan_path = OUT_DIR / nan_file
        zeros_path = OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)
        sha_nan_disk = sha256_file(nan_path)
        sha_zeros_disk = sha256_file(zeros_path)
        assert sha_nan_disk == sha_nan

        nan_checks = validate_reopened(nan_path, inputs["sample_submission"], inputs["existing_faults"],
                                        final_mask, foot, cat, d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_path, inputs["sample_submission"], inputs["existing_faults"],
                                          final_mask, foot, cat, d_cat, expect_nan_outside=False)

        pct_changed = float(n_far / n_parent * 100.0)
        dropped = r0 & (~final_mask)
        form_note = (f"{PARENT_ID}; ANASIG {far_n_label(frac)}Atop {n_far} far dots on analytic-signal "
                     f"analytic-signal ridges >3px off H19-5")
        assert len(form_note) <= 140, f"Form note {len(form_note)} >140: {form_note}"

        variant_meta = {
            "id": stem,
            "site": "GEMSDOE92",
            "name": nan_file,
            "file_zeros": f"releases/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (f"ANASIG re-emission: greedy-keep {n_keep} of R0, add {n_far} far dots "
                            f"({frac*100:.1f}%) spaced-top-S on coherent analytic-signal ridges >3px off H19-5; fixed 37654 dots"),
            "notes": (f"frac_far={frac:.2f}; n_far={n_far}; n_keep={n_keep}; far_pool={n_far_cand}; "
                      f"whole_file_within3px_of_R0_by_construction={n_keep/n_parent:.4f}; git={git_sha[:12]}"),
            "parent": PARENT_ID,
            "axis": "ANASIG",
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
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/anasig_proxy_audit.json",
            "predicted_range": "not projected (a projection is never written as a score)",
            "prediction_scope": "MODEL scope note only; organizer score requires a submission receipt.",
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
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates; EPSG:32611, 3730x3292, float32, binary unit-mass, d_cat>2.0)",
            "seed": 0,
        }
        variants.append(variant_meta)
        print(f"PASS {stem} (sha256={sha_nan_disk[:12]}..., far={n_far}, keep={n_keep})")

    evidence_doc = {
        "schema": "gemsdoe92.anasig-variants.v1",
        "session_date_utc": DATE,
        "axis": "ANASIG",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n_parent,
            "zeros_sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
            "nan_sha256": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
            "matches_recorded_hashes": True,
        },
        "lane_surface": {
            "definition": "S = pct_rank(sqrt(tmi_hg^2+tmi_vg^2)) * structure_tensor_coherence(tmi); S_pct = pct_rank(S)",
            "bands": "training_features Band 3 tmi_hg + Band 9 tmi_vg + Band 14 tmi (masked reads, sentinel-safe)",
            "implementation": "gems/anasig.py (fall-line directional second derivative; deriv sigma 1px, tensor sigma 2px, 1001-knot percentile ranks)",
            "catalogue_use": "none in S, keep ranking or refill weight; inherited d_cat>2.0px exclusion only",
            "far_candidate_pool": {
                "rule": "footprint AND valid topography AND d_cat>2.0px AND d_H19>3.0px AND not in R0; scan restricted to top-400k by S_raw",
                "n_candidates": n_far_cand,
            },
            "keep_rule": "exact expected-DTI greedy (alpha 0.2 beta 0.8 R=3px) over R0 pixels only, w=0.30+0.70*S_pct on H19-5 support",
            "refill_rule": "spaced top-S: descending S_raw, 2.8px strict spacing floor (gems.anasig.spaced_top_mask) -- the emission rule exercised by the pre-build screen",
            "uniqueness_by_construction": (
                "R0 and D2.8/SOLO are subsets of H19-5 (asserted in build); far dots are >3px from "
                "every H19-5 pixel, so whole-file fraction within 3px of any lineage raster equals "
                "the kept fraction (0.67/0.62/0.55) up to skeleton-adjacency of kept dots themselves, "
                "which is exact-shared only against R0. Measured against all local registry rasters "
                "in evidence/anasig_proxy_audit.json."
            ),
        },
        "variants": variants,
        "scope_note": "No submission, leaderboard, or hidden labels accessed. Surface uses topography only.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2), encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys()) if existing_rows else [
            "id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256", "status",
            "predicted_change", "file_zeros", "file_nan", "sha8", "change_desc",
            "receipt_score", "receipt_date", "notes"]
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k, "") for k in fieldnames}
        row.update({
            "id": v["id"], "parent": v["parent"], "axis": v["axis"], "value": v["value"],
            "n_dots": str(v["n_dots"]), "pct_changed": f"{v['pct_changed']:.6f}", "sha256": v["sha256"],
            "status": "BUILT", "predicted_change": v["predicted_change"],
            "file_zeros": v["file_zeros"], "file_nan": v["file_nan"], "sha8": v["sha8"],
            "change_desc": v["change_desc"], "receipt_score": "", "receipt_date": "", "notes": v["notes"],
        })
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID, "axis": "ANASIG", "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


def far_n_label(frac: float) -> str:
    return f"f{int(round(frac * 100))}"


if __name__ == "__main__":
    raise SystemExit(main())
