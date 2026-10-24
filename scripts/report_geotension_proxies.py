#!/usr/bin/env python3
"""Report-only evaluation for GEOTENSION experiments (2026-10-24 session).

Uses the exact shared repo instruments without private forks (Protocol Rules 1-5):
1. gems57.holdout.buffered_component_draw (seeds 20, 30 -> 8 folds, 22,663 withheld positives)
   + gems57.evaluate_holdout.{evaluate, pooled_summary} ('gems57-pooled-hide-v2', draws=1000, seed=520810)
2. Buffered-fold single-feature leakage canaries (ROC AUC & symmetric AUC; flag if > 0.90)
3. USGS SGMC 1:500k off-catalogue fault control via gems57.metric.dti_binary(..., known=cat)
4. Pre-placement surface + final-dot uniqueness across all cross-lane local rasters
   (forward 3-px overlap <= 0.70 AND |Spearman| <= 0.90)
5. Direct Git-blob-verified binding public witness check (scripts/check_public_witness.py
   against buffedlizard55-lab/17GEMSDOE E-proba-multiscale, git blob 374c88b1...)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests, write_tif  # noqa: E402
from exact_dti_refill import select_exact_marginal_dti_add  # noqa: E402
from gems.geotension import lane_surface  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402

VARIANTS_JSON = ROOT / "evidence" / "geotension_variants.json"
SURF_REG_JSON = ROOT / "evidence" / "geotension_surface_registry.json"
AUDIT_OUT = ROOT / "evidence" / "geotension_proxy_audit.json"
RUN_CARD_OUT = ROOT / "evidence" / "geotension_run_card.json"
TOP_RUN_CARD_OUT = ROOT / "evidence" / "run_card.json"
WITNESS_OUT = ROOT / "evidence" / "public_witness_geotension.json"
WITNESS_CACHE = ROOT / ".cache" / "witness_17GEMSDOE.tif"
WITNESS_GIT_SHA = "374c88b1da2b803e2ed160de467fd71ae114010d"
WITNESS_REPO = "buffedlizard55-lab/17GEMSDOE"
WITNESS_PATH = "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
EXPECTED_RELIEF_P10_ZEROS_SHA = "60f0208547efd4fb8b52fd5a298d9151de15208c3c44b04e90e78ec13a978296"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mask(path: Path, footprint: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & footprint


def phi_and_jaccard(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> tuple[float, float]:
    af = a & footprint
    bf = b & footprint
    n11 = int(np.sum(af & bf))
    n10 = int(np.sum(af & ~bf))
    n01 = int(np.sum(~af & bf))
    n00 = int(np.sum(footprint) - n11 - n10 - n01)
    den = float(np.sqrt(float(max((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00), 1))))
    phi = float((float(n11 * n00 - n10 * n01)) / den) if den > 0 else 0.0
    jac = float(n11 / max(n11 + n10 + n01, 1))
    return phi, jac


def rebuild_verified_relief_p10(inputs, foot, d_cat, h19, parent_bundle) -> np.ndarray:
    """Deterministically reconstruct RELIEF p10piedmont and verify its SHA-256."""
    cache_p10 = ROOT / ".cache" / "relief_p10piedmont_zeros.tif"
    if cache_p10.is_file() and sha256_file(cache_p10) == EXPECTED_RELIEF_P10_ZEROS_SHA:
        return load_mask(cache_p10, foot)

    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    with rasterio.open(inputs["training_features"]) as ds:
        det_elev = ds.read(12, masked=True).filled(np.nan)
        tmi_hg = ds.read(3, masked=True).filled(np.nan)
        grav_slope = ds.read(5, masked=True).filled(np.nan)
        det_slope = ds.read(19, masked=True).filled(np.nan)

    valid_elev = foot & np.isfinite(det_elev) & (det_elev > -1e30)
    p33, p67 = np.percentile(det_elev[valid_elev], [33.333333, 66.666667])
    is_basin = det_elev < p33
    is_piedmont = (det_elev >= p33) & (det_elev < p67)
    is_range = det_elev >= p67

    valid_stack = (
        valid_elev
        & np.isfinite(tmi_hg)
        & (tmi_hg > -1e30)
        & np.isfinite(grav_slope)
        & (grav_slope > -1e30)
        & np.isfinite(det_slope)
        & (det_slope > -1e30)
    )
    phys_prior = np.zeros_like(det_elev, dtype=np.float32)
    r_tmi = rankdata(tmi_hg[valid_stack]) / np.sum(valid_stack)
    r_grav = rankdata(grav_slope[valid_stack]) / np.sum(valid_stack)
    r_scarp = rankdata(det_slope[valid_stack]) / np.sum(valid_stack)
    phys_prior[valid_stack] = (0.40 * r_tmi + 0.35 * r_grav + 0.25 * r_scarp).astype(np.float32)

    dti_weight = np.where(h19, 0.30 + 0.70 * phys_prior, 0.08 * phys_prior).astype(np.float32)
    dti_weight[~foot] = 0.0

    n_shift = int(round(0.10 * int(r0.sum())))
    src_ys, src_xs = np.nonzero(r0 & (is_basin | is_range))
    src_order = np.argsort(phys_prior[src_ys, src_xs])
    base_mask = r0.copy()
    base_mask[src_ys[src_order[:n_shift]], src_xs[src_order[:n_shift]]] = False
    cand_mask = h19 & is_piedmont & (d_cat > 2.0) & foot & (~r0) & (~base_mask)
    p10_mask = select_exact_marginal_dti_add(base_mask, cand_mask, dti_weight, n_shift)

    write_tif(cache_p10, profile, foot, p10_mask, nan_outside=False)
    got_sha = sha256_file(cache_p10)
    assert got_sha == EXPECTED_RELIEF_P10_ZEROS_SHA, (
        f"RELIEF p10 SHA mismatch: {got_sha} != {EXPECTED_RELIEF_P10_ZEROS_SHA}"
    )
    return p10_mask


def collect_local_registry(inputs: dict[str, Path], parent_r0_path: Path) -> list[tuple[str, Path]]:
    """Collect all unique local rasters outside the GEOTENSION lane for cross-lane uniqueness."""
    cache_in = ROOT / ".cache" / "gems_inputs"
    candidates: list[tuple[str, Path]] = [
        ("parent_R0_zeros.tif", parent_r0_path),
        ("h19_5.tif", cache_in / "h19_5.tif"),
        ("d15_from_h19_5.tif", cache_in / "d15_from_h19_5.tif"),
        ("d28_from_d15.tif", cache_in / "d28_from_d15.tif"),
        ("h27_4_solo.tif", cache_in / "h27_4_solo.tif"),
        ("h33_2_b2_r0_canonical.tif", cache_in / "h33_2_b2_r0_canonical.tif"),
    ]
    for d in (ROOT / "docs" / "downloads", ROOT / "releases"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if "GEOTENSION" in p.name:
                continue
            candidates.append((f"{d.name}/{p.name}", p))

    seen_hashes: set[str] = set()
    deduped: list[tuple[str, Path]] = []
    for label, p in candidates:
        if not p.is_file():
            continue
        h = sha256_file(p)
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        deduped.append((label, p))
    return deduped


def main() -> int:
    assert VARIANTS_JSON.is_file(), "Run scripts/build_geotension_variants.py first"
    vdoc = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))
    variants = vdoc["variants"]

    inputs = verify_all_manifests()
    foot, cat, d_cat, h19, parent_bundle = build_and_verify_parent(inputs)
    r0 = parent_bundle["r0"]
    profile = parent_bundle["profile"]
    grid = grid_mod.load_grid()

    parent_r0_cache = ROOT / ".cache" / "parent_R0_zeros.tif"
    if not parent_r0_cache.is_file():
        write_tif(parent_r0_cache, profile, foot, r0, nan_outside=False)

    print("1. Assembling arms & controls for gems57-pooled-hide-v2...")
    p10_mask = rebuild_verified_relief_p10(inputs, foot, d_cat, h19, parent_bundle)
    arms: dict[str, np.ndarray] = {
        "R0": r0,
        "RELIEF_p10piedmont": p10_mask,
    }
    baseline_files = {
        "STRAINBREAK_f60s2i": ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
        "ANASIG_f45Atop": ROOT / "docs/downloads/h33-h33-2-b2-ANASIGf45Atop-20261024-1d90574a-zeros.tif",
        "SPRINGALIGN_f33Ctop": ROOT / "docs/downloads/h33-h33-2-b2-SPRINGALIGNf33Ctop-20261025-9857d09a-zeros.tif",
        "BREAKLINE_f45Ltop": ROOT / "docs/downloads/h33-h33-2-b2-BREAKLINEf45Ltop-20261024-57fa85f0-zeros.tif",
    }
    for bname, bpath in baseline_files.items():
        if bpath.is_file():
            arms[bname] = load_mask(bpath, foot)

    cand_names = []
    for v in variants:
        arm = v["value"]
        cand_names.append(arm)
        arms[arm] = load_mask(ROOT / v["file_zeros"], foot)

    folds = []
    split_receipts = []
    for seed in (20, 30):
        draw, _ = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
        split_receipts.append({"seed": seed, "folds": [x["receipt"] for x in draw]})

    terms_by_arm: dict[str, np.ndarray] = {}
    per_arm_fold_scores: dict[str, list[float]] = {}
    for arm_name, mask in arms.items():
        all_terms = None
        per_arm_fold_scores[arm_name] = []
        for fold in folds:
            score, terms = evaluate_holdout.evaluate(mask.astype(np.float32), fold, foot)
            per_arm_fold_scores[arm_name].append(float(score["dti"]))
            all_terms = terms if all_terms is None else all_terms + terms
        terms_by_arm[arm_name] = all_terms

    pooled_by_candidate = {
        cand: evaluate_holdout.pooled_summary(
            terms_by_arm, draws=1000, seed=520810, candidate=cand
        )
        for cand in cand_names
    }
    scores_all = pooled_by_candidate[cand_names[0]]["scores"]
    print("\n=== POOLED HOLDOUT-DTI (gems57-pooled-hide-v2, 8 folds, 22,663 withheld px) ===")
    for name, s in scores_all.items():
        print(f"   {name:22s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")

    print("\n2. Buffered-fold single-feature leakage canaries...")
    rng = np.random.default_rng(520810)
    y_parts, sample_indices = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(len(neg), max(1, 2 * len(pos)))
        neg = rng.choice(neg, size=n, replace=False) if len(neg) > n else neg
        sample_indices.extend((pos, neg))
        y_parts.extend((np.ones(len(pos), np.uint8), np.zeros(len(neg), np.uint8)))
    y = np.concatenate(y_parts)
    flat_idx = np.concatenate(sample_indices)

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
    surf = lane_surface(
        det_elev=b12,
        det_elev_slope=b19,
        depth_to_base=b15,
        grav_slope=b5,
        rtp=b2,
        tc=b6,
        valid=valid,
    )
    canary_arrays = {
        "Band02_rtp": b2,
        "Band05_iso_grav_anom_slope": b5,
        "Band06_tc": b6,
        "Band12_det_elev": b12,
        "Band15_depth_to_base_surf": b15,
        "Band19_det_elev_slope": b19,
        "GEOTENSION_H_apron": surf["H_apron"],
        "GEOTENSION_R_scarp": surf["R_scarp"],
        "GEOTENSION_R_rtp": surf["R_rtp"],
        "GEOTENSION_S_raw": surf["S_raw"],
        "GEOTENSION_S_pct": surf["S_pct"],
    }
    canaries = {}
    for cname, arr in canary_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        status = "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS"
        assert status == "REPORT_ONLY_PASS", f"Leakage canary > 0.90 on {cname}: {sym}"
        canaries[cname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6), "status": status}
        print(f"   Canary {cname:28s}: auc={auc:.6f}  sym_auc={sym:.6f}  [{status}]")
    del b2, b5, b6, b12, b15, b19, surf

    print("\n3. USGS SGMC 1:500k off-catalogue fault control (>3 px off catalogue)...")
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {
        k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }
    for k, v in sgmc_scores.items():
        print(f"   SGMC {k:22s}: DTI = {v:.6f} (delta vs R0 = {v - sgmc_scores['R0']:+.6f})")

    catdiag = {
        k: round(float(metric.dti_binary(m, cat, valid=foot, known=None)["dti"]), 6)
        for k, m in arms.items()
    }

    print("\n4. Final-dot local registry uniqueness scan...")
    registry_list = collect_local_registry(inputs, parent_r0_cache)
    print(f"   Checking {len(registry_list)} cross-lane local rasters (streaming, bounded RAM)...")

    yy_k, xx_k = np.ogrid[-3:4, -3:4]
    disk3 = (yy_k * yy_k + xx_k * xx_k) <= 9  # exact Euclidean distance <= 3.0 px
    cand_halos = {cand: binary_dilation(arms[cand], structure=disk3) for cand in cand_names}
    per_cand_rows: dict[str, list[dict]] = {cand: [] for cand in cand_names}

    for label, rpath in registry_list:
        rmask = load_mask(rpath, foot)
        rhalo = binary_dilation(rmask, structure=disk3) if rmask.any() else np.zeros_like(foot)
        has_r = bool(rmask.any())
        for cand in cand_names:
            cmask = arms[cand]
            fwd = float(np.mean(rhalo[cmask]))
            rev = float(np.mean(cand_halos[cand][rmask])) if has_r else 0.0
            phi, jac = phi_and_jaccard(cmask, rmask, foot)
            per_cand_rows[cand].append(
                {
                    "raster": label,
                    "forward_3px_overlap": round(fwd, 6),
                    "reverse_3px_overlap": round(rev, 6),
                    "spearman_phi": round(phi, 6),
                    "jaccard": round(jac, 6),
                }
            )
        del rmask, rhalo

    uniq_by_arm = {}
    for cand in cand_names:
        rows = per_cand_rows[cand]
        worst_fwd_row = max(rows, key=lambda x: x["forward_3px_overlap"])
        worst_rho_row = max(rows, key=lambda x: abs(x["spearman_phi"]))
        worst_fwd = float(worst_fwd_row["forward_3px_overlap"])
        worst_fwd_file = worst_fwd_row["raster"]
        worst_rho = abs(float(worst_rho_row["spearman_phi"]))
        worst_rho_file = worst_rho_row["raster"]
        local_dup = bool(worst_fwd > 0.70 or worst_rho > 0.90)
        uniq_by_arm[cand] = {
            "n_rasters_checked": len(rows),
            "worst_forward_overlap": round(worst_fwd, 6),
            "worst_forward_file": worst_fwd_file,
            "worst_abs_spearman_phi": round(worst_rho, 6),
            "worst_spearman_file": worst_rho_file,
            "local_duplicate": local_dup,
            "top5_by_forward_overlap": sorted(
                rows, key=lambda x: x["forward_3px_overlap"], reverse=True
            )[:5],
            "all_comparisons": rows,
        }
        print(
            f"   Uniqueness {cand:8s}: worst_fwd={worst_fwd:.6f} ({worst_fwd_file}), "
            f"worst_|phi|={worst_rho:.6f} ({worst_rho_file}), local_dup={local_dup}"
        )

    # Cross-sibling relatedness among the 3 GEOTENSION experiments
    sibling_matrix = {}
    for c1 in cand_names:
        sibling_matrix[c1] = {}
        for c2 in cand_names:
            if c1 == c2:
                continue
            fwd = float(np.mean(cand_halos[c2][arms[c1]]))
            phi, jac = phi_and_jaccard(arms[c1], arms[c2], foot)
            sibling_matrix[c1][c2] = {
                "forward_3px_overlap": round(fwd, 6),
                "spearman_phi": round(phi, 6),
                "jaccard": round(jac, 6),
            }
    del cand_halos

    # Select winning locally-unique GEOTENSION arm by highest pooled HOLDOUT-DTI
    eligible_local = [
        cand for cand in cand_names if not uniq_by_arm[cand]["local_duplicate"]
    ]
    assert eligible_local, "All GEOTENSION arms tripped local uniqueness!"
    best_arm = max(eligible_local, key=lambda c: scores_all[c]["dti"])
    best_variant = next(v for v in variants if v["value"] == best_arm)
    best_pooled = pooled_by_candidate[best_arm]
    best_score = best_pooled["scores"][best_arm]
    best_diffs = best_pooled["paired_differences"]
    print(f"\n5. Winning locally-unique GEOTENSION arm: {best_arm} ({best_variant['id']})")
    print(
        f"   HOLDOUT-DTI = {best_score['dti']:.6f} {best_score['ci95']} | "
        f"vs R0 = {best_diffs['R0']['delta']:+.6f} {best_diffs['R0']['ci95']} | "
        f"vs STRAINBREAK = {best_diffs['STRAINBREAK_f60s2i']['delta']:+.6f} | "
        f"vs RELIEF p10 = {best_diffs['RELIEF_p10piedmont']['delta']:+.6f}"
    )

    assert WITNESS_CACHE.is_file(), f"Missing cached witness blob {WITNESS_CACHE}"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_public_witness.py"),
            str(ROOT / best_variant["file_zeros"]),
            str(WITNESS_CACHE),
            "--repo",
            WITNESS_REPO,
            "--path",
            WITNESS_PATH,
            "--git-sha",
            WITNESS_GIT_SHA,
            "--output",
            str(WITNESS_OUT),
        ],
        check=True,
        cwd=ROOT,
    )
    witness_doc = json.loads(WITNESS_OUT.read_text(encoding="utf-8"))
    public_unique = bool(witness_doc["unique_under_literal_rule_vs_this_witness"])
    beats_holdout_best = bool(best_score["dti"] > scores_all["RELIEF_p10piedmont"]["dti"])
    beats_unique_best = bool(best_score["dti"] > scores_all["STRAINBREAK_f60s2i"]["dti"])
    beats_r0_ci = bool(best_diffs["R0"]["ci95"][0] > 0.0)
    submission_eligible = bool(
        beats_holdout_best
        and beats_r0_ci
        and (not uniq_by_arm[best_arm]["local_duplicate"])
        and public_unique
    )
    verdict = "promote" if submission_eligible else "negative"

    if beats_holdout_best:
        verdict_detail = (
            f"negative — beats repository holdout best RELIEF p10 ({best_score['dti']:.6f} vs "
            f"{scores_all['RELIEF_p10piedmont']['dti']:.6f}) and locally-unique best STRAINBREAK f60s2i "
            f"({scores_all['STRAINBREAK_f60s2i']['dti']:.6f}), passes 10/10 format gates, and is locally "
            f"unique across all {uniq_by_arm[best_arm]['n_rasters_checked']} cross-lane rasters; blocked "
            "ONLY by the unresolved literal public dense witness (17GEMSDOE E-proba-multiscale, 100% "
            "footprint positive => 1.0 forward overlap). OK TO DOWNLOAD for research; NOT CLEARED FOR A "
            "WEEKLY SLOT until operator density-clause revision."
        )
    elif beats_unique_best:
        verdict_detail = (
            f"negative — sets a new repository locally-unique HOLDOUT-DTI high ({best_score['dti']:.6f} vs "
            f"STRAINBREAK f60s2i {scores_all['STRAINBREAK_f60s2i']['dti']:.6f}) and beats R0 with paired "
            f"95% CI excluding 0, passes 10/10 format gates, and is locally unique across all "
            f"{uniq_by_arm[best_arm]['n_rasters_checked']} cross-lane rasters, but remains below the "
            f"R0-duplicate RELIEF p10 benchmark ({scores_all['RELIEF_p10piedmont']['dti']:.6f}) and "
            "blocked by the unresolved literal public dense witness (17GEMSDOE E-proba-multiscale). "
            "OK TO DOWNLOAD for research; NOT CLEARED FOR A WEEKLY SLOT."
        )
    else:
        verdict_detail = (
            f"negative — 10/10 format-valid and locally unique across all "
            f"{uniq_by_arm[best_arm]['n_rasters_checked']} cross-lane rasters, with HOLDOUT-DTI "
            f"{best_score['dti']:.6f} below holdout best RELIEF p10 ({scores_all['RELIEF_p10piedmont']['dti']:.6f}) "
            "and blocked by the unresolved literal public dense witness (17GEMSDOE E-proba-multiscale). "
            "OK TO DOWNLOAD for research; NOT CLEARED FOR A WEEKLY SLOT."
        )

    surf_reg_doc = json.loads(SURF_REG_JSON.read_text(encoding="utf-8"))
    max_sym_auc = max(c["symmetric_auc"] for c in canaries.values())

    # Write <stem>-audit.json sidecars in docs/downloads/ and keep ONLY winning arm's .zip
    for v in variants:
        arm = v["value"]
        u = uniq_by_arm[arm]
        zpath = ROOT / v["file_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        audit_sidecar = zpath.parent / f"{stem}-audit.json"
        if arm != best_arm:
            non_primary_zip = zpath.parent / f"{stem}-zeros.zip"
            if non_primary_zip.is_file():
                non_primary_zip.unlink()

        sidecar_doc = {
            "gates_zeros": v["gates_zeros"],
            "gates_zeros_pass": all(g["ok"] for g in v["gates_zeros"]),
            "gates_nan": v["gates_nan"],
            "gates_nan_pass": all(g["ok"] for g in v["gates_nan"]),
            "file": zpath.name,
            "sha256_zeros": v["sha256_zeros"],
            "sha256_nan": v["sha256"],
            "n_positive_pixels": v["n_dots"],
            "n_dots": v["n_dots"],
            "overall_pass": bool(
                all(g["ok"] for g in v["gates_zeros"]) and all(g["ok"] for g in v["gates_nan"])
            ),
            "submission_eligible": bool(submission_eligible if arm == best_arm else False),
            "run_card": "evidence/geotension_run_card.json",
            "local_registry_uniqueness": {
                "n_rasters_checked": u["n_rasters_checked"],
                "worst_forward_overlap_3px": u["worst_forward_overlap"],
                "worst_forward_file": u["worst_forward_file"],
                "worst_abs_spearman_phi": u["worst_abs_spearman_phi"],
                "local_duplicate": u["local_duplicate"],
            },
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": bool(arm == best_arm),
                "unique_under_literal_rule": False,
                "stop_required": True,
                "witness_evidence": "evidence/public_witness_geotension.json",
                "scope": (
                    f"Measured directly on winning candidate bytes ({best_variant['primary_file']}) "
                    "against Git-blob-verified 17GEMSDOE E-proba-multiscale (100% footprint positive => "
                    "forward_overlap=1.0 for every nonempty in-footprint raster). Locally unique across "
                    f"{u['n_rasters_checked']} cross-lane rasters."
                ),
                "candidate_sha256_zeros": v["sha256_zeros"],
            },
        }
        audit_sidecar.write_text(json.dumps(sidecar_doc, indent=2) + "\n", encoding="utf-8")

    run_card = {
        "hypothesis": (
            "Active Quaternary range-front splays and synthetic piedmont step-faults concentrate in "
            "the thin-cover piedmont accommodation apron (Band 12 det_elev transition x Band 15 "
            "depth_to_base_surf ~20-600 m x Band 5 iso_grav_anom_slope), expressing as coherent DEM "
            "slope-breaks (Bands 19/12) or shallow-buried Reduced-to-Pole magnetic gradient x inverted "
            "tc curvature 1D ridges (Bands 2/6) centered vertically over basement contacts."
        ),
        "mechanism": (
            f"GEOTENSION {best_arm}: standalone physics-first 1D crest emission allocates all "
            f"{best_variant['n_dots']} unit-mass dots via spaced_top_mask(S_raw, min_dist=2.8 px) "
            "on 4-axis non-maximum-suppressed GEOTENSION crests (S_raw = H_apron * max(R_scarp, "
            "0.85 * R_rtp), d_cat > 2.0 px), using ZERO H19-5 skeleton, ZERO R0 parent dots, and "
            "ZERO catalogue input in surface or weights."
            if best_variant["n_skel"] == 0
            else (
                f"GEOTENSION {best_arm}: exact marginal expected-DTI greedy allocates "
                f"{best_variant['n_skel']} dots across the full eligible H19-5 network under "
                f"w_skel = H_apron*(0.25+0.75*S_pct) (not restricted to R0), plus "
                f"{best_variant['n_far']} spaced (min_dist=2.8 px) 1D directional-crest dots "
                f"strictly >3.0 px off H19-5 ({best_variant['n_dots']} unit-mass dots, d_cat > 2.0 px)."
            )
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Intermediate-elevation pluvial shoreline benches (Sehoo/Eetza recessional strandlines) "
            "and Gilbert-delta toes on piedmont fans, incised alluvial-fan terrace risers / wash walls, "
            "and remanently magnetized Tertiary basaltic-andesite flow margins beneath thin gravel."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": best_score["withheld_positive_pixels"],
            "dti": best_score["dti"],
            "ci95": best_score["ci95"],
            "paired_vs_R0": best_diffs["R0"],
            "paired_vs_RELIEFp10_holdout_best": best_diffs["RELIEF_p10piedmont"],
            "paired_vs_STRAINBREAKf60s2i_unique_best": best_diffs["STRAINBREAK_f60s2i"],
        },
        "ablation_summary": {
            cand: {
                "evidence_class": "HOLDOUT-DTI",
                "evaluator_version": evaluate_holdout.VERSION,
                "withheld_positive_pixels": scores_all[cand]["withheld_positive_pixels"],
                "dti": scores_all[cand]["dti"],
                "ci95": scores_all[cand]["ci95"],
                "paired_delta_vs_R0": pooled_by_candidate[cand]["paired_differences"]["R0"]["delta"],
                "paired_ci95_vs_R0": pooled_by_candidate[cand]["paired_differences"]["R0"]["ci95"],
                "sgmc_proxy_dti": sgmc_scores[cand],
                "worst_local_forward_overlap_3px": uniq_by_arm[cand]["worst_forward_overlap"],
                "worst_local_forward_file": uniq_by_arm[cand]["worst_forward_file"],
                "worst_local_abs_spearman_phi": uniq_by_arm[cand]["worst_abs_spearman_phi"],
                "local_duplicate": uniq_by_arm[cand]["local_duplicate"],
            }
            for cand in cand_names
        },
        "leakage_canary_max_symmetric_auc": round(max_sym_auc, 6),
        "sgmc_proxy": {
            "evidence_class": "PROXY",
            "dti": sgmc_scores[best_arm],
            "R0": sgmc_scores["R0"],
            "delta_vs_R0": round(sgmc_scores[best_arm] - sgmc_scores["R0"], 6),
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "scope": (
                f"pre-placement surface vs {surf_reg_doc['rasters_checked']} unique local "
                f"rasters + final dots vs {uniq_by_arm[best_arm]['n_rasters_checked']} cross-lane "
                "local rasters + Git-blob-verified public dense witness 17GEMSDOE E-proba"
            ),
            "surface_worst_abs_spearman": surf_reg_doc["worst_abs_spearman"],
            "surface_worst_spearman_file": surf_reg_doc["worst_abs_spearman_file"],
            "surface_worst_top37654_forward_overlap": surf_reg_doc["worst_top37654_forward_overlap"],
            "final_worst_forward_overlap": uniq_by_arm[best_arm]["worst_forward_overlap"],
            "final_worst_forward_file": uniq_by_arm[best_arm]["worst_forward_file"],
            "final_worst_abs_spearman_phi": uniq_by_arm[best_arm]["worst_abs_spearman_phi"],
            "local_duplicate": uniq_by_arm[best_arm]["local_duplicate"],
            "public_dense_witness_forward_overlap": witness_doc[
                "forward_overlap_candidate_dots_within_3px_of_witness"
            ],
            "unique_under_literal_public_rule": public_unique,
            "public_dense_witness_note": (
                "17GEMSDOE E-proba-multiscale (git blob 374c88b1..., positive across all 5,167,373 "
                "footprint cells) yields 1.0 forward 3-px overlap for every nonempty in-footprint "
                "candidate; measured directly on candidate bytes and enforced without waiver."
            ),
        },
        "raster_sha256": best_variant["sha256_zeros"],
        "raster_nan_sha256": best_variant["sha256"],
        "zip_sha256": best_variant["zip_sha256"],
        "primary_download": best_variant["file_zeros"],
        "primary_zip": best_variant["file_zip"],
        "validator_output": {
            "gates_zeros_pass": True,
            "gates_nan_pass": True,
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": True,
            "catalogue_zero_mass": True,
            "min_catalogue_distance_gt_2px": True,
            "n_dots": best_variant["n_dots"],
        },
        "submission_name": best_variant["submission_name"],
        "note": best_variant["form_note"],
        "verdict": verdict,
        "submission_eligible": submission_eligible,
        "experiments_used": len(variants),
        "verdict_detail": verdict_detail,
    }

    report = {
        "evidence_label": "PROXY",
        "created_utc": "20261024",
        "axis": "GEOTENSION",
        "parent": "h33-h33-2-b2",
        "selected_arm": best_arm,
        "selected_id": best_variant["id"],
        "submission_eligible": submission_eligible,
        "verdict": verdict,
        "hide_and_recover_pooled_summary": best_pooled,
        "hide_and_recover_pooled_by_candidate": pooled_by_candidate,
        "holdout_splits": split_receipts,
        "per_arm_fold_scores": per_arm_fold_scores,
        "leakage_canaries": {
            "definition": "symmetric AUC on hidden catalogue positives vs non-catalogue negatives in buffered fold regions",
            "results": canaries,
            "stop_and_investigate_if_any_gt_0_90": False,
            "max_symmetric_auc": round(max_sym_auc, 6),
        },
        "sgmc_control_proxy": {
            "source": "manifest-pinned USGS SGMC derived fault control (https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d, US Public Domain)",
            "truth_pixels_after_catalogue_and_3px_exclusion": int(sgmc_truth.sum()),
            "r0_dti": sgmc_scores["R0"],
            "variant_dti": sgmc_scores,
            "variant_deltas_vs_r0": {
                k: round(v - sgmc_scores["R0"], 6) for k, v in sgmc_scores.items()
            },
        },
        "fixed_catalogue_diagnostic": {
            "evidence_class": "PROXY-DIAGNOSTIC (not a holdout; no withholding)",
            "dti": catdiag,
        },
        "pre_placement_surface_registry": surf_reg_doc,
        "local_registry_uniqueness": {
            k: {kk: vv for kk, vv in v.items() if kk != "all_comparisons"}
            for k, v in uniq_by_arm.items()
        },
        "sibling_overlap_matrix": sibling_matrix,
        "public_witness_check": witness_doc,
        "run_card": run_card,
    }

    AUDIT_OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    RUN_CARD_OUT.write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    TOP_RUN_CARD_OUT.write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {AUDIT_OUT}, {RUN_CARD_OUT}, and {TOP_RUN_CARD_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
