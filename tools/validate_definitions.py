"""Script to validate definitions.json against the rippled CI benchmark.

Downloads the server_definitions.json artifact from rippled's develop branch
and compares it against the local definitions.json to ensure structural
correctness and entry consistency.

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

import httpx

UPSTREAM_REPO = "XRPLF/rippled"

# Default JSON-RPC endpoint of a local rippled (e.g. the rippleci/xrpld
# container the CI job starts).
DEFAULT_RPC_URL = "http://localhost:5005"
ARTIFACT_NAME = "server-definitions"

DEFINITIONS_PATH = os.path.join(
    os.path.dirname(__file__),
    "../xrpl/core/binarycodec/definitions/definitions.json",
)

REQUIRED_KEYS = [
    "FIELDS",
    "LEDGER_ENTRY_TYPES",
    "TRANSACTION_RESULTS",
    "TRANSACTION_TYPES",
    "TYPES",
]


def _exec(cmd: list[str]) -> str:
    """Run a command (argv list, no shell) and return its stripped stdout."""
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def _check_gh_cli() -> None:
    try:
        subprocess.run(["gh", "--version"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        print(
            "Error: GitHub CLI (gh) is required but not found.\n"
            "Install from https://cli.github.com/",
            file=sys.stderr,
        )
        sys.exit(1)

    # Installed but unauthenticated fails later as an opaque API error, so
    # check here and say what to do about it. GH_TOKEN satisfies this too.
    try:
        subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as e:
        detail = ((e.stderr or "") + (e.stdout or "")).strip()
        print(
            "Error: GitHub CLI (gh) is not authenticated.\n"
            "Run `gh auth login`, or set GH_TOKEN to a token with access to"
            f" {UPSTREAM_REPO}.\n{detail}",
            file=sys.stderr,
        )
        sys.exit(1)


# The artifacts API cannot filter by branch, so results are scanned page by
# page. rippled publishes enough artifacts that a single 100-item page spans
# only a few hours of the 3-day retention window.
ARTIFACT_PAGE_SIZE = 100
ARTIFACT_MAX_PAGES = 10


def _find_develop_run() -> str | None:
    """Find the newest unexpired server-definitions run on develop.

    Returns None only for a completed scan that matched nothing; a failed
    API call exits non-zero so it cannot be mistaken for an absent artifact.
    """
    for page in range(1, ARTIFACT_MAX_PAGES + 1):
        try:
            raw = _exec(
                [
                    "gh",
                    "api",
                    f"repos/{UPSTREAM_REPO}/actions/artifacts"
                    f"?name={ARTIFACT_NAME}"
                    f"&per_page={ARTIFACT_PAGE_SIZE}&page={page}",
                ]
            )
        except subprocess.CalledProcessError as e:
            # An auth, rate-limit or network failure. Skipping here would
            # turn the check into a no-op that still reports success.
            print(
                "Error: GitHub API query for the benchmark artifact failed:\n"
                f"{(e.stderr or '').strip()}",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            artifacts = json.loads(raw).get("artifacts", [])
        except json.JSONDecodeError:
            return None

        for entry in artifacts:
            run = entry.get("workflow_run") or {}
            if entry.get("expired") is False and run.get("head_branch") == "develop":
                return str(run.get("id", ""))

        if len(artifacts) < ARTIFACT_PAGE_SIZE:
            return None

    return None


def _benchmark_from_rpc(url: str) -> dict:
    """Fetch the benchmark from a running rippled via `server_definitions`.

    Preferred in CI: a container pinned to rippled develop is always
    available, so there is no artifact retention window and no GitHub token
    involved.
    """
    print(f"Requesting server_definitions from {url}...")
    try:
        response = httpx.post(
            url,
            json={"method": "server_definitions", "params": [{}]},
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as e:
        print(
            f"Error: Could not read definitions from {url}: {e}\n"
            "Make sure the rippled container is running and its JSON-RPC"
            " port is exposed.",
            file=sys.stderr,
        )
        sys.exit(1)

    result = payload.get("result")
    if not isinstance(result, dict) or "FIELDS" not in result:
        print(
            f"Error: Unexpected server_definitions response from {url}.",
            file=sys.stderr,
        )
        sys.exit(1)

    # "status" is added by the JSON-RPC layer, not part of the definitions.
    result.pop("status", None)
    return result


def _artifact_expired(run_id: str) -> bool:
    """Report whether the run's server-definitions artifact is gone.

    GitHub purges an artifact's payload once it expires, so the entry either
    reports expired or disappears from the run entirely. Anything else means
    the artifact is still there and a download failure had another cause.
    """
    try:
        raw = _exec(
            ["gh", "api", f"repos/{UPSTREAM_REPO}/actions/runs/{run_id}/artifacts"]
        )
        artifacts = json.loads(raw).get("artifacts", [])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # Cannot confirm expiry, so do not treat it as confirmed.
        return False

    for entry in artifacts:
        if entry.get("name") == ARTIFACT_NAME:
            return bool(entry.get("expired"))
    return True


def _download_benchmark() -> dict | None:
    """Download the develop benchmark, or return None if it is unavailable.

    rippled retains the server-definitions artifact for only 3 days, and
    develop occasionally goes longer than that without a merge. That is an
    upstream availability gap rather than a problem with definitions.json,
    so the caller skips validation instead of failing.

    None is returned only for a confirmed availability gap: a completed scan
    that matched nothing, or an artifact that expired between discovery and
    download. Every other failure exits non-zero, so a bad token, a rate
    limit or a network error cannot quietly disable the check.
    """
    print("Downloading benchmark definitions from rippled develop branch...")

    run_id = _find_develop_run()

    if not run_id:
        print(
            "Warning: No unexpired server-definitions artifact on rippled"
            " develop (artifacts are retained for 3 days)."
        )
        return None

    print(f"Found artifact in run {run_id}")
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
                    UPSTREAM_REPO,
                    "--name",
                    ARTIFACT_NAME,
                    "--dir",
                    tmp_dir,
                ]
            )
        except subprocess.CalledProcessError as e:
            # Skip only if the artifact demonstrably expired between
            # discovery and download. Every other download failure is an
            # infrastructure problem and must not pass as a successful check.
            if _artifact_expired(run_id):
                print(
                    f"Warning: Artifact from run {run_id} expired between"
                    " discovery and download."
                )
                return None
            print(
                f"Error: Failed to download the benchmark artifact from run"
                f" {run_id}, and it has not expired:\n"
                f"{(e.stderr or '').strip()}",
                file=sys.stderr,
            )
            sys.exit(1)

        server_defs_path = os.path.join(tmp_dir, "server_definitions.json")
        if not os.path.exists(server_defs_path):
            print(
                "Error: server_definitions.json not found in the downloaded"
                " artifact.",
                file=sys.stderr,
            )
            sys.exit(1)

        with open(server_defs_path, encoding="utf-8") as f:
            return json.load(f)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── Structure classification ─────────────────────────────────────────────────


def _classify_value(value: object) -> str:
    """Classify a value for validation/comparison."""
    if isinstance(value, list):
        if (
            len(value) > 0
            and isinstance(value[0], list)
            and len(value[0]) == 2
            and isinstance(value[0][0], str)
            and isinstance(value[0][1], dict)
        ):
            return "fields"
        return "skip"

    if not isinstance(value, dict):
        return "skip"

    values = list(value.values())
    if not values:
        return "skip"

    first = values[0]

    if isinstance(first, (int, float)):
        return "simple_map"

    if isinstance(first, dict):
        inner_values = list(first.values())
        if inner_values and isinstance(inner_values[0], (int, float)):
            return "nested_map"

    if isinstance(first, list):
        if (
            len(first) > 0
            and isinstance(first[0], dict)
            and "name" in first[0]
            and "optionality" in first[0]
        ):
            return "format_array"

    return "skip"


# ── Structural validation ────────────────────────────────────────────────────


def _validate_structure(local: dict, benchmark: dict) -> list[str]:
    errors = []

    for key in REQUIRED_KEYS:
        if key not in local:
            errors.append(f'Missing required key: "{key}"')

    for key, local_value in local.items():
        category = (
            _classify_value(benchmark[key])
            if key in benchmark
            else _classify_value(local_value)
        )

        if category == "fields":
            if not isinstance(local_value, list):
                errors.append(f"{key} must be a list")
                continue
            for i, entry in enumerate(local_value):
                if not isinstance(entry, list) or len(entry) != 2:
                    errors.append(f"{key}[{i}]: expected [name, info] pair")
                    continue
                name, info = entry
                if not isinstance(name, str):
                    errors.append(
                        f"{key}[{i}]: name must be a string, got {type(name).__name__}"
                    )
                if not isinstance(info, dict):
                    errors.append(f'{key}[{i}] ("{name}"): info must be a dict')
                    continue
                for prop in ("isSerialized", "isSigningField", "isVLEncoded"):
                    if not isinstance(info.get(prop), bool):
                        errors.append(
                            f'{key} "{name}": "{prop}" must be a bool,'
                            f" got {type(info.get(prop)).__name__}"
                        )
                if not isinstance(info.get("nth"), int):
                    errors.append(
                        f'{key} "{name}": "nth" must be an int,'
                        f" got {type(info.get('nth')).__name__}"
                    )
                if not isinstance(info.get("type"), str):
                    errors.append(
                        f'{key} "{name}": "type" must be a string,'
                        f" got {type(info.get('type')).__name__}"
                    )

        elif category == "simple_map":
            if not isinstance(local_value, dict):
                errors.append(f"{key} must be a dict")
                continue
            for name, val in local_value.items():
                if not isinstance(val, int):
                    errors.append(
                        f'{key} "{name}": value must be an int,'
                        f" got {type(val).__name__}"
                    )

        elif category == "nested_map":
            if not isinstance(local_value, dict):
                errors.append(f"{key} must be a dict")
                continue
            for type_name, flags in local_value.items():
                if not isinstance(flags, dict):
                    errors.append(f'{key} "{type_name}": value must be a dict')
                    continue
                for flag_name, val in flags.items():
                    if not isinstance(val, int):
                        errors.append(
                            f'{key} "{type_name}"."{flag_name}": value must be'
                            f" an int, got {type(val).__name__}"
                        )

        elif category == "format_array":
            if not isinstance(local_value, dict):
                errors.append(f"{key} must be a dict")
                continue
            for type_name, fields in local_value.items():
                if not isinstance(fields, list):
                    errors.append(f'{key} "{type_name}": value must be a list')
                    continue
                for j, field in enumerate(fields):
                    if not isinstance(field, dict):
                        errors.append(f'{key} "{type_name}"[{j}]: field must be a dict')
                        continue
                    if not isinstance(field.get("name"), str):
                        errors.append(
                            f'{key} "{type_name}"[{j}]: "name" must be a string'
                        )
                    if not isinstance(field.get("optionality"), int):
                        errors.append(
                            f'{key} "{type_name}"[{j}]: "optionality" must be' " an int"
                        )

    return errors


# ── Entry comparison ─────────────────────────────────────────────────────────


def _compare_definitions(local: dict, benchmark: dict) -> list[str]:
    errors = []

    for key, bench_value in benchmark.items():
        if key not in local:
            continue

        category = _classify_value(bench_value)
        local_value = local[key]

        if category == "fields":
            bench_map = {}
            for name, info in bench_value:
                if name not in bench_map:
                    bench_map[name] = info
            for name, local_info in local_value:
                bench_info = bench_map.get(name)
                if not bench_info:
                    continue
                for prop in bench_info:
                    if local_info.get(prop) != bench_info[prop]:
                        errors.append(
                            f'{key} "{name}".{prop}: expected'
                            f" {json.dumps(bench_info[prop])}, got"
                            f" {json.dumps(local_info.get(prop))}"
                        )

        elif category == "simple_map":
            for name, local_val in local_value.items():
                if name not in bench_value:
                    continue
                if local_val != bench_value[name]:
                    errors.append(
                        f'{key} "{name}": expected {bench_value[name]},'
                        f" got {local_val}"
                    )

        elif category == "nested_map":
            for type_name, local_flags in local_value.items():
                if type_name not in bench_value:
                    continue
                bench_flags = bench_value[type_name]
                for flag_name, local_val in local_flags.items():
                    if flag_name not in bench_flags:
                        continue
                    if local_val != bench_flags[flag_name]:
                        errors.append(
                            f'{key} "{type_name}"."{flag_name}": expected'
                            f" {bench_flags[flag_name]}, got {local_val}"
                        )

        elif category == "format_array":
            for type_name, local_fields in local_value.items():
                if type_name not in bench_value:
                    continue
                # Entries may be malformed on either side: the local file is
                # structurally validated first, but the benchmark is not.
                bench_fields = {
                    f["name"]: f
                    for f in bench_value[type_name]
                    if isinstance(f, dict) and "name" in f
                }
                for local_field in local_fields:
                    if not isinstance(local_field, dict):
                        continue
                    bench_field = bench_fields.get(local_field.get("name"))
                    if not bench_field:
                        continue
                    for prop in bench_field:
                        if local_field.get(prop) != bench_field[prop]:
                            errors.append(
                                f'{key} "{type_name}" field'
                                f' "{local_field["name"]}".{prop}: expected'
                                f" {bench_field[prop]}, got"
                                f" {local_field.get(prop)}"
                            )

    return errors


# ── Drift detection (non-blocking) ───────────────────────────────────────────


def _find_drift(local: dict, benchmark: dict) -> list[str]:
    """Report entries present upstream but absent locally.

    This is reported as a warning rather than an error: rippled develop is
    normally ahead of xrpl-py, because definitions.json is bumped
    deliberately when an amendment is adopted rather than on every merge.
    """
    warnings = []

    for key, bench_value in benchmark.items():
        if key not in local:
            warnings.append(f'Key "{key}" is present upstream but missing locally')
            continue

        category = _classify_value(bench_value)
        local_value = local[key]

        if category == "fields":
            local_names = {name for name, _ in local_value}
            missing = [name for name, _ in bench_value if name not in local_names]
        elif category in ("simple_map", "nested_map", "format_array"):
            missing = [name for name in bench_value if name not in local_value]
        else:
            continue

        if missing:
            shown = ", ".join(sorted(missing)[:10])
            more = f" (+{len(missing) - 10} more)" if len(missing) > 10 else ""
            warnings.append(
                f"{key}: {len(missing)} missing upstream entries: {shown}{more}"
            )

    return warnings


# ── Main ─────────────────────────────────────────────────────────────────────


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validates definitions.json against rippled. The benchmark comes"
            " from a running rippled when a URL is given, otherwise from the"
            " latest server-definitions artifact on develop."
        )
    )
    parser.add_argument(
        "benchmark",
        nargs="?",
        default="",
        metavar="URL",
        help=(
            "JSON-RPC URL of a running rippled to validate against"
            f' (e.g. "{DEFAULT_RPC_URL}"). Omit to use the latest'
            " server-definitions artifact on develop."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Entry point."""
    args = _parse_args()

    if not args.benchmark:
        _check_gh_cli()

    print(f"Reading {DEFINITIONS_PATH}...")
    try:
        with open(DEFINITIONS_PATH, encoding="utf-8") as f:
            local = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: Failed to parse definitions.json: {e}", file=sys.stderr)
        sys.exit(1)

    if args.benchmark:
        benchmark = _benchmark_from_rpc(args.benchmark)
    else:
        benchmark = _download_benchmark()
        if benchmark is None:
            print("Skipping validation: no benchmark available from rippled develop.")
            return

    print("Validating structure...")
    struct_errors = _validate_structure(local, benchmark)
    if struct_errors:
        print(
            f"\n{len(struct_errors)} structural validation error(s):", file=sys.stderr
        )
        for e in struct_errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("Structure OK")

    print("Comparing entries against benchmark...")
    compare_errors = _compare_definitions(local, benchmark)
    if compare_errors:
        print(f"\n{len(compare_errors)} entry mismatch(es) found:", file=sys.stderr)
        for e in compare_errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)

    drift = _find_drift(local, benchmark)
    if drift:
        print(
            f"\nNote: definitions.json is behind the benchmark in"
            f" {len(drift)} place(s):"
        )
        for w in drift:
            print(f"  - {w}")
        print(
            "This is not a failure. Run `poetry run poe definitions` to bump"
            " definitions.json when adopting these amendments."
        )

    print("\nAll shared entries match the benchmark. Validation passed.")


if __name__ == "__main__":
    main()
