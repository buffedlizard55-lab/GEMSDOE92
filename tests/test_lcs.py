"""Unit tests for the LCS lane (gems/lcs.py) and the tiered uniqueness verdict (gems/uniqueness_policy.py)."""
from __future__ import annotations

import json

import numpy as np
import pytest

from gems import lcs, uniqueness_policy as up


def test_credit_inversion_round_trips_the_official_algebra():
    for score, n in ((0.2778, 37654), (0.1922, 121131), (0.05, 44090)):
        c = lcs.credit_per_dot(score, n)
        assert lcs.project_dti(c * n, n) == pytest.approx(score, abs=1e-9)


def test_credit_inversion_rejects_impossible_scores():
    with pytest.raises(ValueError):
        lcs.credit_per_dot(0.0, 10)
    with pytest.raises(ValueError):
        lcs.credit_per_dot(1.0, 10)
    with pytest.raises(ValueError):
        lcs.credit_per_dot(0.3, 0)


def test_random_dot_credit_is_below_break_even_and_scales_with_truth_density():
    c = lcs.random_dot_credit(5_167_373)
    assert 0.02 < c < 0.03 < lcs.BREAK_EVEN_CREDIT
    assert lcs.random_dot_credit(5_167_373, g=25_000.0) == pytest.approx(2 * c)


def test_halo_survival_is_low_near_the_catalogue_and_one_far_away():
    h = w = 400
    d_cat = np.abs(np.arange(w) - 200).astype(float)[None, :].repeat(h, 0)      # vertical fault at x=200
    fp = np.ones((h, w), bool)
    skeleton = np.zeros((h, w), bool)
    rng = np.random.default_rng(0)
    p = 0.02 + 0.5 * np.exp(-d_cat / 4.0)                                           # enriched near the fault
    skeleton[rng.random((h, w)) < p] = True
    edges, surv, bg = lcs.halo_survival_profile(d_cat, fp, skeleton, max_d=60, background_from=40)
    assert np.interp(2.0, edges, surv) < 0.5
    assert np.interp(40.0, edges, surv) > 0.9
    assert 0.0 < bg < 2.0
    assert np.all((surv >= 0) & (surv <= 1))


def test_lane_weights_are_nonnegative_and_monotone_in_credit():
    w = lcs.lane_weights({"a": 0.01, "b": 0.05, "c": 0.15}, c_random=0.0228)
    assert w["a"] == 0.0 and 0.0 < w["b"] < w["c"]


def test_stratified_excess_has_zero_mean_inside_each_stratum():
    rng = np.random.default_rng(1)
    d = rng.uniform(2.5, 40, size=(60, 60)).astype(np.float32)
    votes = rng.normal(5, 2, size=(60, 60)).astype(np.float32) + d / 10     # votes drift with distance
    strata = lcs.stratum_index(d)
    pool = np.ones_like(d, bool)
    z = lcs.stratified_excess(votes, strata, pool)
    for k in range(int(strata.max()) + 1):
        sel = strata == k
        if sel.any():
            assert abs(z[sel].mean()) < 1e-4


def _grid_candidates(n_side=40):
    yy, xx = np.mgrid[0:n_side, 0:n_side]
    return np.column_stack([yy.ravel(), xx.ravel()]).astype(np.int32)


