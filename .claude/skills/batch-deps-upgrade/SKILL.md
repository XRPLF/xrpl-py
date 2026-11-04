---
name: batch-deps-upgrade
description: Batch all open Dependabot dependency upgrade PRs into a single PR, plus any further upgrades needed to resolve open Semgrep JIRA tickets that a package upgrade can fix
disable-model-invocation: true
---

Batch all open Dependabot dependency upgrade PRs into a single PR for this repository, **plus any further upgrades needed to resolve the open Semgrep JIRA tickets that a package upgrade can fix**.

**Scope — only tickets about a vulnerable dependency:** ones naming the package, with or without a fix version. Code and configuration findings are out of scope.

Within that scope, the two inputs are independent. Every in-scope ticket gets fixed whether or not a Dependabot PR happens to propose that upgrade. Where no open Dependabot PR covers an impacted package, this PR adds the upgrade itself.

**Two modes — decide which before doing anything else.** The invocation argument arrives as `ARGUMENTS`:

- **empty** (`/batch-deps-upgrade`) — run Steps 1-4, then **stop**. Do not continue into "Closing run" even though it appears further down; this mode writes nothing to JIRA or GitHub, only the working tree and local files.
- **`close`** (`/batch-deps-upgrade close`) — run **only** "Closing run" at the bottom. No discovery, no branch, no install, no tests. Normally used after the batch PR merges.
- **anything else** — stop and ask which was meant. Do not guess.

Requires `gh auth login` and, for the Semgrep parts, the Atlassian MCP.

## Step 1: Discover

Run: gh pr list --repo XRPLF/xrpl-py --label dependencies --state open --limit 500 --json number,title,headRefName,body,url

Parse each PR to extract package names and versions. Dependabot PRs come in two formats:

- **Single-package PRs**: title is `chore(deps): bump <pkg> from <old> to <new>` (`chore(deps-dev):` for dev dependencies) — parse from title
- **Grouped PRs**: title is `bump <pkg1> and <pkg2>` with no versions — parse from PR body, which contains a structured list of package updates with version ranges

Two open PRs can propose the same package (Dependabot opens a new one when a newer release appears before the older PR is closed). Treat them as one upgrade to the highest proposed version, but keep a row for each PR.

If any PR can't be parsed from either title or body, flag it for manual review. Build a table of all proposed upgrades. Report the table to the user before proceeding.

Also fetch the Semgrep tickets per **Where the list comes from** under "Semgrep tickets" below, and add them to the same table.

## Step 2: Apply all upgrades

**Poetry setup, before running any `poetry` command:**

- Use the Poetry version CI uses, `POETRY_VERSION` in `.github/workflows/unit_test.yml`, so the `poetry.lock` header matches what CI writes. Check `poetry --version`; if it differs, install that version in a throwaway virtualenv (`python3 -m venv /tmp/poetry-<ver> && /tmp/poetry-<ver>/bin/pip install poetry==<ver>`) and put its `bin/` first on `PATH` — not just call that binary — because the `lint` poe task runs `poetry run` itself and would otherwise pick up the other Poetry.
- Run every Poetry command with `VIRTUAL_ENV` unset (`env -u VIRTUAL_ENV poetry ...`). If the shell exports `VIRTUAL_ENV`, Poetry installs into that interpreter instead of the project's `.venv` (`poetry.toml` sets `in-project = true`), which pollutes a shared environment.

1. Create a branch from main: `deps/batch-deps-upgrade-YYYY-QN` (use current year and quarter)
2. Check for **dependency conflicts** before upgrading. For each proposed upgrade, review `pyproject.toml` constraints and run `poetry show <pkg>` to check if any other dependency pins a version range that would block the upgrade. Mark conflicts as Skipped (dependency conflict: <details>) and do not attempt them.
3. For each remaining upgrade, apply it:
   - **Direct deps** (listed in `pyproject.toml` under `[tool.poetry.dependencies]` or `[tool.poetry.group.dev.dependencies]`): update the version constraint in `pyproject.toml` to the new version using caret (`^<new_version>`), then run `poetry update <pkg>`. Always update `pyproject.toml` for direct deps — even if the current constraint already allows the new version — so the pinned minimum stays current.
   - **Transitive deps** (not in `pyproject.toml`): run `poetry update <pkg>` to update within the existing constraint range.
   - Never hand-edit `poetry.lock` to force a version, and never loosen a direct dependency's constraint just to let the resolver pick a transitive version it wouldn't otherwise choose — that risks resolving to a combination no maintainer has tested together.
   - When `poetry update <pkg>` can't reach the target version, find the parent constraining it (`poetry show <pkg>` lists "required by"). If that parent is a **direct** dep we declare in `pyproject.toml`, bumping *it* is an ordinary upgrade rather than a workaround — try that, even across a major version, and let Step 3 validate. Nothing else will surface it: a security ticket names the vulnerable transitive package, never the parent pinning it, and Dependabot may have no PR open for the parent. Mark Skipped only when the blocker is itself transitive (not something we declare), or when bumping the parent fails validation.
