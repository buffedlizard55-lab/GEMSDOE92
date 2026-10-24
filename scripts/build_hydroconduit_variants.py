#!/usr/bin/env python3
"""Build the 3 pre-registered HYDROCONDUIT experiments from pinned physical inputs.

Pre-registered in docs/HYPOTHESES_20261024_HYDROCONDUIT.md (strict 3-experiment cap):
  1. f45pied  : 55% (20,710) repacked H19-5 piedmont-tectonic skeleton + 45% (16,944)
                spaced off-skeleton dots (>3 px off H19-5) on S_pied.
  2. f45hydro : 55% (20,710) repacked H19-5 piedmont+hydrothermal skeleton + 45% (16,944)
                spaced off-skeleton dots (>3 px off H19-5) on S_hydro (RTP tilt/demag +
                GeoDAWN K/Th + MT conductivity + GDR thermal & blind geothermometer plume).
  3. f50hydro : 50% (18,827) repacked H19-5 piedmont+hydrothermal skeleton + 50% (18,827)
                spaced off-skeleton dots (>3 px off H19-5) on S_hydro.

All 3 experiments hold total mass fixed at 37,654 unit-mass dots, zero catalogue mass,
and d_cat > 2.0 px, and pass both gems.gates and vendor/gems57/validate.py.
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
from gems.hydroconduit import (  # noqa: E402
    gdr_blind_thermal_plume,
    hydroconduit_surface,
    spaced_top_mask,
)
from gems57 import grid as grid_mod, validate as gems57_validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
OUT_DIR = ROOT / "releases"
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "hydroconduit_variants.json"
CARDS_JSON = ROOT / "ledger" / "mechanism_cards.json"

MECHANISM_CARD = {
    "hypothesis": (
        "Active Quaternary Basin-and-Range normal faults and >75% of blind INGENIOUS "
        "geothermal conduits localize on subtle 1-5 m piedmont/shallow-basement breaks "
        "in slope rather than 25-40 deg bare range-core cliffs (which consumed 74.8% of "
        "BREAKLINE far dots), and carry hydrothermal magnetite-destruction / RTP contact "
        "troughs, K/Th potassic alteration, MT clay-cap conductivity, and blind silica/"
        "cation geothermometer (>=80 C) signatures."
    ),
    "mechanism": (
        "Relative log-slope break ||grad log(slope+1 deg)|| * 600 m cross-strike step "
        "monotonicity mu_step * elevation coherence detects one-sided piedmont scarps "
        "while rejecting V-shaped erosional canyons; unified placement repacks H19-5 "
        "piedmont strands via exact marginal expected DTI and places 45-50% spaced dots "
        ">3 px off H19-5."
    ),
    "non_fault_mimic": (
        "Piedmont alluvial-fan coalescing bajada aprons, non-tectonic Pleistocene Lake "
        "Lahontan recessional shorelines at piedmont elevations, and altered volcanic "
        "contacts or lateral thermal-outflow paleochannels."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI failing to beat RELIEF p10 (0.006045) or paired 95% CI vs R0 "
        "straddling 0, single-feature canary symmetric AUC > 0.90, or forward 3-px "
        "overlap > 0.70 / |rho| > 0.90 vs any registry raster."
    ),
    "decision_rule": (
        "Promote only if literal local + public registry uniqueness passes AND pooled "
        "HOLDOUT-DTI beats RELIEF p10 (0.006045) with CI > 0 vs R0 AND all format gates "
        "pass; otherwise verdict='negative' (OK TO DOWNLOAD, NOT CLEARED FOR A WEEKLY SLOT)."
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
    grid = grid_mod.load_grid(ROOT / ".cache" / "gems_inputs" / "bridge")

    assert not np.any(r0 & ~h19), "R0 is not a subset of H19-5"
    n_parent = int(r0.sum())
    assert n_parent == 37654
    collar_r0 = int(np.sum(r0 & (d_cat <= 3.0)))

    with rasterio.open(inputs["training_features"]) as ds:
        b2_rtp = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4_s2i = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b8_dil = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b12_el = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15_db = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17_cd = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19_sl = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    with rasterio.open(inputs["ext_geodawn_rad_u8"]) as ds:
        rad_k = ds.read(1)
        rad_th = ds.read(2)

    valid_base = foot & np.isfinite(b12_el) & (b12_el > -1e30)
    gdr_info = gdr_blind_thermal_plume(
        inputs["gdr_wellspring_in_footprint"], foot.shape, valid_base, sigma_px=15.0
    )
    surf = hydroconduit_surface(
        det_elev=b12_el,
        det_elev_slope=b19_sl,
        depth_to_base=b15_db,
        geod_2ndinv=b4_s2i,
        geod_dilaterate=b8_dil,
        rtp=b2_rtp,
        cond_surf=b17_cd,
        rad_k=rad_k,
        rad_th=rad_th,
        gdr_plume_pct=gdr_info["plume_pct"],  # type: ignore[arg-type]
        footprint=foot,
    )
    # Terciles of det_elev for diagnostic piedmont/range-core dot accounting
    el_valid_vals = b12_el[valid_base]
    q33, q67 = [float(x) for x in np.percentile(el_valid_vals, [33.333, 66.667])]
    is_basin = valid_base & (b12_el < q33)
    is_pied = valid_base & (b12_el >= q33) & (b12_el < q67)
    is_range = valid_base & (b12_el >= q67)
    del b2_rtp, b4_s2i, b8_dil, b12_el, b15_db, b17_cd, b19_sl, rad_k, rad_th

    d_h19 = distance_transform_edt(~h19)
    skel_cand = foot & surf["valid"] & h19 & (d_cat > 2.0)
    far_cand = foot & surf["valid"] & (d_cat > 2.0) & (d_h19 > 3.0) & (~r0)
    n_skel_cand = int(skel_cand.sum())
    n_far_cand = int(far_cand.sum())
    print(f"Skeleton pool (H19-5 & d_cat>2): {n_skel_cand}; Far pool (d_H19>3 & d_cat>2): {n_far_cand}")

    w_skel_pied = np.where(h19, 0.25 + 0.75 * surf["hab_pied_pct"], 0.05 * surf["S_pied_pct"]).astype(np.float32)
    w_skel_pied[~foot] = 0.0
    w_skel_hydro = np.where(h19, 0.25 + 0.75 * surf["hab_hydro_pct"], 0.05 * surf["S_hydro_pct"]).astype(np.float32)
    w_skel_hydro[~foot] = 0.0

    experiments = [
        ("f45pied", 0.45, w_skel_pied, surf["S_pied_raw"], surf["S_pied_pct"],
         "geom-tectonic piedmont relative monoclinal scarp"),
        ("f45hydro", 0.45, w_skel_hydro, surf["S_hydro_raw"], surf["S_hydro_pct"],
         "piedmont scarp x hydrothermal RTP/KTh/MT/GDR conduit"),
        ("f50hydro", 0.50, w_skel_hydro, surf["S_hydro_raw"], surf["S_hydro_pct"],
         "piedmont scarp x hydrothermal RTP/KTh/MT/GDR conduit (50% far)"),
    ]

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    empty_base = np.zeros_like(r0, dtype=bool)
    variants = []

    for val_name, frac, w_skel, s_raw, s_pct, desc_short in experiments:
        n_far = int(round(frac * n_parent))
        n_keep = n_parent - n_far
        print(f"\nBuilding HYDROCONDUIT {val_name}: n_skel={n_keep} ({(1-frac)*100:.0f}%), n_far={n_far} ({frac*100:.0f}%)...")

        skel_mask = select_exact_marginal_dti_add(
            base_mask=empty_base,
            cand_mask=skel_cand,
            w=w_skel,
            n_add=n_keep,
        )
        far_mask = spaced_top_mask(s_raw, far_cand, n_far)
        assert int(skel_mask.sum()) == n_keep
        assert int(far_mask.sum()) == n_far
        assert not np.any(skel_mask & far_mask)

        final_mask = skel_mask | far_mask
        assert int(final_mask.sum()) == n_parent
        assert not np.any(final_mask & cat)
        assert float(d_cat[final_mask].min()) > 2.0
        assert float(d_h19[far_mask].min()) > 3.0

        stem_base = f"{PARENT_ID}-HYDROCONDUIT{val_name}-{DATE}"
        tmp_nan = OUT_DIR / f"._{stem_base}-nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        tmp_nan.unlink()

        stem = f"{PARENT_ID}-HYDROCONDUIT{val_name}-{DATE}-{sha8}"
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
            final_mask, foot, cat, d_cat, expect_nan_outside=True
        )
        zeros_checks = validate_reopened(
            zeros_path, inputs["sample_submission"], inputs["existing_faults"],
            final_mask, foot, cat, d_cat, expect_nan_outside=False
        )
        g57_zeros = gems57_validate.validate(zeros_path, footprint=foot, catalogue=cat)
        gems57_validate.assert_submittable(g57_zeros)

        shared_exact_r0 = int(np.sum(final_mask & r0))
        dropped = r0 & (~final_mask)
        added = final_mask & (~r0)
        pct_changed = float(added.sum() / n_parent * 100.0)

        far_pied_frac = float(np.sum(far_mask & is_pied) / max(n_far, 1))
        far_range_frac = float(np.sum(far_mask & is_range) / max(n_far, 1))
        far_basin_frac = float(np.sum(far_mask & is_basin) / max(n_far, 1))
        skel_pied_frac = float(np.sum(skel_mask & is_pied) / max(n_keep, 1))

        form_note = (
            f"{PARENT_ID}; HYDROCONDUIT {val_name}: {n_keep} piedmont H19-5 + {n_far} "
            f"off-skel scarp/RTP/GDR dots (>3px H19-5)"
        )
        assert len(form_note) <= 140, f"Form note {len(form_note)} > 140: {form_note}"

        variant_meta = {
            "id": stem,
            "site": "GEMSDOE92",
            "name": nan_file,
            "file_zeros": f"releases/{zeros_file}",
            "file_nan": f"releases/{nan_file}",
            "sha8": sha8,
            "change_desc": (
                f"HYDROCONDUIT ({desc_short}): repack {n_keep} H19-5 piedmont dots + "
                f"emit {n_far} ({frac*100:.0f}%) spaced dots >3px off H19-5; fixed 37654 dots"
            ),
            "notes": (
                f"frac_far={frac:.2f}; n_skel={n_keep}; n_far={n_far}; shared_exact_R0={shared_exact_r0}; "
                f"far_pied_frac={far_pied_frac:.4f}; far_range_frac={far_range_frac:.4f}; git={git_sha[:12]}"
            ),
            "parent": PARENT_ID,
            "axis": "HYDROCONDUIT",
            "value": val_name,
            "n_dots": n_parent,
            "pct_changed": pct_changed,
            "removed": int(dropped.sum()),
            "added": int(added.sum()),
            "sha256": sha_nan_disk,
            "sha256_zeros": sha_zeros_disk,
            "primary_file": zeros_file,
            "fallback_file": nan_file,
            "primary_encoding": "zero outside footprint",
            "fallback_encoding": "NaN outside footprint",
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/hydroconduit_proxy_audit.json",
            "predicted_range": "not projected (never write a projection as a competition score)",
            "prediction_scope": "MODEL scope note only; organizer score requires a submission receipt.",
            "parent_diff": {
                "removed": int(dropped.sum()),
                "added": int(added.sum()),
                "shared_exact_r0": shared_exact_r0,
                "n_skeleton_repacked": n_keep,
                "n_far_off_h19": n_far,
                "moved_pct": pct_changed,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "far_min_distance_to_h19_px": float(d_h19[far_mask].min()),
                "collar_dots_final_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "collar_dots_parent_dcat_le_3": collar_r0,
                "far_tercile_fractions": {
                    "basin": round(far_basin_frac, 6),
                    "piedmont": round(far_pied_frac, 6),
                    "range_core": round(far_range_frac, 6),
                },
                "skeleton_piedmont_fraction": round(skel_pied_frac, 6),
                "mean_S_pct_far": float(s_pct[far_mask].mean()),
            },
            "format_validation": {
                "nan": nan_checks,
                "zeros": zeros_checks,
                "gems57_zeros_all_checks_passed": g57_zeros["all_checks_passed"],
            },
            "form_note": form_note,
            "gate_status": (
                "PASS (disk reread + gems.gates + gems57.validate; EPSG:32611, 3730x3292, "
                "float32, [0,1] finite, zero catalogue mass, d_cat>2.0)"
            ),
            "seed": 0,
        }
        variants.append(variant_meta)
        print(
            f"PASS {stem}: exact_shared_R0={shared_exact_r0}, collar={variant_meta['parent_diff']['collar_dots_final_dcat_le_3']}, "
            f"far_pied={far_pied_frac:.3f}, far_range={far_range_frac:.3f}"
        )

    evidence_doc = {
        "schema": "gemsdoe92.hydroconduit-variants.v1",
        "session_date_utc": DATE,
        "axis": "HYDROCONDUIT",
        "hypothesis_doc": "docs/HYPOTHESES_20261024_HYDROCONDUIT.md",
        "preplacement_screen": "evidence/hydroconduit_preplacement_screen.json",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "gdr_summary": {
            "n_thermal_pixels": gdr_info["n_thermal_pixels"],
            "n_blind_geotherm_pixels": gdr_info["n_blind_geotherm_pixels"],
        },
        "pools": {
            "skeleton_h19_dcat_gt_2": n_skel_cand,
            "far_dh19_gt_3_dcat_gt_2": n_far_cand,
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
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {
            "parent": PARENT_ID,
            "axis": "HYDROCONDUIT",
            "value": v["value"],
            **MECHANISM_CARD,
            "predicted_sign_and_size": v["predicted_change"],
        }
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
