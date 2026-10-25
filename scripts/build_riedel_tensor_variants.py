#!/usr/bin/env python3
"""Build the three pre-registered RIEDELTENSOR experiments (2026-10-25 session).

Lane: RIEDELTENSOR -- 3D Laplace-Consistent Gravity-Gradient Tensor Invariants,
En-Echelon Riedel (R/R') Transtensional Relay Obliquity, Radiometric-Potential
Alteration Contact Coupling, Wallace Basal Piedmont Toe Concavity & Selective
Province-Debiased 4-Branch LOQO (Hypothesis 1 in docs/HYPOTHESES_20261025_RIEDEL_TENSOR.md).

Reuses shared tools without private forks (Protocol Rule 2):
- Cached LOQO surfaces from scripts/screen_riedel_tensor.py (pre-screened <=0.90 canary,
  <=0.70 pre-placement local overlap)
- Exact marginal expected-DTI greedy in scripts/exact_dti_refill.py (for hybrid35 arm)
- Packaging & on-disk validation via vendor/gems57/submission_writer.py + gems/gates.py

Three pre-registered arms (hard budget = 3 experiments):
1. standalone : 37,654 (100%) standalone 1D gravity-tensor + Riedel + basal-toe + knickzone
                crests of S_cal at submodular-coverage-optimal min_dist = 4.48 px
                (zero H19-5 or R0 skeleton input)
2. uncal      : 37,654 (100%) standalone 1D crests of S_uncal at min_dist = 4.48 px
                (pre-registered ablation without within-quadrant quantile calibration)
3. hybrid35   : 13,179 (35%) S_cal-repacked H19-5 skeleton + 24,475 (65%) spaced 1D
                RIEDELTENSOR crests >3 px off H19-5 at min_dist = 4.48 px
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
from gems.gates import run_gates, summarise  # noqa: E402
from gems.riedel_tensor import build_riedel_tensor_crest_surface, spaced_top_mask  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261025"
CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "riedel_tensor_cache.npz"
SURFACE_TIF = CACHE_DIR / "riedel_tensor_S_cal_surface.tif"
CACHE_BUILD_DIR = ROOT / ".cache" / "riedel_tensor_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "riedel_tensor_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Unmapped Quaternary Basin-and-Range faults and blind INGENIOUS geothermal upflow "
        "zones concentrate along (1) 1/z^3 Laplace-consistent 3D gravity-gradient tensor "
        "vertical-derivative ridges (||grad_h g_z||_2 / sqrt(||grad_h g_z||_2^2 + G_zz^2)) "
        "and normal-fault step-dipole contacts (Pedersen & Rasmussen 1990; Beiki 2010), "
        "(2) en-echelon synthetic Riedel (R ~ 19 deg) and conjugate (R' ~ 68 deg) "
        "transtensional relay zones between shallow scarp and deep basement strike tensors "
        "(Faulds & Hinz 2015), (3) 3D radiometric-potential (K/Th, U/Th x tensor-tilt x MT) "
        "hydrothermal alteration contacts, and (4) Wallace (1977) upward-concave basal "
        "piedmont fault toes."
    ),
    "mechanism": (
        "A 4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative "
        "buffer) 4-branch HistGradientBoostingClassifier ensemble (Full 36-feature, "
        "30-feature Province-Debiased, 31-feature Subsurface-Tensor-Riedel, and 28-feature "
        "Basal-Toe-Riedel) with selective branch-specific within-quadrant quantile "
        "calibration predicts P_cal(x) (resolving #IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION), "
        "sharpened along 1D gravity-tensor + Riedel + basal-toe + knickzone crests and "
        "emitted at S=37,654 unit-mass dots (d_cat > 2.0 px, min_dist = 4.48 px)."
    ),
    "non_fault_mimic": (
        "Rootless surficial felsic ash-flow tuff radiometric boundaries lacking basement "
        "gravity-tensor/RTP step concordance, circular caldera/pluton gravity centers "
        "violating normal-fault step-dipole polarity, contour-parallel Lake Lahontan "
        "shorelines, and high-alpine erosion cliffs."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat repository static holdout best KNICKLOQO "
        "standalone (0.010788) on gems57-pooled-hide-v2, any single-feature leakage canary "
        "symmetric AUC > 0.90, or local/dual-reading public forward 3-px overlap > 0.70 / "
        "|Spearman| > 0.90."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats KNICKLOQO standalone (0.010788) with "
        "paired 95% CI > 0, all canaries <= 0.90, 10/10 format gates + 13/13 validate checks "
        "pass, AND both local registry and public dual_reading_decision uniqueness pass "
        "(<=0.70). Because 17GEMSDOE E-proba-multiscale sets every in-footprint pixel > 0 "
        "under the literal >70% public overlap clause, record submission_eligible=false and "
        "verdict='negative' (OK TO DOWNLOAD, NOT CLEARED FOR A WEEKLY SLOT)."
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not NPZ_CACHE.is_file() or not SURFACE_TIF.is_file():
        raise SystemExit("Run scripts/screen_riedel_tensor.py before building variants.")

    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    n_budget = int(r0.sum())
    assert n_budget == 37654
    assert not np.any(r0 & ~h19), "R0 must be a subset of H19-5"

    with rasterio.open(inputs["training_features"]) as ds:
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)

    cache = np.load(NPZ_CACHE)
    valid = cache["valid"].astype(bool)
    l_topo = cache["L_topo"].astype(np.float32)
    l_knick = cache["L_knick"].astype(np.float32)
    l_toe = cache["L_toe"].astype(np.float32)
    l_sub = cache["L_sub"].astype(np.float32)
    p_cal = cache["P_cal"].astype(np.float32)
    p_uncal = cache["P_uncal"].astype(np.float32)

    crest_cal = build_riedel_tensor_crest_surface(
        p_cal, l_topo, l_toe, l_knick, l_sub, valid,
        topo_weight=0.12, toe_weight=0.58, knick_weight=0.80, sub_weight=1.65,
    )
    crest_uncal = build_riedel_tensor_crest_surface(
        p_uncal, l_topo, l_toe, l_knick, l_sub, valid,
        topo_weight=0.12, toe_weight=0.58, knick_weight=0.80, sub_weight=1.65,
    )
    s_cal = crest_cal["S_crest"]
    s_uncal = crest_uncal["S_crest"]
    ridge_cal = crest_cal["ridge_1d"]
    ridge_uncal = crest_uncal["ridge_1d"]

    z_valid = b12[foot & valid]
    p33, p67 = float(np.percentile(z_valid, 33.333)), float(np.percentile(z_valid, 66.667))

    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    surf_sha256 = sha256_file(SURFACE_TIF)

    d_h19 = distance_transform_edt(~h19)
    pool_cal_1d = foot & valid & ridge_cal & (d_cat > 2.0)
    pool_uncal_1d = foot & valid & ridge_uncal & (d_cat > 2.0)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    far_cand = foot & valid & ridge_cal & (d_cat > 2.0) & (d_h19 > 3.0)

    w_skel = np.where(h19 & valid, s_cal, 0.10 * s_cal).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    arms_spec = [
        (
            "standalone",
            0,
            37654,
            s_cal,
            pool_cal_1d,
            "37654 standalone 1D RIEDELTENSOR gravity-tensor+Riedel+basal-toe+knickzone crests (0 H19-5)",
            f"{PARENT_ID}; RIEDELTENSOR standalone: 37654 1D gravity-tensor+Riedel+toe+knick crests",
        ),
        (
            "uncal",
            0,
            37654,
            s_uncal,
            pool_uncal_1d,
            "37654 standalone 1D RIEDELTENSOR uncalibrated ablation crests (0 H19-5)",
            f"{PARENT_ID}; RIEDELTENSOR uncal: 37654 1D uncalibrated ablation tensor+Riedel crests",
        ),
        (
            "hybrid35",
            13179,
            24475,
            s_cal,
            far_cand,
            "13179 RIEDELTENSOR-repacked H19-5 + 24475 off-skeleton (>3px) 1D RIEDELTENSOR crests",
            f"{PARENT_ID}; RIEDELTENSOR hybrid35: 13179 RIEDELTENSOR-H19 + 24475 far 1D tensor+Riedel crests",
        ),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, n_skel, n_far, surf_arr, cand_pool, short_desc, form_note in arms_spec:
        print(f"\n=== Building Experiment {val_name}: n_skel={n_skel}, n_far={n_far} ===", flush=True)
        assert len(form_note) <= 140, f"form_note len {len(form_note)} > 140"

        if n_skel > 0:
            skel_score = np.where(skel_cand, (l_toe + l_sub) * (0.30 + 0.70 * s_cal), 0.0).astype(np.float32)
            skel_mask = spaced_top_mask(skel_score, skel_cand, n_skel, min_dist_px=4.50, cand_cap=900_000)
            far_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=4.70, cand_cap=900_000)
            assert not np.any(skel_mask & far_mask)
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            final_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=4.48, cand_cap=900_000)

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap violation"

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-RIEDELTENSOR{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-RIEDELTENSOR-{val_name}-{DATE}"
        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "RIEDELTENSOR", "arm": val_name, "surface_sha256": surf_sha256},
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

        z_dots = b12[final_mask]
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        surf_max_f = np.maximum(np.maximum(0.12 * l_topo[final_mask], 0.58 * l_toe[final_mask]), 0.80 * l_knick[final_mask])
        sub_dom = int(np.sum((1.65 * l_sub[final_mask]) > surf_max_f))
        toe_dom = int(np.sum((0.58 * l_toe[final_mask]) >= np.maximum(0.12 * l_topo[final_mask], 0.80 * l_knick[final_mask])))
        knick_dom = int(np.sum((0.80 * l_knick[final_mask]) >= np.maximum(np.maximum(0.12 * l_topo[final_mask], 0.58 * l_toe[final_mask]), 1.65 * l_sub[final_mask])))
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
                "file_nan_cache": f".cache/riedel_tensor_builds/{stem}.tif",
                "sha8": sha8,
                "change_desc": f"RIEDELTENSOR ({val_name}): {short_desc}; fixed 37654 unit dots",
                "notes": (
                    f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                    f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; "
                    f"sub_dom_dots={sub_dom}; toe_dom_dots={toe_dom}; knick_dom_dots={knick_dom}; git={git_sha[:12]}"
                ),
                "parent": PARENT_ID,
                "axis": "RIEDELTENSOR",
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
                "predicted_change": "MODEL: unprojected; HOLDOUT-DTI recorded in evidence/riedel_tensor_holdout_audit.json",
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
                    "subsurface_channel_dominant_dots": sub_dom,
                    "subsurface_channel_dominant_frac": round(sub_dom / n_budget, 4),
                    "basal_toe_dominant_over_scarp_dots": toe_dom,
                    "basal_toe_dominant_over_scarp_frac": round(toe_dom / n_budget, 4),
                    "knickzone_channel_dominant_dots": knick_dom,
                    "knickzone_channel_dominant_frac": round(knick_dom / n_budget, 4),
                    "within_3px_of_h19_5_frac": round(within3_h19, 6),
                    "shared_exact_pixels_with_R0": shared_r0,
                    "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                    "collar_dots_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                    "mean_P_loqo_emitted": float(p_cal[final_mask].mean()),
                    "mean_S_emitted": float(surf_arr[final_mask].mean()),
                },
                "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
                "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
                "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
                "form_note": form_note,
                "gate_status": "PASS (submission_writer + disk reread + 10/10 gems.gates)",
                "seed": 20261025,
            }
        )
        print(
            f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]}... "
            f"basin={n_basin/n_budget:.1%}, piedmont={n_pied/n_budget:.1%}, range={n_range/n_budget:.1%}, "
            f"sub_dom={sub_dom} ({sub_dom/n_budget:.1%}), knick_dom={knick_dom} ({knick_dom/n_budget:.1%}), "
            f"within3px_H19={within3_h19:.4f}, shared_R0={shared_r0}",
            flush=True,
        )

    evidence_doc = {
        "schema": "gemsdoe92.riedel-tensor-variants.v1",
        "session_date_utc": DATE,
        "axis": "RIEDELTENSOR",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/gems_inputs/riedel_tensor_S_cal_surface.tif",
            "sha256": surf_sha256,
            "registry_check": "evidence/riedel_tensor_screen.json",
        },
        "lane_surface": {
            "definition": "S_cal = P_cal(X_36) * (0.14 + 0.86 * max(0.12*L_topo, 0.58*L_toe, 0.80*L_knick, 1.65*L_sub))",
            "bands": (
                "Bands 2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19 + "
                "GeoDAWN K/Th/U + GDR #1391 thermal & blind geothermometry"
            ),
            "implementation": "gems/riedel_tensor.py",
            "catalogue_use": (
                "Features strictly catalogue-free (dist_known_fault_px dropped); "
                "LOQO 4-branch ensemble trained strictly out-of-quadrant (>=1.2 km guard, >500 m neg buffer) "
                "with selective branch-specific within-quadrant quantile calibration; placement uses d_cat > 2.0 px gate"
            ),
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
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}", flush=True)

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "RIEDELTENSOR",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
