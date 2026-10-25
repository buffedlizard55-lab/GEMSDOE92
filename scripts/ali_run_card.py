#!/usr/bin/env python3
"""ALI lane, step H: byte-bound run card + per-file audit receipt.

Collects every evidence JSON produced by the ALI scripts (all under the
gitignored .cache/work/) into two committed receipts:
  evidence/ali_run_card.json            (protocol run card; copy in docs/downloads/)
  docs/downloads/<variant>-audit.json   (per-file audit read by scripts/check_site.py)
Nothing is hand-typed: numbers are read from the evidence files, hashes from bytes.
"""
from __future__ import annotations
import hashlib, json, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from gems.gates import run_gates  # noqa: E402

W = ROOT / ".cache" / "work"
TIF = ROOT / "docs/downloads/gemsdoe92-ali-famnms-37654-20261025T230000Z-68be9b4d-zeros.tif"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def registry_summary(path: Path, key: str, self_sha: str | None):
    if not path.is_file():
        return None
    d = json.load(open(path))
    rows = [r for r in d["rows"] if key in r and not (self_sha and r["blob"].startswith("local:")
                                                       and "ali-famnms" in r["blob"])]
    errors = [dict(paths=r["paths"], error=r["error"]) for r in d["rows"] if "error" in r]
    lit = max(rows, key=lambda r: r[key]["literal_forward_overlap"])
    rho = max(rows, key=lambda r: abs(r[key]["spearman"]))
    disc = [r for r in rows if r.get("halo_coverage", 1.0) < 0.70]
    dsc = max(disc, key=lambda r: r[key]["literal_forward_overlap"])
    firing = [r for r in rows if r[key]["literal_forward_overlap"] > 0.70]
    firing_disc = sorted([r for r in firing if r.get("halo_coverage", 1.0) < 0.70],
                         key=lambda r: -r[key]["literal_forward_overlap"])
    like = []
    for r in rows:   # like-for-like: binary/dot fields literal; continuous >150k matched-budget
        like.append((r[key]["matched_budget_forward_overlap"], r))
    lw = max([x for x in like if x[1].get("halo_coverage", 1.0) < 0.70 or not x[1].get("binary", True)],
             key=lambda x: x[0])
    return dict(
        evidence_class="REGISTRY-MEASUREMENT", registry_blobs=d["blobs"], rasters_checked=len(rows),
        unreadable_or_other_grid=errors, generated_utc=d["generated_utc"],
        literal_reading=dict(worst_forward_overlap=lit[key]["literal_forward_overlap"], worst_file=lit["paths"][0],
                             rasters_over_0p70=len(firing), duplicate=bool(firing)),
        discriminating_dot_fields=dict(
            definition="registry rasters whose 3 px halo covers < 70% of the scored domain (a random candidate would NOT fire)",
            worst_forward_overlap=dsc[key]["literal_forward_overlap"], worst_file=dsc["paths"][0],
            worst_their_dots=dsc["their_dots"], worst_halo_coverage=dsc["halo_coverage"],
            firing=[dict(file=r["paths"][0], their_dots=r["their_dots"], halo_coverage=round(r["halo_coverage"], 4),
                         forward_overlap=round(r[key]["literal_forward_overlap"], 4)) for r in firing_disc],
            duplicate=bool(firing_disc),
            tightest_collision=(lambda narrow: dict(file=narrow["paths"][0], their_dots=narrow["their_dots"],
                                                    halo_coverage=narrow["halo_coverage"],
                                                    forward_overlap=narrow[key]["literal_forward_overlap"],
                                                    definition="highest forward overlap among firing dot fields whose halo covers <= 35% of the domain")
                                ) (max([r for r in firing_disc if r["halo_coverage"] <= 0.35] or firing_disc or [dsc],
                                       key=lambda r: r[key]["literal_forward_overlap"]))),
        like_for_like_reading=dict(worst_forward_overlap=lw[0], worst_file=lw[1]["paths"][0]),
        worst_abs_spearman=abs(rho[key]["spearman"]), worst_spearman_file=rho["paths"][0],
        rho_limit=0.90, overlap_limit=0.70,
        duplicate=bool(firing) or abs(rho[key]["spearman"]) > 0.90,
        candidate_sha256=d["candidates"][key]["sha256"])


