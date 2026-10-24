#!/usr/bin/env python3
"""Build the three pre-registered COULOMB-LOQO experiments (2026-10-24 session).

Lane: COULOMB-LOQO -- Spatially Cross-Fitted (LOQO) Polarity-Locked Multi-Scale
Hessian & 2D Coulomb Transtensional Ridge Model
(Hypothesis 1 in docs/HYPOTHESES_20261024_COULOMBLOQO.md).

Reuses shared tools without private forks (Protocol Rule 2):
- Cached LOQO surfaces from scripts/screen_coulomb_loqo.py (pre-screened <=0.90 canary,
  <=0.70 pre-placement local overlap)
- Exact marginal expected-DTI greedy in scripts/exact_dti_refill.py (for dual45 arm)
- Packaging & on-disk validation via vendor/gems57/submission_writer.py + gems/gates.py

Three pre-registered arms (hard budget = 3 experiments):
1. standalone : 37,654 (100%) standalone 1D structural crests of S_full (Groups A-E;
                zero H19-5 or R0 skeleton input)
2. nocoulomb  : 37,654 (100%) standalone 1D crests of S_topo (Group A topographic/cover
                features only -- ablation of polarity, RTP, Coulomb & hydrothermal groups)
3. dual45     : 16,944 (45%) S_full-repacked H19-5 skeleton + 20,710 (55%) spaced 1D
                crests >3 px off H19-5
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
from gems.coulomb_loqo import build_crest_surface, spaced_top_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "coulomb_loqo_cache.npz"
SURFACE_TIF = CACHE_DIR / "coulomb_loqo_S_full_surface.tif"
CACHE_BUILD_DIR = ROOT / ".cache" / "coulomb_loqo_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "coulomb_loqo_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Active Quaternary Basin-and-Range normal/transtensional faults and blind "
        "INGENIOUS geothermal conduits exhibit concordant footwall-hangingwall polarity "
        "between detrended elevation, Band 18 E-W horizontal gravity gradient "
        "(iso_grav_anom_hg), and basement relief, axial strike phase-locking across "
        "topography + true Band 2 RTP magnetics + gravity, high 2D Coulomb slip/dilation "
        "tendency along N15E normal and NW/ENE conjugate strikes, and MT clay-cap / "
        "radioelement / blind silica-cation geothermometer (>=80 C) halos."
    ),
    "mechanism": (
        "A 4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative "
        "buffer) HistGradientBoostingClassifier fit strictly on 24 catalogue-free physical "
        "features (dropping dist_known_fault_px; zero cross-quadrant quantile sharing) "
        "predicts out-of-quadrant fault probability P_LOQO(x), sharpened by 1D topographic "
        "Hessian/scarp and subsurface RTP/basement/MT crest localization, then emitted at "
        "fixed budget S=37,654 unit-mass dots with d_cat > 2.0 px and min_dist = 2.8 px."
    ),
    "non_fault_mimic": (
        "Pleistocene Lake Lahontan wave-cut shorelines, radial alluvial-fan incised wash "
        "walls, remanently magnetized Tertiary lava flow edges, and flat-lying conductive "
        "playa evaporite lenses."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat repository holdout best HYDROCONDUIT f45hydro "
        "(0.008549) on gems57-pooled-hide-v2, any single-feature leakage canary symmetric "
        "AUC > 0.90, or local registry forward 3-px overlap > 0.70 / |Spearman| > 0.90."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats HYDROCONDUIT f45hydro (0.008549) with "
        "paired 95% CI > 0, all canaries <= 0.90, 10/10 format gates pass, AND literal "
        "uniqueness passes on both local and public registries. Because 17GEMSDOE "
        "E-proba-multiscale sets every in-footprint pixel > 0 under the literal >70% "
        "public overlap clause, record submission_eligible=false and verdict='negative' "
        "(OK TO DOWNLOAD, NOT CLEARED FOR A WEEKLY SLOT) without waiving the rule."
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
        raise SystemExit("Run scripts/screen_coulomb_loqo.py before building variants.")

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
    l_sub = cache["L_sub"].astype(np.float32)
    p_full = cache["P_full"].astype(np.float32)
    p_topo = cache["P_topo"].astype(np.float32)

    crest_full = build_crest_surface(p_full, l_topo, l_sub, valid, sub_weight=0.80)
    crest_topo = build_crest_surface(p_topo, l_topo, None, valid)
    s_full = crest_full["S_crest"]
    s_topo = crest_topo["S_crest"]
    ridge_full = crest_full["ridge_1d"]
    ridge_topo = crest_topo["ridge_1d"]

    z_valid = b12[foot & valid]
    p33, p67 = float(np.percentile(z_valid, 33.333)), float(np.percentile(z_valid, 66.667))

    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    surf_sha256 = sha256_file(SURFACE_TIF)

    d_h19 = distance_transform_edt(~h19)
    pool_full_1d = foot & valid & ridge_full & (d_cat > 2.0)
    pool_topo_1d = foot & valid & ridge_topo & (d_cat > 2.0)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    far_cand = foot & valid & ridge_full & (d_cat > 2.0) & (d_h19 > 3.0)

    w_skel = np.where(h19 & valid, s_full, 0.10 * s_full).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    arms_spec = [
        (
            "standalone",
            0,
            37654,
            s_full,
            pool_full_1d,
            "37654 standalone 1D LOQO multi-physics Coulomb/polarity/RTP crests (0 H19-5)",
            f"{PARENT_ID}; COULOMBLOQO standalone: 37654 1D LOQO Coulomb+polarity+RTP crests (0 H19-5)",
        ),
        (
            "nocoulomb",
            0,
            37654,
            s_topo,
            pool_topo_1d,
            "37654 standalone 1D LOQO Group-A topo/cover crests (ablation without Coulomb/RTP/hydro)",
            f"{PARENT_ID}; COULOMBLOQO nocoulomb: 37654 1D LOQO topo-only ablation crests (0 H19-5)",
        ),
        (
            "dual45",
            16944,
            20710,
            s_full,
            far_cand,
            "16944 LOQO-repacked H19-5 + 20710 off-skeleton (>3px) 1D LOQO Coulomb crests",
            f"{PARENT_ID}; COULOMBLOQO dual45: 16944 LOQO-H19 + 20710 far 1D Coulomb crests >3px off H19-5",
        ),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, n_skel, n_far, surf_arr, cand_pool, short_desc, form_note in arms_spec:
        print(f"\n=== Building Experiment {val_name}: n_skel={n_skel}, n_far={n_far} ===", flush=True)
        assert len(form_note) <= 140, f"form_note len {len(form_note)} > 140"

        if n_skel > 0:
            skel_mask = select_exact_marginal_dti_add(
                base_mask=np.zeros_like(r0),
                cand_mask=skel_cand,
                w=w_skel,
                n_add=n_skel,
            )
            far_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=2.8, cand_cap=700_000)
            assert not np.any(skel_mask & far_mask)
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            final_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=2.8, cand_cap=900_000)

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap violation"

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-COULOMBLOQO{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-COULOMBLOQO-{val_name}-{DATE}"
        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "COULOMBLOQO", "arm": val_name, "surface_sha256": surf_sha256},
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
        sub_dom = int(np.sum((0.80 * l_sub[final_mask]) > l_topo[final_mask]))
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
                "file_nan_cache": f".cache/coulomb_loqo_builds/{stem}.tif",
                "sha8": sha8,
                "change_desc": f"COULOMBLOQO ({val_name}): {short_desc}; fixed 37654 unit dots",
                "notes": (
                    f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                    f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; "
                    f"sub_dom_dots={sub_dom}; git={git_sha[:12]}"
                ),
                "parent": PARENT_ID,
                "axis": "COULOMBLOQO",
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
                "predicted_change": "MODEL: unprojected; HOLDOUT-DTI recorded in evidence/coulomb_loqo_proxy_audit.json",
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
                    "within_3px_of_h19_5_frac": round(within3_h19, 6),
                    "shared_exact_pixels_with_R0": shared_r0,
                    "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                    "collar_dots_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                    "mean_P_loqo_emitted": float(p_full[final_mask].mean()),
                    "mean_S_emitted": float(surf_arr[final_mask].mean()),
                },
                "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
                "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
                "format_validation": {"nan": nan_checks, "zeros": zeros_checks},
                "form_note": form_note,
                "gate_status": "PASS (submission_writer + disk reread + 10/10 gems.gates)",
                "seed": 20261024,
            }
        )
        print(
            f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]}... "
            f"basin={n_basin/n_budget:.1%}, piedmont={n_pied/n_budget:.1%}, range={n_range/n_budget:.1%}, "
            f"sub_dom={sub_dom} ({sub_dom/n_budget:.1%}), within3px_H19={within3_h19:.4f}, shared_R0={shared_r0}",
            flush=True,
        )

    evidence_doc = {
        "schema": "gemsdoe92.coulomb-loqo-variants.v1",
        "session_date_utc": DATE,
        "axis": "COULOMBLOQO",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/gems_inputs/coulomb_loqo_S_full_surface.tif",
            "sha256": surf_sha256,
            "registry_check": "evidence/coulomb_loqo_screen.json",
        },
        "lane_surface": {
            "definition": "S_full = P_LOQO(X_24) * (0.15 + 0.85 * max(L_topo, 0.80 * L_sub))",
            "bands": (
                "Bands 2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19 + "
                "GeoDAWN K/Th/U + GDR #1391 thermal & blind geothermometry"
            ),
            "implementation": "gems/coulomb_loqo.py",
            "catalogue_use": (
                "Features strictly catalogue-free (dist_known_fault_px dropped); "
                "LOQO classifier trained strictly out-of-quadrant (>=1.2 km guard, >500 m neg buffer); "
                "placement uses d_cat > 2.0 px gate"
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
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}", flush=True)

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "COULOMBLOQO",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
