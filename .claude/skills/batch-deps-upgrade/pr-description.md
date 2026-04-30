## High Level Overview of Change

Batch dependency upgrade for Q2 2026. Each upgrade was applied and validated individually (unit + integration tests) before committing.

### Context of Change

This PR batches open Dependabot PRs to reduce merge noise. Each dependency was upgraded one at a time, validated with unit and integration tests on the current Python version, then committed individually. A full matrix validation across all CI Python versions was run after all upgrades.

### Type of Change

This is a maintenance upgrade of dependencies and does not fit any of the standard categories. No library code behavior changes unless noted below.

### Did you update CHANGELOG.md?

- [ ] Yes
- [x] No, this change does not impact library users

## Test Plan

- Each dependency was upgraded individually and validated with unit tests and integration tests
- Full CI matrix validation (lint, type-check, unit, integration, faucet) run after all upgrades

## Superseded Dependabot PRs

| PR | Package | From | To | Status | MajorVersionUpgrade |
|---|---|---|---|---|---|
| [#941](https://github.com/XRPLF/xrpl-py/pull/941) | requests | 2.32.4 | 2.33.1 | Upgraded | No |
| [#939](https://github.com/XRPLF/xrpl-py/pull/939) | sphinx-rtd-theme | 3.0.2 | 3.1.0 | Upgraded | No |
| [#938](https://github.com/XRPLF/xrpl-py/pull/938) | packaging | 25.0 | 26.2 | Upgraded | Yes ([v26](https://github.com/pypa/packaging/releases/tag/26.0)) |

### Major version upgrade notes

**packaging 25.0 → 26.2** ([release notes](https://github.com/pypa/packaging/releases/tag/26.0)): v26 adds PEP 751 pylock support, PEP 794 import name metadata, ~3x faster tokenization, and caching for Version/Specifier objects. The deprecated `._version` NamedTuple has a compatibility shim. No code changes were required because xrpl-py does not import packaging directly — it is only a transitive dependency of black and sphinx, pinned as a dev dep.
| [#936](https://github.com/XRPLF/xrpl-py/pull/936) | types-deprecated | 1.2.15.20241117 | 1.3.1.20260408 | Upgraded | No |
| [#935](https://github.com/XRPLF/xrpl-py/pull/935) | poethepoet | 0.30.0 | — | Pending | — |
| [#934](https://github.com/XRPLF/xrpl-py/pull/934) | typing-extensions | 4.13.2 | — | Pending | — |
| [#933](https://github.com/XRPLF/xrpl-py/pull/933) | mypy | 1.16.1 | — | Pending | — |
| [#932](https://github.com/XRPLF/xrpl-py/pull/932) | websockets | 13.1 | — | Pending | — |
| [#931](https://github.com/XRPLF/xrpl-py/pull/931) | pydoclint | 0.5.19 | — | Pending | — |
| [#930](https://github.com/XRPLF/xrpl-py/pull/930) | coverage | 7.9.1 | — | Pending | — |
| [#928](https://github.com/XRPLF/xrpl-py/pull/928) | isort | 5.13.2 | — | Pending | — |
| [#926](https://github.com/XRPLF/xrpl-py/pull/926) | pygments | 2.19.2 | — | Pending | — |

**Progress: 4/12 dependencies processed**

### Closing instructions

*(will be filled in after all dependencies are processed)*
