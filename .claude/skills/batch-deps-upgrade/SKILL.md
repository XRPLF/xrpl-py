---
name: batch-deps-upgrade
description: Batch all open Dependabot dependency upgrade PRs into a single PR, plus any further upgrades needed to resolve open Semgrep JIRA tickets that a package upgrade can fix
disable-model-invocation: true
---

Batch all open Dependabot dependency upgrade PRs into a single PR for this repository, **plus any further upgrades needed to resolve the open Semgrep JIRA tickets that a package upgrade can fix**.

**Scope — only tickets a package upgrade can fix:** ones naming a vulnerable dependency and a version that fixes it.

Within that scope, the two inputs are independent. Every in-scope ticket gets fixed whether or not a Dependabot PR happens to propose that upgrade. Where no open Dependabot PR covers an impacted package, this PR adds the upgrade itself.

**Two modes — decide which before doing anything else.** The invocation argument arrives as `ARGUMENTS`:

- **empty** (`/batch-deps-upgrade`) — run Steps 1-4, then **stop**. Do not continue into "Closing run" even though it appears further down; this mode writes nothing to JIRA or GitHub, only the working tree and local files.
- **`close`** (`/batch-deps-upgrade close`) — run **only** "Closing run" at the bottom. No discovery, no branch, no install, no tests. Normally used after the batch PR merges.
- **anything else** — stop and ask which was meant. Do not guess.

Requires `gh auth login` and, for the Semgrep parts, the Atlassian MCP.

## Step 1: Discover

Run: gh pr list --repo XRPLF/xrpl-py --label dependencies --state open --limit 500 --json number,title,headRefName,body,url

Parse each PR to extract package names and versions. Dependabot PRs come in two formats:

- **Single-package PRs**: title is `bump <pkg> from <old> to <new>` — parse from title
- **Grouped PRs**: title is `bump <pkg1> and <pkg2>` with no versions — parse from PR body, which contains a structured list of package updates with version ranges

If any PR can't be parsed from either title or body, flag it for manual review. Build a table of all proposed upgrades. Report the table to the user before proceeding.

Also fetch the Semgrep tickets per **Where the list comes from** under "Semgrep tickets" below, and add them to the same table.

## Step 2: Apply all upgrades

1. Create a branch from main: `deps/batch-deps-upgrade-YYYY-QN` (use current year and quarter)
2. Check for **dependency conflicts** before upgrading. For each proposed upgrade, review `pyproject.toml` constraints and run `poetry show <pkg>` to check if any other dependency pins a version range that would block the upgrade. Mark conflicts as Skipped (dependency conflict: <details>) and do not attempt them.
3. For each remaining upgrade, apply it:
   - **Direct deps** (listed in `pyproject.toml` under `[tool.poetry.dependencies]` or `[tool.poetry.group.dev.dependencies]`): update the version constraint in `pyproject.toml` to the new version using caret (`^<new_version>`), then run `poetry update <pkg>`. Always update `pyproject.toml` for direct deps — even if the current constraint already allows the new version — so the pinned minimum stays current.
   - **Transitive deps** (not in `pyproject.toml`): run `poetry update <pkg>` to update within the existing constraint range.
   - Never hand-edit `poetry.lock` to force a version, and never loosen a direct dependency's constraint just to let the resolver pick a transitive version it wouldn't otherwise choose — that risks resolving to a combination no maintainer has tested together.
   - When `poetry update <pkg>` can't reach the target version, find the parent constraining it (`poetry show <pkg>` lists "required by"). If that parent is a **direct** dep we declare in `pyproject.toml`, bumping *it* is an ordinary upgrade rather than a workaround — try that, even across a major version, and let Step 3 validate. Nothing else will surface it: a security ticket names the vulnerable transitive package, never the parent pinning it, and Dependabot may have no PR open for the parent. Mark Skipped only when the blocker is itself transitive (not something we declare), or when bumping the parent fails validation.
4. After all upgrades are applied, run `poetry lock` to regenerate `poetry.lock`. **Do NOT delete `poetry.lock` and regenerate from scratch**.
5. Run `poetry install` to sync the virtual environment.
6. Diff `pyproject.toml` and `poetry.lock` against main to classify each Dependabot PR **and each Semgrep ticket** as:
   - Upgraded: version changed
   - No-op: version was already current or newer

   For tickets, see **Picking the target and matching results** under "Semgrep tickets" below — several tickets can share one install, and the match is per ticket.
7. If any upgrade changes the public API of the library (new errors, changed return types, removed functionality) and results in a breaking change, add an entry under `## [Unreleased]` in `CHANGELOG.md`.
8. Verify completeness: every PR and every ticket from Step 1 must have a status (Upgraded, No-op, or Skipped). If any is unaccounted for, stop and report it before proceeding.

## Step 3: Validate

Run the **full validation suite across all Python versions** from the CI matrix. Repeat until everything passes.

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
       --volume "$PWD/.ci-config/:/etc/xrpld/" \
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

