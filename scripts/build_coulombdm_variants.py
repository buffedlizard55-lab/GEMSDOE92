#!/usr/bin/env python3
"""Build the 3 pre-registered COULOMBDM experiments from SHA-256-verified inputs.

Pre-registered in docs/HYPOTHESES_20261024_COULOMBDM.md (strict 3-experiment budget):
  1. coulomb1d    : 0 H19-5 + 37,654 (100%) standalone 1D Canny-NMS COULOMBDM crests.
  2. s35coulomb65 : 13,179 (35%) submodular Coulomb-weighted H19-5 + 24,475 (65%)
                    spaced 1D COULOMBDM crests (>3 px off H19-5).
  3. s45coulomb55 : 16,944 (45%) submodular Coulomb-weighted H19-5 + 20,710 (55%)
                    spaced 1D COULOMBDM crests (>3 px off H19-5).

Reuses shared tools (Protocol Rule 2):
  - Feature stack restored via scripts/restore_inputs.py
  - Surface physics in gems/coulombdm.py (reusing gems.hydroconduit & gems.breakline)
  - Exact marginal expected-DTI greedy in scripts/exact_dti_refill.py
  - Fail-closed GeoTIFF + single-TIFF ZIP packaging via vendor/gems57/submission_writer.py
  - Independent disk re-read validation via gems/gates.py & vendor/gems57/validate.py
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
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
from gems.coulombdm import (  # noqa: E402
    coulombdm_surface,
    gdr_blind_thermal_plume,
    spaced_top_mask,
)
from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
CACHE_BUILD_DIR = ROOT / ".cache" / "coulombdm_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
SCREEN_JSON = ROOT / "evidence" / "coulombdm_preplacement_screen.json"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "coulombdm_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Active NW Great Basin normal and conjugate Walker Lane / Humboldt transtensional "
        "geothermal faults express across three complementary regimes: (1) piedmont-hinge "
        "one-sided monoclinal scarps, (2) concealed thin-to-moderate cover faults detected by "
        "multi-altitude upward-continued RTP magnetic tilt/demagnetization + gravity contact + "
        "MT smectite clay-cap lateral edges + blind >=80 C geothermometers, and (3) geophysically "
        "corroborated range-front/relay bedrock faults under oriented 2D Mohr-Coulomb criticality."
    ),
    "mechanism": (
        "Projects GPS/InSAR dilatation (Band 8) onto N18E extension cos^2(az-18 deg) and shear "
        "sqrt(Band 7 * Band 4) onto +/-45 deg conjugate orientations sin^2(2*(az-15 deg)) "
        "(both vanishing at N105E clamping/fan-wash azimuths), fuses rank-calibrated surface, "
        "upward-continued RTP/gravity/MT/GDR subsurface, and corroborated bedrock channels, and "
        "emits 37,654 unit-mass dots along strict bilinear Canny cross-strike 1D NMS centrelines."
    ),
    "non_fault_mimic": (
        "NNE-trending Pleistocene Lake Lahontan recessional strandlines on piedmont fans, "
        "remanently magnetized Miocene basalt dike/flow margins beneath gravel cover, "
        "saline playa-margin MT conductivity gradients, and linear lithologic contacts."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat repository best HYDROCONDUIT f45hydro (0.008549) "
        "or APRONRIDGE free1d (0.008354) on gems57-pooled-hide-v2, any single-feature canary "
        "symmetric AUC > 0.90, or local/sparse-public forward 3-px overlap > 0.70."
    ),
    "decision_rule": (
        "Promote only if literal local + public registry uniqueness passes AND pooled "
        "HOLDOUT-DTI beats current repo best with 95% CI > 0 vs R0 AND 10/10 format gates pass; "
        "under the binding 17GEMSDOE full-footprint dense public witness, never waive silently: "
        "record submission_eligible=false and verdict='negative' pending human selector policy."
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    # Enforce pre-placement canary + surface uniqueness screen before building
    if not SCREEN_JSON.is_file():
        raise RuntimeError(f"Pre-placement screen missing: {SCREEN_JSON}")
    screen = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    if not screen["leakage_canaries"]["all_pass_le_0_90"]:
        raise RuntimeError("Pre-placement leakage canary failed (>0.90)")
    for key in ("SURF_COULOMB1D_TOP37654", "SURF_COULOMBFAR_TOP37654"):
        if screen["preplacement_surface_uniqueness"][key]["duplicate"]:
            raise RuntimeError(f"Pre-placement surface duplicate on {key}; aborting")

    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    n_budget = int(r0.sum())
    assert n_budget == 37654
    assert not np.any(r0 & ~h19), "R0 must be a subset of H19-5"

    with rasterio.open(inputs["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5_gsl = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7_shr = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b11_gvg = ds.read(11, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)
        rad_u = ds.read(3)

    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        inputs["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = coulombdm_surface(
        det_elev=b12_el,
        det_elev_slope=b19_sl,
        depth_to_base=b15_db,
        grav_slope=b5_gsl,
        grav_vg=b11_gvg,
        geod_2ndinv=b4_s2i,
        geod_shearrate=b7_shr,
        geod_dilaterate=b8_dil,
        rtp=b2_rtp,
        cond_surf=b17_cd,
        rad_k=rad_k,
        rad_th=rad_th,
        rad_u=rad_u,
        gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )
    valid = np.asarray(surf["valid"], bool)
    s_raw = np.asarray(surf["S_raw"], dtype=np.float32)
    s_pct = np.asarray(surf["S_pct"], dtype=np.float32)
    hab_pct = np.asarray(surf["hab_coulomb_pct"], dtype=np.float32)
    crest_1d = np.asarray(surf["crest_1d"], bool)
    r_pied = np.asarray(surf["r_pied"], dtype=np.float32)
    r_sub = np.asarray(surf["r_sub"], dtype=np.float32)
    r_bed = np.asarray(surf["r_bed"], dtype=np.float32)
    p33 = float(surf["p33_det_elev_m"])
    p67 = float(surf["p67_det_elev_m"])
    del b2_rtp, b4_s2i, b5_gsl, b7_shr, b8_dil, b11_gvg, b15_db, b17_cd, b19_sl, rad_k, rad_th, rad_u

    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    surf_tif = ROOT / ".cache" / "gems_inputs" / "coulombdm_S_surface.tif"
    write_prof = profile.copy()
    write_prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(surf_tif, "w", **write_prof) as ds:
        ds.write(np.where(foot, s_pct, 0.0).astype(np.float32), 1)
    surf_sha256 = sha256_file(surf_tif)

    d_h19 = distance_transform_edt(~h19)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    far_cand = foot & valid & crest_1d & (d_cat > 2.0) & (d_h19 > 3.0)
    free_cand = foot & valid & crest_1d & (d_cat > 2.0)

    w_skel = np.where(
        h19 & valid,
        0.25 + 0.75 * hab_pct,
        0.05 * s_pct,
    ).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    # Strict 3-experiment budget pre-registered in docs/HYPOTHESES_20261024_COULOMBDM.md
    arms_spec = [
        ("coulomb1d", 0, 37654, "37654 standalone 1D Canny-NMS Coulomb/RTP/clay-cap ridges (0 H19-5)"),
        ("s35coulomb65", 13179, 24475, "13179 Coulomb H19-5 + 24475 off-skel 1D Coulomb/RTP/clay-cap ridges (>3px H19-5)"),
        ("s45coulomb55", 16944, 20710, "16944 Coulomb H19-5 + 20710 off-skel 1D Coulomb/RTP/clay-cap ridges (>3px H19-5)"),
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
            far_mask = spaced_top_mask(s_raw, far_cand, n_far, min_dist_px=2.8, cand_cap=650_000)
            assert not np.any(skel_mask & far_mask)
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            skel_mask = np.zeros_like(r0)
            far_mask = spaced_top_mask(s_raw, free_cand, n_far, min_dist_px=2.8, cand_cap=850_000)
            final_mask = far_mask.copy()

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap violation"

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-COULOMBDM{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-COULOMBDM-{val_name}-{DATE}"
        if n_skel > 0:
            form_note = (
                f"{PARENT_ID}; COULOMBDM {val_name}: {n_skel} Coulomb-H19 + {n_far} off-skel "
                f"1D Coulomb/RTP/clay ridges (>3px H19-5)"
            )
        else:
            form_note = (
                f"{PARENT_ID}; COULOMBDM {val_name}: 37654 standalone 1D 2D-Coulomb + "
                f"upcont-RTP/clay-cap ridges (0 H19-5)"
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
            metadata={"axis": "COULOMBDM", "arm": val_name, "surface_sha256": surf_sha256},
        )
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
            require_submission_encoding=True,
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

        z_dots = b12_el[final_mask]
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        win_sub = int(np.sum(final_mask & (r_sub >= r_pied) & (r_sub >= r_bed)))
        win_bed = int(np.sum(final_mask & (r_bed > r_pied) & (r_bed > r_sub)))
        win_pied = n_budget - win_sub - win_bed
        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        moved_pct = float((n_budget - shared_r0) / n_budget * 100.0)

        # Write initial per-file format audit sidecar (updated with public-registry scan after audit)
        audit_doc = {
            "file": zeros_filename,
            "sha256_zeros": sha_zeros_disk,
            "sha256_nan": sha_nan,
            "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
            "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
            "overall_pass": True,
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "note": "All gates PASS on independent disk reread; values in [0,1], no NaN inside footprint, zero catalogue mass",
            "n_positive_pixels": n_budget,
            "n_dots": n_budget,
            "gates_zeros_pass": True,
            "gates_nan_pass": True,
            "submission_eligible": False,
            "verdict": "negative",
            "run_card": "evidence/coulombdm_run_card.json",
        }
        (DOWNLOADS_DIR / f"{stem}-audit.json").write_text(
            json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8"
        )

        variants.append(
            {
                "id": stem,
                "site": "GEMSDOE92",
                "submission_name": sub_name,
                "name": f"{stem}.tif",
                "file_zeros": f"docs/downloads/{zeros_filename}",
                "file_zip": f"docs/downloads/{stem}-zeros.zip",
                "file_nan_cache": f".cache/coulombdm_builds/{stem}.tif",
                "sha8": sha8,
                "change_desc": f"COULOMBDM ({val_name}): {short_desc}; fixed 37654 unit dots",
                "notes": (
                    f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                    f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; "
                    f"sub_dom={win_sub}; bed_dom={win_bed}; git={git_sha[:12]}"
                ),
                "parent": PARENT_ID,
                "axis": "COULOMBDM",
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
                "predicted_change": "MODEL: unprojected; HOLDOUT-DTI recorded in evidence/coulombdm_proxy_audit.json",
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
                    "piedmont_scarp_dominant_dots": win_pied,
                    "subsurface_rtp_grav_mt_dominant_dots": win_sub,
                    "corroborated_bedrock_dominant_dots": win_bed,
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
                "gate_status": "PASS (submission_writer + disk reread + 11/11 gems.gates)",
                "seed": 0,
            }
        )
        print(
            f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]}... "
            f"pied={n_pied} ({n_pied/n_budget:.1%}), range={n_range} ({n_range/n_budget:.1%}), "
            f"within3px_H19={within3_h19:.4f}, shared_R0={shared_r0}"
        )

    evidence_doc = {
        "schema": "gemsdoe92.coulombdm-variants.v1",
        "session_date_utc": DATE,
        "axis": "COULOMBDM",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/gems_inputs/coulombdm_S_surface.tif",
            "sha256": surf_sha256,
            "screen_evidence": "evidence/coulombdm_preplacement_screen.json",
        },
        "lane_surface": {
            "definition": "S_raw = smooth(max(r_pied, r_sub, r_bed)) extracted along oriented_nms_1d",
            "bands": (
                "Bands 2 rtp, 4 geod_2ndinv, 5 iso_grav_anom_slope, 7 geod_shearrate, "
                "8 geod_dilaterate, 11 iso_grav_anom_vg, 12 det_elev, 15 depth_to_base_surf, "
                "17 cond_surf, 19 det_elev_slope + GeoDAWN K,Th,U + GDR #1391"
            ),
            "implementation": "gems/coulombdm.py",
            "catalogue_use": "zero in surface, skeleton weights, or 1D NMS extraction; d_cat>2.0px gate only",
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
            "axis": "COULOMBDM",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
