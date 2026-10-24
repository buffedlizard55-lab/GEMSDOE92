#!/usr/bin/env python3
"""Build three deterministic SCARPDIPOLE variants using shared submission_writer.py.

Axis: SCARPDIPOLE -- Hanks-Bucknam-Wallace piedmont-to-range-front scarp-diffusion
profile-curvature dipole zero-crossing (session 2026-10-24).

Budget compliance (Parallel-Run Protocol Rule 6): exactly 3 built doses:
- f42dipole : 15,815 far dots (42% >3px off H19-5) + 21,839 H19-5 dots = 37,654
- f45dipole : 16,944 far dots (45% >3px off H19-5) + 20,710 H19-5 dots = 37,654
- f50dipole : 18,827 far dots (50% >3px off H19-5) + 18,827 H19-5 dots = 37,654

Reuses:
- Cached pinned stack (.cache/gems_inputs/training_features.tif Bands 12 & 19)
- gems.breakline.spaced_top_mask (2.8 px Poisson-equivalent spacing floor)
- vendor.gems57.uniqueness.compare_array_to_registry (pre-placement surface gate)
- vendor.gems57.submission_writer.write_submission (atomic fail-closed GeoTIFF + ZIP)
- gems.gates.run_gates (10 MUST format/domain/catalogue gates)
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
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import (  # noqa: E402
    build_and_verify_parent,
    validate_reopened,
    verify_all_manifests,
    write_tif,
)
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.scarpdipole import scarpdipole_surface  # noqa: E402
from gems57 import submission_writer  # noqa: E402
from vendor.gems57.uniqueness import compare_array_to_registry  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
RELEASES_DIR = ROOT / "releases"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"
EVIDENCE = ROOT / "evidence" / "scarpdipole_variants.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Under linear hillslope diffusion dz/dt = kappa * laplacian(z) (Wallace 1977; "
        "Bucknam & Anderson 1979; Hanks et al. 1984), a degraded Basin-and-Range normal "
        "fault scarp forms an antisymmetric profile-curvature dipole along the downslope "
        "vector s_hat: convex scarp crest (z_ss < 0) upslope transitioning across z_ss = 0 "
        "at the fault trace midpoint (dz_ss/ds > 0) into a concave colluvial-wedge toe "
        "(z_ss > 0) downslope, with low along-strike bending |z_tt| and high orientation "
        "coherence within the piedmont-to-range-front habitat ([p15, p85] of Band 12 "
        "detrended elevation). Re-ranking the H19-5 share recovers piedmont scarp junctions "
        "dropped by R0's scan-order thinning, while emitting 42-50% of the 37,654-dot budget "
        ">3 px off H19-5 detects intra-alluvial and homogeneous-volcanic faults that lack "
        "magnetic/gravity contrast."
    ),
    "mechanism": (
        "Compute multi-scale (sigma = 100 m, 200 m) directional profile curvature z_ss and "
        "strike bending z_tt on Band 12 det_elev, weight positive convex->concave dipole "
        "zero-crossings by structure-tensor coherence, sqrt(pct_rank(Band 19 det_elev_slope)), "
        "and the [p15, p85] piedmont-range habitat envelope. Emit n_on dots on H19-5 "
        "(d_cat > 2 px, >=2.8 px spacing) and n_far dots >3 px off H19-5 (d_cat > 2 px, "
        ">=2.8 px spacing) via spaced_top_mask, holding total unit-mass budget at 37,654."
    ),
    "non_fault_mimic": (
        "Pleistocene Lake Lahontan regressive/highstand wave-cut shoreline scarps, fluvial "
        "terrace risers, and landslide headscarps in the [p15, p85] elevation zone can exhibit "
        "paired convex-crest / concave-toe profiles without Quaternary tectonic slip."
    ),
    "falsifier": (
        "HOLDOUT-DTI below R0 or failing to beat prior physical holdout best (RELIEF p10, "
        "0.006045), off-catalogue USGS SGMC control below R0 (0.096060), or live organizer "
        "receipt delta <= -0.010 vs R0."
    ),
    "decision_rule": (
        "Require 10/10 format gates, leakage canary <= 0.90, HOLDOUT-DTI above R0 and prior "
        "physical lanes, SGMC proxy above R0, and binding public-registry uniqueness clearance. "
        "Under the un-waived literal all-rasters positive-support rule, universal saturation "
        "witness 17GEMSDOE E-proba-multiscale (5,167,373 positive footprint cells) forces "
        "verdict negative / NOT CLEARED for a weekly slot unless continuous surfaces are exempted."
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
    n_parent = int(r0.sum())
    assert n_parent == 37654
    assert not np.any(r0 & ~h19), "R0 must be a subset of H19-5"

    with rasterio.open(inputs["training_features"]) as ds:
        det_elev = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        det_slope = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
    valid = (
        foot
        & np.isfinite(det_elev) & (det_elev > -1e30)
        & np.isfinite(det_slope) & (det_slope > -1e30)
    )

    surf = scarpdipole_surface(det_elev, det_slope, valid)
    s_pct = np.where(foot & valid & np.isfinite(surf["S_pct"]),
                     np.clip(surf["S_pct"], 0.0, 1.0), 0.0).astype(np.float32)
    habitat_lo, habitat_hi = surf["habitat_bounds_m"]  # type: ignore[misc]
    del det_elev, det_slope

    diag_dir = ROOT / ".cache" / "diag"
    diag_dir.mkdir(parents=True, exist_ok=True)
    np.save(diag_dir / "scarpdipole_S_pct.npy", s_pct)

    # Pre-placement surface check against local lane registry BEFORE emitting any dots
    local_reg_index = ROOT / "evidence" / "lane_registry_index.json"
    pre_local = compare_array_to_registry(s_pct, local_reg_index, foot)
    pre_max_rho = max(
        abs(r["spearman_full_footprint"])
        for r in pre_local["rows"]
        if r.get("spearman_full_footprint") is not None
    )
    if pre_max_rho > 0.90:
        raise RuntimeError(f"Pre-placement surface Spearman {pre_max_rho:.6f} > 0.90")
    print(f"Pre-placement surface local registry max |rho| = {pre_max_rho:.6f} (PASS <= 0.90)")

    d_h19 = distance_transform_edt(~h19)
    on_pool = foot & valid & h19 & (d_cat > 2.0)
    far_pool = foot & valid & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
    n_on_pool = int(on_pool.sum())
    n_far_pool = int(far_pool.sum())
    print(f"Candidate pools: on_H19={n_on_pool:,}, far_off_H19={n_far_pool:,}")

    doses = [
        ("f42dipole", 0.42, int(round(0.42 * n_parent))),
        ("f45dipole", 0.45, int(round(0.45 * n_parent))),
        ("f50dipole", 0.50, int(round(0.50 * n_parent))),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    variants = []
    for val_name, frac, n_far in doses:
        n_on = n_parent - n_far
        on_mask = spaced_top_mask(s_pct, on_pool, n_on, min_dist_px=2.8, cand_cap=200_000)
        far_mask = spaced_top_mask(s_pct, far_pool, n_far, min_dist_px=2.8, cand_cap=400_000)
        final_mask = on_mask | far_mask

        assert int(final_mask.sum()) == n_parent
        assert int(on_mask.sum()) == n_on and int(far_mask.sum()) == n_far
        assert not np.any(on_mask & far_mask)
        assert np.all(d_h19[far_mask] > 3.0), "far dot within 3 px of H19-5"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue mass violation"

        # Deterministic SHA8 from canonical NaN-outside release representation
        tmp_nan = RELEASES_DIR / f"._{PARENT_ID}-SCARPDIPOLE{val_name}-{DATE}.tif"
        tmp_nan.unlink(missing_ok=True)
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]

        stem = f"{PARENT_ID}-SCARPDIPOLE{val_name}-{DATE}-{sha8}"
        nan_file = f"{stem}.tif"
        zeros_file = f"{stem}-zeros.tif"
        nan_rel = RELEASES_DIR / nan_file
        zeros_rel = RELEASES_DIR / zeros_file
        nan_rel.unlink(missing_ok=True)
        zeros_rel.unlink(missing_ok=True)
        tmp_nan.replace(nan_rel)
        write_tif(zeros_rel, profile, foot, final_mask, nan_outside=False)

        # Write portal-safe downloadable zeros-outside GeoTIFF + single-TIFF ZIP via shared submission_writer.py
        dl_tif = DOWNLOADS_DIR / zeros_file
        for ext in (".tif", ".zip", ".json"):
            dl_tif.with_suffix(ext).unlink(missing_ok=True)

        sub_name = f"GEMSDOE92-SCARPDIPOLE-{val_name}-{DATE}"
        form_note = (
            f"SCARPDIPOLE {val_name}: {n_far} off-H19 scarp-dipole dots + "
            f"{n_on} piedmont H19 dots (37,654 total)"
        )
        assert len(form_note) <= 140
        writer_receipt = submission_writer.write_submission(
            dl_tif,
            final_mask.astype(np.float32),
            ROOT / "data" / "bridge" / "sample_submission.tif",
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "SCARPDIPOLE", "value": val_name, "frac_far": frac},
        )
        # Keep releases/ zeros copy byte-identical to the submission_writer output
        zeros_rel.write_bytes(dl_tif.read_bytes())
        # Remove auxiliary .json written by submission_writer for non-primary siblings if desired;
        # keeping only primary ZIP or all 3 ZIPs is valid (<230 KB each). Keep primary ZIP, clean sibling ZIP/json to stay lean.
        if val_name != "f42dipole":
            dl_tif.with_suffix(".zip").unlink(missing_ok=True)
        dl_tif.with_suffix(".json").unlink(missing_ok=True)

        sha_zeros = sha256_file(dl_tif)
        assert sha_zeros == writer_receipt["sha256"]

        nan_checks = validate_reopened(
            nan_rel, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=True,
        )
        zeros_checks = validate_reopened(
            dl_tif, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=False,
        )
        gates = run_gates(
            str(dl_tif),
            str(ROOT / "data" / "bridge" / "sample_submission.tif"),
            str(ROOT / "data" / "bridge" / "labels.tif"),
            prune_radius=2,
        )
        gates_ok, gate_report = summarise(gates)
        if not gates_ok:
            raise RuntimeError(f"Gates failed on {dl_tif}:\n{gate_report}")

        shared_r0 = int((final_mask & r0).sum())
        added_total = int((final_mask & ~r0).sum())
        removed_total = int((r0 & ~final_mask).sum())
        pct_changed = float(added_total / n_parent * 100.0)

        variants.append({
            "id": stem,
            "site": "GEMSDOE92",
            "submission_name": sub_name,
            "name": nan_file,
            "file_zeros": f"docs/downloads/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (
                f"SCARPDIPOLE {val_name}: {n_on} piedmont scarp-dipole H19-5 dots + "
                f"{n_far} off-skeleton (>3px H19-5) scarp-dipole zero-crossing dots; 37,654 total"
            ),
            "notes": (
                f"frac_far={frac:.2f}; n_far={n_far}; n_on_h19={n_on}; shared_with_r0={shared_r0}; "
                f"within3px_of_H19_by_construction={n_on/n_parent:.4f}; git={git_sha[:12]}"
            ),
            "parent": PARENT_ID,
            "axis": "SCARPDIPOLE",
            "value": val_name,
            "n_dots": n_parent,
            "n_on_h19": n_on,
            "n_far_off_h19": n_far,
            "pct_changed": pct_changed,
            "frac_far": frac,
            "removed": removed_total,
            "added": added_total,
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "primary_file": nan_file,
            "fallback_file": zeros_file,
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/scarpdipole_proxy_audit.json",
            "predicted_range": "not projected (a projection is never written as a score)",
            "form_note": form_note,
            "parent_diff": {
                "removed_from_r0": removed_total,
                "added_total": added_total,
                "shared_exact_r0": shared_r0,
                "on_h19_count": n_on,
                "far_off_h19_count": n_far,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_mask].min()),
                "collar_dots_final_dcat_le_3": int((final_mask & (d_cat <= 3.0)).sum()),
                "mean_S_pct_on": float(s_pct[on_mask].mean()),
                "mean_S_pct_far": float(s_pct[far_mask].mean()),
            },
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates],
        })
        print(f"BUILT {stem} | zeros_sha256={sha_zeros[:16]}… | shared_R0={shared_r0} | far={n_far}")

    evidence_doc = {
        "schema": "gemsdoe92.scarpdipole-variants.v1",
        "session_date_utc": DATE,
        "axis": "SCARPDIPOLE",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "lane_surface": {
            "definition": (
                "S = pct_rank(mean_{sigma in {1,2}} pct_rank(max(0, dz_ss/ds) * exp(-0.5*(z_ss/s75)^2) * "
                "(dz_ss/ds / (dz_ss/ds + |z_tt| + 1e-6))) * coherence(Band12) * sqrt(pct_rank(Band19)) * "
                "piedmont_envelope(Band12 in [p15, p85] -> 1.0 else 0.45))"
            ),
            "bands": "training_features.tif Band 12 (det_elev) and Band 19 (det_elev_slope); zero catalogue inputs",
            "habitat_bounds_det_elev_m": [round(habitat_lo, 4), round(habitat_hi, 4)],
            "implementation": "gems/scarpdipole.py + vendor/gems57/submission_writer.py",
            "preplacement_local_registry": {
                "evidence_class": "REGISTRY-MEASUREMENT",
                "worst_abs_spearman": pre_max_rho,
                "worst_rho_submission": pre_local["worst_rho_submission"],
                "rasters_checked": pre_local["registry_rasters_checked"],
            },
            "candidate_pools": {
                "on_h19_pool": n_on_pool,
                "far_off_h19_pool": n_far_pool,
            },
        },
        "variants": variants,
    }
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2) + "\n", encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    kept_rows = [r for r in existing_rows if r.get("axis") != "SCARPDIPOLE"]
    for v in variants:
        row = {k: "" for k in fieldnames}
        row.update({
            "id": v["id"],
            "parent": v["parent"],
            "axis": v["axis"],
            "value": v["value"],
            "n_dots": str(v["n_dots"]),
            "pct_changed": f"{v['pct_changed']:.6f}",
            "sha256": v["sha256_zeros"],
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
        kept_rows.append(row)
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
    cards = {k: val for k, val in cards.items() if val.get("axis") != "SCARPDIPOLE"}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "SCARPDIPOLE",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {EVIDENCE} and updated ledger ({len(kept_rows)} total rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
