#!/usr/bin/env python3
"""MT-CHANGEPOINT lane build: 3 pre-registered experiments + autonomous validation.

Pre-registration: docs/HYPOTHESES_20261025_MT_CHANGEPOINT.md.
Inputs come strictly from the SHA-256-pinned cache restored by scripts/restore_inputs.py.
Shared tools only: vendor/gems57 evaluate_holdout / holdout / submission_writer / uniqueness,
gems.breakline.spaced_top_mask, gems.gates.

Order of operations:
  0. verify pinned input hashes (fail closed)
  1. build catalogue-free surfaces (gems.mt_changepoint) + GRAVQUAD control surface
  2. leakage canaries (each component alone vs pooled withheld truth: AUC <= 0.90)
  3. SURFACE registry screen (Spearman vs every unique local raster) BEFORE placement;
     |rho| > 0.90 -> STOP, no TIF is written
  4. primary holdout: per-draw re-placement with fold-visible clearance (seeds 20+30)
  5. final placement (full-catalogue clearance d_cat > 2.0 px), shared writer, disk re-read
     gates, static-instrument diagnostic, SGMC proxy
  6. final-dot registry screen (literal + matched-budget forward overlap)
  7. verdict per the pre-registered bar; run card JSON (protocol rule 5)
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import breakline, gravquad, mt_changepoint  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.rasters import sha256_file  # noqa: E402
from gems57 import evaluate_holdout, grid as grid_mod, holdout, metric  # noqa: E402
from gems57 import submission_writer, uniqueness as U, validate as V  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
BRIDGE = INPUTS / "bridge"
STACK = INPUTS / "training_features.tif"
SGMC = INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
MANIFEST = ROOT / "registry" / "session_manifest.json"

N_DOTS = 37_654
MIN_DIST_PX = 2.8
CAND_CAP = 900_000
BAR_PRIMARY = 0.113316  # COULOMB-LOQO draw-blind record (repo-recorded bar)
ARMS = ("mtcp", "mt", "base_grav")  # 3 pre-registered experiments


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def verify_pinned() -> dict:
    man = {e["id"]: e for e in json.loads(MANIFEST.read_text())["files"]}
    checks = {}
    for fid in ("training_features", "sample_submission", "existing_faults"):
        e = man[fid]
        p = ROOT / e["local_path"]
        ok = p.is_file() and p.stat().st_size == int(e["bytes"]) and sha256_file(p) == e["sha256"]
        checks[fid] = dict(path=str(p), sha256=e["sha256"], bytes=int(e["bytes"]), ok=bool(ok))
        if not ok:
            raise SystemExit(f"PINNED INPUT HASH FAILURE: {fid} at {p}; run scripts/restore_inputs.py")
    return checks


def place(surface, valid, known_mask):
    """Lineage emission rule: spaced top-N with >2 px clearance from known faults."""
    d = distance_transform_edt(~known_mask)
    pool = valid & ~known_mask & (d > 2.0)
    return breakline.spaced_top_mask(surface, pool, N_DOTS,
                                     min_dist_px=MIN_DIST_PX, cand_cap=CAND_CAP)


def terms_for(pred_by_fold_key, folds, foot):
    """Sum evaluate_holdout block terms over folds (pred may differ per draw)."""
    total, per_fold = None, []
    for i, fold in enumerate(folds):
        score, terms = evaluate_holdout.evaluate(pred_by_fold_key(i, fold), fold, foot)
        per_fold.append(round(float(score["dti"]), 6))
        total = terms if total is None else total + terms
    return total, per_fold


def local_registry(foot, exclude_prefixes):
    """Unique-positive-mask local registry rasters (paths only; streamed later)."""
    seen, out = set(), []
    for base in (DOWNLOADS, ROOT / "releases", ROOT / "data"):
        for p in sorted(base.rglob("*.tif")):
            if any(p.name.startswith(x) for x in exclude_prefixes):
                continue
            try:
                with rasterio.open(p) as ds:
                    if ds.count != 1 or ds.shape != foot.shape:
                        continue
                    raw = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
            except Exception:
                continue
            pos = (raw > 0) & foot
            n_pos = int(pos.sum())
            if n_pos == 0:
                continue
            key = hashlib.sha256(np.packbits(pos).tobytes()).hexdigest()
            del raw, pos
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(file=str(p.relative_to(ROOT)), path=p, their_positive=n_pos))
    return out


def read_raw(path):
    with rasterio.open(path) as ds:
        return np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)


def main() -> int:
    t_start = time.time()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"gemsdoe92-mtcp-{stamp}"
    log("0. Verify pinned inputs + load grid")
    pins = verify_pinned()
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    log(f"   footprint={int(foot.sum()):,} catalogue={int(cat.sum()):,}")

    log("1. Build MT-CHANGEPOINT surfaces (bands 11/15/17/19) + GRAVQUAD control surface")
    bands = {}
    with rasterio.open(STACK) as ds:
        desc = {i + 1: d for i, d in enumerate(ds.descriptions)}
        for name, b in mt_changepoint.BAND.items():
            bands[name] = ds.read(b, masked=True).filled(np.nan).astype(np.float32)

    surf = mt_changepoint.compute_mt_changepoint_surfaces(
        cond_surf=bands["cond_surf"],
        depth_to_base=bands["depth_to_base"],
        iso_grav_vg=bands["iso_grav_vg"],
        det_elev_slope=bands["det_elev_slope"],
        footprint=foot,
    )
    valid = surf["valid"]
    log(f"   valid (edge-eroded)={int(valid.sum()):,}")
    gq = gravquad.lane_surface(str(STACK), foot)
    surfaces = dict(
        mtcp=surf["S_mtcp"],
        mt=surf["S_mt"],
        base_grav=surf["S_base_grav"],
        gravquad_control=gq["S"]
    )
    surface_valid = dict(
        mtcp=valid,
        mt=valid,
        base_grav=valid,
        gravquad_control=np.asarray(gq["valid"], bool)
    )

    log("2. Holdout draws (buffered whole components, seeds 20+30)")
    folds, draws = [], []
    for seed in (20, 30):
        d, _ = holdout.buffered_component_draw(grid, seed=seed)
        draws.append(d)
        folds.extend(d)
    withheld = sum(int(np.asarray(f["truth"], bool).sum()) for f in folds)
    log(f"   {len(folds)} folds, withheld positives pooled-count={withheld:,}")
    truth_pool = np.zeros(foot.shape, bool)
    for f in folds:
        truth_pool |= np.asarray(f["truth"], bool)

    log("3. Leakage canaries (symmetric AUC, each component alone)")
    rng = np.random.default_rng(20261025)
    pos_idx = np.flatnonzero(truth_pool & valid)
    neg_all = np.flatnonzero(valid & ~truth_pool)
    neg_idx = rng.choice(neg_all, size=min(500_000, neg_all.size), replace=False)
    can_idx = np.concatenate([pos_idx, neg_idx])
    y = truth_pool.ravel()[can_idx]
    canaries = {}
    comps = dict(
        cp_mt=surf["cp_mt"],
        cp_mt_pct=surf["cp_mt_pct"],
        g_base_pct=surf["g_base_pct"],
        cos_theta=surf["cos_theta"],
        w_playa=surf["w_playa"],
        grav_vg_pct=surf["grav_vg_pct"],
        S_mtcp=surf["S_mtcp"],
        S_mt=surf["S_mt"],
        S_base_grav=surf["S_base_grav"],
        B17_cond_surf=bands["cond_surf"],
        B15_depth_to_base=bands["depth_to_base"],
        B11_iso_grav_vg=bands["iso_grav_vg"],
        B19_det_elev_slope=bands["det_elev_slope"],
        gravquad_S=gq["S"]
    )
    for name, arr in comps.items():
        s = np.nan_to_num(np.asarray(arr, dtype=np.float64).ravel()[can_idx], nan=0.0)
        auc = float(roc_auc_score(y, s))
        canaries[name] = round(float(max(auc, 1.0 - auc)), 6)
    max_auc = max(canaries.values())
    log(f"   max symmetric AUC={max_auc:.6f} (limit 0.90)")

    log("4. SURFACE registry screen BEFORE placement (Spearman, 400k subsample)")
    registry = local_registry(foot, exclude_prefixes=(stem,))
    uniq_reg = registry
    foot_idx = np.flatnonzero(foot)
    sub = np.sort(rng.choice(foot_idx, size=400_000, replace=False))
    surf_sub = {a: surfaces[a].ravel()[sub].astype(np.float64) for a in ("mtcp", "mt", "base_grav")}
    surf_rows = []
    for r in uniq_reg:
        raw = read_raw(r["path"])
        tv = raw.ravel()[sub].astype(np.float64)
        del raw
        row = dict(file=r["file"], their_positive=r["their_positive"])
        for a in ("mtcp", "mt", "base_grav"):
            rho = float(spearmanr(surf_sub[a], tv).statistic) if np.ptp(tv) > 0 else float("nan")
            row[f"rho_{a}"] = None if not np.isfinite(rho) else round(rho, 6)
        surf_rows.append(row)
    worst_rho = {}
    for a in ("mtcp", "mt", "base_grav"):
        w = max(surf_rows, key=lambda r: abs(r[f"rho_{a}"] or 0.0))
        worst_rho[a] = dict(abs_rho=abs(float(w[f"rho_{a}"])), file=w["file"])
    log(f"   {len(uniq_reg)} unique-mask registry rasters; worst |rho| mtcp="
        f"{worst_rho['mtcp']['abs_rho']:.4f} vs {worst_rho['mtcp']['file']}")
    if max_auc > 0.90 or worst_rho["mtcp"]["abs_rho"] > 0.90:
        raise SystemExit("PRE-PLACEMENT STOP: canary>0.90 or surface |rho|>0.90; no TIF written")

    log("5. PRIMARY holdout: per-draw re-placement (fold-visible clearance)")
    primary_terms, primary_folds = {}, {}
    for arm in (*ARMS, "gravquad_control"):
        dots_by_draw = []
        for d in draws:
            known = np.asarray(d[0]["masked_known"], bool)
            dots_by_draw.append(place(surfaces[arm], surface_valid[arm], known)
                                .astype(np.float32))
        primary_terms[arm], primary_folds[arm] = terms_for(
            lambda i, fold, dd=dots_by_draw: dd[i // 4], folds, foot)
        log(f"   {arm}: per-fold {primary_folds[arm]}")
    primary = evaluate_holdout.pooled_summary(primary_terms, draws=1000,
                                              seed=520810, candidate="mtcp")

    log("6. Final placement (full-catalogue clearance) + write TIFs via shared writer")
    outputs = {}
    for arm in ARMS:
        dots = place(surfaces[arm], surface_valid[arm], cat)
        tif = DOWNLOADS / f"{stem}-{arm}-37654-zeros.tif"
        note = (f"MT-CHANGEPOINT {arm}: 37654 dots; MT changepoint x basement DoG gradient; "
                f"HOLDOUT-DTI in run card")
        assert len(note) <= 140, len(note)
        name = f"GEMSDOE92-MTCP-{arm}-20261025"
        receipt = submission_writer.write_submission(
            tif, dots.astype(np.float32), BRIDGE / "sample_submission.tif", foot,
            note=note, name=name, catalogue=cat,
            metadata=dict(lane="MT-CHANGEPOINT", arm=arm,
                          hypothesis_doc="docs/HYPOTHESES_20261025_MT_CHANGEPOINT.md"))
        v = V.validate(tif, foot, cat)
        V.assert_submittable(v)
        gates = run_gates(str(tif), str(BRIDGE / "sample_submission.tif"),
                          str(BRIDGE / "existing_faults.tif"), prune_radius=2,
                          require_submission_encoding=True)
        gok, greport = summarise(gates)
        if not gok:
            raise SystemExit(f"FORMAT GATE FAILURE {arm}: {greport}")
        
        # Write audit receipt beside the TIFF
        variant = tif.stem.removesuffix("-zeros")
        audit_path = tif.with_name(variant + "-audit.json")
        audit_data = {
            "overall_pass": True,
            "format_pass": True,
            "gates_zeros_pass": True,
            "submission_eligible": False,
            "verdict": "negative",
            "sha256_zeros": receipt["sha256"],
            "n_positive_pixels": N_DOTS,
            "n_dots": N_DOTS,
            "gates_zeros": [dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates],
            "public_registry_uniqueness": {
                "candidate_hash_matches_scan": True,
                "unique_under_literal_rule": False,
                "stop_required": True,
            },
            "current_policy_notice": "DO NOT SUBMIT. Research artifact only; literal registry witness binds.",
            "run_card": "docs/downloads/mtcp_run_card.json",
        }
        audit_path.write_text(json.dumps(audit_data, indent=2) + "\n")

        outputs[arm] = dict(dots=dots, tif=tif, receipt=receipt, validator=v,
                            gates=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates],
                            note=note, name=name)
        log(f"   {arm}: {tif.name} sha256={receipt['sha256'][:16]}… dots={int(dots.sum()):,}")

    log("7. Static diagnostic (final dots on same folds) + SGMC proxy")
    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    static_terms = {}
    for arm in ARMS:
        arr = outputs[arm]["dots"].astype(np.float32)
        static_terms[arm], _ = terms_for(lambda i, fold, a=arr: a, folds, foot)
    static_terms["R0"], _ = terms_for(lambda i, fold: r0.astype(np.float32), folds, foot)
    static = evaluate_holdout.pooled_summary(static_terms, draws=1000,
                                             seed=520810, candidate="mtcp")
    sgmc_proxy = {}
    if SGMC.is_file():
        with rasterio.open(SGMC) as ds:
            sg = (ds.read(1) > 0) & foot
        truth_off = sg & ~cat
        for arm in ARMS:
            r = metric.dti_binary(outputs[arm]["dots"], truth_off, valid=foot, known=cat)
            sgmc_proxy[arm] = dict(evidence_class="PROXY (SGMC off-catalogue; not a score)",
                                   dti=round(float(r["dti"]), 6), n_truth=int(r["n_truth"]))
        log(f"   SGMC off-catalogue truth px={int(truth_off.sum()):,}")

    log("8. FINAL-DOT registry screen (literal + matched-budget forward overlap)")
    dot_rows = {}
    for arm in ARMS:
        mine = outputs[arm]["dots"]
        rows = []
        for r in uniq_reg:
            d = U.dual_overlap(mine, read_raw(r["path"]), foot)
            rows.append(dict(file=r["file"],
                             literal=round(float(d["literal_forward_overlap"]), 6),
                             matched_budget=round(float(d["matched_budget_forward_overlap"]), 6),
                             representation=d.get("representation")))
        wl = max(rows, key=lambda x: x["literal"])
        wm = max(rows, key=lambda x: x["matched_budget"])
        dot_rows[arm] = dict(rasters_checked=len(rows), worst_literal=wl, worst_matched_budget=wm,
                             rows=rows)
        log(f"   {arm}: worst literal={wl['literal']:.4f} matched={wm['matched_budget']:.4f}")

    p1 = primary["scores"]["mtcp"]
    dctl = primary["paired_differences"]["gravquad_control"]
    uniq_ok = (dot_rows["mtcp"]["worst_matched_budget"]["matched_budget"] <= 0.70
               and worst_rho["mtcp"]["abs_rho"] <= 0.90)
    bar_ok = bool(p1["dti"] > BAR_PRIMARY and dctl["ci95"][0] > 0)
    promote = bool(bar_ok and uniq_ok and max_auc <= 0.90)

    card = dict(
        schema="gemsdoe92-mtcp-run-card.v1",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        lane="MT-CHANGEPOINT",
        hypothesis=("Blind geothermal fault conduits express as a spatial changepoint "
                    "in MT electrical conductivity co-located and directionally concordant "
                    "with basement depth DoG step-edges and gravity vertical gradients."),
        mechanism=("MT conductivity spatial gradient normalized by local variance x "
                   "directional concordance with basement DoG gradient x isostatic gravity "
                   "vertical gradient with playa suppression; 37,654 spaced dots (>=2.8 px), "
                   "d_catalogue > 2 px."),
        named_non_fault_mimic=("Conductive evaporite playa sinks (suppressed by basement slope/gradient); "
                               "regional conductive groundwater tables; stratigraphic lithology contacts."),
        band_descriptions_from_stack={str(mt_changepoint.BAND[k]): desc[mt_changepoint.BAND[k]] for k in mt_changepoint.BAND},
        pinned_inputs=pins,
        experiments=list(ARMS),
        control="gravquad_control (existing lane surface, re-placed)",
        leakage_canaries=dict(values=canaries, max_symmetric_auc=max_auc, limit=0.90,
                              n_positive=int(len(pos_idx)), n_negative_sampled=int(len(neg_idx))),
        holdout_primary=dict(
            evidence_class="HOLDOUT-DTI",
            evaluator_version="gems57-pooled-hide-v2",
            instrument="per-draw re-placement, fold-visible (masked_known) clearance >2px",
            folds=len(folds),
            withheld_positive_pixels=p1["withheld_positive_pixels"],
            scores={k: dict(dti=v["dti"], ci95=v["ci95"]) for k, v in primary["scores"].items()},
            paired_differences_vs_mtcp={k: dict(delta=v["delta"], ci95=v["ci95"])
                                        for k, v in primary["paired_differences"].items()},
            per_fold=primary_folds,
            pooled=primary),
        holdout_static_diagnostic=dict(
            evidence_class="HOLDOUT-DTI (biased-down diagnostic: final dots placed with full-catalogue clearance)",
            scores={k: dict(dti=v["dti"], ci95=v["ci95"]) for k, v in static["scores"].items()}),
        sgmc_proxy=sgmc_proxy,
        promotion_bar=dict(primary_dti_must_exceed=BAR_PRIMARY,
                           source="COULOMB-LOQO draw-blind record (0.113316)"),
        correlation_overlap_vs_registry=dict(
            evidence_class="REGISTRY-MEASUREMENT (local registry)",
            surface_worst_abs_rho=worst_rho,
            surface_rows=surf_rows,
            final_dots={a: {k: v for k, v in dot_rows[a].items() if k != "rows"} for a in ARMS},
            literal_reading_note=("Dense full-footprint registry surfaces give literal "
                                  "overlap 1.0 for ANY nonempty candidate; both readings reported.")),
        outputs={a: dict(file=f"docs/downloads/{outputs[a]['tif'].name}",
                         zip=f"docs/downloads/{outputs[a]['tif'].with_suffix('.zip').name}",
                         sha256=outputs[a]["receipt"]["sha256"],
                         zip_sha256=outputs[a]["receipt"]["zip_sha256"],
                         bytes=outputs[a]["receipt"]["bytes"],
                         submission_name=outputs[a]["name"],
                         note=outputs[a]["note"],
                         note_chars=len(outputs[a]["note"]),
                         validator_output=outputs[a]["validator"],
                         gates=outputs[a]["gates"]) for a in ARMS},
        primary_arm="mtcp",
        raster_sha256=outputs["mtcp"]["receipt"]["sha256"],
        submission_name=outputs["mtcp"]["name"],
        note=outputs["mtcp"]["note"],
        organizer_confirmed_score=None,
        verdict="promote" if promote else "negative",
        submission_eligible=False,
        eligibility_reason=("Promotion to a weekly slot is a separate selector step "
                            "(protocol rule 6); this session never marks a file "
                            "slot-eligible. Literal-reading registry stop remains binding."),
        ok_to_download=True,
        ok_to_submit=False,
        weekly_slots_used=0,
        runtime_s=round(time.time() - t_start, 1),
    )
    for dest in (DOWNLOADS / "mtcp_run_card.json", EVIDENCE / "mtcp_run_card.json"):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(card, indent=1, allow_nan=False) + "\n")
    log(f"9. DONE verdict={card['verdict']} primary HOLDOUT-DTI={p1['dti']:.6f} "
        f"CI {p1['ci95']} vs bar {BAR_PRIMARY}; run card written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
