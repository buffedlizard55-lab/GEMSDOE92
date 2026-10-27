"""Known unsafe runners stop before loading data, placement, or overwrites."""
from __future__ import annotations

from pathlib import Path
import importlib
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_blindext_stops_before_creating_or_overwriting_files(tmp_path, monkeypatch):
    from scripts import build_blindext_submission as runner

    previous = tmp_path / 'prior.tif'
    previous.write_bytes(b'previous immutable artifact')
    monkeypatch.setattr(runner, 'DOWNLOADS', tmp_path)
    monkeypatch.setattr(runner, 'BRIDGE', tmp_path / 'missing-inputs')
    with pytest.raises(SystemExit, match='literal pre-placement registry duplicate'):
        runner.main()
    assert previous.read_bytes() == b'previous immutable artifact'
    assert list(tmp_path.iterdir()) == [previous]


def test_gapbridge_stops_before_its_import_time_work(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit, match='literal pre-placement registry duplicate'):
        runpy.run_path(str(ROOT / 'scripts/run_gapbridge.py'))
    assert list(tmp_path.iterdir()) == []


MAIN_RUNNERS = [
    'run_blindfault', 'run_poissonflex', 'run_poissonknick', 'run_provincetoe',
    'run_riedelvalve', 'run_riedelvent', 'run_ventscarp', 'run_listricdip',
    'finalize_poissonknick', 'finalize_poissonflex', 'finalize_netexpand',
    'finalize_faultnet', 'finalize_blindfault', 'build_radiodecouple_submission',
    'ali_build_submission', 'build_visible_collar_submission',
    'build_adaptive_crest_submission', 'package_vario', 'run_relayconduit',
]
STAGES = [
    ('run_vario', 'stage_stack', ()), ('run_vario', 'stage_holdout', ()),
    ('run_vario', 'stage_deploy', ()), ('run_faultnet', 'stage_holdout', ()),
    ('run_faultnet', 'stage_deploy', ()), ('run_faultnet', 'stage_farcontrol', ()),
    ('run_netexpand', 'stage_stack', ()), ('run_netexpand', 'stage_holdout', ()),
    ('run_netexpand', 'stage_deploy', ()),
    ('run_relayconduit', 'stage_stack_and_canary', ()),
    ('run_relayconduit', 'stage_deploy_and_screen', ()),
    ('run_relayconduit', 'stage_holdout_seed', (20,)),
    ('run_relayconduit', 'stage_finalize', (1.0,)),
]


@pytest.mark.parametrize('module,entrypoint,args',
                         [(name, 'main', ()) for name in MAIN_RUNNERS] + STAGES)
def test_legacy_entrypoints_stop_before_output_mutation(tmp_path, monkeypatch, module, entrypoint, args):
    runner = importlib.import_module(f'scripts.{module}')
    previous = tmp_path / 'prior.tif'
    previous.write_bytes(b'prior evidence')
    # Make any unguarded use of these common output roots visible to the test.
    for attribute in ('DOWNLOADS', 'EVIDENCE', 'CACHE', 'CACHE_LANE'):
        if hasattr(runner, attribute):
            monkeypatch.setattr(runner, attribute, tmp_path / attribute)
    with pytest.raises(SystemExit, match='literal pre-placement registry duplicate'):
        getattr(runner, entrypoint)(*args)
    assert previous.read_bytes() == b'prior evidence'
    assert list(tmp_path.iterdir()) == [previous]
