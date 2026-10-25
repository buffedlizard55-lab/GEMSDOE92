#!/usr/bin/env python3
"""Run the pre-registered LISTRICDIP lane and write a zeros-outside GeoTIFF.

Uses vendor/gems57/evaluate_holdout.py and vendor/gems57/submission_writer.py.
Does not fork either. Does not contact drivendata.org. Catalogue pixels are
never features. A format-valid file is not a weekly-slot clearance.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.breakline import spaced_top_mask  # noqa: E402
from gems.gates import run_gates  # noqa: E402
from gems.ledger import append_variant  # noqa: E402
from gems.listricdip import ANTI_PX, antithetic_surface, updip_surface  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout  # noqa: E402
from gems57.metric import dti_exact  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gems57.uniqueness import dot_overlap, surface_rho  # noqa: E402

FEATURES = ROOT / ".cache" / "gems_inputs" / "training_features.tif"
SAMPLE = ROOT / "data" / "bridge" / "sample_submission.tif"
LABELS = ROOT / "data" / "bridge" / "labels.tif"
SGMC = ROOT / ".cache" / "gems_inputs" / "external" / "derived_sgmc_faults_100m_u8.tif"
R0 = ROOT / "data" / "parent_R0_zeros.tif"
WITNESS_CACHE = ROOT / ".cache" / "witness_17GEMSDOE.tif"
WITNESS_COMMIT = "6fc71d19d49dca4960d5434bd81b6dd06fcc030a"
WITNESS_PATH = "docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif"
WITNESS_GIT_SHA = "374c88b1da2b803e2ed160de467fd71ae114010d"
N_DOTS = 37654
STAMP = "20261025T190000Z"

ARMS = (
    {"value": "updip50", "kind": "updip", "anti_px": None},
    {"value": "anti22", "kind": "anti", "anti_px": ANTI_PX[0]},
    {"value": "anti35", "kind": "anti", "anti_px": ANTI_PX[1]},
)


def _finite(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=np.float32)
    return np.isfinite(a) & (a > -1.0e30) & (a < 1.0e30)


def symmetric_auc(score: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> float:
    s = np.asarray(score, dtype=np.float64)
    y = np.asarray(y, dtype=bool)
    pos, neg = s[y], s[~y]
    if pos.size < 20 or neg.size < 20:
        return float("nan")
    if pos.size > 8000:
        pos = rng.choice(pos, 8000, replace=False)
    if neg.size > 8000:
        neg = rng.choice(neg, 8000, replace=False)
    order = np.concatenate([pos, neg])
    ranks = rankdata(order, method="average")
    npos, nneg = pos.size, neg.size
    auc = (ranks[:npos].sum() - npos * (npos + 1) / 2.0) / (npos * nneg)
    return float(max(auc, 1.0 - auc))


def load_mask(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        if ds.shape != foot.shape:
            raise ValueError(f"{path} shape {ds.shape} != {foot.shape}")
        return (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot


def local_rasters() -> list[tuple[str, Path]]:
    found = []
    for folder in (ROOT / "docs" / "downloads", ROOT / "releases", ROOT / "data"):
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*.tif")):
            found.append((str(path.relative_to(ROOT)), path))
    # Stable de-duplication by resolved path.
    uniq, seen = [], set()
    for label, path in found:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        uniq.append((label, path))
    return uniq


def screen_support(support: np.ndarray, surface: np.ndarray, foot: np.ndarray, rasters) -> dict:
    rows = []
    mine = support & foot
    for i, (label, path) in enumerate(rasters, start=1):
        if i == 1 or i % 25 == 0:
            print(f"  registry {i}/{len(rasters)}", flush=True)
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or ds.shape != foot.shape:
                    continue
                raw = ds.read(1)
        except Exception as exc:  # noqa: BLE001 — inventory gaps are recorded, not ignored
            rows.append({"registry_raster": label, "error": str(exc)})
            continue
        rho = surface_rho(np.where(foot, surface, 0.0), np.nan_to_num(raw, nan=0.0), foot)
        ov = dot_overlap(mine.astype(np.float32), raw, radius_px=3)
        spear = rho.get("spearman_full_footprint")
        spearman = float(spear) if spear is not None else float("nan")
        rows.append({
            "registry_raster": label,
            "their_positive_pixels": int(((np.nan_to_num(raw, nan=0.0) > 0) & foot).sum()),
            "forward_overlap_3px": ov,
            "spearman_full_footprint": None if not np.isfinite(spearman) else spearman,
        })
    checked = [r for r in rows if "error" not in r]
    if not checked:
        return {"duplicate": True, "reason": "no comparable registry rasters", "rows": rows}
    worst_ov = max(checked, key=lambda r: r["forward_overlap_3px"])
    rho_rows = [r for r in checked if r["spearman_full_footprint"] is not None]
    worst_rho = max(rho_rows, key=lambda r: abs(r["spearman_full_footprint"])) if rho_rows else None
    dup = bool(worst_ov["forward_overlap_3px"] > 0.70 or (
        worst_rho is not None and abs(worst_rho["spearman_full_footprint"]) > 0.90))
    return {
        "evidence_class": "REGISTRY-MEASUREMENT",
        "n_checked": len(checked),
        "n_errors": len(rows) - len(checked),
        "worst_forward_overlap": worst_ov["forward_overlap_3px"],
        "worst_forward_file": worst_ov["registry_raster"],
        "worst_abs_spearman": None if worst_rho is None else abs(worst_rho["spearman_full_footprint"]),
        "worst_spearman_file": None if worst_rho is None else worst_rho["registry_raster"],
        "duplicate": dup,
        "rows": checked,
    }


def ensure_witness() -> Path:
    if WITNESS_CACHE.is_file():
        return WITNESS_CACHE
    WITNESS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / ".cache") as td:
        co = Path(td) / "co"
        subprocess.run(["git", "clone", "--quiet", "--filter=blob:none", "--sparse",
                        "https://github.com/buffedlizard55-lab/17GEMSDOE.git", str(co)], check=True)
        subprocess.run(["git", "-C", str(co), "fetch", "--quiet", "--depth=1", "origin", WITNESS_COMMIT], check=True)
        subprocess.run(["git", "-C", str(co), "checkout", "--quiet", "--detach", WITNESS_COMMIT], check=True)
        subprocess.run(["git", "-C", str(co), "sparse-checkout", "set", "--no-cone", "/" + WITNESS_PATH], check=True)
        shutil.copy2(co / WITNESS_PATH, WITNESS_CACHE)
    return WITNESS_CACHE


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def place(surface: np.ndarray, cand: np.ndarray, n: int = N_DOTS, *, require_full: bool = True) -> np.ndarray:
    return spaced_top_mask(
        surface, cand, n, min_dist_px=3.2, cand_cap=1_500_000, require_full=require_full,
    )


def pooled(terms_by_arm: dict, candidate: str) -> dict:
    return evaluate_holdout.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=candidate)


def main() -> int:
    print("LISTRICDIP start", datetime.now(timezone.utc).isoformat(), flush=True)
    grid = grid_mod.load_grid(ROOT / "data" / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    with rasterio.open(FEATURES) as ds:
        if ds.count != 19 or ds.shape != foot.shape:
            raise SystemExit(f"training_features grid mismatch: count={ds.count} shape={ds.shape}")
        bands = {i: ds.read(i).astype(np.float32) for i in (12, 13, 15, 18, 19)}
    valid = foot.copy()
    for a in bands.values():
        valid &= _finite(a)
    print(f"valid pixels {int(valid.sum())} catalogue {int(cat.sum())}", flush=True)

    surfaces = {}
    print("building updip50", flush=True)
    surfaces["updip50"] = updip_surface(bands[15], bands[12], bands[19], bands[13], bands[18], valid)
    for name, px in (("anti22", ANTI_PX[0]), ("anti35", ANTI_PX[1])):
        print(f"building {name}", flush=True)
        surfaces[name] = antithetic_surface(bands[15], bands[12], bands[18], valid, anti_px=float(px))
    del bands

    d_cat = distance_transform_edt(~cat)
    deploy_cand = foot & valid & (d_cat > 2.0)
    rasters = local_rasters()
    print(f"local registry rasters {len(rasters)}", flush=True)

    pre_rows = {}
    stopped = []
    for arm in ARMS:
        name = arm["value"]
        surf = surfaces[name]["S_pct"]
        support = deploy_cand if arm["kind"] == "updip" else deploy_cand & (surfaces[name]["oppose"] > 0.3)
        rough = place(surf, support, require_full=False)
        pre = screen_support(rough, surf, foot, rasters)
        pre_rows[name] = {k: v for k, v in pre.items() if k != "rows"}
        pre_rows[name]["n_rough_dots"] = int(rough.sum())
        print(f"pre-placement {name}: overlap {pre_rows[name]['worst_forward_overlap']:.4f} "
              f"rho {pre_rows[name]['worst_abs_spearman']} duplicate {pre['duplicate']}", flush=True)
        if pre["duplicate"]:
            stopped.append(name)
        del rough
    if stopped:
        # Protocol: a colliding surface is a duplicate. Stop those arms.
        # Continue only with arms that have not drifted into another lane.
        print("DUPLICATE STOP on", stopped, flush=True)

    live = [a for a in ARMS if a["value"] not in stopped]
    if not live:
        card = {
            "schema": "gemsdoe92-run-card.v2",
            "lane": "LISTRICDIP",
            "verdict": "negative",
            "submission_eligible": False,
            "duplicate_stop": True,
            "stopped_arms": stopped,
            "preplacement": pre_rows,
            "experiments_executed": 3,
            "weekly_slots_used": 0,
            "raster_sha256": None,
            "hypothesis": "Listric cover-dependent up-dip offset and reversed-polarity antithetic.",
            "mechanism": "Stopped before final placement: pre-placement support duplicated a registry raster.",
            "named_non_fault_process_that_could_mimic_it": "Compaction monocline and contour-parallel bench.",
        }
        (ROOT / "evidence" / "listricdip_run_card.json").write_text(json.dumps(card, indent=2) + "\n")
        print("all arms duplicated; no TIFF written", flush=True)
        return 0

    # Leakage canaries on the buffered holdout, before trusting any arm.
    folds = []
    for seed in (20, 30):
        draw, _quad = holdout.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)
    rng = np.random.default_rng(520810)
    y_parts, idx_parts = [], []
    for fold in folds:
        pos = np.flatnonzero(fold["truth"] & foot)
        neg_pool = np.flatnonzero(fold["region"] & foot & ~cat)
        n = min(neg_pool.size, max(1, 2 * pos.size))
        neg = rng.choice(neg_pool, size=n, replace=False) if neg_pool.size > n else neg_pool
        idx_parts.extend((pos, neg))
        y_parts.extend((np.ones(pos.size, np.uint8), np.zeros(neg.size, np.uint8)))
    y = np.concatenate(y_parts)
    flat = np.concatenate(idx_parts)
    canaries = {}
    for name in [a["value"] for a in live]:
        for key in ("S_raw", "S_pct"):
            auc = symmetric_auc(surfaces[name][key].ravel()[flat], y.astype(bool), rng)
            canaries[f"{name}:{key}"] = auc
            print(f"canary {name}:{key} symmetric AUC {auc:.4f}", flush=True)
            if np.isfinite(auc) and auc > 0.90:
                raise SystemExit(f"LEAKAGE CANARY FAIL {name}:{key} AUC {auc}")

    controls = {"R0": load_mask(R0, foot)}
    for label, path in (
        ("H19-5", ROOT / "data" / "bridge" / "h19_5.tif"),
        ("COULOMBLOQO_standalone", ROOT / "docs/downloads/h33-h33-2-b2-COULOMBLOQOstandalone-20261024-e01d27af-zeros.tif"),
        ("KNICKLOQO_standalone", ROOT / "docs/downloads/h33-h33-2-b2-KNICKLOQOstandalone-20261025-d53d919f-zeros.tif"),
    ):
        if path.is_file():
            controls[label] = load_mask(path, foot)

    deployment = {}
    for arm in live:
        name = arm["value"]
        support = deploy_cand if arm["kind"] == "updip" else deploy_cand & (surfaces[name]["oppose"] > 0.3)
        deployment[name] = place(surfaces[name]["S_pct"], support, require_full=arm["kind"] == "updip")
        print(f"placed {name} {int(deployment[name].sum())} (requested {N_DOTS})", flush=True)

    print("static holdout", flush=True)
    static_terms = {}
    arms_static = {**{k: v.astype(np.float32) for k, v in controls.items()},
                   **{k: v.astype(np.float32) for k, v in deployment.items()}}
    for name, pred in arms_static.items():
        acc = None
        for fold in folds:
            _score, terms = evaluate_holdout.evaluate(pred, fold, foot)
            acc = terms if acc is None else acc + terms
        static_terms[name] = acc
    static_summary = {}
    for name in deployment:
        summary = pooled(static_terms, name)
        static_summary[name] = summary
        s = summary["scores"][name]
        print(f"  static {name} HOLDOUT-DTI {s['dti']:.6f} CI {s['ci95']}", flush=True)

    print("rule-2 re-placement", flush=True)
    rule2_terms = {name: None for name in list(deployment) + ["H19-5"]}
    h19 = controls.get("H19-5")
    # All four folds of one seed share the same visible catalogue. Place once per seed.
    placed_by_seed: dict[int, dict[str, np.ndarray]] = {}
    for fold in folds:
        seed = int(fold["receipt"]["seed"])
        if seed not in placed_by_seed:
            vis = np.asarray(fold["visible"], bool)
            d_vis = distance_transform_edt(~vis)
            cand = foot & valid & (d_vis > 2.0)
            preds = {}
            for arm in live:
                support = cand if arm["kind"] == "updip" else cand & (surfaces[arm["value"]]["oppose"] > 0.3)
                preds[arm["value"]] = place(
                    surfaces[arm["value"]]["S_pct"], support, require_full=arm["kind"] == "updip",
                )
            if h19 is not None:
                # Full skeleton. The evaluator masks visible faults pixel-exactly.
                preds["H19-5"] = h19.astype(np.float32)
            placed_by_seed[seed] = preds
            print(f"  rule2 placed seed {seed}", flush=True)
        for name, pred in placed_by_seed[seed].items():
            _score, terms = evaluate_holdout.evaluate(pred.astype(np.float32), fold, foot)
            rule2_terms[name] = terms if rule2_terms[name] is None else rule2_terms[name] + terms
    rule2_summary = {}
    for name in deployment:
        summary = pooled({k: v for k, v in rule2_terms.items() if v is not None}, name)
        rule2_summary[name] = summary
        s = summary["scores"][name]
        print(f"  rule2 {name} HOLDOUT-DTI {s['dti']:.6f} CI {s['ci95']}", flush=True)

    # SGMC proxy, labeled PROXY, not HOLDOUT-DTI.
    sgmc_proxy = {}
    if SGMC.is_file():
        with rasterio.open(SGMC) as ds:
            sgmc = (ds.read(1) > 0) & foot & (d_cat > 3.0)
        print(f"SGMC off-catalogue pixels {int(sgmc.sum())}", flush=True)
        for name, mask in deployment.items():
            sgmc_proxy[name] = dti_exact(mask.astype(np.float32), sgmc, valid=foot & ~cat)
            print(f"  SGMC PROXY {name} {sgmc_proxy[name]['dti']:.6f}", flush=True)

    final_unique = {}
    for name, mask in deployment.items():
        final_unique[name] = screen_support(mask, surfaces[name]["S_pct"], foot, rasters)
        final_unique[name].pop("rows", None)
        print(f"final {name} overlap {final_unique[name]['worst_forward_overlap']:.4f} "
              f"duplicate {final_unique[name]['duplicate']}", flush=True)

    # Choose the research primary: best static HOLDOUT-DTI among arms that are
    # not local duplicates. Never a slot recommendation.
    eligible_names = [n for n in deployment if not final_unique[n]["duplicate"]]
    if not eligible_names:
        print("final dots duplicated a local registry raster; no TIFF promoted to download", flush=True)
        card = _card(stopped, pre_rows, canaries, static_summary, rule2_summary, sgmc_proxy,
                     final_unique, None, None, None)
        _write_card(card)
        return 0
    primary_name = max(eligible_names, key=lambda n: static_summary[n]["scores"][n]["dti"])
    print("research primary", primary_name, flush=True)

    witness = ensure_witness()
    blob = git_blob_sha(witness)
    if blob != WITNESS_GIT_SHA:
        raise SystemExit(f"witness git blob mismatch {blob}")

    written = {}
    for name, mask in deployment.items():
        if final_unique[name]["duplicate"]:
            continue
        pred = np.zeros(foot.shape, np.float32)
        pred[mask] = 1.0
        pred[~foot] = 0.0
        if np.any((pred > 0) & cat):
            raise SystemExit(f"{name} has catalogue mass")
        n_dots = int(mask.sum())
        stem = f"gemsdoe92-listricdip-{name}-{n_dots}-{STAMP}"
        path = ROOT / "docs" / "downloads" / f"{stem}-zeros.tif"
        note = _note(name, static_summary[name]["scores"][name], n_dots)
        sub_name = f"GEMSDOE92-LISTRICDIP-{name}-20261025"
        receipt = write_submission(
            path, pred, SAMPLE, foot,
            note=note, name=sub_name, catalogue=cat,
            metadata={"lane": "LISTRICDIP", "arm": name, "evidence_class": "local format validation"},
        )
        written[name] = {"path": path, "receipt": receipt, "note": note,
                         "submission_name": sub_name, "n_dots": n_dots}
        print("wrote", path.name, receipt["sha256"], flush=True)

    primary = written[primary_name]
    witness_doc = _witness(primary["path"], witness, foot)
    audit = _audit(primary, witness_doc, final_unique[primary_name], primary["n_dots"])
    audit_path = primary["path"].with_name(primary["path"].name.replace("-zeros.tif", "-audit.json"))
    audit_path.write_text(json.dumps(audit, indent=2) + "\n")
    card = _card(stopped, pre_rows, canaries, static_summary, rule2_summary, sgmc_proxy,
                 {k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in final_unique.items()},
                 primary_name, primary, witness_doc)
    _write_card(card)
    for name, item in written.items():
        score = static_summary[name]["scores"][name]
        append_variant({
            "id": item["path"].stem,
            "parent": "h33-h33-2-b2",
            "axis": "LISTRICDIP",
            "value": name,
            "n_dots": str(item["n_dots"]),
            "pct_changed": "",
            "sha256": item["receipt"]["sha256"],
            "status": "BUILT",
            "predicted_change": "not a projection; see HOLDOUT-DTI in the run card",
            "file_zeros": str(item["path"].relative_to(ROOT)),
            "file_nan": "",
            "sha8": item["receipt"]["sha256"][:8],
            "change_desc": item["note"],
            "receipt_score": "",
            "receipt_date": "",
            "notes": "verdict negative; not organizer-confirmed; 0 weekly slots",
        })
        print(f"ledger {name} static DTI {score['dti']:.6f}", flush=True)
    print("DONE", flush=True)
    return 0


def _note(name: str, score: dict, n_dots: int) -> str:
    text = (f"LISTRICDIP {name}: {n_dots} listric-offset dots; "
            f"HOLDOUT-DTI {score['dti']:.6f}; negative")
    if len(text) > 140:
        raise ValueError(f"note length {len(text)}")
    return text


def _witness(candidate: Path, witness: Path, foot: np.ndarray) -> dict:
    with rasterio.open(candidate) as ds:
        cand = ds.read(1)
    with rasterio.open(witness) as ds:
        wit = ds.read(1)
        same = ds.shape == cand.shape
    support = (wit > 0) & foot
    ov = dot_overlap(cand, wit, radius_px=3)
    return {
        "evidence_class": "REGISTRY-MEASUREMENT",
        "witness_repo": "buffedlizard55-lab/17GEMSDOE",
        "witness_path": WITNESS_PATH,
        "witness_commit": WITNESS_COMMIT,
        "witness_git_blob_sha": git_blob_sha(witness),
        "witness_sha256": sha256_file(witness),
        "grid_match": bool(same),
        "positive_in_footprint": int(support.sum()),
        "footprint_pixels": int(foot.sum()),
        "covers_entire_footprint": bool(support.sum() == int(foot.sum()) and foot.any()),
        "forward_overlap_3px": ov,
        "unique_under_literal_rule": False if ov > 0.70 else True,
        "stop_required": bool(ov > 0.70),
        "scope": "Single pinned dense witness. Rejection only. Not a 102-repo clearance.",
    }


def _audit(primary: dict, witness_doc: dict, local_unique: dict, n_dots: int) -> dict:
    path = primary["path"]
    gates = run_gates(str(path), str(SAMPLE), str(LABELS), prune_radius=2, require_submission_encoding=True)
    gate_rows = [{"name": g.name, "ok": bool(g.ok), "detail": g.detail} for g in gates]
    sha = sha256_file(path)
    return {
        "schema": "gemsdoe92-listricdip-audit.v1",
        "file": str(path.relative_to(ROOT)),
        "sha256_zeros": sha,
        "sha256_nan": None,
        "n_dots": int(n_dots),
        "n_positive_pixels": int(n_dots),
        "overall_pass": all(g.ok for g in gates),
        "gates_zeros": gate_rows,
        "gates_zeros_pass": all(g.ok for g in gates),
        "gates_nan": [],
        "gates_nan_pass": False,
        "submission_eligible": False,
        "verdict": "negative",
        "note": primary["note"],
        "submission_name": primary["submission_name"],
        "run_card": "evidence/listricdip_run_card.json",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "local_registry_uniqueness": local_unique,
        "public_registry_uniqueness": {
            "candidate_hash_matches_scan": True,
            "candidate_sha256_zeros": sha,
            "unique_under_literal_rule": False,
            "stop_required": True,
            "witness_evidence": witness_doc,
            "scope": witness_doc["scope"],
            "worst_forward_overlap": witness_doc["forward_overlap_3px"],
        },
    }


def _card(stopped, pre_rows, canaries, static_summary, rule2_summary, sgmc_proxy,
          final_unique, primary_name, primary, witness_doc) -> dict:
    def pack(summary, name):
        if not summary or name not in summary:
            return None
        s = summary[name]["scores"][name]
        return {
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": evaluate_holdout.VERSION,
            "withheld_positive_pixels": s["withheld_positive_pixels"],
            "dti": s["dti"],
            "ci95": s["ci95"],
            "paired_differences": summary[name]["paired_differences"],
        }
    sha = None if primary is None else primary["receipt"]["sha256"]
    return {
        "schema": "gemsdoe92-run-card.v2",
        "session_id": "arena/5162a107-gemsdoe92",
        "date": "2026-10-25",
        "lane": "LISTRICDIP",
        "hypothesis": (
            "A 50-degree normal fault under 400-1100 m of cover has its near-surface "
            "trace up-dip of the basement cutoff by C*cot(dip); an antithetic strand "
            "sits 2.2 or 3.5 km further down-dip where the depth gradient reverses."
        ),
        "mechanism": (
            "Catalogue-free basement-gradient crest, shifted up-dip by smoothed cover "
            "times cot(50 deg), or scored where the local gradient opposes the 1.2 km "
            "regional dip at 22 px or 35 px. 37654 unit dots, spacing 3.2 px, d_cat>2."
        ),
        "named_non_fault_process_that_could_mimic_it": (
            "Compaction monocline or alluvial-fan trench over an unfaulted density step, "
            "and a contour-parallel pluvial bench. Absolute Lahontan elevation was not used."
        ),
        "holdout_dti": None if primary_name is None else pack(static_summary, primary_name),
        "holdout_dti_by_arm": {n: pack(static_summary, n) for n in static_summary},
        "rule2_dti_by_arm": {n: pack(rule2_summary, n) for n in rule2_summary},
        "sgmc_proxy": {n: {"evidence_class": "PROXY", "dti": float(v["dti"]),
                          "n_truth": int(v["n_truth"])} for n, v in sgmc_proxy.items()},
        "canaries": canaries,
        "preplacement": pre_rows,
        "final_uniqueness": final_unique,
        "duplicate_arms_stopped": stopped,
        "primary_arm": primary_name,
        "raster_sha256": sha,
        "submission_name": None if primary is None else primary["submission_name"],
        "submission_note": None if primary is None else primary["note"],
        "validator": None if primary is None else {
            "no_nan_inside_footprint": True,
            "values_in_0_1": True,
            "crs_shape_transform_match": True,
            "zeros_outside_footprint": True,
            "writer": "vendor/gems57/submission_writer.py",
        },
        "public_witness": witness_doc,
        "verdict": "negative",
        "submission_eligible": False,
        "weekly_slots_used": 0,
        "experiments_executed": 3,
        "organizer_confirmed_score": None,
        "leaderboard_snapshot": {
            "evidence_class": "LEADERBOARD-SNAPSHOT",
            "read_utc_date": "2026-10-25",
            "url": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "rank_1_public_dw_tversky": 0.4413,
            "participant": "xiaofanhu",
            "not_a_receipt_for_this_file": True,
        },
    }


def _write_card(card: dict) -> None:
    text = json.dumps(card, indent=2, allow_nan=False) + "\n"
    path = ROOT / "evidence" / "listricdip_run_card.json"
    path.write_text(text)
    shutil.copy2(path, ROOT / "docs" / "downloads" / "listricdip_run_card.json")


if __name__ == "__main__":
    raise SystemExit(main())
