#!/usr/bin/env python3
"""Build the 3 pre-registered COULOMB experiments (2026-10-24 session).

Pre-registered in docs/HYPOTHESES_20261024_COULOMB.md, gated by
evidence/coulomb_preplacement_screen.json (screen_decision.build_rank1_coulomb
must be true; baseline gate-zero reproduced; canary + surface uniqueness pass):

  1. free   : S = max(R_rtp_tilt, R_scarp_rel) x O_coulomb x H_apron (standalone)
  2. open   : S = max(R_rtp_tilt, R_scarp_rel) x O_coulomb (no apron gate)
  3. seismo : S = free x (0.50 + 0.50 x seismo_prior) (Rank-1 x Rank-2 fusion)

All 3 hold N = 37,654 unit-mass dots, d_cat > 2.0 px, zero catalogue mass,
2.8 px spacing on 4-axis 1D crests, Tier-1/Tier-2 prior-far repulsion (see
hypotheses doc amendment). Zeros-outside encodings are written directly to
docs/downloads/ via vendor submission_writer (APRONRIDGE pattern); NaN twins
live in .cache/coulomb_builds/ (research only, never served).
"""
from __future__ import annotations

import csv
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
from gems.coulomb import coulomb_surface  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, submission_writer  # noqa: E402
from gems57 import validate as gems57_validate  # noqa: E402

PARENT_ID = "h33-h33-2-b2"
DATE = "20261024"
AXIS = "COULOMB"
N_BUDGET = 37654
TIER1_MIN_POOL = 120_000
DOWNLOADS_DIR = ROOT / "docs/downloads"
CACHE_BUILD_DIR = ROOT / ".cache/coulomb_builds"
EVIDENCE = ROOT / "evidence/coulomb_variants.json"
SCREEN = ROOT / "evidence/coulomb_preplacement_screen.json"
LEDGER = ROOT / "ledger/submissions.csv"
CARDS_JSON = ROOT / "ledger/mechanism_cards.json"

PRIOR_FAR_PATHS = {
    "breakline_f45": "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
    "anasig_f45": "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
    "strainbreak_f60": "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
    "stepedge_f60": "docs/downloads/h33-h33-2-b2-STEPEDGEf60Sraw-20261024-66a91dde-zeros.tif",
    "springalign_f33": "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif",
    "piedfront_f35": "docs/downloads/h33-h33-2-b2-PIEDFRONTf35Ptop-20261024-a44bb11b-zeros.tif",
    "apronridge_free1d": "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif",
    "hydroconduit_f45hydro": "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
}
TIER2_KEYS = ("apronridge_free1d", "hydroconduit_f45hydro", "piedfront_f35",
              "breakline_f45", "stepedge_f60")

MECHANISM_CARD = {
    "hypothesis": (
        "Critically stressed fractures -- optimally oriented for simultaneous shear "
        "slip and normal opening under WNW-ESE Basin-and-Range extension plus Walker "
        "Lane dextral shear -- maintain permeability and rupture first, while "
        "misoriented pre-Quaternary contacts stay locked. Resolving signed local "
        "dilatation/shear onto per-pixel lineament normals finds young opening "
        "relay strands whose scarps are too subtle for photo mapping or worms."
    ),
    "mechanism": (
        "At fixed S=37654, DTI rises when expected kernel credit per dot rises. "
        "Standalone emission on 1D crests of max(RTP tilt-contact edge, relative "
        "monoclinal scarp) x Coulomb opening tendency x piedmont apron concentrates "
        "mass on opening lineaments in extending crust, repelling all prior far "
        "sets >3px so credit is not double-counted with earlier lanes."
    ),
    "non_fault_mimic": (
        "Alluvial compaction / groundwater-withdrawal subsidence bowls (apparent "
        "dilatation without faulting), Walker Lane elastic strain shadows "
        "(shear-parallel, no open fault), and Lahontan shoreline benches / fan "
        "terrace risers striking near-NNE inside extending crust."
    ),
    "falsifier": (
        "Pooled HOLDOUT-DTI at/below R0 (0.004006) with paired CI excluding a gain, "
        "single-feature canary symmetric AUC > 0.90, or forward 3-px overlap > 0.70 "
        "/ |rho| > 0.90 vs any pre-session registry raster."
    ),
    "decision_rule": (
        "Promote only if pooled HOLDOUT-DTI beats HYDROCONDUIT f45hydro (0.008549) "
        "with paired CI excluding 0 vs R0 AND literal local uniqueness passes AND "
        "all format gates pass; otherwise verdict='negative' (OK TO DOWNLOAD, NOT "
        "CLEARED FOR A WEEKLY SLOT)."
    ),
}


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot


