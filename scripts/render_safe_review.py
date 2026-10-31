"""Fail-closed presentation of the 2026-10-28 / 2026-10-29 protocol review.

This renderer is intentionally rejection-only. It never infers eligibility from
model projections or from a format check. Inputs are historical owner claims and
byte-bound run cards; they are not organizer receipts.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import zipfile
from pathlib import Path

try:
    from scripts.render_20261029_pages import (
        load_lidarsintervalve_20261029,
        render_executive_summary_20261029,
        render_lidarsintervalve_hero,
    )
except ImportError:  # pragma: no cover - direct script execution from scripts/
    from render_20261029_pages import (  # type: ignore[no-redef]
        load_lidarsintervalve_20261029,
        render_executive_summary_20261029,
        render_lidarsintervalve_hero,
    )

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
DL = DOCS / 'downloads'


def load_dexp_kostrov_status():
    """Load and cryptographically bind the 2026-10-29 DEXP-KOSTROV-KOENDERINK research artifact."""
    card_path = DL / 'gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17_run_card.json'
    if not card_path.is_file():
        return None
    card = json.loads(card_path.read_text(encoding='utf-8'))
    tif_name = Path(card['raster']['file']).name
    zip_name = Path(card['raster']['zip_file']).name
    audit_name = Path(card['raster']['audit_file']).name
    tif_path = DL / tif_name
    zip_path = DL / zip_name
    audit_path = DL / audit_name
    if not tif_path.is_file() or not zip_path.is_file() or not audit_path.is_file():
        raise ValueError('DEXP-KOSTROV TIFF, ZIP, or audit JSON is missing')
    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    if digest != card.get('raster_sha256'):
        raise ValueError('DEXP-KOSTROV raster SHA-256 does not match its run card')
    with zipfile.ZipFile(zip_path) as archive:
        members = [n for n in archive.namelist() if not n.endswith('/')]
        if len(members) != 1 or Path(members[0]).name != tif_name:
            raise ValueError('DEXP-KOSTROV ZIP must contain exactly the bound TIFF')
        if hashlib.sha256(archive.read(members[0])).hexdigest() != digest:
            raise ValueError('DEXP-KOSTROV ZIP payload does not match TIFF bytes')
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('DEXP-KOSTROV must remain fail-closed (verdict=negative, submission_eligible=false)')
    if audit.get('sha256_zeros') != digest or audit.get('verdict') != 'negative' or audit.get('submission_eligible') is not False:
        raise ValueError('DEXP-KOSTROV audit disagrees with its byte-bound run card')
    gates = audit.get('gates_zeros', [])
    if audit.get('overall_pass') is not True or not gates or any(g.get('ok') is not True for g in gates):
        raise ValueError('DEXP-KOSTROV format audit is missing or has a failing gate')
    if not (0 < len(card.get('note', '')) <= 140):
        raise ValueError('DEXP-KOSTROV note must be 1..140 characters')

    h = card['holdout_dti']
    u = card['uniqueness']
    pi1 = u['pi1_operational_reading']
    lit = u['literal_reading']
    can = card['leakage_canaries']
    status = {
        'schema': 'gemsdoe92-candidate-readiness-v2',
        'artifact': 'DEXP-KOSTROV-KOENDERINK',
        'date': '2026-10-29',
        'file': f'downloads/{tif_name}',
        'zip': f'downloads/{zip_name}',
        'audit': audit_name,
        'run_card': card_path.name,
        'executive_summary': 'executive-summary-20261029-dexp-kostrov.html',
        'raster_sha256': digest,
        'zip_sha256': zip_digest,
        'n_dots': int(card['raster']['n_dots']),
        'bytes': int(card['raster']['bytes']),
        'submission_name': card['submission_name'],
        'note': card['note'],
        'verdict': 'negative',
        'submission_eligible': False,
        'download_status': 'OK TO DOWNLOAD FOR RESEARCH ONLY',
        'submission_status': 'DO NOT SUBMIT',
        'format_validation': {'status': 'all 11 gates pass', 'gate_count': len(gates)},
        'leakage_canaries': {
            'status': 'pass',
            'n_features_tested': can['n_features_tested'],
            'max_symmetric_auc': can['max_auc'],
            'threshold_auc': can['threshold_auc'],
        },
        'holdout_dti': {
            'evidence_class': 'HOLDOUT-DTI',
            'evaluator_version': h['evaluator_version'],
            'withheld_positive_pixels': h['withheld_positive_pixels'],
            'e3_candidate': h['e3_candidate'],
            'e2_dual_regime': h['e2_dual_regime'],
            'e1_blind_loqo': h['e1_blind_loqo'],
            'r0_recipe_control': h['r0_recipe_control'],
            'paired_e3_vs_r0_recipe': h['paired_e3_vs_r0_recipe'],
        },
        'uniqueness': {
            'registry_owners': len(u['registry_owners']),
            'registry_non_empty_repos': u['registry_non_empty_repos'],
            'registry_unique_rasters': u['registry_unique_rasters'],
            'dot_field_rasters': u['dot_field_rasters'],
            'surface_rasters': u['surface_rasters'],
            'pi1_pre_placement_surface_pass': pi1['pre_placement_surface_pass'],
            'pi1_surface_worst_overlap': pi1['surface_worst_overlap'],
            'pi1_surface_worst_abs_rho': pi1['surface_worst_abs_rho'],
            'pi1_final_dots_pass': pi1['final_dots_pass'],
            'pi1_final_worst_overlap': pi1['final_worst_overlap'],
            'pi1_final_worst_abs_rho': pi1['final_worst_abs_rho'],
            'literal_duplicate_under_dense_witness': lit['duplicate_under_literal'],
            'literal_worst_overlap': lit['worst_literal_overlap'],
        },
        'blocking_reasons': [
            'literal full-support continuous witness (17GEMSDOE E-proba-multiscale = 1.000 > 0.70) and binary lattice (13GEMSDOE r13-lattice-s5) remain unresolved without owner policy disposition',
            'official organizer origin and redistribution rights of restored mirror inputs remain unverified',
            'weekly competition slot promotion requires a separate human selector decision (3 per week limit)',
        ],
    }
    return card, audit, status


def load_gx_20261031_status():
    """Load and cryptographically bind the 2026-10-31 GX external-layer research artifact.

    Fail-closed: any missing file, hash mismatch, failing format gate, or a
    non-negative verdict raises. The artifact is research-only by construction.
    """
    card_path = DL / 'gx1_run_card_20261031.json'
    if not card_path.is_file():
        return None
    card = json.loads(card_path.read_text(encoding='utf-8'))
    tif_name = Path(card['raster']['file']).name
    zip_name = Path(card['raster']['zip']).name
    tif_path = DL / tif_name
    zip_path = DL / zip_name
    audit_path = DL / (tif_name[:-4] + '-audit.json')
    for path in (tif_path, zip_path, audit_path):
        if not path.is_file():
            raise ValueError(f'GX 2026-10-31 artifact is missing: {path.name}')
    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    if digest != card['raster']['sha256']:
        raise ValueError('GX 2026-10-31 raster SHA-256 does not match its run card')
    with zipfile.ZipFile(zip_path) as archive:
        members = [n for n in archive.namelist() if not n.endswith('/')]
        if len(members) != 1 or Path(members[0]).name != tif_name:
            raise ValueError('GX 2026-10-31 ZIP must contain exactly the bound TIFF')
        if hashlib.sha256(archive.read(members[0])).hexdigest() != digest:
            raise ValueError('GX 2026-10-31 ZIP payload does not match TIFF bytes')
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    if audit.get('sha256') != digest:
        raise ValueError('GX 2026-10-31 audit disagrees with the TIFF bytes')
    if audit.get('ok') is not True or audit.get('problems'):
        raise ValueError('GX 2026-10-31 format audit has a failing gate')
    if audit.get('nan_pixels') or audit.get('infinity_pixels'):
        raise ValueError('GX 2026-10-31 raster contains NaN or Inf')
    if not (audit.get('min') >= 0.0 and audit.get('max') <= 1.0):
        raise ValueError('GX 2026-10-31 raster values fall outside [0, 1]')
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('GX 2026-10-31 must remain fail-closed (verdict=negative, submission_eligible=false)')
    if not (0 < len(card['submission']['note']) <= 140):
        raise ValueError('GX 2026-10-31 note must be 1..140 characters')
    if not (0 < len(card['submission']['name']) <= 140):
        raise ValueError('GX 2026-10-31 name must be 1..140 characters')
    hold = card['holdout']
    uniq = card['correlation_and_overlap_vs_registry']
    can = card['leakage_canaries']
    est = card['score_estimate']
    return {
        'schema': 'gemsdoe92-gx-readiness-20261031',
        'file': tif_name,
        'zip': zip_name,
        'audit': audit_path.name,
        'run_card': card_path.name,
        'bytes': audit.get('bytes'),
        'raster_sha256': digest,
        'zip_sha256': card['raster']['zip_sha256'],
        'n_dots': card['raster']['n_dots'],
        'submission_name': card['submission']['name'],
        'note': card['submission']['note'],
        'holdout_dti': hold['candidate_dti'],
        'holdout_ci95': hold['candidate_ci95'],
        'r0_recipe_dti': hold['r0_recipe_dti'],
        'paired_delta': hold['paired_candidate_minus_r0']['delta'],
        'paired_ci95': hold['paired_candidate_minus_r0']['ci95'],
        'evaluator': hold['evaluator'],
        'withheld_positive_pixels': hold['withheld_positive_pixels'],
        'n_draws': hold['n_draws'],
        'canary_max_auc': can['max_solo_holdout_auc'],
        'canary_n': can['n_features'],
        'worst_dot_field_overlap': uniq['worst_dot_field_overlap'],
        'worst_lattice_overlap': uniq['worst_dense_lattice_overlap'],
        'n_lattice_above': uniq['dense_lattices_above_0_70'],
        'max_abs_rho': uniq['max_abs_spearman_full_footprint'],
        'registry_rasters': uniq['n_registry_sha256'],
        'model_estimate': est['ridge_estimate'],
        'model_rmse': est['leave_group_out_rmse'],
        'focus9_overlap_min': min(uniq['overlap_vs_focus_nine'].values()),
        'focus9_overlap_max': max(uniq['overlap_vs_focus_nine'].values()),
        'holdout_vs_claim_rho': card['method_finding']['spearman_per_dot_yield_vs_claim'],
    }


def load_blindcorridor_status():
    """Load and bind the additional format-only artifact without authorizing it."""
    card_path = DL / 'gemsdoe92-blindcorridor-37654dots-20261028-11f8999c_run_card.json'
    if not card_path.is_file():
        return None
    try:
        card = json.loads(card_path.read_text(encoding='utf-8'))
        tif_name = Path(card['raster']['file']).name
        zip_name = Path(card['raster']['zip']).name
        tif_path = DL / tif_name
        zip_path = DL / zip_name
        audit_path = tif_path.with_name(tif_path.stem + '-audit.json')
        audit = json.loads(audit_path.read_text(encoding='utf-8'))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ValueError(f'BLINDCORRIDOR evidence is incomplete: {exc}') from exc

    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest() if tif_path.is_file() else None
    if digest is None or digest != card.get('raster_sha256') or digest != card.get('raster', {}).get('sha256'):
        raise ValueError('BLINDCORRIDOR raster SHA-256 does not match its run card')
    if not zip_path.is_file() or not audit_path.is_file():
        raise ValueError('BLINDCORRIDOR ZIP or format audit is missing')
    try:
        with zipfile.ZipFile(zip_path) as archive:
            members = [name for name in archive.namelist() if not name.endswith('/')]
            if len(members) != 1 or Path(members[0]).name != tif_name:
                raise ValueError('BLINDCORRIDOR ZIP must contain exactly the bound TIFF')
            if hashlib.sha256(archive.read(members[0])).hexdigest() != digest:
                raise ValueError('BLINDCORRIDOR ZIP payload does not match the TIFF bytes')
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f'BLINDCORRIDOR ZIP is invalid: {exc}') from exc
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if card.get('verdict') != 'format_pass' or card.get('submission_eligible') is not False:
        raise ValueError('BLINDCORRIDOR must remain format_pass only and not submission-eligible')
    if audit.get('sha256_zeros') != digest or audit.get('verdict') != 'format_pass' or audit.get('submission_eligible') is not False:
        raise ValueError('BLINDCORRIDOR audit disagrees with its byte-bound run card')
    gates = audit.get('gates_zeros')
    if audit.get('overall_pass') is not True or not isinstance(gates, list) or not gates or any(row.get('ok') is not True for row in gates):
        raise ValueError('BLINDCORRIDOR format audit is missing or has a failing gate')

    holdout = card.get('holdout_dti', {})
    if (not isinstance(holdout, dict) or 'dti' in holdout or 'ci95' in holdout
            or 'evaluator_version' in holdout or 'withheld_positive_pixels' in holdout
            or card.get('leakage_canaries', {}).get('canaries_run') is not False):
        raise ValueError('BLINDCORRIDOR holdout/canary status changed; review and update required')
    uniqueness = card.get('uniqueness', {})
    references = uniqueness.get('references')
    if not isinstance(references, list) or not references:
        raise ValueError('BLINDCORRIDOR local reference scope is missing')
    measured_worst = max(float(ref['overlap_3px']) for ref in references)
    recorded_worst = float(uniqueness['worst_overlap_3px'])
    if not math.isclose(measured_worst, recorded_worst, rel_tol=0, abs_tol=1e-9):
        raise ValueError('BLINDCORRIDOR worst local overlap disagrees with its reference rows')

    # The original card covers only three local references. A later historical
    # registry audit exists separately; bind it to the same bytes, do not let
    # an older card hide a known failure or treat the snapshot as current.
    registry_path = ROOT / 'evidence/uniq_full_registry/blindcorridor-37654dots-11f8999c.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    if (registry.get('candidate_sha256') != digest or registry.get('pi1_pass') is not False
            or registry.get('worst_overlap', {}).get('value', 0) <= 0.70):
        raise ValueError('BLINDCORRIDOR historical registry evidence changed; review required')

    status = {
        'schema': 'gemsdoe92-candidate-readiness-v1',
        'artifact': 'BLINDCORRIDOR',
        'file': f'downloads/{tif_name}',
        'zip': f'downloads/{zip_name}',
        'audit': audit_path.name,
        'run_card': card_path.name,
        'raster_sha256': digest,
        'zip_sha256': zip_digest,
        'submission_name': card['submission_name'],
        'note': card['note'],
        'verdict': 'format_pass',
        'submission_eligible': False,
        'download_status': 'OK TO DOWNLOAD FOR RESEARCH ONLY',
        'submission_status': 'DO NOT SUBMIT',
        'format_validation': {'status': 'recorded pass', 'gate_count': len(gates)},
        'holdout_dti': {'status': 'not independently computed', 'evidence_class': 'no HOLDOUT-DTI result'},
        'leakage_canaries': {'status': 'not run', 'canaries_run': False},
        'uniqueness': {
            'status': 'partial local check only',
            'scope': 'available bridge rasters only',
            'checked_reference_count': len(references),
            'worst_overlap_3px': recorded_worst,
            'full_registry_audit': 'not performed',  # original run card only
            'historical_registry_audit': {'candidate_sha256': digest, 'registry_unique_sha256': registry['registry_unique_sha256'], 'worst_overlap_3px': registry['worst_overlap']['value'], 'worst_repositories': registry['worst_overlap']['repos'], 'pi1_pass': False, 'current': False},
            'literal_dense_witness': 'unresolved',
        },
        'blocking_reasons': [
            'independent HOLDOUT-DTI and 95% CI are absent',
            'individual-feature leakage canaries were not run',
            'historical registry audit fails the overlap stop; current registry not verified',
            'the literal dense-witness interpretation remains unresolved',
        ],
    }
    return card, audit, status


def load_marussi_20261029_status():
    """Load and byte-verify the 2026-10-29 MARUSSI-TRISHEAR negative research artifact."""
    import hashlib
    import zipfile

    card_path = DL / 'gemsdoe92-marussitrishear-34000dots-20261029-236171af_run_card.json'
    status_path = DL / 'marussi_trishear_readiness_20261029.json'
    if not card_path.is_file() or not status_path.is_file():
        return None
    card = json.loads(card_path.read_text(encoding='utf-8'))
    status = json.loads(status_path.read_text(encoding='utf-8'))
    tif_name = Path(card['raster']['file']).name
    zip_name = Path(card['raster']['zip']).name
    tif_path = DL / tif_name
    zip_path = DL / zip_name
    audit = json.loads((DL / status['audit']).read_text(encoding='utf-8'))
    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    if digest != card.get('raster_sha256') or digest != status.get('raster_sha256') or digest != audit.get('sha256_zeros'):
        raise ValueError('MARUSSI-TRISHEAR SHA-256 mismatch across TIFF, run card, status, or audit')
    with zipfile.ZipFile(zip_path) as zf:
        if zf.namelist() != [tif_name] or hashlib.sha256(zf.read(tif_name)).hexdigest() != digest:
            raise ValueError('MARUSSI-TRISHEAR single-TIFF ZIP payload mismatch')
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('MARUSSI-TRISHEAR must remain fail-closed negative')
    if status.get('verdict') != 'negative' or status.get('submission_eligible') is not False:
        raise ValueError('MARUSSI-TRISHEAR readiness must remain fail-closed negative')
    return card, audit, status


def load_admitrelay_status():
    """Load and byte-verify the 2026-10-29 ADMITRELAY + LBM-v3 negative research artifact."""
    import hashlib
    import zipfile

    feed_path = DL / 'admitrelay_readiness_20261029.json'
    if not feed_path.is_file():
        return None
    status = json.loads(feed_path.read_text(encoding='utf-8'))
    card_path = DL / status['run_card']
    audit_path = DL / status['audit']
    tif_path = DOCS / status['file']
    zip_path = DOCS / status['zip']
    card = json.loads(card_path.read_text(encoding='utf-8'))
    audit = json.loads(audit_path.read_text(encoding='utf-8'))
    digest = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    zip_digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    if digest != card.get('raster_sha256') or digest != audit.get('sha256_zeros') or digest != status.get('raster_sha256'):
        raise ValueError('ADMITRELAY raster SHA-256 mismatch across run card / audit / readiness feed')
    if zip_digest != status.get('zip_sha256'):
        raise ValueError('ADMITRELAY ZIP SHA-256 mismatch')
    with zipfile.ZipFile(zip_path) as zf:
        members = [m for m in zf.namelist() if not m.endswith('/')]
        if len(members) != 1 or Path(members[0]).name != tif_path.name:
            raise ValueError('ADMITRELAY ZIP must contain exactly its single bound TIFF')
        if hashlib.sha256(zf.read(members[0])).hexdigest() != digest:
            raise ValueError('ADMITRELAY ZIP payload SHA-256 mismatch')
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('ADMITRELAY must remain verdict=negative and submission_eligible=false')
    if status.get('verdict') != 'negative' or status.get('submission_eligible') is not False:
        raise ValueError('ADMITRELAY readiness feed must remain verdict=negative and submission_eligible=false')
    return card, audit, status


def render(card):
    if card.get('verdict') != 'negative' or card.get('submission_eligible') is not False:
        raise ValueError('blocked: review renderer cannot authorize promotion')
    esc = lambda x: html.escape(str(x), quote=True)
    sources = json.loads((ROOT / 'evidence/focus9_sources_20261028.json').read_text())
    unique = json.loads((ROOT / 'evidence/focus9_uniqueness_20261028.json').read_text())

    dexp = load_dexp_kostrov_status()
    dexp_feed_path = DL / 'dexpkostrov_readiness_20261029.json'
    dexp_section = ''
    dexp_howto_block = ''
    f9_vs_dexp = {}
    if dexp:
        dexp_card, dexp_audit, dexp_status = dexp
        f9_vs_dexp = dexp_card.get('uniqueness', {}).get('focus9_comparison', {})
        dh = dexp_card['holdout_dti']
        du = dexp_card['uniqueness']['pi1_operational_reading']
        d_e3 = dh['e3_candidate']
        d_e2 = dh['e2_dual_regime']
        d_r0 = dh['r0_recipe_control']
        d_pair = dh['paired_e3_vs_r0_recipe']
        d_tif = Path(dexp_status['file']).name
        d_zip = Path(dexp_status['zip']).name
        dexp_section = f'''<section id="dexp-kostrov-20261029" class="stop"><h2>2026-10-29 Unique Candidate: DEXP-KOSTROV-KOENDERINK (E3) — Research Download Only · DO NOT SUBMIT</h2>
<p><strong>✅ OK TO DOWNLOAD FOR RESEARCH ONLY (11/11 [0, 1] Format Gates PASS · 36/36 Leakage Canaries PASS · HOLDOUT-DTI {d_e3['dti']:.5f} &gt; R0 {d_r0['dti']:.5f} · Full 2,262-SHA PI-1 Surface &amp; Final Uniqueness PASS)</strong><br>
<strong>⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT</strong> (<code>verdict=negative</code>, <code>submission_eligible=false</code>; held fail-closed at literal dense-witness gate <code>1.000 &gt; 0.70</code> &amp; unverified official redistribution provenance; 0 weekly slots used).</p>
<p><a class="btn" href="downloads/{esc(d_tif)}" download>⬇ One-Click Download 2026-10-29 Unique GeoTIFF ({esc(d_tif)})</a> ·
<a href="downloads/{esc(d_zip)}" download>one-TIFF ZIP</a> ·
<a href="downloads/{esc(dexp_status['run_card'])}">byte-bound run card</a> ·
<a href="downloads/{esc(dexp_status['audit'])}">11-gate format audit</a> ·
<a href="downloads/{esc(dexp_feed_path.name)}">readiness feed</a> ·
<a href="executive-summary-20261029-dexp-kostrov.html"><strong>2026-10-29 Executive Summary &amp; PhD Analysis</strong></a> ·
<a href="how-to-submit.html"><strong>How to submit subpage</strong></a></p>
<p>SHA-256: <code>{esc(dexp_status['raster_sha256'])}</code> · <code>{dexp_status['n_dots']:,}</code> binary <code>{{0.0, 1.0}}</code> dots · single-band <code>float32</code> · <code>EPSG:32611</code> · <code>3730×3292</code> · 0 NaN anywhere (prevents <em>“Predicted values must be in range [0, 1]”</em>). Archive metadata only (not an upload instruction): name <code>{esc(dexp_status['submission_name'])}</code>; short note (<code>{len(dexp_status['note'])}/140</code> chars): <code>{esc(dexp_status['note'])}</code>.</p>
<table>
<tr><th><code>HOLDOUT-DTI</code> (<code>{esc(dh['evaluator_version'])}</code>, {dh['withheld_positive_pixels']:,} withheld positives)</th><td><strong>E3 diversified candidate: <code>{d_e3['dti']:.6f}</code></strong> 95% CI <code>[{d_e3['ci95'][0]:.6f}, {d_e3['ci95'][1]:.6f}]</code> · <strong>E2 unconstrained dual: <code>{d_e2['dti']:.6f}</code></strong> <code>[{d_e2['ci95'][0]:.6f}, {d_e2['ci95'][1]:.6f}]</code> · <strong>R0-recipe control: <code>{d_r0['dti']:.6f}</code></strong> <code>[{d_r0['ci95'][0]:.6f}, {d_r0['ci95'][1]:.6f}]</code> · Paired <code>E3 − R0</code>: <strong><code>{d_pair['delta']:+.6f}</code> 95% CI <code>[{d_pair['ci95'][0]:+.6f}, {d_pair['ci95'][1]:+.6f}]</code></strong> (strictly &gt; 0).</td></tr>
<tr><th>Leakage canaries &amp; <code>MODEL</code> diagnostic</th><td>36 / 36 single-feature holdout canaries PASS (max symmetric AUC <code>{dexp_card['leakage_canaries']['max_auc']:.5f} &le; 0.90</code>). Calibrated 132-claim LOGO <code>MODEL</code> diagnostic (not a score): <code>LBM-v3 = {dexp_card['model_estimate']['lbm_v3_saturated_132']:.4f}</code>; prospective OOT check on 4 newly scored 2026-10-29 claims (<code>GEMSDOE92 lbmc1 = 0.2784 CLAIM</code>, <code>GEMSDOEkarage1 = 0.1648 CLAIM</code>, <code>ApartGEMSDOE3 = 0.1625 CLAIM</code>, <code>KANLERGEMSDOE3 = 0.1233 CLAIM</code>) achieved exact <code>4/4</code> rank order (<code>Spearman = 1.000</code>, 3-repo <code>RMSE = 0.01828</code>).</td></tr>
<tr><th>Full 8-owner / 108-repo / 2,262-SHA registry uniqueness</th><td><strong>Operational PI-1 PASS</strong> across all <code>2,262</code> unique SHA-256 rasters (<code>2,139</code> dot fields + <code>123</code> continuous surfaces; fixes <code>IR-1029-3</code>): pre-placement surface worst 3-px overlap <code>{du['surface_worst_overlap']:.5f} &le; 0.70</code> (<code>|ρ| = {du['surface_worst_abs_rho']:.5f} &le; 0.90</code>); final 40,000 dots worst 3-px overlap <code>{du['final_worst_overlap']:.5f} &le; 0.70</code> (<code>|ρ| = {du['final_worst_abs_rho']:.5f} &le; 0.90</code>); overlap vs <code>GEMSDOE92 lbmc1</code> (<code>0.2784 CLAIM</code>) = <code>0.17533</code>; overlap vs all 9 focus sites = <code>0.2663–0.2867</code>. Literal dense-witness reading remains <code>1.000 &gt; 0.70</code> (<code>DO NOT SUBMIT</code>).</td></tr>
</table></section>'''
        dexp_howto_block = f'''<section class="stop" id="dexp-howto"><h2>2026-10-29 Candidate Status: DEXP-KOSTROV-KOENDERINK — Research Download Only · DO NOT SUBMIT</h2>
<p><strong>OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT.</strong> File <a href="downloads/{esc(d_tif)}" download><code>{esc(d_tif)}</code></a> (SHA-256 <code>{esc(dexp_status['raster_sha256'])}</code>, <a href="downloads/{esc(d_zip)}" download>one-TIFF ZIP</a>, <a href="downloads/{esc(dexp_status['run_card'])}">run card</a>, <a href="downloads/{esc(dexp_status['audit'])}">11-gate audit</a>) passes all 11 automated format/range gates, 36/36 leakage canaries (<code>max AUC = {dexp_card['leakage_canaries']['max_auc']:.5f} &le; 0.90</code>), fold-proper <code>HOLDOUT-DTI</code> vs R0 recipe (<code>{d_e3['dti']:.5f}</code> vs <code>{d_r0['dti']:.5f}</code>, paired 95% CI <code>[{d_pair['ci95'][0]:+.5f}, {d_pair['ci95'][1]:+.5f}]</code>), and operational PI-1 uniqueness across all <code>2,262</code> fleet rasters (surface <code>{du['surface_worst_overlap']:.5f}</code>, final <code>{du['final_worst_overlap']:.5f} &le; 0.70</code>), but remains <code>verdict=negative</code> and <code>submission_eligible=false</code> under the unresolved literal dense-witness rule (<code>17GEMSDOE = 1.000 &gt; 0.70</code>) and unverified official input redistribution provenance.</p></section>'''

    rows = []
    if dexp:
        d_tif = Path(dexp[2]['file']).name
        d_e3 = dexp[0]['holdout_dti']['e3_candidate']
        rows.append(
            f"<tr><td><strong>GEMSDOE92</strong> <small>(2026-10-29 new)</small></td>"
            f"<td><a href=\"downloads/{esc(d_tif)}\" download>{esc(d_tif)}</a> <small>(research only, 40,000d)</small></td>"
            f"<td><code>HOLDOUT-DTI</code> {d_e3['dti']:.5f} [{d_e3['ci95'][0]:.5f}, {d_e3['ci95'][1]:.5f}]; <code>MODEL</code> 0.0961; no organizer receipt</td>"
            f"<td>PI-1 PASS vs all 2,262 SHAs (surface 0.6541, final 0.6389 &le; 0.70); literal witness 1.000 &gt; 0.70 — DO NOT SUBMIT</td></tr>"
        )
    rows.append(
        "<tr><td><strong>GEMSDOE92</strong> <small>(2026-10-27 lbmc1)</small></td>"
        "<td><a href=\"downloads/gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif\" download>gemsdoe92-lbmc1-35801dots-20261027-89a660f6-zeros.tif</a> <small>(research only, 35,801d)</small></td>"
        "<td>0.2784 user-reported <code>CLAIM</code> (#1 fleet high, unverified); <code>HOLDOUT-DTI</code> 0.01970</td>"
        "<td>Already in GEMSDOE92 registry (0.1753 overlap vs dexpkostrov1); study only — DO NOT SUBMIT</td></tr>"
    )
    for site, d in sources.items():
        u = unique[site]
        if u['best'] != d['best'] or u['claim'] != d['claim']:
            raise ValueError('focus site records disagree')
        ov_vs_new = f9_vs_dexp.get(site, {}).get('final_overlap_pi1')
        ov_note = f"; {ov_vs_new:.4f} vs dexpkostrov1" if isinstance(ov_vs_new, (int, float)) else ""
        rows.append(
            f"<tr><td>{esc(site)}</td><td><a href=\"{esc(d['blob_url'])}\">{esc(d['best'])}</a> <small>(research only)</small></td>"
            f"<td>{d['claim']:.4f} user-reported <code>CLAIM</code>, unverified</td>"
            f"<td>Fails historical registry test (1.000 clone{ov_note}); not eligible — DO NOT SUBMIT</td></tr>"
        )

    file = Path(card['raster']['file']).name
    name = esc(card['submission_name']); note = esc(card['note']); digest = esc(card['raster_sha256'])

    # Show the latest TIPCOMP artifact on the landing page, but keep it explicitly
    # research-only: its own byte-bound run card is negative and non-eligible.
    tipcomp_card_path = DL / 'gemsdoe92-tipcomp-40000dots-20261028-8f27b9d6_run_card.json'
    tipcomp_section = ''
    if tipcomp_card_path.is_file():
        tipcomp = json.loads(tipcomp_card_path.read_text())
        tip_rel = tipcomp['raster']['file'].removeprefix('docs/')
        tip_file = DL / Path(tip_rel).name
        if hashlib.sha256(tip_file.read_bytes()).hexdigest() != tipcomp.get('raster_sha256'):
            raise ValueError('TIPCOMP raster SHA-256 does not match its run card')
        if tipcomp.get('verdict') != 'negative' or tipcomp.get('submission_eligible') is not False:
            raise ValueError('review renderer cannot advertise a non-negative TIPCOMP candidate')
        h = tipcomp['holdout_dti']
        e2 = h['foldproper_e2']; control = h['r0_recipe_control']; paired = h['paired_e2_vs_r0_recipe']
        model = tipcomp['model_estimate']['candidate']
        registry = tipcomp['correlation_overlap_vs_registry']
        tipcomp_section = f'''<section class="stop"><h2>Latest additional candidate: TIPCOMP — DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(Path(tip_rel).name)}" download>Download TIPCOMP GeoTIFF for research only — DO NOT SUBMIT</a> ·
<a href="downloads/{esc(tipcomp_card_path.name)}">byte-bound run card</a> ·
<a href="executive-summary-20261028-tipcomp.html">full experiment summary</a></p>
<p>SHA-256 <code>{esc(tipcomp['raster_sha256'])}</code>. Local format validation was recorded as 11/11 gates PASS; that is only file-format validation, not science or organizer acceptance. Metadata is archived for audit and is not a portal-upload recommendation.</p>
<table><tr><th>Estimated value</th><td><code>MODEL</code>, not a score: published-128 estimate {model['published128']:.4f}; 26-claim refit {model['refit26']:.4f} (bootstrap q05 {model['bootstrap_refit26']['q05']:.4f}). The pre-registered q05 bound 0.2778 was not met.</td></tr>
<tr><th>HOLDOUT-DTI</th><td><code>{esc(e2['evaluator_version'])}</code>, {e2['withheld_positive_pixels']:,} withheld positives: fold-proper TIPCOMP {e2['dti']:.5f} [{e2['ci95'][0]:.5f}, {e2['ci95'][1]:.5f}]; R0-recipe control {control['dti']:.5f} [{control['ci95'][0]:.5f}, {control['ci95'][1]:.5f}]; paired difference {paired['delta']:.5f} [{paired['ci95'][0]:.5f}, {paired['ci95'][1]:.5f}] (CI spans zero; no holdout win).</td></tr>
<tr><th>Uniqueness scope</th><td>The archived PI-1 measurement reports {registry['registry_unique_rasters']} local rasters, max dot overlap {registry['worst_overlap']['value']:.5f}, and max sampled |ρ| {registry['worst_abs_rho_surface']['value']:.5f}. This is an earlier partial scan. A later historical full-registry PI-1 audit reports 0.9180 overlap against GEMSDOE22, above 0.70; it fails. The dense-witness interpretation remains unresolved; do not claim global uniqueness.</td></tr>
<tr><th>Decision</th><td><strong>DO NOT SUBMIT.</strong> Run card verdict is negative and <code>submission_eligible=false</code>. No slot was selected. No organizer-confirmed score is recorded.</td></tr></table></section>'''

    blindcorridor = load_blindcorridor_status()
    blindcorridor_section = ''
    blindcorridor_feed_path = DL / 'blindcorridor_readiness_20261028.json'
    if blindcorridor:
        blind_card, blind_audit, blind_status = blindcorridor
        blind_file = Path(blind_status['file']).name
        blind_zip = Path(blind_status['zip']).name
        blind_refs = blind_card['uniqueness']['references']
        blind_worst = blind_status['uniqueness']['worst_overlap_3px']
        blind_model = blind_card.get('model_estimate', {}).get('projection', 'not recorded')
        blindcorridor_section = f'''<section id="blindcorridor" class="stop"><h2>Latest additional artifact: BLINDCORRIDOR — FORMAT PASS ONLY; DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(blind_file)}" download>Download GeoTIFF for research only — DO NOT SUBMIT</a> ·
<a href="downloads/{esc(blind_zip)}" download>one-TIFF ZIP (research only)</a> ·
<a href="downloads/{esc(blind_status['run_card'])}">byte-bound run card</a> ·
<a href="downloads/{esc(blind_status['audit'])}">format audit</a> ·
<a href="downloads/{esc(blindcorridor_feed_path.name)}">readiness feed</a></p>
<p>SHA-256 <code>{esc(blind_status['raster_sha256'])}</code>. The stored file-format audit records {blind_status['format_validation']['gate_count']}/{blind_status['format_validation']['gate_count']} gates PASS; this is not scientific validation or upload approval.</p>
<table><tr><th>Run-card projection</th><td><code>MODEL</code>, not a score: {esc(blind_model)}. The run card has no independent <code>HOLDOUT-DTI</code> or 95% CI, so this projection is not validated and is not a submission basis.</td></tr>
<tr><th>HOLDOUT-DTI</th><td>Not independently computed; withheld-positive count and 95% CI are absent.</td></tr>
<tr><th>Leakage canaries</th><td>Not run on the full feature stack.</td></tr>
<tr><th>Local overlap scope</th><td>Recorded worst 3-px overlap {blind_worst:.6f} across {len(blind_refs)} available bridge references only. The original run card did not include a full registry audit. A separate <a href="https://github.com/buffedlizard55-lab/GEMSDOE92/blob/913af0ad6e163c86b46ccd4260207862fb805e79/evidence/uniq_full_registry/blindcorridor-37654dots-11f8999c.json">historical registry audit</a> reports worst 3-px overlap {blind_status['uniqueness']['historical_registry_audit']['worst_overlap_3px']:.6f} versus 13GEMSDOE, above the 0.70 stop. The registry snapshot is not current; the literal dense-witness interpretation remains unresolved. This is not globally unique or cleared.</td></tr>
<tr><th>Decision</th><td><strong>DO NOT SUBMIT.</strong> Run card says <code>verdict=format_pass</code> and <code>submission_eligible=false</code>. Do not use the stored submission name or note as upload instructions.</td></tr></table></section>'''

    secondary_meta_path = DL / 'gemsdoe92-damagezone-close-dots-20261028-zeros.json'
    secondary = json.loads(secondary_meta_path.read_text()) if secondary_meta_path.is_file() else None
    secondary_section = ''
    if secondary:
        secondary_file = esc(secondary['file'])
        secondary_digest = esc(secondary['sha256'])
        secondary_section = f'''<section><h2>Separate candidate in repository — not cleared</h2>
<p><a href="downloads/{secondary_file}"><code>{secondary_file}</code></a> (SHA-256 <code>{secondary_digest}</code>) was added by a later merged change. It is not this review's selected artifact and was not run through an assigned-lane pre-registration or a full registry uniqueness gate. The local site checker validates format/range/grid only; that cannot authorize a competition slot.</p>
<p>The accompanying experiment note reports a local surrogate HOLDOUT-DTI of 0.05164 against an R0 raster at 0.00473, but below the recorded R0 recipe value of 0.09775; the label raster is byte-identical to the visible-fault catalogue according to the independent review. This is not evidence of generalization to missing faults. Keep this file research-only; do not submit. See <a href="HYPOTHESES_UNTRYED.md">the candidate note</a> and <a href="REVIEW_20261028_SESSION.md">independent limitations review</a>.</p></section>'''
    legacy_knickloqo = '''<!-- KNICKLOQO:BEGIN -->
<section class="stop" id="historical-knickloqo"><h2>Historical KNICKLOQO record — DO NOT SUBMIT</h2>
<p>This superseded diagnostic recorded literal registry overlap <strong>1.000 &gt; 0.70</strong>; a sparse matched-budget reading was diagnostic only and did not clear any weekly slot. It is retained for audit, not as a candidate recommendation.</p>
</section>
<!-- KNICKLOQO:END -->'''
    admitrelay = load_admitrelay_status()
    admitrelay_section = ''
    admitrelay_feed_path = DL / 'admitrelay_readiness_20261029.json'
    if admitrelay:
        ar_card, _, ar_status = admitrelay
        ar_file = Path(ar_status['file']).name
        ar_zip = Path(ar_status['zip']).name
        ar_h = ar_card['holdout_dti']
        ar_m = ar_card['model_estimate']
        ar_u = ar_card['uniqueness']
        admitrelay_section = f'''<section id="admitrelay-20261029" class="stop"><h2>Latest 2026-10-29 experiment: ADMITRELAY + LBM-v3 — OK TO DOWNLOAD FOR RESEARCH ONLY; DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(ar_file)}" download>Download ADMITRELAY GeoTIFF for research only — DO NOT SUBMIT</a> ·
<a href="downloads/{esc(ar_zip)}" download>one-TIFF ZIP (research only)</a> ·
<a href="downloads/{esc(ar_status['run_card'])}">byte-bound run card</a> ·
<a href="downloads/{esc(ar_status['audit'])}">11-gate format audit</a> ·
<a href="downloads/{esc(admitrelay_feed_path.name)}">readiness feed</a> ·
<a href="executive-summary-20261029-admitrelay.html"><strong>2026-10-29 PhD Executive Summary &amp; LBM-v3 Audit</strong></a></p>
<p>SHA-256 <code>{esc(ar_status['raster_sha256'])}</code> ({ar_card['raster']['n_dots']:,} binary dots in <code>[0, 1]</code>, zero NaN anywhere; 11/11 format gates PASS; 20/20 leakage canaries PASS with max symmetric AUC <code>{ar_card['leakage_canary_max_symmetric_auc']:.4f} &le; 0.90</code>).</p>
<table><tr><th>2026-10-29 ledger &amp; <code>MODEL</code></th><td><code>GEMSDOE92 lbmc1</code> is newly reported at <code>0.2784 CLAIM</code> (#1 across 123 repos, +0.0006 over <code>GEMSDOE32 0.2778</code>). Centerline-monotone <code>LBM-v3</code> cuts 4-claim prospective 2026-10-29 OOT RMSE by 57.4% (<code>0.03159 &rarr; 0.01344</code>; <code>lbmc1</code> OOT <code>0.2818</code> vs <code>0.2784</code>). For <code>ADMITRELAY</code>, <code>LBM-v3</code> estimates <code>{ar_m['lbm_v3_monotone']:.4f} MODEL</code> (not an organizer score).</td></tr>
<tr><th><code>HOLDOUT-DTI</code></th><td><code>gems57-pooled-hide-v2</code>, 22,663 withheld positives: zero-catalogue 12-feature <code>E1 = {ar_h['e1_admitrelay_blind']['dti']:.6f}</code>; fold-proper <code>E2 = {ar_h['e2_admitrelay_ps_loqo']['dti']:.6f}</code> (above <code>R0_recipe = {ar_h['r0_recipe_control']['dti']:.6f}</code> by <code>{ar_h['paired_e2_vs_r0_recipe']['delta']:+.6f}</code>, paired 95% CI <code>[{ar_h['paired_e2_vs_r0_recipe']['ci95'][0]:+.6f}, {ar_h['paired_e2_vs_r0_recipe']['ci95'][1]:+.6f}]</code>); deployed unique <code>E3 = {ar_h['e3_admitrelay_lbmv3_unique']['dti']:.6f}</code> (2.05&times; RIESZ E3 &amp; 3.95&times; LBMC1, but below <code>R0_recipe</code>).</td></tr>
<tr><th>Uniqueness scope</th><td>Full 8-owner scan across <code>{ar_u['registry_rasters']:,}</code> unique SHA-256 rasters: PI-1 passes on <strong>both</strong> pre-placement surface (worst 3-px overlap <code>{ar_u['surface_worst_overlap']:.6f} &le; 0.70</code>, <code>|&rho;| = {ar_u['surface_worst_abs_rho']:.4f} &le; 0.90</code>) and final dots (<code>{ar_u['final_worst_overlap']:.6f} &le; 0.70</code>, <code>|&rho;| = {ar_u['final_worst_abs_rho']:.4f} &le; 0.90</code>). Literal full-support witness <code>17GEMSDOE E-proba-multiscale</code> remains <code>1.000 &gt; 0.70</code>.</td></tr>
<tr><th>Decision</th><td><strong>DO NOT SUBMIT.</strong> <code>verdict=negative</code>, <code>submission_eligible=false</code>, 0 weekly slots spent. Archived name/note are audit metadata only, not upload instructions.</td></tr></table></section>'''

    marussi = load_marussi_20261029_status()
    marussi_section = ''
    marussi_top_line = ''
    marussi_root_line = ''
    if marussi:
        m_card, m_audit, m_status = marussi
        m_tif = Path(m_status['file']).name
        m_zip = Path(m_status['zip']).name
        m_sha = esc(m_status['raster_sha256'])
        m_e3 = m_card['holdout_dti']['e3_deployed_recipe']
        m_e2 = m_card['holdout_dti']['e2_marussi_trishear_relay']
        m_r0 = m_card['holdout_dti']['r0_recipe_control']
        m_p3 = m_card['holdout_dti']['paired_e3_vs_r0_recipe']
        m_u = m_card['uniqueness']
        m_lbm = m_card['model_estimate']['lbm_v3_estimate']
        marussi_top_line = (
            f'<p><strong>Latest 2026-10-29 candidate (MARUSSI-TRISHEAR, 34,000 dots — OK TO DOWNLOAD FOR RESEARCH ONLY / DO NOT SUBMIT):</strong> '
            f'<a href="downloads/{esc(m_tif)}" download><strong>⬇ Download {esc(m_tif)} (1-click GeoTIFF, research only)</strong></a> · '
            f'<a href="downloads/{esc(m_zip)}" download>ZIP</a> · '
            f'<a href="executive-summary-20261029-marussi-trishear.html">2026-10-29 MARUSSI-TRISHEAR Executive Summary &amp; 0.2784 Fleet Analysis</a> · '
            f'<a href="downloads/{esc(m_status["run_card"])}">Run Card JSON</a></p>'
        )
        marussi_root_line = (
            f'<p><strong>2026-10-29 MARUSSI-TRISHEAR research GeoTIFF (DO NOT SUBMIT):</strong> '
            f'<a href="docs/downloads/{esc(m_tif)}" download><code>{esc(m_tif)}</code></a> (SHA-256 <code>{m_sha}</code>) · '
            f'<a href="docs/executive-summary-20261029-marussi-trishear.html">2026-10-29 MARUSSI-TRISHEAR Executive Summary</a></p>'
        )
        marussi_section = f'''<section id="marussi-20261029" class="stop"><h2>Latest 2026-10-29 candidate: MARUSSI-TRISHEAR — OK TO DOWNLOAD FOR RESEARCH ONLY; DO NOT SUBMIT</h2>
<p><a href="downloads/{esc(m_tif)}" download><strong>⬇ Download MARUSSI-TRISHEAR GeoTIFF (34,000 dots) for research only — DO NOT SUBMIT</strong></a> ·
<a href="downloads/{esc(m_zip)}" download>one-TIFF ZIP (research only)</a> ·
<a href="downloads/{esc(m_status['run_card'])}">byte-bound run card</a> ·
<a href="downloads/{esc(m_status['audit'])}">11-gate format audit</a> ·
<a href="downloads/marussi_trishear_readiness_20261029.json">readiness feed</a> ·
<a href="executive-summary-20261029-marussi-trishear.html"><strong>2026-10-29 MARUSSI-TRISHEAR Executive Summary &amp; 0.2784 Fleet Report</strong></a></p>
<p>SHA-256 <code>{m_sha}</code> ({m_card['raster']['n_dots']:,} binary dots in <code>[0, 1]</code>, zero NaN anywhere; 11/11 format gates PASS; 24/24 solo leakage canaries PASS with max symmetric AUC <code>{m_card['leakage_canaries']['max_symmetric_auc_all_24_channels']:.4f} &le; 0.90</code>).</p>
<table><tr><th><code>HOLDOUT-DTI</code></th><td><code>{esc(m_card['holdout_dti']['evaluator_version'])}</code>, {m_card['holdout_dti']['withheld_positive_pixels']:,} withheld positives: deployed unique <code>E3 = {m_e3['dti']:.6f}</code> <code>[{m_e3['ci95'][0]:.6f}, {m_e3['ci95'][1]:.6f}]</code> (beats <code>R0_recipe = {m_r0['dti']:.6f}</code> by <code>{m_p3['delta']:+.6f}</code>, paired 95% CI <code>[{m_p3['ci95'][0]:+.6f}, {m_p3['ci95'][1]:+.6f}]</code>); full 24-ch <code>E2 = {m_e2['dti']:.6f}</code> <code>[{m_e2['ci95'][0]:.6f}, {m_e2['ci95'][1]:.6f}]</code>. Held back because neither exceeded the repo all-time <code>HOLDOUT-DTI</code> best (<code>relay_conduit = 0.184485</code>).</td></tr>
<tr><th>Uniqueness scope</th><td>Full 8-owner scan across <code>{m_u['registry_rasters']:,}</code> unique SHA-256 rasters ({m_u['registry_repos']} repos): PI-1 passes on <strong>both</strong> pre-placement surface (<code>{m_u['surface_worst_overlap']:.4f} &le; 0.70</code>, <code>|&rho;| = {m_u['surface_worst_abs_rho']:.4f} &le; 0.90</code>) and final binary dots (<code>{m_u['final_worst_overlap']:.4f} &le; 0.70</code>, <code>|&rho;| = {m_u['final_worst_abs_rho']:.4f} &le; 0.90</code>). Literal full-support witness <code>17GEMSDOE E-proba-multiscale</code> remains <code>1.000 &gt; 0.70</code>.</td></tr>
<tr><th><code>MODEL</code> &amp; Decision</th><td><code>MODEL</code> (not a score): <code>{m_lbm:.5f}</code>. <strong>DO NOT SUBMIT.</strong> <code>verdict=negative</code>, <code>submission_eligible=false</code>, 0 weekly slots spent.</td></tr></table></section>'''

    gx = load_gx_20261031_status()
    gx_section = ''
    if gx:
        gx_section = f'''<section id="gx-20261031" class="stop"><h2>2026-10-31 Unique Candidate: GX external-layer fault-appearance model — OK TO DOWNLOAD FOR RESEARCH ONLY · DO NOT SUBMIT</h2>
<p><strong>✅ OK TO DOWNLOAD FOR RESEARCH ONLY</strong> ({gx['n_dots']:,} binary dots · {gx['canary_n']}/{gx['canary_n']} leakage canaries PASS (max solo AUC <code>{gx['canary_max_auc']:.4f} &le; 0.90</code>) · <code>HOLDOUT-DTI {gx['holdout_dti']:.5f}</code> vs R0 recipe <code>{gx['r0_recipe_dti']:.5f}</code>, paired <code>{gx['paired_delta']:+.5f}</code> 95% CI <code>[{gx['paired_ci95'][0]:+.5f}, {gx['paired_ci95'][1]:+.5f}]</code> · worst dot-field registry overlap <code>{gx['worst_dot_field_overlap']:.4f} &le; 0.70</code> over {gx['registry_rasters']:,} rasters)<br>
<strong>⛔ DO NOT SUBMIT — NOT CLEARED FOR A WEEKLY SLOT</strong> (<code>verdict=negative</code>, <code>submission_eligible=false</code>, 0 weekly slots spent; <code>MODEL</code> estimate <code>{gx['model_estimate']:.4f}</code> &plusmn; <code>{gx['model_rmse']:.3f}</code> is below the best focus-site claim <code>0.2778</code>, the holdout does not beat the repo all-time best <code>0.184485</code>, and the literal dense-lattice reading measures <code>{gx['worst_lattice_overlap']:.3f} &gt; 0.70</code>).</p>
<p><a class="btn" href="downloads/{esc(gx['file'])}" download>⬇ One-Click Download 2026-10-31 Unique GeoTIFF ({esc(gx['file'])})</a> ·
<a class="btn" href="downloads/{esc(gx['zip'])}" download>one-TIFF ZIP</a> ·
<a href="downloads/{esc(gx['audit'])}">format audit</a> ·
<a href="downloads/{esc(gx['run_card'])}">byte-bound run card</a> ·
<a href="executive-summary-20261031-gx.html"><strong>2026-10-31 Nine-Site Executive Summary &amp; PhD Analysis</strong></a> ·
<a href="how-to-submit.html"><strong>How to submit subpage</strong></a></p>
<p>SHA-256: <code>{esc(gx['raster_sha256'])}</code> · <code>{gx['n_dots']:,}</code> binary <code>{{0.0, 1.0}}</code> dots · single-band <code>float32</code> · <code>EPSG:32611</code> · <code>3730&times;3292</code> · 0 NaN / 0 Inf anywhere (prevents <em>&ldquo;Predicted values must be in range [0, 1]&rdquo;</em>). Archive metadata only (not an upload instruction): name <code>{esc(gx['submission_name'])}</code>; short note (<code>{len(gx['note'])}/140</code> chars): <code>{esc(gx['note'])}</code>.</p>
<table>
<tr><th>What makes it new</th><td>Built only from externally sourced public layers — 1 m-lidar scarp operators, GeoDAWN radiometrics &amp; TMI, USGS SGMC faults and GDR thermal indicators — by a logistic appearance model refit on every holdout draw. No previous submission raster is read for dot placement.</td></tr>
<tr><th><code>HOLDOUT-DTI</code></th><td><code>{esc(gx['evaluator'])}</code>, {gx['withheld_positive_pixels']:,} withheld positives, {gx['n_draws']} draws. Overlap vs each of the nine focus files is <code>{gx['focus9_overlap_min']:.3f}&ndash;{gx['focus9_overlap_max']:.3f}</code>; worst <code>|&rho;|</code> over the registry is <code>{gx['max_abs_rho']:.3f} &le; 0.90</code>.</td></tr>
<tr><th>Method warning (negative result)</th><td>Inside the H19-5 lineage the hide-and-recover holdout is <em>anti</em>-correlated with the reported leaderboard score (Spearman <code>{gx['holdout_vs_claim_rho']:+.3f}</code>), because the instrument's truth is drawn <em>from</em> the catalogue while scoring rewards catalogue-distant dots. A holdout win is necessary but not sufficient, and a holdout number is <strong>not</strong> a score forecast.</td></tr>
<tr><th>Blocking reasons</th><td><code>MODEL</code> estimate below the best focus-site claim; holdout below the repository all-time best; unresolved literal dense-lattice rule ({gx['n_lattice_above']} registry rasters exceed 150,000 positive pixels, so the 0.70 gate is unsatisfiable for any non-empty candidate — owner decision D1).</td></tr>
</table></section>'''

    gx_howto_block = ''
    if gx:
        gx_howto_block = f'''<section class="stop" id="gx-howto"><h2>2026-10-31 Candidate Status: GX external-layer model — Research Download Only · DO NOT SUBMIT</h2>
<p><code>{esc(gx['file'])}</code> (SHA-256 <code>{esc(gx['raster_sha256'])}</code>) is <strong>format-clean but not cleared</strong>: 0 NaN / 0 Inf, values in <code>[0, 1]</code>, single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3730&times;3292</code>, zeros outside the footprint — so it cannot trigger <em>&ldquo;Predicted values must be in range [0, 1]&rdquo;</em>. It is nevertheless held at <code>verdict=negative</code>, <code>submission_eligible=false</code>: its <code>MODEL</code> estimate <code>{gx['model_estimate']:.4f}</code> &plusmn; <code>{gx['model_rmse']:.3f}</code> is below the best focus-site claim <code>0.2778</code>, its fold-proper <code>HOLDOUT-DTI {gx['holdout_dti']:.5f}</code> does not beat the repository all-time best <code>0.184485</code>, and the unresolved literal dense-lattice rule measures <code>{gx['worst_lattice_overlap']:.3f} &gt; 0.70</code>. If a future selector clears it, the exact archive metadata to paste into the portal is name <code>{esc(gx['submission_name'])}</code> and note (<code>{len(gx['note'])}/140</code> chars) <code>{esc(gx['note'])}</code>.</p></section>'''

    lsv29 = load_lidarsintervalve_20261029()
    lsv_hero = render_lidarsintervalve_hero(lsv29[0], lsv29[2]) if lsv29 else ''
    lsv_root_hero = render_lidarsintervalve_hero(lsv29[0], lsv29[2], href_prefix='docs/') if lsv29 else ''
    body = f'''<p class="small"><a href="executive-summary-nine-sites-20261030.html"><strong>2026-10-30 Focus-9 Executive Summary — DO NOT SUBMIT</strong></a> · <a href="REVIEW_20261030_FOCUS9.md">2026-10-30 Three-Pass Repository Review</a> · <a href="REVIEW_20261030_ARENA.md">Arena evidence-gate review</a> · <a href="executive-summary-20261029-dexp-kostrov.html"><strong>2026-10-29 DEXP-KOSTROV Summary</strong></a> · <a href="HYPOTHESES_20261029_DEXP_KOSTROV.md">DEXP-KOSTROV Hypotheses</a> · <a href="executive-summary-20261029-lidarsintervalve.html"><strong>2026-10-29 LIDAR-SINTERVALVE Nine-Site Summary</strong></a> · <a href="HYPOTHESES_20261029_LIDAR_SINTERVALVE.md">LIDAR-SINTERVALVE Hypotheses</a> · <a href="WHY_0_2778_AND_0_2784_20261029.md">Why 0.2778 vs 0.2784</a> · <a href="executive-summary-20261029-marussi-trishear.html"><strong>2026-10-29 MARUSSI-TRISHEAR Summary</strong></a> · <a href="HYPOTHESES_20261029_MARUSSI_TRISHEAR.md">MARUSSI Hypotheses</a> · <a href="executive-summary-20261029-admitrelay.html"><strong>2026-10-29 ADMITRELAY + LBM-v3 Summary</strong></a> · <a href="HYPOTHESES_20261029_ADMITRELAY.md">ADMITRELAY Hypotheses</a> · <a href="executive-summary-20261031-gx.html"><strong>2026-10-31 GX Summary</strong></a> · <a href="STANDING_PROMPT_20261031.md">2026-10-31 Standing Prompt</a> · <a href="STANDING_PROMPT.md">Standing Prompt</a> · <a href="executive-summary-nine-sites-20261028.html">Nine-site executive summary</a></p><nav><a href="how-to-submit.html">How to submit</a> · <a href="nine-sites.html">Nine-site review</a> · <a href="REVIEW_20261029_DEXP_KOSTROV.md">2026-10-29 three-pass audit</a> · <a href="REVIEW_20261028_MAIN_INTEGRATION.md">2026-10-28 main-integration review</a> · <a href="REVIEW_20261028_SESSION.md">Independent overlap review</a></nav>
{gx_section}
{dexp_section}
{lsv_hero}
<section id="submit-now" class="stop"><h1>DO NOT SUBMIT — no eligible new TIFF (weekly limit: 3 per week)</h1>
<p>No competition slot was used. The prior Riesz candidate fails the literal registry rule and did not beat the holdout control, and all four 2026-10-29 research candidates (DEXP-KOSTROV-KOENDERINK, LIDAR-SINTERVALVE, MARUSSI-TRISHEAR, and ADMITRELAY) remain fail-closed negative. A range-valid raster is not automatically submission-ready.</p>
{marussi_top_line}
<p><a data-primary="true" href="downloads/{esc(file)}" download>Download existing Riesz TIFF for research only</a> · <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Historical run card, reclassified negative</a></p>
<p>SHA-256: <code>{digest}</code>. Historical name: <code>{name}</code>. Historical note (not an instruction to upload): <code>{note}</code></p></section>
{marussi_section}
{admitrelay_section}
{tipcomp_section}
{blindcorridor_section}
{legacy_knickloqo}
<section id="summary"><h2>Executive summary across Focus-9 &amp; GEMSDOE92</h2><p>No <code>ORGANIZER-CONFIRMED</code> competition receipt is stored in this repository. Owner-reported <code>CLAIM</code> figures, spatially-blocked <code>HOLDOUT-DTI</code> results, and <code>MODEL</code> diagnostics are strictly separated below.</p>
<table><thead><tr><th>Site</th><th>File to download — research only</th><th>Score / estimate (strictly labeled)</th><th>Uniqueness across listed GEMSDOE sites &amp; status</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<p>The 2026-10-29 full 8-owner registry cache (<code>108</code> non-empty repos, <code>3,421</code> grid files, <code>2,262</code> unique SHA-256 rasters = <code>2,139</code> dot fields + <code>123</code> surfaces) verifies operational PI-1 uniqueness for <code>dexpkostrov1</code> while confirming all 9 historical focus-site peaks have exact clones elsewhere. The <a href="downloads/focus9_pairwise_recheck_14f85876.json">row-safe pairwise recheck</a> warns that earlier pairwise results contained errors. A separate pinned full-footprint witness causes a literal stop for any nonempty candidate, not a claim that every pair is byte-identical. A later measurement reports 0.00698 overlap under a top-K reading of this witness, versus 1.0 literally; the representation rule remains unresolved, so this alternate measurement is not clearance or a waiver. See the <a href="REVIEW_20261028_SESSION.md">independent review and receipt</a>.</p></section>
<section><h2>Why GEMSDOE32 (0.2778 CLAIM) &amp; GEMSDOE92 lbmc1 (0.2784 CLAIM)?</h2><p>Under the pooled Distance-Buffered Tversky Index (<code>α=0.2, β=0.8</code>, <code>300 m</code> triangular kernel, pixel-exact masking of public catalogue traces), <code>TPw</code> is submodular via <code>max</code> within 3 px while <code>FPw</code> is linear in emitted mass. <code>GEMSDOE32</code> <code>R0</code> (<code>37,654</code> binary dots, <code>0.2778 CLAIM</code>) Poisson-disk thinned <code>H19-5</code> at <code>2.8 px</code> and pruned <code>6,435</code> twin dots within <code>d_cat &le; 2 px</code> (<code>41.6%</code> in <code>2 &lt; d_cat &le; 15 px</code>, <code>58.4%</code> in <code>d_cat &gt; 15 px</code>). Meanwhile <code>GEMSDOE92</code> <code>lbmc1</code> (<code>35,801</code> dots, newly reported <code>0.2784 CLAIM</code>) placed <code>98.45%</code> of its dots in distal blind corridors (<code>d_cat &gt; 15 px</code>), establishing that unmapped faults span both proximal splays/stepovers and distal blind basin structures. Full PhD derivations and how to surpass <code>0.2784</code> toward external benchmarks (<code>0.3195</code> / <code>0.4413</code> <code>CLAIM</code>) are in <a href="WHY_0_2778_AND_0_2784_20261029.md"><code>docs/WHY_0_2778_AND_0_2784_20261029.md</code></a> and <a href="WHY_0_2778.md"><code>docs/WHY_0_2778.md</code></a>.</p>
<p>Measured <code>HOLDOUT-DTI</code> on <code>gems57-pooled-hide-v2</code> (<code>22,663</code> withheld positive pixels): 2026-10-29 <code>DEXP-KOSTROV E3</code> <code>0.11744</code> (95% CI <code>0.10423–0.13027</code>; unconstrained <code>E2</code> <code>0.14181</code>) vs R0 recipe <code>0.09775</code> (95% CI <code>0.08573–0.10954</code>); historical Riesz candidate <code>0.03799</code> (95% CI <code>0.03101–0.04466</code>). These are local holdout measurements, not leaderboard receipts. <a href="downloads/gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17_run_card.json">2026-10-29 Run Card</a> · <a href="downloads/gemsdoe92-rieszlbm2-50000dots-20261028-79041788_run_card.json">Historical Riesz Evidence</a>.</p></section>
<section><h2>Next steps &amp; limitations</h2><p>Resolve the literal dense-witness policy (<code>17GEMSDOE</code> continuous surface &amp; <code>13GEMSDOE</code> 206,895-dot lattice) and authenticate official organizer redistribution provenance before promoting any candidate to one of the 3 per week competition slots. On an open-network workstation, integrate free public-domain USGS 3DEP 1 m LiDAR scarp wavelets (<code>H4</code>) and Gallardo–Meju gravity×MT cross-gradients (<code>H2</code>) with <code>DEXP-KOSTROV</code>. This sandbox cannot reach <code>drivendata.org</code>, USGS, Dropbox, or DOE GDR directly; portal rules, weekly limit, and live leaderboard cannot be fetched here.</p>
<p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a> · <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN</a> · <a href="https://gdr.openei.org/submissions/1391">INGENIOUS</a> · <a href="https://data.usgs.gov/datacatalog/data/USGS:77ae0551-c61e-4979-aedd-d797abdcde0e">USGS 3DEP 1 m LiDAR</a> · <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Rules PDF</a> · <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a>. The organizer leaderboard is not mirrored.</p></section>{secondary_section}'''

    guide = f'''<nav><a href="index.html">← Executive summary</a> · <a href="executive-summary-20261029-dexp-kostrov.html">2026-10-29 DEXP-Kostrov summary</a> · <a href="nine-sites.html">Nine-site review</a></nav>
<section class="stop"><h1>DO NOT SUBMIT — no candidate is cleared for a weekly competition slot</h1>
<p><strong>Current gate indicator:</strong> All files served in this repository are <strong>research downloads only (<code>DO NOT SUBMIT</code>)</strong>. Do not spend one of the 3 per week DrivenData submission slots until a human selector resolves the literal dense-witness rule and verifies official input provenance.</p>
<ul>
  <li><strong>2026-10-29 <code>DEXP-KOSTROV-KOENDERINK</code> (<code>gemsdoe92-dexpkostrov1-40000dots-20261029-ffa21c17-zeros.tif</code>):</strong> passes 11/11 format gates, 36/36 leakage canaries, fold-proper <code>HOLDOUT-DTI</code> vs R0 recipe (<code>0.11744 &gt; 0.09775</code>), and operational PI-1 uniqueness across all <code>2,262</code> fleet rasters, but is held at <code>verdict=negative</code>, <code>submission_eligible=false</code> under the literal dense-witness rule (<code>17GEMSDOE = 1.000 &gt; 0.70</code>).</li>
  <li><strong><code>BLINDCORRIDOR</code> (<code>gemsdoe92-blindcorridor-37654dots-20261028-11f8999c-zeros.tif</code>):</strong> format pass only (<code>verdict=format_pass</code>, <code>submission_eligible=false</code>); lacks independent <code>HOLDOUT-DTI</code> and leakage canaries; a separate historical registry audit reports <code>0.769108</code> overlap versus <code>13GEMSDOE</code>, above the <code>0.70</code> stop (<a href="downloads/blindcorridor_readiness_20261028.json">readiness feed</a>).</li>
  <li><strong>2026-10-31 <code>GX</code> (<code>gemsdoe92-gx1-50000dots-20261031-zeros.tif</code>):</strong> built from externally sourced public layers only (1 m-lidar scarp operators, GeoDAWN radiometrics/TMI, USGS SGMC, GDR thermal indicators); 47/47 leakage canaries pass, fold-proper <code>HOLDOUT-DTI 0.14808 &gt; 0.09775</code> R0 recipe, worst dot-field registry overlap <code>0.6948 &le; 0.70</code> — but <code>MODEL</code> estimate <code>0.1782</code> is below the best focus-site claim, so it remains <code>verdict=negative</code>, <code>submission_eligible=false</code>. See the <a href="executive-summary-20261031-gx.html">2026-10-31 GX executive summary</a> and its <a href="downloads/gx1_run_card_20261031.json">byte-bound run card</a>.</li>
  <li><strong>Status-feed baseline <code>RIESZ-LOCKED</code> (<code>{esc(file)}</code>, SHA-256 <code>{digest}</code>):</strong> <code>verdict=negative</code>, <code>submission_eligible=false</code>; below R0 on <code>HOLDOUT-DTI</code>.</li>
</ul></section>
{gx_howto_block}
{dexp_howto_block}
<section><h2>Exact DrivenData #306 Submission Procedure (Conditional — Only After Future Human Selector Clearance)</h2>
<ol>
  <li><strong>Verify automated local gates (zero human pixel inspection):</strong> run <code>.venv/bin/python validate_submission.py docs/downloads/&lt;candidate&gt;-zeros.tif</code> and confirm <code>11/11</code> format gates pass: single-band <code>float32</code>, <code>EPSG:32611</code>, shape <code>3730×3292</code>, affine transform <code>(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)</code>, <code>nodata=None</code>, all <code>12,279,160</code> cells finite in <code>[0.0, 1.0]</code>, <code>0.0</code> outside the <code>5,167,373</code>-cell footprint, and <code>0</code> dots within <code>&le; 3 px</code> of mapped catalogue faults.</li>
  <li><strong>Why <em>“Predicted values must be in range [0, 1]”</em> happened previously — and how our automated pipeline prevents it:</strong> DrivenData's portal validator inspects raw raster values across the full <code>3730×3292</code> array. Files storing GDAL float32 sentinels (<code>-3.4028235e+38</code>), unclipped continuous scores (<code>&lt; 0</code> or <code>&gt; 1</code>), or unhandled exterior values trigger <em>“Predicted values must be in range [0, 1]”</em>. <code>vendor/gems57/submission_writer.py</code> and <code>gems/gates.py</code> enforce strict all-finite <code>[0.0, 1.0]</code> values with exact <code>0.0</code> outside the valid footprint before writing bytes. Local checks are necessary preflight guards, not a guarantee of portal acceptance.</li>
  <li><strong>Check the weekly limit (3 per week) on the official portal:</strong> open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">drivendata.org/competitions/306/competition-doe-gems/submissions/</a> in a browser, verify remaining weekly slots, and upload the exact cleared single-band <code>.tif</code> (or single-TIFF <code>.zip</code>) without opening or re-saving in GIS software.</li>
  <li><strong>Use a unique submission name and concise note (<code>&le; 140</code> characters):</strong> never reuse a historical filename or note from another GEMSDOE repository. After scoring, record the exact DrivenData score and timestamp in <code>ledger/submissions.csv</code> as an <code>ORGANIZER-CONFIRMED</code> receipt.</li>
</ol></section>
<section><h2>Summary of Focus-9 &amp; GEMSDOE92 Files (Research Reference Only)</h2>
<table><thead><tr><th>Site</th><th>File to download — research only</th><th>Score / estimate (strictly labeled)</th><th>Uniqueness across listed GEMSDOE sites &amp; status</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>'''

    css = 'body{font:16px/1.55 system-ui;color:#18212e;background:#f4f6f8;margin:0}main{max-width:1100px;margin:auto;padding:24px}section{background:white;padding:20px;margin:18px 0;border-radius:8px}.stop{border:3px solid #b91c1c;background:#fff4f3}.btn{display:inline-block;background:#1d4ed8;color:#fff!important;padding:9px 14px;border-radius:7px;font-weight:700;text-decoration:none;margin:4px 6px 4px 0}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #ccd5df;text-align:left;vertical-align:top}code{overflow-wrap:anywhere}a{color:#124ec0}@media(max-width:700px){table{display:block;overflow:auto}}'
    def page(title, content):
        prefix = '<aside>Current review: DO NOT SUBMIT · <a href="' + ('docs/' if title == 'GEMSDOE92' else '') + 'REVIEW_20261030_ARENA.md"><strong>2026-10-30 focus-nine review &amp; score/uniqueness table</strong></a> · <a href="' + ('docs/' if title == 'GEMSDOE92' else '') + 'review-47314b7f.html">Independent review</a></aside><details data-status-archive="true"><summary>Earlier independent review</summary><p>See linked review; historical clearance is superseded.</p></details>'
        return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{css}</style></head><body><main>{prefix}{content}</main></body></html>\n'

    uniqueness = card.get('uniqueness', {})
    literal = uniqueness.get('literal_reading', {})
    holdout = card.get('holdout_dti', {})
    candidate_dti = holdout.get('exp1', {}).get('dti')
    r0_dti = holdout.get('r0_recipe_control', {}).get('dti')
    paired_ci = holdout.get('paired_delta_vs_r0_recipe', {}).get('ci95')
    blockers = []
    surface_overlap = uniqueness.get('surface_worst_overlap')
    if surface_overlap is None or float(surface_overlap) > 0.70:
        blockers.append('pre-placement surface overlap is missing or exceeds 0.70')
    if literal.get('duplicate_under_literal') is not False:
        blockers.append('literal full-support registry witness triggers the Rule 1 duplicate stop')
    if (candidate_dti is None or r0_dti is None or float(candidate_dti) <= float(r0_dti)
            or not isinstance(paired_ci, list) or len(paired_ci) != 2 or float(paired_ci[0]) <= 0):
        blockers.append('HOLDOUT-DTI did not beat the R0 recipe control with paired 95% CI above zero')
    canary_auc = card.get('leakage_canaries', {}).get('max_auc')
    if canary_auc is None or float(canary_auc) > 0.90:
        blockers.append('feature-alone leakage canary is missing or exceeds AUC 0.90')
    reason = 'Research only; mandatory promotion protocol gates failed.'
    current = {'file': card['raster']['file'], 'sha256':card['raster_sha256'], 'submission_name':card['submission_name'], 'note':card['note'], 'verdict':'negative','ok_to_download':True,'ok_to_submit':False,'reason':reason,'blocking_reasons':blockers, 'run_card': 'downloads/'+Path(card['raster']['file']).name.replace('-zeros.tif','_run_card.json')}
    readiness = {'file':'downloads/'+file, 'raster_sha256':card['raster_sha256'],'submission_name':card['submission_name'],'note':card['note'], 'verdict':'negative','submission_eligible':False,'download_status':'OK TO DOWNLOAD FOR RESEARCH','submission_status':'DO NOT SUBMIT','reason':reason,'blocking_reasons':blockers,'gates':card.get('gates_passed',{})}
    dexp_root_line = ''
    if dexp:
        d_tif = Path(dexp[2]['file']).name
        dexp_root_line = f'<p><strong>2026-10-29 DEXP-KOSTROV-KOENDERINK research GeoTIFF (11/11 format gates PASS, HOLDOUT-DTI 0.11744 &gt; R0 0.09775, 2,262-SHA PI-1 PASS · DO NOT SUBMIT):</strong> <a class="btn" href="docs/downloads/{esc(d_tif)}" download>⬇ Download {esc(d_tif)}</a> · <a href="docs/executive-summary-20261029-dexp-kostrov.html">2026-10-29 DEXP-KOSTROV Executive Summary</a></p>'
    root = f'<p>The organizer leaderboard is not mirrored. <a href="https://www.drivendata.org/termsofuse/">DrivenData Terms of Use</a></p><h1>GEMSDOE92</h1><p class="small"><a href="docs/executive-summary-nine-sites-20261030.html"><strong>2026-10-30 Focus-9 Executive Summary — DO NOT SUBMIT</strong></a> · <a href="docs/REVIEW_20261030_FOCUS9.md">2026-10-30 Three-Pass Repository Review</a> · <a href="docs/REVIEW_20261030_ARENA.md">Arena evidence-gate review</a> · <a href="docs/executive-summary-20261029-dexp-kostrov.html"><strong>2026-10-29 DEXP-KOSTROV Summary</strong></a> · <a href="docs/executive-summary-20261029-lidarsintervalve.html"><strong>2026-10-29 LIDAR-SINTERVALVE Nine-Site Summary</strong></a> · <a href="docs/executive-summary-20261029-marussi-trishear.html"><strong>2026-10-29 MARUSSI-TRISHEAR Executive Summary</strong></a> · <a href="docs/executive-summary-20261029-admitrelay.html"><strong>2026-10-29 ADMITRELAY + LBM-v3 Executive Summary</strong></a> · <a href="docs/executive-summary-nine-sites-20261028.html">Nine-site executive summary</a> · <a href="docs/HYPOTHESES_20261029_DEXP_KOSTROV.md">2026-10-29 DEXP-KOSTROV Hypotheses</a> · <a href="docs/HYPOTHESES_20261029_LIDAR_SINTERVALVE.md">2026-10-29 LIDAR Hypotheses</a> · <a href="docs/STANDING_PROMPT.md">Standing Prompt</a></p>{lsv_root_hero}<section class="stop"><h2>DO NOT SUBMIT — no eligible new TIFF</h2>{dexp_root_line}{marussi_root_line}<p>Research-only file: <a href="docs/downloads/{esc(file)}"><code>{esc(file)}</code></a>; SHA-256 <code>{digest}</code>.</p><p>The 2026-10-29 ADMITRELAY + LBM-v3 candidate is also research-only and <strong>DO NOT SUBMIT</strong>; see its <a href="docs/executive-summary-20261029-admitrelay.html">executive summary &amp; run card</a>. The additional BLINDCORRIDOR artifact is format-pass only and also <strong>DO NOT SUBMIT</strong>; see its <a href="docs/index.html#blindcorridor">byte-bound status and audit</a>.</p><p><a href="docs/index.html">Read the executive summary and research downloads</a> · <a href="docs/how-to-submit.html">How to submit when cleared</a></p></section>'
    outputs = {
        DOCS/'index.html': page('GEMSDOE92 — Executive summary', body),
        DOCS/'nine-sites.html': page('GEMSDOE92 — Nine-site review', body),
        DOCS/'how-to-submit.html': page('GEMSDOE92 — How to submit', guide),
        ROOT/'index.html': page('GEMSDOE92', root),
        DL/'current_submission.json': json.dumps(current, indent=2)+'\n',
        DL/'readiness.json': json.dumps(readiness, indent=2)+'\n',
    }
    if lsv29:
        outputs[DOCS/'executive-summary-20261029-lidarsintervalve.html'] = render_executive_summary_20261029(lsv29[0], lsv29[2])
    if blindcorridor:
        outputs[blindcorridor_feed_path] = json.dumps(blind_status, indent=2)+'\n'
    if dexp:
        outputs[dexp_feed_path] = json.dumps(dexp_status, indent=2)+'\n'
    if admitrelay:
        outputs[admitrelay_feed_path] = json.dumps(ar_status, indent=2)+'\n'
    return outputs
