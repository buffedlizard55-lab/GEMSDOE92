#!/usr/bin/env python3
"""Build three deterministic DILATATION variants from parent R0.

Axis: DILATATION (shift mass into high geodetic dilatation zones).

Parent R0: h33-h33-2-b2 (37,654 unit-mass dots; min_nn >= 2.828 px; d_cat > 2.0 px).

Mechanism (Basin-and-Range geodesy → geothermal permeability):
Geodetic dilatation rate (Band 8 geod_dilaterate, nstrain/yr) measures volumetric
opening of the crust. In the Great Basin, geothermal fluids ascend where normal-fault
step-overs, relay ramps and terminations are actively dilating — ~32% of systems
in step-overs, another ~25% at terminations/intersections (Faulds et al. 2006,
2010, 2021a; Giddens & Faulds 2025). The catalogue maps Quaternary scarps; the
strain field maps where those scarps are currently opening. A blind fault under
10-100 m of alluvium has no scarp but still dilates, and will be missed by
topography/magnetics alone. GeoDAWN was flown at 400 m spacing — positional
uncertainty ~300 m is the DTI kernel, so we shift mass into high-dilatation
corridors at the same H19-5 ridge geometry.

We test a controlled dose ladder:
- p10dilatation : shift 10% (3,765 dots) lowest-dilatation → highest-dilatation
- p12dilatation : shift 12% (4,518 dots)
- p15dilatation : shift 15% (5,648 dots)

Refill pixels are selected greedily by exact expected marginal DTI gain on the
label-free dilatation prior (ranked Band 8), strictly constrained to the high-
dilatation tercile (w >= p67), H19-5 support, off catalogue (d_cat > 2.0 px),
and preserving R0's unit mass and exact 37,654 count. No catalogue information
enters the prior.
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
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests, write_tif, validate_reopened
from exact_dti_refill import select_exact_marginal_dti_add

PARENT_ID = "h33-h33-2-b2"
DATE = "20261025"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "dilatation_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

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

    print("Loading 19-band geodetic fields (Band 8 dilatation + Band 7 shear context)...")
    with rasterio.open(inputs["training_features"]) as ds:
        dilat = ds.read(8, masked=True).filled(np.nan)  # geod_dilaterate
        shear = ds.read(7, masked=True).filled(np.nan)  # geod_shearrate (context only)
        tmi_hg = ds.read(3, masked=True).filled(np.nan)
        grav_slope = ds.read(5, masked=True).filled(np.nan)
        det_slope = ds.read(19, masked=True).filled(np.nan)

    valid_dilat = foot & np.isfinite(dilat) & (dilat > -1e30)
    # Also need valid stack for physical prior component that shares placement weight
    valid_stack = (
        valid_dilat
        & np.isfinite(tmi_hg) & (tmi_hg > -1e30)
        & np.isfinite(grav_slope) & (grav_slope > -1e30)
        & np.isfinite(det_slope) & (det_slope > -1e30)
    )
    print(f"Valid footprint {int(foot.sum())}, valid dilat {int(valid_dilat.sum())}, valid stack {int(valid_stack.sum())}")

    # Dilatation terciles on valid footprint pixels
    p33, p67 = np.percentile(dilat[valid_dilat], [33.333333, 66.666667])
    print(f"Dilatation terciles: p33={p33:.4f} nstrain/yr, p67={p67:.4f} nstrain/yr (valid N={int(valid_dilat.sum())})")
    # Define zones
    is_low = (dilat < p33) & valid_dilat
    is_mid = (dilat >= p33) & (dilat < p67) & valid_dilat
    is_high = (dilat >= p67) & valid_dilat

    # Ranked dilatation prior (0..1) on valid_dilat
    # Use rankdata for robustness to heavy tails (p99=27, max 34.5)
    dilat_prior = np.zeros_like(dilat, dtype=np.float32)
    r_dilat = rankdata(dilat[valid_dilat]) / float(np.sum(valid_dilat))
    dilat_prior[valid_dilat] = r_dilat.astype(np.float32)

    # Also compute the established physical prior for off-H19 weighting (tmi/grav/scarp)
    # Keep exactly the project-standard mix so the only new information is dilatation
    phys_prior = np.zeros_like(dilat, dtype=np.float32)
    r_tmi = rankdata(tmi_hg[valid_stack]) / float(np.sum(valid_stack))
    r_grav = rankdata(grav_slope[valid_stack]) / float(np.sum(valid_stack))
    r_scarp = rankdata(det_slope[valid_stack]) / float(np.sum(valid_stack))
    phys_prior[valid_stack] = (0.40 * r_tmi + 0.35 * r_grav + 0.25 * r_scarp).astype(np.float32)

    # DTI weight field: on H19-5 ridges, dilatation matters most (70%); off ridges, keep gentle 8% base
    # Blend: w_dti = 0.70*dilat_prior + 0.30*phys_prior on ridges (so we stay on geophysically plausible pixels)
    # Off ridges we never place (cand_mask requires h19), but we define anyway for completeness.
    dti_weight = np.zeros_like(dilat, dtype=np.float32)
    # On-ridge weight emphasizes dilatation but respects scarp/gravity plausibility
    w_on = 0.70 * dilat_prior + 0.30 * phys_prior
    dti_weight = np.where(h19 & valid_dilat, 0.30 + 0.70 * w_on, 0.08 * dilat_prior).astype(np.float32)
    dti_weight[~foot] = 0.0
    # Zero weight where dilatation invalid
    dti_weight[~valid_dilat] = 0.0

    # Parent dot distribution across dilatation terciles
    r0_ys, r0_xs = np.nonzero(r0)
    n_parent = len(r0_ys)
    assert n_parent == 37654, f"Parent dot count {n_parent} != 37654"
    dill_at_dots = dilat[r0_ys, r0_xs]
    n_low = int(np.sum(dill_at_dots < p33))
    n_mid = int(np.sum((dill_at_dots >= p33) & (dill_at_dots < p67)))
    n_high = int(np.sum(dill_at_dots >= p67))
    print(f"R0 distribution: low={n_low} ({n_low/n_parent:.1%}), mid={n_mid} ({n_mid/n_parent:.1%}), high={n_high} ({n_high/n_parent:.1%})")

    # Source pool: R0 dots in low + mid terciles (least dilatational)
    # Rank source dots by dilatation prior (lowest first)
    src_mask = r0 & (is_low | is_mid)
    src_ys, src_xs = np.nonzero(src_mask)
    src_priors = dilat_prior[src_ys, src_xs]
    src_order = np.argsort(src_priors, kind="stable")
    print(f"Source dots (low+mid): {len(src_ys)}")

    # Candidate refill pool: high dilatation tercile, H19-5 positive, d_cat>2, in footprint, not already in R0
    cand_mask = h19 & is_high & (d_cat > 2.0) & foot & (~r0) & valid_dilat
    print(f"Refill candidates (high dilatation, H19-5, d_cat>2): {int(np.sum(cand_mask))}")
    if int(np.sum(cand_mask)) < 6000:
        raise RuntimeError(f"Candidate pool too small: {int(np.sum(cand_mask))} < 6000 needed for 15% shift")

    # Dose ladder
    doses = [
        ("p10dilatation", 0.10, int(round(0.10 * n_parent)), "+0.005", "[-0.004,+0.016]"),
        ("p12dilatation", 0.12, int(round(0.12 * n_parent)), "+0.007", "[-0.003,+0.019]"),
        ("p15dilatation", 0.15, int(round(0.15 * n_parent)), "+0.006", "[-0.005,+0.018]"),
    ]

    variants = []
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    for val_name, frac, n_shift, pred_mean, pred_range in doses:
        print(f"\nBuilding DILATATION {val_name}: shifting {n_shift} dots ({frac*100:.0f}%) low→high dilatation...")
        drop_y = src_ys[src_order[:n_shift]]
        drop_x = src_xs[src_order[:n_shift]]

        base_mask = r0.copy()
        base_mask[drop_y, drop_x] = False
        assert int(np.sum(base_mask)) == n_parent - n_shift

        cands_for_rung = cand_mask & (~base_mask)
        final_mask = select_exact_marginal_dti_add(
            base_mask=base_mask,
            cand_mask=cands_for_rung,
            w=dti_weight,
            n_add=n_shift,
        )
        final_ys, final_xs = np.nonzero(final_mask)
        assert len(final_ys) == n_parent, f"Count {len(final_ys)} != {n_parent}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat violation"
        assert np.sum(final_mask & cat) == 0, "catalogue mass violation"

        # Distribution check
        final_dill = dilat[final_mask]
        n_b_low = int(np.sum(final_dill < p33))
        n_b_mid = int(np.sum((final_dill >= p33) & (final_dill < p67)))
        n_b_high = int(np.sum(final_dill >= p67))

        # Write both encodings
        stem_base = f"{PARENT_ID}-DILATATION{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()

        stem = f"{PARENT_ID}-DILATATION{val_name}-{DATE}-{sha8}"
        nan_file = f"{stem}.tif"
        zeros_file = f"{stem}-zeros.tif"
        nan_path = OUT_DIR / nan_file
        zeros_path = OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)

        sha_nan_disk = sha256_file(nan_path)
        sha_zeros_disk = sha256_file(zeros_path)
        assert sha_nan_disk == sha_nan

        # Validate
        nan_checks = validate_reopened(nan_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=False)

        moved_pct = float(n_shift / n_parent * 100.0)
        form_note = f"{PARENT_ID}; DILATATION shift {n_shift} dots ({frac*100:.0f}%) low→high dilat; pred MODEL:{pred_mean}"
        assert len(form_note) <= 140, f"Form note {len(form_note)} >140: {form_note}"

        variant_meta = {
            "id": stem,
            "site": "GEMSDOE92",
            "name": nan_file,
            "file_zeros": f"releases/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": f"DILATATION shift {n_shift} dots ({frac*100:.1f}%) low/mid→high dilatation tercile; fixed 37654 dots",
            "notes": f"frac={frac:.2f}; n_shifted={n_shift}; low={n_b_low}; mid={n_b_mid}; high={n_b_high}; p33={p33:.2f}; p67={p67:.2f}; MODEL range {pred_range}; git={git_sha[:12]}",
            "parent": PARENT_ID,
            "axis": "DILATATION",
            "value": val_name,
            "n_dots": n_parent,
            "pct_changed": moved_pct,
            "removed": n_shift,
            "added": n_shift,
            "sha256": sha_nan_disk,
            "sha256_zeros": sha_zeros_disk,
            "primary_file": nan_file,
            "fallback_file": zeros_file,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": f"MODEL:{pred_mean}",
            "predicted_range": pred_range,
            "prediction_scope": "MODEL scenario range; public chunk deltas under 0.01 are no evidence.",
            "dilatation_distribution": {
                "low_dots": n_b_low, "low_pct": float(n_b_low/n_parent*100),
                "mid_dots": n_b_mid, "mid_pct": float(n_b_mid/n_parent*100),
                "high_dots": n_b_high, "high_pct": float(n_b_high/n_parent*100),
                "p33_nstrain_per_yr": float(p33), "p67_nstrain_per_yr": float(p67),
            },
            "parent_diff": {
                "removed": n_shift, "added": n_shift, "shared": n_parent - n_shift,
                "moved_pct": moved_pct,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates; EPSG:32611, 3730x3292, float32, binary unit-mass, d_cat>2.0)",
            "seed": 0,
        }
        variants.append(variant_meta)
        print(f"PASS {stem} (sha256={sha_nan_disk[:12]}..., high={n_b_high} [{n_b_high/n_parent:.1%}])")

    # Write evidence
    evidence_doc = {
        "schema": "gemsdoe92.dilatation-variants.v1",
        "session_date_utc": DATE,
        "axis": "DILATATION",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n_parent, "zeros_sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
            "nan_sha256": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
            "matches_recorded_hashes": True,
        },
        "dilatation_terciles": {
            "band": "Band 8 geod_dilaterate (geodetic dilatation rate, nstrain/yr)",
            "p33": float(p33), "p67": float(p67),
            "r0_baseline": {"low_dots": n_low, "low_pct": float(n_low/n_parent*100), "mid_dots": n_mid, "mid_pct": float(n_mid/n_parent*100), "high_dots": n_high, "high_pct": float(n_high/n_parent*100)},
        },
        "variants": variants,
        "scope_note": "No submission, leaderboard, or hidden labels accessed. Prior uses only dilatation + TMI/grav/scarp plausibility, no catalogue.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2), encoding="utf-8")

    # Append to ledger
    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys()) if existing_rows else ["id","parent","axis","value","n_dots","pct_changed","sha256","status","predicted_change","file_zeros","file_nan","sha8","change_desc","receipt_score","receipt_date","notes"]
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k, "") for k in fieldnames}
        # Map correct fields
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

    # Merge mechanism cards
    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID, "axis": "DILATATION", "value": v["value"],
            "hypothesis": "Geodetic dilatation (volumetric extensional strain, Band 8 geod_dilaterate) marks where the crust is actively opening. Great Basin geothermal systems concentrate in dilatational step-overs/relay ramps (32% of systems) and terminations/intersections (45% combined) where opening fractures provide vertical permeability (Faulds et al. 2006, 2021a). Shifting dots from contractive/low-dilatation pixels into the high-dilatation tercile increases the probability of intersecting a blind, actively dilating fault without surface scarp.",
            "mechanism": "At fixed S=37,654, DTI rises when T gains outweigh S-M+|G|. Dilatational zones have higher expected truth density; weighting H19-5 ridge placement by 0.70*dilatation + 0.30*geophysical plausibility (TMI/grav/scarp) via exact marginal DTI greed places new dots where kernel credit k(d)=1-d/3 is most likely to be earned, without cannibalizing existing coverage.",
            "non_fault_mimic": "Alluvial subsidence bowls (Clayton Valley brine pumping, agricultural drawdown), elastic strain shadows around locked Walker Lane strike-slip segments, and thick-fill basin stretching without brittle faulting can produce high dilatation without Quaternary fault permeability. A high-dilatation dot in deep basin fill (depth_to_base_surf >1500 m, Band 15) may be ductile stretching, not a fault.",
            "predicted_sign_and_size": f"{v['predicted_change']} (range {v['predicted_range']}); 10-20% of shifted dots converting from 0 to ~2.5 credit units yields +0.005-0.008 DTI.",
            "falsifier": "Live receipt delta <= -0.010 vs R0 rejects active dilatation as predictor; it would imply Phase-2 truth is dominated by inactive exhumed structures or compressional relics where dilatation is low. |delta|<0.01 is no evidence.",
            "decision_rule": "Treat absolute live change <0.01 as no evidence; compare only organizer receipts.",
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
