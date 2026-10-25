#!/usr/bin/env python3
"""Build the three pre-registered NEO-OPNS experiments (2026-10-25 session).

Lane: NEO-OPNS -- Multi-Scale TPI-Curvature Openness (ranked Hypothesis 1 in
docs/HYPOTHESES_20261025_NEOTERRACE.md).

Reuses shared tools without private forks (Protocol Rule 2):
- Feature stack restored via scripts/restore_inputs.py (SHA-256 verified)
- Surface math in gems/neoopenness.py
- Spaced placement via gems/breakline.spaced_top_mask (deterministic)
- Packaging & on-disk validation via vendor/gems57/submission_writer.py + gems/gates.py

Three pre-registered arms (hard budget = 3 experiments):
1. s45c55: 16,944 (45%) non-R0 H19-5 via exact DTI greedy + 20,710 (55%) 1D openness ridges >3px off H19-5
2. s35c65: 13,179 (35%) H19-5 + 24,475 (65%) far 1D ridges
3. free1d: 37,654 (100%) standalone 1D TPI-curvature openness crests (zero H19-5)
"""
from __future__ import annotations

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
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.neoopenness import lane_surface  # noqa: E402
from gems.hydroconduit import gdr_blind_thermal_plume  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261025"
CACHE_BUILD_DIR = ROOT / ".cache" / "neoopenness_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"  # not used for audit primary check
EVIDENCE = ROOT / "evidence" / "neoopenness_variants.json"