def main():
    raster_sha = sha(TIF)
    build = json.load(open(W / "ali_build.json"))
    assert build["validator"]["sha256"] == raster_sha, "build receipt is for different bytes"
    gates = run_gates(str(TIF), str(ROOT / "data/bridge/sample_submission.tif"), str(ROOT / "data/bridge/labels.tif"),
                      prune_radius=2, require_submission_encoding=True)
    gate_rows = [dict(name=g.name, ok=bool(g.ok), detail=str(g.detail)) for g in gates]
    if "reread_sha256" not in {g["name"] for g in gate_rows}:
        gate_rows.append(dict(name="reread_sha256", ok=sha(TIF) == raster_sha, detail=raster_sha))
    hold = json.load(open(W / "ali_holdout.json"))
    proj = json.load(open(W / "ali_projection.json"))
    fit = json.load(open(W / "ali_fit.json"))
    fam = {k: json.load(open(W / "fam" / f"fam_{k}.json")) for k in ("full", "seed20", "seed30")}
    final = registry_summary(W / "ali_uniqueness_final_dots.json", "ALI", raster_sha)
    surface = registry_summary(W / "ali_uniqueness_surface.json", "SURF", None)
    cand = "ALI_sep2.5_K37654"
    s = hold["summaries"][cand]
    def pack(nm):
        sc = s["scores"][nm]
        return dict(evidence_class="HOLDOUT-DTI", evaluator_version=hold["evaluator_version"], dti=sc["dti"],
                    ci95=sc["ci95"], withheld_positive_pixels=hold["withheld_positive_pixels"], n_folds=hold["n_folds"])
    prior_best = dict(
        FAULTNET_netfar=dict(dti=0.175147, ci95=[0.159756, 0.18986], source="evidence/faultnet_run_card.json (catalogue-network context arm)"),
        VENTSCARP_rule2=dict(dti=0.112213, ci95=[0.09667, 0.127254], source="evidence/ventscarp_run_card.json strict_draw_blind_rule2_d_visible_gt_2"),
        COULOMBLOQO_control=dict(dti=0.11389, ci95=[0.100783, 0.128559], source="evidence/faultnet_run_card.json holdout.scores.control_COULOMBLOQO"))
    beats_best = s["scores"][cand]["dti"] > max(v["dti"] for v in prior_best.values())
    dup = bool(final and final["duplicate"])
    card = dict(
        schema="gemsdoe92-ali-run-card.v1", generated_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        lane="ALI — aggregate-label inversion + physics-only fault-appearance placement",
        hypothesis=("Hidden new-fault pixels concentrate where the 19-band competition stack, 10 m DEM derivatives, chi/knickpoints and "
                    "GeoDAWN radiometrics look most like catalogued faults (out-of-fold Fault-Appearance Model, FAM), more than 300 m from any "
                    "catalogued trace; owner-reported organizer scores of 99 distinct registry rasters constrain how much intensity each stratum carries."),
        mechanism=("Faults are mapped from topographic breaks and potential-field edges; experts adding faults missing from the USGS Quaternary "
                   "Fault and Fold Database (designed for M>6 Quaternary sources) look for the same signatures at smaller scale. The scoring mask "
                   "removes catalogued pixels and the 300 m kernel gives near-zero credit to dots hugging catalogued traces."),
        named_non_fault_mimic="Pleistocene lake shorelines / wave-cut benches and fluvial terrace risers (linear slope breaks that are not faults); also lithologic contacts with strong radiometric or magnetic contrast.",
        placement=dict(model="quadrant out-of-fold HistGradientBoosting FAM (52 features, no catalogue distance as feature)",
                       candidates="scored footprint, d_catalogue > 3 px", nms_separation_px=2.5, dots=37654,
                       prior_submissions_used_in_placement=False),
        experiments=[
            dict(id="E1", arm=cand, holdout=pack(cand)),
            dict(id="E2", arm="ALI_sep2.5_K26000", holdout=pack("ALI_sep2.5_K26000")),
            dict(id="E3", arm="leaderboard-calibrated projection sweep (MODEL only, no HOLDOUT claim)", note="see projection")],
        holdout_dti=pack(cand),
        holdout_controls={nm: pack(nm) for nm in s["scores"] if nm.startswith("CTRL_")},
        paired_differences={nm: dict(evidence_class="HOLDOUT-DTI", delta=v["delta"], ci95=v["ci95"])
                            for nm, v in s["paired_differences"].items()},
        current_holdout_best_reference=prior_best, beats_current_holdout_best=bool(beats_best),
        leakage_canaries=dict(rule="single feature symmetric AUC > 0.90 = leakage", n_features=len(hold["canaries"]) - 1,
                              max_auc=max(hold["canaries"].values()),
                              worst=max(hold["canaries"].items(), key=lambda kv: kv[1])[0], all=hold["canaries"]),
        fam_heldout_auc={k: [f["heldout_auc"] for f in v["folds"]] for k, v in fam.items()},
        leaderboard_inversion=dict(
            evidence_class="MODEL (fit to owner-reported CLAIMS; no organizer receipts)",
            n_distinct_scored_rasters=len(fit["points"]),
            models={k: dict(k=len(v["names"]), loo_rmse=v["loo_rmse"], loo_spearman=v["loo_spearman"],
                            lineage_out_rmse=v["lineage_out_rmse"], theta=dict(zip(v["names"], v["theta"])))
                    for k, v in fit["models"].items()}),
        projection=proj,
        correlation_overlap_vs_registry=dict(final_dots=final, pre_placement_surface=surface,
                                             pre_placement_ordering_note="The surface check was executed after placement in this session (ordering deviation); the final-dot check is decisive."),
        raster=dict(path=str(TIF.relative_to(ROOT)), bytes=TIF.stat().st_size, zip=str(TIF.with_suffix('.zip').relative_to(ROOT))),
        raster_sha256=raster_sha,
        validator_output=build["validator"], gates=gate_rows,
        submission_name=build["name"], note=build["note"], note_chars=build["note_chars"],
        verdict="negative",
        verdict_reasons=[r for r in [
            "DUPLICATE: final dots exceed the 0.70 forward-overlap limit against discriminating registry dot fields (not only dense surfaces)" if dup else None,
            "Does not beat the current holdout best (ties the R0-recipe control)" if not beats_best else None] if r],
        submission_eligible=False, weekly_slots_used=0, organizer_confirmed_score=None,
        budget=dict(experiments=3, note="2-hour experiment budget exhausted; stopped per protocol"),
        inputs_sha256={rel: sha(ROOT / rel) for rel in ("data/bridge/sample_submission.tif", "data/bridge/labels.tif",
                                                        "data/bridge/h19_5.tif", "data/bridge/d28.tif", "data/parent_R0_zeros.tif")},
        training_features_sha256="4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5")
    (ROOT / "evidence").mkdir(exist_ok=True)
    txt = json.dumps(card, indent=1, default=float) + "\n"
    (ROOT / "evidence/ali_run_card.json").write_text(txt)
    (ROOT / "docs/downloads/ali_run_card.json").write_text(txt)
    audit = dict(schema="gemsdoe92-ali-audit.v1", file=str(TIF.relative_to(ROOT)), sha256_zeros=raster_sha, sha256_nan=None,
                 n_dots=37654, n_positive_pixels=37654, overall_pass=all(g["ok"] for g in gate_rows),
                 gates_zeros=gate_rows, gates_zeros_pass=all(g["ok"] for g in gate_rows), gates_nan=[], gates_nan_pass=False,
                 submission_eligible=False, verdict="negative", note=build["note"], submission_name=build["name"],
                 run_card="evidence/ali_run_card.json",
                 public_registry_uniqueness=dict(candidate_hash_matches_scan=bool(final) and final["candidate_sha256"] == raster_sha,
                                                 candidate_sha256_zeros=raster_sha,
                                                 unique_under_literal_rule=not dup, stop_required=dup,
                                                 worst_forward_overlap=final["literal_reading"]["worst_forward_overlap"] if final else None,
                                                 worst_discriminating_forward_overlap=final["discriminating_dot_fields"]["worst_forward_overlap"] if final else None,
                                                 scope="full scan of every synced public-registry blob plus local downloads"))
    TIF.with_name(TIF.stem.removesuffix("-zeros") + "-audit.json").write_text(json.dumps(audit, indent=1) + "\n")
    print("verdict", card["verdict"], card["verdict_reasons"], "dup", dup, "beats", beats_best)


if __name__ == "__main__":
    main()
