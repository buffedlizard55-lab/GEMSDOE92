"""Shared literal parallel-run gates.

Forward overlap above 0.70 or rank correlation above 0.90 blocks against ANY
registry raster. Dense/lattice priors are not exempt; reverse overlap and
Jaccard are diagnostic only. Incomplete inventories fail closed. Earlier
module documentation described an informative-only exception, but the actual
comparison and summary functions already implement the literal user rule.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from numbers import Real
import numpy as np
import rasterio
from scipy.ndimage import binary_dilation
from scipy.stats import rankdata, spearmanr
from .metric import RADIUS_PX

RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
JACCARD_LIMIT = 0.50
ROOT = Path(__file__).resolve().parents[2]


def stop_historical_runner(lane: str) -> None:
    """Fail before placement or writes while the pinned literal witness binds.

    Historical runners that performed registry checks only after placement must
    not be used for a new experiment. Re-enabling requires a genuinely complete
    pre-placement gate and a legitimate resolution of the published witness;
    there is deliberately no flag or environment-variable bypass.
    """
    raise SystemExit(
        f"STOP: literal pre-placement registry duplicate; {lane} historical runner disabled "
        "(docs/downloads/review_14f85876_run_card.json)."
    )


def _dots(a):
    a = np.asarray(a)
    return np.isfinite(a) & (a > 0)


def _near(support, radius_px=RADIUS_PX):
    support = np.asarray(support, dtype=bool)
    if radius_px < 0 or support.ndim != 2:
        return np.zeros_like(support, dtype=bool) if radius_px < 0 else support.copy()
    r = int(np.floor(radius_px))
    if r == 0:
        return support.copy()
    r2 = float(radius_px) * float(radius_px)
    # Exact separable decomposition of {dy^2 + dx^2 <= radius_px^2}:
    # |dy| <= floor(radius_px), and for each |dy|, |dx| ranges contiguously over
    # 0..floor(sqrt(radius_px^2 - dy^2)). Identical bit-for-bit to
    # scipy.ndimage.binary_dilation(..., border_value=0) for all grids and radii.
    max_dx_by_abs_dy = {ay: int(np.floor(np.sqrt(max(0.0, r2 - ay * ay)))) for ay in range(r + 1)}
    row_dilated: dict[int, np.ndarray] = {}
    for m in sorted(set(max_dx_by_abs_dy.values())):
        if m == 0:
            row_dilated[0] = support
        else:
            prev_m = max((k for k in row_dilated if k < m), default=None)
            cur = row_dilated[prev_m].copy() if prev_m is not None else support.copy()
            start = (prev_m + 1) if prev_m is not None else 1
            for dx in range(start, m + 1):
                if dx < support.shape[1]:
                    cur[:, dx:] |= support[:, :-dx]
                    cur[:, :-dx] |= support[:, dx:]
            row_dilated[m] = cur
    out = row_dilated[max_dx_by_abs_dy[0]].copy()
    for ay in range(1, r + 1):
        if ay >= support.shape[0]:
            break
        w = row_dilated[max_dx_by_abs_dy[ay]]
        out[ay:, :] |= w[:-ay, :]
        out[:-ay, :] |= w[ay:, :]
    return out


def mark_sparse_near_inplace(out, indices, shape, radius_px=RADIUS_PX, *, value=True):
    """Mark/clear a sparse 2-D support's Euclidean halo without row wrapping.

    ``out`` is a flat boolean buffer for one raster at a time. To clear it,
    pass the same support and ``value=False`` before processing another raster;
    clearing overlapping halos for multiple simultaneous supports is unsafe.
    This is equivalent to ``_near`` with zero outside the grid, including edges.
    """
    if (not isinstance(shape, tuple) or len(shape) != 2
            or any(isinstance(x, bool) or not isinstance(x, (int, np.integer)) or x <= 0 for x in shape)):
        raise ValueError('shape must be a positive (height, width) tuple')
    h, w = map(int, shape)
    if (not isinstance(out, np.ndarray) or out.dtype != np.bool_
            or out.ndim != 1 or out.size != h * w):
        raise ValueError('out must be a flat boolean buffer matching shape')
    idx = np.asarray(indices)
    if idx.ndim != 1 or idx.dtype.kind not in 'iu':
        raise ValueError('indices must be a one-dimensional integer array')
    if idx.size and (np.any(idx < 0) or np.any(idx >= h * w)):
        raise ValueError('support index outside grid')
    if isinstance(radius_px, bool) or not isinstance(radius_px, Real) or not np.isfinite(radius_px) or radius_px < 0:
        raise ValueError('radius must be a finite nonnegative number')
    if not isinstance(value, (bool, np.bool_)):
        raise ValueError('value must be boolean')
    idx = idx.astype(np.intp, copy=False)
    y, x = np.divmod(idx, w)
    r = int(np.floor(radius_px))
    # Offsets larger than the grid cannot contribute, even for a huge radius.
    ry, rx = min(r, h - 1), min(r, w - 1)
    radius = float(radius_px)
    r2 = radius * radius
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if dy * dy + dx * dx > r2:
                continue
            yy, xx = y + dy, x + dx
            valid = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
            out[yy[valid] * w + xx[valid]] = value
    return out


def dot_overlap(mine, theirs, radius_px=RADIUS_PX):
    m, t = _dots(mine), _dots(theirs)
    if m.shape != t.shape:
        raise ValueError('overlap grid shape mismatch')
    if not m.any() or not t.any():
        return 0.0
    return float(_near(t, radius_px)[m].mean())


def _jaccard(a, b):
    u = int((a | b).sum())
    return float((a & b).sum() / u) if u else 0.0


def summarize_registry_rows(rows, *, registry_rasters_expected, complete_accessible_scan,
                            source_errors, candidate_meta, scope):
    """Apply the same literal thresholds to already hash-verified comparison rows.

    This allows a complete immutable prior audit to be extended with only newly
    published blobs, instead of re-downloading hundreds of unchanged rasters.
    The caller must prove candidate identity and the completeness/count of the
    combined registry before passing ``complete_accessible_scan=True``.
    """
    rows = list(rows)
    source_errors = list(source_errors or [])
    if (isinstance(registry_rasters_expected, bool)
            or not isinstance(registry_rasters_expected, (int, np.integer))
            or registry_rasters_expected < 0):
        raise ValueError('expected registry count must be a nonnegative integer')
    expected = int(registry_rasters_expected)
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError('registry rows must be objects')
    checked = [r for r in rows if 'error' not in r]
    errors = [r for r in rows if 'error' in r]
    # An empty inventory or a truthy string such as "false" is not a scan.
    inventory_complete = bool(complete_accessible_scan is True and expected > 0
                              and expected == len(rows) and not errors and not source_errors)
    # A sampled Spearman value cannot prove the literal full-raster threshold.
    # Historical rows lacking an explicit exactness attestation fail closed.
    rank_exact = bool(checked) and all(r.get('rank_exact') is True for r in checked)
    complete = bool(inventory_complete and rank_exact)
    for row in checked:
        overlap = row.get('my_dots_within_3px_of_theirs')
        if (not isinstance(overlap, Real) or isinstance(overlap, (bool, np.bool_))
                or not np.isfinite(overlap) or not 0 <= overlap <= 1):
            raise ValueError('invalid or missing literal forward overlap')
        if 'spearman_full_footprint' not in row:
            raise ValueError('missing full-footprint rank correlation')
        rho = row['spearman_full_footprint']
        if rho is not None and (not isinstance(rho, Real) or isinstance(rho, (bool, np.bool_))
                                or not np.isfinite(rho) or not -1.000000000001 <= rho <= 1.000000000001):
            raise ValueError('invalid full-footprint rank correlation')
        jac = row.get('jaccard_dot_sets')
        if jac is not None and (not isinstance(jac, Real) or isinstance(jac, (bool, np.bool_))
                                or not np.isfinite(jac) or not 0 <= jac <= 1):
            raise ValueError('invalid Jaccard diagnostic')
        for key in ('duplicate_by_rho', 'duplicate_by_overlap', 'rank_exact',
                    'identical_bytes', 'identical_decoded_predictions'):
            if key in row and not isinstance(row[key], (bool, np.bool_)):
                raise ValueError(f'invalid registry boolean: {key}')
    # Derive stops from the measurements, not just caller-supplied flags. A
    # contradictory true flag remains a conservative stop; false cannot erase
    # a measured breach. Jaccard remains diagnostic only.
    flags = [r for r in checked if (
        r['my_dots_within_3px_of_theirs'] > OVERLAP_LIMIT
        or (r['spearman_full_footprint'] is not None
            and abs(r['spearman_full_footprint']) > RHO_LIMIT)
        or any(r.get(k, False) for k in ('duplicate_by_rho', 'duplicate_by_overlap',
                                         'identical_bytes', 'identical_decoded_predictions')))]
    rank_rows = [r for r in checked if r['spearman_full_footprint'] is not None]
    worst_rho = max(rank_rows, key=lambda r: abs(r['spearman_full_footprint']), default=None)
    worst_ov = max(checked, key=lambda r: r['my_dots_within_3px_of_theirs'], default=None)
    jaccard_rows = [r for r in checked if r.get('jaccard_dot_sets') is not None]
    worst_jac = max(jaccard_rows, key=lambda r: r['jaccard_dot_sets'], default=None)
    count = candidate_meta['my_dots']
    if isinstance(count, (bool, np.bool_)) or not isinstance(count, (int, np.integer)) or count < 0:
        raise ValueError('candidate dot count must be a nonnegative integer')
    variation = candidate_meta['candidate_rank_variation']
    if not isinstance(variation, (bool, np.bool_)):
        raise ValueError('candidate rank variation must be boolean')
    my_dot_count = int(count)
    norm = bool(variation)
    unique = complete and my_dot_count > 0 and norm and not flags
    return dict(
        my_file=candidate_meta.get('my_file'), evidence_class='REGISTRY-MEASUREMENT',
        my_dots=my_dot_count,
        candidate_decoded_sha256=candidate_meta.get('candidate_decoded_sha256'),
        candidate_file_sha256=candidate_meta.get('candidate_file_sha256'),
        rho_limit=RHO_LIMIT, overlap_limit=OVERLAP_LIMIT, jaccard_limit=JACCARD_LIMIT,
        registry_rasters_expected=expected, registry_rasters_checked=len(checked),
        complete_accessible_scan=complete, registry_inventory_complete=inventory_complete,
        full_grid_rank_complete=rank_exact, missing_or_invalid=len(errors),
        source_errors=source_errors,
        worst_spearman_full_footprint=(worst_rho['spearman_full_footprint'] if worst_rho else None),
        worst_abs_spearman_full_footprint=(abs(worst_rho['spearman_full_footprint']) if worst_rho else None),
        worst_rho_submission=(worst_rho.get('submission') if worst_rho else None),
        worst_dot_overlap=(worst_ov['my_dots_within_3px_of_theirs'] if worst_ov else None),
        worst_overlap_submission=(worst_ov.get('submission') if worst_ov else None),
        worst_jaccard_dot_sets=(worst_jac['jaccard_dot_sets'] if worst_jac else None),
        worst_jaccard_submission=(worst_jac.get('submission') if worst_jac else None),
        byte_unique_among_checked=bool(checked) and not any(r.get('identical_bytes', False) for r in checked),
        pixel_unique_among_checked=bool(checked) and not any(r.get('identical_decoded_predictions', False) for r in checked),
        duplicate_count=len(flags), unique=bool(unique), rows=rows,
        jaccard_diagnostic_only=True,
        verdict='promote-to-selector-only' if unique else 'negative',
        stop_required=bool(flags or not complete or not my_dot_count or not norm),
        candidate_rank_variation=norm,
        scope=scope)


def merge_registry_audits(previous, extension, *, registry_rasters_expected,
                          complete_accessible_scan=True, scope=None):
    """Extend a full prior raster audit with a checked delta and keep fail-closed.

    Both audits must describe the same exact candidate bytes and decoded pixels.
    Duplicate file hashes are retained once; contradictory measurements for one
    SHA256 are rejected rather than averaged or silently overwritten.
    """
    identity_keys = ('candidate_file_sha256', 'candidate_decoded_sha256', 'my_dots',
                     'candidate_rank_variation')
    for key in identity_keys:
        if previous.get(key) != extension.get(key):
            raise ValueError(f'cannot merge audits with different candidate {key}')
    for key in ('candidate_file_sha256', 'candidate_decoded_sha256'):
        pin = previous.get(key)
        if (not isinstance(pin, str) or len(pin) != 64
                or any(c not in '0123456789abcdef' for c in pin)):
            raise ValueError(f'cannot merge audits without a valid candidate {key}')
    count = previous.get('my_dots')
    if (isinstance(count, (bool, np.bool_)) or not isinstance(count, (int, np.integer))
            or count <= 0 or previous.get('candidate_rank_variation') is not True):
        raise ValueError('cannot merge audits without a nonempty variable candidate')
    limits = {'rho_limit': RHO_LIMIT, 'overlap_limit': OVERLAP_LIMIT, 'jaccard_limit': JACCARD_LIMIT}
    if any(previous.get(key) != value or extension.get(key) != value for key, value in limits.items()):
        raise ValueError('cannot merge audits with missing or different uniqueness thresholds')
    if previous.get('complete_accessible_scan') is not True:
        raise ValueError('base audit is not a complete accessible registry scan')
    if extension.get('complete_accessible_scan') is not True:
        raise ValueError('registry delta is incomplete')
    if previous.get('missing_or_invalid') or extension.get('missing_or_invalid'):
        raise ValueError('registry audit contains missing or invalid raster rows')
    if previous.get('source_errors') or extension.get('source_errors'):
        raise ValueError('registry audit contains source errors')

    merged = {}
    for row in [*previous['rows'], *extension['rows']]:
        if 'error' in row:
            raise ValueError('cannot extend a registry audit with an errored row')
        digest = row.get('sha256')
        if (not isinstance(digest, str) or len(digest) != 64
                or any(c not in '0123456789abcdef' for c in digest)):
            raise ValueError('registry audit row has no valid content SHA256')
        old = merged.get(digest)
        if old is not None:
            for metric in ('my_dots_within_3px_of_theirs', 'spearman_full_footprint', 'rank_exact',
                           'jaccard_dot_sets', 'identical_bytes',
                           'identical_decoded_predictions'):
                if old.get(metric) != row.get(metric):
                    raise ValueError(f'conflicting registry measurements for SHA256 {digest}: {metric}')
            sources = set(old.get('sources', []))
            if old.get('submission'):
                sources.add(old['submission'])
            if row.get('submission'):
                sources.add(row['submission'])
            sources.update(row.get('sources', []))
            old['sources'] = sorted(sources)
        else:
            merged[digest] = dict(row)
            sources = set(row.get('sources', []))
            if row.get('submission'):
                sources.add(row['submission'])
            merged[digest]['sources'] = sorted(sources)
    rows = sorted(merged.values(), key=lambda r: (r.get('repo', ''), r.get('submission', ''), r['sha256']))
    meta = {k: previous.get(k) for k in identity_keys}
    meta['my_file'] = previous.get('my_file')
    if (isinstance(registry_rasters_expected, (bool, np.bool_))
            or not isinstance(registry_rasters_expected, (int, np.integer))
            or registry_rasters_expected < 0):
        raise ValueError('expected registry count must be a nonnegative integer')
    expected = int(registry_rasters_expected)
    complete = bool(complete_accessible_scan is True and len(rows) == expected)
    result = summarize_registry_rows(
        rows, registry_rasters_expected=expected,
        complete_accessible_scan=complete,
        source_errors=[], candidate_meta=meta,
        scope=scope or 'Indexed public owner-repository inventory; not a complete organizer registry. External, private, unlinked, inaccessible, and later-written sources may be absent.',
    )
    result['phase'] = extension.get('phase', previous.get('phase'))
    result['reviewed_utc'] = extension.get('reviewed_utc')
    result['submission_slots_used'] = int(previous.get('submission_slots_used', 0))
    result['incremental_extension'] = dict(
        base_rasters=previous.get('registry_rasters_checked'),
        newly_discovered_rasters=extension.get('registry_rasters_checked'),
        deduplicated_rasters=expected,
    )
    return result


def surface_rho(mine, theirs, valid):
    m = np.asarray(mine, np.float32)[valid]
    t = np.asarray(theirs, np.float32)[valid]
    mb, tb = _dots(m), _dots(t)
    union = mb | tb
    rho_union = float('nan')
    if union.sum() > 10 and mb[union].any() and tb[union].any() and not (mb[union].all() or tb[union].all()):
        rho_union = float(spearmanr(m[union], t[union]).statistic)
    rho = float(spearmanr(m, t).statistic) if np.ptp(m) and np.ptp(t) else float('nan')
    return dict(spearman_on_dot_union=rho_union, n_dot_union=int(union.sum()),
                jaccard_dot_sets=_jaccard(mb,tb), spearman_full_footprint=rho)


def _sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for c in iter(lambda: stream.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def records_from_index(index):
    if isinstance(index, list):
        return index, False, ["Legacy list has no complete-inventory certificate; diagnostic only"]
    if not isinstance(index, dict) or 'rasters' not in index:
        raise ValueError('registry must be a list or a full inventory with rasters')
    records = [dict(repo=r['repo_first'], submission=r['sources'][0], file=r['cache_file'],
                    sha256=r['sha256'], sources=r['sources']) for r in index['rasters']]
    # Historical /tmp inventory never had a completeness certificate; file checks
    # below still prevent it from passing when all ephemeral caches disappear.
    # JSON strings such as "false" are truthy in Python but are not proof of a
    # completed scan. Only an actual boolean may claim completeness.
    complete = index.get('complete_accessible_scan', False) is True
    return records, complete, index.get('errors', [])


def compare_array_to_registry(mine, registry_index, footprint, *, file_sha256=None,
                              include_reverse=True, progress=None, expected_grid=None):
    # Validate the original values before any lossy dtype conversion; casting
    # 1+epsilon to float32 first can silently turn an invalid value into 1.
    mine = np.asarray(mine)
    fp = np.asarray(footprint, bool)
    if mine.ndim != 2 or mine.shape != fp.shape or not fp.any():
        raise ValueError('candidate / footprint grid mismatch or empty footprint')
    if (not (np.issubdtype(mine.dtype, np.number) or np.issubdtype(mine.dtype, np.bool_))
            or np.iscomplexobj(mine) or not np.isfinite(mine).all()
            or (mine < 0).any() or (mine > 1).any()):
        raise ValueError('candidate must already be finite in [0,1]')
    if (mine[~fp] > 0).any():
        raise ValueError('positive candidate mass outside footprint')
    idx = registry_index if isinstance(registry_index, (list, dict)) else json.loads(Path(registry_index).read_text())
    records, inventory_complete, source_errors = records_from_index(idx)
    rows = []
    values = mine[fp]
    ranks = rankdata(values).astype(np.float64)
    ranks -= ranks.mean()
    norm = float(np.linalg.norm(ranks))
    my_support = _dots(mine) & fp
    my_dot_count = int(my_support.sum())
    my_near = _near(my_support) if include_reverse else None
    # The on-disk submission representation is float32. Hash that encoding for
    # identity checks, but use the original precision above for validity/ranks.
    decoded_digest = hashlib.sha256(np.ascontiguousarray(mine, dtype=np.float32).tobytes()).hexdigest()
    for i, rec in enumerate(records):
        p = Path(rec['file'])
        if not p.is_absolute():
            p = ROOT / p
        base = dict(repo=rec.get('repo'), submission=rec.get('submission',p.name), file=str(p))
        try:
            if not p.exists():
                raise FileNotFoundError('missing registry file; cannot certify uniqueness')
            digest = _sha(p)
            pin = rec.get('sha256')
            if (not isinstance(pin, str) or len(pin) != 64
                    or any(c not in '0123456789abcdef' for c in pin)
                    or digest != pin):
                raise ValueError('registry SHA256 pin missing, malformed, or mismatched')
            with rasterio.open(p) as src:
                if src.count != 1 or src.shape != mine.shape:
                    raise ValueError('registry grid or band-count mismatch')
                if expected_grid is not None and (src.shape, src.crs, src.transform) != expected_grid:
                    raise ValueError('registry CRS/transform differs from reference')
                if mine.shape == (3730,3292):
                    from .grid import TRANSFORM
                    if src.crs is None or src.crs.to_epsg()!=32611 or src.transform != TRANSFORM:
                        raise ValueError('registry CRS/transform mismatch')
                theirs = src.read(1).astype(np.float32)
            # Missing values inside the compared domain are not zero evidence;
            # accepting them could manufacture uniqueness against a partial prior.
            if not np.isfinite(theirs[fp]).all():
                raise ValueError('registry has nonfinite values inside the candidate footprint')
            # Outside-footprint values are ignored for support and pixel identity.
            theirs[~fp] = 0
            tv = theirs[fp]
            support = (theirs > 0) & fp
            tb = support[fp]
            # Exact Spearman with tied ranks; candidate ranks are reused for all priors.
            if norm == 0 or np.ptp(tv) == 0:
                rho = None
            elif np.all((tv == 0) | (tv == 1)):
                nt = int(tb.sum()); n = len(tv)
                rho = float(ranks[tb].sum() / (norm * np.sqrt(nt*(n-nt)/n)))
            else:
                tr = rankdata(tv).astype(np.float64)
                tr -= tr.mean()
                rho = float(np.dot(ranks,tr)/(norm*np.linalg.norm(tr)))
            near_sup = _near(support)
            ov = float(near_sup[my_support].mean()) if my_dot_count else 0.0
            halo_cov = float(near_sup[fp].mean())
            reverse = float(my_near[support].mean()) if include_reverse and support.any() else 0.0
            jac = _jaccard(my_support, support)
            their_decoded = hashlib.sha256(np.ascontiguousarray(theirs).tobytes()).hexdigest()
            row = {**base, 'sha256':digest, 'decoded_sha256':their_decoded,
                'their_dots':int(support.sum()), 'my_dots_within_3px_of_theirs':ov,
                'forward_overlap':ov, 'halo_coverage':halo_cov,
                'their_dots_within_3px_of_mine':reverse, 'spearman_full_footprint':rho,
                'rank_exact':True, 'jaccard_dot_sets':jac,
                'identical_bytes':bool(file_sha256 and digest==file_sha256),
                'identical_decoded_predictions':bool(their_decoded==decoded_digest),
                'duplicate_by_rho':bool(rho is not None and abs(rho) > RHO_LIMIT),
                'duplicate_by_overlap':bool(ov > OVERLAP_LIMIT),
                'duplicate_by_jaccard':bool(jac > JACCARD_LIMIT)}
            rows.append(row)
        except (OSError, ValueError, rasterio.errors.RasterioError) as e:
            rows.append({**base, 'error':str(e)})
        if progress:
            progress(i+1,len(records),rows[-1])
    complete = inventory_complete and bool(records) and not source_errors
    return summarize_registry_rows(
        rows,
        registry_rasters_expected=len(records),
        complete_accessible_scan=complete,
        source_errors=source_errors,
        candidate_meta=dict(
            my_file=None,
            my_dots=my_dot_count,
            candidate_decoded_sha256=decoded_digest,
            candidate_file_sha256=file_sha256,
            candidate_rank_variation=norm > 0,
        ),
        scope='All hash-verified accessible entries in the indexed public owner-repository inventory; not a complete organizer registry. External/private/unlinked/inaccessible files may be absent. Reverse overlap is diagnostic only.',
    )


def compare_to_registry(mine_path, registry_index, footprint, **kwargs):
    mine_path = Path(mine_path)
    with rasterio.open(mine_path) as src:
        if src.count != 1:
            raise ValueError('candidate must be single band')
        expected = kwargs.get('expected_grid')
        if expected is not None and (src.shape, src.crs, src.transform) != expected:
            raise ValueError('candidate CRS/shape/transform differs from reference grid')
        if src.shape == (3730, 3292):
            from .grid import TRANSFORM
            if src.crs is None or src.crs.to_epsg() != 32611 or src.transform != TRANSFORM:
                raise ValueError('candidate CRS/transform differs from pinned grid')
        mine = src.read(1)
    result = compare_array_to_registry(mine, registry_index, footprint,
        file_sha256=_sha(mine_path), **kwargs)
    result['my_file'] = str(mine_path)
    return result


def saturation_certificate(registry_path, footprint, catalogue=None, *, expected_grid=None):
    """Certify whether one prior covers every allowed cell within the literal 3 px halo.

    Supply ``expected_grid=(shape, crs, transform)`` when using this as a
    pre-placement gate. A coincidentally equal-shaped raster on a different
    map grid is not a valid witness.
    """
    fp = np.asarray(footprint, bool)
    if fp.ndim != 2 or not fp.any():
        raise ValueError('empty or non-2D footprint')
    if catalogue is not None and np.asarray(catalogue).shape != fp.shape:
        raise ValueError('catalogue / footprint grid mismatch')
    allowed = fp if catalogue is None else fp & ~np.asarray(catalogue, bool)
    if not allowed.any():
        raise ValueError('empty allowed domain cannot certify a meaningful blocker')
    with rasterio.open(registry_path) as src:
        if src.shape != fp.shape or src.count != 1:
            raise ValueError('witness grid mismatch')
        if expected_grid is not None and (src.shape, src.crs, src.transform) != expected_grid:
            raise ValueError('witness CRS/transform differs from reference grid')
        a = src.read(1)
    positive = _dots(a) & fp
    covered = _near(positive)
    uncovered = int((allowed & ~covered).sum())
    return dict(evidence_class='REGISTRY-MEASUREMENT', witness_file=str(registry_path),
        witness_sha256=_sha(registry_path), positive_pixels=int(positive.sum()),
        allowed_pixels=int(allowed.sum()), uncovered_allowed_pixels=uncovered,
        covered_allowed_fraction=float(covered[allowed].mean()),
        universal_overlap_blocker=uncovered==0, overlap_limit=OVERLAP_LIMIT,
        support_definition='finite prediction > 0 (inherited literal support rule)',
        implication='Every nonempty candidate dot set in the allowed domain has forward overlap 1.0 with this prior; therefore it cannot pass the 0.70 gate.' if uncovered==0 else 'No universal blockage established.')


DENSE_SUPPORT_FRACTION = 0.20
"""Support fraction above which a registry raster is a *continuous surface*.

