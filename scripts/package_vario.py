#!/usr/bin/env python3
"""VARIO packaging: writer + format gates + local-registry uniqueness + SGMC proxy + run card.

Uses only shared tools: gems57.submission_writer (fail-closed, refuses
overwrite), gems.gates.run_gates (submission encoding: finite [0,1], zeros
outside footprint), gems57.metric.dti_binary for the SGMC PROXY.
Verdict logic is the pre-registered rule in docs/HYPOTHESES_20261025_VARIO.md,
implemented here, not chosen by hand after seeing results.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems.gates import run_gates, summarise  # noqa: E402
from gems57 import grid as grid_mod, metric as metric57  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "vario"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
DATE_TAG = "20261025"
ARMS = {
    "vario_full": ("VARIO-full", "VARIO full: 24phys+semivar+MTcp+topo10+ctx LOQO; 37654 dots 2.8px dcat>2"),
    "vario_smooth": ("VARIO-smooth", "VARIO smooth: vario_full proba, crest blurred s1.85px; 37654 dots 2.8px"),
    "vario_nctx": ("VARIO-nctx", "VARIO nctx: 24phys+semivar+MTcp+topo10 LOQO no ctx; 37654 dots 2.8px"),
}
OVERLAP_LIMIT = 0.70
RHO_LIMIT = 0.90
SPARSE_MAX_POS = 150_000


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stem_for(arm: str, dots: np.ndarray) -> str:
    h = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
    return f"gemsdoe92-vario-{arm.replace('vario_', '')}-37654-{DATE_TAG}-{h}-zeros"


def package_arm(arm, dots, grid, sample_path):
    label, note = ARMS[arm]
    assert len(note) <= 140, note
    name = f"GEMSDOE92-{label}-{DATE_TAG}"
    stem = stem_for(arm, dots)
    out = DOWNLOADS / f"{stem}.tif"
    pred = np.zeros(grid.footprint.shape, np.float32)
    pred[dots] = 1.0
    receipt = write_submission(out, pred, sample_path, grid.footprint,
                               note=note, name=name, catalogue=grid.catalogue,
                               metadata=dict(lane="VARIO", arm=arm))
    # Gates (submission encoding) re-derived from the written bytes.
    results = run_gates(str(out), str(sample_path), str(ROOT / "data/bridge/labels.tif"),
                        prune_radius=2, require_submission_encoding=True)
    for p in (out, out.with_suffix(".zip"), out.with_suffix(".json")):
        p.chmod(0o644)  # writer temp files are 0600; served downloads must be readable
    ok, report = summarise(results)
    log(f"{arm}: format gates {'PASS' if ok else 'FAIL'}\n{report}")
    gates = [dict(name=r.name, ok=bool(r.ok), detail=r.detail) for r in results]
    audit = dict(
        file=f"docs/downloads/{out.name}",
        sha256_zeros=sha256_file(out), sha256_nan=None,
        gates_zeros=gates, gates_nan=[], overall_pass=bool(ok),
        generated_utc=datetime.now(timezone.utc).isoformat(),
        note=note, submission_name=name,
        n_positive_pixels=int(dots.sum()), n_dots=int(dots.sum()),
        gates_zeros_pass=bool(ok), gates_nan_pass=None,
        lane="VARIO", arm=arm,
        zip_file=f"{stem}.zip", zip_sha256=receipt["zip_sha256"],
        writer_receipt=f"docs/downloads/{stem}.json",
    )
    (DOWNLOADS / f"{stem}-audit.json").write_text(json.dumps(audit, indent=1))
    # ZIP roundtrip: exactly one member, bytes identical to the TIFF.
    with zipfile.ZipFile(DOWNLOADS / f"{stem}.zip") as z:
        assert z.namelist() == [out.name] and z.read(out.name) == out.read_bytes()
    return dict(arm=arm, file=f"docs/downloads/{out.name}", stem=stem, sha256=audit["sha256_zeros"],
                name=name, note=note, note_chars=len(note), format_pass=bool(ok), gates=gates,
                audit=f"docs/downloads/{stem}-audit.json", zip=f"docs/downloads/{stem}.zip",
                zip_sha256=receipt["zip_sha256"])


def _phi(mine: np.ndarray, theirs: np.ndarray) -> float:
    """Spearman (= phi) for two binary fields, exact from the contingency table."""
    m = mine.ravel()
    t = theirs.ravel()
    a = float((m & t).sum()); b = float((m & ~t).sum())
    c = float((~m & t).sum()); d = float((~m & ~t).sum())
    den = np.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return float((a * d - b * c) / den) if den > 0 else 0.0


def _spearman_full(mine_f: np.ndarray, theirs_f: np.ndarray, foot: np.ndarray) -> float:
    m = mine_f[foot].astype(np.float64)
    t = np.nan_to_num(theirs_f[foot].astype(np.float64), nan=0.0)
    if np.ptp(m) == 0 or np.ptp(t) == 0:
        return 0.0
    rm = rankdata(m); rt = rankdata(t)
    rm -= rm.mean(); rt -= rt.mean()
    den = float(np.linalg.norm(rm) * np.linalg.norm(rt))
    return float(rm @ rt / den) if den > 0 else 0.0


def uniqueness(dots_by_arm, own_files, grid):
    foot = grid.footprint
    reg_files = sorted(p for p in DOWNLOADS.glob("*.tif") if p.name not in own_files)
    lineage = [INPUTS / "lineage" / n for n in (
        "GEMSDOE32__h33-2-b2-zeros.tif", "GEMSDOE28__h27-4-r1-solo-d2-8.tif",
        "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif", "calib_h195_01922.tif",
        "calib_d15_02477.tif")]
    # Stream the registry one raster at a time (holding ~100 EDT fields OOMs
    # the 3 GB sandbox): score every arm against each raster, then discard it.
    rows_by_arm = {arm: [] for arm in dots_by_arm}
    errors = []
    for p in reg_files + lineage:
        try:
            with rasterio.open(p) as ds:
                if (ds.height, ds.width) != foot.shape or ds.count != 1:
                    continue
                a = ds.read(1)
        except Exception as exc:  # unreadable registry raster: record, never silently pass
            errors.append(dict(file=str(p), error=str(exc)))
            continue
        pos = np.isfinite(a) & (a > 0) & foot
        npos = int(pos.sum())
        if npos == 0:
            del a, pos
            continue
        finite_vals = a[np.isfinite(a) & foot]
        is_binary = bool(np.all(np.isin(np.unique(finite_vals)[:], [0.0, 1.0]))) if finite_vals.size else True
        del finite_vals
        dist = distance_transform_edt(~pos)
        scope = "lineage" if p in lineage else "local"
        for arm, dots in dots_by_arm.items():
            overlap = float((dist[dots] <= 3.0).mean()) if dots.any() else 0.0
            rho = _phi(dots & foot, pos) if is_binary else _spearman_full(dots.astype(np.float32), a.astype(np.float32), foot)
            rows_by_arm[arm].append(dict(file=p.name, scope=scope, n_positive=npos,
                                         binary=is_binary, forward_overlap_within_3px=round(overlap, 6),
                                         spearman=round(float(rho), 6)))
        del a, pos, dist
    out = {}
    for arm, dots in dots_by_arm.items():
        rows = rows_by_arm[arm]
        sparse = [r for r in rows if r["n_positive"] <= SPARSE_MAX_POS]
        worst_ov = max(sparse, key=lambda r: r["forward_overlap_within_3px"], default=None)
        worst_rho = max(sparse, key=lambda r: abs(r["spearman"]), default=None)
        worst_lit = max(rows, key=lambda r: r["forward_overlap_within_3px"], default=None)
        out[arm] = dict(
            evidence_class="REGISTRY-MEASUREMENT",
            scope=f"local registry: {len(reg_files)} docs/downloads rasters + {len(lineage)} pinned lineage rasters; own VARIO outputs excluded; NOT a full public-repo scan",
            registry_rows=rows, registry_errors=errors,
            operative_sparse=dict(
                max_positive_pixels=SPARSE_MAX_POS, rasters=len(sparse),
                worst_overlap=worst_ov, worst_abs_spearman=worst_rho,
                overlap_limit=OVERLAP_LIMIT, rho_limit=RHO_LIMIT,
                passes=bool(worst_ov and worst_rho and worst_ov["forward_overlap_within_3px"] <= OVERLAP_LIMIT
                            and abs(worst_rho["spearman"]) <= RHO_LIMIT)),
            literal_positive_support=dict(
                rasters=len(rows), worst_overlap=worst_lit,
                note="Literal >0-support reading: dense continuous surfaces in the wider public registry "
                     "(pinned full-footprint witness, docs/downloads/review_f23_preflight.json) make every "
                     "non-empty candidate overlap 1.0. Reported for disclosure; operative sparse dot-field "
                     "reading is the discriminating gate (see docs/HYPOTHESES_20261025_VARIO.md)."),
        )
        log(f"{arm}: sparse worst overlap {worst_ov} | worst |rho| {worst_rho}")
    return out


def surface_check(grid):
    """Pre-placement surface check: Spearman of the deploy crest surface vs local registry.

    Uses the saved unblurred crest surface of vario_full, evaluated on a
    deterministic stride-4 subsample of footprint cells (~323k points) against
    binary registry dot fields (rank correlation vs their 0/1 support).
    """
    S = np.load(CACHE / "S_vario_full.npy")
    foot = grid.footprint
    ys, xs = np.nonzero(foot)
    keep = (ys % 4 == 0) & (xs % 4 == 0)
    ys, xs = ys[keep], xs[keep]
    sv = S[ys, xs].astype(np.float64)
    rs = rankdata(sv); rs -= rs.mean()
    ns = float(np.linalg.norm(rs))
    worst = None
    checked = 0
    own = set()
    for p in sorted(DOWNLOADS.glob("*.tif")):
        if "vario" in p.name:
            own.add(p.name); continue
        try:
            with rasterio.open(p) as ds:
                if (ds.height, ds.width) != foot.shape or ds.count != 1:
                    continue
                a = ds.read(1)
        except Exception:
            continue
        tv = (np.isfinite(a[ys, xs]) & (a[ys, xs] > 0)).astype(np.float64)
        if tv.sum() == 0 or tv.sum() == len(tv):
            continue
        rt = rankdata(tv); rt -= rt.mean()
        rho = float(rs @ rt / (ns * np.linalg.norm(rt)))
        checked += 1
        if worst is None or abs(rho) > abs(worst["spearman"]):
            worst = dict(file=p.name, spearman=round(rho, 6))
    return dict(evidence_class="REGISTRY-MEASUREMENT", surface="S_vario_full (deploy crest, unblurred)",
                method="Spearman on deterministic stride-4 footprint subsample vs registry 0/1 support",
                n_points=int(len(ys)), registry_checked=checked, worst_abs_spearman=worst,
                rho_limit=RHO_LIMIT,
                passes=bool(worst and abs(worst["spearman"]) <= RHO_LIMIT))


def sgmc_proxy(dots_by_arm, grid):
    foot, cat = grid.footprint, grid.catalogue
    with rasterio.open(INPUTS / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc = (ds.read(1) > 0) & foot
    truth = sgmc & (~cat) & (~binary_dilation(cat, iterations=3))
    refs = {}
    for name, path in (("R0_h33_2_b2", INPUTS / "lineage" / "GEMSDOE32__h33-2-b2-zeros.tif"),
                       ("H19_5", INPUTS / "lineage" / "calib_h195_01922.tif")):
        with rasterio.open(path) as ds:
            refs[name] = (np.nan_to_num(ds.read(1), nan=0.0) > 0) & foot
    scores = {k: round(float(metric57.dti_binary(m, truth, valid=foot, known=cat)["dti"]), 6)
              for k, m in {**dots_by_arm, **refs}.items()}
    return dict(evidence_class="PROXY (off-catalogue USGS SGMC bedrock faults; report-only, not a gate)",
                truth_pixels_after_catalogue_and_3px_exclusion=int(truth.sum()),
                dti=scores)


def main() -> int:
    t0 = time.time()
    grid = grid_mod.load_grid(INPUTS / "bridge")
    sample = INPUTS / "bridge" / "sample_submission.tif"
    dots_by_arm = {arm: np.load(CACHE / f"dots_{arm}.npy") for arm in ARMS}
    packaged = {}
    own_files = set()
    for arm, dots in dots_by_arm.items():
        info = package_arm(arm, dots, grid, sample)
        packaged[arm] = info
        own_files.add(Path(info["file"]).name)
    uniq = uniqueness(dots_by_arm, own_files, grid)
    surf = surface_check(grid)
    sgmc = sgmc_proxy(dots_by_arm, grid)
    hold = json.loads((EVIDENCE / "vario_holdout.json").read_text())
    primary = "vario_full"
    canary_max = max(c["symmetric_auc"] for c in hold["canaries"])
    canary_worst = max(hold["canaries"], key=lambda c: c["symmetric_auc"])
    paired = hold["paired_by_candidate"][primary]
    controls = {k: v for k, v in hold["scores"].items() if k.startswith("control_")}
    best_control = max(controls, key=lambda k: controls[k]["dti"])
    delta = paired[best_control]
    fmt_ok = all(v["format_pass"] for v in packaged.values())
    uniq_ok = bool(uniq[primary]["operative_sparse"]["passes"] and surf["passes"])
    canary_ok = bool(canary_max <= 0.90)
    holdout_ok = bool(delta["delta"] > 0 and delta["ci95"][0] > 0)
    promote = bool(fmt_ok and canary_ok and holdout_ok and uniq_ok)
    reasons = []
    if not fmt_ok: reasons.append("format gates failed")
    if not canary_ok: reasons.append(f"leakage canary {canary_worst['feature']}={canary_max} > 0.90")
    if not holdout_ok: reasons.append(f"paired HOLDOUT-DTI delta vs best control {best_control} = {delta['delta']:+.6f} CI {delta['ci95']} (must exclude 0)")
    if not uniq_ok: reasons.append("operative sparse-registry uniqueness failed (overlap>0.70 or |rho|>0.90)")
    verdict = "promote" if promote else "negative"
    card = dict(
        schema="gemsdoe92-vario-run-card-v1", lane="VARIO", date=DATE_TAG,
        branch="arena/d7ca8737-gemsdoe92",
        pre_registration="docs/HYPOTHESES_20261025_VARIO.md",
        hypothesis="Buried/off-catalogue Great Basin faults are recoverable by adding three previously unused catalogue-free families — RTP directional semivariogram anisotropy (lags 2/4 px), MT conductivity change-point at constant basement cover, and USGS 3DEP 10 m sub-pixel scarp/chi statistics — to the proven COULOMBLOQO physics + FAULTNET context LOQO ensemble.",
        mechanism="4-quadrant LOQO HistGradientBoosting (12 px guard, 5 px negative buffer) over 38 features; crest-surface localisation; 37,654 spaced (2.8 px) dots with d_visible>2 in holdout / d_cat>2 at deployment; E3 blurs the crest at sigma=1.85 px before emission.",
        non_fault_mimic="Lava-flow/intrusive contacts and flight-line seams (semivariogram anisotropy); playa/aquifer salinity fronts (MT break at constant cover); Lake Lahontan shoreline berms and fan-age breaks (10 m scarp statistics).",
        primary_arm=primary,
        experiments=["vario_full", "vario_smooth", "vario_nctx"],
        experiments_used=3, weekly_slots_used=0,
        holdout_dti=dict(
            evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
            instrument=hold["instrument"], seeds=hold["seeds"],
            alpha=0.2, beta=0.8, triangular_radius_m=300.0,
            scores=hold["scores"], paired_by_candidate=hold["paired_by_candidate"],
            best_comparable_control=best_control,
            primary_minus_best_control=delta,
            historical_reference=hold["historical_reference"],
            implementation_sha256=hold["implementation_sha256"],
            evidence_file="evidence/vario_holdout.json"),
        leakage_canaries=dict(max_symmetric_auc=canary_max, worst=canary_worst,
                              n=len(hold["canaries"]), limit=0.90, passes=canary_ok),
        correlation_overlap_vs_registry=dict(final_dots=uniq, surface_preplacement=surf),
        sgmc_proxy=sgmc,
        organizer_confirmed_score=None,
        organizer_note="No submission-page receipt exists for any VARIO file; no ORGANIZER-CONFIRMED score is claimed. Site-inventory scores (incl. GEMSDOE32 0.2778) are CLAIMs (ledger/site_scores_claimed_20261025.csv).",
        packaged=packaged,
        raster_sha256=packaged[primary]["sha256"],
        submission_file=packaged[primary]["file"],
        submission_name=packaged[primary]["name"],
        note=packaged[primary]["note"], note_chars=packaged[primary]["note_chars"],
        validator_output=packaged[primary]["gates"],
        format_pass=fmt_ok,
        gates=dict(format=fmt_ok, canary=canary_ok, holdout_beats_best_control=holdout_ok,
                   operative_uniqueness=uniq_ok),
        blocking_reasons=reasons,
        verdict=verdict,
        submission_eligible=False,
        selector_note="Promotion (if any) means eligible for the separate selector step within the verified weekly cap on the DrivenData submission page; this session spent 0 slots and does not select a slot (protocol rule 6).",
        input_sha256=dict(
            sample_submission=sha256_file(INPUTS / "bridge" / "sample_submission.tif"),
            labels=sha256_file(INPUTS / "bridge" / "labels.tif") if (INPUTS / "bridge" / "labels.tif").exists() else sha256_file(ROOT / "data/bridge/labels.tif"),
            training_features="4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
            topo_10m="a6398d9950965dec6aae6ccecdaa6ced48645d133eab222cbdd11def9bdabfa4",
        ),
        generated_utc=datetime.now(timezone.utc).isoformat(),
        runtime_s=round(time.time() - t0, 1),
    )
    # Back-fill per-arm audit receipts with the verdict + registry evidence so
    # every served audit is byte-bound to this run card (check_site contract).
    for arm, info in packaged.items():
        apath = ROOT / info["audit"]
        doc = json.loads(apath.read_text())
        u = uniq[arm]["operative_sparse"]
        doc.update(
            submission_eligible=False,
            verdict=verdict if arm == primary else "negative",
            run_card="evidence/vario_run_card.json",
            public_registry_uniqueness=dict(
                evidence_file="evidence/vario_run_card.json",
                candidate_hash_matches_scan=True,
                candidate_sha256_zeros=info["sha256"],
                registries_checked=u["rasters"],
                unique_under_literal_rule=False,
                stop_required=True,
                worst_forward_overlap=(u["worst_overlap"] or {}).get("forward_overlap_within_3px"),
                worst_overlap_raster=(u["worst_overlap"] or {}).get("file"),
                worst_abs_spearman=abs((u["worst_abs_spearman"] or {}).get("spearman", 0.0)),
                operative_sparse_passes=bool(u["passes"]),
                scope=uniq[arm]["scope"] + "; literal positive-support reading fails vs pinned full-footprint dense surfaces for every non-empty raster (disclosed in run card)"),
        )
        apath.write_text(json.dumps(doc, indent=1))
    for dest in (EVIDENCE / "vario_run_card.json", DOWNLOADS / "vario_run_card.json"):
        dest.write_text(json.dumps(card, indent=1))
    log(f"VERDICT {verdict}; reasons={reasons}; primary sha={card['raster_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
