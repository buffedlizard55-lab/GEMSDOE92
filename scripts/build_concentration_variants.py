#!/usr/bin/env python3
"""Reproducibly build three fixed-mass CONCENTRATION rungs from parent R0.

Reads only SHA-256-pinned inputs listed in registry/session_manifest.json,
rebuilds R0 through the full H19-5 -> D1.5 -> D2.8 -> SOLO -> R0 lineage and
requires both recorded raster hashes to match, then moves a fixed fraction of
the 37,654-dot budget from the lowest-prior to the highest-prior 5 km blocks.

Axis definition (this session)
------------------------------
* block size  : 50 px = 5 km, stated per variant
* prior       : block mean of the parent's own evidence surface ``w``
                (0.30 + 0.70 * [0.40*TMI-hg + 0.35*gravity-hg + 0.25*slope] on
                the H19-5 ridge support, 0.08 * phys off it) -- the identical
                field the PRUNE session's refill machinery used
* source      : lowest-prior blocks, expanded upward until they hold at least
                2x the demanded dots; within that pool the dots with the
                smallest exact marginal DTI removal loss are taken
* destination : top quintile of blocks by prior; quota proportional to the
                block prior, capped by the pixels actually available
* placement   : exact marginal DTI gain on the legal support
                (in footprint, on H19-5, > 2 px from the catalogue)

Count, total mass and total support are unchanged, so the only thing that moves
is the block allocation. No label, leaderboard, submission endpoint or
off-manifest data is touched. Candidate TIFFs are written to releases/, which
this repository gitignores.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, binary_dilation

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor"), str(ROOT / "scripts")]

from build_prune_rungs import (  # noqa: E402
    PARENT_SHA, PARENT_ID, DATE, OUT_DIR, LEDGER, RECEIPTS as _UNUSED,
    build_parent, make_prior, percentile_rank, sha256_file, validate_reopened,
    verify_inputs, write_tif,
)
from concentration_axis import (  # noqa: E402
    DotState, allocate_quotas, block_index, block_mean, greedy_add_blocked,
    greedy_remove,
)
from gems57 import metric  # noqa: E402

EVIDENCE = ROOT / "evidence" / "concentration.json"
BLOCK_PX = 50
RUNGS = (0.10, 0.15, 0.20)

# MODEL expectation. The two local instruments disagree in sign, so the central
# value is a blend and the range spans both. Neither number is a score.
#   SGMC-off-catalogue control (the closer analogue of NEW-fault truth):
#       -0.004851 / -0.007066 / -0.010416
#   catalogue hide-and-recover holdout (scores KNOWN faults, which the
#   organisers mask out of the live metric):
#       +0.001807 / +0.001853 / +0.001870
PREDICTION = {
    0.10: ("MODEL:-0.001", "[-0.021,+0.011]"),
    0.15: ("MODEL:-0.003", "[-0.023,+0.011]"),
    0.20: ("MODEL:-0.005", "[-0.026,+0.011]"),
}

# Recorded output of scripts/screen_concentration_priors.py (run 2026-10-23):
# the local consequence of moving a fixed fraction of the budget under several
# candidate block priors, in both directions, at 5 km blocks. Ordering the
# priors and the dose-response; not a score and not a gate.
SCREENING = {
    "evidence_label": "PROXY",
    "script": "scripts/screen_concentration_priors.py",
    "block_px": 50,
    "reference_r0": {"sgmc_off_catalogue_dti": 0.096060,
                     "declared_model_dti": 0.261133,
                     "n_sgmc_control_pixels": 62703},
    "runs": [
        {"prior": "w_evidence", "frac": 0.05, "direction": "concentrate",
         "sgmc_delta": -0.001794, "declared_model_delta": 0.001812},
        {"prior": "phys_only", "frac": 0.05, "direction": "concentrate",
         "sgmc_delta": -0.002297, "declared_model_delta": 0.001000},
        {"prior": "phys_only", "frac": 0.05, "direction": "inverted",
         "sgmc_delta": -0.004076, "declared_model_delta": -0.007043},
        {"prior": "cat_network", "frac": 0.05, "direction": "concentrate",
         "sgmc_delta": -0.001615, "declared_model_delta": -0.000509},
        {"prior": "cat_network", "frac": 0.05, "direction": "inverted",
         "sgmc_delta": -0.001665, "declared_model_delta": -0.003759},
        {"prior": "cat_nodes", "frac": 0.05, "direction": "concentrate",
         "sgmc_delta": -0.001597, "declared_model_delta": -0.001251},
        {"prior": "cat_nodes", "frac": 0.05, "direction": "inverted",
         "sgmc_delta": -0.001321, "declared_model_delta": -0.003529},
        {"prior": "w_evidence", "frac": 0.10, "direction": "concentrate",
         "sgmc_delta": -0.004793, "declared_model_delta": -0.000387},
        {"prior": "w_evidence", "frac": 0.10, "block_px": 100,
         "direction": "concentrate", "sgmc_delta": -0.005461,
         "declared_model_delta": -0.002067},
        {"prior": "w_evidence", "frac": 0.10, "block_px": 100,
         "direction": "inverted", "sgmc_delta": -0.006963,
         "declared_model_delta": -0.014123},
        {"prior": "w_evidence", "frac": 0.20, "direction": "concentrate",
         "sgmc_delta": -0.010423, "declared_model_delta": -0.008693},
        {"prior": "phys_only", "frac": 0.20, "direction": "concentrate",
         "sgmc_delta": -0.011826, "declared_model_delta": -0.010821},
        {"prior": "cat_network", "frac": 0.20, "direction": "concentrate",
         "sgmc_delta": -0.012462, "declared_model_delta": -0.016250},
        {"prior": "cat_nodes", "frac": 0.20, "direction": "concentrate",
         "sgmc_delta": -0.012281, "declared_model_delta": -0.016900},
        {"prior": "random_null", "frac": 0.20, "direction": "concentrate",
         "sgmc_delta": -0.012365, "declared_model_delta": -0.019574},
        {"prior": "random_null", "frac": 0.20, "direction": "inverted",
         "sgmc_delta": -0.010382, "declared_model_delta": -0.019623},
    ],
    "reading": (
        "Every prior and every dose loses against the independent-fault control, "
        "including the randomised null, so most of the loss is the generic cost of "
        "replacing a surviving dot with a thinned-away neighbour rather than a failure "
        "of the ordering. The ordering itself does carry signal: at 20% the parent's own "
        "evidence surface recovers +0.0019 of the randomised -0.0124 loss on the control "
        "and +0.0109 on the declared model, and at 10 km blocks concentrating beats the "
        "inverted direction by +0.0015 (control) and +0.0121 (declared model). The loss "
        "grows roughly linearly with dose; nothing in this grid is predicted to gain."
    ),
}


def value_name(frac: float) -> str:
    return f"C{int(round(frac * 100)):02d}_b{BLOCK_PX // 10}km"


def _link_distance(added: np.ndarray, removed: np.ndarray) -> float:
    """Mean distance from each added dot to the nearest removed dot, in pixels.

    Not a physical displacement (dots are not paired); it is the scale over
    which the budget actually travelled.
    """
    from scipy.spatial import cKDTree
    if not added.any() or not removed.any():
        return 0.0
    tree = cKDTree(np.c_[np.nonzero(removed)[0], np.nonzero(removed)[1]])
    d, _ = tree.query(np.c_[np.nonzero(added)[0], np.nonzero(added)[1]], k=1)
    return round(float(d.mean()), 3)


def block_stats(mask: np.ndarray, block_px: int, foot: np.ndarray,
                in_fp: np.ndarray) -> dict:
    bi, nby, nbx = block_index(mask.shape, block_px)
    nblk = nby * nbx
    cnt = np.bincount(bi[foot], minlength=nblk)
    sel = cnt > 0.5 * block_px * block_px
    dots = np.bincount(bi[mask], minlength=nblk)[sel].astype(float)
    return {
        "block_px": block_px,
        "block_km": block_px / 10.0,
        "n_blocks_in_footprint": int(sel.sum()),
        "dots_per_block_mean": round(float(dots.mean()), 3),
        "block_density_cv": round(float(dots.std() / dots.mean()), 4),
        "block_density_min": int(dots.min()),
        "block_density_max": int(dots.max()),
    }


def concentrate(parent_mask: np.ndarray, w: np.ndarray, foot: np.ndarray,
                d_cat: np.ndarray, h19: np.ndarray, frac: float,
                block_px: int = BLOCK_PX) -> tuple[np.ndarray, dict]:
    H, W = foot.shape
    bi, nby, nbx = block_index((H, W), block_px)
    nblk = nby * nbx
    bp, _ = block_mean(w.astype(np.float64), bi, nblk, weight=foot)
    cnt = np.bincount(bi[foot], minlength=nblk)
    fin = np.isfinite(bp) & (cnt > 0.5 * block_px * block_px)
    bp = np.where(fin, bp, np.nan)

    n_move = int(round(frac * int(parent_mask.sum())))
    legal = h19 & (d_cat > 2.0) & foot          # R0's own legality rule
    elig = legal & ~parent_mask

    dest_ids = np.nonzero(fin & (bp >= np.nanpercentile(bp[fin], 80)))[0]
    wts = bp[dest_ids]
    wts = wts - np.nanmin(wts)
    if not np.isfinite(wts).all() or wts.max() <= 0:
        wts = np.ones(len(dest_ids))

    dot_b = bi[parent_mask]
    dot_cnt = np.bincount(dot_b, minlength=nblk)
    order = np.argsort(np.where(fin, bp, np.inf), kind="stable")
    k = int(np.searchsorted(np.cumsum(dot_cnt[order]), 2 * n_move)) + 1
    src_ids = order[:k]
    allowed = np.isin(dot_b, src_ids)

    state = DotState(parent_mask, w)
    removed = greedy_remove(state, n_move, allowed=allowed, batch=100)
    base = state.mask

    avail = np.bincount(bi[elig & ~base], minlength=nblk)[dest_ids]
    quota = allocate_quotas(wts, avail, n_move)
    dest_index = np.full(nblk, -1, dtype=np.int32)
    dest_index[dest_ids] = np.arange(len(dest_ids), dtype=np.int32)
    greedy_add_blocked(state, elig & ~base, n_move, dest_index[bi].astype(np.int32), quota)

    out = state.mask
    assert int(out.sum()) == int(parent_mask.sum())
    moved_out = parent_mask & ~out
    moved_in = out & ~parent_mask
    stats = {
        "frac": frac,
        "n_moved": n_move,
        "pct_of_parent_dots": round(100.0 * n_move / int(parent_mask.sum()), 4),
        "n_source_blocks": int(len(src_ids)),
        "n_destination_blocks": int((quota > 0).sum()),
        "prior_mean_source_blocks": round(float(np.nanmean(bp[src_ids])), 6),
        "prior_mean_destination_blocks": round(float(np.nanmean(bp[dest_ids])), 6),
        "prior_mean_dots_removed": round(float(np.nanmean(bp[bi[moved_out]])), 6),
        "prior_mean_dots_added": round(float(np.nanmean(bp[bi[moved_in]])), 6),
        "quota_min": int(quota[quota > 0].min()),
        "quota_max": int(quota.max()),
    }
    return out, stats


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, h19, parent = build_parent(inputs)
    r0 = parent["r0"]
    n0 = int(r0.sum())
    if n0 != 37654 or np.any(r0 & cat) or np.any(d_cat[r0] <= 2.0):
        raise RuntimeError("R0 parent invariants failed")
    w = make_prior(inputs, foot, h19)

    with rasterio.open(inputs["sgmc_faults_control"]) as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    sgmc_off = sgmc_raw & ~cat & ~binary_dilation(cat, iterations=3)
    sgmc_reference = metric.dti_binary(r0, sgmc_off, valid=foot, known=cat)["dti"]
    w_reference = DotState(r0, w).dti()

    r0_block = block_stats(r0, BLOCK_PX, foot, foot)
    print(f"R0 block-density CV ({BLOCK_PX}px) = {r0_block['block_density_cv']}")
    print(f"R0 SGMC PROXY = {sgmc_reference:.6f}; w-MODEL = {w_reference:.6f}")

    variants: list[dict] = []
    mechanism_cards: dict[str, dict] = {}
    used_hashes = {PARENT_SHA["nan"], PARENT_SHA["zeros"]}

    for frac in RUNGS:
        mask, stats = concentrate(r0, w, foot, d_cat, h19, frac, BLOCK_PX)
        assert int(mask.sum()) == n0
        assert not np.any(mask & cat)
        assert np.all(d_cat[mask] > 2.0), "catalogue clearance violated"
        after = block_stats(mask, BLOCK_PX, foot, foot)

        moved_out = r0 & ~mask
        moved_in = mask & ~r0
        n_moved = int(moved_out.sum())
        pct = 100.0 * n_moved / n0
        if not (1.0 <= pct <= 50.0):
            raise RuntimeError(f"changed {pct:.2f}% outside the brief's 1-50% window")

        value = value_name(frac)
        tmp_nan = OUT_DIR / f"._building-{value}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{value}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)
        checks_nan = validate_reopened(tmp_nan, inputs["sample_submission"], mask,
                                       foot, cat, d_cat, True)
        checks_zero = validate_reopened(tmp_zeros, inputs["sample_submission"], mask,
                                        foot, cat, d_cat, False)
        sha_nan, sha_zeros = sha256_file(tmp_nan), sha256_file(tmp_zeros)
        if sha_nan == sha_zeros or sha_nan in used_hashes or sha_zeros in used_hashes:
            raise RuntimeError(f"Exact duplicate SHA-256 at {value}")
        used_hashes.update((sha_nan, sha_zeros))

        short_id = f"{PARENT_ID}-CONC_{value}-{DATE}-{sha_nan[:8]}"
        nan_path = OUT_DIR / f"{short_id}.tif"
        zeros_path = OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)
        checks_nan = validate_reopened(nan_path, inputs["sample_submission"], mask,
                                       foot, cat, d_cat, True)
        checks_zero = validate_reopened(zeros_path, inputs["sample_submission"], mask,
                                        foot, cat, d_cat, False)
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Final-path re-read hash changed at {value}")

        pred_text, pred_range = PREDICTION[frac]
        note = (f"{PARENT_ID}; CONCENTRATION move {int(frac*100)}% of dots from "
                f"lowest- to highest-prior {BLOCK_PX//10} km blocks; fixed {n0}; {pred_text}")
        if len(note) > 140:
            raise RuntimeError(f"Form note exceeds 140 chars ({len(note)}): {note}")

        sgmc_dti = metric.dti_binary(mask, sgmc_off, valid=foot, known=cat)["dti"]
        record = {
            "id": short_id,
            "site": "GEMSDOE92",
            "name": nan_path.name,
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "file_nan": str(nan_path.relative_to(ROOT)),
            "sha8": sha_nan[:8],
            "change_desc": (f"move {n_moved} dots ({pct:.2f}%) from the lowest-prior to "
                            f"the highest-prior {BLOCK_PX//10} km blocks of the parent's "
                            f"own evidence surface; removal by exact marginal DTI loss, "
                            f"placement by exact marginal DTI gain; count held at {n0}"),
            "notes": (f"MODEL range {pred_range}; SGMC-off-catalogue PROXY delta "
                      f"{sgmc_dti - sgmc_reference:+.6f}; declared w-MODEL delta "
                      f"{DotState(mask, w).dti() - w_reference:+.6f}; "
                      f"block-density CV {r0_block['block_density_cv']} -> "
                      f"{after['block_density_cv']}; see evidence/concentration.json"),
            "parent": PARENT_ID,
            "axis": "CONCENTRATION",
            "value": value,
            "n_dots": n0,
            "pct_changed": round(pct, 6),
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "primary_file": nan_path.name,
            "fallback_file": zeros_path.name,
            "primary_encoding": "NaN outside footprint",
            "fallback_encoding": "zero outside footprint",
            "status": "BUILT",
            "predicted_change": pred_text,
            "predicted_range": pred_range,
            "prediction_scope": ("MODEL scenario range only; public-chunk changes under "
                                 "0.01 are no evidence. PROXY instruments are diagnostics, "
                                 "never gates."),
            "sgmc_control_proxy": {
                "evidence_label": "PROXY",
                "dti": round(sgmc_dti, 6),
                "delta_vs_r0": round(sgmc_dti - sgmc_reference, 6),
                "n_withheld_control_pixels": int(sgmc_off.sum()),
            },
            "declared_model": {
                "evidence_label": "MODEL",
                "dti_on_evidence_weight_w": round(DotState(mask, w).dti(), 6),
                "delta_vs_r0": round(DotState(mask, w).dti() - w_reference, 6),
            },
            "parent_diff": {
                "removed": int(moved_out.sum()),
                "added": int(moved_in.sum()),
                "shared": n0 - int(moved_out.sum()),
                "moved_pct": round(pct, 6),
                "symmetric_diff_px": int(moved_out.sum() + moved_in.sum()),
                "min_catalogue_distance_px": round(float(d_cat[mask].min()), 4),
                "mean_link_distance_added_to_nearest_removed_px": _link_distance(
                    moved_in, moved_out),
            },
            "block_stats_before": r0_block,
            "block_stats_after": after,
            "concentration_stats": stats,
            "format_validation": {"nan": checks_nan, "zeros": checks_zero},
            "form_note": note,
            "gate_status": "PASS (local reread; file not tracked in public Git repo)",
            "git_sha_at_build": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        }
        variants.append(record)
        mechanism_cards[short_id] = {
            "parent": PARENT_ID,
            "axis": "CONCENTRATION",
            "value": value,
            "hypothesis": (
                f"At fixed mass, the marginal fault yield per dot is higher inside {BLOCK_PX//10} km "
                "blocks where the parent's own geophysical evidence surface is strong, so moving "
                f"{int(frac*100)}% of the budget out of the weakest blocks into the strongest blocks "
                "raises distance-tolerant fault detection."
            ),
            "mechanism": (
                "The 300 m triangular kernel rewards covering continuous, strongly expressed "
                "lineaments: one dot inside a dense scarp segment converts several truth pixels at "
                "once, which is the regime in which a dot pays for its 0.2 denominator cost. R0's "
                "Poisson-disk thinning instead spaces dots evenly along every H19-5 ridge regardless "
                "of how strongly that ridge is expressed in TMI/gravity gradient and slope, so block "
                "mean evidence and block dot count are only partly aligned."
            ),
            "non_fault_mimic": (
                "TMI and gravity horizontal-gradient highs and steep slope also mark lithologic "
                "contacts, dikes, caldera ring fractures and erosional scarps, so the strongest "
                "blocks can be geophysically loud and structurally barren; the destination pixels "
                "are also the thinned-away neighbours of surviving dots, which are partly redundant."
            ),
            "predicted_sign_and_size": (
                f"{pred_text} vs R0, scenario range {pred_range}; MODEL only, not a score. "
                "The two local instruments disagree in sign: the SGMC off-catalogue control, "
                "which is the closer analogue of new-fault truth, falls monotonically with dose "
                f"({sgmc_dti - sgmc_reference:+.6f} here), while the catalogue hide-and-recover "
                "holdout, which scores known faults the organisers mask out, rises by about "
                "+0.0018 at every dose."
            ),
            "falsifier": (
                "A receipt gain of at least +0.01 over R0 at any dose would reject the reading that "
                "R0's block allocation is already locally optimal and would vindicate the "
                "hide-and-recover instrument over the SGMC control. A loss materially worse than "
                f"{pred_range} at {int(frac*100)}% would show the refill pixels degrade faster than "
                "either local instrument indicates, and would also rule out combining this axis "
                "with anything else."
            ),
            "decision_rule": ("Treat absolute live change <0.01 as no evidence; compare only "
                              "human-provided receipt scores."),
        }
        print(f"BUILT {short_id}: moved={pct:.2f}%  SGMC {sgmc_dti - sgmc_reference:+.6f}  "
              f"CV {r0_block['block_density_cv']} -> {after['block_density_cv']}")

    # ---- ledger ---------------------------------------------------------
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    default_fields = ["id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                      "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                      "change_desc", "receipt_score", "receipt_date", "notes"]
    existing: list[dict] = []
    fields = default_fields
    if LEDGER.exists():
        with LEDGER.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing = list(reader)
            if reader.fieldnames:
                fields = list(reader.fieldnames)
    new_values = {rec["value"]: rec for rec in variants}
    retained = []
    for row in existing:
        key = (row.get("parent", ""), row.get("axis", ""), row.get("value", ""))
        if key[0] == PARENT_ID and key[1] == "CONCENTRATION" and key[2] in new_values:
            if row.get("sha256") != new_values[key[2]]["sha256"]:
                raise RuntimeError(f"Existing (parent, axis, value) has conflicting SHA: {key}")
            continue
        retained.append(row)
    seen = {(r.get("parent", ""), r.get("axis", ""), r.get("value", "")) for r in retained}
    for rec in variants:
        triple = (rec["parent"], rec["axis"], rec["value"])
        if triple in seen:
            raise RuntimeError(f"Repeated (parent, axis, value) pair: {triple}")
    with LEDGER.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in retained:
            writer.writerow({k: row.get(k, "") for k in fields})
        for rec in variants:
            writer.writerow({k: rec.get(k, "") for k in fields})

    report = {
        "schema": "gemsdoe92.concentration.v1",
        "session_date_utc": DATE,
        "built_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "axis": "CONCENTRATION",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": n0,
            "zeros_sha256": parent["parent_hashes"]["zeros"],
            "nan_sha256": parent["parent_hashes"]["nan"],
            "matches_recorded_hashes": parent["parent_hashes"] == PARENT_SHA,
        },
        "block_prior": {
            "field": "block mean of the parent's own evidence surface w",
            "w_definition": ("w = 0.30 + 0.70*phys on the H19-5 ridge support, 0.08*phys off it; "
                             "phys = 0.40*percentile(TMI band 3) + 0.35*percentile(gravity band 18) "
                             "+ 0.25*percentile(slope band 19) -- identical to the PRUNE session"),
            "block_px": BLOCK_PX,
            "block_km": BLOCK_PX / 10.0,
            "destination_rule": "top quintile of in-footprint blocks by prior, quota proportional to prior",
            "source_rule": ("lowest-prior blocks expanded upward until they hold >= 2x the demand; "
                            "removal ordered by exact marginal DTI loss"),
        },
        "r0_block_density_cv": r0_block,
        "screening": SCREENING,
        "proxy_audit_file": "evidence/proxy_audit_concentration.json",
        "r0_sgmc_proxy_dti": round(sgmc_reference, 6),
        "r0_declared_model_dti": round(w_reference, 6),
        "input_manifest_sha256": sha256_file(ROOT / "registry" / "session_manifest.json"),
        "variants": variants,
        "scope_note": ("No submission, leaderboard, hidden labels or off-manifest data accessed. "
                       "Candidate rasters are generated locally and gitignored."),
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    cards_path = ROOT / "ledger" / "mechanism_cards.json"
    cards_path.write_text(json.dumps(mechanism_cards, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {EVIDENCE.relative_to(ROOT)} and {cards_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