The inherited literal gate compares "my dots" against "one registry raster's
dots" with a 70 % / 3 px forward-overlap test.  A raster whose positive support
covers a large part of the study area has no dot set to compare against: every
nonempty candidate is trivially within 3 px of it.  This was measured, not
assumed -- see ``evidence/uniqueness_saturation_certificate.json`` and the
independent re-measurement recorded with this session's certificate: the 17GEMSDOE
``E-proba-multiscale`` surface (sha256 ``ab0a0a62…``) is positive on all 5,167,373
footprint cells and leaves **0** of the 5,106,385 allowed cells uncovered, so the
literal gate fires on any nonempty candidate in the allowed domain.

The classification below does not weaken any threshold.  It separates the two
tests the protocol already names -- rank correlation on the *surface*, 3 px dot
overlap on the *dots* -- and applies each to representations it can discriminate
between.  Both readings are always reported.
"""


DENSE_HALO_FRACTION = 0.70


def halo_coverage(support, allowed, radius_px: float = RADIUS_PX) -> float:
    """Fraction of ``allowed`` cells inside the ``radius_px`` halo of ``support``.

    This is the expected overlap for uniformly sampled allowed cells, NOT
    an upper bound for an arbitrary candidate. A candidate concentrated on
    the support can have overlap 1 even when halo coverage is much smaller.
    Only complete allowed-domain coverage proves universal overlap 1.
    """
    sup = np.asarray(support, bool)
    alw = np.asarray(allowed, bool)
    if sup.shape != alw.shape:
        raise ValueError("halo coverage grid shape mismatch")
    n = int(alw.sum())
    if n == 0 or not sup.any():
        return 0.0
    return float(_near(sup, radius_px)[alw].sum() / n)


def representation_class_v2(support, allowed, radius_px: float = RADIUS_PX) -> dict:
    """Classify one prior by halo coverage, the quantity the overlap test uses."""
    cov = halo_coverage(support, allowed, radius_px)
    return dict(kind=("space_filling" if cov >= DENSE_HALO_FRACTION else "discriminating"),
                halo_coverage=cov, limit=DENSE_HALO_FRACTION,
                support_fraction=float(np.asarray(support, bool).sum()
                                       / max(int(np.asarray(allowed, bool).sum()), 1)))


def binding_duplicate_decision(rows, *, rho_limit: float = RHO_LIMIT,
                               overlap_limit: float = OVERLAP_LIMIT) -> dict:
    """Summarize literal duplicate evidence; never authorize a submission.

    A nonempty row set and valid measurements are required. Error rows are
    binding stops, not silently omitted. This helper cannot establish registry
    completeness, even when none of the supplied rows breaches a threshold.
    ``None`` rank is allowed for a constant prior (undefined correlation).
    """
    if rho_limit != RHO_LIMIT or overlap_limit != OVERLAP_LIMIT:
        raise ValueError('literal protocol thresholds may not be changed')
    rows = list(rows)
    if not rows or any(not isinstance(r, dict) for r in rows):
        raise ValueError('nonempty registry rows must be objects')
    checked = [r for r in rows if 'error' not in r]
    errors = [r for r in rows if 'error' in r]
    if not checked:
        raise ValueError('no valid registry rows')
    for row in checked:
        overlap = row.get('forward_overlap', row.get('my_dots_within_3px_of_theirs'))
        if (not isinstance(overlap, Real) or isinstance(overlap, (bool, np.bool_))
                or not np.isfinite(overlap) or not 0 <= overlap <= 1):
            raise ValueError('invalid or missing literal forward overlap')
        if 'spearman_full_footprint' in row:
            rho = row['spearman_full_footprint']
        elif 'spearman' in row:
            rho = row['spearman']
        else:
            raise ValueError('missing full-footprint rank correlation')
        if rho is not None and (not isinstance(rho, Real) or isinstance(rho, (bool, np.bool_))
                                or not np.isfinite(rho) or not -1.000000000001 <= rho <= 1.000000000001):
            raise ValueError('invalid full-footprint rank correlation')
        coverage = row.get('halo_coverage', 0.0)
        if (not isinstance(coverage, Real) or isinstance(coverage, (bool, np.bool_))
                or not np.isfinite(coverage) or not 0 <= coverage <= 1):
            raise ValueError('invalid halo coverage')
    disc = [r for r in checked if r.get('halo_coverage', 0.0) < DENSE_HALO_FRACTION]
    space = [r for r in checked if r not in disc]
    # Diagnostic representation groups do NOT exempt any prior from the user's
    # literal >0.70 forward-overlap stop rule. Earlier code silently dropped
    # space-filling rasters here and could falsely approve a duplicate.
    def _fwd_val(r):
        if r.get("forward_overlap") is not None:
            return float(r["forward_overlap"])
        if r.get("my_dots_within_3px_of_theirs") is not None:
            return float(r["my_dots_within_3px_of_theirs"])
        return None

    def _rho_val(row):
        return row['spearman_full_footprint'] if 'spearman_full_footprint' in row else row['spearman']

    fwd = [r for r in checked if _fwd_val(r) is not None]
    rho = [r for r in checked if _rho_val(r) is not None]
    worst_fwd = max(fwd, key=_fwd_val) if fwd else None
    worst_rho = max(rho, key=lambda r: abs(_rho_val(r))) if rho else None
    is_dup = bool((worst_fwd and _fwd_val(worst_fwd) > overlap_limit)
                  or (worst_rho and abs(float(_rho_val(worst_rho))) > rho_limit))
    stop = bool(is_dup or errors)
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        binding_rule="literal-all-rasters",
        discriminating_priors=len(disc),
        space_filling_priors=len(space),
        space_filling_files=[r.get("file") or r.get("submission") for r in space],
        worst_forward_overlap=_fwd_val(worst_fwd) if worst_fwd else None,
        worst_forward_overlap_file=(worst_fwd.get("file") or worst_fwd.get("submission")) if worst_fwd else None,
        worst_abs_spearman=abs(float(_rho_val(worst_rho))) if worst_rho else None,
        worst_abs_spearman_file=(worst_rho.get("file") or worst_rho.get("submission")) if worst_rho else None,
        overlap_limit=overlap_limit, rho_limit=rho_limit,
        duplicate=is_dup, missing_or_invalid=len(errors),
        stop_required=stop,
        verdict=("negative" if stop else "diagnostic-clear-only"),
        submission_eligible=False,
        note=("Space-filling priors remain binding under the literal rule. This "
              "row summary cannot prove inventory completeness or authorize a slot."))


def representation_class(their_dots: int, footprint_cells: int,
                         limit: float = DENSE_SUPPORT_FRACTION) -> dict:
    """Classify one registry raster by the denseness of its positive support."""
    if footprint_cells <= 0:
        raise ValueError("footprint_cells must be positive")
    fraction = float(their_dots) / float(footprint_cells)
    return dict(kind=("continuous_surface" if fraction > limit else "dot_field"),
                support_fraction=fraction, limit=float(limit))


def two_phase_summary(rows, footprint_cells: int, *, rho_limit: float = RHO_LIMIT,
                      overlap_limit: float = OVERLAP_LIMIT,
                      jaccard_limit: float = JACCARD_LIMIT,
                      expected_rasters: int | None = None) -> dict:
    """Report the literal and the like-for-like readings side by side.

    ``rows`` is the row list produced by :func:`compare_array_to_registry` (or an
    extension of it).  Nothing is filtered out of the *literal* reading: it keeps
    the inherited definition (every positive finite pixel is a dot) and reports
    its worst case and firing count.  The like-for-like reading applies the same
    inherited thresholds to the subset of rasters that are dot fields, which is
    the only comparison in which a dot-overlap test carries information.  The
    rank-correlation test is applied to every raster in both readings.
    """
    rows = list(rows)
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError("registry rows must be objects")
    checked = [dict(r) for r in rows if "error" not in r]
    if not checked:
        raise ValueError("no checked registry rows to summarise")
    # Use the shared literal validator so missing/NaN metrics and error rows
    # cannot be transformed into a positive interpretation by this diagnostic.
    literal = binding_duplicate_decision(rows, rho_limit=rho_limit, overlap_limit=overlap_limit)
    for r in checked:
        r.setdefault("representation", representation_class(
            int(r.get("their_dots", 0)), footprint_cells)["kind"])

    def _worst(subset, key, *, absolute=False):
        vals = [r for r in subset if r.get(key) is not None]
        if not vals:
            return None, None
        who = max(vals, key=lambda r: abs(r[key]) if absolute else r[key])
        return float(who[key]), who

    rho_lit, rho_who = _worst(checked, "spearman_full_footprint", absolute=True)
    ov_lit, ov_who = _worst(checked, "my_dots_within_3px_of_theirs")
    dot_rows = [r for r in checked if r["representation"] == "dot_field"]
    surf_rows = [r for r in checked if r["representation"] == "continuous_surface"]
    ov_dot, ov_dot_who = _worst(dot_rows, "my_dots_within_3px_of_theirs")
    ov_rev, ov_rev_who = _worst(checked, "their_dots_within_3px_of_mine")
    jac, jac_who = _worst(checked, "jaccard_dot_sets")
    literal_firings = [dict(submission=r.get("submission"), repo=r.get("repo"),
                            representation=r["representation"],
                            forward_overlap=r["my_dots_within_3px_of_theirs"],
                            their_dots=r.get("their_dots"))
                       for r in checked if r["my_dots_within_3px_of_theirs"] > overlap_limit]
    like_firings = [f for f in literal_firings if f["representation"] == "dot_field"]
    literal_rho_firings = [r.get("submission") for r in checked
                           if r.get("spearman_full_footprint") is not None
                           and abs(r["spearman_full_footprint"]) > rho_limit]
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        submission_eligible=False,
        stop_required=literal['stop_required'],
        missing_or_invalid=literal['missing_or_invalid'],
        rasters_checked=len(checked),
        rasters_expected=expected_rasters,
        scope_note=("Checked against every registry raster whose bytes are present locally (plus any "
                    "explicitly fetched witnesses). Un-fetched registry entries are a stated scope "
                    "limitation, never a claim of absence."),
        footprint_cells=int(footprint_cells),
        dense_support_fraction=DENSE_SUPPORT_FRACTION,
        thresholds=dict(rho=rho_limit, forward_overlap=overlap_limit, jaccard=jaccard_limit),
        literal_reading=dict(
            worst_spearman_full_footprint=rho_lit, worst_spearman_submission=(rho_who or {}).get("submission"),
            worst_forward_overlap=ov_lit, worst_overlap_submission=(ov_who or {}).get("submission"),
            forward_overlap_firings=len(literal_firings),
            rho_firings=len(literal_rho_firings),
            duplicate=bool(literal_firings or literal_rho_firings),
            note=("Literal support includes continuous surfaces. A threshold firing is a binding "
                  "protocol duplicate, though it does not by itself prove pixel identity."),
        ),
        like_for_like_reading=dict(
            dot_field_rasters=len(dot_rows), continuous_surface_rasters=len(surf_rows),
            worst_forward_overlap_dot_fields=ov_dot,
            worst_forward_overlap_dot_field_submission=(ov_dot_who or {}).get("submission"),
            worst_reverse_overlap=ov_rev,
            worst_reverse_overlap_submission=(ov_rev_who or {}).get("submission"),
            worst_jaccard=jac, worst_jaccard_submission=(jac_who or {}).get("submission"),
            forward_overlap_firings=len(like_firings),
            duplicate=bool(like_firings or literal_rho_firings),
            note=("Inherited thresholds, applied to dot fields only; rank correlation still applies to "
                  "every raster including the continuous surfaces."),
        ),
        literal_firings=literal_firings,
    )


# ---------------------------------------------------------------------------
# Matched-budget support for dense registry rasters (added 2026-10-25, BLINDFAULT
# session; see IRREGULARITIES.md #IR-92-DENSE-WITNESS-MATCHED-BUDGET).
#
# Matched-budget overlap is a useful representation diagnostic, NOT permission
# to replace the user's literal overlap gate. Retain both measurements, but a
# dense registry raster is never exempt from a literal duplicate stop.
# ---------------------------------------------------------------------------

DOT_FIELD_MAX_SUPPORT = 150_000


def matched_budget_support(their_values, footprint, k):
    """Top-``k`` positive finite cells of ``their_values`` inside ``footprint``."""
    v = np.asarray(their_values, dtype=np.float64)
    fp = np.asarray(footprint, dtype=bool)
    pos = fp & np.isfinite(v) & (v > 0)
    n_pos = int(pos.sum())
    out = np.zeros(v.shape, dtype=bool)
    if n_pos == 0 or k <= 0:
        return out
    if n_pos <= k:
        return pos
    flat_idx = np.flatnonzero(pos)
    vals = v.ravel()[flat_idx]
    order = np.argsort(-vals, kind="stable")[:int(k)]
    out.ravel()[flat_idx[order]] = True
    return out


def dual_overlap(mine, their_values, footprint, radius_px=RADIUS_PX,
                 dot_field_max_support=DOT_FIELD_MAX_SUPPORT):
    """Literal and matched-budget forward overlap of ``mine`` against one raster."""
    m = _dots(mine)
    their_support = _dots(their_values) & np.asarray(footprint, bool)
    n_theirs = int(their_support.sum())
    k = int(m.sum())
    literal = dot_overlap(m, their_support, radius_px)
    if n_theirs <= dot_field_max_support:
        matched = literal
        representation = "dot_field"
    else:
        matched = dot_overlap(m, matched_budget_support(their_values, footprint, k), radius_px)
        representation = "continuous_surface"
    return dict(their_dots=int(n_theirs), my_dots=k, representation=representation,
                literal_forward_overlap=float(literal), matched_budget_forward_overlap=float(matched),
                matched_budget_k=k if representation == "continuous_surface" else None)


def dual_reading_decision(rows, *, rho_limit=RHO_LIMIT, overlap_limit=OVERLAP_LIMIT):
    """Apply the literal gate; matched-budget overlap remains diagnostic only.

    Error rows stop clearance rather than being silently dropped. This helper
    summarizes supplied rows, not inventory completeness, and never authorizes
    a competition slot. Historical matched-budget receipts are not rewritten.
    """
    if not all(isinstance(v, Real) and not isinstance(v, bool) and np.isfinite(v)
               and 0 <= v <= 1 for v in (rho_limit, overlap_limit)):
        raise ValueError("thresholds must be finite and in [0,1]")
    rows = list(rows)
    if not rows:
        raise ValueError("no registry rows")
    if any(not isinstance(r, dict) for r in rows):
        raise ValueError("registry rows must be objects")
    checked = [r for r in rows if "error" not in r]
    errors = [r for r in rows if "error" in r]
    if not checked:
        raise ValueError("no valid registry rows")
    for r in checked:
        for key in ("literal_forward_overlap", "matched_budget_forward_overlap"):
            value = r.get(key)
            if (not isinstance(value, Real) or isinstance(value, bool)
                    or not np.isfinite(value) or not 0 <= value <= 1):
                raise ValueError(f"invalid {key}")
        if "spearman_surface" not in r:
            raise ValueError("missing spearman_surface")
        rho = r["spearman_surface"]
        if rho is not None and (not isinstance(rho, Real) or isinstance(rho, bool)
                                or not np.isfinite(rho) or not -1 <= rho <= 1):
            raise ValueError("invalid spearman_surface")
        if r.get("representation") not in ("dot_field", "continuous_surface"):
            raise ValueError("invalid registry representation")

    def _rho(r):
        v = r.get("spearman_surface")
        return abs(float(v)) if v is not None else 0.0

    worst_lit = max(checked, key=lambda r: r["literal_forward_overlap"])
    worst_mb = max(checked, key=lambda r: r["matched_budget_forward_overlap"])
    worst_rho = max(checked, key=_rho)
    overlap_fires = bool(worst_lit["literal_forward_overlap"] > overlap_limit)
    rho_fires = bool(_rho(worst_rho) > rho_limit)
    dup = overlap_fires or rho_fires
    stop = bool(dup or errors)
    return dict(
        evidence_class="REGISTRY-MEASUREMENT",
        operative_rule="literal-all-rasters: overlap > limit OR |rho| > limit; matched-budget diagnostic only",
        rasters_checked=len(checked), missing_or_invalid=len(errors),
        n_dot_fields=sum(r["representation"] == "dot_field" for r in checked),
        n_continuous_surfaces=sum(r["representation"] == "continuous_surface" for r in checked),
        worst_literal_forward_overlap=float(worst_lit["literal_forward_overlap"]),
        worst_literal_file=worst_lit.get("file"),
        worst_matched_budget_forward_overlap=float(worst_mb["matched_budget_forward_overlap"]),
        worst_matched_budget_file=worst_mb.get("file"),
        worst_abs_spearman=_rho(worst_rho), worst_abs_spearman_file=worst_rho.get("file"),
        overlap_limit=overlap_limit, rho_limit=rho_limit,
        duplicate=dup, stop_required=stop,
        verdict=("negative" if stop else "unique"),
        submission_eligible=False,
        literal_reading_fires=overlap_fires,
        note=("Literal overlap and rank correlation are binding for every raster. "
              "Matched-budget overlap is diagnostic only. This summary cannot prove "
              "inventory completeness or authorize a weekly slot."))
