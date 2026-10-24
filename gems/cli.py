"""Command line entry points. Human-facing; no network, no credentials."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import ledger
from .gates import run_gates, summarise
from .manifest import verify


def cmd_validate(a) -> int:
    results = run_gates(
        a.candidate,
        a.reference,
        catalogue_path=a.catalogue,
        prune_radius=a.prune_radius,
        require_submission_encoding=True,
    )
    ok, report = summarise(results)
    print(report)
    if a.json:
        print(json.dumps([{"gate": r.name, "ok": r.ok, "detail": r.detail}
                          for r in results], indent=2))
    return 0 if ok else 1


def cmd_manifest(a) -> int:
    rep = verify(a.manifest, a.data_root)
    for e in rep.get("entries", []):
        print(f"  {e['status']:12s} {e['path']}")
    if rep.get("error"):
        print(f"ERROR: {rep['error']}", file=sys.stderr)
    for p in rep.get("problems", []):
        print(f"  PROBLEM: {p}", file=sys.stderr)
    print("RESULT:", "OK" if rep["ok"] else "FAILED")
    return 0 if rep["ok"] else 1


def cmd_parent(a) -> int:
    from .parent import (ParentUnavailable, Recipe, compare_claimed_invariants,
                         verify_inputs, verify_pinned_artefact)
    try:
        recipe = Recipe.load(a.recipe)
    except ParentUnavailable as e:
        print(f"PARENT UNAVAILABLE: {e}", file=sys.stderr)
        return 2

    if recipe.mode == "pinned_artefact":
        report = verify_pinned_artefact(recipe, a.data_root, measure=not a.no_measure)
        for enc, got in report["measured"].items():
            # "remeasured" is the invariant block, not an encoding entry
            if isinstance(got, dict) and "sha256" in got:
                print(f"  {enc:8s} {got['sha256'][:12]}… {got['bytes']} B  {got['path']}")
        remeasured = report["measured"].get("remeasured")
        if remeasured:
            drift = compare_claimed_invariants(a.recipe, remeasured)
            for k, v in remeasured.items():
                flag = "  <-- DRIFT" if any(d.startswith(f"{k}:") for d in drift) else ""
                print(f"  {k:28s} {v}{flag}")
            if drift:
                for d in drift:
                    print(f"  PROBLEM: record disagrees with raster: {d}", file=sys.stderr)
        for p in report["problems"]:
            print(f"  PROBLEM: {p}", file=sys.stderr)
        if report["ok"] and not (remeasured and compare_claimed_invariants(a.recipe, remeasured)):
            print(f"PARENT VERIFIED (pinned artefact): {recipe.parent_id} "
                  f"sha256 {recipe.expected_sha256[:12]}…")
            return 0
        print("Refusing to approximate the parent: the pinned bytes or the recorded "
              "invariants do not hold.", file=sys.stderr)
        return 2

    problems = verify_inputs(recipe, a.data_root)
    if problems:
        print("PARENT UNAVAILABLE -- pinned inputs unusable:", file=sys.stderr)
        for p in problems:
            print(f"  {p}", file=sys.stderr)
        print("Refusing to approximate the parent. Provide the pinned inputs.",
              file=sys.stderr)
        return 2
    print(f"inputs verified for {recipe.parent_id}; rebuild via gems.builders")
    return 0


def cmd_ledger(a) -> int:
    rows = ledger.load(a.path)
    if not rows:
        print("ledger is empty (or absent)")
        return 0
    print(f"{len(rows)} rows")
    ids, shas = set(), set()
    for r in rows:
        if r.get("sha256") in shas:
            print(f"  DUPLICATE sha256: {r.get('id')}")
        shas.add(r.get("sha256"))
        if r.get("id") in ids:
            print(f"  DUPLICATE id: {r.get('id')}")
        ids.add(r.get("id"))
        print(f"  {r.get('id','?'):28s} {ledger.evidence(r):8s} "
              f"{r.get('receipt_score','')}")
    best_id, best = ledger.best_receipt(rows)
    print(f"best RECEIPT: {best_id or 'none'} {best if best is not None else ''}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="gems", description="GEMS candidate toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="run the strict, upload-safe local format preflight")
    v.add_argument("candidate")
    v.add_argument("--reference", required=True)
    v.add_argument("--catalogue", default=None)
    v.add_argument("--prune-radius", type=int, default=None)
    v.add_argument("--json", action="store_true")
    v.set_defaults(fn=cmd_validate)

    m = sub.add_parser("manifest", help="verify pinned input hashes")
    m.add_argument("--manifest", default="registry/data_manifest.json")
    m.add_argument("--data-root", default="data")
    m.set_defaults(fn=cmd_manifest)

    p = sub.add_parser("parent", help="verify the parent recipe's inputs")
    p.add_argument("--recipe", default="registry/parents/R0.json")
    p.add_argument("--data-root", default="data")
    p.add_argument("--no-measure", action="store_true",
                   help="pinned-artefact mode: check sha256/length only, skip the "
                        "raster re-measurement of the recorded invariants")
    p.set_defaults(fn=cmd_parent)

    l = sub.add_parser("ledger", help="summarise the ledger")
    l.add_argument("--path", default=str(ledger.LEDGER))
    l.set_defaults(fn=cmd_ledger)

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
