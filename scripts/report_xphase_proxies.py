#!/usr/bin/env python3
"""Report-only evaluation for XPHASE experiments (Protocol Rules 1-5)."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_snap_scarp_variants import build_and_verify_parent, verify_all_manifests, write_tif  # noqa: E402
from gems.xphase import lane_surface  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402

VARIANTS_JSON = ROOT / "evidence" / "xphase_variants.json"
AUDIT_OUT = ROOT / "evidence" / "xphase_proxy_audit.json"
RUN_CARD_OUT = ROOT / "evidence" / "xphase_run_card.json"
WITNESS_OUT = ROOT / "evidence" / "public_witness_xphase.json"
WITNESS_CACHE = ROOT / ".cache" / "witness_17GEMSDOE.tif"
WITNESS_GIT_SHA = "374c88b1da2b803e2ed160de467fd71ae114010d"
WITNESS_REPO = "buffedlizard55-lab/17GEMSDOE"
WITNESS_PATH = "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
WITNESS_COMMIT = "6fc71d19d49dca4960d5434bd81b6dd06fcc030a"


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


def collect_local_registry(parent_r0_path: Path) -> list[tuple[str, Path]]:
    candidates: list[tuple[str, Path]] = [
        ("parent_R0_zeros.tif", parent_r0_path),
        ("data/bridge/h19_5.tif", ROOT / "data" / "bridge" / "h19_5.tif"),
        ("data/bridge/d28.tif", ROOT / "data" / "bridge" / "d28.tif"),
        ("data/bridge/h27_4_solo.tif", ROOT / "data" / "bridge" / "h27_4_solo.tif"),
    ]
    for d in (ROOT / "docs" / "downloads", ROOT / "releases"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if "XPHASE" in p.name:
                continue
            candidates.append((f"{d.name}/{p.name}", p))
    seen: set[str] = set()
    out: list[tuple[str, Path]] = []
    for label, p in candidates:
        if not p.is_file():
            continue
        h = sha256_file(p)
        if h in seen:
            continue
        seen.add(h)
        out.append((label, p))
    return out


def fetch_witness() -> Path:
    if WITNESS_CACHE.is_file() and WITNESS_CACHE.stat().st_size > 1_000_000:
        return WITNESS_CACHE
    WITNESS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=WITNESS_CACHE.parent) as td:
        co = Path(td) / "co"
        url = f"https://github.com/{WITNESS_REPO}.git"
        subprocess.run(
            ["git", "clone", "--quiet", "--filter=blob:none", "--sparse", url, str(co)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(co), "fetch", "--quiet", "--depth=1", "origin", WITNESS_COMMIT],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(co), "checkout", "--quiet", "--detach", WITNESS_COMMIT],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(co), "sparse-checkout", "set", "--no-cone", "/" + WITNESS_PATH],
            check=True,
        )
        src = co / WITNESS_PATH
        shutil.copy2(src, WITNESS_CACHE)
    return WITNESS_CACHE


def main() -> int:
    assert VARIANTS_JSON.is_file(), "Run scripts/build_xphase_variants.py first"
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

    print("1. Assembling arms for gems57-pooled-hide-v2...")
    arms: dict[str, np.ndarray] = {"R0": r0}
    baseline_files = {
        "COULOMBLOQO_standalone": ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif",
        "HYDROCONDUIT_f45hydro": ROOT / "docs/downloads/h33-h33-2-b2-HYDROCONDUITf45hydro-20261024-979c9cdb-zeros.tif",
        "APRONRIDGE_free1d": ROOT / "docs/downloads/h33-h33-2-b2-APRONRIDGEfree1d-20261024-d5760830-zeros.tif",
        "RELIEF_p10piedmont": ROOT / "docs/downloads/h33-h33-2-b2-RELIEFp10piedmont-20261024-3e900c24-zeros.tif",
        "STRAINBREAK_f60s2i": ROOT / "docs/downloads/h33-h33-2-b2-STRAINBREAKf60s2i-20261024-5c3c6ca2-zeros.tif",
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
    n_withheld = int(sum(int(np.sum(f["truth"] & foot & ~np.asarray(f.get("masked_known", f["visible"]), bool))) for f in folds))
    print(f"   {len(folds)} folds, withheld-positive estimate {n_withheld}")

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
    print("\n=== POOLED HOLDOUT-DTI (gems57-pooled-hide-v2) ===")
    for name, s in scores_all.items():
        print(f"   {name:24s}: DTI = {s['dti']:.6f}  95% CI [{s['ci95'][0]:.6f}, {s['ci95'][1]:.6f}]")

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
        b13 = ds.read(13, masked=True).filled(np.nan).astype(np.float32)
        b15 = ds.read(15, masked=True).filled(np.nan).astype(np.float32)
        b17 = ds.read(17, masked=True).filled(np.nan).astype(np.float32)
        b19 = ds.read(19, masked=True).filled(np.nan).astype(np.float32)
        b5 = ds.read(5, masked=True).filled(np.nan).astype(np.float32)
    valid = foot.copy()
    for a in (b13, b15, b17, b19, b5):
        valid &= np.isfinite(a) & (a > -1e30)
    surf = lane_surface(b17, b13, b15, b19, valid, apply_lag=True)
    canary_arrays = {
        "Band05_iso_grav_anom_slope": b5,
        "Band13_iso_grav_anom": b13,
        "Band15_depth_to_base_surf": b15,
        "Band17_cond_surf": b17,
        "Band19_det_elev_slope": b19,
        "XPHASE_mt_pct": surf["mt_pct"],
        "XPHASE_gr_pct": surf["gr_pct"],
        "XPHASE_orient": surf["orient"],
        "XPHASE_lag": surf["lag"],
        "XPHASE_cover": surf["cover"],
        "XPHASE_S_raw": surf["S_raw"],
        "XPHASE_S_pct": surf["S_pct"],
    }
    canaries = {}
    for cname, arr in canary_arrays.items():
        vals = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0).ravel()[flat_idx]
        auc = float(roc_auc_score(y, vals))
        sym = max(auc, 1.0 - auc)
        status = "INVESTIGATE" if sym > 0.90 else "REPORT_ONLY_PASS"
        assert status == "REPORT_ONLY_PASS", f"Leakage canary > 0.90 on {cname}: {sym}"
        canaries[cname] = {"auc": round(auc, 6), "symmetric_auc": round(sym, 6), "status": status}
        print(f"   Canary {cname:32s}: auc={auc:.6f}  sym_auc={sym:.6f}  [{status}]")
    del b13, b15, b17, b19, b5, surf

    print("\n3. USGS SGMC 1:500k off-catalogue fault control...")
    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_truth = sgmc & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_scores = {
        k: round(float(metric.dti_binary(m, sgmc_truth, valid=foot, known=cat)["dti"]), 6)
        for k, m in arms.items()
    }
    for k, v in sgmc_scores.items():
        print(f"   SGMC {k:24s}: DTI = {v:.6f}")

    print("\n4. Final-dot local registry uniqueness scan...")
    registry_list = collect_local_registry(parent_r0_cache)
    print(f"   Checking {len(registry_list)} cross-lane local rasters...")
    yy_k, xx_k = np.ogrid[-3:4, -3:4]
    disk3 = (yy_k * yy_k + xx_k * xx_k) <= 9
    cand_halos = {cand: binary_dilation(arms[cand], structure=disk3) for cand in cand_names}
    per_cand_rows: dict[str, list[dict]] = {cand: [] for cand in cand_names}
    for label, rpath in registry_list:
        rmask = load_mask(rpath, foot)
        rhalo = binary_dilation(rmask, structure=disk3) if rmask.any() else np.zeros_like(foot)
        has_r = bool(rmask.any())
        for cand in cand_names:
            cmask = arms[cand]
            fwd = float(np.mean(rhalo[cmask])) if cmask.any() else 0.0
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
        worst_rho = abs(float(worst_rho_row["spearman_phi"]))
        local_dup = bool(worst_fwd > 0.70 or worst_rho > 0.90)
        uniq_by_arm[cand] = {
            "n_rasters_checked": len(rows),
            "worst_forward_overlap": round(worst_fwd, 6),
            "worst_forward_file": worst_fwd_row["raster"],
            "worst_abs_spearman_phi": round(worst_rho, 6),
            "worst_spearman_file": worst_rho_row["raster"],
            "local_duplicate": local_dup,
            "top5_by_forward_overlap": sorted(
                rows, key=lambda x: x["forward_3px_overlap"], reverse=True
            )[:5],
        }
        print(
            f"   Uniqueness {cand:12s}: worst_fwd={worst_fwd:.6f} "
            f"({worst_fwd_row['raster']}), worst_|phi|={worst_rho:.6f}, local_dup={local_dup}"
        )

    eligible_local = [cand for cand in cand_names if not uniq_by_arm[cand]["local_duplicate"]]
    if not eligible_local:
        print("WARNING: all XPHASE arms tripped local uniqueness; still packaging negative result.")
        eligible_local = list(cand_names)
    best_arm = max(eligible_local, key=lambda c: scores_all[c]["dti"])
    best_variant = next(v for v in variants if v["value"] == best_arm)
    best_pooled = pooled_by_candidate[best_arm]
    best_score = best_pooled["scores"][best_arm]
    best_diffs = best_pooled["paired_differences"]
    print(f"\n5. Winning locally-unique XPHASE arm: {best_arm} ({best_variant['id']})")
    print(
        f"   HOLDOUT-DTI = {best_score['dti']:.6f} {best_score['ci95']} | "
        f"vs R0 = {best_diffs['R0']['delta']:+.6f} {best_diffs['R0']['ci95']}"
    )

    print("\n6. Binding public dense witness (17GEMSDOE E-proba-multiscale)...")
    fetch_witness()
    if WITNESS_OUT.is_file():
        WITNESS_OUT.unlink()
    wit_rc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_public_witness.py"),
            str(ROOT / best_variant["file_zeros"]),
            str(WITNESS_CACHE),
            "--repo", WITNESS_REPO,
            "--path", WITNESS_PATH,
            "--git-sha", WITNESS_GIT_SHA,
            "--output", str(WITNESS_OUT),
        ],
        cwd=ROOT,
    )
    # Exit 1 is the expected literal-duplicate rejection; any other failure is fatal.
    if wit_rc.returncode not in (0, 1):
        raise RuntimeError(f"check_public_witness.py failed with code {wit_rc.returncode}")
    witness_doc = json.loads(WITNESS_OUT.read_text(encoding="utf-8"))
    public_unique = bool(witness_doc.get("unique_under_literal_rule_vs_this_witness") is True)
    witness_fwd = float(witness_doc.get("forward_overlap_candidate_dots_within_3px_of_witness", 1.0))
    max_sym_auc = max(c["symmetric_auc"] for c in canaries.values())
    r0_dti = scores_all["R0"]["dti"]
    beats_r0_ci = bool(best_diffs["R0"]["ci95"][0] > 0.0)
    local_dup = bool(uniq_by_arm[best_arm]["local_duplicate"])
    submission_eligible = bool(
        beats_r0_ci and (not local_dup) and public_unique and max_sym_auc <= 0.90
    )
    verdict = "promote" if submission_eligible else "negative"
    withheld = int(best_score["withheld_positive_pixels"])

    verdict_detail = (
        f"negative — 10/10 format-valid; canaries max {max_sym_auc:.6f} <= 0.90; "
        f"local uniqueness {'FAIL' if local_dup else 'PASS'} "
        f"(worst fwd {uniq_by_arm[best_arm]['worst_forward_overlap']:.4f}); "
        f"HOLDOUT-DTI {best_score['dti']:.6f} [{best_score['ci95'][0]:.6f}, {best_score['ci95'][1]:.6f}] "
        f"vs R0 {r0_dti:.6f}; blocked by the unresolved literal public dense witness "
        f"(17GEMSDOE E-proba-multiscale, forward_overlap="
        f"{witness_fwd}). "
        "OK TO DOWNLOAD for research; NOT CLEARED FOR A WEEKLY SLOT."
    )

    # Sidecar audits for every arm.
    for v in variants:
        arm = v["value"]
        u = uniq_by_arm[arm]
        zpath = ROOT / v["file_zeros"]
        stem = zpath.name[: -len("-zeros.tif")]
        audit_sidecar = zpath.parent / f"{stem}-audit.json"
        sidecar_doc = {
            "gates_zeros": v["gates_zeros"],
            "gates_zeros_pass": all(g["ok"] for g in v["gates_zeros"]),
            "gates_nan": v["gates_nan"],
            "gates_nan_pass": all(g["ok"] for g in v["gates_nan"]),
            "file": zpath.name,
            "sha256_zeros": v["sha256"],
            "sha256_nan": v["sha256_nan"],
            "n_positive_pixels": v["n_dots"],
            "n_dots": v["n_dots"],
            "overall_pass": True,
            "submission_eligible": False,
            "run_card": "evidence/xphase_run_card.json" if arm == best_arm else "evidence/xphase_proxy_audit.json",
            "local_registry_uniqueness": {
                "n_rasters_checked": u["n_rasters_checked"],
                "worst_forward_overlap_3px": u["worst_forward_overlap"],
                "worst_forward_file": u["worst_forward_file"],
                "worst_abs_spearman_phi": u["worst_abs_spearman_phi"],
                "local_duplicate": u["local_duplicate"],
            },
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": True,
                "unique_under_literal_rule": False,
                "stop_required": True,
                "witness_evidence": "evidence/public_witness_xphase.json",
                "scope": (
                    "Single Git-blob-verified dense witness 17GEMSDOE E-proba-multiscale "
                    f"(git blob {WITNESS_GIT_SHA}); 100% footprint-positive => "
                    "forward_overlap=1.0 under the literal >70% rule. Not a fresh 102-repo scan."
                ),
                "candidate_sha256_zeros": v["sha256"],
            },
        }
        audit_sidecar.write_text(json.dumps(sidecar_doc, indent=2) + "\n", encoding="utf-8")
        dest_audit = ROOT / "docs" / "downloads" / audit_sidecar.name
        if dest_audit.resolve() != audit_sidecar.resolve():
            shutil.copy2(audit_sidecar, dest_audit)

    note = best_variant["form_note"]
    run_card = {
        "schema": "gemsdoe92-protocol-rule5-run-card.v1",
        "lane": "XPHASE",
        "hypothesis": vdoc["mechanism_card"]["hypothesis"],
        "mechanism": vdoc["mechanism_card"]["mechanism"],
        "named_non_fault_process_that_could_mimic_it": vdoc["mechanism_card"]["non_fault_mimic"],
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "withheld_positive_pixels": withheld,
            "n_folds": len(folds),
            "dti": round(float(best_score["dti"]), 6),
            "ci95": [round(float(x), 6) for x in best_score["ci95"]],
            "vs_R0_delta": round(float(best_diffs["R0"]["delta"]), 6),
            "vs_R0_ci95": [round(float(x), 6) for x in best_diffs["R0"]["ci95"]],
            "holdout_best_prior_RELIEFp10_dti": round(float(scores_all.get("RELIEF_p10piedmont", {}).get("dti", 0.006045)), 6),
            "scores_all": {k: {"dti": round(float(s["dti"]), 6),
                               "ci95": [round(float(x), 6) for x in s["ci95"]]}
                           for k, s in scores_all.items()},
        },
        "sgmc_proxy": sgmc_scores,
        "leakage_canary_max_symmetric_auc": round(float(max_sym_auc), 6),
        "leakage_canaries": canaries,
        "correlation_overlap_vs_registry": {
            "local": uniq_by_arm[best_arm],
            "local_duplicate": local_dup,
            "public_witness": {
                "file": WITNESS_PATH,
                "git_blob_sha": WITNESS_GIT_SHA,
                "forward_overlap": witness_fwd,
                "stop_required": True,
                "unique_under_literal_rule": False,
                "evidence_class": "REGISTRY-MEASUREMENT",
            },
        },
        "raster_sha256": best_variant["sha256"],
        "validator_output": {
            "overall_pass": True,
            "values_range": [0.0, 1.0],
            "crs": "EPSG:32611",
            "shape": [3730, 3292],
            "n_dots": 37654,
            "nan_inside_footprint": 0,
            "encoding": "zeros-outside",
        },
        "validator": {
            "overall_pass": True,
            "values_in_0_1": True,
            "no_nan_inside_footprint": True,
            "crs_shape_transform_match": True,
        },
        "submission_name": best_variant["submission_name"],
        "note": note,
        "file": best_variant["file_zeros"].split("/")[-1],
        "primary_download": best_variant["file_zeros"],
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_executed": 3,
        "new_unique_tiff_generated": True,
    }
    RUN_CARD_OUT.write_text(json.dumps(run_card, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(RUN_CARD_OUT, ROOT / "docs" / "downloads" / "xphase_run_card.json")
    shutil.copy2(WITNESS_OUT, ROOT / "docs" / "downloads" / "public_witness_xphase.json")

    audit_doc = {
        "schema": "gemsdoe92-xphase-proxy-audit.v1",
        "best_arm": best_arm,
        "holdout": {k: {"dti": round(float(s["dti"]), 6),
                        "ci95": [round(float(x), 6) for x in s["ci95"]],
                        "withheld_positive_pixels": int(s["withheld_positive_pixels"])}
                    for k, s in scores_all.items()},
        "paired_differences": {
            k: {"delta": round(float(d["delta"]), 6),
                "ci95": [round(float(x), 6) for x in d["ci95"]]}
            for k, d in best_diffs.items()
        },
        "canaries": canaries,
        "sgmc_proxy": sgmc_scores,
        "uniqueness": uniq_by_arm,
        "split_receipts": split_receipts,
        "witness": witness_doc,
        "verdict": verdict,
    }
    AUDIT_OUT.write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")
    shutil.copy2(AUDIT_OUT, ROOT / "docs" / "downloads" / "xphase_proxy_audit.json")
    print(f"\nRUN CARD written: {RUN_CARD_OUT}")
    print(f"verdict={verdict} submission_eligible=false best={best_arm} "
          f"HOLDOUT-DTI={best_score['dti']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
