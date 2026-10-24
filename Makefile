.PHONY: test verify manifest ledger validate clean site

# Prefer the project's ignored virtual environment when it exists, but honor
# an explicit `PYTHON=...` override and retain system Python as the fallback.
PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

test:
	$(PYTHON) -m pytest tests -q

site:
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
	$(PYTHON) -m gems validate "$(FILE)" --reference $(REFERENCE)

clean:
	rm -rf .pytest_cache **/__pycache__ __pycache__
