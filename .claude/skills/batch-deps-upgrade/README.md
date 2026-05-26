# Batch Dependency Upgrade

Batches all open Dependabot PRs into a single upgrade PR.

## Prerequisites

- `pyenv` installed with Python versions matching the CI matrix (see `.github/workflows/unit_test.yml`)
- `poetry` installed (the project uses Poetry for dependency management)
- Docker daemon running — the skill starts a rippled container for integration tests

## Usage

From the xrpl-py repo root, start a new Claude Code session and run:

```
/batch-deps-upgrade
```

## What it does

1. Discovers all open Dependabot PRs via `gh pr list`
2. Applies upgrades to `pyproject.toml`, runs `poetry lock` and `poetry install`
3. Validates with lint, type-check, unit tests, integration tests, and faucet tests across all CI Python versions
4. Generates output files and a commit message for the human to use

## Python version testing

The skill reads the CI workflow files to determine which Python versions to test against. It uses `pyenv` and `poetry env use` to switch between versions, matching the CI matrix exactly. Lint and type-check run on a single version; unit, integration, and faucet tests run across the full matrix.

## After it finishes

1. Review the changes and generated files. Ask Claude questions about specific changes if they don't make sense — the code changes may need multiple rounds of discussion and correction before they're ready.
2. Stage and commit using the suggested commit message (the skill already creates a branch)
3. Push and open a PR using the generated PR description
4. After merge, close the superseded Dependabot PRs listed in the description
