---
name: batch-deps-upgrade
description: Batch all open Dependabot dependency upgrade PRs into a single PR
disable-model-invocation: true
---

Batch all open Dependabot dependency upgrade PRs into a single PR for this repository.

## Step 1: Discover

Run: gh pr list --repo XRPLF/xrpl-py --label dependencies --state open --limit 500 --json number,title,headRefName,body,url

Parse each PR to extract package names and versions. Dependabot PRs come in two formats:

- **Single-package PRs**: title is `bump <pkg> from <old> to <new>` — parse from title
- **Grouped PRs**: title is `bump <pkg1> and <pkg2>` with no versions — parse from PR body, which contains a structured list of package updates with version ranges

If any PR can't be parsed from either title or body, flag it for manual review. Build a table of all proposed upgrades. Report the table to the user before proceeding.

## Step 2: Apply, Validate, and Commit (one dependency at a time)

1. Create a branch from main: `deps/batch-deps-upgrade-YYYY-QN` (use current year and quarter)
2. Check for **dependency conflicts** before upgrading. For each proposed upgrade, review `pyproject.toml` constraints and run `poetry show <pkg>` to check if any other dependency pins a version range that would block the upgrade. Mark conflicts as Skipped (dependency conflict: <details>) and do not attempt them.

### For each remaining dependency, repeat the following cycle:

#### 2a. Apply the single upgrade

1. Determine if the dep is direct or transitive:
   - **Direct deps** (listed in `pyproject.toml` under `[tool.poetry.dependencies]` or `[tool.poetry.group.dev.dependencies]`): update the version constraint in `pyproject.toml` to the new version using caret (`^<new_version>`), then run `poetry update <pkg>`. Always update `pyproject.toml` for direct deps — even if the current constraint already allows the new version — so the pinned minimum stays current.
   - **Transitive deps** (not in `pyproject.toml`): run `poetry update <pkg>` to update within the existing constraint range
2. Run `poetry lock` to regenerate `poetry.lock`. **Do NOT delete `poetry.lock` and regenerate from scratch** — this can change dependency resolution and break builds even when no versions changed.
3. Run `poetry install` to sync the virtual environment.
4. Diff `pyproject.toml` and `poetry.lock` against the previous state to confirm the version actually changed. If the version was already current or newer, classify the PR as No-op and move on to the next dependency.

#### 2b. Run per-dependency validation (current Python only)

Run the following on the **current Python version** only (not the full matrix — that happens in Step 3 after all upgrades). Lint and type-check are also deferred to Step 3 since CI only runs them on Python 3.10.

1. **Unit tests**:
   ```bash
   poetry run poe test_unit
   poetry run coverage report --fail-under=85
   ```

2. **Integration tests** (requires a running xrpld Docker container — see Step 3 for container setup):
   ```bash
   poetry run poe test_integration
   poetry run coverage report --fail-under=70
   ```

If any step fails:

- **Attempt to fix** the breaking change with code modifications before rolling back (see Step 3 for common fix patterns).
- If the fix requires a large-scale migration or is blocked by an external constraint, **roll back** the single upgrade (`git checkout -- pyproject.toml poetry.lock` and re-run `poetry install`), mark it as Skipped, and move on.

#### 2c. Pause for user review

If the upgrade changes the public API of the library (new errors, changed return types, removed functionality), add an entry under `## [Unreleased]` in `CHANGELOG.md`.

Then **pause and wait for the user** to review the changes and make a commit before proceeding to the next dependency. Suggest a commit message: `chore(deps): upgrade <pkg> from <old> to <new>`.

### After all dependencies are processed

Verify completeness: every PR from Step 1 must have a status (Upgraded, No-op, or Skipped). If any PR is unaccounted for, stop and report it.

## Step 3: Full matrix validation (after all upgrades are committed)

After all dependencies have been processed and committed individually in Step 2, run the **full validation suite across all Python versions** to catch any cross-version issues.

### Determine Python versions

Read each workflow file under `.github/workflows/` to determine the Python versions used:

- `.github/workflows/unit_test.yml` — the `unit-test` job uses a matrix of Python versions; the `lint-and-type-check` job uses a single Python version (not a matrix)
- `.github/workflows/integration_test.yml` — the `integration-test` job uses a matrix of Python versions
- `.github/workflows/faucet_test.yml` — the `faucet-test` job uses a matrix of Python versions

Extract the exact Python versions from each workflow's `matrix.python-version` array (or the `PYTHON_VERSION` env var for lint). These versions are the source of truth for validation.

### Switching between Python versions

To switch Python versions for testing, use `pyenv` and `poetry`:

```bash
pyenv install <version>    # install if not already present
pyenv local <version>      # set the local Python version
poetry env use python<version>  # point poetry to the correct interpreter
poetry install             # reinstall deps for this interpreter
```

Replace `<version>` with the target version (e.g. `3.10`, `3.11`, `3.12`, `3.13`, `3.14`). After running all tests for one version, repeat these steps to switch to the next.

### Validation order

Run validation **in parallel across all Python versions** from the unit test matrix to speed things up. For each Python version, create a separate working directory (e.g. using `git worktree` or by spawning parallel agents) so that each version's virtual environment does not interfere with the others.

