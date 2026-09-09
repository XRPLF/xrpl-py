## High Level Overview of Change

Batches five open Dependabot dependency-upgrade PRs into a single upgrade of `pyproject.toml`
and `poetry.lock`:

- `idna` 3.10 → 3.19 (transitive)
- `urllib3` 2.6.3 → 2.7.0 (transitive)
- `poethepoet` 0.37.0 → 0.45.0 (direct, dev)
- `websockets` 15.0.1 → 16.1.1 (direct, major version bump)
- `pydoclint` 0.7.6 → 0.8.7 (direct, dev)

No dependency conflicts were found; no source code changes were required (see
`.claude/skills/batch-deps-upgrade/code-changes.md` for full validation notes, including a
pre-existing, unrelated Python 3.14 test issue and a local xrpld Docker image note).

### Context of Change

Five separate Dependabot PRs were open against this repo, each bumping one dependency. Merging
them individually creates redundant CI runs and review overhead, and several of them had
automatic rebases disabled after being open for 30+ days. This PR consolidates all of them
into a single reviewable change and supersedes the individual PRs. This is a routine
maintenance upgrade, not a refactor.

### Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Refactor (non-breaking change that only restructures code)
- [ ] Tests (You added tests for code that already exists, or your new feature included in this PR)
- [ ] Documentation Updates
- [ ] Release

This is a dependency-maintenance change. No Type of Change box is checked: the `websockets`
major-version bump (15 → 16) does not change xrpl-py's own public API (see "Major version
upgrade notes" below), so it doesn't qualify as "Breaking change" for this library's users,
and it isn't a code restructuring, so "Refactor" doesn't apply either.

### Did you update CHANGELOG.md?

- [ ] Yes
- [x] No, this change does not impact library users

## Test Plan

* Unit tests
  * Ran `poetry run poe test_unit` + `poetry run coverage report --fail-under=85` on Python
    3.10, 3.11, 3.12, 3.13, and 3.14 (via parallel git worktrees, one per interpreter). All
    pass on 3.10–3.13. Python 3.14 has 3 pre-existing failures unrelated to this batch (see
    `code-changes.md`).
  * Ran `poetry run poe lint` and `poetry run mypy --strict --implicit-reexport xrpl` on
    Python 3.10 (the CI lint version). Both pass.
* Integration tests
  * Ran `poetry run poe test_integration` + `poetry run coverage report --fail-under=70`
    against a shared standalone xrpld Docker container for all 5 Python versions. All 200
    tests pass (2 skipped) on every version, coverage 73.90% (73.62% on 3.14).
* Other tests
  * Ran `poetry run poe test_faucet` on all 5 Python versions. All pass.

## Superseded Dependabot PRs

| PR | Package | From | To | Status | MajorVersionUpgrade |
|----|---------|------|----|--------|----------------------|
| [#1000](https://github.com/XRPLF/xrpl-py/pull/1000) | idna | 3.10 | 3.19 | Upgraded | No |
| [#998](https://github.com/XRPLF/xrpl-py/pull/998) | urllib3 | 2.6.3 | 2.7.0 | Upgraded | No |
| [#935](https://github.com/XRPLF/xrpl-py/pull/935) | poethepoet | 0.37.0 | 0.45.0 | Upgraded | No |
| [#932](https://github.com/XRPLF/xrpl-py/pull/932) | websockets | 15.0.1 | 16.1.1 | Upgraded | Yes ([v16](https://github.com/python-websockets/websockets/releases/tag/16.0)) |
| [#931](https://github.com/XRPLF/xrpl-py/pull/931) | pydoclint | 0.7.6 | 0.8.7 | Upgraded | No |

All 5 PRs discovered in Step 1 are accounted for above; none were Skipped (no dependency
conflicts or CI failures were attributable to any of the 5 packages).

## Major version upgrade notes

### websockets 15 → 16 ([release notes](https://github.com/python-websockets/websockets/releases/tag/16.0), [changelog](https://websockets.readthedocs.io/en/stable/project/changelog.html))

Key changes in 16.0:
- Backwards-incompatible: drops support for Python 3.9 (websockets 15.0 was the last version
  supporting 3.9). xrpl-py's minimum supported Python version is already 3.10, so this has no
  effect.
- New features: validated compatibility with Python 3.14; added support for free-threaded
  Python; separate `max_size` limits for messages vs. fragments; HTTP/1.0 proxy support;
  customizable close code/reason in `Server.close`.
- Bug fixes: `Connection.recv` no longer returns `bytearray` instead of `bytes` in edge cases;
  fixed a `threading`-implementation race condition on close.

No code changes were required: xrpl-py only imports `websockets.asyncio.client` and
`websockets.protocol.State` (in `xrpl/asyncio/clients/websocket_base.py`), and neither the
public surface of those modules nor their behavior changed in a way that affects xrpl-py. The
full unit, integration, and faucet suites pass unchanged on all 5 supported Python versions
with `websockets` 16.1.1.

## Closing instructions

After merging, close the following superseded PRs (Skipped ones remain open for future
handling): #1000, #998, #935, #932, #931.

No PRs were Skipped in this batch, so there are none that need to remain open.
