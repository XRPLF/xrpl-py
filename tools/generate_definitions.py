"""Script to generate the definitions.json file from rippled.

By default this downloads the server-definitions artifact built by rippled CI
and saves it as definitions.json, which requires the GitHub CLI (gh) to be
installed and authenticated:
  https://cli.github.com/

Two local sources are also supported, for when CI has no usable artifact:
rippled retains them for only 3 days, external-contributor PRs need workflow
approval before CI runs at all, and a branch that has not been pushed has no
CI run to download from.

  - A filesystem path runs `xrpld --definitions` against a local build.
  - An http(s) URL or a loopback host:port sends a `server_definitions`
    request to a running node (a Docker container, or a standalone build).

All three sources return the same payload: rippled builds the definitions
once at startup from its compiled-in format tables, and both `--definitions`
and the RPC return that same object.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

import httpx

UPSTREAM_REPO = "XRPLF/rippled"
ARTIFACT_NAME = "server-definitions"

# rippled renamed its binary from "rippled" to "xrpld"; accept either.
BINARY_NAMES = ("xrpld", "rippled")

# Relative locations searched when given a rippled source/build directory.
BUILD_SUBDIRS = ("", ".build", "build", "build/Release", "build/Debug")

# Hosts accepted without a scheme, e.g. "localhost:5005". Restricted to
# loopback so an "owner:branch" fork reference is never mistaken for a host.
LOOPBACK_HOSTS = ("localhost", "127.0.0.1", "::1", "[::1]")

# rippled's default JSON-RPC admin port.
DEFAULT_RPC_PORT = 5005

DEFAULT_OUTPUT = os.path.join(
    os.path.dirname(__file__),
    "../xrpl/core/binarycodec/definitions/definitions.json",
)


def _exec(cmd: list[str]) -> str:
    """Run a command (argv list, no shell) and return its stripped stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_gh_cli() -> None:
    """Verify the GitHub CLI is installed."""
    try:
        subprocess.run(["gh", "--version"], capture_output=True, text=True, check=True)
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
            [
                "gh",
                "api",
                f"repos/{UPSTREAM_REPO}/pulls/{pr_number}",
                "--jq",
                "{headRefName: .head.ref, headRefOid: .head.sha}",
            ]
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
            [
                "gh",
                "api",
                f"repos/{UPSTREAM_REPO}/pulls"
                f"?head={fork_owner}:{branch}&state=open&per_page=1",
                "--jq",
                "[.[] | {number: .number, headRefOid: .head.sha}]",
            ]
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
            [
                "gh",
                "api",
                f"repos/{repo}/actions/artifacts" f"?name={ARTIFACT_NAME}&per_page=50",
                "--jq",
                "[.artifacts[]"
                f' | select(.workflow_run.head_branch == "{branch}"'
                " and .expired == false)] | .[0].workflow_run.id // empty",
            ]
        )
        return raw if raw else None
    except subprocess.CalledProcessError:
        return None


def _find_artifact_by_sha(repo: str, sha: str) -> str | None:
    """Find the server-definitions artifact for a specific commit SHA."""
    try:
        raw = _exec(
            [
                "gh",
                "api",
                f"repos/{repo}/actions/artifacts" f"?name={ARTIFACT_NAME}&per_page=50",
                "--jq",
                "[.artifacts[]"
                f' | select(.workflow_run.head_sha == "{sha}"'
                " and .expired == false)] | .[0].workflow_run.id // empty",
            ]
        )
        return raw if raw else None
    except subprocess.CalledProcessError:
        return None


def _write_definitions(server_defs: dict, output_file: str) -> None:
    """Write definitions to disk in the repo's canonical formatting."""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(server_defs, f, indent=2)
        f.write("\n")


def _as_rpc_url(source: str) -> str | None:
    """Return a JSON-RPC URL if the source names a running server, else None."""
    if source.startswith(("http://", "https://")):
        return source

    host, sep, port = source.rpartition(":")
    if sep and host.lower() in LOOPBACK_HOSTS and port.isdigit():
        return f"http://{source}"
    if not sep and source.lower() in LOOPBACK_HOSTS:
        return f"http://{source}:{DEFAULT_RPC_PORT}"
    return None


