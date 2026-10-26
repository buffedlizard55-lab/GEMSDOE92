# Frozen audit-source archive

`audit_readiness_20261025.py` is an exact byte-for-byte copy of the rejection-audit implementation used by the earlier `session_78db3076_final.json` and the pre-fix 2026-10-26 review card. SHA-256: `297d0489b88824fc64bf565ac832b14f305f6dcc8986c65f72f6d448d6fad8c6`.

It is retained solely to verify those historical run-card input hashes. It is **not** imported, executed, or maintained as a private runtime fork. The active shared implementation is `scripts/audit_readiness.py`; its rejection-only counter behavior is covered by `tests/test_readiness_audit.py::test_rejection_audit_does_not_inherit_readiness_activity`.
