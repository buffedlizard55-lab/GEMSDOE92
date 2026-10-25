#!/usr/bin/env python3
"""Build the three pre-registered LISTRICLOQO experiments (2026-10-25 session).

Lane: LISTRICLOQO -- Listric Normal-Fault Dip-Offset Hanging-Wall Pullback,
Full 2D Gravity-Gradient Tensor & Riedel (18 deg) En-Echelon Coupling, and
Selective Subsurface-Branch Quadrant-Calibrated LOQO
(Hypothesis 1 in docs/HYPOTHESES_20261025_LISTRICLOQO.md).

Reuses shared tools without private forks (Protocol Rule 2):
- Cached LOQO surfaces from scripts/screen_listric_loqo.py (pre-screened <=0.90 canary,
  <=0.70 pre-placement local overlap)
- Exact marginal expected-DTI greedy in scripts/exact_dti_refill.py (for dual35 arm)
- Packaging & on-disk validation via vendor/gems57/submission_writer.py + gems/gates.py

Three pre-registered arms (hard budget = 3 experiments):
1. standalone : 37,654 (100%) standalone 1D listric-scarp + down-dip splay + Wallace-toe
                + gravity-tensor/Riedel crests of S_cal (zero H19-5 or R0 skeleton input)
2. nolistric  : 37,654 (100%) standalone 1D crests of S_uncal (pre-registered ablation
                without selective subsurface-branch quadrant calibration)
3. dual35     : 13,179 (35%) S_cal-repacked H19-5 skeleton + 24,475 (65%) spaced 1D
                LISTRICLOQO crests >3 px off H19-5
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
from gems.listric_loqo import build_listric_crest_surface, spaced_top_mask  # noqa: E402
from gems57 import submission_writer, validate as gems57_validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261025"
CACHE_DIR = ROOT / ".cache" / "gems_inputs"
NPZ_CACHE = CACHE_DIR / "listric_loqo_cache.npz"
SURFACE_TIF = CACHE_DIR / "listric_loqo_S_cal_surface.tif"
CACHE_BUILD_DIR = ROOT / ".cache" / "listric_loqo_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "listric_loqo_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Basin-and-Range normal faults dip 45-60 deg into the hanging wall, displacing the "
        "subsurface gravity/basement/RTP/MT inflection 300-500 m (3-5 px) downslope into the "
        "hanging wall relative to the surface Wallace basal toe / scarp trace. Up-dip "
        "hanging-wall pullback (+3, +5 px along n_hw), down-dip footwall splay projection "
        "(-2.5, -4 px), full 2D horizontal-vertical gravity gradient tensor invariants "
        "(Pedersen & Rasmussen 1990), and 18-deg synthetic Riedel en-echelon obliquity "
        "recover unmapped dipping normal faults and transtensional geothermal relay ramps."
    ),
    "mechanism": (
        "A 4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative "
        "buffer) 3-branch HistGradientBoostingClassifier ensemble (Full 36-feature, "
        "30-feature Province-Debiased, and 31-feature Subsurface-Listric) with selective "
        "subsurface-branch within-quadrant quantile calibration predicts P_cal(x) "
        "(resolving #IR-92-NE-QUADRANT-DOUBLE-EDGED-CALIBRATION), sharpened along 1D "
        "listric-scarp + down-dip splay + gravity-tensor/Riedel crests at S=37,654 unit-mass "
        "dots (d_cat > 2.0 px, min_dist = 3.4 px)."
    ),
    "non_fault_mimic": (
        "Bare >16 deg alpine erosional mountain cliffs lacking hanging-wall basin deepening, "
        "contour-parallel Pleistocene Lake Lahontan wave-cut shorelines, radial alluvial-fan "
        "incision walls, and flat-lying conductive playa evaporite lenses."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat repository holdout best KNICKLOQO standalone "
        "(0.010788 static / 0.010958 draw-blind d_cat > 2.0; 0.109043 strict draw-blind "
        "d_vis > 2.0) on gems57-pooled-hide-v2, any single-feature leakage canary symmetric "
        "AUC > 0.90, or local/dual-reading public forward 3-px overlap > 0.70 / |Spearman| > 0.90."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats KNICKLOQO standalone (0.010788) with "
        "paired 95% CI > 0, all canaries <= 0.90, 11/11 format gates pass, AND both local "
        "registry and public dual_reading_decision uniqueness pass (<=0.70). Because "
        "17GEMSDOE E-proba-multiscale sets every in-footprint pixel > 0 under the literal "
        ">70% public overlap clause, record submission_eligible=false and verdict='negative' "
        "(OK TO DOWNLOAD, NOT CLEARED FOR A WEEKLY SLOT) without waiving the literal rule."
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
        raise SystemExit("Run scripts/screen_listric_loqo.py before building variants.")

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
    l_topo_listric = cache["L_topo_listric"].astype(np.float32)
    l_knick = cache["L_knick"].astype(np.float32)
    l_sub = cache["L_sub"].astype(np.float32)
    p_cal = cache["P_cal"].astype(np.float32)
    p_uncal = cache["P_uncal"].astype(np.float32)

    crest_cal = build_listric_crest_surface(
        p_cal, l_topo_listric, l_sub, valid, l_knick=l_knick,
        topo_weight=1.00, knick_weight=1.00, sub_weight=1.00,
    )
    crest_uncal = build_listric_crest_surface(
        p_uncal, l_topo_listric, l_sub, valid, l_knick=l_knick,
        topo_weight=1.00, knick_weight=1.00, sub_weight=1.00,
    )
    s_cal = crest_cal["S_crest"]
    s_uncal = crest_uncal["S_crest"]
    ridge_cal = crest_cal["ridge_1d"]
    ridge_uncal = crest_uncal["ridge_1d"]

    z_valid = b12[foot & valid]
    p33, p67 = float(np.percentile(z_valid, 33.333)), float(np.percentile(z_valid, 66.667))

    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for old_f in list(DOWNLOADS_DIR.glob("*LISTRICLOQO*")) + list(CACHE_BUILD_DIR.glob("*LISTRICLOQO*")):
        old_f.unlink()
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
            "37654 standalone 1D LISTRICLOQO selective-calibrated listric+splay+tensor+Riedel crests (0 H19-5)",
            f"{PARENT_ID}; LISTRICLOQO standalone: 37654 1D listric+splay+tensor+Riedel crests",
        ),
        (
            "nolistric",
            0,
            37654,
            s_uncal,
            pool_uncal_1d,
            "37654 standalone 1D LISTRICLOQO uncalibrated ablation crests (0 H19-5)",
            f"{PARENT_ID}; LISTRICLOQO nolistric: 37654 1D uncalibrated ablation listric crests",
        ),
        (
            "dual35",
            13179,
            24475,
            s_cal,
            far_cand,
            "13179 LISTRICLOQO-repacked H19-5 + 24475 off-skeleton (>3px) 1D LISTRICLOQO crests",
            f"{PARENT_ID}; LISTRICLOQO dual35: 13179 LISTRIC-H19 + 24475 far 1D listric+tensor crests",
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
            far_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=3.4, cand_cap=900_000)
            assert not np.any(skel_mask & far_mask)
            assert np.all(d_h19[far_mask] > 3.0)
            final_mask = skel_mask | far_mask
        else:
            final_mask = spaced_top_mask(surf_arr, cand_pool, n_far, min_dist_px=3.4, cand_cap=900_000)

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <= 2.0 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap violation"

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-LISTRICLOQO{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-LISTRICLOQO-{val_name}-{DATE}"
        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "LISTRICLOQO", "arm": val_name, "surface_sha256": surf_sha256},
        )
        aux_writer_json = zeros_dl_path.with_suffix(".json")
        if aux_writer_json.is_file():
            aux_writer_json.replace(CACHE_BUILD_DIR / aux_writer_json.name)

        sha_zeros_disk = sha256_file(zeros_dl_path)
        assert sha_zeros_disk == writer_receipt["sha256"]
        zeros_dl_path.chmod(0o644)
        zip_dl_path = DOWNLOADS_DIR / f"{stem}-zeros.zip"
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

        v_gems57 = gems57_validate.validate(zeros_dl_path, foot, cat)
        assert v_gems57["all_checks_passed"], f"gems57.validate failed: {v_gems57}"

        z_dots = b12[final_mask]
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        sub_dom = int(np.sum(l_sub[final_mask] > np.maximum(l_topo_listric[final_mask], l_knick[final_mask])))
        knick_dom = int(np.sum(l_knick[final_mask] >= np.maximum(l_topo_listric[final_mask], l_sub[final_mask])))
        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        moved_pct = float((n_budget - shared_r0) / n_budget * 100.0)

        audit_sidecar_path = DOWNLOADS_DIR / f"{stem}-audit.json"
        variant_row = {
            "id": stem,
            "site": "GEMSDOE92",
            "submission_name": sub_name,
            "name": f"{stem}.tif",
            "file_zeros": f"docs/downloads/{zeros_filename}",
            "file_zip": f"docs/downloads/{stem}-zeros.zip",
            "file_audit": f"docs/downloads/{audit_sidecar_path.name}",
            "file_nan_cache": f".cache/listric_loqo_builds/{stem}.tif",
            "sha8": sha8,
            "change_desc": f"LISTRICLOQO ({val_name}): {short_desc}; fixed 37654 unit dots",
            "notes": (
                f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/n_budget*100:.1f}%; "
                f"sub_dom_dots={sub_dom}; splay_dom_dots={knick_dom}; git={git_sha[:12]}"
            ),
            "parent": PARENT_ID,
            "axis": "LISTRICLOQO",
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
            "predicted_change": "MODEL: unprojected; HOLDOUT-DTI recorded in evidence/listric_loqo_proxy_audit.json",
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
                "subsurface_tensor_channel_dominant_dots": sub_dom,
                "subsurface_tensor_channel_dominant_frac": round(sub_dom / n_budget, 4),
                "downdip_splay_channel_dominant_dots": knick_dom,
                "downdip_splay_channel_dominant_frac": round(knick_dom / n_budget, 4),
                "within_3px_of_h19_5_frac": round(within3_h19, 6),
                "shared_exact_pixels_with_R0": shared_r0,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "collar_dots_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "mean_P_loqo_emitted": float(p_cal[final_mask].mean()),
                "mean_S_emitted": float(surf_arr[final_mask].mean()),
            },
            "gates_zeros": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_z],
            "gates_nan": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates_n],
            "format_validation": {"nan": nan_checks, "zeros": zeros_checks, "gems57_validate": v_gems57},
            "form_note": form_note,
            "gate_status": "PASS (submission_writer + disk reread + 10/10 gems.gates)",
            "seed": 20261025,
        }
        audit_sidecar_path.write_text(json.dumps(variant_row, indent=2) + "\n", encoding="utf-8")
        variants.append(variant_row)
        print(
            f"PASS {stem}: zeros_sha256={sha_zeros_disk[:16]}... "
            f"basin={n_basin/n_budget:.1%}, piedmont={n_pied/n_budget:.1%}, range={n_range/n_budget:.1%}, "
            f"sub_dom={sub_dom} ({sub_dom/n_budget:.1%}), splay_dom={knick_dom} ({knick_dom/n_budget:.1%}), "
            f"within3px_H19={within3_h19:.4f}, shared_R0={shared_r0}",
            flush=True,
        )

    evidence_doc = {
        "schema": "gemsdoe92.listric-loqo-variants.v1",
        "session_date_utc": DATE,
        "axis": "LISTRICLOQO",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/gems_inputs/listric_loqo_S_cal_surface.tif",
            "sha256": surf_sha256,
            "registry_check": "evidence/listric_loqo_screen.json",
        },
        "lane_surface": {
            "definition": "S_cal = (P_cal(X_36)**0.75) * (0.01 + 0.99 * max(L_topo_listric, L_knick_splay, L_sub_tensor))",
            "bands": (
                "Bands 2, 4, 5, 7, 8, 11, 12, 13, 15, 17, 18, 19 + "
                "GeoDAWN K/Th/U + GDR #1391 thermal & blind geothermometry"
            ),
            "implementation": "gems/listric_loqo.py",
            "catalogue_use": (
                "Features strictly catalogue-free (dist_known_fault_px dropped); "
                "LOQO 3-branch ensemble trained strictly out-of-quadrant (>=1.2 km guard, >500 m neg buffer) "
                "with selective subsurface-branch within-quadrant quantile calibration; placement uses d_cat > 2.0 px gate"
            ),
            "experiments_built": len(variants),
            "budget_limit": 3,
        },
        "variants": variants,
    }
    EVIDENCE.write_text(json.dumps(evidence_doc, indent=2) + "\n", encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = [r for r in csv.DictReader(f) if r.get("axis") != "LISTRICLOQO"]
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
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(existing_rows + new_rows)
    print(f"Updated {LEDGER} (+{len(new_rows)} LISTRICLOQO rows)", flush=True)

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    cards = {k: val for k, val in cards.items() if val.get("axis") != "LISTRICLOQO"}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "LISTRICLOQO",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