If a failure is traced to a specific dependency upgrade, revert that upgrade in `pyproject.toml`, re-run `poetry lock && poetry install`, mark it as Skipped, and re-run validation until green.

## Step 4: Generate Outputs

Do NOT commit or create a PR. Instead, generate the following outputs for the human to use.

**Formatting for every generated markdown file:** one line per paragraph and one line per list item — never hard-wrap prose mid-sentence. Editors soft-wrap it anyway, and mid-paragraph breaks make later diffs noisy. Blank line between blocks, no trailing whitespace.

1. **Code changes note** — write `.claude/skills/batch-deps-upgrade/code-changes.md` documenting every non-`pyproject.toml` source code change, explaining what broke, why, and the minimal fix applied.

2. **Commit message** — output a concise commit message the human can copy-paste into `git commit -m "..."`. Format: `chore(deps): quarterly batch dependency upgrade YYYY-QN` followed by a brief summary of upgrades, skips, and removals.

3. **PR description** — write `.claude/skills/batch-deps-upgrade/pr-description.md` following the repo's PR template (`.github/pull_request_template.md`):
   - For "High Level Overview of Change", summarize the batch upgrade.
   - For "Context of Change", explain that this batches Dependabot PRs (and any Semgrep-driven upgrades) to reduce merge noise and close outstanding security tickets.
   - For "Type of Change", determine dynamically:
     - Check "Breaking change" ONLY if any upgrade visibly changes the library's public API (e.g., error messages, return types, removed functions). This aligns with whether a `CHANGELOG.md` entry was added in Step 2.7.
     - Otherwise, do not check any Type of Change — dependency upgrades are maintenance and don't fit "Refactor" (which means restructuring code without behavior change). Note in the PR body that the upgrade is maintenance.
   - For "Did you update CHANGELOG.md?", check "Yes" if an entry was added, otherwise check "No, this change does not impact library users".
   - Include a "Superseded Dependabot PRs" section with a table: PR (linked), Package, From, Asked for, Resolved, Status, MajorVersionUpgrade. The **Semgrep tickets** table uses these same columns, with the first headed `Ticket` — one shape for both artifacts.
     - `From` is the version on `main`; `Asked for` is what the PR proposed or the ticket requires (`≥ x.y.z`); `Resolved` is what `poetry.lock` actually holds after the batch. Keep them in separate columns: the three routinely differ (a PR proposing 4.1.0 can resolve to 4.2.1), and burying the real version in Status prose makes the table unverifiable.
     - Status values: Upgraded, No-op (reason), Skipped (dependency conflict / CI failure: error) — a status and its reason, never a version number.
     - MajorVersionUpgrade: `No` if the major version number did not change. Otherwise `Yes` plus a link for each major version crossed. For example, 1.x → 3.x yields `Yes ([v2](url), [v3](url))`. Each link should point to the package's release notes or changelog for that major version. Verify each link returns HTTP 200 and has meaningful content (e.g., `curl -sL -o /dev/null -w "%{http_code}" <url>`); if a package doesn't publish per-version GitHub releases, fall back to the CHANGELOG file or the closest valid release tag.
   - For every **major version upgrade**, add a "Major version upgrade notes" section below the table. For each major-version package, include:
     - A link to the release notes
     - A brief summary of key changes (breaking changes, deprecations, new features)
     - An explanation of why no code changes were required, OR a summary of the code changes that were made. This helps reviewers understand the impact without having to read the full release notes themselves.
   - Closing instructions with two paragraphs:
     1. "After merging, run `/batch-deps-upgrade close` to close the superseded PRs and the resolved Semgrep tickets." Follow it with the list of Upgraded and No-op PRs (#X, #Y, #Z) as a record, so the PR documents what will be closed even if the skill isn't used.
     2. "The following PRs were Skipped and should remain open: #A (package-a), #B (package-b), ..." — annotate each with the package name. These stay open so Dependabot keeps rebasing them.
   - Include a **"Semgrep tickets"** table with the same columns, the first headed `Ticket`. Status alone cannot be verified against `main`, so `Asked for` and `Resolved` must be their own columns. Because `close-list.md` is not committed, this table is the closing run's fallback.
   - Give ticket-driven upgrades that no Dependabot PR proposed their own table naming the motivating ticket — they are additions, not supersessions.
   - Call out separately, in the overview, any **major** bump taken to unblock a ticket: no PR or ticket asked for it, so a reviewer will not be expecting it and must see it flagged rather than buried in a table.

4. **Close list** — write `.claude/skills/batch-deps-upgrade/close-list.md` recording every ticket and Dependabot PR the batch makes closable. This is the input to the closing run.

   1. **Close** — every Upgraded and No-op ticket and PR, in one shape for both so a single parser handles them:

      ```
      <ticket-key or #pr> | <package> | installed <resolved> (<asked for>) | Comment: "<text>"
      ```

      The third field must carry the **resolved** version, not the proposed one — that is what step 1 of the closing run checks against `main`, and a proposed version cannot be verified.

      Every comment must reference the batch PR, which does not exist yet at this point. Write that reference as the literal token `<PR>`; the closing run substitutes the merged PR's URL. Use a URL rather than `#1234`, which JIRA renders as plain text.
   2. **Left open** — every Skipped one, with its reason. Each is a security fix that did not land, so this is worth reading. Skipped PRs stay open for Dependabot to keep rebasing.

   **Do NOT commit `close-list.md`** — local scratch, like `code-changes.md` and `pr-description.md`. That is why the PR body must carry the same lists (item 3): it is the closing run's fallback when this file is gone.

## Semgrep tickets

Treat each in-scope ticket as one more row in Step 1's table: a package plus a target version, carried through Steps 1-4 and classified Upgraded / No-op / Skipped like any Dependabot PR. Only the differences are below.

### Where the list comes from (Step 1)

Fetch open tickets via the Atlassian MCP:

```
parent = DGE-3869 AND project = DGE
AND status IN ("To Do", "in review", Blocked, "In Progress")
AND created >= "2022-01-01"
AND textfields ~ "xrpl-py"
ORDER BY rank
```

**Take the package name from the summary, not the description** — a description may list several packages sharing one advisory, so it picks the wrong one. Take the fix version, severity and CVE/GHSA link from the description. Wording varies, so read for intent rather than matching labels literally.

Keep tickets naming a package and a fix version; drop the rest — for example, a ticket describing a broad class of finding across many call sites (no single vulnerable dependency or fix version) is out of scope for this skill and needs a human-authored fix. If tickets came back but none of them could be parsed, that is a parsing failure — stop. If the query returned nothing, or nothing was in scope, there is simply no Semgrep work this quarter: record zero and carry on with the Dependabot batch. A ticket becomes a row whether or not a Dependabot PR proposes that package; a ticket is reason enough on its own.

### Picking the target and matching results (Step 2)

Where a ticket and a PR both want the same install, the target is the **highest** version either wants. Three matching rules — get them wrong and you close tickets whose vulnerability is still installed:

- Compare using proper version ordering (e.g. `poetry show <pkg>` or a real version-parsing library), never as strings — lexically `"7.5.9" > "7.5.21"`.
- Check the install the ticket means. A package's installed version may satisfy the ticket's target on a different major line than the ticket was filed against — match the install on the ticket's own major line. If that line is gone because the package moved to a **higher** major, the ticket is satisfied — the vulnerable line is no longer installed — provided the advisory's affected range does not extend into the new major.
- Match per ticket, not per package. Tickets sharing one install can want different versions. Never conclude "we upgraded X, so close the X tickets".

Classify from the Step 2.6 diff, not from which PR did what: a parent bump carries along a dependency it pins exactly, so a ticket can come out Upgraded with no PR naming its package.

Write `close-list.md` — the closing run's input, so keep it parseable, one item per line.

### Non-goal

Never remove a dependency to resolve a finding. A transitive dep leaves only when its parent stops depending on it; a direct dep with no published fix needs whatever imported it rewritten, which belongs in a human-authored PR.

## Closing run (`/batch-deps-upgrade close`)

> **Runs only when `ARGUMENTS` is `close`.** If you reached this section by reading past Step 4 during a default run, stop here — everything below comments on and closes real JIRA tickets and real public PRs.

Runs none of Steps 1-4: no ticket discovery, no bumps, and none of Step 3's build/test chain. That exclusion does **not** cover the per-item check in step 1 below — that one always runs, and it is the safeguard against closing something whose fix was reverted. Read section 1 of `close-list.md`; if it is missing, fall back to the merged PR body's lists. Identify the batch PR from an argument or `gh pr list --repo XRPLF/xrpl-py --state merged --head <branch>`, and replace the `<PR>` token in every comment with its URL. **Check that no comment still contains `<PR>` before posting anything** — if one does, the substitution failed, so stop rather than post a placeholder onto dozens of tickets.

1. **Verify each item against the current `main`** and skip anything not genuinely satisfied — a reviewer may have had an upgrade reverted. This is what makes the run safe whether or not the batch has merged.
2. **Close everything that verified.** Do not ask for approval; the engineer reviewed both lists on the PR, and step 1 is the real check.
   - **JIRA tickets** — resolve the ticket's `Done` transition **before** commenting: query the issue's available transitions and take the one whose destination status is `Done`. Then post the comment and transition. Resolving first avoids the half-state where a ticket is commented on but left open.
   - **Dependabot PRs** — `gh pr close <n> --repo XRPLF/xrpl-py --comment "<comment>"`.
3. Report in this shape:

   ```
   Closed <n> JIRA tickets, <n> Dependabot PRs.

   Skipped — not satisfied on main @ <sha> (<n>):
     <TICKET-KEY>   <pkg> needs <version>, main has <version>
     #<pr-number>   <pkg> <version> never applied (<reason from close-list>)
   ```

   If nothing was skipped, say so rather than omitting the section.
