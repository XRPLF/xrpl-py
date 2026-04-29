"""Script to generate the definitions.json file from rippled CI artifacts.

Downloads server_definitions.json from rippled CI artifacts and saves it
as definitions.json.

Requires the GitHub CLI (gh) to be installed and authenticated.
  https://cli.github.com/
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

UPSTREAM_REPO = "XRPLF/rippled"
ARTIFACT_NAME = "server-definitions"

DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__),
    "../xrpl/core/binarycodec/definitions/definitions.json",
)


def _exec(cmd: str) -> str:
    """Run a shell command and return its stripped stdout."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _check_gh_cli() -> None:
    """Verify the GitHub CLI is installed."""
    try:
        subprocess.run(
            ["gh", "--version"], capture_output=True, text=True, check=True
        )
    except FileNotFoundError:
        print(
            "Error: GitHub CLI (gh) is required but not found.\n"
            "Install from https://cli.github.com/",
            file=sys.stderr,
        )
        sys.exit(1)


def _get_pr_info(pr_number: str) -> dict:
    """Get branch name and head SHA for a pull request."""
    try:
        raw = _exec(
            f'gh api "repos/{UPSTREAM_REPO}/pulls/{pr_number}"'
            " --jq '{headRefName: .head.ref, headRefOid: .head.sha}'"
        )
        return json.loads(raw)
    except subprocess.CalledProcessError:
        print(
            f"Error: Could not find PR #{pr_number} in {UPSTREAM_REPO}",
            file=sys.stderr,
        )
        sys.exit(1)


def _find_pr_for_fork_branch(fork_owner: str, branch: str) -> dict | None:
    """Find a PR in the upstream repo for a fork branch."""
    try:
        raw = _exec(
            f'gh api "repos/{UPSTREAM_REPO}/pulls?head={fork_owner}:{branch}'
            f'&state=open&per_page=1"'
            " --jq '[.[] | {number: .number, headRefOid: .head.sha}]'"
        )
        prs = json.loads(raw)
        if prs:
            return prs[0]
    except subprocess.CalledProcessError:
        pass
    return None


def _find_artifact_by_branch(repo: str, branch: str) -> str | None:
    """Find the most recent server-definitions artifact on a branch.

    Uses the artifacts API to search by name directly, then filters by branch.
    This works even if the overall CI run failed, as long as the artifact was
    produced before the failure.
    """
    try:
        raw = _exec(
            f'gh api "repos/{repo}/actions/artifacts'
            f"?name={ARTIFACT_NAME}&per_page=50\""
            f" --jq '[.artifacts[] | select(.workflow_run.head_branch == \"{branch}\""
            f' and .expired == false)] | .[0].workflow_run.id // empty\''
        )
        return raw if raw else None
    except subprocess.CalledProcessError:
        return None


def _find_artifact_by_sha(repo: str, sha: str) -> str | None:
    """Find the server-definitions artifact for a specific commit SHA."""
    try:
        raw = _exec(
            f'gh api "repos/{repo}/actions/artifacts'
            f"?name={ARTIFACT_NAME}&per_page=50\""
            f" --jq '[.artifacts[] | select(.workflow_run.head_sha == \"{sha}\""
            f' and .expired == false)] | .[0].workflow_run.id // empty\''
        )
        return raw if raw else None
    except subprocess.CalledProcessError:
        return None