4. After all upgrades are applied, run `poetry lock` to regenerate `poetry.lock`. **Do NOT delete `poetry.lock` and regenerate from scratch**.

   xrpl-py supports every Python in `python = ">=3.10,<4.0"`, so the lock must resolve for all of them. When a package's newest release needs a newer Python than 3.10, Poetry may lock two versions split by a `python_version` marker (e.g. `flake8 7.4.1` for `< "3.15"`, `7.5.0` for `>= "3.15"`). That is expected, not a conflict. Classify by the entry the CI matrix versions use, and note the split in the PR description.
5. Run `poetry install` to sync the virtual environment.
6. Diff `pyproject.toml` and `poetry.lock` against main to classify each Dependabot PR **and each Semgrep ticket** as:
   - Upgraded: version changed
   - No-op: version was already current or newer

   For tickets, see **Picking the target and matching results** under "Semgrep tickets" below — several tickets can share one install, and the match is per ticket.
7. If any upgrade changes the public API of the library (new errors, changed return types, removed functionality) and results in a breaking change, add an entry under `## [Unreleased]` in `CHANGELOG.md`.
8. Verify completeness: every PR and every ticket from Step 1 must have a status (Upgraded, No-op, or Skipped). If any is unaccounted for, stop and report it before proceeding.

## Step 3: Validate

Run the **full validation suite across all Python versions** from the CI matrix. Repeat until everything passes.

### Determine Python versions and jobs

Read each workflow file under `.github/workflows/` to determine the Python versions and jobs CI runs. These are the source of truth for validation; re-read them every run, since jobs get added.

- `.github/workflows/unit_test.yml` — the `unit-test` job uses a matrix of Python versions; the `lint-and-type-check` job uses a single Python version (`PYTHON_VERSION`)
- `.github/workflows/integration_test.yml` — the `integration-test` job uses a matrix of Python versions; the `confidential-integration-test` job uses a single Python version and builds the native Confidential MPT extension
- `.github/workflows/faucet_test.yml` — the `faucet-test` job uses a matrix of Python versions

