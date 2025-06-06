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

To run integration tests, you'll need a standalone rippled node running with WS port `6006` and JSON RPC port `5005`. You can run a docker container for this:

```bash
docker run -dit -p 5005:5005 -p 6006:6006 --volume $PWD/.ci-config/:/etc/opt/ripple/ --entrypoint bash rippleci/rippled:develop -c 'rippled -a'
```

Breaking down the command:
* `docker run -p 5005:5005 -p 6006:6006` starts a Docker container with an open port for admin JsonRPC and WebSocket requests.
* `-it` allows you to interact with the container.
* `-d` runs the docker container in detached mode. The container will run in the background and developer gets back control of the terminal
* `-t` starts a terminal in the container for you to send commands to.
* `--volume $PWD/.ci-config:/etc/opt/ripple/` mounts the directories as indicated. It must be an absolute path, so we use `$PWD` instead of `./`. `rippled` software searches the location `/etc/opt/ripple/` (default behavior) for the config files. Hence there is no need to explicitly specify the config-file path.
* `rippleci/rippled:develop` is an image that is regularly updated with the latest build of the `develop` branch of `rippled`.
* `-a` starts `rippled` in standalone mode

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

## Release process

### Editing the Code

- Your changes should have unit and/or integration tests.
- Your changes should pass the linter.
- Your code should pass all the unit and integration tests on Github (which check all versions of Python).
- Open a PR against `main` and ensure that all CI passes.
- Get a full code review from one of the maintainers.
- Merge your changes.

### Release
1. Please increment the version in `pyproject.toml` and update the `CHANGELOG.md` file appropriately. We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
2. Please select a commit that is suitable for release and create a tag. The following commands can be helpful:
`git tag -s -a <tag-title> -m "Optional Message describing the tag"`
`git tag` -- This command displays all the tags in the repository.
`git push <remote_name, e.g. upstream> tag <tag_title>`
3. A [Github Workflow](.github/workflows/publish_to_pypi.yml) completes the rest of the Release steps (building the project, generating a .whl and tarball, publishing on the PyPI platform). The workflow uses OpenID Connect's temporary keys to obtain the necessary PyPI authorization.
As a prerequisite, the PyPI `xrpl-py` project needs to authorize Github Actions as a "Trusted Publisher". This page contains helpful resources: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/#configuring-trusted-publishing
4. Send an email to [xrpl-announce](https://groups.google.com/g/xrpl-announce).
5. Post an announcement in the [XRPL Discord #python channel](https://discord.com/channels/886050993802985492/886053080913821717) with a link to the changes and highlighting key changes.


**Note: If maintainers prefer to manually release the xrpl-py software distribution, the below steps are relevant.**
1. Create a branch off main that properly increments the version in `pyproject.toml` and updates the `CHANGELOG` appropriately. We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
2. Merge this branch into `main`.
3. Locally build and download the package.
   1. Pull main locally.
   2. Run `poetry build` to build the package locally.
   3. Locally download the package by running `pip install path/to/local/xrpl-py/dist/.whl`.
   4. Make sure that this local installation works as intended, and that the changes are reflected properly.
4. Run `poetry publish --dry-run` and make sure everything looks good.
5. Publish the update by running `poetry publish`.
   - This will require entering PyPI login info.
6. Create a new Github release/tag off of this branch.
7. Send an email to [xrpl-announce](https://groups.google.com/g/xrpl-announce).
8. Post an announcement in the [XRPL Discord #python channel](https://discord.com/channels/886050993802985492/886053080913821717) with a link to the changes and highlighting key changes.

## Mailing Lists

We have a low-traffic mailing list for announcements of new `xrpl-py` releases. (About 1 email every couple of weeks)

- [Subscribe to xrpl-announce](https://groups.google.com/g/xrpl-announce)

If you're using the XRP Ledger in production, you should run a [rippled server](https://github.com/ripple/rippled) and subscribe to the ripple-server mailing list as well.

- [Subscribe to ripple-server](https://groups.google.com/g/ripple-server)