def _download_artifact(repo: str, run_id: str, output_file: str) -> None:
    """Download the artifact and write it as definitions.json."""
    tmp_dir = tempfile.mkdtemp(prefix="server-definitions-")
    try:
        try:
            _exec(
                f"gh run download {run_id} --repo {repo}"
                f' --name {ARTIFACT_NAME} --dir "{tmp_dir}"'
            )
        except subprocess.CalledProcessError:
            print(
                f"Error: Failed to download artifact from run {run_id}.\n"
                "The artifact may have expired (GitHub retains artifacts for a"
                " limited time).\n"
                "Try a branch with a more recent CI run.",
                file=sys.stderr,
            )
            sys.exit(1)

        server_defs_path = os.path.join(tmp_dir, "server_definitions.json")
        if not os.path.exists(server_defs_path):
            print(
                "Error: server_definitions.json not found in downloaded artifact",
                file=sys.stderr,
            )
            sys.exit(1)

        with open(server_defs_path, encoding="utf-8") as f:
            server_defs = json.load(f)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(server_defs, f, indent=2)
            f.write("\n")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Downloads server_definitions.json from rippled CI artifacts"
            " and saves it as definitions.json."
        ),
        epilog=(
            "Requires the GitHub CLI (gh) to be installed and authenticated.\n"
            "  https://cli.github.com/\n\n"
            "Examples:\n"
            "  python %(prog)s\n"
            "  python %(prog)s develop\n"
            "  python %(prog)s pr:6858\n"
            "  python %(prog)s contributor:my-feature\n"
            "  python %(prog)s feature-branch -o ./custom-output.json"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="develop",
        help=(
            'Branch name, PR number (e.g. "pr:7008"), or fork branch'
            ' (e.g. "contributor:my-feature"). Default: develop'
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output file path (default: definitions.json in binarycodec)",
    )
    args = parser.parse_args()

    # Parse "pr:<number>" format
    if args.source.startswith("pr:"):
        args.pr_number = args.source[3:]
        args.branch = "develop"
    else:
        args.pr_number = None
        args.branch = args.source

    return args


def main() -> None:
    """Entry point."""
    _check_gh_cli()
    args = _parse_args()

    branch = args.branch
    pr_number = args.pr_number
    output_file = args.output

    run_id = None
    repo = UPSTREAM_REPO

    # Parse "owner:branch" format for fork branches
    fork_owner = None
    if not pr_number and ":" in branch:
        colon_idx = branch.index(":")
        fork_owner = branch[:colon_idx]
        branch = branch[colon_idx + 1 :]

    if pr_number:
        pr_info = _get_pr_info(pr_number)
        sha_short = pr_info["headRefOid"][:7]
        print(
            f'Resolved PR #{pr_number} to branch'
            f' "{pr_info["headRefName"]}" ({sha_short})'
        )

        # Try commit SHA first — works for fork PRs where the branch name
        # belongs to the fork repo and won't be found by branch-based search.
        print("Searching by commit SHA...")
        run_id = _find_artifact_by_sha(UPSTREAM_REPO, pr_info["headRefOid"])

        if not run_id:
            print(
                f"No artifact found by SHA, trying branch"
                f' "{pr_info["headRefName"]}"...'
            )
            run_id = _find_artifact_by_branch(
                UPSTREAM_REPO, pr_info["headRefName"]
            )

    elif fork_owner:
        fork_repo = f"{fork_owner}/rippled"
        print(f'Fork branch detected: "{fork_owner}:{branch}"')

        # Check if there's a PR in the upstream repo for this fork branch
        print(f"Checking for PR in {UPSTREAM_REPO}...")
        pr = _find_pr_for_fork_branch(fork_owner, branch)

        if pr:
            sha_short = pr["headRefOid"][:7]
            print(
                f"Found PR #{pr['number']} ({sha_short}), searching upstream CI..."
            )
            run_id = _find_artifact_by_sha(UPSTREAM_REPO, pr["headRefOid"])

            if not run_id:
                run_id = _find_artifact_by_branch(UPSTREAM_REPO, branch)

        if not run_id:
            # No PR or no artifact in upstream — search the fork repo's CI
            print(
                f'Searching fork repo {fork_repo} for CI on branch "{branch}"...'
            )
            repo = fork_repo
            run_id = _find_artifact_by_branch(fork_repo, branch)

    else:
        print(
            f'Searching for "{ARTIFACT_NAME}" artifact on branch "{branch}"...'
        )
        run_id = _find_artifact_by_branch(UPSTREAM_REPO, branch)

    if not run_id:
        print(
            f'Error: No CI runs with "{ARTIFACT_NAME}" artifact found.\n'
            "Make sure the branch has a successful CI run that produced"
            " the server-definitions artifact.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found artifact in run {run_id}")

    print("Downloading artifact...")
    _download_artifact(repo, run_id, output_file)
    print(f"Definitions written to {output_file}")


if __name__ == "__main__":
    main()
