#!/usr/bin/env python3
"""Build three pre-registered XPHASE experiments (2026-10-24 session).

Lane: XPHASE -- Magnetotelluric-Gravity Transverse-Phase Concordance
(ranked #1 in docs/HYPOTHESES_20261024_XPHASE.md).

Reuses shared tools (Protocol Rule 2):
- Feature stack restored via scripts/restore_inputs.py (SHA-256 verified)
- Surface math in gems/xphase.py (reusing gems.breakline primitives)
- Packaging via vendor/gems57/submission_writer.py + gems/gates.py
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
from gems.xphase import lane_surface  # noqa: E402
from gems57 import submission_writer  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
CACHE_BUILD_DIR = ROOT / ".cache" / "xphase_builds"
DOWNLOADS_DIR = ROOT / "docs" / "downloads"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "xphase_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"
SURF_TIF = ROOT / ".cache" / "xphase_surface.tif"

MECHANISM_CARD = {
    "hypothesis": (
        "Blind Great Basin feeders juxtapose dense basement against basin fill "
        "(isostatic gravity gradient, Band 13) and bound a smectite clay-cap / "
        "upflow (MT log-conductivity gradient, Band 17) with shared strike but a "
        "100-300 m transverse phase lag, under intermediate Band 15 cover and "
        "away from high Band 19 slope."
    ),
    "mechanism": (
        "S = pct(|grad log B17|) * pct(|grad B13|) * 2-theta orientation agreement "
        "* cover-gate * transverse-lag * slope-suppress * (0.35+0.65*coherence); "
        "emit 37654 2.8 px-spaced 1D crests with d_cat > 2.0."
    ),
    "non_fault_mimic": (
        "Saline playa clay rings on a non-tectonic basin-fill density contact; "
        "irrigation conductivity fronts; Tertiary tuff/basalt pinchouts."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat R0 (0.004006) with paired 95% CI "
        "excluding 0, any canary symmetric AUC > 0.90, or local 3-px overlap > 0.70."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats COULOMB-LOQO standalone "
        "(0.009220) with paired 95% CI excluding 0 vs R0, all canaries <=0.90, "
        "10/10 gates pass, AND literal uniqueness passes. Dense public witness "
        "(>150k px) is recorded, not waived; submission_eligible stays false "
        "under the literal rule until operator density-clause revision."
    ),
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _gate_list(results) -> list[dict]:
    return [{"name": r.name, "ok": bool(r.ok), "detail": r.detail} for r in results]


def emit_spaced(surface, cand, n, min_dist_px=2.8, cand_cap=800_000):
    try:
        return spaced_top_mask(surface, cand, n, min_dist_px=min_dist_px, cand_cap=cand_cap)
    except ValueError:
        # Expand off the 1-D crest onto positive-support pixels if the ridge pool is thin.
        extra = cand | (np.asarray(surface) > 0)
        return spaced_top_mask(surface, extra, n, min_dist_px=min_dist_px, cand_cap=cand_cap)


def main() -> int:
    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    n_budget = int(r0.sum())
    assert n_budget == 37654
    assert not np.any(r0 & ~h19), "R0 must be subset of H19-5"

    print("Loading SHA-verified 19-band stack (Bands 5,13,15,17,19)...")
    with rasterio.open(inputs["training_features"]) as ds:
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b13 = ds.read(13, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17 = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    valid = foot.copy()
    for a in (b5, b13, b15, b17, b19):
        valid &= np.isfinite(a) & (a > -1e30)
    print(f"Footprint px: {int(foot.sum())}, valid 5-band px: {int(valid.sum())}")

    surf = lane_surface(b17, b13, b15, b19, valid, apply_lag=True)
    surf_nophase = lane_surface(b17, b13, b15, b19, valid, apply_lag=False)
    s_raw = surf["S_raw"]
    s_pct = surf["S_pct"]
    ridge_1d = surf["ridge_1d"]
    s_raw_np = surf_nophase["S_raw"]
    ridge_np = surf_nophase["ridge_1d"]

    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    write_save_prof = profile.copy()
    write_save_prof.update(dtype="float32", count=1, nodata=None, compress="deflate")
    with rasterio.open(SURF_TIF, "w", **write_save_prof) as ds:
        ds.write(np.where(foot, s_pct, 0.0).astype(np.float32), 1)
    surf_sha256 = sha256_file(SURF_TIF)
    print(f"Saved pre-placement surface {SURF_TIF} (sha256={surf_sha256[:16]}...)")

    d_h19 = distance_transform_edt(~h19)
    skel_cand = foot & valid & h19 & (d_cat > 2.0)
    far_cand = foot & valid & ridge_1d & (d_cat > 2.0) & (d_h19 > 3.0)
    free_cand = foot & valid & ridge_1d & (d_cat > 2.0)
    far_np = foot & valid & ridge_np & (d_cat > 2.0) & (d_h19 > 3.0)
    free_np = foot & valid & ridge_np & (d_cat > 2.0)
    print(
        f"Candidate pools: skel={int(skel_cand.sum())}, "
        f"far={int(far_cand.sum())}, free1d={int(free_cand.sum())}, "
        f"nophase_free={int(free_np.sum())}"
    )

    w_skel = np.where(h19 & valid, s_pct, 0.0).astype(np.float32)
    w_skel[~(foot & valid)] = 0.0

    arms_spec = [
        ("standalone", 0, 37654, True,
         "37654 standalone MT-grav transverse-phase 1D crests (zero H19-5/R0)"),
        ("nophase", 0, 37654, False,
         "37654 standalone MT-grav orientation 1D crests, lag ablated (zero H19-5/R0)"),
        ("dual40", 15062, 22592, True,
         "15062 S-ranked H19-5 + 22592 far MT-grav phase crests >3px off H19-5"),
    ]
    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()

    variants = []
    for val_name, n_skel, n_far, use_lag, short_desc in arms_spec:
        print(f"\n=== Building Experiment {val_name}: n_skel={n_skel}, n_far={n_far} ===")
        surface = s_raw if use_lag else s_raw_np
        if n_skel > 0:
            skel_mask = emit_spaced(w_skel, skel_cand, n_skel)
            far_mask = emit_spaced(surface, far_cand & ~skel_mask, n_far)
            # Drop collisions with skeleton (rare); refill from remaining far pool.
            collision = skel_mask & far_mask
            if collision.any():
                far_mask = far_mask & ~skel_mask
                need = n_far - int(far_mask.sum())
                if need > 0:
                    refill_pool = far_cand & ~skel_mask & ~far_mask
                    extra = emit_spaced(surface, refill_pool, need)
                    far_mask = far_mask | extra
            assert not np.any(skel_mask & far_mask)
            final_mask = skel_mask | far_mask
        else:
            skel_mask = np.zeros_like(r0)
            pool = free_cand if use_lag else free_np
            far_mask = emit_spaced(surface, pool, n_far)
            final_mask = far_mask.copy()

        assert int(final_mask.sum()) == n_budget, f"Dot count {int(final_mask.sum())} != {n_budget}"
        assert np.all(d_cat[final_mask] > 2.0), "d_cat <=2 violation"
        assert int((final_mask & cat).sum()) == 0, "catalogue overlap"

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-XPHASE{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-XPHASE-{val_name}-{DATE}"
        if n_skel > 0:
            form_note = (
                f"{PARENT_ID}; XPHASE {val_name}: {n_skel} H19-5 + {n_far} far "
                f"MT-grav phase crests"
            )
        elif use_lag:
            form_note = (
                f"{PARENT_ID}; XPHASE standalone: 37654 MT-grav transverse-phase "
                f"1D crests (0 H19-5)"
            )
        else:
            form_note = (
                f"{PARENT_ID}; XPHASE nophase: 37654 MT-grav orientation 1D "
                f"crests, no lag (0 H19-5)"
            )
        assert len(form_note) <= 140, f"form_note len {len(form_note)} >140"

        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path,
            pred_f32,
            inputs["sample_submission"],
            foot,
            note=form_note,
            name=sub_name,
            catalogue=cat,
            metadata={"axis": "XPHASE", "arm": val_name, "surface_sha256": surf_sha256},
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
            nan_cache_path, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=True,
        )
        zeros_checks = validate_reopened(
            zeros_dl_path, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=False,
        )
        gates_z = run_gates(
            str(zeros_dl_path), str(inputs["sample_submission"]),
            str(inputs["existing_faults"]), prune_radius=2,
            require_submission_encoding=True,
        )
        ok_z, rep_z = summarise(gates_z)
        assert ok_z, f"Gates failed on {zeros_dl_path}:\n{rep_z}"
        gates_n = run_gates(
            str(nan_cache_path), str(inputs["sample_submission"]),
            str(inputs["existing_faults"]), prune_radius=2,
        )
        ok_n, _ = summarise(gates_n)
        assert ok_n

        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        moved_pct = float((n_budget - shared_r0) / n_budget * 100.0)
        print(
            f"  dots={n_budget} shared_R0={shared_r0} moved={moved_pct:.2f}% "
            f"within3_H19={within3_h19:.4f} sha256={sha_zeros_disk[:16]}..."
        )

        variants.append(
            {
                "id": stem,
                "site": "GEMSDOE92",
                "submission_name": sub_name,
                "form_note": form_note,
                "name": f"{stem}.tif",
                "file_zeros": f"docs/downloads/{zeros_filename}",
                "file_zip": f"docs/downloads/{stem}-zeros.zip",
                "file_nan_cache": f".cache/xphase_builds/{stem}.tif",
                "sha256": sha_zeros_disk,
                "sha256_nan": sha_nan,
                "sha8": sha8,
                "parent": PARENT_ID,
                "axis": "XPHASE",
                "value": val_name,
                "n_dots": n_budget,
                "n_skel": n_skel,
                "n_far": n_far,
                "apply_lag": use_lag,
                "pct_changed": moved_pct,
                "shared_R0": shared_r0,
                "within3px_H19": round(within3_h19, 6),
                "min_d_cat_px": round(float(d_cat[final_mask].min()), 6),
                "predicted_change": "HOLDOUT-DTI vs R0 unknown until report_xphase_proxies.py",
                "change_desc": f"XPHASE ({val_name}): {short_desc}; fixed 37654 unit dots",
                "notes": (
                    f"arm={val_name}; n_skel={n_skel}; n_far={n_far}; shared_R0={shared_r0}; "
                    f"within3px_H19={within3_h19:.4f}; git={git_sha[:12]}"
                ),
                "gates_zeros": _gate_list(gates_z),
                "gates_nan": _gate_list(gates_n),
                "zeros_checks": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else v)
                                 for k, v in zeros_checks.items()},
                "nan_checks": {k: (bool(v) if isinstance(v, (bool, np.bool_)) else v)
                               for k, v in nan_checks.items()},
                "writer_sha256": writer_receipt["sha256"],
            }
        )

    evidence_doc = {
        "schema": "gemsdoe92-xphase-variants.v1",
        "session_date_utc": DATE,
        "axis": "XPHASE",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "pre_placement_surface": {
            "cache_path": ".cache/xphase_surface.tif",
            "sha256": surf_sha256,
        },
        "lane_surface": {
            "definition": (
                "S = pct(|grad log B17|) * pct(|grad B13|) * orient_2theta * cover "
                "* lag * slope_suppress * (0.35+0.65*coh)"
            ),
            "bands": "Band 13 iso_grav_anom, Band 15 depth_to_base_surf, "
                     "Band 17 cond_surf, Band 19 det_elev_slope",
            "implementation": "gems/xphase.py",
            "catalogue_use": "zero in surface; d_cat>2.0 px emission gate only",
            "experiments_built": len(variants),
            "budget_limit": 3,
        },
        "mechanism_card": MECHANISM_CARD,
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
            "axis": "XPHASE",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    print("BUILD XPHASE complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
