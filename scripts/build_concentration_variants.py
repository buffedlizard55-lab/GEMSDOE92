#!/usr/bin/env python3
"""Build fixed-count CONCENTRATION dose variants from exactly rebuilt R0.

The controlled axis is the fraction moved (10%, 15%, 20%) between 1 km blocks.
The block prior is the mean label-free multiphysics edge response. All variants
share the 2,171 relocations required to clear R0's inherited <=3 px catalogue
collar; remaining movers come from the lowest-prior occupied blocks. Destinations
are legal, un-emitted H19-5 support pixels nearest high-priority block centres,
so the build does not secretly add SNAP or truth/DTI ranking.

Run after scripts/restore_inputs.py:
    .venv/bin/python scripts/build_concentration_variants.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "vendor")]

from build_prune_rungs import (  # noqa: E402
    PARENT_SHA_NAN,
    PARENT_SHA_ZEROS,
    build_parent,
    sha256_file,
    validate_reopened,
    verify_inputs,
    write_tif,
)
from build_snap_variants import git_sha, hash_owners, make_responses  # noqa: E402
from gems.gates import run_gates, summarise  # noqa: E402
from gems.ledger import append_variant, load  # noqa: E402
from gems.variants import (  # noqa: E402
    Dots,
    Variant,
    block_density_cv,
    block_prior,
)

PARENT_ID = "h33-h33-2-b2"
DATE = "20261023"
N_DOTS = 37654
BLOCK_PX = 10  # 100 m pixels -> 1 km
CLEARANCE_PX = 3.0
LEDGER = ROOT / "ledger" / "submissions.csv"
EVIDENCE = ROOT / "evidence" / "concentration_session.json"
OUT_DIR = ROOT / "releases"

SPECS = {
    "blk1km-f10": {
        "fraction": 0.10,
        "prediction": "MODEL:+0.001",
        "range": "[-0.008,+0.009]",
        "hypothesis": "A conservative 10% reallocation toward high-prior 1 km blocks should improve fault coverage while retaining most of R0's spatial distribution.",
        "falsifier": "A receipt at least 0.01 below R0 rejects a beneficial low-dose concentration mechanism; absolute changes below 0.01 are no evidence.",
    },
    "blk1km-f15": {
        "fraction": 0.15,
        "prediction": "MODEL:+0.002",
        "range": "[-0.009,+0.012]",
        "hypothesis": "A 15% move is the central dose: enough low-prior mass is relocated to test the block mechanism above the shared compliance movement without the dilution risk of the 20% arm.",
        "falsifier": "If the 15% receipt is at least 0.01 below both R0 and the 10% arm, reject the predicted middle-dose benefit.",
    },
    "blk1km-f20": {
        "fraction": 0.20,
        "prediction": "MODEL:-0.001",
        "range": "[-0.012,+0.008]",
        "hypothesis": "A 20% move should over-concentrate the fixed budget into high-edge blocks, reducing spatial coverage and acting as the dose-response turnover control.",
        "falsifier": "If the 20% receipt beats both lower doses and R0 by at least 0.01, reject the predicted turnover and test whether the prior remains monotone.",
    },
}
MIMIC = "High multiphysics block response can reflect lithologic contacts, basin-fill density contrasts, intrusive boundaries, or erosional scarps rather than faults; block aggregation can also smooth away a narrow fault tip."


def count_snap_infeasible(parent_yx: np.ndarray, foot: np.ndarray, d_cat: np.ndarray) -> int:
    """Document why the initially considered SNAP axis was not built."""
    h, w = foot.shape
    offsets = [
        (dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
        if np.hypot(dy, dx) <= 2
    ]
    count = 0
    for y, x in parent_yx[d_cat[parent_yx[:, 0], parent_yx[:, 1]] <= CLEARANCE_PX]:
        legal = False
        for dy, dx in offsets:
            yy, xx = int(y + dy), int(x + dx)
            if 0 <= yy < h and 0 <= xx < w and foot[yy, xx] and d_cat[yy, xx] > CLEARANCE_PX:
                legal = True
                break
        count += not legal
    return int(count)


def destination_groups(
    legal: np.ndarray, bp: np.ndarray, block_px: int
) -> tuple[dict[int, list[tuple[int, int]]], list[int], int]:
    """Group legal candidates by block, nearest block centre first."""
    h, w = legal.shape
    nbx = bp.shape[1]
    yy, xx = np.nonzero(legal)
    by, bx = yy // block_px, xx // block_px
    bids = by * nbx + bx
    centre_y = by * block_px + np.minimum(block_px // 2, h - 1 - by * block_px)
    centre_x = bx * block_px + np.minimum(block_px // 2, w - 1 - bx * block_px)
    centre_distance = (yy - centre_y) ** 2 + (xx - centre_x) ** 2
    order = np.lexsort((xx, yy, centre_distance, bids))
    groups: dict[int, list[tuple[int, int]]] = {}
    for i in order:
        groups.setdefault(int(bids[i]), []).append((int(yy[i]), int(xx[i])))
    finite = np.isfinite(bp.ravel())
    block_order = sorted(groups, key=lambda b: (-bp.ravel()[b] if finite[b] else np.inf, b))
    if any(not finite[b] for b in block_order):
        raise RuntimeError("A legal destination block has no finite prior")
    return groups, block_order, nbx


def move_dose(
    fraction: float,
    r0: np.ndarray,
    prior: np.ndarray,
    legal_candidates: np.ndarray,
    d_cat: np.ndarray,
    foot: np.ndarray,
) -> tuple[Dots, dict]:
    parent_yx = np.argwhere(r0)
    bp, _nby, nbx = block_prior(prior, BLOCK_PX)
    dot_prior = bp[parent_yx[:, 0] // BLOCK_PX, parent_yx[:, 1] // BLOCK_PX]
    n_move = int(round(fraction * N_DOTS))
    mandatory_mask = d_cat[parent_yx[:, 0], parent_yx[:, 1]] <= CLEARANCE_PX
    mandatory = np.flatnonzero(mandatory_mask)
    if len(mandatory) > n_move:
        raise RuntimeError("Mandatory compliance movers exceed the requested dose")
    low_order = np.argsort(np.where(np.isfinite(dot_prior), dot_prior, np.inf), kind="stable")
    additional = [int(i) for i in low_order if not mandatory_mask[i]][: n_move - len(mandatory)]
    movers = np.r_[mandatory, np.asarray(additional, dtype=np.int64)]
    if len(movers) != n_move or len(np.unique(movers)) != n_move:
        raise RuntimeError("Source mover selection is incomplete or duplicated")

    # Exclude every original parent pixel, including source pixels: each mover
    # must create a real parent diff rather than a swap invisible to the mask.
    groups, block_order, group_nbx = destination_groups(legal_candidates & ~r0, bp, BLOCK_PX)
    if group_nbx != nbx:
        raise RuntimeError("Block indexing mismatch")
    cursors = {b: 0 for b in block_order}
    destinations: list[tuple[int, int]] = []
    cursor = 0
    for _ in range(n_move):
        for attempt in range(len(block_order)):
            j = (cursor + attempt) % len(block_order)
            bid = block_order[j]
            k = cursors[bid]
            if k < len(groups[bid]):
                destinations.append(groups[bid][k])
                cursors[bid] += 1
                cursor = (j + 1) % len(block_order)
                break
        else:
            raise RuntimeError("Legal high-prior destination capacity exhausted")

    keep = np.ones(N_DOTS, dtype=bool)
    keep[movers] = False
    kept = parent_yx[keep]
    dest = np.asarray(destinations, dtype=np.int64)
    dots = Dots(
        np.r_[kept[:, 0], dest[:, 0]],
        np.r_[kept[:, 1], dest[:, 1]],
        np.ones(N_DOTS),
    )
    mask = np.zeros(r0.shape, dtype=bool)
    mask[dots.ys, dots.xs] = True
    removed = int(np.count_nonzero(r0 & ~mask))
    added = int(np.count_nonzero(mask & ~r0))
    if removed != n_move or added != n_move or len(dots.keys) != N_DOTS:
        raise RuntimeError(f"Parent diff mismatch: removed={removed}, added={added}, expected={n_move}")
    if not foot[dots.ys, dots.xs].all() or not (d_cat[dots.ys, dots.xs] > CLEARANCE_PX).all():
        raise RuntimeError("Output violates footprint or catalogue clearance")
    if not legal_candidates[dots.ys, dots.xs].all():
        raise RuntimeError("Output left the common H19-5/legal support")

    dest_blocks = (dest[:, 0] // BLOCK_PX) * nbx + dest[:, 1] // BLOCK_PX
    stats = {
        "n_dots": N_DOTS,
        "mass_per_dot": 1.0,
        "fraction_requested": fraction,
        "removed": removed,
        "added": added,
        "shared": N_DOTS - removed,
        "pct_changed": 100.0 * removed / N_DOTS,
        "block_px": BLOCK_PX,
        "block_km": BLOCK_PX / 10.0,
        "mandatory_compliance_movers": int(len(mandatory)),
        "additional_low_prior_movers": int(len(additional)),
        "mean_prior_movers_before": float(dot_prior[movers].mean()),
        "mean_prior_additional_low_before": float(dot_prior[additional].mean()),
        "mean_prior_destinations": float(bp.ravel()[dest_blocks].mean()),
        "min_destination_block_prior": float(bp.ravel()[dest_blocks].min()),
        "n_source_blocks": int(len(np.unique((parent_yx[movers, 0] // BLOCK_PX) * nbx + parent_yx[movers, 1] // BLOCK_PX))),
        "n_destination_blocks": int(len(np.unique(dest_blocks))),
        "block_density_cv_before": block_density_cv(
            Dots(parent_yx[:, 0], parent_yx[:, 1], np.ones(N_DOTS)), prior, foot, BLOCK_PX
        ),
        "block_density_cv_after": block_density_cv(dots, prior, foot, BLOCK_PX),
        "min_catalogue_distance_px": float(d_cat[mask].min()),
    }
    if stats["mean_prior_destinations"] <= stats["mean_prior_movers_before"]:
        raise RuntimeError("Destinations do not raise mean block prior")
    variant = Variant("CONCENTRATION", f"blk10px-f{fraction:.2f}", dots, N_DOTS, removed, stats)
    variant.check_change()
    return dots, stats


def main() -> int:
    inputs = verify_inputs()
    foot, cat, d_cat, h19, parent = build_parent(inputs)
    r0 = parent["r0"]
    if int(r0.sum()) != N_DOTS:
        raise RuntimeError("R0 dot count mismatch")
    parent_yx = np.argwhere(r0)
    snap_infeasible = count_snap_infeasible(parent_yx, foot, d_cat)

    prior = make_responses(inputs, foot)["fused-edge-r2"].astype(np.float32)
    prior[~foot] = np.nan
    legal = foot & h19 & ~cat & (d_cat > CLEARANCE_PX)
    rows = load(LEDGER)
    existing_pairs = {(r.get("parent"), r.get("axis"), r.get("value")): r for r in rows}
    owners = hash_owners(rows)
    records: list[dict] = []
    git = git_sha()
    script_sha = sha256_file(Path(__file__))
    response_script_sha = sha256_file(ROOT / "scripts" / "build_snap_variants.py")

    for value, spec in SPECS.items():
        pair = (PARENT_ID, "CONCENTRATION", value)
        dots, stats = move_dose(spec["fraction"], r0, prior, legal, d_cat, foot)
        mask = np.zeros(r0.shape, dtype=bool)
        mask[dots.ys, dots.xs] = True
        stem = f"{PARENT_ID}-CONCENTRATION{value}-{DATE}"
        tmp_nan = OUT_DIR / f"._building-{value}-nan.tif"
        tmp_zeros = OUT_DIR / f"._building-{value}-zeros.tif"
        write_tif(tmp_nan, parent["profile"], foot, mask, True)
        write_tif(tmp_zeros, parent["profile"], foot, mask, False)
        sha_nan, sha_zeros = sha256_file(tmp_nan), sha256_file(tmp_zeros)
        short_id = f"{stem}-{sha_nan[:8]}"
        nan_path, zeros_path = OUT_DIR / f"{short_id}.tif", OUT_DIR / f"{short_id}-zeros.tif"
        tmp_nan.replace(nan_path)
        tmp_zeros.replace(zeros_path)

        for path, expect_nan in ((nan_path, True), (zeros_path, False)):
            checks = validate_reopened(path, inputs["sample_submission"], mask, foot, cat, d_cat, expect_nan)
            gate_results = run_gates(path, inputs["sample_submission"], catalogue_path=inputs["existing_faults"])
            ok, report = summarise(gate_results)
            if not ok or not all(checks.values()):
                raise RuntimeError(f"Re-read/gate failure for {path}:\n{report}\n{checks}")
            if expect_nan:
                checks_nan, report_nan = checks, report
            else:
                checks_zeros, report_zeros = checks, report
        if sha256_file(nan_path) != sha_nan or sha256_file(zeros_path) != sha_zeros:
            raise RuntimeError(f"Final-path hash drift for {value}")
        for sha in (sha_nan, sha_zeros):
            owner = owners.get(sha)
            if owner is not None and owner != pair:
                raise RuntimeError(f"Exact hash duplicate: {value} {sha} owned by {owner}")
        previous = existing_pairs.get(pair)
        if previous is not None and previous.get("sha256") != sha_nan:
            raise RuntimeError(f"Repeated (parent, axis, value) with conflicting hash: {pair}")
        owners[sha_nan], owners[sha_zeros] = pair, pair

        note = (
            f"{PARENT_ID}; CONC 1km f{int(spec['fraction'] * 100)}; moved {stats['removed']} "
            f"({stats['pct_changed']:.2f}%); fixed {N_DOTS}; pred {spec['prediction']}"
        )
        if len(note) > 140:
            raise RuntimeError("Form note exceeds 140 characters")
        mechanism = (
            "Move a fixed number of unit-mass dots from lower to higher mean-response 1 km blocks while holding S and count constant. "
            "The shared compliance movers are identical across doses; incremental dose comparisons therefore isolate concentration. "
            "Destination pixels stay on R0's H19-5 support and are nearest block centres, not response maxima."
        )
        record = {
            "id": short_id,
            "parent": PARENT_ID,
            "axis": "CONCENTRATION",
            "value": value,
            "n_dots": N_DOTS,
            "pct_changed": round(stats["pct_changed"], 6),
            "sha256": sha_nan,
            "sha256_zeros": sha_zeros,
            "status": "BUILT",
            "predicted_change": spec["prediction"],
            "predicted_range": spec["range"],
            "file_nan": str(nan_path.relative_to(ROOT)),
            "file_zeros": str(zeros_path.relative_to(ROOT)),
            "primary_file": nan_path.name,
            "fallback_file": zeros_path.name,
            "sha8": sha_nan[:8],
            "change_desc": f"move {stats['removed']} dots ({stats['pct_changed']:.3f}%) among 1km blocks; shared 2171 compliance movers; fixed unit mass/count on H19-5 support",
            "receipt_score": previous.get("receipt_score", "") if previous else "",
            "receipt_date": previous.get("receipt_date", "") if previous else "",
            "notes": f"1km block CV {stats['block_density_cv_before']:.6f}->{stats['block_density_cv_after']:.6f}; git={git[:12]}; see evidence/concentration_session.json",
            "form_note": note,
            "parent_diff": stats,
            "format_validation": {"nan": checks_nan, "zeros": checks_zeros},
            "gate_reports": {"nan": report_nan, "zeros": report_zeros},
            "mechanism_card": {
                "hypothesis": spec["hypothesis"],
                "mechanism": mechanism,
                "non_fault_mimic": MIMIC,
                "predicted_sign_and_size": f"{spec['prediction']} versus R0; scenario range {spec['range']}; MODEL only. Absolute live changes below 0.01 are no evidence.",
                "falsifier": spec["falsifier"],
            },
            "git_sha_at_build": git,
            "builder_sha256": script_sha,
            "response_builder_sha256": response_script_sha,
            "ledger_append_needed": previous is None,
        }
        records.append(record)
        print(
            f"BUILT {short_id}: moved={stats['removed']} ({stats['pct_changed']:.3f}%), "
            f"CV={stats['block_density_cv_before']:.4f}->{stats['block_density_cv_after']:.4f}, sha256={sha_nan}"
        )

    for record in records:
        if record["ledger_append_needed"]:
            append_variant(
                {k: v for k, v in record.items() if k in {
                    "id", "parent", "axis", "value", "n_dots", "pct_changed", "sha256",
                    "status", "predicted_change", "file_zeros", "file_nan", "sha8",
                    "change_desc", "receipt_score", "receipt_date", "notes"
                }}, LEDGER
            )

    report = {
        "schema": "gemsdoe92.concentration-session.v1",
        "session_date_utc": DATE,
        "axis": "CONCENTRATION",
        "parent": PARENT_ID,
        "parent_claim": {"score": 0.2778, "evidence_label": "CLAIM", "receipt": False},
        "exact_parent_rebuild": {
            "n_dots": N_DOTS,
            "zeros_sha256": PARENT_SHA_ZEROS,
            "nan_sha256": PARENT_SHA_NAN,
            "matches_recorded_hashes": True,
        },
        "axis_selection": {
            "initial_axis": "SNAP",
            "snap_rasters_built": 0,
            "snap_infeasible_parent_dots": snap_infeasible,
            "reason": "These inherited <=3px dots have no destination simultaneously <=2px away and >3px from the catalogue; no SNAP constraint was relaxed.",
            "selected_axis": "CONCENTRATION",
        },
        "design": {
            "block_size": "10 px = 1 km at 100 m",
            "prior": "block mean of equal-weight percentile-rank TMI HG, absolute gravity HG, and detrended-elevation slope; no labels",
            "common_compliance_movers": 2171,
            "destination_rule": "round-robin descending block prior; nearest-to-block-centre legal un-emitted H19-5 support pixel",
            "count_and_mass": "37,654 dots, 1.0 each, unchanged",
            "seed": "not used; deterministic sorting and tie breaks",
        },
        "input_manifest_sha256": sha256_file(ROOT / "registry" / "session_manifest.json"),
        "input_count": len(inputs),
        "variants": records,
        "scope_note": "No submission, leaderboard, hidden labels, or off-manifest data accessed. Candidate rasters are local and gitignored. Predictions are MODEL judgments, never scores.",
    }
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {EVIDENCE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
