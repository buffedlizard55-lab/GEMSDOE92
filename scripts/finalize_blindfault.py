#!/usr/bin/env python3
"""BLINDFAULT finalizer: local + (cached) public registry uniqueness with the dual
(literal / matched-budget) reading, submission_writer packaging of all three
pre-registered arms, and the Protocol Rule 5 run card.

Inputs: .cache/blindfault/{dots_<arm>.npy, S_<arm>_full.npy}, evidence/blindfault_holdout.json
Outputs: docs/downloads/gemsdoe92-blindfault-<arm>-...-zeros.{tif,zip}, *-audit.json,
         evidence/blindfault_uniqueness.json, evidence/blindfault_run_card.json,
         docs/downloads/blindfault_run_card.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems57 import grid as grid_mod, submission_writer, uniqueness as U, validate as V  # noqa: E402

CACHE = ROOT / ".cache" / "blindfault"
INPUTS = ROOT / ".cache" / "gems_inputs"
PUBLIC = ROOT / ".cache" / "gemsdoe_public_registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
HOLDOUT_JSON = EVIDENCE / "blindfault_holdout.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def local_registry(exclude_stems):
    files = []
    for d in (DOWNLOADS, ROOT / "releases", ROOT / "data", ROOT / "data" / "bridge"):
        for p in sorted(d.glob("*.tif")):
            if any(p.name.startswith(s) for s in exclude_stems):
                continue
            files.append(("local:" + str(p.relative_to(ROOT)), p))
    return files


def public_registry():
    inv = PUBLIC / "repo_inventory.json"
    if not inv.is_file():
        return [], dict(status="public inventory absent", complete=False)
    trees = json.loads(inv.read_text())
    seen, files = set(), []
    n_paths = 0
    missing = 0
    for t in trees:
        for f in t.get("tifs", []):
            n_paths += 1
            if f["sha"] in seen:
                continue
            seen.add(f["sha"])
            p = PUBLIC / f"{f['sha']}.tif"
            if p.is_file():
                files.append((f"{t['repo']}/{f['path']}", p))
            else:
                missing += 1
    return files, dict(status="cached Git-blob inventory (102 owner repos)", repos=len(trees),
                       tif_paths=n_paths, unique_blobs=len(seen), cached_blobs=len(files),
                       missing_blobs=missing, complete=(missing == 0))


def compare(cands, surfaces, foot, registry, expected):
    """cands: arm -> bool dots; surfaces: arm -> float32 surface. Returns rows per arm."""
    rows = {a: [] for a in cands}
    foot_idx = np.flatnonzero(foot)
    # Spearman on a fixed 400k-cell footprint subsample (SE of rho ~ 0.0016; threshold is 0.90)
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=400_000, replace=False))
    surf_rank = {}
    for a, S in surfaces.items():
        surf_rank[a] = S.ravel()[sub].astype(np.float32)
    skipped = []
    for label, path in registry:
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    skipped.append(dict(file=label, reason="grid/band mismatch"))
                    continue
                raw = ds.read(1)
        except Exception as exc:  # unreadable
            skipped.append(dict(file=label, reason=str(exc)[:80]))
            continue
        vals = np.nan_to_num(raw.astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        del raw
        support = (vals > 0) & foot
        n_sup = int(support.sum())
        if n_sup == 0:
            skipped.append(dict(file=label, reason="empty"))
            continue
        near_lit = U._near(support, 3.0)
        tv = vals.ravel()[sub]
        for a, m in cands.items():
            k = int(m.sum())
            lit = float(near_lit[m].mean())
            if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
                mb, rep = lit, "dot_field"
            else:
                mb = float(U._near(U.matched_budget_support(vals, foot, k), 3.0)[m].mean())
                rep = "continuous_surface"
            rho = float(spearmanr(surf_rank[a], tv).statistic) if (n_sup > 1 and surf_rank[a] is not None) else float("nan")
            rows[a].append(dict(file=label, their_dots=n_sup, my_dots=k, representation=rep,
                                literal_forward_overlap=round(lit, 6),
                                matched_budget_forward_overlap=round(mb, 6),
                                spearman_surface=None if not np.isfinite(rho) else round(rho, 6),
                                spearman_scope="400k-cell footprint subsample of the pre-placement surface"))
        del vals, support, near_lit
    return rows, skipped


def package(arms, hold, cands, foot, cat, best, primary_scores):
    built = {}
    for a in arms:
        stem = hold["deployment"][a]["stem"]
        tif = DOWNLOADS / f"{stem}.tif"
        sc = primary_scores[a]
        note = f"BLINDFAULT {a}: 37654 LOQO dots, slope-blind cov-shift wts; HOLDOUT-DTI {sc['dti']:.6f}"
        name = f"GEMSDOE92-BLINDFAULT-{a}-20261025"
        assert len(note) <= 140 and len(name) <= 140
        if tif.is_file():
            log(f"  {a}: {tif.name} already exists (pinned bytes); not rewriting")
            receipt = json.loads((CACHE / f"{stem}.receipt.json").read_text())
        else:
            receipt = submission_writer.write_submission(
                tif, cands[a].astype(np.float32), INPUTS / "bridge" / "sample_submission.tif", foot,
                note=note, name=name, catalogue=cat,
                metadata=dict(lane="BLINDFAULT", arm=a, hypothesis_doc="docs/HYPOTHESES_20261025_BLINDFAULT.md"))
            (CACHE / f"{stem}.receipt.json").write_text(json.dumps(receipt, indent=2))
            aux = tif.with_suffix(".json")
            if aux.is_file():
                aux.replace(CACHE / aux.name)
        if a != best:
            z = tif.with_suffix(".zip")
            if z.is_file():
                z.unlink()
        # independent disk re-read validation (fail closed)
        v = V.validate(tif, foot, cat)
        V.assert_submittable(v)
        with rasterio.open(tif) as ds:
            arr = ds.read(1)
        assert arr.dtype == np.float32 and arr.shape == foot.shape
        assert np.isfinite(arr).all() and arr.min() >= 0 and arr.max() <= 1
        assert int((arr > 0).sum()) == 37654 and not ((arr > 0) & ~foot).any() and not ((arr > 0) & cat).any()
        built[a] = dict(file=f"docs/downloads/{tif.name}", sha256=sha256_file(tif), bytes=tif.stat().st_size,
                        zip=(f"docs/downloads/{stem}.zip" if a == best else None),
                        zip_sha256=(sha256_file(tif.with_suffix('.zip')) if a == best else None),
                        submission_name=name, note=note, note_chars=len(note), validator=v)
        log(f"  built {a}: {tif.name} sha256={built[a]['sha256'][:16]} validator ok")

    return built


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-public", action="store_true")
    ap.add_argument("--max-public", type=int, default=0, help="0 = all cached blobs")
    args = ap.parse_args()

    hold = json.loads(HOLDOUT_JSON.read_text())
    arms = list(hold["deployment"])
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ref:
        expected = (ref.shape, ref.crs, ref.transform)

    cands = {a: np.load(CACHE / f"dots_{a}.npy") for a in arms}
    surfaces = {a: np.load(CACHE / f"S_{a}_full.npy") for a in arms}
    stems = [hold["deployment"][a]["stem"] for a in arms]

    # ---- 0. package via submission_writer FIRST (format gates do not depend on registry scans) ----
    primary_scores = hold["holdout"]["primary_dvis2"]["scores"]
    best = max(arms, key=lambda a: primary_scores[a]["dti"])
    built = package(arms, hold, cands, foot, cat, best, primary_scores)

    # ---- 1. local registry (complete) ----
    reg_local = local_registry(exclude_stems=stems)
    log(f"local registry: {len(reg_local)} rasters")
    rows_local, skipped_local = compare(cands, surfaces, foot, reg_local, expected)

    # ---- 2. public registry (cached blobs) ----
    pub_files, pub_meta = ([], dict(status="skipped by flag", complete=False)) if args.no_public else public_registry()
    if args.max_public and len(pub_files) > args.max_public:
        pub_files = pub_files[: args.max_public]
        pub_meta["complete"] = False
        pub_meta["status"] += f" (truncated to {args.max_public})"
    log(f"public registry: {len(pub_files)} cached rasters ({pub_meta})")
    rows_pub, skipped_pub = compare(cands, surfaces, foot, pub_files, expected) if pub_files else ({a: [] for a in arms}, [])

    # ---- 2b. specificity proof for the dense-witness policy (#IR-92-DENSE-WITNESS-MATCHED-BUDGET) ----
    specificity = None
    witness = PUBLIC / "374c88b1da2b803e2ed160de467fd71ae114010d.tif"   # 17GEMSDOE E-proba-multiscale (Git blob SHA-1)
    if witness.is_file():
        with rasterio.open(witness) as ds:
            wv = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
        with rasterio.open(ROOT / "data/parent_R0_zeros.tif") as ds:
            r0 = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
        with rasterio.open(INPUTS / "bridge" / "sample_submission.tif") as ds:
            samp = np.nan_to_num(ds.read(1), nan=0.0)
        samp_pos = (samp > 0) & foot
        specificity = dict(
            witness="17GEMSDOE/docs/downloads/17GEMSDOE_E-proba-multiscale_20260930T044527Z.tif",
            witness_git_blob_sha1="374c88b1da2b803e2ed160de467fd71ae114010d",
            witness_positive_footprint_cells=int(((wv > 0) & foot).sum()), footprint_cells=int(foot.sum()),
            R0_parent_literal_overlap=U.dual_overlap(r0, wv, foot)["literal_forward_overlap"],
            R0_parent_matched_budget_overlap=U.dual_overlap(r0, wv, foot)["matched_budget_forward_overlap"],
            sample_submission_positive_cells=int(samp_pos.sum()),
            sample_submission_literal_overlap=(U.dual_overlap(samp_pos, wv, foot)["literal_forward_overlap"] if samp_pos.any() else None),
            note=("If the organiser-scored R0 parent (a distinct submission by construction) has literal overlap 1.0 with the witness, "
                  "the literal reading has zero specificity against this raster and cannot be a lane-duplication test."))
        for a in arms:
            d = U.dual_overlap(cands[a], wv, foot)
            specificity[f"{a}_literal_overlap"] = d["literal_forward_overlap"]
            specificity[f"{a}_matched_budget_overlap"] = d["matched_budget_forward_overlap"]
        del wv
        log(f"dense-witness specificity: R0 literal={specificity['R0_parent_literal_overlap']:.3f} "
            f"matched-budget={specificity['R0_parent_matched_budget_overlap']:.3f}")

    # ---- 3. cross-arm (sibling) overlap, informational ----
    sib = {}
    for a in arms:
        for b in arms:
            if a != b:
                sib[f"{a}_vs_{b}"] = round(float(U._near(cands[b], 3.0)[cands[a]].mean()), 6)

    uniq = {}
    for a in arms:
        dl = U.dual_reading_decision(rows_local[a])
        dp = U.dual_reading_decision(rows_pub[a]) if rows_pub[a] else None
        uniq[a] = dict(local=dl, public=dp,
                       top_local=sorted(rows_local[a], key=lambda r: -r["matched_budget_forward_overlap"])[:5],
                       top_public=sorted(rows_pub[a], key=lambda r: -r["matched_budget_forward_overlap"])[:8],
                       top_public_rho=sorted([r for r in rows_pub[a] if r["spearman_surface"] is not None],
                                             key=lambda r: -abs(r["spearman_surface"]))[:5])
        log(f"  {a}: local worst MB={dl['worst_matched_budget_forward_overlap']:.4f} ({dl['worst_matched_budget_file']}), "
            f"lit={dl['worst_literal_forward_overlap']:.4f}, |rho|={dl['worst_abs_spearman']:.4f}"
            + (f" | public worst MB={dp['worst_matched_budget_forward_overlap']:.4f} ({dp['worst_matched_budget_file']}), "
               f"lit={dp['worst_literal_forward_overlap']:.4f}, |rho|={dp['worst_abs_spearman']:.4f}" if dp else ""))
    (EVIDENCE / "blindfault_uniqueness.json").write_text(json.dumps(dict(
        schema="gemsdoe92-blindfault-uniqueness.v1", lane="BLINDFAULT",
        policy="#IR-92-DENSE-WITNESS-MATCHED-BUDGET: literal and matched-budget readings reported; operative = matched-budget for >150k-px surfaces",
        local_registry_files=len(reg_local), public_registry=pub_meta, skipped_local=skipped_local,
        skipped_public=skipped_pub[:50], sibling_overlap=sib, dense_witness_specificity=specificity, by_arm=uniq,
        rows_local={a: rows_local[a] for a in arms}, rows_public={a: rows_pub[a] for a in arms}), indent=1) + "\n")

    # ---- 4. audit sidecars ----
    for a in arms:
        stem = hold["deployment"][a]["stem"]
        sc = primary_scores[a]
        audit = dict(schema="gemsdoe92-blindfault-audit.v1", lane="BLINDFAULT", arm=a, **built[a],
                     holdout_primary=sc, holdout_static=hold["holdout"]["static_dcat2_deployment"]["scores"][a],
                     holdout_low_conspicuity=hold["holdout"]["low_conspicuity_tercile"]["scores"][a],
                     uniqueness=dict(local=uniq[a]["local"], public=uniq[a]["public"]))
        (DOWNLOADS / f"{stem[:-len('-zeros')]}-audit.json").write_text(json.dumps(audit, indent=2) + "\n")

    # ---- 5. run card ----
    # ---- 5. run card ----
    best_sc = primary_scores[best]
    ref = hold["holdout_best_reference"]
    flat = primary_scores.get("blindflat")
    paired = hold["holdout"]["primary_dvis2"].get("paired", {})
    u_best = uniq[best]
    unique_ok = (not u_best["local"]["duplicate"]) and (u_best["public"] is not None and not u_best["public"]["duplicate"]
                                                        and pub_meta.get("complete", False))
    beats_best = best_sc["dti"] > ref["dti"]
    verdict = "promote" if (beats_best and unique_ok) else "negative"
    card = dict(
        schema="gemsdoe92-run-card.v3", lane="BLINDFAULT", date="2026-10-25", primary_arm=best,
        hypothesis=("The USGS/INGENIOUS catalogue is a scarp catalogue; faults missing from it are topographically "
                    "subtle. A subsurface-only LOQO model whose positives are importance-weighted toward low-conspicuity "
                    "catalogue faults (covariate-shift correction) places dots on the subtle population that scores."),
        mechanism=("Potential-field (RTP, isostatic gravity), basement-depth, MT-conductivity gradient and geodetic strain "
                   "features; HistGradientBoosting, 4-quadrant leave-one-quadrant-out with 1.2 km guard and 500 m negative "
                   "buffer; positive weight 1/(0.1 + rank-normalised 5x5 max log-slope); 37,654 dots spaced >= 2.83 px, d_cat > 2.0."),
        named_non_fault_mimic=("Buried lithologic contacts and dykes in basin fill (potential-field edge without displacement); "
                               "lacustrine clay facies boundaries (MT edge)."),
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
                         withheld_positives=hold["withheld_positive_pixels"],
                         primary_instrument="strict draw-blind LOQO, fold-visible d_visible > 2.0, seeds 20+30, 8 folds",
                         scores={a: primary_scores[a] for a in primary_scores},
                         paired_vs_controls=paired,
                         low_conspicuity_tercile=hold["holdout"]["low_conspicuity_tercile"]["scores"],
                         static_dcat2_deployment=hold["holdout"]["static_dcat2_deployment"]["scores"],
                         repository_holdout_best=ref, beats_holdout_best=beats_best),
        leakage_canaries=dict(max_symmetric_auc=hold["leakage_canaries"]["max_symmetric_auc"],
                              all_pass_le_0p90=hold["leakage_canaries"]["all_pass"]),
        correlation_overlap_vs_registry=dict(local=u_best["local"], public=u_best["public"], public_scope=pub_meta,
                                             sibling_overlap=sib, dense_witness_specificity=specificity, overlap_with_R0_3px=hold["deployment"][best]["overlap_r0_3px"]),
        raster_sha256=built[best]["sha256"], zip_sha256=built[best]["zip_sha256"], file=built[best]["file"],
        validator_output=dict(no_nan_in_footprint=bool(built[best]["validator"]["checks"]["in_footprint_all_finite"]),
                              values_in_0_1=bool(built[best]["validator"]["checks"]["range_0_1_guaranteed"]),
                              crs_shape_transform_match=bool(built[best]["validator"]["checks"]["crs_epsg_32611"]
                                                             and built[best]["validator"]["checks"]["dimensions_3730x3292"]
                                                             and built[best]["validator"]["checks"]["transform_matches_sample_submission"]),
                              dots=37654, checks=built[best]["validator"]["checks"]),
        submission_name=built[best]["submission_name"], submission_note=built[best]["note"],
        note_chars=built[best]["note_chars"], experiments_used=f"{len(arms)}/3", weekly_slots_used=0,
        verdict=verdict,
        submission_eligible=bool(verdict == "promote"),
        verdict_reason=(f"primary HOLDOUT-DTI {best_sc['dti']:.6f} vs holdout-best {ref['dti']:.6f} ({ref['lane']}); "
                        f"unique_ok={unique_ok}"),
        organizer_confirmed=None,
        all_arms=built)
    (EVIDENCE / "blindfault_run_card.json").write_text(json.dumps(card, indent=2) + "\n")
    (DOWNLOADS / "blindfault_run_card.json").write_text(json.dumps(card, indent=2) + "\n")
    log(f"VERDICT {verdict}: {card['verdict_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
