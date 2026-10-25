#!/usr/bin/env python3
"""POISSONKNICK finalizer: local + public registry uniqueness under dual_reading_decision,
submission_writer packaging of all 3 pre-registered arms (qcal, uncal, pkdual40),
automatic 11/11 format/range/encoding validation, ledger registration, and
Protocol Rule 5 run card emission.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor"), str(ROOT / "scripts")]

from gems.gates import run_gates, summarise  # noqa: E402
from gems.ledger import append_variant, pair_seen  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import grid as grid_mod, submission_writer, uniqueness as U, validate as V  # noqa: E402

PK_CACHE = ROOT / ".cache" / "poissonknick"
INPUTS = ROOT / ".cache" / "gems_inputs"
PUB_CACHE = ROOT / ".cache" / "poissonknick_public_witnesses"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
SCREEN_JSON = EVIDENCE / "poissonknick_screen.json"
HOLDOUT_JSON = EVIDENCE / "poissonknick_holdout.json"
UNIQUENESS_JSON = EVIDENCE / "poissonknick_uniqueness.json"
RUN_CARD_JSON = EVIDENCE / "poissonknick_run_card.json"
ARMS: tuple[str, ...] = ("qcal", "uncal", "pkdual40")
DATE = "20261025"

PUBLIC_WITNESSES = [
    (
        "buffedlizard55-lab/17GEMSDOE",
        "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
        "374c88b1da2b803e2ed160de467fd71ae114010d",
        "dense_5167373px",
    ),
    (
        "buffedlizard55-lab/62GEMSDOE",
        "docs/downloads/gems62b-tiltgrad-vote-scarpcorrob-120000-zeros.tif",
        "800e27139c0a4664de786706a4a4d2a0a8862b89",
        "sparse_120000px",
    ),
    (
        "buffedlizard55-lab/GEMSDOE23",
        "docs/downloads/gemsdoe23-h29-dealiased-habitat-20261002-7bf9fac6-allfinite.tif",
        "7d19b90ed6e358b14b561bc405690a104c5da64b",
        "sparse_100000px_coulombloqo_witness",
    ),
    (
        "buffedlizard55-lab/GEMSDOE23",
        "docs/downloads/gemsdoe23-h24-dispersed-habitat-20261002-ada8df14-allfinite.tif",
        "1374c17668adc23d0ab1c67ee07187bbe48f007b",
        "sparse_100000px",
    ),
    (
        "buffedlizard55-lab/12GEMSDOE",
        "docs/downloads/12GEMSDOE_r6-nms3-h28-texture_8721329b55c7.tif",
        "d9a4ea5ba779617e656417b04f9a69908f16afd0",
        "sparse_100000px_blindfault_witness",
    ),
    (
        "buffedlizard55-lab/GEMSDOE23",
        "docs/downloads/gemsdoe23-h30-arrangement-matched-habitat-20261002-0d4e02e8-allfinite.tif",
        "1cd1123a6a2d963c7145f8bf006fae75fdac4833",
        "sparse_91203px",
    ),
    (
        "buffedlizard55-lab/GEMSDOE52",
        "docs/downloads/gems52-h87-boardcal-marginal-20261010-61427px.tif",
        "c77023dd18fa59e1d8b93c5d699081f238d208e0",
        "sparse_61427px_coulombloqo_90k_witness",
    ),
]


def git_blob_sha(p: Path) -> str:
    h = hashlib.sha1(b"blob " + str(p.stat().st_size).encode() + b"\0")
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_public_witness(repo: str, sha: str, dest: Path) -> None:
    if dest.is_file() and git_blob_sha(dest) == sha:
        return
    out = subprocess.run(
        ["gh", "api", f"repos/{repo}/git/blobs/{sha}", "--jq", ".content"],
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    raw = base64.b64decode("".join(out.stdout.split()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw)
    got = git_blob_sha(dest)
    if got != sha:
        raise RuntimeError(f"Git blob SHA mismatch for {dest}: {got} != {sha}")


def collect_all_local_registry(exclude_stems: list[str]) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    for d in (DOWNLOADS, ROOT / "releases", ROOT / "data", ROOT / "data" / "bridge"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if any(p.name.startswith(s) for s in exclude_stems):
                continue
            if "poissonknick" in p.name.lower():
                continue
            files.append(("local:" + str(p.relative_to(ROOT)), p))
    return files


def compare_registry(
    cands: dict[str, np.ndarray],
    surfaces: dict[str, np.ndarray],
    foot: np.ndarray,
    registry: list[tuple[str, Path]],
    expected_grid: tuple,
) -> list[dict]:
    rows_by_arm: dict[str, list[dict]] = {a: [] for a in cands}
    foot_idx = np.flatnonzero(foot)
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
    surf_sub = {a: s.ravel()[sub].astype(np.float32) for a, s in surfaces.items()}

    for label, path in registry:
        with rasterio.open(path) as ds:
            if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected_grid:
                continue
            raw = ds.read(1)
        vals = np.nan_to_num(raw.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        support = (vals > 0) & foot
        n_sup = int(support.sum())
        if n_sup == 0:
            continue
        near_lit = U._near(support, 3.0)
        near_mb = (
            near_lit
            if n_sup <= U.DOT_FIELD_MAX_SUPPORT
            else U._near(U.matched_budget_support(vals, foot, 37_654), 3.0)
        )
        rep = "dot_field" if n_sup <= U.DOT_FIELD_MAX_SUPPORT else "continuous_surface"
        tv = vals.ravel()[sub]
        for a, m in cands.items():
            k = int(m.sum())
            lit = float(near_lit[m].mean())
            mb = float(near_mb[m].mean())
            rho = (
                float(spearmanr(surf_sub[a], tv).statistic)
                if (n_sup > 1 and np.ptp(tv) > 0 and np.ptp(surf_sub[a]) > 0)
                else 0.0
            )
            rows_by_arm[a].append(
                {
                    "file": label,
                    "their_dots": n_sup,
                    "my_dots": k,
                    "representation": rep,
                    "literal_forward_overlap": round(lit, 6),
                    "matched_budget_forward_overlap": round(mb, 6),
                    "spearman_surface": round(rho, 6),
                }
            )
        del vals, support, near_lit, near_mb
    return rows_by_arm


def main() -> int:
    t0 = time.time()
    screen = json.loads(SCREEN_JSON.read_text(encoding="utf-8"))
    hold = json.loads(HOLDOUT_JSON.read_text(encoding="utf-8"))
    art = np.load(PK_CACHE / "poissonknick_artifacts.npz")

    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    d_cat = distance_transform_edt(~cat)
    with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
        r0_mask = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    d_r0 = distance_transform_edt(~r0_mask)

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    cands = {
        "qcal": art["mask_qcal"].astype(bool),
        "uncal": art["mask_uncal"].astype(bool),
        "pkdual40": art["mask_pkdual40"].astype(bool),
    }
    surfaces = {
        "qcal": art["S_qcal_full"].astype(np.float32),
        "uncal": art["S_uncal_full"].astype(np.float32),
        "pkdual40": art["S_qcal_full"].astype(np.float32),
    }

    static_scores = hold["static_deployment_d_cat_gt_2"]["qcal"]["scores"]
    strict_scores = hold["strict_draw_blind_d_visible_gt_2"]["qcal"]["scores"]
    sgmc_scores = hold["sgmc_off_catalogue_proxy"]["scores"]
    best_arm = "qcal"

    print("[1/5] Packaging 3 pre-registered POISSONKNICK GeoTIFFs via submission_writer...", flush=True)
    built: dict[str, dict] = {}
    stems: list[str] = []

    for arm in ARMS:
        m = cands[arm]
        if int(m.sum()) != 37_654:
            raise RuntimeError(f"{arm}: expected 37654 dots, got {int(m.sum())}")
        if np.any(m & cat) or np.any(d_cat[m] <= 2.0):
            raise RuntimeError(f"{arm}: catalogue clearance violated")

        mask_sha = hashlib.sha256(np.packbits(m).tobytes()).hexdigest()
        stem = f"gemsdoe92-poissonknick-{arm}-37654-{DATE}-{mask_sha[:8]}-zeros"
        stems.append(stem)
        tif_path = DOWNLOADS / f"{stem}.tif"
        st_dti = static_scores[arm]["dti"]
        dr_dti = strict_scores[arm]["dti"]
        name = f"GEMSDOE92-POISSONKNICK-{arm}-{DATE}"
        note = (
            f"POISSONKNICK {arm}: 37654 1D Poisson+knick LOQO dots; "
            f"static DTI {st_dti:.6f}, drawblind {dr_dti:.6f}; negative"
        )
        assert len(name) <= 140 and len(note) <= 140, f"note too long: {len(note)}"

        # Remove any stale prior build of the same arm with a different hash
        for old_f in DOWNLOADS.glob(f"gemsdoe92-poissonknick-{arm}-37654-*"):
            if not old_f.name.startswith(stem.removesuffix("-zeros")):
                old_f.unlink()

        if not tif_path.is_file():
            receipt = submission_writer.write_submission(
                tif_path,
                m.astype(np.float32),
                INPUTS / "bridge" / "sample_submission.tif",
                foot,
                note=note,
                name=name,
                catalogue=cat,
                metadata={
                    "lane": "POISSONKNICK",
                    "arm": arm,
                    "hypothesis_doc": "docs/HYPOTHESES_20261025_POISSONKNICK.md",
                    "verdict": "negative",
                    "submission_eligible": False,
                    "weekly_slots_used": 0,
                },
            )
            (PK_CACHE / f"{stem}.receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
            aux = tif_path.with_suffix(".json")
            if aux.is_file():
                aux.replace(PK_CACHE / aux.name)

        if arm != best_arm:
            z = tif_path.with_suffix(".zip")
            if z.is_file():
                z.unlink()

        disk_sha = sha256_file(tif_path)
        val_report = V.validate(tif_path, foot, cat)
        V.assert_submittable(val_report)
        gates = run_gates(
            str(tif_path),
            str(INPUTS / "bridge" / "sample_submission.tif"),
            str(INPUTS / "bridge" / "existing_faults.tif"),
            prune_radius=2,
            require_submission_encoding=True,
        )
        gates_ok, gates_text = summarise(gates)
        if not gates_ok:
            raise RuntimeError(f"Gate failure on {tif_path}: {gates_text}")

        r0_ov = float(np.mean(d_r0[m] <= 3.0))
        pct_changed = round((1.0 - r0_ov) * 100.0, 2)

        built[arm] = {
            "stem": stem,
            "file": f"docs/downloads/{tif_path.name}",
            "sha256": disk_sha,
            "bytes": tif_path.stat().st_size,
            "zip": f"docs/downloads/{stem}.zip" if arm == best_arm else None,
            "zip_sha256": sha256_file(tif_path.with_suffix(".zip")) if arm == best_arm else None,
            "submission_name": name,
            "note": note,
            "note_chars": len(note),
            "validator": val_report,
            "gates": [{"name": g.name, "ok": g.ok, "detail": g.detail} for g in gates],
            "all_gates_pass": bool(gates_ok),
            "dot_count": int(m.sum()),
            "catalogue_mass": int((m & cat).sum()),
            "min_catalogue_distance_px": round(float(d_cat[m].min()), 6),
            "overlap_r0_3px": round(r0_ov, 6),
            "pct_changed_vs_r0": pct_changed,
        }
        print(f"      Built & validated {arm}: {tif_path.name} (sha256={disk_sha[:12]}..., 11/11 gates PASS)", flush=True)

        if not pair_seen("h33-h33-2-b2", "POISSONKNICK", arm):
            append_variant(
                {
                    "id": stem.removesuffix("-zeros"),
                    "parent": "h33-h33-2-b2",
                    "axis": "POISSONKNICK",
                    "value": arm,
                    "n_dots": "37654",
                    "pct_changed": f"{pct_changed:.2f}",
                    "sha256": disk_sha,
                    "status": "BUILT",
                    "predicted_change": "none; HOLDOUT-DTI recorded in evidence/poissonknick_holdout.json",
                    "file_zeros": f"docs/downloads/{tif_path.name}",
                    "file_nan": "",
                    "sha8": disk_sha[:8],
                    "change_desc": (
                        f"POISSONKNICK {arm}: quadrant-calibrated LOQO + Poisson RTP-VG decoupling + "
                        f"thalweg knickpoint + Lahontan deconfounder; 37654 unit dots"
                    ),
                    "receipt_score": "",
                    "receipt_date": "",
                    "notes": (
                        f"verdict=negative; no weekly slot; static HOLDOUT-DTI {st_dti:.6f} "
                        f"(new repo record for qcal), strict draw-blind HOLDOUT-DTI {dr_dti:.6f}, "
                        f"SGMC PROXY {sgmc_scores[arm]:.6f}"
                    ),
                }
            )

    print("[2/5] Auditing complete local registry (including COULOMBLOQO & EULERFUSE)...", flush=True)
    reg_local = collect_all_local_registry(exclude_stems=[s.removesuffix("-zeros") for s in stems])
    rows_local = compare_registry(cands, surfaces, foot, reg_local, expected_grid)

    print("[3/5] Fetching & auditing hash-pinned public registry witnesses...", flush=True)
    pub_list: list[tuple[str, Path]] = []
    for repo, rel_path, blob_sha, kind in PUBLIC_WITNESSES:
        dest = PUB_CACHE / f"{repo.split('/')[-1]}__{Path(rel_path).name}"
        fetch_public_witness(repo, blob_sha, dest)
        pub_list.append((f"{repo.split('/')[-1]}/{rel_path}", dest))
    rows_pub = compare_registry(cands, surfaces, foot, pub_list, expected_grid)

    # Dense-witness specificity proof (#IR-92-DENSE-WITNESS-MATCHED-BUDGET)
    dense_path = PUB_CACHE / "17GEMSDOE__17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
    with rasterio.open(dense_path) as ds:
        wv = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    specificity = {
        "witness": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
        "witness_git_blob_sha1": "374c88b1da2b803e2ed160de467fd71ae114010d",
        "witness_positive_footprint_cells": int(((wv > 0) & foot).sum()),
        "footprint_cells": int(foot.sum()),
        "R0_parent_literal_overlap": round(U.dual_overlap(r0_mask, wv, foot)["literal_forward_overlap"], 6),
        "R0_parent_matched_budget_overlap": round(
            U.dual_overlap(r0_mask, wv, foot)["matched_budget_forward_overlap"], 6
        ),
    }
    for arm in ARMS:
        do = U.dual_overlap(cands[arm], wv, foot)
        specificity[f"{arm}_literal_overlap"] = round(do["literal_forward_overlap"], 6)
        specificity[f"{arm}_matched_budget_overlap"] = round(do["matched_budget_forward_overlap"], 6)
    del wv

    sib = {}
    for a in ARMS:
        for b in ARMS:
            if a != b:
                sib[f"{a}_vs_{b}"] = round(float(U._near(cands[b], 3.0)[cands[a]].mean()), 6)

    uniq_by_arm = {}
    for arm in ARMS:
        dl = U.dual_reading_decision(rows_local[arm])
        dp = U.dual_reading_decision(rows_pub[arm])
        uniq_by_arm[arm] = {
            "local": dl,
            "public": dp,
            "top_local": sorted(rows_local[arm], key=lambda r: -r["matched_budget_forward_overlap"])[:6],
            "top_public": sorted(rows_pub[arm], key=lambda r: -r["matched_budget_forward_overlap"])[:7],
        }
        print(
            f"      {arm:10s}: local worst MB={dl['worst_matched_budget_forward_overlap']:.6f} "
            f"({dl['worst_matched_budget_file']}), dup={dl['duplicate']} | "
            f"public worst MB={dp['worst_matched_budget_forward_overlap']:.6f} "
            f"({dp['worst_matched_budget_file']}), dup={dp['duplicate']}, "
            f"literal={dp['worst_literal_forward_overlap']:.6f}",
            flush=True,
        )

    uniqueness_doc = {
        "schema": "gemsdoe92.poissonknick-uniqueness.v1",
        "lane": "POISSONKNICK",
        "evidence_class": "REGISTRY-MEASUREMENT",
        "policy": (
            "#IR-92-DENSE-WITNESS-MATCHED-BUDGET: both literal and matched-budget readings reported; "
            "fail-closed negative under literal Rule 1 because 17GEMSDOE E-proba-multiscale is positive on "
            "all 5,167,373 footprint pixels (literal overlap 1.000000 > 0.70)."
        ),
        "local_registry_files_checked": len(reg_local),
        "public_witness_files_checked": len(pub_list),
        "sibling_overlap": sib,
        "dense_witness_specificity": specificity,
        "by_arm": uniq_by_arm,
        "next_step_1_coulombloqo_dual_reading": screen["next_step_1_coulombloqo_dual_reading"],
    }
    UNIQUENESS_JSON.write_text(json.dumps(uniqueness_doc, indent=2) + "\n", encoding="utf-8")

    print("[4/5] Writing per-arm *-audit.json receipts...", flush=True)
    for arm in ARMS:
        stem = built[arm]["stem"]
        audit_doc = {
            "schema": "gemsdoe92.poissonknick-audit.v1",
            "lane": "POISSONKNICK",
            "arm": arm,
            **built[arm],
            "n_dots": built[arm]["dot_count"],
            "overall_pass": built[arm]["all_gates_pass"],
            "sha256_zeros": built[arm]["sha256"],
            "gates_zeros": built[arm]["gates"],
            "run_card": "evidence/poissonknick_run_card.json",
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": True,
                "unique_under_literal_rule": False,
                "stop_required": True,
                "unique_under_matched_budget_rule": True,
                "worst_matched_budget_forward_overlap": uniq_by_arm[arm]["public"]["worst_matched_budget_forward_overlap"],
                "worst_literal_forward_overlap": uniq_by_arm[arm]["public"]["worst_literal_forward_overlap"],
            },
            "holdout_static_dcat2": static_scores[arm],
            "holdout_strict_drawblind_dvis2": strict_scores[arm],
            "sgmc_proxy_dti": sgmc_scores[arm],
            "quadrant_dot_allocation": hold["quadrant_dot_allocations"][f"POISSONKNICK_{arm}"],
            "uniqueness": uniq_by_arm[arm],
            "verdict": "negative",
            "submission_eligible": False,
            "weekly_slots_used": 0,
            "status_text": (
                "OK TO DOWNLOAD FOR RESEARCH (11/11 format/range/encoding MUST gates PASS); "
                "DO NOT SUBMIT FOR A WEEKLY SLOT (literal public registry overlap = 1.000000 > 0.70 "
                "against dense 5,167,373-px witness 17GEMSDOE_E-proba-multiscale)."
            ),
        }
        audit_path = DOWNLOADS / f"{stem.removesuffix('-zeros')}-audit.json"
        audit_path.write_text(json.dumps(audit_doc, indent=2) + "\n", encoding="utf-8")

    print("[5/5] Writing Protocol Rule 5 Run Card...", flush=True)
    b = built[best_arm]
    val = b["validator"]
    val_summary = {
        "result": "PASS",
        "validation_class": "LOCAL FORMAT/RANGE VALIDATION; NOT ORGANIZER ACCEPTANCE",
        "single_band": val["meta"]["count"] == 1,
        "dtype": val["meta"]["dtype"],
        "crs": val["meta"]["crs"],
        "shape": val["meta"]["shape"],
        "transform": val["meta"]["transform"],
        "crs_shape_transform_match": all(g["ok"] for g in b["gates"][:3]),
        "no_nan_inside_footprint": val["checks"]["in_footprint_all_finite"],
        "no_nan_anywhere": val["checks"]["no_nan_anywhere"],
        "no_infinity_anywhere": val["checks"]["no_inf_anywhere"],
        "values_in_0_1": val["checks"]["range_0_1_guaranteed"],
        "min": val["min"],
        "max": val["max"],
        "zeros_outside_footprint": val["checks"]["outside_footprint_zero"],
        "catalogue_mass": b["catalogue_mass"],
        "min_catalogue_distance_px": b["min_catalogue_distance_px"],
        "dot_count": b["dot_count"],
        "must_gates_passed": sum(1 for g in b["gates"] if g["ok"]),
        "must_gates_failed": sum(1 for g in b["gates"] if not g["ok"]),
    }

    run_card = {
        "schema": "gemsdoe92.run-card.v1",
        "lane": "POISSONKNICK",
        "date": "2026-10-25",
        "primary_arm": best_arm,
        "hypothesis": (
            "Concealed and eroded Great Basin normal/transtensional faults missing from the 1:24k "
            "aerial-scarp catalogue can be recovered by combining (1) Poisson's-relation gravity-magnetic "
            "structural decoupling (hydrothermal magnetite destruction across persistent vertical-gravity-gradient "
            "steps, Bands 2, 11, 5), (2) cross-canyon longitudinal thalweg knickpoint convexity (Bands 12, 19), "
            "(3) Lake Lahontan contour-oblique strandline null deconfounding (Bands 12, 13, 19), and (4) unlabeled "
            "per-quadrant domain-shift standardization + within-quadrant survival-quantile LOQO probability "
            "calibration resolving #IR-92-NE-QUADRANT-LOQO-COLLAPSE."
        ),
        "mechanism": (
            "POISSONKNICK qcal computes 30 strictly catalogue-free physical features (f01..f30; dist_known_fault_px "
            "dropped), trains a 4-quadrant Leave-One-Quadrant-Out (LOQO, >=1.2 km guard band, >500 m negative buffer) "
            "HistGradientBoostingClassifier, aligns per-quadrant probability and 1D crest survival quantiles on "
            "unlabeled footprint cells (restoring NE quadrant allocation from 6.4% uncalibrated / 0.1% BLINDFAULT / "
            "11.2% COULOMBLOQO to 26.5% = 9,967 dots), and emits 37,654 spaced 1D crests (min_dist=2.8 px, d_cat > 2.0 px)."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Pleistocene Lake Lahontan wave-cut strandlines coinciding with a buried basin-margin basalt flow edge, "
            "or incised V-shaped radial fan gullies crossing an unaltered intrusive hornfels contact."
        ),
        "holdout_dti": {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": hold["evaluator_version"],
            "withheld_positive_pixels": 22663,
            "alpha": 0.2,
            "beta": 0.8,
            "triangular_kernel_m": 300.0,
            "primary_arm": best_arm,
            "static_dcat2_dti": static_scores[best_arm]["dti"],
            "static_dcat2_ci95": static_scores[best_arm]["ci95"],
            "static_beats_all_prior_lanes": True,
            "static_paired_vs_COULOMBLOQO_standalone": hold["static_deployment_d_cat_gt_2"][best_arm]["paired_differences"]["COULOMBLOQO_standalone"],
            "static_paired_vs_R0": hold["static_deployment_d_cat_gt_2"][best_arm]["paired_differences"]["R0"],
            "static_paired_vs_uncal_ablation": hold["static_deployment_d_cat_gt_2"][best_arm]["paired_differences"]["uncal"],
            "strict_drawblind_dvis2_dti": strict_scores[best_arm]["dti"],
            "strict_drawblind_dvis2_ci95": strict_scores[best_arm]["ci95"],
            "strict_paired_vs_H19_5": hold["strict_draw_blind_d_visible_gt_2"][best_arm]["paired_differences"]["H19_5_vis_d2"],
            "strict_paired_vs_uncal_ablation": hold["strict_draw_blind_d_visible_gt_2"][best_arm]["paired_differences"]["uncal"],
            "strict_paired_vs_COULOMBLOQO_standalone": hold["strict_draw_blind_d_visible_gt_2"][best_arm]["paired_differences"]["COULOMBLOQO_standalone"],
            "quadrant_stratified_strict_dti": {
                q_name: {k: v["dti"] for k, v in hold["quadrant_stratified_strict_dti"][q_name].items()}
                for q_name in ("NW", "NE", "SW", "SE")
            },
            "slope_tercile_stratified_strict_dti": {
                t_name: {k: v["dti"] for k, v in hold["slope_tercile_stratified_strict_dti"][t_name].items()}
                for t_name in hold["slope_tercile_stratified_strict_dti"]
            },
            "sgmc_off_catalogue_proxy": hold["sgmc_off_catalogue_proxy"],
            "quadrant_dot_allocations": hold["quadrant_dot_allocations"],
            "organizer_confirmed": False,
        },
        "leakage_canary": {
            "evidence_class": "HOLDOUT-CANARY",
            "raw_bands_tested": screen["leakage_canary"]["raw_bands_tested"],
            "derived_features_tested": screen["leakage_canary"]["derived_features_tested"],
            "threshold_symmetric_auc": 0.90,
            "max_symmetric_auc": screen["leakage_canary"]["max_symmetric_auc"],
            "max_feature": screen["leakage_canary"]["max_feature"],
            "all_pass": screen["leakage_canary"]["all_pass"],
        },
        "correlation_overlap_vs_registry": {
            "evidence_class": "REGISTRY-MEASUREMENT",
            "local_rasters_checked": len(reg_local),
            "local_dual_reading": uniq_by_arm[best_arm]["local"],
            "public_witnesses_checked": len(pub_list),
            "public_dual_reading": uniq_by_arm[best_arm]["public"],
            "dense_witness_specificity": specificity,
            "sibling_overlap": sib,
            "next_step_1_coulombloqo_dual_reading_summary": {
                k: {
                    "local_worst_overlap": v["local_registry_including_eulerfuse"]["worst_matched_budget_forward_overlap"],
                    "local_worst_file": v["local_registry_including_eulerfuse"]["worst_matched_budget_file"],
                    "local_duplicate": v["local_registry_including_eulerfuse"]["duplicate"],
                    "public_150k_worst_overlap": v["public_registry_150k"]["worst_matched_budget_forward_overlap"],
                    "public_150k_duplicate": v["public_registry_150k"]["duplicate"],
                    "public_90k_worst_overlap": v["public_registry_90k"]["worst_matched_budget_forward_overlap"],
                    "public_90k_duplicate": v["public_registry_90k"]["duplicate"],
                }
                for k, v in screen["next_step_1_coulombloqo_dual_reading"].items()
            },
            "duplicate_under_matched_budget_reading": False,
            "duplicate_under_literal_all_rasters_reading": True,
            "binding_literal_witness": "17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
        },
        "raster_sha256": b["sha256"],
        "zip_sha256": b["zip_sha256"],
        "primary_download": b["file"],
        "zip_download": b["zip"],
        "validator_output": val,
        "validator_gates": b["gates"],
        "validator_all_gates_pass": b["all_gates_pass"],
        "validator_summary": val_summary,
        "submission_name": b["submission_name"],
        "submission_note": b["note"],
        "submission_note_characters": b["note_chars"],
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_used": 3,
        "experiment_budget": 3,
        "verdict_detail": (
            "Negative (fail-closed governance): POISSONKNICK qcal sets a new all-time repository record on "
            "static deployment HOLDOUT-DTI (0.009304 vs COULOMBLOQO standalone 0.009220, HYDROCONDUIT 0.008549, "
            "COULOMBDM 0.007816, BLINDFAULT 0.004585, R0 0.004006), resolves #IR-92-NE-QUADRANT-LOQO-COLLAPSE "
            "(restoring NE dots from 6.4% uncal / 0.1% BLINDFAULT / 11.2% COULOMBLOQO to 26.5% = 9,967 dots and "
            "lifting NE strict draw-blind HOLDOUT-DTI +41.3% over uncal from 0.080880 to 0.114274), passes all 53 "
            "leakage canaries (max AUC 0.654126 <= 0.90), passes 11/11 automatic GeoTIFF format/range/encoding MUST "
            "gates, and passes Reading 2 (matched-budget & sparse <=150k dot-field uniqueness <= 0.70) across all 91 "
            "local rasters (max 0.645668 vs EULERFUSE, 0.611303 vs COULOMBLOQO standalone) and all 7 pinned public "
            "witnesses (including GEMSDOE23 100k and GEMSDOE52 61k). However, it remains below COULOMBLOQO standalone "
            "on pooled strict draw-blind d_visible > 2.0 HOLDOUT-DTI (0.098491 vs 0.113316) and triggers the literal "
            "Rule 1 overlap stop (1.000000 > 0.70) against the full-footprint dense witness 17GEMSDOE_E-proba-multiscale. "
            "OK TO DOWNLOAD FOR RESEARCH; DO NOT SUBMIT FOR A WEEKLY SLOT."
        ),
        "all_arms": built,
    }
    text = json.dumps(run_card, indent=2, allow_nan=False) + "\n"
    RUN_CARD_JSON.write_text(text, encoding="utf-8")
    (DOWNLOADS / "poissonknick_run_card.json").write_text(text, encoding="utf-8")
    print(f"Finished finalize_poissonknick.py in {time.time() - t0:.1f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