def test_spaced_greedy_enforces_the_spacing_floor_and_the_count():
    yx = _grid_candidates()
    order = np.arange(len(yx))
    sel = lcs.spaced_capped_greedy(order, yx, (40, 40), n_target=50)
    picked = yx[sel.index]
    assert sel.n_selected == 50
    d2 = ((picked[:, None, :] - picked[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d2, 10 ** 6)
    assert d2.min() >= lcs.MIN_SPACING_SQ


def test_cap_is_never_exceeded():
    yx = _grid_candidates()
    member = np.zeros((len(yx), 1), bool)
    member[yx[:, 1] < 20, 0] = True                      # left half is inside the raster's halo
    order = np.arange(len(yx))                           # tries left-half first
    sel = lcs.spaced_capped_greedy(order, yx, (40, 40), n_target=40, member=member, cap=10)
    assert member[sel.index, 0].sum() <= 10
    assert sel.rejected_cap > 0


def test_lagrangian_reaches_a_feasible_selection_on_a_small_instance():
    yx = _grid_candidates(50)
    n = len(yx)
    rng = np.random.default_rng(3)
    score = rng.random(n) + (yx[:, 1] < 25) * 2.0        # score prefers the left half
    member = np.zeros((n, 2), bool)
    member[yx[:, 1] < 25, 0] = True                      # raster 0 covers the left half
    member[:, 1] = rng.random(n) < 0.3
    rec, hist = lcs.lagrangian_capped_selection(score, yx, (50, 50), n_target=60, member=member,
                                                cap_fraction=0.6, iters=80)
    assert len(rec["index"]) == 60
    assert rec["max_overlap"] <= 0.6 + 1e-9
    assert any(h["feasible"] for h in hist)


def _gate_doc(s_over=0, l_over=0, t_over=3, rho=0.1):
    def tier(n_over, mx):
        return dict(n_distinct=10, n_files=12, max_forward_overlap=mx, n_distinct_over_0_70=n_over,
                    n_files_over_0_70=n_over, max_abs_spearman=rho, n_distinct_over_rho_0_90=0, worst=[])
    return dict(tier_S=tier(s_over, 0.65 if not s_over else 0.8), tier_L=tier(l_over, 0.66 if not l_over else 0.8),
                tier_T_all=tier(t_over, 1.0 if t_over else 0.66))


def test_policy_loader_requires_unchanged_thresholds(tmp_path):
    good = json.loads(up.POLICY.read_text())
    assert good["thresholds"] == {"forward_overlap": 0.70, "abs_spearman": 0.90, "radius_px": 3.0}
    bad = dict(good, thresholds_unchanged=False)
    p = tmp_path / "p.json"
    p.write_text(json.dumps(bad))
    with pytest.raises(ValueError):
        up.load_policy(p)
    p.write_text(json.dumps(dict(good, decisive_tier="X")))
    with pytest.raises(ValueError):
        up.load_policy(p)


def test_decide_reports_all_tiers_and_follows_the_decisive_tier():
    pol = up.load_policy()
    out = up.decide(_gate_doc(), _gate_doc(), pol)
    assert out["tiers"]["S"]["passed"] and out["tiers"]["L"]["passed"] and not out["tiers"]["T"]["passed"]
    assert out["literal_passed"] is False
    assert out["decisive_passed"] == out["tiers"][pol["decisive_tier"]]["passed"]


def test_a_single_failing_phase_fails_the_tier():
    pol = up.load_policy()
    out = up.decide(_gate_doc(), _gate_doc(s_over=1), pol)      # final phase fails Tier S
    assert out["tiers"]["S"]["passed"] is False
    out2 = up.decide(_gate_doc(rho=0.95), _gate_doc(), pol)     # surface phase rank correlation fails
    assert not out2["tiers"]["S"]["passed"]


def test_literal_tier_cannot_pass_when_any_blanket_overlaps():
    pol = up.load_policy()
    assert up.decide(_gate_doc(t_over=0), _gate_doc(t_over=0), pol)["literal_passed"] is True
    assert up.decide(_gate_doc(t_over=1), _gate_doc(t_over=0), pol)["literal_passed"] is False


from gems import verdict as vd  # noqa: E402


def _pol(decisive=True, literal=False):
    return dict(decisive_passed=decisive, decisive_tier="S", literal_passed=literal)


def test_verdict_download_requires_format_only():
    v = vd.derive(True, _pol(decisive=False), True, True, None)
    assert v["ok_to_download"] is True and v["ok_to_submit"] is False
    assert any("uniqueness" in r for r in v["blocking_reasons"])


def test_verdict_submit_needs_every_automated_gate():
    assert vd.derive(True, _pol(), True, True, None)["ok_to_submit"] is True
    assert vd.derive(True, _pol(), False, True, None)["ok_to_submit"] is False
    assert vd.derive(True, _pol(), True, False, None)["ok_to_submit"] is False
    assert vd.derive(False, _pol(), True, True, None)["ok_to_submit"] is False


def test_verdict_promote_requires_paired_ci_above_zero_vs_holdout_best():
    assert vd.derive(True, _pol(), True, True, dict(delta=0.001, ci95=[-0.0005, 0.002]))["verdict"] == "negative"
    assert vd.derive(True, _pol(), True, True, dict(delta=-0.001, ci95=[-0.002, -0.0005]))["verdict"] == "negative"
    assert vd.derive(True, _pol(), True, True, dict(delta=0.001, ci95=[0.0002, 0.002]))["verdict"] == "promote"
    # promotion can never rescue an ineligible file
    assert vd.derive(True, _pol(decisive=False), True, True, dict(delta=0.01, ci95=[0.005, 0.02]))["verdict"] == "negative"


def test_verdict_reports_literal_rule_separately():
    v = vd.derive(True, _pol(literal=False), True, True, None)
    assert v["literal_registry_rule_passed"] is False and v["ok_to_submit"] is True
