import json
from scripts.render_safe_site import ROOT, render

def test_rejection_output_never_claims_clearance():
    outputs = render()
    for name in ['index.html', 'how-to-submit.html', 'nine-sites.html']:
        page = outputs[ROOT / 'docs' / name]
        assert 'DO NOT SUBMIT' in page
        assert 'OK TO SUBMIT' not in page
    for name in ['current_submission.json', 'readiness.json']:
        doc = json.loads(outputs[ROOT / 'docs/downloads' / name])
        assert doc['submission_eligible'] is False
        assert doc['verdict'] == 'negative'

def test_old_renderer_cannot_restore_promoted_pages():
    from scripts import render_site_v3
    assert render_site_v3.render() == render()
