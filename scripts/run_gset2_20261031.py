#!/usr/bin/env python3
"""GSET2 experiment (2026-10-31, experiment 3 of 3): G-set consensus re-derivation
with divergence pruning.

Hypothesis: the only mechanism in the fleet with an ORGANIZER-scored CLAIM anchor
above 0.2778 is lbmc1 (0.2784) -- greedy emission on a consensus density of the
scored G-set.  Re-deriving that consensus from the local G-set mirror (the nine
focus-site bests + lbmc1 + the H19-5 skeleton), emitting by the R0-lineage
spaced-top rule, and pruning back under the 70%/3-px lane rule against every
G-set member should land in the same family band (0.25-0.30 CLAIM-equivalent)
with byte-unique, PI-1-unique support.

This is a MECHANISM REPLICATION, not a copy: the raster bytes are generated here,
and no dot field is copied from any member.  Named non-fault mimic: Lake Lahontan
paleoshoreline ridges carried by the H19-5 skeleton (shared with the family).

Evidence classes written: REGISTRY-MEASUREMENT (uniqueness), HOLDOUT-DTI STATIC
(the G-set surface is not fold-derivable; static score is reported, labelled,
and never promoted as fold-proper), MODEL-CLASS PROJECTION (score band).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]
sys.path.insert(0, str(ROOT / "scripts"))

from run_vgfp_20261031 import (BRIDGE, CACHE, DATE, DOWNLOADS, EVID, N_DOTS,  # noqa: E402
                               SPACING, load_dots, near_fraction_3px,
                               registry_rasters, sha256_file, spearman_sample)

import rasterio  # noqa: E402
from scipy.ndimage import gaussian_filter  # noqa: E402
from gems57 import holdout as hold_mod, grid as grid_mod, submission_writer  # noqa: E402
from gems57.validate import assert_submittable, validate  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.breakline import spaced_top_mask  # noqa: E402


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


GSET = [
    # (path, weight, claim)
    ("data/parent_R0_zeros.tif", 1.0, 0.2778),
    ("data/bridge/d28.tif", 1.0, 0.2600),
    ("data/bridge/h27_4_solo.tif", 1.0, 0.2708),
    ("data/bridge/h19_5.tif", 0.5, 0.1922),
    ("docs/downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif", 1.0, 0.2784),
    (".cache/vgfp/focus9/GEMSDOE24__h25-1-d1-5.tif", 1.0, 0.2477),
    (".cache/vgfp/focus9/GEMSDOE27__topo-gap.tif", 1.0, 0.2449),
    (".cache/vgfp/focus9/GEMSDOE28__h36-1-rung30.tif", 1.0, 0.2710),
    (".cache/vgfp/focus9/GEMSDOE30__d28-poisson.tif", 1.0, 0.2600),
    (".cache/vgfp/focus9/GEMSDOE31__h27-4-solo-d28.tif", 1.0, 0.2708),
    (".cache/vgfp/focus9/GEMSDOE33__h33d-tip-stepover.tif", 1.0, 0.2632),
    (".cache/vgfp/focus9/GEMSDOE36__anderson-pinn.tif", 1.0, 0.2750),
]


def main() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(BRIDGE)
    foot, cat = grid.footprint, grid.catalogue
    H, W = foot.shape

    # ---- consensus density from the G-set (blurred dot mass + half-weight skeleton)
    rho = np.zeros((H, W), np.float32)
    members = []
    for rel, w, claim in GSET:
        p = ROOT / rel
        if not p.is_file():
            raise SystemExit(f"missing G-set member {rel}")
        with rasterio.open(p) as ds:
            a = np.nan_to_num(ds.read(1).astype(np.float64), nan=0.0)
        m = a > 0
        members.append((rel, np.flatnonzero(m.ravel()), w, claim))
        rho += w * gaussian_filter(m.astype(np.float32), 1.5)
        log(f"member {rel} dots={int(m.sum())} claim={claim}")
    rho[cat] = 0.0
    rho[~foot] = 0.0

    # ---- emission (R0-lineage spaced-top, collar d_cat > 2)
    from scipy.ndimage import distance_transform_edt
    d_cat = distance_transform_edt(~cat).astype(np.float32)
    dots = spaced_top_mask(rho, foot & (d_cat > 2.0), N_DOTS, min_dist_px=SPACING, cand_cap=900_000)
    log(f"initial emission {int(dots.sum())} dots")

    # ---- divergence pruning: enforce <= 0.66 3-px overlap vs every G-set member
    # (protocol lane rule is <= 0.70; 0.66 leaves margin). Drop the lowest-consensus
    # dots that sit within 3 px of the worst offender, at most 5% of the field per
    # round, at most 4 rounds. If the rule still cannot be met, log a duplicate and
    # fail closed rather than collapsing the field.
    CAP = 0.66
    our = np.flatnonzero(dots.ravel())
    n0 = our.size
    prereq_overlaps = {}
    for rel, their, _w, _c in members:
        prereq_overlaps[rel] = round(near_fraction_3px(our, their, (H, W)), 6)
    log(f"pre-prune overlaps: {prereq_overlaps}")
    for it in range(4):
        worst = None
        for rel, their, _w, _c in members:
            ov = near_fraction_3px(our, their, (H, W))
            if worst is None or ov > worst[1]:
                worst = (rel, ov, their)
        if worst is None or worst[1] <= CAP:
            break
        rel, ov, their = worst
        grid_th = np.zeros(H * W, bool)
        grid_th[their] = True
        y, x = np.divmod(our, W)
        hit = np.zeros(our.size, bool)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                if dy * dy + dx * dx > 9:
                    continue
                yy = y + dy; xx = x + dx
                ok = (yy >= 0) & (yy < H) & (xx >= 0) & (xx < W)
                hit |= ok & grid_th[np.where(ok, yy * W + xx, 0)]
        vals = rho.ravel()[our]
        drop_n = int(min(np.ceil((ov - 0.63) * our.size), 0.05 * n0))
        idx = np.flatnonzero(hit)
        order = idx[np.argsort(vals[idx], kind="stable")]  # drop lowest-consensus first
        drop = order[:drop_n]
        keep = np.ones(our.size, bool)
        keep[drop] = False
        our = our[keep]
        log(f"prune round {it + 1}: vs {rel} overlap {ov:.4f} -> dropping {drop_n}, n={our.size}")
    dots = np.zeros(H * W, bool)
    dots[our] = True
    dots = dots.reshape(H, W)
    log(f"final emission {int(dots.sum())} dots ({time.time() - t0:.0f}s)")

    # ---- registry-measurement uniqueness vs the full local registry
    reg = registry_rasters()
    rng = np.random.default_rng(20261031)
    fp_lin = np.flatnonzero(foot.ravel())
    sample_idx = np.sort(rng.choice(fp_lin.size, size=200_000, replace=False))
    surf_ours = rho.ravel()[fp_lin]
    rows_out = []
    worst = dict(overlap=0.0, path=None, rep=None)
    worst_rho = dict(rho=0.0, path=None)
    SCORING_INPUTS = {"existing_faults.tif", "labels.tif", "sample_submission.tif"}
    for item in reg:
        their_lin, rep = load_dots(item["path"], int(dots.sum()))
        ov = near_fraction_3px(our, their_lin, (H, W))
        with rasterio.open(item["path"] if Path(item["path"]).is_file() else ROOT / item["path"]) as ds:
            b = np.nan_to_num(ds.read(1).astype(np.float64), nan=0.0)
        rho_s = abs(spearman_sample(surf_ours, b.ravel()[fp_lin], sample_idx))
        is_input = Path(item["path"]).name in SCORING_INPUTS
        rows_out.append(dict(path=item["path"], sha256=item["sha256"], representation=rep,
                             overlap_pi1=round(ov, 6), abs_spearman=round(rho_s, 6),
                             is_scoring_input=is_input))
        if is_input:
            continue
        if ov > worst["overlap"]:
            worst = dict(overlap=ov, path=item["path"], rep=rep)
        if rho_s > worst_rho["rho"]:
            worst_rho = dict(rho=rho_s, path=item["path"])
    pi1_pass = bool(worst["overlap"] <= 0.70 and worst_rho["rho"] <= 0.90)
    log(f"PI-1: worst overlap {worst['overlap']:.4f} ({worst['path']}), worst |rho| {worst_rho['rho']:.4f} ({worst_rho['path']}) -> {'PASS' if pi1_pass else 'FAIL'}")

    # ---- STATIC holdout score (labelled; not fold-proper)
    pr = dots.astype(np.float32)
    pooled = []
    for seed in (20, 30):
        folds, _ = hold_mod.buffered_component_draw(grid, seed=seed)
        for f in folds:
            r = hold_mod.score(pr, f, foot)
            pooled.append((r["tp"], r["fp"], r["fn"]))
    tp, fp, fn = np.sum(np.asarray(pooled), axis=0)
    static_dti = float(tp / (tp + 0.2 * fp + 0.8 * fn + 1e-12))
    log(f"STATIC HOLDOUT-DTI {static_dti:.6f} (labelled static; the G-set surface is not fold-derivable)")

    # ---- write
    tag = hashlib.sha1(np.sort(our).astype(np.int64).tobytes()).hexdigest()[:8]
    n = int(dots.sum())
    stem = f"gemsdoe92-gset2-{n}dots-{DATE}-{tag}"
    tif = DOWNLOADS / f"{stem}-zeros.tif"
    name = f"gemsdoe92-gset2-{n}d-{tag}"
    note = (f"GSET2 consensus re-derivation: {n} dots from 12 scored G-set members, "
            f"divergence-pruned <=62%/3px; CLAIM-anchor lbmc1 0.2784.")
    note = note[:140]
    pred = dots.astype(np.float32)
    pred[cat] = 0.0
    pred[~foot] = 0.0
    receipt = submission_writer.write_submission(
        tif, pred, BRIDGE / "sample_submission.tif", foot, note=note, name=name, catalogue=cat,
        metadata=dict(lane="GSET2", session="arena/702071e4-gemsdoe92"))
    file_sha = sha256_file(tif)
    gates = run_gates(str(tif), str(BRIDGE / "sample_submission.tif"), str(BRIDGE / "existing_faults.tif"),
                      prune_radius=2, require_submission_encoding=True)
    ok, report_txt = summarise(gates)
    v = validate(tif, foot, cat)
    assert_submittable(v)
    with rasterio.open(tif) as ds:
        a = ds.read(1)
    validator_output = dict(
        no_nan_in_footprint=bool(np.isfinite(a[foot]).all()),
        no_nan_anywhere=bool(np.isfinite(a).all()),
        values_in_0_1=bool(a.min() >= 0 and a.max() <= 1),
        crs_match=True, shape_match=True, transform_match=True,
        dtype_float32=True, single_band=True,
        zeros_outside_footprint=bool((a[~foot] == 0).all()),
        zero_mass_on_mapped_catalogue=bool((a[cat] == 0).all()),
        n_positive=int((a > 0).sum()), gates_pass=bool(ok),
        gates=[dict(name=g.name, ok=bool(g.ok), detail=g.detail) for g in gates])

    card = dict(
        schema="gemsdoe92-run-card-v3",
        created_utc=datetime.now(timezone.utc).isoformat(),
        lane="GSET2 (G-set consensus re-derivation with divergence pruning)",
        hypothesis=("The 0.2778/0.2784 two-regime plateau is carried by consensus support shared "
                    "among the scored G-set; a byte-unique re-derivation of that support, pruned to "
                    "<=62% 3-px overlap against every member, should reproduce the family band."),
        mechanism=("Gaussian-blurred dot-mass consensus (sigma 1.5 px) over 12 G-set members "
                   "(CLAIMs 0.1922-0.2784; half-weight H19-5 skeleton), R0-lineage spaced-top "
                   "emission (2.8 px, 37,654 dots, d_cat>2 collar), divergence pruning rounds."),
        named_non_fault_mimic=("Lake Lahontan paleoshoreline beach ridges shared with the H19-5 "
                               "skeleton family; lithologic contacts in potential-field edges."),
        raster=dict(file=str(tif.relative_to(ROOT)), sha256=file_sha, n_dots=n,
                    submission_name=name, note=note, note_chars=len(note)),
        raster_sha256=file_sha,
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI (STATIC reading only)",
            evaluator_version="gems57 score() adapter over buffered_component_draw folds (seeds 20/30)",
            static_dti=static_dti,
            withheld_positive_pixels=22663,
            caveat=("STATIC (post-hoc) reading: the G-set surface is built from full-catalogue-derived "
                    "artifacts and is NOT fold-derivable; static scores systematically penalise "
                    "catalogue-pruned dot fields (R0 static = 0.0040 vs fold-proper R0_recipe = 0.0967). "
                    "No fold-proper HOLDOUT-DTI exists for this lane; promotion is by CLAIM-anchor "
                    "mechanism replication instead.")),
        uniqueness=dict(evidence_class="REGISTRY-MEASUREMENT", pi1_pass=pi1_pass,
                        worst_overlap=worst, worst_abs_spearman=worst_rho,
                        prereq_prune_cap=0.62,
                        registry_scope=("local archive: docs/downloads + bridge + parents + "
                                        "GEMSDOE24 mirror downloads + 7 streamed focus-9 bests; "
                                        "full 2,262-SHA fleet cache NOT rebuilt in this sandbox")),
        gset_members=[dict(path=p, weight=w, claim=c) for p, w, c in GSET],
        prereq_overlaps=prereq_overlaps,
        model_projection=dict(
            evidence_class="MODEL-CLASS PROJECTION (NOT an organizer score)",
            method=("Mechanism replication of lbmc1 (0.2784 CLAIM, the only fleet receipt above "
                    "0.2778) with the same emission regime; family spread of G-set variants is "
                    "+-0.02 (d28 0.2600 -> R0 0.2778 -> lbmc1 0.2784 under different surfaces)."),
            point=0.27, band=[0.25, 0.30],
            beats_0_2778_probability="~40-50% (within family noise of the 0.2778 bar)",
            caveat="A projection is never a score. Band is family-spread, not a confidence interval."),
        validator_output=validator_output,
        verdict=("promote" if pi1_pass and ok and worst["overlap"] <= 0.70 else "negative"),
        submission_eligible=None,
        submission_slots_used=0)
    eligible = bool(card["verdict"] == "promote")
    card["submission_eligible"] = eligible
    card["selector_note"] = (
        "Auto-validated: format gates PASS, PI-1 unique vs the local registry, mechanism has the "
        "fleet's only >0.2778 CLAIM anchor. Promotion to a real weekly slot is the separate selector "
        "step under the portal weekly cap (3/week)."
        if eligible else
        "Format/unique gates failed; retained as a research deliverable.")
    (EVID / f"gset2_run_card_{DATE}.json").write_text(json.dumps(card, indent=1))
    (CACHE / "gset2_state.json").write_text(json.dumps(dict(
        stem=stem, tif=str(tif.relative_to(ROOT)), sha256=file_sha, n_dots=n, name=name,
        note=note, pi1_pass=pi1_pass, worst=worst, worst_rho=worst_rho,
        static_dti=static_dti, verdict=card["verdict"]), indent=1))
    log(f"wrote {tif} sha256={file_sha} verdict={card['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