For each Python version, run the following in order:

1. **Lint and type-check** (only on the single lint Python version from the `lint-and-type-check` job):

   ```bash
   poetry run poe lint
   poetry run mypy --strict --implicit-reexport xrpl
   ```

2. **Unit tests**:

   ```bash
   poetry run poe test_unit
   poetry run coverage report --fail-under=85
   ```

3. **Integration tests** (requires a single shared xrpld Docker container — start it once before running integration tests for any Python version):
   - Pre-run cleanup: `docker rm -f xrpld-service 2>/dev/null || true`
   - Start the container:
     ```bash
     docker run \
       --detach \
       --publish 5005:5005 \
       --publish 6006:6006 \
       --volume "$PWD/.ci-config/:/etc/opt/xrpld/" \
       --name xrpld-service \
       rippleci/xrpld:develop --standalone
     ```
   - Wait for port 6006 with a bounded timeout:
     ```bash
     SECONDS=0
     until nc -z localhost 6006 || [ $SECONDS -gt 120 ]; do sleep 2; done
     if ! nc -z localhost 6006; then
       echo "Error: xrpld did not start within 120s"
       docker logs xrpld-service
       exit 1
     fi
     ```
   - Run for each Python version:
     ```bash
     poetry run poe test_integration
     poetry run coverage report --fail-under=70
     ```
   - Stop container after all versions complete: `docker logs xrpld-service && docker stop xrpld-service`

4. **Faucet tests**:
   ```bash
   poetry run poe test_faucet
   ```

Collect results from all parallel runs. All Python versions must pass.

### Handling failures

If any step fails, **attempt to fix the breaking change with code modifications before rolling back**. Common patterns:

- **Type annotation changes**: newer versions of type stubs or mypy may require updated annotations. Fix the annotations.
- **Deprecated API removals**: if an upgraded dependency removes a previously deprecated function, update calls to use the replacement API.
- **Import path changes**: some packages reorganize their module structure on major bumps. Update import statements.
- **Test compatibility**: if a test utility changes behavior (e.g., aiounittest, coverage), update test configuration or code accordingly.

Only roll back and mark as Skipped if:

- The fix requires a large-scale migration across the codebase
- The upgrade is blocked by an external dependency constraint you cannot update

If a failure is traced to a specific dependency upgrade, revert that commit, mark it as Skipped, and re-run validation until green.

## Step 4: Generate Outputs (incremental)

Build the following output files **incrementally** — update them after each dependency is processed in Step 2, so the user can see cumulative progress at any point.

### 4a. Code changes note (updated after each upgrade)

Append to `.claude/skills/batch-deps-upgrade/code-changes.md` after each dependency that required non-`pyproject.toml` source code changes. Each entry should document what broke, why, and the minimal fix applied.

### 4b. Per-dependency report (after each upgrade)

After each dependency is processed (upgraded, no-op, or skipped), report to the user:

- Package name and version change (old → new)
- Status: Upgraded, No-op, or Skipped (with reason)
- If Upgraded: summary of any code changes required to fix breakage
- Running tally of progress (e.g., "3/12 dependencies processed")

### 4c. PR description (updated after each upgrade)

Maintain `.claude/skills/batch-deps-upgrade/pr-description.md` and update it after each dependency, following the repo's PR template (`.github/pull_request_template.md`):

- For "High Level Overview of Change", summarize the batch upgrade.
- For "Context of Change", explain that this batches Dependabot PRs to reduce merge noise. Note that each upgrade was applied and validated individually.
- For "Type of Change", determine dynamically:
  - Check "Breaking change" ONLY if any upgrade visibly changes the library's public API (e.g., error messages, return types, removed functions). This aligns with whether a `CHANGELOG.md` entry was added during Step 2c.
  - Otherwise, do not check any Type of Change — dependency upgrades are maintenance and don't fit "Refactor" (which means restructuring code without behavior change). Note in the PR body that the upgrade is maintenance.
- For "Did you update CHANGELOG.md?", check "Yes" if an entry was added, otherwise check "No, this change does not impact library users".
- Include a "Superseded Dependabot PRs" section with a table: PR (linked), Package, From, To, Status, MajorVersionUpgrade
  - Status values: Upgraded, No-op (reason), Skipped (dependency conflict / CI failure: error)
  - MajorVersionUpgrade: `No` if the major version number did not change. Otherwise `Yes` plus a link for each major version crossed. For example, 1.x → 3.x yields `Yes ([v2](url), [v3](url))`. Each link should point to the package's release notes or changelog for that major version. Verify each link returns HTTP 200 and has meaningful content (e.g., `curl -sL -o /dev/null -w "%{http_code}" <url>`); if a package doesn't publish per-version GitHub releases, fall back to the CHANGELOG file or the closest valid release tag.
- Closing instructions with two paragraphs:
  1. "After merging, close the following superseded PRs (Skipped ones remain open for future handling): #X, #Y, #Z" — list only Upgraded and No-op PRs.
  2. "The following PRs were Skipped and should remain open: #A (package-a), #B (package-b), ..." — annotate each with the package name. These stay open so Dependabot keeps rebasing them.