def _generate_from_rpc(url: str, output_file: str) -> None:
    """Fetch definitions from a running rippled via `server_definitions`."""
    print(f"Requesting server_definitions from {url}...")
    try:
        response = httpx.post(
            url,
            json={"method": "server_definitions", "params": [{}]},
            timeout=30,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(
            f"Error: {url} returned HTTP {e.response.status_code}",
            file=sys.stderr,
        )
        sys.exit(1)
    except httpx.HTTPError as e:
        print(
            f"Error: Could not reach rippled at {url}: {e}\n"
            "Make sure the server is running and the JSON-RPC port is"
            " exposed.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        payload = response.json()
    except ValueError as e:
        print(f"Error: {url} did not return valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = payload.get("result")
    if not isinstance(result, dict):
        print(
            f'Error: Unexpected response from {url}: missing "result"',
            file=sys.stderr,
        )
        sys.exit(1)

    if result.get("status") == "error" or "error" in result:
        detail = result.get("error_message") or result.get("error")
        print(
            f"Error: server_definitions failed: {detail}\n"
            "The server may be too old to support this request.",
            file=sys.stderr,
        )
        sys.exit(1)

    # "status" is added by the JSON-RPC layer, not part of the definitions.
    result.pop("status", None)

    if "FIELDS" not in result:
        print(
            f"Error: Response from {url} does not look like server" " definitions.",
            file=sys.stderr,
        )
        sys.exit(1)

    _write_definitions(result, output_file)


def _resolve_local_binary(path: str) -> str:
    """Resolve a path to a built xrpld/rippled binary.

    Accepts the binary itself, or a rippled source/build directory to search.
    """
    if os.path.isfile(path):
        if not os.access(path, os.X_OK):
            print(f"Error: {path} is not executable", file=sys.stderr)
            sys.exit(1)
        return path

    if not os.path.isdir(path):
        print(f"Error: No such file or directory: {path}", file=sys.stderr)
        sys.exit(1)

    for subdir in BUILD_SUBDIRS:
        for name in BINARY_NAMES:
            candidate = os.path.join(path, subdir, name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate

    searched = ", ".join(repr(d) for d in BUILD_SUBDIRS if d) or "the directory"
    print(
        f"Error: No xrpld or rippled binary found under {path}.\n"
        f"Searched the directory itself and {searched}.\n"
        "Build rippled first, or pass the path to the binary directly.",
        file=sys.stderr,
    )
    sys.exit(1)


def _generate_from_binary(binary: str, output_file: str) -> None:
    """Run `<binary> --definitions` and write the result."""
    print(f"Running {binary} --definitions...")
    try:
        raw = _exec([binary, "--definitions"])
    except subprocess.CalledProcessError as e:
        stderr = (e.stderr or "").strip()
        print(
            f"Error: {binary} --definitions failed"
            f" (exit {e.returncode}).\n{stderr}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        server_defs = json.loads(raw)
    except json.JSONDecodeError as e:
        print(
            f"Error: {binary} --definitions did not return valid JSON: {e}\n"
            "Make sure this is a rippled binary new enough to support"
            " --definitions.",
            file=sys.stderr,
        )
        sys.exit(1)

    _write_definitions(server_defs, output_file)


def _download_artifact(repo: str, run_id: str, output_file: str) -> None:
    """Download the artifact and write it as definitions.json."""
    tmp_dir = tempfile.mkdtemp(prefix="server-definitions-")
    try:
        try:
            _exec(
                [
                    "gh",
                    "run",
                    "download",
                    run_id,
                    "--repo",
                    repo,
                    "--name",
                    ARTIFACT_NAME,
                    "--dir",
                    tmp_dir,
                ]
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

        _write_definitions(server_defs, output_file)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generates definitions.json from a rippled CI artifact, a local"
            " xrpld build, or a running rippled server."
        ),
        epilog=(
            "Remote sources require the GitHub CLI (gh) to be installed and\n"
            "authenticated: https://cli.github.com/\n\n"
            "Examples:\n"
            "  python %(prog)s                              # develop\n"
            "  python %(prog)s develop\n"
            "  python %(prog)s pr:6858\n"
            "  python %(prog)s contributor:my-feature\n"
            "  python %(prog)s feature-branch -o ./custom-output.json\n\n"
            "Local build (no gh required; runs xrpld --definitions):\n"
            "  python %(prog)s ~/rippled                    # searches"
            " .build/, build/\n"
            "  python %(prog)s ~/rippled/.build/xrpld       # the binary"
            " itself\n\n"
            "Running server (no gh required; sends server_definitions):\n"
            "  python %(prog)s localhost:5005\n"
            "  python %(prog)s http://127.0.0.1:5005"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "source",
        nargs="?",
        default="develop",
        help=(
            'Branch name, PR number (e.g. "pr:7008"), fork branch'
            ' (e.g. "contributor:my-feature"), a path to a local rippled'
            " build or xrpld binary, or a running server"
            ' (e.g. "localhost:5005"). Default: develop'
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output file path (default: definitions.json in binarycodec)",
    )
    args = parser.parse_args()

    # Resolve local sources before remote ones. "pr:<n>" is checked first so
    # it is never read as a host:port.
    if args.source.startswith("pr:"):
        args.rpc_url = None
        args.local_path = None
    else:
        args.rpc_url = _as_rpc_url(args.source)
        expanded = os.path.expanduser(args.source)
        args.local_path = (
            None if args.rpc_url else (expanded if os.path.exists(expanded) else None)
        )

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
    args = _parse_args()

    if args.rpc_url:
        _generate_from_rpc(args.rpc_url, args.output)
        print(f"Definitions written to {args.output}")
        return

    if args.local_path:
        binary = _resolve_local_binary(args.local_path)
        _generate_from_binary(binary, args.output)
        print(f"Definitions written to {args.output}")
        return

    _check_gh_cli()

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
            f"Resolved PR #{pr_number} to branch"
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
            run_id = _find_artifact_by_branch(UPSTREAM_REPO, pr_info["headRefName"])

    elif fork_owner:
        fork_repo = f"{fork_owner}/rippled"
        print(f'Fork branch detected: "{fork_owner}:{branch}"')

        # Check if there's a PR in the upstream repo for this fork branch
        print(f"Checking for PR in {UPSTREAM_REPO}...")
        pr = _find_pr_for_fork_branch(fork_owner, branch)

        if pr:
            sha_short = pr["headRefOid"][:7]
            print(f"Found PR #{pr['number']} ({sha_short}), searching upstream CI...")
            run_id = _find_artifact_by_sha(UPSTREAM_REPO, pr["headRefOid"])

            if not run_id:
                run_id = _find_artifact_by_branch(UPSTREAM_REPO, branch)

        if not run_id:
            # No PR or no artifact in upstream — search the fork repo's CI
            print(f'Searching fork repo {fork_repo} for CI on branch "{branch}"...')
            repo = fork_repo
            run_id = _find_artifact_by_branch(fork_repo, branch)

    else:
        print(f'Searching for "{ARTIFACT_NAME}" artifact on branch "{branch}"...')
        run_id = _find_artifact_by_branch(UPSTREAM_REPO, branch)

    if not run_id:
        print(
            f'Error: No CI runs with "{ARTIFACT_NAME}" artifact found.\n'
            "Artifacts are kept for 3 days, take ~10 minutes to appear after"
            " a push, and are never produced for an unpushed branch or for an"
            " external contributor's PR awaiting workflow approval.\n"
            "Generate from a local rippled instead, e.g.:\n"
            "  python tools/generate_definitions.py ~/path/to/rippled\n"
            "  python tools/generate_definitions.py localhost:5005",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found artifact in run {run_id}")

    print("Downloading artifact...")
    _download_artifact(repo, run_id, output_file)
    print(f"Definitions written to {output_file}")


if __name__ == "__main__":
    main()
