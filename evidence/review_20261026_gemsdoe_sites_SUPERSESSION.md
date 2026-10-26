# Supersession record — 2026-10-26 rejection-only site audit

The original file [`review_20261026_gemsdoe_sites_run_card.json`](review_20261026_gemsdoe_sites_run_card.json) is retained byte-for-byte as a historical receipt, but it is **superseded and must not be used for activity counters**. Its SHA-256 is `3412ad97665389aaa15a61399541d7270f3066f56ad47cba4c75fecdcc582e13`.

The pre-fix generator copied `new_unique_tiff_generated` and `experiments_this_session` from the current readiness/status card into an audit whose scope was rejection-only. Consequently, that JSON incorrectly records `true` and `3`; those values refer to an earlier VARIO research artifact/session, not to this audit. No new GeoTIFF or experiment was created by the audit.

The generator was corrected to write the audit's own activity explicitly as `new_unique_tiff_generated=false`, `experiments=0`, and `weekly_slots_used=0`. Regression coverage is in `tests/test_readiness_audit.py::test_rejection_audit_does_not_inherit_readiness_activity`. The replacement receipt is [`review_20261026_gemsdoe_sites_run_card_v2.json`](review_20261026_gemsdoe_sites_run_card_v2.json), SHA-256 `2087366ff0dfb0b54cf18c50020f0ab6268c2e11cfe9f503996288dfc464f7bf`. The v2 card remains rejection-only, records the pinned literal overlap stop, and cannot grant submission clearance.

Do not rewrite the old card to make it look correct after the fact. Use v2 for the corrected evidence; keep this note adjacent to v1 whenever the historical file is retained or published.
