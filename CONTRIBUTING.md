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

### Manage dependencies and virutal environment

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
poetry env use python3.9
poetry install
```
Replace `python3.9` with whatever version of Python you want to use (you must have it installed with `pyenv` for it to work).

To run the tests on all supported versions of Python without needing to switch your poetry Python version, run:
```bash
poetry run nox -rs unit_tests # for unit tests
poetry run nox -rs unit_tests-3.7 # for a specific version of Python
poetry run nox -rs integration_tests # for integration tests
```

To run a specific unit test:
```bash
poetry run nox -rs unit_tests -- <directory or module> # for unit tets
poetry run nox -rs unit_tests-3.7 -- <directory or module> # for a specific version of Python
poetry run nox -rs integration_tests -- <directory or module> # for integration tests
```


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
