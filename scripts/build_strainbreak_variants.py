#!/usr/bin/env python3
"""Build two deterministic STRAINBREAK variants from parent R0 (2026-10-24 late session).

Axis: STRAINBREAK -- coherent DEM scarp-breaks under high geodetic strain
rate, emitted >3px off the H19-5 worm skeleton.  Ranked hypothesis 2 in
docs/HYPOTHESES_20261024_GRAVCrest.md; rank-1 GRAVCrest was falsified by the
pre-build screen (evidence/gravcrest_screen.json: far-only SGMC DTI
0.005-0.016 vs 0.072 for plain BREAKLINE L) and was NOT built.

Surface (gems/strainbreak.py, from pinned training_features.tif tags:
Band 19 det_elev_slope, Band 12 det_elev, Band 4 geod_2ndinv):

    S = L_raw * pct_rank(geod_2ndinv),  S_pct = pct_rank(S)

KEEP: exact marginal expected-DTI greedy over R0 dots only under
w = 0.30 + 0.70*S_pct on H19-5 support (shared tool, as BREAKLINE).
FAR: spaced top-S (descending S_raw, 2.8px floor) over pixels >3px from
every H19-5 pixel, >2px from catalogue, valid topo+strain, off parent --
AND >3px from every far dot of BREAKLINE f45Ltop, the sibling file whose
far set is the only plausible >70% forward-overlap witness for a second
off-skeleton terrain lane.  Doses f45 (16,944 far) and f60 (22,592 far);
each file exactly 37,654 unit dots.  Whole-file forward overlap vs the
H19-5 lineage equals the kept fraction by construction; measured (not
assumed) against all local registry rasters in
scripts/report_strainbreak_proxies.py.

No catalogue information enters S beyond the inherited d_cat>2px exclusion.
Writes releases/<id>.tif (NaN outside) + <id>-zeros.tif, re-gates both,
appends ledger/submissions.csv + mechanism cards, records
evidence/strainbreak_variants.json.  Structure mirrors
build_breakline_variants.py (shared tools reused, not forked).
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
from gems.breakline import spaced_top_mask
from gems.strainbreak import strainbreak_surface

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "strainbreak_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"
BREAKLINE_F45 = ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif"

MECHANISM_CARD = {
    "hypothesis": (
        "A linear DEM break-in-slope (BREAKLINE L: pct_rank(||grad det_elev_slope||) x "
        "structure-tensor coherence of det_elev) that also sits in high geodetic strain-rate "
        "crust (Band 4 geod_2ndinv percentile) is a scarp on a structure that is currently "
        "loading. Young, still-propagating strands in extensional step-overs/relay ramps can "
        "be geomorphically subtle -- missing from the Qfaults-based catalogue and from the "
        "potential-field worm skeleton -- while actively straining (cf. the 2020 M6.5 Monte "
        "Cristo Range rupture of largely unmapped Candelaria-fault strands). Emitting 45-60% "
        "of the fixed budget on strained coherent breaks >3px off the skeleton (and >3px off "
        "BREAKLINE f45's far dots) tests the strain multiplier as an independent lane."
    ),
    "mechanism": (
        "At fixed S=37,654, DTI rises when expected kernel credit per dot rises. Kept skeleton "
        "dots are chosen by exact marginal expected-DTI greedy (alpha 0.2, beta 0.8, R=3px) "
        "under w=0.30+0.70*S_pct on H19-5 support, so coverage-redundant, low-strain parent "
        "dots are the donors. Far dots take the strongest strained breaks first (descending "
        "S_raw, 2.8px spacing floor): if per-pixel new-fault probability is concentrated where "
        "terrain lineaments and active strain coincide, those dots earn more expected credit "
        "than R0's unranked thinning or BREAKLINE's strain-blind top-L set."
    ),
    "non_fault_mimic": (
        "Walker Lane elastic strain shadows (high total strain rate, shear-parallel, no open "
        "normal fault), alluvial compaction/subsidence strain, and -- inherited from L -- "
        "Lake Lahontan shoreline terraces and alluvial-fan segment boundaries lying in "
        "strained crust all score high on S with no Quaternary fault."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI at or below BREAKLINE f45Ltop (0.004861) with paired CI excluding "
        "a gain rejects the strain multiplier on the catalogue instrument; the pre-build screen "
        "already showed the strain far set UNDERPERFORMS plain L on the SGMC bedrock control "
        "(0.058 vs 0.072 far-only), so a holdout win driven only by catalogue-proximity would "
        "not promote this lane either. Live receipt delta <= -0.010 vs R0 would reject it live."
    ),
    "decision_rule": (
        "Promote only if literal uniqueness (<=70% dots within 3px of every measured registry "
        "raster, |Spearman| <= 0.90, surface and final dots) AND pooled HOLDOUT-DTI beats the "
        "current holdout best comparable arms (RELIEF p10 0.006045; BREAKLINE f45 0.004861) "
        "with paired CI excluding 0 vs R0. Otherwise verdict negative: format-valid and "
        "downloadable, not cleared for a weekly slot."
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
    assert not np.any(r0 & ~h19), "R0 is not a subset of H19-5"

    print("Loading Bands 12/19 (topography) + 4 (geod_2ndinv)...")
    with rasterio.open(inputs["training_features"]) as ds:
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
        strain = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
    valid_topo = (foot & np.isfinite(det_elev) & (det_elev > -1e30)
                  & np.isfinite(det_slope) & (det_slope > -1e30))
    valid_strain = foot & np.isfinite(strain) & (strain > -1e30)
    print(f"Footprint {int(foot.sum())}, valid topo {int(valid_topo.sum())}, valid strain {int(valid_strain.sum())}")

    surf = strainbreak_surface(det_elev, det_slope, strain, valid_topo, valid_strain)
    s_pct, s_raw, valid = surf["S_pct"], surf["S_raw"], surf["valid_both"]
    del det_elev, det_slope, strain

    d_h19 = distance_transform_edt(~h19)
    with rasterio.open(BREAKLINE_F45) as ds:
        bl45 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    bl45_far = bl45 & (d_h19 > 3.0)
    d_bl45far = distance_transform_edt(~bl45_far)
    print(f"BREAKLINE f45 far dots repelled: {int(bl45_far.sum())}")

    far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0) & (d_bl45far > 3.0)
    n_far_cand = int(far_cand.sum())
    print(f"Far candidates (>3px off H19-5 and off BREAKLINE-f45 far, d_cat>2): {n_far_cand}")
    if n_far_cand < 400000:
        raise RuntimeError(f"Far candidate pool too small: {n_far_cand}")

    w_keep = np.where(h19 & valid, 0.30 + 0.70 * s_pct, 0.08 * s_pct).astype(np.float32)
    w_keep[~foot] = 0.0
    w_keep[~valid] = 0.0

    n_parent = int(r0.sum())
    assert n_parent == 37654
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))
    import argparse
    ap = argparse.ArgumentParser(description="STRAINBREAK builder")
    ap.add_argument("--doses", default="f45s2i:0.45,f60s2i:0.60",
                    help="comma list name:frac (f75s2i:0.75 added as experiment 3 after f45<f60 dose-monotone holdout)")
    cli = ap.parse_args()
    doses = [(nm, float(fr), int(round(float(fr) * n_parent)))
             for nm, fr in (p.split(":") for p in cli.doses.split(","))]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, frac, n_far in doses:
        n_keep = n_parent - n_far
        print(f"\nBuilding STRAINBREAK {val_name}: keep {n_keep} + {n_far} far ({frac*100:.0f}%)...")
        keep_mask = select_exact_marginal_dti_add(
            base_mask=np.zeros_like(r0), cand_mask=r0.copy(), w=w_keep, n_add=n_keep)
        assert int(keep_mask.sum()) == n_keep and not np.any(keep_mask & ~r0)
        far_added = spaced_top_mask(s_raw, far_cand, n_far,
                                    cand_cap=1_000_000 if n_far > 22592 else 400_000)
        final_mask = keep_mask | far_added
        assert int(final_mask.sum()) == n_parent
        assert np.array_equal(final_mask & r0, keep_mask)
        far_mask = final_mask & (~r0)
        assert int(far_mask.sum()) == n_far
        assert np.all(d_h19[far_mask] > 3.0)
        assert np.all(d_bl45far[far_mask] > 3.0), "far dot within 3px of a BREAKLINE-f45 far dot"
        assert np.all(d_cat[final_mask] > 2.0)
        assert np.sum(final_mask & cat) == 0

        stem_base = f"{PARENT_ID}-STRAINBREAK{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha8 = sha256_file(tmp_nan)[:8]
        tmp_nan.unlink()
        stem = f"{stem_base}-{sha8}"
        nan_file, zeros_file = f"{stem}.tif", f"{stem}-zeros.tif"
        nan_path, zeros_path = OUT_DIR / nan_file, OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)
        sha_nan_disk, sha_zeros_disk = sha256_file(nan_path), sha256_file(zeros_path)

        nan_checks = validate_reopened(nan_path, inputs["sample_submission"], inputs["existing_faults"],
                                        final_mask, foot, cat, d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_path, inputs["sample_submission"], inputs["existing_faults"],
                                          final_mask, foot, cat, d_cat, expect_nan_outside=False)
        dropped = r0 & (~final_mask)
        form_note = (f"{PARENT_ID}; STRAINBREAK f{int(round(frac*100))}s2i {n_far} far dots on strained "
                     f"scarp-breaks >3px off H19-5")
        assert len(form_note) <= 140, f"Form note {len(form_note)} > 140"
        variants.append({
            "id": stem, "site": "GEMSDOE92", "name": nan_file,
            "file_zeros": f"releases/{zeros_file}", "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (f"STRAINBREAK re-emission: greedy-keep {n_keep} of R0, add {n_far} far dots "
                            f"({frac*100:.1f}%) spaced-top-S (L x strain-rate rank) >3px off H19-5 and "
                            f">3px off BREAKLINE-f45 far dots; fixed 37654 dots"),
            "notes": (f"frac_far={frac:.2f}; n_far={n_far}; n_keep={n_keep}; far_pool={n_far_cand}; "
                      f"whole_file_within3px_of_R0_by_construction={n_keep/n_parent:.4f}; git={git_sha[:12]}"),
            "parent": PARENT_ID, "axis": "STRAINBREAK", "value": val_name,
            "n_dots": n_parent, "pct_changed": float(n_far / n_parent * 100.0),
            "removed": n_far, "added": n_far,
            "sha256": sha_nan_disk, "sha256_zeros": sha_zeros_disk,
            "primary_file": nan_file, "fallback_file": zeros_file,
            "primary_encoding": "NaN outside footprint", "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/strainbreak_proxy_audit.json",
            "predicted_range": "not projected (a projection is never written as a score)",
            "prediction_scope": "MODEL scope note only; organizer score requires a submission receipt.",
            "parent_diff": {
                "removed": int(dropped.sum()), "added": n_far, "shared": n_keep,
                "moved_pct": float(n_far / n_parent * 100.0),
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_mask].min()),
                "far_min_distance_to_breakline45_far_px": float(d_bl45far[far_mask].min()),
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
        print(f"PASS {stem} (nan sha256={sha_nan_disk[:12]}..., zeros sha256={sha_zeros_disk[:12]}...)")

    if EVIDENCE.is_file():  # merge doses built in separate invocations, keyed by id
        prior = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        seen = {v["id"] for v in variants}
        variants = variants + [v for v in prior.get("variants", []) if v["id"] not in seen]
        variants.sort(key=lambda v: v["pct_changed"])
    EVIDENCE.write_text(json.dumps({
        "schema": "gemsdoe92.strainbreak-variants.v1", "session_date_utc": DATE,
        "axis": "STRAINBREAK", "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "lane_surface": {
            "definition": "S = L_raw * pct_rank(geod_2ndinv); S_pct = pct_rank(S); L from gems/breakline.py",
            "bands": "training_features Band 12 det_elev + Band 19 det_elev_slope + Band 4 geod_2ndinv (masked reads)",
            "implementation": "gems/strainbreak.py (reuses gems.breakline lane_surface/percentile_rank)",
            "screen": "evidence/gravcrest_screen.json (GRAVCrest falsified; S selected by pre-registered SGMC rule over the dilatation variant)",
            "catalogue_use": "none in S, keep ranking or refill weight; inherited d_cat>2.0px exclusion only",
            "far_candidate_pool": {"rule": "footprint AND valid topo+strain AND d_cat>2 AND d_H19>3 AND not R0 AND >3px from every BREAKLINE-f45 far dot; scan top-400k by S_raw", "n_candidates": n_far_cand},
            "keep_rule": "exact expected-DTI greedy over R0 pixels only, w=0.30+0.70*S_pct on H19-5 support",
            "refill_rule": "spaced top-S: descending S_raw, 2.8px strict spacing floor (gems.breakline.spaced_top_mask)",
        },
        "variants": variants,
        "scope_note": "No submission, leaderboard, or hidden labels accessed.",
    }, indent=2), encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f)); fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k, "") for k in fieldnames}
        row.update({"id": v["id"], "parent": v["parent"], "axis": v["axis"], "value": v["value"],
                    "n_dots": str(v["n_dots"]), "pct_changed": f"{v['pct_changed']:.6f}", "sha256": v["sha256"],
                    "status": "BUILT", "predicted_change": v["predicted_change"],
                    "file_zeros": v["file_zeros"], "file_nan": v["file_nan"], "sha8": v["sha8"],
                    "change_desc": v["change_desc"], "receipt_score": "", "receipt_date": "", "notes": v["notes"]})
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")
    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {"parent": PARENT_ID, "axis": "STRAINBREAK", "value": v["value"],
                          **MECHANISM_CARD, "predicted_sign_and_size": v["predicted_change"]}
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
