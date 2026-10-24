#!/usr/bin/env python3
"""Build three deterministic PIEDFRONT variants from parent R0 (session 2026-10-24).

Axis: PIEDFRONT -- piedmont range-front relative scarp-break & isostatic gravity
concordance, combining on-skeleton piedmont hole repair with off-skeleton
(>3 px from H19-5) discovery.  Pre-registered rank-1 hypothesis in
docs/HYPOTHESES_20261024_PIEDFRONT.md.

Parent R0: h33-h33-2-b2 (37,654 unit-mass dots; d_cat > 2.0 px).
Surface (gems/piedfront.py, from pinned training_features.tif Bands 5, 12, 15, 19):

    R_scarp(x) = pct_rank(||grad det_elev_slope|| / (max(det_elev_slope,0) + 2.0))
                 * coherence(det_elev)(x)
    W_pied(x)  = exp(-0.5*((pct_rank(det_elev)-0.45)/0.28)^2)
                 * exp(-0.5*((pct_rank(depth_to_base)-0.50)/0.35)^2)
                 * (0.50 + 0.50 * pct_rank(iso_grav_anom_slope)(x))
    S_raw(x)   = R_scarp(x) * W_pied(x),   S_pct(x) = pct_rank(S_raw(x))

Two-stage placement at fixed S = 37,654 dots (resolving NEXT_STEPS items 2 & 3):
1. ON-SKELETON (N_skel = 37,654 - N_far dots on H19-5, d_cat > 2.0 px):
   Keep the top (N_skel - 4,000) dots of R0 ranked by w_pf = (0.30 + 0.70*S_pct)*W_pied,
   then refill 4,000 piedmont H19-5 skeleton holes (h19 & is_piedmont & d_cat>2 & ~R0)
   via exact marginal expected-DTI greedy (select_exact_marginal_dti_add) under
   dti_weight = where(h19, 0.30 + 0.70*S_pct, 0.08*S_pct), repairing the 794 spacing-legal
   holes left when R0 deleted D2.8's d_cat<=2 dots without re-thinning.
2. OFF-SKELETON FAR (N_far dots, f_far in {0.35, 0.40, 0.45}):
   spaced_top_mask(S_raw, far_cand, N_far, min_dist_px=2.8) over valid pixels >3 px
   from every H19-5 pixel, >2 px from the catalogue, and >3 px from the off-skeleton
   dots of prior off-skeleton lanes (BREAKLINE f45, SCARPPOL f45, STRAINBREAK f60,
   ANASIG f45, SPRINGALIGN f33).

By construction, all N_skel dots lie on H19-5 and all N_far dots lie >3 px off H19-5
and >3 px off prior off-skeleton far sets, bounding whole-file 3-px forward overlap
against every local registry raster by (1 - f_far) in {0.65, 0.60, 0.55} <= 0.70.
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

from build_snap_scarp_variants import (  # noqa: E402
    build_and_verify_parent,
    validate_reopened,
    verify_all_manifests,
    write_tif,
)
from exact_dti_refill import select_exact_marginal_dti_add  # noqa: E402
from gems.piedfront import piedfront_surface, spaced_top_mask  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "piedfront_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"
N_PIED_REFILL = 4000

PRIOR_FAR_RASTERS = [
    ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
    ROOT / "releases/h33-h33-2-b2-SCARPPOLf45Stop-20261024-cf4e45c0-zeros.tif",
    ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
    ROOT / "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
    ROOT / "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif",
]

MECHANISM_CARD = {
    "hypothesis": (
        "Active Quaternary normal faults and blind range-front geothermal conduits in the "
        "Great Basin localize at the piedmont-range-front transition where bedrock steps down "
        "across a subsurface density gradient (Band 5 iso_grav_anom_slope) into moderate "
        "alluvial cover (Band 15 depth_to_base_surf, Band 12 det_elev), expressing at the "
        "surface as a sharp relative break-in-slope ||grad(det_elev_slope)||/(det_elev_slope+2 deg) "
        "(Band 19) along an orientation-coherent lineament (Band 12). Unnormalized BREAKLINE "
        "placed 74.8% of its far dots in steep mountain range interiors; normalizing by background "
        "slope and gating by the piedmont gravity-cover envelope concentrates 82.5% of far "
        "candidates in the piedmont while repairing R0's post-b2 skeleton holes."
    ),
    "mechanism": (
        "At fixed S=37,654 unit-mass dots, on-skeleton dots (N_skel = 37,654 - N_far) keep the "
        "highest-w_pf R0 dots and refill 4,000 piedmont H19-5 holes (left when R0 pruned d_cat<=2 "
        "after D2.8 thinning) via exact marginal expected-DTI greedy under S_pct. Off-skeleton "
        "dots (N_far in {13179, 15062, 16944}, 35/40/45%) are placed by spaced_top_mask (2.8 px "
        "floor) on S_raw strictly >3 px off H19-5 and >3 px off prior off-skeleton lanes' far sets."
    ),
    "non_fault_mimic": (
        "Pluvial Lake Lahontan wave-cut shoreline terraces and beach ridges at piedmont "
        "elevations (~1,200-1,330 m AMSL) overlying regional basin-margin gravity gradients, "
        "incised alluvial-fan terrace risers (fan-head trenches), and pediment-alluvium contacts."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat both R0 (0.004006) and the holdout best RELIEF p10 "
        "(0.006045) with paired 95% CI excluding 0, or SGMC off-catalogue DTI falling below R0 "
        "(0.096060), or any single-feature leakage canary > 0.90, or local registry forward "
        "overlap > 0.70 / |rho| > 0.90."
    ),
    "decision_rule": (
        "Promote locally only if pooled HOLDOUT-DTI beats RELIEF p10 (0.006045) with paired CI "
        "excluding 0 vs R0 AND vs RELIEF p10, SGMC PROXY beats R0 (0.096060), leakage canaries "
        "<= 0.90, local registry uniqueness passes on surface and final dots, and 10/10 format "
        "gates pass. Public dense-witness policy blocker (17GEMSDOE E-proba 100% footprint halo) "
        "remains reported and binding for live slot eligibility until operator policy resolution."
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

    print("Loading Bands 5 (iso_grav_anom_slope), 12 (det_elev), 15 (depth_to_base_surf), 19 (det_elev_slope)...")
    with rasterio.open(inputs["training_features"]) as ds:
        grav_slope = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        depth_base = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    valid = (
        foot
        & np.isfinite(grav_slope) & (grav_slope > -1e30)
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(depth_base) & (depth_base > -1e30)
        & np.isfinite(det_slope) & (det_slope > -1e30)
    )
    print(f"Footprint {int(foot.sum())}, valid 4-band intersection {int(valid.sum())}")

    p33, p67 = np.percentile(det_elev[valid], [33.333333, 66.666667])
    is_piedmont = valid & (det_elev >= p33) & (det_elev < p67)

    surf = piedfront_surface(det_elev, det_slope, grav_slope, depth_base, valid)
    s_raw, s_pct, w_pied = surf["S_raw"], surf["S_pct"], surf["W_pied"]

    # Save pre-placement surface into gitignored .cache/ for surface uniqueness audit
    surf_path = ROOT / ".cache" / "piedfront_surface.tif"
    surf_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(inputs["sample_submission"]) as ds:
        s_prof = ds.profile.copy()
    s_prof.update(dtype="float32", count=1, nodata=None)
    with rasterio.open(surf_path, "w", **s_prof) as ds:
        ds.write(s_pct.astype(np.float32), 1)
    surf_sha = sha256_file(surf_path)
    print(f"Saved pre-placement surface: {surf_path} (sha256={surf_sha[:12]}...)")

    d_h19 = distance_transform_edt(~h19)

    # Accumulate off-skeleton dots of prior off-skeleton lanes to repel >3 px
    prior_far_union = np.zeros_like(foot, dtype=bool)
    for p in PRIOR_FAR_RASTERS:
        if p.is_file():
            with rasterio.open(p) as ds:
                m = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
            prior_far_union |= m & (d_h19 > 3.0)
    d_prior_far = distance_transform_edt(~prior_far_union)
    print(f"Prior off-skeleton far dots repelled (>3 px): {int(prior_far_union.sum())}")

    far_cand = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0) & (d_prior_far > 3.0)
    n_far_cand = int(far_cand.sum())
    print(f"Far candidates (>3 px off H19-5 & prior far sets, d_cat>2): {n_far_cand}")
    if n_far_cand < 400_000:
        raise RuntimeError(f"Far candidate pool too small: {n_far_cand}")

    # On-skeleton weight and candidate pool for piedmont H19-5 hole repair
    w_pf = ((0.30 + 0.70 * s_pct) * w_pied).astype(np.float32)
    w_pf[~valid] = 0.0
    dti_weight = np.where(h19 & valid, 0.30 + 0.70 * s_pct, 0.08 * s_pct).astype(np.float32)
    dti_weight[~valid] = 0.0

    r0_ys, r0_xs = np.nonzero(r0)
    n_parent = len(r0_ys)
    assert n_parent == 37654
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))

    # Deterministic ranking of R0 dots by w_pf (highest kept first; ties broken by y, x)
    r0_scores = w_pf[r0_ys, r0_xs]
    r0_order_desc = np.lexsort((r0_xs, r0_ys, -r0_scores))

    pied_skel_cand = h19 & is_piedmont & (d_cat > 2.0) & foot & (~r0)
    print(f"Piedmont H19-5 hole-repair candidates (h19 & is_piedmont & d_cat>2 & ~r0): {int(pied_skel_cand.sum())}")

    doses = [
        ("f35Ptop", 0.35, int(round(0.35 * n_parent))),
        ("f40Ptop", 0.40, int(round(0.40 * n_parent))),
        ("f45Ptop", 0.45, int(round(0.45 * n_parent))),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, frac, n_far in doses:
        n_skel = n_parent - n_far
        n_keep_r0 = n_skel - N_PIED_REFILL
        print(
            f"\nBuilding PIEDFRONT {val_name}: {n_keep_r0} kept R0 + {N_PIED_REFILL} piedmont H19-5 refill "
            f"({n_skel} on-skeleton) + {n_far} far off-skeleton ({frac*100:.0f}%)..."
        )

        r0_kept_mask = np.zeros_like(r0, dtype=bool)
        keep_idx = r0_order_desc[:n_keep_r0]
        r0_kept_mask[r0_ys[keep_idx], r0_xs[keep_idx]] = True
        assert int(r0_kept_mask.sum()) == n_keep_r0

        skel_mask = select_exact_marginal_dti_add(
            base_mask=r0_kept_mask,
            cand_mask=pied_skel_cand & (~r0_kept_mask),
            w=dti_weight,
            n_add=N_PIED_REFILL,
        )
        assert int(skel_mask.sum()) == n_skel
        assert not np.any(skel_mask & ~h19), "on-skeleton dot placed off H19-5"

        far_added = spaced_top_mask(s_raw, far_cand, n_far, min_dist_px=2.8, cand_cap=500_000)
        assert int(far_added.sum()) == n_far
        assert not np.any(far_added & skel_mask)

        final_mask = skel_mask | far_added
        assert int(final_mask.sum()) == n_parent
        assert np.all(d_h19[far_added] > 3.0), "far dot within 3 px of H19-5"
        assert np.all(d_prior_far[far_added] > 3.0), "far dot within 3 px of prior off-skeleton lane"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert np.sum(final_mask & cat) == 0, "catalogue mass violation"

        # Relief distribution of final dots and far dots
        fe = det_elev[final_mask]
        n_b = int(np.sum(fe < p33))
        n_p = int(np.sum((fe >= p33) & (fe < p67)))
        n_r = int(np.sum(fe >= p67))
        fe_far = det_elev[far_added]
        far_pied_frac = float(np.mean((fe_far >= p33) & (fe_far < p67)))

        stem_base = f"{PARENT_ID}-PIEDFRONT{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()

        stem = f"{stem_base}-{sha8}"
        nan_file = f"{stem}.tif"
        zeros_file = f"{stem}-zeros.tif"
        nan_path = OUT_DIR / nan_file
        zeros_path = OUT_DIR / zeros_file
        write_tif(nan_path, profile, foot, final_mask, nan_outside=True)
        write_tif(zeros_path, profile, foot, final_mask, nan_outside=False)
        sha_nan_disk = sha256_file(nan_path)
        sha_zeros_disk = sha256_file(zeros_path)
        assert sha_nan_disk == sha_nan

        nan_checks = validate_reopened(
            nan_path, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=True,
        )
        zeros_checks = validate_reopened(
            zeros_path, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=False,
        )

        dropped_r0 = r0 & (~final_mask)
        n_changed = int(dropped_r0.sum())
        pct_changed = float(n_changed / n_parent * 100.0)
        form_note = (
            f"{PARENT_ID}; PIEDFRONT {val_name} {n_far} far piedmont scarp-gravity dots >3px off H19-5 "
            f"+ {N_PIED_REFILL} H19-5 hole refill"
        )
        assert len(form_note) <= 140, f"Form note {len(form_note)} > 140: {form_note}"

        variants.append({
            "id": stem,
            "site": "GEMSDOE92",
            "name": nan_file,
            "file_zeros": f"releases/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (
                f"PIEDFRONT re-emission: keep {n_keep_r0} R0 + refill {N_PIED_REFILL} piedmont H19-5 holes "
                f"({n_skel} on-skeleton) + {n_far} far dots ({frac*100:.0f}%) on piedmont relative scarp-break "
                f"x gravity slope >3px off H19-5 and prior far sets; fixed 37654 dots"
            ),
            "notes": (
                f"frac_far={frac:.2f}; n_far={n_far}; n_skel={n_skel}; n_keep_r0={n_keep_r0}; "
                f"n_pied_refill={N_PIED_REFILL}; far_piedmont_frac={far_pied_frac:.4f}; "
                f"max_on_skel_overlap_bound={n_skel/n_parent:.4f}; git={git_sha[:12]}"
            ),
            "parent": PARENT_ID,
            "axis": "PIEDFRONT",
            "value": val_name,
            "n_dots": n_parent,
            "pct_changed": pct_changed,
            "removed": n_changed,
            "added": n_changed,
            "sha256": sha_nan_disk,
            "sha256_zeros": sha_zeros_disk,
            "primary_file": nan_file,
            "fallback_file": zeros_file,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/piedfront_proxy_audit.json",
            "predicted_range": "not projected (a projection is never written as a score)",
            "prediction_scope": "MODEL scope note only; organizer score requires a submission receipt.",
            "relief_distribution": {
                "basin_dots": n_b,
                "basin_pct": float(n_b / n_parent * 100.0),
                "piedmont_dots": n_p,
                "piedmont_pct": float(n_p / n_parent * 100.0),
                "range_dots": n_r,
                "range_pct": float(n_r / n_parent * 100.0),
                "far_piedmont_pct": float(far_pied_frac * 100.0),
            },
            "parent_diff": {
                "removed": n_changed,
                "added": n_changed,
                "shared_with_r0": n_keep_r0,
                "on_skeleton_total": n_skel,
                "piedmont_h19_refill": N_PIED_REFILL,
                "far_off_skeleton": n_far,
                "moved_pct": pct_changed,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_added].min()),
                "far_min_distance_to_prior_far_px": float(d_prior_far[far_added].min()),
                "collar_dots_final_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "collar_dots_parent_dcat_le_3": collar_r0,
                "mean_S_pct_far": float(s_pct[far_added].mean()),
                "mean_S_pct_dropped_r0": float(s_pct[dropped_r0].mean()),
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates; EPSG:32611, 3730x3292, float32, binary unit-mass, d_cat>2.0)",
            "seed": 0,
        })
        print(
            f"PASS {stem} (zeros sha256={sha_zeros_disk[:12]}..., "
            f"piedmont_total={n_p/n_parent:.1%}, far_piedmont={far_pied_frac:.1%})"
        )

    EVIDENCE.write_text(
        json.dumps(
            {
                "schema": "gemsdoe92.piedfront-variants.v1",
                "session_date_utc": DATE,
                "axis": "PIEDFRONT",
                "parent": PARENT_ID,
                "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
                "exact_parent_rebuild": {
                    "n_dots": n_parent,
                    "zeros_sha256": "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
                    "nan_sha256": "baeae3219bba6a19bc8cfe79224e28555c50184b7c1ca65c2a822f54807c77dd",
                    "matches_recorded_hashes": True,
                },
                "lane_surface": {
                    "definition": (
                        "S_raw = R_scarp * W_pied; R_scarp = pct_rank(||grad det_elev_slope|| / "
                        "(max(det_elev_slope,0)+2.0)) * coherence(det_elev); W_pied = "
                        "exp(-0.5*((elev_pct-0.45)/0.28)^2) * exp(-0.5*((depth_pct-0.50)/0.35)^2) "
                        "* (0.50 + 0.50*grav_slope_pct)"
                    ),
                    "bands": (
                        "training_features Band 5 iso_grav_anom_slope, Band 12 det_elev, "
                        "Band 15 depth_to_base_surf, Band 19 det_elev_slope"
                    ),
                    "implementation": "gems/piedfront.py",
                    "surface_cache_sha256": surf_sha,
                    "catalogue_use": "none in S_raw, S_pct, W_pied, keep ranking, or refill weight; inherited d_cat>2.0px exclusion only",
                    "far_candidate_pool": {
                        "rule": (
                            "footprint AND valid 4-band intersection AND d_cat>2.0px AND d_H19>3.0px "
                            "AND not in R0 AND >3.0px from prior off-skeleton far sets"
                        ),
                        "n_candidates": n_far_cand,
                        "prior_far_dots_repelled": int(prior_far_union.sum()),
                    },
                    "on_skeleton_rule": (
                        "keep top (N_skel - 4000) R0 dots by w_pf = (0.30+0.70*S_pct)*W_pied, "
                        "refill 4000 piedmont H19-5 holes (h19 & is_piedmont & d_cat>2 & ~R0) "
                        "via select_exact_marginal_dti_add"
                    ),
                    "far_refill_rule": "spaced_top_mask(S_raw, far_cand, n_far, min_dist_px=2.8, cand_cap=500000)",
                },
                "variants": variants,
                "scope_note": "No submission, leaderboard, or hidden labels accessed.",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: v.get(k, "") for k in fieldnames}
        row.update({
            "id": v["id"],
            "parent": v["parent"],
            "axis": v["axis"],
            "value": v["value"],
            "n_dots": str(v["n_dots"]),
            "pct_changed": f"{v['pct_changed']:.6f}",
            "sha256": v["sha256"],
            "status": "BUILT",
            "predicted_change": v["predicted_change"],
            "file_zeros": v["file_zeros"],
            "file_nan": v["file_nan"],
            "sha8": v["sha8"],
            "change_desc": v["change_desc"],
            "receipt_score": "",
            "receipt_date": "",
            "notes": v["notes"],
        })
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "PIEDFRONT",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
