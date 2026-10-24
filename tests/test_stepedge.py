"""STEPEDGE surface: synthetic step/channel/ridge discrimination.

The geological claim under test is aperture cancellation: a sustained step
keeps a large two-sided offset, a V-channel and an inverted-V ridge cancel.
"""

import numpy as np

from gems.stepedge import lane_surface, sustained_step, tensor_direction


def _field(kind: str, n: int = 80) -> np.ndarray:
    cols = np.arange(n, dtype=np.float32)[None, :]
    if kind == "step":
        base = np.where(cols >= n // 2, 6.0, 0.0)
    elif kind == "channel":  # V: low in the middle, equal height both sides
        base = -6.0 * np.exp(-((cols - n // 2) ** 2) / 8.0)
    elif kind == "ridge":    # inverted V
        base = 6.0 * np.exp(-((cols - n // 2) ** 2) / 8.0)
    else:
        raise ValueError(kind)
    return np.repeat(base.astype(np.float32), n, axis=0)


def test_step_beats_channel_and_ridge_at_line():
    # One field containing all three landforms, ranked ONCE (as on the real
    # footprint). Ranking each landform in its own field would be vacuous:
    # percentile ranks are relative to whatever field they are computed on.
    n = 80
    combo = np.concatenate([_field("step", n), _field("channel", n),
                            _field("ridge", n)], axis=1)
    valid = np.ones(combo.shape, bool)
    surf = lane_surface(combo, valid)
    s, step_m = surf["S_raw"], surf["step"]
    rows = slice(20, 60)
    s_step = s[rows, 38:43].mean()
    s_chan = s[rows, 80 + 38:80 + 43].mean()
    s_ridge = s[rows, 160 + 38:160 + 43].mean()
    assert s_step > 0.5
    # Rank-based S compresses ratios on a mostly-flat synthetic field (any
    # non-zero step outranks the flat majority); ordering must still hold.
    # The quantitative separation is asserted in metres below, and on real
    # data by the SGMC screen -- not by a synthetic rank ratio.
    assert s_step > s_chan
    assert s_step > s_ridge
    # And in raw metres the aperture-persistent offset separates them ~4x.
    assert step_m[rows, 38:43].mean() > 3.0 * step_m[rows, 80 + 38:80 + 43].mean()


def test_direction_points_across_a_vertical_step():
    valid = np.ones((80, 80), bool)
    coh, u_row, u_col = tensor_direction(_field("step"), valid)
    mid = (slice(20, 60), slice(35, 46))
    # Across a vertical (N-S) step the dominant gradient is E-W (columns).
    assert np.abs(u_col[mid]).mean() > 0.9
    assert np.abs(u_row[mid]).mean() < 0.2
    assert coh[mid].mean() > 0.9


def test_sustained_step_is_offset_width_not_derivative():
    valid = np.ones((80, 80), bool)
    step_field = _field("step")
    _, u_row, u_col = tensor_direction(step_field, valid)
    step = sustained_step(step_field, valid, u_row, u_col)
    # At the scarp face the sustained offset recovers ~the 6 m throw.
    assert step[40, 40] > 4.0
    # Far from the face (both samples on the same side) it decays to ~0.
    assert step[40, 60] < 0.5