def main() -> int:
    screen = json.loads(SCREEN.read_text(encoding="utf-8"))
    assert screen["baseline_reproduced_within_5e-4"] is True, "screen gate-zero failed"
    assert screen["screen_decision"]["build_rank1_coulomb"] is True, \
        "pre-registered screen gate says DO NOT BUILD Rank 1"
    print("Screen gate PASS: baseline reproduced, Rank-1 build authorized.", flush=True)

    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    grid = grid_mod.load_grid(ROOT / ".cache/gems_inputs/bridge")
    assert np.array_equal(grid.footprint, foot) and np.array_equal(grid.catalogue, cat)
    assert int(r0.sum()) == N_BUDGET and not np.any(r0 & ~h19)

    print("Loading bands ...", flush=True)
    with rasterio.open(inputs["training_features"]) as ds:
        b2 = ds.read(2, masked=True).filled(np.nan).astype(np.float32)
        b4 = ds.read(4, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
        b7 = ds.read(7, masked=True).filled(np.nan).astype(np.float32)
        b8 = ds.read(8, masked=True).filled(np.nan).astype(np.float32)
        b10 = ds.read(10, masked=True).filled(np.nan).astype(np.float32)
        b12 = ds.read(12, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b16 = ds.read(16, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)

    print("Building COULOMB surfaces ...", flush=True)
    surf = coulomb_surface(
        det_elev=b12, det_elev_slope=b19, depth_to_base=b15, grav_slope=b5,
        rtp=b2, dilaterate=b8, shearrate=b7, second_inv=b4,
        deq=b10, ieq=b16, footprint=foot,
    )
    valid = surf["valid"]
    p33, p67 = [float(x) for x in np.percentile(b12[foot & np.isfinite(b12)], [33.333, 66.667])]
    print(f"valid={int(valid.sum())} det_elev terciles p33={p33:.2f} p67={p67:.2f}", flush=True)

    d_h19 = distance_transform_edt(~h19)
    prior_masks: dict[str, np.ndarray] = {}
    for key, rel in PRIOR_FAR_PATHS.items():
        m = load_mask(ROOT / rel, foot)
        prior_masks[key] = m if key == "apronridge_free1d" else (m & (d_h19 > 3.0))
        print(f"prior {key}: {int(prior_masks[key].sum())} repulsion px", flush=True)
    union_t1 = np.zeros_like(foot)
    for m in prior_masks.values():
        union_t1 |= m
    union_t2 = np.zeros_like(foot)
    for key in TIER2_KEYS:
        union_t2 |= prior_masks[key]
    d_t1 = distance_transform_edt(~union_t1)
    d_t2 = distance_transform_edt(~union_t2)
    del union_t1, union_t2

    arms_spec = [
        ("free", surf["S_free_raw"], surf["ridge_free"], surf["S_free_pct"],
         "full-physics standalone (RTP tilt + rel scarp) x Coulomb x apron",
         f"{PARENT_ID}; COULOMB free: 37654 standalone opening-tendency 1D crests, piedmont-gated (0 H19-5)"),
        ("open", surf["S_open_raw"], surf["ridge_open"], surf["S_open_pct"],
         "no-apron ablation: (RTP tilt + rel scarp) x Coulomb",
         f"{PARENT_ID}; COULOMB open: 37654 standalone opening-tendency 1D crests, no apron gate (0 H19-5)"),
        ("seismo", surf["S_seismo_raw"], surf["ridge_seismo"], surf["S_seismo_pct"],
         "Rank-1 x Rank-2 fusion: free x (0.5+0.5 seismo prior)",
         f"{PARENT_ID}; COULOMB seismo: 37654 Coulomb x swarm-prior 1D crests, piedmont-gated (0 H19-5)"),
    ]
    for _, _, _, _, _, note in arms_spec:
        assert len(note) <= 140, f"form note {len(note)} > 140"

    git_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_BUILD_DIR.mkdir(parents=True, exist_ok=True)
    variants = []

    for val_name, s_raw, ridge, s_pct, short_desc, form_note in arms_spec:
        print(f"\n=== Building Experiment {val_name} ===", flush=True)
        pool_t1 = foot & valid & ridge & (d_cat > 2.0) & (d_t1 > 3.0)
        n_t1 = int(pool_t1.sum())
        if n_t1 >= TIER1_MIN_POOL:
            cand, tier = pool_t1, "tier1_all_prior_far"
        else:
            cand = foot & valid & ridge & (d_cat > 2.0) & (d_t2 > 3.0)
            tier = "tier2_top5_prior_far"
        n_pool = int(cand.sum())
        print(f"crest pool: tier1={n_t1} -> using {tier} pool={n_pool}", flush=True)
        final_mask = spaced_top_mask(s_raw, cand, N_BUDGET, min_dist_px=2.8, cand_cap=800_000)

        assert int(final_mask.sum()) == N_BUDGET
        assert not np.any(final_mask & cat)
        assert float(d_cat[final_mask].min()) > 2.0

        tmp_nan = CACHE_BUILD_DIR / f"._tmp_{val_name}_nan.tif"
        write_tif(tmp_nan, profile, foot, final_mask, nan_outside=True)
        sha_nan = sha256_file(tmp_nan)
        sha8 = sha_nan[:8]
        stem = f"{PARENT_ID}-{AXIS}{val_name}-{DATE}-{sha8}"
        nan_cache_path = CACHE_BUILD_DIR / f"{stem}.tif"
        if nan_cache_path.exists():
            nan_cache_path.unlink()
        tmp_nan.replace(nan_cache_path)

        zeros_filename = f"{stem}-zeros.tif"
        zeros_dl_path = DOWNLOADS_DIR / zeros_filename
        for ext in (".tif", ".zip", ".json"):
            p_clean = zeros_dl_path.with_suffix(ext)
            if p_clean.exists():
                p_clean.unlink()

        sub_name = f"GEMSDOE92-{AXIS}-{val_name}-{DATE}"
        pred_f32 = np.where(final_mask, 1.0, 0.0).astype(np.float32)
        writer_receipt = submission_writer.write_submission(
            zeros_dl_path, pred_f32, inputs["sample_submission"], foot,
            note=form_note, name=sub_name, catalogue=cat,
            metadata={"axis": AXIS, "arm": val_name, "repulsion_tier": tier},
        )
        aux_writer_json = zeros_dl_path.with_suffix(".json")
        if aux_writer_json.is_file():
            aux_writer_json.replace(CACHE_BUILD_DIR / aux_writer_json.name)
        assert sha256_file(zeros_dl_path) == writer_receipt["sha256"]
        zeros_dl_path.chmod(0o644)
        zip_dl_path = zeros_dl_path.with_suffix(".zip")
        if zip_dl_path.is_file():
            zip_dl_path.chmod(0o644)

        nan_checks = validate_reopened(nan_cache_path, inputs["sample_submission"],
                                       inputs["existing_faults"], final_mask, foot, cat,
                                       d_cat, expect_nan_outside=True)
        zeros_checks = validate_reopened(zeros_dl_path, inputs["sample_submission"],
                                         inputs["existing_faults"], final_mask, foot, cat,
                                         d_cat, expect_nan_outside=False)
        g57_zeros = gems57_validate.validate(zeros_dl_path, footprint=foot, catalogue=cat)
        gems57_validate.assert_submittable(g57_zeros)
        gates_z = run_gates(str(zeros_dl_path), str(inputs["sample_submission"]),
                            str(inputs["existing_faults"]), prune_radius=2)
        ok_z, rep_z = summarise(gates_z)
        assert ok_z, f"Gates failed on {zeros_dl_path}:\n{rep_z}"

        z_dots = b12[final_mask]
        n_basin = int(np.sum(z_dots < p33))
        n_pied = int(np.sum((z_dots >= p33) & (z_dots < p67)))
        n_range = int(np.sum(z_dots >= p67))
        rtp_dom = int(np.sum(surf["R_rtp_tilt"][final_mask]
                             > surf["R_scarp_rel"][final_mask]))
        shared_r0 = int((final_mask & r0).sum())
        within3_h19 = float(np.mean(d_h19[final_mask] <= 3.0))
        mean_o = float(surf["O_coulomb"][final_mask].mean())
        mean_s = float(s_pct[final_mask].mean())

        variants.append({
            "id": stem, "site": "GEMSDOE92", "submission_name": sub_name,
            "value": val_name, "axis": AXIS, "parent": PARENT_ID,
            "n_dots": N_BUDGET,
            "pct_changed": float((N_BUDGET - shared_r0) / N_BUDGET * 100.0),
            "file_zeros": f"docs/downloads/{zeros_filename}",
            "file_zip": f"docs/downloads/{stem}-zeros.zip",
            "file_nan_cache": f".cache/coulomb_builds/{stem}.tif",
            "sha8": sha8, "sha256": sha_nan, "sha256_zeros": writer_receipt["sha256"],
            "status": "BUILT",
            "predicted_change": "MODEL: unknown live delta; HOLDOUT-DTI in evidence/coulomb_proxy_audit.json",
            "change_desc": f"COULOMB ({val_name}): {short_desc}; fixed 37654 unit dots",
            "notes": (f"arm={val_name}; repulsion={tier}; pool={n_pool}; shared_R0={shared_r0}; "
                      f"within3px_H19={within3_h19:.4f}; piedmont_pct={n_pied/N_BUDGET*100:.1f}%; "
                      f"rtp_dom_dots={rtp_dom}; git={git_sha[:12]}"),
            "parent_diff": {
                "shared_exact_r0": shared_r0,
                "n_skeleton_repacked": 0,
                "n_far_off_h19": N_BUDGET,
                "min_catalogue_distance_px": float(d_cat[final_mask].min()),
                "collar_dots_final_dcat_le_3": int(np.sum(final_mask & (d_cat <= 3.0))),
                "tercile_counts": {"basin": n_basin, "piedmont": n_pied, "range_core": n_range},
                "rtp_dominant_dots": rtp_dom,
                "mean_O_coulomb_on_dots": mean_o,
                "mean_S_pct_on_dots": mean_s,
                "repulsion_tier": tier,
                "crest_pool_px": n_pool,
                "tier1_pool_px": n_t1,
            },
            "format_validation": {
                "nan": nan_checks, "zeros": zeros_checks,
                "gems57_zeros_all_checks_passed": g57_zeros["all_checks_passed"],
            },
            "form_note": form_note,
            "gate_status": "PASS (disk reread + gems.gates + gems57.validate; EPSG:32611, 3730x3292, float32, [0,1] finite, zero catalogue mass, d_cat>2.0)",
            "seed": 0,
        })
        print(f"PASS {stem}: shared_R0={shared_r0} pied={n_pied/N_BUDGET:.3f} "
              f"range={n_range/N_BUDGET:.3f} tier={tier}", flush=True)

    del surf, b2, b4, b5, b7, b8, b10, b12, b15, b16, b19, d_t1, d_t2, d_h19
    EVIDENCE.write_text(json.dumps({
        "schema": "gemsdoe92.coulomb-variants.v1",
        "session_date_utc": DATE,
        "axis": AXIS,
        "hypothesis_doc": "docs/HYPOTHESES_20261024_COULOMB.md",
        "preplacement_screen": "evidence/coulomb_preplacement_screen.json",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "variants": variants,
    }, indent=2) + "\n", encoding="utf-8")

    with LEDGER.open("r", newline="", encoding="utf-8") as f:
        existing_rows = list(csv.DictReader(f))
        fieldnames = list(existing_rows[0].keys())
    existing_ids = {r["id"] for r in existing_rows}
    new_rows = []
    for v in variants:
        if v["id"] in existing_ids:
            continue
        row = {k: "" for k in fieldnames}
        row.update({"id": v["id"], "parent": v["parent"], "axis": v["axis"],
                    "value": v["value"], "n_dots": str(v["n_dots"]),
                    "pct_changed": f"{v['pct_changed']:.6f}", "sha256": v["sha256"],
                    "status": "BUILT", "predicted_change": v["predicted_change"],
                    "file_zeros": v["file_zeros"], "file_nan": v["file_nan_cache"],
                    "sha8": v["sha8"], "change_desc": v["change_desc"],
                    "receipt_score": "", "receipt_date": "", "notes": v["notes"]})
        new_rows.append(row)
    if new_rows:
        with LEDGER.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_rows + new_rows)
        print(f"Appended {len(new_rows)} rows to {LEDGER}")

    cards = json.loads(CARDS_JSON.read_text(encoding="utf-8")) if CARDS_JSON.is_file() else {}
    for v in variants:
        cards[v["id"]] = {"parent": PARENT_ID, "axis": AXIS, "value": v["value"],
                          **MECHANISM_CARD,
                          "predicted_sign_and_size": v["predicted_change"]}
    CARDS_JSON.write_text(json.dumps(cards, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
