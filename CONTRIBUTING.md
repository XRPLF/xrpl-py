# Contributing

## Set up your dev environment

If you want to contribute code to `xrpl-py`, the following sections describe how to set up your developer environment.

### Set up Python environment

To make it easy to manage your Python environment with `xrpl-py`, including switching between versions, install `pyenv` and follow these steps:

* Install [`pyenv`](https://github.com/pyenv/pyenv):

        brew install pyenv

    For other installation options, see the [`pyenv` README](https://github.com/pyenv/pyenv#installation).

* Use `pyenv` to install the optimized version for `xrpl-py` (currently 3.9.1):

        pyenv install 3.9.1

* Set the [global](https://github.com/pyenv/pyenv/blob/master/COMMANDS.md#pyenv-global) version of Python with `pyenv`:

        pyenv global 3.9.1

### Set up shell environment

To enable autocompletion and other functionality from your shell, add `pyenv` to your environment.

These steps assume that you're using a [Zsh](http://zsh.sourceforge.net/) shell. For other shells, see the [`pyenv` README](https://github.com/pyenv/pyenv#basic-github-checkout).


* Add `pyenv init` to your Zsh shell:

        echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.zshrc

* Source or restart your terminal:

        . ~/.zshrc

### Manage dependencies and virtual environments

To simplify managing library dependencies and the virtual environment, `xrpl-py` uses [`poetry`](https://python-poetry.org/docs).

* [Install `poetry`](https://python-poetry.org/docs/#osx-linux-bashonwindows-install-instructions):

        curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
        poetry install

### Set up `pre-commit` hooks

To run linting and other checks, `xrpl-py` uses [`pre-commit`](https://pre-commit.com/).

**Note:** You only need to install `pre-commit` if you want to contribute code to `xrpl-py`.


* Install `pre-commit`:

        pip3 install pre-commit
        pre-commit install

### Run the linter

To run the linter:

```bash
poetry run flake8 ./xrpl
```

### Running Tests

To run unit tests:

```bash
poetry run python3 -m unittest discover tests/unit
```

To run integration tests:

```bash
poetry run python3 -m unittest discover tests/integration
```

To switch your python version before running tests:

```bash
pyenv local 3.9
poetry env use python3.9
poetry install
```
Replace `python3.9` with whatever version of Python you want to use (you must have it installed with `pyenv` for it to work).


### Generate reference docs

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
open _build/html/index.html
```


## Release process

### Editing the Code

* Your changes should have unit and/or integration tests.
* Your changes should pass the linter.
* Your code should pass all the unit tests on Github (which check all 3 versions of Python).
* Open a PR against `master` and ensure that all CI passes.
* Get a full code review from one of the maintainers.
* Merge your changes.

### Release

1. Run integration tests on `master`, using [Github Actions](https://github.com/XRPLF/xrpl-py/actions/workflows/integration_test.yml), which runs them on all 3 versions of Python.
2. Create a branch off master that properly increments the version in `pyproject.toml` and updates the `CHANGELOG` appropriately. We follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
3. Merge this branch into `master`.
4. Run integration tests on `master` again just in case.
5. Create a new Github release/tag off of this branch.
6. Locally build and download the package.
    1. Pull master locally.
    2. Locally download the package by running `pip install path/to/local/xrpl-py/dist/.whl`
    3. Make sure that this local installation works as intended, and that changes are reflected properly
7. Run `poetry publish --dry-run` and make sure everything looks good
8. Publish the update by running `poetry publish`
    * This will require entering PyPI login info
