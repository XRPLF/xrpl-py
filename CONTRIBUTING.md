# Contributing

## Set up your dev environment

If you want to contribute code to `xrpl-py`, the following sections describe how to set up your developer environment.

### Set up Python environment

To make it easy to manage your Python environment with `xrpl-py`, including switching between versions, install `pyenv` and follow these steps:

- Install [`pyenv`](https://github.com/pyenv/pyenv):

        brew install pyenv

  For other installation options, see the [`pyenv` README](https://github.com/pyenv/pyenv#installation).

- Use `pyenv` to install the optimized version for `xrpl-py` (currently 3.11.6):

        pyenv install 3.11.6

- Set the [global](https://github.com/pyenv/pyenv/blob/main/COMMANDS.md#pyenv-global) version of Python with `pyenv`:

        pyenv global 3.11.6

  - If you're already using `pyenv` you can instead run the following to just use the desired version for this directory:

        pyenv local 3.11.6

### Set up shell environment

To enable autocompletion and other functionality from your shell, add `pyenv` to your environment.

These steps assume that you're using a [Zsh](http://zsh.sourceforge.net/) shell. For other shells, see the [`pyenv` README](https://github.com/pyenv/pyenv#basic-github-checkout).

- Add `pyenv init` to your Zsh shell:

        echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc

- Source or restart your terminal:

        . ~/.zshrc

### Manage dependencies and virtual environments

To simplify managing library dependencies and the virtual environment, `xrpl-py` uses [`poetry`](https://python-poetry.org/docs).

- [Install `poetry`](https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions):

        curl -sSL https://install.python-poetry.org | python3 -

May need to run `export PATH="$HOME/.local/bin:$PATH"` to invoke Poetry (see step 3 "Add Poetry to your PATH").

- [Install `poetry` dependencies](https://python-poetry.org/docs/pyproject/#scripts) from pyproject.toml:

        poetry install

### Set up `pre-commit` hooks

To run linting and other checks, `xrpl-py` uses [`pre-commit`](https://pre-commit.com/).

**Note:** You only need to install `pre-commit` if you want to contribute code to `xrpl-py`.

- Install `pre-commit`:

        pip3 install pre-commit
        pre-commit install

### Run the linter

To run the linter:

```bash
poetry run poe lint
```

### Running Tests

#### Individual Tests

```bash
# Works for single or multiple unit/integration tests
# Ex: poetry run poe test tests/unit/models/test_response.py tests/integration/transactions/test_account_delete.py
poetry run poe test FILE_PATHS
```

#### Unit Tests

```bash
poetry run poe test_unit
```

#### Integration Tests

To run integration tests, you'll need a standalone `xrpld` node running with WS port `6006` and JSON RPC port `5005`. You can run a docker container for this:

```bash
docker run \
  --detach \
  --publish 5005:5005 \
  --publish 6006:6006 \
  --volume "$PWD/.ci-config/:/etc/xrpld/" \
  --name xrpld-service \
  rippleci/xrpld:develop --standalone
```

Breaking down the command:

- `--detach` — run in background
- `--publish 5005:5005 --publish 6006:6006` — expose JSON-RPC and WebSocket ports
- `--volume "$PWD/.ci-config/:/etc/xrpld/"` — mount local config into the container
- `--name xrpld-service` — name the container
- `rippleci/xrpld:develop` — latest `develop` branch build of xrpld
- `--standalone` — start xrpld in standalone mode

When you're done, stop and remove the container with `docker stop xrpld-service && docker rm xrpld-service`.

Maintainers can run the CI integration tests against a private xrpld image by committing a version to `.github/xrpld-image.env`. Set `XRPLD_PRIVATE_VERSION` to the version without the `private-` prefix (for example, `XRPLD_PRIVATE_VERSION=3.3.0-rc2`); every workflow run triggered afterwards — including pull request runs — pulls `registry.gitlab.com/ripple/xrpledger/xrpld_package_deploy/xrpld-private:private-<version>`. Leave the value empty to use the default public image `rippleci/xrpld:develop`.

Private image access requires the repository variable `GITLAB_REGISTRY_USERNAME` and repository secret `GITLAB_REGISTRY_TOKEN`, configured with a GitLab deploy token that has `read_registry` access. These credentials are not exposed to fork pull requests, so a private version must be tested from a branch in this repository; a fork pull request with a private version set will fail fast rather than silently fall back.

Then to actually run the tests, run the command:

```bash
poetry run poe test_integration
```

#### Faucet Tests

```bash
poetry run poe test_faucet
```

#### Code Coverage

To run both unit and integration tests and see code coverage:

```bash
poetry run poe test_coverage
```

To see manually code coverage after running unit tests or integration tests:

```bash
poetry run coverage report
```

#### Running tests with different Python versions

To switch your python version before running tests:

```bash
pyenv local 3.11
poetry env use python3.11
poetry install
```

Replace `python3.11` with whatever version of Python you want to use (you must have it installed with `pyenv` for it to work).

## Generate reference docs

You can see the complete reference documentation at [`xrpl-py` docs](https://xrpl-py.readthedocs.io/en/latest/index.html). You can also generate them locally using `poetry` and `sphinx`:

```bash
# Go to the docs/ folder
cd docs/

# Build the docs
poetry run sphinx-apidoc -o source/ ../xrpl
poetry run make html
```

To see the output:

```bash
# Go to docs/_build/html/
cd docs/_build/html/

# Open the index file to view it in a browser:
open index.html
```

You can view docs builds for xrpl-py versions on the ReadTheDocs website here: https://readthedocs.org/projects/xrpl-py/builds/

In order to test how a change in docs configuration looks like on ReadTheDocs before merging:

1. Publish a branch with your docs configuration changes
2. Active and hide the branch by scrolling down on this page: https://readthedocs.org/projects/xrpl-py/versions/
3. View the page / build results here: https://readthedocs.org/projects/xrpl-py/builds/
4. Once you're done testing, make the test branch inactive.

## Write integration tests

1. If adding functionality to a new part of the library, create new file with a class that inherits `IntegrationTestCase` from `tests.integration.integration_test_case` to store all individual tests under (ex: `class TestWallet(IntegrationTestCase)`). Otherwise, add to an existing file.
2. Create an async function for each test case (unless the test is only being used for the sync client)
3. Include the `@test_async_and_sync` decorator to test against all client types, unless you specifically only want to test with one client. You can also use the decorator to:
   - Limit tests to sync/async only
   - Limit the number of retries
   - Use Testnet instead of a standalone network
   - Import modules for sync equivalents of any async functions used
4. Be sure to reuse pre-made values, `WALLET`, `DESTINATION`, `TESTNET_WALLET`, `TESTNET_DESTINATION`, `OFFER`, and `PAYMENT_CHANNEL`, from `tests/integrations/reusable_values.py`
5. Be sure to use condensed functions, like `submit_transaction_async` and `sign_and_reliable_submission_async`, from `tests/integrations/it_utils.py`

Examples can be found in subfolders of [tests/integrations](https://github.com/XRPLF/xrpl-py/tree/main/tests/integration)

## Updating `definitions.json` and models

To update just the `definitions.json` file:

```bash
poetry run poe definitions https://github.com/XRPLF/rippled/tree/develop
```

Any Github branch link or local path to rippled will work here.

To update the models as well:

```bash
poetry run poe generate https://github.com/XRPLF/rippled/tree/develop
```

Verify that the changes make sense by inspection before submitting, as there may be updates required for the `xrpl-codec-gen` tool depending on the latest amendments we're updating to match.

## Code review

A PR can merge into `main` when it has:

- **One approving review** from a maintainer with write access.
- **All required checks passing**, including:
  - the lint, unit and integration tests;
  - `ai-review`, the XRPLF AI Reviewer (see [The AI reviewer](#the-ai-reviewer));
  - `second-review`, which only matters on PRs labeled `needs-second-reviewer` (see below).

Approving a PR means you reviewed it yourself. The AI reviewer is an extra check, not a replacement for your review.

### When a PR needs a second review

Add the `needs-second-reviewer` label when one reviewer shouldn't be the only line of defense. The first reviewer usually adds it; authors who can add labels should add it themselves. Use it for:

- Binary serialization or encoding: `xrpl/core/binarycodec` (including `definitions.json`) and `xrpl/core/addresscodec`.
- Keys, signing and cryptography: `xrpl/core/keypairs`, `xrpl/wallet`, transaction signing, multisigning and `Batch`, and confidential MPT (`xrpl/ext/confidential`).
- Breaking changes to the public API.
- Security fixes.
- Release, publishing or CI changes under `.github/`.
- Large or cross-cutting changes that the first reviewer can't fully verify alone.

On a labeled PR, the `second-review` check fails until two reviewers with write access have approved. Only each reviewer's latest review counts, and bot approvals never count. The check updates about a minute after each push, label change or review. Don't remove the label to get around the check; if it was added by mistake, ask the maintainer who added it.

### The AI reviewer

The XRPLF AI Reviewer posts the `ai-review` check and inline comments on every PR.

- **When it runs:** automatically on each push to a PR opened from a branch in this repo. On PRs from forks, the check stays pending until a maintainer comments `/ai-review` on the PR.
- **What fails the check:** an unresolved finding of high or critical severity. Medium and low findings are posted as comments and don't block. Documentation and `*.md` files never block.
- **Fixing a finding:** push a fix. Each push gets a fresh review, and the check updates when it finishes.
- **False positives:** reply to the finding with `False positive:` followed by a short reason, for example `False positive: the value is matched against HEX_REGEX above, so it can't contain non-hex characters`. The finding won't be raised again on that PR. If you have write access, the check is recomputed right away, and the bot replies `Dismissed by @you — gate updated`. If you don't, the check stays failed until a maintainer agrees, either by replying `False positive:` on the same finding or with an override.
- **Overrides:** a maintainer can comment `/ai-review override <reason>` to mark the current commit as passing. Overrides are logged. Use them when a dismissal doesn't apply, and give a real reason.
- **Only dismiss findings that are actually wrong.** Disagreement replies teach the reviewer what not to flag in this repo, so dismissing a valid finding makes future reviews worse.
- **If the check stays pending** for more than about 15 minutes on a PR from this repo, the reviewer service may be down. Ask a repository admin.


## Mailing Lists

We have a low-traffic mailing list for announcements of new `xrpl-py` releases. (About 1 email every couple of weeks)

- [Subscribe to xrpl-announce](https://groups.google.com/g/xrpl-announce)

If you're using the XRP Ledger in production, you should run a [rippled server](https://github.com/ripple/rippled) and subscribe to the ripple-server mailing list as well.

- [Subscribe to ripple-server](https://groups.google.com/g/ripple-server)
