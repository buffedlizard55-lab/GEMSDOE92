.PHONY: test verify manifest ledger validate clean site render-current

PYTHON ?= python3
REFERENCE ?= data/bridge/sample_submission.tif

test:
	$(PYTHON) -m pytest tests -q

render-current:
	$(PYTHON) scripts/render_public_status.py

site:
	$(PYTHON) scripts/render_public_status.py --check
	PYTHONPATH=vendor $(PYTHON) scripts/check_site.py

manifest:
	$(PYTHON) -m gems manifest --manifest registry/data_manifest.json --data-root data

# Refuses loudly if the parent cannot be proven. This is the gate that stops a
# session before it burns slots on descendants of an unverified parent.
verify:
	$(PYTHON) -m gems parent --recipe registry/parents/R0.json --data-root data

ledger:
	$(PYTHON) -m gems ledger

# make validate FILE=releases/x.tif
validate:
	@test -n "$(FILE)" || (echo "usage: make validate FILE=releases/<id>.tif" && exit 2)
	$(PYTHON) -m gems validate "$(FILE)" --reference "$(REFERENCE)"

clean:
	rm -rf .pytest_cache **/__pycache__ __pycache__
