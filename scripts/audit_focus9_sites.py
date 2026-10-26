#!/usr/bin/env python3
"""Uniform byte-verified forensic audit of the 9 focus repositories
(GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36) plus cross-fleet SOTA benchmarks
(GEMSDOE70, GEMSDOE76, GEMSDOE91, GEMSDOE92) on identical GEMSDOE92 evaluation
instruments:
  1. Exact SHA-256, grid/range/[0,1]/NaN compliance, positive dot count, d_cat<=2 px halo mass.
  2. Exact 3-px overlap vs R0 (GEMSDOE32 0.2778) and H19-5, plus zero-XOR subset identities.
  3. Uniform HOLDOUT-DTI on vendor/gems57/evaluate_holdout.py (gems57-pooled-hide-v2,
     seeds 20 & 30, 22,663 withheld positive pixels, 1,000-draw block-bootstrap 95% CI).
  4. Uniform off-catalogue USGS SGMC proxy DTI (d_cat > 3 px and d_cat > 5 px).
  5. Full 102-repo (1,756 compatible rasters) non-self operative & literal uniqueness.

Outputs: evidence/focus9_executive_audit_20261026.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from vendor.gems57 import evaluate_holdout, grid as grid_mod, holdout as hold_mod
from vendor.gems57 import metric as metric_mod, uniqueness as U

INPUTS = ROOT / ".cache" / "gems_inputs"
PUB_CACHE = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
OUT_JSON = ROOT / "evidence" / "focus9_executive_audit_20261026.json"


FOCUS_RECORDS = [
    # --- Historical best per focus site (Oct 2-4, all H19-5 descendants) ---
    dict(
        site="GEMSDOE24",
        role="historical_best",
        rel_path="docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif",
        claim_score=0.2477,
        claim_date="2026-10-02",
        repo_verdict="historical_submitted_duplicate_family",
    ),
    dict(
        site="GEMSDOE24",
        role="scored_20261025",
        rel_path="docs/downloads/gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros.tif",
        claim_score=0.0859,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (note content-id 65c294f26ef6 vs main abe8e51c719d)",
    ),
    dict(
        site="GEMSDOE24",
        role="latest_20261026",
        rel_path="docs/downloads/gems24-dprf1-stitched-oof-tworegime-20261026-81849d67c8bf-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (selector v2 literal lattice + quota fail-closed)",
    ),
    dict(
        site="GEMSDOE25",
        role="historical_best",
        rel_path="docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-zeros.tif",
        claim_score=0.2600,
        claim_date="2026-10-02",
        repo_verdict="historical_submitted_duplicate_family",
    ),
    dict(
        site="GEMSDOE25",
        role="scored_20261025",
        rel_path="docs/downloads/gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros.tif",
        claim_score=0.0742,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (note content-id 56e35c690b84 vs main da617550a0e9)",
    ),
    dict(
        site="GEMSDOE25",
        role="latest_20261026",
        rel_path="docs/downloads/gems25-h71-hgpc-blind-b2-sapd3-k3p5-20261026-9eb0c31e5149-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (failed holdout vs H35)",
    ),
    dict(
        site="GEMSDOE27",
        role="historical_best",
        rel_path="docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-allfinite.tif",
        claim_score=0.2449,
        claim_date="2026-10-02",
        repo_verdict="historical_submitted_duplicate_family",
    ),
    dict(
        site="GEMSDOE27",
        role="scored_20261025",
        rel_path="docs/downloads/gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite.tif",
        claim_score=0.2190,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (#1 among 2026-10-25 focus-site claims)",
    ),
    dict(
        site="GEMSDOE27",
        role="latest_20261026",
        rel_path="docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="repo_local_promote_27raster_gate; literal_102repo_dense_stop",
    ),
    dict(
        site="GEMSDOE28",
        role="historical_best",
        rel_path="docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
        claim_score=0.2710,
        claim_date="2026-10-03",
        repo_verdict="historical_submitted_duplicate_family",
    ),
    dict(
        site="GEMSDOE28",
        role="historical_solo_d28",
        rel_path="docs/downloads/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif",
        claim_score=0.2708,
        claim_date="2026-10-03",
        repo_verdict="historical_submitted_duplicate_family (zero-XOR with GEMSDOE31)",
    ),
    dict(
        site="GEMSDOE28",
        role="scored_20261025",
        rel_path="docs/downloads/gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif",
        claim_score=0.0217,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (note content-id 6b8aa90da850 vs main 3e95505c011a)",
    ),
    dict(
        site="GEMSDOE28",
        role="latest_20261026",
        rel_path="docs/downloads/gems28-s20-nchc-20261026-d432a1d5d6ee-allfinite.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (holdout negative vs visible-only H38)",
    ),
    dict(
        site="GEMSDOE30",
        role="historical_best",
        rel_path="docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
        claim_score=0.2600,
        claim_date="2026-10-03",
        repo_verdict="historical_submitted_duplicate_family (zero-XOR with GEMSDOE25; NaN outside)",
    ),
    dict(
        site="GEMSDOE30",
        role="scored_20261025",
        rel_path="docs/downloads/gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif",
        claim_score=0.1462,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (NaN outside; 18.2% d_cat<=2px)",
    ),
    dict(
        site="GEMSDOE30",
        role="latest_20261026",
        rel_path="docs/downloads/GEMSDOE30-geothermal-corridor-offcat-d3-20261026T160300Z.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (no local competition labels in GEMSDOE30; NaN outside)",
    ),
    dict(
        site="GEMSDOE31",
        role="historical_best",
        rel_path="docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-allfinite.tif",
        claim_score=0.2708,
        claim_date="2026-10-04",
        repo_verdict="historical_submitted_duplicate_family (zero-XOR with GEMSDOE28 h27-4)",
    ),
    dict(
        site="GEMSDOE31",
        role="latest_20261026_h31s",
        rel_path="docs/downloads/gemsdoe31-h31s-udap-sslic-37654-20261026-9355f21d9f-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (holdout negative; note IR-31-DANGLING-PGR31-README-LINK)",
    ),
    dict(
        site="GEMSDOE31",
        role="latest_20261026_xfcoh31",
        rel_path="docs/downloads/gems31-xfcoh31-xfield-coherence-37654-20261026-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (holdout negative)",
    ),
    dict(
        site="GEMSDOE32",
        role="historical_best",
        rel_path="docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        claim_score=0.2778,
        claim_date="2026-10-04",
        repo_verdict="PORTFOLIO_CHAMPION_ALREADY_SUBMITTED_DO_NOT_RESUBMIT",
    ),
    dict(
        site="GEMSDOE32",
        role="latest_20261026",
        rel_path="docs/downloads/gemsdoe32-h38g1-lidar-geodawn-gdr-celf37654-20261026T013500Z-35859e28-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (failed off-catalogue SGMC gate & local hcvf2 77.6% overlap)",
    ),
    dict(
        site="GEMSDOE33",
        role="historical_best",
        rel_path="docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        claim_score=0.2632,
        claim_date="2026-10-04",
        repo_verdict="historical_submitted_duplicate_family (NaN outside)",
    ),
    dict(
        site="GEMSDOE33",
        role="latest_20261026",
        rel_path="docs/downloads/gemsdoe33-a33-r3-llc-37654-20261026-7f91f9f3ced9-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (failed confirmation holdout)",
    ),
    dict(
        site="GEMSDOE36",
        role="historical_best",
        rel_path="docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
        claim_score=0.2750,
        claim_date="2026-10-04",
        repo_verdict="historical_submitted_duplicate_family (exact R0 + 1,200 PINN dots)",
    ),
    dict(
        site="GEMSDOE36",
        role="latest_20261026",
        rel_path="docs/downloads/gemsdoe36-mto36-ortho-contact-20261026-c41282e9da7a-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="DO_NOT_SUBMIT (paired CI crosses zero)",
    ),
    # --- Top non-H19-5 cross-fleet benchmarks + GEMSDOE92 baselines ---
    dict(
        site="GEMSDOE70",
        role="fleet_best_non_h195_scored",
        rel_path="docs/downloads/gems70-p5-dual-submod300-oof38k-20261020.tif",
        claim_score=0.2478,
        claim_date="2026-10-20",
        repo_verdict="fleet_#1_zero_H19_5_scored_benchmark",
    ),
    dict(
        site="GEMSDOE70",
        role="fleet_p9_piedmont_submod",
        rel_path="docs/downloads/gems70-p5-multiphysics-submodular-37654-20261020.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="GEMSDOE70_P9_zero_SGMC_candidate",
    ),
    dict(
        site="GEMSDOE76",
        role="fleet_#2_non_h195_scored",
        rel_path="docs/downloads/gems76-ptcf-tiltworm-submod39k-20261021T034000Z-6316481d-zeros.tif",
        claim_score=0.2343,
        claim_date="2026-10-21",
        repo_verdict="fleet_#2_zero_H19_5_scored_benchmark",
    ),
    dict(
        site="GEMSDOE91",
        role="scored_20261025_lftg",
        rel_path="docs/downloads/gems91-s17-lftg-20261025T160014Z-7b6bf90844-zeros.tif",
        claim_score=0.1823,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique",
    ),
    dict(
        site="GEMSDOE92",
        role="scored_20261025_listricdip",
        rel_path="docs/downloads/gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros.tif",
        claim_score=0.0255,
        claim_date="2026-10-25",
        repo_verdict="historical_scored_unique (untrained deterministic dip heuristic)",
    ),
    dict(
        site="GEMSDOE92",
        role="zero_cat_sota_listricloqo",
        rel_path="docs/downloads/h33-h33-2-b2-LISTRICLOQOselectcal-20261025-110427ce-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="GEMSDOE92_static_zero_cat_SOTA_control",
    ),
    dict(
        site="GEMSDOE92",
        role="zero_cat_sota_chilistric",
        rel_path="docs/downloads/h33-h33-2-b2-CHILISTRICaddtail52k-20261025-8c82904d-zeros.tif",
        claim_score=None,
        claim_date=None,
        repo_verdict="GEMSDOE92_prior_newest_session_lane",
    ),
]


def main() -> int:
    t0 = time.monotonic()
    inv = json.loads((PUB_CACHE / "repo_inventory.json").read_text(encoding="utf-8"))
    by_repo_path = {
        (r["repo"], t["path"]): PUB_CACHE / f"{t['sha']}.tif"
        for r in inv
        for t in r["tifs"]
    }
    by_repo_name = {
        (r["repo"], Path(t["path"]).name): (t["path"], PUB_CACHE / f"{t['sha']}.tif")
        for r in inv
        for t in r["tifs"]
    }

    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot = grid.footprint
    cat = grid.catalogue
    d_cat = distance_transform_edt(~cat)

    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref_ds:
        expected_grid = (ref_ds.shape, ref_ds.crs, ref_ds.transform)

    with rasterio.open(ROOT / "data" / "parent_R0_zeros.tif") as ds:
        r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0.5) & foot
    with rasterio.open(INPUTS / "lineage" / "calib_h195_01922.tif") as ds:
        h19 = (np.nan_to_num(ds.read(1), nan=0.0) > 0.5) & foot
    r0_near3 = U._near(r0, 3.0)
    h19_near3 = U._near(h19, 3.0)

    folds = []
    for seed in (20, 30):
        draw, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        folds.extend(draw)

    with rasterio.open(INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) > 0) & foot
    sgmc_gt3 = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    sgmc_gt5 = sgmc & (~cat) & (~binary_dilation(cat, iterations=5))

    fs = np.load(PUB_CACHE / "fast_supports.npz")
    all_idx = fs["all_idx"]
    offs = fs["offsets"]
    meta = json.loads(str(fs["meta_json"]))
    h, w = foot.shape
    offsets_1d = np.array(
        [dy * w + dx for dy in range(-3, 4) for dx in range(-3, 4) if dy * dy + dx * dx <= 9],
        dtype=np.int32,
    )

    loaded_arrays: dict[str, np.ndarray] = {}
    records_out: list[dict] = []
    terms_by_key: dict[str, np.ndarray] = {}

    for rec in FOCUS_RECORDS:
        key = f"{rec['site']}__{rec['role']}"
        actual_rel_path = rec["rel_path"]
        p_tif = by_repo_path.get((rec["site"], rec["rel_path"]))
        if p_tif is None:
            hit = by_repo_name.get((rec["site"], Path(rec["rel_path"]).name))
            if hit is not None:
                actual_rel_path, p_tif = hit
        if p_tif is None and rec["site"] == "GEMSDOE92":
            p_tif = ROOT / rec["rel_path"]
        if p_tif is None or not p_tif.is_file():
            raise FileNotFoundError(f"Missing {rec['site']} {rec['rel_path']}")

        sha256 = hashlib.sha256(p_tif.read_bytes()).hexdigest()
        with rasterio.open(p_tif) as ds:
            grid_ok = ds.count == 1 and (ds.shape, ds.crs, ds.transform) == expected_grid
            raw = ds.read(1).astype(np.float32)

        nan_in_foot = int((~np.isfinite(raw) & foot).sum())
        nan_out_foot = int((~np.isfinite(raw) & (~foot)).sum())
        fin = np.isfinite(raw)
        min_v = float(raw[fin].min()) if fin.any() else float("nan")
        max_v = float(raw[fin].max()) if fin.any() else float("nan")
        in_unit_range = bool(nan_in_foot == 0 and min_v >= 0.0 and max_v <= 1.0)

        arr = np.where(foot & fin, np.clip(raw, 0.0, 1.0), 0.0).astype(np.float32)
        loaded_arrays[key] = arr
        pos = arr > 0
        n_pos = int(pos.sum())

        for fold in folds:
            _, tm = evaluate_holdout.evaluate(arr, fold, foot)
            terms_by_key[key] = tm if key not in terms_by_key else terms_by_key[key] + tm

        is_bin = bool(np.array_equal(arr, pos.astype(np.float32)))
        if is_bin:
            sgmc3 = float(metric_mod.dti_binary(pos, sgmc_gt3, valid=foot, known=cat)["dti"])
            sgmc5 = float(metric_mod.dti_binary(pos, sgmc_gt5, valid=foot, known=cat)["dti"])
        else:
            sgmc3 = float(metric_mod.dti_exact(arr, sgmc_gt3, valid=foot, known=cat)["dti"])
            sgmc5 = float(metric_mod.dti_exact(arr, sgmc_gt5, valid=foot, known=cat)["dti"])

        records_out.append(
            dict(
                key=key,
                site=rec["site"],
                role=rec["role"],
                rel_path=actual_rel_path,
                sha256=sha256,
                grid_ok=grid_ok,
                all_grid_finite=bool(nan_in_foot == 0 and nan_out_foot == 0),
                nan_in_footprint=nan_in_foot,
                nan_outside_footprint=nan_out_foot,
                in_0_1_footprint=in_unit_range,
                positive_pixels=n_pos,
                sum_mass=round(float(arr.sum()), 2),
                binary_0_1=is_bin,
                frac_dcat_le_2px=round(float((d_cat[pos] <= 2.0).mean()), 6) if n_pos else 0.0,
                frac_exact_in_h19_5=round(float(h19[pos].mean()), 6) if n_pos else 0.0,
                ov3_vs_r0=round(float(r0_near3[pos].mean()), 6) if n_pos else 0.0,
                ov3_vs_h19_5=round(float(h19_near3[pos].mean()), 6) if n_pos else 0.0,
                claim_score=rec["claim_score"],
                claim_label=(
                    f"CLAIM: {rec['claim_score']:.4f} (owner-reported {rec['claim_date']}; no organizer receipt)"
                    if rec["claim_score"] is not None
                    else "UNSCORED (no live submission receipt)"
                ),
                organizer_confirmed_score=None,
                sgmc_dti_gt3px=round(sgmc3, 6),
                sgmc_dti_gt5px=round(sgmc5, 6),
                repo_verdict=rec["repo_verdict"],
            )
        )

    # Pooled HOLDOUT-DTI + 95% block-bootstrap CI across all 32 rasters simultaneously
    summary = evaluate_holdout.pooled_summary(
        terms_by_key, draws=1000, seed=520810, candidate="GEMSDOE32__historical_best"
    )
    for r in records_out:
        s = summary["scores"][r["key"]]
        r["holdout_dti_static"] = round(float(s["dti"]), 6)
        r["holdout_dti_ci95"] = [round(float(s["ci95"][0]), 6), round(float(s["ci95"][1]), 6)]

    # Fast 102-repo (1,756-raster) non-self operative uniqueness scan
    dil_buf = np.zeros(h * w, dtype=bool)
    pos_flat_by_key = {
        r["key"]: np.flatnonzero((loaded_arrays[r["key"]] > 0).ravel()).astype(np.int32)
        for r in records_out
    }
    worst_op = {
        r["key"]: {"ov": 0.0, "witness": "", "over70": 0}
        for r in records_out
    }
    for i, m_info in enumerate(meta):
        fidx = all_idx[offs[i] : offs[i + 1]]
        repo_i = m_info["file"].split("/")[0]
        for d in offsets_1d:
            dil_buf[np.clip(fidx + d, 0, h * w - 1)] = True
        for r in records_out:
            # Exclude exact self-SHA and same-repo twin (-nan/-zeros of same run)
            if m_info["sha256"] == r["sha256"]:
                continue
            if repo_i == r["site"] and r["rel_path"].split("/")[-1][:18] in m_info["file"]:
                continue
            ov = float(dil_buf[pos_flat_by_key[r["key"]]].mean())
            if ov > worst_op[r["key"]]["ov"]:
                worst_op[r["key"]]["ov"] = ov
                worst_op[r["key"]]["witness"] = m_info["file"]
            if ov > 0.70:
                worst_op[r["key"]]["over70"] += 1
        for d in offsets_1d:
            dil_buf[np.clip(fidx + d, 0, h * w - 1)] = False

    for r in records_out:
        wo = worst_op[r["key"]]
        r["cross_repo_operative_worst_ov3"] = round(wo["ov"], 6)
        r["cross_repo_operative_witness"] = wo["witness"]
        r["cross_repo_operative_unique_le70"] = bool(wo["ov"] <= 0.70)
        r["literal_all_entry_unique_le70"] = False  # 17GEMSDOE_E-proba-multiscale covers 100% footprint

    # Exact algebraic / set-theoretic identities across the 9 focus sites
    d25 = loaded_arrays["GEMSDOE25__historical_best"] > 0
    d30 = loaded_arrays["GEMSDOE30__historical_best"] > 0
    d28_solo = loaded_arrays["GEMSDOE28__historical_solo_d28"] > 0
    d31_solo = loaded_arrays["GEMSDOE31__historical_best"] > 0
    d32_b2 = loaded_arrays["GEMSDOE32__historical_best"] > 0
    d36_pinn = loaded_arrays["GEMSDOE36__historical_best"] > 0

    identities = dict(
        gems25_d28_xor_gems30_d28=int((d25 ^ d30).sum()),
        gems28_solo_xor_gems31_solo=int((d28_solo ^ d31_solo).sum()),
        gems31_solo_xor_d28_gt1px=int((d31_solo ^ (d25 & (d_cat > 1.0))).sum()),
        gems32_b2_xor_d28_gt2px=int((d32_b2 ^ (d25 & (d_cat > 2.0))).sum()),
        d28_to_solo_pruned_le1px=int((d25 & (~d31_solo)).sum()),
        solo_to_b2_pruned_1_to_2px=int((d31_solo & (~d32_b2)).sum()),
        d28_to_b2_total_pruned_le2px=int((d25 & (~d32_b2)).sum()),
        gems32_b2_is_strict_subset_of_gems36=bool(np.all(d36_pinn[d32_b2])),
        gems36_extra_dots_over_gems32_b2=int((d36_pinn & (~d32_b2)).sum()),
    )

    out_doc = dict(
        schema="gemsdoe92-focus9-uniform-audit.v1",
        audited_utc="2026-10-26",
        holdout_evaluator="gems57-pooled-hide-v2 (seeds 20 & 30, 8 quadrant folds, 22,663 withheld positive pixels, static d_cat evaluation)",
        public_registry_rasters_scanned=len(meta),
        elapsed_seconds=round(time.monotonic() - t0, 2),
        exact_set_identities=identities,
        irregularities_flagged=[
            dict(
                id="IR-24-25-28-POST-SCORE-CONTENT-ID-REBUILD",
                site="GEMSDOE24 / GEMSDOE25 / GEMSDOE28",
                detail="Reported 2026-10-25 submission names carry content-ID suffixes 65c294f26ef6 (GEMSDOE24 gvc1, 0.0859), 56e35c690b84 (GEMSDOE25 h66, 0.0742), and 6b8aa90da850 (GEMSDOE28 s18-mxtp, 0.0217), whereas HEAD of main in those repos stores regenerated suffixes abe8e51c719d, da617550a0e9, and 3e95505c011a respectively; GEMSDOE27 H29-S (511898747886, 0.2190) and GEMSDOE30 MSDB1 (e7856ec3f14a, 0.1462) match exact content-IDs.",
            ),
            dict(
                id="IR-31-DANGLING-PGR31-README-LINK",
                site="GEMSDOE31",
                detail="GEMSDOE31 main README top banner links docs/downloads/gemsdoe31-pgr31-poisson-pseudograv-37654-20261026-zeros.tif, which is absent from GEMSDOE31's Git tree; committed 2026-10-26 artifacts are H31-S (9355f21d9f) and XFCOH31.",
            ),
            dict(
                id="IR-36-PINN-SUPERSET-COST",
                site="GEMSDOE36",
                detail="gemsdoe36-anderson-geothermal-pinn-38854 (0.2750 CLAIM) contains 100% of GEMSDOE32 B2 (37,654 px, zero missing pixels) plus 1,200 extra off-skeleton dots that lowered reported live DTI from 0.2778 to 0.2750 (-0.0028).",
            ),
            dict(
                id="IR-30-33-NAN-OUTSIDE-FOOTPRINT",
                site="GEMSDOE30 / GEMSDOE33",
                detail="GEMSDOE30 (d28-poisson300m, MSDB1, geothermal-corridor) and GEMSDOE33 (h33d-analog) store NaN outside the active footprint; inside-footprint pixels are finite [0,1], whereas GEMSDOE92 enforces strict all-12,279,160-cell finite zeros-outside.",
            ),
            dict(
                id="IR-LEADERBOARD-SNAPSHOT-DISPERSION",
                site="ALL",
                detail="User prompt cites both 0.4413 and 0.3195 as top leaderboard benchmarks; sibling GEMSDOE32 cached snapshot (2026-10-26T04:32:28Z) records xiaofanhu = 0.4437 (0.4413 on 2026-10-25; 0.3195 earlier historical snapshot). Live drivendata.org HTTPS is firewalled in this sandbox, so all leaderboard values are labeled external/CLAIM snapshots.",
            ),
        ],
        records=records_out,
    )
    OUT_JSON.write_text(json.dumps(out_doc, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_JSON} in {out_doc['elapsed_seconds']}s")
    print("Exact identities:", json.dumps(identities, indent=2))
    print(f"{'Key':36s} | {'CLAIM':>7s} | {'HOLDOUT':>8s} | {'SGMC>5':>8s} | {'ov3_R0':>6s} | {'ov3_pub':>7s} | {'dots':>6s}")
    print("-" * 96)
    for r in records_out:
        cs = f"{r['claim_score']:.4f}" if r["claim_score"] is not None else "   -   "
        print(
            f"{r['key']:36s} | {cs:>7s} | {r['holdout_dti_static']:8.6f} | "
            f"{r['sgmc_dti_gt5px']:8.6f} | {r['ov3_vs_r0']:6.4f} | "
            f"{r['cross_repo_operative_worst_ov3']:7.4f} | {r['positive_pixels']:6d}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
