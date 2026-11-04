# Batch Dependency Upgrade

Batches all open Dependabot PRs into a single upgrade PR, plus any further upgrades needed to resolve the open Semgrep JIRA tickets that a package upgrade can fix.

Only Semgrep JIRA tickets about a vulnerable dependency are in scope. A ticket with no fix version takes its fix version from the advisory: it's upgraded like any other ticket, closed as No-op when the package is gone or already patched, and left open for a human when no fixed release exists or the advisory has no usable affected range.

The two inputs are independent: every in-scope ticket gets fixed whether or not a Dependabot PR proposes that upgrade — where none does, the batch PR adds it.

## The two commands

Run at different times:

| Command | When | What it touches |
| --- | --- | --- |
| `/batch-deps-upgrade` | building the batch | working tree and local files only |
| `/batch-deps-upgrade close` | after the batch upgrade PR is merged | JIRA tickets and Dependabot PRs |

## Prerequisites

- `gh auth login` — needed to list open Dependabot PRs, read advisories, and download the native mpt-crypto library for the Confidential MPT test
- `pyenv` with the Python versions in the CI matrix (see `.github/workflows/unit_test.yml`), or Docker to run the missing versions in `python:<version>` images
- `poetry` installed; the skill uses the version CI pins (`POETRY_VERSION` in the workflows), installing it into a throwaway virtualenv if yours differs
- Docker daemon running — the skill starts an xrpld container for integration tests
- Atlassian MCP available — needed to read the Semgrep tickets and later comment on and close them

## `/batch-deps-upgrade` — build the batch

From the xrpl-py repo root, start a new Claude Code session and run:

```
/batch-deps-upgrade
```

It discovers the open Dependabot PRs and Semgrep tickets, applies the upgrades to `pyproject.toml`, runs `poetry lock` and `poetry install`, validates with lint, type-check, unit tests, integration tests, the Confidential MPT test, and faucet tests across all CI Python versions, and writes `code-changes.md`, `pr-description.md` and `close-list.md` plus a commit message. It creates the branch but does not commit, and writes nothing outside the repo.

Then, by hand:

1. Review the changes and generated files. Ask Claude questions about specific changes if they don't make sense — the code changes may need multiple rounds of discussion and correction before they're ready.
2. Stage and commit using the suggested commit message. Do **not** commit the generated markdown files, `close-list.md` included — they're local scratch.
3. Push and open a PR using the generated PR description. Its "Semgrep tickets" and "Superseded Dependabot PRs" sections are the durable record of what gets closed later.
4. Get the PR reviewed and merged.

### Python version testing

The skill reads the CI workflow files to determine which Python versions and jobs to test. It uses `pyenv` and `poetry env use` to switch between versions (or `python:<version>` Docker images when a version isn't installed), matching the CI matrix exactly. Lint, type-check and the Confidential MPT test run on a single version; unit, integration and faucet tests run across the full matrix. Integration tests run one version at a time, since they share one xrpld node.

Faucet tests matter more than they look: CI runs them only after merge, so the skill's local run is the only faucet check before the PR lands.

## `/batch-deps-upgrade close` — close what the batch superseded

Once the batch upgrade PR is merged, run this from the same working tree if you still have it — it reads `close-list.md`, falling back to the merged PR body if that file is gone:

```
/batch-deps-upgrade close
```

It re-verifies every item against `main` before acting, then comments on and closes the resolved Semgrep tickets and the superseded Dependabot PRs, and reports anything it skipped. Skipped Dependabot PRs are left open so Dependabot keeps rebasing them.

Afterwards, read the "Left open" section of `close-list.md` — each entry is a security fix that didn't land, with its reason. Expect one of: the package holding it back is already at its own latest version, so there is no upgrade left to take and it needs replacing instead; the blocker is a transitive dependency we don't declare; or the unblocking bump failed validation and was rolled back. All three need a human-authored PR.
