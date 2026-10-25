"""NETEXPAND lane unit tests (synthetic arrays only; no competition data)."""
import numpy as np

from gems import netexpand as nx


def _synthetic():
    rng = np.random.default_rng(7)
    sh = (48, 40)
    foot = np.ones(sh, bool)
    f32 = lambda: rng.normal(size=sh).astype(np.float32)  # noqa: E731
    return dict(rtp=f32(), tmi=f32(), tmi_vg=f32(), grav_vg=f32(), grav_anom=f32(),
                grav_hg=f32(), depth_to_base=np.abs(f32()),
                cond_surf=np.abs(f32()) + 1.0, footprint=foot, valid=foot)


def test_new_features_finite_and_ranked():
    feats = nx.compute_netexpand_features(**_synthetic())
    assert tuple(feats) == nx.NEW_FEATURE_NAMES
    for v in feats.values():
        assert v.dtype == np.float32 and np.isfinite(v).all()
        assert 0.0 <= float(v.min()) and float(v.max()) <= 1.0


def test_pure_crest_channel_range():
    d = _synthetic()
    feats = nx.compute_netexpand_features(**d)
    L = nx.build_pure_crest_channel(feats, np.full((48, 40), 0.5, np.float32), d["valid"])
    assert np.isfinite(L).all() and 0.0 <= float(L.min()) and float(L.max()) <= 1.0


def test_branch_columns_partition():
    for ctx in (True, False):
        cols = nx.branch_columns(with_context=ctx)
        if ctx:
            assert cols["full"] == tuple(range(45))
            assert set(nx.CONTEXT_COLS) <= set(cols["debiased"])
        else:
            assert not (set(nx.CONTEXT_COLS) & set(cols["full"]))
            assert not (set(nx.CONTEXT_COLS) & set(cols["sub"]))
        assert set(nx.NEW_COLS) <= set(cols["debiased"]) and set(nx.NEW_COLS) <= set(cols["sub"])
        assert set(nx.LISTRIC_COLS) <= set(cols["sub"])


def test_feature_builder_takes_no_catalogue():
    import inspect
    params = set(inspect.signature(nx.compute_netexpand_features).parameters)
    assert not any("cat" in p or "label" in p or "fault" in p for p in params)
