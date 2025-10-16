# xrpl-py Release Playbook

This guide document describe how to cut and ship a new `xrpl-py` version using the
`Publish xrpl-py 🐍 distribution 📦 to PyPI` GitHub Actions workflow (see
`.github/workflows/release.yml`). It mirrors the automation and reviews that run
when the workflow is manually dispatched.

## 0. Configurations required for this pipeline

- Protected environments `first-review` and `official-release`.
- Access to the shared Slack workspace (notifications go to `#xrpl-py`).
- Reviewers from dev team and infosec team to approve GitHub environment gates and review pull requests.
- PyPI Trusted Publisher to trust the workflow and the protected environment.

### Beta vs. Stable Releases

The workflow automatically differentiates between beta/pre-release versions
and standard releases by reading version under [project] section from pyproject.toml:

- **Beta release**:  
  - Skips creating the release PR from the release branch back to `main`.  
  - The GitHub Release is created with `--prerelease`.  
  - The `latest` tag on GitHub remains unchanged (beta builds do not become the
    default download).

- **Stable release**:  
  - A PR from the release branch to `main` is created (or reused) so the Dev
    team can review and merge after PyPI verification.  
  - The GitHub Release is created with `--latest`, updating the repository’s
    default published release.

## 1. Prepare the Release Branch

1. Create release branch using name pattern `release-x.y.z` (or `release/x.y.z`).
2. Bump `project.version` inside `pyproject.toml` and update `CHANGELOG.md`
   (or other release notes).

The workflow will fail immediately if the version already exists, if the branch
name does not match the required prefix.

## 2. Run the Release Workflow

1. Navigate to **Actions → Publish xrpl-py 🐍 distribution 📦 to PyPI**.
2. Select the release branch and click **Run workflow**.

### What the workflow does

The high-level pipeline is:

| Stage | Purpose (key steps) |
| --- | --- |
| `input-validate` | Checks branch naming, ensures the version in `pyproject.toml` does not already exist as a tag, Detects whether the release is a beta (`a`, `b`, or `rc`). |
| `faucet-tests`, `integration-tests` | Re-usable workflows that run faucet, unit, and integration test matrices against supported Python versions. |
| `pre-release` | Builds the wheel and sdist with Poetry 2.1.1, uploads build artifacts, generates a CycloneDX SBOM, scans it with Trivy, uploads results to OWASP Dependency-Track, and stores both SBOM and vulnerability reports as Actions artifacts. If any CRITICAL/HIGH findings exist, the job opens a GitHub issue linking to the report. |
| `ask_for_dev_team_review` | Creates or reuses a PR from the release branch to `main` (skipped for beta releases), gathers required reviewers from environment protection rules, prints a summary, and posts a Slack message requesting review/approval. |
| `first_review` | Waits for the Dev environment (`first-review`) approval. |
| `ask_for_sec_team_review` | Notifies security reviewers on Slack and waits for the `official-release` environment approval. |
| `publish-to-pypi` | Downloads the built artifacts from previous step, enforces single-run (no retries), and publishes to PyPI via trusted publishing once approvals are in place. |
| `github-release` | Signs artifacts with the Sigstore action, creates or updates the GitHub Release (`--prerelease` for beta versions, `--latest` for stable releases), uploads signatures/provenance, and posts a Slack success message. |

## 3. Approvals & Reviews

- **Dev review**: When `ask_for_dev_team_review` finishes, reviewers receive a
  Slack ping. Approvers must visit the workflow run and approve the
  `first-review` environment gate. 
- **Security review**: After the Dev gate is cleared, the workflow pauses at
  `official-release`. Security reviewers receive a Slack ping and must review the valnervilities approve
  that environment gate.

If the SBOM scan surfaced critical/high vulnerabilities, address the follow-up
GitHub issue before continuing.

## 4. Verify Publication & Finish Up

1. Wait for `publish-to-pypi` and `github-release` to complete successfully.
   Trusted publishing relies on the approved environment gates—reruns are
   blocked, so restart the workflow from scratch if it fails after publishing.
2. Confirm the new version is visible on PyPI:
   `https://pypi.org/project/xrpl-py/<version>/`
3. Confirm the GitHub Release looks correct (artifacts, provenance, and the
   pre-release flag if applicable).
4. Merge the automated release PR into `main` (stable releases only). Do this
   after you verify PyPI.
5. Create any follow-up housekeeping PRs (e.g., bumping `dev` version or
   updating docs) if needed.

## 5. Troubleshooting

- **Workflow fails during validation**: Check the branch name, version bump,
  existing tags (`git ls-remote --tags origin`), and Artifactory references.
- **SBOM scan reports vulnerabilities**: Review the autogenerated GitHub issue
  linked in the workflow logs. Resolve or justify before restarting the run.
- **PyPI publication fails**: Ensure the environment gates are approved only
  once—rerunning `publish-to-pypi` is blocked to prevent double publishes.
- **GitHub release creation fails**: Look at the step output; the workflow will
  show the exact `gh release create` command and any API error returned.

This document should cover the normal release cadence for `xrpl-py`. If the
automation needs adjustments, update both `.github/workflows/release.yml` and
this guide so they stay in sync.
