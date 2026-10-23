"""Synthetic tests for the session's compliance-aware concentration dose."""

import numpy as np

from scripts import build_concentration_variants as session


def test_move_dose_holds_count_and_combines_compliance_with_low_prior(
    monkeypatch,
):
    monkeypatch.setattr(session, "N_DOTS", 20)
    monkeypatch.setattr(session, "BLOCK_PX", 2)
    shape = (8, 8)
    r0 = np.zeros(shape, dtype=bool)
    r0[:5, :4] = True  # exactly 20 parent dots
    parent_yx = np.argwhere(r0)
    foot = np.ones(shape, dtype=bool)
    d_cat = np.full(shape, 10.0)
    # Two inherited dots require compliance relocation. A 20% dose moves four,
    # so exactly two additional dots must come from the lowest-prior blocks.
    d_cat[0, 0] = 2.0
    d_cat[0, 1] = 2.0
    legal = foot & (d_cat > session.CLEARANCE_PX)
    prior = np.full(shape, 0.1, dtype=np.float32)
    prior[4:, 4:] = 0.9

    dots, stats = session.move_dose(0.20, r0, prior, legal, d_cat, foot)

    assert len(dots) == 20
    assert len(dots.keys) == 20
    assert stats["removed"] == stats["added"] == 4
    assert stats["mandatory_compliance_movers"] == 2
    assert stats["additional_low_prior_movers"] == 2
    assert np.all(d_cat[dots.ys, dots.xs] > session.CLEARANCE_PX)
    assert np.all(legal[dots.ys, dots.xs])
    assert stats["mean_prior_destinations"] > stats["mean_prior_movers_before"]
    mask = np.zeros(shape, dtype=bool)
    mask[dots.ys, dots.xs] = True
    assert np.count_nonzero(r0 & ~mask) == 4
    assert np.count_nonzero(mask & ~r0) == 4
    assert np.isfinite(stats["block_density_cv_before"])
    assert np.isfinite(stats["block_density_cv_after"])
