"""Script to validate definitions.json against the rippled CI benchmark.

Downloads the server_definitions.json artifact from rippled's develop branch
and compares it against the local definitions.json to ensure structural
correctness and entry consistency.

Requires the GitHub CLI (gh) to be installed and authenticated.
  https://cli.github.com/
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

UPSTREAM_REPO = "XRPLF/rippled"
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


def _exec(cmd: str) -> str:
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def _check_gh_cli() -> None:
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


def _download_benchmark() -> dict:
    print("Downloading benchmark definitions from rippled develop branch...")

    try:
        raw = _exec(
            f'gh api "repos/{UPSTREAM_REPO}/actions/artifacts'
            f'?name={ARTIFACT_NAME}&per_page=50"'
            f" --jq '[.artifacts[] | select(.workflow_run.head_branch == \"develop\""
            f" and .expired == false)] | .[0].workflow_run.id // empty'"
        )
        run_id = raw if raw else None
    except subprocess.CalledProcessError:
        run_id = None

    if not run_id:
        print(
            "Error: Could not find server-definitions artifact on rippled"
            " develop branch.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Found artifact in run {run_id}")
    tmp_dir = tempfile.mkdtemp(prefix="server-definitions-")

    try:
        try:
            _exec(
                f"gh run download {run_id} --repo {UPSTREAM_REPO}"
                f' --name {ARTIFACT_NAME} --dir "{tmp_dir}"'
            )
        except subprocess.CalledProcessError:
            print(
                f"Error: Failed to download artifact from run {run_id}.\n"
                "The artifact may have expired.",
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
                    errors.append(
                        f'{key} "{type_name}": value must be a list'
                    )
                    continue
                for j, field in enumerate(fields):
                    if not isinstance(field.get("name"), str):
                        errors.append(
                            f'{key} "{type_name}"[{j}]: "name" must be a string'
                        )
                    if not isinstance(field.get("optionality"), int):
                        errors.append(
                            f'{key} "{type_name}"[{j}]: "optionality" must be'
                            " an int"
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
                bench_fields = {f["name"]: f for f in bench_value[type_name]}
                for local_field in local_fields:
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


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    _check_gh_cli()

    print(f"Reading {DEFINITIONS_PATH}...")
    try:
        with open(DEFINITIONS_PATH, encoding="utf-8") as f:
            local = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: Failed to parse definitions.json: {e}", file=sys.stderr)
        sys.exit(1)

    benchmark = _download_benchmark()

    print("Validating structure...")
    struct_errors = _validate_structure(local, benchmark)
    if struct_errors:
        print(f"\n{len(struct_errors)} structural validation error(s):", file=sys.stderr)
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

    print("All entries match the benchmark. Validation passed.")


if __name__ == "__main__":
    main()
