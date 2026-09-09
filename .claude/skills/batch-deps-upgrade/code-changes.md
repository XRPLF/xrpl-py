# Code changes — Q3 2026 batch dependency upgrade

No non-`pyproject.toml`/`poetry.lock` source code changes were required for this batch.

All five upgraded packages (`idna`, `urllib3`, `poethepoet`, `websockets`, `pydoclint`) were
validated against the full CI matrix (Python 3.10, 3.11, 3.12, 3.13, 3.14) with lint,
type-check, unit tests (with coverage), integration tests, and faucet tests, and none of them
required any change to `xrpl/` or `tests/` source. In particular:

- `websockets` 15.0.1 → 16.1.1 (major version bump) only touches the two modules xrpl-py
  imports (`websockets.asyncio.client`, `websockets.protocol.State`) via
  `xrpl/asyncio/clients/websocket_base.py`. The only backwards-incompatible note in the 16.0
  changelog is dropping support for Python 3.9 (xrpl-py's minimum is already 3.10), so no
  code changes were needed.
- `pydoclint` 0.7.6 → 0.8.7 and `poethepoet` 0.37.0 → 0.45.0 are dev-only lint/task-runner
  tools; `poetry run poe lint` and `poetry run mypy --strict --implicit-reexport xrpl` both
  pass unchanged.
- `idna` 3.10 → 3.19 and `urllib3` 2.6.3 → 2.7.0 are transitive dependencies (pulled in via
  `httpx`/`requests`); no direct usage in xrpl-py.

## Pre-existing, unrelated failure noted during validation

While running unit tests on Python 3.14, three pre-existing test failures were observed:

- `tests/unit/models/test_base_model.py::TestBaseModel::test_bad_type`
- `tests/unit/models/test_base_model.py::TestBaseModel::test_bad_type_flags`
- `tests/unit/models/transactions/test_loan_broker_cover_clawback.py::TestLoanBrokerCoverClawback::test_invalid_xrp_amount`

These fail because Python 3.14 changed how `typing.Union[...]` reprs itself (it now renders
using `X | Y` PEP 604 syntax instead of `typing.Union[X, Y]`), and `xrpl/models/base_model.py`
embeds the `repr()` of the expected type directly into its validation error messages, which
these tests assert against verbatim.

This was verified to be **pre-existing on `main`** (reproduced with Python 3.14 and no
dependency changes applied) and is **unrelated to any of the five packages upgraded in this
batch**. Fixing it would mean auditing/updating `xrpl/models/base_model.py`'s error-message
formatting for Python 3.14's typing repr changes and updating three test assertions — a
correctness fix for the library's Python 3.14 support that is out of scope for a dependency
version bump. It is called out here for visibility and left unfixed; recommend a separate
ticket to address Python 3.14 typing-repr compatibility in `base_model.py`.

## Local validation infrastructure note (not part of the PR)

The CI-pinned integration-test image (`ghcr.io/ckeshava/xrpld-batch-v1_1:latest`, referenced
in `.github/workflows/integration_test.yml` with a comment noting it's a temporary pin) fails
to start locally with the repo's current `.ci-config/xrpld.cfg`, which now enables the
`Sponsor` feature:

```
terminate called after throwing an instance of 'std::runtime_error'
  what():  Unknown feature: Sponsor  in config file.
```

This is a pre-existing mismatch between that pinned image and the current `.ci-config`, not
caused by this batch. Local validation instead used `rippleci/xrpld:develop`, which starts
cleanly and supports the `Sponsor` feature; the full integration suite passed with it. Worth
flagging to the team separately — the pinned image may need to be refreshed or CI could
currently be failing/flaky for the same reason.