Also read `POETRY_VERSION` from the workflows (see Step 2's Poetry setup).

### Getting each Python version

Each Python version needs its own interpreter and its own virtualenv. Use `pyenv` and Poetry:

```bash
pyenv install <version>                          # install if not already present
env -u VIRTUAL_ENV poetry env use "$(pyenv root)/versions/<full-version>/bin/python<version>"
env -u VIRTUAL_ENV poetry install                # reinstall deps for this interpreter
env -u VIRTUAL_ENV poetry run python -c "import sys; print(sys.version)"   # must print <version>
```

Always run the last check: CI checks the same thing ("Check virtualenv Python version"), because a virtualenv can silently fall back to a different interpreter.

If installing a version through `pyenv` is not possible, run that version's steps in the official `python:<version>` Docker image instead, with the repository copied into the container so each version gets its own `.venv`. Integration tests in a container must reach xrpld through `host.docker.internal` (Docker Desktop, or `--add-host=host.docker.internal:host-gateway`); `tests/integration/it_utils.py` hard-codes `127.0.0.1`, so rewrite those two URLs in the container's copy only, never in the repository.

### Validation order

Unit tests, lint and faucet tests can run **in parallel across Python versions**, each in its own working directory (e.g. `git worktree`) or container so the virtualenvs don't interfere. Integration tests **must run one Python version at a time** against a single xrpld: every integration test funds wallets from the same genesis account and closes ledgers with `ledger_accept`, so parallel runs against one node collide.

1. **Lint and type-check** (only on the `lint-and-type-check` Python version):

   ```bash
   poetry run poe lint
   poetry run mypy --strict --implicit-reexport xrpl
   ```

2. **Unit tests** (every matrix version):

   ```bash
   poetry run poe test_unit
   poetry run coverage report --fail-under=85
   ```

3. **Integration tests** (every matrix version, one version at a time):
   - Use the xrpld image CI uses. It is `rippleci/xrpld:develop` unless `.github/xrpld-image.env` sets `XRPLD_PRIVATE_VERSION`; a private image needs GitLab registry credentials, so if one is configured and you can't pull it, say so and stop rather than test against a different node. Pull it first (`docker pull <image>`) so a stale local copy isn't used.
   - Pre-run cleanup: `docker rm -f xrpld-service 2>/dev/null || true`
   - Start the container:
     ```bash
     docker run \
       --detach \
       --publish 5005:5005 \
       --publish 6006:6006 \
       --volume "$PWD/.ci-config/:/etc/xrpld/" \
       --name xrpld-service \
       <image> --standalone
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
   - Run for each Python version in turn:
     ```bash
     poetry run poe test_integration
     poetry run coverage report --fail-under=70
     ```
   - Keep the container running for step 4, then stop it: `docker logs xrpld-service && docker stop xrpld-service`

4. **Confidential MPT integration test** (only on the `confidential-integration-test` Python version, against the same xrpld, after step 3). It builds the optional native extension the core unit tests skip. Follow that job's steps in `integration_test.yml`; at the time of writing:

   ```bash
   poetry run pip install cffi setuptools     # build-time only, not project deps
   VERSION=$(grep -E '^MPT_CRYPTO_VERSION=' xrpl/ext/confidential/MPT_CRYPTO_VERSION | cut -d= -f2)
   ./xrpl/ext/confidential/setup_mpt_crypto.sh download --version "$VERSION"   # needs gh auth
   poetry run python xrpl/ext/confidential/build_mpt_crypto.py
   poetry run python -c "from xrpl.ext.confidential import MPT_CRYPTO_AVAILABLE; assert MPT_CRYPTO_AVAILABLE"
   poetry run python -m unittest tests.unit.ext.confidential.test_chaining tests.unit.ext.confidential.test_homomorphic tests.unit.ext.confidential.test_utility_layer
   poetry run python -m unittest tests.integration.transactions.test_confidential_mpt tests.integration.transactions.test_confidential_mpt_batch
   ```

   The native tests self-skip when the extension is missing, so the `MPT_CRYPTO_AVAILABLE` assertion is what makes a pass mean something. The downloaded library and built extension are gitignored; leave them out of the diff.

5. **Faucet tests** (every matrix version; uses the public devnet/testnet faucets, no local node):
   ```bash
   poetry run poe test_faucet
   ```
   CI runs `faucet_test.yml` only on pushes to `main`, never on the PR, so this local run is the only faucet check the batch gets before merge.

Collect results from every run. Every job on every Python version must pass.

- **Bound every run.** Give each job the same limit CI does (`timeout-minutes` in the workflow, e.g. 30 for integration) and treat hitting it as a failure: a full integration run normally takes about 5 minutes, so one still going after 30 is stuck, not slow. Kill it, record it, and restart xrpld before the next version.
- **Check the test count, not only the verdict.** A class whose `setUpClass` fails is reported as one error and its tests never run, so `Ran N tests` drops below the usual count. Compare `N` across Python versions and against `main`; a lower count is a failure even when the remaining tests pass.
- **Clean up on any exit.** If you stop part-way, stop the xrpld container and any test containers or processes you started, so nothing keeps running unattended.

If a test fails in a way that looks unrelated to the upgrade (a timeout, a different test failing on each run), run the same command on `main` in a separate worktree before blaming the batch. Report it as pre-existing only when `main` fails the same way, and give both pass rates in the PR description; one passing run on either side proves nothing.

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
     - `From` is the version on `main`; `Asked for` is what the PR proposed or the ticket requires (`≥ x.y.z`, taken from the advisory when the ticket gives none — one per vulnerable major line; for such a ticket with no upgrade target, the advisory's affected range when it is No-op or has no fixed release, or `unknown` when the advisory gives no usable range); `Resolved` is what `poetry.lock` actually holds after the batch. Keep them in separate columns: the three routinely differ (a PR proposing 4.1.0 can resolve to 4.2.1), and burying the real version in Status prose makes the table unverifiable.
     - Status values: Upgraded, No-op (reason), Skipped (dependency conflict / CI failure: error) — a status and its reason, never a version number.
     - MajorVersionUpgrade: `No` if the major version number did not change. Otherwise `Yes` plus a link for each major version crossed. For example, 1.x → 3.x yields `Yes ([v2](url), [v3](url))`. Each link should point to the package's release notes or changelog for that major version. Verify each link returns HTTP 200 and has meaningful content (e.g., `curl -sL --max-time 20 -o /dev/null -w "%{http_code}" <url>` — always set a timeout; an unbounded `curl` to GitHub can hang indefinitely); if a package doesn't publish per-version GitHub releases, fall back to the CHANGELOG file or the closest valid release tag.
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
   - List incidental lock changes (transitive packages added, removed or moved by a bump, and any `python_version`-split entries from Step 2.4), each with the bump that pulled it in.
   - For "Test Plan", give each Step 3 job's result per Python version, including the Confidential MPT job and the local-only faucet run, plus any failure reported as pre-existing with the `main` comparison behind it.

4. **Close list** — write `.claude/skills/batch-deps-upgrade/close-list.md` recording every ticket and Dependabot PR the batch makes closable. This is the input to the closing run.

   1. **Close** — every Upgraded and No-op ticket and PR, in one shape for both so a single parser handles them:

      ```
      <ticket-key or #pr> | <package> | installed <resolved> (<asked for>) | Comment: "<text>"
      ```

      The third field must carry the **resolved** version, not the proposed one — that is what step 1 of the closing run checks against `main`, and a proposed version cannot be verified.

      A ticket whose fix version came from its advisory, Upgraded or No-op, carries the advisory's affected range instead, so the closing run checks every installed line — and `not installed` when the package is gone: `installed 3.0.3 (outside < 3.0.3)`, `installed 5.7.2, 6.3.1 (outside < 5.7.2, 6.0.0–<6.3.1)`, `not installed (≤ 2.88.2)`.

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

`textfields ~ "xrpl-py"` is a text search, so it also returns tickets for other repositories that mention xrpl-py (e.g. an `XRPLF/xrpl-go` finding). Keep only tickets whose summary or vulnerable-code link names `XRPLF/xrpl-py`.

**Take the package name from the summary, not the description** — a description may list several packages sharing one advisory, so it picks the wrong one. Match it against `poetry.lock` case-insensitively and treat `-`, `_` and `.` as equal (PEP 503 normalisation): tickets and advisories say `Pygments`, the lock says `pygments`. Take the fix version, severity and CVE/GHSA link from the description; if it gives no fix version, see the next paragraph. Wording varies, so read for intent rather than matching labels literally.

Keep every ticket that names a vulnerable package. Drop tickets that name no vulnerable package, such as code and configuration findings. A package ticket with no fix version is still a row: take the fix version from its advisory (the GHSA link; read it with `gh api /advisories/<GHSA-id> --jq '.vulnerabilities[] | {package: .package.name, range: .vulnerable_version_range, patched: .first_patched_version}'`) instead — for each installed major line inside the affected range, the first patched version on that line, or on a higher major if that line has none — and handle it like any other ticket. It is satisfied only when every installed version falls outside the advisory's affected range: No-op if that was already true on `main` or the package is no longer installed, Upgraded if the batch made it true. Mark it Skipped only when the advisory has no patched version at all ("no fixed release exists") or has no usable range ("flag for manual review") — both need a human decision. If tickets came back but none of them could be parsed, that is a parsing failure — stop. If the query returned nothing, or nothing was in scope, there is simply no Semgrep work this quarter: record zero and carry on with the Dependabot batch. A ticket becomes a row whether or not a Dependabot PR proposes that package; a ticket is reason enough on its own.

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

1. **Verify each item against the current `main`** and skip anything not genuinely satisfied — a reviewer may have had an upgrade reverted. This is what makes the run safe whether or not the batch has merged. For a range-based item, verify that every installed version on `main` is still outside the range, or the package is still absent.
2. **Close everything that verified.** Do not ask for approval; the engineer reviewed both lists on the PR, and step 1 is the real check.
   - **JIRA tickets** — complete the `Done` transition first (query available transitions, take the one to `Done`), then post the comment. This avoids open-but-commented tickets if transition fails.
   - **Dependabot PRs** — `gh pr close <n> --repo XRPLF/xrpl-py --comment "<comment>"`.
3. Report in this shape:

   ```
   Closed <n> JIRA tickets, <n> Dependabot PRs.

   Skipped — not satisfied on main @ <sha> (<n>):
     <TICKET-KEY>   <pkg> needs <version>, main has <version>
     #<pr-number>   <pkg> <version> never applied (<reason from close-list>)
   ```

   If nothing was skipped, say so rather than omitting the section.
