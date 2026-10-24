#!/usr/bin/env python3
"""Build the three pre-registered APRONRIDGE experiments (2026-10-24 session).

Lane: APRONRIDGE -- Thin-Cover Piedmont Accommodation Apron & Inclination-Corrected
RTP-Curvature 1D Ridges (ranked Hypothesis 1 in docs/HYPOTHESES_20261024_APRONRIDGE.md).

Reuses shared tools without private forks (Protocol Rule 2):
- Feature stack restored via scripts/restore_inputs.py (SHA-256 verified)
- Surface math in gems/apronridge.py (reusing gems.breakline primitives)
- Exact marginal expected-DTI greedy in scripts/exact_dti_refill.py
- Packaging & on-disk validation via vendor/gems57/submission_writer.py + gems/gates.py

Three pre-registered arms (hard budget = 3 experiments):
1. s60f40: 22,592 (60%) non-R0 piedmont-apron H19-5 greedy + 15,062 (40%) 1D ridge >3px off H19-5
2. s50f50: 18,827 (50%) non-R0 piedmont-apron H19-5 greedy + 18,827 (50%) 1D ridge >3px off H19-5
3. free1d: 37,654 (100%) standalone 1D APRONRIDGE crests (zero H19-5 or R0 input)
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
from exact_dti_refill import select_exact_marginal_dti_add  # noqa: E402
from gems.apronridge import lane_surface, spaced_top_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
CACHE_BUILD_DIR = ROOT / ".cache" / "apronridge_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "apronridge_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Active Quaternary range-front splays and synthetic piedmont step-faults "
        "concentrate in the thin-cover piedmont accommodation apron (Band 12 det_elev "
        "transition x Band 15 depth_to_base_surf ~20-600 m x Band 5 iso_grav_anom_slope), "
        "expressing either as coherent DEM slope-breaks (Bands 19/12) or shallow-buried "
        "Reduced-to-Pole magnetic gradient x inverted tc curvature ridges (Bands 2/6) "
        "centered directly vertically over basement contacts without raw-TMI dipolar skew."
    ),
    "mechanism": (
        "At fixed budget S=37,654 unit-mass dots, replacing R0's row-major scan-order "
        "basin/range dots with exact marginal expected-DTI greedy allocation across the "
        "full H19-5 structural network under w_skel = H_apron*(0.25+0.75*S_pct) concentrates "
        "skeleton coverage onto thin-cover piedmont fault corridors while capping H19-5 "
        "support <=60% (<70% uniqueness bound), and spaced 1D directional-crest emission "
        "(min_dist=2.8 px) >3 px off H19-5 captures off-skeleton alluvial scarps and "
        "inclination-corrected RTP basement steps while suppressing deep-playa shorelines "
        "and high-range bedrock cliffs."
    ),
    "non_fault_mimic": (
        "Intermediate-elevation pluvial shoreline benches (Sehoo/Eetza recessional strandlines) "
        "and Gilbert-delta foreset toes on piedmont fans, incised alluvial-fan terrace risers / "
        "ephemeral wash walls, and remanently magnetized Tertiary basaltic-andesite flow margins "
        "pinched out beneath thin piedmont gravel."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat repository holdout best RELIEF p10 (0.006045) "
        "on gems57-pooled-hide-v2, any single-feature leakage canary symmetric AUC >0.90, "
        "or local registry forward 3-px overlap >0.70 / |Spearman| >0.90."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats RELIEF p10 (0.006045) with paired 95% CI "
        "excluding 0 vs R0, all canaries <=0.90, 10/10 format gates pass, AND literal "
        "uniqueness passes on both local and public registries. Because the binding dense "
        "public witness (17GEMSDOE E-proba, 100% footprint positive) triggers the literal "
        "public overlap rule for every nonempty in-footprint raster until operator policy "
        "revision, never waive it silently: record submission_eligible=false and verdict=negative."
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
    n_budget = int(r0.sum())
    assert n_budget == 37654
    assert not np.any(r0 & ~h19), "R0 must be a subset of H19-5"

    print("Loading SHA-verified 19-band stack (Bands 2, 5, 6, 12, 15, 19)...")
    with rasterio.open(inputs["training_features"]) as ds:
        b2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b6 = ds.read(6, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    valid = foot.copy()
    for a in (b2, b5, b6, b12, b15, b19):
        valid &= np.isfinite(a) & (a > -1e30)
    print(f"Footprint px: {int(foot.sum())}, valid 6-band px: {int(valid.sum())}")

    surf = lane_surface(
        det_elev=b12,
        det_elev_slope=b19,
        depth_to_base=b15,
        grav_slope=b5,
        rtp=b2,
        tc=b6,
        valid=valid,
    )
    h_apron = surf["H_apron"]
    r_scarp = surf["R_scarp"]
    r_rtp = surf["R_rtp"]
    s_raw = surf["S_raw"]
    s_pct = surf["S_pct"]
    ridge_1d = surf["ridge_1d"]
    p33, p67 = surf["p33_det_elev_m"], surf["p67_det_elev_m"]
    del b2, b5, b6, b15, b19

    # Persist pre-placement surface in .cache/ for reproducible surface audits
    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    surf_tif = ROOT / ".cache" / "apronridge_surface.tif"
    write_save_prof = profile.copy()
    write_save_prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(surf_tif, "w", **write_save_prof) as ds:
        ds.write(np.where(foot, s_pct, 0.0).astype(np.float32), 1)
    surf_sha256 = sha256_file(surf_tif)
    print(f"Saved pre-placement surface {surf_tif} (sha256={surf_sha256[:16]}...)")

    d_h19 = distance_transform_edt(~h19)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    far_cand = foot & valid & ridge_1d & (d_cat > 2.0) & (d_h19 > 3.0)
    free_cand = foot & valid & ridge_1d & (d_cat > 2.0)
    print(
        f"Candidate pools: skel={int(skel_cand.sum())}, "
        f"far(>3px H19-5 & 1D crest)={int(far_cand.sum())}, "
        f"free1d={int(free_cand.sum())}"
    )

    w_skel = np.where(
        h19 & valid,
        h_apron * (0.25 + 0.75 * s_pct),
        0.10 * s_raw,
    ).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    # Pre-registered 3-experiment ablation (exact budget = 3)
    arms_spec = [
        ("s60f40", 22592, 15062, "22592 piedmont-apron H19-5 + 15062 far 1D apron/RTP ridges >3px off H19-5"),
        ("s50f50", 18827, 18827, "18827 piedmont-apron H19-5 + 18827 far 1D apron/RTP ridges >3px off H19-5"),
        ("free1d", 0, 37654, "37654 standalone 1D apron/RTP ridges (zero H19-5 or R0 skeleton input)"),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, n_skel, n_far, short_desc in arms_spec:
        print(f"\n=== Building Experiment {val_name}: n_skel={n_skel}, n_far={n_far} ===")
        if n_skel > 0:
            skel_mask = select_exact_marginal_dti_add(
                base_mask=np.zeros_like(r0),
                cand_mask=skel_cand,
                w=w_skel,
                n_add=n_skel,
            )
            far_mask = spaced_top_mask(s_raw, far_cand, n_far, min_dist_px=2.8, cand_cap=600_000)
            assert not np.any(skel_mask & far_mask)
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            skel_mask = np.zeros_like(r0)
            far_mask = spaced_top_mask(s_raw, free_cand, n_far, min_dist_px=2.8, cand_cap=800_000)
            final_mask = far_mask.copy()

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap violation"

        # Compute deterministic 8-hex digest from NaN-outside encoding (repo convention)
        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-APRONRIDGE{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        # Clean up any prior exact stem if re-running deterministically
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-APRONRIDGE-{val_name}-{DATE}"
        if n_skel > 0:
            form_note = (
                f"{PARENT_ID}; APRONRIDGE {val_name}: {n_skel} apron-H19 + {n_far} far 1D "
                f"apron/RTP ridges >3px off H19-5"
            )
        else:
            form_note = (
                f"{PARENT_ID}; APRONRIDGE {val_name}: 37654 standalone 1D piedmont-apron + "
                f"RTP ridges (0 H19-5)"
            )
        assert len(form_note) <= 140, f"form_note len {len(form_note)} > 140"

        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "APRONRIDGE", "arm": val_name, "surface_sha256": surf_sha256},
        )
        # Remove the writer's auxiliary <stem>-zeros.json in docs/downloads so only canonical
        # <stem>-audit.json lives beside <stem>-zeros.tif; archive writer receipt in .cache/
        aux_writer_json = zeros_dl_path.with_suffix(".json")
        if aux_writer_json.is_file():
            aux_writer_json.replace(CACHE_BUILD_DIR / aux_writer_json.name)

        sha_zeros_disk = sha256_file(zeros_dl_path)
        assert sha_zeros_disk == writer_receipt["sha256"]
        zeros_dl_path.chmod(0o644)
        zip_dl_path = zeros_dl_path.with_suffix(".zip")
        if zip_dl_path.is_file():
            zip_dl_path.chmod(0o644)

        nan_checks = validate_reopened(
            nan_cache_path,
            inputs["sample_submission"],
            inputs["existing_faults"],
            final_mask,
            foot,
            cat,
            d_cat,
            expect_nan_outside=True,
        )
        zeros_checks = validate_reopened(
            zeros_dl_path,
            inputs["sample_submission"],
            inputs["existing_faults"],
            final_mask,
            foot,
            cat,
            d_cat,
            expect_nan_outside=False,
        )
        gates_z = run_gates(
            str(zeros_dl_path),
            str(inputs["sample_submission"]),
            str(inputs["existing_faults"]),
            prune_radius=2,
        )
        ok_z, rep_z = summarise(gates_z)
        assert ok_z, f"Gates failed on {zeros_dl_path}:\n{rep_z}"
        gates_n = run_gates(
            str(nan_cache_path),
            str(inputs["sample_submission"]),
            str(inputs["existing_faults"]),
            prune_radius=2,
        )
        ok_n, _ = summarise(gates_n)
        assert ok_n

        # Relief tercile & channel breakdown
        z_dots = b12[final_mask]
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        rtp_dom = int(np.sum((0.85 * r_rtp[final_mask]) > r_scarp[final_mask]))
        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        moved_pct = float((n_budget - shared_r0) / n_budget * 100.0)

        variants.append(
            {
                "id": stem,
                "site": "GEMSDOE92",
                "submission_name": sub_name,
                "name": f"{stem}.tif",
                "file_zeros": f"docs/downloads/{zeros_filename}",
                "file_zip": f"docs/downloads/{stem}-zeros.zip",
                "file_nan_cache": f".cache/apronridge_builds/{stem}.tif",
                "sha8": sha8,
                "change_desc": f"APRONRIDGE ({val_name}): {short_desc}; fixed 37654 unit dots",
                "notes": (
                    f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                    f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; "
                    f"rtp_dom_dots={rtp_dom}; git={git_sha[:12]}"
                ),
                "parent": PARENT_ID,
                "axis": "APRONRIDGE",
                "value": val_name,
                "n_dots": n_budget,
                "n_skel": n_skel,
                "n_far": n_far,
                "pct_changed": moved_pct,
                "removed": n_budget - shared_r0,
                "added": n_budget - shared_r0,
                "sha256": sha_nan,
                "sha256_zeros": sha_zeros_disk,
                "zip_sha256": writer_receipt["zip_sha256"],
                "primary_file": zeros_filename,
                "fallback_file": zeros_filename,
                "status": "BUILT",
                "predicted_change": "MODEL: unprojected; HOLDOUT-DTI recorded in evidence/apronridge_proxy_audit.json",
                "predicted_range": "not projected (Protocol Rule 3)",
                "relief_distribution": {
                    "basin_dots": n_basin,
                    "basin_pct": round(n_basin / n_budget * 100.0, 3),
                    "piedmont_dots": n_pied,
                    "piedmont_pct": round(n_pied / n_budget * 100.0, 3),
                    "range_dots": n_range,
                    "range_pct": round(n_range / n_budget * 100.0, 3),
                },
                "channel_diagnostics": {
                    "rtp_channel_dominant_dots": rtp_dom,
                    "rtp_channel_dominant_frac": round(rtp_dom / n_budget, 4),
                    "within_3px_of_h19_5_frac": round(within3_h19, 6),
                    "shared_exact_pixels_with_R0": shared_r0,
                    "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                    "collar_dots_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                    "mean_S_pct_emitted": float(s_pct[final_mask].mean()),
                },
                "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
                "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
                "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
                "form_note": form_note,
                "gate_status": "PASS (submission_writer + disk reread + 10/10 gems.gates)",
                "seed": 0,
            }
        )
        print(
            f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]}... "
            f"piedmont={n_pied} ({n_pied/n_budget:.1%}), within3px_H19={within3_h19:.4f}, shared_R0={shared_r0}"
        )

    evidence_doc = {
        "schema": "gemsdoe92.apronridge-variants.v1",
        "session_date_utc": DATE,
        "axis": "APRONRIDGE",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/apronridge_surface.tif",
            "sha256": surf_sha256,
            "registry_check": "evidence/apronridge_surface_registry.json",
        },
        "lane_surface": {
            "definition": "S_raw = H_apron(B12, B15, B5) * max(R_scarp(B12, B19), 0.85 * R_rtp(B2, B6))",
            "bands": (
                "Band 2 rtp, Band 5 iso_grav_anom_slope, Band 6 tc, "
                "Band 12 det_elev, Band 15 depth_to_base_surf, Band 19 det_elev_slope"
            ),
            "implementation": "gems/apronridge.py",
            "catalogue_use": "zero in surface, skeleton weights, or ridge extraction; d_cat>2.0px gate only",
            "experiments_built": len(variants),
            "budget_limit": 3,
        },
        "variants": variants,
    }
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2) + "\n", encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: "" for k in fieldnames}
        row.update(
            {
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
                "file_nan": v["file_nan_cache"],
                "sha8": v["sha8"],
                "change_desc": v["change_desc"],
                "receipt_score": "",
                "receipt_date": "",
                "notes": v["notes"],
            }
        )
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
            "parent": PARENT_ID,
            "axis": "APRONRIDGE",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
