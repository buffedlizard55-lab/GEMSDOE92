#!/usr/bin/env python3
"""Finalize NETEXPAND: Rule-1 uniqueness (surface + final, local registry),
package via shared submission_writer, independent [0,1] validation, run card.

Pre-registration / decision rule: docs/HYPOTHESES_20261025_NETEXPAND.md.
Promote (per arm) iff: canaries <=0.90 AND format gates pass AND operative
local uniqueness (dot-fields literal; continuous matched-budget; |rho|<=0.90)
AND HOLDOUT-DTI beats in-run control_knick with paired CI>0 AND exceeds the
recorded FAULTNET netfar level 0.175147. Literal positive-support overlaps
are always published alongside (dense-witness disclosure). Even a promoted
arm is "promote-to-selector": spending a weekly slot is a separate step
(Protocol Rule 6), so ok_to_submit stays False in machine-readable status.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "vendor")]

from gems import gates as G  # noqa: E402
from gems57 import grid as grid_mod, submission_writer, uniqueness as U, validate as V  # noqa: E402

INPUTS = ROOT / ".cache" / "gems_inputs"
CACHE = ROOT / ".cache" / "netexpand"
DL = ROOT / "docs" / "downloads"
EV = ROOT / "evidence"
DATE = "20261025"
ARMS = ("netexpand", "netexpand_far", "nocontext")
SURF = {"netexpand": "S_netexpand.npy", "netexpand_far": "S_netexpand.npy", "nocontext": "S_nocontext.npy"}
NOTES = {
    "netexpand": "NETEXPAND: KNICK30+LISTRIC4+FAULTNETctx5+ASA/coh/curie/MT6 LOQO pure crest; 37654 dots 2.8px dcat>2",
    "netexpand_far": "NETEXPAND far: same LOQO pure-crest surface, dots >4px off catalogue; 37654 dots 2.8px",
    "nocontext": "NETEXPAND nocontext ablation: identical minus catalogue-network context; 37654 dots 2.8px dcat>2",
}
FAULTNET_BEST = 0.17514739242453894


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def local_registry(foot):
    cands = []
    for d in (DL, ROOT / "releases", ROOT / "data", ROOT / "data/bridge",
              INPUTS / "lineage", INPUTS / "bridge"):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.tif")):
            if "netexpand" in p.name.lower():
                continue
            if p.name in ("sample_submission.tif", "existing_faults.tif", "labels.tif"):
                continue
            cands.append(p)
    seen, out = set(), []
    for p in cands:
        try:
            s = sha256_file(p)
        except OSError:
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append((str(p.relative_to(ROOT)) if str(p).startswith(str(ROOT)) else str(p), p))
    return out


def scan_arm(dots, surface, foot, registry, expected):
    foot_idx = np.flatnonzero(foot.ravel())
    sub = np.sort(np.random.default_rng(20261025).choice(foot_idx, size=250_000, replace=False))
    surf_sub = surface.ravel()[sub].astype(np.float32)
    dot_mask = dots & foot
    k = int(dot_mask.sum())
    rows = []
    for label, path in registry:
        try:
            with rasterio.open(path) as ds:
                if ds.count != 1 or (ds.shape, ds.crs, ds.transform) != expected:
                    rows.append(dict(file=label, error="grid/band mismatch"))
                    continue
                raw = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0, posinf=0.0, neginf=0.0)
        except Exception as exc:  # noqa: BLE001
            rows.append(dict(file=label, error=str(exc)[:80]))
            continue
        support = (raw > 0) & foot
        n_sup = int(support.sum())
        if n_sup == 0:
            rows.append(dict(file=label, error="empty"))
            continue
        lit = float(U._near(support, 3.0)[dot_mask].mean())
        if n_sup <= U.DOT_FIELD_MAX_SUPPORT:
            mb, rep = lit, "dot_field"
        else:
            mb = float(U._near(U.matched_budget_support(raw, foot, k), 3.0)[dot_mask].mean())
            rep = "continuous_surface"
        tv = raw.ravel()[sub]
        rho = float(spearmanr(surf_sub, tv).statistic) if (np.ptp(surf_sub) and np.ptp(tv)) else float("nan")
        rows.append(dict(file=label, their_positive=n_sup, representation=rep,
                         literal_forward_overlap=round(lit, 6),
                         operative_forward_overlap=round(mb, 6),
                         spearman_surface=None if not np.isfinite(rho) else round(rho, 6)))
        del raw, support
    ok = [r for r in rows if "error" not in r]
    worst_op = max(ok, key=lambda r: r["operative_forward_overlap"])
    worst_lit = max(ok, key=lambda r: r["literal_forward_overlap"])
    rho_rows = [r for r in ok if r["spearman_surface"] is not None]
    worst_rho = max(rho_rows, key=lambda r: abs(r["spearman_surface"])) if rho_rows else None
    dup_op = [r for r in ok if r["operative_forward_overlap"] > 0.70]
    dup_rho = [r for r in rho_rows if abs(r["spearman_surface"]) > 0.90]
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        scope="complete local registry (docs/downloads + releases + data + pinned lineage, byte-deduped); public fleet NOT re-scanned this session",
        rasters_checked=len(ok), errors=len(rows) - len(ok),
        worst_operative_overlap=dict(value=worst_op["operative_forward_overlap"], raster=worst_op["file"],
                                     representation=worst_op["representation"], their_positive=worst_op["their_positive"]),
        worst_literal_overlap=dict(value=worst_lit["literal_forward_overlap"], raster=worst_lit["file"],
                                   their_positive=worst_lit["their_positive"]),
        worst_abs_spearman_surface=(dict(value=abs(worst_rho["spearman_surface"]), raster=worst_rho["file"]) if worst_rho else None),
        duplicates_operative=len(dup_op) + len(dup_rho),
        unique_operative_local=bool(not dup_op and not dup_rho),
        literal_rasters_over_0p70=int(sum(1 for r in ok if r["literal_forward_overlap"] > 0.70)),
        rows=rows,
    )


def independent_validate(tif: Path, foot, cat, sample: Path):
    with rasterio.open(sample) as ref:
        ref_crs, ref_tr, ref_shape = ref.crs, ref.transform, ref.shape
    with rasterio.open(tif) as ds:
        a = ds.read(1)
        meta = dict(count=ds.count, dtype=str(ds.dtypes[0]), crs=str(ds.crs),
                    shape=list(ds.shape), nodata=(None if ds.nodata is None else float(ds.nodata)))
        tr_ok = ds.transform == ref_tr
    checks = dict(
        single_band=meta["count"] == 1,
        dtype_float32=meta["dtype"] == "float32",
        crs_epsg_32611=("32611" in meta["crs"] or "WGS 84 / UTM zone 11N" in meta["crs"]),
        crs_matches_sample=str(ref_crs) == meta["crs"],
        shape_matches_sample=list(ref_shape) == meta["shape"],
        transform_matches_sample=bool(tr_ok),
        no_nan_anywhere=bool(np.isfinite(a).all()),
        no_inf_anywhere=bool(np.isfinite(a).all()),
        values_in_0_1=bool(float(a.min()) >= 0.0 and float(a.max()) <= 1.0),
        no_nan_inside_footprint=bool(np.isfinite(a[foot]).all()),
        outside_footprint_zero=bool((a[~foot] == 0).all()),
        zero_dots_on_catalogue=int(((a > 0) & cat).sum()) == 0,
        nodata_is_none=meta["nodata"] is None,
    )
    return dict(meta=meta, checks=checks, all_pass=bool(all(checks.values())),
                min=float(a.min()), max=float(a.max()), dots=int((a > 0).sum()),
                nan_cells=int(np.isnan(a.astype(np.float64)).sum()))


def main() -> int:
    from gems57.uniqueness import stop_historical_runner
    stop_historical_runner("finalize_netexpand:main")

    for n in NOTES.values():
        assert len(n) <= 140, n
    assert (EV / "netexpand_holdout.json").is_file(), "run holdout first"
    hold = json.loads((EV / "netexpand_holdout.json").read_text())
    grid = grid_mod.load_grid(INPUTS / "bridge")
    foot, cat = grid.footprint, grid.catalogue
    sample = INPUTS / "bridge" / "sample_submission.tif"
    cat_path = INPUTS / "bridge" / "existing_faults.tif"
    with rasterio.open(sample) as ds:
        expected = (ds.shape, ds.crs, ds.transform)
    canary_max = max(c["symmetric_auc"] for c in hold["canaries"])
    canary_worst = max(hold["canaries"], key=lambda c: c["symmetric_auc"])["feature"]
    log(f"canary max {canary_max:.4f} ({canary_worst}); building local registry...")
    registry = local_registry(foot)
    log(f"local registry: {len(registry)} byte-unique rasters")
    d_cat = distance_transform_edt(~cat)

    arms = {}
    for arm in ARMS:
        dots = np.load(CACHE / f"dots_{arm}.npy")
        surface = np.load(CACHE / SURF[arm])
        log(f"{arm}: Rule-1 scan (surface rho + final dots, {int(dots.sum())} dots)...")
        uniq = scan_arm(dots, surface, foot, registry, expected)
        log(f"  operative worst {uniq['worst_operative_overlap']['value']:.4f} vs "
            f"{uniq['worst_operative_overlap']['raster']}; unique_local={uniq['unique_operative_local']}")
        pred = np.where(dots & foot, 1.0, 0.0).astype(np.float32)
        tag = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
        stem = f"gemsdoe92-netexpand-{arm.replace('_', '')}-{int(dots.sum())}-{DATE}-{tag}-zeros"
        tif = DL / f"{stem}.tif"
        for ext in (".tif", ".zip", ".json"):
            tif.with_suffix(ext).unlink(missing_ok=True)
        receipt = submission_writer.write_submission(
            tif, pred, sample, foot, note=NOTES[arm],
            name=f"gemsdoe92-netexpand-{arm}-{DATE}-{tag}", catalogue=cat,
            metadata=dict(lane="NETEXPAND", arm=arm))
        gr = G.run_gates(str(tif), str(sample), str(cat_path),
                         prune_radius=(None if arm == "netexpand_far" else 2),
                         require_submission_encoding=True)
        gates_ok, gates_rep = G.summarise(gr)
        ind = independent_validate(tif, foot, cat, sample)
        v57 = V.validate(tif, foot, cat)
        s = hold["scores"][arm]
        d_ctrl = hold["paired_by_candidate"][arm]["control_knick"]
        beats_ctrl = bool(s["dti"] > hold["scores"]["control_knick"]["dti"] and d_ctrl["ci95"][0] > 0)
        # far arm must also beat the emission-matched control when available
        if arm == "netexpand_far" and "control_knick_far" in hold["scores"]:
            d_far = hold["paired_by_candidate"][arm]["control_knick_far"]
            beats_ctrl = bool(beats_ctrl and s["dti"] > hold["scores"]["control_knick_far"]["dti"]
                              and d_far["ci95"][0] > 0)
        beats_best = bool(s["dti"] > FAULTNET_BEST)
        promote = bool(canary_max <= 0.90 and gates_ok and ind["all_pass"]
                       and uniq["unique_operative_local"] and beats_ctrl and beats_best)
        arms[arm] = dict(
            file=f"docs/downloads/{tif.name}", zip=f"docs/downloads/{stem}.zip",
            writer_receipt=f"docs/downloads/{stem}.json",
            sha256=receipt["sha256"], zip_sha256=receipt["zip_sha256"], bytes=receipt["bytes"],
            submission_name=f"gemsdoe92-netexpand-{arm}-{DATE}-{tag}", note=NOTES[arm],
            dots=int(dots.sum()), min_dcat_px=float(d_cat[dots].min()),
            holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
                             dti=s["dti"], ci95=s["ci95"], withheld_positives=s["withheld_positive_pixels"],
                             paired_vs_control_knick=d_ctrl,
                             paired_vs_control_knick_far=hold["paired_by_candidate"][arm].get("control_knick_far"),
                             paired_vs_R0=hold["paired_by_candidate"][arm].get("control_R0")),
            beats_knick_control_paired=beats_ctrl, exceeds_faultnet_netfar_recorded=beats_best,
            format_gates_pass=bool(gates_ok), gates=[dict(name=g.name, ok=g.ok, detail=g.detail) for g in gr],
            independent_validator=ind, gems57_validate=v57,
            uniqueness_local=uniq,
            ok_to_download=bool(gates_ok and ind["all_pass"]),
            ok_to_submit=False,
            verdict=("promote" if promote else "negative"),
            promote_to_selector=promote,
        )
        audit = dict(file=arms[arm]["file"], sha256_zeros=receipt["sha256"],
                     gates_zeros=arms[arm]["gates"], overall_pass=bool(gates_ok and ind["all_pass"]),
                     submission_eligible=False, verdict=arms[arm]["verdict"],
                     promote_to_selector=promote, note=NOTES[arm],
                     n_dots=int(dots.sum()), independent_validator=ind,
                     uniqueness_local={k: v for k, v in uniq.items() if k != "rows"},
                     run_card="evidence/netexpand_run_card.json")
        (DL / f"{stem}-audit.json").write_text(json.dumps(audit, indent=1))
        log(f"  {arm}: DTI {s['dti']:.6f} beats_ctrl={beats_ctrl} beats_best={beats_best} "
            f"gates={gates_ok} verdict={arms[arm]['verdict']}")

    primary = max(ARMS, key=lambda a: hold["scores"][a]["dti"])
    card = dict(
        schema="gemsdoe92-run-card.v3", lane="NETEXPAND",
        generated_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis=("Catalogue-missing geothermal faults are subordinate splays/relays of mapped "
                    "systems whose scarps are diffused/buried but whose strike-blind gravity/magnetic "
                    "analytic-signal edges, RTP demagnetization suppression and MT clay-cap "
                    "change-points persist; learning network-context x ASA/coherence x alteration "
                    "interactions in a quadrant-LOQO ensemble and emitting on pure new-channel "
                    "1-D crests recovers them off-catalogue."),
        mechanism=("45-feature 3-branch LOQO HGB (KNICK30 + LISTRIC4 + self-excluded visible-catalogue "
                   "context5 + grav/mag ASA & coherence, curie suppression, MT change-point), "
                   "within-quadrant quantile calibration, pure ASA/coherence/listric crest, "
                   "37,654 unit dots >=2.8 px spacing, d_cat>2 (far arm >4), zeros-outside float32."),
        named_non_fault_mimic=("Range-front lithologic contacts parallel to mapped faults; equant "
                               "plutons; thick non-magnetic Lahontan sediments; playa salinity fronts."),
        experiments=list(ARMS), primary_arm=primary,
        holdout_dti=dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"],
                         instrument=hold["instrument"], scores=hold["scores"],
                         paired_by_candidate=hold["paired_by_candidate"],
                         withheld_positives=hold["scores"]["netexpand"]["withheld_positive_pixels"],
                         bootstrap=hold["bootstrap"],
                         recorded_prior_best=dict(lane="FAULTNET netfar", dti=FAULTNET_BEST,
                                                  evidence_class="HOLDOUT-DTI",
                                                  source="evidence/faultnet_holdout.json")),
        leakage_canaries=dict(max_symmetric_auc=canary_max, worst_feature=canary_worst,
                              all_pass_le_0p90=bool(canary_max <= 0.90), features=hold["canaries"]),
        organizer_confirmed_score=None,
        arms=arms,
        raster_sha256=arms[primary]["sha256"],
        validator_output=dict(no_nan_in_footprint=arms[primary]["independent_validator"]["checks"]["no_nan_inside_footprint"],
                              values_in_0_1=arms[primary]["independent_validator"]["checks"]["values_in_0_1"],
                              crs_shape_transform_match=bool(
                                  arms[primary]["independent_validator"]["checks"]["crs_matches_sample"]
                                  and arms[primary]["independent_validator"]["checks"]["shape_matches_sample"]
                                  and arms[primary]["independent_validator"]["checks"]["transform_matches_sample"]),
                              dots=arms[primary]["dots"],
                              checks=arms[primary]["independent_validator"]["checks"]),
        correlation_overlap_vs_registry=dict(
            local_primary=arms[primary]["uniqueness_local"],
            public=dict(available=False, scope="not re-scanned this session; literal dense-witness disclosure in docs/ANALYSIS_20261025_NETEXPAND.md")),
        submission_name=arms[primary]["submission_name"], note=arms[primary]["note"],
        ok_to_download=bool(arms[primary]["ok_to_download"]), ok_to_submit=False,
        submission_status=("CLEARED FOR SELECTOR (promote) — spending a weekly slot is a separate "
                           "selector step; do not auto-submit" if arms[primary]["verdict"] == "promote"
                           else "DO NOT SUBMIT — verdict negative (see gates); research download only"),
        verdict=arms[primary]["verdict"],
        weekly_slots_used=0, input_pins=dict(
            training_features="4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
            sample_submission="2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
            existing_faults="7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
            parent_R0_zeros="c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"),
    )
    (EV / "netexpand_run_card.json").write_text(json.dumps(card, indent=1))
    shutil.copy2(EV / "netexpand_run_card.json", DL / "netexpand_run_card.json")
    (EV / "netexpand_uniqueness.json").write_text(
        json.dumps({a: arms[a]["uniqueness_local"] for a in ARMS}, indent=1))
    # ledger rows (BUILT, no receipt) + mechanism card
    led = ROOT / "ledger/submissions.csv"
    with led.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f)); fields = list(rows[0].keys())
    have = {r["id"] for r in rows}
    added = 0
    for arm in ARMS:
        a = arms[arm]
        rid = a["submission_name"]
        if rid in have:
            continue
        row = {k: "" for k in fields}
        row.update(id=rid, parent="h33-h33-2-b2", axis="NETEXPAND", value=arm,
                   n_dots=str(a["dots"]), sha256=a["sha256"], status="BUILT",
                   predicted_change="MODEL: unprojected; HOLDOUT-DTI in evidence/netexpand_run_card.json",
                   file_zeros=a["file"], file_nan="", sha8=a["sha256"][:8],
                   change_desc=a["note"], notes=f"verdict={a['verdict']}; HOLDOUT-DTI={hold['scores'][arm]['dti']:.6f}")
        rows.append(row); added += 1
    if added:
        with led.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    cards_path = ROOT / "ledger/mechanism_cards.json"
    cards = json.loads(cards_path.read_text()) if cards_path.is_file() else {}
    for arm in ARMS:
        cards[arms[arm]["submission_name"]] = dict(
            parent="h33-h33-2-b2", axis="NETEXPAND", value=arm,
            hypothesis=card["hypothesis"], mechanism=card["mechanism"],
            non_fault_mimic=card["named_non_fault_mimic"],
            falsifier="HOLDOUT-DTI <= control_knick paired, canary >0.90, or operative overlap >0.70",
            decision_rule="Promote-to-selector only per docs/HYPOTHESES_20261025_NETEXPAND.md; slots spent by selector step only.",
            predicted_sign_and_size="unprojected (Protocol Rule 3)")
    cards_path.write_text(json.dumps(cards, indent=2) + "\n")
    log(f"run card written; primary={primary} verdict={card['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