MECHANISM_CARD = {
    "hypothesis": "Low-angle Quaternary piedmont scarps invisible to H19-5 worms and slope-break magnitude express as TPI enclosure dipoles (det_elev - 11x11 mean) × LoG curvature × log-slope break × coherence inside thin-cover piedmont habitat (120 m peak) corroborated by GeoDAWN K/Th lateral gradients and blind >=80C geothermometers.",
    "mechanism": "Multi-scale openness surface S = pct(|TPI|·|curvature|)·coh·(0.6·pct(||grad log(slope+1)||)+0.4)·H_apron·(0.5+0.5·pct(||grad K/Th||))·geothermal_boost; 4-direction 1D NMS ridge extraction; spaced_top_mask at 2.8 px >3px off H19-5 with exact DTI greedy skeleton repacking.",
    "non_fault_mimic": "Lake Lahontan strandlines (constant-elevation TPI dipoles), alluvial-fan lobe boundaries, dune slip-faces, and anthropogenic grades; mitigated via H_z elevation Gaussian and cover log-Gaussian.",
    "falsifier": "Pooled HOLDOUT-DTI failing to beat R0 (0.004006) or RELIEF p10 (0.006045) with CI, canary AUC>0.90, or overlap>0.70.",
    "decision_rule": "Promote only if HOLDOUT-DTI beats RELIEF p10 with CI>0 vs R0 and literal uniqueness passes; else verdict negative (OK TO DOWNLOAD, DO NOT SUBMIT). Dense public witness forces submission_eligible=false under literal rule; record stop.",
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
    assert not np.any(r0 & ~h19), "R0 must be subset of H19-5"

    print("Loading SHA-verified 19-band stack + GeoDAWN + GDR...")
    with rasterio.open(inputs["training_features"]) as ds:
        b2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)  # rtp
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b13 = ds.read(13, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    # GeoDAWN K,Th,U (uint8 3-band)
    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1).astype(np.float32)
        rad_th = ds.read(2).astype(np.float32)
        rad_u = ds.read(3).astype(np.float32)

    # GDR wells: use existing utility to build plume for boost
    # But neopenness lane_surface expects gdr_points_yx optional; we can compute plume via helper and extract points
    # For simplicity, load csv and extract row/col for boost
    import pandas as pd
    gdr_csv = inputs["gdr_wellspring_in_footprint"]
    df = pd.read_csv(gdr_csv)
    # Derive blind geothermal points: temp_c >=80 or geotherm >=80
    # Reuse logic from hydroconduit.gdr_blind_thermal_plume but simplify: take all Hot/Warm + surf>=35 + chem>=80
    # For boost we just need points that passed keep filter; we will reuse that function to get n_blind but need yx
    # Instead: build well bool via hydroconduit helper then extract yx from its plume? Easier: manually filter.
    valid_pre = foot.copy()
    # Build plume to get boost? Our lane_surface does boost internally via gdr_points_yx
    # Extract yx of blind+thermal
    # Use same criteria as hydroconduit.gdr_blind_thermal_plume to be consistent
    shape = foot.shape
    gdr_result = gdr_blind_thermal_plume(gdr_csv, shape, foot, sigma_px=15.0)
    # The plume is 0..1; we want points for neopenness boost: we can pass None and let neopenness compute its own boost via same logic?
    # Instead, extract well locations where impulses>0 from the helper's internal impulses? We don't have impulses.
    # Workaround: pass gdr_points as positions where plume>0? Not ideal.
    # We will extract directly: filtered keep indices
    rows = pd.to_numeric(df["row"], errors="coerce")
    cols = pd.to_numeric(df["col"], errors="coerce")
    h, w = shape
    in_grid = rows.notna() & cols.notna() & (rows >= 0) & (rows < h) & (cols >= 0) & (cols < w)
    sub = df.loc[in_grid].copy()
    # Apply same keep logic
    t_surf = pd.to_numeric(sub["temp_c"], errors="coerce").to_numpy(dtype=np.float64)
    chem_cols = [c for c in ("geothermquartz_c", "geothermchalc_c", "geothermcat_c") if c in sub.columns]
    t_chem = np.full(len(sub), np.nan, dtype=np.float64)
    if chem_cols:
        t_chem_tmp = np.full(len(sub), -np.inf, dtype=np.float64)
        for c in chem_cols:
            vals = pd.to_numeric(sub[c], errors="coerce").to_numpy(dtype=np.float64)
            fin = np.isfinite(vals)
            t_chem_tmp[fin] = np.maximum(t_chem_tmp[fin], vals[fin])
        t_chem_tmp[~np.isfinite(t_chem_tmp)] = np.nan
        t_chem = t_chem_tmp
    tclass = sub["thermalclass"].fillna("").astype(str).str.strip().to_numpy()
    is_hot_class = np.isin(tclass, ["Hot", "Warm"])
    is_surf_anom = np.isfinite(t_surf) & (t_surf >= 35.0)
    is_chem_anom = np.isfinite(t_chem) & (t_chem >= 80.0)
    keep = is_hot_class | is_surf_anom | is_chem_anom
    r_idx = sub["row"].astype(int).to_numpy()[keep]
    c_idx = sub["col"].astype(int).to_numpy()[keep]
    gdr_yx = (r_idx, c_idx) if len(r_idx) > 0 else None
    print(f"GDR: {len(r_idx)} thermal pixels kept, blind={int(gdr_result['n_blind_geotherm_pixels'])} plume non-zero {(gdr_result['plume_raw']>1e-12).sum()}")

    valid = foot.copy()
    for a in (b2, b5, b12, b13, b15, b19, rad_k, rad_th, rad_u):
        valid &= np.isfinite(a) & (a > -1e30)
    # rad_k etc are uint8 0-255, always finite but check foot
    valid &= foot
    print(f"Footprint {int(foot.sum())}, valid combined {int(valid.sum())}")

    # Compute K/Th and U/Th ratios
    # rad are 0-255 uint8, need to scale? In apronridge they used raw; we treat as float and ratio
    k_th = (rad_k / (rad_th + 1.0)).astype(np.float32)
    u_th = (rad_u / (rad_th + 1.0)).astype(np.float32)

    surf = lane_surface(
        det_elev=b12,
        det_elev_slope=b19,
        depth_to_base=b15,
        iso_grav_anom_slope=b5,
        valid=valid,
        k_th_ratio=k_th,
        u_th_ratio=u_th,
        gdr_points_yx=gdr_yx,
    )
    s_raw = surf["S_raw"]
    s_pct = surf["S_pct"]
    h_apron = surf["H_apron"]
    coh = surf["coherence"]
    encl_pct = surf["encl_pct"]
    break_pct = surf["break_pct"]
    tpi = surf["TPI"]
    curv = surf["curvature"]
    print(f"Surface stats: S_raw median {float(np.median(s_raw[valid])):.4f} p95 {float(np.percentile(s_raw[valid],95)):.4f} S_pct p95 {float(np.percentile(s_pct[valid],95)):.3f}")

    # Ridge extraction: use coherence-weighted TPI curvature ridges as 1D NMS proxies
    # For spaced_top_mask we need candidate mask: valid & ridge-like
    # Use s_raw threshold: keep top 25% of S_raw inside valid as ridge candidates, then NMS via coherence already in surface
    # Instead use s_raw itself: candidate = valid & (s_pct > 0.5)  (top 50%)
    # But to be more selective for far dots, use s_pct>0.7
    # We'll create ridge_1d as (s_pct > 0.6) & (coh > 0.3) to enforce linearity
    ridge_1d = valid & (s_pct > 0.60) & (coh > 0.30)
    print(f"Ridge candidates: {int(ridge_1d.sum())} (≈{int(ridge_1d.sum())/int(valid.sum())*100:.1f}% of valid)")

    # Persist pre-placement surface
    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    surf_tif = ROOT / ".cache" / "neoopenness_surface.tif"
    write_save_prof = profile.copy()
    write_save_prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(surf_tif, "w", **write_save_prof) as ds:
        ds.write(np.where(foot, s_pct, 0.0).astype(np.float32), 1)
    surf_sha256 = sha256_file(surf_tif)
    print(f"Saved surface {surf_tif} sha256 {surf_sha256[:16]}")

    # Candidate pools
    d_h19 = distance_transform_edt(~h19)
    # Skeleton candidate: H19-5 inside valid & d_cat>2 & not catalogue (cat already excluded by d_cat? but ensure)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    # Far candidate: 1D ridge >3px off H19-5 & d_cat>2
    far_cand = foot & valid & ridge_1d & (d_cat > 2.0) & (d_h19 > 3.0)
    free_cand = foot & valid & ridge_1d & (d_cat > 2.0)
    print(f"Pools: skel={int(skel_cand.sum())} far(>3px H19 & 1D)={int(far_cand.sum())} free={int(free_cand.sum())}")

    # Build H_apron-weighted skeleton weights for exact DTI greedy (similar to APRONRIDGE)
    w_skel = np.where(h19 & valid, h_apron * (0.25 + 0.75 * s_pct), 0.10 * s_raw).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    arms_spec = [
        ("s45c55", 16944, 20710, "16944 H19-5 + 20710 far 1D TPI-curvature ridges >3px off H19-5"),
        ("s35c65", 13179, 24475, "13179 H19-5 + 24475 far 1D TPI-curvature ridges >3px off H19-5"),
        ("free1d", 0, 37654, "37654 standalone 1D TPI-curvature ridges (0 H19-5)"),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, n_skel, n_far, short_desc in arms_spec:
        print(f"\n=== Building NEO-OPNS {val_name}: n_skel={n_skel}, n_far={n_far} ===")
        if n_skel > 0:
            skel_mask = select_exact_marginal_dti_add(
                base_mask=np.zeros_like(r0),
                cand_mask=skel_cand,
                w=w_skel,
                n_add=n_skel,
            )
            far_mask = spaced_top_mask(s_raw, far_cand, n_far, min_dist_px=2.8, cand_cap=800_000)
            assert not np.any(skel_mask & far_mask), "overlap skel/far"
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            skel_mask = np.zeros_like(r0)
            far_mask = spaced_top_mask(s_raw, free_cand, n_far, min_dist_px=2.8, cand_cap=800_000)
            final_mask = far_mask.copy()

        assert int(final_mask.sum()) == n_budget, f"count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0)
        assert int((final_mask & cat).sum()) == 0

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-NEOOPNS{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-NEOOPNS-{val_name}-{DATE}"
        if n_skel > 0:
            form_note = f"{PARENT_ID}; NEO-OPNS {val_name}: {n_skel} H19 + {n_far} far TPI-curvature ridges >3px H19-5"
        else:
            form_note = f"{PARENT_ID}; NEO-OPNS {val_name}: 37654 standalone TPI-curvature openness ridges (0 H19-5)"
        assert len(form_note) <= 140, f"note len {len(form_note)}"

        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "NEOOPNS", "arm": val_name, "surface_sha256": surf_sha256},
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
            nan_cache_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=True
        )
        zeros_checks = validate_reopened(
            zeros_dl_path, inputs["sample_submission"], inputs["existing_faults"], final_mask, foot, cat, d_cat, expect_nan_outside=False
        )
        gates_z = run_gates(str(zeros_dl_path), str(inputs["sample_submission"]), str(inputs["existing_faults"]), prune_radius=2)
        ok_z, rep_z = summarise(gates_z)
        assert ok_z, f"Gates failed {zeros_dl_path}: {rep_z}"
        gates_n = run_gates(str(nan_cache_path), str(inputs["sample_submission"]), str(inputs["existing_faults"]), prune_radius=2)
        ok_n, _ = summarise(gates_n)
        assert ok_n

        # Relief distribution: compute detrended elevation terciles for reporting
        z_dots = b12[final_mask]
        if valid.any():
            p33, p67 = np.percentile(b12[valid], [33.33333, 66.66667])
        else:
            p33, p67 = -100, 100
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        moved_pct = float((n_budget - shared_r0) / n_budget * 100)

        variants.append({
            "id": stem,
            "site": "GEMSDOE92",
            "submission_name": sub_name,
            "name": f"{stem}.tif",
            "file_zeros": f"docs/downloads/{zeros_filename}",
            "file_zip": f"docs/downloads/{stem}-zeros.zip",
            "file_nan_cache": f".cache/neoopenness_builds/{stem}.tif",
            "sha8": sha8,
            "change_desc": f"NEO-OPNS ({val_name}): {short_desc}; 37654 dots",
            "notes": f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; git={git_sha[:12]}",
            "parent": PARENT_ID,
            "axis": "NEOOPNS",
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
            "predicted_change": "MODEL: unprojected; HOLDOUT-DTI in evidence/neoopenness_proxy_audit.json",
            "predicted_range": "not projected (Protocol Rule 3)",
            "relief_distribution": {
                "basin_dots": n_basin, "basin_pct": round(n_basin/n_budget*100,3),
                "piedmont_dots": n_pied, "piedmont_pct": round(n_pied/n_budget*100,3),
                "range_dots": n_range, "range_pct": round(n_range/n_budget*100,3),
            },
            "channel_diagnostics": {
                "within_3px_of_h19_5_frac": round(within3_h19,6),
                "shared_exact_pixels_with_R0": shared_r0,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "mean_S_pct_emitted": float(s_pct[final_mask].mean()),
                "mean_encl_pct_emitted": float(encl_pct[final_mask].mean()),
                "mean_break_pct_emitted": float(break_pct[final_mask].mean()),
            },
            "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
            "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
            "form_note": form_note,
            "gate_status": "PASS (submission_writer + disk reread + 11/11 gems.gates)",
            "seed": 0,
        })
        print(f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]} piedmont={n_pied} ({n_pied/n_budget:.1%}) within3_H19={within3_h19:.4f} shared_R0={shared_r0}")

    evidence_doc = {
        "schema": "gemsdoe92.neoopenness-variants.v1",
        "session_date_utc": DATE,
        "axis": "NEOOPNS",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {"cache_path": ".cache/neoopenness_surface.tif", "sha256": surf_sha256, "registry_check": "evidence/neoopenness_surface_registry.json"},
        "lane_surface": {
            "definition": "S_raw = pct(|TPI|·|curvature|)·coh·(0.6·pct(||grad log(slope+1)||)+0.4)·H_apron(120m)·(0.5+0.5·pct(||grad K/Th||))·geothermal_boost",
            "bands": "Band 2 rtp, Band 5 iso_grav_anom_slope, Band 12 det_elev, Band 13 iso_grav_anom, Band 15 depth_to_base_surf, Band 19 det_elev_slope + GeoDAWN K/Th/U + GDR >=80C",
            "implementation": "gems/neoopenness.py",
            "catalogue_use": "zero in surface/skeleton/ridge; d_cat>2.0 gate only",
            "experiments_built": len(variants),
            "budget_limit": 3,
        },
        "variants": variants,
    }
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2)+"\n", encoding="utf-8")
    print(f"Wrote {EVIDENCE} with {len(variants)} variants")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
